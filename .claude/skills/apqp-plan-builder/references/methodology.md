# APQP Methodology Reference

## Overview

Advanced Product Quality Planning (APQP) is a structured framework defined by the Automotive Industry Action Group (AIAG) to ensure that a product or service meets customer expectations through systematic planning, design, process, validation, and feedback phases. APQP is mandatory for Tier-1 automotive suppliers seeking IATF 16949 certification and is required by most Original Equipment Manufacturers (OEMs) before shipping parts.

APQP is complementary to:
- **PPAP (Production Part Approval Process):** Demonstrates that the supplier can consistently produce parts that meet customer drawings and specifications during production trials and sustained production.
- **FMEA (Failure Mode and Effects Analysis):** Identifies and mitigates potential design (DFMEA) and process (PFMEA) failures.
- **MSA (Measurement System Analysis):** Validates that gaging systems are adequate for measuring special characteristics.
- **SPC (Statistical Process Control):** Ensures ongoing process stability and capability after production launch.

## The Five APQP Phases

### Phase 1: Plan and Define Program

**Goal:** Establish program scope, customer voice, business plan, and preliminary design/process roadmap.

**Key Activities:**
- Capture Voice of Customer (VOC) and define customer requirements
- Develop business case and cost targets
- Form cross-functional team
- Define preliminary BOM and manufacturing process flow
- Establish design and reliability goals
- Identify preliminary special characteristics (SC) and critical characteristics (CC)

**Key Deliverables:**
- Customer Requirements Review (CRR)
- Preliminary BOM and Process Flow
- Design Goals and Reliability Targets
- Preliminary SC/CC List
- Team Kickoff and Role Definition
- Gate 1 Review

**Exit Criteria (Gate 1):**
- VOC captured and documented
- Customer requirements and CSL clearly defined
- Team aligned on program schedule and deliverables
- Preliminary process approach feasible
- Business plan approved

### Phase 2: Product Design and Development

**Goal:** Complete product design and validate design adequacy through analysis and testing.

**Key Activities:**
- Perform Design FMEA (DFMEA) per AIAG-VDA
- Design for Assembly (DFA) and Design for Manufacturability (DFM) reviews
- Develop and execute Design Verification Plan and Report (DVP&R)
- Conduct Design Reviews (DR1, DR2, DR3 with prototypes)
- Finalize engineering drawings and specifications
- Cascade APQP requirements to suppliers

**Key Deliverables:**
- DFMEA (Design Failure Mode and Effects Analysis)
- DFA/DFM Report
- Design Verification Plan and Report (DVP&R)
- Design Review Reports (with prototype hardware/software)
- Final Engineering Drawings and Specifications
- Finalized SC/CC List
- Supplier APQP Inputs and Schedule
- Gate 2 Review

**Exit Criteria (Gate 2):**
- Design FMEA complete and risk-mitigated
- DVP&R plan approved, testing underway or complete
- Prototype build successful, preliminary performance meets targets
- Design reviews conclusive: design adequate to proceed to process design
- All SC/CC finalized per customer designation

### Phase 3: Process Design and Development

**Goal:** Design the manufacturing and assembly process, establish capability, and prepare for production trials.

**Key Activities:**
- Document complete process flow charts and work instructions
- Perform Process FMEA (PFMEA) per AIAG-VDA
- Establish Characteristics Matrix linking product characteristics to process variables
- Define packaging and shipping specifications
- Develop pre-launch control plan (reaction plan for non-conformances)
- Plan Measurement System Analysis (MSA/Gage R&R) for all SC/CC
- Develop preliminary process capability study plan

**Key Deliverables:**
- Process Flow Chart (with all operations and parameters)
- Process FMEA (Manufacturing/Assembly Failure Mode and Effects Analysis)
- Characteristics Matrix (Product-to-Process Traceability)
- Pre-Launch Control Plan (PLCP) with reaction plans
- Process Instructions and Work Instructions (SOP stubs)
- Packaging Specifications
- MSA Plan (defining measurement methods and adequacy)
- Preliminary Process Capability Study Plan
- Gate 3 Review

**Exit Criteria (Gate 3):**
- Process design complete and documented
- PFMEA complete and controls defined
- Process capability study plan and sampling strategy approved
- MSA plan finalized for all critical characteristics
- Pre-launch control plan ready for trial run execution
- Preliminary SPC charting strategy defined

### Phase 4: Product and Process Validation

**Goal:** Execute production trials, confirm process capability, obtain customer approval, and prepare for full-rate production.

**Key Activities:**
- Execute Production Trial Run (PRR) at production rates
- Conduct full Measurement System Analysis and Gage R&R on production gages
- Execute Preliminary Process Capability Study (PPC) — collect Cpk/Ppk data
- Perform comprehensive production validation testing (functional, environmental, reliability)
- Prepare and submit Production Part Approval Plan (PPAP) per AIAG PPAP manual and customer level
- Finalize Production Control Plan (PCP) — ongoing SPC, control limits, inspection frequency
- Demonstrate sustained production at planned rates
- Obtain customer and quality sign-off

