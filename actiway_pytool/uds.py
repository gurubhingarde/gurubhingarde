"""UDS (ISO 14229) client + flash-download sequencer.

Reconstruction of ACTIA.clDownloadApp.vDLDll_iExecute_Thread and
ACTIA.Protocol.clDoCPro.StateMachine: the request/response services and the
ordered reprogramming sequence the original tool runs.
"""
from __future__ import annotations

import datetime
import time
from dataclasses import dataclass
from typing import Callable

from . import crypto
from .firmware import ReprogrammingBlock, Segment
from .transport.base import Transport, TransportError

# UDS service IDs
SID_SESSION = 0x10
SID_RESET = 0x11
SID_READ_DID = 0x22
SID_SECURITY = 0x27
SID_REQUEST_DOWNLOAD = 0x34
SID_TRANSFER_DATA = 0x36
SID_TRANSFER_EXIT = 0x37
SID_ROUTINE = 0x31

# session / subfunction constants
SESSION_PROGRAMMING = 0x02
SESSION_EXTENDED = 0x03

NRC_RESPONSE_PENDING = 0x78


class UdsError(Exception):
    def __init__(self, sid: int, nrc: int):
        self.sid, self.nrc = sid, nrc
        super().__init__(f"negative response to SID 0x{sid:02X}: NRC 0x{nrc:02X}")


@dataclass
class FlashConfig:
    """Mirrors the original *.exe.config keys."""
    sec_key: int = 0xFFFF
    programming_session: int = SESSION_PROGRAMMING
    security_level: int = 0x01       # SecurityAccess subfunction for the Simulator
    security_seed_sub: int = 0x03    # CONFIRMED from IL: requestSeed level 3 (27 03)
    security_key_sub: int = 0x04     # CONFIRMED from IL: sendKey level 4 (27 04)
    seed_width: int = 2
    addr_len: int = 4                # bytes for address in RequestDownload
    size_len: int = 4                # bytes for size in RequestDownload
    data_format_id: int = 0x00       # 0x00 = uncompressed; high nibble = compression
    use_lzo: bool = False
    min_block_size_can: int = 0x10
    min_block_size_doip: int = 0x400
    addr_start: int = 0              # mapping range; 0/0 means "use file addresses"
    addr_end: int = 0
    # --- ACTIA two-phase flash parameters (CALIBRATE from a real CAN trace) ---
    dtc_control_off: int = 0x85       # ControlDTCSetting
    comm_control: int = 0x28          # CommunicationControl
    comm_control_sub: int = 0x03      # disableRxAndTx
    comm_control_param: int = 0x03    # CONFIRMED from IL: 28 03 03
    jump_to_boot_reset_sub: int = 0x02   # ECUReset keyOffOnReset (CONFIRMED: 11 02 -> 51 02)
    diag_version_did: int = 0xF1F0    # "get diag version" DID (CONFIRMED from IL: 22 F1 F0)
    fingerprint_did: int = 0xF183     # fingerprint DID (CONFIRMED from IL: 2E F1 83 ...)
    erase_routine: int = 0xFF00       # eraseMemory routine id (CONFIRMED: 31 01 FF 00 <zone>)
    checksum_routine: int = 0xFF01    # check-CRC routine (CONFIRMED: 31 01 FF 01 <crc16>)
    zone: int = 0                     # memory zone byte for erase (from mapping)
    crc16_init: int = 0xFFFF          # CRC-16/CCITT init (CALIBRATE)
    tool_id: bytes = b"720001"        # 6-byte tester ID in the fingerprint (CALIBRATE)
    crc: crypto.Crc32Config = None
    aes: crypto.AesConfig = None

    def __post_init__(self):
        if self.crc is None:
            self.crc = crypto.Crc32Config()
        if self.aes is None:
            self.aes = crypto.AesConfig()


