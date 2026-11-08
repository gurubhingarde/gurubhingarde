---
name: fmeda-checklist-reviewer
description: Technical reviewer for ISO 26262 FMEDA xlsx; verifies metric calculations (SPFM/LFM/PMHF), assumption completeness, catalog coverage, classification, DC allocation, and produces audit-ready checklist with visual dashboard. Automatic metric-target checks compare SPFM/LFM/PMHF against ASIL-specific ISO 26262-5 targets. Skill is independent and does not modify source FMEDA.
---

# FMEDA Checklist Reviewer

This skill turns FMEDA technical review — the most detail-intensive part of a hardware safety case — into a one-shot run that produces an audit-ready confirmation checklist with metric validation, gap findings, recommended actions, and roll-up statistics.

The skill is opinionated about **what to check** (ISO 26262-5 Section 8 confirmation set) and conservative about **what to assert**. Every metric-target check (SPFM, LFM, PMHF) is verified automatically by reading computed values from the FMEDA xlsx and comparing to per-ASIL targets. Subjective checks (mission consistency, FIT justification) are drafted for reviewer acceptance.

## When to Use This Skill

Use whenever the user wants to:
- Review or audit an FMEDA workbook
- Verify metric calculations and ASIL compliance
- Run a functional safety assessment on FMEDA
- Produce a confirmation-measures checklist
- Get technical gap analysis of failure mode coverage

The skill is the natural counterpart to `fmeda-builder` — `fmeda-builder` produces the artifact, `fmeda-checklist-reviewer` confirms it meets ISO 26262-5 requirements.

## Workflow

### Step 1 — Get the FMEDA Path

Ask the user for the FMEDA xlsx path. If they provide a folder, scan for `*.xlsx` and ask which is the FMEDA.

### Step 2 — Read References on First Use

- `references/methodology.md` — scoring conventions (FC/LC/PC/NO/NA), confidence levels, what the skill does
- `references/fmeda_checks.md` — each of 14 + 14 checks with confidence rationale
- `references/metric_targets.md` — ISO 26262-5 SPFM/LFM/PMHF targets per ASIL with calculations

### Step 3 — Generate the Checklist

```bash
python scripts/generate_checklist.py <fmeda.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional; detects formula errors
```

The script prints a JSON summary including computed metrics vs targets so you immediately see metric validation results.

### Step 4 — Walk the User Through the Review

The checklist xlsx has 7 tabs. Direct the user in this order:

1. **Title** — confirm the FMEDA being assessed is correct
2. **Summary** — read KPI tiles, compliance %, and Findings (NO and PC) list
3. **Confirmation Review** — focus on rows with Assessment = "—" (pending) or "NO"
4. **FMEDA Assessment** — **focus on rows #8–10 (metric targets)** — these are headline validations
5. **Verification Assessment** — most rows Pending (external Verification Plan required)

For each Pending row, reviewer accepts/refines the drafted finding. For PC/NO rows, reviewer reads Recommended Action and decides whether to update source FMEDA.

### Step 5 — Iterate

When the user updates the FMEDA and re-runs the skill:
- A new checklist is produced fresh; the skill v0.1 does not preserve manual edits
- Recommended workflow: keep old checklist for diff comparison, generate new one each time FMEDA changes

## Output Structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | FMEDA being assessed; reviewer info |
| 2 | General Info | TOC of checklist + references |
| 3 | Guide | How to interpret ratings, obligations, confidence |
| 4 | Summary | Statistical roll-up + Findings (NO/PC items) + charts |
| 5 | Confirmation Review | 14 generic doc-quality checks (ISO 26262-8 §10) |
| 6 | FMEDA Assessment | 14 substantive FMEDA checks (ISO 26262-5 §8) — **includes metric targets** |
| 7 | Verification Assessment | External verification checks (all Pending without external docs) |

## Auto-Fill Confidence Model

| Confidence | When Assigned | Examples |
|------------|---------------|----------|
| High | Verified directly from xlsx | "Author populated"; "All elements have FIT"; "SPFM 92% >= 90% target" |
| Medium | Inferred with caveat | "HW catalog 95% complete"; LFM calculation present but needs review |
| Low / Draft | Subjective or external artifact | "Mission consistent with vehicle program" (needs Item Definition); "FIT source justified" |

Every Low-confidence finding starts "(Auto-suggest, requires reviewer judgment)" so the reviewer knows human attention is required.

## Metric Target Checks (The Headline Value)

Checks **#8–10** in FMEDA Assessment are **the headline auto-verifications**:

- **Check #8 (SPFM)**: Reads computed SPFM from xlsx, compares to ASIL target (B≥90%, C≥97%, D≥99%)
- **Check #9 (LFM)**: Reads computed LFM from xlsx, compares to ASIL target (B≥60%, C≥80%, D≥90%)
- **Check #10 (PMHF)**: Reads computed PMHF (FIT) from xlsx, compares to ASIL target (B/C<100 FIT, D<10 FIT)

All three return **FC** if metrics meet targets, **NO** if failed. These checks use `openpyxl.load_workbook(..., data_only=True)` to read evaluated cell values, so formula-driven FMEDA worksheets are fully supported.

## Common Pitfalls to Flag

1. **Checklist is not a substitute for independent reviewer.** ISO 26262-2 requires confirmation reviews by an independent person (I1), team (I2), or org unit (I3) per ASIL. The skill is a workbench.

2. **FMEDA produced by fmeda-builder always passes metric consistency.** Metrics are formula-driven; if calculations are present, they are internally consistent. The skill verifies they meet *targets*.

3. **Many VA rows Pending is normal.** 4 of 4 VA checks describe external Verification Plan / Report. They are correctly marked Pending; reviewer ticks them off once verification docs are available.

4. **NO rows point at specific gaps.** Most common NO findings are missing assumptions, incomplete HW catalog, or metric shortfalls. These are actionable.

5. **The skill does not modify the source FMEDA.** All corrective actions go in Recommended Actions. The analyst decides whether to update the FMEDA and re-run.

## Files in This Skill

```
fmeda-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── fmeda_probe.py               # FMEDA content extractor
│   ├── check_definitions.py         # canonical checks with logic
│   ├── recalc.py
│   ├── dashboard.py                 # shared visual dashboard
│   └── office/
└── references/
    ├── methodology.md               # scoring conventions, what skill does/doesn't do
    ├── fmeda_checks.md              # detailed checklist reference (14+14 checks)
    └── metric_targets.md            # ISO 26262-5 SPFM/LFM/PMHF targets, examples
```

## Key Design Points

- **Automatic Metric Validation**: The three metric-target checks read computed values and compare to ISO 26262-5 targets. High-value auto-fill.
- **Uses openpyxl data_only=True**: Supports formula-heavy FMEDA worksheets; reads evaluated cells, not formulas.
- **Shared Dashboard Module**: Renders KPI tiles, pie chart, compliance bars, stacked ratings by section, findings table.
- **Reusable Check Pattern**: Same CheckDef / CheckResult pattern as hara-checklist-reviewer, tsc-checklist-reviewer.
