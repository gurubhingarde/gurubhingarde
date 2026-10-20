"""Command-line interface for dltool.

Subcommands:
    discover   DoIP vehicle discovery (UDP broadcast)
    info       connect and read common software-version DIDs
    read-did   read one Data Identifier
    session    enter a diagnostic session (connectivity test)
    flash      download an S-record firmware file to the ECU
    srec       inspect an S-record file (offline, no ECU)
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

from . import security
from .config import Config
from .firmware import parse_srecord_file
from .hexutil import bytes_to_hex, parse_addr, to_ascii
from .uds.client import NegativeResponse, UdsClient
from .uds.services import COMMON_DIDS, Session


def _log_setup(verbose: int) -> None:
    level = logging.WARNING - (10 * min(verbose, 2))
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")


def _cfg_from_args(args) -> Config:
    cfg = Config.load(args.config) if args.config else Config()
    for attr in ("transport", "doip_host", "doip_bind_addr"):
        v = getattr(args, attr, None)
        if v is not None:
            setattr(cfg, attr, v)
    if getattr(args, "tester_addr", None) is not None:
        cfg.tester_addr = parse_addr(args.tester_addr)
    if getattr(args, "ecu_addr", None) is not None:
        cfg.ecu_addr = parse_addr(args.ecu_addr)
    if getattr(args, "can_interface", None):
        cfg.transport = "can"
        cfg.can_interface = args.can_interface
    if getattr(args, "can_channel", None) is not None:
        cfg.can_channel = args.can_channel
    if getattr(args, "can_fd", False):
        cfg.can_fd = True
    if getattr(args, "can_tx", None) is not None:
        cfg.can_tx_id = parse_addr(args.can_tx)
    if getattr(args, "can_rx", None) is not None:
        cfg.can_rx_id = parse_addr(args.can_rx)
    return cfg


def _open_client(cfg: Config):
    from .transport.factory import build_transport
    transport = build_transport(cfg)
    transport.open()
    client = UdsClient(transport, p2_timeout=cfg.p2_timeout, p2_star_timeout=cfg.p2_star_timeout)
    return transport, client


# -- subcommands ---------------------------------------------------------------
def cmd_discover(args) -> int:
    from .transport.doip_discovery import discover
    entities = discover(timeout=args.timeout, bind_addr=args.bind or "0.0.0.0")
    if not entities:
        print("No DoIP entities responded.")
        print("Check: correct NIC (--bind <local-ip>), same subnet, UDP 13400 open in firewall.")
        return 1
    print(f"Found {len(entities)} DoIP entity(ies):\n")
    for e in entities:
        print(" ", e)
    return 0


def cmd_presets(args) -> int:
    from .presets import load_presets, load_zones
    presets = load_presets(args.file)
    print(f"Mapping presets ({len(presets)}):\n")
    for p in presets:
        extra = []
        if p.seckey is not None:
            extra.append(f"seckey=0x{p.seckey:X}")
        if p.sha256_start is not None:
            extra.append(f"sha256@0x{p.sha256_start:08X}")
        print(f"  {p}  blkCAN=0x{p.min_data_can:X} blkDoIP=0x{p.min_data_doip:X} "
              + " ".join(extra))
    if args.zones:
        print("\nZones:")
        for z in load_zones():
            print(f"  idx {z.index:<2} value {z.value:<3} {z.name}")
    return 0


def cmd_srec(args) -> int:
    fw = parse_srecord_file(args.file)
    print(f"File: {args.file}")
    if fw.header:
        print(f"Header: {to_ascii(fw.header)!r} ({bytes_to_hex(fw.header)})")
    if fw.entry_point is not None:
        print(f"Entry point: 0x{fw.entry_point:08X}")
    print(f"Blocks: {len(fw.blocks)}  Total: {fw.total_size} bytes\n")
    for block in fw.blocks:
        print(f"  block {block.name!r}: {len(block.segments)} segment(s), {block.total_size} bytes")
        for seg in block.segments:
            print(f"    0x{seg.start_addr:08X} .. 0x{seg.end_addr:08X}  ({seg.size} bytes)")
    return 0


def cmd_info(args) -> int:
    cfg = _cfg_from_args(args)
    transport, client = _open_client(cfg)
    try:
        client.diagnostic_session_control(Session.EXTENDED)
        print("Connected. Reading software-version identifiers:\n")
        results = client.read_identifiers(list(COMMON_DIDS))
        for did, val in results.items():
            name = COMMON_DIDS.get(did, "")
            if isinstance(val, Exception):
                print(f"  0x{did:04X} {name:<40} -- {val}")
            else:
                print(f"  0x{did:04X} {name:<40} {to_ascii(val)!r}  [{bytes_to_hex(val)}]")
        return 0
    finally:
        transport.close()


def cmd_read_did(args) -> int:
    cfg = _cfg_from_args(args)
    did = parse_addr(args.did)
    transport, client = _open_client(cfg)
    try:
        client.diagnostic_session_control(Session.EXTENDED)
        val = client.read_data_by_identifier(did)
        print(f"0x{did:04X}: {to_ascii(val)!r}  [{bytes_to_hex(val)}]")
        return 0
    except NegativeResponse as exc:
        print(f"0x{did:04X}: {exc}")
        return 1
    finally:
        transport.close()


def cmd_session(args) -> int:
    cfg = _cfg_from_args(args)
    transport, client = _open_client(cfg)
    try:
        client.diagnostic_session_control(Session.EXTENDED)
        print("Session established OK (ECU is reachable and responding).")
        return 0
    finally:
        transport.close()


def cmd_flash(args) -> int:
    from .flash import flash_firmware
    cfg = _cfg_from_args(args)
    # Apply a Mapping preset first (sets zone, flash window, block size, seckey);
    # explicit flags below still override it.
    if args.preset:
        from .presets import load_presets, find_preset, apply_preset
        preset = find_preset(load_presets(args.presets_file), args.preset)
        apply_preset(cfg, preset)
        print(f"Mapping: {preset.desc}  (zone={cfg.zone}, "
              f"window=0x{preset.start:08X}..0x{preset.end:08X}, block=0x{cfg.block_size:X})")
    if args.block_size is not None:
        cfg.block_size = parse_addr(args.block_size)
    if args.security_level is not None:
        cfg.security_level = parse_addr(args.security_level)
    cfg.lzo = args.lzo
    cfg.unlock_all = args.unlock_all

    fw = parse_srecord_file(args.file)
    print(f"Firmware: {args.file}  ({fw.total_size} bytes, {len(fw.blocks)} block(s))")

    if args.sec_algo:
        key_fn = security.get(args.sec_algo)
    elif args.sec_secret:
        from .hexutil import hex_to_bytes
        key_fn = security.xor_key(hex_to_bytes(args.sec_secret))
    else:
        key_fn = security.get("passthrough")

    def progress(label, done, total):
        pct = (100 * done) // total if total else 100
        print(f"\r  {label}: {done}/{total} ({pct}%)", end="", flush=True)
        if done >= total:
            print()

    if args.dry_run:
        print("Dry run - not connecting. Flash plan:")
        for b in fw.blocks:
            for s in b.segments:
                print(f"  RequestDownload @0x{s.start_addr:08X} size={s.size}, "
                      f"TransferData in {cfg.block_size}-byte blocks")
        return 0

    transport, client = _open_client(cfg)
    try:
        flash_firmware(
            client, fw, cfg, key_fn,
            progress=progress,
            erase_routine=parse_addr(args.erase_routine) if args.erase_routine else None,
            check_routine=parse_addr(args.check_routine) if args.check_routine else None,
            reset=not args.no_reset,
        )
        print("Flash complete.")
        return 0
    finally:
        transport.close()


# -- parser --------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="dltool", description=__doc__.splitlines()[0])
    p.add_argument("-v", "--verbose", action="count", default=0, help="repeat for more logging")
    p.add_argument("-c", "--config", help="JSON config file")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_common(sp, need_ecu=True):
        sp.add_argument("--transport", choices=["doip", "can"])
        sp.add_argument("--doip-host", help="ECU/entity IP address (DoIP)")
        sp.add_argument("--doip-bind-addr", help="local NIC IP to bind (DoIP)")
        sp.add_argument("--tester-addr", help="tester logical address, e.g. 0x0E00")
        sp.add_argument("--ecu-addr", help="ECU logical address, e.g. 0x0E80")
        sp.add_argument("--can-interface", help="python-can interface (pcan/vector/zlgcan/...)")
        sp.add_argument("--can-channel")
        sp.add_argument("--can-fd", action="store_true")
        sp.add_argument("--can-tx", help="CAN request id (hex)")
        sp.add_argument("--can-rx", help="CAN response id (hex)")

    sp = sub.add_parser("discover", help="DoIP vehicle discovery")
    sp.add_argument("--timeout", type=float, default=2.0)
    sp.add_argument("--bind", help="local NIC IP to broadcast from")
    sp.set_defaults(func=cmd_discover)

    sp = sub.add_parser("srec", help="inspect an S-record file (offline)")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_srec)

    sp = sub.add_parser("presets", help="list Mapping presets (and zones)")
    sp.add_argument("--file", help="preset XML (default: bundled presets.xml)")
    sp.add_argument("--zones", action="store_true", help="also list memory zones")
    sp.set_defaults(func=cmd_presets)

    sp = sub.add_parser("session", help="connectivity test (open a session)")
    add_common(sp)
    sp.set_defaults(func=cmd_session)

    sp = sub.add_parser("info", help="read software-version identifiers")
    add_common(sp)
    sp.set_defaults(func=cmd_info)

    sp = sub.add_parser("read-did", help="read one Data Identifier")
    add_common(sp)
    sp.add_argument("did", help="DID, e.g. 0xF190")
    sp.set_defaults(func=cmd_read_did)

    sp = sub.add_parser("flash", help="download an S-record firmware to the ECU")
    add_common(sp)
    sp.add_argument("file", help="S-record (.s19/.srec/.mot) firmware file")
    sp.add_argument("--preset", help='Mapping preset, e.g. "Multic-S -> CALIB"')
    sp.add_argument("--presets-file", help="preset XML (default: bundled presets.xml)")
    sp.add_argument("--block-size", help="max TransferData block (e.g. 0x400)")
    sp.add_argument("--security-level", help="SecurityAccess request-seed level (odd)")
    sp.add_argument("--sec-algo", choices=security.available(),
                    help="registered seed->key algorithm")
    sp.add_argument("--sec-secret", help="hex secret for the built-in XOR key algorithm")
    sp.add_argument("--erase-routine", help="RoutineControl id to erase before download")
    sp.add_argument("--check-routine", help="RoutineControl id to check after download")
    sp.add_argument("--lzo", action="store_true", help="LZO-compress segments (needs dltool[lzo])")
    sp.add_argument("--unlock-all", action="store_true", help="attempt all security levels")
    sp.add_argument("--no-reset", action="store_true", help="skip ECUReset at the end")
    sp.add_argument("--dry-run", action="store_true", help="parse + print plan, do not connect")
    sp.set_defaults(func=cmd_flash)

    return p


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)
    _log_setup(args.verbose)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001 - top-level friendly error
        if args.verbose:
            raise
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
