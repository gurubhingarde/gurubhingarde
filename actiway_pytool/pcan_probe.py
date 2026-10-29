#!/usr/bin/env python3
"""PCAN diagnostic probe — finds a working PEAK configuration.

Run this when the GUI can't open the channel. It tries classic CAN and several
CAN-FD timings on each PCAN channel and reports which ones initialize, so you
know exactly what to put in the Transport tab.

    python actiway_pytool/pcan_probe.py
    python actiway_pytool/pcan_probe.py PCAN_USBBUS1
"""
from __future__ import annotations

import sys

CHANNELS = [f"PCAN_USBBUS{i}" for i in range(1, 9)]


def _try(desc, **kwargs):
    import can
    try:
        bus = can.Bus(**kwargs)
        bus.shutdown()
        print(f"  OK    {desc}")
        return True
    except Exception as e:
        print(f"  fail  {desc}  -> {type(e).__name__}: {e}")
        return False


def main(argv):
    try:
        import can  # noqa: F401
    except ImportError:
        print("python-can not installed. Run: pip install python-can")
        return 1

    channels = argv[1:] or CHANNELS
    from actiway_pytool.transport.can_isotp import pcan_fd_params

    print("Probing PCAN channels (close PCAN-View and the supplier tool first!)\n")
    any_ok = False
    for ch in channels:
        print(f"[{ch}]")
        if _try(f"classic CAN @ 500k", interface="pcan", channel=ch, bitrate=500000):
            any_ok = True
            print(f"    --> Transport tab: bustype=pcan channel={ch}, CAN-FD OFF, bitrate 500000")
        p = pcan_fd_params(500000, 2000000)
        if _try(f"CAN-FD 500k/2M", interface="pcan", channel=ch, fd=True, **p):
            any_ok = True
            print(f"    --> Transport tab: bustype=pcan channel={ch}, CAN-FD ON, 500000/2000000")
        print()

    if not any_ok:
        print("Nothing opened. Most likely causes:")
        print("  * The channel is busy — close PCAN-View / CHActi-ToolSet (only one")
        print("    program can own a PCAN channel at a time).")
        print("  * Wrong channel name — check PCAN-View's device list.")
        print("  * Driver/device not present — replug the PCAN-USB, check Device Manager.")
    return 0 if any_ok else 2


if __name__ == "__main__":
    # allow running as a loose script
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.exit(main(sys.argv))
