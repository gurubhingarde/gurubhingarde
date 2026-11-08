---
name: odx-checklist-reviewer
description: Run a confirmation review on any ODX authoring xlsx and produce a completed checklist with visual dashboard plus auto-filled findings and recommended actions covering ~30 checks across Variant Definition, PDU Library, Service Definitions, Communication Parameters, Vehicle Information, Flash Data, and Inherit-From Relationships.
---

# ODX Checklist Reviewer

Runs an ISO 22901-1 confirmation review on any ODX authoring xlsx and produces a completed checklist with a visual dashboard.

## When to use this skill

- Review or audit an ODX workbook
- Verify variant hierarchy completeness
- Check PDU library coverage and signal definitions
- Validate service-to-PDU mappings
- Confirm communication parameter correctness
- Verify Flash Data memory layout
- Check for circular inheritance

## Workflow

1. Get the ODX xlsx path.
2. Read `references/methodology.md` and `references/odx_checks.md` on first use.
3. `python scripts/generate_checklist.py <odx.xlsx> <output_checklist.xlsx>`
4. Walk the user through the **Summary dashboard** first, then the per-tab review.
5. Iterate on findings.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | What ODX is being assessed |
| 2 | General Info | TOC of the checklist |
| 3 | Guide | Rating / confidence / obligation legend |
| 4 | Summary | Visual dashboard with KPI tiles, pie/bar charts, findings table |
| 5 | Variant & Layer Review | 8 variant definition checks |
| 6 | PDU & Service Review | 12 PDU library and service definition checks |
| 7 | Communication & Flash Review | 10 communication parameter and flash data checks |

## Files in this skill

```
odx-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── odx_probe.py
│   ├── check_definitions.py
│   ├── dashboard.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── odx_checks.md
```
