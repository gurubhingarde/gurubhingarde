# ECU Flash Tool — Debug & Development Notes

## Overview

Custom CAN-based flash tool for Air Pump and Oil Pump ECUs on S32K144 platform.
Built with Python + tkinter GUI + python-can library.

---

## Protocol Summary

### CAN IDs (J1939 PDU1, extended 29-bit)

| Role | Air Pump | Oil Pump |
|------|----------|----------|
| Tool → ECU | `0x180006FF` | `0x180005FF` |
| ECU → Tool | `0x1800FF06` | `0x1800FF05` |
| Broadcast | `0x1800FFFF` | `0x1800FFFF` |

### Frame Format

8 bytes: `[TYPE][B1][B2][B3][B4][B5][B6][XOR]`
- XOR = XOR of bytes 0–6
- ECU echoes every received frame verbatim as ACK

### Frame Types

| Type | Description |
|------|-------------|
| `0x00` | Heartbeat / End-of-Block |
| `0x01` / `0x02` | Data toggle A / B |
| `0x03` | Close session |
| `0x04` | Block init / erase |

### Flash Layout

| Constant | Value |
|----------|-------|
| `ECU_FLASH_BASE` | `0x003E8000` |
| `ADDR_STEP` | `0x2000` (8 KB) |
| `MAX_BLOCK` | `0x4000` (16 KB) |
| CRC address | `0x003F5FFE` |

### Block ID Formula

```python
raw_ids   = list(range(total + 1, 1, -1))
block_ids = [1 if x == 2 else x for x in raw_ids]
```

---

## Hex File Handling

### Sequential Reading (confirmed working approach)

All Intel HEX data records (`rt==0`) are concatenated in file order — **not** address-mapped.
Last 4 bytes of the sequential stream = CRC, remainder = firmware.

```python
def load_hex(path):
    # Pass 1: find crc_addr and base_addr
    # Pass 2: concatenate all rt==0 records sequentially
    crc_bytes = bytes(seq[-4:])
    firmware  = bytes(seq[:-4])
    return firmware, crc_bytes, crc_addr, base_addr
```

`base_addr` = 32-bit address of the first data record with `bc > 4`.

### Key Fix — 0xFF Padding for Misaligned Hex Files

Some hex files start at `0x003EA000` instead of `0x003E8000`.
Without correction the firmware lands 8 KB too early in flash.

```python
def build_blocks(firmware, base_addr, log_fn=None):
    pad = base_addr - ECU_FLASH_BASE
    if pad > 0:
        firmware = bytes([0xFF] * pad) + firmware  # erased flash = 0xFF
    ...
```

---

## Firmware Versions Analyzed

### Air Pump Versions

| Version | base_addr | block 5 size | CRC | App starts? |
|---------|-----------|-------------|-----|-------------|
| VER3 | `0x003E8000` | `0x1DAC` (7596 B) | `0x007EEB3D` | ✅ Yes |
| VER1 | `0x003EA000` | `0x3DD8` (15832 B) | `0x007F0B57` | ❌ No |
| VER2 | `0x003EA000` | `0x3DD8` (15832 B) | `0x007F0B57` | ❌ No |
| Unknown (OEM) | `0x003E8000` | `0x1F06` (7942 B) | `0x007EEC94` | ✅ Yes |

VER1 and VER2 hex files are **byte-for-byte identical**.

---

## CAN Trace Analysis Results

### OEM Tool Trace — VER3 (`app_flash_airp.trc`)

- 6 blocks total: 4×16 KB + 1×7596 B + CRC write
- Block 1 first frame: `01 76 1F 02 61 2B 1E 3E` — real code at `0x003E8000`
- Zero 0xFF padding frames
- CRC written: `0x007EEB3D`
- After close: ECU broadcasts on `0x0CF402A1` (J1939, app running)

### OEM Tool Trace — Unknown version (`airpump_flashing_log.trc`)

- **7 blocks**: 4×16 KB + 7942 B + **extra patch block** (addr=`0x003F0F84`, size=176 B) + CRC write
- Block 1 first frame: `01 AA BD FE 02 5A A9 19` — real code at `0x003E8000`
- Zero 0xFF padding frames
- CRC written: `0x007EEC94`
- After close: ECU broadcasts on `0x0CF402A1` ✅

