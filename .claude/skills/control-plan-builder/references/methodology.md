# Control Plan Methodology

## What is a Control Plan?

A Production Control Plan (CP) is the AIAG-defined operational document that specifies how each manufacturing characteristic will be controlled during production. It is the essential link between engineering (PFMEA, specification) and the manufacturing floor (operator, inspector, maintenance).

The CP answers: For each characteristic that matters, what method will we use to detect drift or failure, what sample size and frequency, what is the reaction if we go out of control, and who owns the action?

## Control Plan Types (AIAG)

### 1. Prototype Control Plan
- **Timing**: Early stages of design verification (DFMEA/PFMEA in progress)
- **Characteristics**: Covers all potentially critical features; control methods are exploratory (SPC setup, trial 100% inspection)
- **Audience**: Design team, prototype builder, early supplier
- **Output**: Identifies which characteristics need tighter control in pre-launch; feeds into Pre-launch CP

### 2. Pre-Launch Control Plan
- **Timing**: After design is released; before full production ramp
- **Characteristics**: Refined based on pilot build; includes reaction plans and gage R&R targets
- **Control Methods**: SPC control limits calculated from pilot data; 100% inspection on high-risk items; poka-yoke proven in trial
- **Audience**: Manufacturing engineering, supplier quality, customer quality
- **Output**: Ready for production release; approved by OEM

### 3. Production Control Plan
- **Timing**: Ongoing, updated as needed during production
- **Characteristics**: Same as Pre-launch, but with live data (actual Cpk, Ppk, capability metrics)
- **Control Methods**: SPC charts live on shop floor; control limits from initial production runs; reaction plans tested
- **Audit Frequency**: Layered process audit (LPA) per OEM requirement
- **Audience**: Manufacturing floor (operators, inspectors, supervisors), maintenance, quality
- **Output**: Active document; reviewed quarterly or after process changes

## Relationship to PFMEA and MSA

### PFMEA Inputs
Each row in the Control Plan corresponds to one or more failure modes from the Production FMEA:
- **PFMEA Failure Mode** — the undesired state (e.g., "Solder joint cold")
- **PFMEA Severity/Occurrence/Detection** — drives priority and control urgency
- **PFMEA Preventive Actions** — inform the control method choice

High S/O/D (RPN > 100 typically) → Control method: SPC or 100% inspection
Medium S/O/D → Control method: SPC with audit
Low S/O/D → Control method: audit or mistake-proofing

### MSA Integration
Each gage (measurement instrument) referenced in the CP must have a Measurement System Analysis plan:
- **Gage R&R Study** (for variable data: Xbar-R or Xbar-S approach) — target R&R < 10% (acceptable), < 30% (conditional)
- **Attribute Agreement Analysis** (for pass/fail data: ICT, FCT, visual) — target > 90% appraiser agreement
- **Gage Capability** (if applicable) — verify discrimination (number of distinct categories ≥ 5 for attribute gages)
- **Periodic Verification** — annual or per OEM requirement

If a gage fails MSA, the CP characteristic cannot be relied upon; control method must shift (e.g., if dimensional gage R&R > 30%, move from SPC to 100% sorted inspection).

## AIAG Control Plan Layout

The standard AIAG CP worksheet contains these columns (left to right):

1. **Part/Process Number** — assembly/subassembly identifier
2. **Process Name/Operation Description** — "Solder PCB", "ICT test", "Label apply"
3. **Machine/Device/Jig/Tools for Mfg** — specific equipment
4. **Characteristics** — sub-columns:
   - Char number from drawing/spec
   - Product (dimension, function) or Process (temperature, pressure)
   - Spec/Tolerance
5. **Evaluation/Measurement Technique** — gage ID, e.g. "Coordinate Measuring Machine", "Automated Optical Inspection", "ICT Tester"
6. **Sample Size** — e.g., 5 parts, 1 part, every part (100%)
7. **Sample Frequency** — e.g., "every 1 hour", "every 50 parts", "continuous"
8. **Control Method** — e.g., "Xbar-R chart", "100% ICT", "Poka-yoke stop", "LPA quarterly"
9. **Reaction Plan** — triggers and actions if out of control

## Special Characteristics (SC)

