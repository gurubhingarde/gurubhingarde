---
name: dfmea-checklist-reviewer
description: Technical reviewer for AIAG-VDA 2019 DFMEA xlsx. Verifies header block completeness, structure and function analysis population, DFMEA worksheet row integrity, S/O/D ratings, Action Priority assignment, and action plan closure. Headline metric identifies high-AP items pending completion. Produces audit-ready checklist with visual dashboard. Skill is independent and does not modify source DFMEA.
---

# DFMEA Checklist Reviewer

This skill turns DFMEA technical review into a one-shot run that produces an audit-ready confirmation checklist with automatic structural validation, risk assessment completeness checks, action priority tracking, and roll-up statistics.

The skill is opinionated about what to check (AIAG-VDA 2019 Section 7 confirmation set + ISO 26262-3 requirements) and conservative about what to assert. Every row-level check (severity/occurrence/detection/AP) is verified automatically by reading actual values from the DFMEA xlsx. Subjective checks (design intent, customer impact) are drafted for reviewer acceptance.

## When to Use This Skill

Use whenever the user wants to:
- Review or audit a DFMEA workbook
- Verify DFMEA completeness per AIAG-VDA 2019
- Run a confirmation-measures assessment on DFMEA
- Identify pending high-priority actions (headline metric)
- Produce an audit-ready checklist with visual dashboard
- Get technical gap analysis of risk assessment coverage

The skill is the natural counterpart to `dfmea-builder` — `dfmea-builder` produces the artifact, `dfmea-checklist-reviewer` confirms it meets AIAG-VDA 2019 and ISO 26262-3 requirements.

## Workflow

### Step 1 — Get the DFMEA Path

Ask the user for the DFMEA xlsx path. If they provide a folder, scan for `*.xlsx` and ask which is the DFMEA.

### Step 2 — Read References on First Use

- `references/methodology.md` — scoring conventions, confidence levels, what the skill does/doesn't do
- `references/dfmea_checks.md` — each of 14+14 checks with detailed rationale

### Step 3 — Generate the Checklist

```bash
python scripts/generate_checklist.py <dfmea.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional; detects formula errors
```

The script prints a JSON summary with headline metrics so you immediately see pending high-AP items.

### Step 4 — Walk the User Through the Review

The checklist xlsx has 7 tabs. Direct the user in this order:

1. **Title** — confirm the DFMEA being assessed is correct
2. **Summary** — read KPI tiles, compliance %, and Findings (NO and PC) list
3. **Confirmation Review** — focus on rows with Assessment = Pending or NO
4. **DFMEA Assessment** — **focus on Check#14 (high-AP pending)** — this is the headline validation
5. **Verification Assessment** — most rows Pending (external Verification Plan required)

For each Pending row, reviewer accepts/refines the drafted finding. For PC/NO rows, reviewer reads Recommended Action and decides whether to update source DFMEA.

### Step 5 — Iterate

When the user updates the DFMEA and re-runs the skill:
- A new checklist is produced fresh; the skill does not preserve manual edits
- Recommended workflow: keep old checklist for diff comparison, generate new one each time DFMEA changes

## Output Structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | DFMEA being assessed; reviewer info |
| 2 | General Info | TOC of checklist + references |
| 3 | Guide | How to interpret ratings, obligations, confidence |
| 4 | Summary | Statistical roll-up + Findings (NO/PC items) + charts |
| 5 | Confirmation Review | 14 generic doc-quality checks (CR) |
| 6 | DFMEA Assessment | 14 substantive DFMEA checks (DFMEAA) — includes headline pending-AP metric |
| 7 | Verification Assessment | External verification checks (all Pending without external docs) |

## Headline Metric: High-AP Items Pending Completion

Check #14 in DFMEA Assessment is the **headline value**:

- **Finding**: Count of High-AP failure modes whose status is not Closed/Completed
- **Rationale**: AIAG-VDA 2019 requires all high-priority actions be tracked and closed. This metric surfaces untracked work.
- **Rating**: FC if zero pending, NO if any pending with count

## Auto-Fill Confidence Model

| Confidence | When Assigned | Examples |
|------------|---------------|----------|
| High | Verified directly from xlsx | "All 47 rows have S/O/D rated"; "19 High-AP items, 15 have actions" |
| Medium | Inferred with caveat | "Header block 80% complete"; "Structure has subsystems but no components" |
| Low / Draft | Subjective or external artifact | "Design intent matches product family goals" (needs design spec); auto-suggest |

Every Low-confidence finding starts "(Auto-suggest, requires reviewer judgment)" so the reviewer knows human attention is required.

## Common Pitfalls to Flag

1. **Checklist is not a substitute for independent reviewer.** AIAG-VDA 2019 requires confirmation review by a senior engineer. The skill is a workbench.

2. **Missing S/O/D values block AP computation.** If any failure mode lacks Severity, Occurrence, or Detection, the AP cannot be assigned. The skill flags incomplete rows.

3. **High-AP items without actions are blockers.** DFMEA is only useful if you close the loop. Every High-AP item must have a recommended action with owner and due date.

4. **NO rows point at specific gaps.** Most common NO findings are missing S/O/D, unrated AP, or high-AP items without actions. These are actionable.

5. **The skill does not modify the source DFMEA.** All corrective actions go in Recommended Actions. The analyst decides whether to update the DFMEA and re-run.

## Files in This Skill

```
dfmea-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── dfmea_probe.py               # DFMEA content extractor
│   ├── check_definitions.py         # canonical checks with logic
│   ├── recalc.py
│   ├── dashboard.py                 # shared visual dashboard
│   └── office/
└── references/
    ├── methodology.md               # scoring conventions, what skill does/doesn't do
    └── dfmea_checks.md              # detailed checklist reference (14+14 checks)
```

## Key Design Points

- **Automatic Row Validation**: All S/O/D and AP checks read computed values directly from worksheet.
- **Uses openpyxl data_only=True**: Supports formula-heavy DFMEA worksheets; reads evaluated cells.
- **Shared Dashboard Module**: Renders KPI tiles, pie chart, compliance bars, stacked ratings by section, findings table.
- **Reusable Check Pattern**: Same CheckDef / CheckResult pattern as hara/fsc/tsc checklist reviewers.
- **Headline Metric**: Check #14 flags all high-AP items pending closure — the single most important DFMEA verification.
