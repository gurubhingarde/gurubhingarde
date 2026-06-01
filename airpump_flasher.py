#!/usr/bin/env python3
"""
Airpump ECU Flash Tool
Protocol: Custom 8-byte CAN frames (NOT UDS)

CAN IDs:
  Tool → ECU : 0x180006FF  (SA=0xFF, DA=0x06)
  ECU  → Tool: 0x1800FF06  (SA=0x06, DA=0xFF)
  Broadcast  : 0x1800FFFF  (flash-complete notify)

Frame layout:
  [TYPE] [B1] [B2] [B3] [B4] [B5] [B6] [XOR]
  Byte7 = XOR of bytes 0..6

Frame types:
  0x00 = Heartbeat / End-of-block
  0x01 = Data frame toggle-A
  0x02 = Data frame toggle-B
  0x03 = Close session
  0x04 = Block init / Program command
  0xFF = Broadcast complete (ECU → all)

Hex file format:
  Intel HEX with interleaved 32-byte records (16-byte overlap).
  Data is read SEQUENTIALLY as a flat bytestream — NOT address-mapped.
  Last 4 bytes of the stream = 32-bit CRC (stored at 0x003F5FFE).
"""

import can
import time
import sys
import argparse
import logging
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

TOOL_ID = 0x180006FF   # Tool → ECU
ECU_ID  = 0x1800FF06   # ECU  → Tool
BCAST_ID = 0x1800FFFF  # ECU broadcast on completion

HEARTBEAT       = bytes([0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00, 0x07])
HEARTBEAT_INTERVAL = 0.101      # 101 ms between keepalives
HEARTBEAT_COUNT    = 20         # send this many before expecting ECU to respond
ECU_WAKEUP_TIMEOUT = 3.0        # seconds to wait for ECU to echo first heartbeat

BLOCK_SIZE      = 0x4000        # 16 384 bytes for full blocks
PAYLOAD_BYTES   = 6             # data bytes per CAN frame
ERASE_TIMEOUT   = 2.0           # ECU erase can take ~730 ms, give 2 s margin
PROG_TIMEOUT    = 2.0           # final NVM write ~754 ms
ACK_TIMEOUT     = 0.5           # normal echo ACK
LAST_FRAME_TIMEOUT = 0.5        # ECU may take ~10 ms on last block frame

log = logging.getLogger("flasher")


# ── Utility ───────────────────────────────────────────────────────────────────

def xor8(data: bytes) -> int:
    """XOR checksum of bytes 0-6."""
    result = 0
    for b in data[:7]:
        result ^= b
    return result


def make_frame(b0: int, payload: bytes) -> bytes:
    """Build a valid 8-byte frame: [b0, p0..p5, xor]."""
    assert len(payload) == PAYLOAD_BYTES
    raw = bytes([b0]) + payload
    return raw + bytes([xor8(raw)])


def verify_frame(data: bytes) -> bool:
    """Return True if the XOR checksum is valid."""
    return len(data) == 8 and xor8(data) == data[7]


# ── Hex File Parser ───────────────────────────────────────────────────────────

def load_hex(path: str) -> tuple[bytes, bytes, int]:
    """
    Parse Intel HEX file in the interleaved format used by this ECU.
    Records are read SEQUENTIALLY as a bytestream (ignoring addresses).

    The CRC record is identified as the final data record with exactly 4 bytes —
    its address is remembered so the PROGRAM command can target it precisely.

    Returns (firmware_payload, crc_4bytes, crc_flash_address).
    """
    seq       = bytearray()
    ela       = 0
    crc_addr  = None  # flash address of the 4-byte CRC record

    with open(path) as f:
        records = []
        for line in f:
            line = line.strip()
            if not line.startswith(':'):
                continue
            bc   = int(line[1:3], 16)
            addr = int(line[3:7], 16)
            rt   = int(line[7:9], 16)
            data = bytes.fromhex(line[9:9 + bc * 2])
            records.append((bc, addr, rt, data))

    # Forward pass: find CRC record (last 4-byte data record) and base address
    # (first data record with more than 4 bytes).
    ela = 0
    base_addr = None
    for bc, addr, rt, data in records:
        if rt == 4:
            ela = int.from_bytes(data, "big") << 16
        elif rt == 0:
            if bc == 4:
                crc_addr = ela | addr   # overwritten → ends up as last 4-byte record
            if base_addr is None and bc > 4:
                base_addr = ela | addr  # first real data record

    if crc_addr is None:
        raise ValueError("Could not locate 4-byte CRC record in hex file")
    if base_addr is None:
        raise ValueError("No data records found in hex file")

    # Second pass: collect sequential data bytes
    ela = 0
    for bc, addr, rt, data in records:
        if rt == 4:
            ela = int.from_bytes(data, "big") << 16
        elif rt == 0:
            seq += data
        elif rt == 1:
            break

    if len(seq) < 4:
        raise ValueError("HEX file too small")

    crc_bytes = bytes(seq[-4:])
    firmware  = bytes(seq[:-4])
    log.info("Hex loaded: %d payload bytes + 4-byte CRC 0x%s  base=0x%08X  crc_addr=0x%08X",
             len(firmware), crc_bytes.hex().upper(), base_addr, crc_addr)
    return firmware, crc_bytes, crc_addr, base_addr


