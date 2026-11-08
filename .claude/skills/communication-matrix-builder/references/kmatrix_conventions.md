# K-Matrix Naming and Conventions

## Message ID Convention

### CAN Classical
- Format: 0x[HHH] (3 hex digits, 0x000 to 0x7FF for 11-bit identifiers)
- Allocation strategy:
  - 0x000-0x0FF: Powertrain messages
  - 0x100-0x1FF: Chassis messages
  - 0x200-0x2FF: Body messages
  - 0x300-0x3FF: ADAS messages
  - 0x400-0x4FF: Infotainment messages
  - 0x500-0x7FF: Reserved and diagnostics

### CAN FD
- Format: Same as CAN classical with extended payload (up to 64 bytes)
- Prefix message names with "FD_" for clarity (e.g., FD_ADASPerception)

### LIN
- Format: 0-59 (linear addressing per LIN 2.x spec)
- Cluster-specific: LIN1, LIN2, etc.

## Signal Naming Convention

Format: `[SystemPrefix]_[FunctionName]_[Property]`

Examples:
- `PT_EngineSpeed` (Powertrain system, engine speed signal)
- `CH_BrakePressure` (Chassis system, brake pressure)
- `BD_DoorLock` (Body system, door lock)
- `AD_ObjectRange` (ADAS system, object detection range)

## ECU ID Scheme

Format: `ECU[NNNX]` where:
- N = sequential number
- X = optional function letter (P=Powertrain, C=Chassis, B=Body, A=ADAS)

Examples:
- ECU001P (Powertrain control module)
- ECU002C (Chassis control module)
- ECU003B (Body control module)
- ECU004A (ADAS sensor fusion)
- ECU005G (Gateway)

## Bus Type Abbreviations

- CAN: Classical CAN 2.0B
- CFD: CAN FD
- LIN: Local Interconnect Network
- FLX: FlexRay
- ETH: Automotive Ethernet

## Cycle Time Standards

- 1 ms: High-priority control signals (steering, braking)
- 5-10 ms: Engine control, transmission
- 20-50 ms: Sensor telemetry, diagnostics
- 100+ ms: Status monitoring, infotainment

## Signal Type Mapping

| Type | Range | Description |
|------|-------|-------------|
| uint8 | 0-255 | Unsigned 8-bit |
| uint16 | 0-65535 | Unsigned 16-bit |
| int16 | -32768-32767 | Signed 16-bit |
| uint32 | 0-4294967295 | Unsigned 32-bit |
| float | IEEE 754 | Single precision |
| bool | 0-1 | Boolean flag |

## Endianness Conventions

- **Motorola (Big-Endian)**: Most significant byte first; common in automotive
- **Intel (Little-Endian)**: Least significant byte first; used in CAN FD
- Always specify explicitly in signal definitions
