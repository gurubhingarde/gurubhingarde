---
name: autosar-rte-mapping-checklist-reviewer
description: Run a confirmation-measures compliance audit on any AUTOSAR RTE (Run-Time Environment) mapping specification xlsx per AUTOSAR R22-11. Validate data mappings, runnable-to-task allocation, exclusive area bindings, and timing consistency across AUTOSAR Classic ECU integration. Use this skill when the user mentions autosar rte mapping checklist reviewer.
---

# autosar-rte-mapping-checklist-reviewer

Run a confirmation-measures compliance audit on any AUTOSAR RTE (Run-Time Environment) mapping specification xlsx per AUTOSAR R22-11. Validate data mappings, runnable-to-task allocation, exclusive area bindings, and timing consistency across AUTOSAR Classic ECU integration.

## When to use

Use this skill whenever the user mentions AUTOSAR RTE mapping review, RTE validation, runnable-to-task verification, or RTE generation audit.

## How to use

Upload or reference an AUTOSAR RTE mapping xlsx workbook (output from autosar-rte-mapping-builder or any RTE mapping document):

The skill automatically:
- Probes the xlsx for SWC ports, Com signals, task allocations, exclusive areas, mode mappings
- Runs ~28 compliance checks covering port-to-signal mapping completeness, task allocation consistency, timing constraints, exclusive area bindings, priority inversion detection
- Generates a visual Summary dashboard with KPI tiles, pie chart, compliance % bars, and findings table
- Outputs a detailed checklist report with ratings (FC, LC, PC, NO, NA) and recommended actions

## Output

Multi-tab XLSX checklist report (audit-ready):
- Title, Document Control, Summary (dashboard + KPIs)
- Compliance results per mapping category (Data Mappings, Task Allocation, Exclusive Areas)
- Detailed findings, ratings, and recommended corrective actions
- References