# ── Block Layout ──────────────────────────────────────────────────────────────

def build_blocks(firmware: bytes, base_addr: int) -> list[dict]:
    """
    Split firmware into flash blocks. Base address comes from the hex file
    (first data record's full address) so different firmware versions with
    different flash layouts are handled automatically.
    """
    ADDR_STEP = 0x2000
    MAX_BLOCK = 0x4000

    total_blocks = -(-len(firmware) // MAX_BLOCK)
    raw_ids   = list(range(total_blocks + 1, 1, -1))
    block_ids = [1 if x == 2 else x for x in raw_ids]

    blocks = []
    offset = 0
    addr   = base_addr

    for b_id in block_ids:
        chunk = firmware[offset:offset + MAX_BLOCK]
        blocks.append({
            "addr":     addr,
            "size":     len(chunk),
            "data":     chunk,
            "block_id": b_id,
        })
        offset += MAX_BLOCK
        addr   += ADDR_STEP

    return blocks


def addr_to_04_payload(full_addr: int, size: int) -> bytes:
    """
    Convert a 32-bit address + size into the 6-byte payload of a 04 frame.
    Format: [SEG=0x00] [ADDR_H] [ADDR_L] [ADDR_LL] [SIZE_H] [SIZE_L]
    e.g. addr=0x003E8000, size=0x4000 → 00 3E 80 00 40 00
    """
    seg     = (full_addr >> 24) & 0xFF
    addr_h  = (full_addr >> 16) & 0xFF
    addr_l  = (full_addr >>  8) & 0xFF
    addr_ll = (full_addr >>  0) & 0xFF
    size_h  = (size >> 8) & 0xFF
    size_l  =  size        & 0xFF
    return bytes([seg, addr_h, addr_l, addr_ll, size_h, size_l])


# ── CAN Transport ─────────────────────────────────────────────────────────────

class CANFlasher:
    def __init__(self, interface: str, channel: str, bitrate: int = 500_000):
        self.bus = can.interface.Bus(
            interface=interface,
            channel=channel,
            bitrate=bitrate,
        )
        log.info("CAN bus open: %s %s @ %d bps", interface, channel, bitrate)

    def close(self):
        self.bus.shutdown()

    def send(self, arb_id: int, data: bytes):
        msg = can.Message(arbitration_id=arb_id, data=data, is_extended_id=True)
        self.bus.send(msg)

    def recv_ack(self, timeout: float = ACK_TIMEOUT) -> bytes | None:
        """Wait for an ECU echo on ECU_ID. Returns 8-byte data or None."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            msg = self.bus.recv(timeout=deadline - time.monotonic())
            if msg is None:
                break
            if msg.arbitration_id == ECU_ID and len(msg.data) == 8:
                return bytes(msg.data)
        return None

    def send_and_wait(self, data: bytes, timeout: float = ACK_TIMEOUT,
                      expected: bytes | None = None) -> bytes:
        """
        Send a frame on TOOL_ID and wait for the ECU to echo it back.
        Raises RuntimeError if no ACK or ACK mismatch.
        """
        assert verify_frame(data), f"TX frame bad XOR: {data.hex()}"
        self.send(TOOL_ID, data)
        ack = self.recv_ack(timeout)
        if ack is None:
            raise RuntimeError(f"No ACK for frame {data.hex()}")
        if expected is None:
            expected = data
        if ack != expected:
            raise RuntimeError(
                f"ACK mismatch:\n  sent: {data.hex()}\n  got:  {ack.hex()}"
            )
        return ack

    # ── High-level steps ──────────────────────────────────────────────────────

    def phase_keepalive(self):
        """Send heartbeats and wait for ECU to mirror back."""
        log.info("Phase 1: Keepalive — waking ECU...")
        for i in range(HEARTBEAT_COUNT):
            self.send(TOOL_ID, HEARTBEAT)
            time.sleep(HEARTBEAT_INTERVAL)

        # Wait for ECU to start echoing
        deadline = time.monotonic() + ECU_WAKEUP_TIMEOUT
        while time.monotonic() < deadline:
            msg = self.bus.recv(timeout=0.2)
            if msg and msg.arbitration_id == ECU_ID:
                log.info("ECU responded (msg: %s) — proceeding", msg.data.hex())
                return
        raise RuntimeError("ECU did not respond to keepalive within timeout")

    def phase_flash_block(self, block: dict, progress_cb=None):
        """
        Transfer one block of firmware to the ECU.
        block = {addr, size, data, block_id}
        """
        addr   = block["addr"]
        data   = block["data"]
        b_id   = block["block_id"]
        size   = block["size"]
        n_frames = (size + PAYLOAD_BYTES - 1) // PAYLOAD_BYTES

        log.info("  Block 0x%08X  size=0x%04X (%d bytes)  id=%02X",
                 addr, size, size, b_id)

        # ── Step A: 04 Init (triggers ECU erase, expect ~730ms delay) ────────
        init_payload = addr_to_04_payload(addr, size)
        init_frame   = make_frame(0x04, init_payload)
        log.debug("    → INIT %s", init_frame.hex().upper())
        self.send_and_wait(init_frame, timeout=ERASE_TIMEOUT)
        log.debug("    ← INIT ACK (erase done)")

        # ── Step B: Stream data frames ────────────────────────────────────────
        toggle  = 0x01
        offset  = 0
        sent    = 0

        for frame_idx in range(n_frames):
            chunk = data[offset:offset + PAYLOAD_BYTES]
            # Pad with 0xFF (erased flash value) only if last chunk is short.
            # Never overwrite actual firmware bytes — the FF FF seen in the
            # original capture was real firmware data, not a protocol marker.
            if len(chunk) < PAYLOAD_BYTES:
                chunk = chunk.ljust(PAYLOAD_BYTES, b'\xFF')

            is_last = (frame_idx == n_frames - 1)
            frame = make_frame(toggle, chunk)
            ack_timeout = LAST_FRAME_TIMEOUT if is_last else ACK_TIMEOUT
            self.send_and_wait(frame, timeout=ack_timeout)

            toggle = 0x02 if toggle == 0x01 else 0x01
            offset += PAYLOAD_BYTES
            sent   += 1

            if progress_cb:
                progress_cb(sent, n_frames, addr)

        log.debug("    Sent %d data frames", sent)

        # ── Step C: End-of-block marker ───────────────────────────────────────
        # Mirror bytes 3-6 of the last data frame into the end-of-block payload
        last_chunk = chunk  # preserved from loop above
        eob_payload = bytes([0x00, b_id]) + bytes(last_chunk[2:6])
        eob_frame   = make_frame(0x00, eob_payload)
        log.debug("    → EOB  %s", eob_frame.hex().upper())
        self.send_and_wait(eob_frame)
        log.debug("    ← EOB ACK")

    def phase_program(self, crc_addr: int, crc_bytes: bytes):
        """
        Send the final PROGRAM command that writes the 4-byte CRC to flash.
        ECU takes ~754ms to respond (actual NVM write cycle).
        """
        assert len(crc_bytes) == 4
        prog_payload = addr_to_04_payload(crc_addr, 4)
        prog_frame   = make_frame(0x04, prog_payload)
        log.info("Phase 3: Program command (address=0x%08X, CRC=%s)",
                 crc_addr, crc_bytes.hex().upper())
        self.send_and_wait(prog_frame, timeout=PROG_TIMEOUT)
        log.info("  Program ACK received")

    def phase_verify_close(self, crc_bytes: bytes):
        """
        Send verify (type=01) then close (type=03) frames with firmware CRC.
        Wait for ECU broadcast on 0x1800FFFF.
        """
        # CRC payload: 00 CRC_B1 CRC_B2 CRC_B3 FF FF
        crc_payload = bytes([0x00]) + crc_bytes[1:4] + bytes([0xFF, 0xFF])

        verify_frame_ = make_frame(0x01, crc_payload)
        close_frame_  = make_frame(0x03, crc_payload)

        log.info("Phase 4: Verify  (CRC=0x%s)", crc_bytes.hex().upper())
        self.send_and_wait(verify_frame_)
        log.info("  Verify ACK")

        log.info("Phase 4: Close session")
        self.send_and_wait(close_frame_, timeout=0.5)
        log.info("  Close ACK")

        # Wait for broadcast from 0x1800FFFF
        log.info("Phase 5: Waiting for ECU broadcast...")
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            msg = self.bus.recv(timeout=0.2)
            if msg and msg.arbitration_id == BCAST_ID:
                log.info("  ✓ Broadcast received: %s", bytes(msg.data).hex().upper())
                return
        log.warning("  No broadcast received (may still have succeeded)")


# ── Progress display ──────────────────────────────────────────────────────────

def make_progress(total_fw_bytes: int):
    """Returns a progress callback that prints a progress bar."""
    total_frames = (total_fw_bytes + PAYLOAD_BYTES - 1) // PAYLOAD_BYTES
    sent_so_far  = [0]

    def cb(sent_block, total_block, addr):
        sent_so_far[0] += 1
        pct = sent_so_far[0] * 100 // total_frames
        bar = "█" * (pct // 2) + "░" * (50 - pct // 2)
        print(f"\r  [{bar}] {pct:3d}%  addr=0x{addr:08X}  frame {sent_so_far[0]}/{total_frames}",
              end="", flush=True)

    return cb


# ── Main ──────────────────────────────────────────────────────────────────────

def flash(hex_path: str, interface: str, channel: str,
          bitrate: int = 500_000, dry_run: bool = False,
          args_crc_addr: int = None):

    # 1. Parse hex file — base address and CRC address auto-detected from file
    firmware, crc_bytes, crc_addr_hex, base_addr = load_hex(hex_path)
    crc_int  = int.from_bytes(crc_bytes, "big")
    CRC_ADDR = args_crc_addr if args_crc_addr else crc_addr_hex
    log.info("Firmware: %d bytes  base=0x%08X  CRC=0x%08X  crc_addr=0x%08X",
             len(firmware), base_addr, crc_int, CRC_ADDR)

    # 2. Split into blocks
    blocks = build_blocks(firmware, base_addr)
    log.info("Split into %d blocks:", len(blocks))
    for b in blocks:
        log.info("  0x%08X  %5d bytes  id=0x%02X", b["addr"], b["size"], b["block_id"])

    if dry_run:
        log.info("Dry run — not opening CAN bus")
        return

    # 3. Open CAN
    flasher = CANFlasher(interface, channel, bitrate)
    progress = make_progress(len(firmware))

    try:
        # Phase 1: Keepalive
        flasher.phase_keepalive()

        # Phase 2: Transfer all blocks
        log.info("Phase 2: Flashing %d blocks...", len(blocks))
        for i, block in enumerate(blocks):
            log.info("  Block %d/%d", i + 1, len(blocks))
            flasher.phase_flash_block(block, progress_cb=progress)
        print()  # newline after progress bar

        # Phase 3: Program (write CRC to flash)
        flasher.phase_program(CRC_ADDR, crc_bytes)

        # Phase 4+5: Verify + Close + Broadcast
        flasher.phase_verify_close(crc_bytes)

        log.info("✓ Flash complete!")

    except RuntimeError as e:
        log.error("Flash FAILED: %s", e)
        sys.exit(1)
    finally:
        flasher.close()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Airpump ECU flash tool — custom 8-byte CAN protocol"
    )
    parser.add_argument("hex",        help="Path to .hex firmware file")
    parser.add_argument("--interface", default="pcan",
                        help="python-can interface (pcan, socketcan, kvaser, …)")
    parser.add_argument("--channel",   default="PCAN_USBBUS1",
                        help="CAN channel (e.g. PCAN_USBBUS1, can0, …)")
    parser.add_argument("--bitrate",   type=int, default=500_000,
                        help="CAN bitrate in bps (default 500000)")
    parser.add_argument("--dry-run",   action="store_true",
                        help="Parse hex and show block layout without opening CAN")
    parser.add_argument("--crc-addr",  type=lambda x: int(x, 16),
                        default=0x003F5FFE,
                        help="Flash address where CRC is written (hex, default 0x3F5FFE)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S.%f"[:-3],
    )

    flash(
        hex_path=args.hex,
        interface=args.interface,
        channel=args.channel,
        bitrate=args.bitrate,
        dry_run=args.dry_run,
        args_crc_addr=args.crc_addr,
    )


if __name__ == "__main__":
    main()
