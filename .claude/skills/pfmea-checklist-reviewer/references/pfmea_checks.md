# PFMEA Checklist — Detailed Check Reference

## Confirmation Review (CR) — 14 Generic Doc-Quality Checks

Per AIAG-VDA Handbook Section 4 (Document Management & Configuration Control).

### CR-01: Document Structured
- **Requirement**: Document is organized into logically distinct sections (tabs).
- **Obligation**: Shall
- **How Verified**: Count sheet names. FC if >= 10 tabs; PC if 6-9.
- **Confidence**: High
- **Common Finding**: AIAG-VDA template typically has 12+ tabs (Title, Document Control, Header Block, Process Flow, Functions, PFMEA, Special Characteristics, Action Plan Tracker, Summary, Linkage to Control Plan, Lessons Learned, References).

### CR-02: Template Used
- **Requirement**: AIAG-VDA Handbook 2019 or equivalent PFMEA template used.
- **Obligation**: Should
- **How Verified**: Cannot be verified programmatically. Reviewer confirms template version by inspecting workbook.
- **Confidence**: Low (requires reviewer judgment)
- **Recommended Action**: If not using AIAG-VDA template, confirm equivalent methodology is applied.

### CR-03: Document Searchable
- **Requirement**: Document includes TOC and References for easy navigation.
- **Obligation**: Should
- **How Verified**: Check for "Title"/"Content" tab near beginning and "References" tab present.
- **Confidence**: High
- **Common Finding**: Small PFMEAs sometimes omit TOC; acceptable if only a few tabs.

### CR-04a: Title and Scope
- **Requirement**: Process title and scope clearly documented.
- **Obligation**: Shall
- **How Verified**: Title page has "Process Title" or "Process Name" field populated.
- **Confidence**: High
- **Common Finding**: FC if process name is clear; PC if title is generic ("Welding") without context.

### CR-04b: Author and Approver
- **Requirement**: Document author and approver (or responsible person) identified.
- **Obligation**: Shall
- **How Verified**: Title page has "Author" and "Approver" fields with names.
- **Confidence**: High
- **Common Finding**: NO if either is missing; affects traceability and accountability.

### CR-04c: Unique Revision ID
- **Requirement**: Current revision has a unique identifier.
- **Obligation**: Shall
- **How Verified**: Title page has "Revision" field (e.g., "Rev. A", "Rev. 1.2").
- **Confidence**: High
- **Common Finding**: Critical for configuration management; NO if missing.

### CR-04d: Change History
- **Requirement**: Document control tab logs revision history and changes.
- **Obligation**: Should
- **How Verified**: Sheet "01_Document_Control" present with date, revision, author, change summary.
- **Confidence**: High
- **Common Finding**: PC if missing; small internal documents sometimes forgo formal change log.

### CR-04e: Status
- **Requirement**: Document status (Draft/Review/Released) clearly marked.
- **Obligation**: Shall
- **How Verified**: Title page has "Status" field.
- **Confidence**: High
- **Common Finding**: Critical for release management; NO if missing.

### CR-05: Current Revision Identifiable
- **Requirement**: Current revision is unambiguous (related to CR-04c).
- **Obligation**: Shall
- **How Verified**: Revision ID is visible and consistent (e.g., in header, title page, document control tab).
- **Confidence**: High
- **Common Finding**: Ensures no confusion between versions in email/sharepoint circulation.

### CR-06: Configuration Management
- **Requirement**: Document is under configuration management (CM) system (Git, Sharepoint, Polarion, etc.).
- **Obligation**: Should
- **How Verified**: Cannot be verified from xlsx. Reviewer confirms CM system is in place.
- **Confidence**: Low
- **Recommended Action**: Organizational practice; confirm PFMEA is stored in CM and version history is tracked.

### CR-07: Headers/Footers
- **Requirement**: Page headers/footers display document ID, revision, date, and page number.
- **Obligation**: Should
- **How Verified**: Cannot be verified programmatically (property of Excel print settings). Reviewer manually checks.
- **Confidence**: Low
- **Recommended Action**: Review in Print Preview to ensure headers/footers reflect current revision.

### CR-08: Table of Contents
- **Requirement**: Dedicated TOC tab or outline for easy navigation.
- **Obligation**: Should
- **How Verified**: Check for "Title" or "Content" tab in first 3 sheets.
- **Confidence**: Medium
- **Common Finding**: Optional for small documents; expected for formal manufacturing PFMEAs.

### CR-09: References
- **Requirement**: References tab cites key standards and sources.
- **Obligation**: Should
- **How Verified**: Check for "References" or "Bibliography" tab.
- **Confidence**: High
- **Common Finding**: Should cite AIAG-VDA Handbook, Control Plan standard, and any cross-referenced DFMEA.

