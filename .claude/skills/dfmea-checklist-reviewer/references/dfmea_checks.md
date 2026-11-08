# DFMEA Checklist — Detailed Check Reference

## Confirmation Review (CR) — 14 Doc-Quality Checks

### CR-1: Document Structure

**Requirement**: Is the document structured clearly?  
**Obligation**: Shall  
**Confidence**: High

The DFMEA workbook should be organized into distinct tabs, each with a clear purpose.

| Finding | When to Assign |
|---------|---|
| FC | 10 or more tabs detected |
| PC | Fewer than 10 tabs; suggest adding structure |

**Recommended Action**: Ensure AIAG-VDA 12-tab template is used.

---

### CR-2: Template Compliance

**Requirement**: Was the latest AIAG-VDA 2019 template used?  
**Obligation**: Should  
**Confidence**: Medium

AIAG-VDA released the 2019 harmonized methodology in partnership with the German VDA. Use of this template ensures alignment with global automotive safety standards.

| Finding | When to Assign |
|---------|---|
| FC | dfmea-builder or equivalent detected |
| Draft | Cannot verify from xlsx alone |

**Recommended Action**: Confirm AIAG-VDA 2019 template was used as starting point.

---

### CR-3: Document Search Aids

**Requirement**: Does structure facilitate search (TOC + References)?  
**Obligation**: Should  
**Confidence**: High

A Table of Contents and References tab help reviewers navigate and verify sources.

| Finding | When to Assign |
|---------|---|
| FC | Both TOC and References tabs present |
| PC | Missing either TOC or References |

**Recommended Action**: Add missing tabs.

---

### CR-4a: Title and Scope

**Requirement**: Does title cover scope?  
**Obligation**: Shall  
**Confidence**: High

Every DFMEA needs a clear, unambiguous title identifying the design being analyzed.

| Finding | When to Assign |
|---------|---|
| Draft | Title detected; reviewer confirms it covers scope |
| NO | No title found |

**Recommended Action**: Add document title (e.g., "Design FMEA for ESC ECU Rev C").

---

### CR-4b: FMEA Owner Identified

**Requirement**: Is FMEA owner identified?  
**Obligation**: Shall  
**Confidence**: High

The FMEA owner is the senior engineer responsible for the analysis. May differ from the team lead.

| Finding | When to Assign |
|---------|---|
| FC | FMEA owner field populated |
| NO | Owner not identified |

**Recommended Action**: Assign FMEA owner on Title page.

---

### CR-4c: Unique Revision

**Requirement**: Is revision uniquely identified?  
**Obligation**: Shall  
**Confidence**: High

Unique revision ID (e.g., "Rev 1.0", "Rev A", date stamp) ensures traceability.

| Finding | When to Assign |
|---------|---|
| FC | Revision field populated |
| NO | Revision not populated |

**Recommended Action**: Assign unique revision identifier.

---

### CR-4d: Change History

**Requirement**: Is change history available?  
**Obligation**: Shall  
**Confidence**: High

Document Control tab (or equivalent) tracks what changed between revisions.

| Finding | When to Assign |
|---------|---|
| FC | Document Control tab present |
| PC | No dedicated tab but history may be in Title page |

**Recommended Action**: Maintain revision log on Document Control tab.

---

### CR-4e: Status Field

**Requirement**: Is work-product status provided?  
**Obligation**: Shall  
**Confidence**: High

Status (Draft / Review / Released) indicates maturity and approval state.

| Finding | When to Assign |
|---------|---|
| FC | Status field populated |
| NO | Status not set |

**Recommended Action**: Set status to Draft, Review, or Released.

---

### CR-5: Current Revision Identifiable

**Requirement**: Is current revision clearly identifiable?  
**Obligation**: Shall  
**Confidence**: High

A reader should be able to quickly identify which revision they are looking at.

| Finding | When to Assign |
|---------|---|
| FC | Revision field and metadata are clear |
| NO | Revision ambiguous or missing |

**Recommended Action**: Ensure revision is visible in Title page and document metadata.

---

### CR-6: Configuration Management

