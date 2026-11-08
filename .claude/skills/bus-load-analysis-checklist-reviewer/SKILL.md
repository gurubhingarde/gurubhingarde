---
name: bus-load-analysis-checklist-reviewer
description: Run a confirmation review on any bus load analysis xlsx to validate load calculations, scenario coverage, protocol compliance, and engineering recommendations Use this skill when the user mentions bus load analysis checklist reviewer.
---

# Bus Load Analysis Checklist Reviewer

Audit and validate any bus load analysis workbook with 28 confirmation checks.

## What this skill does

- Validates xlsx structure and document control
- Checks load calculations and formula integrity
- Confirms per-bus load < 60% nominal, < 80% peak (CAN targets)
- Verifies frame overhead per protocol
- Validates scenario coverage and headroom margins
- Checks all messages included in analysis
- Provides dashboard summary + detailed checklist

## How to use it

Upload a bus load analysis xlsx (from bus-load-analysis-builder or similar).

## What you get

- Visual dashboard summary (pass/fail counts)
- 28-point checklist with ratings (FC/PC/NO/NA)
- Detailed findings and recommended actions
- References to methodology

---

*Use this skill whenever the user needs to audit or verify a bus load analysis workbook.*
