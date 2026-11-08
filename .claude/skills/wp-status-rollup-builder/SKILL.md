---
name: wp-status-rollup-builder
description: Generate an audit-ready work product status roll-up workbook for ISO 26262 and ISO 21434 program management aggregating completion percentage, owner, due date, dependencies, ASIL, and blocking issues across all safety lifecycle work products from Safety Plan baseline.
---

# Work Product Status Rollup Builder

A work product status rollup aggregates the completion status of every work product defined in the Safety Plan, providing a project-level dashboard for the Safety Manager and Program Management. This skill produces an audit-ready Status Rollup workbook with burndown trends, dependency mapping, and risk escalation.

## When to use this skill

Use whenever the user wants to:
- Create or update a work product status rollup per ISO 26262-2 program management requirements
- Aggregate WP status, owner, due date, dependencies, and ASIL across all lifecycle phases
- Track % complete for each WP and identify critical path items
- Identify WPs with blocking issues
- Build a project health dashboard with trend analysis

## Workflow

### Step 1 — Gather status inputs

Ask for:

1. **Project name and reporting period**
2. **Complete list of WPs from Safety Plan** with: ID, name, owner, planned due date, current % complete, dependencies, ASIL
3. **Blocking issues** — any WPs blocked or at risk of slipping

### Step 2 — Build input JSON

Create input.json conforming to the schema in `scripts/generate_wp_status.py`.

### Step 3 — Generate

```bash
python scripts/generate_wp_status.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

### Step 4 — Present

Display the output xlsx highlighting:
- The **Work Product Roll-up** tab — is every WP tracked with status %, owner, due date?
- The **Critical Path WPs** tab — which WPs are on the critical path?
- The **Dependency Map** tab — are dependencies forming a valid DAG?
- The **Burndown Trend** tab — is progress trending correctly?

## Output structure (10 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Project name, reporting period, Safety Manager, baseline summary |
| 01 | Document Control | Revision history |
| 02 | Reporting Period | Start/end dates, WPs reported, status as of date |
| 03 | Lifecycle Phase Inventory | Rows per phase (Concept, System, HW, SW, Integration, Validation, Release): WP count, % complete aggregate |
| 04 | Work Product Roll-up | Rows per WP: status %, owner, due date, dependencies, ASIL, blocker status |
| 05 | Critical Path WPs | WPs on critical path with schedule impact |
| 06 | Dependency Map | WP ID relationships: predecessor, successor, dependency type |
| 07 | Burndown Trend | Historical % complete per reporting period |
| 08 | Risk Linkage | Open risks affecting WP completion |
| 09 | References | ISO 26262-2 program management requirements |

## Files in this skill

```
wp-status-rollup-builder/
├── SKILL.md
├── scripts/
│   ├── generate_wp_status.py
│   ├── recalc.py
│   └── office/
├── references/
│   └── methodology.md
└── examples/
    └── sample_wp_status.json
```
