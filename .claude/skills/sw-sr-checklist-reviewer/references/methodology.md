# SW Safety Requirements Checklist — Methodology

## Overview

The SW Safety Requirements (SW-SR) Checklist Reviewer applies ISO 26262-6 Section 6 (Software Requirements Specification) confirmation-measures principles to an existing SW-SR workbook, producing an audit-ready checklist with auto-filled findings, evidence references, and recommended corrective actions.

The skill does **not** generate SW-SRs or modify the source workbook. It **assesses** completeness, consistency, and compliance of an existing SW-SR specification against 38 canonical checks organized into three categories:

1. **Confirmation Review (CR)** — 14 document-quality checks (ISO 26262-8 Section 10)
2. **SW Safety Requirements Assessment (SWSRA)** — 12 substantive checks per ISO 26262-6 Section 6
3. **Verification Assessment (VA)** — 22 external + 5 SW-SR-specific checks

## Confirmation Review (CR) — Document Quality

CR applies generic document-hygiene checks to any structured specification:

| ID | Obligation | Check | Auto-detect |
|:---|:-----------|:------|:------------|
| 1 | Shall | Document structured into distinct tabs | Tab count >= 5 |
| 2 | Should | Latest template used | Low confidence draft |
| 3 | Should | Structure facilitates search (TOC, index) | Title tab in first 3 sheets |
| 4a | Shall | Title covers scope | Title detected |
| 4b | Shall | Author and Approver listed | Both populated |
| 4c | Shall | Unique revision identification | Revision field set |
| 4d | Shall | Change history available | Low confidence draft |
| 4e | Shall | Status of work product provided | Status field set |
| 5 | Shall | Current revision identifiable | Revision field set |
| 6 | Shall | Document under configuration management | Low confidence draft |
| 7 | Should | Header/footer updated | Low confidence draft |
| 8 | Shall | Table of Contents present | TOC or General Info tab detected |
| 9 | Should | Reference Table lists all references | Low confidence draft |
| 10 | Should | All sections completed | >= 95% of SR attributes populated |

**Rating scale:**
- **FC (Fully Compliant):** Evidence found in xlsx (count >= threshold, field populated).
- **LC (Largely Compliant):** Most checks pass; minor gaps.
- **PC (Partially Compliant):** Significant structure or metadata gaps.
- **NO (Not Compliant):** Critical field missing (Author, Status, Revision).
- **NA (Not Applicable):** Not applicable to this document.

## SW Safety Requirements Assessment (SWSRA) — ISO 26262-6 §6

SWSRA substantively assesses the derived SW-SR catalog against ISO 26262-6 Section 6 (Software Requirements Specification) requirements. Each check is machine-verifiable from the content of tabs:
- 02_SW_TSRs_From_TSC (parent requirements)
- 03_SW_Safety_Requirements (SR catalog)
- 04_Failure_Mode_Mapping, 05_HSI_Reference, 06_Verification_Methods_per_ASIL, 07_MISRA_Mapping, 08_Test_Strategy, 09_Independence_Considerations (supporting content)

| ID | Obligation | Check | Verification |
|:---|:-----------|:------|:------------|
| 1 | Shall | SW-TSRs successfully imported from TSC | Count > 0 in tab 02 |
| 2 | Shall | At least one SW-SR derived per SW-TSR (no orphans) | Unique parent_tsr values >= count(SW-TSRs) |
| 3 | Shall | ASIL assigned consistent with parent TSR | >= 99% of SW-SRs have asil field populated |
| 4 | Shall | Allocated SWC specified (no <TBD>) | >= 99% of SW-SRs have allocated_swc, not <TBD> |
| 5 | Shall | Requirement text present (no empty rows) | >= 99% of SW-SRs have text field |
| 6 | Shall | Target detection time specified | >= 99% of SW-SRs have target_detection_time |
| 7 | Shall | Failure mode mapping covers standard SW failure modes | Count >= 10 in tab 04 (deadline miss, illegal state, divide-by-zero, etc) |
| 8 | Shall | Each SW-SR has verification method | >= 99% of SW-SRs have verification_method field |
| 9 | Shall | Verification methods appropriate for ASIL (MC/DC for D) | Low confidence draft; reviewer verifies per ISO 26262-6 Tables 7-10 |
| 10 | Shall | Test strategy covers unit/integration/back-to-back/fault-injection | Count >= 6 in tab 08 with diverse test topics |
| 11 | Should | Independence considerations documented (if cascading) | Count > 0 in tab 09, or draft if not applicable |
| 12 | Should | MISRA C:2012 mapping present for safety-relevant SW-SRs | Count > 0 in tab 07, or draft if not applicable |

## Verification Assessment (VA) — External + SW-SR-specific

VA acknowledges that most verification checks (planning, execution, traceability) are external to the SW-SR specification; they belong in a separate Verification Plan and Report. Rows 24-32 are drafted as Pending, requiring manual verification against project docs.

Rows 33a-e are SW-SR-specific and machine-verifiable:

