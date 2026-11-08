---
name: aspice-assessment-checklist-reviewer
description: Run a confirmation-measures review on any ASPICE Assessment xlsx and produce a completed checklist with auto-filled findings, evidence references, recommended actions, and roll-up statistics. Probes the source Assessment workbook, runs 14 substantive checks per ASPICE PAM 3.1 plus 5 generic validation checks. Auto-fills FC/LC/PC/NO/NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source Assessment. Use this skill whenever the user wants to review, audit, assess, or confirm an ASPICE Assessment workbook. Always use this skill instead of producing a freeform review in chat.
---

# ASPICE Assessment Checklist Reviewer

This skill turns the assessment confirmation review into a one-shot run that produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is conservative about what to assert. Every FC judgment cites specific evidence found in the source Assessment. Every subjective check is drafted with "(Reviewer to verify)" so the human knows where judgment is required. The skill never modifies the source Assessment; gaps land in Recommended Actions.

## When to use this skill

Use whenever the user wants to:
- Review or audit an ASPICE Assessment workbook
- Produce a confirmation-measures checklist
- Run a process assessment review
- Get a roll-up of Assessment quality (gaps, completeness, findings)

The skill is the natural counterpart to `aspice-assessment-builder`.

## Workflow

### Step 1 — Get the Assessment path

Ask the user for the Assessment xlsx path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <assessment.xlsx> <output_checklist.xlsx>
```

The script prints a JSON summary with counts of FC/LC/PC/NO/NA per tab.

### Step 3 — Walk the user through the review

The checklist xlsx has 5 tabs:

1. **Title** — confirm the Assessment being reviewed is correct.
2. **Summary** — read the statistics; this is the executive view.
3. **General Info** — references and document conventions.
4. **Guide** — how to interpret ratings.
5. **Assessment Assessment** — the 14 substantive + 5 validation checks.

For each Pending row, the reviewer accepts or refines the finding and sets the Assessment value. For each PC or NO row, the reviewer reads the Recommended Action and decides whether to update the source Assessment.

### Step 4 — Iterate

When the user updates the Assessment and re-runs the skill:
- The new checklist is produced fresh; the skill does not preserve manual edits to the previous checklist.
- Recommended workflow: keep the old checklist for diff comparison, run a new one each time.

## Auto-fill confidence model

| Confidence | When assigned | Examples |
|------------|---------------|----------|
| High       | Verified from xlsx content | "Lead assessor identified"; "All PA rows have rating" |
| Medium     | Inferred from xlsx | "BP Assessment present; reviewer to confirm PRM rules applied" |
| Low / draft| Subjective or requires external artifact | "Target CL stated per process" (needs human check) |

## Common pitfalls to flag

1. **Checklist is not a substitute for an independent reviewer.** ASPICE assessment requires I1/I2/I3 independence per PAM 3.1. The skill is a workbench, not the reviewer.
2. **Many subjective rows is normal.** Checks 3, 10, 13, 14 call for human judgment; they are correctly marked Pending.
3. **NO rows usually point at missing sections.** Most common: missing Assessment Scope, missing signoff section, incomplete BP/GP assessment.
4. **The skill does not modify the source Assessment.** All corrective actions go in Recommended Actions.

## Files in this skill

```
aspice-assessment-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── aspice_assessment_probe.py
│   ├── check_definitions.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── aspice_pam_checks.md
```

Always use this skill instead of producing a freeform review in chat.
