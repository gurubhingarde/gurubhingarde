# GB/T 27930-2015 Protocol Conformance Audit

Generated: 2026-06-25  
Standard: 电动汽车非车载传导式充电机与电池管理系统之间的通信协议 (GB/T 27930-2015)  
File: `gbt27930_bms_validator.py`

---

## 1. Message Content vs Standard Tables

### 1.1 BHM — Battery Handshake Message (Table A.1)

| Field | Standard | Code |
|---|---|---|
| Max total voltage | Bytes 0-1, 0.1V, 0–65535 | `encode_signal(d, 0, 16, voltage, 0.1, 0.0)` |

✅ **Correct.**

---

### 1.2 BCP — Battery Charge Parameters (Table A.5)

| Field | Byte | Factor | Offset | Code |
|---|---|---|---|---|
| Max single cell voltage | 0-1 | 0.01 V | 0 | `encode_signal(d, 0, 16, cell_max_v, 0.01, 0.0)` ✅ |
| Max charge current | 2-3 | 0.1 A | −400 A | `encode_signal(d, 16, 16, max_i, 0.1, -400.0)` ✅ |
| Total energy (rated) | 4-5 | 0.1 kWh | 0 | `encode_signal(d, 32, 16, energy, 0.1, 0.0)` ✅ |
| Max total voltage | 6-7 | 0.1 V | 0 | `encode_signal(d, 48, 16, max_v, 0.1, 0.0)` ✅ |
| Max temperature | 8 | 1 °C | −50 | `encode_signal(d, 64, 8, temp, 1.0, -50.0)` ✅ |
| SOC | 9-10 | 0.1 % | 0 | `encode_signal(d, 72, 16, soc, 0.1, 0.0)` ✅ |
| Current pack voltage | 11-12 | 0.1 V | 0 | `encode_signal(d, 88, 16, pack_v, 0.1, 0.0)` ✅ |

✅ **All fields correct.** 13-byte message correctly triggers J1939 TP.

---

### 1.3 BCL — Battery Charge Limits (Table A.9)

| Field | Standard | Code |
|---|---|---|
| Voltage demand | Bytes 0-1, 0.1V | `encode_signal(d, 0, 16, v_demand, 0.1, 0.0)` ✅ |
| Current demand | Bytes 2-3, 0.1A, offset −400 | `encode_signal(d, 16, 16, i_demand, 0.1, -400.0)` ✅ |
| Charge mode | Byte 4, 0=CV, 1=CC | `d[4] = mode` ✅ |

⚠️ **BCL mode always sent as 1 (constant current).** The `_periodic_loop` calls:

```python
bcl = self.msgs.BCL(
    v_demand=min(max_v, sim_pack_v + 5),
    i_demand=self.params.get('charge_current_demand', 100.0)
    # mode not passed → defaults to 1 (CC)
)
```

GB/T 27930 §10.2.3: the BMS should set mode=0 (CV) when pack voltage approaches the target voltage (taper phase). Sending CC mode throughout violates the charging profile. **Fix:** switch to mode=0 when `sim_pack_v ≥ max_total_voltage − threshold`.

---

### 1.4 BCS — Battery Charge Status (Table A.10)

| Field | Bits | Factor | Code |
|---|---|---|---|
| Charging voltage | 0–15 | 0.1 V | `encode_signal(d, 0, 16, v, 0.1, 0.0)` ✅ |
| Charging current | 16–31 | 0.1 A, −400 | `encode_signal(d, 16, 16, i, 0.1, -400.0)` ✅ |
| Max cell voltage | 32–43 (12 bits) | 0.01 V | `encode_signal(d, 32, 12, cell_v, 0.01, 0.0)` ✅ |
| Max cell group no. | 44–47 (4 bits) | — | `encode_signal(d, 44, 4, grp, 1.0, 0.0)` ✅ |
| SOC | 48–55 | 1 % | `encode_signal(d, 48, 8, soc, 1.0, 0.0)` ✅ |
| Est. remaining time | 56–71 | 1 min | `encode_signal(d, 56, 16, t_remain, 1.0, 0.0)` ✅ |

✅ **9-byte message, all fields correct.** Requires J1939 TP (9 > 8 bytes).

---

