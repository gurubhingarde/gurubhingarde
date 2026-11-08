---
name: safety-gate-review-checklist-reviewer
description: Run an automated and manual confirmation review on any ISO 26262 safety gate review record capturing 25+ audit checks for entry criteria, deliverable completeness, exit criteria verification, action items, and gate decision documentation. Produces an audit-ready review report with dashboard summary.
---

# Safety Gate Review Checklist Reviewer

This skill automatically audits an existing gate review record workbook for completeness and rigor per ISO 26262-2 Clause 8.2. It generates a detailed checklist with 25+ confirmation points, a visual dashboard summary, and recommendations.

## When to use this skill

Use whenever the user wants to:
- Review and audit an existing gate review record for compliance
- Verify all entry criteria are satisfied
- Confirm deliverable inventory is complete
- Audit exit criteria measurement and achievement
- Validate gate decision documentation and attendees
- Generate an audit-ready gate review confirmation report

## Workflow

### Step 1 — Provide the gate review xlsx

Ask the user to provide the gate review record workbook.

### Step 2 — Run the review

```bash
python scripts/generate_checklist.py <input.xlsx> <output_review.xlsx>
```

### Step 3 — Present findings

Display the output_review.xlsx highlighting the Dashboard and Checklist tabs.

## Checks performed (25+)

1. Gate milestone identified and valid
2. Target ASIL assigned and consistent with project baseline
3. Gate scope clearly defined
4. Predecessor gate referenced
5. Entry criteria checklist complete (all rows populated)
6. Entry criteria satisfied (yes/no decision recorded)
7. Entry criteria evidence documented
8. Entry criteria reviewers assigned
9. All entry criteria evidenced with sign-off
10. Deliverable inventory complete per Safety Plan
11. All required work products listed
12. All deliverables marked present/absent
13. Deliverable quality status assigned (draft/complete/approved)
14. Deliverable owners identified
15. Exit criteria defined per phase
16. Exit criteria measurable (quantified)
17. Exit criteria met status documented
18. Exit criteria evidence provided
19. Action items from gate review recorded
20. Action items have owner and due date
21. High-priority action items identified
22. Open risks linked and acknowledged
23. Gate decision recorded (Go/Conditional/No-Go)
24. Gate decision rationale documented
25. Gate chair and attendees signatures captured

## Output structure

| Tab | Purpose |
|---|---|
| Dashboard | Visual summary of review results, pass/fail counts, gate health |
| Checklist Results | Detailed results for each of 25+ checks |
| Findings | Summary of gaps and improvement recommendations |
| Compliance Map | Traceability to ISO 26262-2 Clause 8.2 |

## Files in this skill

```
safety-gate-review-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── gate_probe.py
│   ├── check_definitions.py
│   ├── build_dashboard.py
│   ├── recalc.py
│   └── office/
├── references/
│   └── gate_checks.md
└── examples/
    └── sample_gate_review_output.xlsx
```
