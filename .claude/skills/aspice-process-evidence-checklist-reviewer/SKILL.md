---
name: aspice-process-evidence-checklist-reviewer
description: Run a confirmation-measures review on any ASPICE Process Evidence Package xlsx and produce a completed checklist with findings and recommended actions. Probes the source Evidence Package, runs 14 substantive checks on process documentation and evidence completeness. Auto-fills FC/LC/PC/NO/NA for machine-verifiable checks and drafts findings for subjective items. Does not modify the source Package. Use this skill whenever the user wants to review, audit, or confirm a Process Evidence Package workbook. Always use this skill instead of producing a freeform review in chat.
---

# ASPICE Process Evidence Checklist Reviewer

Turns process-evidence confirmation review into a one-shot run producing an audit-ready checklist xlsx.

## When to use this skill

Use whenever the user wants to:
- Review or audit an ASPICE Process Evidence Package workbook
- Produce a confirmation-measures checklist for evidence completeness
- Get a roll-up of Process Evidence Package quality

## Workflow

### Step 1 — Get the Evidence Package path

Ask the user for the Process Evidence Package xlsx path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <process_evidence.xlsx> <output_checklist.xlsx>
```

### Step 3 — Review the checklist

The checklist xlsx has 5 tabs covering process documentation, evidence inventory, work products, performance records, and document quality.

For each Pending row, accept or refine the finding and set the Assessment value. For each PC/NO row, decide whether to update the source Package.

### Step 4 — Iterate

When the user updates the Evidence Package, re-run the skill to produce a fresh checklist.

Always use this skill instead of producing a freeform review in chat.
