# ISO 26262-6 Section 7 → Worksheet Tab Mapping

This document maps each requirement of ISO 26262-6 Section 7 (Software Architectural Design) to the worksheet tabs produced by `sw-arch-builder`.

## Clause 7.1 – General Requirements

**7.1.1** — The software architecture shall be a hierarchical decomposition of the software system into software units.

**Implemented in:**
- **Tab 03: SW Component Catalog** — lists all SWCs, their parent partitions, types, and dependencies
- **Tab 07: Inter-Component Interfaces** — documents component-to-component contracts

**7.1.2** — The software architecture shall be defined for each ASIL level allocated to the software.

**Implemented in:**
- **Tab 03: SW Component Catalog** — ASIL column per SWC
- **Tab 04: RTOS/OS Configuration** — OS ASIL
- **Tab 05: Task Scheduling Map** — ensures ASIL-consistent scheduling
- **Tab 08: Safety Mechanism Allocation** — safety mechanisms per ASIL

## Clause 7.2 – Architectural Design

**7.2.1** — The software architecture shall be defined with respect to:
- (a) the software functional and technical safety requirements
- (b) the software units
- (c) the interfaces between software units
- (d) the external interfaces

**Implemented in:**
- **Tab 02: TSC Architecture Echo** — reads system-level FSRs and SW partitions from TSC
- **Tab 03: SW Component Catalog** — maps FSRs and SW-TSRs to SWCs
- **Tab 07: Inter-Component Interfaces** — all internal and external data flow
- **Tab 05: Task Scheduling Map** — execution scheduling across OS
- **Tab 06: MPU Memory Partitioning** — isolation and external OS services

**7.2.2** — The software architecture shall reflect the software safety requirements and safety mechanisms.

**Implemented in:**
- **Tab 08: Safety Mechanism Allocation** — explicit mapping of mechanisms to SWCs
- **Tab 07: Inter-Component Interfaces** — integrity protection per interface
- **Tab 04: RTOS/OS Configuration** — OS services supporting safety (MPU, interrupts, scheduling)

**7.2.3** — The software architecture shall be understandable and well-structured.

**Implemented in:**
- All tabs use consistent naming conventions (SWC_ID, Task_ID, etc.)
- Hierarchical structure: SWCs grouped by partition
- Clear traceability back to TSC and FSRs

## Clause 7.3 – Software Partitioning

**7.3.1** — Software shall be partitioned as appropriate for the software system architecture and integrity level.

**Implemented in:**
- **Tab 02: TSC Architecture Echo** — identifies SW partitions from TSC
- **Tab 03: SW Component Catalog** — parent partition for each SWC
- **Tab 06: MPU Memory Partitioning** — memory-level isolation per partition

**7.3.2** — The software partitions shall be designed to avoid unintended interaction between partitions, particularly with respect to the use of shared resources.

**Implemented in:**
- **Tab 06: MPU Memory Partitioning** — separate regions, no shared data between ASIL boundaries
- **Tab 07: Inter-Component Interfaces** — explicit message passing (no direct memory sharing)
- **Tab 08: Safety Mechanism Allocation** — fault handlers enforce partition containment

**7.3.3** — If shared resources are used, the software partitions shall be designed to ensure that accessing the shared resource does not lead to a failure due to interference.

**Implemented in:**
- **Tab 07: Inter-Component Interfaces** — synchronization primitives (mutex, semaphore) documented
- **Tab 05: Task Scheduling Map** — priority-based locking or rate-monotonic analysis
- **Tab 06: MPU Memory Partitioning** — shared resource access rules

**7.3.4** — The software partitions shall provide the basis for the implementation of the following safety mechanisms:
- (a) isolation of faults
- (b) communication between partitions
- (c) exception handling

**Implemented in:**
- **Tab 06: MPU Memory Partitioning** — isolation, fault behavior on violation
- **Tab 07: Inter-Component Interfaces** — partition-to-partition messaging
- **Tab 08: Safety Mechanism Allocation** — exception handler allocation

## Clause 7.4 – Software Units

**7.4.1** — Software units shall be defined and their purposes shall be described.

**Implemented in:**
- **Tab 03: SW Component Catalog** — one row per SWC; name, type, purpose implicit in name and allocated FSRs

**7.4.2** — The software units shall be designed for unambiguous invocation and return.

**Implemented in:**
- **Tab 07: Inter-Component Interfaces** — clear interface types (data, event, RTE, CAN)
- **Tab 05: Task Scheduling Map** — task invocation (periodic, event-driven) and return via OS scheduler