### 1.5 BSM — Battery Status Message (Table A.11)

| Field | Byte | Factor | Code |
|---|---|---|---|
| Max cell voltage | 0-1 | 0.01 V | `encode_signal(d, 0, 16, max_v, 0.01, 0.0)` ✅ |
| Max voltage cell no. | 2 | — | `d[2] = max_v_grp` ✅ |
| Min cell voltage | 3-4 | 0.01 V | `encode_signal(d, 24, 16, min_v, 0.01, 0.0)` ✅ |
| Min voltage cell no. | 5 | — | `d[5] = min_v_grp` ✅ |
| Max temp probe no. | 6 | — | `d[6] = max_t_grp` ✅ |

✅ **Correct** (matches the fix already applied for min_v_grp at byte 5).

---

### 1.6 BSD — Battery Stop Data (Table A.15)

| Field | Byte | Factor | Code |
|---|---|---|---|
| SOC | 0 | 1% | `d[0] = int(soc)` ✅ |
| Min cell voltage | 1-2 | 0.01 V | `encode_signal(d, 8, 16, min_v, 0.01, 0.0)` ✅ |
| Max cell voltage | 3-4 | 0.01 V | `encode_signal(d, 24, 16, max_v, 0.01, 0.0)` ✅ |
| Min temperature | 5 | 1 °C, −50 | `encode_signal(d, 40, 8, min_t, 1.0, -50.0)` ✅ |
| Max temperature | 6 | 1 °C, −50 | `encode_signal(d, 48, 8, max_t, 1.0, -50.0)` ✅ |

✅ **Correct.** 7-byte message, single CAN frame.

---

### 1.7 CML decode — Charger Max Limits (Table A.7)

| Field | Bits | Code |
|---|---|---|
| Max output voltage | 0-15 | `decode_signal(data, 0, 16, 0.1)` ✅ |
| Min output voltage | 16-31 | `decode_signal(data, 16, 16, 0.1)` ✅ |
| Max output current | 32-47 | `decode_signal(data, 32, 16, 0.1, -400.0)` ✅ |
| Min output current | 48-63 | `decode_signal(data, 48, 16, 0.1, -400.0)` ✅ |

✅ **Correct.**

---

### 1.8 CCS decode — Charger Charge Status (Table A.12) — INCOMPLETE

```python
@staticmethod
def decode_CCS(data: bytes) -> dict:
    return {
        'voltage': decode_signal(data,  0, 16, 0.1),
        'current': decode_signal(data, 16, 16, 0.1, -400.0),
        # MISSING:
        # bytes 4-5: cumulative charging time (1 min)
        # bytes 6-7: cumulative output energy (0.1 kWh)
    }
```

CCS is 8 bytes. Bytes 4–7 (cumulative time + energy) are decoded by nothing.
These are informational for a validator but the CSD cross-check (comparing charger-reported energy vs BMS-observed) cannot be done without them.

**Fix:**
```python
'cum_time_min':  int.from_bytes(data[4:6], 'little'),
'cum_energy_kwh': decode_signal(data, 48, 16, 0.1),
```

---

## 2. Timing Deviations from Standard

### 2.1 CCS cycle: 50 ms instead of 250 ms  — **NON-CONFORMANT**

GB/T 27930 §10.2.3 specifies CCS cycle = **250 ms**.

```python
# ChargerSimulator._charging_phase
ccs_period = 0.8 if self.faults['slow_ccs'] else 0.050   # ← should be 0.250
for cycle in range(cycles):
    ...
    self._send(self.cid.CCS, bytes(ccs))
    time.sleep(ccs_period)
```

`0.050` s = 50 ms. This is 5× faster than spec.

Impact: BMS `_rx_CCS` updates `sim_current` and `sim_soc` on every CCS. At 50 ms the BMS state advances 5× faster than a real charger would cause. SOC will hit target prematurely in demo mode.

**Fix:** Change to `0.250` for normal, `0.8` for fault (slow CCS).

---

### 2.2 BCS priority: 7 (lowest) instead of 6

GB/T 27930 specifies J1939 priority **6** for BCS.

```python
# DEMO_CID
BCS = j1939_id(PGN._BCS, SA_BMS, SA_CHARGER, prio=7)   # ← should be prio=6
```

