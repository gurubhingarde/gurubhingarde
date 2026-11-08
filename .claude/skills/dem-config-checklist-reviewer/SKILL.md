---
name: dem-config-checklist-reviewer
description: Run a confirmation review on any DEM (Diagnostic Event Manager) configuration xlsx and produce a completed checklist with visual dashboard plus auto-filled findings and recommended actions covering ~28 checks across Event Configuration, Debounce Algorithms, Memory Allocation, Snapshot Records, NvM Storage, and OBD Freeze Frame Layout.
---

# DEM Config Checklist Reviewer

Runs an AUTOSAR SWS_Dem confirmation review on any DEM configuration xlsx and produces a completed checklist with a visual dashboard.

## When to use this skill

- Review or audit a DEM configuration workbook
- Verify debounce threshold appropriateness
- Check memory allocation vs. event count
- Validate NvM block mapping
- Verify snapshot and EDR record coverage
- Confirm OBD freeze frame configuration
- Check for DTC-to-event mapping completeness

## Workflow

1. Get the DEM config xlsx path.
2. Read `references/methodology.md` and `references/dem_checks.md` on first use.
3. `python scripts/generate_checklist.py <dem_config.xlsx> <output_checklist.xlsx>`
4. Walk the user through the **Summary dashboard** first, then the per-tab review.
5. Iterate on findings.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | What DEM config is being assessed |
| 2 | General Info | TOC of the checklist |
| 3 | Guide | Rating / confidence / obligation legend |
| 4 | Summary | Visual dashboard with KPI tiles, pie/bar charts, findings table |
| 5 | Event & Debounce Review | 10 event and debounce configuration checks |
| 6 | Memory & Storage Review | 10 memory and NvM mapping checks |
| 7 | Snapshot & OBD Review | 8 snapshot, EDR, and OBD freeze frame checks |

## Files in this skill

```
dem-config-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── dem_probe.py
│   ├── check_definitions.py
│   ├── dashboard.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── dem_checks.md
```
