# PFMEA Methodology — AIAG-VDA 2019

## Overview

Process Failure Mode, Effects, and Analysis (PFMEA) is a systematic, cross-functional approach to identify potential failures in manufacturing process steps and implement controls to prevent or detect those failures before they reach the customer.

The PFMEA is a **foundational control document** that directly feeds the **Control Plan**. Every high-priority failure mode identified in PFMEA spawns one or more control methods in the Control Plan (e.g., 100% inspection, SPC charting, mistake-proofing).

## AIAG-VDA 7-Step PFMEA Process

### 1. **Plan and Prepare**
   - Define scope: which manufacturing steps to analyze
   - Assemble cross-functional team (manufacturing engineer, quality, operations, maintenance)
   - Review related documents: process flow chart, DFMEA, prior FMEAs, field failure history
   - Establish timeline and responsibilities

### 2. **Review the Process Function**
   - Itemize each process step in sequence (e.g., PCB receive → SMT placement → reflow → ICT → assembly → FCT → programming → pack)
   - For each step, document:
     - What it must accomplish (function)
     - How it accomplishes it (method, equipment, parameters)
     - What characteristics it produces or verifies
   - Identify special characteristics (SC) early: safety, performance, or customer-critical attributes

### 3. **Structure Analysis**
   - **Process Step** — discrete manufacturing operation (e.g., "Reflow Solder")
   - **Process Function** — what the step must do (e.g., "Melt solder and form reliable electrical/mechanical joints")
   - **Requirements** — specification or standard (e.g., "IPC J-STD-001 Class A")

### 4. **Failure Mode Identification**
   For each process step, brainstorm failure modes:
   - How can the process step fail to perform its function?
   - What can go wrong (process-wise, not product-wise)?

   Examples:
   - SMT placement: wrong component, wrong orientation, misalignment, missing component
   - Reflow: temperature out of spec, insufficient dwell time, oxygen-rich atmosphere, solder bridging
   - ICT: probe misalignment, test program error, false pass/false fail, test coverage gap
   - Final assembly: wrong variant installed, mechanical damage, loose fastener

### 5. **Effects and Severity Analysis**
   - **Failure Effect (Next Operation)** — how does this failure propagate to the next process step?
   - **Failure Effect (End User)** — what is the final impact if the failure escapes to the customer?
   - **Severity Rating (1-10)** — how serious is the end-user effect? (See AIAG-VDA Severity Table)

   Severity guidelines:
   - **9-10**: Hazardous (safety), customer can be injured, or regulatory non-compliance
   - **7-8**: Major (performance loss, warranty return, customer dissatisfaction)
   - **5-6**: Moderate (reduced performance, may be noticed)
   - **3-4**: Minor (customer may not notice, or easily reparable)
   - **1-2**: Negligible (no customer impact)

### 6. **Causes, Occurrence, and Detection**
   
   **Failure Cause** — root cause(s):
   - What design, process, or operational factor allows this failure mode to occur?
   
   **Occurrence Rating (1-10)** — how likely is the failure mode to occur?
   - Baseline from process capability, pilot yield, field data, or engineering judgment
   - 1-2: Rare (< 1 in 100,000 units)
   - 3-4: Low (1 in 10,000 to 100,000)
   - 5-6: Moderate (1 in 1,000 to 10,000)
   - 7-9: High (1 in 10 to 1,000)
   - 10: Almost certain (> 1 in 10)
   
   **Detection Control** — inspection or test method:
   - 100% automated (AOI, X-ray, functional test): Detection rating 1-4
   - 100% manual (visual, dimensional gage): Detection rating 5-7
   - Sampling (SPC, AQL): Detection rating 7-9
   - No inspection: Detection rating 10 (not detectable)
   
   **Detection Rating (1-10)** — likelihood the detection control catches the defect before shipment
   - 1: Almost certain to detect
   - 5: Moderate chance to detect
   - 10: Cannot detect (or control does not exist)

