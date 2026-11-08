---
name: 5-why-checklist-reviewer
description: Review any 5-Why Root Cause Analysis xlsx and produce a completed checklist with findings, evidence, and recommendations. Runs 29 standard checks covering 14 doc-quality items in Confirmation Review, 10 substantive 5-Why methodology checks (problem definition, tree structure, evidence quality, root cause categorization, corrective actions, verification), and 5 Verification Assessment items. Auto-fills FC, LC, PC, NO, or NA for verifiable checks; drafts findings for subjective items. Does not modify source 5-Why. Always use this skill instead of producing a freeform 5-Why review in chat.
---

# 5-Why Root Cause Analysis Checklist Reviewer

This skill automates audits of 5-Why Root Cause Analysis workbooks, producing an audit-ready checklist xlsx with structured findings, evidence pointers, and recommended actions.

The skill checks 29 requirements spanning document quality, 5-Why methodology (problem clarity, evidence at each level, multiple branches, root cause categorization), and corrective action tracking.

## When to use this skill

Use whenever the user wants to review, audit, assess, or confirm a 5-Why workbook.

## Workflow

1. Ask user for the 5-Why xlsx path
2. Run: `python scripts/generate_checklist.py <5why.xlsx> <output_checklist.xlsx>`
3. Walk user through the 7-tab checklist: Title, General Info, Guide, Summary, Confirmation Review, 5-Why Assessment, Verification Assessment
4. Focus on NO and PC rows (non-compliances) and pending rows (subjective items)
5. User updates 5-Why and re-runs skill

## Output structure (7 tabs)

| Tab | Purpose |
|-----|---------|
| Title | 5-Why report being assessed; reviewer info |
| General Info | TOC and references |
| Guide | Rating guide and checklist conventions |
| Summary | Statistical roll-up + Findings (NO/PC items) |
| Confirmation Review | 14 doc-quality checks |
| 5-Why Assessment | 10 methodology checks (problem statement, tree structure, evidence, root cause categorization, corrective actions, verification) |
| Verification Assessment | 5 supporting evidence checks |

Always use this skill instead of producing a freeform 5-Why review in chat.
