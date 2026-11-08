# Safety Plan Checks — Detailed Reference

## Confirmation Review Checks (CR 1–10)

These 14 checks verify document quality per ISO 26262-8 §10. They are generic across all work products.

| # | Requirement | Obligation | What's Verified | Confidence | Auto-Fill Method |
|---|-------------|-----------|-----------------|------------|------------------|
| 1 | Is the document structured in a clear manner? | Shall | Multiple tabs with distinct sections | Medium | Tab count ≥ 8 |
| 2 | Was the latest template used? | Should | Template version | Low | Auto-suggests; reviewer confirms |
| 3 | Does structure facilitate search? | Should | Searchable layout, TOC, references | Medium | Numbered tabs (0x_Name format) |
| 4a | Does the title cover the scope? | Shall | Title page title field populated | Low | Auto-suggests; reviewer confirms |
| 4b | Are author and approver listed? | Shall | Author and Approver fields | High | Both fields non-empty |
| 4c | Unique revision identification? | Shall | Revision field on Title page | High | Revision field populated |
| 4d | Change history available? | Shall | Document Control tab with history | High | safety-plan-builder format detection |
| 4e | Status provided? | Shall | Status field on Title page | High | Status field populated |
| 5 | Current revision clearly identifiable? | Shall | Revision on Title page | High | Revision field populated |
| 6 | Under configuration management? | Shall | CM system (Polarion, DOORS, Git) | Low | Auto-suggests; reviewer confirms |
| 7 | Header and footer updated? | Should | Worksheet header/footer | Low | Cannot verify programmatically |
| 8 | Correct table of contents? | Shall | TOC tab or numbered sheets | Medium | Sheets named 0x_Name... |
| 9 | References listed? | Should | References tab | Medium | "References" sheet detected |
| 10 | All sections completed? | Should | Major tabs populated (≥3 of 4 critical) | High | Tab presence: Project Info, Roles, WPs, CRs |

---

## Safety Plan Assessment Checks (SPA 1–14)

These 14 checks verify substantive Safety Plan compliance per **ISO 26262-2:2018 clause 6 (Safety Planning)**.

### SPA-1: Functional Safety Manager Assigned (Shall)

**Requirement**: FSM must be assigned and identified in the Safety Plan.

**What's Verified**: At least one role entry has "FSM" or "Functional Safety Manager" in the role field.

**Confidence**: High (direct text match in Roles tab)

**Auto-Fill Logic**:
- FC: Role with "FSM" or "Functional Safety Manager" found; returns name and role
- NO: No FSM role detected; recommends "Assign a Functional Safety Manager and document in Roles & Responsibilities tab"

**Reviewer Guidance**: Confirm the assigned FSM has the independence, experience, and authority to oversee the entire functional safety program.

---

### SPA-2: Roles & Responsibilities Defined (Shall)

**Requirement**: Roles including FSM, Project Manager, HW Lead, SW Lead must be defined.

**What's Verified**: ≥3 roles defined; at least 3 of {FSM, Project Manager, Hardware, Software} present.

**Confidence**: High (role count and type detection)

**Auto-Fill Logic**:
- FC: ≥4 roles found including key leadership positions
- LC: 3+ roles found; some key roles may be absent
- NO: <3 roles total; major roles missing

**Reviewer Guidance**: Ensure clear RACI matrix is defined. Each role must have documented authority, responsibility, and independence level.

---

### SPA-3: Tailoring Justified (Shall)

**Requirement**: All "Not Applicable" or "Partial" tailoring decisions must have written justifications.

**What's Verified**: For each tailoring decision marked Partial or NA, a justification field is populated.

**Confidence**: High (cell content check)

**Auto-Fill Logic**:
- FC: All decisions are Applicable OR all Partial/NA have justifications
- LC: 80%+ of Partial/NA decisions justified
- PC: <80% of decisions justified
- NO: No tailoring tab detected (cannot verify)

**Reviewer Guidance**: Per ISO 26262-2:2018 clause 6.3.2, each tailoring decision must cite the basis (e.g., "Not applicable because item is not safety-critical per ASIL decomposition").

---

### SPA-4: Work Products List Complete (Shall)

**Requirement**: All safety-relevant work products must be listed (HARA, FSC, TSC, FMEDA, Safety Case, etc.).

**What's Verified**: ≥5 work products listed; at least 3 of {HARA, FSC, TSC, FMEDA, Safety Case} found by name match.

**Confidence**: High (heuristic name match)

