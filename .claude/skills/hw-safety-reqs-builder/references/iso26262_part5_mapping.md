# ISO 26262-5 §6 — Specification of Hardware Safety Requirements

This document maps the HW Safety Requirements workbook tabs to the normative requirements in ISO 26262:2018, Part 5 (Product development at the hardware level), Clause 6 (Specification of hardware safety requirements).

## Part 5 §6 Overview

ISO 26262-5 §6 requires the hardware development team to:

1. **a) Develop a specification** of hardware safety requirements (HW-SRs) that **implement the HW-TSRs** from the TSC.
2. **b) Specify for each HW-SR:**
   - Allocated ASIL
   - Failure modes to be addressed
   - Diagnostic coverage targets
   - Verification method(s)
   - Associated timing constraints

3. **c) Review the HW-SR specification** for:
   - Consistency with HW-TSRs
   - Completeness of failure mode coverage
   - Feasibility of diagnostic coverage targets
   - Alignment with chosen verification methods

## Workbook Tab Mapping

### Tab 00: Title Page

**Maps to:** ISO 26262-5 §6 (document identification and scope)

- Project name, document ID, revision, date, author, approver.
- Reference to linked TSC workbook (traceability).
- Statement of methodology: "This specification derives HW-SRs from TSC HW-TSRs per ISO 26262-5 §6 templates."

### Tab 01: Document Control

**Maps to:** ISO 26262-5 §2 (Product development planning) and §3 (Document management)

- Revision history.
- Date, author, and approver per revision.
- Description of changes (e.g., "Initial draft from TSC," "FMEDA refinement incorporated," "Released to HW design").

### Tab 02: HW TSRs From TSC

**Maps to:** ISO 26262-5 §6(a) — "input to the specification of hardware safety requirements"

**Read-only echo of:**
- FSR_ID (traceability back to functional safety concept)
- HW-TSR_ID, mechanism, ASIL (inherited or allocated)
- Linked architecture node
- Mechanism name (e.g., SM10, SM01, SM16)
- FTTI timing constraint

This tab confirms that the HW team has correctly understood the scope of requirements handed off from TSC.

### Tab 03: HW Safety Requirements

**Maps to:** ISO 26262-5 §6(b) — "each hardware safety requirement shall specify"

**Columns:**

| Column | Requirement | Mapping |
|--------|-------------|---------|
| HW-SR_ID | Unique identifier | §6(b): identification |
| Parent HW-TSR_ID | Traceability | §6(a): derives from HW-TSR |
| ASIL | Allocated ASIL | §6(b): allocated ASIL |
| Allocated HW Element | Hardware component (MCU pin, ADC channel, comparator, driver IC) | §6(b): "specified in relation to the hardware elements" |
| Requirement Text | Concrete, testable statement (e.g., "ADC channel for sensor with 12-bit resolution, 0–5V input range, ±5% accuracy") | §6(b): specification of the requirement |
| Addressed Failure Modes | List of failure modes (stuck, drift, open, short, latch-up) | §6(b): "failure modes to be addressed" |
| Target DC% | Diagnostic coverage target (from catalog default or FMEDA refinement) | §6(b): "diagnostic coverage" |
| Verification Method(s) | Electrical test, fault injection, simulation, inspection | §6(b): "verification and validation methods" |

### Tab 04: Failure Mode Mapping

**Maps to:** ISO 26262-5 §6(b) — "failure modes to be addressed"

For each HW-SR, documents which standard hardware failure modes are addressed:

**Failure Mode Classes:**
- **Sensing:** No output, Stuck, Drifted, Noisy, Out-of-range
- **Processing:** Stuck-at, Transient bit flip, Lockstep mismatch, Watchdog timeout, Illegal opcode
- **Actuation:** Open, Short-to-supply, Short-to-ground, Gate driver fault, Thermal shutdown

**Mapping:** Rows enumerate the HW-SR and its addressed failure modes with checkmarks or coverage percentage. This tab provides **traceability from HW-SR to FMEA rows** (ISO 26262-5 §7).

### Tab 05: HSI Reference

**Maps to:** ISO 26262-5 §6(b) — "diagnostic coverage" and associated signal interface

For each HW-SR, cross-references:
- HSI signal names (from HSI specification, typically upstream from TSC §06_HSI_Specification)
- Signal direction (HW → SW diagnostic, SW → HW liveness)
- Encoding and update rate
- Integrity protection (parity, CRC)
- Allocated ASIL

This ensures that the HW team has a **concrete contract with the SW team** for every diagnostic signal.

### Tab 06: Verification Methods

