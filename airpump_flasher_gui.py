#!/usr/bin/env python3
"""
Airpump ECU Flash Tool — GUI
Requires: pip install python-can
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import time
import logging
import queue
import sys

import can

# ── Protocol constants ────────────────────────────────────────────────────────

PUMP_TYPES = {
    "Air Pump": {"tool_id": 0x180006FF, "ecu_id": 0x1800FF06, "ecu_addr": 0x06},
    "Oil Pump": {"tool_id": 0x180005FF, "ecu_id": 0x1800FF05, "ecu_addr": 0x05},
}
BCAST_ID = 0x1800FFFF

HEARTBEAT_INTERVAL = 0.101
HEARTBEAT_COUNT    = 60        # up to ~6 s; stops early on ECU response
ECU_WAKEUP_TIMEOUT = 3.0
PAYLOAD_BYTES      = 6
ERASE_TIMEOUT      = 5.0
PROG_TIMEOUT       = 5.0
ACK_TIMEOUT        = 1.0
LAST_FRAME_TIMEOUT = 1.0


# ── Protocol helpers ──────────────────────────────────────────────────────────

def xor8(data):
    r = 0
    for b in data[:7]:
        r ^= b
    return r

def make_frame(b0, payload):
    raw = bytes([b0]) + bytes(payload)
    return raw + bytes([xor8(raw)])

def verify_frame(data):
    return len(data) == 8 and xor8(data) == data[7]


# ── Hex loader ────────────────────────────────────────────────────────────────

ECU_FLASH_BASE = 0x003E8000
BLOCK_ID_BASE  = ECU_FLASH_BASE + 6 * 0x2000  # 0x003F4000
ADDR_STEP      = 0x2000
N_SLOTS        = (BLOCK_ID_BASE - ECU_FLASH_BASE) // ADDR_STEP  # 6

def load_hex(path):
    """
    Parse Intel HEX into address-contiguous segments.
    Each segment = one contiguous run of records (gap or backward jump → new segment).
    The CRC segment (bc==4, exactly 4 bytes at crc_addr) is extracted separately.
    Returns: crc_bytes, crc_addr, base_addr, segments[(start_addr, data), ...]
    """
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line.startswith(':'):
                continue
            bc   = int(line[1:3], 16)
            addr = int(line[3:7], 16)
            rt   = int(line[7:9], 16)
            data = bytes.fromhex(line[9:9 + bc * 2])
            records.append((bc, addr, rt, data))

    # First pass: find crc_addr and base_addr
    ela = 0
    crc_addr  = None
    base_addr = None
    for bc, addr, rt, data in records:
        if rt == 4:
            ela = int.from_bytes(data, "big") << 16
        elif rt == 0:
            if bc == 4:
                crc_addr = ela | addr
            if base_addr is None and bc > 4:
                base_addr = ela | addr

    if crc_addr is None:
        raise ValueError("No 4-byte CRC record found in hex file")
    if base_addr is None:
        raise ValueError("No data records found in hex file")

    # Second pass: build address→byte map (overlapping records: last write wins)
    addr_map = {}
    ela = 0
    for bc, addr, rt, data in records:
        if rt == 4:
            ela = int.from_bytes(data, "big") << 16
            continue
        if rt == 1:
            break
        if rt != 0:
            continue
        full_addr = ela | addr
        for i, byte in enumerate(data):
            addr_map[full_addr + i] = byte

    # Extract truly contiguous address ranges as segments
    all_segs = []
    if addr_map:
        sorted_addrs = sorted(addr_map.keys())
        seg_start = sorted_addrs[0]
        prev_addr = sorted_addrs[0]
        for a in sorted_addrs[1:]:
            if a > prev_addr + 1:
                seg_data = bytes(addr_map[x] for x in range(seg_start, prev_addr + 1))
                all_segs.append((seg_start, seg_data))
                seg_start = a
            prev_addr = a
        seg_data = bytes(addr_map[x] for x in range(seg_start, prev_addr + 1))
        all_segs.append((seg_start, seg_data))

    # Separate CRC segment from firmware segments
    crc_bytes = None
    fw_segs   = []
    for seg_addr, seg_data in all_segs:
        if seg_addr == crc_addr and len(seg_data) == 4:
            crc_bytes = seg_data
        else:
            fw_segs.append((seg_addr, seg_data))

    if crc_bytes is None:
        raise ValueError(f"CRC segment not found at 0x{crc_addr:08X}")

    return crc_bytes, crc_addr, base_addr, fw_segs


# ── Block builder ─────────────────────────────────────────────────────────────

def split_at_boundaries(segments):
    """
    Split segments at 8KB (ADDR_STEP) flash-erase boundaries relative to
    ECU_FLASH_BASE.  Segments already aligned are returned unchanged.
    """
    result = []
    for seg_addr, seg_data in segments:
        start = seg_addr
        data  = seg_data
        while data:
            next_boundary = ((start - ECU_FLASH_BASE) // ADDR_STEP + 1) * ADDR_STEP + ECU_FLASH_BASE
            if next_boundary >= start + len(data):
                result.append((start, data))
                break
            cut = next_boundary - start
            result.append((start, data[:cut]))
            start = next_boundary
            data  = data[cut:]
    return result


def build_blocks(segments, log_fn=None):
    """
    One block per hex segment (after 8KB-boundary splitting).
    Block-id formula: b_id = N_SLOTS + 1 - slot_i; last block always id=1.
    """
    segments = split_at_boundaries(segments)
    blocks = []
    total  = len(segments)
    for i, (seg_addr, seg_data) in enumerate(segments):
        is_last = (i == total - 1)
        if is_last:
            b_id = 1
        else:
            end_addr = seg_addr + len(seg_data) - 1
            slot_i   = (end_addr - ECU_FLASH_BASE) // ADDR_STEP
            b_id     = N_SLOTS + 1 - slot_i
        if log_fn:
            log_fn(f"    0x{seg_addr:08X}  {len(seg_data):5d} B  id=0x{b_id:02X}")
        blocks.append({"addr": seg_addr, "size": len(seg_data),
                       "data": bytes(seg_data), "block_id": b_id})
    return blocks

def addr_to_04_payload(full_addr, size):
    return bytes([
        (full_addr >> 24) & 0xFF,
        (full_addr >> 16) & 0xFF,
        (full_addr >>  8) & 0xFF,
        (full_addr      ) & 0xFF,
        (size      >>  8) & 0xFF,
         size             & 0xFF,
    ])


# ── Flash worker (runs in background thread) ──────────────────────────────────

class FlashWorker:
    def __init__(self, interface, channel, bitrate, hex_path, log_q, progress_q,
                 tool_id, ecu_id, ecu_addr):
        self.interface  = interface
        self.channel    = channel
        self.bitrate    = bitrate
        self.hex_path   = hex_path
        self.log_q      = log_q      # queue for log messages (str)
        self.tool_id    = tool_id
        self.ecu_id     = ecu_id
        self.ecu_addr   = ecu_addr   # low byte of ecu_id, used in broadcast frame
        self.progress_q = progress_q # queue for progress (0.0–1.0)
        self.bus        = None
        self.abort      = False

    def log(self, msg):
        self.log_q.put(msg)

    def progress(self, val):
        self.progress_q.put(val)  # negative = failure sentinel, pass through as-is

    def send_and_wait(self, data, timeout=ACK_TIMEOUT):
        assert verify_frame(data)
        msg = can.Message(arbitration_id=self.tool_id, data=data, is_extended_id=True)
        self.bus.send(msg)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.abort:
                raise RuntimeError("Aborted by user")
            # Cap recv at 50 ms so the abort flag is checked frequently
            rx = self.bus.recv(timeout=min(0.05, deadline - time.monotonic()))
            if rx and rx.arbitration_id == self.ecu_id and bytes(rx.data) == data:
                return
            if rx and rx.arbitration_id == 0x1800EEEE:
                nak_data = bytes(rx.data)
                self.log(f"  ⚠️  ECU NAK (0x1800EEEE): {nak_data.hex().upper()}")
                raise RuntimeError(
                    f"ECU rejected frame — address incompatible with current firmware.\n"
                    f"  Sent   : {data.hex().upper()}\n"
                    f"  ECU NAK: {nak_data.hex().upper()}\n"
                    f"  Likely cause: hex file base address differs from firmware in ECU.\n"
                    f"  Solution: use the correct hex file for this ECU version."
                )
        raise RuntimeError(f"No ACK for {data.hex().upper()}")

    def run(self):
        try:
            # ── Parse hex ────────────────────────────────────────────────────
            self.log("Loading hex file...")
            self.log(f"  Tool ID  : 0x{self.tool_id:08X}  ECU ID: 0x{self.ecu_id:08X}")
            crc_bytes, crc_addr, base_addr, segments = load_hex(self.hex_path)
            crc_int = int.from_bytes(crc_bytes, "big")
            firmware_size = sum(len(d) for _, d in segments)
            self.log(f"  Firmware : {firmware_size:,} bytes  ({len(segments)} segment(s))")
            self.log(f"  Base addr: 0x{base_addr:08X}")
            self.log(f"  CRC      : 0x{crc_int:08X}")
            self.log(f"  CRC addr : 0x{crc_addr:08X}")

            self.log(f"  Blocks:")
            blocks = build_blocks(segments, log_fn=self.log)

            total_frames = sum(
                -(-b["size"] // PAYLOAD_BYTES) for b in blocks
            )

            # ── Open CAN ─────────────────────────────────────────────────────
            self.log(f"\nOpening CAN: {self.interface} / {self.channel} @ {self.bitrate} bps")
            try:
                self.bus = can.interface.Bus(
                    interface=self.interface,
                    channel=self.channel,
                    bitrate=self.bitrate,
                )
            except Exception as e:
                hint = ""
                msg  = str(e).lower()
                if "invalid" in msg or "handle" in msg:
                    hint = (
                        "\n  Hint: Channel not found — use '🔍 Detect' button to find"
                        " your PCAN device,\n  or check that PCAN-USB is plugged in"
                        " and the Peak driver is installed."
                    )
                elif "access" in msg or "permission" in msg:
                    hint = "\n  Hint: Permission denied — try running as Administrator (Windows) or check udev rules (Linux)."
                elif "bitrate" in msg or "baud" in msg:
                    hint = "\n  Hint: Bitrate mismatch — verify the correct bitrate is selected."
                raise RuntimeError(f"Cannot open CAN bus: {e}{hint}") from None
            self.log("  CAN bus open ✓")

            # ── Phase 1: Keepalive ────────────────────────────────────────────
            # Step 1a: Send "enter bootloader" broadcast so a live (running) ECU
            # reboots into its bootloader without needing a power cycle.
            # Broadcast frame: FF 02 <ecu_addr> 00 00 00 00 <XOR>
            # ECU ACKs with:   FF 82 <ecu_addr> 00 00 00 00 <XOR>  (bit7 of byte1 set)
            bcast_pl  = bytes([0x02, self.ecu_addr, 0x00, 0x00, 0x00, 0x00])
            bcast_raw = bytes([0xFF]) + bcast_pl
            bcast_xor = 0
            for b in bcast_raw:
                bcast_xor ^= b
            bcast_frame = bcast_raw + bytes([bcast_xor])
            bcast_msg   = can.Message(arbitration_id=BCAST_ID, data=bcast_frame,
                                      is_extended_id=True)

            self.log("\n[1/5] Keepalive — waking ECU...")
            self.log(f"  Sending 'enter bootloader' broadcast on 0x{BCAST_ID:08X}:")
            self.log(f"    {bcast_frame.hex().upper()}")
            self.bus.send(bcast_msg)

            # Wait up to 500 ms for ECU broadcast ACK
            bcast_acked = False
            deadline = time.monotonic() + 0.5
            while time.monotonic() < deadline:
                rx = self.bus.recv(timeout=0.05)
                if rx and rx.arbitration_id == self.ecu_id:
                    rx_data = bytes(rx.data)
                    if rx_data[0] == 0xFF and rx_data[1] == 0x82:
                        self.log(f"  Broadcast ACK ✓  ({rx_data.hex().upper()})")
                        bcast_acked = True
                        break

            if bcast_acked:
                self.log("  ECU is rebooting to bootloader — waiting ~300 ms...")
                time.sleep(0.3)
            else:
                self.log("  No broadcast ACK (ECU may already be in bootloader)")

            # Step 1b: Heartbeat loop
            # Heartbeat byte[2] encodes the expected base address so the ECU
            # unlocks the correct flash region.
            # Formula: byte = (BLOCK_ID_BASE - base_addr) / 8KB + 1
            #   base=0x3E8000 → byte=7 → frame 00 00 07 00 00 00 00 07  (VER3)
            #   base=0x3EA000 → byte=6 → frame 00 00 06 00 00 00 00 06  (VER2)
            hb_byte = (BLOCK_ID_BASE - base_addr) // 0x2000 + 1
            hb_data = make_frame(0x00, bytes([0x00, hb_byte, 0x00, 0x00, 0x00, 0x00]))
            hb_msg  = can.Message(arbitration_id=self.tool_id, data=hb_data, is_extended_id=True)

            self.log(f"  Heartbeat: 0x{hb_byte:02X}  (base 0x{base_addr:08X})")
            self.log(f"  Waiting up to {HEARTBEAT_COUNT * HEARTBEAT_INTERVAL:.0f} s ...")

            ecu_woke = False
            hb_sent  = 0
            for i in range(HEARTBEAT_COUNT):
                if self.abort:
                    raise RuntimeError("Aborted")
                self.bus.send(hb_msg)
                hb_sent += 1
                self.progress(0.01 * i / HEARTBEAT_COUNT)
                rx = self.bus.recv(timeout=0.08)
                if rx and rx.arbitration_id == self.ecu_id:
                    elapsed = hb_sent * HEARTBEAT_INTERVAL
                    mode = "live ECU → rebooted to bootloader" if bcast_acked else "bootloader / cold-start"
                    self.log(f"  ECU responded ✓  ({bytes(rx.data).hex().upper()})")
                    self.log(f"  Mode: {mode}  (after {hb_sent} heartbeats, ~{elapsed:.1f} s)")
                    ecu_woke = True
                    break
                time.sleep(max(0, HEARTBEAT_INTERVAL - 0.08))

            if not ecu_woke:
                deadline = time.monotonic() + ECU_WAKEUP_TIMEOUT
                while time.monotonic() < deadline:
                    if self.abort:
                        raise RuntimeError("Aborted")
                    rx = self.bus.recv(timeout=0.2)
                    if rx and rx.arbitration_id == self.ecu_id:
                        self.log(f"  ECU responded ✓  ({bytes(rx.data).hex().upper()})")
                        ecu_woke = True
                        break

            if not ecu_woke:
                raise RuntimeError(
                    "ECU did not respond to keepalive.\n"
                    "  • For cold-start: power on ECU while tool is running\n"
                    "  • For live flash : ECU app must be running before clicking Flash"
                )

            # ── Phase 2: Flash blocks ─────────────────────────────────────────
            self.log(f"\n[2/5] Flashing {len(blocks)} blocks...")
            frames_done = 0

            for blk_idx, block in enumerate(blocks):
                if self.abort:
                    raise RuntimeError("Aborted")
                self.log(f"  Block {blk_idx+1}/{len(blocks)}  "
                         f"0x{block['addr']:08X}  {block['size']} B  "
                         f"id=0x{block['block_id']:02X}")

                # 04 init
                init_pl = addr_to_04_payload(block["addr"], block["size"])
                self.send_and_wait(make_frame(0x04, init_pl), timeout=ERASE_TIMEOUT)
                self.log(f"    Erase ACK ✓")

                # data frames
                toggle  = 0x01
                data    = block["data"]
                n       = -(-block["size"] // PAYLOAD_BYTES)
                offset  = 0
                chunk   = b""

                for fi in range(n):
                    if self.abort:
                        raise RuntimeError("Aborted")
                    chunk = data[offset:offset + PAYLOAD_BYTES]
                    if len(chunk) < PAYLOAD_BYTES:
                        chunk = chunk.ljust(PAYLOAD_BYTES, b'\xFF')
                    is_last = (fi == n - 1)
                    t = LAST_FRAME_TIMEOUT if is_last else ACK_TIMEOUT
                    self.send_and_wait(make_frame(toggle, chunk), timeout=t)
                    toggle = 0x02 if toggle == 0x01 else 0x01
                    offset += PAYLOAD_BYTES
                    frames_done += 1
                    self.progress(0.05 + 0.85 * frames_done / total_frames)

                # end-of-block
                eob_pl = bytes([0x00, block["block_id"]]) + bytes(chunk[2:6])
                self.send_and_wait(make_frame(0x00, eob_pl))
                self.log(f"    Block done ✓")

                # Re-arm: send heartbeats between blocks so ECU is ready for next erase
                if blk_idx < len(blocks) - 1:
                    for _ in range(5):
                        self.bus.send(hb_msg)
                        rx = self.bus.recv(timeout=0.05)
                        if rx and rx.arbitration_id == self.ecu_id:
                            break
                        time.sleep(0.05)

            # ── Phase 3: Program ──────────────────────────────────────────────
            self.log("\n[3/5] Program command (writing CRC to NVM)...")
            prog_pl = addr_to_04_payload(crc_addr, 4)
            self.send_and_wait(make_frame(0x04, prog_pl), timeout=PROG_TIMEOUT)
            self.log("  Program ACK ✓")
            self.progress(0.93)

            # ── Phase 4: Verify ───────────────────────────────────────────────
            self.log("\n[4/5] Verify...")
            crc_pl = bytes([0x00]) + crc_bytes[1:4] + bytes([0xFF, 0xFF])
            self.send_and_wait(make_frame(0x01, crc_pl))
            self.log("  Verify ACK ✓")
            self.progress(0.96)

            # ── Phase 5: Close ────────────────────────────────────────────────
            self.log("\n[5/5] Close session...")
            self.send_and_wait(make_frame(0x03, crc_pl), timeout=0.5)
            self.log("  Close ACK ✓")
            self.progress(0.99)

            # Broadcast
            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline:
                rx = self.bus.recv(timeout=0.2)
                if rx and rx.arbitration_id == BCAST_ID:
                    self.log(f"  Broadcast: {bytes(rx.data).hex().upper()} ✓")
                    break

            self.progress(1.0)
            self.log("\n✅  FLASH COMPLETE!")

        except Exception as e:
            self.log(f"\n❌  ERROR: {e}")
        finally:
            self.progress(-1)   # always signal UI to re-enable Flash button
            if self.bus:
                self.bus.shutdown()


# ── GUI ───────────────────────────────────────────────────────────────────────

INTERFACES = ["pcan", "socketcan", "kvaser", "vector", "ixxat", "usb2can", "virtual"]

PCAN_CHANNELS = [
    "PCAN_USBBUS1", "PCAN_USBBUS2", "PCAN_USBBUS3", "PCAN_USBBUS4",
    "PCAN_PCIBUS1", "PCAN_PCIBUS2",
]
SOCKETCAN_CHANNELS = ["can0", "can1", "vcan0"]
KVASER_CHANNELS    = ["0", "1", "2"]
VECTOR_CHANNELS    = ["0", "1", "2"]
DEFAULT_CHANNELS   = {
    "pcan":      PCAN_CHANNELS,
    "socketcan": SOCKETCAN_CHANNELS,
    "kvaser":    KVASER_CHANNELS,
    "vector":    VECTOR_CHANNELS,
    "ixxat":     ["0", "1"],
    "usb2can":   ["COM3", "COM4", "/dev/ttyUSB0"],
    "virtual":   ["0"],
}

BITRATES = ["125000", "250000", "500000", "1000000"]


def detect_pcan_channels():
    found = []
    try:
        import can
        for ch in ["PCAN_USBBUS1","PCAN_USBBUS2","PCAN_USBBUS3","PCAN_USBBUS4",
                   "PCAN_USBBUS5","PCAN_USBBUS6","PCAN_USBBUS7","PCAN_USBBUS8"]:
            try:
                bus = can.interface.Bus(interface="pcan", channel=ch, bitrate=500_000)
                bus.shutdown()
                found.append(ch)
            except Exception:
                pass
    except Exception:
        pass
    return found


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ECU Flash Tool")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        self.worker    = None
        self.log_q     = queue.Queue()
        self.prog_q    = queue.Queue()
        self._build_ui()
        self._poll()

    # ── UI build ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        PAD  = dict(padx=12, pady=6)
        CPAD = dict(padx=12, pady=3)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel",      background="#1e1e2e", foreground="#cdd6f4",
                        font=("Segoe UI", 10))
        style.configure("TFrame",      background="#1e1e2e")
        style.configure("TLabelframe", background="#1e1e2e", foreground="#89b4fa",
                        font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background="#1e1e2e", foreground="#89b4fa")
        style.configure("TButton",     font=("Segoe UI", 10, "bold"),
                        background="#313244", foreground="#cdd6f4")
        style.map("TButton",
                  background=[("active", "#45475a"), ("disabled", "#181825")],
                  foreground=[("disabled", "#6c7086")])
        style.configure("Flash.TButton", background="#89b4fa", foreground="#1e1e2e",
                        font=("Segoe UI", 11, "bold"))
        style.map("Flash.TButton",
                  background=[("active", "#b4befe"), ("disabled", "#313244")],
                  foreground=[("disabled", "#6c7086")])
        style.configure("TCombobox",   fieldbackground="#313244", background="#313244",
                        foreground="#cdd6f4", selectbackground="#45475a")
        style.configure("TEntry",      fieldbackground="#313244", foreground="#cdd6f4",
                        insertcolor="#cdd6f4")
        style.configure("green.Horizontal.TProgressbar",
                        troughcolor="#313244", background="#a6e3a1", thickness=18)
        style.configure("red.Horizontal.TProgressbar",
                        troughcolor="#313244", background="#f38ba8", thickness=18)

        root = ttk.Frame(self, padding=16)
        root.pack(fill="both", expand=True)

        # ── Pump type ─────────────────────────────────────────────────────────
        pg = ttk.LabelFrame(root, text=" Pump Type ", padding=10)
        pg.pack(fill="x", **PAD)

        self.pump_var = tk.StringVar(value="Air Pump")
        for name in PUMP_TYPES:
            ttk.Radiobutton(
                pg, text=name, variable=self.pump_var, value=name,
                style="TRadiobutton",
            ).pack(side="left", padx=16)

        style.configure("TRadiobutton", background="#1e1e2e", foreground="#cdd6f4",
                        font=("Segoe UI", 10))
        style.map("TRadiobutton",
                  background=[("active", "#1e1e2e")],
                  foreground=[("active", "#89b4fa")])

        # ── Hex file ──────────────────────────────────────────────────────────
        fg = ttk.LabelFrame(root, text=" Firmware File ", padding=10)
        fg.pack(fill="x", **PAD)

        self.hex_var = tk.StringVar()
        ttk.Entry(fg, textvariable=self.hex_var, width=52,
                  font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        ttk.Button(fg, text="Browse…", command=self._browse).pack(side="left")

        # ── CAN settings ──────────────────────────────────────────────────────
        cg = ttk.LabelFrame(root, text=" CAN Settings ", padding=10)
        cg.pack(fill="x", **PAD)

        row1 = ttk.Frame(cg)
        row1.pack(fill="x", pady=(0, 4))

        ttk.Label(row1, text="Interface").pack(side="left")
        self.iface_var = tk.StringVar(value="pcan")
        iface_cb = ttk.Combobox(row1, textvariable=self.iface_var,
                                values=INTERFACES, width=14, state="readonly")
        iface_cb.pack(side="left", padx=(6, 24))
        iface_cb.bind("<<ComboboxSelected>>", self._iface_changed)

        ttk.Label(row1, text="Channel").pack(side="left")
        self.chan_var = tk.StringVar(value="PCAN_USBBUS1")
        self.chan_cb  = ttk.Combobox(row1, textvariable=self.chan_var,
                                     values=PCAN_CHANNELS, width=18)
        self.chan_cb.pack(side="left", padx=(6, 6))

        self.detect_btn = ttk.Button(row1, text="🔍 Detect",
                                     command=self._detect_channels, width=10)
        self.detect_btn.pack(side="left", padx=(0, 18))

        ttk.Label(row1, text="Bitrate").pack(side="left")
        self.baud_var = tk.StringVar(value="250000")
        ttk.Combobox(row1, textvariable=self.baud_var,
                     values=BITRATES, width=10, state="readonly").pack(side="left", padx=6)

        # ── Flash button + progress ───────────────────────────────────────────
        bg = ttk.Frame(root)
        bg.pack(fill="x", **CPAD)

        self.flash_btn = ttk.Button(bg, text="⚡  Flash ECU", style="Flash.TButton",
                                    command=self._start_flash, width=18)
        self.flash_btn.pack(side="left")

        self.abort_btn = ttk.Button(bg, text="■  Stop", command=self._abort,
                                    state="disabled", width=9)
        self.abort_btn.pack(side="left", padx=8)

        self.status_lbl = ttk.Label(bg, text="Ready", foreground="#a6e3a1",
                                    font=("Segoe UI", 10, "italic"))
        self.status_lbl.pack(side="left", padx=12)

        self.prog_var  = tk.DoubleVar(value=0)
        self.prog_bar  = ttk.Progressbar(root, variable=self.prog_var,
                                         maximum=100,
                                         style="green.Horizontal.TProgressbar",
                                         length=520)
        self.prog_bar.pack(fill="x", **CPAD)

        # ── Log console ───────────────────────────────────────────────────────
        lg = ttk.LabelFrame(root, text=" Log ", padding=6)
        lg.pack(fill="both", expand=True, **PAD)

        self.console = scrolledtext.ScrolledText(
            lg, height=16, width=72,
            bg="#181825", fg="#cdd6f4",
            font=("Consolas", 9),
            insertbackground="#cdd6f4",
            state="disabled",
            relief="flat",
        )
        self.console.pack(fill="both", expand=True)

        self.console.tag_config("ok",    foreground="#a6e3a1")
        self.console.tag_config("err",   foreground="#f38ba8")
        self.console.tag_config("info",  foreground="#89dceb")
        self.console.tag_config("dim",   foreground="#6c7086")

        bot = ttk.Frame(root)
        bot.pack(fill="x", padx=12, pady=(0, 4))
        ttk.Button(bot, text="Clear log", command=self._clear_log).pack(side="left")
        ttk.Button(bot, text="Exit", command=self._exit,
                   style="TButton").pack(side="right")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select firmware hex file",
            filetypes=[("Intel HEX", "*.hex"), ("All files", "*.*")],
        )
        if path:
            self.hex_var.set(path)

    def _iface_changed(self, _=None):
        iface = self.iface_var.get()
        channels = DEFAULT_CHANNELS.get(iface, ["0"])
        self.chan_cb["values"] = channels
        self.chan_var.set(channels[0])
        if iface == "pcan":
            self.detect_btn.pack(side="left", padx=(0, 18))
        else:
            self.detect_btn.pack_forget()

    def _detect_channels(self):
        self.detect_btn.configure(state="disabled", text="Scanning…")
        self.status_lbl.configure(text="Detecting…", foreground="#fab387")
        self.update_idletasks()

        def _scan():
            found = detect_pcan_channels()
            self.after(0, lambda: self._on_detect_done(found))

        threading.Thread(target=_scan, daemon=True).start()

    def _on_detect_done(self, found):
        self.detect_btn.configure(state="normal", text="🔍 Detect")
        if found:
            self.chan_cb["values"] = found
            self.chan_var.set(found[0])
            self.status_lbl.configure(
                text=f"Found: {', '.join(found)}", foreground="#a6e3a1")
            self._log(f"Detected PCAN channels: {', '.join(found)}")
        else:
            self.status_lbl.configure(
                text="No PCAN device found", foreground="#f38ba8")
            self._log(
                "❌  No PCAN device detected.\n"
                "    • Make sure the PCAN-USB is plugged in\n"
                "    • Windows: install PCAN driver from peak-system.com\n"
                "    • Linux:   sudo modprobe peak_usb  (then use socketcan/can0)"
            )

    def _clear_log(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def _log(self, msg):
        self.console.configure(state="normal")
        if msg.startswith("✅"):
            tag = "ok"
        elif msg.startswith("❌") or "ERROR" in msg or "FAILED" in msg:
            tag = "err"
        elif msg.startswith("[") or msg.startswith("\n["):
            tag = "info"
        elif msg.strip().startswith("0x") or "id=0x" in msg:
            tag = "dim"
        else:
            tag = None
        self.console.insert("end", msg + "\n", tag)
        self.console.see("end")
        self.console.configure(state="disabled")

    def _set_running(self, running: bool):
        self.flash_btn.configure(state="disabled" if running else "normal")
        self.abort_btn.configure(state="normal"   if running else "disabled")

    # ── Flash start/stop ──────────────────────────────────────────────────────

    def _start_flash(self):
        path = self.hex_var.get().strip()
        if not path:
            self._log("❌  ERROR: No hex file selected")
            return

        pump = PUMP_TYPES[self.pump_var.get()]
        self.prog_var.set(0)
        self.prog_bar.configure(style="green.Horizontal.TProgressbar")
        self.status_lbl.configure(text="Flashing…", foreground="#fab387")
        self._set_running(True)
        self._clear_log()

        self.worker = FlashWorker(
            interface=self.iface_var.get(),
            channel=self.chan_var.get(),
            bitrate=int(self.baud_var.get()),
            hex_path=path,
            log_q=self.log_q,
            progress_q=self.prog_q,
            tool_id=pump["tool_id"],
            ecu_id=pump["ecu_id"],
            ecu_addr=pump["ecu_addr"],
        )
        threading.Thread(target=self.worker.run, daemon=True).start()

    def _abort(self):
        if self.worker:
            self.worker.abort = True
        self.abort_btn.configure(state="disabled", text="Stopping…")
        self.status_lbl.configure(text="Stopping…", foreground="#f38ba8")
        self.after(3000, self._force_reset_if_stopping)

    def _exit(self):
        if self.worker:
            self.worker.abort = True
        self.destroy()

    def _reset_progress(self):
        self.prog_var.set(0)
        self.prog_bar.configure(style="green.Horizontal.TProgressbar")
        self.status_lbl.configure(text="Ready", foreground="#a6e3a1")

    def _force_reset_if_stopping(self):
        if self.status_lbl.cget("text") in ("Stopping…", "Aborting…"):
            self.abort_btn.configure(text="■  Stop")
            self._set_running(False)
            self._reset_progress()

    # ── Poll queues ───────────────────────────────────────────────────────────

    def _poll(self):
        while not self.log_q.empty():
            self._log(self.log_q.get_nowait())

        while not self.prog_q.empty():
            val = self.prog_q.get_nowait()
            if val < 0:
                if self.status_lbl.cget("text") == "Done ✓":
                    continue
                self.prog_bar.configure(style="red.Horizontal.TProgressbar")
                self.prog_var.set(100)
                was_aborted = self.worker and self.worker.abort
                self.status_lbl.configure(
                    text="Stopped" if was_aborted else "Failed",
                    foreground="#f38ba8",
                )
                self.abort_btn.configure(text="■  Stop")
                self._set_running(False)
                self.after(2000, self._reset_progress)
            else:
                self.prog_var.set(min(val, 1.0) * 100)
                if val >= 1.0:
                    self.status_lbl.configure(text="Done ✓", foreground="#a6e3a1")
                    self._set_running(False)

        self.after(80, self._poll)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
