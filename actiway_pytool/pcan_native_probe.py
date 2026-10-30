#!/usr/bin/env python3
"""Native PCAN diagnostic using PEAK's PCANBasic.dll directly.

Answers the key questions behind an InitializeFD failure:
  * Is the PCANBasic DLL loadable, and what API version?
  * Which PCAN channels are attached, and is each one CAN-FD capable?
  * Is the target channel free, or busy (owned by PCAN-View / another tool)?
  * Does classic Initialize (500k) work?  Does InitializeFD (500k/2M) work?

Run it with PCAN-View and the supplier tool CLOSED:
    python actiway_pytool/pcan_native_probe.py
    python actiway_pytool/pcan_native_probe.py PCAN_USBBUS1
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))           # for PCANBasic.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # for package

CONDITION = {0: "UNAVAILABLE", 1: "AVAILABLE (free)", 2: "OCCUPIED (busy)",
             3: "AVAILABLE but a PCAN-View is connected"}


def main(argv):
    try:
        import PCANBasic as P
    except Exception as e:
        print(f"Could not import PCANBasic.py: {e}")
        print("Put PEAK's PCANBasic.py next to this script.")
        return 1

    try:
        api = P.PCANBasic()
    except Exception as e:
        print(f"Could not load PCANBasic.dll: {e}")
        print("Install/repair the PEAK driver; ensure its bitness matches Python.")
        return 1

    import platform
    import struct
    print(f"Python {platform.python_version()} ({struct.calcsize('P') * 8}-bit)\n")

    st, ver = api.GetValue(P.PCAN_NONEBUS, P.PCAN_API_VERSION)
    if st == P.PCAN_ERROR_OK:
        print(f"PCAN-Basic API version: {ver.decode(errors='replace')}")

    # Attached channels + FD capability
    target_handle = None
    want = argv[1] if len(argv) > 1 else "PCAN_USBBUS1"
    print("\nAttached PCAN channels:")
    st, chans = api.GetValue(P.PCAN_NONEBUS, P.PCAN_ATTACHED_CHANNELS)
    if st == P.PCAN_ERROR_OK:
        for ch in chans:
            name = ch.device_name.decode(errors="replace")
            fd = bool(ch.device_features & P.FEATURE_FD_CAPABLE)
            h = int(ch.channel_handle)
            cond = CONDITION.get(ch.channel_condition, str(ch.channel_condition))
            tag = "CAN-FD capable" if fd else "NOT FD capable (classic CAN only)"
            print(f"  handle=0x{h:X}  {name}  [{tag}]  condition={cond}")
    else:
        print(f"  (could not list channels: 0x{st:X})")

    # Resolve target handle from name
    handles = {f"PCAN_USBBUS{i}": 0x50 + i for i in range(1, 9)}
    target_handle = handles.get(want, 0x51)
    print(f"\nTarget channel {want} (handle 0x{target_handle:X}):")

    # classic init
    st = api.Initialize(P.TPCANHandle(target_handle), P.TPCANBaudrate(0x001C))  # 500k
    print(f"  classic Initialize(500k): {_txt(api, P, st)}")
    if st == P.PCAN_ERROR_OK:
        api.Uninitialize(P.TPCANHandle(target_handle))

    # FD init
    brs = (b"f_clock_mhz=80,nom_brp=10,nom_tseg1=12,nom_tseg2=3,nom_sjw=1,"
           b"data_brp=4,data_tseg1=7,data_tseg2=2,data_sjw=1")
    st = api.InitializeFD(P.TPCANHandle(target_handle), P.TPCANBitrateFD(brs))
    print(f"  InitializeFD(500k/2M):    {_txt(api, P, st)}")
    if st == P.PCAN_ERROR_OK:
        api.Uninitialize(P.TPCANHandle(target_handle))

    print("\nReading of results:")
    print("  * If the channel line says 'NOT FD capable' -> your adapter is a plain")
    print("    PCAN-USB; use classic CAN (untick CAN-FD in the tool).")
    print("  * If condition=OCCUPIED/PCAN-View -> close that program and re-run.")
    print("  * If classic works but FD says ILLOPERATION -> non-FD hardware or old driver.")
    return 0


def _txt(api, P, st):
    if st == P.PCAN_ERROR_OK:
        return "OK"
    r, msg = api.GetErrorText(st, 0x09)
    return f"0x{st:X} ({msg.decode(errors='replace') if r == P.PCAN_ERROR_OK else '?'})"


if __name__ == "__main__":
    sys.exit(main(sys.argv))
