# HW Architecture Refinement Methodology

## Overview

ISO 26262-5 §7 (Hardware Architecture) bridges the TSC's system-level safety mechanisms into concrete hardware designs. The TSC specifies *what* safety mechanisms must be implemented (e.g., "dual-core lockstep with cross-check"); the HW Architecture specifies *where* and *how* on the physical board.

## Key Refinements

### 1. Bill of Materials (BOM)

The HW Architecture inventory lists every IC, passive component, connector, and discrete element:

- **HW Element ID** (HW-E-001, HW-E-002, …): unique identifier per part instance
- **Type**: MCU, Sensor IC, Actuator IC, Power IC, Discrete, Connector, Passive
- **Part Number**: e.g., TMS570LC4357 (TI ARM Cortex-R5), ADXL375 (Analog Devices accelerometer)
- **Package**: BGA-337, LQFP-144, SOIC-8, 0603 resistor, etc.
- **Supplier** and **Part Number** for traceability and procurement
- **Baseline FIT Rate** (Failures In Time per billion hours): derived from IEC 62380 or supplier datasheet
  - Typical ranges: MCU ~50–200 FIT, analog sensor IC ~30–100 FIT, discrete ~1–10 FIT, passive ~0.1–5 FIT
  - Higher qualification (AEC-Q100 Grade 0 vs. Grade 2) reduces FIT ~20–50%
- **Safety Qualification**: AEC-Q100 (automotive), AEC-Q200 (extended temp), none (QM)

### 2. Linking BOM to TSC

Each HW element has a `tsc_node_id` field linking it back to the TSC's block diagram:

- TSC node N10 (Main MCU) → HW-E-001 (TMS570LC4357)
- TSC node N20 (Redundant Safety MCU) → HW-E-002 (TMS570LC4357)
- TSC node N30 (IMU Sensor) → HW-E-003 (ADXL375) + HW-E-004 (L3GD20)

This traceability enables:
- Automatic roll-up of FIT from HW elements to TSC nodes
- Common-cause analysis: if two TSC nodes map to different ICs but share a power rail, that coupling is captured
- FMEDA cross-checks: failure modes from datasheet link to TSC nodes and FSRs

### 3. Safety Mechanism Allocation to ICs

The TSC chose mechanisms (lockstep, ECC, BIST, watchdog, etc.). The HW Architecture maps each mechanism to concrete silicon:

- **Lockstep** (TSC SM01): implemented in TMS570LC4357 (dual ARM Cortex-R5 cores + compare unit)
- **ECC on RAM** (TSC SM05): built-in on TMS570LC4357 (SECDED on SRAM)
- **Plausibility Check** (TSC SM11): firmware routine running on main MCU, not a specific IC
- **Supply Monitor** (TSC SM14): dedicated OV/UV IC (e.g., TLV803 or integrated in power MCU) or MCU internal ADC

Each HW element lists:
- Which TSC safety mechanisms it implements (IDs and names)
- The allocated ASIL for that mechanism
- Detection coverage % (DC), to be validated by FMEDA

### 4. Power Architecture

Defines the voltage rails, regulators, monitoring, fusing, and isolation:

- **Rails**: 12V_main (battery input), 5V_sensor_A (logic IO), 3.3V_logic (MCU core), isolated 5V_diag (diagnostics)
- **Regulator Type**: linear (low noise, low efficiency), switching (high efficiency, EMI), isolated (high voltage/current difference)
- **Monitoring**: OV threshold (e.g., 5.5V for 5V rail), UV threshold (e.g., 4.5V), reaction (assert fault flag, trigger watchdog, disable outputs)
- **Fusing**: amperage per rail, response time, and reset behavior (auto-reset vs. manual)
- **Isolation**: document which rails are isolated (e.g., 12V isolated from 5V via optocoupler or transformer) and which are grounds-connected
- **Common-cause risk**: if two redundant channels both draw from 5V_sensor_A, a regulator fault affects both — must be mitigated by independent power monitoring or dual regs

### 5. Clock Architecture

Defines the clock sources, distribution, monitoring, and redundancy:

- **Sources**: 
  - XTAL_50MHz_A: external 50 MHz crystal oscillator on main PCB
  - RC_internal: on-chip RC oscillator (lower accuracy, used as watchdog backup)
  - PLL_from_XTAL: phase-locked loop derived from XTAL, used for MCU core clock
