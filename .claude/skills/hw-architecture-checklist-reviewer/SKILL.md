---
name: hw-architecture-checklist-reviewer
description: Run a confirmation-measures review on any ISO 26262 HW Architecture xlsx and produce a checklist with auto-filled findings, evidence references, recommended actions, and visual dashboard. Probes the source HW Architecture workbook, runs ~29 standard checks split across Confirmation Review (generic doc-quality), HW Architecture Assessment (ISO 26262-5 §7), and Verification Assessment (ISO 26262-8 §9). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source HW Architecture. Use this skill whenever the user wants to review, audit, assess, or confirm a HW Architecture workbook, or asks for a confirmation review or checklist, even casual phrasings like 'check my HW arch'.
---

# HW Architecture Checklist Reviewer

This skill automates the confirmation-measures review of an ISO 26262 HW Architecture workbook (produced by `hw-architecture-builder` or similar tools). The skill probes the HW Architecture xlsx, runs ~29 structured checklist requirements, and produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is conservative about assertions: every Fully-Compliant judgment cites specific evidence. Every subjective check is drafted with a "(Reviewer to verify)" preface. The skill never modifies the source HW Architecture; gaps land in the Recommended Actions column.

## When to use this skill

Use whenever the user wants to:
- Review or audit a HW Architecture workbook
- Produce a confirmation-measures checklist
- Run a HW architecture assessment (ISO 26262-5 §7 compliance)
- Run a verification assessment on HW architecture
- Get a roll-up of HW Architecture quality (gaps, missing elements, incomplete sections)

The skill is the natural counterpart to `hw-architecture-builder` — `hw-architecture-builder` produces the artifact, `hw-architecture-checklist-reviewer` confirms it.

## Workflow

### Step 1 — Get the HW Architecture path

Ask the user for the HW Architecture xlsx path. If they upload a folder, scan for `*.xlsx` files and ask which one is the HW Architecture.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <hw_arch.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional; surfaces any errors
```

The script prints a JSON summary including counts of FC/LC/PC/NO/NA/PENDING per tab.

### Step 3 — Walk the user through the review

The checklist xlsx has 7 tabs. Direct the user's attention in this order:

1. **Title** — confirm the HW Architecture being assessed is the right one.
2. **Summary** — read the statistics and the Findings (NO and PC) list. Executive view.
3. **Confirmation Review** — focus on rows with Assessment = "—" (pending) or "NO". Usually title-page hygiene or config management.
4. **HW Architecture Assessment** — focus on rows with PC or NO. These are substantive gaps (catalog, power, clock, traceability, etc.).
5. **Verification Assessment** — most will be Pending because they reference external Verification Plan / Spec / Report. Check for HARA-specific rows that can be evaluated.

For each Pending row the reviewer accepts or refines the drafted finding and sets Assessment. For each PC or NO row, the reviewer reads Recommended Action, decides whether to update the source HW Architecture, and re-runs.

### Step 4 — Iterate

When the user updates the HW Architecture and re-runs the skill:
- The new checklist is produced fresh (skill does not preserve manual edits to previous checklist).
- Recommended workflow: keep old checklist for diff comparison; run new checklist each time source changes.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | HW Architecture being assessed; reviewer info |
| 2 | General Info | TOC and references |
| 3 | Guide | How to interpret ratings, confidence, obligations |
| 4 | Summary | Statistical roll-up (KPIs, pie chart, bar charts) + Findings list (NO + PC items) |
| 5 | Confirmation Review | 12 generic doc-quality checks (ISO 26262-8 §10) |
| 6 | HW Architecture Assessment | 12 HW substantive checks (ISO 26262-5 §7) |
| 7 | Verification Assessment | 5 verification checks (ISO 26262-8 §9; most external) |

## Auto-fill confidence model

| Confidence | When the skill assigns this | Examples |
|------------|----------------------------|----------|
| High       | Verified directly from xlsx content | "Author and Approver populated"; "HW Element Catalog has 15 elements" |
| Medium     | Inferred from xlsx with caveat | "Power rails present; reviewer to confirm voltage and monitor detail" |
| Low / draft| Subjective or requires external artifact | "Independence strategy enforced" (design review); "Verification Plan addresses methods" (external doc) |

The Findings cell of every Low-confidence draft starts with "(Auto-suggest, requires reviewer judgment)" so it is unambiguous to the reviewer that human judgment is required.

## Common pitfalls to flag

1. **Checklist is not a substitute for an independent reviewer.** ISO 26262-2 Clause 6.4.7 requires confirmation reviews to be performed by an independent person (I1), team (I2), or organisational unit (I3) depending on ASIL. The skill is a workbench, not the reviewer.

2. **Many VA rows pending is normal.** Most Verification Assessment checks describe external artifacts (Verification Plan, Test Specification, Test Report). They are correctly marked Pending; the reviewer verifies them against project documents.

3. **NO rows often point at title-page hygiene.** The most common NO findings are missing Title page fields (Status, real Author/Approver names). These are easy fixes that can move a checklist from PC to FC overall.

4. **The skill does not modify the source HW Architecture.** All corrective actions go in the Recommended Actions column. The analyst decides whether to update and re-run.

5. **Independence verification is qualitative.** The skill checks that TSC references exist; actual independence of fault domains requires design review (electrical isolation, different packages, separate rails, etc.).

## Files in this skill

```
hw-architecture-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── hw_arch_probe.py             # HW Architecture content extractor
│   ├── check_definitions.py         # canonical checklist with verification logic
│   ├── dashboard.py                 # shared visual dashboard for Summary tab
│   ├── recalc.py
│   └── office/
│       ├── __init__.py
│       └── soffice.py
└── references/
    └── methodology.md               # scoring conventions and check categories
```
