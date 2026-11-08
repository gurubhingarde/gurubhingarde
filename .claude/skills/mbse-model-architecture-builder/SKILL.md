---
name: mbse-model-architecture-builder
description: Generate an audit-ready MBSE model architecture workbook scaffolding the four ARCADIA layers of operational, system, logical, and physical analysis with viewpoints, structural elements, behavioral elements, and inter-layer traceability for Capella, Cameo, or Rhapsody import preparation per INCOSE and OMG MBSE practices. Use this skill when the user mentions mbse model architecture builder.
---

# mbse-model-architecture-builder

Generate an audit-ready MBSE model architecture workbook scaffolding the four ARCADIA layers of operational, system, logical, and physical analysis with viewpoints, structural elements, behavioral elements, and inter-layer traceability for Capella, Cameo, or Rhapsody import preparation per INCOSE and OMG MBSE practices.

Use this skill whenever the user mentions MBSE, model-based systems engineering, ARCADIA, Capella, Cameo, MagicGrid, system architecture model, or four-layer engineering model.

## Inputs
- JSON describing system identification, operational context, system functions, logical architecture, physical deployment
- Viewpoint definitions, assumptions, design constraints

## Outputs
- 12-tab xlsx workbook: Title, Document Control, System Identification, Operational Analysis, System Analysis, Logical Analysis, Physical Analysis, Viewpoint Inventory, Inter-Layer Traceability, Modeling Conventions, Validation Rules, References
- Engineering-ready scaffolding for Capella/Cameo/Rhapsody import

## Example

```json
{
  "system": {
    "name": "Autonomous Vehicle",
    "abbr": "AV",
    "description": "Electric autonomous vehicle platform"
  },
  "operational_scenarios": [
    {"id": "OS01", "name": "Highway Cruising", "actors": ["Driver", "Environment"], "description": "Steady-state highway travel"}
  ],
  "system_functions": [
    {"id": "SF01", "name": "Manage Motion", "description": "Plan and execute vehicle motion"}
  ]
}
```
