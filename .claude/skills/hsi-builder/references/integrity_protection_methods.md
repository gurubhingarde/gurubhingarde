# Integrity Protection Methods for HSI Signals

## Overview

Every HSI signal crossing the HW-SW boundary requires **integrity protection** to detect transmission faults (bit flips, stuck-at, timing errors, missing updates). This document compares four methods and guides selection.

## 1. Parity (Single-bit Error Detection)

### Description
A single parity bit is appended to the signal. The parity bit is computed such that the total count of 1s in the data + parity is always odd (or even).

**Example**: 8-bit data `0b10110010` has 4 ones. To maintain odd parity, append 1, giving 9 bits `0b101100101`.

### Detection
Receiver XORs all 9 bits. If result is 0 (even parity check) or 1 (odd parity check), all bits match the parity rule. If not, a flip is detected.

### Properties
- **Pros**: 
  - Minimal cost: 1 extra bit.
  - Simple HW implementation (XOR gates).
  - Fast (single parallel XOR operation).
- **Cons**:
  - Detects only an **odd** number of bit flips (2-bit flip goes undetected).
  - Diagnostic Coverage (DC): 50% for random errors, 90-99% for single-bit faults.
  
### When to Use
- 1-bit signals (e.g., simple fault flags).
- Multi-bit signals with low flip probability and cost constraints.
- Applications requiring **detection only** (no correction).

### Implementation
```c
// Compute parity bit
uint8_t parity = 0;
for (int i = 0; i < 8; i++) {
    parity ^= (data >> i) & 1;
}
uint8_t tx = (data << 1) | parity;  // append parity as LSB

// Check parity on receive
uint8_t rx_parity = 0;
for (int i = 0; i < 9; i++) {
    rx_parity ^= (rx >> i) & 1;
}
if (rx_parity != 0) {
    // Parity error detected
}
```

---

## 2. CRC (Cyclic Redundancy Check)

### Description
CRC is a polynomial-based checksum computed over the data using a generator polynomial. The sender appends the CRC; the receiver recomputes it and compares.

**Common polynomials**:
- **CRC-8**: 8-bit checksum, polynomial `x^8 + x^7 + x^6 + x^4 + x^2 + 1`. DetectsErrors up to 7 bits.
- **CRC-16**: 16-bit checksum (e.g., CRC-CCITT: `x^16 + x^12 + x^5 + 1`). Detects errors up to 15 bits.
- **CRC-32**: 32-bit checksum (Ethernet, ZIP, PNG). Detects errors up to 31 bits.

### Detection
Receiver computes CRC over received data + received CRC. If result is zero (for correctly paired data/CRC), no error. Otherwise, error detected.

### Properties
- **Pros**:
  - High DC: 99% for CRC-16, 99.99% for CRC-32.
  - Detects all single-bit errors, most multi-bit patterns.
  - Well-standardized (AUTOSAR, CAN, Ethernet, etc.).
  - Tables or bit-shift SW implementations available.
- **Cons**:
  - Extra 8-32 bits per message.
  - SW compute: 8-200 CPU cycles depending on CRC width and unrolling.
  - Does **not correct** errors (detection only).

### When to Use
- **2-32 bit signals** requiring high assurance.
- **Streaming data** (sensor values, messages) where multi-bit corruption is plausible.
- ASIL C and D designs.
- Cost-sensitive designs where SECDED HW is too expensive.

### Implementation (CRC-16 example, bit-by-bit)
```c
#define CRC_POLY 0x1021  // CRC-CCITT polynomial

uint16_t compute_crc16(const uint8_t *data, int len) {
    uint16_t crc = 0;
    for (int i = 0; i < len; i++) {
        crc ^= ((uint16_t)data[i]) << 8;
        for (int j = 0; j < 8; j++) {
            crc = (crc & 0x8000) ? ((crc << 1) ^ CRC_POLY) : (crc << 1);
        }
    }
    return crc;
}

// Transmit
uint16_t crc = compute_crc16(data, data_len);
// tx = data || crc (append CRC to data)

// Receive and check
uint16_t rx_crc = compute_crc16(rx_data, rx_data_len);
if (rx_crc == 0) {
    // No error
} else {
    // Error detected
}
```

---

## 3. SECDED (Single Error Correction, Double Error Detection)

### Description
Hamming code with an extra parity bit for double-bit error detection. For each data bit position, a parity bit covers all positions whose binary representation has a 1 in a specific bit position.

**Example for 64-bit data**: 7 parity bits (positions 1, 2, 4, 8, 16, 32, 64) + 1 overall parity = 8 extra bits.

### Detection and Correction
Receiver computes syndrome (parity check result). If syndrome is 0, no error. If syndrome is nonzero, it indicates the error bit position. If the overall parity check fails and syndrome is nonzero, a single-bit error is corrected. If syndrome is nonzero but overall parity is OK, a two-bit error is detected (but not corrected).

### Properties
- **Pros**:
  - **Correction** of single-bit errors (automatic, no retry).
  - Detection of double-bit errors.
  - High DC: 99.9% for memory applications.
  - Transparent to SW (HW encoder/decoder).
  - Ideal for RAM/Flash where SEU (Single Event Upset) is concern.
- **Cons**:
  - HW cost: Encoder and decoder circuits (~50-200 gates each).
  - Not practical for low-width signals (overhead > signal width).
  - Requires dedicated HW logic; not portable across platforms.

### When to Use
- **RAM and Flash protection** (critical memory).
- **Registers storing liveness counters or validity bits** where single-bit flip must not brick the system.
- **ASIL C/D** with high reliability targets.
- Designs where HW IP (ECC controller) is available.

