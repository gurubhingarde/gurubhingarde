---
name: flexray-config-checklist-reviewer
description: Run a confirmation review on any FlexRay cluster configuration xlsx and produce a completed checklist with auto-filled findings, dashboard visualization, and recommended actions for ISO 17458 compliance.
---

# FlexRay Configuration Checklist Reviewer

Runs a comprehensive review on any FlexRay cluster configuration xlsx and produces a completed checklist with visual dashboard (KPI tiles, compliance charts, findings table) plus auto-filled findings and recommended actions. Pairs with `flexray-config-builder` but works on any FlexRay config xlsx via best-effort probing.

## When to use this skill

- Review or audit a FlexRay cluster configuration
- Validate timing parameters per ISO 17458
- Check slot allocation and frame distribution
- Verify node inventory and dual-channel consistency
- Get a roll-up of configuration quality with charts and metrics

## Workflow

1. Get the FlexRay config xlsx path
2. `python scripts/generate_checklist.py <flexray_config.xlsx> <output_checklist.xlsx>`
3. Walk through the Summary dashboard, then per-tab review
4. Iterate on configuration

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | Cluster being assessed |
| 2 | General Info | TOC and document conventions |
| 3 | Guide | Rating / confidence / obligation legend |
| 4 | Summary | Visual dashboard with KPI tiles, pie/bar charts, findings table |
| 5 | Configuration Review | ~14 doc-quality checks |
| 6 | Technical Assessment | ~14 timing/allocation substantive checks |
| 7 | Validation Assessment | ~14 cycle closure and redundancy checks |

## Files

```
flexray-config-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── flexray_probe.py
│   ├── check_definitions.py
│   ├── dashboard.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
```