**Requirement**: Is document under configuration management?  
**Obligation**: Shall  
**Confidence**: Low/Draft

Configuration management (Polarion, DOORS, Git, etc.) is an organizational practice.

| Finding | When to Assign |
|---------|---|
| Draft | Auto-suggest; reviewer confirms CM system is in place |

**Recommended Action**: Register DFMEA in organization's document control system.

---

### CR-7: Headers/Footers Updated

**Requirement**: Are headers/footers updated to reflect current revision?  
**Obligation**: Should  
**Confidence**: Low/Draft

Headers and footers are not readable from xlsx by automation.

| Finding | When to Assign |
|---------|---|
| Draft | Auto-suggest; manual verification required |

**Recommended Action**: Manually verify header/footer match current revision.

---

### CR-8: Table of Contents

**Requirement**: Is table of contents correct?  
**Obligation**: Shall  
**Confidence**: High

TOC should list all major sections and tabs.

| Finding | When to Assign |
|---------|---|
| FC | TOC tab present and appears complete |
| PC | No TOC detected |

**Recommended Action**: Add TOC listing all tabs and major sections.

---

### CR-9: References Tab

**Requirement**: Does Reference Table list all citations?  
**Obligation**: Should  
**Confidence**: High

References should cite AIAG-VDA Handbook, ISO standards, and design specifications.

| Finding | When to Assign |
|---------|---|
| FC | References tab present |
| PC | No References tab |

**Recommended Action**: Add References section with source citations.

---

### CR-10: Sections Complete

**Requirement**: Have all sections been completed?  
**Obligation**: Should  
**Confidence**: High

Structure Analysis, Function Analysis, and DFMEA Worksheet should all be populated.

| Finding | When to Assign |
|---------|---|
| FC | Element hierarchy present (>90% complete) |
| PC | Sparse element catalog |

**Recommended Action**: Populate system/subsystem/component hierarchy.

---

### CR-11: Document ID Unique

**Requirement**: Is FMEA ID unique and persistent?  
**Obligation**: Shall  
**Confidence**: High

FMEA ID (e.g., "DFMEA-ESC-001") must be unique within the organization.

| Finding | When to Assign |
|---------|---|
| FC | FMEA ID populated |
| NO | FMEA ID missing |

**Recommended Action**: Assign unique FMEA identifier per organizational numbering scheme.

---

### CR-12: Project Context

**Requirement**: Is project/program context identified?  
**Obligation**: Should  
**Confidence**: High

Project name helps reviewers understand design scope and timing.

| Finding | When to Assign |
|---------|---|
| FC | Project field populated |
| Draft | Not detected; reviewer to add |

**Recommended Action**: Add project/program name (e.g., "ESC Upgrade 2027").

---

### CR-13: References Complete

**Requirement**: Are all references complete and traceable?  
**Obligation**: Should  
**Confidence**: Medium/Draft

References should include AIAG-VDA 2019 Handbook, ISO 26262 (if safety-related), and customer requirements.

| Finding | When to Assign |
|---------|---|
| Draft | References tab present; reviewer confirms completeness |
| PC | No References tab |

**Recommended Action**: Cite AIAG-VDA 2019, ISO 26262, and OEM requirements.

---

### CR-14: All Sections Populated

**Requirement**: Are all major DFMEA sections populated?  
**Obligation**: Shall  
**Confidence**: High

Core tabs: Title Page, Header Block, Structure Analysis, Function Analysis, DFMEA Worksheet.

| Finding | When to Assign |
|---------|---|
| FC | All core tabs present |
| PC | Some tabs missing |

**Recommended Action**: Ensure AIAG-VDA tab structure is complete.

---

## DFMEA Assessment (DFMEAA) — 14 Substantive Checks

### DFMEAA-1: Header Block Complete

**Requirement**: Is header block complete (subject, owner, ID)?  
**Obligation**: Shall  
**Confidence**: High

Per AIAG-VDA 2019, Header Block (Tab 02) contains: Subject, Project, FMEA Owner, Customer, Model Years, FMEA ID, Confidentiality, Dates.

| Finding | When to Assign |
|---------|---|
| FC | Subject, Owner, FMEA ID all populated |
| PC | One or more fields missing |

