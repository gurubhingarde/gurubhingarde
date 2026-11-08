---
name: automotive-ethernet-checklist-reviewer
description: Run a confirmation review on any Automotive Ethernet network configuration xlsx and produce a completed checklist with auto-filled findings, dashboard visualization, and recommended actions for IEEE 100BASE-T1 compliance.
---

# Automotive Ethernet Checklist Reviewer

Runs a comprehensive review on any Automotive Ethernet network configuration xlsx and produces a completed checklist with visual dashboard (KPI tiles, compliance charts, findings table) plus auto-filled findings and recommended actions. Pairs with `automotive-ethernet-builder` but works on any Ethernet config xlsx via best-effort probing.

## When to use this skill

- Review or audit an Automotive Ethernet network configuration
- Validate VLAN segmentation and switch configuration
- Check SOME/IP service allocation and provider/consumer mappings
- Verify AVB stream bandwidth reservation and TSN scheduling
- Validate multicast routing and MAC address uniqueness
- Get a roll-up of network design quality with charts and metrics

## Workflow

1. Get the Automotive Ethernet config xlsx path
2. `python scripts/generate_checklist.py <autoeth_config.xlsx> <output_checklist.xlsx>`
3. Walk through the Summary dashboard, then per-tab review
4. Iterate on network design

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | Network being assessed |
| 2 | General Info | TOC and document conventions |
| 3 | Guide | Rating / confidence / obligation legend |
| 4 | Summary | Visual dashboard with KPI tiles, pie/bar charts, findings table |
| 5 | Configuration Review | ~14 doc-quality checks |
| 6 | Technical Assessment | ~14 VLAN/SOME/IP/AVB substantive checks |
| 7 | Validation Assessment | ~14 bandwidth budget and routing checks |

## Files

```
automotive-ethernet-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── autoeth_probe.py
│   ├── check_definitions.py
│   ├── dashboard.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
```
