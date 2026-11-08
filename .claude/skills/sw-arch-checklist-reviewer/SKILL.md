---
name: sw-arch-checklist-reviewer
description: Run a confirmation-measures review on any ISO 26262 SW Architecture xlsx and produce a checklist with auto-filled findings, evidence references, and visual dashboard. Probes the source SW Architecture workbook, runs ~31 standard checks split across Confirmation Review (generic doc-quality), SW Architecture Assessment (ISO 26262-6 §7), and Verification Assessment (ISO 26262-8 §9). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source SW Architecture.
---

# SW Architecture Checklist Reviewer

This skill automates the confirmation-measures review of an ISO 26262 SW Architecture workbook (produced by `sw-arch-builder` or similar tools). The skill probes the SW Architecture xlsx, runs ~31 structured checklist requirements, and produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is conservative about assertions: every Fully-Compliant judgment cites specific evidence. Every subjective check is drafted with a "(Reviewer to verify)" preface. The skill never modifies the source SW Architecture; gaps land in the Recommended Actions column.

## When to use this skill

Use whenever the user wants to:
- Review or audit a SW Architecture workbook
- Produce a confirmation-measures checklist
- Run a SW architecture assessment (ISO 26262-6 §7 compliance)
- Run a verification assessment on SW architecture
- Get a roll-up of SW Architecture quality (gaps, missing elements, incomplete sections)

The skill is the natural counterpart to `sw-arch-builder` — `sw-arch-builder` produces the artifact, `sw-arch-checklist-reviewer` confirms it.

## Workflow

### Step 1 — Get the SW Architecture path

Ask the user for the SW Architecture xlsx path. If they upload a folder, scan for `*.xlsx` files and ask which one is the SW Architecture.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <sw_arch.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional; surfaces any errors
```

The script prints a JSON summary including counts of FC/LC/PC/NO/NA per tab.

### Step 3 — Walk the user through the review

The checklist xlsx has 7 tabs. Direct the user's attention in this order:

1. **Title** — confirm the SW Architecture being assessed is the right one.
2. **Summary** — read the statistics and the Findings (NO and PC) list. Executive view.
3. **Confirmation Review** — focus on rows with Assessment = empty or "NO". Usually title-page hygiene or config management.
4. **SW Architecture Assessment** — focus on rows with PC or NO. These are substantive gaps (component catalog, RTOS config, task scheduling, MPU, interfaces, etc.).
5. **Verification Assessment** — most will be Pending because they reference external Verification Plan / Spec / Report. Check for SW-arch-specific rows that can be evaluated.

For each Pending row the reviewer accepts or refines the drafted finding and sets Assessment. For each PC or NO row, the reviewer reads Recommended Action, decides whether to update the source SW Architecture, and re-runs.

### Step 4 — Iterate

When the user updates the SW Architecture and re-runs the skill:
- The new checklist is produced fresh (skill does not preserve manual edits to previous checklist).
- Recommended workflow: keep old checklist for diff comparison; run new checklist each time source changes.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | SW Architecture being assessed; reviewer info |
| 2 | General Info | TOC and references |
| 3 | Guide | How to interpret ratings, confidence, obligations |
| 4 | Summary | Statistical roll-up (KPIs, pie chart, bar charts) + Findings list (NO + PC items) |
| 5 | Confirmation Review | 14 generic doc-quality checks (ISO 26262-8 §10) |
| 6 | SW Architecture Assessment | 12 SW substantive checks (ISO 26262-6 §7) |
| 7 | Verification Assessment | 5 verification checks (ISO 26262-8 §9; most external) |

## Auto-fill confidence model

| Confidence | When the skill assigns this | Examples |
|------------|----------------------------|----------|
| High       | Verified directly from xlsx content | "Author and Approver populated"; "SW Component Catalog has 15 components" |
| Medium     | Inferred from xlsx with caveat | "RTOS present; reviewer to confirm scheduling support"; "Tasks defined; reviewer to verify schedulability" |
| Low / draft| Subjective or requires external artifact | "Independence strategy enforced" (design review); "Verification Plan addresses test methods" (external doc) |

The Findings cell of every Low-confidence draft starts with "(Auto-suggest, requires reviewer judgment)" so it is unambiguous to the reviewer that human judgment is required.

## Common pitfalls to flag

1. **Checklist is not a substitute for an independent reviewer.** ISO 26262-2 Clause 6.4.7 requires confirmation reviews to be performed by an independent person (I1), team (I2), or organisational unit (I3) depending on ASIL. The skill is a workbench, not the reviewer.

2. **Many VA rows pending is normal.** Most Verification Assessment checks describe external artifacts (Verification Plan, Test Specification, Test Report). They are correctly marked Pending; the reviewer verifies them against project documents.

3. **NO rows often point at title-page hygiene.** The most common NO findings are missing Title page fields (Status, real Author/Approver names). These are easy fixes that can move a checklist from PC to FC overall.

4. **The skill does not modify the source SW Architecture.** All corrective actions go in the Recommended Actions column. The analyst decides whether to update and re-run.

5. **WCET and schedulability are critical.** The skill checks that WCET (Worst-Case Execution Time) is populated for all tasks. Schedulability analysis (sum(WCET/Period) < 1.0 per priority) requires manual verification.

## Files in this skill

```
sw-arch-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── sw_arch_probe.py             # SW Architecture content extractor
│   ├── check_definitions.py         # canonical checklist with verification logic
│   ├── dashboard.py                 # shared visual dashboard for Summary tab
│   ├── recalc.py
│   └── office/
│       ├── __init__.py
│       └── soffice.py
└── references/
    ├── methodology.md               # scoring conventions and check categories
    └── sw_arch_checks.md            # detailed check catalog
```
