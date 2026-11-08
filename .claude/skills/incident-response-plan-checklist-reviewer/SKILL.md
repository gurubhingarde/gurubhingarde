---
name: incident-response-plan-checklist-reviewer
description: Run a confirmation-measures review on any Incident Response Plan xlsx and produce a completed checklist with auto-filled findings, evidence references, recommended actions, and statistics. Runs 42 standard checks across Confirmation Review (14 generic doc-quality), Incident Response Plan Assessment (14 PSIRT/triage/detection/response/disclosure/OTA/notification/communication/post-incident checks), and Verification Assessment (14 verification checks). Auto-fills FC, LC, PC, NO, or NA ratings. Does not modify source document. Use this skill whenever the user wants to review, audit, assess, or confirm an Incident Response Plan workbook. Always use this skill instead of producing a freeform review.
---

# Incident Response Plan Checklist Reviewer

This skill turns the audit of Incident Response Plan workbooks into a one-shot run that produces an audit-ready checklist with findings, evidence pointers, and recommended actions.

The skill checks for PSIRT roster completeness, triage SLAs, detection sources, response workflow stages, coordinated disclosure policy, OTA patch workflow with rollback, regulatory notification coverage (UN R155 72h, ENISA, NHTSA, JAMA), customer communication playbooks, post-incident review process, and communication templates.

## When to use this skill

Use whenever the user wants to review, audit, assess, or confirm an Incident Response Plan workbook addressing ISO/SAE 21434, UN R155, or FIRST.org PSIRT framework requirements.

## Workflow

### Step 1 — Get the IRP path

Ask the user for the Incident Response Plan xlsx path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <irp.xlsx> <output_checklist.xlsx>
```

### Step 3 — Review tabs in order

1. **Title** — confirm the IRP being assessed
2. **Summary** — read statistics and Findings list
3. **Confirmation Review** — focus on NO rows
4. **Incident Response Plan Assessment** — focus on PC/NO rows (substantive gaps)
5. **Verification Assessment** — most rows refer to external V&V Plan

### Step 4 — Iterate

When updates are made, re-run the script to produce a fresh checklist.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | IRP being assessed; reviewer info |
| 2 | General Info | TOC and conventions |
| 3 | Guide | How to interpret ratings |
| 4 | Summary | Dashboard with findings |
| 5 | Confirmation Review | 14 document-quality checks |
| 6 | Incident Response Plan Assessment | 14 IRP substantive checks |
| 7 | Verification Assessment | 14 verification checks |

## Files in this skill

```
incident-response-plan-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── irp_probe.py
│   ├── check_definitions.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── irp_checks.md
```
