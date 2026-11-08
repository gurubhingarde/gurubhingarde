---
name: odx-builder
description: Generate an audit-ready ODX (Open Diagnostic Data Exchange) authoring workbook per ISO 22901-1 covering ECU base variants, derived variants, ODX layers (Data, Communication, Vehicle, Flash Data), PDU library, request/response definitions, DTCs, and data object properties for standardized diagnostic data exchange.
---

# ODX Builder

Generates a multi-tab ISO 22901-1 ODX authoring workbook from a JSON input.

## When to use this skill

- Author ODX diagnostic data exchange structures
- Define ECU base and derived variants
- Configure ODX-D (Data), ODX-C (Communication), ODX-V (Vehicle), ODX-FD (Flash Data) layers
- Build PDU libraries and service definitions
- Map DTCs to data objects
- Prepare for XML export and standardized diagnostic toolchain integration

## Workflow

1. Get the ODX requirements (ECU variants, services, PDUs, DTCs).
2. Read `references/methodology.md` and `references/odx_layers.md` on first use.
3. Prepare JSON input (see `examples/sample_input.json` for schema).
4. `python scripts/generate_odx.py <input.json> <output.xlsx>`
5. Review the workbook tabs in order: Title → Document Control → ODX Layer Hierarchy → variants → PDU Library → Services → Communication Parameters → Vehicle Info → Flash Data → Inherit-From Relationships → References.

## Output structure (13 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | Document header, project metadata |
| 2 | Document Control | Revision history, approvals, traceability |
| 3 | ODX Layer Hierarchy | Layer structure and dependencies (ODX-D/C/V/FD) |
| 4 | Base Variant Definition | ECU base variant, interfaces, communication channels |
| 5 | Derived Variants | Variant hierarchy, inherited properties |
| 6 | PDU Library | PDU definitions, structure, multiplexing |
| 7 | Diag Layer Containers | Container definitions and mapping |
| 8 | Service Definitions (ODX-D) | Request/response services, parameters, semantics |
| 9 | Communication Parameters (ODX-C) | Bus parameters, physical channels, timing |
| 10 | Vehicle Information (ODX-V) | Vehicle network topology, ECU mapping |
| 11 | Flash Data (ODX-FD) | Flash programming, memory layout |
| 12 | Inherit-From Relationships | Variant inheritance chains, property override |
| 13 | References | External file links, standard references |

## Files in this skill

```
odx-builder/
├── SKILL.md
├── scripts/
│   ├── generate_odx.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── odx_layers.md
```
