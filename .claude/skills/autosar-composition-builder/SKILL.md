---
name: autosar-composition-builder
description: Generate an audit-ready AUTOSAR Composition SWC specification workbook per AUTOSAR R22-11 covering composition hierarchy, contained SWC instances, assembly connectors, delegation connectors, port mappings, and port boundary aggregation for hierarchical software component composition. Use this skill when the user mentions autosar composition builder.
---

# autosar-composition-builder

Generate an audit-ready AUTOSAR Composition SWC specification workbook per AUTOSAR R22-11 covering composition hierarchy, contained SWC instances, assembly connectors, delegation connectors, port mappings, and port boundary aggregation for hierarchical software component composition.

## Usage

Use this skill whenever the user mentions AUTOSAR composition, composition SWC, assembly connector, delegation connector, or hierarchical SWC structure.

## Inputs

Accepts a JSON input file with composition name, contained SWC instances, assembly connectors (port-to-port within composition), delegation connectors (outer boundary), port mappings, and variation points.

## Output

Produces a 12-tab audit-ready xlsx workbook:
- Title, Document Control
- Composition Identity
- Contained SWC Instances
- Assembly Connectors (port-to-port)
- Delegation Connectors (outer boundary)
- Port Boundary
- Hierarchy Tree
- Variation Points (if used)
- Port Compatibility Rules
- Validation Rules
- References

---

**Commands:**
- `/autosar-composition-builder <Composition name> <count-swc>` — generate composition workbook