### 7. **Action Prioritization and Control Planning**
   
   **Action Priority (AP)** — computed from Severity × Occurrence × Detection lookup table (AIAG-VDA):
   - **H (High)**: Risk is unacceptable; requires immediate action
   - **M (Medium)**: Risk is marginal; action recommended
   - **L (Low)**: Risk is acceptable; monitor or document
   
   **Recommended Action** — if AP = H or M:
   - Prevent the failure (design change, process improvement, mistake-proofing)
   - Detect the failure (add or enhance inspection, increase detection capability)
   - Both (preferred)
   
   **Assigned To & Target Date** — owner and completion deadline
   
   **Verify & Close** — once action is implemented, re-rate S/O/D and verify AP improves

## Integration with Control Plan

The Control Plan is the **manufacturing control document** that translates PFMEA findings into operational controls:

| PFMEA | Control Plan |
|-------|--------------|
| Failure Mode | Special Characteristic |
| Severity + Occurrence + Detection | Control Method (e.g., 100% inspection, SPC) |
| Prevention Control | Process Control (design/setup to prevent) |
| Detection Control | Inspection/Test Method (sampling plan, acceptance limits) |
| Recommended Action | Control Verification (how you prove the control is working) |

Example:
- PFMEA: "Cold solder joint" (S=8, O=3, D=4, AP=M)
- Control Plan: "Reflow Temperature Profile" — continuous SPC monitoring; upper/lower control limits per IPC J-STD-001; reaction plan if out of control

## Integration with DFMEA

- **DFMEA** identifies design-level risks (component selection, schematic, layout)
- **PFMEA** identifies manufacturing-level risks (process capability, operator skill, equipment maintenance)

They are complementary:
- DFMEA may identify a risk "Component soldered backwards"; PFMEA addresses "How do we prevent/detect it in manufacturing?"
- DFMEA: severity, design mitigation; PFMEA: process mitigation (inspection, mistake-proofing)

## Special Characteristics (SC vs. CC)

- **SC (Special Characteristic)** — attribute that is critical to safety, performance, legal/regulatory compliance, or vehicle functionality. Requires 100% verification and formal control in the Control Plan.
- **CC (Customer Characteristic)** — attribute that is critical to customer expectation (appearance, durability, convenience). Requires statistical control (SPC, sampling).

SC/CC flags in PFMEA guide Control Plan control method selection:
- SC → 100% Inspection (AOI, X-ray, functional test, manual 100%)
- CC → Statistical Control (SPC charting, AQL sampling)

## Key Metrics & Targets

PFMEA does not use the metrics formula (S × O × D as a raw score is discouraged in AIAG-VDA 2019). Instead:
- **Action Priority** is looked up from the AIAG-VDA 3D table: (S, O, D) → (H/M/L)
- **High (H)** items require action before production release
- **Medium (M)** items recommended for action; may be deferred with justification
- **Low (L)** items may be monitored or documented

## Common Process Step Taxonomy (Electronics / PCB Assembly)

1. **PCB Receive & Inspection** — incoming QC on bare PCBs
2. **Component Kitting / Preparation** — sort, verify, dispense components
3. **Solder Paste Printing** — screen print or stencil paste onto PCB
4. **SMT Component Placement** — pick-and-place machine (accuracy, orientation)
5. **Reflow Soldering** — thermal profile; solder joint formation
6. **Automated Optical Inspection (AOI)** — detect placement and solder defects
7. **Wave Solder or Hand Solder** — through-hole components (if applicable)
8. **ICT (In-Circuit Test)** — electrical continuity, shorts, opens, parametric test
9. **Conformal Coating** — moisture/corrosion protection (if required)
10. **Final Assembly** — mechanical integration (mechanical sub-assemblies, connectors, enclosure)
11. **Functional Test (FCT)** — verify end-to-end product functionality
12. **Programming** — load firmware, calibration, serial number programming
13. **Labeling & Serialization** — barcode, label, BOM verification
14. **Packaging & Shipping** — cushioning, moisture barrier, documentation

## Document Retention

PFMEA is a **living document**:
- Update when process capability improves (lower O)
- Update when detection controls enhance (lower D)
- Add lessons learned from production yield/field data
- Archive prior versions as historical record

Standard retention: for life of product + 3 years (or per customer/regulatory requirement)
