import struct

import pytest

from dltool.transport import doip
from dltool.transport.base import TransportError
from dltool.transport.doip_discovery import parse_announcement


def test_header_roundtrip():
    msg = doip.pack_header(doip.PayloadType.DIAGNOSTIC_MESSAGE, b"\x22\xf1\x90")
    version, ptype, length = doip.unpack_header(msg)
    assert version == doip.PROTOCOL_VERSION
    assert ptype == doip.PayloadType.DIAGNOSTIC_MESSAGE
    assert length == 3
    assert msg[doip.DOIP_HEADER_SIZE:] == b"\x22\xf1\x90"


def test_header_inverse_check():
    bad = bytearray(doip.pack_header(doip.PayloadType.VEHICLE_IDENT_REQ, b""))
    bad[1] ^= 0xFF  # corrupt the inverse-version byte
    with pytest.raises(TransportError):
        doip.unpack_header(bytes(bad))


def test_routing_activation_request_layout():
    payload = doip.routing_activation_request(0x0E00, activation_type=0x01)
    assert payload[:2] == b"\x0e\x00"
    assert payload[2] == 0x01
    assert len(payload) == 7  # source(2)+type(1)+reserved(4)


def test_diagnostic_message_layout():
    msg = doip.diagnostic_message(0x0E00, 0x0E80, b"\x10\x03")
    assert msg[:2] == b"\x0e\x00"
    assert msg[2:4] == b"\x0e\x80"
    assert msg[4:] == b"\x10\x03"


def test_parse_announcement():
    vin = b"WVWZZZ1KZ9W000001"            # 17 bytes
    payload = vin + struct.pack(">H", 0x0E80) + bytes.fromhex("112233445566") \
        + bytes.fromhex("AABBCCDDEEFF")
    ent = parse_announcement(payload)
    assert ent.vin == "WVWZZZ1KZ9W000001"
    assert ent.logical_address == 0x0E80
    assert ent.eid == "112233445566"
    assert ent.gid == "AABBCCDDEEFF"