### Our Tool Trace — VER1/2 (after 0xFF padding fix applied)

- 6 blocks: 4×16 KB + **15832 B** + CRC write
- Block 1: first **8192 bytes are 0xFF** (padding), real code from offset `0x2000`
- CRC written: `0x007F0B57`
- After close: **ECU silent** — no broadcast, app does not start ❌

---

## Root Cause: VER1/VER2 Do Not Boot

### Why the 0xFF padding fix is insufficient

1. VER1/VER2 hex files were compiled with application entry point at `0x003EA000`
2. The Interrupt Vector Table (IVT / reset vector) is at `0x003EA000`, not `0x003E8000`
3. The ECU bootloader always jumps to `0x003E8000` after flashing
4. With `0xFF` at `0x003E8000`, the CPU jumps to an invalid address → hard fault → app never starts
5. Additionally, the CRC (`0x007F0B57`) may have been calculated only over `0x003EA000→end`, not over the padded region — causing bootloader CRC validation to fail

### What every working OEM flash has in common

All working OEM traces show **real firmware code starting at `0x003E8000`** — no 0xFF padding at block 1.

### Required fix

The VER1/VER2 hex files must be **rebuilt from source** with the linker base address set to `0x003E8000`. This is a firmware build issue — the flash tool cannot compensate.

**Pending:** OEM traces for VER1/VER2 flash to confirm what data the OEM tool sends at `0x003E8000` for those versions.

---

## Bugs Found & Fixed in Flash Tool

### 1. Wrong sequential data at wrong flash address (VER1/VER2)

- **Symptom:** Flash reports success but ECU does not start application
- **Root cause:** `build_blocks()` ignored `base_addr`; firmware placed 8 KB too early
- **Fix:** Prepend `(base_addr - ECU_FLASH_BASE)` bytes of `0xFF` before splitting into blocks

### 2. Stop button stuck in "Stopping…"

- **Root cause 1:** `progress()` clamped `-1` to `0.0` — failure signal silently dropped
- **Root cause 2:** `progress(-1)` was in `except` block, not `finally` — missed on some paths
- **Root cause 3:** `bus.recv()` could block up to 1 s, delaying abort detection
- **Fix:** Pass negative values through in `progress()`, move `progress(-1)` to `finally`, cap recv at 50 ms, add 3-second force-reset fallback

### 3. Oil Pump block 4 ACK timeout

- **Symptom:** `No ACK for 01F808FFFFF1F0F0`
- **Root cause:** `ACK_TIMEOUT = 0.5 s` too tight for Oil Pump ECU echo latency
- **Fix:** `ACK_TIMEOUT` 0.5 → 1.0 s, `ERASE_TIMEOUT`/`PROG_TIMEOUT` 2 → 5 s

---

## Tool Features

- Air Pump and Oil Pump selection via radio button
- PCAN-USB interface with auto-detect (`🔍 Detect`)
- Configurable interface, channel, bitrate
- Dark Catppuccin theme GUI
- Progress bar with green (success) / red (failure) states
- Stop button with 3-second force-reset fallback
- Exit button (aborts flash and closes)
- Auto-resets progress bar 2 s after failure/stop
- Colored log console (green=ok, red=error, cyan=phase headers)

---

## GitHub Actions — Windows EXE Build

Workflow: `.github/workflows/build_exe.yml`
Branch: `claude/epic-keller-v4KgD`

```yaml
runs-on: windows-latest
python-version: "3.11"
pip install pyinstaller python-can
pyinstaller --onefile --windowed --name "ECU_Flash_Tool" ...
```

Artifacts uploaded to GitHub Release at tag `latest-build`.
Triggers automatically on push to `ecu_flash_tool.py` or via `workflow_dispatch`.

---

## Pending

- [ ] Get OEM tool traces for VER1/VER2 successful flash
- [ ] Confirm whether OEM has corrected hex files (base addr `0x003E8000`) for VER1/VER2
- [ ] Rebuild VER1/VER2 hex files with correct linker base address if source is available