### CR-14: All Sections Complete
- **Requirement**: All core PFMEA tabs are populated (Title, Header Block, Process Flow, PFMEA, Action Plan, Control Plan Linkage).
- **Obligation**: Shall
- **How Verified**: Check presence of "00_Title_Page", "02_Header_Block", "05_PFMEA_Worksheet".
- **Confidence**: High
- **Common Finding**: FC if all core tabs present; PC if some tabs are skipped or empty.

---

## PFMEA Assessment (PFMEAA) — 14 AIAG-VDA 2019 Specific Checks

Per AIAG-VDA Handbook Section 5 (Process FMEA).

### PFMEA-01: Header Block Complete
- **Requirement**: Header block contains part number, part name, process name, and date prepared.
- **Obligation**: Shall
- **How Verified**: Tab "02_Header_Block" has fields populated (or inline on Title page).
- **Confidence**: High
- **Common Finding**: FC if all 4 fields present; PC if 2-3 present; NO if missing entirely.
- **Rationale**: Header block ties PFMEA to BOM and manufacturing schedule.

### PFMEA-02: Process Flow Chart
- **Requirement**: Process flow chart documents all significant manufacturing steps with type, equipment, and process characteristics.
- **Obligation**: Shall
- **How Verified**: Tab "03_Process_Flow" has rows for each step with ID, Type (e.g., Assembly, Welding), Equipment (e.g., spot welder), Characteristics.
- **Confidence**: High
- **Common Finding**: FC if all steps have equipment identified; PC if equipment missing for some steps; NO if flow is empty.
- **Rationale**: Process flow is the backbone of PFMEA; every failure mode is tied to a step.

### PFMEA-03: Process Functions
- **Requirement**: Process functions are identified for each manufacturing step.
- **Obligation**: Shall
- **How Verified**: Tab "04_Process_Function_Analysis" lists functions per step (e.g., Step 1: "Position part", "Clamp", "Weld").
- **Confidence**: High
- **Common Finding**: FC if 1+ functions per major step; PC if sparse; NA if simple single-operation process.
- **Rationale**: Functions drive the failure modes; missed function = missed failure mode.

### PFMEA-04: PFMEA Worksheet Complete
- **Requirement**: PFMEA worksheet rows are populated for all failure modes with FM, FE, and cause documented.
- **Obligation**: Shall
- **How Verified**: Tab "05_PFMEA_Worksheet" has rows with Failure Mode, Failure Effect, and Failure Cause (minimum).
- **Confidence**: High
- **Common Finding**: FC if all mandatory fields populated; PC if 70-90% complete; NO if worksheet is empty or sparse.
- **Rationale**: Completeness of FM/FE/Cause drives quality of action plan.

### PFMEA-05: S/O/D Ratings (1-10)
- **Requirement**: Severity, Occurrence, and Detection are rated on a scale of 1-10 for every failure mode.
- **Obligation**: Shall
- **How Verified**: Tab "05_PFMEA_Worksheet" has Severity, Occurrence, Detection columns with values 1-10.
- **Confidence**: High
- **Common Finding**: NO if any S/O/D is missing or out-of-range (< 1 or > 10); PC if some missing.
- **Rationale**: S/O/D ratings drive Action Priority (S*O*D); missing ratings = no priority guidance.

### PFMEA-06: Action Priority Computed
- **Requirement**: Action Priority (AP) is computed as S*O*D for every failure mode.
- **Obligation**: Shall
- **How Verified**: Tab "05_PFMEA_Worksheet" has AP column with values > 0 for all rows with S/O/D.
- **Confidence**: High
- **Common Finding**: FC if AP computed for all rows; PC if computed for most; NO if AP column is empty.
- **Rationale**: AP determines which items require action plan closure.

### PFMEA-07: High-AP Items Have Actions
- **Requirement**: All failure modes with AP >= 100 have a recommended corrective action.
- **Obligation**: Shall
- **How Verified**: Tab "05_PFMEA_Worksheet", filter AP >= 100, verify "Recommended Action" column is not empty.
- **Confidence**: High
- **Common Finding**: FC if all high-AP items have actions; NO if any high-AP item lacks action.
- **Rationale**: High-AP items are the critical risk; must be addressed.

### PFMEA-08: Action Ownership and Due Date
- **Requirement**: All high-AP items (AP >= 100) have an assigned responsible person and target completion date.
- **Obligation**: Shall
- **How Verified**: Tab "05_PFMEA_Worksheet", for AP >= 100, check "Responsible" and "Due Date" columns.
- **Confidence**: High
- **Common Finding**: NO if responsibility or due date missing; LC if some incomplete.
- **Rationale**: Ownership ensures accountability; due date tracks closure.

### PFMEA-09: Special Characteristics
- **Requirement**: High-severity failure modes (S >= 8) are flagged as special characteristics and linked to process controls.
- **Obligation**: Should
- **How Verified**: Tab "06_Special_Characteristics" has entries for high-S items (or items marked as special in PFMEA).
- **Confidence**: Medium
- **Common Finding**: FC if all high-S items flagged; PC if most flagged; NA if no high-S items.
- **Rationale**: High-S items require heightened awareness and control (e.g., SPC, 100% inspection).

