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


# Canonical PEAK FD bit-timings at f_clock = 80 MHz (nominal SP ~81%, data ~80%).
# These are the per-parameter kwargs the python-can PCAN backend expects for FD.
PCAN_FD_TIMINGS = {
    # (nominal, data): params
    (500_000, 2_000_000): dict(f_clock_mhz=80, nom_brp=10, nom_tseg1=12, nom_tseg2=3,
                               nom_sjw=1, data_brp=4, data_tseg1=7, data_tseg2=2, data_sjw=1),
    (500_000, 4_000_000): dict(f_clock_mhz=80, nom_brp=10, nom_tseg1=12, nom_tseg2=3,
                               nom_sjw=1, data_brp=2, data_tseg1=7, data_tseg2=2, data_sjw=1),
    (500_000, 1_000_000): dict(f_clock_mhz=80, nom_brp=10, nom_tseg1=12, nom_tseg2=3,
                               nom_sjw=1, data_brp=8, data_tseg1=7, data_tseg2=2, data_sjw=1),
    (250_000, 2_000_000): dict(f_clock_mhz=80, nom_brp=20, nom_tseg1=12, nom_tseg2=3,
                               nom_sjw=1, data_brp=4, data_tseg1=7, data_tseg2=2, data_sjw=1),
    (1_000_000, 2_000_000): dict(f_clock_mhz=80, nom_brp=5, nom_tseg1=12, nom_tseg2=3,
                                 nom_sjw=1, data_brp=4, data_tseg1=7, data_tseg2=2, data_sjw=1),
    (1_000_000, 4_000_000): dict(f_clock_mhz=80, nom_brp=5, nom_tseg1=12, nom_tseg2=3,
                                 nom_sjw=1, data_brp=2, data_tseg1=7, data_tseg2=2, data_sjw=1),
}


def pcan_fd_params(bitrate: int, data_bitrate: int) -> dict:
    """Canonical PEAK FD timing kwargs for (bitrate, data_bitrate). Falls back to
    the 500k/2M timing if the exact pair is not tabulated."""
    return PCAN_FD_TIMINGS.get((bitrate, data_bitrate),
                               PCAN_FD_TIMINGS[(500_000, 2_000_000)])


def make_bus(bustype: str, channel: str, is_fd: bool, bitrate: int,
             data_bitrate: int):
    """Open a python-can bus. PCAN CAN-FD uses the documented per-parameter FD
    timing kwargs (the backend rejects fd=True with only data_bitrate)."""
    import can

    if not is_fd:
        return can.Bus(interface=bustype, channel=channel, bitrate=bitrate)

    if bustype == "pcan":
        return can.Bus(interface="pcan", channel=channel, fd=True,
                        **pcan_fd_params(bitrate, data_bitrate))

    return can.Bus(interface=bustype, channel=channel, fd=True,
                   bitrate=bitrate, data_bitrate=data_bitrate)


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
