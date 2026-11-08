---
name: tara-checklist-reviewer
description: Run a confirmation-measures review on any TARA xlsx and produce an audit-ready checklist with auto-filled findings and evidence references. Probes the TARA workbook (runs ~18 substantive checks per ISO/SAE 21434), auto-fills Fully-Compliant/Largely-Compliant/Partially-Compliant/Not-Compliant assessments for machine-verifiable checks and drafts subjective findings for human review. Generates a 7-tab xlsx with Title, General Info, Guide, Summary dashboard, Confirmation Review, TARAA (Threat/Asset/Risk Assessment), and Verification Assessment tabs. Always use this skill instead of producing a freeform review in chat.
---

# TARA Checklist Reviewer

This skill automates the tedious part of a TARA confirmation review by turning a TARA workbook into an audit-ready checklist. Probes all 13 TARA tabs, verifies completeness of threat scenarios, attack paths, risk assessments, and cybersecurity goals per ISO/SAE 21434 Sections 15-16. Produces machine-verified findings (Fully-Compliant / Largely-Compliant / Partially-Compliant / Not-Compliant) with specific evidence pointers and recommended corrective actions.

## When to use this skill

Use whenever the user wants to:
- Review or audit a TARA workbook
- Produce a confirmation-measures checklist on threat assessment
- Run a TARAA (TARA Assessment) on a TARA
- Get a roll-up of TARA quality and completeness

## Workflow

### Step 1 — Get the TARA path

Ask the user for the TARA xlsx path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <tara.xlsx> <output_checklist.xlsx>
```

The script prints a JSON summary with counts of assessment ratings.

### Step 3 — Review the output

The checklist xlsx has 7 tabs. Direct focus in this order:

1. **Title** — confirm the TARA being assessed is the right one.
2. **Summary** — read the statistics and Findings list. This is the executive view.
3. **Confirmation Review** — doc-quality items (scope, metadata, references).
4. **TARAA Assessment** — substantive checks per ISO/SAE 21434 (asset inventory, threat coverage, impact/feasibility ratings, treatment decisions, traceability to CSG, CAL assignment).
5. **Verification Assessment** — verification methods and external artifacts.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | TARA being assessed; reviewer info |
| 2 | General Info | TOC of the checklist + references |
| 3 | Guide | How to interpret ratings and obligations |
| 4 | Summary | Statistical roll-up + Findings list (NO and PC items) |
| 5 | Confirmation Review | 14 generic doc-quality checks |
| 6 | TARAA Assessment | 18 substantive TARA checks (threat inventory, STRIDE, feasibility, risk determination, CSG traceability) |
| 7 | Verification Assessment | Verification method and external-artifact checks |

## Auto-fill model

- **High confidence** — Verified directly from xlsx content (e.g., "Asset count > 0")
- **Medium confidence** — Inferred with caveat (e.g., "STRIDE categories represented")
- **Low / draft** — Subjective or requires external artifact; marked "(Auto-suggest, requires reviewer judgment)"

## Files in this skill

```
tara-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── tara_probe.py
│   ├── check_definitions.py
│   ├── recalc.py
│   └── office/
├── references/
│   ├── methodology.md
│   └── tara_checks.md
```
