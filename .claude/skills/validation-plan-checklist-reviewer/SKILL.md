---
name: validation-plan-checklist-reviewer
description: Run validation plan confirmation measures against ISO 26262-4 Section 9 covering validation scope against safety goals, scenario coverage completeness, environment adequacy, resource allocation, and exit criteria measurability with pass-fail-partial assessment. Use this skill when the user mentions validation plan checklist reviewer.
---

## Overview

Analyzes a Validation Plan xlsx against 28 confirmation measures per ISO 26262-4 §9. Returns assessment table and visual dashboard.

## Inputs

- Validation Plan xlsx from validation-plan-builder
- (Optional) linked Safety Goals document for scope validation

## Checks

Verifies:
- Validation scope covers all safety goals
- Scenarios capture operational and edge cases
- Environments (bench, track, road) specified with adequate detail
- Resources allocated (test vehicles, drivers, instrumentation)
- Use cases representative of customer workflows
- Methods (bench, track, road simulation) defined
- Exit criteria objective and measurable
- Schedule realistic and covers all validation activities
- Traceability to safety goals and system verification explicit
- Risk assessment for residual validation gaps

## Outputs

1. **Checklist** tab (FC/LC/PC/NO ratings)
2. **Findings** tab (gaps, risks, recommendations)
3. **Dashboard** (visual summary)
4. **Signoff** tab (reviewer approval)

## Usage

```bash
python scripts/generate_checklist.py valplan.xlsx output_checklist.xlsx
```