Special Characteristics are those with outsized impact on safety, function, or fit-and-assembly. They are identified by:
- **Drawing callout** (flagged on engineering drawing, e.g., with black diamond or customer symbol)
- **PFMEA severity** (S ≥ 8) and/or **RPN threshold** (RPN > threshold, often 100)
- **OEM convention** — customer-specific definition (e.g., Critical = OEM safety-critical; Significant = OEM core function)

### Special Characteristic Classes

1. **Critical (SC-C)** — safety or legal regulation impact; color: red
   - Examples: brake stopping distance, airbag deployment, power steering function
   - Audit frequency: weekly
   - Control method: SPC with < 2σ control limits OR 100% inspection
   - Reaction plan: immediate stop + root cause

2. **Significant (SC-S)** — core function or fit/assembly impact; color: orange
   - Examples: bearing bore tolerance, connector pin length, firmware compatibility
   - Audit frequency: bi-weekly
   - Control method: SPC or 100% inspection, depending on process capability
   - Reaction plan: hold + 100% sort

3. **Standard** — routine production characteristic; color: light yellow
   - Examples: finish, cosmetic dimension, label position
   - Audit frequency: monthly
   - Control method: audit-based or mistake-proofing
   - Reaction plan: rework/scrap decision per quality engineer

## Process Capability and Control Method Selection

### Cpk ≥ 1.67 (or Ppk ≥ 1.33 for pre-launch)
→ Process is capable. Control method: **SPC (Xbar-R, Xbar-S, or p-chart)** with standard ±3σ or ±2σ limits.

### 1.33 ≤ Cpk < 1.67
→ Process is marginal. Control method: **SPC with tighter limits** (±1.5σ or ±2σ) and more frequent sampling, OR **100% inspection** if process unstable.

### Cpk < 1.33
→ Process is incapable. Control method: **100% inspection** (visual, dimensional, functional) until root cause corrected and Cpk improved.

If 100% is impractical → **Poka-yoke (mistake-proofing)** to prevent nonconforming parts from shipping.

## Control Methods in Detail

### 1. SPC (Statistical Process Control)

**Xbar-R Chart** (subgroup size 2–9, rational subgroups)
- Plot: Xbar (subgroup average) and R (subgroup range)
- Control limits: Xbar ±3σ; R chart ±D3/D4
- Used for: continuous variables (dimensions, temperatures, pressures)
- Frequency: e.g., every 1 hour, every 50 parts

**Xbar-S Chart** (subgroup size > 9, or unequal subgroups)
- Plot: Xbar and sample std dev S
- Used for: same as Xbar-R but larger subgroups or variable frequency

**p-Chart** (proportion defective)
- Plot: fraction of nonconforming parts per sample
- Used for: attribute data (pass/fail, good/bad), e.g. ICT test pass rate
- Frequency: e.g., every 100 parts, end of each shift

**np-Chart** (count of nonconforming)
- Plot: number of nonconforming in fixed subgroup
- Used for: attribute count when sample size constant

**c-Chart** (count of defects)
- Plot: number of defects per unit
- Used for: e.g., solder defects per board, visual flaws per part

**u-Chart** (defects per unit, variable unit size)
- Plot: defects per unit, normalized
- Used for: e.g., defects per meter of wire, flaws per square meter

### 2. 100% Inspection (Acceptance/Rejection)

**Visual Inspection**
- Operator or automated vision system checks all parts
- Criteria: spec limits, finish, color, label, orientation
- Risk: inspector fatigue (eye fatigue after 30–60 min continuous inspection)
- Best for: characteristics with clear pass/fail (not borderline)

**Dimensional Measurement**
- Gage (CMM, caliper, height gauge) measures 100% of critical dimensions
- Control: accept if within spec; reject if out
- Risk: gage R&R must be < 10% to be trusted
- Best for: tight tolerances where Cpk < 1.33

**Functional Test (100%)**
- ICT (In-Circuit Test) — electrical connectivity and component values
- FCT (Functional Test) — unit powers on, outputs correct function
- Burn-in — parts stressed under load to detect early failures
- Control: test result (pass/fail) is definitive
- Best for: electronic assemblies, firmware version check

### 3. Mistake-Proofing (Poka-Yoke)

