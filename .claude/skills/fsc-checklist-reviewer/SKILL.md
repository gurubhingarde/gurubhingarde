---
name: fsc-checklist-reviewer
description: Run a confirmation-measures review on any ISO 26262 FSC xlsx and produce a completed checklist with a visual dashboard (KPI tiles, pie chart, compliance bar chart, rating breakdown by section) plus auto-filled findings and recommended actions. Probes the FSC content (best-effort, optimal on fsc-builder outputs), runs ~64 checks across Confirmation Review (doc-quality per ISO 26262-8 §10), Functional Safety Assessment (FSC substantive checks per ISO 26262-3 §8 covering FSR derivation, ASIL inheritance, safe states, FTTI, architecture allocation, decomposition independence, FSC-vs-SG verification), and Verification Assessment. Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks; drafts low-confidence findings for subjective items. Does not modify the source FSC. Use this skill whenever the user wants to review, audit, assess, or confirm an FSC, or asks for an FSC checklist, even casual phrasings like 'check my FSC'. Always use this skill instead of producing a freeform review in chat.
---

# FSC Checklist Reviewer

Runs an ISO 26262 confirmation review on any Functional Safety Concept (FSC) xlsx and produces a completed checklist with a visual dashboard. Pairs naturally with `fsc-builder` (which produces the artifact) but works on any FSC xlsx via best-effort probing.

## When to use this skill

- Review or audit an FSC workbook
- Produce a confirmation-measures checklist for an FSC
- Run a functional safety assessment on an FSC
- Verify ASIL decomposition independence claims
- Get a roll-up of FSC quality with charts and metrics

## Workflow

1. Get the FSC xlsx path from the user.
2. Read `references/methodology.md`, `references/fsc_checks.md` on first use.
3. Run `python scripts/generate_checklist.py <fsc.xlsx> <output_checklist.xlsx>`.
4. Walk the user through the **Summary dashboard** first (KPI tiles + charts), then the per-tab review:
   - **Confirmation Review** (14 checks) — focus on Pending and NO rows
   - **Functional Safety Assessment** (16 checks) — focus on PC and NO rows; the decomposition-independence check (FSA #10) is often the highest-value finding when decomposition is applied
   - **Verification Assessment** (34 checks) — most are external (Verification Plan / Spec / Report); 5 FSC-specific ones (33a–e) are auto-evaluated
5. For gaps, the analyst updates the FSC and re-runs the skill.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | What FSC is being assessed |
| 2 | General Info | TOC of the checklist |
| 3 | Guide | Rating / confidence / obligation legend |
| 4 | Summary | Visual dashboard: KPI tiles, pie chart (rating distribution), bar chart (compliance %), stacked bar (rating breakdown by section), findings table |
| 5 | Confirmation Review | 14 doc-quality checks |
| 6 | Functional Safety Assessment | 16 FSC substantive checks |
| 7 | Verification Assessment | 34 verification checks |

## Files in this skill

```
fsc-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── fsc_probe.py
│   ├── check_definitions.py
│   ├── dashboard.py                 # shared visual dashboard
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── fsc_checks.md
```
