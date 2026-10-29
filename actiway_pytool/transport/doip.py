"""DoIP (ISO 13400) transport — minimal diagnostic message exchange over TCP.

Optional: imported only when DoIP is selected. Implements the subset the flash
flow needs: routing activation + diagnostic message request/response. The
original tool's clDoIP/clDoIPDiscovery broadcast on 255.255.255.255 for vehicle
discovery; discovery is left as a helper and not required if you know the IP.
"""
from __future__ import annotations

import socket
import struct

from .base import Transport, TransportError

PROTO = 0x02  # DoIP ISO 13400-2:2012
_HDR = struct.Struct(">BBHI")  # version, inv-version, payload-type, length


class DoIPTransport(Transport):
    name = "DoIP (ISO 13400)"

    def __init__(self, host: str, port: int = 13400,
                 source_addr: int = 0x0E80, target_addr: int = 0x1000,
                 timeout: float = 3.0, log=print):
        self.host = host
        self.port = port
        self.source_addr = source_addr
        self.target_addr = target_addr
        self.timeout = timeout
        self._log = log
        self._sock = None

    def _pack(self, ptype: int, payload: bytes) -> bytes:
        return _HDR.pack(PROTO, PROTO ^ 0xFF, ptype, len(payload)) + payload

    def _read_msg(self) -> tuple[int, bytes]:
        hdr = self._recv_exact(_HDR.size)
        _, _, ptype, length = _HDR.unpack(hdr)
        return ptype, self._recv_exact(length)

    def _recv_exact(self, n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = self._sock.recv(n - len(buf))
            if not chunk:
                raise TransportError("DoIP socket closed")
            buf += chunk
        return buf

    def open(self):
        self._sock = socket.create_connection((self.host, self.port), self.timeout)
        self._sock.settimeout(self.timeout)
        # Routing activation (type 0x0005): source addr + activation type 0x00
        payload = struct.pack(">HBI", self.source_addr, 0x00, 0x00000000)
        self._sock.sendall(self._pack(0x0005, payload))
        ptype, resp = self._read_msg()
        if ptype != 0x0006 or len(resp) < 5 or resp[4] not in (0x10, 0x11):
            raise TransportError(f"routing activation failed (type=0x{ptype:04X})")
        self._log(f"[doip] routing active to {self.host}:{self.port} "
                  f"src=0x{self.source_addr:04X} tgt=0x{self.target_addr:04X}")

    def close(self):
        if self._sock:
            self._sock.close()
            self._sock = None

    def send(self, payload: bytes):
        msg = struct.pack(">HH", self.source_addr, self.target_addr) + bytes(payload)
        self._sock.sendall(self._pack(0x8001, msg))
        # optional positive-ack (0x8002) is consumed in recv()

    def recv(self, timeout: float = 2.0) -> bytes:
        self._sock.settimeout(timeout)
        while True:
            ptype, resp = self._read_msg()
            if ptype == 0x8002:      # diag message positive ack -> keep waiting
                continue
            if ptype == 0x8003:      # negative ack
                raise TransportError(f"DoIP diag NACK: {resp.hex()}")
            if ptype == 0x8001:      # diagnostic message (SA, TA, data...)
                return resp[4:]
            # ignore alive-check etc.
