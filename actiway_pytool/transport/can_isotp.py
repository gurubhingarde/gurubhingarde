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


class CanIsoTpTransport(Transport):
    name = "CAN / CAN-FD (ISO-TP)"

    def __init__(self, channel: str, bustype: str = "pcan",
                 req_id: int = 0x18DA10F9, resp_id: int = 0x18DAF910,
                 is_fd: bool = True, bitrate: int = 500000,
                 data_bitrate: int = 2000000, extended_id: bool = True,
                 padding: int = 0xAA, log=print):
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

        kwargs = dict(interface=self.bustype, channel=self.channel,
                      fd=self.is_fd, bitrate=self.bitrate)
        if self.is_fd:
            kwargs["data_bitrate"] = self.data_bitrate
        self._bus = can.Bus(**kwargs)

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
