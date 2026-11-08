---
name: apqp-plan-checklist-reviewer
description: Review any APQP Plan xlsx and produce a completed checklist with auto-filled findings, evidence references, and recommended actions. Probes the source APQP Plan workbook (works on apqp-plan-builder outputs and best-effort on others), runs 32 standard checklist requirements split across Confirmation Review (14 generic doc-quality), APQP Assessment (12 per AIAG APQP Manual and IATF 16949), and Verification Assessment (6 external). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source APQP Plan. Use this skill whenever the user wants to review, audit, assess, or confirm an APQP Plan workbook.
---

# APQP Plan Checklist Reviewer

This skill turns the most tedious part of an APQP Plan audit into a one-shot run that produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is opinionated about *what to check* (the standard AIAG APQP Manual + IATF 16949 confirmation set) and conservative about *what to assert*. Every Fully-Compliant judgment cites the specific evidence the script found in the source APQP Plan. Every subjective check is drafted with a "(Reviewer to verify)" preface so the human knows where their judgment is required. The skill never modifies the source APQP Plan; gaps land in the Recommended Actions column.

## When to use this skill

Use whenever the user wants to:
- Review or audit an APQP Plan workbook
- Produce a confirmation-measures checklist for APQP
- Run a program readiness assessment on an APQP Plan
- Get a roll-up of APQP Plan quality (gaps, missing ownership, incomplete phases)

The skill is the natural counterpart to `apqp-plan-builder` — `apqp-plan-builder` produces the artifact, `apqp-plan-checklist-reviewer` confirms it.

## Workflow

### Step 1 — Get the APQP Plan path

Ask the user for the APQP Plan xlsx path. If they say "my folder" or upload a folder, scan the folder for `*.xlsx` files and ask which one is the APQP Plan.

### Step 2 — Read the references on first use

- `references/methodology.md` — scoring conventions (FC/LC/PC/NO/NA), confidence levels, what the skill does and does not do.
- `references/apqp_checks.md` — what each of the 32 checks verifies, with confidence rationale.

### Step 3 — Generate the checklist

```bash
cd scripts
python generate_checklist.py <apqp_plan.xlsx> <output_checklist.xlsx>
python recalc.py <output_checklist.xlsx>      # optional; surfaces any formula errors
```

The script prints a JSON summary including counts of FC/LC/PC/NO/NA/PENDING per tab.

### Step 4 — Walk the user through the review

The checklist xlsx has 7 tabs. Direct the user's attention in this order:

1. **Title** — confirm the APQP Plan being assessed is the right one.
2. **Summary** — read the statistics and the Findings (NO and PC) list. This is the executive view.
3. **Confirmation Review** — focus on rows with Assessment = "—" (pending) or "NO". These point at missing Title-page fields or incomplete revision history.
4. **APQP Assessment** — focus on rows with Assessment = "PC" or "NO". These are the substantive gaps (missing phases, incomplete deliverables, unassigned owners). The highest-value checks are Program Manager/Quality Lead assignment and cross-functional team completeness.
5. **Verification Assessment** — most rows are Pending because they ask about separate external processes (PPL analysis, supplier capability, customer approval, etc.). All are marked as external; the reviewer ticks them off against the project's external documents.

For each Pending row the reviewer accepts or refines the drafted finding and sets the Assessment value. For each PC or NO row, the reviewer reads the Recommended Action, decides whether to update the source APQP Plan, and re-runs the skill.

### Step 5 — Iterate

When the user updates the APQP Plan and re-runs the skill:
- The new checklist is produced fresh; the skill does not preserve manual edits to the previous checklist.
- Recommended workflow: keep the old checklist for diff comparison, run a new one each time the APQP Plan changes.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | APQP Plan being assessed; reviewer info |
| 2 | General Info | TOC of the checklist + references |
| 3 | Guide | How to interpret ratings, confidence, obligations |
| 4 | Summary | Statistical roll-up + Findings list (NO + PC items) |
| 5 | Confirmation Review | 14 generic doc-quality checks |
| 6 | APQP Assessment | 12 APQP substantive checks per AIAG + IATF 16949 |
| 7 | Verification Assessment | 6 verification/launch checks (external) |

## Auto-fill confidence model

| Confidence | When the skill assigns this | Examples |
|------------|----------------------------|----------|
| High       | Verified directly from xlsx content | "Author and Approver populated"; "All phases have deliverables" |
| Medium     | Inferred from xlsx with caveat | "Phase deliverables present; reviewer to confirm completeness" |
| Low / draft| Subjective or requires external artifact | "Title covers scope" (subjective); "PPL analysis complete" (external doc) |

The Findings cell of every Low-confidence draft starts with "(Auto-suggest, requires reviewer judgment)" so it is unambiguous to the reviewer that human attention is required.

## Files in this skill

```
apqp-plan-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── apqp_probe.py                # best-effort APQP Plan content extractor
│   ├── check_definitions.py         # canonical check list with verification logic
│   ├── dashboard.py                 # shared visual dashboard for Summary tab
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── apqp_checks.md
```
