---
name: pfmea-checklist-reviewer
description: Technical reviewer for PFMEA xlsx (AIAG-VDA 2019); verifies header block completion, process flow and function mapping, S/O/D ratings, action priority computation, high-AP closure, special characteristics flagging, and control plan linkage. Produces audit-ready checklist with visual dashboard showing compliance metrics and gap findings.
---

# PFMEA Checklist Reviewer

This skill turns PFMEA technical review into a one-shot run that produces an audit-ready confirmation checklist with risk assessment validation, action plan verification, and roll-up statistics per AIAG-VDA Handbook 2019 methodology.

The skill is opinionated about **what to check** (14 doc-quality + 14 PFMEA-specific checks) and conservative about **what to assert**. Every S/O/D rating and Action Priority (AP = S*O*D) computation is verified automatically by reading values from the PFMEA xlsx. High-AP items are cross-checked for recommended actions, ownership, due dates, and control plan linkage.

## When to Use This Skill

Use whenever the user wants to:
- Review or audit a PFMEA workbook
- Verify severity/occurrence/detection ratings and AP computations
- Confirm high-priority items have closure plans
- Run a manufacturing process FMEA assessment
- Produce a confirmation-measures checklist for sign-off
- Get gap analysis of process control coverage

The skill is the natural counterpart to `pfmea-builder` — `pfmea-builder` produces the artifact, `pfmea-checklist-reviewer` confirms it meets AIAG-VDA requirements.

## Workflow

### Step 1 — Get the PFMEA Path

Ask the user for the PFMEA xlsx path. If they provide a folder, scan for `*.xlsx` and ask which is the PFMEA.

### Step 2 — Read References on First Use

- `references/methodology.md` — scoring conventions, confidence levels, what the skill does/doesn't do
- `references/pfmea_checks.md` — detailed checklist reference (14+14 checks with AIAG-VDA mapping)

### Step 3 — Generate the Checklist

```bash
python scripts/generate_checklist.py <pfmea.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional; detects formula errors
```

The script prints a JSON summary showing all probed content: process steps, functions, PFMEA rows, ratings, AP distribution, and high-AP closure status.

### Step 4 — Walk the User Through the Review

The checklist xlsx has 7 tabs. Direct the user in this order:

1. **Title** — confirm the PFMEA being assessed is correct
2. **Summary** — read KPI tiles, compliance %, and Findings list
3. **Confirmation Review** — focus on rows with Rating = "—" (pending) or "NO"
4. **PFMEA Assessment** — **focus on rows #5–7 (S/O/D ratings, AP computation, high-AP closure)** — these are headline validations
5. **Verification Assessment** — most rows Pending (external Verification Plan required)

For each Pending row, reviewer accepts/refines the drafted finding. For PC/NO rows, reviewer reads Recommended Action and decides whether to update source PFMEA.

### Step 5 — Iterate

When the user updates the PFMEA and re-runs the skill:
- A new checklist is produced fresh
- Recommended workflow: keep old checklist for diff comparison, generate new one each time PFMEA changes

## Output Structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | PFMEA being assessed; document identification |
| 2 | General Info | TOC of checklist + references |
| 3 | Guide | How to interpret ratings, obligations, confidence |
| 4 | Summary | Statistical roll-up + KPI tiles + Findings (NO/PC items) + charts |
| 5 | Confirmation Review | 14 generic doc-quality checks |
| 6 | PFMEA Assessment | 14 AIAG-VDA 2019 specific checks — **includes S/O/D validation** |
| 7 | Verification Assessment | External verification checks (all Pending without evidence) |

## Auto-Fill Confidence Model

| Confidence | When Assigned | Examples |
|------------|---------------|----------|
| High | Verified directly from xlsx | "All rows have S/O/D"; "Header block complete"; "AP = S*O*D verified" |
| Medium | Inferred with caveat | "Process flow 85% complete"; "Action plan mostly assigned" |
| Low / Draft | Subjective or external artifact | "High-AP items align with manufacturing capability" (needs process data); "Control plan sufficiency" |

Every Low-confidence finding starts "(Auto-suggest, requires reviewer judgment)" so the reviewer knows human attention is required.

## Rating Definitions

| Rating | Meaning | Action |
|--------|---------|--------|
| FC | Fully Compliant | No corrective action needed; requirement satisfied. |
| LC | Largely Compliant | Substantially satisfied; minor gaps acceptable. |
| PC | Partially Compliant | Partially satisfied; corrective action recommended. |
| NO | Not Compliant | Not satisfied; must be corrected before sign-off. |
| NA | Not Applicable | Requirement not applicable to this PFMEA. |
| (Pending) | Pending Review | Automated check suggests; requires reviewer judgment. |

## Key Checks (Headlines)

**Checks #5–7 in PFMEA Assessment are the headline validations:**

- **Check #5 (S/O/D Ratings)**: Verifies all failure modes have Severity, Occurrence, Detection rated 1-10
- **Check #6 (AP Computation)**: Verifies Action Priority = S*O*D calculated for all rows (or reads pre-calculated AP)
- **Check #7 (High-AP Closure)**: Verifies all AP >= 100 items have recommended actions with owner and due date

All three return **FC** if conditions met, **NO** if failed. These checks read evaluated cell values from the PFMEA, so formula-driven worksheets are fully supported.

## Common Pitfalls to Flag

1. **Checklist is not a substitute for independent reviewer.** AIAG-VDA expects confirmed FMEA by knowledgeable team member (manufacturer and supplier representatives). The skill is a workbench.

2. **PFMEA produced by pfmea-builder always passes rating consistency.** Ratings are value-driven; if S/O/D are entered, AP is consistently computed. The skill verifies completeness.

3. **Many VA rows Pending is normal.** All VA checks describe external Verification Plan / Report. They are correctly marked Pending; reviewer ticks them off once verification docs are available.

4. **NO rows point at specific gaps.** Most common NO findings are missing S/O/D ratings, incomplete action plan ownership, or orphan steps. These are actionable.

5. **The skill does not modify the source PFMEA.** All corrective actions go in Recommended Actions. The analyst decides whether to update the PFMEA and re-run.

## Files in This Skill

```
pfmea-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── pfmea_probe.py               # PFMEA content extractor
│   ├── check_definitions.py         # canonical checks with logic
│   ├── recalc.py
│   ├── dashboard.py                 # shared visual dashboard
│   └── office/
└── references/
    ├── methodology.md               # scoring conventions, what skill does/doesn't do
    └── pfmea_checks.md              # detailed checklist reference (14+14 checks)
```

## Key Design Points

- **Automatic Rating Validation**: S/O/D checks read values and verify ratings 1-10. AP verification reads or computes S*O*D. High-value auto-fill.
- **Uses openpyxl data_only=True**: Supports formula-heavy PFMEA worksheets; reads evaluated cells, not formulas.
- **Shared Dashboard Module**: Renders KPI tiles, pie chart, compliance bars, stacked ratings by section, findings table.
- **Reusable Check Pattern**: Same CheckResult / CheckDef pattern as fmeda-checklist-reviewer and other reviewer skills.
