---
name: control-plan-checklist-reviewer
description: Run a Control Plan audit on any AIAG Control Plan xlsx and produce a checklist with findings, evidence references, and recommended actions. Probes the source workbook (works on control-plan-builder outputs and best-effort on others), runs 36 checks across Confirmation Review (doc-quality), Control Plan Assessment (AIAG substantive), and Verification Assessment (testing adequacy). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Produces audit-ready checklist with visual dashboard, KPI summary, and roll-up statistics.
---

# Control Plan Checklist Reviewer

Turn the tedious task of hand-auditing a Control Plan xlsx into a one-shot run that produces an audit-ready checklist with findings, evidence pointers, and recommended actions.

The skill is opinionated about *what to check* (the standard AIAG Control Plan assessment set per IATF 16949) and conservative about *what to assert*. Every Fully-Compliant judgment cites the specific evidence found. Every subjective check is drafted with a "(Reviewer to verify)" preface so you know where human judgment is required. The skill never modifies the source Control Plan; all corrective actions go in the Recommended Actions column.

## When to use this skill

Use whenever you want to:
- Audit or review a Control Plan workbook
- Produce a confirmation-measures checklist (IATF 16949 §8.1)
- Run a Control Plan Assessment (AIAG standard)
- Run a Verification Assessment on controls and testing adequacy
- Get a roll-up of Control Plan quality and gaps

The skill is the natural counterpart to `control-plan-builder` — the builder produces the artifact, the reviewer confirms it.

## Workflow

### Step 1 — Get the Control Plan path

Ask the user for the Control Plan xlsx path. If they upload a folder, scan for `*.xlsx` files and ask which one is the Control Plan.

### Step 2 — Read the references on first use

- `references/methodology.md` — scoring conventions, check categories, what the skill does/does not do
- `references/control_plan_checks.md` — detailed check definitions, auto-fill logic, release criteria

### Step 3 — Generate the checklist

```bash
python scripts/generate_checklist.py <control_plan.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>  # optional; surfaces any formula errors
```

The script prints a JSON summary with check counts (FC/LC/PC/NO/NA/PENDING) per tab so you immediately see auto-fill yield.

### Step 4 — Walk the user through the review

The checklist xlsx has 7 tabs. Direct the user's attention in this order:

1. **Title** — confirm the Control Plan being assessed is correct
2. **Summary** — read the statistics and Findings (NO and PC) list; this is the executive view
3. **General Info** — understand the scoring scale and methodology
4. **Guide** — read the suggested workflow for resolving findings
5. **Confirmation Review** — focus on NO and PC rows; these point at doc-quality gaps (title, team, approval, revision history)
6. **Control Plan Assessment** — focus on PC and NO rows; these are the substantive gaps (missing gages, sample plans, reaction plans, etc.)
7. **Verification Assessment** — most rows will be Pending because they refer to external Verification Plan/Report; focus on Control-Plan-specific items (MSA adequacy, poka-yoke testing, special characteristic control)

For each Pending row, the reviewer applies judgment and sets the Assessment value. For each PC or NO row, the reviewer reads the Recommended Action, decides whether to update the source Control Plan, and re-runs the skill.

### Step 5 — Iterate

When the user updates the Control Plan and re-runs the skill:
- The new checklist is produced fresh
- Recommended workflow: keep the old checklist for diff comparison, run a new one each time the Control Plan changes

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | What Control Plan is being assessed; checklist ID |
| 2 | General Info | Scoring scale, rating definitions, methodology |
| 3 | Guide | How to use the checklist; recommended workflow |
| 4 | Summary | Statistical roll-up + KPI dashboard + Findings list (NO + PC) |
| 5 | Confirmation Review | 16 doc-quality checks (IATF 16949) |
| 6 | Control Plan Assessment | 14 AIAG substantive checks (IATF 16949 + ISO 26262-5) |
| 7 | Verification Assessment | 8 testing adequacy checks (5 external; 3 Control-Plan-specific) |

## Auto-fill confidence model

| Confidence | When the skill assigns this | Examples |
|------------|----------------------------|----------|
| High | Verified directly from xlsx content | "Header block complete"; "All rows have gages"; "MSA plan exists" |
| Medium | Inferred from xlsx with caveat | "control-plan-builder format detected" |
| Low / draft | Subjective or requires external artifact | "Title covers scope" (subjective); "Reaction plans tested" (external doc) |

Every Low-confidence finding starts with "(Auto-suggest, requires reviewer judgment)" so it is unambiguous to the reviewer that human attention is required.

## Common pitfalls to flag

1. **Checklist is not a substitute for an independent reviewer.** IATF 16949 §8.1 requires Control Plan approval by core team and management. The skill is a workbench, not the approver.
2. **Control plans from control-plan-builder always pass header-block completeness.** The builder enforces title, contact, approval fields. HARAs from other tools may lack these. The Findings cell notes when detected.
3. **Many VA rows pending is normal.** 5 of 8 VA checks describe a Verification Plan/Report that lives outside the Control Plan xlsx. They are correctly marked Pending; the reviewer ticks them off against the project's verification documents.
4. **Most NO rows point at worksheet structure.** The most common NO ratings are missing process steps, gages, sample plans, or reaction plan references. These are easy fixes that take a Control Plan from PC to FC overall.
5. **The skill does not modify the source Control Plan.** All corrective actions go in the Recommended Actions column. The analyst decides whether to update the Control Plan and re-run.

## Files in this skill

```
control-plan-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── control_plan_probe.py         # best-effort Control Plan content extractor
│   ├── check_definitions.py          # canonical checklist with verification logic
│   ├── dashboard.py                  # shared visual dashboard for Summary tab
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── control_plan_checks.md
```

## Release criteria (per IATF 16949)

| Criterion | Standard | Target |
|-----------|----------|--------|
| Header Block complete | Shall | FC (5/5 fields) |
| Control Plan Type specified | Shall | FC (recognized value) |
| Worksheet rows complete | Shall | ≤ LC (90%+ have all fields) |
| MSA Plan exists | Shall | FC (≥1 entry per unique gage) |
| Reaction Plans exist | Shall | FC (all referenced IDs in library) |
| Special Characteristics echoed | Shall | FC or NA (from PFMEA) |
| Doc quality (CR) | Should | ≤ PC (title, contact, approval) |
| Verification Plan ready | Shall | External (before production) |

A Control Plan is **release-ready** when:
- All Shall items are FC or LC (zero PC/NO on Shall checks)
- All Should items are ≤ PC
- Zero critical Pending rows
- Reviewer has approved all PC items with justification
