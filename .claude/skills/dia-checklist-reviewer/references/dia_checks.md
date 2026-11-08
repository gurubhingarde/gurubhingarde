# DIA Assessment Checks — Detailed Reference

## Confirmation Review (CR) — 14 Doc-Quality Checks

Standard ISO 26262-8 Section 10 checks applied to any work product:

| # | Check | Purpose | Obligation |
|---|-------|---------|-----------|
| 1 | Document Structuring | Is the document structured (headlines, template layouts) for maintainability? | Shall |
| 2 | Latest Template | Was the latest available template used at creation? | Should |
| 3 | Search Aids | Does structure facilitate search (cross-references, index, abbreviations)? | Should |
| 4a | Title Covers Scope | Does the title cover the scope of the content? | Shall |
| 4b | Author & Approver | Are author and approver(s) listed? | Shall |
| 4c | Unique Revision ID | Is each revision uniquely identified? | Shall |
| 4d | Change History | Is there a change history available? | Shall |
| 4e | Status | Is the work product status provided (Draft/In Review/Released)? | Shall |
| 5 | Current Revision Identifiable | Is the current revision clearly identifiable? | Shall |
| 6 | Configuration Management | Is the document under configuration and change management? | Shall |
| 7 | Header/Footer | Are header and footer updated with doc ID and revision? | Should |
| 8 | Table of Contents | Does the document contain a correct table of contents? | Shall |
| 9 | References | Does the Reference Table list all referenced documents? | Should |
| 10 | Sections Complete | Have all sections of the work product been completed? | Should |

### CR Auto-Fill Logic

- **FC (Fully Compliant)**: All expected title fields (Item, Doc ID, Revision, Status) are populated; 11+ tabs present.
- **LC (Largely Compliant)**: Most fields populated; some tabs missing; revision history incomplete.
- **PC (Partially Compliant)**: Multiple fields missing; <11 tabs; structure incomplete.
- **NO (Not Compliant)**: Title missing, no revision, no author/approver, zero doc structure.

---

## DIA Assessment (DIAA) — 14 Substantive Checks per ISO 26262-8 Section 5

The most critical checks for a Design Interface Agreement. These verify parties, roles, RACI completeness, communication, deliverables, and agreement terms.

### DIAA Checks 1–6: Party & RACI Completeness (HIGHEST VALUE)

| # | Check | Purpose | Obligation | Auto-Fill Logic |
|---|-------|---------|-----------|-----------------|
| 1 | All parties identified with role | OEM, Tier-1, Tier-2, IC suppliers explicitly named; each has a role. | Shall | FC: 2+ parties with roles. NO: <2 parties or missing roles. |
| 2 | FuSa contact per party | Each party has a designated Functional Safety contact (not just commercial). | Shall | FC: 100% have FuSa contact. NO: Any party missing FuSa contact. |
| 3 | RACI covers major WPs | RACI matrix includes at minimum: HARA, Item Def, FSC, TSC, FMEDA, SW Reqs, Safety Case. | Shall | FC: 5-7 major WPs present. LC: 3-4. PC: <3. NO: 0 RACI entries. |
| 4 | Exactly one Accountable per WP | No double-assignment or missing Accountable. | Shall | FC: 100% of rows have exactly 1 A. NO: Any row with 0 or 2+ A. |
| 5 | At least one Responsible per WP | Every work product has ≥1 R. | Shall | FC: 100% of rows have ≥1 R. NO: Any row with 0 R. |
| 6 | No completely empty WP rows | Every work product has ≥1 RACI assignment (R/A/C/I). | Shall | FC: 100% non-empty. NO: Any row completely empty. |

**Rationale**: These six checks validate the fundamental agreement structure. Missing parties, incomplete RACI, and duplicate Accountable assignments are ISO 26262 showstoppers.

---

### DIAA Checks 7–14: Communication & Governance

| # | Check | Purpose | Obligation | Auto-Fill Logic |
|---|-------|---------|-----------|-----------------|
| 7 | Communication protocol defined | Channels, cadence, format, owner, and escalation path documented. | Shall | FC: 1+ channel with cadence+escalation. LC: Channels present but incomplete escalation. PC: Only channel names. NO: No communication protocol. |
| 8 | Joint review schedule | Milestones, participants, and schedules for major reviews. | Shall | FC: 1+ milestone with schedule. LC: Milestones present, some unscheduled. PC: Incomplete. NO: None defined. |
| 9 | Supplier deliverables | Format, language, planned date, and acceptance criteria listed. | Shall | FC: All items have format+criteria. LC: Format present, missing criteria. PC: Incomplete. NO: None listed. |
| 10 | Change management process | Process for handling scope/content changes clearly described. | Shall | FC/LC: Process documented. PC/NO: Missing or vague. |
| 11 | Tool sharing terms (if applicable) | If tools are shared, terms are documented. | Should | NA: No tools shared. LC/FC: Terms documented. PC: Incomplete. |
| 12 | Confidentiality & IP terms | Confidentiality, IP ownership, and usage restrictions documented. | Shall | FC: All terms present. LC/PC: Partial. NO: Missing. |
| 13 | References | Master agreement, item definition, standards cited. | Should | FC: References present and complete. PC: Incomplete or missing. |
| 14 | Item scope bounded | In-scope and out-of-scope items clearly enumerated. | Shall | FC: Both enumerated. PC: Only in-scope or out-of-scope. NO: Neither. |

