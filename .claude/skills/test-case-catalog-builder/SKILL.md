---
name: test-case-catalog-builder
description: Generate an audit-ready Test Case Catalog workbook capturing test case identification, preconditions, inputs, expected outputs, pass-fail criteria, traceability to requirements, test level (unit, integration, system, vehicle), test environment, automation status, and execution priority for safety and quality verification activities per ISO 26262 and IEEE 1012. Use this skill when the user mentions test case catalog builder.
---

## Overview

Generates a multi-tab ISO 26262 compliant Test Case Catalog (11-tab xlsx) documenting test case design with traceability and automation status.

## Inputs

JSON with test cases including ID, preconditions, inputs, expected outputs, pass/fail criteria, requirement traceability, test level, environment, automation status, and priority.

## Outputs

11-tab workbook:
1. **Title** — Project, scope
2. **Document Control** — Version history
3. **Test Case Inventory** — All test cases with IDs
4. **Preconditions** — System and environment setup per case
5. **Inputs** — Input values and ranges
6. **Expected Outputs** — Pass criteria definitions
7. **Pass-Fail Criteria** — Objective measurement rules
8. **Requirement Traceability** — Bidirectional links
9. **Test Level Allocation** — Unit/integration/system/vehicle
10. **Automation Status** — Manual/automated/deferred
11. **Execution Priority** — Must-run, should-run, nice-to-have

## Usage

```bash
python scripts/generate_tc_catalog.py input.json output.xlsx
```
