# Actiway Download Tool — Python reimplementation

A clean-room Python rebuild of the ACTIA *Actiway* ECU flash-download tool, with
a Tkinter GUI you fully control. It performs **UDS (ISO 14229)** reprogramming
over **CAN / CAN-FD / DoIP**, parses **Motorola S-record / Intel-HEX** firmware,
and implements the **AES / CRC-32 / seed→key** primitives recovered from the
original binaries.

A built-in **UDS ECU simulator** lets you test the entire flash workflow with no
hardware.

## Quick start

```bash
# 1. (Linux only) Tkinter:   sudo apt install python3-tk
# 2. Launch the GUI:
python actiway_pytool/run_gui.py
#    or
python -m actiway_pytool.gui
```

No pip packages are needed for the GUI + simulator. Optional extras (real CAN,
AES, LZO) are in `requirements.txt`.

### GUI walkthrough
1. **Transport tab** — pick `Simulator` (default), `CAN / CAN-FD`, or `DoIP`,
   and fill in the matching connection fields.
2. **Flash tab** — `Browse...` a firmware file (segments appear in the table),
   then pick a **Mapping**. Selecting a mapping auto-fills its **Sec Key**,
   **Zone** and **address range** — exactly like the supplier CHActi-ToolSet.
   The image is clipped to that mapping's address window before flashing.
3. Click **Read ECU Info** or **Flash**. The log streams every UDS frame live;
   the progress bar tracks TransferData.

### Mappings (full supplier list)
All 18 mappings (Multic-SX / Multic-S / IRB-STD3X / IRB-STD3 / CSG / Power33S /
ACH-PowersC / ACH-LCC …) are loaded from **`data/presets.xml`** — the same file
format the original tool uses (`Actiway_DownLoad_Tool.xml`). Each mapping holds
its own zone, address range, min block sizes, optional SHA-256 region and
optional `<seckey>`. **Edit `data/presets.xml` to add or change mappings** — no
code change needed. Zones come from `data/zones.xml` (`Actiway_Zones_Config.xml`).

## Headless use (no display / scripting / CI)

```bash
python -m actiway_pytool.cli selftest            # full self-check
python -m actiway_pytool.cli info                # read DIDs from the simulator
python -m actiway_pytool.cli flash fw.s19 --seckey 0xFFFF
```

## Testing against the simulator vs. real hardware

- **Simulator** (`transport/simulator.py`) implements a real UDS server:
  SessionControl, SecurityAccess (seed→key checked with your `SecKey`),
  RequestDownload/TransferData/TransferExit, ECUReset, ReadDataByIdentifier.
  Wrong key → `NRC 0x35`, exactly like an ECU.
- **PCAN native** (`transport/pcan_native.py`) talks straight to PEAK's
  `PCANBasic.dll` via the bundled `PCANBasic.py`, with a built-in ISO-TP layer
  (classic + CAN-FD). **Recommended for PEAK hardware** — it avoids python-can's
  PCAN backend quirks and matches how the supplier tool drives the DLL. Needs
  only the PEAK driver installed (bitness must match your Python).
- **CAN/CAN-FD** (`transport/can_isotp.py`) uses `python-can` + `can-isotp` for
  non-PEAK interfaces (Vector, Kvaser, SocketCAN, …). Set bustype, channel, and
  request/response IDs.
- **DoIP** (`transport/doip.py`) connects over TCP (ISO 13400), does routing
  activation, then diagnostic messages.

## Layout

| File | Purpose |
|---|---|
| `gui.py` | Tkinter GUI (presentation only) |
| `run_gui.py` | launcher |
| `cli.py` | headless runner + self-test |
| `uds.py` | UDS client + `FlashSequencer` (the reprogramming sequence) |
| `firmware.py` | S-record / Intel-HEX / binary parsing → segments |
| `crypto.py` | AES-128 (`actiacsg`), CRC-32, SHA-256, seed→key |
| `lzo.py` | optional LZO1X compression shim |
| `config.py` | defaults, zones, presets, DID catalogue from the original |
| `transport/` | `simulator`, `can_isotp`, `doip` backends |
| `tests/` | headless tests |

## Calibration notes (match your real ECU)

The original IL did not expose every constant. These are **configurable** (GUI
*Crypto/Checksum* tab or `FlashConfig`) and marked `CALIBRATE` in the source:

- **seed→key** (`crypto.seed_to_key_u16`) — default 16-bit mix keyed by `SecKey`;
  replace with your ECU's exact algorithm if it differs.
- **CRC-32** params (poly/init/xorout) — default is standard zlib CRC-32.
- **AES mode** — defaults to CBC + zero IV; switch to ECB if needed.

All of these are isolated so you can drop in the real algorithm without touching
the GUI or transport code.

## Scope / safety

This reimplements a **diagnostic/reprogramming** workflow for ECUs you are
authorised to service. Flashing real hardware with a wrong image, address range,
or key can brick a module — test against the simulator first, and only flash
hardware you own or are authorised to work on.
