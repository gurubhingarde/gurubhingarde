---
name: mbse-model-architecture-checklist-reviewer
description: Run a confirmation review on any MBSE model architecture xlsx workbook, executing 30+ checks across four ARCADIA layers to confirm structural completeness, inter-layer traceability, and readiness for Capella, Cameo, or Rhapsody import. Use this skill when the user mentions mbse model architecture checklist reviewer.
---

# mbse-model-architecture-checklist-reviewer

Run a confirmation review on any MBSE model architecture xlsx workbook, executing 30+ checks across four ARCADIA layers to confirm structural completeness, inter-layer traceability, and readiness for Capella, Cameo, or Rhapsody import.

Use this skill to audit MBSE model architecture workbooks for completeness, consistency, and traceability coverage.

## Inputs
- Completed mbse-model-architecture-builder xlsx workbook

## Outputs
- Confirmation checklist xlsx with dashboard, rating summary (FC/LC/PC/NO), findings, and recommended actions
- Visual compliance KPIs, per-layer coverage analysis

## Check Categories

1. **Structure** (5 checks): Tab completeness, document control, system identification
2. **Operational Layer** (6 checks): Scenario population, actor inventory, capability allocation
3. **System Layer** (6 checks): Function definition, interface specification, functional chains
4. **Logical Layer** (6 checks): Component decomposition, behavioral allocation, port definitions
5. **Physical Layer** (4 checks): Component deployment, hardware/software split, physical interfaces
6. **Traceability** (3 checks): Layer-to-layer links, end-to-end coverage, orphan detection

## Ratings
- FC (Fully Compliant): Passes all defined criteria
- LC (Largely Compliant): Minor gaps, easily resolved
- PC (Partially Compliant): Significant gaps requiring rework
- NO (Non-Compliant): Major deficiencies
- NA (Not Applicable): Check not relevant to this design