**Rationale**: Checks 7–14 ensure the agreement is operationalizable: parties know how to communicate, when reviews occur, what is expected, and who owns what.

---

## Verification Assessment (VA) — 5 External Governance Checks

Most VA items refer to external Verification Plan, governance, or meeting evidence. These are marked Pending and reviewed offline against project records.

| # | Check | Purpose | Obligation |
|---|-------|---------|-----------|
| 1 | Verification Plan ensures DIA compliance | Verification Plan demonstrates DIA compliance and consistency with FSC. | Shall |
| 2 | DIA reviews held per schedule | Joint reviews actually occurred per the schedule. | Should |
| 3 | Action items tracked | DIA action items from reviews tracked to closure. | Should |
| 4 | Issues recorded | Issues and non-conformances recorded and dispositioned. | Should |
| 5 | Governance effectiveness | DIA governance effectiveness verified and demonstrated. | Should |

All VA items remain Pending unless the reviewer manually verifies against external governance evidence.

---

## How to Read Findings in the Checklist

### High-Confidence Findings

> **Finding**: "All 4 parties identified with roles: OEM, Tier-1, Tier-2, IC Supplier."  
> **Confidence**: High  
> **Meaning**: The skill found this directly in the Parties tab.

### Medium-Confidence Findings

> **Finding**: "RACI matrix covers 5/7 major work products (HARA, Item Def, FSC, TSC, FMEDA); reviewer to confirm against FSC definition."  
> **Confidence**: Medium  
> **Meaning**: The skill found the RACI entries but can't verify they match the actual FSC scope.

### Low-Confidence (Drafted) Findings

> **Finding**: "(Auto-suggest, requires reviewer judgment) Communication protocol text present: monthly reviews, email escalation. Reviewer to confirm cadence is workable given project schedule."  
> **Confidence**: Low  
> **Meaning**: The skill found text; the reviewer must apply judgment.

---

## Recommended Review Workflow

1. **Open the Summary tab** — scan the KPI dashboard and Findings table.
2. **Look for NO ratings on Shall items** — these are mandatory non-conformances that block acceptance.
3. **Review DIAA checks 1–6** first (parties, FuSa contacts, RACI) — these are the highest-value findings.
4. **For each NO or PC item**:
   - Read the Recommended Action.
   - Update the source DIA if needed.
   - Re-run the skill.
5. **For each Pending item**:
   - Apply reviewer judgment (read the "(Auto-suggest)" comment).
   - Check the Page/Section reference in the source DIA.
   - Set the Assessment to FC / LC / PC / NO / NA as appropriate.
6. **When all Shall items are FC and major issues are zero**, DIA acceptance can be granted.

---

## Common Defects and Fixes

| Defect | Check | Fix |
|--------|-------|-----|
| "Company X has no FuSa contact" | Check 2 | Add functional safety contact name/title in 02_Parties, FuSa Contact column. |
| "FSC work product has no Accountable" | Check 4 | Edit 04_RACI_Matrix; assign exactly one party as "A" for FSC. |
| "Item Definition has no Responsible" | Check 5 | Edit 04_RACI_Matrix; assign at least one party as "R" for Item Definition. |
| "No Communication Protocol tab" | Check 7 | Create 05_Communication_Protocol tab; add channels, cadence, escalation. |
| "Communication Protocol missing escalation" | Check 7 | Add escalation path (e.g., "Lead → Steering Committee → Executive") to each channel. |
| "Supplier deliverables incomplete" | Check 9 | Add format (e.g., "PDF"), language (e.g., "English"), date, and acceptance criteria. |
| "No change management process" | Check 10 | Document in 08_Change_Management tab: how scope changes are approved, who decides, timeline. |
| "No confidentiality/IP terms" | Check 12 | Document in 10_Confidentiality_IP tab: IP ownership, confidentiality periods, usage rights. |
| "Scope not bounded" | Check 14 | List in-scope items (e.g., "Brake System, Steering") and out-of-scope (e.g., "SOTIF, Cybersecurity") in 03_Item_Scope. |
