---
name: hw-safety-reqs-checklist-reviewer
description: Run a confirmation-measures review on any ISO 26262 HW Safety Requirements xlsx and produce a completed checklist with auto-filled findings, evidence references, recommended actions, and roll-up statistics. Probes the source HW-SR xlsx, runs 29 standard checks split across Confirmation Review (14 doc-quality items), HW Safety Requirements Assessment (12 ISO 26262-5 §6 checks), and Verification Assessment (3 HW-SR-specific items). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source HW-SR. Use this whenever reviewing, auditing, or confirming an HW-SR workbook.
---

# HW Safety Requirements Checklist Reviewer

This skill turns the tedious part of an ISO 26262 HW-SR confirmation review — opening the workbook, scrolling through all requirements checking that every HW-SR has ASIL, allocated element, verification method, target DC — into a one-shot run that produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is opinionated about *what to check* (standard ISO 26262-5 confirmation set) and conservative about *what to assert*. Every Fully-Compliant judgment cites the specific evidence found in the source HW-SR. Every subjective check is drafted with a "(Reviewer to verify)" preface so you know where your judgment is required. The skill never modifies the source HW-SR; gaps land in Recommended Actions.

## When to use this skill

Use whenever you need to:
- Review or audit an HW-SR workbook
- Produce a confirmation-measures checklist for ISO 26262 compliance
- Run a HW Safety Requirements Assessment on HW-SRs
- Run a verification assessment on HW-SR coverage and completeness
- Get a roll-up of HW-SR quality (gaps, missing allocations, incomplete sections)

## Workflow

### Step 1 — Get the HW-SR path

Ask the user for the HW-SR xlsx path. If they say "my folder" or upload a folder, scan for `*.xlsx` files and ask which one is the HW-SR.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <hw_sr.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional
```

The script prints a JSON summary of FC/LC/PC/NO/NA/PENDING counts per tab.

### Step 3 — Walk the user through review

The checklist xlsx has 7 tabs. Direct attention in this order:

1. **Title** — confirm the HW-SR being assessed is the right one
2. **Summary** — read statistics and key findings (NO and PC items)
3. **Confirmation Review** — focus on rows with Assessment "—" (pending) or "NO"
4. **HW-SR Assessment** — substantive gaps. Focus on PC and NO findings
5. **Verification Assessment** — mostly external Verification Plan. Focus on HW-SR-specific rows 33a–e

For each Pending row the reviewer accepts or refines the finding and sets Assessment. For each PC or NO row, decide whether to update the source HW-SR and re-run.

### Step 4 — Iterate

When the user updates the HW-SR and re-runs:
- A new checklist is produced fresh (v0.1 does not preserve manual edits)
- Recommended workflow: keep old checklist for diff comparison, run new one each time

## Output structure (7 tabs)

| Tab | Purpose |
|-----|---------|
| Title | What HW-SR is being assessed; checklist metadata |
| General Info | TOC of checklist, references |
| Guide | How to interpret ratings, confidence, workflow |
| Summary | Statistical roll-up + Findings list (NO + PC items) |
| Confirmation Review | 14 generic doc-quality checks (ISO 26262-8 §10) |
| HW-SR Assessment | 12 substantive checks per ISO 26262-5 §6 |
| Verification Assessment | 22 verification checks; 5 HW-SR-specific items (33a–e) |

## Auto-fill confidence model

| Confidence | When assigned | Examples |
|------------|---------------|----------|
| High | Verified directly from xlsx | "All 42 HW-SRs have ASIL"; "HW-TSR count = 8" |
| Medium | Inferred from xlsx with caveat | "Failure mode mapping present; reviewer confirm coverage" |
| Low / draft | Subjective or requires external | "Verification methods appropriate for ASIL (reviewer verify)" |

Every Low-confidence draft starts with "(Auto-suggest, requires reviewer judgment)" so you know human attention is required.

## Common pitfalls

1. **Checklist is not a substitute for an independent reviewer.** ISO 26262-2 Clause 6.4.7 requires reviews by independent person (I1) or team (I2+). The skill is a workbench.
2. **Many VA rows pending is normal.** Most VA checks describe an external Verification Plan. They are correctly marked Pending; you verify them against project docs.
3. **NO rows usually point at title-page hygiene.** Common gaps are missing Status, Author/Approver, Revision. These are easy fixes.
4. **The skill does not modify the source.** All corrective actions go in Recommended Actions column. You decide whether to update the source and re-run.

## Files in this skill

```
hw-safety-reqs-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── hw_sr_probe.py               # HW-SR content extractor
│   ├── check_definitions.py         # canonical checks with verification logic
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── hw_sr_checks.md
```
