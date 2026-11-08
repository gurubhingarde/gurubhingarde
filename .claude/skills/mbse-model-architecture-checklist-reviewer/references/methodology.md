# MBSE Model Architecture Checklist Methodology

## Purpose

Confirm that MBSE model architecture workbooks are complete, consistent, and ready for import into Capella, Cameo, or Rhapsody.

## Check Categories

1. **Structure**: Workbook tabs, document control, system identification
2. **Operational Layer**: Scenarios, capabilities, actor inventory
3. **System Layer**: Functions, interfaces, functional chains
4. **Logical Layer**: Components, behavioral allocation, ports
5. **Physical Layer**: Hardware/software split, deployment
6. **Traceability**: Inter-layer coverage, orphan detection

## Ratings

- **FC (Fully Compliant)**: All criteria met
- **LC (Largely Compliant)**: Minor gaps, easily resolved
- **PC (Partially Compliant)**: Significant gaps requiring rework
- **NO (Non-Compliant)**: Major deficiencies blocking import
- **NA (Not Applicable)**: Not relevant to this design

## Recommended Workflow

1. Run checklist on draft model
2. Address all NO findings first
3. Resolve PC findings where feasible
4. Review LC findings with domain expert
5. Re-checklist after rework
6. Proceed to tool import when FC/LC only
