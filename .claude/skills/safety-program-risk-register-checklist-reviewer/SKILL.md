---
name: safety-program-risk-register-checklist-reviewer
description: Run an automated and manual confirmation review on any ISO 26262 safety program risk register capturing 25+ audit checks for risk scoring methodology, mitigation ownership, escalation triggers, and completeness. Produces an audit-ready review report with checklist results and dashboard summary.
---

# Safety Program Risk Register Checklist Reviewer

This skill automatically probes and audits an existing Safety Program Risk Register workbook for completeness, rigor, and consistency per ISO 26262-2 Clause 7. It generates a detailed checklist with 25+ confirmation points, a visual dashboard summary, and a recommendation report.

## When to use this skill

Use whenever the user wants to:
- Review and audit an existing risk register workbook for compliance
- Verify risk scoring methodology and likelihood/impact calibration
- Confirm mitigation plans are owned and scheduled
- Audit escalation triggers and decision records
- Generate an audit-ready confirmation review report

## Workflow

### Step 1 — Provide the risk register xlsx

Ask the user to provide the risk register workbook (typically output from safety-program-risk-register-builder).

### Step 2 — Run the review

```bash
python scripts/generate_checklist.py <input.xlsx> <output_review.xlsx>
```

The script will:
- Probe the Risk Catalog tab and extract all risk data
- Apply 25+ confirmation checks
- Generate a detailed checklist tab
- Build a visual dashboard with pass/fail summary
- Output a review report with findings and recommendations

### Step 3 — Present findings

Display the output_review.xlsx to the user highlighting:
- **Dashboard** tab — overall pass/fail status and risk health summary
- **Checklist** tab — detailed results for each of the 25+ checks
- **Findings** tab — any gaps or recommendations for improvement
- **Risk Health Metrics** tab — scoring distribution, trending analysis

## Checks performed (25+)

1. Risk ID uniqueness
2. All risks have category assigned (resource/tool/supplier/schedule/compliance/scope/other)
3. All risks have description (non-empty, >10 chars)
4. Likelihood values in range 1-5
5. Impact values in range 1-5
6. Risk score formula present (Likelihood × Impact)
7. Risk score values correct
8. All risks have owner assigned
9. Owner field non-empty and valid (matches project roster if available)
10. Status field populated (Open/In Progress/Mitigated/Closed)
11. Target date field populated and future-dated
12. Mitigation plan exists for all open risks
13. Mitigation actions are specific and actionable
14. Mitigation owner assigned to each risk
15. Contingency plan exists for high-risk items (score ≥12)
16. Contingency trigger criteria defined
17. Escalation log captures at least one escalation event
18. Escalation reason documented
19. Escalation authority (who was it escalated to) recorded
20. No duplicate risk descriptions (prevent double-counting)
21. Risk categories distributed appropriately (not all one type)
22. High-risk items (score >15) have accelerated review schedule
23. Trend analysis tab shows historical data points
24. References section lists applicable standards
25. Document control revision history present

## Output structure

| Tab | Purpose |
|---|---|
| Dashboard | Visual summary of review results, pass/fail counts, risk heat map |
| Checklist Results | Detailed results for each of 25+ checks with status and comments |
| Findings | Summary of gaps, non-conformances, and improvement recommendations |
| Risk Health Metrics | Statistical analysis: score distribution, category breakdown, trend summary |
| Compliance Map | Traceability to ISO 26262-2 Clause 7 requirements |

## Files in this skill

```
safety-program-risk-register-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── risk_probe.py
│   ├── check_definitions.py
│   ├── build_dashboard.py
│   ├── recalc.py
│   └── office/
├── references/
│   ├── methodology.md
│   └── risk_checks.md
└── examples/
    └── sample_review_output.xlsx
```
