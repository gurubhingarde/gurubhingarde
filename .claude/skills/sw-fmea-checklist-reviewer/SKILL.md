---
name: sw-fmea-checklist-reviewer
description: Technical reviewer for ISO 26262-9 SW FMEA xlsx. Verifies failure mode coverage, severity/frequency/detection ratings, residual risk acceptance per ASIL threshold (auto-verification), assumption completeness, and produces audit-ready checklist with visual dashboard. Automatic residual risk checks validate post-mitigation risk against per-ASIL limits (D at most 1, C at most 3, B at most 9, A at most 27). Skill is independent and does not modify source SW FMEA. Use this skill whenever the user wants to review, audit, or confirm a SW FMEA workbook, even casual phrasings like 'check my SW FMEA'. Always use this skill instead of producing a freeform review in chat.
---

# SW FMEA Checklist Reviewer

This skill turns SW FMEA technical review — the detail-intensive foundational step of a software safety case — into a one-shot run that produces an audit-ready confirmation checklist with residual risk validation, gap findings, recommended actions, and roll-up statistics.

The skill is opinionated about **what to check** (ISO 26262-9 Section 8 confirmation set) and conservative about **what to assert**. Residual risk acceptance is verified automatically by reading post-mitigation risk values from the SW FMEA xlsx and comparing to per-ASIL thresholds. Subjective checks (methodology consistency, test coverage justification) are drafted for reviewer acceptance.

## When to Use This Skill

Use whenever the user wants to:
- Review or audit an SW FMEA workbook
- Verify failure mode coverage and rating completeness
- Validate residual risk acceptance per ASIL
- Run a functional safety assessment on SW FMEA
- Produce a confirmation-measures checklist
- Get technical gap analysis of failure mode detection and mitigation

The skill is the natural counterpart to `sw-fmea-builder` — `sw-fmea-builder` produces the artifact, `sw-fmea-checklist-reviewer` confirms it meets ISO 26262-9 requirements.

## Workflow

### Step 1 — Get the SW FMEA Path

Ask the user for the SW FMEA xlsx path. If they provide a folder, scan for `*.xlsx` and ask which is the SW FMEA.

### Step 2 — Read References on First Use

- `references/methodology.md` — scoring conventions (FC/LC/PC/NO/NA), confidence levels, what the skill does
- `references/sw_fmea_checks.md` — each of 14 + 14 checks with confidence rationale

### Step 3 — Generate the Checklist

```bash
python scripts/generate_checklist.py <sw_fmea.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional; detects formula errors
```

The script prints a JSON summary including residual risk validation results so you immediately see risk acceptance outcomes.

### Step 4 — Walk the User Through the Review

The checklist xlsx has 7 tabs. Direct the user in this order:

1. **Title** — confirm the SW FMEA being assessed is correct
2. **Summary** — read KPI tiles, compliance %, and Findings (NO and PC) list
3. **Confirmation Review** — focus on rows with Assessment = "—" (pending) or "NO"
4. **SW FMEA Assessment** — **focus on row #10 (residual risk)** — this is the headline auto-validation
5. **Verification Assessment** — most rows Pending (external Verification Plan required)

For each Pending row, reviewer accepts/refines the drafted finding. For PC/NO rows, reviewer reads Recommended Action and decides whether to update source SW FMEA.

### Step 5 — Iterate

When the user updates the SW FMEA and re-runs the skill:
- A new checklist is produced fresh; the skill v0.1 does not preserve manual edits
- Recommended workflow: keep old checklist for diff comparison, generate new one each time SW FMEA changes

## Output Structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | SW FMEA being assessed; reviewer info |
| 2 | General Info | TOC of checklist + references |
| 3 | Guide | How to interpret ratings, obligations, confidence |
| 4 | Summary | Statistical roll-up + Findings (NO/PC items) + charts |
| 5 | Confirmation Review | 14 generic doc-quality checks (ISO 26262-8 §10) |
| 6 | SW FMEA Assessment | 14 substantive SW-FMEA checks (ISO 26262-9 §8) — **includes residual risk auto-verification** |
| 7 | Verification Assessment | External verification checks (all Pending without external docs) |

## Auto-Fill Confidence Model

| Confidence | When Assigned | Examples |
|------------|---------------|----------|
| High | Verified directly from xlsx | "All failure modes rated"; "Post-risk 2 <= ASIL D threshold 1" |
| Medium | Inferred with caveat | "SW catalog 95% complete"; detection coverage present but needs review |
| Low / Draft | Subjective or external artifact | "Methodology consistent with architectural decomposition" (needs System FMEA) |

Every Low-confidence finding starts "(Auto-suggest, requires reviewer judgment)" so the reviewer knows human attention is required.

## Residual Risk Checks (The Headline Value)

Check **#10** in SW FMEA Assessment is **the headline auto-verification**:

- **Check #10 (Residual Risk Acceptable)**: Reads post-mitigation risk from xlsx, compares to ASIL-specific threshold (D<=1, C<=3, B<=9, A<=27)

Returns **FC** if all failure modes meet thresholds, **NO** if any exceeded. This check uses `openpyxl.load_workbook(..., data_only=True)` to read evaluated cell values, so formula-driven SW FMEA worksheets are fully supported.

## Common Pitfalls to Flag

1. **Checklist is not a substitute for independent reviewer.** ISO 26262-2 requires confirmation reviews by an independent person (I1), team (I2), or org unit (I3) per ASIL. The skill is a workbench.

2. **SW FMEA produced by sw-fmea-builder always has consistent risk ratings.** Risk values are formula-driven; if post-mitigation risk is populated, it reflects detection & mitigation. The skill verifies they meet *acceptance thresholds*.

3. **Many VA rows Pending is normal.** All 4 VA checks describe external Verification Plan / Report. They are correctly marked Pending; reviewer ticks them off once verification docs are available.

4. **NO rows point at specific gaps.** Most common NO findings are missing severity/frequency/detection ratings, incomplete SW component catalog, or unmitigated high-risk failure modes. These are actionable.

5. **The skill does not modify the source SW FMEA.** All corrective actions go in Recommended Actions. The analyst decides whether to update the SW FMEA and re-run.

## Files in This Skill

```
sw-fmea-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── sw_fmea_probe.py             # SW FMEA content extractor
│   ├── check_definitions.py         # canonical checks with logic
│   ├── recalc.py
│   ├── dashboard.py                 # shared visual dashboard
│   └── office/
└── references/
    ├── methodology.md               # scoring conventions, what skill does/doesn't do
    └── sw_fmea_checks.md            # detailed checklist reference (14+14 checks)
```

## Key Design Points

- **Automatic Residual Risk Validation**: Check #10 reads post-risk values and compares to ISO 26262-9 ASIL thresholds. High-value auto-fill.
- **Uses openpyxl data_only=True**: Supports formula-heavy SW FMEA worksheets; reads evaluated cells, not formulas.
- **Shar