Same issue in `SOCKET2_CID.BCS = 0x1C1155F5` — leading `0x1C` = priority 7.

| Priority | Binary | Hex prefix |
|---|---|---|
| 6 | 110 | 0x18xxxxxx |
| 7 | 111 | 0x1Cxxxxxx |

**Fix:** `j1939_id(PGN._BCS, SA_BMS, SA_CHARGER, prio=6)` → CAN ID prefix becomes `0x18`.

---

### 2.3 CML / CRO timing in parameter phase

GB/T 27930 Table D.1:  
- CML cycle: **250 ms** during parameter and ready phases  
- CRO cycle: **250 ms**  
- CTS cycle: **500 ms**

Charger simulator:
```python
# Loop 2 in _parameter_phase
if (now - last_cml) >= 0.250:   # CML 250ms ✅
    self._send(self.cid.CML, ...)
if (now - last_cts) >= 0.500:   # CTS 500ms ✅
    self._send(self.cid.CTS, ...)
self._send(self.cid.CRO, cro_unready)
time.sleep(0.25)                # CRO ~250ms ✅
```

✅ **Timing correct.**

---

### 2.4 BCL / BCS / BSM timing in charging phase

GB/T 27930 §10.2.3:
- BCL: **50 ms**  
- BCS: **250 ms**  
- BSM: **250 ms**

Code `_periodic_loop`:
```python
self._send(self.cid.BCL, bcl)            # every iteration
if now - last_bcs >= 0.250:              # BCS 250ms ✅
    self._send_app("BCS", ...)           
    self._send(self.cid.BSM, bsm)        # BSM tied to BCS 250ms ✅
time.sleep(0.050)                        # BCL 50ms ✅
```

✅ **BCL/BCS/BSM timing correct.**

---

## 3. State Machine Sequence vs Standard Appendix A

### 3.1 BHM stop condition

GB/T 27930 Appendix A: BHM must stop when the BMS receives the first CRM (either 0x00 or 0xAA).

Code: `_stop_bhm_periodic()` is called inside `_rx_CRM` before branching on ack value. ✅

---

### 3.2 BRM — recognition loop

GB/T 27930 §10.1.3: BMS responds to CRM=0x00 by continuously sending BRM (multi-packet) until charger acknowledges with CRM=0xAA.

Code: `_start_brm_periodic()` loop sends BRM via RTS/CTS, waits for EOM, sleeps 500 ms, repeats. Stops only when `_brm_running=False` (set by CRM=0xAA handler). ✅

---

### 3.3 BCP vs CTS order

GB/T 27930 Table D.1: Charger sends CTS (time sync), BMS sends BCP, charger sends CML.

Actual observed behaviour with some real chargers: CRM=0xAA triggers CTS before BCP arrives. The code starts BCP on CRM=0xAA and handles CTS whenever it arrives (CTS handler just advances state, BCP thread continues independently). This is correct.

---

### 3.4 BRO sequence

GB/T 27930 §10.2.1:
1. BMS starts sending BRO=0x00 after receiving CML  
2. BMS switches to BRO=0xAA when ready  
3. Charger sends CRO=0x00 while BRO=0x00, then CRO=0xAA when BRO=0xAA

Code:
- `_rx_CML` → sends immediate BRO=0x00, starts periodic loop (5 × BRO=0x00 then auto-flip to 0xAA)  
- `_rx_CRO(ready=False)` → logs; BRO loop already handles the flip  
- `_rx_CRO(ready=True)` → stops BRO loop, enters CHARGING  

✅ **Sequence correct.**

---

### 3.5 BSM — start condition

GB/T 27930 Table D.1: BSM starts transmitting after the **first CCS is received**.

Code:
```python
def _rx_CCS(self, data):
    ...
    if not getattr(self, '_bsm_started', False):
        self._bsm_started = True
        self._log("First CCS received — BSM transmission enabled")
```

However, BSM is sent in `_periodic_loop` regardless of whether `_bsm_started` is True:

```python
# _periodic_loop sends BSM inside the BCS 250ms block:
if now - last_bcs >= 0.250:
    self._send_app("BCS", ...)
    self._send(self.cid.BSM, bsm)   # sent even before first CCS
```

