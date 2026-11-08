# AUTOSAR Composition SWC Specification Methodology

## Overview

Composition SWCs provide hierarchical decomposition in AUTOSAR. A composition encapsulates multiple SWCs and exposes a port boundary, enabling modular architectures and reusable assemblies.

## Key Concepts

**Assembly Connectors**: Intra-composition links connecting a Provided port (from one SWC) to a Required port (from another SWC).

**Delegation Connectors**: Mapping from internal SWC ports to the composition's outer boundary ports, externalizing functionality.

**Port Boundary**: The set of ports exposed by the composition to external consumers, aggregated via delegation.

**Hierarchy Tree**: Composition contains SWC instances; compositions may themselves be SWC instances in a parent composition.

## Validation Rules

1. Every SWC instance must be wired via assembly or delegation connectors.
2. Assembly connectors must link compatible port interfaces.
3. Delegation connectors must map all exposed functionality to the boundary.
4. No orphaned ports; all boundary ports must be backed by delegation.

## Best Practices

- Use descriptive instance names (e.g., BrakeSWC_Instance, ClimateControl_Comp)
- Document each connector with source/target interface types
- Validate port multiplicity rules
- Trace hierarchy through the Hierarchy Tree tab
