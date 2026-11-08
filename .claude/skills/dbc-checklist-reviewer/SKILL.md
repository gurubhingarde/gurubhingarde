---
name: dbc-checklist-reviewer
description: Run a confirmation-measures review on any DBC specification xlsx and produce a completed checklist with a visual dashboard (KPI tiles, pie chart, compliance bar chart, section breakdown) plus auto-filled findings and recommended actions. Probes the DBC content to verify message IDs are unique, signals fit within DLC, no bit overlap occurs, every signal has scale/offset/unit, multiplexors are defined, and every message has a sender. Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks; drafts low-confidence findings for subjective items. Does not modify the source DBC. Use whenever the user wants to review, audit, or confirm a DBC specification, even in casual phrasings like "check my CAN database". Always use this skill instead of a freeform review.
---

# DBC Checklist Reviewer

Runs an ISO 11898 confirmation review on any CAN Database (DBC) specification xlsx and produces a completed checklist with a visual dashboard. Pairs naturally with `dbc-builder` (which produces the artifact) but works on any DBC xlsx via best-effort probing.

## When to use this skill

- Review or audit a DBC specification workbook
- Verify signal encoding completeness and consistency
- Check message structure and signal allocation
- Validate multiplexing logic
- Confirm ECU and network topology
- Get a roll-up of DBC quality with charts and metrics

## Workflow

1. Get the DBC xlsx path.
2. Read `references/methodology.md` and `references/dbc_checks.md` on first use.
3. `python scripts/generate_checklist.py <dbc.xlsx> <output_checklist.xlsx>`
4. Walk the user through the **Summary dashboard** first, then the per-tab review.
5. Iterate.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | What DBC is being assessed |
| 2 | General Info | TOC of the checklist |
| 3 | Guide | Rating / confidence / obligation legend |
| 4 | Summary | Visual dashboard with KPI tiles, pie/bar/stacked-bar charts, findings table |
| 5 | Confirmation Review | 14 doc-quality checks |
| 6 | Technical DBC Assessment | 18 DBC substantive checks (ISO 11898 & AUTOSAR compliance) |
| 7 | Verification Assessment | 10 signal and message validation checks |

## Files in this skill

```
dbc-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── dbc_probe.py
│   ├── check_definitions.py
│   ├── dashboard.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── dbc_checks.md
```

## Rating Legend

- **FC** (Fully Conforming): Requirement met; high confidence from direct inspection.
- **LC** (Largely Conforming): Requirement mostly met; minor gaps or inferred from structure.
- **PC** (Partially Conforming): Requirement partially met; significant work remains.
- **NO** (Non-Conforming): Requirement not met; corrective action required.
- **NA** (Not Applicable): Requirement does not apply to this DBC (e.g., J1939 checks on standard CAN).

## Obligation Levels

- **Shall**: Mandatory per ISO 11898 or AUTOSAR spec. NO rating = major non-conformance.
- **Should**: Recommended best practice. LC or PC acceptable with justification.
