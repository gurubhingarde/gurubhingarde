# AIAG APQP Phase Deliverables Reference

This document lists the complete standard deliverable checklist per APQP phase from the AIAG APQP Manual (2nd Edition). These are default items; customize per your customer's specific requirements.

## Phase 1: Plan and Define Program

Standard deliverables and descriptions:

| ID | Deliverable | Description | Owner | Notes |
|---|---|---|---|---|
| P1-D01 | Voice of Customer (VOC) Analysis | Document customer inputs, expectations, and stated needs for the program. Includes customer survey, interviews, design requirements handoff. | Quality Engineer | Foundation for CSL/CTQ definition |
| P1-D02 | Business Case / Business Plan | Program business justification: revenue opportunity, cost targets, ROI, strategic fit, contract terms, margin targets. | Program Manager | Financial commitment decision point |
| P1-D03 | Customer Requirements Review (CRR) | Formal review and sign-off of all customer-stated requirements (drawing, specification, CSL, testing, packaging, delivery). | Quality Engineer | Defines scope and acceptance criteria |
| P1-D04 | Preliminary Bill of Materials (BOM) | Initial component list with make/buy decisions, long-lead suppliers identified, cost estimates, sourcing strategy. | Design Engineer | Input to supplier cascade |
| P1-D05 | Preliminary Process Flow | High-level manufacturing and assembly process flow; identifies key operations, equipment needs, capacity constraints. | Manufacturing Engineer | Input to PFMEA planning |
| P1-D06 | Design Goals and Targets | Product performance targets (dimensional, functional, environmental, reliability, cost, weight, etc.). Derived from customer requirements. | Design Engineer | Drives design phase activities |
| P1-D07 | Reliability and Durability Targets | MTBF (Mean Time Between Failures), MTTR, design life, FTA (Fault Tree Analysis) scope, environmental stress screening, warranty implications. | Quality Engineer | Input to DFMEA and testing plans |
| P1-D08 | Preliminary Special Characteristics List | Initial list of Critical Characteristics (CC) and Special Characteristics (SC) per customer and regulatory requirements; symbols to be finalized in Phase 2. | Quality Engineer | Traceability foundation |
| P1-D09 | Team Kickoff and Gate 1 Review | Cross-functional team established, roles assigned, APQP schedule agreed, Gate 1 review held and passed (decision: proceed to design). | Program Manager | Program governance checkpoint |

**Gate 1 Exit Criteria:**
- VOC captured and clearly documented
- Customer requirements review complete, CSL/CTQ defined
- Preliminary process flow feasible at planned volumes
- Preliminary BOM and make/buy strategy documented
- Business plan approved by management
- Team aligned on program schedule and governance
- Team member roles and responsibilities defined

## Phase 2: Product Design and Development

Standard deliverables and descriptions:

| ID | Deliverable | Description | Owner | Notes |
|---|---|---|---|---|
| P2-D01 | Design FMEA (DFMEA) | Per AIAG-VDA, document all design failure modes, effects (severity), current controls, RPN, and mitigation actions. Update iteratively through design reviews. | Design Engineer | Supports design maturity |
| P2-D02 | Design for Assembly (DFA) and Design for Manufacturability (DFM) | Report on design simplification, ease of assembly, component standardization, cost optimization. Incorporates manufacturing and assembly insights. | Design Engineer + Manufacturing Engineer | Reduces design defects |
| P2-D03 | Design Verification Plan and Report (DVP&R) | Plan describes all verification tests (dimensional, functional, environmental, fatigue, reliability). Report documents test results, comparison to targets, sign-off. | Quality Engineer | Proves design meets requirements |
| P2-D04 | Design Reviews (with Prototype Build) | Three design review gates (DR1 Preliminary, DR2 Interim, DR3 Final) with progressively mature prototypes (breadboard, prototype, design validation hardware/software). | Design Engineer | Gate events ensure design progression |
| P2-D05 | Engineering Drawings and Specifications | Final product drawings (per ISO, ASME, customer standard), material specifications, assembly drawings, electrical schematics, firmware/software source code snapshots. | Design Engineer | Foundation for manufacturing |
| P2-D06 | Finalized Special Characteristics (SC/CC) List | Final list of all SC and CC per customer drawing symbols, AIAG definition, and regulatory requirements. Cross-referenced to drawings and test plans. | Quality Engineer | Traceability lock |
| P2-D07 | Supplier APQP Cascaded | APQP requirements, schedule, drawings, specifications, special characteristics, and PPAP level communicated to all suppliers. Supplier acknowledgment obtained. | Supplier Quality | Supply chain alignment |
| P2-D08 | Prototype Build and Functional Testing | Prototype hardware/software built and tested to validate design intent. Includes performance testing, assembly process validation, design change log. | Manufacturing Engineer + Design Engineer | Design proof-of-concept |
| P2-D09 | Gate 2 Review (Design Confirmation) | Formal review confirming design adequacy to proceed to process design phase (decision: proceed, hold, or rework). | Program Manager | Design maturity gate |