class UdsClient:
    def __init__(self, transport: Transport, log: Callable[[str], None] = print,
                 timeout: float = 3.0):
        self.t = transport
        self.log = log
        self.timeout = timeout

    # -- primitive ----------------------------------------------------------
    def request(self, payload: bytes, timeout: float | None = None) -> bytes:
        to = self.timeout if timeout is None else timeout
        self.log(f">> {payload.hex(' ').upper()}")
        resp = self.t.request(bytes(payload), to)
        # handle responsePending (0x78) by waiting for the real answer
        while len(resp) >= 3 and resp[0] == 0x7F and resp[2] == NRC_RESPONSE_PENDING:
            self.log("<< 7F .. 78 (responsePending, waiting)")
            resp = self.t.recv(to)
        self.log(f"<< {resp.hex(' ').upper()}")
        if resp and resp[0] == 0x7F:
            raise UdsError(resp[1] if len(resp) > 1 else 0, resp[2] if len(resp) > 2 else 0)
        return resp

    # -- services -----------------------------------------------------------
    def diagnostic_session(self, session: int) -> bytes:
        return self.request(bytes([SID_SESSION, session]))

    def ecu_reset(self, rtype: int = 0x01) -> bytes:
        return self.request(bytes([SID_RESET, rtype]))

    def read_did(self, did: int) -> bytes:
        resp = self.request(bytes([SID_READ_DID, (did >> 8) & 0xFF, did & 0xFF]))
        return resp[3:]

    def security_access(self, cfg: FlashConfig, seed_sub: int | None = None,
                        key_sub: int | None = None) -> None:
        seed_sub = cfg.security_level if seed_sub is None else seed_sub
        key_sub = (seed_sub + 1) if key_sub is None else key_sub
        resp = self.request(bytes([SID_SECURITY, seed_sub]))
        seed = resp[2:]
        if not any(seed):
            self.log("security: seed already unlocked (all-zero)")
            return
        key = crypto.seed_to_key_bytes(seed, cfg.sec_key, cfg.seed_width)
        self.log(f"security: seed={seed.hex().upper()} -> key={key.hex().upper()}")
        self.request(bytes([SID_SECURITY, key_sub]) + key)

    def request_download(self, addr: int, size: int, cfg: FlashConfig) -> int:
        alf = (cfg.size_len << 4) | cfg.addr_len
        msg = bytes([SID_REQUEST_DOWNLOAD, cfg.data_format_id, alf])
        msg += addr.to_bytes(cfg.addr_len, "big") + size.to_bytes(cfg.size_len, "big")
        resp = self.request(msg)
        # resp: 0x74, lengthFormatId, maxNumberOfBlockLength[...]
        lfid = (resp[1] >> 4) & 0x0F
        max_block = int.from_bytes(resp[2:2 + lfid], "big")
        self.log(f"request_download ok, maxBlockLength={max_block}")
        return max_block

    def transfer_data(self, seq: int, chunk: bytes) -> bytes:
        return self.request(bytes([SID_TRANSFER_DATA, seq & 0xFF]) + chunk)

    def transfer_exit(self) -> bytes:
        return self.request(bytes([SID_TRANSFER_EXIT]))

    def routine_control(self, sub: int, rid: int, data: bytes = b"") -> bytes:
        return self.request(bytes([SID_ROUTINE, sub, (rid >> 8) & 0xFF, rid & 0xFF]) + data)


