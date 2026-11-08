# PPAP Element Requirements (AIAG 4th Edition)

Detailed requirements per each of the 18 PPAP elements, including typical format, OEM expectations, and pass/fail criteria.

## Element 1: Design Records

**Purpose:** Establish traceability to the authorized engineering design.

**Required Content:**
- Complete set of engineering drawings with all dimensions, tolerances, notes, and material specifications
- All drawing revisions and change history (drawing revision level and effective date)
- Designer and checker signatures
- Customer approval signature (if required by contract)
- Bill of materials (BOM) with part numbers, revisions, and supplier identification
- Specifications for purchased parts and materials
- Interface/assembly drawings showing how the part integrates with mating components

**Format:** PDF or hardcopy drawings; digital CAD files optional but recommended

**Acceptance Criteria:**
- All current drawings must be at the revision level used for production
- No open hold/engineering notes
- All referenced specifications and standards (e.g., IEC, ISO, customer-specific) must be listed
- BOM must match the drawing change level

**Common Issues:**
- Drawing revisions not synchronized with production tooling
- Missing customer approval signature on customer-specific features
- Specifications referenced but not provided

---

## Element 2: Authorized Engineering Change Documents

**Purpose:** Document all design and process changes and demonstrate customer notification/approval.

**Required Content:**
- Engineering Change Notice (ECN) or Engineering Change Order (ECO) for every change to design, material, manufacturing process, or sourcing
- Date of change authorization
- Description of change and technical justification
- List of all affected drawings/documents
- Effective date of change (when supplier must begin using new design/process)
- Evidence of customer notification (email, letter, meeting minutes)
- For customer-initiated changes: customer's ECN/PCN number and signature
- Impact assessment (design, cost, schedule, risk)

**Format:** ECN/ECO log spreadsheet or summary document per internal procedures; original ECN documents

**Acceptance Criteria:**
- All changes since last PPAP approval must be documented
- Each ECN must show customer notification before effective date
- Supplier has evidence of implementing change by effective date
- No unauthorized or undocumented process changes

**Common Issues:**
- Process changes made without formal ECN (not traceable)
- Customer notification via email only (hard to prove); meeting minute preferred
- Change effective date before customer approval

---

## Element 3: Engineering Approval

**Purpose:** Confirm that the customer has formally approved the design for production.

**Required Content:**
- Signed approval letter from customer engineering authority (not just purchasing)
- Approval date and approver name/title
- Approval scope (drawing numbers, revision levels covered)
- Customer document reference number
- If approval is conditional: open items list and closure evidence

**Format:** Email, letter, or meeting minutes with printed signature; scanned copy acceptable

**Acceptance Criteria:**
- Approval is from customer engineering, not purchasing
- Approval date is recent (recent = within 12 months for unchanged designs; within 3 months if PPAP submission is after long gap)
- Approval covers the exact drawing revisions used for production samples
- No open conditions or escalation requests

**Required If:**
- Contract or customer specification requires engineering approval
- Design includes customer-proprietary or customer-specified components
- Part is critical to vehicle safety or performance
- First PPAP submission or design change PPAP

**Typical OEM Position:** "Design approved by Phoenix Motors Engineering on 2026-03-15; covers drawing revisions A through B; open item: material RoHS cert closure by 2026-05-01"

---

## Element 4: Design FMEA

**Purpose:** Demonstrate that design risks have been systematically identified and controlled.

**Required Content:**
- FMEA worksheet with columns: Function, Failure Mode, Effects, Cause, Current Control, Severity, Occurrence, Detection, Risk Priority Number (RPN), Recommended Action, Responsibility, Target Completion
- For each high-risk failure mode (Severity >= 8 or RPN > 100): design control strategy (design review, analysis, prototype test, redundancy, derating)
- Evidence of design control closure (test reports, design review meeting notes, simulation results)
- Design FMEA revision number and date
- FMEA leader/owner name

**Format:** Excel spreadsheet with embedded formulas for RPN calculation; embedded test report references or links to supporting documents

