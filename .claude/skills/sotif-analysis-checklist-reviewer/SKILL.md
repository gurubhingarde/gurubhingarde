---
name: sotif-analysis-checklist-reviewer
description: Run a confirmation-measures review on any ISO 21448 SOTIF Analysis xlsx and produce a completed checklist with auto-filled findings, evidence references, recommended actions, and roll-up statistics. Probes the source SOTIF Analysis (works on sotif-analysis-builder outputs and best-effort on others), runs ~28 standard checklist requirements split across Confirmation Review (14 generic doc-quality) and SOTIF Analysis Assessment (14 per ISO 21448 §6). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source SOTIF Analysis. Use this skill whenever the user wants to review, audit, assess, or confirm a SOTIF Analysis workbook, or asks for a confirmation review or SOTIF Analysis checklist. Always use this skill instead of producing a freeform review in chat.
---

# SOTIF Analysis Checklist Reviewer

This skill turns confirmation review of a SOTIF Analysis — verifying ODD definition, performance limitations, triggering conditions, scenario classification, and acceptance criteria — into a one-shot run that produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is opinionated about what to check (the standard ISO 21448 confirmation set) and conservative about what to assert. Every Fully-Compliant judgment cites specific evidence found. Every subjective check is drafted with a "(Reviewer to verify)" preface so the human knows where judgment is required. The skill never modifies the source SOTIF Analysis; gaps land in the Recommended Actions column.

## When to use this skill

Use whenever the user wants to:
- Review or audit a SOTIF Analysis workbook
- Produce a confirmation-measures checklist for ISO 21448 compliance
- Run a SOTIF Analysis assessment
- Get a roll-up of SOTIF Analysis quality (gaps, missing sections, incomplete coverage)

## Workflow

### Step 1 — Get the SOTIF Analysis path

Ask the user for the SOTIF Analysis xlsx path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <sotif-analysis.xlsx> <output_checklist.xlsx>
```

The script prints a JSON summary including probed counts (ODD definition, performance limitations, triggering conditions, scenario classes, acceptance criteria) and ratings distribution.

### Step 3 — Walk the user through the review

The checklist xlsx has 7 tabs. Direct the user's attention in this order:

1. **Title** — confirm the SOTIF Analysis being assessed is correct.
2. **Summary** — read the statistics and Findings (NO and PC items). Executive view.
3. **Confirmation Review** — focus on rows with Assessment = "—" (pending) or "NO". These typically point at missing Title-page fields or organizational issues.
4. **SOTIF Analysis Assessment** — focus on rows with Assessment = "PC" or "NO". These are substantive gaps. Pending rows for checks #2, #6, #9 usually need external judgment or confirmation against project artifacts.

For each Pending row the reviewer accepts or refines the drafted finding and sets Assessment. For each PC or NO row, the reviewer reads the Recommended Action, decides whether to update the source SOTIF Analysis, and re-runs the skill.

### Step 4 — Iterate

When the user updates the SOTIF Analysis and re-runs the skill:
- The new checklist is produced fresh; the skill does not preserve manual edits to the previous checklist.
- Recommended workflow: keep the old checklist for diff comparison, run a new one each time the SOTIF Analysis changes.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | SOTIF Analysis being assessed; reviewer info |
| 2 | General Info | TOC of the checklist + references |
| 3 | Guide | How to interpret ratings, confidence, obligations |
| 4 | Summary | Statistical roll-up + Findings list (NO + PC items) |
| 5 | Confirmation Review | 14 generic doc-quality checks (ISO 21448-1 §3) |
| 6 | SOTIF Analysis Assessment | 14 SOTIF substantive checks (ISO 21448-1 §6) |
| 7 | Acceptance Criterion Tracking | Measurability and coverage summary |

## Common pitfalls to flag

1. **Checklist is not a substitute for independent review.** The skill is a workbench, not the reviewer.
2. **ODD definition must span four dimensions.** Scenery, environment, dynamics (vehicle and other road users), and driver state must all be documented.
3. **Triggering conditions must cover six standard categories.** Environmental, sensor, road infrastructure, other road user, system state, driver state.
4. **Scenario quadrant classification is mandatory.** Known Safe / Known Unsafe / Unknown Safe / Unknown Unsafe must be assigned to all scenarios.
5. **Unknown Unsafe scenarios require mitigation or acceptance.** The skill flags each Unknown Unsafe scenario in the headline check (check #14).
6. **Acceptance criteria must be quantified.** Statements like "residual unintended behavior rate < 1e-6 per vehicle-lifetime" are required, not qualitative targets.
7. **The skill does not modify the source SOTIF Analysis.** All corrective actions go in the Recommended Actions column.

## Files in this skill

```
sotif-analysis-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── sotif_analysis_probe.py      # content extractor
│   ├── check_definitions.py         # canonical check list with verification logic
│   ├── dashboard.py                 # shared summary tab renderer
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── sotif_analysis_checks.md
```

Always use this skill instead of producing a freeform review in chat.
