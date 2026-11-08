# ISO 26262-3 Clause 5 Mapping

This document maps each tab in the Item Definition workbook to the corresponding requirement in **ISO 26262-3:2018, Clause 5 (Item Definition)**.

## ISO 26262-3 Clause 5 Overview

Clause 5 specifies the requirements for an Item Definition during the concept phase. The Item Definition establishes:

- The **scope and boundaries** of the safety-critical item
- The **functions** the item performs
- The **assumptions** that enable safe operation
- The **architectural allocation** (HW/SW/Mechanical)
- The **external interfaces** and dependencies

The item definition is the **primary input to the HARA** (Clause 6) and shapes all downstream analysis and design.

## Tab-to-Clause Mapping

### Tab 00: Title Page
**ISO 26262-3:2018, Clause 5.2 (General)**

Provides document metadata and context:
- Item identification (name, abbreviation)
- Project scope (project ID, revision, date)
- Stakeholders (author, approver, company)
- Reference to the standard and item definition phase

**Requirement met:** 5.2.1 — "The item definition shall be documented."

---

### Tab 01: Document Control
**ISO 26262-3:2018, Clause 5.2.1**

Establishes configuration management and traceability:
- Revision history tracking changes to the item definition
- Distribution list (change log recipients)
- Approval sign-off

**Requirement met:** 5.2.1 — Documentation shall be versioned and controlled.

---

### Tab 02: Item Description
**ISO 26262-3:2018, Clause 5.3 (Item Definition — Scope and Boundaries)**

Defines the item in terms of:
- **Item classification** — vehicle system, subsystem, or component
- **Scope description** — clear statement of what the item does and does NOT do
- **Distinguishing notes** — how this item differs from neighboring items

**Requirement met:** 5.3.1 — "The item shall be described and its interfaces shall be defined."

5.3.2 — "The item boundary definition shall clearly distinguish the item from other items and the environment."

**Example:**
- **Item:** Electronic Stability Control (ESC)
- **Does:** Maintains lateral stability by applying selective brake pressure and modulating engine torque
- **Does NOT:** Provide primary braking, steering motor control, or engine idle control
- **Classification:** Vehicle subsystem (part of chassis control)
- **Distinguishing:** ESC differs from ABS (which only provides emergency braking) by including yaw moment correcting via selective braking and torque modulation

---

### Tab 03: Functions
**ISO 26262-3:2018, Clause 5.4 (Functions)**

Enumerates the item's functions with:
- **Function ID** (F01, F02, ...) — traceable identifier used in HARA and FSC
- **Function name** — canonical name
- **Function description** — what the function does (not how)
- **Criticality hint** — guidance for HARA kinetic-authority classification (high/medium/low/none)

**Requirement met:** 5.4.1 — "The item shall be described by its functions."

5.4.2 — "Each function shall be described in sufficient detail for use in hazard analysis."

**Example for ESC:**
- F01: Yaw stability control — Compares measured yaw rate with reference; applies selective braking to correct deviations. (Criticality: high)
- F02: Engine torque modulation — Requests engine torque reduction via CAN to assist yaw correction. (Criticality: high)
- F03: Driver warning lamp — Illuminates ESC lamp during intervention or fault. (Criticality: low)
- F04: Self-diagnostic monitoring — Monitors sensor plausibility and actuator response; reports DTCs. (Criticality: none)

These functions directly feed the HARA's malfunction enumeration (Clause 6).

---

### Tab 04: Non-Functional Requirements
**ISO 26262-3:2018, Clause 5.5 (Non-Functional Properties and Environmental Conditions)**

Documents constraints that shape the item's design and HARA:
- **Performance requirements** — response time, bandwidth, throughput, accuracy
- **Environmental requirements** — temperature, humidity, vibration, EMI/RFI
- **Regulatory requirements** — emissions, crash safety, accessibility
- **Market requirements** — cost, power budget, legacy compatibility

**Requirement met:** 5.5.1 — "Non-functional properties of the item shall be defined."

5.5.2 — "Environmental conditions under which the item operates shall be defined."

**Example for ESC:**
- Performance: Yaw rate control response time < 100 ms; control accuracy within 5 deg/s
- Environmental: Operating temperature -40 to +85 deg C; vibration per ISO 16750-3; EMC per ISO 7637
- Regulatory: NHTSA FMVSS 126 (electronic stability control); EU Regulation 661/2009
- Market: Cost < 150 EUR per unit; compatible with 12V and 24V electrical systems

---

### Tab 05: Boundary Diagram
**ISO 26262-3:2018, Clause 5.3 (Item Boundaries)**