**Acceptance Criteria:**
- All functional requirements must have at least one failure mode documented
- No high-severity failure modes (S >= 8) without design control
- No open RPN > 150 items (or per customer-defined threshold)
- Design FMEA is at the same revision as production design
- Design change PPAP: FMEA must show review/update of affected failure modes

**Common Issues:**
- FMEA severity/occurrence/detection ratings not justified (no supporting data)
- High-RPN items with only "customer complaint monitoring" as control (not sufficient for design)
- FMEA not updated when design changes

**OEM Expectation:** "Design FMEA Rev 2.0 (2026-03-01) identifies 12 failure modes; 3 high-RPN items controlled via design review and derating; closure evidence provided in test reports TR-001, TR-002"

---

## Element 5: Process Flow Diagrams

**Purpose:** Establish the manufacturing and assembly sequence and identify key process steps.

**Required Content:**
- Diagram or table showing the sequence of all manufacturing, assembly, test, and packaging steps
- For each major step: equipment type, operator skill level (e.g., "Technician per SOP-123"), process parameters (if critical)
- Identification of inspection and test points (visual, dimensional, electrical)
- Process hold/release points (e.g., "Hold for visual inspection before reflow")
- Material flow and part traceability mechanism

**Format:** Flow chart (Visio, Draw.io) or detailed process step table; can reference manufacturing work instructions (SOPs)

**Acceptance Criteria:**
- Process flow matches production floor reality (not theoretical)
- All test/inspection points are identified
- Critical parameters are called out (e.g., reflow temperature profile, placement accuracy tolerance)
- Material traceability mechanism is described (lot tracking, serial number assignment)
- Documented handling requirements (ESD protection, temperature control, cleanliness)

**Common Issues:**
- Flow diagram shows ideal process but production reality is different
- Test points listed but acceptance criteria not defined (covered in Control Plan element)
- Material handling and ESD controls not mentioned

---

## Element 6: Process FMEA

**Purpose:** Demonstrate that process risks have been systematically identified and controlled.

**Required Content:**
- FMEA worksheet: Process Step, Failure Mode, Effect, Cause, Current Control, Detection Method, Severity, Occurrence, Detection, RPN, Recommended Action, Owner
- For each process step: identification of potential failure modes and their effects on product quality
- For high-RPN items: process control strategy (100% inspection, SPC, fixture validation, statistical proof of control, machine capability study)
- Evidence of process control closure (machine capability studies, SPC charts, first-piece inspection results, operator qualification records)
- Process FMEA revision and date; must align with process flow diagram revision

**Format:** Excel spreadsheet with process step reference and embedded control evidence

**Acceptance Criteria:**
- All manufacturing and assembly steps covered
- No high-RPN items (RPN > 100) without process control
- Process controls are verified (e.g., SPC data, Cpk > 1.67 for critical steps)
- FMEA is dated after process design is complete
- For design change PPAP: FMEA must address impact of change on all downstream process steps

**Common Issues:**
- FMEA written for theoretical process, not validated with actual data
- Process controls documented in FMEA but not proven to work in production (no SPC data, no Cpk)
- Discrepancy between PFMEA and actual control plan (e.g., PFMEA says 100% inspection but control plan says AQL sampling)

**OEM Expectation:** "Process FMEA Rev 1.0 (2026-02-15) identifies 18 process steps; 7 high-RPN items controlled via 100% ICT testing and visual inspection; machine capability data attached for placement accuracy, solder joint count; SPC charts show process stable over 500-part run"

---

## Element 7: Control Plan

**Purpose:** Specify the ongoing production control strategy for every monitored characteristic.

**Required Content:**
- One row per controlled characteristic (design parameter, process parameter, or output parameter)
- Columns: Characteristic, Specification/Tolerance, Type of Inspection (100%, AQL sampling, variable, attribute), Gage/Equipment, Acceptance Criteria, Frequency, Reaction Plan, Responsibility
- For special characteristics or customer requirements: enhanced monitoring (e.g., 100% inspection, SPC with control limits)
- Documented reaction plan for out-of-spec condition (stop production, rework criteria, customer notification)
- Control plan revision number, date, and approval (production engineer, quality manager)

