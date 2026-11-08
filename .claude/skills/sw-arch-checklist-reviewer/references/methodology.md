# SW Architecture Checklist Methodology

## Overview

This document describes the assessment methodology, check categories, and scoring conventions used by the sw-arch-checklist-reviewer skill.

## Check Categories

The checklist is organized into three categories aligned with ISO 26262:

### 1. Confirmation Review (CR) — 14 Checks
ISO 26262-8 §10 document quality checks. These are generic and applicable to any engineering artifact: title page hygiene, author/approver identification, document control, structure, references, formatting consistency.

**Example CR checks:**
- CR-01: Document is structured into distinct sections
- CR-03: Author and Approver identified
- CR-06: Document ID and Project specified
- CR-12: Cross-references to TSC present

These checks focus on *form* rather than *substance*. A document can fail CR due to missing metadata, even if the technical content is sound.

### 2. SW Architecture Assessment (SWAA) — 12 Checks
ISO 26262-6 §7 substantive architectural checks specific to Software Architecture. These assess:
- Component definition (catalog, ASIL assignment, partition mapping)
- RTOS/OS configuration (name, version, scheduling policy, ASIL support)
- Task scheduling (period, priority, WCET, schedulability)
- Memory protection (MPU regions, partitioning strategy)
- Inter-component communication (interfaces, integrity protection)
- Safety mechanisms (allocation per ASIL)
- MISRA C:2012 compliance targets
- Initialization sequence
- TSC integration

**Example SWAA checks:**
- SWAA-01: SW Component Catalog populated
- SWAA-02: Each SW component has ASIL assigned
- SWAA-05: Task scheduling map includes WCET
- SWAA-06: Schedulability verified (sum(WCET/Period) < 1.0)
- SWAA-08: Inter-component interfaces have integrity protection

SWAA checks are *machine-verifiable* where data is present in the xlsx; subjective checks are drafted for reviewer judgment.

### 3. Verification Assessment (VA) — 5 Checks
ISO 26262-8 §9 verification checks, mostly external to the architecture artifact. These reference Verification Plans, Test Specifications, Test Reports.

**Example VA checks:**
- VA-01: Verification Plan covers all SW components with SW-TSR traceability
- VA-02: MPU isolation verified for all ASIL-relevant partitions
- VA-03: Task scheduling and priority inversion handling tested
- VA-04: All inter-component interfaces have integration test coverage
- VA-05: MISRA C:2012 compliance verified or waived per component

Most VA checks are marked Pending; the reviewer verifies them against external project artifacts.

## Rating Scheme

Each check receives one of six ratings:

| Rating | Hex Code | Meaning | Confidence |
|--------|----------|---------|------------|
| **FC** (Fully Compliant) | `70AD47` (green) | Requirement met; specific evidence cited; audit-ready. | High |
| **LC** (Low Confidence) | `9DC3E6` (light blue) | Requirement met but confidence is limited; reviewer judgment helpful. | Medium |
| **PC** (Partially Compliant) | `FFC000` (orange) | Requirement partially met; gaps identified; corrective action recommended. | High |
| **NO** (Non-Compliant) | `C00000` (red) | Requirement not met; significant gap; corrective action required. | High |
| **NA** (Not Applicable) | `BFBFBF` (grey) | Requirement does not apply to this artifact or context. | High |
| **(empty)** | n/a | Pending — reviewer to assess. | Low |

## Confidence Levels

Confidence indicates how much the rating relies on direct data vs. inference vs. external verification:

### High Confidence
Checks marked "High" have been directly verified against xlsx content. Examples:
- "Author field populated: John Smith" (direct read from Title page)
- "SW Component Catalog has 15 components" (direct count from sheet)
- "All components have ASIL assigned" (verified by iteration)

### Medium Confidence
Checks marked "Medium" are inferred from xlsx data but require reviewer judgment. Examples:
- "RTOS configuration documented as VxWorks 7.0; reviewer to verify scheduling policy matches requirements"
- "Task WCET defined; reviewer to verify schedulability analysis performed"

