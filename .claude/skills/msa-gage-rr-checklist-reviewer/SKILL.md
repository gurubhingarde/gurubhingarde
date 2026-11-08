---
name: msa-gage-rr-checklist-reviewer
description: Review any MSA Gauge R&R (Measurement System Analysis) xlsx and produce a completed checklist with findings and recommendations. Runs 34 standard checks covering 14 doc-quality items, 15 substantive AIAG MSA 4th edition checks (gage information, study design per AIAG recommendations, ANOVA calculations, Gauge R&R percentage, ndc, bias, linearity, stability, attribute agreement, acceptance decision), and 5 Verification Assessment items. Flags if Gauge R&R exceeds 30 percent (unacceptable per AIAG). Auto-fills ratings; drafts findings for subjective items. Does not modify source MSA. Always use this skill instead of producing a freeform MSA review in chat.
---

# MSA Gauge R&R Checklist Reviewer

This skill audits Measurement System Analysis (Gauge R&R) workbooks per AIAG MSA 4th edition, producing an audit-ready checklist xlsx with findings and recommendations.

Checks 34 requirements spanning document quality, AIAG study design recommendations (3+ operators, 10+ parts, 2-3 trials, randomization), ANOVA calculations, Gauge R&R percentage (target <10% acceptable, 10-30% marginal, >30% unacceptable), ndc, bias, linearity, stability, and attribute agreement (Cohen's kappa for attribute studies).

## When to use this skill

Use whenever the user wants to review, audit, or assess an MSA Gauge R&R workbook.

## Workflow

1. Ask user for the MSA xlsx path
2. Run: `python scripts/generate_checklist.py <msa_gage_rr.xlsx> <output_checklist.xlsx>`
3. Walk user through the 7-tab checklist
4. Note headline: skill flags if Gauge R&R % > 30% (unacceptable per AIAG)
5. Focus on NO and PC rows and pending items
6. User updates MSA and re-runs skill

## Output structure (7 tabs)

| Tab | Purpose |
|-----|---------|
| Title | MSA being assessed; reviewer info |
| General Info | TOC and references |
| Guide | Rating guide and AIAG conventions |
| Summary | Statistical roll-up + Findings |
| Confirmation Review | 14 doc-quality checks |
| MSA Assessment | 15 AIAG MSA checks (gage info, study design, ANOVA, R&R %, ndc, bias, linearity, stability, attribute agreement, acceptance decision) |
| Verification Assessment | 5 supporting evidence checks |

Always use this skill instead of producing a freeform MSA review in chat.
