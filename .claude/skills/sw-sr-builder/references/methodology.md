# Software Safety Requirements (SW-SRs) — Methodology and Derivation

## Overview

The Software Safety Requirements (SW-SRs) represent the middle of the ISO 26262-6 chain:

**TSC (Technical Safety Concept)**
↓
**SW-SRs (Software Safety Requirements)** ← *You are here*
↓
**Detailed Software Design** (function specifications, state machines, algorithms)

While the **Technical Safety Concept (SW-TSRs)** answers "What safety mechanisms shall be deployed?" at an architectural level (e.g., "the software shall monitor signal X with debouncing"), the **Software Safety Requirements (SW-SRs)** answer "How will the software implement those mechanisms in code?" in concrete, testable, implementation-independent terms.

---

## Key Differences: SW-TSR vs. SW-SR

### SW-TSR (from TSC)
- *Scope*: Architecture-level safety decision
- *Form*: "The system shall implement monitoring of signal X with debouncing and safe-state command"
- *Audience*: System architect, safety manager
- *Traceability*: Linked to FSRs (Functional Safety Requirements) and ASIL allocation
- *Verification*: High-level design review, architecture audit

### SW-SR (derived from SW-TSR)
- *Scope*: Implementation-level specification for software engineers
- *Form*: "The SW shall sample signal X every 10 ms; debounce with 3 consecutive reads; command safe state within 100 ms"
- *Audience*: Software architect, code reviewer, test engineer
- *Traceability*: Linked to SW-TSRs, allocated to SW components (tasks, modules, state machines)
- *Verification*: Code review, static analysis, unit test, integration test

---

## SW-SR Derivation Process

### 1. Read SW-TSR from TSC

Example SW-TSR (TSR-001-03-02):
```
Type: SW-TSR
ASIL: ASIL-C
Mechanism: Diagnostic flag sampling + debounce + safe-state transition
Text: "The software shall consume the wheel speed sensor diagnostic 
       flag, debounce transients over a 50-ms window, and command 
       motor neutral within 100 ms of fault confirmation."
```

### 2. Identify Mechanism Category and Failure Modes

Mechanism: **Diagnostic monitoring** (detect sensor fault → trigger safe state)

Failure modes the SW-SR must address:
- Deadline miss (sampling task overrun, late debounce completion)
- Illegal state (debounce counter corruption, state machine stuck)
- Lost update (race condition in flag sampling)
- ECC error (memory-protected diagnostic state)
- Deadlock (mutual exclusion hold)
- False negative (flag not recognized due to noise or corruption)
- False positive (spurious fault diagnosis due to timing anomaly)

### 3. Apply Template to Derive Sub-Requirements

For **diagnostic monitoring**, use this template:

```
SW-SR-A: Sampling
  "The SW shall read the diagnostic flag every {period_ms} ms 
   within the {task_name} task period, store in {shared_var}, 
   with parity/CRC integrity protection."

SW-SR-B: Debouncing
  "The SW shall accumulate {N_consecutive} confirmed flag-true 
   states within a {persistence_ms} ms window before declaring fault."

SW-SR-C: Safe-State Transition
  "Upon confirmed fault, the SW shall clear all control outputs 
   and command the motor to neutral state within {FRTI_ms} ms, 
   with rollback on power loss."
```

Plugging in values from the SW-TSR:
```
TSR-001-03-02-SR-01: Sampling
  "The SW shall read the WSS diagnostic flag every 10 ms 
   within the Sensor_Monitor task, with parity protection."

TSR-001-03-02-SR-02: Debouncing
  "The SW shall require 5 consecutive flag-true readings 
   (50 ms) to confirm a fault condition."

TSR-001-03-02-SR-03: Safe-State Transition
  "Upon confirmed fault, the SW shall clear PWM outputs 
   and set motor to neutral within 100 ms of fault 
   confirmation, with persistence across power cycles."
```

### 4. Allocate to Software Components

Map each SW-SR to a software module/task:

| SW-SR | Allocated Component | Responsibility |
|-------|-------------------|-----------------|
| TSR-001-03-02-SR-01 | `wss_sensor_monitor.c::SensorMonitorTask` | Sample diagnostic flag, buffer, integrity check |
| TSR-001-03-02-SR-02 | `wss_sensor_monitor.c::DebounceFilter` | Debounce counter state machine, accumulation logic |
| TSR-001-03-02-SR-03 | `motor_control.c::SafeStateHandler` | Clear outputs, command neutral, log event |

### 5. Assign Detection Times

For each SW-SR, allocate from timing budget (FTTI split into FDTI + FRTI):

