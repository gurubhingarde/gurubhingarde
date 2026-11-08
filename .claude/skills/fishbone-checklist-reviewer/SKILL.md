---
name: fishbone-checklist-reviewer
description: Review any Fishbone (Ishikawa) Diagram xlsx and produce a completed checklist with findings and recommendations. Runs 29 standard checks covering 14 doc-quality items, 10 substantive Fishbone methodology checks (effect clarity, 6Ms coverage, cause specificity, Mermaid diagram completeness, cross-functional contribution, prioritization), and 5 Verification Assessment items. Auto-fills ratings for machine-verifiable checks; drafts findings for subjective items. Does not modify source Fishbone. Always use this skill instead of producing a freeform Fishbone review in chat.
---

# Fishbone Diagram Checklist Reviewer

This skill audits Fishbone (Ishikawa) Diagram workbooks, producing an audit-ready checklist xlsx with structured findings and recommended actions.

Checks 29 requirements spanning document quality, methodology (effect clarity, systematic 6Ms coverage, specific causes, Mermaid rendering, cross-functional team), and verification.

## When to use this skill

Use whenever the user wants to review, audit, or assess a Fishbone Diagram workbook.

## Workflow

1. Ask user for the Fishbone xlsx path
2. Run: `python scripts/generate_checklist.py <fishbone.xlsx> <output_checklist.xlsx>`
3. Walk user through the 7-tab checklist
4. Focus on NO and PC rows and pending subjective items
5. User updates Fishbone and re-runs skill

## Output structure (7 tabs)

| Tab | Purpose |
|-----|---------|
| Title | Fishbone diagram being assessed; reviewer info |
| General Info | TOC and references |
| Guide | Rating guide and conventions |
| Summary | Statistical roll-up + Findings |
| Confirmation Review | 14 doc-quality checks |
| Fishbone Assessment | 10 methodology checks (effect, 6Ms coverage, cause specificity, Mermaid diagram, team contribution, prioritization) |
| Verification Assessment | 5 supporting evidence checks |

Always use this skill instead of producing a freeform Fishbone review in chat.