- **Distribution tree**: main MCU → daughter cards via SPI/CAN (often clock-encoded in messages)
- **Monitoring**: 
  - **XTAL fail detection**: watchdog timer expects a clock edge within a window; if missed, triggers safe state
  - **PLL lock loss**: PLL monitor detects lock loss (jitter or frequency drift) and switches to RC backup or asserts fault
  - **Clock gating**: ensure no synchronous logic is clock-gated without monitoring (frozen logic is invisible to watchdog)
- **Redundancy**: 
  - **Single-channel** (XTAL only): watchdog via independent RC acts as secondary detection
  - **Dual-channel** (XTAL + independent backup crystal): increases availability, requires independent monitoring

### 6. Common-Cause Failure Analysis (CCFA)

For every redundancy pair (e.g., dual lockstep cores, dual sensors, dual power monitors), the architecture documents potential couplings:

- **Shared rail**: both channels powered by the same 5V regulator
  - Mitigation: independent regs, fused separately, monitored independently, or accept reduced DC and rely on functional test
- **Shared package**: both channels on the same IC (e.g., dual Cortex-R5 in one TMS570LC4357)
  - Mitigation: none (inherent); must accept coupling or use external redundancy (second IC)
- **Shared PCB region**: both channels in same thermal zone or humidity region
  - Mitigation: physical separation, conformal coating, or accept test-time/field monitoring
- **Shared environmental zone**: both in engine bay with same vibration/temperature exposure
  - Mitigation: design isolation (thermal sleeve, EM shielding), or accept and validate robustness

Unmitigated couplings feed into FMEDA as dependencies: a single failure cause may affect both channels, reducing SPFM.

### 7. FIT Rate Aggregation

The HW Element Catalog lists baseline FIT for each part. The Bill of Materials (tab 10) rolls up FIT:

- **Per element type**: sum MCU FIT, sum sensor FIT, sum passive FIT
- **Per safety function**: attribute FIT to the TSC safety function it supports
  - E.g., HW-E-001 (main MCU) + HW-E-014 (watchdog IC) + HW-E-015 (clock monitor) → FIT for the "Process Fault Detection" function

Total FIT is used in FMEDA for:
- SPFM (Single Point Failure Metric) = 1 − (undetected single failures / total failures)
- PMHF (Probabilistic Metric for Hardware Failures): λ_det and λ_undetected per failure class

Do **not** replace FMEDA-grade FIT estimation with BOM-level baseline. The baseline is an order-of-magnitude starting point; FMEDA refines it per failure mode and per design choice (e.g., which input drives which safety mechanism, whether feedback is monitored).

## Integration with Downstream Activities

### FMEDA (Failure Modes, Effects, Defect Analysis)

FMEDA uses the HW Architecture as input:
- Part numbers and datasheets from the HW Element Catalog
- Functional safety mechanisms from the Safety Mechanism Allocation tab
- Common-cause risks from the CCFA tab

### Layout and Schematic

Layout uses the HW Architecture's power/clock architecture and PCB design constraints:
- Separate analog and digital grounds as per power architecture
- Route clock and power distribution per the clock/power architecture tabs
- Physical placement (separation, thermal management) per common-cause mitigation notes

### Test and Verification

- **Production test** validates presence and function of ICs (JTAG scan, signature test)
- **HIL (Hardware-in-the-Loop)** stress-tests safety mechanisms (voltage ramps, clock faults, sensor injection)
- **Field diagnostics** monitor power rails and clocks per HSI spec (from TSC)

## Key Metrics and Acceptance Criteria

1. **BOM Coverage**: 100% of TSC nodes must map to HW elements (no orphaned nodes)
2. **FIT Budget**: total system FIT ≤ FMEDA baseline derived from PMHF requirement
3. **Power/Clock Redundancy**: every safety-critical rail/clock has monitoring; undetected loss of power or clock → ASIL-dependent timeout
4. **Common-Cause**: every coupling ≥ ASIL C must have documented mitigation or justified acceptance with test evidence
5. **Qualification**: MCU and sensor ICs ≥ AEC-Q100; passive capacitors ≥ X7R or equivalent

## References

- ISO 26262-5:2018, Part 5 — Product development at the hardware level
  - §7: Hardware design (architecture, FMEDA, metrics)
  - Annex B: SPFM, LFM, PMHF calculation examples
- IEC 62380:2004 — Reliability data for electronic components used in telecommunications equipment
- AEC-Q100, AEC-Q200 — Automotive component qualification standards
- Component datasheets: FIT rates, FMEDA reports, absolute maximum ratings, derating curves