| ID | Obligation | Check | Verification |
|:---|:-----------|:------|:------------|
| 33a | Shall | Completeness of SW-SR coverage | Count(SW-SRs) >= 5 -> FC; > 0 -> LC; = 0 -> NO |
| 33b | Shall | Consistency of ASIL assignments | All SW-SRs have ASIL -> FC; none -> NO |
| 33c | Shall | Consistency with HSI specifications | Low confidence draft; reviewer verifies alignment |
| 33d | Shall | Completeness of SWC mapping | Count(distinct allocated_swc) > 0 -> FC; = 0 -> NO |
| 33e | Shall | Completeness of requirement attributes | >= 99% have (text, ASIL, SWC, detection_time) -> FC; else PC/NO |

## Confidence Model

Each CheckResult includes a **Confidence** field indicating how much trust to place in the auto-filled assessment:

| Confidence | Source | Example |
|:-----------|:--------|:--------|
| **High** | Directly counted from xlsx | "All 42 SW-SRs have ASIL" (regex match / count of populated cells) |
| **Medium** | Heuristic inference from xlsx | "Failure mode mapping covers 15 rows; reviewer confirm adequacy" (count is reliable, but interpretation may need human judgment) |
| **Low** | Subjective or external | "Verification methods appropriate for ASIL (reviewer verify per ISO 26262-6 Tables 7-10)" (requires domain judgment or cross-check against external docs) |
| **(blank)** | Pending | Row left for manual completion by reviewer |

**Draft convention:** Every Low-confidence finding starts with "(Auto-suggest, requires reviewer judgment)" so the reviewer immediately knows that human judgment is required.

## Output: 7-Tab Checklist Workbook

| Tab | Purpose | Audience |
|:---|:--------|:---------|
| **Title** | Document metadata (title, ID, revision, author, approver, project, linked TSC). Generated date, format detected. | Project stakeholders, audit trail |
| **General Info** | Checklist overview, tab guide, references (ISO 26262, TSC, sw-sr-builder) | Readers unfamiliar with structure |
| **Guide** | Legend: FC/LC/PC/NO/NA/Pending ratings; High/Medium/Low confidence; iteration workflow | Reviewers |
| **Summary** | Dashboard: KPI tiles (Total, Compliance%, Pending, Major Issues); pie chart (rating distribution); bar charts (compliance % by tab, rating breakdown by section); findings table (NO + PC items only) | Decision-makers, program leads |
| **Confirmation Review** | 14 CR checks, one row per check; Assessment (FC/LC/PC/NO/NA/''), Finding, Page Section, Recommended Action, Confidence | Document reviewer |
| **SWSRA** | 12 SWSRA checks, one row per check; same columns as CR tab | Requirements reviewer, safety engineer |
| **VA** | 22 VA checks (24-32 external, 33a-e SW-SR-specific); mostly Pending awaiting manual verification against Verification Plan | Verification lead |

## Iteration Workflow

1. **Initial run:** Generate checklist from SW-SR.xlsx
2. **Reviewer inspection:** Open Summary tab; read KPIs and findings. Walk CR/SWSRA/VA tabs; focus on NO and PC rows.
3. **Remediation decision:** For each NO/PC, decide:
   - If easy fix (missing author, status, etc.) → update source SW-SR.xlsx directly.
   - If gap in requirements → refactor SW-SR.xlsx in source workbook, re-run skill.
   - If external → note in Recommended Actions, verify later against Verification Plan.
4. **Re-run:** Once source SW-SR.xlsx updated, re-run skill to produce fresh checklist. (v0.1 does not preserve manual edits; keep old checklist for diff comparison.)
5. **Acceptance:** When Summary tab shows acceptable status (low NO, low PC, most CR/SWSRA/VA FC or LC), sign off in Title page Status field.

## Common Findings and Remediation

| Finding | Root Cause | Remediation |
|---------|-----------|-------------|
| "No title detected on Title page" (NO) | Title field missing or not detected | Add "Document Title" label + value on Title page |
| "Missing: Author, Approver" (NO) | Metadata incomplete | Populate Author and Approver fields on Title page |
| "Revision field not populated" (NO) | No revision ID | Assign revision (e.g., v0.1, v1.0) on Title page |
| "No HW-TSRs detected in TSR import tab" (NO) | SW-TSRs never imported from TSC | Import SW-TSRs from linked TSC workbook into tab 02 |
| "orphans / SW-TSRs lack derived SW-SRs" (PC) | Not all SW-TSRs have corresponding SW-SRs | Derive at least one SW-SR per orphaned SW-TSR in tab 03 |
| "SRs have ASIL" (PC) | Incomplete ASIL assignment | Ensure every SW-SR row has ASIL consistent with parent TSR |
| "No failure mode mapping rows detected" (NO) | Tab 04 is empty or missing | Create failure mode mapping for SW-relevant failures (deadline miss, illegal state, divide-by-zero) |
| "Test strategy has 2 rows" (LC) | Sparse test coverage | Expand tab 08 to cover unit, integration, back-to-back, fault-injection testing (goal: >= 6 rows) |

## Design Decisions

1. **Conservative ratings:** Every FC (Fully Compliant) requires direct evidence; every PC/NO cites specific gap.
2. **No source modification:** The skill never updates the input SW-SR.xlsx. Corrective actions are recommendations only.
3. **Standard checks:** The 38 checks are reusable across all SW-SR workbooks and follow ISO 26262-6 structure.
4. **Confidence separation:** Low-confidence findings are clearly marked; reviewers know where to apply judgment.
5. **Dashboard summary:** The Summary tab leads with KPIs and findings; reviewers don't need to read all 38 rows to understand status.
