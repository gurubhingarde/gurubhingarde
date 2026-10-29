"""Transport abstraction: anything that can send/receive one UDS payload.

The UDS client talks to a `Transport`; concrete transports implement ISO-TP
over CAN/CAN-FD, DoIP, or the in-process simulator. This mirrors the original
tool's ACTIA.Tools.ICanDrv / clIProtocol split.
"""
from __future__ import annotations

import abc


class TransportError(Exception):
    pass


class Transport(abc.ABC):
    """Exchanges whole UDS messages (service id + data), hiding framing."""

    name = "base"

    @abc.abstractmethod
    def open(self) -> None:
        ...

    @abc.abstractmethod
    def close(self) -> None:
        ...

    @abc.abstractmethod
    def send(self, payload: bytes) -> None:
        """Send one UDS request payload (SID + params)."""

    @abc.abstractmethod
    def recv(self, timeout: float = 2.0) -> bytes:
        """Block for one UDS response payload, or raise TransportError on timeout."""

    def request(self, payload: bytes, timeout: float = 2.0) -> bytes:
        self.send(payload)
        return self.recv(timeout)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.close()
