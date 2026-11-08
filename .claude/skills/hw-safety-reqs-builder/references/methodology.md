# Hardware Safety Requirements — Methodology

## The HW-TSR → HW-SR Hierarchy

The Technical Safety Concept (TSC) produces **Hardware Technical Safety Requirements** (HW-TSRs) — high-level, architecture-independent statements of what safety mechanisms must be implemented. For example:

> "The HW shall implement Range / out-of-range check (SM10) on Wheel Speed Sensor FL with diagnostic coverage of at least 60-80% and assert the fault flag within 1 sample."

This HW-TSR is a *contract* between the systems team and the hardware team. It says **what** must happen, but not **how**. The hardware team, during detailed design, must refine each HW-TSR into one or more **Hardware Safety Requirements** (HW-SRs) that:

1. Allocate to **specific hardware elements** (MCU pins, ADC channels, comparators, driver ICs, etc.)
2. Specify **concrete electrical or logical parameters** (input range, threshold values, timing)
3. Address **specific failure modes** (stuck, drift, open, short, latch-up, thermal shutdown, etc.)
4. Define **diagnostic coverage targets** based on FMEDA analysis (order-of-magnitude defaults in templates)
5. Prescribe **verification methods** appropriate to the allocated ASIL (electrical test, fault injection, simulation, inspection)

## HW-SR Templates by Mechanism Category

For each HW-TSR, the skill proposes template-derived HW-SRs by architectural function:

### Input Path (Sensing)

**Mechanism: Range / out-of-range check (SM10)**

Template HW-SRs:

1. **Input Conditioning**  
   "The HW shall provide a 12-bit ADC channel for [sensor_name] with:
   - Input voltage range: [Vmin] to [Vmax] (typically 0–5V)
   - Input impedance: [Zin]
   - Sampling rate: [fs Hz] (minimum [ftti_ms] ms latency)
   - Accuracy: [tolerance]%"

2. **Monitoring and Detection**  
   "The HW shall implement a digital out-of-range comparator logic on the sampled ADC value with:
   - Low threshold: [Tlow] (e.g., 0.5V → 10 km/h)
   - High threshold: [Thigh] (e.g., 4.5V → 200 km/h)
   - Assertion latency: ≤ [fdti_ms] ms (within FDTI budget)
   - Debounce: [N] consecutive samples out-of-range before flagging fault"

3. **Diagnostic Communication**  
   "The HW shall route the out-of-range fault flag to the safety MCU diagnostic input pin:
   - Signal name: [esc.diag.fl_sm10] (from HSI spec)
   - Encoding: 1 bit (0 = OK, 1 = fault) + companion validity bit
   - Integrity: Parity or CRC per signal encoding
   - Reaction: SW shall consume within [frti_ms] ms and command safe state"

### Process Path (Monitoring)

**Mechanism: Dual-core lockstep (SM01)**

Template HW-SRs:

1. **Processor Pairing**  
   "The HW shall pair two identical processor cores (Core A and Core B) running synchronized instruction streams:
   - Synchronization: Locked step at cycle-by-cycle granularity
   - Mismatch detection: Within 1 cycle (typical latency << 1 µs)"

