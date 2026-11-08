---
name: safety-plan-checklist-reviewer
description: Run a confirmation-measures review on any ISO 26262 Safety Plan xlsx and produce a completed checklist (TOMCO-style) with auto-filled findings, evidence references, and recommended actions. Probes the source Safety Plan workbook (works on safety-plan-builder outputs and best-effort on others), runs 34 standard checklist requirements split across Confirmation Review (14 generic doc-quality), Safety Plan Assessment (14 per ISO 26262-2 clause 6), and Verification Assessment (6 external). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source Safety Plan. Use this skill whenever the user wants to review, audit, assess, or confirm a Safety Plan workbook.
---

# Safety Plan Checklist Reviewer

This skill turns the most tedious part of an ISO 26262 confirmation review — opening the Safety Plan, scrolling through roles, work products, and confirmation reviews, checking that every cell is populated with proper independence levels matching ASIL — into a one-shot run that produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is opinionated about *what to check* (the standard ISO 26262-2 §6 confirmation set) and conservative about *what to assert*. Every Fully-Compliant judgment cites the specific evidence the script found in the source Safety Plan. Every subjective check is drafted with a "(Reviewer to verify)" preface so the human knows where their judgment is required. The skill never modifies the source Safety Plan; gaps land in the Recommended Actions column.

## When to use this skill

Use whenever the user wants to:
- Review or audit a Safety Plan workbook
- Produce a confirmation-measures checklist
- Run a functional safety assessment on a Safety Plan
- Run a verification assessment on a Safety Plan
- Get a roll-up of Safety Plan quality (gaps, missing ownership, incomplete independence assignments)

The skill is the natural counterpart to `safety-plan-builder` — `safety-plan-builder` produces the artifact, `safety-plan-checklist-reviewer` confirms it.

## Workflow

### Step 1 — Get the Safety Plan path

Ask the user for the Safety Plan xlsx path. If they say "my folder" or upload a folder, scan the folder for `*.xlsx` files and ask which one is the Safety Plan.

### Step 2 — Read the references on first use

- `references/methodology.md` — scoring conventions (FC/LC/PC/NO/NA), confidence levels, what the skill does and does not do.
- `references/safety_plan_checks.md` — what each of the 34 checks verifies, with confidence rationale.

### Step 3 — Generate the checklist

```bash
cd scripts
python generate_checklist.py <safety_plan.xlsx> <output_checklist.xlsx>
python recalc.py <output_checklist.xlsx>      # optional; surfaces any formula errors
```

The script prints a JSON summary including counts of FC/LC/PC/NO/NA/PENDING per tab so you immediately see auto-fill yield.

### Step 4 — Walk the user through the review

The checklist xlsx has 7 tabs. Direct the user's attention in this order:

1. **Title** — confirm the Safety Plan being assessed is the right one.
2. **Summary** — read the statistics and the Findings (NO and PC) list. This is the executive view.
3. **Confirmation Review** — focus on rows with Assessment = "—" (pending) or "NO". These point at missing Title-page fields or incomplete revision history.
4. **Safety Plan Assessment** — focus on rows with Assessment = "PC" or "NO". These are the substantive gaps (missing roles, uncovered work products, independence mismatches). The highest-value check is #9 (independence level must match ASIL).
5. **Verification Assessment** — most rows are Pending because they ask about a separate Verification Plan / Report. All are marked as external; the reviewer ticks them off against the project's verification documents.

For each Pending row the reviewer accepts or refines the drafted finding and sets the Assessment value. For each PC or NO row, the reviewer reads the Recommended Action, decides whether to update the source Safety Plan, and re-runs the skill.

### Step 5 — Iterate

When the user updates the Safety Plan and re-runs the skill:
- The new checklist is produced fresh; the skill does not preserve manual edits to the previous checklist.
- Recommended workflow: keep the old checklist for diff comparison, run a new one each time the Safety Plan changes.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | Safety Plan being assessed; reviewer info |
| 2 | General Info | TOC of the checklist + references |
| 3 | Guide | How to interpret ratings, confidence, obligations |
| 4 | Summary | Statistical roll-up + Findings list (NO + PC items) |
| 5 | Confirmation Review | 14 generic doc-quality checks (ISO 26262-8 §10) |
| 6 | Safety Plan Assessment | 14 Safety Plan substantive checks (ISO 26262-2 §6) |
| 7 | Verification Assessment | 6 verification checks (external; defined per ISO 26262-8 §9) |

## Auto-fill confidence model

| Confidence | When the skill assigns this | Examples |
|------------|----------------------------|----------|
| High       | Verified directly from xlsx content | "Author and Approver populated"; "All 10 roles assigned" |
| Medium     | Inferred from xlsx with caveat | "Work products present; reviewer to confirm against Item Definition" |
| Low / draft| Subjective or requires external artifact | "Title covers scope" (subjective); "Verification Plan addresses methods" (external doc) |

The Findings cell of every Low-confidence draft starts with "(Auto-suggest, requires reviewer judgment)" so it is unambiguous to the reviewer that human attention is required.

## Files in this skill

```
safety-plan-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── safety_plan_probe.py         # best-effort Safety Plan content extractor
│   ├── check_definitions.py         # the canonical check list with verification logic
│   ├── dashboard.py                 # shared visual dashboard for Summary tab
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── safety_plan_checks.md
```