**Recommended Action**: Complete all header block fields.

---

### DFMEAA-2: Structure Analysis Populated

**Requirement**: Is structure analysis (system/subsystem/component) populated?  
**Obligation**: Shall  
**Confidence**: High

Structure Analysis (Tab 03) defines the design hierarchy. Per AIAG-VDA, levels are typically System → Subsystem → Component.

| Finding | When to Assign |
|---------|---|
| FC | All three levels represented; >5 elements per level |
| PC | Sparse or incomplete hierarchy |

**Recommended Action**: Define complete system-to-component hierarchy.

---

### DFMEAA-3: Function Analysis Populated

**Requirement**: Is function analysis populated?  
**Obligation**: Shall  
**Confidence**: High

Function Analysis (Tab 04) lists design functions and links them to structure elements. Each function should be testable and traceable to design requirements.

| Finding | When to Assign |
|---------|---|
| FC | Multiple functions documented and linked |
| PC | Few or no functions listed |

**Recommended Action**: Document all design functions (e.g., "Monitor wheel speed", "Control motor output").

---

### DFMEAA-4: DFMEA Worksheet Rows Complete

**Requirement**: Are DFMEA worksheet rows complete (FM/FE/Cause)?  
**Obligation**: Shall  
**Confidence**: High

Main worksheet (Tab 05) must have Failure Mode, Failure Effect, and Failure Cause populated for every row.

| Finding | When to Assign |
|---------|---|
| FC | All rows have FM, FE, and Cause |
| PC | Some rows missing FE or Cause |
| NO | Many rows incomplete |

**Recommended Action**: Ensure every failure mode row has complete FM/FE/Cause narrative.

---

### DFMEAA-5: Severity Rated (1-10)

**Requirement**: Is Severity rated 1-10 for all failure modes?  
**Obligation**: Shall  
**Confidence**: High

Severity (S) is a 1-10 rating of the worst-case effect on the customer/vehicle if the failure occurs.

| Finding | When to Assign |
|---------|---|
| FC | All rows have S value 1-10 |
| PC | Some rows missing S |
| NO | Many rows unrated |

**Recommended Action**: Rate severity for all failure modes per AIAG-VDA severity table (see references).

---

### DFMEAA-6: Occurrence Rated (1-10)

**Requirement**: Is Occurrence rated 1-10 for all failure modes?  
**Obligation**: Shall  
**Confidence**: High

Occurrence (O) is a 1-10 rating of how likely the failure cause is to occur in production/field.

| Finding | When to Assign |
|---------|---|
| FC | All rows have O value 1-10 |
| PC | Some rows missing O |
| NO | Many rows unrated |

**Recommended Action**: Rate occurrence for all failure modes per field data, design change, or historical analysis.

---

### DFMEAA-7: Detection Rated (1-10)

**Requirement**: Is Detection rated 1-10 for all failure modes?  
**Obligation**: Shall  
**Confidence**: High

Detection (D) is a 1-10 rating of the design's ability to detect the failure before the customer is affected.

| Finding | When to Assign |
|---------|---|
| FC | All rows have D value 1-10 |
| PC | Some rows missing D |
| NO | Many rows unrated |

**Recommended Action**: Rate detection based on built-in tests, diagnostics, and manufacturing process controls.

---

### DFMEAA-8: Action Priority Computed

**Requirement**: Is Action Priority assigned for all failure modes?  
**Obligation**: Shall  
**Confidence**: High

Action Priority (AP) is computed from S, O, D using AIAG-VDA Table P.1 lookup logic: High / Medium / Low.

| Finding | When to Assign |
|---------|---|
| FC | All rows have AP (H, M, or L) |
| PC | Some rows missing AP |
| NO | Many rows without AP |

**Recommended Action**: Ensure AP is auto-computed from S/O/D per AIAG-VDA formula or lookup table.

---

### DFMEAA-9: High-AP Items Have Actions

**Requirement**: Do all High-AP items have recommended actions assigned?  
**Obligation**: Shall  
**Confidence**: High

Every High-AP failure mode must have a specific, actionable recommended action (design change, additional control, verification test).

