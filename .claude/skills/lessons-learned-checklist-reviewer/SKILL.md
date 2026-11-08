---
name: lessons-learned-checklist-reviewer
description: Run an automated and manual confirmation review on any ISO 26262-2 lessons learned register capturing 25+ audit checks for lesson clarity, root cause rigor, corrective action specificity, distribution completeness, application tracking, and effectiveness review. Produces an audit-ready review report with dashboard.
---

# Lessons Learned Checklist Reviewer

This skill automatically audits an existing Lessons Learned Register workbook for completeness and rigor per ISO 26262-2 Section 5 and IATF 16949 Section 10.2.4. It generates a detailed checklist with 25+ confirmation points and a visual dashboard summary.

## When to use this skill

Use whenever the user wants to:
- Review and audit an existing lessons learned register for compliance
- Verify each lesson has a clear root cause analysis
- Confirm corrective actions are specific and assigned
- Audit distribution and tracking of lesson implementation
- Validate effectiveness review and organizational learning
- Generate an audit-ready lessons learned confirmation report

## Checks performed (25+)

1. Lesson ID unique
2. Lesson source identified (incident/audit/RCA/customer return)
3. Lesson summary clear and concise
4. Root cause analysis documented (not just symptom)
5. Root cause is actionable and specific
6. Corrective action defined
7. Corrective action is specific and measurable
8. Corrective action owner assigned
9. Corrective action has target completion date
10. Best practice recommended
11. Best practice is generalizable (not project-specific)
12. Applicability scope defined (which teams/projects/phases)
13. Distribution target identified (who needs to know)
14. Distribution delivery method specified
15. Distribution target completion date assigned
16. Application tracker populated with at least one implementation
17. Application context documented (where/how lesson was applied)
18. Application date recorded
19. Effectiveness assessment documented
20. Effectiveness assessment is quantitative if possible
21. High-impact lessons (related to safety) tracked across organization
22. Lessons are categorized (technical/process/tool/organizational)
23. Trend analysis populated (count of lessons by source)
24. Effectiveness review schedule established
25. Document control revision history present

## Output structure

| Tab | Purpose |
|---|---|
| Dashboard | Visual summary, pass/fail counts, organizational learning health |
| Checklist Results | Detailed results for each of 25+ checks |
| Findings | Summary of gaps and improvement recommendations |
| Lesson Quality Metrics | Analysis of lesson quality, categorization distribution, effectiveness trends |

## Files in this skill

```
lessons-learned-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── ll_probe.py
│   ├── check_definitions.py
│   ├── build_dashboard.py
│   ├── recalc.py
│   └── office/
├── references/
│   └── ll_checks.md
└── examples/
    └── sample_ll_review_output.xlsx
```