### Implementation (Hamming(7,4) for 4-bit data; extend to 64-bit in practice)
```c
// Encode 4-bit data into 7-bit Hamming code
uint8_t hamming_encode(uint8_t data) {
    uint8_t p1 = ((data >> 0) ^ (data >> 1) ^ (data >> 3)) & 1;  // positions 1,3,5,7
    uint8_t p2 = ((data >> 0) ^ (data >> 2) ^ (data >> 3)) & 1;  // positions 2,3,6,7
    uint8_t p4 = ((data >> 1) ^ (data >> 2) ^ (data >> 3)) & 1;  // positions 4,5,6,7
    return (data << 3) | (p4 << 2) | (p2 << 1) | p1;
}

// Decode and correct single-bit errors
uint8_t hamming_decode(uint8_t code) {
    uint8_t s1 = ((code >> 0) ^ (code >> 2) ^ (code >> 4) ^ (code >> 6)) & 1;
    uint8_t s2 = ((code >> 1) ^ (code >> 2) ^ (code >> 5) ^ (code >> 6)) & 1;
    uint8_t s4 = ((code >> 3) ^ (code >> 4) ^ (code >> 5) ^ (code >> 6)) & 1;
    uint8_t error_pos = (s4 << 2) | (s2 << 1) | s1;  // Syndrome points to error bit
    if (error_pos) code ^= (1 << error_pos);  // Flip error bit to correct
    return (code >> 3) & 0x0F;  // Extract original 4 bits
}
```

---

## 4. Dual-Channel Comparison

### Description
The same value is computed or transmitted **twice** over **independent channels** (or on different SW threads with different implementations). The receiver compares the two values. Any mismatch indicates a fault.

**Example**: Processor A and B (lockstep) compute the same result; a mismatch is flagged as fault.

### Detection
Receiver checks: `if (channel_A != channel_B) { fault = 1; }`

### Properties
- **Pros**:
  - Highest DC: 99.9%+ (fails only if both channels fail identically, which is rare if truly independent).
  - Detects **any** fault in either channel (bit flips, computation errors, timing errors).
  - No extra bits on the signal itself (compare is separate).
  - Architectural solution; applies to any signal type.
- **Cons**:
  - **2x cost**: Double the HW (two cores, two memories) or double the SW compute.
  - Coupling risk: If the two channels share the same fault source (e.g., same power supply, same clock), the independence claim fails.
  - DFA (Dependent Failure Analysis) is critical to prove independence.

### When to Use
- **Critical safety mechanisms** (lockstep processors, dual-redundant sensors).
- **ASIL D** designs where single-point faults must be detected.
- **Processor cores** (already dual by architecture).
- **Sensor pairs** (two pressure sensors, two temperature sensors).
- When coupling factors have been analyzed and mitigated per ISO 26262-9 §7 DFA.

### Implementation (Lockstep result comparison)
```c
// HW: both cores compute the same ALU operation
// HW: compare results; assert mismatch flag if different
// SW: reads mismatch flag

extern volatile uint32_t core_a_result;
extern volatile uint32_t core_b_result;

uint32_t result = core_a_result;
if (core_a_result != core_b_result) {
    // Lockstep mismatch detected; transition to safe state
    esc_transition_to_safe_state();
}
```

---

## Decision Matrix

| Signal Characteristic | Parity | CRC | SECDED | Dual-Channel |
|---|---|---|---|---|
| **Signal width** | <= 8 bits (simple flags) | 2–32 bits | Ram/Flash (64+ bits) | Any |
| **DC% target** | 60–90% | 95–99.9% | 99.9%+ | 99.9%+ |
| **Cost (bits)** | +1 | +8 to +32 | +10–15% (for 64-bit data) | +0 (2x channels) |
| **SW compute** | Minimal | 10–200 cycles | Minimal (HW handles) | Minimal (compare) |
| **Correction capability** | No | No | Yes (single-bit) | No |
| **ASIL A/B** | OK | OK | Rare | Rare |
| **ASIL C/D** | Limited | OK | Preferred (memory) | Preferred (high-assurance) |
| **Example signals** | `fault_flag_valid` | `sensor_value`, `dbc_message` | `ecc_ram`, `config_crc` | `processor_result`, `sensor_pair` |

---

## ISO 26262 Compliance Notes

- **ISO 26262-4 §6.4.6**: TSC HSI shall specify integrity protection method per signal. Default recommendations by ASIL are not binding; analyst may argue for lighter or heavier protection.
- **ISO 26262-5 §6.4.6**: HW team shall verify the integrity method's DC% via FMEDA or formal analysis. Register-level FMEDA typically credits parity at 90%, CRC at 99%, SECDED at 99.9%.
- **ISO 26262-9 §7 (DFA)**: If using dual-channel, dependency and coupling analysis is mandatory. Shared power supply, clock, or thermal zone can invalidate independence claims.

---

## Practical Guidance

1. **Start with defaults**: Parity for 1-bit flags, CRC for sensor values, SECDED for critical memory, dual-channel for cross-core checks.
2. **Document DC% target**: State the diagnostic coverage goal for each signal (e.g., "95% for pressure sensor").
3. **FMEDA validation**: After design, run FMEDA to confirm the integrity method's actual DC%. If it falls short, increase protection (e.g., upgrade from CRC-8 to CRC-16) or add a second mechanism (e.g., plausibility check).
4. **Testability**: Plan fault injection tests (bit-flip, stuck-at, timing) to validate detection on bench or in simulation.
5. **Cross-reference**: Link each HSI signal's integrity method back to the FMEA row and the TSR that mandates it.