**Maps to:** ISO 26262-5 §6(b) — "verification and validation methods"

For each HW-SR, specifies the verification method(s) per allocated ASIL:

**Methods (ISO 26262-4 Table 3, adapted for HW):**
- **Inspection:** Visual or electrical check of schematic, layout, component selection
- **Semi-formal verification:** Formal analysis of register transfer language (RTL) logic
- **Formal verification:** Formal proof of safety properties (e.g., watchdog timeout logic)
- **Simulation:** Electrical simulation (SPICE), high-level HDL simulation
- **Prototype testing:** Hardware prototype with fault injection or environmental stress
- **Electrical test:** Bench test with instrumentation (oscilloscope, multimeter, load tester)

**Recommendation levels:**
- **++** (strongly recommended per allocated ASIL)
- **+** (acceptable as supplementary evidence)

### Tab 07: Test Strategy

**Maps to:** ISO 26262-5 §9 — "Verification and validation of hardware"

Organizes verification activities by test category and links each category to the HW-SRs it covers:

**Test Categories:**
- **HIL (Hardware-in-the-Loop):** MCU code + real HW components + simulated environment
- **Fault Injection:** Intentional electrical transients (glitches, supply disruptions) to validate diagnostic detection
- **Electrical Characterization:** Input range, output impedance, temperature coefficient, thermal behavior
- **Environmental Testing:** Temperature cycling, humidity, EMI, vibration per automotive standards (AEC-Q200, etc.)
- **Accelerated Life Testing:** Elevated temperature, voltage, or frequency to validate long-term reliability

Each row maps test category → HW-SR coverage.

### Tab 08: Independence Considerations

**Maps to:** ISO 26262-5 §6(c) and ISO 26262-9 §7 — "Dependent Failure Analysis"

When the TSC applies ASIL decomposition, the hardware team must document:

**Coupling Factor Checklist (from ISO 26262-9 §7):**
1. Shared supply voltage
2. Shared ground
3. Shared clock
4. Shared bus
5. Shared sensor
6. Shared memory
7. Shared SW library
8. Shared OS / scheduler
9. Shared environmental zone (temperature, EMI)
10. Shared development team / process
11. Shared compiler / toolchain
12. Shared production / test process

For each decomposition pair (e.g., "redundant sensor channels"), the team documents:
- **Coupling factor:** Identified coupling?
- **Mitigation:** How is the coupling mitigated (e.g., separate ADC channels, independent watchdog, isolated power, different PCB layout area)?
- **Evidence:** FMEDA row, circuit schematic, layout drawing, electrical simulation result.

### Tab 09: References

**Maps to:** ISO 26262-5 §6(e) — "Any reference material"

Lists normative and informative sources:
- Linked TSC workbook (identifies HW-TSRs)
- Linked FSC workbook (identifies functional requirements)
- HARA report (identifies hazardous events and safe states)
- ISO 26262 standards (Part 1–10)
- Industry standards (AEC-Q200 for component reliability, SAE J1939 for vehicle bus protocols, etc.)
- Project-specific specifications (thermal design guidelines, EMI test plan, prototype testing procedure)

---

## Integration with Part 5 §7 (FMEDA) and §8 (Metrics)

The HW-SR specification (this workbook) is the **input** to:

1. **FMEDA (Part 5 §7):**  
   - Each HW-SR → one or more FMEA rows with failure modes, effects, and detected/undetected analysis.
   - Each HW-SR → DC% calculation (from diagnostic coverage claimed by specification).

2. **Metrics Calculation (Part 5 §8):**  
   - Aggregate DC% over all single-point failures per ASIL.
   - SPFM (Single Point Failure Metric): (failures with DC >= target) / (total single-point failures).
   - LFM (Latent Fault Metric): (undetected failures) / (total failures).
   - PMHF (Probabilistic Metric of Hazard Failure): estimate of random hardware failures leading to hazard.

3. **Verification (Part 5 §9):**  
   - Each HW-SR verification method → test plan (HIL, electrical, fault injection, environmental).
   - Confirmation review per ISO 26262-4 Table 4 (independence requirements for review personnel).

---

## References

- ISO 26262-5:2018 — Product development at the hardware level.
  - Clause 6: Specification of hardware safety requirements.
  - Clause 7: Failure Mode and Effects Analysis (FMEA) at hardware level.
  - Clause 8: Evaluation of hardware metrics.
  - Clause 9: Verification and validation of hardware.
  - Clause 10: Hardware architectural metrics.
- ISO 26262-9:2018 — Functional safety management.
  - Clause 5: ASIL decomposition.
  - Clause 7: Dependent Failure Analysis.
