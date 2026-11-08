---
name: autosar-rte-mapping-builder
description: Generate an audit-ready AUTOSAR RTE (Run-Time Environment) mapping specification workbook per AUTOSAR R22-11 covering data mappings, runnable to OS task allocation, exclusive area to OS resource binding, mode mappings, and signal-to-port routing for AUTOSAR Classic ECU integration projects. Use this skill when the user mentions autosar rte mapping builder.
---

# autosar-rte-mapping-builder

Generate an audit-ready AUTOSAR RTE (Run-Time Environment) mapping specification workbook per AUTOSAR R22-11 covering data mappings, runnable to OS task allocation, exclusive area to OS resource binding, mode mappings, and signal-to-port routing for AUTOSAR Classic ECU integration projects.

## When to use

Use this skill whenever the user mentions AUTOSAR RTE, RTE mapping, runnable-to-task, signal-to-port mapping, or RTE generation configuration.

## How to use

Provide or reference an RTE integration scope:
- SWC (Software Component) port list (sender-receiver, client-server, mode-switch)
- Com signal definitions and CAN/LIN signal layout
- Os task map (periodic tasks, task priorities, periods)
- Exclusive area list and OS resource assignments
- ECU timing constraints and mode-switch triggers

The skill generates a 12-tab workbook with:
- ECU integration identity and scope
- Data mappings (SWC port to Com signal)
- Runnable-to-task allocation and scheduling
- Exclusive area to OS resource binding
- Mode-switch mapping and trigger sources
- Memory mapping and stack sizing
- Validation rules

## Output

Multi-tab XLSX workbook (audit-ready):
- Title, Document Control, ECU Integration Identity
- Data Mappings, Runnable-to-Task Allocation
- Schedulable Period and Priority
- Exclusive Area to OS Resource
- Mode-Switch Mapping, Trigger Source Mappings
- Mem Mapping, Stack Sizing
- Validation Rules, References
