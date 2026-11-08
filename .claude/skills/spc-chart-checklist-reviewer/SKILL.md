---
name: spc-chart-checklist-reviewer
description: Review any Statistical Process Control (SPC) Chart xlsx and produce a completed checklist with findings and recommendations. Runs 33 standard checks covering 14 doc-quality items, 14 substantive AIAG SPC 2nd edition checks (chart type appropriateness, subgroup size, sampling frequency, control limit calculations, statistical control assessment, Cpk calculation and target validation, out-of-control rules monitoring, special cause investigation, process stability, recalculation on change, capability reporting, recommendations), and 5 Verification Assessment items. Flags if Cpk is below 1.33 (process not capable per AIAG). Auto-fills ratings; drafts findings for subjective items. Does not modify source SPC. Always use this skill instead of producing a freeform SPC review in chat.
---

# SPC Control Chart Checklist Reviewer

This skill audits Statistical Process Control (SPC) Chart workbooks per AIAG SPC 2nd edition, producing an audit-ready checklist xlsx with findings and recommendations.

Checks 33 requirements spanning document quality, AIAG chart methodology (appropriate chart type, subgroup sizing, sampling justification, control limit calculations via AIAG constants, statistical control verification, Cpk calculation with target validation for standard (>1.33) and special characteristics (>1.67)), out-of-control rule monitoring (Western Electric/Nelson), special cause investigation, stability documentation, and process capability reporting.

## When to use this skill

Use whenever the user wants to review, audit, or assess an SPC Chart workbook.

## Workflow

1. Ask user for the SPC xlsx path
2. Run: `python scripts/generate_checklist.py <spc_chart.xlsx> <output_checklist.xlsx>`
3. Walk user through the 7-tab checklist
4. Note headline: skill flags if Cpk < 1.33 (process not capable per AIAG)
5. Focus on NO and PC rows and pending items
6. User updates SPC chart and re-runs skill

## Output structure (7 tabs)

| Tab | Purpose |
|-----|---------|
| Title | SPC chart being assessed; reviewer info |
| General Info | TOC and references |
| Guide | Rating guide and AIAG conventions |
| Summary | Statistical roll-up + Findings |
| Confirmation Review | 14 doc-quality checks |
| SPC Assessment | 14 AIAG SPC checks (chart type, subgroup size, sampling, control limits, statistical control, Cpk, out-of-control rules, special cause investigation, stability, recalculation, capability reporting, recommendations) |
| Verification Assessment | 5 supporting evidence checks |

Always use this skill instead of producing a freeform SPC review in chat.
