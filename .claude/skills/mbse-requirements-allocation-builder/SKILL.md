---
name: mbse-requirements-allocation-builder
description: Generate an audit-ready MBSE requirements allocation matrix workbook capturing system, sub-system, and component-level requirement decomposition with allocation to logical and physical model elements, satisfaction relationships, derive relationships, verify relationships, and trace coverage analysis per INCOSE Requirements Engineering practices. Use this skill when the user mentions mbse requirements allocation builder.
---

# mbse-requirements-allocation-builder

Generate an audit-ready MBSE requirements allocation matrix workbook capturing system, sub-system, and component-level requirement decomposition with allocation to logical and physical model elements, satisfaction relationships, derive relationships, verify relationships, and trace coverage analysis per INCOSE Requirements Engineering practices.

Use this skill whenever the user mentions requirements allocation, requirements decomposition, satisfy relationship, verify relationship, derive relationship, requirements model, or MBSE traceability matrix.

## Inputs
- JSON describing requirement hierarchy (stakeholder, system, sub-system, component), allocation targets, relationships

## Outputs
- 11-tab xlsx workbook: Title, Document Control, Requirements Catalog, Allocation Matrix, Decomposition Tree, Satisfy Relationships, Derive Relationships, Verify Relationships, Coverage Analysis, Validation Rules, References
- Engineering-ready allocation and traceability scaffolding

## Example

```json
{
  "system": {"name": "Autonomous Vehicle", "abbr": "AV"},
  "requirements": [
    {"id": "SR01", "level": "system", "text": "Vehicle shall navigate autonomously", "parent": null},
    {"id": "SSR01", "level": "subsystem", "text": "Perception subsystem shall detect obstacles", "parent": "SR01"}
  ]
}
```