Provides the **architectural boundary** defining what is inside vs. outside the item:
- **Boundary notes** — textual description of scope in the vehicle system
- **IN the item** — components and subsystems the item owns (e.g., ESC ECU, HSM, hydraulic modulator)
- **OUT of item** — external dependencies (e.g., brake pedal, master cylinder, engine ECU)
- **Adjacent systems** — neighboring items that interface with this item

**Requirement met:** 5.3.1 — "Item boundaries shall be clearly defined."

5.3.2 — "Interfaces between the item and the environment shall be defined."

**Example for ESC:**
- **Boundary notes:** "ESC ECU + HSM hydraulic control module. Excludes brake pedal, master cylinder, instrument cluster, powertrain ECU."
- **IN:** ESC ECU, HSM, wheel speed sensors (4x), IMU, steering angle sensor, hydraulic modulator
- **OUT:** Brake pedal, master cylinder, ABS pump, engine control, instrument panel
- **Adjacent:** Powertrain ECU (receives torque requests), brake ECU (supervises modulator), steering ECU (receives steering angle)

---

### Tab 06: External Interfaces
**ISO 26262-3:2018, Clause 5.3.3 (Interfaces)**

Documents the **contract** between the item and external dependencies:
- **Interface ID** — traceable identifier
- **Interface name** — e.g., "Wheel Speed Sensors", "Hydraulic Modulator", "CAN Bus"
- **Counterpart system** — which external system provides/receives the interface
- **Direction** — In (sensor/input), Out (actuator/output), or Bidirectional
- **Data type** — signal format, units, range, update rate
- **Integrity protection** — CRC, checksum, redundancy, or none
- **Notes** — any special conditions or dependencies

**Requirement met:** 5.3.3 — "All interfaces between the item and the environment shall be defined."

5.3.4 — "Interface definitions shall include sufficient detail for hazard analysis."

**Example for ESC:**
| ID | Interface | Counterpart | Direction | Data | Integrity | Notes |
|----|-----------|-------------|-----------|------|-----------|-------|
| I01 | Wheel speed sensors x4 | Wheel hubs | In | 0–20 kHz pulse train | None (analog) | Per ABS standard |
| I02 | IMU (yaw + lat accel) | IMU module | In | ±200°/s, ±2g @ 100 Hz | CRC-16 | Via CAN bus |
| I03 | Steering angle sensor | Steering column | In | ±540° @ 1 kHz | CRC-16 | Via CAN |
| I04 | Hydraulic modulator | HSM | Out | Solenoid valve commands (12V PWM) | None | Direct wire |
| I05 | Engine torque request | Powertrain ECU | Out | CAN message, 0–100% torque, 10 ms cycle | CRC-16 + seq | Via CAN |
| I06 | Driver warning lamp | Instrument cluster | Out | CAN message, on/off | CRC-16 | Via CAN |

These interfaces directly inform the HARA's architecture discussion and the FSC's function allocation (Clauses 6–7).

---

### Tab 07: Operating Modes
**ISO 26262-3:2018, Clause 5.6 (Operating Modes)**

Defines the **state machine** of the item:
- **Mode ID** — Off, Initialization, Standby, Active, Degraded, Fault
- **Mode name** — canonical identifier
- **Entry conditions** — what triggers transition into this mode
- **Exit conditions** — what triggers transition out of this mode
- **Safety relevant** — whether failures in this mode can cause hazards

**Requirement met:** 5.6.1 — "All relevant operating modes of the item shall be defined."

5.6.2 — "For each mode, the transitions, entry/exit conditions, and safety relevance shall be documented."

**Example for ESC:**
| ID | Mode | Entry Conditions | Exit Conditions | Safety Relevant |
|----|------|------------------|-----------------|-----------------|
| M01 | Off | Power-down; ignition off | Ignition on; self-test passed | No |
| M02 | Initialization | Ignition on; power-up | Self-test complete (< 5 s) | No |
| M03 | Standby | Self-test passed; vehicle speed < 5 km/h | Vehicle speed > 5 km/h AND driver input detected | Yes (latent faults masked) |
| M04 | Active | Vehicle speed > 5 km/h AND driver input detected | Stability regained > 10 s OR fault detected OR vehicle speed < 5 km/h | Yes |
| M05 | Degraded | Single sensor fault detected (e.g., one wheel speed sensor) | Fault cleared AND self-test passed | Yes |
| M06 | Fault | Multiple faults OR critical component failure | Manual reset required; off/on cycle | Yes |

Operating modes inform the HARA's **exposure assessment** (which functions are active in which conditions) and the FSC's safe-state definition.

---

### Tab 08: Allocation (HW / SW / Mech)
**ISO 26262-3:2018, Clause 5.7 (Allocation of Functions)**

