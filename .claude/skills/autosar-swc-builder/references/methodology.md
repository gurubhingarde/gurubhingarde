# AUTOSAR Classic SWC Specification Methodology

## Overview

This methodology guides creation of audit-ready AUTOSAR R22-11 Software Component (SWC) specifications suitable for architecture review, safety certification, and production deployment.

## SWC Categories

- **Application SWC**: Core vehicle functions (brake control, steering, climate)
- **Sensor/Actuator SWC**: Interface with hardware (sensor drivers, actuator controllers)
- **Service SWC**: Supporting services (diagnostics, communication, timing)
- **Complex Driver**: Specialized integration layer

## Key Artifacts

1. **Port Inventory**: Comprehensive catalog of all provided and required ports
2. **Internal Behavior**: Runnable definitions, event triggers, exclusive areas
3. **Data Types**: Application and implementation type definitions per AUTOSAR
4. **References**: Traceability to requirements and standards

## Best Practices

- Every port must have a corresponding interface definition
- Every runnable must be triggered by at least one event
- Exclusive areas must be documented and referenced from runnables
- Data types must span both application level and implementation details
- Version control all changes through Document Control tab