**Auto-Fill Logic**:
- FC: ≥5 WPs with key WPs (HARA, FSC, TSC, etc.) present
- LC: 3+ WPs listed
- PC: <3 WPs or missing key ones
- NO: <3 WPs

**Reviewer Guidance**: Refer to ISO 26262-2:2018 clause 6.4 for the complete list of required work products per project scope.

---

### SPA-5: Work Product Owner Assigned (Shall)

**Requirement**: Each work product must have an assigned owner/responsible person.

**What's Verified**: "Owner" column populated for each work product.

**Confidence**: High (cell content)

**Auto-Fill Logic**:
- FC: All WPs have owner assigned
- LC: 80%+ WPs have owner
- PC: <80% WPs have owner

**Reviewer Guidance**: Owner must have authority to drive completion and quality. May be a person or team lead.

---

### SPA-6: Planned Date Defined (Shall)

**Requirement**: Planned completion date must be set for each work product.

**What's Verified**: "Planned Date" column non-empty for each WP.

**Confidence**: High (cell content)

**Auto-Fill Logic**:
- FC: All WPs have planned date
- LC: 90%+ WPs have date
- PC: <90% WPs have date

**Reviewer Guidance**: Planned dates drive the project schedule. Each must align with gate reviews and confirmation review availability.

---

### SPA-7: Target ASIL Specified (Shall)

**Requirement**: Target ASIL must be assigned to each work product.

**What's Verified**: "Target ASIL" column populated for each WP.

**Confidence**: High (cell content)

**Auto-Fill Logic**:
- FC: All WPs have ASIL assigned
- LC: 95%+ WPs have ASIL
- PC: <95% WPs have ASIL

**Reviewer Guidance**: ASIL drives confirmation review independence (ISO 26262-2 clause 6.4.7) and work-product complexity. Must be consistent with HARA output.

---

### SPA-8: Confirmation Review Planned for Every WP (Shall)

**Requirement**: Each safety-relevant work product must have a confirmation review planned.

**What's Verified**: For each WP, a matching entry exists in the Confirmation Reviews tab.

**Confidence**: High (cross-tab matching)

**Auto-Fill Logic**:
- FC: All WP IDs matched in CR tab
- LC: 80%+ WPs have CRs
- PC: 50%–80% WPs have CRs
- NO: <50% WPs have CRs

**Reviewer Guidance**: No work product with ASIL≥QM should bypass confirmation review. This is a hard requirement per ISO 26262-2:2018 clause 6.4.7.

---

### SPA-9: Independence Level Matches ASIL (Shall) ⭐ **HIGHEST VALUE**

**Requirement**: Confirmation review independence must match the assigned ASIL.

**What's Verified**: For each CR, the "Required Independence" field matches the expected level for the WP's target ASIL.

**Mapping**:
- ASIL D → I3 (independent organizational unit)
- ASIL C → I2 (independent team)
- ASIL A, B → I1 (independent person)
- QM → none (no CR required)

**Confidence**: High (machine-verifiable mapping)

**Auto-Fill Logic**:
- FC: All CRs have independence matching ASIL
- NO: Any mismatch; reports specific WP/ASIL/independence/expected triplet

**Reviewer Guidance**: This is the highest-value check. A mismatch (e.g., ASIL D with I1) is a critical non-compliance and blocks approval. Always verify the independence assignment against your project's organizational structure.

---

### SPA-10: Tools Listed with TCL Classification (Shall)

**Requirement**: All tools must be classified by Tool Confidence Level per ISO 26262-8:2018 clause 11.

**What's Verified**: "TCL" column populated for each tool entry.

**Confidence**: High (cell content)

**Auto-Fill Logic**:
- FC: All tools have TCL (0, 1, 2, or 3)
- LC: 80%+ tools have TCL
- PC: <80% tools have TCL

**Reviewer Guidance**: TCL0 = not qualified; TCL1 = confidence in quality; TCL2 = confidence + independent testing; TCL3 = full qualification. Tool selection and TCL impact the overall confidence in artifact quality.

---

### SPA-11: Tool Qualification Documented (Shall)

**Requirement**: TCL2 and TCL3 tools must have qualification status documented.

**What's Verified**: For each TCL2/TCL3 tool, "Qualification Status" field is populated.

**Confidence**: High (cell content)

**Auto-Fill Logic**:
- FC: No TCL2/TCL3 tools OR all TCL2/TCL3 tools have qualification documented
- PC: Some TCL2/TCL3 tools lack qualification status
- NA: No TCL2/TCL3 tools (no qualification required)

