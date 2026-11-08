---
name: dem-config-builder
description: Generate an audit-ready AUTOSAR DEM (Diagnostic Event Manager) configuration workbook per AUTOSAR Classic Platform SWS_Dem covering event configuration, debounce algorithms, confirmation and healing logic, snapshot record allocation, extended data records, NvM storage assignments, and OBD freeze frame configuration for production AUTOSAR ECUs.
---

# DEM Config Builder

Generates a multi-tab AUTOSAR DEM configuration workbook from a JSON input.

## When to use this skill

- Configure AUTOSAR DEM event handling and runtime behavior
- Set debounce counter thresholds (pre-passed, pre-confirmed, confirmed, healed)
- Allocate snapshot and extended data records to ECU memory
- Map DTC catalog to DEM event configuration
- Configure OBD freeze frame capture
- Assign NvM blocks for primary/secondary event memory

## Workflow

1. Get the DEM configuration requirements (DTC list, debounce strategy, memory limits).
2. Read `references/methodology.md` and `references/dem_conventions.md` on first use.
3. Prepare JSON input (see `examples/sample_input.json` for schema).
4. `python scripts/generate_dem.py <input.json> <output.xlsx>`
5. Review the workbook tabs in order: Title → Document Control → Module ID → Event Inventory → Debounce Config → Memory Allocation → Snapshot/EDR records → NvM Mapping → Aging Cycles → OBD Freeze Frame → References.

## Output structure (13 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | Document header, project metadata |
| 2 | Document Control | Revision history, approvals |
| 3 | Module Identification | DEM module info, variant assignment |
| 4 | Event Inventory | DTC catalog mapped to events |
| 5 | Debounce Configuration | Counter-based thresholds per event |
| 6 | Memory Allocation | Primary, Secondary, MirrorMem regions |
| 7 | Snapshot Record Class | Snapshot data group allocation |
| 8 | Extended Data Record | EDR configuration and allocation |
| 9 | NvM Block Mapping | Block IDs for storage persistence |
| 10 | Aging Cycles | Cycle counters for aging logic |
| 11 | Operation Cycles | OBD operation cycle definition |
| 12 | OBD Freeze Frame Layout | Freeze frame structure and data assignment |
| 13 | References | Standard references and external links |

## Files in this skill

```
dem-config-builder/
├── SKILL.md
├── scripts/
│   ├── generate_dem.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── dem_conventions.md
```
