---
name: autosar-swc-builder
description: Generate an audit-ready AUTOSAR Classic Platform SWC (Software Component) specification workbook per AUTOSAR R22-11 covering SWC type definition, port interfaces (sender-receiver and client-server, plus mode-switch, NV-data, parameter, and trigger), internal behavior, runnables, RTE events, exclusive areas, and data types for a single application or sensor-actuator component. This builder models Classic Platform SWCs only — for Adaptive Platform application software use autosar-adaptive-app-builder. Use this skill when the user mentions AUTOSAR SWC, software component, port interface, sender-receiver vs client-server, runnable, RTE event, ARXML SWC output, SWC specification, or asks to define an AUTOSAR component.
---

# autosar-swc-builder

Generate an audit-ready AUTOSAR Classic SWC (Software Component) specification workbook per AUTOSAR R22-11 covering SWC type definition, port interfaces, internal behavior, runnables, events, exclusive areas, data types, and implementation data types for a single application or sensor-actuator software component.

## Usage

Use this skill whenever the user mentions AUTOSAR SWC, software component, port interface (sender-receiver or client-server), runnable, RTE event, ARXML SWC output, or SWC specification, or casually asks to define an AUTOSAR component. This builder targets the Classic Platform; for Adaptive Platform application software use `autosar-adaptive-app-builder` instead.

## Inputs

Accepts a JSON input file with SWC name, category (Application, Sensor/Actuator, Service, Complex Driver), ports (sender-receiver, client-server, mode-switch, NV data, parameter, trigger), internal behavior, runnables, events, exclusive areas, and data type definitions.

## Output

Produces a 13-tab audit-ready xlsx workbook:
- Title, Document Control
- SWC Identification (Type, Category, Implementation)
- Port Inventory (Provided + Required)
- Sender-Receiver Interfaces
- Client-Server Interfaces
- Mode-Switch Interfaces
- Internal Behavior
- Runnable Catalog
- Event Catalog
- Exclusive Areas
- Data Types and Implementation Data Types
- References

---

**Commands:**
- `/autosar-swc-builder <SWC name> <category>` — generate SWC workbook
