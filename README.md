# dltool — open DoIP / CAN ECU diagnostic & flash tool

A clean-room, fully-owned alternative to a proprietary CAN/DoIP download
tool. Everything here is implemented from the **public standards**, so you
have complete control over it:

| Layer | Standard |
|-------|----------|
| DoIP (Ethernet transport + discovery) | ISO 13400-2 |
| UDS (diagnostic services) | ISO 14229-1 |
| ISO-TP (CAN / CAN-FD transport) | ISO 15765-2 |
| Firmware format | Motorola S-record (S19/S28/S37) |

No code from any third-party or protected binary is reproduced — only the
documented wire formats.

## Install

```bash
pip install -e .            # library + CLI, DoIP works out of the box
pip install -e '.[can]'     # add CAN/CAN-FD support (python-can + can-isotp)
pip install -e '.[dev]'     # tests
```

DoIP needs nothing beyond the standard library. CAN needs `python-can` plus a
driver for your hardware.

## GUI quick start

A desktop GUI (Tkinter — bundled with standard Python on Windows/macOS) wraps
the whole tool: discover, read ECU info, pick a firmware file, and flash with a
progress bar.

```bash
dltool-gui            # or:  python -m dltool.gui
```

Steps in the window: choose **DoIP** or **CAN** → (DoIP) click **Discover** or
type the ECU IP → **Read ECU Info** to confirm the link → **Browse…** for the
`.s19` file → pick the security algorithm → **FLASH**.

On Linux, Tkinter may need a system package first: `sudo apt install python3-tk`
(Debian/Ubuntu) or `sudo dnf install python3-tkinter` (Fedora). Windows/macOS
need nothing extra.

## CLI quick start

```bash
# 1. Find DoIP entities on the network (pick your NIC if the PC has several)
dltool discover --bind 192.168.1.10

# 2. Confirm you can reach an ECU
dltool session   --doip-host 192.168.1.20 --tester-addr 0x0E00 --ecu-addr 0x0E80

# 3. Read software-version identifiers (F180/F190/...)
dltool info      --doip-host 192.168.1.20 --ecu-addr 0x0E80
dltool read-did  --doip-host 192.168.1.20 --ecu-addr 0x0E80 0xF190

# 4. Inspect a firmware file offline (no ECU)
dltool srec firmware.s19

# 5. Flash it (dry-run prints the plan without connecting)
dltool -v flash --doip-host 192.168.1.20 --ecu-addr 0x0E80 \
       --security-level 0x01 --sec-algo xor_ffff \
       --block-size 0x400 firmware.s19
```

### CAN / CAN-FD instead of DoIP

```bash
dltool info --transport can --can-interface pcan --can-channel PCAN_USBBUS1 \
       --can-tx 0x18DA00F9 --can-rx 0x18DAF900
dltool flash --transport can --can-interface vector --can-fd \
       --can-tx 0x18DA00F9 --can-rx 0x18DAF900 firmware.s19
```

Vendor → `python-can` interface: PEAK=`pcan`, Vector=`vector`, ZLG=`zlgcan`,
Kvaser=`kvaser`, Linux SocketCAN=`socketcan`, no hardware=`virtual`.

## Library

```python
from dltool.config import Config
from dltool.transport.factory import build_transport
from dltool.uds.client import UdsClient
from dltool.firmware import parse_srecord_file
from dltool.flash import flash_firmware
from dltool import security

cfg = Config(transport="doip", doip_host="192.168.1.20",
             tester_addr=0x0E00, ecu_addr=0x0E80, block_size=0x400)

t = build_transport(cfg); t.open()
client = UdsClient(t)
print(client.read_data_by_identifier(0xF190))        # read VIN

fw = parse_srecord_file("firmware.s19")
flash_firmware(client, fw, cfg, security.get("xor_ffff"))
t.close()
```

## Project layout

```
dltool/
  config.py              session settings (JSON load/save)
  hexutil.py             hex/ascii/byte helpers
  firmware.py            S-record parser → Segment / ReprogrammingBlock / Firmware
  security.py            SecurityAccess seed→key algorithms (pluggable)
  flash.py               full reprogramming sequence + background TesterPresent
  cli.py                 command-line interface
  uds/
    services.py          SIDs, sub-functions, NRC codes, common DIDs
    client.py            transport-agnostic UDS client (handles 0x78 pending)
  transport/
    base.py              Transport interface
    doip.py              DoIP header/framing + TCP transport + routing activation
    doip_discovery.py    UDP vehicle discovery
    can_isotp.py         CAN/CAN-FD via python-can + ISO-TP
    factory.py           build a transport from Config
tests/                   pytest suite (DoIP, UDS, S-record, flash — no hardware)
```

## Security access

ISO 14229 defines the *handshake* but leaves the **seed → key algorithm** to
the manufacturer. Built-in examples live in `dltool/security.py`
(`xor_ffff`, `passthrough`, plus `xor_key()` / `add_constant_key()` factories).
Register your ECU's real algorithm:

```python
from dltool import security
security.register("myecu", lambda seed: my_algo(seed))
# then: dltool flash --sec-algo myecu ...
```

## Status & roadmap

Implemented and unit-tested: DoIP framing/discovery, UDS services, the flash
download sequence, and S-record parsing. Not yet implemented: LZO segment
decompression, the OEM `MulticS.xml` test-definition parser, and a GUI — all
straightforward to add on top of this core. CAN paths are implemented against
the `python-can` API but need real hardware to exercise end-to-end.

> Use only on vehicles/ECUs you are authorised to service. Flashing an ECU
> can brick it; keep a known-good image and verify power before programming.
