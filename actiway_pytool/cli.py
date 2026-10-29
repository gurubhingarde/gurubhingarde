"""Headless entry point: run the full flash flow against the simulator (or real
hardware) without the GUI. Also serves as the smoke test.

    python -m actiway_pytool.cli selftest
    python -m actiway_pytool.cli flash firmware.s19 --seckey 0xFFFF
    python -m actiway_pytool.cli info
"""
from __future__ import annotations

import argparse
import sys

from . import config, crypto, firmware
from .transport.simulator import SimulatorTransport
from .uds import FlashConfig, FlashSequencer, UdsClient


def _make_sim(sec_key: int, log):
    return SimulatorTransport(sec_key=sec_key, log=log)


def cmd_info(args):
    log = print
    t = _make_sim(args.seckey, log)
    with t:
        c = UdsClient(t, log=log)
        c.diagnostic_session(0x03)
        for did, name in config.INFO_DIDS.items():
            try:
                val = c.read_did(did)
                log(f"  {did:04X} {name:40s} = {val!r}")
            except Exception as e:
                log(f"  {did:04X} {name:40s} : {e}")


def cmd_flash(args):
    log = print
    block = firmware.load_firmware(args.file)
    log(f"loaded {block.file_type} '{block.name}': {len(block.segments)} segment(s), "
        f"{block.total_size} bytes")
    cfg = FlashConfig(sec_key=args.seckey, use_lzo=args.lzo)
    t = _make_sim(args.seckey, log)
    with t:
        c = UdsClient(t, log=log)
        seq = FlashSequencer(c, cfg,
                             progress=lambda d, tot: log(f"   progress {d}/{tot}"))
        digest = seq.run(block)
    # verify simulator captured exactly the image bytes
    image = b"".join(s.data for s in block.segments)
    ok = t.memory == image
    log(f"simulator captured {len(t.memory)} bytes; matches image: {ok}")
    log(f"CRC-32 = {digest}")
    return 0 if ok else 2


def cmd_selftest(args):
    log = print
    rc = 0

    # 1) crypto round-trips
    if crypto.aes_available():
        ct = crypto.aes_encrypt(b"hello world")
        assert crypto.aes_decrypt(ct).startswith(b"hello world"), "AES round-trip"
        log("[ok] AES round-trip (key='actiacsg')")
    else:
        log("[skip] AES (install pycryptodome to enable)")

    assert crypto.crc32_hex(b"123456789") == "CBF43926", "CRC-32 check value"
    log(f"[ok] CRC-32 check value 123456789 -> {crypto.crc32_hex(b'123456789')}")

    seed = b"\x12\x34"
    key = crypto.seed_to_key_bytes(seed, 0xFFFF, 2)
    log(f"[ok] seed 1234 -> key {key.hex().upper()} (SecKey=0xFFFF)")

    # 2) firmware parse (synthetic S-record)
    srec = _demo_srec()
    segs = firmware.parse_srec(srec)
    assert segs and segs[0].data == bytes(range(16)), "S-record parse"
    log(f"[ok] S-record parse: {segs}")

    # 3) full simulated flash, with wrong + right key
    log("--- flash with WRONG SecKey (expect rejection) ---")
    t = _make_sim(0x1234, log)  # ECU expects 0x1234
    with t:
        c = UdsClient(t, log=lambda *_: None)
        try:
            FlashSequencer(c, FlashConfig(sec_key=0xBEEF)).run(
                firmware.ReprogrammingBlock("demo", segments=segs))
            log("[FAIL] wrong key was accepted"); rc = 1
        except Exception as e:
            log(f"[ok] wrong key rejected: {e}")

    log("--- flash with CORRECT SecKey ---")
    t = _make_sim(0x1234, log)
    with t:
        c = UdsClient(t, log=lambda *_: None)
        FlashSequencer(c, FlashConfig(sec_key=0x1234)).run(
            firmware.ReprogrammingBlock("demo", segments=segs))
        image = b"".join(s.data for s in segs)
        if t.memory == image:
            log(f"[ok] flashed & captured {len(t.memory)} bytes correctly")
        else:
            log("[FAIL] captured bytes mismatch"); rc = 1

    log("SELFTEST PASS" if rc == 0 else "SELFTEST FAIL")
    return rc


def _demo_srec() -> str:
    # one S3 record of bytes 0..15 at 0x18080000, with valid checksum
    def rec(rtype, addr, payload):
        body = addr.to_bytes(4, "big") + payload
        count = len(body) + 1
        cs = (~(count + sum(body)) & 0xFF)
        return f"S{rtype}{count:02X}{body.hex().upper()}{cs:02X}"
    return "S00600004844521B\n" + rec(3, 0x18080000, bytes(range(16))) + "\nS70500000000FA\n"


def main(argv=None):
    p = argparse.ArgumentParser(prog="actiway_pytool")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_seckey(sp):
        sp.add_argument("--seckey", type=lambda x: int(x, 0), default=0xFFFF)

    sp = sub.add_parser("selftest"); add_seckey(sp); sp.set_defaults(fn=cmd_selftest)
    sp = sub.add_parser("info"); add_seckey(sp); sp.set_defaults(fn=cmd_info)
    sp = sub.add_parser("flash"); add_seckey(sp)
    sp.add_argument("file"); sp.add_argument("--lzo", action="store_true")
    sp.set_defaults(fn=cmd_flash)

    args = p.parse_args(argv)
    return args.fn(args) or 0


if __name__ == "__main__":
    sys.exit(main())