class FlashSequencer:
    """Runs the full reprogramming sequence for one block."""

    def __init__(self, client: UdsClient, cfg: FlashConfig,
                 progress: Callable[[int, int], None] = lambda done, total: None):
        self.c = client
        self.cfg = cfg
        self.progress = progress

    def run(self, block: ReprogrammingBlock) -> str:
        c, cfg = self.c, self.cfg
        # Clip the image to the selected mapping's address range, like the
        # supplier tool (prevents flashing outside the zone window).
        if cfg.addr_end > cfg.addr_start:
            from .firmware import filter_range
            before = block.total_size
            block = filter_range(block, cfg.addr_start, cfg.addr_end)
            if block.total_size != before:
                c.log(f"clipped image to mapping range "
                      f"0x{cfg.addr_start:08X}-0x{cfg.addr_end:08X}: "
                      f"{before} -> {block.total_size} bytes")
            if block.total_size == 0:
                raise UdsError(SID_REQUEST_DOWNLOAD, 0x31)  # requestOutOfRange
        c.log(f"=== Flashing '{block.name}' ({block.total_size} bytes, "
              f"{len(block.segments)} segment(s)) ===")

        c.log("1) Enter programming session")
        c.diagnostic_session(cfg.programming_session)

        c.log("2) Security access")
        c.security_access(cfg)

        total = block.total_size
        done = 0
        for seg in block.segments:
            data = seg.data
            if cfg.use_lzo:
                try:
                    from . import lzo
                    data = lzo.compress(data)
                    c.log(f"   LZO: {seg.size} -> {len(data)} bytes")
                except Exception as e:
                    c.log(f"   LZO unavailable ({e}); sending uncompressed")

            c.log(f"3) RequestDownload @0x{seg.start_addr:08X} size={len(data)}")
            max_block = c.request_download(seg.start_addr, len(data), cfg)
            # ISO 14229: block length includes the SID+seq overhead (2 bytes)
            payload = max(1, (max_block or 0x402) - 2)

            seq = 1
            for off in range(0, len(data), payload):
                chunk = data[off:off + payload]
                c.transfer_data(seq, chunk)
                seq = (seq % 0xFF) + 1
                done += len(chunk)
                self.progress(done, total)

            c.log("4) RequestTransferExit")
            c.transfer_exit()

        c.log("5) Verify (CRC-32 of image)")
        image = b"".join(s.data for s in block.segments)
        digest = crypto.crc32_hex(image, cfg.crc)
        c.log(f"   image CRC-32 = {digest}")

        c.log("6) ECU reset")
        try:
            c.ecu_reset(0x01)
        except (UdsError, TransportError) as e:
            c.log(f"   reset note: {e}")

        c.log("=== DONE ===")
        return digest

    # ------------------------------------------------------------------
    # ACTIA two-phase flash (app -> jump to boot -> re-auth -> erase -> download)
    # Reconstructed from the supplier tool log + CDownload.dll service IDs.
    # Routine IDs / DIDs marked (CALIBRATE) still need a CAN trace to be exact.
    # ------------------------------------------------------------------
    def run_actia(self, block: ReprogrammingBlock) -> str:
        c, cfg = self.c, self.cfg
        if cfg.addr_end > cfg.addr_start:
            from .firmware import filter_range
            block = filter_range(block, cfg.addr_start, cfg.addr_end)
        c.log(f"=== ACTIA flash '{block.name}' ({block.total_size} bytes, "
              f"{len(block.segments)} segment(s)) ===")

        # --- Phase 1: application ---
        c.log("1) Extended session")
        c.diagnostic_session(SESSION_EXTENDED)
        c.log("2) ControlDTCSetting off")
        c.request(bytes([cfg.dtc_control_off, 0x02]))
        c.log("3) CommunicationControl (28 03 03)")
        c.request(bytes([cfg.comm_control, cfg.comm_control_sub, cfg.comm_control_param]))
        c.log("4) Programming session (application)")
        c.diagnostic_session(cfg.programming_session)
        c.log("5) Security access level 3 (27 03/04)")
        c.security_access(cfg, cfg.security_seed_sub, cfg.security_key_sub)

        # --- Phase 2: jump to boot (reconnect), re-auth in bootloader ---
        c.log("6) Jump to boot (reconnect)")
        try:
            self.c.t.close()
            time.sleep(0.8)
            self.c.t.open()
        except Exception as e:
            c.log(f"   reconnect note: {e}")
        time.sleep(0.5)
        c.log("7) Programming session (bootloader)")
        c.diagnostic_session(cfg.programming_session)
        c.log("8) Security access level 3 (bootloader)")
        c.security_access(cfg, cfg.security_seed_sub, cfg.security_key_sub)

        c.log("9) Get diag version")
        try:
            c.read_did(cfg.diag_version_did)
        except (UdsError, TransportError) as e:
            c.log(f"   diag-version note: {e}")

        c.log("10) Write fingerprint")
        # CONFIRMED from IL (15 bytes): 2E F1 83 <year_hi><year_lo><month><day>
        #   <hour><minute> <6-byte ToolID>
        now = datetime.datetime.now()
        tid = (cfg.tool_id + b"\x00" * 6)[:6]
        fp_bytes = bytes([(now.year >> 8) & 0xFF, now.year & 0xFF, now.month,
                          now.day, now.hour, now.minute]) + tid
        try:
            c.request(bytes([0x2E, (cfg.fingerprint_did >> 8) & 0xFF,
                             cfg.fingerprint_did & 0xFF]) + fp_bytes)
        except (UdsError, TransportError) as e:
            c.log(f"   fingerprint note: {e}")

        # --- Phase 3: erase ---
        c.log(f"11) Launch erase memory (zone {cfg.zone})")
        # CONFIRMED from IL: 31 01 FF 00 <zone byte>
        c.routine_control(0x01, cfg.erase_routine, bytes([cfg.zone & 0xFF]))
        c.log("12) Wait erase (poll routine result)")
        for _ in range(120):
            try:
                r = c.routine_control(0x03, cfg.erase_routine, bytes([cfg.zone & 0xFF]))
                if r and r[-1] == 0x00:       # routineStatus finished
                    break
            except UdsError:
                pass
            time.sleep(0.5)

        # --- Phase 4: download each page-aligned block (matches supplier) ---
        from .firmware import build_download_blocks
        blocks = build_download_blocks(block, align=cfg.min_block_size_doip or 0x400)
        c.log(f"   {len(blocks)} download block(s) after 0x"
              f"{(cfg.min_block_size_doip or 0x400):X} page alignment")
        total = sum(b.size for b in blocks)
        done = 0
        crc_stream = bytearray()
        for seg in blocks:
            data = seg.data
            crc_stream += data
            if cfg.use_lzo:
                try:
                    from . import lzo
                    data = lzo.compress(data)
                except Exception as e:
                    c.log(f"   LZO unavailable ({e}); uncompressed")
            c.log(f"13) Request download @0x{seg.start_addr:08X} size={len(data)}")
            max_block = c.request_download(seg.start_addr, len(data), cfg)
            payload = max(1, (max_block or 0x402) - 2)
            seq = 1
            for off in range(0, len(data), payload):
                c.transfer_data(seq, data[off:off + payload])
                seq = (seq % 0xFF) + 1
                done += min(payload, len(data) - off)
                self.progress(done, total)
            c.log("15) Exit download")
            c.transfer_exit()

        # --- Phase 5: verify + reset ---
        c.log("16) Check CRC (routine)")
        # CONFIRMED from IL: 31 01 FF 01 <crc16 big-endian>, u16 CRC-16/CCITT
        crc16 = crypto.crc16_ccitt(bytes(crc_stream), cfg.crc16_init)
        try:
            c.routine_control(0x01, cfg.checksum_routine, crc16.to_bytes(2, "big"))
        except (UdsError, TransportError) as e:
            c.log(f"   CRC-routine note: {e}")
        c.log(f"   image CRC-16 = {crc16:04X}")
        digest = f"{crc16:04X}"

        c.log("17) ECU reset")
        try:
            c.ecu_reset(0x01)
        except (UdsError, TransportError) as e:
            c.log(f"   reset note: {e}")
        c.log("=== ACTIA flash sequence complete ===")
        return digest
