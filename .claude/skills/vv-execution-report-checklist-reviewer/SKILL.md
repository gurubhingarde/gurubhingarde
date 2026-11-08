---
name: vv-execution-report-checklist-reviewer
description: Run V and V execution report confirmation measures against ISO 26262-8 Section 9 covering test execution completeness, pass-fail rate justification, defect resolution status, coverage achievement, residual risk acceptance, and signoff authority with pass-fail-partial assessment. Use this skill when the user mentions vv execution report checklist reviewer.
---

## Overview

Analyzes a V&V Execution Report xlsx against 28 confirmation measures per ISO 26262-8 §9. Returns assessment table and visual dashboard.

## Inputs

- V&V Execution Report xlsx from vv-execution-report-builder

## Checks

Verifies:
- Test execution counts documented
- Pass/fail rates justified
- All defects captured and resolved
- Coverage targets achieved
- Residual risk assessment complete
- Signoff authority assigned
- Acceptance criteria met
- Defect resolution traceable
- Lessons learned documented
- Report ready for certification

## Outputs

1. **Checklist** tab (FC/LC/PC/NO ratings)
2. **Findings** tab (gaps, risks, blockers)
3. **Dashboard** (execution metrics, pass rates)
4. **Signoff** tab (reviewer approval)

## Usage

```bash
python scripts/generate_checklist.py report.xlsx output_checklist.xlsx
```