2. **Mismatch Signaling**  
   "The HW shall detect any mismatch in Core A vs. Core B program counter, register file, or memory writes and:
   - Assert a dedicated mismatch flag within 1 cycle
   - Route flag to independent safe-state disable logic (not passing through either core's logic)"

3. **Independent Disable**  
   "The HW shall implement an independent watchdog that monitors the mismatch flag and, if no valid heartbeat is received within [window_ms] ms, shall:
   - Disable the processor pair via latch-free logic
   - Assert the safety output disable within [reaction_ms] ms"

### Output Path (Actuation)

**Mechanism: Current feedback (SM16)**

Template HW-SRs:

1. **Feedback Sensing**  
   "The HW shall provide a high-side or low-side current sense resistor or IC ([0.1–1 ohm] typically) on the actuator power stage with:
   - Sense voltage range: [Vmin] to [Vmax]
   - Accuracy: [±tolerance]%
   - Bandwidth: [BW Hz] (sufficient to track actuator transients)"

2. **ADC Digitization**  
   "The HW shall digitize the current feedback signal via a dedicated ADC channel:
   - ADC resolution: [bits] (12+ for [ASIL])
   - Sampling rate: [fs Hz] (≥ 2× actuator transient frequency)
   - Latency: ≤ [fdti_ms] ms"

3. **Plausibility Check**  
   "The HW shall implement closed-loop current plausibility logic:
   - Expected current for commanded action: [Iexpect_min] to [Iexpect_max]
   - Deviation tolerance: [ΔI]%
   - Assertion of out-of-range flag: ≤ [fdti_ms] ms"

4. **Diagnostic Output**  
   "The HW shall route the current-out-of-range fault flag to the safety MCU:
   - Signal name: [esc.diag.actuator_current] (from HSI spec)
   - Encoding: 1 bit + validity bit
   - Reaction: SW shall command safe state within [frti_ms] ms"

## Failure Modes Addressed

Each HW-SR shall address one or more of these standard failure modes:

**Sensing:**
- No output (open circuit, power loss, sensor mechanical failure)
- Stuck output (sensor stuck at one value)
- Drifted output (gradual calibration shift)
- Noisy output (high-frequency noise, filtering inadequate)
- Out-of-range output (signal exceeds expected bounds)

**Processing:**
- Stuck-at fault (processor state frozen)
- Transient bit flip (SEU in register or memory)
- Lockstep mismatch (cores diverge in execution)
- Watchdog timeout (scheduler deadlock or overload)
- Illegal opcode or memory access

**Actuation:**
- Open circuit (driver output stuck low/floating)
- Short to supply (unintended high state)
- Short to ground (unintended low state)
- Gate driver fault (bootstrap capacitor discharged)
- Thermal shutdown (overjunction temperature)

## Diagnostic Coverage (DC)

**Diagnostic Coverage (DC)** is the percentage of failure modes in a given class that are detected by a single-point failure diagnostic mechanism. DC is typically expressed as a range (e.g., "60–80%" for SM10 range checks) because:

1. The catalog provides **order-of-magnitude defaults** based on the mechanism type.
2. **Actual DC is determined by FMEDA** — the hardware team must analyze the specific implementation to confirm DC.
3. **ASIL decomposition rules** (ISO 26262-9 §7) link SPFM, LFM, and PMHF targets to required DC levels.

For example:
- **SM10 (Range check):** 60–80% DC (detects out-of-range but not stuck-at or slow drift)
- **SM05 (ECC on RAM):** 99%+ DC (detects and corrects single-bit, detects multi-bit)
- **SM01 (Lockstep):** ≥99% DC (detects nearly all bit flips within a single cycle)

The HW-SRs generated by this skill include **placeholder DC% values** from the templates; the analyst must refine these after FMEDA.

## Reference Timing

Each HW-SR shall be tied to the FTTI and FDTI/FRTI timing budgets from the TSC. The HW team must ensure:

- **FDTI (Fault Detection Time Interval):** The HW mechanism detects the fault within FDTI.  
  E.g., SM10 range check must detect out-of-range within 1 sample → FDTI ≥ 1 sampling period.

- **FRTI (Fault Reaction Time Interval):** The SW, upon receiving the HW diagnostic signal, commands the safe state within FRTI.  
  E.g., if FTTI = 100 ms, FDTI = 50 ms (HW detects in 1 sample), then FRTI = 50 ms (SW has 50 ms to react).

## Independence and Decomposition

When ASIL decomposition is applied at the FSC level, the independent verification of each decomposed channel carries forward to HW-level requirements. The HW team must document:

1. **Shared resources:** Which HW elements (power supply, clock, memory, I/O pins) are shared between channels?
2. **Mitigation:** How is each shared resource protected (separate voltage regulators, clock trees, ECC, watchdog, etc.)?
3. **Evidence:** What FMEDA analysis, electrical simulation, or prototype testing confirms independence?

See `08_Independence_Considerations` tab for the checklist of coupling factors from ISO 26262-9 §7.

## Output: FMEDA and HW Metrics

The HW-SRs feed directly into:

1. **Failure Mode, Effects, and Diagnostic Analysis (FMEDA)**  
   Each HW-SR → one or more FMEA rows with DC% achieved.

2. **Hardware Metrics (ISO 26262-5 §8)**  
   Aggregate DC%, SPFM (Single Point Failure Metric), LFM (Latent Fault Metric), and PMHF (Probabilistic Metric of Hazard Failure) per ASIL.

3. **Verification (ISO 26262-5 §9)**  
   Each HW-SR verified by electrical test, fault injection, simulation, or inspection per allocated ASIL and verification method.

---

## References

- ISO 26262-5:2018 — Product development at the hardware level, §6 (Specification of hardware safety requirements).
- ISO 26262-9:2018 — Functional safety management, §5 (ASIL decomposition), §7 (Dependent Failure Analysis).
