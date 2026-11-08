---
name: sysml-block-diagram-builder
description: Generate an audit-ready SysML Block Definition Diagram and Internal Block Diagram authoring workbook per OMG SysML 1.6 and 2.0 capturing blocks, properties, parts, ports (flow, full, proxy), connectors, item flows, and value type definitions for system structural modeling in Cameo, Rhapsody, or Capella import. Use this skill when the user mentions sysml block diagram builder.
---

# sysml-block-diagram-builder

Generate an audit-ready SysML Block Definition Diagram and Internal Block Diagram authoring workbook per OMG SysML 1.6 and 2.0 capturing blocks, properties, parts, ports (flow, full, proxy), connectors, item flows, and value type definitions for system structural modeling in Cameo, Rhapsody, or Capella import.

**Use this skill whenever the user mentions SysML block diagram, BDD, IBD, system structural model, block hierarchy, flow ports, or proxy ports.**

## Generates
- 11-tab audit-ready xlsx workbook
- Blocks with <<block>>, <<actor>> stereotypes
- Properties, parts, reference properties per block
- Flow, full, and proxy port definitions
- Connector topology and item flows
- Value type and interface definitions
- Validation rules per SysML 1.6/2.0

## Tabs
0_Title, 1_Document_Control, 2_Model_Header, 3_Block_Catalog, 4_Property_Catalog, 5_Part_Reference_Properties, 6_Port_Catalog, 7_Connector_Catalog, 8_Item_Flow_Catalog, 9_Value_Type_Definitions, 10_References

## Usage
```bash
python scripts/generate_sysml_block.py <output.xlsx> --input model.json [--title "System"] [--author "Name"]
```
`--title` / `--author` override `system_name` / `author` from the JSON. Without `--input` the
catalog tabs are emitted with headers only (no placeholder rows) and a warning is printed.

## Input (JSON, all keys optional)
| Key | Shape | Feeds tab |
|---|---|---|
| `system_name`, `author`, `version` | strings | 0_Title, 1_Document_Control |
| `model_header` | `{purpose, viewpoint, scope, environment, assumptions, tool}` | 2_Model_Header |
| `blocks` | `[{name, stereotype, description, parent, multiplicity}]` | 3_Block_Catalog |
| `properties` | `[{block, name, type, multiplicity, description}]` | 4_Property_Catalog |
| `parts` | `[{owner, name, type, multiplicity, description}]` | 5_Part_Reference_Properties |
| `ports` | `[{owner, name, port_type, flow_type, direction, description}]` | 6_Port_Catalog |
| `connectors` | `[{name, source, target, type, description}]` — ports as `Block.port` | 7_Connector_Catalog |
| `item_flows` | `[{connector, item_type, multiplicity, direction, description}]` | 8_Item_Flow_Catalog |
| `value_types` | `[{name, base_type, description, unit}]` | 9_Value_Type_Definitions |
| `references` | `[{name, description}]` (appended after the OMG spec rows) | 10_References |

Worked example: `examples/sysml-block-diagram-builder/sample_input.json` (brake-by-wire, 5 blocks,
7 ports, 3 connectors). Connector `source`/`target` must name ports that exist in `ports`;
the paired reviewer's `BDD-12` checks both ends.

## Output
- Cameo/Rhapsody/Capella import ready
- All blocks stereotyped and validated
- Ports fully typed with directions
- Item flows on connectors mapped
