"""Headless tests for the GUI-free core. Run: python -m pytest actiway_pytool/tests"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from actiway_pytool import crypto, firmware
from actiway_pytool.transport.simulator import SimulatorTransport
from actiway_pytool.uds import FlashConfig, FlashSequencer, UdsClient, UdsError


def test_crc32_check_value():
    assert crypto.crc32_hex(b"123456789") == "CBF43926"


def test_seed_to_key_deterministic():
    k1 = crypto.seed_to_key_u16(0x1234, 0xFFFF)
    k2 = crypto.seed_to_key_u16(0x1234, 0xFFFF)
    assert k1 == k2 and 0 <= k1 <= 0xFFFF


def _demo_srec():
    def rec(rtype, addr, payload):
        body = addr.to_bytes(4, "big") + payload
        count = len(body) + 1
        cs = (~(count + sum(body)) & 0xFF)
        return f"S{rtype}{count:02X}{body.hex().upper()}{cs:02X}"
    return rec(3, 0x18080000, bytes(range(16)))


def test_srec_parse_and_checksum():
    segs = firmware.parse_srec(_demo_srec())
    assert len(segs) == 1
    assert segs[0].start_addr == 0x18080000
    assert segs[0].data == bytes(range(16))


def test_ihex_parse():
    # :10 0000 00 <16 bytes 0..15> checksum
    data = bytes(range(16))
    body = bytes([0x10, 0x00, 0x00, 0x00]) + data
    cs = (-sum(body)) & 0xFF
    line = ":" + body.hex().upper() + f"{cs:02X}" + "\n:00000001FF"
    segs = firmware.parse_ihex(line)
    assert segs[0].data == data


def test_full_flash_against_simulator():
    segs = firmware.parse_srec(_demo_srec())
    block = firmware.ReprogrammingBlock("demo", segments=segs)
    t = SimulatorTransport(sec_key=0x1234, log=lambda *_: None)
    with t:
        c = UdsClient(t, log=lambda *_: None)
        FlashSequencer(c, FlashConfig(sec_key=0x1234)).run(block)
    assert t.memory == bytes(range(16))


def test_wrong_seckey_rejected():
    segs = firmware.parse_srec(_demo_srec())
    block = firmware.ReprogrammingBlock("demo", segments=segs)
    t = SimulatorTransport(sec_key=0x1234, log=lambda *_: None)
    with t:
        c = UdsClient(t, log=lambda *_: None)
        try:
            FlashSequencer(c, FlashConfig(sec_key=0xBEEF)).run(block)
            assert False, "wrong key should have been rejected"
        except UdsError as e:
            assert e.nrc == 0x35  # invalidKey
