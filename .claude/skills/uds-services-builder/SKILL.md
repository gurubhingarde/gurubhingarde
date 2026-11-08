---
name: uds-services-builder
description: Generate an audit-ready UDS service catalog workbook per ISO 14229-1 covering supported diagnostic services (0x10-0x86), sub-functions, DID and RID catalogs, session control (default/programming/extended), SecurityAccess levels and seed/key handling, negative response codes (NRC), P2/P2*/S3 timing, and memory programming layout for a target ECU. Use this skill whenever the user mentions UDS, ISO 14229, ISO 14229-1, diagnostic services, DID catalog, RID catalog, SecurityAccess, programming session, extended session, NRC, P2/P2*/S3 timing, or ECU diagnostic specification — even casual phrasings like 'spec the diagnostics for this ECU', 'what DIDs does this ECU support', or 'write up the UDS services'. Use uds-services-builder for the protocol-neutral ISO 14229-1 service catalog; for ODX export use odx-builder, for CANdela use cdd-builder, for DTC inventory use dtc-catalog-builder, and for the AUTOSAR Dem runtime layer use dem-config-builder.
---

# uds-services-builder

Generate an audit-ready UDS service catalog workbook per ISO 14229-1 covering all supported diagnostic services, sub-functions, DIDs, RIDs, security access levels, session dependencies, and timing parameters for a target ECU.

Use this skill whenever the user mentions UDS, ISO 14229 / ISO 14229-1, diagnostic services, DID or RID catalog, SecurityAccess, programming or extended session, NRC, or ECU diagnostic specification — including casual phrasings like 'spec the diagnostics for this ECU'. For ODX export use odx-builder, for CANdela use cdd-builder, for DTC inventory use dtc-catalog-builder, and for the AUTOSAR Dem runtime layer use dem-config-builder.

## Overview

Produces a 13-tab xlsx workbook for specifying all UDS diagnostic services supported by an ECU. Captures service inventory (0x10-0x86), session definitions, DID/RID catalogs, security access configuration, negative response codes, timing parameters, and memory programming layout.

## Input

JSON file with:
- `item`: name, abbr, project, doc_id, revision, date, author, approver, company
- `ecu_identity`: logical_address, physical_address, functional_address, hw_part_number
- `session_definitions`: default, programming, extended session properties
- `service_inventory`: all supported services with sub-functions
- `did_catalog`: read/write data identifiers with security level, session restriction
- `rid_catalog`: routine IDs with execution parameters
- `security_access`: security levels, seed/key algorithm references
- `negative_response_codes`: NRC list with meanings
- `timing_parameters`: P2, P2*, S3 values in milliseconds
- `memory_programming_layout`: start address, size, erase block size

## Output

13-tab Excel workbook:
1. Title — Document metadata
2. Document Control — Revision history
3. ECU Diagnostic Identity — Addressing (logical, physical, functional)
4. Session Definitions — Session types and restrictions
5. Service Inventory — All 0x10-0x86 supported services
6. DID Catalog — Read/Write Data Identifier specifications
7. RID Catalog — Routine ID definitions
8. Security Access Configuration — Security levels and algorithms
9. Negative Response Codes — NRC meanings and triggers
10. Timing Parameters — P2, P2*, S3, session timeouts
11. Memory Programming Layout — Flash memory organization
12. Validation Rules — Input validation and constraints
13. References — ISO 14229-1 service index and conventions

## Usage

```bash
python scripts/generate_uds.py input.json output.xlsx
```
