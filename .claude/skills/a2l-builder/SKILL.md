---
name: a2l-builder
description: Generate an audit-ready A2L (ASAM MCD-2 MC) calibration description authoring workbook per ASAM MCD-2 MC v1.7 covering characteristics, measurements, conversion methods, axis descriptions, record layouts, function definitions, group hierarchy, and memory address mapping for ETK, XCP, and CCP calibration tooling. Use this skill whenever the user mentions A2L, ASAM MCD-2 MC, calibration description, INCA, CANape, characteristic catalog, measurement catalog, or ECU calibration definition.
---

# a2l-builder

Generate an audit-ready A2L (ASAM MCD-2 MC) calibration description authoring workbook per ASAM MCD-2 MC v1.7 covering characteristics, measurements, conversion methods, axis descriptions, record layouts, function definitions, group hierarchy, and memory address mapping for ETK, XCP, and CCP calibration tooling.

Use this skill whenever the user mentions A2L, ASAM MCD-2 MC, calibration description, INCA, CANape, characteristic catalog, measurement catalog, or ECU calibration definition.

## Output

Generates 13-tab Excel workbook with:

- **Title** — Document control header, item identity, revision, author, approver
- **Document Control** — Change log, document properties, approval chain
- **ECU Identity** — Memory map, EPK, ECU address space layout
- **Characteristic Catalog** — VALUE, CURVE, MAP, AXIS_PTS, VAL_BLK parameter definitions
- **Measurement Catalog** — Measurement signals, observable parameters
- **Conversion Methods** — LINEAR, RAT_FUNC, TAB_INTP, TAB_NOINTP, FORMULA definitions
- **Axis Descriptions** — COM_AXIS, RES_AXIS, STD_AXIS point definitions
- **Record Layouts** — STRUCTURE definitions for composite objects
- **Function Hierarchy** — GROUP, FUNCTION nesting and organization
- **Group Hierarchy** — Logical grouping tree
- **Memory Address Mapping** — Address assignment, segment layout, overlap detection
- **Validation Rules** — Consistency checks, naming rules
- **References** — Bibliography, ASAM MCD-2 MC v1.7 cross-references

## Usage

```bash
python generate_a2l.py <input.json> <output.xlsx>
```

Input JSON contains item metadata, ECU identity, characteristics, measurements, conversion methods, axes, records, functions, groups, and memory map.

## References

See `references/methodology.md` for design guidance and `references/a2l_object_types.md` for ASAM object type definitions.