Documents the **architectural decomposition** of functions:
- **Function ID** — reference to Tab 03
- **Allocation type** — Hardware, Software, Mechanical, or Mix
- **Rationale** — why this allocation was chosen

**Requirement met:** 5.7.1 — "Functions shall be allocated to items and sub-items."

5.7.2 — "The allocation shall be documented and justified."

**Example for ESC:**
| Function | Type | Rationale |
|----------|------|-----------|
| F01: Yaw stability control | Mix (SW + Mech) | Yaw rate estimation (Kalman filter, firmware) + selective brake application (hydraulic modulator hardware) |
| F02: Engine torque modulation | SW | Torque request calculation via firmware; transmitted via CAN to powertrain ECU |
| F03: Driver warning lamp | SW | Lamp activation logic in firmware; CAN transmission to instrument cluster |
| F04: Self-diagnostic monitoring | SW | Sensor plausibility checks, DTC reporting via firmware |

This allocation directly feeds the FSC's function decomposition and the TSC's architecture design.

---

### Tab 09: Initial Assumptions
**ISO 26262-3:2018, Clause 5.8 (Assumptions)**

Documents the **constraints and dependencies** that enable safe operation:
- **Vehicle assumptions** — class, weight, drivetrain, market region
- **Driver assumptions** — skill level, reaction time, sobriety
- **Market assumptions** — production volume, update capability, spare parts
- **Lifecycle assumptions** — normal operation, service, off-road use, crash scenarios
- **Other-item assumptions** — what services/inputs the item can rely on from neighboring systems
- **Cybersecurity scope** — threat partitioning to ISO/SAE 21434

**Requirement met:** 5.8.1 — "All assumptions relevant to the item definition shall be documented."

5.8.2 — "Assumptions shall be justified and shall be consistent with the overall system safety concept."

**Example for ESC:**
- A01 (Vehicle): Passenger SUV, GVW 1800–2400 kg, AWD. [Scope: MY2027 compact SUV project]
- A02 (Driver): Average non-expert driver, valid license, alert; reaction time 1.5 s. [Per ISO 26262 controllability definition]
- A03 (Market): North America and Europe, LHD and RHD. [Project scope]
- A04 (Lifecycle): HARA covers normal operation; service and repair states excluded. [Per ISO 26262 scope]
- A05 (Cybersecurity): Cyber threats handled separately under ISO/SAE 21434. [Scope partition]
- A06 (Other-item): Powertrain ECU will accept torque requests within 50 ms. [Powertrain ECU SIL constraint]

These assumptions constrain the HARA's scope and shape the controllability assessment.

---

### Tab 10: References
**ISO 26262-3:2018, Clause 5.9 (References and Related Documents)**

Documents the **supporting standards and related artifacts:**
- **Standards** — ISO 26262 (all parts), domain-specific standards (e.g., ISO 11152 for sensor safety)
- **Related documents** — HARA (when completed), FSC, TSC, system FMEA, requirements specification
- **Regulations** — EPA, NHTSA, EU Type Approval, market-specific rules

**Requirement met:** 5.9.1 — "All applicable standards and normative references shall be cited."

5.9.2 — "Related documents shall be identified and their relationships documented."

**Example for ESC:**
| ID | Title | Version |
|----|-------|---------|
| REF01 | ISO 26262-1:2018 | Functional safety — General concepts and principles |
| REF02 | ISO 26262-3:2018 | Functional safety — Concept phase |
| REF03 | ISO 11152:2020 | Safety of machinery — Human body measurements |
| REF04 | NHTSA FMVSS 126 | Electronic stability control for light vehicles |
| REF05 | ESC System Requirements Spec | v2.1 (internal doc) |
| REF06 | ESC HARA | (to be completed) |

---

## Audit Checklist

When reviewing an Item Definition workbook for completeness against ISO 26262-3 Clause 5:

- [ ] Tab 00 — Title page present with item ID, project, metadata
- [ ] Tab 01 — Document control with revision history
- [ ] Tab 02 — Item name, abbreviation, classification, scope, distinguishing notes
- [ ] Tab 03 — Function enumeration with ID, name, description, criticality hints
- [ ] Tab 04 — Non-functional properties and environmental conditions documented
- [ ] Tab 05 — Boundary diagram with IN/OUT/Adjacent systems
- [ ] Tab 06 — External interfaces with direction, data type, integrity protection
- [ ] Tab 07 — Operating modes with entry/exit conditions and safety relevance
- [ ] Tab 08 — HW/SW/Mech allocation with rationale for each function
- [ ] Tab 09 — Vehicle, driver, market, lifecycle, other-item, and cybersecurity assumptions
- [ ] Tab 10 — References to standards and related documents

A complete Item Definition is ready for handoff to the HARA phase.