**Prevention Poka-Yoke** — stops the process if characteristic goes out
- Example: Part holder has slot only for correct orientation → operator cannot insert wrong way
- Example: Solder machine detects insufficient solder and halts until corrected
- Cost: high (requires hardware/firmware change)
- Benefit: 100% error prevention (if design is correct)

**Warning Poka-Yoke** — alerts operator to condition but doesn't stop
- Example: Audible alarm if component placement X-offset > tolerance
- Example: Light stack (red/yellow/green) indicating process status
- Cost: low
- Benefit: operator catches drift before parts are made

### 4. Audit-Based Control (Layered Process Audit, LPA)

**Frequency per Special Class**
- Critical: weekly (or per shift)
- Significant: bi-weekly (or weekly)
- Standard: monthly (or quarterly)

**Audit Scope**
- Visual check of setup (machine settings, gage calibration)
- Measurement of first-piece and periodic pieces
- Process observation (operator technique, environment)
- Documentation review (SPC charts, gage R&R, maintenance log)

**Control Limit**
- If audit finds condition out of spec → stop run, sort suspect parts, investigate
- If trend visible (e.g., increasing wear) → schedule preventive maintenance

---

## Control Plan Approval & Maintenance

### Pre-Launch Sign-Off
- Supplier Quality Manager approves control methods and feasibility
- Supplier Plant Manager approves resource/cost impact
- Customer Engineering approves control method aligns with design intent
- Customer Quality approves sampling frequency and reaction plan

### Production Release
- Print and post at each operation (laminated, 11x17")
- Train operators, inspectors, and supervisors on reaction plans
- Load SPC data collection into MES or manual log
- Calibrate all gages per measurement plan

### Ongoing Updates
- Quarterly review: Are control limits still valid? Is process drifting?
- Post-change review: If machine, tooling, or setup changed, update CP and pilot
- RPN reduction: If PFMEA corrective action reduces RPN, can control method be relaxed? (rarely done; better to keep tight)

---

## Common Pitfalls

1. **SPC Limits Set Too Tight**
   - Limit: ±2σ when spec is ±3σ. Result: Many false "out-of-control" signals → operator fatigue, shutdown costs.
   - Fix: Align SPC limits to process window, not spec; audit process capability before setting.

2. **Sampling Frequency Too Loose**
   - Frequency: "every 4 hours" for a high-SPC characteristic.
   - Result: Drift detected too late; nonconforming parts ship.
   - Fix: For Critical SC, sample at least every 1–2 hours; for SPC variables, at least every 50–100 parts.

3. **Reaction Plan Not Tested**
   - CP says "100% sort if out of control" but no one is trained or has time.
   - Result: When OOC signal occurs, parts are shipped anyway.
   - Fix: Conduct dry-run (pilot) of reaction plan before production release; assign clear owner and timeline.

4. **Wrong Gage for Control Method**
   - CP specifies SPC Xbar-R but gage R&R is 35% (unacceptable for SPC).
   - Result: SPC chart useless; control method fails.
   - Fix: Verify MSA plan before CP release; if gage inadequate, shift to 100% or poka-yoke.

5. **Special Characteristics Not Clearly Marked**
   - Drawing and CP don't agree on which characteristics are Critical/Significant.
   - Result: Operator audits wrong things; critical feature drifts unnoticed.
   - Fix: Use customer symbol (e.g., diamond, star) on drawing; echo in CP SC tab.

6. **Audit Frequency Disconnected from RPN**
   - High-RPN characteristic (Severity 9, Occurrence 8) audited monthly.
   - Low-RPN characteristic audited weekly.
   - Fix: Tie audit frequency to Special Class (Critical = weekly, Significant = bi-weekly).

---

## Integration with APQP and PPAP

- **APQP (Advanced Product Quality Planning)**: CP is a gate deliverable (Phase 3, Design & Development). Gate sign-off requires approved CP.
- **PPAP (Production Part Approval Process)**: CP is a submission item (core document in Submission Level 3 & above). OEM audits CP before granting production release.
- **IATF 16949**: Section 8.3 on "Control of Production and Service Delivery" and 8.5.1 on "Control of Production Processes" require CP for all special characteristics and processes with special control needs.

Control Plan is foundational to all three frameworks.
