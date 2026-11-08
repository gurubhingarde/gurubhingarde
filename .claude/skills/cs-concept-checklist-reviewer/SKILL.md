---
name: cs-concept-checklist-reviewer
description: Run a confirmation-measures review on any CS Concept xlsx and produce an audit-ready checklist. Probes the CS Concept workbook (runs ~14 substantive checks per ISO/SAE 21434 Section 9), auto-fills assessment ratings for machine-verifiable checks and drafts subjective findings. Generates 7-tab xlsx with Title, General Info, Guide, Summary dashboard, Confirmation Review, CSCA (CS Concept Assessment), and Verification Assessment tabs. Always use this skill instead of producing a freeform review in chat.
---

# CS Concept Checklist Reviewer

Automates confirmation review of CS Concept workbooks per ISO/SAE 21434 Section 9. Verifies CS Goals import, block diagram enumeration, CS Concept Argument derivation trees, CSR catalog coverage, CAL allocation, verification-method specification, and CSI Handoff readiness. Produces machine-verified findings with evidence pointers and corrective actions.

## When to use this skill

Use whenever the user wants to:
- Review or audit a CS Concept workbook
- Produce a confirmation-measures checklist on cybersecurity concept
- Run a CSCA (CS Concept Assessment)
- Get a roll-up of CS Concept quality and completeness

## Workflow

### Step 1 — Get the CS Concept path

Ask the user for the CS Concept xlsx path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <cs_concept.xlsx> <output_checklist.xlsx>
```

### Step 3 — Review the output

The checklist xlsx has 7 tabs. Direct focus in order:

1. **Title** — confirm the CS Concept workbook is correct.
2. **Summary** — read statistics and Findings list.
3. **Confirmation Review** — doc-quality items.
4. **CSCA Assessment** — substantive checks (block diagram, CSR catalog, verification methods, CAL allocation).
5. **Verification Assessment** — CSI Handoff and test planning.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | CS Concept workbook; reviewer info |
| 2 | General Info | TOC |
| 3 | Guide | How to interpret ratings |
| 4 | Summary | Statistical roll-up + Findings list |
| 5 | Confirmation Review | 14 doc-quality checks |
| 6 | CSCA Assessment | 14 substantive CS Concept checks |
| 7 | Verification Assessment | Verification and CSI Handoff checks |

## Auto-fill model

- **High confidence** — Direct xlsx verification
- **Medium confidence** — Inferred with caveat
- **Low / draft** — Subjective or external artifact

## Files in this skill

```
cs-concept-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── cs_concept_probe.py
│   ├── check_definitions.py
│   ├── recalc.py
│   └── office/
├── references/
│   ├── methodology.md
│   └── cs_concept_checks.md
```
