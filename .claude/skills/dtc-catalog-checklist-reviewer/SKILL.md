---
name: dtc-catalog-checklist-reviewer
description: Run a confirmation review on any DTC catalog xlsx and produce a completed checklist with a visual dashboard (KPI tiles, pie chart, compliance bar chart) plus auto-filled findings and recommended actions. Probes DTC content, runs 30 checks across code uniqueness, fault type alignment, status masks, debounce/healing completeness, OBD-II readiness mapping per ISO 14229-1 and SAE J2012. Auto-fills FC, LC, PC, NO, or NA ratings. Does not modify source DTC catalog. Use whenever the user wants to review, audit, or confirm a DTC catalog, even casual phrasings like 'check my DTC catalog'.
---

# DTC Catalog Checklist Reviewer

Runs an ISO 14229-1 and SAE J2012 confirmation review on any DTC catalog xlsx and produces a completed checklist with a visual dashboard.

## When to use this skill

- Review or audit a DTC catalog workbook
- Run a confirmation-measures assessment
- Check DTC code uniqueness and fault-type alignment
- Verify debounce algorithm and healing logic coverage
- Confirm OBD-II mapping and readiness monitor assignment
- Get a roll-up of DTC catalog quality with charts and metrics

## Workflow

1. Get the DTC catalog xlsx path.
2. Read `references/methodology.md` and `references/dtc_checks.md` on first use.
3. `python scripts/generate_checklist.py <dtc_catalog.xlsx> <output_checklist.xlsx>`
4. Walk the user through the **Summary dashboard** first, then the per-section review.
5. Iterate.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | DTC catalog being assessed |
| 2 | General Info | TOC of the checklist |
| 3 | Guide | Rating / confidence / obligation legend |
| 4 | Summary | Visual dashboard with KPI tiles, pie/bar charts, findings table |
| 5 | Confirmation Review | 10 doc-quality checks |
| 6 | DTC Assessment | 15 substantive DTC checks (ISO 14229-1 + SAE J2012) |
| 7 | OBD Assessment | 5 OBD-II mapping checks |

## Files in this skill

```
dtc-catalog-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── dtc_probe.py
│   ├── check_definitions.py
│   ├── dashboard.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── dtc_checks.md
```
