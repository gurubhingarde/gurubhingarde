# Software Architectural Design Methodology
## ISO 26262-6 Section 7 Refinement

Software architecture (ISO 26262-6 §7) refines the system-level Technical Safety Concept (TSC) into concrete SW components, task scheduling, memory partitioning, and inter-component interfaces. The SW architecture bridges system safety requirements down to design details testable in SW implementation.

## Key Responsibilities

### 1. SW Component Decomposition
Decompose each FSR (Functional Safety Requirement) and allocated SW-TSR (Technical Safety Requirement) into concrete **SW Components (SWCs)**. Each SWC:
- Maps to one or more executable tasks (or callbacks)
- Implements one or more safety mechanisms
- Allocates ASIL top-down from FSR or SW-TSR
- Resides in one SW partition (ISO 26262-6 §7.3.4 partition model)
- Implements MISRA C:2012 compliance scope (Required / Advisory / Mandatory)

Types of SWCs:
- **Application**: Implements control algorithms, signal processing
- **Service**: Provides diagnostic, monitoring, or utility functions
- **Driver**: Interfaces to hardware (DAC, CAN, sensors)
- **Diagnostic**: Implements on-board diagnostics, DTC management, fault handling

### 2. Task Scheduling
Partition SW into **real-time tasks** scheduled by the OS. Each task:
- Has a unique priority and period (rate-monotonic analysis)
- Allocates one or more SWCs
- Reports WCET (Worst-Case Execution Time) and deadline
- Operates within jitter and latency budgets from TSC

**Rate Monotonic Test**: For preemptive priority-based scheduling, shorter-period tasks must have higher priority. Check: Σ(WCET_i / Period_i) ≤ ln(2) ≈ 0.693 for utilization bound.

### 3. Memory Partitioning (MPU/MMU)
Implement **SW partitions** using Memory Protection Unit or virtual memory:
- Each partition isolates SWCs from faults (null pointer, stack overflow, unauthorized access)
- Enforce ASIL isolation: ASIL D partitions separate from ASIL B partitions (no shared data)
- Define base address, size, access rights (RW, RO, RX)
- Specify fault behavior: fault handler, reset, state machine transition

### 4. Inter-Component Interfaces
Define **message/signal contracts** between SWCs:
- Data interface: one SWC writes, others read; includes data freshness, staleness
- Event interface: async events with timeout
- RTE port: AUTOSAR Runnable-To-Environment
- CAN/network: includes E2E protection (CRC, counter, timeout)

For each interface:
- Identify payload (struct, size)
- Specify integrity mechanism (CRC, E2E, observer)
- Define synchronous (blocking call) vs. asynchronous (queue)
- Document error handling (retry, flag, fault)

### 5. Safety Mechanism Implementation
Map **safety mechanisms** from TSC into SW architecture:
- **Program Flow Monitoring (PFM)**: watchdog refresh at checkpoints
- **Range/Plausibility Check**: validate sensor inputs
- **E2E Protection**: CRC + counter + timeout on CAN messages
- **Assertion / Diagnostic Check**: abort or flag invalid states
- **Recovery Block**: dual-core or triple-modular voting
- **Partition Isolation**: MPU fault handler

Each mechanism must cite its allocated TSR and ASIL confidence level.

### 6. MISRA C:2012 Compliance
Assign a **MISRA scope** per SWC:
- **Required**: MISRA violations = 0 (no deviations)
- **Mandatory**: MISRA violations = 0 (same as Required for most)
- **Advisory**: Violations allowed with documented deviations

Allocate a static-analysis tool (e.g., Polyspace, LDRA Testbed, Coverity).
Document tool configuration, deviation process, and FMEA correlation for any violations.

### 7. Initialization Sequence
Define **boot sequence** phases:
- **Bootloader**: ROM/RAM/FLASH BIST, configuration load, clock/PLL start
- **OS Start**: Initialize RTOS, memory management, interrupt vectors
- **APP Start**: Initialize all SWCs, run functional BIST, transition to normal operation

For each phase:
- Duration budget (must complete within FTTI)
- SWCs activated
- BIST executed (startup, periodic)
- Fault behavior: proceed, retry, halt, degraded mode

## Common Pitfalls

1. **Missing task precedence / data dependency analysis**: If task A writes data and task B reads it, task B must have lower priority (or be rate-monotonic coherent) to avoid race conditions.

2. **Insufficient partition isolation**: Sharing data across ASIL boundaries without copy/isolation allows faults to propagate. Use separate memory regions and controlled APIs.

3. **Vague error handling**: "Error handler" is not a mechanism. Be explicit: "On CAN timeout, set fault flag, log DTC, command limp-home mode, notify safety monitor."

4. **Ignoring timing coupling**: Even if individually schedulable, task jitter or OS overhead may violate latency budgets. Use worst-case analysis, not average.

5. **MISRA deviations without FMEA traceability**: Every deviation (unchecked cast, inline assembly, pointer arithmetic) must be analyzed in the FMEA for failure mode consequence.

6. **No rollback plan for init failures**: If BIST fails during boot, what happens? Document the fallback mode and how the vehicle is notified (e.g., warning lamp, restricted speed).

## Verification Hooks

- **Architectural Review**: Confirm FSR→SWC mapping, task allocation, partition strategy
- **Code Review**: Check MISRA compliance, interface contracts, error handling
- **Static Analysis**: Run tool suite; classify violations, track deviations
- **Task Scheduling Analysis**: Rate monotonic test, WCET measurement, latency test
- **Integration Test**: Verify inter-component messaging, interface timing, error propagation
- **Fault Injection**: Trigger partition faults, interface timeouts, mechanism failures; verify containment

## References

- ISO 26262-6:2018 Section 7 — Software Architectural Design
- AUTOSAR Classic / Adaptive architecture and runtime specs
- MISRA C:2012 — Guidelines for the use of C in critical systems
- RMA (Rate Monotonic Analysis) — Liu & Layland, 1973