| SW-SR | Target Detection Time | Justification |
|-------|----------------------|---------------|
| SR-01 | 10 ms (1 sample period) | HW provides flag; SW reads synchronously |
| SR-02 | 50 ms (5×10 ms debounce window) | Transient filtering requirement |
| SR-03 | 100 ms (FRTI budget) | Safe-state actuator response deadline |

Total FTTI = 10 + 100 = 110 ms (must fit within system FTTI for this FSR).

### 6. Define Failure Mode Coverage

Per SW-SR, specify which standard failure modes are addressed:

```
TSR-001-03-02-SR-01 addresses:
  [X] Deadline miss (task overrun)
  [X] Lost update (race condition)
  [X] Illegal state (counter corruption)
  [ ] ECC error (handled in TSR-001-03-02-SR-03)

TSR-001-03-02-SR-02 addresses:
  [X] Illegal state (debounce FSM state corruption)
  [X] False negative (debounce threshold miss)
  [X] False positive (noise-induced spurious true)

TSR-001-03-02-SR-03 addresses:
  [X] Deadline miss (safe-state command latency)
  [X] Lost update (output command race)
  [X] ECC error handling (memory protection on status)
  [X] Deadlock (mutex protection for safe-state flag)
```

### 7. Specify Verification Methods

Per allocated ASIL, recommend verification methods from ISO 26262-6 Tables 7–10:

**ASIL-C requirements:**
- Review / Walkthrough / Inspection (++)
- Static analysis (++)
- Control flow analysis (++)
- Data flow analysis (+)
- MC/DC coverage analysis (+)
- Fault injection (supplementary)

Assign to each SW-SR:

```
TSR-001-03-02-SR-01: Static analysis (buffer overflow, use-before-init),
                     Data flow (race condition on flag_buffer)
                     MC/DC (all paths through sampling logic)

TSR-001-03-02-SR-02: Control flow analysis (debounce counter paths),
                     Data flow (counter increment atomicity),
                     Fault injection (bit-flip in counter)

TSR-001-03-02-SR-03: Review + walkthrough (safe-state decision logic),
                     Static analysis (output clearing completeness),
                     Back-to-back test (reference model vs. implementation)
```

### 8. Link to MISRA C:2012 Coding Standards

For each SW-SR, cite applicable MISRA rule categories:

```
TSR-001-03-02-SR-01:
  - MISRA Rule 9.2: Pointer to array element — ensure buffer indexing is bounded
  - MISRA Rule 8.9: Scope — global flag_buffer should be file-static + protected
  - MISRA Rule 10.1: Implicit conversion — ensure flag type matches comparison

TSR-001-03-02-SR-02:
  - MISRA Rule 8.13: Use const for read-only parameters
  - MISRA Rule 12.3: No side effects in loop condition (debounce_counter)

TSR-001-03-02-SR-03:
  - MISRA Rule 16.1: Function should return void if it has no side effects
  - MISRA Rule 6.1: No unreachable code (all safe-state paths must execute)
```

### 9. Scaffold Test Strategy

For each SW-SR, identify test approach(es):

| SW-SR | Unit Test (gtest) | Integration Test (HIL/SIL) | Back-to-Back | Fault Injection | Req Coverage |
|-------|------------------|--------------------------|--------------|-----------------|--------------|
| SR-01 | Mock sensor flag, verify buffer updates | HIL: read real HW flag | N/A | Bit-flip in buffer | ✓ Traceability |
| SR-02 | Mock flag sequence, verify debounce counter | SIL: inject flag patterns | Compare C vs. Python model | Bit-flip counter | ✓ Traceability |
| SR-03 | Mock motor control output, verify command | HIL: verify actual motor neutral | C impl vs. baseline reference | Inject ECC error on status | ✓ Traceability |

---

## Example: SW-SR for Watchdog Mechanism

### SW-TSR from TSC
```
TSR-002-01-03: The software shall service the independent watchdog 
               timer within every 50-ms window to prevent reset.
ASIL: ASIL-B
```

### Derived SW-SRs

**TSR-002-01-03-SR-01: Watchdog Service Insertion**
```
Text: "The Watchdog_Kicker_Task shall service the watchdog register 
       every 25 ms (mid-window of 50 ms budget) by writing the 
       magic sequence 0xABCD to WDOG_KICK register."

Allocated to: `watchdog.c::WatchdogKickerTask`
ASIL: ASIL-B
Failure modes: Deadline miss (task overrun), Lost update (register write loss), 
              Illegal opcode (memory corruption of task code)
Detection time: 25 ms (task period)
Verification: Code review (register write correctness), static analysis 
              (task schedulability), MC/DC (kicker logic)
MISRA: Rule 8.13 (const register pointer), Rule 10.4 (implicit conversion 
       on magic value)
```

