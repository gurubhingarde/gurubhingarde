# DBC Methodology

A DBC (CAN Database) file is the authoritative specification of a Controller Area Network. The DBC Builder workbook organizes this specification across 11 tabs to support implementation, audit, and ISO 11898 / AUTOSAR compliance.

## The 11-Tab Structure

**Tab 00 — Title Page**: Project metadata, document ID, revision, approvers, and network scope.

**Tab 01 — Document Control**: Revision history and distribution list, per ISO 26262 or quality document conventions.

**Tab 02 — ECU Inventory**: List of all Electronic Control Units (nodes) on the network, including manufacturer, software version, and functional scope.

**Tab 03 — Message Catalog**: All CAN messages with:
- Message ID (11-bit or 29-bit hex)
- DLC (Data Length Code: payload in bytes, 0–8 for CAN 2.0, up to 64 for CAN FD)
- Cycle time (in milliseconds, for periodic messages)
- Sender ECU and frame type (Standard / Extended)
- Transmission type (cyclic, event-driven, or spontaneous)

**Tab 04 — Signal Catalog**: Every signal with:
- Bit position (start bit, using CAN bit numbering: bit 0 is LSB of byte 0)
- Bit length (1–64 bits)
- Byte order (little-endian / big-endian Motorola format)
- Encoding: scale, offset, min, max, unit
- Receivers (ECU nodes that consume this signal)
- Multiplexor references (for multiplexed signals)

**Tab 05 — Signal-to-Message Mapping**: Cross-reference showing each signal's parent message and bit position range (e.g., "bits 16–23").

**Tab 06 — Value Tables**: Discrete value enumerations for state signals (e.g., GearPosition: 0=Park, 1=Reverse, 2=Neutral, 3=Drive).

**Tab 07 — Signal Group Definitions**: Multiplexed signal groups and their multiplexor conditions. A multiplexor signal's value determines which other signals are active in that message.

**Tab 08 — Network Topology**: Message flow diagram in tabular form: sender, message ID, receivers, and cycle time. Used for network load and routing analysis.

**Tab 09 — Validation Rules**: Consistency checks applied to the specification:
- Unique message IDs
- No signal bit overlap within a message
- Signal bits fit within DLC
- Every signal belongs to a message
- Multiplexor signals are defined

**Tab 10 — References**: Standard citations (ISO 11898, CAN 2.0A/2.0B, J1939, AUTOSAR, DBC format).

## CAN Message Structure

A CAN 2.0A message carries 11-bit identifiers; CAN 2.0B (Extended) uses 29-bit IDs. Both can appear on the same physical bus (frames flagged by an IDE bit). Each message has:
- **ID**: Identifier (unique within network)
- **DLC**: Payload size in bytes (0–8 for CAN 2.0; 0–64 for FD)
- **Data**: 0–8 bytes of payload
- **Sender**: One ECU that transmits this message
- **Receivers**: Zero or more ECUs that consume it

## Signal Encoding

A signal occupies a contiguous range of bits within a message payload. Encoding is defined by:

- **Bit Start**: The first bit occupied by the signal (CAN bit numbering: byte 0 bits 0–7, byte 1 bits 8–15, etc.)
- **Bit Length**: Number of bits (1–64 for CAN FD)
- **Byte Order**: 
  - **Little-endian (Intel)**: Least-significant bit first; common in automotive
  - **Big-endian (Motorola)**: Most-significant bit first
- **Scaling**: `physical_value = raw_value × scale + offset`
  - Example: RPM signal with scale=0.25, offset=0 means raw value 4000 → 1000 RPM
- **Min/Max**: Physical value range for validation
- **Unit**: Engineering unit (rpm, km/h, °C, %, etc.)

### Value Tables

State signals often use enumerated values rather than continuous scaling:
```
GearShift_Position:
  0 = Park (P)
  1 = Reverse (R)
  2 = Neutral (N)
  3 = Drive (D)
  4 = Sport (S)
```

## Multiplexing

A multiplexed message contains different signal sets based on a multiplexor signal's value. Example:

- Message: EngineStatus (ID 0x100)
  - Signal: GearSelection (multiplexor)
  - If GearSelection = 0 (Park):
    - Signals present: EngineRPM, EngineTemp, IdleVoltage
  - If GearSelection = 3 (Drive):
    - Signals present: EngineRPM, EngineTemp, VehicleSpeed, TorqueCommand

This reduces message payload and makes the network more efficient.

## Naming Conventions

- **Message IDs**: Hexadecimal, padded to 3 digits (0x000–0x7FF for 11-bit; 0x00000000–0x1FFFFFFF for 29-bit)
- **Signal names**: CamelCase, no spaces (e.g., EngineSpeed, BrakePercentApplied)
- **ECU names**: UpperCamelCase (e.g., ECM, TCM, BCM, ABS)
- **Units**: SI or common automotive (rpm, km/h, °C, %, V, A, Nm, Pa, etc.)

## Validation Checklist

Before releasing a DBC specification:
1. Every message has a unique ID
2. Every signal belongs to exactly one message
3. No signal bits overlap within a message
4. Signal bit ranges do not exceed message DLC
5. Scale and offset are dimensionally correct
6. Min and max values are physically sensible
7. All multiplexor signals are explicitly defined
8. All signal receivers are defined ECUs
9. Cycle times are realistic (10 ms for safety-critical; 100+ ms for status)
10. Value tables cover all possible states
