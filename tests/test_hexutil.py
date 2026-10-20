from dltool import hexutil as h


def test_hex_to_bytes_variants():
    assert h.hex_to_bytes("0x1A2B") == b"\x1a\x2b"
    assert h.hex_to_bytes("1A 2B 3C") == b"\x1a\x2b\x3c"
    assert h.hex_to_bytes("1a-2b_3c") == b"\x1a\x2b\x3c"
    assert h.hex_to_bytes("ABC") == b"\x0a\xbc"   # odd nibble padded
    assert h.hex_to_bytes("") == b""


def test_bytes_to_hex():
    assert h.bytes_to_hex(b"\x1a\x2b") == "1A 2B"
    assert h.bytes_to_hex(b"\x1a\x2b", sep="", upper=False) == "1a2b"


def test_ascii_roundtrip():
    assert h.to_ascii(b"AB\x00C") == "AB.C"
    assert h.from_ascii("Hi") == b"Hi"


def test_int_bytes():
    assert h.int_to_bytes(0x0E80, 2) == b"\x0e\x80"
    assert h.bytes_to_int(b"\x0e\x80") == 0x0E80
    assert h.int_to_bytes(1, 2, big_endian=False) == b"\x01\x00"


def test_parse_addr():
    assert h.parse_addr("0xF190") == 0xF190
    assert h.parse_addr(0x27) == 0x27
    assert h.parse_addr("255") == 255