**Gate 2 Exit Criteria:**
- DFMEA complete, all high-RPN items mitigated or accepted
- DVP&R plan approved, testing underway or complete, results meet targets
- Design reviews (DR1/2/3) conclusive: design satisfactory, no major open issues
- Prototype build successful, preliminary performance acceptable
- All SC/CC finalized and traced to drawings
- Supplier APQP cascade complete with acknowledgment
- No critical design risks remaining

## Phase 3: Process Design and Development

Standard deliverables and descriptions:

| ID | Deliverable | Description | Owner | Notes |
|---|---|---|---|---|
| P3-D01 | Packaging Specifications and Standards | Complete packaging design (materials, dimensions, stacking, weight limits, labeling, customer logo, barcode, containment methods, environmental protection). | Quality Engineer | Customer/regulatory compliance |
| P3-D02 | Process Flow Chart | Detailed step-by-step manufacturing and assembly flow with all operations, equipment, sequence, cycle time, yield expectations, rework/scrap paths. | Manufacturing Engineer | PFMEA foundation |
| P3-D03 | Floor Plan and Layout | Facility layout showing equipment placement, material flow, work-in-process (WIP) staging, inspection stations, storage, shipping dock. | Manufacturing Engineer | Capacity and ergonomics validation |
| P3-D04 | Characteristics Matrix | Traceability document linking product characteristics (SC/CC) to process variables (parameters, equipment settings, inspections). Shows which process step controls each characteristic. | Quality Engineer | Control plan basis |
| P3-D05 | Process FMEA (PFMEA) | Per AIAG-VDA, document all process failure modes, effects (severity), current controls, RPN, and mitigation actions. Update through trial run. | Manufacturing Engineer | Identifies critical process variables |
| P3-D06 | Pre-Launch Control Plan (PLCP) | Reaction plan for handling non-conformances or deviations during trial run and pre-SOP production. Defines escalation, customer notification, containment, disposition of out-of-spec parts. | Quality Engineer | Risk management pre-SOP |
| P3-D07 | Process Instructions and Work Instructions | Standard operating procedures (SOPs) for each process step, machine setups, material handling, tooling, safety, quality checkpoints. | Manufacturing Engineer | Operator direction and consistency |
| P3-D08 | Measurement System Analysis (MSA) Plan | Defines measurement methods, gages, repeatability/reproducibility (Gage R&R) requirements, acceptance criteria for all SC/CC. Acceptance threshold typically Gage R&R < 10% for critical, < 30% for important. | Quality Engineer | Measurement adequacy |
| P3-D09 | Preliminary Process Capability Study Plan | Statistical sampling plan for trial run: sample size, frequency, acceptance criteria (Cpk/Ppk targets, confidence level). Defines SPC charting strategy (control limits, action plans). | Quality Engineer | Quantitative capability definition |
| P3-D10 | Gate 3 Review (Process Confirmation) | Formal review confirming process design adequacy to proceed to production trials (decision: proceed, hold, or rework). | Program Manager | Process maturity gate |

**Gate 3 Exit Criteria:**
- Process design documented (flow chart, floor plan, layout)
- PFMEA complete, high-RPN items controlled or mitigated
- Characteristics Matrix complete and approved
- MSA plan finalized for all SC/CC, gages selected
- Preliminary process capability study plan approved
- Pre-launch control plan (reaction plan) approved
- Process instructions and work instructions drafted or finalized
- No critical process risks remaining

## Phase 4: Product and Process Validation

Standard deliverables and descriptions:

| ID | Deliverable | Description | Owner | Notes |
|---|---|---|---|---|
| P4-D01 | Production Trial Run (PRR) Report | Execution of production run at planned rates (volume, cycle time, operator count). Documents setup, process adjustments, yield, defects, rework, scrap, lessons learned. | Manufacturing Engineer | Production readiness evidence |
| P4-D02 | Measurement System Analysis (MSA) Executed | Gage R&R studies completed on all measuring devices (CMM, calipers, test fixtures, functional testers) for SC/CC. Results documented, gages accepted for production. | Quality Engineer | Measurement validity confirmation |
| P4-D03 | Preliminary Process Capability Study (PPC) Results | SPC data (minimum 100 parts, preferably 125+ per PPAP) collected during trial run. Cpk/Ppk calculated for each critical characteristic. Control limits established, histogram and SPC charts generated. | Quality Engineer | Quantitative capability proof |
| P4-D04 | Production Validation Testing | Comprehensive testing on trial run parts: dimensional (CMM, go/no-go), functional (bench/rig test), environmental (thermal, vibration, humidity), reliability (accelerated life test if applicable), chemical analysis (material cert). | Quality Engineer | Performance validation |
| P4-D05 | Production Part Approval Plan (PPAP) Submission | Per AIAG PPAP manual, customer approval level (1–5) determined. PPAP package assembled: First Article Inspection Report (FAIR), capability data, SPC charts, PFMEA, control plan, supplier declaration, customer approval sign-off. | Quality Engineer | Formal customer approval |
| P4-D06 | Production Control Plan (PCP) Final | Final ongoing control plan defining: characteristics monitored (SC/CC list), sampling frequency (100%, AQL-based, SPC charting), control methods (inline inspection, SPC, functional test), reaction plan for out-of-control conditions. | Quality Engineer | Production governance |
| P4-D07 | Production Run at Sustained Rate (@SOP Rate) | Extended production runs (minimum 2–4 weeks of calendar time) at planned volume demonstrating sustained capability, delivery schedule, quality consistency. | Manufacturing Engineer | Operational stability proof |
| P4-D08 | Quality Planning Sign-Off | Formal approval and sign-off from customer quality/engineering, supplier quality, and manufacturing. Confirms all PPAP and APQP requirements met. | Program Manager + Customer Quality | Program acceptance |
| P4-D09 | Gate 4 Review (Production Readiness) | Final gate review confirming production readiness and customer approval (decision: proceed to SOP and Phase 5). | Program Manager | Production launch authority |

**Gate 4 Exit Criteria:**
- Production Trial Run completed at planned rates with acceptable results
- MSA (Gage R&R) completed on all gaging, all gages accepted
- Preliminary Process Capability Study shows Cpk/Ppk ≥ 1.33 (or customer minimum, e.g., 1.67)
- SPC charts demonstrate process stability (no special cause variations)
- All SC/CC in statistical control
- Production Validation Testing complete, results acceptable
- PPAP submission accepted by customer
- Production Control Plan finalized and approved
- Customer quality sign-off obtained
- Sustained production @ rate demonstrated

## Phase 5: Feedback, Assessment, and Corrective Action

Standard deliverables and descriptions:

| ID | Deliverable | Description | Owner | Notes |
|---|---|---|---|---|
| P5-D01 | Variation Reduction Plan and Results | Documented continuous improvement initiatives: process optimization experiments, fixture/tool improvements, operator training, material standardization. Trend charts showing defect/variation reduction over time. | Manufacturing Engineer + Quality Engineer | Ongoing excellence |
| P5-D02 | Customer Satisfaction Monitoring | On-time delivery metrics, quality metrics (PPM, first-pass yield), customer complaint rate, feedback score. Comparison to target. Feedback from customer quality audits. | Supplier Quality + Program Manager | Voice of customer feedback |
| P5-D03 | Delivery and Service Performance | Delivery schedule adherence, lead time consistency, inventory management, expedite request handling, after-sales support (warranty claims, field returns, service bulletins). | Supply Chain + Supplier Quality | Supply chain excellence |
| P5-D04 | Lessons Learned Documentation | Project retrospective capturing: design decisions (what worked, what didn't), manufacturing process insights, testing and validation findings, team feedback, recommendations for future programs. | Program Manager | Organizational learning |
| P5-D05 | Effective Use of Corrective Actions | Documentation of all corrective actions taken in response to non-conformances, customer complaints, or process deviations. Root cause analysis (RCCA), preventive actions implemented, effectiveness verified. | Quality Engineer | Problem resolution discipline |
| P5-D06 | Gate 5 Review (Feedback and Optimization) | Final gate review summarizing Phase 5 performance metrics, lessons learned, and program close-out approval (decision: close program with improvement actions noted). | Program Manager | Program completion authority |

**Gate 5 Exit Criteria:**
- Production stable (no major non-conformances in past 90 days)
- Variation trending downward; process improvements documented
- Customer satisfaction metrics at or above target
- On-time delivery performance ≥ 98% (or customer target)
- All corrective actions completed and effective
- Lessons learned captured and shared with organization
- Customer satisfaction sign-off obtained
- Program closed or transitioned to steady-state supply
