# DBC Conventions and Signal Encoding Rules

## Byte Order (Endianness)

CAN signals can be stored in **little-endian** (Intel) or **big-endian** (Motorola) byte order. This determines how multi-byte values are distributed across the CAN frame.

### Little-Endian (Intel Format)
- Least significant byte (LSB) comes first
- Bit numbering: bit 0 is the rightmost bit of the first byte
- Common in automotive (AUTOSAR default)
- Example: 16-bit value 0x1234
  - Byte 0: 0x34 (LSB)
  - Byte 1: 0x12 (MSB)

### Big-Endian (Motorola Format)
- Most significant byte (MSB) comes first
- Bit numbering: bit 7 is the leftmost bit of the first byte
- Used in J1939 and some legacy systems
- Example: 16-bit value 0x1234
  - Byte 0: 0x12 (MSB)
  - Byte 1: 0x34 (LSB)

## Signal Types

### Unsigned Integer
- Range: 0 to (2^bit_length - 1)
- Used for counts, speeds, pressures (positive only)
- Example: 16-bit unsigned speed: 0–65535 km/h (with scaling)

### Signed Integer (Two's Complement)
- Range: -(2^(bit_length-1)) to (2^(bit_length-1) - 1)
- Used for temperatures, angles, accelerations (signed values)
- Example: 16-bit signed temperature: -32768 to 32767 raw (scaled to -50 to +50 °C)

### Floating Point (IEEE 754)
- 32-bit or 64-bit IEEE 754 single/double precision
- Used in advanced networks (CAN FD, high-precision data)
- Rarely used in low-bandwidth CAN 2.0

## Scaling and Offset

Physical value is computed from raw digital value:

```
physical_value = (raw_value × scale) + offset
```

### Example: Engine RPM
- Bit length: 16 bits unsigned
- Scale: 0.25
- Offset: 0
- Raw range: 0–65535
- Physical range: 0–16383.75 RPM
- Example: raw = 4000 → physical = (4000 × 0.25) + 0 = 1000 RPM

### Example: Engine Coolant Temperature
- Bit length: 8 bits signed
- Scale: 1
- Offset: -40
- Raw range: -128–127
- Physical range: -168–87 °C
- Example: raw = 60 → physical = (60 × 1) + (-40) = 20 °C

### Inverse Scaling (Receiver to Sender)
When a receiver must transmit a value, reverse the formula:

```
raw_value = (physical_value - offset) / scale
```

## Multiplexed Signals

A **multiplexor signal** in a message determines which other signals are valid in that frame.

### Structure
- One signal designated as the **multiplexor** (e.g., `GearPosition`)
- Multiple **multiplexed signal groups**, each with a condition on the multiplexor
- Example:
  ```
  Message: TransmissionStatus (ID 0x150, DLC 8)
    Signal: GearPosition (bits 0–3, multiplexor)
    Signal: TorqueCommand (bits 8–15, active if GearPosition in {2, 3, 4})
    Signal: LineVoltage (bits 16–23, active if GearPosition in {0, 1})
    Signal: FrictionLoss (bits 24–31, active always)
  ```

### Benefits
- Reduces message size by not transmitting irrelevant signals
- Improves network efficiency
- Supports conditional signal sets (e.g., engine data only when engine running)

### Implementation Caution
- Code generators must handle multiplexor values correctly
- Receivers must ignore signals outside their valid multiplex group
- Signal overlap is allowed only across different multiplex groups

## Value Tables (Enumerations)

For discrete state signals, define a mapping:

```
Signal: GearShift_Position
  0 = Park
  1 = Reverse
  2 = Neutral
  3 = Drive
  4 = Sport
  5 = Low
  Reserved/Undefined = 6–15
```

### Rules
- Use 0-based indexing
- Reserve undefined values at the end
- Document any "error" or "invalid" codes
- Avoid gaps unless they have meaning

## Message Cycle Time

Cycle time indicates how often a message is transmitted:

### Typical Values
- **10 ms**: High-priority safety signals (brake, steering, throttle)
- **20 ms**: Real-time control signals (engine, transmission)
- **50 ms**: Sensor data (engine temperature, pressures)
- **100 ms**: Status and diagnostics
- **1000 ms+**: Low-priority monitoring, heartbeat signals

### Event-Driven Messages
- No fixed cycle; sent only when a condition occurs
- Example: Fault messages, door-open alerts
- Note as "Event" or "On-demand" in transmission type

## Frame Type

### Standard (CAN 2.0A)
- 11-bit identifier (0x000–0x7FF)
- Shorter arbitration field
- Common in road vehicles

### Extended (CAN 2.0B)
- 29-bit identifier (0x00000000–0x1FFFFFFF)
- Longer arbitration field
- Used in heavy-duty vehicles (J1939), industrial, and some automotive modules
- Example: J1939 uses network/node/message structure within the 29-bit space

## DLC (Data Length Code)

- CAN 2.0: DLC 0–8 (frames with 0–8 bytes payload)
- CAN FD: DLC 0–15 (mapped to 0, 8, 12, 16, 20, 24, 32, 48, 64 bytes)
- A signal must fit completely within the declared DLC
- Example: 16-bit signal starting at bit 0 requires DLC ≥ 2 (bits 0–15 span 2 bytes)

## J1939 Awareness

J1939 is a specialized protocol for heavy-duty vehicles built atop CAN 2.0B:

- **29-bit ID structure**: P (8 bits, priority) + F (8 bits, PF, page selection) + PS (8 bits, group/address) + S (1 bit, source)
- **Message length**: Always 8 bytes
- **Byte numbering**: Starts at 1 (not 0) in some documentation
- **CTS/CM protocol**: Multi-frame messages via handshake (Connection Management)
- **BAM (Broadcast Announcement Message)**: For large data transfers

When working with J1939 in a DBC:
- Document the bit numbering convention clearly (0-based or 1-based)
- Indicate which signals are multi-frame (CTS/CM) vs. single-frame
- Account for 8-byte DLC (always)
- Reference the J1939 SAE standard for parameter allocation

## Common Pitfalls

1. **Bit numbering confusion**: Clearly document whether signals use Intel (bit 0 LSB) or Motorola (bit 7 MSB) numbering.
2. **Overlapping signals**: In non-multiplexed messages, overlapping signal bits will corrupt data. Always validate.
3. **DLC underflow**: A signal spanning bits 24–31 requires DLC ≥ 4 (4 bytes × 8 bits = 32 bits, bits 0–31).
4. **Missing multiplexor definition**: Multiplexor signals must be explicitly listed; receivers need their full definition.
5. **Inconsistent byte order**: Using mixed byte orders in the same message makes parsing error-prone.
6. **Unrealistic cycle times**: 1 ms cycle on a standard CAN bus (1 Mbit/s) is aggressive; 10 ms is more typical.
7. **Undefined scaling**: Always document scale, offset, min, max, and unit. Ambiguity leads to implementation bugs.