**Reviewer Guidance**: Per ISO 26262-8:2018 clause 12, TCL2/TCL3 tools require evidence of qualification (e.g., certification from vendor, internal validation report, third-party assessment).

---

### SPA-12: Anomaly Resolution Process (Shall)

**Requirement**: Procedure for detecting, reporting, resolving, and closing anomalies must be documented.

**What's Verified**: Dedicated "Anomaly Resolution" tab or equivalent section exists.

**Confidence**: Medium (tab detection is heuristic)

**Auto-Fill Logic**:
- FC: 09_Anomaly_Resolution or similar tab found; reviewer to verify completeness
- PC: No anomaly tab detected; recommends adding one

**Reviewer Guidance**: Anomaly resolution is a critical process; it bridges work-product review findings to corrective actions. Define entry/exit criteria, escalation paths, and closure criteria.

---

### SPA-13: Schedule Milestones Defined (Shall)

**Requirement**: Major safety-relevant milestones (gate reviews, WP completions) must be in the project schedule.

**What's Verified**: ≥3 milestone entries in the Schedule tab.

**Confidence**: Medium (count-based heuristic)

**Auto-Fill Logic**:
- FC: ≥3 milestones defined
- LC: 1–2 milestones defined
- PC: No milestones or empty Schedule tab

**Reviewer Guidance**: Milestones anchor the Safety Plan to the project schedule. Include: project start, HARA completion, FSC/TSC gate, tool qualification, CR completion, and project closeout.

---

### SPA-14: ISO 26262 References (Shall)

**Requirement**: The Safety Plan must reference applicable ISO 26262 parts and standards.

**What's Verified**: References tab exists and contains ISO 26262 citations.

**Confidence**: Medium (tab detection + auto-suggest)

**Auto-Fill Logic**:
- FC: References tab found; reviewer to verify ISO 26262 is cited
- PC: No References tab

**Reviewer Guidance**: At minimum, cite ISO 26262-1 (overview), -2 (safety management), -3 (HARA), -4 (concept phase), -5 (product development), and -8 (supporting processes). Include item definition, HARA output, FMEA standards (IEC 60812), and any OEM-specific safety requirements.

---

## Verification Assessment Checks (VA 1–6)

These 6 checks confirm that a Verification Plan exists and addresses the required topics. **All are marked external** (i.e., the verification artifacts live outside the Safety Plan xlsx); the reviewer ticks them off against the project's Verification Plan and Report documents.

| # | Topic | Obligation | Notes |
|---|-------|-----------|-------|
| 1 | VP ensures compliance with Safety Plan | Shall | External; reviewer verifies against VP document |
| 2 | Verification methods and tools specified | Shall | External; defined in VP Specification section |
| 3 | Pass/fail criteria defined | Shall | External; per ISO 26262-8:2018 clause 9.4.3 |
| 4 | Verification environment specified | Shall | External; lab, MIL, HIL, vehicle, etc. |
| 5 | Anomaly handling for verification deviations | Shall | External; part of Verification Plan anomaly process |
| 6 | Regression testing strategy | Shall | External; re-test scope after changes |

**Reviewer Guidance**: These rows will remain Pending in the auto-fill. The reviewer must manually assess each against the Verification Plan document and set FC/LC/PC/NO accordingly.

---

## Common Review Patterns

### Pattern 1: Missing Roles
If SPA-2 returns NO, immediately check:
- Do you have an FSM assigned? (SPA-1)
- Are key roles (Project Manager, HW/SW Leads) assigned?
- Do all roles have documented independence levels?

### Pattern 2: Incomplete Work Products
If SPA-4 or SPA-5 return PC/NO:
- Are all work products listed? (SPA-4)
- Are all owners assigned? (SPA-5)
- Does each WP have a planned date? (SPA-6)
- Does each WP have a target ASIL? (SPA-7)

### Pattern 3: CR Independence Mismatch (Highest Priority)
If SPA-9 returns NO:
- This is a critical non-compliance.
- Review the Recommended Actions for specific WP/ASIL/independence mismatches.
- Realign independence to ASIL per the mapping (ASIL D→I3, C→I2, A/B→I1).
- This alone can block Safety Plan approval.

### Pattern 4: External Items Pending
If VA 1–6 are all Pending:
- This is normal; these items live in the Verification Plan.
- Obtain the Verification Plan document from the project.
- For each row, read the VP section and set FC/LC/PC/NO.
- If the Verification Plan does not exist, set all to NO with recommended action to create it.
