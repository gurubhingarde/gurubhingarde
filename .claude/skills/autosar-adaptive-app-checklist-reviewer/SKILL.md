---
name: autosar-adaptive-app-checklist-reviewer
description: Run a confirmation-measures compliance audit on any AUTOSAR Adaptive Application specification xlsx per AUTOSAR Adaptive Platform R22-11. Validate application manifests, service manifests, ara - -com interfaces, ara - -exec lifecycle, and deployment topology for service-oriented automotive applications. Use this skill when the user mentions autosar adaptive app checklist reviewer.
---

# autosar-adaptive-app-checklist-reviewer

Run a confirmation-measures compliance audit on any AUTOSAR Adaptive Application specification xlsx per AUTOSAR Adaptive Platform R22-11. Validate application manifests, service manifests, ara::com interfaces, ara::exec lifecycle, and deployment topology for service-oriented automotive applications.

## When to use

Use this skill whenever the user mentions AUTOSAR Adaptive app review, Adaptive Application validation, ara::com verification, application manifest audit, or service-oriented automotive software verification.

## How to use

Upload or reference an AUTOSAR Adaptive Application xlsx workbook (output from autosar-adaptive-app-builder or any Adaptive App specification document):

The skill automatically:
- Probes the xlsx for application manifest, service interfaces, machine manifest, ara::exec states, deployment topology
- Runs ~28 compliance checks covering manifest completeness, service instance mapping, ara::exec state consistency, SOME/IP uniqueness, resource budget feasibility
- Generates a visual Summary dashboard with KPI tiles, pie chart, compliance % bars, and findings table
- Outputs a detailed checklist report with ratings (FC, LC, PC, NO, NA) and recommended actions

## Output

Multi-tab XLSX checklist report (audit-ready):
- Title, Document Control, Summary (dashboard + KPIs)
- Compliance results per specification category (Application Manifest, Service Manifest, ara::exec)
- Detailed findings, ratings, and recommended corrective actions
- References
