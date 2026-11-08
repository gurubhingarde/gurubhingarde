# ISO 26262-5 §7 Hardware Architecture — Tab Mapping

## Standard Structure

ISO 26262-5 §7 (Hardware design) requires:

1. **Hardware architecture specification** — block diagram, components, interfaces
2. **Hardware design specification** — schematic, PCB layout, power/clock distribution
3. **Hardware FMEA and FMEDA** — failure mode enumeration and metric calculation
4. **Safety mechanisms** — how each ISO 26262 mechanism (lockstep, ECC, watchdog, etc.) is implemented
5. **Common-mode and common-cause analysis** — shared faults affecting redundant channels
6. **Hardware metrics** (SPFM, LFM, PMHF) — verification that hardware meets allocated ASIL
7. **Hardware verification report** — traceability to design, test coverage, design review

## Generator Output Alignment

The hw-architecture-builder generates 12 tabs, aligned to §7 requirements:

### Tab 00: Title Page
**Standard Ref**: §7.1 (Hardware design specification contents)
- Document ID, revision, project, author, approver
- Linked TSC (upstream architectural decision record)
- Statement that this document implements ISO 26262-5 §7 per allocated ASIL

### Tab 01: Document Control
**Standard Ref**: §7.1.1 (Document management)
- Revision history with change descriptions and approval
- Traceability to FMEA updates when architecture is revised

### Tab 02: TSC Architecture Echo
**Standard Ref**: §7.2.1 (Architecture specification — imports from system level)
- Read-only echo of TSC's HW components and SW partitions
- Ensures bidirectional traceability: TSC node → HW element → FMEDA failure mode

### Tab 03: PCB Design
**Standard Ref**: §7.2.2 (Hardware design specification)
- Board-level layout: main PCB, daughter cards, interconnect
- Layers, dimensions, key areas (analog region, digital region, power distribution)
- Foundation for schematic routing and layout verification

### Tab 04: HW Element Catalog
**Standard Ref**: §7.2.2 (Component specifications)
- Concrete list of every IC, discrete, passive, connector
- Part number, package, pin count, supplier
- Baseline FIT rate (IEC 62380 or datasheet source)
- Safety qualification (AEC-Q100/Q200 grade)
- Links to datasheets and absolute maximum ratings

### Tab 05: Safety Mechanism Allocation
**Standard Ref**: §7.3 (Safety mechanisms — how are ISO 26262 mechanisms implemented?)
- Per HW element, which safety mechanisms apply
- Cross-reference to TSC mechanism catalog (mechanism ID, name)
- Allocated ASIL for each mechanism
- Detection coverage target (DC %, to be validated by FMEDA)

### Tab 06: HW SR Allocation Matrix
**Standard Ref**: §7.3.1 (Requirements allocation — mapping HW-SR to architecture)
- Cross-reference matrix: rows = HW Safety Requirements (derived from HW-TSRs), columns = HW elements
- Marks which HW element(s) implement each HW-SR
- Enables traceability: FSR → HW-TSR → HW-SR → HW element → FMEA failure mode

