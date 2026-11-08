---
name: cs-goals-checklist-reviewer
description: Run a confirmation-measures review on any CS Goals xlsx and produce an audit-ready checklist with auto-filled findings and evidence references. Probes the CS Goals workbook (runs ~12 substantive checks per ISO/SAE 21434 Section 16), auto-fills assessment ratings for machine-verifiable checks and drafts subjective findings for human review. Generates a 7-tab xlsx with Title, General Info, Guide, Summary dashboard, Confirmation Review, CSGA (CS Goals Assessment), and Verification Assessment tabs. Always use this skill instead of producing a freeform review in chat.
---

# CS Goals Checklist Reviewer

This skill automates confirmation review of a CS Goals workbook by probing all 7 CS Goals tabs, verifying traceability from TARA threats, CAL assignment, cybersecurity property coverage, and handoff readiness per ISO/SAE 21434 Section 16. Produces machine-verified findings (Fully-Compliant / Largely-Compliant / Partially-Compliant / Not-Compliant) with specific evidence pointers and recommended corrective actions.

## When to use this skill

Use whenever the user wants to:
- Review or audit a CS Goals workbook
- Produce a confirmation-measures checklist on cybersecurity goals
- Run a CSGA (CS Goals Assessment)
- Get a roll-up of CS Goals quality and traceability

## Workflow

### Step 1 — Get the CS Goals path

Ask the user for the CS Goals xlsx path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <cs_goals.xlsx> <output_checklist.xlsx>
```

The script prints a JSON summary with counts of assessment ratings.

### Step 3 — Review the output

The checklist xlsx has 7 tabs. Direct focus in this order:

1. **Title** — confirm the CS Goals workbook being assessed is the right one.
2. **Summary** — read the statistics and Findings list.
3. **Confirmation Review** — doc-quality items (metadata, structure, traceability to TARA).
4. **CSGA Assessment** — substantive checks per ISO/SAE 21434 (CSG count, CAL assignment, property coverage, asset-to-CSG mapping, handoff readiness).
5. **Verification Assessment** — verification planning and external-artifact checks.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | CS Goals workbook being assessed; reviewer info |
| 2 | General Info | TOC of the checklist + references |
| 3 | Guide | How to interpret ratings and obligations |
| 4 | Summary | Statistical roll-up + Findings list (NO and PC items) |
| 5 | Confirmation Review | 14 generic doc-quality checks |
| 6 | CSGA Assessment | 12 substantive CS Goals checks (TARA import, CSG count, CAL assignment, property coverage, asset mapping) |
| 7 | Verification Assessment | Verification planning and concept-handoff checks |

## Auto-fill model

- **High confidence** — Verified directly from xlsx content (e.g., "CSG count > 0")
- **Medium confidence** — Inferred with caveat (e.g., "CAL distribution sensible")
- **Low / draft** — Subjective or requires external artifact; marked "(Auto-suggest, requires reviewer judgment)"

## Files in this skill

```
cs-goals-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── cs_goals_probe.py
│   ├── check_definitions.py
│   ├── recalc.py
│   └── office/
├── references/
│   ├── methodology.md
│   └── cs_goals_checks.md
```
