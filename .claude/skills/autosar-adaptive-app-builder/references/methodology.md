# AUTOSAR Adaptive Platform Methodology

## Overview
AUTOSAR Adaptive Platform supports service-oriented, dynamic middleware for modern automotive ECUs. Distinct from Classic: POSIX-based, dynamic deployment, ara:: APIs, SOME/IP discovery.

## Core Concepts

### Application Manifest
- Defines application lifecycle and service dependencies
- Service required: application depends on services
- Service provided: application offers services
- Lifecycle hooks: init, run, shutdown

### Service Manifest
- Describes service interface: methods, events, fields
- ara::com service types: request-response, fire-and-forget, event, field
- Instance mappings to machine manifest
- SOME/IP configuration: service ID, instance ID

### Machine Manifest
- Host ECU configuration: processors, network interfaces
- Service instance deployment to machines
- TCP/UDP port allocation
- Routing configuration for SOME/IP

### ara::com Communication
- Request-response: synchronous, call-response pattern
- Fire-and-forget: asynchronous, one-way
- Event: publish-subscribe, event notification
- Field: getter/setter with notification option

### ara::exec Lifecycle
- States: Init, Run, Shutdown
- Deterministic state machine
- Entry/exit actions per state
- State transition triggers

## Validation Rules

1. Application manifest references only existing services
2. Machine manifest covers all deployed services
3. ara::exec states transition consistently
4. SOME/IP service IDs unique per system
5. Resource budget (CPU, memory) feasible
6. Port numbers non-overlapping
7. Network interfaces properly configured

## References
- AUTOSAR Adaptive Platform R22-11 / R23-11 specification
- ara:: API reference documentation
- SOME/IP protocol specification

