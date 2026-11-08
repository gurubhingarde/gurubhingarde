---
name: safety-program-risk-register-builder
description: Generate an audit-ready safety program risk register workbook for ISO 26262 and ISO 21434 program management capturing risks affecting safety case delivery including resource gaps, tool qualification gaps, supplier delays, late requirements changes, and compliance risks with likelihood and impact scoring.
---

# Safety Program Risk Register Builder

A programmatic risk register tracks risks affecting the delivery and assurance of the safety case (not functional hazards, but management and delivery risks). This skill produces a complete, audit-ready Risk Register workbook by capturing risk ID, description, category, likelihood, impact, and calculated risk score; defining mitigation and contingency plans; and tracking status and trends over time.

## When to use this skill

Use whenever the user wants to:
- Create or update a safety program risk register per ISO 26262-2 Clause 7
- Track resource gaps, tool qualification gaps, supplier delays, or late requirements changes
- Document likelihood/impact scoring and risk mitigation strategies
- Maintain a risk escalation log and trend analysis
- Build the documentation that supports program-level risk management

## Workflow

### Step 1 — Gather risk inputs

Ask for:

1. **Project name and document ID**
2. **Target ASIL** (A, B, C, or D)
3. **Reporting period** (start/end dates)
4. **Known risks** — list each with: category (resource, tool, supplier, schedule, compliance, other), description, owner, likelihood (1-5), impact (1-5), planned mitigation

### Step 2 — Build the input JSON

Create input.json conforming to the schema in `scripts/generate_risk_register.py`. Example structure:

```json
{
  "project": {
    "name": "Project Phoenix",
    "doc_id": "RR-001",
    "target_asil": "D"
  },
  "reporting_period": {
    "start": "2024-01-01",
    "end": "2024-03-31"
  },
  "risks": [
    {
      "id": "R01",
      "category": "resource",
      "description": "Insufficient verification engineer availability",
      "owner": "FSM",
      "likelihood": 3,
      "impact": 4,
      "mitigation": "Contract external verification support",
      "contingency": "Reduce scope to critical WPs",
      "status": "Open"
    }
  ]
}
```

### Step 3 — Generate

```bash
python scripts/generate_risk_register.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

### Step 4 — Present

Present the xlsx to the user and call out:
- The **Risk Catalog** tab — is the risk scoring (likelihood × impact) defensible?
- The **Mitigation Plan** tab — is each mitigation owned and scheduled?
- The **Risk Trend** tab — ships empty; tell the user it needs manual population.
- The **Escalation Log** tab — ships empty; tell the user it needs manual population.

## Output structure (8 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Project name, document ID, target ASIL, reporting period, document date, revision |
| 01 | Document Control | Revision history and release record |
| 02 | Risk Catalog | Rows: ID, category, description, likelihood, impact, score (formula `=L*I`), owner, status, target date |
| 03 | Mitigation Plan | Risk ID, mitigation action, owner, target completion, status |
| 04 | Contingency Plan | Risk ID, contingency action, trigger criteria, decision owner |
| 05 | Risk Trend | Scaffold — headers only; populate manually across reporting periods |
| 06 | Escalation Log | Scaffold — headers only; add escalation events as risks exceed thresholds |
| 07 | References | Standards (ISO 26262-2 Clause 7, ISO 21434), risk category values, scoring convention |

**Known limitations (do not promise these to the user):**
- **Risk Trend** and **Escalation Log** ship as empty scaffolds. The generator writes headers and a placeholder line only; there is no historical-score input in the schema yet.
- **Mitigation Plan → Status** is hardcoded to `In Progress` for every row; the per-risk `status` field feeds only the Risk Catalog.
- **Contingency Plan → Trigger Criteria** is auto-templated as "If \<risk id\> exceeds score threshold" — edit it by hand before review.

## Files in this skill

```
safety-program-risk-register-builder/
├── SKILL.md
└── scripts/
    ├── generate_risk_register.py
    ├── recalc.py
    └── office/
```

No `references/` or `examples/` directory ships with this skill — use the JSON example in Step 2 as the input template.