**7.4.3** — The input and output of each software unit shall be defined.

**Implemented in:**
- **Tab 07: Inter-Component Interfaces** — all from/to SWC pairs with payload definition

**7.4.4** — The software units shall interact only by means of their defined inputs and outputs.

**Verified by:**
- Static analysis (Tab 09: MISRA Compliance Targets) — no undefined global accesses
- Integration test plan (cross-reference to FSC / TSC test lists)

## Clause 7.5 – Scheduling and Timing

**7.5.1** — The software architecture shall be designed to meet the timing requirements of the software safety requirements.

**Implemented in:**
- **Tab 05: Task Scheduling Map** — period, priority, WCET, deadline per task
- **Tab 04: RTOS/OS Configuration** — OS tick rate, interrupt latency
- **Tab 02: TSC Architecture Echo** — FTTI from FSRs (timing requirement source)

**7.5.2** — The scheduling policy and priority assignment shall be documented.

**Implemented in:**
- **Tab 04: RTOS/OS Configuration** — scheduling policy (priority preemptive, round-robin, etc.)
- **Tab 05: Task Scheduling Map** — priority column; rate monotonic feasibility check

**7.5.3** — In a preemptive scheduling environment, higher priority shall be assigned to tasks with shorter periods (rate monotonic).

**Implemented in:**
- **Tab 05: Task Scheduling Map** — "Rate Monotonic OK" column validates assignment

## Clause 7.6 – Safety Mechanisms

**7.6.1** — The software architecture shall include the safety mechanisms that are required to implement the software technical safety requirements.

**Implemented in:**
- **Tab 08: Safety Mechanism Allocation** — maps each mechanism to allocated TSR(s)

**7.6.2** — The software safety mechanisms shall be appropriate for the ASIL allocated to the software safety requirement.

**Implemented in:**
- **Tab 08: Safety Mechanism Allocation** — ASIL per mechanism
- **Tab 02: TSC Architecture Echo** — SW-TSR ASIL; cross-reference to mechanism effectiveness

**7.6.3** — The software architecture shall support the operation of the safety mechanisms.

**Implemented in:**
- **Tab 04: RTOS/OS Configuration** — OS features (watchdog, MPU, exception handling)
- **Tab 05: Task Scheduling Map** — periodic task structure for watchdog refresh
- **Tab 06: MPU Memory Partitioning** — MPU fault handler support

## Clause 7.7 – MISRA Conformance

**7.7.1** — The software shall conform to MISRA C (or equivalent).

**Implemented in:**
- **Tab 09: MISRA Compliance Targets** — per-SWC MISRA scope and tool
- **Tab 03: SW Component Catalog** — MISRA scope per SWC

**7.7.2** — Deviations from MISRA C shall be documented and justified.

**Implemented in:**
- **Tab 09: MISRA Compliance Targets** — deviation process reference; tool output links
- **Tab 03: SW Component Catalog** — MISRA scope (Required = 0 deviations, Advisory = documented)

## Clause 7.8 – External Interfaces

**7.8.1** — The software architecture shall define all interfaces to external components (hardware, communication, user input).

**Implemented in:**
- **Tab 07: Inter-Component Interfaces** — from/to columns include hardware drivers
- **Tab 03: SW Component Catalog** — Driver type SWCs

## Clause 7.9 – Verification

**7.9.1** — The software architecture shall be verified against the software requirements.

**Verification Approach:**
- Trace each SWC back to an FSR or SW-TSR (Tab 03)
- Verify each interface contract has error handling (Tab 07)
- Verify task scheduling is feasible (Tab 05)
- Verify MISRA compliance scope is appropriate (Tab 09)

**Verification Methods (per ASIL):**
- QM: Document review
- ASIL A–C: Architectural review + static analysis
- ASIL D: Review + static analysis + formal analysis (timing proof) + integration testing

## Summary Checklist

- [ ] All FSRs allocated to at least one SWC (Tab 02 → Tab 03)
- [ ] All SW-TSRs mapped to safety mechanisms (Tab 02, Tab 08)
- [ ] All SWCs allocated to at least one task (Tab 03, Tab 05)
- [ ] Task scheduling is rate-monotonic feasible (Tab 05, rate monotonic test)
- [ ] All interfaces have error handling defined (Tab 07)
- [ ] All partitions have memory regions defined (Tab 06)
- [ ] MISRA compliance scope specified per SWC (Tab 09)
- [ ] Initialization sequence covers all SWCs (Tab 10)
- [ ] References to TSC, FSC, and tool artifacts complete (Tab 11)
