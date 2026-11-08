---
name: item-def-checklist-reviewer
description: Run a confirmation-measures review on any ISO 26262 Item Definition xlsx and produce a completed checklist with auto-filled findings, evidence references, recommended actions, and roll-up statistics. Probes the source Item Definition workbook (works on item-definition-builder outputs and best-effort on others), runs ~24 standard checklist requirements split across Confirmation Review (generic doc-quality per ISO 26262-8 Clause 10), Item Definition Assessment (substantive per ISO 26262-3 Clause 5), and Verification Assessment (ISO 26262-8 Clause 9). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source Item Definition. Use this skill whenever the user wants to review, audit, assess, or confirm an Item Definition workbook, or asks for a confirmation review or Item Definition checklist. Always use this skill instead of producing a freeform review in chat.
---

# Item Definition Checklist Reviewer

This skill turns the rote work of reviewing an Item Definition — checking that title, scope, functions, interfaces, allocations, and assumptions are present and clear — into a one-shot run that produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is opinionated about what to check (the standard ISO 26262 Item Definition confirmation set per Clause 5 of Part 3) and conservative about what to assert. Every Fully-Compliant judgment cites the specific evidence found in the source Item Definition. Every subjective check is drafted with a "(Reviewer to verify)" preface so the human knows where judgment is required. The skill never modifies the source Item Definition; gaps land in the Recommended Actions column.

## When to use this skill

Use whenever the user wants to:
- Review or audit an Item Definition workbook
- Produce a confirmation-measures checklist
- Run a substantive assessment on an Item Definition
- Run a verification readiness check on an Item Definition
- Get a roll-up of Item Definition quality (gaps, missing sections, incomplete metadata)

The skill is the natural counterpart to item-definition-builder — item-definition-builder produces the artifact, item-def-checklist-reviewer confirms it.

## Workflow

### Step 1 — Get the Item Definition path

Ask the user for the Item Definition xlsx path. If they say "my folder" or upload a folder, scan for *.xlsx files and ask which one is the Item Definition.

### Step 2 — Read the references on first use

- references/methodology.md — scoring conventions (FC/LC/PC/NO/NA), confidence levels, what the skill does and does not do.
- references/item_def_checks.md — what each of the ~24 substantive checks verifies, with confidence rationale.

### Step 3 — Generate the checklist

```bash
python scripts/generate_checklist.py <item_def.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional; surfaces any errors
```

The script prints a JSON summary including counts of FC/LC/PC/NO/NA/Pending per tab so you immediately see auto-fill yield.

### Step 4 — Walk the user through the review

The checklist xlsx has 7 tabs. Direct the user's attention in this order:

1. **Title** — confirm the Item Definition being assessed is the right one.
2. **Summary** — read the statistics and the Findings (NO and PC) list. This is the executive view.
3. **Confirmation Review** — focus on rows with Assessment = "—" (pending) or "NO". Pending rows are typically subjective doc-quality items; NO rows point at missing Title-page fields or incomplete sections.
4. **Item Definition Assessment** — focus on rows with Assessment = "PC" or "NO". These are substantive gaps (missing functions, boundary, interfaces, allocations). Pending rows (#2, #3, #5, #6) typically need human judgment.
5. **Verification Assessment** — all rows are Pending because verification planning lives in external documents (Design Spec, Test Plan). The reviewer ticks them off against those artifacts.

For each Pending row the reviewer accepts or refines the drafted finding and sets the Assessment value. For each PC or NO row, the reviewer reads the Recommended Action, decides whether to update the source Item Definition, and re-runs the skill.

### Step 5 — Iterate

When the user updates the Item Definition and re-runs the skill:
- The new checklist is produced fresh; the skill does not preserve manual edits from the previous checklist.
- Recommended workflow: keep the old checklist for diff comparison, run a new one each time the Item Definition changes.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | Item Definition being assessed; reviewer info |
| 2 | General Info | TOC of the checklist + references |
| 3 | Guide | How to interpret ratings, confidence, obligations |
| 4 | Summary | Statistical roll-up + Findings list (NO + PC items) |
| 5 | Confirmation Review | 10 generic doc-quality checks (ISO 26262-8 §10) |
| 6 | Item Definition Assessment | 10 Item Definition substantive checks (ISO 26262-3 §5) |
| 7 | Verification Assessment | 3 verification readiness checks (ISO 26262-8 §9) |

## Auto-fill confidence model

| Confidence | When the skill assigns this | Examples |
|------------|----------------------------|----------|
| High       | Verified directly from xlsx content | "Author and Approver populated"; "All functions have descriptions"; "Revision set" |
| Medium     | Inferred from xlsx with caveat | "Function list present; reviewer to confirm against scope"; "Boundary has items but not detailed" |
| Low / draft| Subjective or requires external artifact | "Title describes scope" (subjective); "Test plan addresses all functions" (external doc) |

The Findings cell of every Low-confidence draft starts with "(Auto-suggest, requires reviewer judgment)" so it is unambiguous to the reviewer that human attention is required.

## Common pitfalls to flag

1. **Checklist is not a substitute for an independent reviewer.** ISO 26262-2 Clause 6.4.7 requires confirmation reviews to be performed by an independent person (I1), team (I2), or organisational unit (I3) depending on ASIL. The skill is a workbench, not the reviewer.
2. **Many VA rows pending is normal.** All 3 VA checks describe external verification artifacts (Design Spec, Test Plan, Test Report) that live outside the Item Definition xlsx. They are correctly marked Pending; the reviewer ticks them off against project documents.
3. **NO rows usually point at title-page hygiene or missing content.** Common NO findings on item-definition-builder output are missing Title-page fields (Status, real Author/Approver names) or missing required tabs. These are easy fixes that take an Item Definition from PC to FC overall.
4. **The skill does not modify the source Item Definition.** All corrective actions go in the Recommended Actions column. The analyst decides whether to update the Item Definition and re-run.

## Files in this skill

```
item-def-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── item_def_probe.py            # best-effort Item Definition content extractor
│   ├── check_definitions.py         # the canonical check list with verification logic
│   ├── dashboard.py                 # visual dashboard for Summary tab
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── item_def_checks.md
```

Always use this skill instead of producing a freeform review in chat.