**TSR-002-01-03-SR-02: Watchdog Timeout Handler**
```
Text: "Upon watchdog timeout expiration, the hardware generates an 
       interrupt. The Watchdog_ISR shall save diagnostic state to 
       persistent memory (Flash) and transition to safe state within 
       1 ms of interrupt entry."

Allocated to: `watchdog.c::WatchdogISR()`
ASIL: ASIL-B
Failure modes: ECC error (Flash write corruption), Deadlock (ISR preemption), 
              Memory corruption (stack smash)
Detection time: <1 ms (ISR latency)
Verification: Code review (ISR stack depth), static analysis (Flash write atomicity),
              Fault injection (bit-flip in diag state during write)
MISRA: Rule 8.5 (static declaration for ISR context), Rule 17.7 
       (no unprotected ISR state access)
```

---

## Mapping SW-SR to Detailed Software Design

Once SW-SRs are approved and baselined, they become input to **detailed software design**:

1. **Software Architecture** — define task interactions, message flows, state machines
2. **Data Dictionary** — specify all variables backing SW-SRs (types, ranges, update rates)
3. **Function Specifications** — break down each SW-SR into concrete functions and algorithms
4. **Interface Specifications** — HSI signals, inter-module APIs, interrupt handlers
5. **Code Review Checklist** — use SW-SRs as pass/fail criteria during code review

Example: Function spec derived from TSR-001-03-02-SR-01:

```c
/**
 * @brief Read the WSS diagnostic flag with integrity protection.
 * @param out_flag Pointer to output flag buffer (parity-protected).
 * @return true if read succeeded, false if parity error detected.
 * 
 * Implements: TSR-001-03-02-SR-01
 * MISRA: Rule 9.2, Rule 17.7, Rule 10.1
 * Verification: Static analysis, MC/DC test, unit test (test_wss_flag_read_*).
 */
bool WSS_ReadDiagnosticFlag(uint8_t * out_flag) { ... }
```

---

## Independence and Decomposition

When ASIL decomposition cascades from **TSC → SW**, document independence requirements:

**Example:** TSR-001-03-02 allocated ASIL-C via decomposition of ASIL-D FSR into two ASIL-B channels (A and B).

For **Channel A** (debounce logic in task A) and **Channel B** (debounce logic in task B) to be independent, SW-SRs must specify:

- **Separate compilation units**: Task A code in `channel_a.c`, Task B in `channel_b.c` (no shared .o file)
- **Separate memory regions**: Channel A uses RAM block 0, Channel B uses RAM block 1 (ECC blocks separate)
- **Separate interrupt priority**: Channel A at high priority, Channel B at lower priority (preemption isolation)
- **Separate scheduling**: Channel A scheduled by timer 0, Channel B by timer 1 (no shared scheduler state)
- **Separate code review**: Different reviewer for each channel (independent verification)

SW-SR text for independence:
```
TSR-001-03-02-SR-02-Decomp: "The debounce logic for Channel A shall reside 
                             in a separate compilation unit (channel_a.c) 
                             with independent task scheduling (Timer0 interrupt), 
                             separate memory allocation (RAM block 0), and 
                             separate code review, to satisfy ASIL decomposition 
                             independence per ISO 26262-9 Clause 7."
```

---

## Quality Checks for SW-SRs

Before handoff to detailed design:

- [ ] Each SW-SR is traceable to exactly one SW-TSR
- [ ] Each SW-SR names a specific software component (task, module, function, state machine)
- [ ] Each SW-SR specifies detection time (tied to FDTI / FRTI budget)
- [ ] Failure modes are identified (deadline, illegal state, race, ECC, deadlock, false +/-)
- [ ] Verification methods match ASIL (Table 7–10 from ISO 26262-6)
- [ ] MISRA rule categories are cited and implementable
- [ ] Test strategy covers unit, integration, back-to-back, fault injection, and traceability
- [ ] Independence requirements documented if ASIL decomposition applies
- [ ] All "<TBD>" fields resolved in review
- [ ] No dangling requirements (each SW-SR maps to at least one test case)

---

## References

- **ISO 26262-6:2018** — Product development at the software level, Clause 6 (Specification of software safety requirements)
- **ISO 26262-9:2018** — Functional Safety Management, Clause 7 (Dependent failure analysis)
- **MISRA C:2012** — Guidelines for the use of the C language in critical systems (via AUTOSAR, embedded systems)
- **IEC 61508-3** — Functional safety of electrical/electronic/programmable electronic safety-related systems, Part 3 (Software requirements and techniques)
