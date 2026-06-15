#!/usr/bin/env python3
"""
hex_rebase.py  —  POC tool to shift the load address of an Intel HEX firmware file.

Usage:
    python hex_rebase.py input.hex output.hex <from_addr> <to_addr>

Example (VER1/VER3 base → VER2 base):
    python hex_rebase.py Oilpump_ver1.hex Oilpump_ver1_rebased.hex 0x3E8000 0x3EA000

WARNING: Only use this on firmware compiled as position-independent or
         if you are certain the new base address is correct for the target ECU.
         Rebasing position-dependent code will cause a crash on boot.
"""

import sys
import os


def ihex_checksum(record_bytes):
    """Two's complement of the sum of all record bytes (excluding the leading colon)."""
    return ((~sum(record_bytes) + 1) & 0xFF)


def rebase_hex(src_path, dst_path, from_base, to_base):
    offset = to_base - from_base
    print(f"  Input : {src_path}")
    print(f"  Output: {dst_path}")
    print(f"  Shift : 0x{from_base:08X} → 0x{to_base:08X}  (offset {offset:+d} / 0x{offset & 0xFFFFFFFF:08X})")

    records_in  = 0
    records_mod = 0
    ela         = 0          # current extended linear address (upper 16 bits << 16)

    out_lines = []

    with open(src_path) as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line.startswith(':'):
                out_lines.append(line)
                continue

            bc   = int(line[1:3],  16)
            addr = int(line[3:7],  16)
            rt   = int(line[7:9],  16)
            data = bytes.fromhex(line[9:9 + bc * 2])
            records_in += 1

            if rt == 4:
                # Extended Linear Address — update ELA tracker, don't modify
                ela = int.from_bytes(data, "big") << 16
                out_lines.append(line)
                continue

            if rt != 0:
                # EOF, Start Segment/Linear Address — keep as-is
                out_lines.append(line)
                continue

            # Data record — shift address
            full_addr     = ela | addr
            new_full_addr = full_addr + offset
            new_ela       = new_full_addr & 0xFFFF0000
            new_addr16    = new_full_addr & 0x0000FFFF

            # If the shift crosses a 64 KB segment boundary we need a new ELA record
            if new_ela != ela:
                new_ela_data = (new_ela >> 16).to_bytes(2, "big")
                ela_body     = bytes([0x02, 0x00, 0x00, 0x04]) + new_ela_data
                ela_cs       = ihex_checksum(ela_body)
                out_lines.append(f":{ela_body.hex().upper()}{ela_cs:02X}")
                ela = new_ela
                print(f"  ⚠  ELA boundary crossed at 0x{full_addr:08X} — inserted new ELA record 0x{new_ela >> 16:04X}")

            # Rebuild data record with new address
            body = bytes([bc,
                          (new_addr16 >> 8) & 0xFF,
                           new_addr16       & 0xFF,
                          rt]) + data
            cs   = ihex_checksum(body)
            out_lines.append(f":{body.hex().upper()}{cs:02X}")
            records_mod += 1

    with open(dst_path, "w") as f:
        for l in out_lines:
            f.write(l + "\n")

    print(f"  Records processed : {records_in}")
    print(f"  Data records moved: {records_mod}")
    print(f"  Done → {dst_path}")


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)

    src      = sys.argv[1]
    dst      = sys.argv[2]
    from_b   = int(sys.argv[3], 16)
    to_b     = int(sys.argv[4], 16)

    if not os.path.isfile(src):
        print(f"Error: input file not found: {src}")
        sys.exit(1)

    rebase_hex(src, dst, from_b, to_b)


if __name__ == "__main__":
    main()
