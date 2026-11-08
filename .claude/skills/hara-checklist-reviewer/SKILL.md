---
name: hara-checklist-reviewer
description: Run a confirmation-measures review on any ISO 26262 HARA xlsx and produce a completed checklist (TOMCO-style) with auto-filled findings, evidence references, recommended actions, and roll-up statistics. Probes the source HARA workbook (works on hara-builder outputs and best-effort on others), runs ~80 standard checklist requirements split across Confirmation Review (generic doc-quality), Functional Safety Assessment (per ISO 26262-3 Clause 7), and Verification Assessment (per ISO 26262-8 Clause 9). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source HARA. Use this skill whenever the user wants to review, audit, assess, or confirm a HARA workbook, or asks for a confirmation review or HARA checklist, even casual phrasings like 'check my HARA'. Always use this skill instead of producing a freeform review in chat.
---

# HARA Checklist Reviewer

This skill turns the most tedious part of an ISO 26262 confirmation review — opening the HARA, scrolling through 900 rows checking that every cell has a rationale, every safety goal has a safe state, every malfunction was considered — into a one-shot run that produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is opinionated about *what to check* (the standard ISO 26262 confirmation set) and conservative about *what to assert*. Every Fully-Compliant judgment cites the specific evidence the script found in the source HARA. Every subjective check is drafted with a "(Reviewer to verify)" preface so the human knows where their judgment is required. The skill never modifies the source HARA; gaps land in the Recommended Actions column.

## When to use this skill

Use whenever the user wants to:
- Review or audit a HARA workbook
- Produce a confirmation-measures checklist
- Run a functional safety assessment on a HARA
- Run a verification assessment on a HARA
- Get a roll-up of HARA quality (gaps, missing rationales, incomplete sections)

The skill is the natural counterpart to `hara-builder` — `hara-builder` produces the artifact, `hara-checklist-reviewer` confirms it.

## Workflow

### Step 1 — Get the HARA path

Ask the user for the HARA xlsx path. If they say "my folder" or upload a folder, scan the folder for `*.xlsx` files and ask which one is the HARA (skill v0.1 does not auto-discover; let the user pick).

### Step 2 — Read the references on first use

- `references/methodology.md` — scoring conventions (FC/LC/PC/NO/NA), confidence levels, what the skill does and does not do.
- `references/confirmation_review_checks.md` — what each of the 14 generic doc-quality checks verifies.
- `references/functional_safety_checks.md` — what each of the 24 substantive HARA checks verifies, with confidence rationale.
- `references/verification_checks.md` — why most VA checks are "external" (live in a separate Verification Plan) and which 5 (33a–e) are HARA-specific.

### Step 3 — Generate the checklist

```bash
python scripts/generate_checklist.py <hara.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional; the checklist has no formulas, but recalc surfaces any errors
```

The script prints a JSON summary including counts of FC/LC/PC/NO/NA/PENDING per tab so you immediately see auto-fill yield.

### Step 4 — Walk the user through the review

The checklist xlsx has 7 tabs. Direct the user's attention in this order:

1. **Title** — confirm the HARA being assessed is the right one.
2. **Summary** — read the statistics and the Findings (NO and PC) list. This is the executive view.
3. **Confirmation Review** — focus on the rows with Assessment = "—" (pending) or "NO". The Pending rows are usually subjective doc-quality items; the NO rows usually point at missing Title-page fields or missing revision history.
4. **Functional Safety Assessment** — focus on rows with Assessment = "PC" or "NO". These are the substantive gaps. The Pending rows for FSA #2, #3, #4, #9, #10, #14, #17 typically need the human to verify against external artifacts or apply judgment.
5. **Verification Assessment** — most of this tab will be Pending because it asks about a separate Verification Plan / Spec / Report. Focus on the HARA-specific rows 33a–e which the skill does evaluate.

For each Pending row the reviewer accepts or refines the drafted finding and sets the Assessment value. For each PC or NO row, the reviewer reads the Recommended Action, decides whether to update the source HARA, and re-runs the skill.

### Step 5 — Iterate

When the user updates the HARA and re-runs the skill:
- The new checklist is produced fresh; the skill v0.1 does not preserve manual edits to the previous checklist.
- Recommended workflow: keep the old checklist for diff comparison, run a new one each time the HARA changes.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | What HARA is being assessed; reviewer info |
| 2 | General Info | TOC of the checklist + references |
| 3 | Guide | How to interpret ratings, confidence, obligations |
| 4 | Summary | Statistical roll-up + Findings list (NO + PC items) |
| 5 | Confirmation Review | 14 generic doc-quality checks (ISO 26262-8 §10) |
| 6 | Functional Safety Assessment | 24 HARA substantive checks (ISO 26262-3 §7) |
| 7 | Verification Assessment | 44 verification checks (HARA-specific items 33a–e are the only ones the skill evaluates without external artifacts) |

## Auto-fill confidence model

| Confidence | When the skill assigns this | Examples |
|------------|----------------------------|----------|
| High       | Verified directly from xlsx content | "Author and Approver populated"; "All 900 rows have S, E, C populated" |
| Medium     | Inferred from xlsx with caveat | "Function list present; reviewer to confirm against Item Definition" |
| Low / draft| Subjective or requires external artifact | "Title covers scope" (subjective); "Verification Plan addresses methods" (external doc) |

The Findings cell of every Low-confidence draft starts with "(Auto-suggest, requires reviewer judgment)" so it is unambiguous to the reviewer that human attention is required.

## Common pitfalls to flag

1. **Checklist is not a substitute for an independent reviewer.** ISO 26262-2 Clause 6.4.7 requires confirmation reviews to be performed by an independent person (I1), team (I2), or organisational unit (I3) depending on ASIL. The skill is a workbench, not the reviewer.
2. **HARA produced by hara-builder always passes ASIL consistency (33e).** The ASIL column is formula-driven; recorded ASIL == derived ASIL by construction. The Findings cell notes this; reviewers should not interpret this as universal compliance for HARAs from other tools.
3. **Many VA rows pending is normal.** 32 of the 44 VA checks describe a Verification Plan / Spec / Report that lives outside the HARA xlsx. They are correctly marked Pending; the reviewer ticks them off against the project's verification documents.
4. **NO rows usually point at title-page hygiene.** The most common NO findings on a hara-builder output are missing Title-page fields (Status, real Author/Approver names instead of placeholders). These are easy fixes that take a HARA from PC to FC overall.
5. **The skill does not modify the source HARA.** All corrective actions go in the Recommended Actions column. The analyst decides whether to update the HARA and re-run.

## Files in this skill

```
hara-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── hara_probe.py                # best-effort HARA content extractor
│   ├── check_definitions.py         # the canonical check list with verification logic
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    ├── confirmation_review_checks.md
    ├── functional_safety_checks.md
    └── verification_checks.md
```
