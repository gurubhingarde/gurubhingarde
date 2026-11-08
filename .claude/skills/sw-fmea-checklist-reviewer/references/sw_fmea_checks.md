# SW FMEA Checklist — Check Definitions & Rationale

This document details the 32 checks (14 CR + 14 SWFMEAA + 4 VA) run by `sw-fmea-checklist-reviewer`.

## Confirmation Review (CR) — Generic Doc-Quality Checks

**Purpose**: Verify the SW FMEA meets document structure, completeness, and traceability standards per ISO 26262-8 Section 10 (Generic Confirmation Measures).

### CR-1: Document Structured Clearly
- **Requirement**: Is the document structured into distinct, logically grouped sections?
- **Obligation**: Shall
- **What We Check**: Count of worksheet tabs (>= 10 indicates good structure)
- **Pass (FC)**: 10+ tabs with distinct purposes (Title, Components, FMEA, Detection, etc.)
- **Fail (PC/NO)**: Fewer than 10 tabs suggests under-organization
- **Confidence**: Medium (heuristic; actual structure quality is subjective)

### CR-2: Latest Template Used
- **Requirement**: Was a current, reviewed template used as starting point?
- **Obligation**: Should
- **What We Check**: Cannot verify from xlsx alone
- **Auto-Fill**: Draft finding; reviewer confirms template version manually
- **Confidence**: Low (external knowledge required)

### CR-3: Document Facilitates Search
- **Requirement**: Can reviewers easily navigate and find specific content?
- **Obligation**: Should
- **What We Check**: Presence of Title/Document Control tab in first 3 sheets + References tab
- **Pass (FC)**: Both present
- **Fail (PC)**: Missing TOC or References
- **Confidence**: Medium

### CR-4a-e: Title, Authorship, Revision, Status
- **Requirement** (4a-e): Title covers scope; author & approver listed; revision unique; change history present; status indicated
- **Obligation**: All Shall
- **What We Check**: Presence of fields on Title page (extracted by probe)
- **Pass (FC)**: All fields populated
- **Fail (NO)**: Any field missing
- **Confidence**: High (direct xlsx inspection)

### CR-5: Current Revision Identifiable
- **Requirement**: Is the current revision number clear and unique?
- **Obligation**: Shall
- **What We Check**: Revision field populated
- **Pass (FC)**: Revision present
- **Fail (NO)**: Revision not set
- **Confidence**: High

### CR-6: Configuration Management
- **Requirement**: Is the document under a configuration management system?
- **Obligation**: Shall
- **What We Check**: Cannot verify from xlsx; this is an org-level practice
- **Auto-Fill**: Draft; reviewer confirms CM system used (Polarion, DOORS, Git, etc.)
- **Confidence**: Low

### CR-7: Headers/Footers Updated
- **Requirement**: Do headers and footers reflect current revision and project info?
- **Obligation**: Should
- **What We Check**: Cannot verify from xlsx headers/footers programmatically
- **Auto-Fill**: Draft; reviewer manually checks printed/exported PDF
- **Confidence**: Low

### CR-8: Table of Contents
- **Requirement**: Is TOC present and accurate?
- **Obligation**: Shall
- **What We Check**: Presence of "Title" or "Document Control" tab near top
- **Pass (FC)**: Found
- **Fail (PC)**: Not found
- **Confidence**: High

### CR-9: References
- **Requirement**: Are all citations listed in a References section?
- **Obligation**: Should
- **What We Check**: Presence of "References" tab
- **Pass (FC)**: Found
- **Fail (PC)**: Not found
- **Confidence**: High

### CR-10: Sections Complete
- **Requirement**: Have all major sections been completed?
- **Obligation**: Should
- **What We Check**: SW component catalog — % of components with ASIL assigned
- **Pass (FC)**: >= 90% complete
- **Fail (LC)**: 70–90%
- **Fail (PC)**: < 70%
- **Confidence**: High

### CR-11: Document ID Unique
- **Requirement**: Is there a unique, persistent document ID?
- **Obligation**: Shall
- **What We Check**: Doc ID field on Title page
- **Pass (FC)**: Present
- **Fail (NO)**: Not set
- **Confidence**: High

