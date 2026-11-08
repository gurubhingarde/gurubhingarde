---
name: test-case-catalog-checklist-reviewer
description: Run test case catalog confirmation measures against ISO 26262 and IEEE 1012 covering test design completeness, traceability to requirements, precondition definition, pass-fail criteria clarity, test level allocation, automation status, and execution priority with pass-fail-partial assessment. Use this skill when the user mentions test case catalog checklist reviewer.
---

## Overview

Analyzes a Test Case Catalog xlsx against 28 confirmation measures per ISO 26262 and IEEE 1012. Returns assessment table and visual dashboard.

## Inputs

- Test Case Catalog xlsx from test-case-catalog-builder
- (Optional) linked requirements for traceability validation

## Checks

Verifies:
- All test cases have unique IDs
- Preconditions clearly defined
- Inputs specified with ranges and bounds
- Expected outputs measurable and objective
- Pass/fail criteria unambiguous
- Traceability to requirements bidirectional
- Test levels (unit/integration/system) allocated
- Automation status documented
- Execution priority assigned
- Orphan test cases identified

## Outputs

1. **Checklist** tab (FC/LC/PC/NO ratings)
2. **Findings** tab (gaps, ambiguities)
3. **Dashboard** (visual summary)
4. **Signoff** tab (reviewer approval)

## Usage

```bash
python scripts/generate_checklist.py catalog.xlsx output_checklist.xlsx
```
