import pytest

from dltool.firmware import parse_srecord, SRecordError


def srec_line(rtype: str, address: int, data: bytes) -> str:
    """Build a valid S-record line (computes byte count + checksum)."""
    addr_bytes = {"0": 2, "1": 2, "2": 3, "3": 4, "7": 4, "8": 3, "9": 2}[rtype]
    addr = address.to_bytes(addr_bytes, "big")
    body = addr + data
    count = len(body) + 1  # + checksum byte
    chk = (~(count + sum(body)) & 0xFF)
    return "S" + rtype + f"{count:02X}" + body.hex().upper() + f"{chk:02X}"


def test_parse_s1_contiguous():
    text = "\n".join([
        srec_line("0", 0, b"HDR"),
        srec_line("1", 0x1000, b"\xaa\xbb\xcc\xdd"),
        srec_line("1", 0x1004, b"\xee\xff"),
        srec_line("9", 0x1000, b""),
    ])
    fw = parse_srecord(text)
    assert fw.header == b"HDR"
    assert fw.entry_point == 0x1000
    assert len(fw.blocks) == 1
    segs = fw.blocks[0].segments
    assert len(segs) == 1  # coalesced
    assert segs[0].start_addr == 0x1000
    assert bytes(segs[0].data) == b"\xaa\xbb\xcc\xdd\xee\xff"
    assert segs[0].end_addr == 0x1006
    assert fw.total_size == 6


def test_parse_s3_gap_keeps_two_segments():
    text = "\n".join([
        srec_line("3", 0x08000000, b"\x01\x02"),
        srec_line("3", 0x08001000, b"\x03\x04"),
        srec_line("7", 0x08000000, b""),
    ])
    fw = parse_srecord(text)
    segs = fw.blocks[0].segments
    assert len(segs) == 2
    assert segs[0].start_addr == 0x08000000
    assert segs[1].start_addr == 0x08001000


def test_bad_checksum_raises():
    good = srec_line("1", 0x1000, b"\xaa")
    bad = good[:-2] + "00"  # clobber checksum
    with pytest.raises(SRecordError):
        parse_srecord(bad)


def test_bad_byte_count_raises():
    with pytest.raises(SRecordError):
        parse_srecord("S1FF1000AA")  # count says many bytes, none present