### CR-12: Project Context
- **Requirement**: Is project/program name identified?
- **Obligation**: Should
- **What We Check**: Project field on Title page
- **Pass (FC)**: Present
- **Fail**: Draft; reviewer provides project context
- **Confidence**: Medium

### CR-13: References Complete
- **Requirement**: Are all citations complete and traceable?
- **Obligation**: Should
- **What We Check**: Presence of References tab + manual review of citations
- **Auto-Fill**: Draft if References tab present; reviewer confirms completeness
- **Confidence**: Low

### CR-14: All FMEA Sections Populated
- **Requirement**: Do all mandatory FMEA tabs exist?
- **Obligation**: Shall
- **What We Check**: Presence of 00_Title_Page, 03_SW_Component_Catalog, 05_FMEA_Worksheet
- **Pass (FC)**: All present
- **Fail (PC)**: Some missing
- **Confidence**: High

---

## SW FMEA Assessment (SWFMEAA) — Substantive Checks

**Purpose**: Verify the SW FMEA content meets ISO 26262-9 Section 8 and ISO 26262-6 (SW safety requirements) requirements.

### SWFMEAA-1: Assumptions Documented
- **Requirement**: Have all scope, methodology, and FM library source assumptions been documented?
- **Obligation**: Shall
- **What We Check**: Populated fields in 02_Assumptions: Scope, Methodology, FM Library Source
- **Pass (FC)**: All three present
- **Fail (PC)**: Any missing
- **Confidence**: High (direct inspection)

### SWFMEAA-2: SW Component Catalog Complete
- **Requirement**: Is the SW component catalog complete with ASIL assignments?
- **Obligation**: Shall
- **What We Check**: Number of components with ASIL field set
- **Pass (FC)**: 100% of components have ASIL
- **Fail (PC)**: < 100%
- **Fail (NO)**: Catalog empty
- **Confidence**: High

### SWFMEAA-3: Coverage of Safety-Critical Components
- **Requirement**: Does each safety-critical SW component have at least one failure mode in the FMEA worksheet?
- **Obligation**: Shall
- **What We Check**: For each component marked "Safety-Critical" in catalog, verify >= 1 FMEA row exists
- **Pass (FC)**: All safety-critical components represented
- **Fail (PC)**: Some missing
- **Confidence**: High

### SWFMEAA-4: Severity Rated
- **Requirement**: Is every failure mode rated for severity?
- **Obligation**: Shall
- **What We Check**: Each FMEA row has Severity in {S0, S1, S2, S3}
- **Pass (FC)**: 100% of rows rated
- **Fail (PC)**: Partial coverage
- **Confidence**: High

### SWFMEAA-5: Frequency Rated
- **Requirement**: Is every failure mode rated for frequency?
- **Obligation**: Shall
- **What We Check**: Each FMEA row has Frequency in {Rare, Occasional, Frequent}
- **Pass (FC)**: 100% of rows rated
- **Fail (PC)**: Partial coverage
- **Confidence**: High

### SWFMEAA-6: Detection Mechanism Specified
- **Requirement**: Does every failure mode have a detection mechanism specified?
- **Obligation**: Shall
- **What We Check**: Each FMEA row has non-empty Detection Mechanism cell
- **Pass (FC)**: 100% specified
- **Fail (PC)**: Partial coverage
- **Confidence**: High

### SWFMEAA-7: Detection Coverage Rated
- **Requirement**: Does every failure mode have detection coverage rated?
- **Obligation**: Shall
- **What We Check**: Each FMEA row has Coverage in {Low, Med, High}
- **Pass (FC)**: 100% rated
- **Fail (PC)**: Partial coverage
- **Confidence**: High

### SWFMEAA-8: Pre-Risk Computed
- **Requirement**: Is pre-mitigation risk computed for all failure modes?
- **Obligation**: Shall
- **What We Check**: Each FMEA row has Pre-Risk > 0 (usually Severity × Frequency)
- **Pass (FC)**: 100% computed
- **Fail (PC)**: Partial coverage
- **Confidence**: High

### SWFMEAA-9: Post-Risk Computed
- **Requirement**: Is post-mitigation risk computed for all failure modes?
- **Obligation**: Shall
- **What We Check**: Each FMEA row has Post-Risk > 0 (after detection & mitigation applied)
- **Pass (FC)**: 100% computed
- **Fail (PC)**: Partial coverage
- **Confidence**: High