**Format:** Excel spreadsheet organized by process flow step or characteristic type

**Acceptance Criteria:**
- All critical characteristics have monitoring defined
- Sampling plan (if used) is per ANSI/ASQ Z1.4 or customer-defined AQL
- Acceptance criteria match design specifications
- Reaction plan is specific (not vague): "Stop production and investigate" is good; "Contact supervisor" is not sufficient
- No gap between characteristics controlled in PFMEA and characteristics in Control Plan (must align)

**Common Issues:**
- Control plan has characteristics from PFMEA but doesn't specify frequency or acceptance criteria
- Sampling plan is non-standard (e.g., "inspect every 10th part" instead of standard AQL 0.65)
- Reaction plan is reactive only (no SPC or preemptive control)
- Outdated control plan not updated after process changes

**OEM Expectation:** "Control Plan Rev 1.0 specifies 12 monitored characteristics: PCB placement accuracy (100% vision inspection, accept ±0.5mm, frequency every part), solder joint count (100% X-ray, accept 95-105%, frequency every hour), ICT result (100%, pass/fail, frequency every part). Reaction plan: placement out-of-spec → adjust fixture and rerun 10-part verification; solder out-of-spec → investigate reflow profile and recalibrate"

---

## Element 8: Measurement System Analysis (MSA)

**Purpose:** Demonstrate that all measurement systems (gages, fixtures, software) are fit for purpose and not contributing to false accept/reject decisions.

**Required Content:**
- Gage R&R study for each critical gage/measurement system
- MSA format (short form or full ANOVA method acceptable; ANOVA preferred for larger studies)
- For each gage: 
  - Part number, gage ID, measurement characteristic
  - Reproducibility (variation due to operator/setup)
  - Repeatability (variation due to gage repeatability)
  - % Tolerance (%R&R: ratio of R&R variation to tolerance width)
  - Bias (systematic offset from reference)
  - Linearity (accuracy across range of measurement)
  - Stability over time (short-term and long-term)
- For each gage: acceptance criterion (typically %R&R < 10% = Acceptable; 10%-30% = Conditional; > 30% = Not Acceptable)

**Format:** Excel spreadsheet with data, formulas, and control charts; embedded test reports

**Acceptance Criteria:**
- All gages used for acceptance inspection must have MSA study completed
- %R&R < 10% for all critical characteristics
- If %R&R 10%-30%: documented justification (e.g., "No better gage available; customer aware") AND enhanced reaction plan (more frequent recalibration, backup measurement method)
- No gage with %R&R > 30% (not fit for purpose; must replace or retire)
- MSA data must be recent (within 12 months of PPAP submission for unchanged process; immediately after gage change)

**Common Issues:**
- MSA study performed on gage but results not linked to actual parts measured in production
- Bias or linearity study not performed; only R&R reported
- High %R&R (> 20%) rationalized away without compensating controls
- Gage replaced or modified after MSA but study not repeated

**OEM Expectation:** "MSA completed 2026-03-10 for 3 critical gages (placement, solder, thickness). Results: Gage-001 %R&R 8.5% (Acceptable), Gage-002 %R&R 6.3% (Acceptable), Gage-003 %R&R 7.1% (Acceptable). All gages bias and linearity OK. Gage recalibration per ISO 17025 every 6 months."

---

## Element 9: Dimensional Results

**Purpose:** Demonstrate that the design intent is achievable via production and that first production parts meet specification.

**Required Content:**
- First-piece dimensional inspection report (FPIR) for every dimension and tolerance on the drawing
- For each characteristic: nominal specification, tolerance (e.g., ±0.5 mm), measured value from first production sample, in/out of spec status
- Sample size (typically minimum 5-10 parts for low-precision parts; minimum 25-30 for high-precision parts)
- Date of inspection and inspector ID
- Evidence of measurement (CMM reports, calipers, gages with calibration status)
- For out-of-spec dimensions: root cause analysis and corrective action (rework, tool adjustment, design change)

