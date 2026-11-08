# DEM Configuration Conventions and Best Practices

## Naming Conventions

### Event IDs
Event IDs should map directly to DTC numbers for clarity:
```
P0100 → Event 0x0100 or DemEventId_P0100
P0101 → Event 0x0101 or DemEventId_P0101
U0001 → Event 0xF401 or DemEventId_U0001
```

### NvM Block IDs
Allocate a contiguous block ID range for DEM events:
```
0x01 - 0x40: DEM Event 0 - 63
0x41 onwards: Other modules (BSW/application)
```

### Snapshot Class Names
Use semantic naming:
```
SnapshotClass_Engine = {RPM, Temp, Pressure}
SnapshotClass_Transmission = {GearPos, TorqueReq, PressureFilter}
SnapshotClass_ABS = {WheelSpeed_FL, WheelSpeed_FR, ...}
```

## Debounce Threshold Guidelines

### Safety-Critical Events (ASIL C/D)
Faster confirmation to detect failures quickly:
```
Pre-Passed: 1-3
Pre-Confirmed: 1-2
Confirmed: 1
Healed: 40-80 (slower healing to prevent flutter)
```

### Non-Critical Events (QM)
More robust against noise:
```
Pre-Passed: 5-10
Pre-Confirmed: 3-5
Confirmed: 5-10
Healed: 40-80
```

### Default Template
Use this as a starting point:
```
Pre-Passed: 5
Pre-Confirmed: 3
Confirmed: 5
Healed: 40
```

## Memory Allocation Standards

### Minimum Memory Budget
- Baseline (no snapshot/EDR): 256 bytes
- Per event (~4 bytes): 64 events = 256 bytes
- **Primary total**: 512 bytes minimum

### Typical Memory Budget
- 64 events × 20 bytes (with snapshot) = 1.28 KB
- + 20% overhead = **~1.5 KB primary**
- Secondary: 512-768 bytes (50% of primary)

### Maximum Density
- Avoid allocating >90% of available memory to DEM.
- Reserve 10% for future events and aging data.

## Snapshot Data Guidelines

### Mandatory Snapshots (for confirmed events)
Every confirmed DTC should capture at least:
- Current state or flag that triggered the fault
- Sensor reading or signal value that failed
- Engine speed (RPM) and load
- Ambient or operating conditions

### Typical Snapshot Size
- 4-8 data elements per snapshot
- 1-4 bytes per element
- Total: 8-32 bytes per snapshot

### Snapshot Class Allocation
```
SnapshotClass_Powertrain:
  - EngineSpeed (2 bytes)
  - EngineLoad (1 byte)
  - CoolantTemp (1 byte)
  - FuelPressure (2 bytes)
  Total: 6 bytes

SnapshotClass_Emission:
  - O2SensorVoltage (1 byte)
  - LambdaIntegrator (2 bytes)
  - CatConverterTemp (1 byte)
  Total: 4 bytes
```

## EDR (Extended Data Record) Guidelines

EDR captures statistical or meta data about the fault:
- Fault occurrence counter (how many times DTC triggered)
- First occurrence timestamp (if RTC available)
- Total aging counter
- ODX Data Identifier (DID) that reported the fault

Typical EDR size: 4-8 bytes per event.

## OBD Freeze Frame Configuration

### Frame 0 (Mandatory)
Captures data when DTC first confirmed:
```
Byte 0: Status Mask (supported/enabled/failure/confirmed)
Bytes 1-4: Engine Speed, Load, Coolant Temp, ...
(Minimum 4 bytes, max 6)
```

### Frames 1-4 (Optional)
Capture additional states if failure persists or occurs again.

### Freeze Frame Data Selection
Use standardized OBD PIDs:
- 0x01-0x20: Essential powertrain data
- 0x21-0x30: Emission control data
- 0x31-0x40: Auxiliary input/output
- 0x41-0x60: Standardized test results

## Operation Cycle Definition

### Ignition Cycle (Most Common)
- Starts at key ON
- Ends at key OFF
- Typically 1-10 minutes per cycle
- Used for aging counters

### Warmup Cycle
- Starts at cold engine (< 20C)
- Ends when engine reaches operating temp (80C)
- Typically 5-10 minutes
- Used for O2 sensor and catalyst monitors

### OBD Cycle (Per SAE J1979)
- Defined per regulation (EPA, CARB, EU)
- Typically 505 seconds @ 25 km/h average speed
- Must include warm-up, steady-state, and transient phases

## Healing Strategy Considerations

### Aggressive Healing (Fast)
- Threshold: 10-20 cycles
- Pros: Clears temporary faults quickly
- Cons: May reappear if condition persists, user confusion
- Use for: Non-critical electrical noise, sensor transients

### Conservative Healing (Slow)
- Threshold: 40-80 cycles
- Pros: Confirms fault is truly gone
- Cons: Codes persist longer, may frustrate user
- Use for: Safety-critical faults, emissions faults

### No Healing (Persistent)
- Threshold: Never
- Pros: Fault never auto-clears; forces technician diagnosis
- Cons: Service required to clear
- Use for: Permanent faults, warranty-related issues

## ASIL Mapping Guidelines

**ASIL D (Highest Integrity)**:
- Confirmed threshold: 1 cycle (immediate confirmation)
- Healing disabled or very long (> 100 cycles)
- Snapshot mandatory
- OBD freeze frame mandatory

**ASIL C**:
- Confirmed threshold: 1-5 cycles
- Healing: 40-80 cycles
- Snapshot mandatory
- OBD freeze frame mandatory

**ASIL B**:
- Confirmed threshold: 5-10 cycles
- Healing: 40-80 cycles
- Snapshot optional but recommended
- OBD freeze frame if applicable

**QM (Functional Safety Unrequired)**:
- Confirmed threshold: 5-20 cycles
- Healing: 40-80 cycles
- Snapshot optional
- OBD freeze frame if applicable

## Validation Checklist

- [ ] Event IDs match DTC numbers or use clear mapping
- [ ] NvM block IDs are unique and contiguous
- [ ] Debounce thresholds are within recommended ranges
- [ ] Memory allocation does not exceed available ECU RAM
- [ ] All safety-critical events have snapshots
- [ ] OBD freeze frame enabled for emissions-related events
- [ ] Aging thresholds align with vehicle requirements
- [ ] Operation cycle definition is unambiguous
- [ ] EDR configuration is complete for key events
- [ ] Configuration reviewed by system safety engineer
