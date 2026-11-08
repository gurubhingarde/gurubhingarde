---
name: arxml-system-checklist-reviewer
description: Run a confirmation review on any ARXML system specification xlsx, generating an audit checklist with 30+ conformance checks against AUTOSAR R22-11+ standards covering ECU mappings, signal composition, port interface bindings, and frame layouts with dashboard visualization. Use this skill when the user mentions arxml system checklist reviewer.
---

# arxml-system-checklist-reviewer

Run a confirmation review on any ARXML system specification xlsx, generating an audit checklist with 30+ conformance checks against AUTOSAR R22-11+ standards covering ECU mappings, signal composition, port interface bindings, and frame layouts with dashboard visualization.

Use this skill whenever the user wants to verify an existing ARXML system specification for completeness, consistency, and AUTOSAR compliance.

## Overview

Audits a 13-tab ARXML system specification xlsx workbook. Executes 30+ confirmation and technical checks covering:
- ECU instance definitions and mapping coverage
- Signal-to-PDU-to-frame composition completeness
- Port interface binding status
- Communication connector definitions
- Orphaned or unbound elements
- Data type consistency
- Trigger and event mapping validity

## Input

- ARXML system specification xlsx workbook (13 tabs: Title, Document Control, System Header, ECU Instances, System Mappings, Communication Connectors, Signal Catalog, PDU Catalog, Frame Catalog, Port Interfaces, Composition SWC References, Trigger and Event Mappings, References)

## Output

Checklist xlsx with tabs:
1. Title — Review metadata
2. General Info — Document structure guide
3. Guide — Rating and interpretation rules
4. Summary — Visual dashboard with KPI tiles, compliance pie chart, findings table
5. Confirmation Review — 14 document-quality checks (ISO 26262 Part 8)
6. Technical Assessment — 16 ARXML-specific checks (AUTOSAR composition, binding, frame layout)

Ratings: FC (Fully Conformant), LC (Largely Conformant), PC (Partially Conformant), NO (Not Conformant), NA (Not Applicable)

## Usage

```bash
python scripts/generate_checklist.py <arxml_system.xlsx> <output_checklist.xlsx>
```

Optionally run probe-only (no xlsx):
```bash
python scripts/arxml_probe.py <arxml_system.xlsx>
```