**Format:** CMM report, spreadsheet, or FPIR form with scan of data; PDF acceptable

**Acceptance Criteria:**
- All dimensions on drawing are measured (no skipped dimensions)
- All measured values are within tolerance (if out-of-spec: documented corrective action and rework/rework-test evidence)
- Sample size is adequate (typically 25+ parts for first PPAP; smaller sample only if justified by high-capability process)
- Measurement system accuracy is adequate (gage must be at least 10:1 accuracy ratio compared to tolerance)
- For design change PPAP: dimensions affected by change must be re-measured (not reuse old FPIR data)

**Common Issues:**
- FPIR missing some dimensions (example: "measured length, width, height but not all positional tolerances")
- Out-of-spec dimension reported but no root cause or corrective action
- FPIR from old production lot reused for PPAP submission (must be current)
- Measurement uncertainty not documented (customer cannot verify measurement system was adequate)

**OEM Expectation:** "First-piece dimensional inspection completed 2026-03-20 on 25 production parts. All 28 dimensions per drawing DWG-2024-001 measured via calibrated CMM. Results: 27 dimensions within tolerance; 1 dimension (Boss height, spec 10.0 ±0.5 mm) average measured 10.1 mm — within tolerance. No rework required. CMM calibration current (good through 2026-10-30)."

---

## Element 10: Records of Material and Performance Test Results

**Purpose:** Demonstrate that the material and design perform per specification and regulatory requirements (RoHS, environmental, EMC, reliability).

**Required Content:**
- **Material Certifications:**
  - RoHS Certificate (EU 2011/65/EU for lead-free, hazardous substances): supplier name, lot number, test date, passing result
  - IMDS (International Material Data System) submission ID and submission date (typically due within 30 days of PPAP submission)
  - REACH compliance documentation (if applicable: hazardous substance assessment)
  - Supplier material data sheet and certificates of conformance
  
- **Environmental Performance Testing:**
  - Thermal cycling test (IEC 60068-2-14, e.g., -10°C to +85°C, 500 cycles)
  - Thermal shock test (if applicable to part design)
  - Vibration endurance test (MIL-STD-810 or customer-specified spec)
  - Humidity test (if applicable: salt spray, moisture resistance)
  
- **Electrical Performance Testing (if applicable):**
  - EMC testing (FCC, CE mark, CISPR, per application)
  - Leakage/safety testing
  - Signal integrity testing (if high-speed interface)
  
- **Reliability Testing (if applicable):**
  - Accelerated life testing (HALT, HASS)
  - Failure rate testing (MTBF demonstration per MIL-HDBK-217 or Telcordia)

**Format:** Test reports from qualified third-party labs (with A2LA or ISO 17025 accreditation); embedded into PPAP package with pass/fail summary

**Acceptance Criteria:**
- All required certifications present and dated (no "pending" items)
- All test results pass per applicable standard
- RoHS certificate is current (not expired; supplier is responsible for recertification)
- IMDS submission ID is provided (even if marked "Pending" at PPAP submission, supplier must commit to submission within 30 days)
- Testing performed at qualified labs with accreditation per Element 12
- Material lot must match production lot (no substitution)

**Common Issues:**
- RoHS certificate from supplier but not verified independent test (customer may require third-party confirmation)
- IMDS submission not done; supplier promises to do "later" (typical cause of PPAP rejection)
- Environmental or EMC testing not required per specification but performed anyway with mediocre results (can trigger customer concern)
- Test report shows "Fail" on secondary characteristic but supplier rationalized as "not critical" (customer gets final say)

**OEM Expectation:** "RoHS certificate provided (Supplier Cert 2026-001, lot XYZ-12345, pass). IMDS submission ID TBD-2026-0015 (submission due by 2026-05-15). Thermal cycling test passed (IEC 60068-2-14, 500 cycles, -10/+85°C, no functional failure). Vibration test passed (MIL-STD-810H, 10-500 Hz, 7.5 G, 4 hours per axis)."

---

## Element 11: Initial Process Studies

