---
name: vv-execution-report-builder
description: Generate an audit-ready V and V Execution Report workbook per ISO 26262-8 Section 9 capturing executed test cases, pass and fail rates, defects discovered, defect resolution status, residual risk acceptance, requirements coverage achieved, and signoff for verification and validation campaigns at unit, integration, system, and vehicle levels. Use this skill when the user mentions vv execution report builder.
---

## Overview

Generates a multi-tab ISO 26262-8 §9 compliant V&V Execution Report (11-tab xlsx) documenting test campaign results, defects, and closure criteria.

## Inputs

JSON with test execution data: test case IDs, pass/fail status, defect IDs with severity/resolution, coverage metrics, residual risk assessment.

## Outputs

11-tab workbook:
1. **Title** — Campaign scope, period, item
2. **Document Control** — Version history, approval
3. **Campaign Identity** — Scope, period, test level
4. **Test Execution Summary** — Executed/pass/fail/blocked counts
5. **Defect Catalog** — All defects with severity, status, resolution
6. **Coverage Achieved** — Requirement and test level coverage %
7. **Residual Risk Acceptance** — Remaining risks documented
8. **Findings and Recommendations** — Issues, blockers, gaps
9. **Signoff Block** — Test lead, QA, project manager approval
10. **Lessons Learned Summary** — Recommendations for next cycle
11. **References** — Verification plan, test cases, standards

## Usage

```bash
python scripts/generate_vvr.py input.json output.xlsx
```
