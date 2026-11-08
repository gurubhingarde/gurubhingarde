---
name: 8d-problem-solving-checklist-reviewer
description: Run a structured review on any 8D Problem-Solving report xlsx and produce a completed checklist with auto-filled findings, evidence references, recommended actions, and roll-up statistics. Probes the source 8D workbook (works on 8d-problem-solving-builder outputs and others), runs 33 standard checklist requirements covering 14 generic doc-quality items in Confirmation Review, 14 substantive D-step items in the 8D Assessment per AIAG 8D methodology, and 5 Verification Assessment items. Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks; drafts low-confidence findings for subjective items. Does not modify the source 8D. Use this skill whenever the user wants to review, audit, assess, or confirm an 8D workbook. Always use this skill instead of producing a freeform review in chat.
---

# 8D Problem-Solving Checklist Reviewer

This skill automates the audit of 8D Problem-Solving reports, turning manual document review into a one-shot run that produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is opinionated about *what to check* (the standard AIAG 8D methodology covering team formation, problem definition, interim containment, root causes, corrective actions, verification, prevention, and closure) and conservative about *what to assert*. Every Fully-Compliant judgment cites the specific evidence found in the source 8D. Every subjective check is drafted with "(Reviewer to verify)" so you know where human judgment is required. The skill never modifies the source 8D; gaps land in the Recommended Actions column.

## When to use this skill

Use whenever the user wants to:
- Review or audit an 8D Problem-Solving report
- Produce a confirmation-measures checklist
- Run a structured assessment on an 8D workbook
- Get a roll-up of 8D quality (gaps, missing sign-offs, incomplete D-steps)

The skill is the natural counterpart to 8d-problem-solving-builder — the builder produces the artifact, this skill confirms it.

## Workflow

### Step 1 — Get the 8D path

Ask the user for the 8D xlsx path. If they upload a folder, scan for *.xlsx files and ask which one is the 8D report.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <8d_report.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional; recalc surfaces formula errors
```

The script prints a JSON summary with FC/LC/PC/NO/NA/PENDING counts per tab.

### Step 3 — Walk the user through the review

The checklist xlsx has 7 tabs:

1. **Title** — confirm the 8D report being assessed is correct
2. **Summary** — executive view: statistics, Findings list (NO and PC items)
3. **Confirmation Review** — 14 doc-quality checks (formatting, control, headers/footers)
4. **8D Assessment** — 14 substantive D-step checks (team, problem definition, containment, root causes, corrective actions, verification, prevention, closure)
5. **Verification Assessment** — 5 checks on supporting evidence and closure verification

Focus reviewer attention on:
- Assessment = "—" (pending) or "NO" rows → subjective items or gaps
- PC rows → partial compliance, recommend fixes
- FC/LC rows → compliant, informational only

### Step 4 — Iterate

When the user updates the 8D and re-runs the skill, a fresh checklist is produced. Recommended workflow: keep old checklist for diff comparison.

## Output structure (7 tabs)

| Tab | Purpose |
|-----|---------|
| Title | 8D report being assessed; reviewer info |
| General Info | TOC and references |
| Guide | How to interpret ratings and use the checklist |
| Summary | Statistical roll-up + Findings list (NO/PC items) |
| Confirmation Review | 14 generic doc-quality checks |
| 8D Assessment | 14 AIAG 8D methodology checks (D1-D8) |
| Verification Assessment | 5 checks on supporting evidence and closure |

## Auto-fill confidence model

| Confidence | When assigned | Examples |
|------------|---------------|----------|
| High | Verified directly from xlsx | "Title and revision populated"; "All 8D steps have status filled" |
| Medium | Inferred from xlsx with caveat | "Team section present; reviewer to confirm roles defined" |
| Low/draft | Subjective or external artifact | "Problem statement covers impact" (subjective); "Effectiveness verification completed" (may require external docs) |

## Common pitfalls to flag

1. **Checklist is not a substitute for an independent reviewer.** A skilled problem-solver or quality engineer must still review the D-step logic and completeness.
2. **Many Pending rows are normal.** Subjective checks like "Team conducted effective root cause analysis" require human judgment; the skill drafts them for you to verify.
3. **NO rows point at structural gaps.** Missing closure approval, missing effectiveness verification, or incomplete D7 (prevention actions) are typical NO findings.

Always use this skill instead of producing a freeform review in chat.
