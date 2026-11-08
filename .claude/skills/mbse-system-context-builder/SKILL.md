---
name: mbse-system-context-builder
description: Generate an audit-ready MBSE system context workbook capturing system boundaries, external actors, system interfaces, operational scenarios, use cases, and stakeholder needs as the foundation for the operational analysis layer in ARCADIA, MagicGrid, or STRATA modeling methodologies per INCOSE Systems Engineering Handbook. Use this skill when the user mentions mbse system context builder.
---

# mbse-system-context-builder

Generate an audit-ready MBSE system context workbook capturing system boundaries, external actors, system interfaces, operational scenarios, use cases, and stakeholder needs as the foundation for the operational analysis layer in ARCADIA, MagicGrid, or STRATA modeling methodologies per INCOSE Systems Engineering Handbook.

Use this skill whenever the user mentions system context diagram, operational analysis, system boundary, actor inventory, use case model, or stakeholder needs capture.

## Inputs
- JSON describing system boundary, actor inventory, interfaces, use cases, scenarios, stakeholder needs

## Outputs
- 11-tab xlsx workbook: Title, Document Control, System Identification, System Boundary Definition, Actor Inventory, External Interfaces, Use Case Catalog, Operational Scenarios, Stakeholder Needs, Assumptions and Constraints, References
- Ready for operational analysis layer population in ARCADIA tool

## Example

```json
{
  "system": {"name": "Vehicle Automation", "abbr": "VA"},
  "actors": [
    {"id": "A01", "name": "Driver", "type": "human"},
    {"id": "A02", "name": "Road Network", "type": "system"}
  ],
  "use_cases": [
    {"id": "UC01", "name": "Enable Autonomous Driving", "actors": ["A01", "A02"]}
  ]
}
```
