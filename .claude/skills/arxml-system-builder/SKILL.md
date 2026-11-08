---
name: arxml-system-builder
description: Generate an audit-ready AUTOSAR ARXML system specification workbook per AUTOSAR Classic Platform R22-11+ covering ECU instances, system mappings, communication stack, FibexElements, port interfaces, and signal-to-PDU-to-frame composition for system extract authoring. Use this skill when the user mentions arxml system builder.
---

# arxml-system-builder

Generate an audit-ready AUTOSAR ARXML system specification workbook per AUTOSAR Classic Platform R22-11+ covering ECU instances, system mappings, communication stack, FibexElements, port interfaces, and signal-to-PDU-to-frame composition for system extract authoring.

Use this skill whenever the user mentions ARXML, AUTOSAR system extract, AUTOSAR system description, ECU instance, FibexElement, or AUTOSAR composition.

## Overview

Produces a 13-tab xlsx workbook for authoring AUTOSAR ARXML system extracts. Captures ECU instances, system mappings, communication stack, signal-to-PDU-to-frame composition, port interfaces (Sender-Receiver, Client-Server, Mode-Switch), and all dependencies needed before XML generation.

## Input

JSON file with:
- `item`: name, abbr, project, doc_id, revision, date, author, approver, company
- `ecu_instances`: list of ECU instances with names, comm stacks
- `system_mappings`: signal/PDU routing between ECUs
- `signal_catalog`: signals with properties (ID, length, byte order)
- `pdu_catalog`: PDUs with signal groupings
- `frame_catalog`: CAN/LIN frames with PDU packing
- `port_interfaces`: Sender-Receiver, Client-Server, Mode-Switch definitions
- `composition`: SWC references and triggers

## Output

13-tab Excel workbook:
1. Title — Document metadata
2. Document Control — Revision history
3. System Header — System context and scope
4. ECU Instances — All ECU definitions
5. System Mappings — Signal/PDU routing matrix
6. Communication Connectors — Logical network definitions
7. Signal Catalog — Signal properties and types
8. PDU Catalog — PDU compositions
9. Frame Catalog — Frame layouts (CAN/LIN/FlexRay)
10. Port Interfaces — Sender-Receiver, Client-Server, Mode-Switch
11. Composition SWC References — Component-to-port bindings
12. Trigger and Event Mappings — Timing and event triggers
13. References — Methodology and convention standards

## Usage

```bash
python scripts/generate_arxml_system.py input.json output.xlsx
```
