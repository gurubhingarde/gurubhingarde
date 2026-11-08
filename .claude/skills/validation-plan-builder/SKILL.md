---
name: validation-plan-builder
description: Generate an audit-ready Validation Plan workbook per ISO 26262-4 Section 9 covering validation scope, validation against safety goals, validation environments including vehicle level testing, validation scenarios, customer-relevant use cases, exit criteria, and signoff for end-of-development item validation activities. Use this skill when the user mentions validation plan builder.
---

## Overview

Generates a multi-tab ISO 26262-4 §9 compliant Validation Plan (11-tab xlsx) documenting validation strategy against safety goals, end-to-end scenarios, and customer use cases.

## Inputs

JSON file with structure:
```json
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "scope_description": str,
  "safety_goals": [{id, goal, metric}],
  "validation_environments": [{env, description, location}],
  "scenarios": [{id, description, use_case, edge_case}],
  "validation_methods": [{method, applicability}],
  "exit_criteria": [{criterion, measurement, threshold}],
  "resources": [{resource, quantity, specification}]
}
```

## Outputs

11-tab workbook:
1. **Title** — Project, scope, document control
2. **Document Control** — Version history, review/approval
3. **Validation Scope** — Item definition, safety goals vs requirements
4. **Validation Environments** — Vehicle, proving ground, public road specs
5. **Scenario Catalog** — Operational scenarios, edge cases, use cases
6. **Use Cases** — Customer workflows, safety-relevant interactions
7. **Validation Methods** — Testing approaches (bench, track, road, simulation)
8. **Schedule** — Timeline, resource allocation
9. **Resources** — Test vehicles, drivers, instrumentation, test sites
10. **Exit Criteria and Signoff** — Pass/fail metrics, approval authority
11. **References** — Safety goals, system requirements, test plan links
