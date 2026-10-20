"""DoIP (ISO 13400) transport over Ethernet.

Implements the DoIP generic header, the payload types used by a tester, and
the TCP diagnostic-message exchange. The codec (header pack/unpack) is kept
as pure functions so it can be unit-tested without a socket.

Standard constants (ISO 13400-2):
    * TCP/UDP data port      : 13400
    * protocol version       : 0x02 (2012) / 0x03 (2019); default 0x02 here
    * generic header         : version(1) ~version(1) payloadType(2) length(4)
"""

from __future__ import annotations

import logging
import socket
import struct
from dataclasses import dataclass
from typing import Optional, Tuple

from .base import Transport, TransportError

log = logging.getLogger("dltool.doip")

DOIP_PORT = 13400
DOIP_HEADER_SIZE = 8
PROTOCOL_VERSION = 0x02


class PayloadType:
    """DoIP payload type identifiers (ISO 13400-2)."""

    GENERIC_NACK = 0x0000
    VEHICLE_IDENT_REQ = 0x0001
    VEHICLE_IDENT_REQ_EID = 0x0002
    VEHICLE_IDENT_REQ_VIN = 0x0003
    VEHICLE_ANNOUNCEMENT = 0x0004        # also vehicle identification response
    ROUTING_ACTIVATION_REQ = 0x0005
    ROUTING_ACTIVATION_RESP = 0x0006
    ALIVE_CHECK_REQ = 0x0007
    ALIVE_CHECK_RESP = 0x0008
    ENTITY_STATUS_REQ = 0x4001
    ENTITY_STATUS_RESP = 0x4002
    POWER_MODE_INFO_REQ = 0x4003
    POWER_MODE_INFO_RESP = 0x4004
    DIAGNOSTIC_MESSAGE = 0x8001
    DIAGNOSTIC_MESSAGE_ACK = 0x8002
    DIAGNOSTIC_MESSAGE_NACK = 0x8003


ROUTING_ACT_RESP_CODES = {
    0x00: "Routing activation denied: unknown source address",
    0x01: "Routing activation denied: all sockets registered/active",
    0x02: "Routing activation denied: source address mismatch",
    0x03: "Routing activation denied: source address already registered",
    0x04: "Routing activation denied: missing authentication",
    0x05: "Routing activation denied: rejected confirmation",
    0x06: "Routing activation denied: unsupported activation type",
    0x10: "Routing successfully activated",
    0x11: "Routing will be activated; confirmation required",
}

GENERIC_NACK_CODES = {
    0x00: "Incorrect pattern format",
    0x01: "Unknown payload type",
    0x02: "Message too large",
    0x03: "Out of memory",
    0x04: "Invalid payload length",
}


def pack_header(payload_type: int, payload: bytes, version: int = PROTOCOL_VERSION) -> bytes:
    """Build a DoIP message: generic header + payload."""
    return struct.pack(">BBHI", version, (~version) & 0xFF, payload_type, len(payload)) + payload


def unpack_header(data: bytes) -> Tuple[int, int, int]:
    """Parse a DoIP generic header. Returns ``(version, payload_type, length)``.

    Raises :class:`TransportError` if the header is malformed (short, or the
    version/inverse-version pair is inconsistent).
    """
    if len(data) < DOIP_HEADER_SIZE:
        raise TransportError(f"short DoIP header: {len(data)} bytes")
    version, inv, ptype, length = struct.unpack(">BBHI", data[:DOIP_HEADER_SIZE])
    if inv != ((~version) & 0xFF):
        raise TransportError(
            f"DoIP header version/inverse mismatch: 0x{version:02X}/0x{inv:02X}"
        )
    return version, ptype, length


def routing_activation_request(source_addr: int, activation_type: int = 0x00) -> bytes:
    """Build a routing activation request payload (ISO 13400-2, 0x0005)."""
    # sourceAddress(2) activationType(1) reserved(4) [+ OEM-specific(4)]
    return struct.pack(">HB", source_addr, activation_type) + b"\x00\x00\x00\x00"


def diagnostic_message(source_addr: int, target_addr: int, uds_payload: bytes) -> bytes:
    """Build a diagnostic-message payload (0x8001)."""
    return struct.pack(">HH", source_addr, target_addr) + uds_payload


