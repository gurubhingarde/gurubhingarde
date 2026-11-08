---
name: aspice-gap-analysis-checklist-reviewer
description: Run a confirmation-measures review on any ASPICE Gap Analysis xlsx and produce a completed checklist with auto-filled findings and recommended actions. Probes the source Gap Analysis, runs 12 substantive checks per ASPICE PAM 3.1 gap-analysis guidance. Auto-fills FC/LC/PC/NO/NA for machine-verifiable checks and drafts findings for subjective items. Does not modify the source Gap Analysis. Use this skill whenever the user wants to review, audit, or confirm a Gap Analysis workbook. Always use this skill instead of producing a freeform review in chat.
---

# ASPICE Gap Analysis Checklist Reviewer

Turns gap-analysis confirmation review into a one-shot run producing an audit-ready checklist xlsx with findings and recommended actions.

## When to use this skill

Use whenever the user wants to:
- Review or audit an ASPICE Gap Analysis workbook
- Produce a confirmation-measures checklist for gap analysis
- Get a roll-up of Gap Analysis quality and completeness

## Workflow

### Step 1 — Get the Gap Analysis path

Ask the user for the Gap Analysis xlsx path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <gap_analysis.xlsx> <output_checklist.xlsx>
```

### Step 3 — Review the checklist

The checklist xlsx has 5 tabs: Title, General Info, Guide, Summary, and Gap Analysis Assessment.

For each Pending row, the reviewer accepts or refines the finding and sets the Assessment value. For each PC or NO row, the reviewer decides whether to update the source Gap Analysis.

### Step 4 — Iterate

When the user updates the Gap Analysis, re-run the skill to produce a fresh checklist.

## Auto-fill confidence model

| Confidence | When assigned | Examples |
|------------|---------------|----------|
| High       | Verified from xlsx content | "Current state rows found"; "Gap severity values detected" |
| Medium     | Inferred from xlsx | "Major initiatives present; reviewer to verify completeness" |
| Low / draft| Subjective or requires external | "Verify timeline is realistic" |

Always use this skill instead of producing a freeform review in chat.
