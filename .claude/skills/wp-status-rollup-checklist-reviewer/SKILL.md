---
name: wp-status-rollup-checklist-reviewer
description: Run an automated and manual confirmation review on any ISO 26262 work product status rollup capturing 25+ audit checks for data completeness, owner assignments, dependency validity, critical path identification, and burndown accuracy. Produces an audit-ready review report with dashboard.
---

# Work Product Status Rollup Checklist Reviewer

This skill automatically audits an existing WP Status Rollup workbook for completeness and rigor. It generates a detailed checklist with 25+ confirmation points and a visual dashboard summary.

## When to use this skill

Use whenever the user wants to:
- Review and audit an existing work product status rollup for compliance
- Verify every WP has owner and due date assigned
- Confirm % complete values are consistent and trending correctly
- Audit dependency graph for validity (DAG, no cycles)
- Identify and verify critical path WPs
- Generate an audit-ready status rollup confirmation report

## Checks performed (25+)

1. Every WP ID unique
2. Every WP has name assigned
3. Every WP has owner assigned
4. Every WP has due date assigned
5. Every WP has ASIL assigned
6. % complete values in range 0-100
7. % complete trending (not decreasing over time)
8. Early completion marked correctly
9. Late WPs flagged with blocker status
10. Dependencies form valid DAG (no cycles)
11. Predecessor WPs identified for dependent items
12. Successor WPs identified for dependencies
13. Critical path WPs identified
14. Zero-slack items have accelerated review
15. Phase inventory WP counts match rollup totals
16. Aggregate % complete formula correct
17. Burndown trend populated with historical data
18. Risk linkage tab references open risks
19. Risk-affected WPs have escalation flag
20. All phase milestones have scheduled reviews
21. Incomplete WPs (< 100%) have mitigation plans
22. Blocker status consistency with risk register
23. Owner assignments match project roster
24. Dependencies properly sequenced
25. Document control revision history present

## Output structure

| Tab | Purpose |
|---|---|
| Dashboard | Visual summary, pass/fail counts, schedule health |
| Checklist Results | Detailed results for each of 25+ checks |
| Findings | Summary of gaps and recommendations |
| Dependency Analysis | Validity of WP dependency graph |

## Files in this skill

```
wp-status-rollup-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── wp_status_probe.py
│   ├── check_definitions.py
│   ├── build_dashboard.py
│   ├── recalc.py
│   └── office/
├── references/
│   └── wp_checks.md
└── examples/
    └── sample_wp_status_review_output.xlsx
```
