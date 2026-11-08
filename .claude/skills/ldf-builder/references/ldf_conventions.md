# LDF Conventions

## Frame Types

### Unconditional
- Published on a fixed, periodic schedule
- Every cycle: 1 slot allocated in every schedule table
- Period ranges 10–1000 ms (typical 50, 100, 200 ms)
- Use for: continuous sensor readouts, command signals

### Event-Triggered
- Published on demand; master arbitrates collision recovery via timeout
- Slot allocated conditionally; retries on collision
- Use for: state changes, alarms, button presses

### Sporadic
- Lowest priority; fills idle slots if frame has data
- No guaranteed latency
- Use for: non-critical status, history logs

### Diagnostic
- Master-to-slave service requests (e.g., 0x22 Read Data, 0x2E Write Data)
- Fixed response time (e.g., 25 ms per ISO 14229)
- Use for: OBD, manufacturing diagnostics, calibration

## Schedule Timing

- Master sends a timing header every frame period (e.g., 100 ms)
- Slaves respond within the allocated slot (typically 10 ms)
- Minimum inter-frame spacing: slot time ≥ 10 bits at baud rate
  - At 19.2 kbps: 10 bits ≈ 0.52 ms
- Slot allocation: start_time (ms) + max_response_time (typically 10 ms)

## Encoding Types

### Physical
- Real-world units: temperature (°C), voltage (V), speed (km/h)
- Formula: physical_value = raw_value × scale + offset
- Min/max: physical bounds (e.g., 0–120°C)

### Logical
- Enumerated states: OFF/ON, IDLE/ACTIVE, Error codes (0–15)
- Min/max: raw value bounds (0–255 for 8-bit)
- Scale/offset typically 1.0 / 0.0

## Signal Allocation Rules

1. Each signal belongs to **exactly one frame**
2. Signals do not span frame boundaries (start_bit + length ≤ 64 bits)
3. Start bit ordering: byte 0 (LSB) to byte 7 (MSB)
4. Producer = frame publisher node
5. Consumers = all subscriber nodes (from schedule table)

## Baud Rate Specification

- Range: 1–20 kbps per LIN 2.2A
- Common values: 19.2, 10, 9.6 kbps
- Specification in LDF file as **BAU**: baudrate in bits/sec
  - Example: BAU = 19200 (for 19.2 kbps)

## Validation Sequence

1. Syntax: All frame IDs, signal IDs unique
2. Structure: No signal in multiple frames
3. Schedule: All frames present in at least one schedule table mode
4. Coverage: All nodes have a defined role in at least one frame
5. Timing: Total scheduled frame duration ≤ 100% of a mode's cycle time
