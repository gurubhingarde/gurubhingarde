"""DoIP vehicle discovery over UDP (ISO 13400-2).

Sends a Vehicle Identification Request as a UDP broadcast to port 13400 and
collects Vehicle Announcement / Identification responses from DoIP entities
on the local network.
"""

from __future__ import annotations

import logging
import socket
import struct
import time
from dataclasses import dataclass
from typing import List

from .doip import PROTOCOL_VERSION, DOIP_PORT, PayloadType, pack_header, unpack_header

log = logging.getLogger("dltool.doip.discovery")


@dataclass
class DoIPEntity:
    """A discovered DoIP entity (one row of the 'Select DoIP devices' list)."""

    ip_address: str
    vin: str
    logical_address: int
    eid: str
    gid: str

    def __str__(self) -> str:
        return (
            f"{self.ip_address:<15}  LA=0x{self.logical_address:04X}  "
            f"VIN={self.vin or '-':<17}  EID={self.eid}  GID={self.gid}"
        )


def parse_announcement(payload: bytes) -> DoIPEntity:
    """Parse a Vehicle Announcement/Identification response payload.

    Layout: VIN(17) logicalAddress(2) EID(6) GID(6) [furtherAction(1)
    syncStatus(1)]. The optional trailing bytes are ignored.
    """
    vin = payload[0:17].decode("latin-1", errors="replace").rstrip("\x00 ")
    logical = struct.unpack(">H", payload[17:19])[0]
    eid = payload[19:25].hex().upper()
    gid = payload[25:31].hex().upper()
    return DoIPEntity(ip_address="", vin=vin, logical_address=logical, eid=eid, gid=gid)


def discover(
    *,
    timeout: float = 2.0,
    broadcast_addr: str = "255.255.255.255",
    bind_addr: str = "0.0.0.0",
    version: int = PROTOCOL_VERSION,
) -> List[DoIPEntity]:
    """Broadcast a Vehicle Identification Request and collect responses.

    :param bind_addr: local interface IP to send from (pick your Ethernet NIC
        when the PC has several; ``0.0.0.0`` lets the OS choose).
    """
    entities: List[DoIPEntity] = []
    seen = set()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        sock.bind((bind_addr, 0))
        msg = pack_header(PayloadType.VEHICLE_IDENT_REQ, b"", version)
        log.info("DoIP discovery broadcast to %s:%d from %s",
                 broadcast_addr, DOIP_PORT, bind_addr)
        sock.sendto(msg, (broadcast_addr, DOIP_PORT))

        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            sock.settimeout(remaining)
            try:
                data, addr = sock.recvfrom(1024)
            except socket.timeout:
                break
            try:
                _, ptype, length = unpack_header(data)
            except Exception:  # noqa: BLE001 - ignore malformed packets
                continue
            if ptype not in (PayloadType.VEHICLE_ANNOUNCEMENT,):
                continue
            payload = data[8:8 + length]
            if len(payload) < 31:
                continue
            ent = parse_announcement(payload)
            ent.ip_address = addr[0]
            key = (ent.ip_address, ent.logical_address)
            if key not in seen:
                seen.add(key)
                entities.append(ent)
                log.info("found %s", ent)
    finally:
        sock.close()
    return entities
