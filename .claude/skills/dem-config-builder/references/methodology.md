# DEM Configuration Methodology

## Overview

DEM (Diagnostic Event Manager) is an AUTOSAR Classic module that manages the runtime behavior of diagnostic events, including debouncing, fault confirmation, healing, memory allocation, and OBD freeze frame capture. The DEM Configuration Workbook bridges the DTC catalog (defined in ODX or similar) and the runtime event handling.

## Key Concepts

### Events vs. DTCs

- **DTC** (Diagnostic Trouble Code): A static identifier defined in the diagnostic specification (e.g., P0100). Defines the "what".
- **Event**: An AUTOSAR runtime construct that manages the state machine and behavior of a DTC. Defines the "how".

Each DTC is mapped to exactly one DEM Event.

### Debounce Logic

Debouncing prevents false fault reports due to electrical noise or transient conditions. DEM uses a counter-based approach:

**Pre-Passed State**: Fault condition is not met.
- Counter increments toward pre-passed threshold (typically 0-10 counts).
- Once threshold reached, event transitions to **Passed** state.

**Confirmed State**: Fault condition persists.
- Counter increments toward confirmed threshold (typically 3-20 counts).
- Once threshold reached, event transitions to **Confirmed** state.
- Confirmed state triggers DTC storage and freeze frame capture (if OBD enabled).

**Healing State**: Fault condition clears after confirmed.
- Counter increments toward healed threshold (typically 40-80 counts).
- Once threshold reached, event returns to **Passed** state.
- Healing may be optional depending on vehicle safety requirements.

### Memory Allocation

DEM manages two primary memory regions:

**Primary Memory**: 
- Stores active and confirmed events (NvM-backed).
- Survives power loss (persistent).
- Limited size (typically 1-4 KB).

**Secondary Memory**:
- Optional; stores aging/statistical data.
- Survives power loss.
- Smaller than primary.

**Mirror Memory**:
- Optional; used for redundant storage of critical events.
- Adds safety margin at the cost of memory.

### Snapshot and Extended Data Records (EDR)

When an event is confirmed:

**Snapshot Record**: 
- Captures specific data values at the moment of DTC confirmation.
- Helps diagnose the root cause.
- Example: Engine RPM, coolant temperature, fuel pressure at DTC trigger.

**Extended Data Record**:
- Captures additional context (e.g., freeze frame counter, aging counters).
- Helps track event history and aging.

### OBD Freeze Frame

OBD-II requires:
- **Freeze Frame**: A snapshot of data when DTC first confirms.
- Storage: Frame 0 (mandatory), Frames 1-4 (optional).
- Data: Mandatory PIDs + optional PIDs from the standard list.

### Aging Cycles

After a confirmed fault is healed (clears), DEM maintains an aging counter:
- Increments each operation cycle (ignition cycle, warmup cycle, etc.).
- After N cycles (typically 40-80), the event is considered "aged" and removed from memory.
- Allows temporary fault codes to disappear over time.

## Authoring Workflow

1. **Extract DTC Catalog**: Gather all DTC definitions from diagnostic specification (ODX, ASAP2, etc.).
2. **Map DTC to Events**: Create a 1-to-1 mapping of DTC → DEM Event ID.
3. **Define Debounce Thresholds**: Set pre-passed, pre-confirmed, confirmed, and healed counters for each event.
   - Pre-passed: 5-10 (quick acceptance of good signal)
   - Pre-confirmed: 3-5 (quick confirmation of fault)
   - Confirmed: 1-20 (depends on safety criticality; ASIL D may need 1)
   - Healed: 40-80 (slower healing to avoid flutter)
4. **Allocate Memory**: Determine primary and secondary memory size based on event count and snapshot/EDR data.
5. **Define Snapshot Classes**: For each event, list data to capture at DTC confirmation.
6. **Define EDR Classes**: For each event, list additional diagnostic data (optional).
7. **Map to NvM**: Assign each event to a persistent NvM block for storage.
8. **Configure Aging**: Set aging thresholds per event or use a default (e.g., 40 cycles).
9. **Define Operation Cycles**: Specify what constitutes an operation cycle (ignition, warmup, etc.).
10. **Configure OBD**: Enable/disable freeze frame, set capture triggers.

## Debounce Strategy Examples

### Quick Response (High Sensitivity)
Used for safety-critical events where false negatives are worse than false positives.
```
Pre-Passed: 1
Pre-Confirmed: 1
Confirmed: 1
Healed: 40
```
FTC = 3 engine cycles (1+1+1) to confirm, 40 cycles to heal.

### Robust (Low False Positive Rate)
Used for non-critical events where robustness against noise is paramount.
```
Pre-Passed: 10
Pre-Confirmed: 5
Confirmed: 10
Healed: 80
```
FTC = 25 cycles (10+5+10) to confirm, 80 cycles to heal.

### Balanced (Default)
General-purpose debounce for most events.
```
Pre-Passed: 5
Pre-Confirmed: 3
Confirmed: 5
Healed: 40
```
FTC = 13 cycles (5+3+5) to confirm, 40 cycles to heal.

## Memory Calculation

Event storage requirement per event (typical):
- Event status: 1 byte (state machine, enable/disable)
- Counters: 2 bytes (pre-passed, pre-confirmed, confirmed, healed)
- Snapshot data: variable (1-64 bytes depending on data size)
- EDR data: variable (0-32 bytes if used)

Example:
- 64 events × 4 bytes (minimum) = 256 bytes
- + 64 events × 20 bytes (snapshot avg) = 1280 bytes
- Total: ~1.5 KB primary memory

Secondary memory: typically 50% of primary (for aging statistics, occurrence counter, etc.).

## Integration with DTC Catalog

The DEM Configuration references an external DTC catalog (often from ODX or ASAP2). The workflow is:

1. ODX Builder produces ODX with DTC definitions.
2. DEM Config Builder consumes the DTC list and adds runtime behavior.
3. DEM Config feeds back to calibration tools and diagnostic testers.

## Key Compliance Points

For a DEM configuration to be audit-ready:
- [ ] Every DTC has a mapped DEM Event
- [ ] All events have valid debounce thresholds (within reasonable ranges)
- [ ] Primary and secondary memory allocation is adequate
- [ ] All confirmed events have snapshot or EDR defined
- [ ] OBD freeze frame is enabled (if vehicle is OBD-compliant)
- [ ] Aging cycles are documented
- [ ] Operation cycle definition is clear
- [ ] NvM block mapping is complete and non-overlapping

## AUTOSAR SWS_Dem Compliance

The workbook ensures compliance with:
- **SWS_Dem.EB.DEBOUNCE**: Debounce mechanism selection and thresholds
- **SWS_Dem.EB.EVENTMEMORYDESTINATION**: Primary/secondary memory routing
- **SWS_Dem.EB.SNAPSHOTRECORDCLASS**: Snapshot record structure
- **SWS_Dem.EB.EXTENDEDDATARECORD**: EDR class definition
- **SWS_Dem.EB.OBDFREEZEFRAMECAPTURE**: OBD freeze frame trigger and storage
- **SWS_Dem.EB.OPERATIONCYCLETYPE**: Cycle definition for aging

## Production Readiness Checklist

- [ ] DEM configuration matches DTC catalog version
- [ ] Debounce thresholds validated by system engineering
- [ ] Memory footprint verified against ECU RAM budget
- [ ] NvM block IDs do not conflict with other modules
- [ ] OBD freeze frame configuration matches regulatory requirements (if applicable)
- [ ] Aging strategy aligns with vehicle product requirements
- [ ] Configuration tested in HIL and vehicle testing
