# ARCADIA Layer Definitions

## Operational Analysis Layer

Purpose: Define operational needs and capabilities without prescribing implementation

Elements:
- Missions: Top-level goals (e.g., "Deliver cargo")
- Capabilities: Ability to achieve a mission (e.g., "Path Planning")
- Actors: External entities (human, system, environment)
- Operational Scenarios: Sequences of interactions among actors

## System Analysis Layer

Purpose: Define system-level functional and interface requirements

Elements:
- System Functions: What the system must do (e.g., "Plan Route")
- Functional Exchanges: Data and control flows between functions
- System Interfaces: Points of interaction with external actors
- Functional Chains: Critical sequences of functions

## Logical Analysis Layer

Purpose: Design system in implementation-independent terms

Elements:
- Logical Components: Self-contained functional units
- Logical Ports: Component connection points
- Logical Data Flows: Exchange of information
- Behavioral Allocations: Which functions each component performs

## Physical Analysis Layer

Purpose: Map logical design to real implementation

Elements:
- Physical Components: Actual hardware or software units
- Deployment Diagram: Physical node topology
- Hardware/Software Split: Technology choices
- Physical Interfaces: Concrete protocols and physical connections
