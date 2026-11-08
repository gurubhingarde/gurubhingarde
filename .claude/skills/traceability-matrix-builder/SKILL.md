---
name: traceability-matrix-builder
description: Generate an audit-ready bidirectional traceability matrix workbook linking stakeholder needs to system requirements to subsystem requirements to component requirements to design elements to test cases to test results per ISO 26262, ISO 21434, and IEEE 1012 traceability obligations including coverage analysis and orphan identification. Use this skill when the user mentions traceability matrix builder.
---

## Overview

Generates a multi-tab ISO 26262 compliant Traceability Matrix (11-tab xlsx) documenting bidirectional traceability from needs through tests with gap identification.

## Inputs

JSON with stakeholder needs, requirements (system/subsystem/component levels), design elements, and test cases with cross-references.

## Outputs

11-tab workbook:
1. **Title** — Project, scope
2. **Document Control** — Version history
3. **Trace Source Catalog** — All source elements (needs, reqs, design, tests)
4. **Forward Traceability** — Needs to tests forward trace
5. **Backward Traceability** — Tests to needs backward trace
6. **Coverage Analysis** — Orphan requirements and orphan tests
7. **Trace Quality Metrics** — Coverage %, completeness stats
8. **Gap Identification** — Missing links, untraceable items
9. **Trace Convention Rules** — ID patterns, link rules
10. **Validation Rules** — Coverage requirements (95% mandatory)
11. **References** — Standards, scope documents

## Usage

```bash
python scripts/generate_trace.py input.json output.xlsx
```