### SWFMEAA-10: Residual Risk Acceptable (HEADLINE CHECK)
- **Requirement**: Is residual risk acceptable per ASIL threshold (D<=1, C<=3, B<=9, A<=27)?
- **Obligation**: Shall
- **What We Check**: For each FMEA row, Post-Risk <= ASIL threshold (inferred from SW component ASILs)
- **Pass (FC)**: All failure modes pass
- **Fail (NO)**: Any failure mode exceeds threshold (blocking issue)
- **Confidence**: High (data-driven; reads evaluated Post-Risk cells with data_only=True)
- **Importance**: HEADLINE VALIDATION — unmitigated high-risk modes must be resolved before FMEA acceptance

### SWFMEAA-11: Propagation Paths Documented
- **Requirement**: Are propagation paths documented for high-severity failure modes?
- **Obligation**: Should
- **What We Check**: 07_Propagation_Paths tab has content; if severity S2/S3 exists, paths should be present
- **Pass (FC)**: Paths documented or no high-severity modes
- **Fail (PC)**: High-severity modes but no propagation analysis
- **Confidence**: Medium

### SWFMEAA-12: Coverage Summary
- **Requirement**: Is coverage summary computed per Safety Goal?
- **Obligation**: Should
- **What We Check**: 08_Coverage_Summary tab has content
- **Pass (FC)**: Summary present
- **Fail (PC)**: Missing or sparse
- **Confidence**: Medium

### SWFMEAA-13: Open Items Reviewed
- **Requirement**: Have open items been reviewed for criticality?
- **Obligation**: Should
- **What We Check**: 09_Open_Items tab; flag critical items (keywords: "critical", "blocker")
- **Pass (FC)**: No open items, or only non-critical
- **Fail (NO)**: Critical items found
- **Fail (LC)**: Non-critical items present
- **Confidence**: High

### SWFMEAA-14: Verification Hooks Defined
- **Requirement**: Are verification plan hooks defined per failure mode?
- **Obligation**: Should
- **What We Check**: 10_Verification_Plan_Hooks tab has content linking modes to test cases
- **Pass (FC)**: Hooks present
- **Fail (PC)**: Missing or sparse
- **Confidence**: High

---

## Verification Assessment (VA) — External Verification

**Purpose**: Identify external artifacts required for full FMEA validation.

All 4 VA checks are **Draft** (Pending) by default because they require documents outside the SW FMEA xlsx:

### VA-1: Verification Plan Compliance
- **Requirement**: Does a Verification Plan ensure all FMEA failure modes are tested?
- **External Artifact**: Verification Plan (separate document or test spec)
- **Auto-Fill**: Pending (Draft); reviewer obtains Verification Plan and confirms coverage

### VA-2: Verification Methods & Criteria
- **Requirement**: Are verification methods, pass/fail criteria, and environment defined?
- **External Artifact**: Verification Plan / Test Specification
- **Auto-Fill**: Pending; reviewer confirms completeness

### VA-3: Verification Executed
- **Requirement**: Was verification executed per plan?
- **External Artifact**: Verification Execution Log, Test Reports
- **Auto-Fill**: Pending; reviewer obtains execution evidence

### VA-4: Verification Report
- **Requirement**: Does Verification Report document pass/fail and provide traceability evidence?
- **External Artifact**: Verification Report, Test Summary
- **Auto-Fill**: Pending; reviewer obtains and reviews report

---

## Check Execution Logic

Each check follows this pattern:

```python
def check_name(p: ProbedSwFmea) -> CheckResult:
    # 1. Extract data from probed SW FMEA
    # 2. Apply verification logic (thresholds, comparisons, counts)
    # 3. Return CheckResult with:
    #    - rating: FC / LC / PC / NO / NA / ""(pending)
    #    - finding: evidence from xlsx or explanation
    #    - recommended_action: what analyst should do if PC/NO
    #    - confidence: High / Medium / Low
```

**Exception Handling**: If a check raises an exception (malformed data, missing columns), it returns a Pending finding with the exception message; checklist generation continues.

---

## References

- ISO 26262:2018 Part 9 §8 — SW FMEA confirmation measures
- ISO 26262:2018 Part 6 §5 — SW safety requirements specification
- ISO 26262:2018 Part 2 §10 — Confirmation Review per ASIL
