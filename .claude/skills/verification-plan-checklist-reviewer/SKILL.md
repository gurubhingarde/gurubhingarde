---
name: verification-plan-checklist-reviewer
description: Run verification plan confirmation measures against ISO 26262-8 Section 9 covering scope completeness, method traceability, requirement coverage, environment specifications, schedule realism, and acceptance criteria measurability with pass-fail-partial assessment and visual dashboard. Use this skill when the user mentions verification plan checklist reviewer.
---

## Overview

Analyzes a Verification Plan xlsx against 28 confirmation measures per ISO 26262-8 §9 and IEEE 1012. Returns assessment table and visual dashboard.

## Inputs

- Verification Plan xlsx from verification-plan-builder
- (Optional) linked FSC or System Requirements document for scope validation

## Checks

Verifies:
- Scope covers all safety goals and requirements
- Each requirement mapped to ≥1 verification method
- All methods (review/analysis/simulation/test) defined with entry/exit criteria
- Environments specified for each method and level
- Schedule realistic and phases aligned with V-cycle
- Acceptance criteria measurable (no vague "ensure" language)
- Test levels (unit, integration, system, vehicle) documented
- Traceability to TSC and requirements explicit
- Roles and responsibilities assigned
- Risk assessment included for residual verification gaps

## Outputs

1. **Checklist** tab (FC/LC/PC/NO ratings)
2. **Findings** tab (gaps, risks, recommendations)
3. **Dashboard** (visual summary, pie charts, trend indicators)
4. **Signoff** tab (reviewer name, date, approval authority)

## Usage

```bash
python scripts/generate_checklist.py vplan.xlsx output_checklist.xlsx
```
