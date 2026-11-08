# HSI Specification Methodology

## What is the HSI?

The Hardware-Software Interface (HSI) is the **contract** between the HW and SW teams. It specifies:
- Which signals cross the HW-SW boundary
- The encoding, timing, and integrity of each signal
- The failure modes and detection strategies
- The initialization sequence and hand-shake protocol
- Traceability to safety requirements and verification methods

Per ISO 26262-4 §6.4.6 (Technical Safety Concept), the TSC must define the HSI signals that implement each safety mechanism. Per ISO 26262-5 §6.4.6 (Hardware Concept), the HSI specification is the input to HW FMEDA and verification planning.

## Contract-Grade HSI Properties

A contract-grade HSI specification:
1. **Exhaustive**: Every signal that crosses HW-SW has a row in the HSI catalog.
2. **Unambiguous**: Data type, bit width, encoding, timing, and integrity method are explicit.
3. **Traceable**: Each signal links back to the FSR and safety mechanism that creates it.
4. **Verifiable**: Timing budgets and failure modes enable test planning.
5. **Implementable**: Register addresses, bit offsets, and C struct definitions are present.

## The 11-Tab Structure

### 00_Title_Page
Project ID, document metadata, linked TSC and HW architecture, methodology statement.

### 01_Document_Control
Revision history: 0.1 (initial draft), 0.2 (refinement), 1.0 (release).

### 02_HSI_Signal_Catalog
One row per signal. Columns: signal name, direction (HW->SW or SW->HW), data type, bit width, range, units, default value, encoding rules, integrity protection, validity bit, allocated ASIL.

The signal catalog is the **single source of truth** for the HW-SW interface.

### 03_Register_Map
For memory-mapped signals: register address (e.g., 0x4001_0010), bit offset, access mode (R/RW/W), reset value, bit-field layout, lock bit. Placeholder rows for signals without fixed addresses.

### 04_Timing_Specification
Per signal: sample rate (Hz), max age (ms) that SW may consume without error, latency budget HW->SW (ms), latency budget SW->HW (ms), worst-case detection time, settling time.

These constraints enable end-to-end FTTI budget verification.

### 05_Failure_Modes_and_Reactions
Per signal: possible faults (stuck-at, parity error, missing, late, out-of-range), detection method (BIST, periodic check, watchdog), SW reaction on detection, HW fail-safe behavior, target detection coverage %.

Links to FMEDA and verification planning.

### 06_Initialization_Sequence
HW power-on diagnostic (BIST, register lock, supply monitor), SW startup checks (validity bit polling), hand-shake protocol (first message, liveness counter confirm), timing and success conditions.

Critical for safe startup mode: HW and SW must agree on initial state before entering normal operation.

### 07_Cross_Reference
Traceability matrix: HSI signal -> FSR_ID -> TSR_ID -> Safety Mechanism -> ASIL. Enables impact analysis for design changes and verification mapping.

### 08_C_Header_Stub
Auto-generated C struct definitions for embedded SW (preview tab). Full .h file written to `<output>_hsi.h` alongside the xlsx.

### 09_Test_Cases
Per signal: nominal path, fault injection scenarios (stuck-at, parity), boundary conditions, timing edge cases. Basis for HW/SW integration tests and verification.

### 10_References
TSC, HW architecture, ISO 26262 Parts 4 & 5 §6.4.6, AUTOSAR (if applicable), methodology documents.

## Integrity Protection Methods

### Parity (single-bit signals)
- **When**: 1-bit fault detection on simple signals (e.g., single fault flag).
- **How**: Odd or even parity bit appended; receiver XORs all bits (including parity) and checks result.
- **DC%**: 90-99% (fails only if multiple bits flip).
- **Cost**: 1 extra bit, minimal SW compute.