**Purpose:** Demonstrate that the manufacturing process can produce parts that consistently meet specification (process capability = Cpk >= 1.67 for critical characteristics).

**Required Content:**
- Process capability study (Pp and Ppk) or process performance study (Cp and Cpk) for every monitored characteristic
- Minimum sample size:
  - For variable data (continuous measurement): minimum 100 parts (50 minimum if justified; 125+ preferred)
  - Data collection over production run of at least 3-5 days (continuous production to include setup/drift variation)
- For each characteristic: histogram, control limits, calculated Cpk/Ppk with formula shown
- If Cpk < 1.67: documented root cause analysis and corrective action (e.g., "Adjusted fixture offset; re-ran study with revised data showing Cpk 1.85")
- Acceptance criteria: Cpk >= 1.67 for critical/special characteristics; Cpk >= 1.33 acceptable for non-critical

**Format:** Excel spreadsheet with embedded control charts; statistical software output acceptable (Minitab, JMP, etc.)

**Acceptance Criteria:**
- Study must be performed with production equipment, tooling, and operators (not prototype equipment)
- Sample size >= 100 parts (or justified smaller sample)
- Data collection period >= 3 days of continuous or representative production
- No missing data or excluded outliers without documented justification
- For short-run or low-volume parts: capability study acceptable using simulation if actual production run not feasible
- Design change PPAP: re-study characteristics affected by design change; use old capability data for unaffected characteristics if data < 1 year old

**Common Issues:**
- Study run on setup alone (not including drift over time): artificially high Cpk
- Sample size too small (30-50 parts): inadequate for reliable capability assessment
- Long gap between capability study and PPAP submission (> 1 year): capability data may be stale if process drift suspected
- Cpk < 1.67 reported; no compensating control plan or root cause action

**OEM Expectation:** "Initial process studies completed 2026-03-01 for 4 critical characteristics using production equipment. Data collected over 5-day run (500 parts); sample size 125 per characteristic. Results: Placement accuracy Cpk 1.85; solder joint Cpk 2.10; ICT yield Cpk 1.95; thickness Cpk 1.72. All >= customer minimum of 1.67. SPC charts attached; process stable with no trends."

---

## Element 12: Qualified Laboratory Documentation

**Purpose:** Ensure all testing performed under Element 10 was conducted at qualified, accredited laboratories with defined scope.

**Required Content:**
- List of all testing labs used with the following information for each:
  - Lab name and location
  - Accreditation body (A2LA, ILAC, IATF, ISO 17025, etc.)
  - Accreditation certificate number
  - Scope of accreditation (specific test methods or equipment covered)
  - Accreditation expiry date
  - Calibration status of critical test equipment

**Format:** Lab qualification list spreadsheet or summary document with embedded copies of accreditation certificates

**Acceptance Criteria:**
- Every lab used must have current accreditation (not expired)
- Scope of accreditation must cover the specific tests performed (example: "A2LA accredited for thermal cycling per IEC 60068-2-14" with scope number)
- For material composition testing: labs must be A2LA or ISO 17025 accredited for materials testing
- For RoHS/REACH: supplier must provide lab accreditation or third-party verification (not in-house testing only)

**Common Issues:**
- Lab accreditation cited in test report but certificate not provided with PPAP
- Accreditation scope does not cover the specific test method used (e.g., lab is accredited for "Thermal cycling" but not for the specific temperature range or cycle used)
- Supplier performed in-house testing for materials/chemistry without third-party verification (typically not acceptable for RoHS/REACH)
- Lab accreditation is expired but used to support current PPAP submission

---

## Element 13: Appearance Approval Report (AAR)

**Purpose:** If the part has appearance, color, gloss, finish, or surface-quality requirements, document that the customer has approved the appearance of first production samples.

**Required Content:**
- Appearance Approval Report form (customer-provided template or standard IPC-A-610 Visual Standard)
- Inspection of first production parts against appearance standard (color match, gloss level, surface texture, scratches, contamination)
- Signature/approval from customer quality or engineering authority
- Approval date
- If part fails appearance: documented rework and re-approval

