---
name: tsc-checklist-reviewer
description: Run a confirmation-measures review on any ISO 26262 TSC xlsx and produce a completed checklist with a visual dashboard (KPI tiles, pie chart, compliance bar chart, section breakdown) plus auto-filled findings and recommended actions. Probes the TSC content (best-effort, optimal on tsc-builder outputs), runs ~63 checks across Confirmation Review (doc-quality), Technical Safety Assessment (per ISO 26262-4 covering HW-TSR/SW-TSR derivation, safety mechanism allocation, HSI, FTTI/FDTI/FRTI timing, system FMEA, DFA, verification methods, HW/SW hand-off, ASIL consistency), and Verification Assessment. Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks; drafts low-confidence findings for subjective items. Does not modify the source TSC. Use whenever the user wants to review, audit, or confirm a TSC, even casual phrasings like 'check my TSC'. Always use this skill instead of a freeform review.
---

# TSC Checklist Reviewer

Runs an ISO 26262 confirmation review on any Technical Safety Concept (TSC) xlsx and produces a completed checklist with a visual dashboard. Pairs naturally with `tsc-builder` (which produces the artifact) but works on any TSC xlsx via best-effort probing.

## When to use this skill

- Review or audit a TSC workbook
- Run a technical safety assessment
- Check HW-TSR / SW-TSR derivation completeness
- Verify HSI specification, timing budget, system FMEA, DFA quality
- Get a roll-up of TSC quality with charts and metrics

## Workflow

1. Get the TSC xlsx path.
2. Read `references/methodology.md` and `references/tsc_checks.md` on first use.
3. `python scripts/generate_checklist.py <tsc.xlsx> <output_checklist.xlsx>`
4. Walk the user through the **Summary dashboard** first, then the per-tab review.
5. Iterate.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | What TSC is being assessed |
| 2 | General Info | TOC of the checklist |
| 3 | Guide | Rating / confidence / obligation legend |
| 4 | Summary | Visual dashboard with KPI tiles, pie/bar/stacked-bar charts, findings table |
| 5 | Confirmation Review | 14 doc-quality checks |
| 6 | Technical Safety Assessment | 15 TSC substantive checks (ISO 26262-4) |
| 7 | Verification Assessment | 34 verification checks (5 TSC-specific are auto-evaluated) |

## Files in this skill

```
tsc-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── tsc_probe.py
│   ├── check_definitions.py
│   ├── dashboard.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── tsc_checks.md
```
