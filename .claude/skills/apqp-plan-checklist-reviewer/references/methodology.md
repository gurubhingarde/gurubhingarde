# APQP Plan Checklist Reviewer — Methodology

## Overview

This document explains the scoring conventions, confidence levels, and design philosophy of the APQP Plan Checklist Reviewer skill.

## Scoring Ratings

| Rating | Meaning | When to assign |
|--------|---------|----------------|
| **FC** | Fully Compliant | Requirement met; evidence found in APQP Plan; no gaps. |
| **LC** | Largely Compliant | Requirement mostly met; minor gaps or partial completion (80%+). |
| **PC** | Partially Compliant | Requirement partially met; significant gaps (20-80%); corrective action recommended. |
| **NO** | Not Compliant | Requirement not met; critical gap; must be addressed. |
| **NA** | Not Applicable | Requirement does not apply to this APQP Plan (e.g., no special characteristics = NA on SC list). |
| **(blank)** | Pending Review | Subjective or external check awaiting human judgment. |

### Obligation context

- **Shall**: Mandatory requirement per AIAG APQP Manual or IATF 16949. NO rating on Shall = major issue; PC on Shall = conditional approval.
- **Should**: Recommended best practice. NO or PC on Should = minor non-conformance.

## Confidence Levels

| Level | Definition | Examples |
|-------|-----------|----------|
| **High** | Evidence directly verified from xlsx content | "Author field populated"; "All 5 gates scheduled"; "Risk Register has 8 items" |
| **Medium** | Inferred from xlsx with caveat or assumptions | "Phase deliverables present; reviewer to confirm completeness against scope" |
| **Low** | Subjective interpretation or requires external document | "Title covers scope" (requires reading); "PPL analysis complete" (external document required) |

## What this skill does

1. **Content extraction (probe)**: Best-effort extraction of APQP Plan structure, metadata, team, phases, deliverables, gates, risks, special characteristics, open items.
2. **Verification logic**: Runs 32 canonical checks against the probed content:
   - 14 Confirmation Review (doc-quality per ISO standards conventions)
   - 12 APQP Assessment (per AIAG APQP Manual + IATF 16949 requirements)
   - 6 Verification Assessment (external launch/readiness checks)
3. **Checklist generation**: Produces a 7-tab xlsx with findings, recommendations, and visual dashboard.
4. **Evidence citation**: Every FC/LC/PC/NO rating cites where in the source APQP Plan the evidence (or gap) was found.

## What this skill does NOT do

1. **Does not modify the source APQP Plan**. The skill is read-only; all recommendations land in the checklist only.
2. **Does not make organizational decisions**. Pending/subjective items require human judgment (e.g., "does the title adequately cover scope?" is a human decision).
3. **Does not verify external artifacts**. All Verification Assessment checks (PPL, supplier capability, customer approval, etc.) are marked as external; the reviewer must verify these against project documents.
4. **Does not enforce audit independence**. The skill outputs confidence levels; organizational policy determines which independence level (I1/I2/I3) is required for the review itself.

## Confidence Model and Auto-fill Strategy

The skill auto-fills High/Medium confidence checks with machine-verifiable ratings (FC/LC/PC/NO). Low-confidence checks are drafted as pending findings with a "(Auto-suggest, requires reviewer judgment)" preface.

### Example: Phase 1 Deliverables Complete

**Check**: "Is Phase 1 planning complete (VOC, business case, customer requirements, preliminary BOM)?"

- **Probe**: Extract all deliverables from Phase 1 tab; count how many match expected keywords.
- **High confidence**: If all 4 expected items found → **FC** ("Phase 1 has 4 deliverables including VOC, requirements, preliminary BOM").
- **Medium confidence**: If 2-3 items found → **LC** ("Phase 1 has 3 deliverables; some expected items may be missing").
- **Low confidence**: If fewer than 2 → **PC** ("Phase 1 incomplete: only 1 deliverable").

### Example: Title Covers Scope

**Check**: "Does the APQP Plan title reflect scope and content?"

- **Probe**: Extract title text.
- **Output**: Always **PENDING** (draft) — "Title is '{title}'. Reviewer to confirm it reflects APQP scope." This requires a human to read and judge.

## Tab Organization

| Tab | Role | Auto-fill rate |
|-----|------|-----------------|
| Confirmation Review | Document quality; structure; version control | ~70% (mostly objective) |
| APQP Assessment | Substantive plan completeness; phase deliverables; team; risk mgmt | ~80% (objective data extraction) |
| Verification Assessment | External launch readiness; supplier capability; customer approval | ~0% (all external; all pending) |

## Iteration and Remediation Workflow

1. **Initial review**: Run the skill on the source APQP Plan. Checklist shows gaps (NO, PC, PENDING).
2. **Triage**: User reads Summary tab; identifies major issues (NO + Shall = must-fix).
3. **Remediate**: User updates source APQP Plan (add deliverables, assign owners, define gates, etc.).
4. **Re-run**: User runs the skill again on updated APQP Plan.
5. **Verify**: Skill produces fresh checklist; gaps are now resolved or refined.

**Note**: The skill does NOT preserve manual edits from the previous checklist. Each run is a fresh generation from the current APQP Plan state.

## Integration with APQP Lifecycle

This skill fits into the broader APQP workflow:

- **apqp-plan-builder**: Creates the APQP Plan (phases, gates, deliverables, team).
- **apqp-plan-checklist-reviewer** (this skill): Audits and confirms the plan against AIAG + IATF standards.
- **dfmea-builder, pfmea-builder**: Build the Design and Process FMEAs referenced in Phase 2 and Phase 3.
- **control-plan-builder**: Builds the Control Plan referenced in Phase 3.
- **ppap-package-builder**: Builds the PPAP submission package (Phase 4).

## References

- **AIAG APQP Manual** — Advanced Product Quality Planning, latest edition.
- **IATF 16949:2016** — Automotive Quality Management System standard.
- **apqp_checks.md** — Detailed rationale for each of the 32 checks.