❌ **BSM is transmitted from the moment CHARGING state begins, not from the first CCS.**
`_bsm_started` is set but never checked before transmitting BSM.

**Fix:** Guard the BSM send:
```python
if now - last_bcs >= 0.250:
    ...
    if getattr(self, '_bsm_started', False):
        self._send(self.cid.BSM, bsm)
```

---

### 3.6 BST reason bits (Table A.16)

GB/T 27930 BST byte 0:

| Bit | Meaning |
|---|---|
| 0 | SOC reached (1=yes) |
| 2 | Fault (1=fault) |
| 4 | Connector over-temperature |
| 6 | BMS insulation fault |

Code: `BST(reason=0x01)` → bit 0 set = SOC reached. ✅

---

### 3.7 BEM — never transmitted

GB/T 27930 §10.x: BMS shall transmit BEM when it detects charger-side timeouts (CRO not received, CCS not received, etc.).

`BMSMessages.BEM()` is defined but `VirtualBMS` never calls it. The timeout detection logic that should trigger BEM does not exist.

**Impact:** A real charger may keep waiting for BEM as a fault acknowledgement. For a validator this is an informational gap.

---

## 4. Source Address Assignments

GB/T 27930-2015 Annex B:

| Gun | Charger SA | BMS SA |
|---|---|---|
| Gun 1 | 0x56 | 0xF4 |
| Gun 2 | 0x55 | 0xF5 |

Code:
- `DEMO_CID`: SA_CHARGER=0x56, SA_BMS=0xF4 ✅
- `SOCKET2_CID`: SA_CHARGER=0x55, SA_BMS=0xF5 ✅

---

## 5. J1939 Priority Assignments

GB/T 27930 priority assignments:

| Message | Standard Priority | Code Priority |
|---|---|---|
| CHM, BHM, CRM, BRM, CTS, BCP, CML, CCS | 6 | 6 ✅ |
| CRO, BRO, CST, BST | 4 | 4 ✅ |
| BCL | 6 | 6 ✅ |
| **BCS** | **6** | **7 ❌** |
| BSD, CSD, BEM, CEM | 6 | 6 ✅ |

Only BCS uses the wrong priority (7 instead of 6).

---

## 6. Multi-packet Messages Summary

| Message | Size | TP required | Code |
|---|---|---|---|
| BRM | 49 B | Yes (RTS/CTS) | `send_rts` ✅ |
| BCP | 13 B | Yes (RTS/CTS) | `send_rts` ✅ |
| BCS | 9 B | Yes (RTS/CTS) | `send_rts` ✅ |
| BSD | 7 B | No (single frame) | `_send` (via `_send_app` ≤ 8B path) ✅ |
| All others | ≤ 8 B | No | `_send` ✅ |

---

## 7. Summary

### Non-Conformances (affects real charger interoperability)

| # | Severity | Finding |
|---|---|---|
| NC-1 | **High** | CCS cycle 50 ms (code) vs 250 ms (standard §10.2.3) |
| NC-2 | **Medium** | BSM starts at CHARGING entry, not at first CCS receipt (Table D.1) |
| NC-3 | **Medium** | BCL mode always CC (1); no CV (0) switch during taper phase |
| NC-4 | **Low** | BCS J1939 priority 7 instead of 6 |
| NC-5 | **Low** | BEM never transmitted on timeout conditions |

### Decode Gaps (validator coverage)

| # | Finding |
|---|---|
| DG-1 | `decode_CCS` missing cumulative time (bytes 4-5) and energy (bytes 6-7) |

### Correctly Implemented

- All message byte/bit layouts: BHM, BCP, BCL, BCS, BSM, BSD, CML, CRO, CCS (partial), CST, CSD, BST  
- CHM/BHM handshake and BHM stop on CRM  
- CRM=0x00 → BRM loop → CRM=0xAA → BCP sequence  
- BRO=0x00 → BRO=0xAA on CML, CRO=0xAA triggers charging  
- BCL 50 ms / BCS 250 ms / BSM 250 ms cycle times  
- J1939 TP (RTS/CTS) for BRM, BCP, BCS  
- Source addresses per Annex B  
- BST reason bit 0 for SOC-reached stop  
- CST/BSD/CSD stop sequence  
