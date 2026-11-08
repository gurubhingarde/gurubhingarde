---
name: gateway-routing-builder
description: Generate an audit-ready gateway routing specification workbook for vehicle network gateway ECUs covering signal, PDU, and frame routing across CAN, CAN FD, LIN, FlexRay, and Automotive Ethernet with latency budgets and security rules Use this skill when the user mentions gateway routing builder.
---

# Gateway Routing Builder

Build a professional 11-tab xlsx workbook specifying how a gateway ECU routes signals, PDUs, and frames between buses.

## What this skill does

- Generates audit-ready gateway routing specification
- Supports multi-protocol environments (CAN, CAN FD, LIN, FlexRay, Ethernet)
- Defines per-route signal/PDU/frame mappings
- Includes latency budgets and path analysis
- Specifies security and firewall rules for inter-domain routing
- Provides performance validation and diagnostic routing

## How to use it

Provide a JSON input with:
- Gateway ECU definition
- Source and destination bus inventories
- Routing table (signal/PDU, source bus, destination bus, transformation rules)
- Latency budget per route
- Security/firewall rules

## What you get

11-tab professional xlsx:
1. Title
2. Document Control
3. Gateway ECU Definition
4. Source Bus Inventory
5. Destination Bus Inventory
6. Routing Table (live formulas)
7. Latency Budget per Route
8. Security/Firewall Rules
9. Performance Validation
10. Diagnostic Routing
11. References

---

*Use this skill whenever the user mentions gateway routing, ECU gateway, cross-bus signal routing, AUTOSAR PDU router, or central gateway specification.*