**Key Deliverables:**
- Production Trial Run Report
- MSA/Gage R&R Results (all measuring devices)
- Preliminary Process Capability Study (PPC with SPC charts)
- Production Validation Test Report
- PPAP Submission Package (per customer level 1–5)
- Production Control Plan (PCP with SPC strategy and reaction plans)
- First Article Inspection Report (FAIR)
- Quality Planning Sign-Off
- Gate 4 Review

**Exit Criteria (Gate 4):**
- PRR completed at production rates, all results acceptable
- Cpk/Ppk ≥ 1.33 or customer minimum (e.g., 1.67 per IATF)
- Process capable and stable (SPC charts show control)
- PPAP submission accepted by customer (PPAP approval status)
- Production @ rate demonstrated — sustained production capability proven
- All SC/CC in control
- Quality planning sign-off obtained

### Phase 5: Feedback, Assessment, and Corrective Action

**Goal:** Monitor production performance, respond to customer feedback, and drive continuous improvement.

**Key Activities:**
- Monitor on-time delivery and quality performance metrics
- Track customer satisfaction and complaints
- Implement corrective actions for any non-conformances or deviations
- Drive variation reduction and process improvements
- Document lessons learned
- Assess effectiveness of control plans and adjust as needed

**Key Deliverables:**
- Variation Reduction Report
- Customer Satisfaction Metrics
- Delivery/Service Performance Summary
- Corrective Action Summary (RCCA, preventive actions taken)
- Lessons Learned Documentation
- Continuous Improvement Action Plan
- Gate 5 Review (close-out)

**Exit Criteria (Gate 5):**
- Program stable in production; no major non-conformances
- Variation trending downward
- Customer satisfaction metrics at target
- Delivery performance on schedule
- Lessons learned captured and shared
- APQP program closed with customer approval

## AIAG vs VDA FMEA

The AIAG and Verband der Automobilindustrie (VDA) have historically published separate FMEA methodologies, though alignment efforts have improved compatibility:

- **AIAG FMEA (5th Edition, 2019):** Emphasis on Risk Priority Number (RPN), failure effect severity, occurrence, detection.
- **VDA FMEA (Edition 1.1, 2019):** More process-oriented, emphasizes parameter relationships and system thinking.

Many Tier-1 suppliers now use **AIAG-VDA harmonized FMEA** (blended approach), which respects both methodologies. Check customer purchase orders or IATF 16949 clauses to confirm which method is required.

## Integration with PPAP and IATF 16949

**PPAP (Production Part Approval Process):**
- APQP Phase 4 culminates in PPAP submission.
- PPAP demonstrates that the supplier can consistently produce conforming parts.
- PPAP includes first article inspection, process capability data, and dimensional records.
- Customer specifies PPAP level (1–5, where 5 is most stringent).

**IATF 16949 (Automotive Quality Management System Standard):**
- APQP is a core requirement in IATF 16949 Section 8.2 (Planning).
- Suppliers must demonstrate APQP discipline for all new programs and design changes.
- Gate reviews (5 gates per APQP) align with IATF governance and management review checkpoints.
- MSA, SPC, and FMEA are integrated into IATF supplier process audits.

## When to Use APQP

**Always use APQP when:**
- Developing a new product or major design change for an OEM customer
- Seeking IATF 16949 certification or maintaining certification
- Contracting with Tier-1 automotive suppliers
- Responding to a customer Request for Proposal (RFP) that includes "APQP required"

**May use APQP (or tailored version) when:**
- Supplying to non-automotive industries with similar rigor expectations (e.g., medical devices, aerospace)
- Managing internal product development in manufacturing companies
- Integrating supplier quality across a supply chain

## Key Metrics and Definitions

- **Critical Characteristic (CC):** A characteristic that directly affects safety, regulatory compliance, or core customer requirement. Always tracked in PPAP and SPC.
- **Special Characteristic (SC):** A characteristic that affects fit, function, appearance, or performance. Tracked per customer designation (symbol on drawing).
- **Cpk (Capability Index):** Ratio of design tolerance to actual process spread; typically ≥ 1.33 for production readiness.
- **Ppk (Preliminary Capability Index):** Cpk during trial run (smaller sample, higher variability expected); typically ≥ 1.33 for production trial approval.
- **FMEA RPN (Risk Priority Number):** Severity × Occurrence × Detection; higher RPN = higher priority for control or design change.

## References

- AIAG APQP Manual, 2nd Edition
- AIAG PPAP Manual, 4th Edition
- AIAG FMEA Manual, 5th Edition (AIAG-VDA Harmonized)
- IATF 16949:2016 Automotive Quality Management System Standard
- AIAG DFMEA Handbook
- AIAG PFMEA Handbook
