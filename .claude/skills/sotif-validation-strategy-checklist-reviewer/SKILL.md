---
name: sotif-validation-strategy-checklist-reviewer
description: Run a confirmation-measures review on any ISO 21448 SOTIF Validation Strategy xlsx and produce a completed checklist with auto-filled findings, evidence references, recommended actions, and roll-up statistics. Probes the source validation-strategy workbook, runs 26 standard checklist requirements (14 generic doc-quality + 12 substantive per ISO 21448 §10). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source document. Use this skill whenever the user wants to review, audit, assess, or confirm a SOTIF Validation Strategy workbook. Always use this skill instead of producing a freeform review in chat.
---

# SOTIF Validation Strategy Checklist Reviewer

Confirmation review of a SOTIF Validation Strategy — verifying coverage of real-world driving, simulation, proving ground, and field monitoring validation methods — turned into a one-shot checklist xlsx with findings, evidence pointers, and recommended actions.

Conservative about assertions. Every FC judgment cites specific evidence found. Every subjective check is drafted with "(Reviewer to verify)" so humans know where judgment is required. Never modifies source; gaps land in Recommended Actions.

## When to use this skill

- Review or audit a SOTIF Validation Strategy workbook
- Produce a confirmation-measures checklist for ISO 21448 §10-11 compliance
- Run a SOTIF Validation Strategy assessment
- Get a roll-up of validation strategy quality and completeness

## Workflow

### Step 1 — Get the Validation Strategy xlsx path

Ask the user for the path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <sotif-validation-strategy.xlsx> <output_checklist.xlsx>
```

Script prints JSON summary: probed validation methods (real-world mileage target, simulation library cited, proving ground tests, field monitoring), acceptance tracking status, coverage gaps, statistical significance documentation, ratings distribution.

### Step 3 — Walk the user through the review

Six-tab checklist:

1. **Title** — confirm this is the right Validation Strategy document
2. **Summary** — statistics and findings (NO + PC items)
3. **Confirmation Review** — doc-quality checks; focus on "—" (pending) or "NO"
4. **Validation Strategy Assessment** — substantive checks per ISO 21448 §10; focus on "PC" or "NO"

For each Pending row, reviewer accepts or refines finding and sets Assessment. For PC/NO rows, reviewer reads Recommended Action and decides whether to update source and re-run.

### Step 4 — Iterate

New checklist is fresh; old edits don't carry forward. Keep old checklist for diff, run new one each time source changes.

## Output structure (6 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | Document being assessed; reviewer info |
| 2 | General Info | TOC and references |
| 3 | Guide | Rating interpretation |
| 4 | Summary | Statistical roll-up + Findings |
| 5 | Confirmation Review | 14 doc-quality checks |
| 6 | Validation Strategy Assessment | 12 substantive checks per ISO 21448 §10-11 |

## Common pitfalls

1. **Acceptance criteria must be referenced from SOTIF Analysis**: Clear traceability from acceptance criteria down to validation evidence.
2. **Four validation methods are mandatory**: Real-world driving, simulation, proving ground, and field monitoring must all be covered.
3. **Real-world mileage target must be quantified**: Statement like "100k miles across fleet" or "50M miles total", not qualitative.
4. **Simulation correlation with real-world must be validated**: Document that simulation scenarios match real-world driving patterns.
5. **Proving ground test catalog must include pass/fail criteria**: Each test case has explicit acceptance criteria.
6. **Field monitoring telemetry plan must be defined**: What data is logged, how often, detection thresholds for anomalies.
7. **Coverage gaps must be explicitly noted and justified**: Any scenarios NOT covered require explanation and planned validation.
8. **Statistical significance must be justified**: Confidence intervals or sample size analysis for validation evidence.
9. **ISO 21448 §10-11 must be cited**: Explicit references to validation planning, specification, and execution requirements.
10. **Acceptance criterion tracking shows progress**: Current status vs. target, what evidence is complete, what is pending.

Always use this skill instead of producing a freeform review in chat.
