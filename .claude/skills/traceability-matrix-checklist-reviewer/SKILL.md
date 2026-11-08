---
name: traceability-matrix-checklist-reviewer
description: Run traceability matrix confirmation measures against ISO 26262, ISO 21434, and IEEE 1012 covering bidirectional trace completeness, orphan identification, coverage analysis, gap identification, and validation rule compliance with pass-fail-partial assessment. Use this skill when the user mentions traceability matrix checklist reviewer.
---

## Overview

Analyzes a Traceability Matrix xlsx against 25 confirmation measures per ISO 26262, ISO 21434, and IEEE 1012. Returns assessment table and visual dashboard.

## Inputs

- Traceability Matrix xlsx from traceability-matrix-builder

## Checks

Verifies:
- All stakeholder needs trace to requirements
- All requirements trace to tests
- No orphan requirements
- No orphan tests
- Coverage >= 95% achieved
- Bidirectional traceability established
- Convention rules followed (naming, patterns)
- Gap identification complete
- Trace quality metrics computed
- Validation rules met

## Outputs

1. **Checklist** tab (FC/LC/PC/NO ratings)
2. **Findings** tab (orphans, gaps, risks)
3. **Dashboard** (coverage pie charts, metrics)
4. **Signoff** tab (reviewer approval)

## Usage

```bash
python scripts/generate_checklist.py matrix.xlsx output_checklist.xlsx
```
