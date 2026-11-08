# AUTOSAR Classic BSW Configuration Methodology

## Overview
Basic Software (BSW) configuration defines the middleware stack for an AUTOSAR Classic ECU, spanning MCAL, ECU Abstraction, Service Layer, and Complex Drivers.

## Stack Layers

### 1. MCAL (Microcontroller Abstraction Layer)
- Port, GPIO, UART, SPI, CAN, LIN, Ethernet
- Memory interfaces: EEPROM, Flash
- Timing services: STM, GPT
- Configured per target microcontroller

### 2. ECU Abstraction Layer
- EcuM (ECU Manager): startup, shutdown, state machine
- FeeM (Flash EEPROM Emulation Manager)
- Common drivers for hardware abstraction

### 3. Service Layer
- Com (Communication): PDU/signal handling
- PduR (PDU Router): signal-to-PDU mapping
- CanIf, CanTp (CAN Interface/Transport)
- NvM (NVRAM Manager): non-volatile storage
- Det (Diagnostics): error tracking
- Os (Operating System): task scheduling, resources

### 4. Complex Drivers
- Modules with special timing or interaction patterns
- Bus drivers (CAN, LIN controllers)
- Memory controllers with custom logic

## Configuration Approach

1. **ECU Target Definition**: microcontroller, memory, interfaces
2. **Module Inventory**: identify required BSW modules per stack layer
3. **Container Configuration**: define containers (e.g., Com PDUs, Os tasks)
4. **Parameter Assignment**: set module-specific configuration
5. **Post-Build Variants**: define selectable configurations per ECU
6. **Memory Allocation**: assign RAM/ROM per module
7. **Schedule Tables**: define Os task periods, priorities
8. **Validation**: check inter-module dependencies, no conflicts

## Key Considerations

- Target microcontroller constraints (memory, interfaces)
- Bus topology and communication requirements
- Safety integrity level (ASIL) if applicable
- Timing requirements (task periods, latencies)
- NvM block alignment with module data
- No parameter naming conflicts
- Consistent memory regions (no overlaps)

## References
- AUTOSAR R22-11 Classic Platform specification
- Target microcontroller datasheet
- System integration requirements
