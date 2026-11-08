---
name: autosar-bsw-config-builder
description: Generate an audit-ready AUTOSAR Classic BSW (Basic Software) configuration workbook per AUTOSAR R22-11 covering MCAL, ECU Abstraction, Service Layer, and Complex Driver modules with container parameters, post-build variants, and ECU-C top-level configuration for ECU integration projects. Use this skill when the user mentions autosar bsw config builder.
---

# autosar-bsw-config-builder

Generate an audit-ready AUTOSAR Classic BSW (Basic Software) configuration workbook per AUTOSAR R22-11 covering MCAL, ECU Abstraction, Service Layer, and Complex Driver modules with container parameters, post-build variants, and ECU-C top-level configuration for ECU integration projects.

## When to use

Use this skill whenever the user mentions AUTOSAR BSW, basic software config, MCAL, EcuC, or AUTOSAR Classic configuration.

## How to use

Provide or reference an ECU configuration:
- Target microcontroller model (vendor, part number)
- Bus interfaces (CAN, LIN, Ethernet, FlexRay)
- Memory layout (RAM, ROM, flash)
- Safety requirements (ASIL level if applicable)
- SWC (Software Component) list requiring BSW support

A worked sample input is shipped at `examples/sample_input.json`; run it with:

```
python scripts/generate_bsw.py examples/sample_input.json bsw_config.xlsx
```

The skill generates a 15-tab workbook with:
- ECU-C top-level configuration
- Bus interfaces (CAN, LIN, Ethernet, FlexRay)
- Module inventory per stack layer
- Container and parameter definitions
- Post-build variants
- Memory and task scheduling
- Inter-module dependencies
- Validation rules

## Output

Multi-tab XLSX workbook (audit-ready):
- Title, Document Control, ECU-C Top-Level, Bus Interfaces
- MCAL Module Inventory, ECU Abstraction, Service Layer, Complex Drivers
- Module Configuration Parameters (per module)
- Post-Build Variants, Memory Map, Schedule Tables
- Inter-Module Dependencies, Validation Rules, References