### Low Confidence
Checks marked "Low" are subjective or depend on external artifacts. Examples:
- "(Auto-suggest, requires reviewer judgment) Reviewer to verify MPU isolation testing documented in Verification Plan."
- "(Auto-suggest, requires reviewer judgment) Reviewer to assess independence of Author vs. Approver per ISO 26262-2."

Low-confidence findings always begin with the phrase *"(Auto-suggest, requires reviewer judgment)"* so the reviewer immediately knows manual review is needed.

## Obligation Hierarchy

Each check is tagged with an obligation level:

- **Shall** — Normative requirement; non-compliance is a defect.
- **Should** — Recommended best practice; deviation requires justification.
- **(blank)** — Informational or context-dependent.

## Scoring Example

**SW Component Catalog**

- **Check SWAA-01:** "SW Component Catalog shall be populated with all SW components"
- **Data:** xlsx tab "03_SW_Component_Catalog" contains 23 rows (23 components)
- **Rating:** FC (Fully Compliant)
- **Finding:** "SW Component Catalog populated with 23 components."
- **Confidence:** High
- **Obligation:** Shall
- **Recommended Action:** (empty — no action needed)

---

**ASIL Assignment**

- **Check SWAA-02:** "Each SW component shall have ASIL assigned"
- **Data:** Iteration of 23 components reveals 2 components missing ASIL column value
- **Rating:** NO (Non-Compliant)
- **Finding:** "2 SW component(s) missing ASIL: SWC-008, SWC-015."
- **Confidence:** High
- **Obligation:** Shall
- **Recommended Action:** "Assign ASIL (QM / ASIL A/B/C/D) to all safety-relevant components."

---

**Schedulability**

- **Check SWAA-06:** "Schedulability analysis shall confirm sum(WCET/Period) < 1.0 per priority"
- **Data:** Task Scheduling Map has 8 tasks with WCET and Period populated; no explicit schedulability analysis result in xlsx
- **Rating:** (pending)
- **Finding:** "(Auto-suggest, requires reviewer judgment) Reviewer to verify rate-monotonic schedulability: sum(WCET/Period) < 1.0 per priority. 8 task(s) defined."
- **Confidence:** Low
- **Obligation:** Shall
- **Recommended Action:** "Complete WCET and Period for all tasks; run schedulability analysis."

## Summary Statistics

The Summary tab aggregates all ratings across all three check categories:

- **Total Checks:** Sum of all CR, SWAA, VA checks run (typically 31)
- **Compliant %:** (FC + LC) / Total
- **Major Issues:** NO + PC (requires corrective action)
- **Pending:** Empty ratings (reviewer to assess)
- **Not Applicable:** NA (by context)

Pie chart shows distribution of FC / LC / PC / NO / NA / Pending.

Bar charts per checklist tab show compliance percentage.

## Iteration Workflow

1. **Initial Review:** Run skill on source SW Architecture xlsx. Most CR and SWAA checks auto-fill; most VA checks draft.
2. **Remediation:** Reviewer identifies NO and PC items. Analyzes Recommended Actions. Decides whether to:
   - Update source SW Architecture and re-run skill, OR
   - Close item as "accepted risk" or "future work" in Recommended Action column
3. **Re-run:** Skill generates fresh checklist. Previous checklist retained for diff comparison.
4. **Iterate:** Repeat until all CR and SWAA items are FC or NA. VA items typically remain Pending until Verification Plan/Report available.

## Use in Audit

The checklist workbook is audit-ready once:
- All CR items are FC or NA
- All SWAA items are FC, LC, or NA
- All PC items have documented mitigation in Recommended Action
- All VA items have external evidence reference or are marked LC/Pending with clear justification
- Reviewer is identified (independence per ISO 26262-2)
- Review date and sign-off present
