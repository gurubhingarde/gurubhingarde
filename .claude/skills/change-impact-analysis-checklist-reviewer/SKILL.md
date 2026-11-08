---
name: change-impact-analysis-checklist-reviewer
description: Run an automated and manual confirmation review on any ISO 26262-8 change impact analysis capturing 25+ audit checks for change classification justification, affected work product completeness, ASIL impact assessment, re-verification scope definition, and approval authority. Produces an audit-ready review report with dashboard.
---

# Change Impact Analysis Checklist Reviewer

This skill automatically audits an existing Change Impact Analysis workbook for completeness and rigor per ISO 26262-8 Clause 8. It generates a detailed checklist with 25+ confirmation points and a visual dashboard summary.

## When to use this skill

Use whenever the user wants to:
- Review and audit an existing change impact analysis for compliance
- Verify change classification is justified
- Confirm all affected work products are identified
- Audit ASIL impact assessment and re-verification scope
- Validate approval authority and signatures
- Generate an audit-ready change analysis confirmation report

## Checks performed (25+)

1. Change ID unique and valid
2. Change title clear and descriptive
3. Requesting party identified
4. Request date recorded
5. Change description complete (rationale present)
6. Change classification assigned (minor/major/safety-impacting)
7. Classification justification documented
8. All potentially affected WPs identified
9. Impact type assigned to each affected WP (modified/created/obsoleted)
10. Impact description specific for each WP
11. Original ASIL assigned
12. Modified ASIL assigned
13. ASIL impact justification documented
14. No unjustified ASIL increases
15. Re-verification activities defined
16. Re-verification scope measurable
17. Re-verification owner assigned
18. Re-verification target date assigned
19. Re-validation activities defined
20. Re-validation scope clear
21. Re-validation owner assigned
22. Re-validation target date assigned
23. Safety Manager approval captured with signature
24. Change Board approval captured
25. Conditional approvals documented (if any)

## Output structure

| Tab | Purpose |
|---|---|
| Dashboard | Visual summary, pass/fail counts, change health |
| Checklist Results | Detailed results for each of 25+ checks |
| Findings | Summary of gaps and recommendations |
| Impact Summary | Consolidated view of affected WPs and ASIL impact |

## Files in this skill

```
change-impact-analysis-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── cia_probe.py
│   ├── check_definitions.py
│   ├── build_dashboard.py
│   ├── recalc.py
│   └── office/
├── references/
│   └── cia_checks.md
└── examples/
    └── sample_cia_review_output.xlsx
```
