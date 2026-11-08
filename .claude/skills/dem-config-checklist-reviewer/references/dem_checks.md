# DEM Checklist — Check Definitions and Rationale

## Event Definition Checks (E1-E3)

### E1: DTC-to-Event Mapping Complete
**Obligation**: MUST | **Confidence**: High

Every DTC in the catalog must map to exactly one DEM Event. A missing mapping means a fault code cannot be stored or reported by DEM.

**Check**: Compare DTC list (from ODX or catalog) against Event Inventory sheet.
- All DTCs have events → **Rating: FC**
- 1-2 missing DTCs → **Rating: LC**
- 3+ missing DTCs → **Rating: NC**

---

### E2: Event Inventory Completeness
**Obligation**: MUST | **Confidence**: High

All configured events should be enumerated in the Event Inventory sheet. This ensures visibility and traceability.

**Check**: Count unique event IDs. Verify Event Inventory tab lists all of them.
- All events listed → **Rating: FC**
- Missing 1-2 events from tab → **Rating: LC**
- Missing 3+ events → **Rating: NC**

---

### E3: Event ID Uniqueness
**Obligation**: MUST | **Confidence**: High

No two events should share the same Event ID. Duplicate IDs cause memory corruption and loss of diagnostic data.

**Check**: Extract all event IDs from Event Inventory. Check for duplicates.
- No duplicates → **Rating: FC**
- 1-2 duplicates detected → **Rating: LC**
- 3+ duplicates → **Rating: NC**

---

## Debounce Configuration Checks (E4-E7)

### E4: Pre-Passed Threshold Range
**Obligation**: SHOULD | **Confidence**: High

Pre-passed threshold should be 5-10 counts, allowing quick acceptance of a good signal after a transient fault.

**Check**: Extract pre-passed values from Debounce Configuration sheet.
- All values in 5-10 range → **Rating: FC**
- 80% in range, 1-2 outliers → **Rating: LC**
- <80% in range or outliers >20 → **Rating: PC**

**Rationale**: Too low (<5) may accept noise; too high (>10) may reject good signals.

---

### E5: Pre-Confirmed Threshold Range
**Obligation**: SHOULD | **Confidence**: High

Pre-confirmed threshold should be 3-5 counts, balancing quick confirmation against transient immunity.

**Check**: Extract pre-confirmed values from Debounce Configuration sheet.
- All values in 3-5 range → **Rating: FC**
- 80% in range → **Rating: LC**
- <80% in range → **Rating: PC**

---

### E6: Confirmed Threshold Range
**Obligation**: MUST | **Confidence**: High

Confirmed threshold depends on ASIL:
- **ASIL D**: 1 count (immediate confirmation for safety)
- **ASIL C**: 1-5 counts
- **ASIL B/QM**: 5-20 counts

**Check**: Extract confirmed values. Cross-check against ASIL mapping (if available).
- All values appropriate for ASIL → **Rating: FC**
- 1-2 out-of-range values → **Rating: LC**
- 3+ significantly out-of-range → **Rating: NC**

**Non-Compliance**: If ASIL D event has confirmed > 1 → **Rating: NC**

---

### E7: Healed Threshold Range
**Obligation**: SHOULD | **Confidence**: High

Healed threshold should be 40-80 counts, ensuring slow healing to prevent DTC flutter (false clear/set cycles).

**Check**: Extract healed values from Debounce Configuration sheet.
- All values in 40-80 range → **Rating: FC**
- 80% in range, 1-2 <40 or >80 → **Rating: LC**
- <80% in range or many values <20 → **Rating: PC**

**Rationale**: Too low (<30) risks DTC flutter; too high (>100) may frustrate users.

---

## Safety and Event Marking Checks (E8-E10)

### E8: Safety-Critical Event Marking
**Obligation**: SHOULD | **Confidence**: Medium

Events related to ASIL functions (safety-critical faults) should be marked as safety-relevant.

**Check**: Identify ASIL functions from system design. Check Event Inventory for safety flag.
- All ASIL events marked → **Rating: FC**
- 80% marked, 1-2 missed → **Rating: LC**
- <80% marked or significant gaps → **Rating: PC**

**Note**: Marking may be implicit (event ID convention) or explicit (safety_flag column).

---

### E9: Event Enable/Disable Consistency
**Obligation**: SHOULD | **Confidence**: Medium

All events should be enabled unless explicitly disabled with documented rationale.

**Check**: Look for disabled events. Verify each has a rationale (comment or disable_reason field).
- All enabled (normal) → **Rating: FC**
- Disabled events have rationale → **Rating: FC**
- Disabled event(s) without rationale → **Rating: LC**
- Many disabled events, unclear why → **Rating: PC**

