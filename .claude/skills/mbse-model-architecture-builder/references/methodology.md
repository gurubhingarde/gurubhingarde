# MBSE Model Architecture Methodology

## ARCADIA Layers

ARCADIA (Architecture Analysis and Design Integrated Approach) defines four successive analysis layers in MBSE:

1. **Operational Analysis**: Describes missions, capabilities, and scenarios independent of implementation
2. **System Analysis**: Defines system-level functions, exchanges, and interfaces
3. **Logical Analysis**: Decomposes system into logical components and their behavioral interactions
4. **Physical Analysis**: Maps logical components to physical elements (hardware/software)

## Viewpoints

Viewpoints organize architectural views for stakeholder communication:
- Operational Viewpoint (missions, actors, capabilities)
- Functional Viewpoint (system functions, data flows)
- Structural Viewpoint (component hierarchies)
- Behavioral Viewpoint (state machines, interactions)
- Deployment Viewpoint (physical allocation)

## Inter-layer Traceability

Traceability ensures complete coverage from requirements through physical implementation:
- Operational scenarios → System functions
- System functions → Logical components
- Logical components → Physical components
- Requirements → Implementation

## References

- INCOSE Systems Engineering Handbook (v4.0+)
- OMG MBSE Initiative
- Capella / Cameo / Rhapsody documentation