@dataclass
class DoIPTransport(Transport):
    """A DoIP client transport bound to one ECU entity.

    :param host: entity IP address.
    :param source_addr: the tester's logical address (e.g. 0x0E00).
    :param target_addr: the ECU's logical address.
    :param port: TCP data port (default 13400).
    :param activation_type: routing activation type (0x00 default, 0x01 WWH-OBD).
    :param auto_activate: perform routing activation automatically on open().
    """

    host: str
    source_addr: int
    target_addr: int
    port: int = DOIP_PORT
    activation_type: int = 0x00
    auto_activate: bool = True
    version: int = PROTOCOL_VERSION
    connect_timeout: float = 5.0

    _sock: Optional[socket.socket] = None

    # -- lifecycle -------------------------------------------------------------
    def open(self) -> None:
        log.info("DoIP connect %s:%d (tester 0x%04X -> ecu 0x%04X)",
                 self.host, self.port, self.source_addr, self.target_addr)
        self._sock = socket.create_connection((self.host, self.port), self.connect_timeout)
        self._sock.settimeout(self.connect_timeout)
        if self.auto_activate:
            self.activate_routing()

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            finally:
                self._sock = None

    # -- DoIP framing ----------------------------------------------------------
    def _send_doip(self, payload_type: int, payload: bytes) -> None:
        if self._sock is None:
            raise TransportError("transport not open")
        self._sock.sendall(pack_header(payload_type, payload, self.version))

    def _recv_doip(self, timeout: float) -> Tuple[int, bytes]:
        """Read one complete DoIP message. Returns ``(payload_type, payload)``."""
        if self._sock is None:
            raise TransportError("transport not open")
        self._sock.settimeout(timeout)
        header = self._recv_exact(DOIP_HEADER_SIZE)
        if header is None:
            return (-1, b"")
        _, ptype, length = unpack_header(header)
        payload = self._recv_exact(length) if length else b""
        if payload is None:
            raise TransportError("connection closed mid-message")
        return (ptype, payload)

    def _recv_exact(self, n: int) -> Optional[bytes]:
        assert self._sock is not None
        buf = bytearray()
        while len(buf) < n:
            try:
                chunk = self._sock.recv(n - len(buf))
            except socket.timeout:
                return None
            if not chunk:
                if not buf:
                    return None
                raise TransportError("connection closed")
            buf.extend(chunk)
        return bytes(buf)

    # -- routing activation ----------------------------------------------------
    def activate_routing(self, timeout: float = 5.0) -> int:
        """Perform routing activation. Returns the response code (0x10 == OK)."""
        self._send_doip(
            PayloadType.ROUTING_ACTIVATION_REQ,
            routing_activation_request(self.source_addr, self.activation_type),
        )
        ptype, payload = self._recv_doip(timeout)
        if ptype == PayloadType.GENERIC_NACK:
            code = payload[0] if payload else -1
            raise TransportError(f"DoIP generic NACK: {GENERIC_NACK_CODES.get(code, code)}")
        if ptype != PayloadType.ROUTING_ACTIVATION_RESP:
            raise TransportError(f"unexpected payload type 0x{ptype:04X} to routing activation")
        # tester(2) entity(2) responseCode(1) reserved(4) ...
        resp_code = payload[4]
        log.info("routing activation -> 0x%02X (%s)",
                 resp_code, ROUTING_ACT_RESP_CODES.get(resp_code, "?"))
        if resp_code not in (0x10, 0x11):
            raise TransportError(
                f"routing activation denied: "
                f"{ROUTING_ACT_RESP_CODES.get(resp_code, resp_code)}"
            )
        return resp_code

    # -- UDS PDU transport -----------------------------------------------------
    def send(self, payload: bytes) -> None:
        self._send_doip(
            PayloadType.DIAGNOSTIC_MESSAGE,
            diagnostic_message(self.source_addr, self.target_addr, payload),
        )

    def receive(self, timeout: float) -> bytes:
        """Receive the next UDS response, swallowing ACKs and alive checks."""
        import time
        deadline = time.monotonic() + timeout
        while True:
            remaining = max(0.0, deadline - time.monotonic())
            ptype, payload = self._recv_doip(remaining or 0.001)
            if ptype == -1:
                return b""  # timeout
            if ptype == PayloadType.DIAGNOSTIC_MESSAGE_ACK:
                continue  # positive ack; the real response follows
            if ptype == PayloadType.DIAGNOSTIC_MESSAGE_NACK:
                code = payload[4] if len(payload) > 4 else -1
                raise TransportError(f"DoIP diagnostic NACK code 0x{code:02X}")
            if ptype == PayloadType.ALIVE_CHECK_REQ:
                self._send_doip(
                    PayloadType.ALIVE_CHECK_RESP,
                    struct.pack(">H", self.source_addr),
                )
                continue
            if ptype == PayloadType.DIAGNOSTIC_MESSAGE:
                # source(2) target(2) uds...
                return payload[4:]
            log.debug("ignoring DoIP payload type 0x%04X", ptype)
