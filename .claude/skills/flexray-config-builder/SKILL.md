---
name: flexray-config-builder
description: Generate an audit-ready FlexRay cluster configuration workbook per ISO 17458 covering communication cycle structure, static and dynamic segments, frame allocation, slot assignment, and cluster timing parameters for time-triggered and event-triggered automotive networks.
---

# FlexRay Configuration Builder

Generates a complete, audit-ready FlexRay cluster configuration xlsx per ISO 17458. Covers communication cycle structure, static and dynamic segments, frame allocation, slot assignment, cluster timing parameters (gdCycle, gdMacrotick, gMacroPerCycle, etc.), and both Channel A and Channel B dual-redundancy configuration.

## When to use this skill

Use whenever the user mentions:
- FlexRay, time-triggered networking, event-triggered networking
- ISO 17458 FIBEX FlexRay cluster design
- Static segment, dynamic segment, symbol window, NIT
- FlexRay cluster configuration, slot allocation
- Dual-channel A/B, 10 Mbps automotive networks

## Workflow

1. Gather item definition: cluster name, network topology, ECU list, timing constraints
2. Build input JSON per schema in `scripts/generate_flexray.py`
3. Generate: `python scripts/generate_flexray.py <input.json> <output.xlsx>`
4. Recalc formulas: `python scripts/recalc.py <output.xlsx>`
5. Review and iterate

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | Cluster name, project, doc ID, revision |
| 2 | Document Control | Revision history, distribution list |
| 3 | Cluster Parameters | gdCycle, gdMacrotick, gMacroPerCycle, gNumberOfStaticSlots, gNumberOfMinislots, channel speeds |
| 4 | Channel A/B Config | PHY layer, link speed, duplex settings per channel |
| 5 | Node Inventory | ECUs, controllers, timing properties per node |
| 6 | Frame Catalog | All frames with CAN-like identifiers, data length, priority |
| 7 | Static Slot Allocation | Slot assignment for time-triggered frames |
| 8 | Dynamic Slot Allocation | Minislot assignment for event-triggered frames |
| 9 | Symbol Window | NIT, CAS, DTS timing |
| 10 | Validation Rules | Formulas checking cycle timing consistency |
| 11 | References | ISO 17458 and FlexRay specification citations |
| 12 | Recalc Notes | Formula evaluation metadata |

## Files

```
flexray-config-builder/
├── SKILL.md
├── scripts/
│   ├── generate_flexray.py
│   ├── recalc.py
│   └── office/soffice.py
├── references/
│   ├── methodology.md
│   └── flexray_conventions.md
└── examples/
```