### Tab 07: Power Architecture
**Standard Ref**: §7.2.3 (Power distribution, §7.3.2 (Supply monitoring)
- Power rails: 12V_main, 5V_logic, 3.3V_core, isolated domains
- Regulator specs: input/output voltage, current capacity, efficiency, thermal derating
- OV/UV monitoring: thresholds, reaction (fault flag, watchdog trigger)
- Fusing: amperage, reset behavior
- Isolation between rails (ground-connected, opto-isolated, transformer-isolated)
- Failure modes: regulator dropout, fuse nuisance trip, floating rail
- Common-cause risks: dual channels on same regulator, same fuse

### Tab 08: Clock Architecture
**Standard Ref**: §7.2.4 (Oscillator and clock distribution), §7.3.3 (Oscillator monitoring)
- Clock sources: crystal (XTAL), internal RC, PLL
- Frequency, tolerance, temperature stability
- Distribution: MCU clock → daughter cards (via message encoding or direct)
- Monitoring: XTAL fail detection (watchdog timeout if no clock edge within window), PLL lock loss
- Redundancy: single XTAL + RC backup vs. dual independent crystals
- Failure modes: XTAL failure, PLL lock loss, clock gating unnoticed, jitter
- Common-cause risks: all logic shares one XTAL

### Tab 09: Common-Cause Analysis
**Standard Ref**: §7.3.4 (Dependent failure analysis — CCFA for redundant channels)
- Per redundant pair (e.g., dual MCUs, dual sensors), enumerate shared resources:
  - Shared power supply → mitigated by independent monitoring or dual regs?
  - Shared IC package → inherent; mitigated by external redundancy?
  - Shared PCB region → thermal coupling? Conformal coating?
  - Shared environmental zone → temperature/vibration exposure?
- Mark each coupling as:
  - **No** — coupling not present (independent supply, independent package, separate physical location)
  - **Yes — Mitigated by** [design feature, e.g., "separate 5V regs + independent monitoring"] — coupling exists but mitigated
  - **Yes — Unmitigated** — coupling exists with no mitigation; must justify via testing or reduce ASIL
- Unmitigated couplings feed into FMEDA as dependencies for λ_detected and λ_undetected calculation

### Tab 10: Bill of Materials (BOM)
**Standard Ref**: §7.2.2 (Hardware design specification — component list), §7.4 (Hardware metrics — FIT aggregation)
- Summary BOM: list each unique part number, quantity, total FIT per part type
- Roll up FIT by element type (MCUs, sensors, power ICs, discretes, passives)
- Roll up FIT by safety function (fault detection, reaction, monitoring)
- Total system FIT: used in PMHF calculation (ISO 26262-5 Annex B)

### Tab 11: References
**Standard Ref**: §7.1 (Traceability)
- TSC file path and revision
- Schematic and layout documents (for detailed design phase)
- Component datasheets (for absolute maximum ratings, FIT sources, ESD/EMI specs)
- IEC 62380 or supplier FIT data sources
- Applicable standards: ISO 26262-5, IEC 61508 (if applicable), AEC-Q100/Q200
- FMEA/FMEDA references (link to Part 5 §7.4.1 FMEA requirements, Annex B FMEDA guidance)

## Verification Rigor by ASIL

### ASIL A
- ✓ BOM traceability (every TSC node → HW element)
- ✓ FIT rate baseline (IEC 62380 or datasheet)
- ✓ Power/clock monitoring present
- Verification: walk-through of architecture, component selection rationale

### ASIL B
- All ASIL A, plus:
- ✓ Common-cause analysis for redundant pairs
- ✓ Safety mechanism mapping with DC target
- ✓ Power/clock redundancy documented
- Verification: semi-formal review (checklist), FMEA scaffolding against failure mode taxonomy

### ASIL C
- All ASIL B, plus:
- ✓ Detailed CCFA with quantitative coupling analysis
- ✓ Functional FMEDA with DC validation (test or analysis)
- ✓ Qualification evidence (AEC-Q100 certs, supplier FMEA)
- Verification: formal FMEDA per ISO 26262-5 Annex B, design review with external audit

### ASIL D
- All ASIL C, plus:
- ✓ Comprehensive FMEDA with all failure modes enumerated
- ✓ PMHF metric validation (λ_detected, λ_undetected within budget)
- ✓ Independence evidence for safety mechanisms (e.g., lockstep cores + independent feedback, watchdog with independent oscillator)
- ✓ Environmental stress screening and device selection validation
- Verification: full FMEDA per Annex B, design review by independent party (V&V team)

## Handoff to Downstream Activities

### To Layout / Schematic Team
- Tab 03 (PCB Design): board dimensions, layers, key areas
- Tab 07 (Power Architecture): rail assignments, regulator specs, ground/power routing rules
- Tab 08 (Clock Architecture): clock distribution tree, skew limits

### To FMEDA Team
- Tab 02 (TSC Echo): system-level function assignments
- Tab 04 (HW Element Catalog): part numbers, datasheets
- Tab 05 (Safety Mechanism Allocation): which mechanism is on which IC, DC targets
- Tab 09 (CCFA): shared resources and mitigation strategies

### To Verification / Test Team
- Tab 05 (Safety Mechanism Allocation): detection mechanisms to be functionally tested
- Tab 07, 08 (Power, Clock): thresholds and monitoring to validate (voltage/frequency sweep, injection)
- Tab 10 (BOM): component selection for procurement, supply chain risk

## Gap Analysis Checklist

When reviewing the generated tabs:

1. **Traceability**: Every HW-SR in Tab 06 must map to ≥1 HW element in Tab 04. No orphaned requirements.
2. **FIT sourcing**: Every part in Tab 04 must have a baseline FIT with source citation (datasheet, IEC 62380, supplier FMEDA).
3. **Mechanism coverage**: Every TSC mechanism (Tab 05) must have a concrete implementation (e.g., lockstep → TMS570 dual cores, watchdog → separate IC).
4. **Common-cause**: Every redundant pair in Tab 09 must have either "No" or "Yes — mitigated by" with rationale. No "TBD".
5. **Power/clock**: Every rail and clock source must have monitoring (Tab 07, 08) with thresholds and reaction defined.
6. **References**: Every part number must cite a datasheet; every FIT rate must cite a source (Tab 11).

## References

- ISO 26262-5:2018, §7 — Product development at the hardware level
- ISO 26262-5:2018, Annex B — SPFM, PMHF, diagnostic coverage calculation
- IEC 62380 — Reliability data for electronic components
