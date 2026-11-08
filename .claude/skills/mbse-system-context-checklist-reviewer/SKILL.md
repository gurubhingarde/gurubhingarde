---
name: mbse-system-context-checklist-reviewer
description: Run a confirmation review on any MBSE system context xlsx workbook, executing 25+ checks to confirm complete actor inventory, interface definition, use case population, and stakeholder needs capture. Use this skill when the user mentions mbse system context checklist reviewer.
---

# mbse-system-context-checklist-reviewer

Run a confirmation review on any MBSE system context xlsx workbook, executing 25+ checks to confirm complete actor inventory, interface definition, use case population, and stakeholder needs capture.

Use this skill to audit system context workbooks for completeness before operational analysis layer population.

## Inputs
- Completed mbse-system-context-builder xlsx workbook

## Outputs
- Confirmation checklist xlsx with dashboard, rating summary (FC/LC/PC/NO), findings, recommended actions
- Actor-interface consistency analysis, use case coverage, stakeholder needs traceability

## Check Categories

1. **Structure** (4 checks): Tabs present, document control, system identification
2. **Boundary** (3 checks): Boundary statement, scope exclusions, environment definition
3. **Actors** (5 checks): Actor inventory population, type assignment, goal clarity
4. **Interfaces** (5 checks): Every actor has interface, direction specified, media/protocol defined
5. **Use Cases** (4 checks): Primary/secondary actors, preconditions/postconditions, flow completeness
6. **Stakeholder Needs** (2 checks): Needs populated, priority assigned
7. **Scenarios** (2 checks): Multiple scenarios, consistency with use cases

## Ratings
- FC (Fully Compliant): All criteria met
- LC (Largely Compliant): Minor gaps, easily resolved
- PC (Partially Compliant): Significant gaps
- NO (Non-Compliant): Major deficiencies
- NA (Not Applicable): Not relevant