---

### E10: Debounce Strategy Consistency
**Obligation**: SHOULD | **Confidence**: Medium

Events within the same functional domain should use consistent debounce thresholds to prevent surprises.

**Check**: Group events by functional domain (Powertrain, Emission, ABS, etc.). Compare debounce within each group.
- Consistent within domains (±1 count variance) → **Rating: FC**
- Mostly consistent, 1-2 outliers → **Rating: LC**
- Inconsistent or random variation → **Rating: PC**

**Rationale**: Consistency helps technicians understand diagnostic behavior across the ECU.

---

## Memory Allocation Checks (M1-M3)

### M1: Primary Memory Allocation Defined
**Obligation**: MUST | **Confidence**: High

Primary memory size must be explicitly specified in the Memory Allocation sheet.

**Check**: Verify primary_memory or primary_size_bytes field is present and non-zero.
- Present and >512 bytes → **Rating: FC**
- Present but <512 bytes → **Rating: PC** (too small)
- Missing → **Rating: NC**

**Typical range**: 512 bytes - 4 KB depending on event count.

---

### M2: Memory Adequacy for Event Count
**Obligation**: MUST | **Confidence**: High

Allocated memory must accommodate all events (baseline ~4 bytes per event, plus snapshot/EDR data).

**Check**: Calculate:
```
Min required = (event_count × 4) + (snapshot_count × 20) + (edr_count × 4)
```

Compare against allocated primary memory.
- Allocated > required × 1.1 (10% margin) → **Rating: FC**
- Allocated > required → **Rating: LC** (minimal headroom)
- Allocated < required → **Rating: NC** (overflow risk)

---

### M3: Secondary Memory Allocation
**Obligation**: SHOULD | **Confidence**: High

Secondary memory should be configured at ~50% of primary (for aging data, statistics).

**Check**: Verify secondary memory is defined and is 40-60% of primary.
- 50% ± 10% → **Rating: FC**
- 30-70% → **Rating: LC**
- Missing or <30% or >100% → **Rating: PC**

---

## NvM Storage Mapping Checks (M4-M5)

### M4: NvM Block Mapping Complete
**Obligation**: MUST | **Confidence**: High

Every event must be assigned to a persistent NvM block ID. Block mapping is mandatory for event persistence.

**Check**: Compare event count against NvM Block Mapping sheet entries.
- All events have block IDs → **Rating: FC**
- 1-2 events missing block IDs → **Rating: LC**
- 3+ events missing → **Rating: NC**

---

### M5: NvM Block ID Uniqueness
**Obligation**: MUST | **Confidence**: High

No two events should share the same NvM block ID (each event needs its own persistent storage).

**Check**: Extract all block IDs from NvM Block Mapping. Check for duplicates.
- No duplicates → **Rating: FC**
- 1-2 duplicates → **Rating: LC**
- 3+ duplicates → **Rating: NC**

---

## Memory Utilization Checks (M6-M10)

### M6: Memory Utilization vs. ECU Budget
**Obligation**: SHOULD | **Confidence**: Medium

DEM memory should not exceed 90% of available ECU memory (reserve headroom for other modules).

**Check**: Calculate:
```
DEM utilization = (primary + secondary) / total_available_memory
```

- <90% → **Rating: FC**
- 90-95% → **Rating: LC** (tight but acceptable)
- >95% → **Rating: PC** (too tight)

---

### M7: Mirror Memory Configuration
**Obligation**: MAY | **Confidence**: Medium

Mirror memory (redundant storage) is optional but recommended for safety-critical events.

**Check**: Check if mirror_enabled flag is set.
- Enabled and properly configured → **Rating: FC**
- Not enabled but not required → **Rating: NA**
- Required but missing → **Rating: LC**

---

### M8: Aging Counter Memory Allocation
**Obligation**: SHOULD | **Confidence**: Medium

Memory for aging counters (used for DTC healing) should be included in secondary memory allocation.

**Check**: Verify secondary memory calculation includes aging counter space.
- Aging memory included in secondary → **Rating: FC**
- Aging memory noted separately → **Rating: LC**
- No aging memory allocation mentioned → **Rating: PC**

---

### M9: Persistent Storage Redundancy
**Obligation**: SHOULD | **Confidence**: Low

Critical event memory should have redundancy mechanism (mirror memory or backup).

**Check**: Check for redundancy strategy in Memory Allocation or design documentation.
- Redundancy implemented → **Rating: FC**
- Not implemented but documented as not required → **Rating: NA**
- Missing and would be beneficial → **Rating: LC**

