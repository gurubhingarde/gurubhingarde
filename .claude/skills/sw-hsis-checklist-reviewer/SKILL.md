---
name: sw-hsis-checklist-reviewer
description: Review any ISO 26262 SW HSI Specification xlsx and produce a checklist with findings, evidence references, recommended actions, and visual dashboard. Probes source SW HSI workbook (sw-hsis-builder outputs and others), runs 32 checklist items across Confirmation Review (14 doc-quality checks), SW HSI Assessment (12 substantive checks per ISO 26262-6 §7 and ISO 26262-4 §6.4.6), and Verification Assessment (5 HSI-specific verification checks). Auto-fills FC/LC/PC/NO/NA for machine-verifiable checks, drafts low-confidence findings for subjective items. Does not modify source SW HSI. Use when user wants to review, audit, or assess any SW HSI Specification, or asks for SW HSI confirmation review or checklist.
---

# SW HSI Specification Checklist Reviewer

Automates the confirmation-measures review of ISO 26262 SW HSI Specifications. Opens the xlsx, extracts signals, handlers, debounce strategies, RTOS integration, and fault propagation rows. Checks whether every signal has an assigned handler, SWC allocation, calling RTOS task, debounce strategy (if safety-relevant), and supporting test cases.

## When to use this skill

Use whenever the user wants to:
- Review or audit a SW HSI Specification workbook
- Produce a confirmation-measures checklist for SW HSI
- Run a doc-quality assessment on SW HSI documents
- Get a roll-up of SW HSI quality (missing handler attrs, incomplete timing, test gaps)

## Workflow

### Step 1 — Get the SW HSI path

Ask the user for the SW HSI xlsx path. If they upload a folder, scan for `*.xlsx` and ask which is the SW HSI Specification.

### Step 2 — Generate the checklist

```bash
cd scripts
python generate_checklist.py <sw_hsis.xlsx> <output_checklist.xlsx>
python recalc.py <output_checklist.xlsx>  # optional; surfaces any errors
```

The script prints JSON summary with signal count, handler count, debounce strategies, and rating distribution.

### Step 3 — Walk the user through the review

Direct user attention in this order:

1. **Title** — confirm correct SW HSI Specification.
2. **Summary** — read statistics and Findings (NO and PC items).
3. **Confirmation Review** — focus on Assessment = "—" (pending) or "NO". Usually doc-quality issues.
4. **SW HSI Assessment** — focus on PC or NO. These are substantive gaps (missing handlers, SWC alloc, RTOS tasks, debounce, latency).
5. **Verification Assessment** — mostly Pending; requires external docs (timing analysis, RTOS scheduling, FMEA). Focus on any NO/PC.

### Step 4 — Iterate

When user updates SW HSI and re-runs:
- Generate fresh checklist (skill does not preserve edits from previous run).
- Compare old and new checklists for progress.

## Output structure (7 tabs)

| Tab | Purpose |
|-----|---------|
| Title | SW HSI being assessed; reviewer info |
| General Info | TOC and references |
| Guide | How to interpret ratings and obligations |
| Summary | Statistical roll-up with KPIs, pie chart, findings table |
| Confirmation Review | 14 generic doc-quality checks (ISO 26262-8 §10) |
| SW HSI Assessment | 12 substantive checks (signal handlers, SWC, RTOS, debounce, fault propagation per ISO 26262-6) |
| Verification Assessment | 5 SW HSI-specific verification checks |

## Auto-fill confidence

- **High**: Verified directly from xlsx (handler count, SWC allocation, RTOS task assignment, debounce presence).
- **Medium**: Inferred from xlsx with caveat (debounce parameters adequacy, latency compliance).
- **Low / draft**: Subjective or requires external artifact (debounce effectiveness, FRTI budget satisfaction, end-to-end timing).

## Scoring model

| Rating | Meaning |
|--------|---------|
| FC | Fully Compliant — evidence found, requirement satisfied |
| LC | Largely Compliant — mostly correct, minor gaps |
| PC | Partially Compliant — significant gaps identified |
| NO | Not Compliant — requirement not met; corrective action recommended |
| NA | Not Applicable — check does not apply |
| — | Pending — requires reviewer judgment |

## Common findings

1. **Missing handler function names** — signals present but no SW handler assigned. Fix: populate SW Handler Catalog tab.
2. **Incomplete SWC allocation** — handlers exist but not mapped to Software Components. Fix: add SWC column and allocate.
3. **No RTOS task identification** — handlers present but calling RTOS task unknown. Fix: populate Calling Task column.
4. **Missing debounce strategy** — safety-relevant signals lack debounce (N-of-M, time threshold). Fix: add Debounce Strategy tab.
5. **Incomplete fault propagation** — signals without documented failure modes or vehicle reactions. Fix: add Fault Propagation Maps tab.
6. **No initialization sequence** — startup and HW BIST coordination undocumented. Fix: add Init Sequence SW Side tab.
7. **Test coverage gaps** — handlers without test cases (nominal, fault injection, boundary, timing). Fix: add Test Cases tab.

## Files in this skill

```
sw-hsis-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py         # orchestrator + xlsx writer
│   ├── sw_hsis_probe.py              # SW HSI content extractor
│   ├── check_definitions.py          # canonical check list
│   ├── dashboard.py                  # Summary tab visualizations
│   ├── recalc.py
│   └── office/
└── references/
    ├── methodology.md
    └── sw_hsis_checks.md
```
