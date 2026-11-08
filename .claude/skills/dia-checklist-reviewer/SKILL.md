---
name: dia-checklist-reviewer
description: Run a confirmation-measures review on any ISO 26262 DIA xlsx and produce a completed checklist with auto-filled findings, evidence references, recommended actions, and roll-up statistics. Probes the source DIA workbook (works on dia-builder outputs and best-effort on others), runs 33 standard checklist requirements split across Confirmation Review (14 generic doc-quality), DIA Assessment (14 substantive per ISO 26262-8 Section 5), and Verification Assessment (5 external governance). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source DIA. Use this skill whenever the user wants to review, audit, assess, or confirm a DIA workbook, or asks for a confirmation review or DIA checklist.
---

# DIA Checklist Reviewer

This skill turns the tedious part of a DIA confirmation review — opening the agreement, verifying all parties have roles assigned, checking RACI completeness, confirming communication and joint review schedules — into a one-shot run that produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is opinionated about what to check (the standard ISO 26262-8 Section 5 agreement requirements) and conservative about what to assert. Every Fully-Compliant judgment cites specific evidence found in the source DIA. Every subjective check is drafted with a "(Reviewer to verify)" preface so the human knows where their judgment is required. The skill never modifies the source DIA; gaps land in the Recommended Actions column.

## When to use this skill

Use whenever the user wants to:
- Review or audit a DIA workbook
- Produce a confirmation-measures checklist for a DIA
- Run a functional safety assessment on a DIA
- Run a verification assessment on a DIA
- Get a roll-up of DIA quality (gaps in RACI, missing FuSa contacts, incomplete communication protocol)

The skill is the natural counterpart to `dia-builder` — `dia-builder` produces the artifact, `dia-checklist-reviewer` confirms it.

## Workflow

### Step 1 — Get the DIA path

Ask the user for the DIA xlsx path. If they say "my folder" or upload a folder, scan the folder for `*.xlsx` files and ask which one is the DIA.

### Step 2 — Read the references on first use

- `references/methodology.md` — scoring conventions (FC/LC/PC/NO/NA), confidence levels.
- `references/dia_checks.md` — what each of the 33 checks verifies, with substantive focus on the 14 RACI / parties / communication checks.

### Step 3 — Generate the checklist

```bash
python scripts/generate_checklist.py <dia.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional
```

The script prints a JSON summary including counts of FC/LC/PC/NO/NA/PENDING per tab so you immediately see auto-fill yield.

### Step 4 — Walk the user through the review

The checklist xlsx has 7 tabs. Direct the user's attention in this order:

1. **Title** — confirm the DIA being assessed is the right one.
2. **Summary** — read the statistics and the Findings (NO and PC) list.
3. **Confirmation Review** — focus on rows with Assessment = "NO". These usually point at missing Title-page fields or incomplete revision history.
4. **DIA Assessment** — focus on rows with Assessment = "PC" or "NO". These are the substantive gaps (missing FuSa contacts, incomplete RACI, no communication protocol). The Pending rows for items requiring external document reference can be reviewed offline.
5. **Verification Assessment** — all external items; reviewer ticks them off against project governance and verification evidence.

For each Pending row the reviewer accepts or refines the drafted finding and sets the Assessment value. For each PC or NO row, the reviewer reads the Recommended Action, decides whether to update the source DIA, and re-runs the skill.

### Step 5 — Iterate

When the user updates the DIA and re-runs the skill:
- The new checklist is produced fresh; the skill does not preserve manual edits to the previous checklist.
- Recommended workflow: keep the old checklist for diff comparison, run a new one each time the DIA changes.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | DIA being assessed; reviewer info |
| 2 | General Info | TOC of the checklist + references |
| 3 | Guide | How to interpret ratings, confidence, obligations |
| 4 | Summary | Statistical roll-up + Findings list (NO + PC items) + KPI dashboard |
| 5 | Confirmation Review | 14 generic doc-quality checks (ISO 26262-8 §10) |
| 6 | DIA Assessment | 14 substantive agreement checks (ISO 26262-8 §5) |
| 7 | Verification Assessment | 5 external governance / verification checks |

## Auto-fill confidence model

| Confidence | When the skill assigns this | Examples |
|------------|----------------------------|----------|
| High       | Verified directly from xlsx content | "All 4 parties identified with roles"; "RACI matrix covers 6/7 major WPs" |
| Medium     | Inferred from xlsx with caveat | "Parties list present; reviewer to verify roles match project" |
| Low / draft| Subjective or requires external artifact | "Communication protocol text readable; reviewer to confirm cadence/escalation are acceptable" |

## Common pitfalls to flag

1. **DIA Assessment checks 1–6 are the highest-value findings.** Incomplete RACI, missing FuSa contacts, duplicate Accountable parties, and missing Responsible assignments are showstoppers per ISO 26262. The skill is rigorous about detecting these.
2. **Checklist is not a substitute for independent review.** ISO 26262-2 Clause 6.4.7 requires confirmation reviews by an independent person (I1), team (I2), or organisational unit (I3) depending on ASIL. The skill is a workbench, not the reviewer.
3. **Many VA rows pending is normal.** 5 of the 5 VA checks describe external Verification Plan / Governance / Meeting evidence that lives outside the DIA xlsx. They are correctly marked Pending; the reviewer ticks them off against project governance documents.
4. **NO rows usually point at missing populated fields.** The most common NO findings on a dia-builder output are Title-page hygiene, missing FuSa contacts, or incomplete RACI rows. These are easy fixes.
5. **The skill does not modify the source DIA.** All corrective actions go in the Recommended Actions column. The analyst decides whether to update the DIA and re-run.

## Files in this skill

```
dia-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── dia_probe.py                 # DIA content extractor
│   ├── check_definitions.py         # canonical checklist with verification logic
│   ├── recalc.py
│   ├── dashboard.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── dia_checks.md
```
