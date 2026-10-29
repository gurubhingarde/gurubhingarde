"""ISO-TP (ISO 15765-2) over CAN / CAN-FD, using python-can.

Optional: only imported when the user selects a real CAN interface. Install:
    pip install python-can can-isotp
Supports classic CAN (8-byte) and CAN-FD (up to 64-byte) frames. Addressing
defaults mirror the original tool: tester SA 0xF9, extended 29-bit priority
0x18 — but request/response CAN IDs are set explicitly here.
"""
from __future__ import annotations

import time

from .base import Transport, TransportError


def _solve(bitrate: int, f_clock: int, tseg1_max: int, tseg2_max: int,
           sample_point: float = 0.8):
    """Find (brp, tseg1, tseg2) for `bitrate` from `f_clock`. Returns None if no
    exact division is found."""
    for brp in range(1, 65):
        total = f_clock / (brp * bitrate)
        if abs(total - round(total)) > 1e-9:
            continue
        total = round(total)
        if total < 4:
            continue
        tseg1 = round(total * sample_point) - 1
        tseg2 = total - 1 - tseg1
        if 1 <= tseg1 <= tseg1_max and 1 <= tseg2 <= tseg2_max:
            return brp, tseg1, tseg2
    return None


def make_bus(bustype: str, channel: str, is_fd: bool, bitrate: int,
             data_bitrate: int, f_clock: int = 80_000_000):
    """Open a python-can bus, handling PCAN CAN-FD bit-timing (which needs full
    timing parameters, not just data_bitrate)."""
    import can

    if is_fd and bustype == "pcan":
        try:
            from can import BitTimingFd
            nom = _solve(bitrate, f_clock, 256, 128)
            dat = _solve(data_bitrate, f_clock, 32, 16)
            if nom and dat:
                timing = BitTimingFd(
                    f_clock=f_clock,
                    nom_brp=nom[0], nom_tseg1=nom[1], nom_tseg2=nom[2], nom_sjw=min(nom[2], 16),
                    data_brp=dat[0], data_tseg1=dat[1], data_tseg2=dat[2], data_sjw=min(dat[2], 8),
                )
                return can.Bus(interface="pcan", channel=channel, fd=True, timing=timing)
        except Exception:
            pass  # fall through to the simple path below

    kwargs = dict(interface=bustype, channel=channel, fd=is_fd, bitrate=bitrate)
    if is_fd:
        kwargs["data_bitrate"] = data_bitrate
    return can.Bus(**kwargs)


class CanIsoTpTransport(Transport):
    name = "CAN / CAN-FD (ISO-TP)"

    def __init__(self, channel: str, bustype: str = "pcan",
                 req_id: int = 0x18DA10F9, resp_id: int = 0x18DAF910,
                 is_fd: bool = True, bitrate: int = 500000,
                 data_bitrate: int = 2000000, extended_id: bool = True,
                 padding: int = 0xFF, log=print):  # 0xFF padding, matching the supplier tool
        self.channel = channel
        self.bustype = bustype
        self.req_id = req_id
        self.resp_id = resp_id
        self.is_fd = is_fd
        self.bitrate = bitrate
        self.data_bitrate = data_bitrate
        self.extended_id = extended_id
        self.padding = padding
        self._log = log
        self._bus = None
        self._stack = None

    def open(self):
        try:
            import can
            import isotp
        except ImportError as e:
            raise TransportError(
                "python-can / can-isotp not installed: "
                "pip install python-can can-isotp") from e

        try:
            self._bus = make_bus(self.bustype, self.channel, self.is_fd,
                                  self.bitrate, self.data_bitrate)
        except Exception as e:
            raise TransportError(
                f"could not open {self.bustype}:{self.channel} ({e}). "
                "If PCAN: close PCAN-View / the supplier tool (the channel may be "
                "busy), check the channel name, or untick CAN-FD to try classic CAN."
            ) from e

        addr = isotp.Address(isotp.AddressingMode.Normal_29bits
                             if self.extended_id else isotp.AddressingMode.Normal_11bits,
                             txid=self.req_id, rxid=self.resp_id)
        params = {
            "tx_padding": self.padding,
            "blocking_send": True,
            "can_fd": self.is_fd,
            "tx_data_length": 64 if self.is_fd else 8,
        }
        self._stack = isotp.NotifierBasedCanStack(self._bus, address=addr, params=params) \
            if hasattr(isotp, "NotifierBasedCanStack") else \
            isotp.CanStack(self._bus, address=addr, params=params)
        self._log(f"[can] open {self.bustype}:{self.channel} "
                  f"fd={self.is_fd} tx=0x{self.req_id:X} rx=0x{self.resp_id:X}")

    def close(self):
        try:
            if self._stack and hasattr(self._stack, "stop"):
                self._stack.stop()
            if self._bus:
                self._bus.shutdown()
        finally:
            self._bus = self._stack = None

    def send(self, payload: bytes):
        if not self._stack:
            raise TransportError("transport not open")
        self._stack.send(bytes(payload))

    def recv(self, timeout: float = 2.0) -> bytes:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if hasattr(self._stack, "process"):
                self._stack.process()
            if self._stack.available():
                return bytes(self._stack.recv())
            time.sleep(0.005)
        raise TransportError(f"ISO-TP receive timeout ({timeout}s)")
