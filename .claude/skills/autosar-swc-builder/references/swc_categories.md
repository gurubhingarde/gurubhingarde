# AUTOSAR SWC Categories and Implementation Types

## Category Definitions (AUTOSAR R22-11)

### Application SWC
Core vehicle logic implementing active safety, propulsion, or comfort features. Example: ABS controller, cruise control, climate comfort module.

**Characteristics:**
- Highest complexity and interaction density
- Typically multiple ports and runnables
- Requires extensive internal behavior definition
- Often targets ASIL B–D functions

### Sensor/Actuator SWC
Hardware interface abstraction layer. Example: wheel speed sensor driver, brake pressure actuator interface.

**Characteristics:**
- Bridging physical I/O and virtual signal space
- Defined by sensor/actuator semantics (raw counts, physical units)
- Linear or piecewise-linear transformations common
- Lower-complexity internal logic

### Service SWC
Supporting infrastructure and cross-cutting concerns. Example: diagnostics server, communication manager, timing synchronizer.

**Characteristics:**
- Often stateless or lightly stateful
- Serves multiple clients via standardized interfaces
- Timing and throughput critical
- Limited exclusive area requirement

### Complex Driver
Integration or abstraction layer managing multiple subordinate SWCs. Example: integrated powertrain coordinator, integrated safety manager.

**Characteristics:**
- Orchestration and mode management
- Mode-switch port interfaces common
- Hierarchical composition (via Composition SWCs)
- Boundary-crossing coordination

## Implementation Type Options

- **Software**: Pure algorithmic SWC (most common)
- **Hardware**: Physical interface wrapping (unusual)
- **Mixed**: Software with hardware-tightly-coupled behavior
