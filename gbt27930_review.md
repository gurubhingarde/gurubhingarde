# GB/T 27930 BMS Validator — Code Review Findings

Generated: 2026-06-25  
Reviewer: Claude Code (claude-sonnet-4-6)  
File reviewed: `gbt27930_bms_validator.py`

---

## Critical Bugs

### 1. `charge_current_demand` sign error in `main()`

```python
# main() bms_params dict
'charge_current_demand': -100.0,   # BUG: should be +100.0
```

The GUI default entry is `'100.0'`. `BMSMessages.BCL` encodes current with `factor=0.1, offset=-400.0`:

| Value | Raw | Decoded |
|---|---|---|
| +100.0 A | 5000 | +100 A ✓ |
| −100.0 A | 3000 | −100 A (discharge!) ✗ |

**Fix:** Change to `'charge_current_demand': 100.0`.

---

### 2. Duplicate CAN IDs in `CID` class

```python
BCP = 0x1809F4   # BMS→Charger  Parameters
BRO = 0x1809F4   # BMS→Charger  Ready Output  ← same ID as BCP
```

`CID` appears unused at runtime (nothing imports it), but the identical IDs are wrong and would cause silent message misclassification if the class were ever used. BRO PGN is `0x0900` (PF=0x09); BCP PGN is `0x0600` (PF=0x06) — they must differ.

---

### 3. Missing `request_stop()` — GUI stop buttons are dead code

`_stop_from_bms` and `_stop_from_charger` both guard with `hasattr(..., 'request_stop')`:

```python
def _stop_from_bms(self):
    if hasattr(self.bms, 'request_stop'):   # always False
        self.bms.request_stop(0x01)         # never reached
```

Neither `VirtualBMS` nor `ChargerSimulator` defines `request_stop()`.  
The on-screen buttons do nothing when clicked.

**Fix — add to `VirtualBMS`:**
```python
def request_stop(self, reason: int = 0x01):
    if self.state == ChargeState.CHARGING:
        self._stop_periodic()
        self._send_BST(reason)
        self.state = ChargeState.STOPPING
```

**Fix — add to `ChargerSimulator`:**
```python
def request_stop(self, reason: int = 0x01):
    self._running = False   # causes _charging_phase loop to exit → _stop_phase runs
```

---

### 4. `_classify_charger_message` uses wrong PF for CST

```python
# VirtualBMS._classify_charger_message
if self.state in {ChargeState.READY, ChargeState.CHARGING} \
        and len(data) >= 4 and pf in (0x1D, 0x9B):
    return 'CST'
```

| Message | PGN | PF |
|---|---|---|
| CST | 0x1A00 | 0x1A |
| CSD | 0x1D00 | **0x1D** ← what the code checks |

PF `0x1D` is CSD, not CST. In the fallback heuristic path a real CST frame would be missed, and a CSD frame during CHARGING/READY would be misclassified as CST, triggering `_rx_CST` prematurely.

**Fix:**
```python
pf in (0x1A,):   # CST only
```

---

## Protocol Concerns

### 5. DP bit placed at bit 25 instead of bit 24 in `j1939_id`

```python
def j1939_id(pgn, sa, da=0xFF, prio=6):
    ...
    return (prio << 26) | (dp << 25) | ...
```

J1939 29-bit frame layout:

| Bits | Field |
|---|---|
| 28–26 | Priority (3 bits) |
| 25 | Reserved |
| **24** | **Data Page** |
| 23–16 | PF |
| 15–8 | PS / DA |
| 7–0 | SA |

DP should be at bit 24, not 25. No functional impact because all GB/T 27930 PGNs use DP=0, but a DP=1 PGN would produce a wrong CAN ID.

**Fix:** `(dp << 24)`

---

### 6. BAM TPDT has no sequence number validation

In `J1939_TP.on_tpdt` the out-of-order and bad-sequence checks are inside
`if rec.get('mode') == self.CM_RTS:` — BAM packets bypass all checks. Out-of-order BAM frames silently corrupt the assembled payload.

**Fix:** Move sequence validation outside the RTS guard (abort not required for BAM, but at minimum log and drop out-of-order packets).

---

### 7. `_bcp_started` flag never resets between sessions

```python
# VirtualBMS._rx_CRM  (CRM=0xAA handler)
if getattr(self, '_bcp_started', False):
    return
self._bcp_started = True
```

If any code path reuses the same `VirtualBMS` instance across sessions, the BCP phase is permanently skipped. Safe today because the GUI recreates all objects in `_make_demo_runtime`, but fragile.

**Fix:** Set `self._bcp_started = False` in `__init__` and reset it alongside `self._brm_running` when a new session starts.

---

## Thread Safety

### 8. `ChargerSimulator` shared state written from two threads without locks

Attributes `_got_bhm`, `_got_brm`, `_got_bcp`, `_bms_ready`, `last_bms_voltage`, `last_bms_current`, `last_bms_soc` are written by `on_message` (VirtualBus subscriber thread) and read by `_run` (charger thread). No lock protects them.

In CPython the GIL protects simple attribute assignment, but the busy-wait patterns like:

```python
while ... and not self._got_brm:
    ...
```

are classic TOCTOU races if `_got_brm` is set between the check and the loop body. Add a `threading.RLock` matching `VirtualBMS._lock`.

---

## Minor Issues

| # | Location | Issue |
|---|---|---|
| 9 | `CID.BCS`, `CID.BCL`, `CID.BSM` | SA = `0x04`, should be `0xF4` (BMS source address) |
| 10 | `_build_right` → `can_log.tag_config` | Tag `'BSM'` is used in `_id_to_name` but never registered via `tag_config`; text falls back to default colour |
| 11 | `ChargerSimulator.on_message` BCS fallback | `pf in (0x10, 0x96)` — BCS PGN 0x1100 → PF 0x11; neither 0x10 nor 0x96 matches. Fallback is never triggered for BCS (TP path handles it correctly, so no visible bug today) |
| 12 | `_periodic_loop` BCL timing | `time.sleep(0.050)` is placed after BCS/BSM block, so BCL jitter grows when BCS TP exchange takes longer than 50 ms |

---

## Severity Summary

| Severity | Count | Items |
|---|---|---|
| Bug — functional | 4 | #1 current sign, #2 duplicate CID, #3 dead stop buttons, #4 wrong PF |
| Protocol deviation | 3 | #5 DP bit, #6 BAM ordering, #7 bcp_started reset |
| Thread safety | 1 | #8 ChargerSimulator races |
| Minor / cosmetic | 4 | #9 #10 #11 #12 |

**Highest-priority fixes:** #1 (negative charge demand corrupts BCL output) and #3 (stop buttons completely non-functional).
