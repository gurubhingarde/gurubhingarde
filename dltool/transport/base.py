"""Abstract transport interface for carrying UDS application PDUs."""

from __future__ import annotations

import abc


class TransportError(Exception):
    """Base error for transport-layer failures."""


class Transport(abc.ABC):
    """Carries UDS request/response PDUs over a specific physical layer.

    A UDS PDU is the service bytes only (SID + data); the transport adds and
    strips whatever framing/addressing its protocol requires (DoIP header and
    logical addresses, or ISO-TP segmentation over CAN).
    """

    @abc.abstractmethod
    def open(self) -> None:
        """Establish the connection (TCP connect, CAN bus up, etc.)."""

    @abc.abstractmethod
    def close(self) -> None:
        """Tear down the connection."""

    @abc.abstractmethod
    def send(self, payload: bytes) -> None:
        """Send one UDS request PDU."""

    @abc.abstractmethod
    def receive(self, timeout: float) -> bytes:
        """Receive one UDS response PDU, or b"" on timeout."""

    def request(self, payload: bytes, timeout: float) -> bytes:
        """Send a request and wait for one response (default = send+receive)."""
        self.send(payload)
        return self.receive(timeout)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.close()
        return False
