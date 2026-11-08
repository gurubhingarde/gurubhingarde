# ODX Layer Roles and Dependencies

## Layer Interaction Model

```
┌─────────────────────────────────────────────────────────┐
│ ODX-V (Vehicle Layer)                                  │
│ • Vehicle network topology                             │
│ • ECU mapping / multiplexing strategy                  │
│ • Variant strategy (base + derived)                    │
│ └─ Depends on: ODX-D, ODX-C, ODX-FD                   │
└─────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────┐
│ ODX-D (Data Layer) + ODX-C (Communication Layer)       │
│ • Service definitions (request/response semantics)    │
│ • PDU structures and signals                           │
│ • Communication timing and protocol details           │
│ • Data object properties (units, conversions)         │
│ • DTC definitions and fault reporting                 │
│ └─ Depends on: Physical protocol spec (CAN/LIN/ETH)   │
└─────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────┐
│ ODX-FD (Flash Data Layer)                              │
│ • Memory layout and segments                           │
│ • Programming algorithm                                │
│ • Security access / unlock procedures                  │
│ • CRC algorithms                                       │
│ └─ Depends on: ECU memory map (hardware spec)         │
└─────────────────────────────────────────────────────────┘
```

## ODX-D (Data Layer) Responsibilities

The Data layer defines the **semantic content** of diagnostic communication:

### Services
- Service ID (e.g., 0x22 = ReadDataByIdentifier)
- Request message format (parameters, constraints)
- Response format (positive and negative responses)
- Supported data identifiers (DIDs)
- DTCs that can be reported

### Data Identifiers (DIDs)
- Physical meaning (e.g., "Engine Speed")
- Unit (RPM, km/h, etc.)
- Conversion formula (raw value → physical value)
- Valid range (min/max)
- Refresh rate / sampling period

### Diagnostic Trouble Codes (DTCs)
- DTC number (e.g., P0100)
- Symptom / failure description
- Severity (warning, critical, fatal)
- Functionally safe indicator (safety-relevant yes/no)
- Associated data for fault reporting (freeze frame data, extended data record)

### Parameters
- Input parameters (e.g., DID to read, write value)
- Output parameters (data, status codes)
- Security level (no auth, level 1, level 2, etc.)
- Timing constraints (response time budget)

## ODX-C (Communication Layer) Responsibilities

The Communication layer specifies **how** data is physically transmitted:

### Physical Channels
- Protocol type (CAN, CAN FD, LIN, FlexRay, Ethernet, K-Line)
- Bus speed (e.g., 500 kbps for CAN)
- Node address / ECU address on the bus
- Baud rate for serial protocols

### Timing Parameters
- Transmission timeout (P2* timeout in UDS)
- Inter-frame delay (minimum gap between requests)
- Response delay (minimum time until response appears)
- Flow control timing (CTS, WAIT frames for large transfers)

### Protocol Specifics
- CAN: Frame ID, DLC, extended/standard addressing
- LIN: Frame header, checksum algorithm, response length
- Ethernet: IP address, port, protocol (TCP/UDP/DoIP)
- K-Line: Baud rate initialization, timing for bit-bang protocol

### Flow Control
- CTS (Clear To Send) / WT (Wait) mechanisms
- Block size for multi-frame transfers
- Separation time between consecutive frames

## ODX-V (Vehicle Layer) Responsibilities

The Vehicle layer defines the **system integration** and variant strategy:

### Vehicle Structure
- Vehicle configuration (which ECUs are present)
- ECU network topology (how ECUs communicate)
- System boundaries and interfaces

### Variant Strategy
A variant is a **variant of the diagnostic description**, not a vehicle variant:

**Base Variant**: Complete, standalone diagnostic specification
- Defines all services, DTCs, data objects
- No inheritance; is a leaf or root of the tree
- Example: "Engine ECU - Base 2020"

**Derived Variant**: Specializes or extends a base variant
- Inherits most of the base variant's content
- Can override specific services (market-specific features)
- Can add new data objects (market-specific diagnostics)
- Reduces engineering effort through reuse
- Example: "Engine ECU - North America Market (inherits from Base 2020)"

### Inherit-From Relationships
```
Base-EngineECU
  │
  ├─ EU-EngineECU (inherits, disables adaptive throttle)
  │   └─ EU-Stage2 (inherits from EU-EngineECU, adds Euro 6d)
  │
  └─ NA-EngineECU (inherits, enables OBD-II expanded DTCs)
      └─ NA-2024 (inherits from NA-EngineECU, adds new SOD services)
```

Inheritance rules:
- A child variant always inherits from exactly one parent
- Properties can be overridden in the child
- Circular inheritance is forbidden
- The inheritance chain forms a forest (multiple root variants allowed)

## ODX-FD (Flash Data Layer) Responsibilities

The Flash Data layer specifies the **firmware update interface**:

### Memory Map
- Boot ROM (read-only, immutable)
- Application firmware (programmable)
- Calibration data (programmable, tuning parameters)
- NV data (non-volatile user data, persists after power loss)
- Safety-critical backup regions

### Programming Algorithm
- Erase procedure (sector erase, bulk erase)
- Write procedure (block programming, streaming write)
- Verify procedure (checksum, CRC)
- Security unlock procedure (authentication sequence)

### CRC/Checksum
- Algorithm (CRC-32, CRC-16, SHA-256)
- Polynomial and initialization
- Protected regions (boot + app + calib)
- Failure actions (reject programming, rollback)

### Security
- Authentication level (no auth, PIN, ECC certificate)
- Access timing (immediate, after delay, after power cycle)
- Brute-force protection (retry limits)
- Secure boot verification

## Layer Assembly Checklist

When building an ODX workbook:

- [ ] **ODX-D**: All services defined, all DTCs enumerated, all DIDs have units and ranges
- [ ] **ODX-C**: Bus speeds and protocols specified, timing parameters valid, flow control defined
- [ ] **ODX-V**: Vehicle topology documented, all variants listed, inheritance chains are acyclic
- [ ] **ODX-FD**: Memory segments defined, programming sequence specified, CRC algorithm chosen
- [ ] **Cross-layer**: Every service in ODX-D has a physical mapping in ODX-C
- [ ] **Cross-layer**: Every variant in ODX-V references valid services from ODX-D
- [ ] **Cross-layer**: Every variant's ECU ID is unique and non-overlapping
