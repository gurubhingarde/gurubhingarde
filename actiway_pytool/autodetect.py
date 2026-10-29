"""ECU autodetect — replicate the supplier tool's Autodetect sweep.

Observed CAN trace from the real CHActi-ToolSet autodetect:
    ID=0x18DAFFF9 (29-bit)  Data=02 10 02 FF FF FF FF FF
    ID=0x7FF     (11-bit)   Data=02 10 02 FF FF FF FF FF
    ID=0x7DF     (11-bit)   Data=02 10 02 FF FF FF FF FF

i.e. it sends UDS DiagnosticSessionControl(programmingSession) = `10 02` as an
ISO-TP single frame (0xFF padding) to three functional/broadcast IDs, then
listens for any ECU that answers. From a responder's arbitration ID it derives
the ECU's physical request/response IDs for subsequent flashing.
"""
from __future__ import annotations

from dataclasses import dataclass

TESTER_SA = 0xF9                     # from the trace / *.exe.config TOOL_SA
PROBE_PAYLOAD = bytes([0x10, 0x02])  # enter programming session
SINGLE_FRAME = bytes([0x02]) + PROBE_PAYLOAD + b"\xFF" * 5  # 02 10 02 FF FF FF FF FF

# (arbitration id, is_extended)
PROBES = [
    (0x18DAFFF9, True),   # 29-bit normal-fixed functional, TA=FF SA=F9
    (0x7FF, False),       # 11-bit broadcast
    (0x7DF, False),       # 11-bit standard OBD functional
]


@dataclass
class Found:
    resp_id: int
    extended: bool
    ecu_addr: int
    req_id: int            # physical request ID to use for flashing
    phys_resp_id: int      # physical response ID to expect
    first_data: bytes

    def __str__(self):
        w = 8 if self.extended else 3
        return (f"ECU 0x{self.ecu_addr:02X} answered on 0x{self.resp_id:0{w}X} "
                f"-> physical req=0x{self.req_id:0{w}X} resp=0x{self.phys_resp_id:0{w}X} "
                f"[{self.first_data.hex(' ').upper()}]")


def _derive(resp_id: int, extended: bool) -> tuple[int, int, int]:
    """Return (ecu_addr, physical_req_id, physical_resp_id) from a responder ID."""
    if extended:
        # normal-fixed: response = 0x18DA | tester<<8 | ecu ; request swaps TA/SA
        ecu = resp_id & 0xFF
        req = 0x18DA0000 | (ecu << 8) | TESTER_SA
        return ecu, req, resp_id
    # 11-bit: ECUs answer on 0x7E8..0x7EF, physical request is resp-8 (0x7E0..0x7E7)
    if 0x7E8 <= resp_id <= 0x7EF:
        return resp_id & 0x07, resp_id - 8, resp_id
    # unknown 11-bit scheme: best-effort, assume request = resp-8
    return resp_id & 0xFF, resp_id - 8, resp_id


def autodetect_can(bustype: str, channel: str, is_fd: bool = True,
                   bitrate: int = 500000, data_bitrate: int = 2000000,
                   listen: float = 0.3, log=print) -> list[Found]:
    """Send the probe sweep on real hardware and collect responders.

    Uses python-can directly (raw frames), independent of the ISO-TP stack.
    """
    try:
        import can  # noqa: F401
    except ImportError as e:
        raise RuntimeError("python-can not installed: pip install python-can") from e
    import time

    from .transport.can_isotp import make_bus
    try:
        bus = make_bus(bustype, channel, is_fd, bitrate, data_bitrate)
    except Exception as e:
        raise RuntimeError(
            f"could not open {bustype}:{channel} ({e}). If PCAN: close PCAN-View / "
            "the supplier tool (channel busy), verify the channel name, or untick "
            "CAN-FD to try classic CAN.") from e
    found: dict[int, Found] = {}
    try:
        for probe_id, ext in PROBES:
            msg = can.Message(arbitration_id=probe_id, is_extended_id=ext,
                              data=SINGLE_FRAME, is_fd=is_fd)
            log(f"[autodetect] -> 0x{probe_id:X} {SINGLE_FRAME.hex(' ').upper()}")
            try:
                bus.send(msg)
            except Exception as e:
                log(f"[autodetect] send failed on 0x{probe_id:X}: {e}")
                continue
            deadline = time.time() + listen
            while time.time() < deadline:
                rx = bus.recv(timeout=max(0.0, deadline - time.time()))
                if rx is None or rx.arbitration_id == probe_id:
                    continue
                data = bytes(rx.data)
                # accept a positive (50 02) or any UDS response to our probe
                if rx.arbitration_id in found:
                    continue
                ecu, req, presp = _derive(rx.arbitration_id, rx.is_extended_id)
                f = Found(rx.arbitration_id, rx.is_extended_id, ecu, req, presp, data)
                found[rx.arbitration_id] = f
                log(f"[autodetect] <- {f}")
    finally:
        bus.shutdown()
    if not found:
        log("[autodetect] no ECU responded")
    return list(found.values())


def autodetect_sim(sim, log=print) -> list[Found]:
    """Autodetect against the in-process simulator (so the button works with no
    hardware). The simulator answers 10 02, so we report its physical IDs."""
    log(f"[autodetect] -> functional 0x18DAFFF9 {SINGLE_FRAME.hex(' ').upper()}")
    ecu = getattr(sim, "ecu_addr", 0x01)
    resp_id = 0x18DA0000 | (TESTER_SA << 8) | ecu
    f = Found(resp_id, True, ecu, 0x18DA0000 | (ecu << 8) | TESTER_SA, resp_id,
              bytes([0x06, 0x50, 0x02, 0x00, 0x32, 0x01, 0xF4]))
    log(f"[autodetect] <- {f}")
    return [f]