### CRC (multi-bit signals)
- **When**: 2-32 bit signals; higher assurance than parity.
- **How**: Polynomial division (e.g., CRC-16, CRC-32). Transmit signal + CRC; receiver checks.
- **DC%**: 99%+ (detects all single and most multi-bit errors up to polynomial degree).
- **Cost**: 16-32 extra bits; 10-100 CPU cycles to compute.

### SECDED (memory protection)
- **When**: Ram/Flash with single-bit corruption risk (e.g., SEU in space, thermal drift).
- **How**: Hamming code; 7 parity bits per 64 bits data. Detects and corrects single-bit, detects double-bit.
- **DC%**: 99%+.
- **Cost**: HW encoder/decoder; transparent to SW.

### Dual-channel comparison
- **When**: Highest assurance; two independent channels (HW or SW) compute same value; compare on receipt.
- **How**: Transmit value twice; receiver compares; mismatch = fault.
- **DC%**: 99%+ (fails only if both channels fail identically, which is rare if truly independent).
- **Cost**: 2x bandwidth; 2x compute for second channel.

## Validity Bits

Each diagnostic signal typically includes a **companion validity bit** (e.g., `esc.diag.lockstep_mismatch` + `esc.diag.lockstep_mismatch_valid`).

- **Purpose**: SW cannot distinguish between "signal is 0 because no fault" and "signal is 0 because HW comms lost".
- **Encoding**: 
  - 0 = not valid (HW has not yet asserted a value; ignore the signal)
  - 1 = valid (HW has computed and presented the signal; SW may act on it)
- **Lifetime**: Set by HW at first update; cleared by SW on acknowledgement or timeout.

## Liveness Signals

Every diagnostic signal pairs with a **liveness counter** (e.g., `esc.live.lockstep_ack`):
- **Direction**: SW -> HW (SW sends, HW monitors).
- **Encoding**: 8-bit rolling counter; SW increments per task period (e.g., 10ms).
- **Purpose**: HW watchdog detects if SW task hangs (counter stops incrementing).
- **Detection**: HW measures time between counter increments; mismatch triggers independent disable.

## Timing Budgets

Per ISO 26262-4 §5.3.3, the Functional Time Interval (FTTI) is split into:
- **FDTI** (Fault Detection Time Interval): HW detects fault; SW receives diagnostic flag.
- **FRTI** (Fault Reaction Time Interval): SW reacts; actuator responds.
- **FTTI = FDTI + FRTI** must be <= FTTI requirement from the FSC.

HSI specification provides:
- **Sample rate**: How often HW updates the signal (e.g., 100 Hz = 10 ms).
- **Max age**: Latest acceptable SW read age (e.g., if max_age=10ms and sample_rate=100Hz, SW misses <= 1 sample).
- **Latency HW->SW**: Time from HW detection to SW receipt (register read + any ISR/task overhead).
- **Latency SW->HW**: Time from SW decision to HW acknowledgement receipt (actuator command + register write + HW capture).

## Verification Mapping

Each HSI signal traces to:
1. **FSR** (Functional Safety Requirement): E.g., "ESC shall detect processor lockstep mismatch".
2. **TSR** (Technical Safety Requirement): "HW shall assert `esc.diag.processor_sm01` within 1 µs; SW shall command safe state within 50 ms".
3. **Safety Mechanism**: E.g., "SM01 — Dual-core lockstep" with target DC% 99%.
4. **ASIL**: The allocated ASIL (post-decomposition) determines verification rigor.

HW verification (FMEDA, SPFM, LFM, PMHF):
- Confirms DC% claim via fault injection or analytical assessment.
- Validates timing against FDTI budget.
- Verifies register lock, BIST, and initialization hand-shake.

SW verification (MISRA C, MC/DC, system test):
- Confirms debounce and filter logic on liveness counter.
- Validates timeout handling (e.g., "if liveness_counter unchanged for 100 ms, enter safe state").
- Verifies cross-check logic if two independent detectors feed the same safety mechanism.