| Finding | When to Assign |
|---------|---|
| FC | All H-AP items have actions |
| NO | Some H-AP items lack actions |

**Recommended Action**: Assign corrective/preventive actions to all High-AP items.

---

### DFMEAA-10: Action Plan Owner and Due Date

**Requirement**: Does Action Plan Tracker have owner and due date for every action?  
**Obligation**: Shall  
**Confidence**: High

Action Plan Tracker (Tab 08) must assign each action to an owner and give a target completion date.

| Finding | When to Assign |
|---------|---|
| FC | All actions have owner and due date |
| PC | Some actions missing owner or due date |
| NO | Many actions untracked |

**Recommended Action**: Complete Action Plan Tracker with owner and due-date assignments.

---

### DFMEAA-11: Special Characteristics Identified

**Requirement**: Are special characteristics identified for high-severity items?  
**Obligation**: Should  
**Confidence**: High

Special Characteristics (Tab 06) are design parameters, tolerances, or manufacturing controls critical to prevent or detect high-severity failure modes (S >= 8).

| Finding | When to Assign |
|---------|---|
| FC | High-severity modes have SCs identified |
| PC | Few SCs despite high-severity modes |
| NA | No high-severity modes |

**Recommended Action**: Link high-severity failure modes to Special Characteristics for design/manufacturing control.

---

### DFMEAA-12: Lessons Learned

**Requirement**: Are lessons learned documented?  
**Obligation**: Should  
**Confidence**: Medium/Draft

Lessons Learned tab (or equivalent) cross-references prior DFMEAs, family DFMEA insights, and reusable solutions.

| Finding | When to Assign |
|---------|---|
| FC | Lessons Learned tab present |
| Draft | Lessons not yet compiled; auto-suggest |

**Recommended Action**: Document lessons from prior designs and recommend reuse of solutions.

---

### DFMEAA-13: AIAG-VDA References

**Requirement**: Is AIAG-VDA 2019 Handbook referenced?  
**Obligation**: Should  
**Confidence**: Medium/Draft

References tab should cite the AIAG-VDA FMEA Handbook (2019 edition) as the methodology source.

| Finding | When to Assign |
|---------|---|
| Draft | References present; reviewer confirms AIAG-VDA cite |
| PC | No References tab |

**Recommended Action**: Add AIAG-VDA 2019 Handbook citation.

---

### DFMEAA-14: High-AP Items Pending Closure (Headline Metric)

**Requirement**: How many High-AP items are pending closure?  
**Obligation**: Shall  
**Confidence**: High

**This is the headline metric.** Count High-AP failure modes whose status is not Closed, Completed, or Verified.

| Finding | When to Assign |
|---------|---|
| FC | 0 high-AP items pending |
| NO | Any high-AP items pending closure |

**Interpretation**: Untracked high-AP items signal an incomplete DFMEA. Every High-AP item must have a corrective action with owner, due date, and closure status.

**Recommended Action**: Track all High-AP actions to completion; retest if status changes.

---

## Verification Assessment (VA) — 4 External Checks

All VA checks are marked **Pending by default** because they require external Verification Plan and Verification Report documents. Reviewer ticks these off once verification artifacts are available.

### VA-1: Verification Plan Compliance

**Requirement**: Does Verification Plan ensure DFMEA compliance?  
**Obligation**: Shall

Verification Plan should explicitly reference DFMEA items being verified.

---

### VA-2: Verification Methods, Criteria, Environment

**Requirement**: Does plan address methods, criteria, and environment?  
**Obligation**: Shall

Verification should state: (a) how tests are performed (e.g., lab rig, field trial), (b) pass/fail criteria, (c) environmental conditions tested.

---

### VA-3: Verification Executed

**Requirement**: Was verification executed per plan?  
**Obligation**: Shall

Evidence of test execution: test logs, lab notes, field test reports.

---

### VA-4: Verification Report

**Requirement**: Does Verification Report include results and evidence?  
**Obligation**: Shall

Report should show: (a) which DFMEA items were tested, (b) results for each test (pass/fail), (c) sign-off by verification engineer.