**Format:** Signed letter, email approval, or completed AAR form

**Acceptance Criteria:**
- AAR is required only if the drawing or specification includes appearance requirements
- Approval must be from customer (not supplier's opinion)
- Approval must be recent (within 1-3 months of PPAP submission)
- If appearance rejection occurred: documented rework and second AAR approval must be provided

**Common Issues:**
- Appearance requirement on drawing but no AAR provided (critical gap)
- AAR performed but not approved by customer (in-house sample comparison)
- AAR approved but then production process changed (change triggers re-approval requirement)

**OEM Expectation (if appearance is critical):** "Appearance Approval Report signed by Phoenix Motors Quality Lead on 2026-03-15, approving black anodized finish per IPC-A-610 standard. First production samples match approved color and gloss standard. No rework required."

---

## Element 14: Sample Production Parts

**Purpose:** Provide the customer with physical production samples for evaluation, testing, and retention.

**Required Content:**
- Physical sample parts produced from production tooling and process
- Minimum quantity: typically 25 units (some customers may require 50+ for safety-critical parts)
- Serial number or part ID on each sample (traceability)
- Shipment evidence: date shipped, shipping carrier, tracking number, receipt confirmation
- Identification of who will retain samples at customer (Quality Lab, Design Engineering, etc.)

**Format:** Shipping documentation, packing list, signed receipt from customer

**Acceptance Criteria:**
- Samples must be from actual production run (not special build, prototype, or hand-assembled)
- Samples must have the same serial numbering/traceability as production
- Samples must be shipped at appropriate temperature/humidity (no damage in transit)
- Customer must sign receipt (proof of delivery)
- Samples retained by customer for minimum of 1-2 years or per customer requirement

**Common Issues:**
- Samples hand-assembled or built specially for PPAP (not representative of production)
- Samples shipped but no proof of receipt
- Insufficient quantity (customer wants 50 but supplier ships 25)
- Samples damaged in shipment

---

## Element 15: Master Sample

**Purpose:** Supplier retains a reference standard part for all future production comparisons.

**Required Content:**
- One production part identified as "Master Sample"
- Unique ID (e.g., "MASTER-2026-ESC-001")
- Location: stored in secure location at supplier quality lab or equivalent (locked cabinet, climate-controlled)
- Retention period: until part design is superseded or per customer requirement (typically 3+ years)
- Condition checks: documented periodic visual inspection (monthly or quarterly) to ensure no deterioration
- Access control: list of authorized personnel who may handle master sample

**Format:** Master sample ID label on part; storage location and retention log document

**Acceptance Criteria:**
- Master sample must be clearly marked and stored separate from production inventory
- Location must be climate-controlled and protected from contamination
- Periodic condition checks documented (no rust, corrosion, or physical damage)
- Retention period extends for life of part design or per customer agreement

**Common Issues:**
- Master sample not segregated from production (risk of use in shipment)
- Storage location inadequate (exposed to temperature/humidity variations)
- No documented condition checks
- Supplier unsure how long to retain (check customer requirement)

---

## Element 16: Checking Aids

**Purpose:** Document any custom gages, fixtures, or inspection equipment unique to the part.

**Required Content:**
- For each custom gage/fixture:
  - Gage ID (e.g., "FIX-PLACEMENT-001")
  - Description and function
  - Part number and revision (if applicable)
  - Drawing or CAD model reference
  - Acceptance criteria or tolerance range
  - Calibration certificate and schedule (next calibration due date)
  - Status (in-use, spare, retired)

**Format:** Gage tracking spreadsheet or log with embedded calibration certificates

**Acceptance Criteria:**
- All custom gages documented with clear identification and drawing
- Calibration status current (not overdue)
- Calibration records traceable (ISO 17025 if required; in-house calibration acceptable if documented procedure followed)
- For high-precision gages: NIST traceability or third-party calibration preferred

**Common Issues:**
- Custom fixtures documented but calibration status unknown
- Gage ID not marked on actual fixture (confusion about which gage is which)
- Calibration overdue or missing
- Replacement/retirement of gage not coordinated with quality planning

---

## Element 17: Customer-Specific Requirements

**Purpose:** Document and evidence any supplemental PPAP requirements imposed by the specific OEM beyond AIAG baseline.

**Required Content:**
- List of all customer-specific requirements (e.g., Phoenix Motors PPAP Supplement v2.1)
- For each requirement: ID, requirement text, evidence/reference, completion status
- Examples of typical customer-specific requirements:
  - "Submit IMDS within 30 days of PPAP approval"
  - "Supply RoHS certificate from third-party lab (not supplier certification)"
  - "Provide on-site audit access within 60 days"
  - "Maintain Process Capability Cpk >= 1.67 throughout production"
  - "SPC charts submitted monthly for first 6 months of production"
  - "Configuration control: any component substitution requires ECN and supplier approval"

**Format:** Checklist or tracking spreadsheet with evidence column

**Acceptance Criteria:**
- All customer-specific requirements identified and evidenced
- No open or "pending" items at time of PPAP submission (unless customer pre-approved timeline)
- Supplier clear on long-term ongoing commitments (e.g., "monthly SPC submission for 6 months" must start after approval)

**Common Issues:**
- Customer requirements not identified or documented
- Requirements identified but evidence missing ("we'll submit later")
- PPAP approved but supplier unaware of ongoing requirements (monthly SPC, periodic audits, etc.)

---

## Element 18: Part Submission Warrant (PSW)

**Purpose:** Formal supplier authorization that all data is accurate and PPAP submission is complete.

**Required Content:**
- Part identification: name, number, supplier code, customer code, model year (if applicable)
- Current drawing revision and date
- Engineering change history (if applicable): list all ECNs since last approval with effective dates
- Weight or mass of part
- Reason for submission (initial production, design change, process change, supplier change, etc.)
- Submission level (1-5) with brief explanation if non-standard (e.g., "Level 2 per customer agreement")
- Submission results matrix: for each of 18 elements, mark as Submitted/Retained/N/A per level
- Supplier declaration: statement affirming that all data is accurate, complete, and represents production intent
- Authorized signature block:
  - Organization name
  - Signatory name and title (must be supervisor-level or above; quality manager, engineering manager, or plant manager typical)
  - Email and phone
  - Signature and date
  - Do not use stamped signature; handwritten preferred for formal submission

**Format:** Structured form (AIAG template or customer-specific PSW form); spreadsheet or PDF acceptable

**Acceptance Criteria:**
- PSW must be physically signed (handwritten signature or, if digital, recognized e-signature)
- Signatory must be authorized representative (not operator, not technician)
- All fields filled (no blanks)
- Submission level is justified per AIAG or customer requirement
- Submission results matrix matches actual package content (no claiming "Submitted" for elements that are actually retained)

**Common Issues:**
- PSW signed by non-authorized person (e.g., quality technician vs. quality manager)
- Stamped or printed signature (not acceptable; original handwritten required)
- PSW submitted without supporting documentation (elements marked "Submitted" but not actually included)
- PSW submission results matrix does not match actual content (claim Submitted but didn't send the data)

---

## Summary: What Makes a Strong PPAP Submission

1. **Completeness:** All 18 elements present and accurate per submission level
2. **Traceability:** Cross-references between elements (DFMEA → PFMEA → Control Plan → MSA → Process Studies)
3. **Data Integrity:** All measurements, tests, and capability studies support the part specification
4. **Customer Alignment:** Submission level, format, and content match customer expectations
5. **Contemporaneity:** Data is current (< 1 year for capability studies; < 3 months for dimensional/MSA if unchanged process)
6. **Authorization:** PSW signed by authorized supplier representative
7. **Evidence:** Copies of all referenced documents (certificates, test reports, CMM reports) embedded or available for review

A weak submission will have missing elements, outdated data, or unresolved open items — typically resulting in customer rejection ("PPAP Denied — resubmit when complete") or conditional approval ("PPAP Conditional — address 5 open items within 30 days").
