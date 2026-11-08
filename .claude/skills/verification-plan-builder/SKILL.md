---
name: verification-plan-builder
description: Generate an audit-ready Verification Plan workbook per ISO 26262-8 Section 9 and IEEE 1012 covering verification scope, verification methods (review, analysis, simulation, test), per-requirement verification objectives, traceability targets, environment definitions, schedule, and acceptance criteria for safety and quality lifecycle verification activities. Use this skill when the user mentions verification plan builder.
---

## Overview

Generates a multi-tab ISO 26262-8 §9 compliant Verification Plan (11-tab xlsx) that documents the complete verification strategy, method allocation, environment configuration, and acceptance criteria.

## Inputs

JSON file with structure:
```json
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "scope_description": str,
  "requirements": [{id, title, safety_level}],
  "verification_methods": [{method, applicability, level}],
  "environments": {hil: {desc, tools}, sil: {desc, tools}, vehicle: {desc}, bench: {desc}},
  "test_levels": [{level, description, scope}],
  "schedule": [{phase, start, end, activities}],
  "acceptance_criteria": [{criterion, measurement, pass_threshold}]
}
```

## Outputs

11-tab workbook:
1. **Title** — Project, scope, document control
2. **Document Control** — Version history, review/approval
3. **Verification Scope** — Item definition, safety goals, scope boundaries
4. **Verification Strategy** — Overall approach, V-cycle mapping
5. **Method Allocation per Requirement** — review, analysis, simulation, test per req
6. **Environment Definitions** — HIL, SIL, Vehicle, Bench specs
7. **Test Levels** — Unit, integration, system, vehicle breakdown
8. **Schedule** — Timeline, phases, milestones
9. **Roles and Responsibilities** — Test lead, reviewers, signoff
10. **Acceptance Criteria** — Pass/fail metrics, coverage thresholds
11. **References** — Applicable standards, requirements documents

## Usage

```bash
python scripts/generate_vplan.py input.json output.xlsx
```
