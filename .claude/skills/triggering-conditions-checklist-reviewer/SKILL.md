---
name: triggering-conditions-checklist-reviewer
description: Run a confirmation-measures review on any ISO 21448 Triggering Conditions xlsx and produce a completed checklist with auto-filled findings, evidence references, recommended actions, and roll-up statistics. Probes the source triggering-conditions workbook, runs 26 standard checklist requirements (14 generic doc-quality + 12 substantive per ISO 21448 Annex B). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source document. Use this skill whenever the user wants to review, audit, assess, or confirm a Triggering Conditions workbook. Always use this skill instead of producing a freeform review in chat.
---

# Triggering Conditions Checklist Reviewer

Confirmation review of triggering conditions analysis — verifying environmental, sensor, road, system-state, driver-state, and combined conditions — turned into a one-shot checklist xlsx with findings, evidence pointers, and recommended actions.

Conservative about assertions. Every FC judgment cites specific evidence. Every subjective check is drafted with "(Reviewer to verify)" so humans know where judgment is required. Never modifies source; gaps land in Recommended Actions.

## When to use this skill

- Review or audit a Triggering Conditions workbook
- Produce a confirmation-measures checklist for ISO 21448 Annex B compliance
- Run a Triggering Conditions assessment
- Get a roll-up of Triggering Conditions quality and coverage

## Workflow

### Step 1 — Get the Triggering Conditions xlsx path

Ask the user for the path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <triggering-conditions.xlsx> <output_checklist.xlsx>
```

Script prints JSON summary: probed condition counts (environmental, sensor, road, system-state, driver-state), combined conditions, likelihood/detectability estimates, mitigation strategies, ratings distribution.

### Step 3 — Walk the user through the review

Seven-tab checklist:

1. **Title** — confirm this is the right Triggering Conditions document
2. **Summary** — statistics and findings (NO + PC items)
3. **Confirmation Review** — doc-quality checks; focus on "—" (pending) or "NO"
4. **Triggering Conditions Assessment** — substantive checks per ISO 21448 Annex B; focus on "PC" or "NO"

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
| 6 | Triggering Conditions Assessment | 12 substantive checks per ISO 21448 Annex B |

## Common pitfalls

1. **Triggering conditions must cover six standard categories**: Environmental, sensor, road infrastructure, other road user, system state, driver state.
2. **Combined conditions are mandatory**: Cartesian or pairwise analysis of interactions between single triggering conditions.
3. **Likelihood and detectability must be estimated**: For each triggering condition, assign likelihood (e.g., H/M/L) and detectability (e.g., High/Low).
4. **Mitigation per high-risk condition**: High likelihood + low detectability conditions require explicit mitigation strategy.
5. **ISO 21448 Annex B methodologies must be cited**: Explicit reference to ISO 21448 Part 1 Annex B for category definitions and analysis approach.
6. **The skill does not modify the source**: All corrective actions go in Recommended Actions.

Always use this skill instead of producing a freeform review in chat.
