# Item Definition Methodology

An Item Definition is a structured artifact that establishes the scope, boundary, and requirements of a safety-critical vehicle system or subsystem. It is the **input to the HARA** (Hazard Analysis and Risk Assessment) and the **source of truth** for what the item is supposed to do, what is outside its scope, and what assumptions enable safe operation.

## Why Item Definitions Matter

ISO 26262 Concept Phase begins with a clear, unambiguous definition of the item being analyzed. Without an Item Definition:

- The HARA cannot distinguish between **safety-critical functions** (those owned by the item) and **external dependencies** (sensors, actuators, other ECUs).
- Analysts disagree on **item boundaries**, leading to incomplete hazard analysis (missing failure modes because they're "someone else's problem") or over-scoped analysis (redundant work on non-item concerns).
- **Assumptions** remain implicit and undocumented, causing design conflicts downstream.
- **Allocation decisions** (HW vs. SW vs. mechanical) are deferred, delaying architecture and enabling rework.

## Structure of an Item Definition

The Item Definition workbook contains 11 tabs, each addressing a specific aspect of item scope:

### 00 Title Page
- Item identity: name, abbreviation, project context
- Document metadata: ID, revision, date, author, approver, company
- Reference to ISO 26262-3 Clause 5

### 01 Document Control
- Revision history: capture iterations as the item scope is refined
- Distribution list: who owns the definition, who approves it

### 02 Item Description
- **Item name and abbreviation** — the canonical identifier used throughout the HARA and FSC
- **Item classification** — vehicle system (e.g., "Powertrain"), subsystem (e.g., "Engine Control"), or component (e.g., "ECU")
- **Scope description** — plain-language statement of what the item does and explicitly does NOT do
  - Example: "ESC maintains lateral stability by selectively applying brake pressure and modulating engine torque. Item does NOT include brake pedal, master cylinder, or driver-assistance ECUs."
- **Distinguishing notes** — how this item differs from neighboring systems (e.g., ESC vs. ABS, Transmission ECU vs. Engine ECU)

### 03 Functions
- **Function list** with ID (F01, F02, ...), name, description, criticality hint
- Criticality hints guide the HARA's kinetic-authority classification (high/medium/low/none)
- Example functions for ESC: Yaw stability control, Engine torque modulation, Driver warning lamp control, Self-diagnostic monitoring

### 04 Non-Functional Requirements
- **Performance constraints**: response time, computational throughput, signal accuracy
- **Environmental constraints**: temperature, humidity, vibration, EMI/RFI bands
- **Regulatory constraints**: emissions, safety standards, market-specific regulations
- **Market constraints**: cost targets, OEM platform compatibility, legacy system integration
- Each NFR should map to the item's technical specification

### 05 Boundary Diagram
- **Boundary notes** — textual description of the item's scope in the vehicle architecture (e.g., "ESC ECU + HSM + hydraulic modulator, excluding brake pedal and master cylinder")
- **IN the item** — components, subsystems, software modules that the item owns
- **OUT of item** — components, subsystems, or software that are external dependencies (sensors, downstream actuators, other ECUs)
- **Adjacent systems** — neighboring items that interact with this item (e.g., powertrain ECU, brake ECU, steering ECU)

### 06 External Interfaces
- **Interface catalog** with ID, interface name, counterpart system, direction (In/Out), data type, and integrity protection
- Defines the **contract** between the item and external dependencies
- Example: "Wheel speed sensors" (in), "Hydraulic modulator" (out), "Engine torque request" (out), "Driver display lamp" (out)
- Integrity protection (e.g., CRC, checksum, redundancy) is noted here and flows into the HARA for controllability assessment

### 07 Operating Modes
- **Mode enumeration**: Off, Initialization, Standby, Active, Degraded, Fault
- For each mode: entry conditions, exit conditions, safety relevance
- Example: "Active mode" entered when vehicle speed > 5 km/h and driver intent detected; exited when stability regained or fault detected; **safety relevant**
- Operating modes govern the HARA's exposure assessment (e.g., some functions are only safety-critical in Active mode)

### 08 Allocation HW/SW/Mech
- **Function × allocation** table: for each function, which implementation type (Hardware, Software, Mechanical, or Mix) is responsible
- Rationale for each allocation (e.g., "Yaw rate sensing via IMU (hardware), yaw control law via ECU firmware (software), brake modulation via hydraulic valve (mechanical)")
- This allocation informs the HARA's architecture discussion and feeds into the FSC decomposition

### 09 Initial Assumptions
- **Vehicle assumptions**: class (sedan, SUV, truck), GVW, drivetrain (FWD, RWD, AWD), market region (US, EU, CN)
- **Driver assumptions**: non-expert, valid license, not impaired, average reaction time
- **Market assumptions**: production lifetime, field update capability, spare parts availability
- **Lifecycle assumptions**: which phases of the vehicle lifecycle are in scope (normal operation, service, off-road use)
- **Other-item assumptions**: what services or sensor inputs the item can rely on from neighboring systems (e.g., "engine ECU will accept torque requests within 50 ms")
- **Cybersecurity scope**: whether cyber threats are handled in this HARA or partitioned to ISO/SAE 21434 analysis

### 10 References
- **Standards**: ISO 26262 (all parts), ISO 13121 (glossary), ISO 11152 (safety of hazards)
- **Related documents**: HARA (when completed), Functional Safety Concept (FSC), Technical Safety Concept (TSC), System FMEA
- **Regulations**: EPA, NHTSA, EU Type Approval, market-specific requirements

## How Item Definitions Feed the HARA

Once the Item Definition is approved, it becomes the **input to HARA**:

1. **Function list** (Tab 03) — becomes the HARA's function enumeration
2. **Criticality hints** — guide the HARA's kinetic-authority classification (high/medium/low/none)
3. **Operating modes** (Tab 07) — define the HARA's exposure assessment (which functions are active in which environments)
4. **Boundary and interfaces** (Tabs 05–06) — clarify which failure modes are the item's responsibility vs. external dependencies
5. **Assumptions** (Tab 09) — constrain the HARA's scope and shape the controllability assessment

## Common Pitfalls

1. **Vague scope statements.** "ESC controls stability" is too broad. Better: "ESC maintains lateral stability by applying selective brake pressure when yaw rate deviates from reference; does NOT include primary brake control, steering motor, or engine idle control."

2. **Forgetting to list what is OUT.** The "out of item" section is as important as "in the item." Explicitly state what your item does NOT own (e.g., "ESC does not own the hydraulic pump; relies on brake system to provide modulation capability").

3. **Under-documenting assumptions.** Implicit assumptions cause surprises in the HARA (e.g., "I assumed the powertrain ECU would always accept torque requests" vs. recording that assumption explicitly in Tab 09).

4. **Allocations without rationale.** "Why is yaw control software?" Answer: "Kalman-filter-based yaw rate estimation requires iterative computation; firmware-based implementation chosen to enable over-the-air updates and to leverage existing ECU HW platform."

5. **Mixing item scope with feature descriptions.** An Item Definition documents what the item is; a Requirements Specification documents how it is built. Keep the Item Definition focused on boundary and scope.

## Integration with the 26262 Framework

The Item Definition aligns with ISO 26262-3 Clause 5 (Item Definition) and flows into:

- **Clause 6 (Hazard Analysis and Risk Assessment)** — the HARA reads the item scope, functions, and assumptions
- **Clause 7 (Functional Safety Concept)** — the FSC decomposition and allocation are justified by the item's architectural boundary
- **Clause 8 (Technical Safety Concept)** — hardware/software/mechanical allocation informs the TSC's architecture
- **Clause 9 (Architecture Design)** — the detailed design realizes the allocations and assumptions documented here

A well-written Item Definition is an anchor point that prevents scope creep and rework throughout the concept phase and beyond.
