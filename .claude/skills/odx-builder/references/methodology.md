# ODX Builder Methodology

## ODX Overview

ODX (Open Diagnostic Data Exchange) is a standardized XML format per ISO 22901-1 for describing automotive ECU diagnostic data, services, and communication parameters. ODX enables interoperability between diagnostic tools, testers, and ECU suppliers by providing a machine-readable specification of diagnostic interfaces.

## ODX Layers

ODX is structured in four layers, each addressing a specific aspect of diagnostic communication:

### ODX-D (Data Layer)
Describes the diagnostic data and services offered by an ECU:
- Service definitions (request/response pairs)
- Parameters and their semantics
- Data object properties (units, conversion formulas, ranges)
- DTC (Diagnostic Trouble Code) definitions
- Positive/negative response specifications

### ODX-C (Communication Layer)
Specifies the lower-level communication parameters:
- Physical channels (CAN, LIN, Ethernet, K-Line)
- Bus speeds and baud rates
- Timing parameters (timeouts, inter-frame delays)
- Flow control mechanisms
- Protocol-specific headers and responses

### ODX-V (Vehicle Layer)
Defines the vehicle network topology and variant strategy:
- ECU mapping in the vehicle
- Variant hierarchies (base variants, derived variants)
- Inherit-From relationships for code reuse
- Vehicle configuration parameters

### ODX-FD (Flash Data Layer)
Describes the programming interface for ECU firmware updates:
- Memory layout and segments
- Programming sequences and algorithms
- CRC algorithms and checksums
- Security access procedures

## Variant Patterns

### Base Variant
A base variant is a complete, self-contained diagnostic description of an ECU. It defines:
- ECU identification (part number, serial number)
- Supported services
- Communication channels
- Data objects

### Derived Variant
A derived variant specializes or extends a base variant by:
- Overriding service definitions
- Adding vehicle-specific data objects
- Disabling certain services (e.g., for market-specific variants)
- Inheriting the majority of the base variant's specification

### Inheritance Chain
Variants can be organized hierarchically to minimize duplication:
```
Base-ECU-A
  ├─ Variant-1 (market A)
  ├─ Variant-2 (market B)
  └─ Variant-3 (market C)
```

## Authoring Workflow

1. **Define Item Metadata**: Project name, ECU abbreviation, document control info
2. **Establish Layer Hierarchy**: List all ODX layers needed (typically all four)
3. **Define Variants**: Create base variant(s), then derived variants
4. **Build PDU Library**: Define all protocol data units (requests, responses)
5. **Define Services**: Map each service to request/response PDUs
6. **Specify Parameters**: Add communication timing, bus speed, flow control
7. **Add Vehicle Info**: Vehicle topology, ECU network placement
8. **Configure Flash Data**: Memory segments, programming info
9. **Define Relationships**: Inherit-From chains for variant inheritance
10. **Export to XML**: Use ODX XML export tools to generate the final deliverable

## Key Compliance Points

- Every base variant must have a unique ECU ID
- Every derived variant must inherit from a base variant
- Every service must have both request and response PDU definitions
- PDU library must include all referenced PDUs
- Communication parameters must align with the physical protocol (CAN/LIN/Ethernet)
- Flash data must define at least Boot and Application memory segments
- No circular inheritance (parent cannot inherit from child)

## Integration Points

The ODX workbook serves as the source for:
- ODX XML export (via ODX export tools)
- UDS service specification (ISO 14229-1 mapping)
- Vehicle diagnostic tool calibration
- Test case generation for diagnostic verification
- OBD-II compliance documentation