---

### M10: Memory Growth Margin
**Obligation**: SHOULD | **Confidence**: High

Reserve at least 15-20% memory headroom for future events and features.

**Check**: Calculate:
```
Growth margin = (allocated - used) / allocated
```

- >20% margin → **Rating: FC**
- 15-20% → **Rating: LC** (acceptable but tight)
- <15% → **Rating: PC** (insufficient)

---

## Snapshot Configuration Checks (S1-S4)

### S1: Snapshot Record Class Definition
**Obligation**: SHOULD | **Confidence**: Medium

Every confirmed event should have a snapshot record class defined.

**Check**: Compare events in Event Inventory against Snapshot Record Class sheet.
- All confirmed events have snapshots → **Rating: FC**
- 80% have snapshots → **Rating: LC**
- <80% have snapshots → **Rating: PC**

---

### S2: Snapshot Data Adequacy
**Obligation**: SHOULD | **Confidence**: Medium

Snapshot should capture 4-8 data elements, total 8-32 bytes, to aid diagnosis without excessive storage.

**Check**: For each snapshot, count data elements and estimate total bytes.
- 4-8 elements, 8-32 bytes → **Rating: FC**
- 3 elements or <8 bytes → **Rating: LC** (may be insufficient)
- >8 elements or >32 bytes → **Rating: LC** (wasteful)

---

### S3: Extended Data Record (EDR) Definition
**Obligation**: MAY | **Confidence**: Low

EDR records (occurrence counter, timestamp, aging counter) are optional but helpful.

**Check**: Check for EDR Class sheet or similar.
- EDR defined for key events → **Rating: FC**
- Not implemented but documented → **Rating: NA**
- Could be helpful but missing → **Rating: LC**

---

### S4: EDR Data Completeness
**Obligation**: SHOULD | **Confidence**: Medium

EDR should include at least:
1. Fault occurrence counter
2. Aging counter (or max aging counter)
3. Timestamp (if RTC available)

**Check**: Examine EDR configuration.
- All three components present → **Rating: FC**
- 2 of 3 components → **Rating: LC**
- <2 components → **Rating: PC**

---

## OBD Freeze Frame Checks (S5-S7)

### S5: OBD Freeze Frame Enabled
**Obligation**: MUST | **Confidence**: High

OBD-relevant events (emissions, powertrain) must have freeze frame capture enabled.

**Check**: Check OBD Freeze Frame Layout sheet or obd_config flag.
- Enabled for OBD events → **Rating: FC**
- Not enabled but vehicle not OBD-compliant → **Rating: NA**
- Should be enabled but isn't → **Rating: NC**

---

### S6: OBD Frame 0 Configuration
**Obligation**: MUST | **Confidence**: High

Frame 0 (mandatory frame) must define required OBD PIDs.

**Check**: Verify Frame 0 captures PIDs per SAE J1979 standard.
- All mandatory PIDs captured → **Rating: FC**
- Most PIDs captured → **Rating: LC**
- Missing key PIDs → **Rating: NC**

---

### S7: OBD Additional Frames (1-4)
**Obligation**: MAY | **Confidence**: Low

Optional frames may be configured for extended diagnostic data (not required by standard).

**Check**: Check if frames 1-4 are configured.
- Configured and make sense → **Rating: FC**
- Not configured (acceptable) → **Rating: NA**
- Partially configured → **Rating: LC**

---

### S8: Safety-Critical Event Snapshots
**Obligation**: MUST | **Confidence**: High

All ASIL C/D events must have snapshot records defined for safety-critical diagnostics.

**Check**: Cross-check ASIL mapping against Snapshot Record Class.
- All ASIL C/D events have snapshots → **Rating: FC**
- 1-2 ASIL events missing snapshots → **Rating: LC**
- 3+ ASIL events missing snapshots → **Rating: NC**

---

## End-to-End Compliance Checklist

For a DEM configuration to be audit-ready, at minimum:
- [ ] E1 (DTC-to-event mapping): FC or LC
- [ ] E3 (event ID uniqueness): FC
- [ ] E6 (confirmed threshold): FC
- [ ] E7 (healed threshold): FC
- [ ] M1 (primary memory): FC
- [ ] M2 (memory adequacy): FC
- [ ] M4 (NvM mapping): FC
- [ ] M5 (NvM uniqueness): FC
- [ ] S5 (OBD freeze frame): FC or NA
- [ ] S6 (OBD frame 0): FC or NA
- [ ] S8 (safety-critical snapshots): FC or NA
