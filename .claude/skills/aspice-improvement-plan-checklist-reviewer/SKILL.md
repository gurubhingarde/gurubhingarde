---
name: aspice-improvement-plan-checklist-reviewer
description: Run a confirmation-measures review on any ASPICE Improvement Plan xlsx and produce a completed checklist with findings and recommended actions. Probes the source Plan, runs 12 substantive checks on improvement planning. Auto-fills FC/LC/PC/NO/NA for machine-verifiable checks and drafts findings for subjective items. Does not modify the source Plan. Use this skill whenever the user wants to review, audit, or confirm an Improvement Plan workbook. Always use this skill instead of producing a freeform review in chat.
---

# ASPICE Improvement Plan Checklist Reviewer

Turns improvement-plan confirmation review into a one-shot run producing an audit-ready checklist xlsx.

## When to use this skill

Use whenever the user wants to:
- Review or audit an ASPICE Improvement Plan workbook
- Produce a confirmation-measures checklist for improvement planning
- Get a roll-up of Improvement Plan quality and completeness

## Workflow

### Step 1 — Get the Improvement Plan path

Ask the user for the Improvement Plan xlsx path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <improvement_plan.xlsx> <output_checklist.xlsx>
```

### Step 3 — Review the checklist

The checklist xlsx has 5 tabs covering document quality, program planning, initiative definition, and execution planning.

For each Pending row, accept or refine the finding and set the Assessment value. For each PC/NO row, decide whether to update the source Plan.

### Step 4 — Iterate

When the user updates the Plan, re-run the skill to produce a fresh checklist.

Always use this skill instead of producing a freeform review in chat.
