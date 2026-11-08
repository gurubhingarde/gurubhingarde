---
name: autosar-bsw-config-checklist-reviewer
description: Run a confirmation-measures compliance audit on any AUTOSAR Classic Basic Software (BSW) configuration workbook xlsx per AUTOSAR R22-11. Validate MCAL layer, ECU Abstraction, Service Layer, and Complex Driver module configurations against BSW best practices and ECU-C integration requirements. Use this skill when the user mentions autosar bsw config checklist reviewer.
---

# autosar-bsw-config-checklist-reviewer

Run a confirmation-measures compliance audit on any AUTOSAR Classic Basic Software (BSW) configuration workbook xlsx per AUTOSAR R22-11. Validate MCAL layer, ECU Abstraction, Service Layer, and Complex Driver module configurations against BSW best practices and ECU-C integration requirements.

## When to use

Use this skill whenever the user mentions AUTOSAR BSW config review, BSW validation, MCAL verification, or ECU-C configuration audit.

## How to use

Upload or reference an AUTOSAR BSW configuration xlsx workbook (output from autosar-bsw-config-builder or any BSW config document):

The skill automatically:
- Probes the xlsx for module inventory, containers, parameters, memory mappings
- Runs ~30 compliance checks covering module completeness, MCAL target alignment, task scheduling, NvM alignment, parameter conflicts
- Generates a visual Summary dashboard with KPI tiles, pie chart, compliance % bars, and findings table
- Outputs a detailed checklist report with ratings (FC, LC, PC, NO, NA) and recommended actions

## Output

Multi-tab XLSX checklist report (audit-ready):
- Title, Document Control, Summary (dashboard + KPIs)
- Compliance results per module (MCAL, ECU Abstraction, Service Layer, Complex Drivers)
- Detailed findings, ratings, and recommended corrective actions
- References
