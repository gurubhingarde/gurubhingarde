# SW HSI Specification Confirmation Measures Methodology

## Overview

This skill audits Software-side HSI (Hardware-Software Interface) Specifications against ISO 26262:2018 Part 6 (Software Development, Section 7: Software Unit Design and Implementation) and Part 4 (Concepts, Section 6.4.6: HSI Specification Requirements).

A SW HSI Specification documents:
- How HSI signals (inputs from hardware) are received and handled by software
- Which Software Components (SWCs) own which handlers
- What RTOS tasks execute each handler and how often
- How debouncing is applied to noisy or slow signals
- How signal faults propagate to vehicle-level reactions
- Test cases covering nominal, fault injection, boundary, and timing scenarios

## Checklist Structure

### Confirmation Review (CR) — 14 checks

Generic document-quality checks applicable to any formal specification:
1. **Structured** — tabs, sections, logical organization
2. **Template** — latest version used
3. **Searchable** — TOC, Index, References
4a. **Title & Scope** — clear document purpose
4b. **Authorship** — author and approver assigned
4c. **Revision** — unique ID per version
4d. **Change History** — revision log populated
4e. **Status** — Draft / In Review / Released
5. **Revision Identifiability** — current version clear
6. **Configuration Management** — under CM control
7. **Headers/Footers** — updated with doc ID, revision
8. **Table of Contents** — present and accurate
9. **References** — all source documents listed
10. **Completeness** — all major sections populated

### SW HSI Assessment (SWHSIA) — 12 checks

Substantive checks specific to software HSI:
1. **HSI Signal Catalog Echo** — signals echoed from source HSI (count > 0)
2. **Handler Function Names** — each signal has SW handler function name
3. **SWC Allocation** — each handler allocated to Software Component
4. **Calling RTOS Task** — each handler's RTOS task identified
5. **Max Execution Time** — handler execution budget specified
6. **Debounce Specified** — safety-relevant signals have debounce strategy
7. **Debounce Parameters Reasonable** — N-of-M (N>=2), time threshold sensible
8. **Fault Propagation Trace** — signal failures map to vehicle reactions
9. **RTOS Integration** — task names, priorities, periods, signals documented
10. **Latency within FRTI** — signal-to-handler latency meets Functional Requirements for Timing Interval
11. **Init Sequence Coordinated** — SW startup aligned with HW BIST
12. **Test Cases Comprehensive** — nominal, fault, boundary, timing cases defined

### Verification Assessment (VA) — 5 checks

Verification items requiring external evidence (TSC, RTOS scheduling, FMEA):
1. **Signal Integrity Protection** — safety signals use Parity/CRC/SECDED/Dual-channel
2. **Handler Coverage** — all HSI signals handled (90%+ coverage)
3. **Debounce Effectiveness** — N-of-M and time thresholds match signal rise/fall times
4. **Call Frequency Consistency** — handler call frequency aligns with signal sample rate
5. **End-to-End Latency** — signal arrival to vehicle reaction meets FRTI

## Key Concepts

### SW Handler
A function that processes an HSI signal when it arrives. Properties:
- Signal name (which HSI signal it reads)
- Function name (C/C++ identifier)
- Allocated SWC (which software component owns it)
- Calling task (which RTOS task runs it)
- Call frequency (how often, e.g., every 10ms)
- Max execution time (WCET budget, e.g., 2ms)

### Debounce Strategy
Filters noisy or slow signals before handler execution. Per ISO 26262-6 §7.4.11:
- **N-of-M filter**: signal must be stable for N consecutive samples out of M to be accepted
- **Time threshold**: signal must remain constant for X milliseconds
- Safety-relevant signals must have documented debounce

### Fault Propagation Map
Traces signal faults (stuck-at-0, stuck-at-1, missing, incorrect encoding) through software logic to vehicle-level consequences:
- Signal name + failure mode
- Detection mechanism (explicit check, timeout, integrity protection)
- Vehicle reaction (error report, limp home, full safe state)

### RTOS Integration
Documents which RTOS tasks process which signals:
- Task name, priority, period (e.g., "Sensor_Task", Priority=10, Period=10ms)
- Signals processed by the task
- Timeout / watchdog if task becomes unresponsive

## Scoring Rationale

| Rating | Rationale |
|--------|-----------|
| FC | Direct evidence in xlsx (e.g., all handlers have SWC, all safety signals have debounce). |
| LC | Mostly present, minor gaps (e.g., 95% handlers have SWC, 1-2 missing). |
| PC | Significant gaps (e.g., 70% handlers have SWC, major test cases missing). |
| NO | Requirement clearly not met (e.g., no handlers, no RTOS integration tab). |
| NA | Check not applicable (e.g., no safety-relevant signals; debounce check skipped). |
| — | Requires external evidence or subjective judgment (debounce effectiveness, FRTI adequacy). |

## ISO 26262 Mapping

| Check | ISO 26262 Citation | Rationale |
|-------|------------------|-----------|
| SWHSIA 1-5 | Part 6, §7.4 — Software Unit Design | Handler definition, SWC allocation, RTOS assignment are unit design artifacts. |
| SWHSIA 6-7 | Part 6, §7.4.11 — Debouncing | ISO requires documented debounce for safety-relevant input signals. |
| SWHSIA 8 | Part 4, §6.4.6 — HSI Specification | Fault propagation required in TSC (Technical Safety Concept), derived from HSI. |
| SWHSIA 9 | Part 6, §7.3 — RTOS Configuration | RTOS task scheduling and timing constraints documented. |
| SWHSIA 10 | Part 6, §7.4.9 — Timing Analysis | Latency from sensor input to actuator output must be within FRTI. |
| SWHSIA 11 | Part 6, §7.4 — Initialization | SW startup and HW BIST sequencing required for safe operation. |
| SWHSIA 12 | Part 6, §7.2 — Unit Testing | Unit test cases covering nominal, fault, boundary, timing per ASIL. |

## External Dependencies

To complete the full verification, the reviewer must cross-check with:
1. **HW Architecture Specification** — signal definitions, pin assignments
2. **SW Architecture Specification** — SWC design, RTOS configuration, FRTI definition
3. **Technical Safety Concept (TSC)** — fault reactions and safe states
4. **Test Specification Catalogue (TSC)** — unit test cases and their coverage
5. **FMEA / FTA** — failure propagation confirmation
6. **System Timing Analysis** — FRTI budgets and latency paths

## Limitations

This skill does NOT:
- Validate signal values or ranges (done in TSC)
- Verify RTOS scheduling feasibility (requires schedulability analysis)
- Check test case adequacy against ASIL (done in TSC review)
- Confirm fault reaction correctness (done in TSC + FMEA cross-check)
- Validate signal integrity mechanisms against CRC/Parity implementation (done in unit testing)

It DOES:
- Confirm all required tabs and columns are present
- Verify data completeness (all handlers have SWC, all safety signals have debounce, etc.)
- Flag missing handler attributes or orphaned signals
- Produce a structured checklist for reviewer approval
- Summarize findings and compliance status in a visual dashboard
