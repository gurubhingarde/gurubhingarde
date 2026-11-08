---
name: cdd-checklist-reviewer
description: Run a confirmation review on any CDD (CANdela Diagnostic Description) xlsx and produce a completed checklist with a visual dashboard (KPI tiles, pie chart, compliance bar chart) plus auto-filled findings and recommended actions. Probes CDD content, runs 28 checks across variant consistency, DID coverage, service alignment, security pairing, DTC cross-reference per ISO 14229-1 and Vector CANdela conventions. Auto-fills FC, LC, PC, NO, or NA ratings. Does not modify source CDD. Use whenever the user wants to review, audit, or confirm a CDD workbook, even casual phrasings like 'check my CDD'.
---

# CDD Checklist Reviewer

Runs an ISO 14229-1 and Vector CANdela confirmation review on any CDD xlsx and produces a completed checklist with a visual dashboard.

## When to use this skill

- Review or audit a CDD authoring workbook
- Run a confirmation-measures assessment
- Check variant coding consistency and inheritance
- Verify DID coverage and service alignment
- Confirm security access level pairing (request-seed, send-key)
- Validate DTC cross-reference completeness
- Get a roll-up of CDD quality with charts and metrics

## Workflow

1. Get the CDD xlsx path.
2. Read `references/methodology.md` and `references/cdd_checks.md` on first use.
3. `python scripts/generate_checklist.py <cdd.xlsx> <output_checklist.xlsx>`
4. Walk the user through the **Summary dashboard** first, then the per-section review.
5. Iterate.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | CDD being assessed |
| 2 | General Info | TOC of the checklist |
| 3 | Guide | Rating / confidence / obligation legend |
| 4 | Summary | Visual dashboard with KPI tiles, pie/bar charts, findings table |
| 5 | Confirmation Review | 10 doc-quality checks |
| 6 | CDD Assessment | 12 substantive CDD checks (ISO 14229-1 + Vector conventions) |
| 7 | Variant Assessment | 6 variant coding and inheritance checks |

## Files in this skill

```
cdd-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── cdd_probe.py
│   ├── check_definitions.py
│   ├── dashboard.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── cdd_checks.md
```
