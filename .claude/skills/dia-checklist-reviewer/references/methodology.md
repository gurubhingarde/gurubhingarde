# DIA Checklist Reviewer — Methodology & Scoring Conventions

## Overview

The DIA Checklist Reviewer probes a Design Interface Agreement (DIA) xlsx and runs 33 standard checks organized into three tabs:

1. **Confirmation Review (CR)** — 14 generic document-quality checks per ISO 26262-8 Section 10
2. **DIA Assessment (DIAA)** — 14 substantive agreement checks per ISO 26262-8 Section 5
3. **Verification Assessment (VA)** — 5 external governance and verification checks

The skill uses a conservative verification model: it only assigns a Fully Compliant (FC) or Largely Compliant (LC) rating when it can directly verify evidence in the xlsx. Subjective checks are drafted as Low-confidence findings marked "(Auto-suggest, requires reviewer judgment)" so the human knows exactly where their judgment is needed.

## Rating Scale

| Rating | Meaning | When Used |
|--------|---------|-----------|
| **FC** | Fully Compliant | Requirement is met; evidence found in the DIA xlsx. |
| **LC** | Largely Compliant | Requirement is mostly met; minor gaps or incomplete entries. |
| **PC** | Partially Compliant | Requirement is partially met; significant gaps or missing entries. |
| **NO** | Not Compliant | Requirement is not met; corrective action required. |
| **NA** | Not Applicable | Requirement does not apply to this DIA (e.g., Tool Sharing if no tools are shared). |
| **(blank)** | Pending | Requires reviewer judgment; finding is auto-drafted with Low confidence. |

## Confidence Levels

| Confidence | Definition | Examples |
|------------|-----------|----------|
| **High** | Evidence directly verified from xlsx content; no inference required. | "Author field populated"; "All 4 parties have FuSa contact"; "RACI has exactly one A per WP". |
| **Medium** | Inferred from xlsx with reasonable caveat; some human judgment involved. | "Operating environment tab present; reviewer to confirm completeness against Item Def". |
| **Low** | Subjective check or requires external artifact (Verification Plan, governance docs, meeting notes). | "Communication protocol text present; reviewer to confirm cadence and escalation are workable". |

## Obligation vs Assessment

- **Obligation column** shows whether the check is a **Shall** (mandatory) or **Should** (recommended) requirement from the standard.
- **Assessment column** shows your evaluation: FC / LC / PC / NO / NA / pending.
- A **NO** on a **Shall** item is a major non-conformance.
- A **NO** on a **Should** item is a minor non-conformance.

The Summary dashboard automatically counts major vs minor issues and determines overall acceptance status.

## DIA Assessment Checks — Highest Value (Items 1–6)

The most critical checks for a DIA are the party/RACI/responsibility checks:

1. **All parties identified with role** — Are OEM, Tier-1, Tier-2, IC suppliers all present? Do they have roles?
2. **Each party has FuSa contact** — Not just a commercial contact; a designated functional safety point.
3. **RACI matrix covers major WPs** — Minimum: HARA, Item Def, FSC, TSC, Safety Case.
4. **Exactly one A per WP** — No double-assignment or missing Accountable.
5. **At least one R per WP** — No work product is un-owned.
6. **No completely empty WP rows** — Every work product has at least one RACI assignment.

These six checks catch the most common DIA gaps: incomplete party lists, missing FuSa contacts, and broken RACI matrices. A DIA with any NO on these items is not acceptable.

## Common No/PC Findings and Recommended Actions

| Check | Common NO | Recommended Action |
|-------|-----------|-------------------|
| Parties (1) | "Only 1 party identified" | Add all parties (OEM, suppliers, IC vendors) to the Parties tab. |
| FuSa Contact (2) | "3 parties missing FuSa contact" | Add functional safety contact name/role in the FuSa Contact column. |
| RACI Coverage (3) | "RACI covers only 3/7 major WPs" | Add RACI rows for FSC, TSC, FMEDA, Software Requirements. |
| Accountable (4) | "FSC WP has 0 Accountable" | Assign exactly one party as Accountable (A) for each work product. |
| Responsible (5) | "Item Definition WP has no R" | Assign at least one party as Responsible (R) for each work product. |
| Communication (7) | "No Communication Protocol tab" | Create 05_Communication_Protocol tab; define channels, cadence, escalation. |
| Supplier Deliverables (9) | "Only format field; missing criteria" | Add language, planned date, and acceptance criteria to each deliverable. |

## Recommendation for Use

1. **Run the skill** on a complete dia-builder output.
2. **Focus on the Summary tab** — read the KPI tiles and Findings table (NO and PC items).
3. **Drill into DIAA Assessment tab** — items 1–6 are critical; items 7–14 are important but less showstopping.
4. **For each NO**, update the source DIA and re-run.
5. **For each Pending**, apply reviewer judgment (read the "(Auto-suggest)" comment, check the Page/Section, decide Yes/No/Maybe).
6. **When all Shall items are FC and major issues are zero**, acceptance can be granted.

## What This Skill Does NOT Do

- **Does not modify the source DIA.** All corrective actions are suggestions in the Recommended Actions column.
- **Does not replace an independent review.** ISO 26262-2 requires an independent reviewer (I1/I2/I3 per ASIL).
- **Does not verify external artifacts** (Verification Plan, governance meeting minutes, tool qualification docs).
- **Does not grade overall "pass/fail".** It flags issues; the reviewer decides acceptance.

## What This Skill DOES Do

- **Extracts and validates** party lists, roles, FuSa contacts, scope, RACI matrix, communication protocol, joint review schedule, supplier deliverables, change process, tool sharing, confidentiality terms.
- **Runs 33 checks** with machine-verifiable logic on ~20 of them.
- **Auto-fills ratings** for checks that can be verified from xlsx content (High confidence).
- **Drafts findings** for subjective checks, marked Low confidence so the reviewer knows they need judgment.
- **Produces a roll-up** with KPI dashboard, pie chart of rating distribution, compliance % by tab, Findings table.
- **Generates recommendations** for every NO/PC item.
