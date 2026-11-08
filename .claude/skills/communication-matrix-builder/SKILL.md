---
name: communication-matrix-builder
description: Generate an audit-ready K-Matrix communication matrix workbook covering all bus traffic across CAN, CAN FD, LIN, FlexRay, and Automotive Ethernet networks for cross-ECU coordination and signal allocation. Accepts AUTOSAR system extracts or FIBEX inputs and outputs a 12-tab xlsx specification with message catalogs, sender-receiver tables, gateway routing requirements, and signal timing budgets. Use this skill whenever the user mentions a K-Matrix, communication matrix, signal database, cross-bus signal mapping, ECU signal allocation, gateway routing specification, or automotive network audit preparation.
---

# communication-matrix-builder

Generate an audit-ready K-Matrix communication matrix workbook covering all bus traffic across CAN, CAN FD, LIN, FlexRay, and Automotive Ethernet networks for cross-ECU coordination and signal allocation. Accepts AUTOSAR system extracts or FIBEX inputs and outputs a 12-tab xlsx specification with message catalogs, sender-receiver tables, gateway routing requirements, and signal timing budgets.

## When to use this skill

Use this skill whenever the user mentions K-Matrix, communication matrix, signal database, cross-bus signal mapping, vehicle network coordination, ECU signal allocation, gateway routing specification, or automotive network audit preparation.

## What you'll get

A production-ready K-Matrix workbook with:
- Title and Document Control tabs
- Vehicle Network Topology diagram
- ECU Inventory with bus memberships
- Message Catalog (consolidated across buses)
- Signal Catalog and ownership matrix
- Sender-Receiver Matrix
- Bus Allocation specifications
- Gateway Routing Requirements
- Signal Timing Budget analysis
- Validation Rules and References

## How to use it

1. Upload your AUTOSAR extract (XML/FIBEX) or JSON input describing ECUs, buses, messages, and signals
2. Specify the vehicle architecture (e.g., Classical CAN, CAN FD backbone with LIN clusters, Ethernet gateway)
3. Set signal timing constraints and gateway routing policies
4. Receive audit-ready K-Matrix workbook with cross-checks and traceability