### PFMEA-10: Control Plan Linkage
- **Requirement**: All high-AP items (AP >= 100) are linked to a control method in the Control Plan.
- **Obligation**: Shall
- **How Verified**: Tab "10_Linkage_to_Control_Plan" maps failure mode -> control method -> sample size for all high-AP items.
- **Confidence**: High
- **Common Finding**: FC if all high-AP items have control linkage; PC if most; NO if linkage is missing.
- **Rationale**: Linkage ensures PFMEA actions are realized in Control Plan (sampling, acceptance criteria).

### PFMEA-11: Process Step Traceability
- **Requirement**: Every failure mode in PFMEA can be traced back to a process step in the flow chart. No orphan modes.
- **Obligation**: Shall
- **How Verified**: PFMEA "Step ID" column matches process flow "Step ID". Scan for mismatches.
- **Confidence**: High
- **Common Finding**: PC if step IDs are inconsistent or some modes lack step ID; NO if orphan modes exist.
- **Rationale**: Traceability ensures FMEA is complete and accountable to process design.

### PFMEA-12: Lessons Learned
- **Requirement**: Lessons Learned from prior programs are cross-referenced in the PFMEA (e.g., similar failure modes, proven mitigations).
- **Obligation**: Should
- **How Verified**: Tab "11_Lessons_Learned_Crossref" present with references to prior issues.
- **Confidence**: Medium
- **Common Finding**: PC if tab missing; FC if prior lessons are cited and risk reduction is justified.
- **Rationale**: Reuses industry knowledge; prevents repeat failures.

### PFMEA-13: DFMEA Cross-Link
- **Requirement**: PFMEA is linked to DFMEA (Design FMEA) for traceability of design inputs and manufacturing constraints.
- **Obligation**: Should
- **How Verified**: Cannot be verified entirely from PFMEA xlsx. Reviewer checks Design Review notes for DFMEA cross-reference.
- **Confidence**: Low
- **Recommended Action**: Confirm Design Review documents which DFMEA failure modes are driven by process (e.g., assembly mistakes, handling damage).
- **Rationale**: Design and process are coupled; changes to either should update the other.

### PFMEA-14: High-AP Completion Status
- **Requirement**: High-AP (>= 100) recommended actions are completed or have a documented closure plan with target date.
- **Obligation**: Shall
- **How Verified**: Tab "05_PFMEA_Worksheet" or "08_Action_Plan_Tracker", check "Status" or "Target Completion" for all high-AP items.
- **Confidence**: High
- **Common Finding**: NO if high-AP items are "Open" with no target date; LC if mostly closed; FC if all closed or tracked.
- **Rationale**: Open high-AP items indicate unresolved risk; must be addressed before production release.

---

## Verification Assessment (VA) — 4 External Verification Checks

Per AIAG-VDA Handbook Section 6 (Verification & Validation).

### VA-01: Verification Plan Compliance
- **Requirement**: A Verification Plan exists that confirms PFMEA alignment with production requirements.
- **Obligation**: Should
- **How Verified**: Reviewer checks Design Review or Quality Plan for Verification Plan reference.
- **Confidence**: Low (external document)
- **Common Finding**: Pending until Verification Plan is provided.

### VA-02: Verification Methods and Sample Sizes
- **Requirement**: Verification methods (e.g., SPC, capability study, 100% inspection) and sample sizes are specified.
- **Obligation**: Should
- **How Verified**: Reviewer checks Control Plan and PPAP for sampling strategy.
- **Confidence**: Low (external document)
- **Common Finding**: Pending until Control Plan is finalized.

### VA-03: Verification Executed
- **Requirement**: Verification per plan has been executed and results documented.
- **Obligation**: Should
- **How Verified**: Reviewer checks Ppap Run @ Rate phase for production data.
- **Confidence**: Low (external document)
- **Common Finding**: Pending until production data is available.

### VA-04: Verification Report
- **Requirement**: Verification Report summarizes results, acceptance criteria, and sign-off.
- **Obligation**: Should
- **How Verified**: Reviewer checks Quality Plan closure or PPAP final approval.
- **Confidence**: Low (external document)
- **Common Finding**: Pending until PPAP submission phase.

---

## Rating Color Guide (for Excel Dashboard)

- **FC** (Fully Compliant): Green (#C6EFCE)
- **LC** (Largely Compliant): Light Blue (#9DC3E6)
- **PC** (Partially Compliant): Yellow (#FFC000)
- **NO** (Not Compliant): Orange/Red (#F8CBAD)
- **NA** (Not Applicable): Grey (#E0E0E0)
- **Pending**: Dark Grey (#808080)
