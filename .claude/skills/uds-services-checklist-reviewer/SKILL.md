---
name: uds-services-checklist-reviewer
description: Run a confirmation review on any UDS service catalog xlsx, generating an audit checklist with 30+ conformance checks against ISO 14229-1 standards covering service definitions, DID/RID uniqueness, security configuration, session dependencies, and timing parameters with dashboard visualization. Use this skill when the user mentions uds services checklist reviewer.
---

# uds-services-checklist-reviewer

Run a confirmation review on any UDS service catalog xlsx, generating an audit checklist with 30+ conformance checks against ISO 14229-1 standards covering service definitions, DID/RID uniqueness, security configuration, session dependencies, and timing parameters with dashboard visualization.

Use this skill whenever the user wants to verify an existing UDS diagnostic service specification for completeness, consistency, and ISO 14229-1 compliance.

## Overview

Audits a 13-tab UDS service catalog xlsx workbook. Executes 30+ confirmation and technical checks covering:
- Service inventory completeness (0x10-0x86 support)
- DID and RID uniqueness and address ranges
- Security access level configuration and completeness
- Session dependency rules and restrictions
- Timing parameter validity (P2, P2*, S3 ranges)
- Negative response code mappings
- Memory programming address layout
- Service-to-session binding validation

## Input

- UDS service catalog xlsx workbook (13 tabs: Title, Document Control, ECU Diagnostic Identity, Session Definitions, Service Inventory, DID Catalog, RID Catalog, Security Access Configuration, Negative Response Codes, Timing Parameters, Memory Programming Layout, Validation Rules, References)

## Output

Checklist xlsx with tabs:
1. Title — Review metadata
2. General Info — Document structure guide
3. Guide — Rating and interpretation rules
4. Summary — Visual dashboard with KPI tiles, compliance pie chart, findings table
5. Confirmation Review — 14 document-quality checks (ISO 14229 conventions)
6. Technical Assessment — 16 UDS-specific checks (service completeness, DID/RID integrity, security, timing)

Ratings: FC (Fully Conformant), LC (Largely Conformant), PC (Partially Conformant), NO (Not Conformant), NA (Not Applicable)

## Usage

```bash
python scripts/generate_checklist.py <uds_services.xlsx> <output_checklist.xlsx>
```

Optionally run probe-only (no xlsx):
```bash
python scripts/uds_probe.py <uds_services.xlsx>
```
