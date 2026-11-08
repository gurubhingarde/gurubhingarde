---
name: safety-case-checklist-reviewer
description: Run a Safety Case confirmation review on any ISO 26262 Safety Case xlsx and produce a checklist with auto-filled findings, evidence references, and visual dashboard. Probes the source Safety Case, runs 31 standard checklist items across Confirmation Review (doc quality), Safety Case Assessment (ISO 26262-2 §6.5 argument chain verification), and Verification Assessment. Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source Safety Case. Use this skill whenever the user wants to review, audit, assess, or confirm a Safety Case workbook.
---

# Safety Case Checklist Reviewer

This skill turns Safety Case confirmation review into a one-shot run that produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions. Perfect for verifying that the Safety Case argument chain is complete and traceable (Top Claim → Safety Goals → FSR → HW metrics → SW verification).

The skill is opinionated about *what to check* (ISO 26262-2 §6.5 Safety Case Assessment) and conservative about *what to assert*. Every Fully-Compliant judgment cites specific evidence found in the source Safety Case. Every subjective check is drafted with a "(Auto-suggest)" preface so the human knows where their judgment is required. The skill never modifies the source Safety Case; gaps land in the Recommended Actions column.

## When to use this skill

Use whenever the user wants to:
- Review or audit a Safety Case workbook
- Produce a Safety Case confirmation-measures checklist
- Verify the Safety Case argument chain (top claim → sub-claims → evidence)
- Run a functional safety assessment on a Safety Case
- Get a roll-up of Safety Case quality (gaps, missing metrics, incomplete sections)

The skill is the natural follow-on to `safety-case-builder` — `safety-case-builder` produces the artifact, `safety-case-checklist-reviewer` confirms it.

## Workflow

### Step 1 — Get the Safety Case path

Ask the user for the Safety Case xlsx path. If they upload a folder, scan for `*.xlsx` files and ask which one is the Safety Case.

### Step 2 — Read the references on first use

- `references/methodology.md` — scoring conventions (FC/LC/PC/NO/NA), confidence levels.
- `references/safety_case_checks.md` — what each of the 31 checks verifies.

### Step 3 — Generate the checklist

```bash
python scripts/generate_checklist.py <safety_case.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional
```

The script prints a JSON summary with counts per tab so you immediately see auto-fill yield.

### Step 4 — Walk the user through the review

The checklist xlsx has 7 tabs. Direct attention in this order:

1. **Title** — confirm the Safety Case being assessed is the right one.
2. **Summary** — read the statistics and Findings (NO and PC) list.
3. **Confirmation Review** — focus on rows with Assessment = blank or NO. These are usually doc-quality items.
4. **Safety Case Assessment** — focus on rows with Assessment = PC or NO. These are the substantive gaps.
5. **Verification Assessment** — most rows are Pending; these describe external verification documents.

For each Pending row, accept or refine the drafted finding. For each PC or NO row, read the Recommended Action and decide whether to update the source Safety Case and re-run.

### Step 5 — Iterate

When the user updates the Safety Case and re-runs the skill:
- The new checklist is produced fresh; the skill does not preserve manual edits to the previous checklist.
- Recommended workflow: keep the old checklist for diff comparison, run a new one each time the Safety Case changes.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | Safety Case being assessed; reviewer info |
| 2 | General Info | TOC and document references |
| 3 | Guide | How to interpret ratings and use the checklist |
| 4 | Summary | Statistical roll-up + Findings list (NO + PC items) with charts |
| 5 | Confirmation Review | 14 generic doc-quality checks (ISO 26262-8 §10) |
| 6 | Safety Case Assessment | 12 Safety Case substantive checks (ISO 26262-2 §6.5) |
| 7 | Verification Assessment | 5 verification checks specific to Safety Case |

## Auto-fill confidence model

| Confidence | When the skill assigns this | Examples |
|------------|----------------------------|----------|
| High | Verified directly from xlsx content | "All 12 safety goals populated"; "FSR-TSR traceability complete" |
| Medium | Inferred from xlsx with caveat | "Safety goals present; reviewer to confirm argument coverage" |
| Low / draft | Subjective or requires external artifact | "Signoff block detected; verify all signers" (subjective) |

## Common pitfalls to flag

1. **Checklist is not a substitute for independent review.** ISO 26262-2 §6.4.7 requires confirmation reviews by an independent person (I1), team (I2), or org unit (I3) depending on ASIL. The skill is a workbench, not the reviewer.
2. **Argument chain is complex.** The Safety Case ties together HARA, FSC, TSC, HW metrics, SW verification, and tool qualification. The checklist verifies cross-references exist; reviewers must verify each linked document is complete.
3. **Open items and risks must be accepted.** The checklist checks that all open items have documented risk assessment. If any are not accepted, the Safety Case assessment cannot be granted.
4. **Signoff is mandatory.** The Assessment Conclusion must carry signoff blocks for Functional Safety Manager, Project Manager, and Assessor — not just placeholders.

## Files in this skill

```
safety-case-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── safety_case_probe.py         # best-effort Safety Case content extractor
│   ├── check_definitions.py         # the canonical check list with verification logic
│   ├── recalc.py                    # optional: recalc xlsx formulas
│   └── office/
│       ├── __init__.py
│       └── soffice.py               # optional: LibreOffice helper
└── references/
    ├── methodology.md
    └── safety_case_checks.md
```
