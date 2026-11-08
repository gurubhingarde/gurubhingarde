# SW FMEA Methodology — ISO 26262-9 §8 + ISO 26262-6 §7-8

## Overview

The Software FMEA is a qualitative, architecture-level analysis per ISO 26262-9 (Functional Safety - Part 9). Unlike Hardware FMEA (which derives quantitative safety metrics: SPFM, LFM, PMHF), Software FMEA focuses on:

1. **Failure Mode Enumeration**: Listing credible failure modes per SW component type
2. **Severity Assessment**: Assigning ASIL-aligned severity per functional context
3. **Frequency Estimation**: Operational likelihood (rare, occasional, frequent)
4. **Detection Mechanism Allocation**: Mapping safety mechanisms from TSC to failure modes
5. **Residual Risk Scoring**: Qualitative formula (severity × frequency × detection coverage adjustment)
6. **Propagation Analysis**: Tracing failure chains from SWC → vehicle behavior

## Failure Mode Taxonomy

### Application SWC (e.g., ESC controller, LKAS)
- **Deadline miss** (task timeout): Real-time constraint violated; control loop delayed or skipped
- **Illegal state** (FSM violation): State machine enters undefined state; control logic invalid
- **Divide-by-zero**: Arithmetic fault; computation halted or produces NaN
- **NaN propagation**: Invalid float spread through calculation chain
- **Stack overflow / heap exhaustion**: Memory allocation fails; execution halted
- **Configuration corruption**: Persistent parameters (EEPROM/Flash) overwritten or lost

### Service SWC (e.g., CAN stack, OS scheduler)
- **Missed periodic execution**: Service callable but not invoked on schedule
- **Race condition**: Shared resource accessed concurrently; data corruption or inconsistent reads
- **Mutex deadlock**: Lock contention causes tasks to block indefinitely
- **Resource leak**: Memory/handles not released; resource exhaustion over time

### Driver SWC (e.g., CAN transceiver, PWM output)
- **Incorrect register write**: Wrong value written to peripheral; incorrect output
- **Missed interrupt**: ISR deferred too long; event not processed
- **Stuck busy bit**: Peripheral status indicates unavailable longer than hardware latency
- **Transmit underrun / Receive overrun**: Buffer boundary condition; frame corruption

### Diagnostic SWC (e.g., on-board diagnostics, health monitor)
- **False positive** (nuisance DTC): Fault detected but not real; false alarm
- **False negative** (missed fault): Fault not detected; real problem unmasked
- **Priority inversion**: Low-priority fault reported as high-priority; diagnostic order wrong
- **Log corruption / rollover**: DTC list overwritten or lost

## Severity Scoring (Log Scale)

| Level | Score | Definition |
|-------|-------|-----------|
| S0 | 0 | No vehicle safety impact; QM-only component |
| S1 | 1 | Minor impact; safe state reachable, or loss of non-critical function |
| S2 | 3 | Major impact; safety goal violation possible but recoverable with secondary mechanism |
| S3 | 9 | Hazardous; uncontrolled vehicle behavior or loss of critical steering/braking |

**Rationale**: Log scale (0, 1, 3, 9) weights high-severity failures more heavily in risk scoring. A single S3 failure is treated as critical regardless of frequency.

## Frequency Scoring

| Level | Score | Rationale |
|-------|-------|-----------|
| Rare | 1 | Failure condition occurs < 1 in 1,000 operating hours or requires unusual environment/user action |
| Occasional | 3 | Failure condition likely 1-10 times in system lifetime under normal operation |
| Frequent | 9 | Failure condition likely > 10 times per lifetime or unavoidable under normal operation |

## Detection Coverage Scoring

| Level | Adjustment Factor | Definition |
|-------|-------------------|-----------|
| Low | ×1.0 | Detection mechanism uncertain, untested, or limited scope (e.g., code review without metrics) |
| Medium | ×0.4 | Detection mechanism proven for subset of cases; evidence (test DC 60-80%, design analysis) |
| High | ×0.1 | Detection mechanism proven for all cases; strong evidence (unit test DC > 90%, watchdog HW timer, assertion coverage analysis) |

## Risk Scoring Formula

**Pre-Mitigation Risk** = Severity Score × Frequency Score

| Frequency | S0 | S1 | S2 | S3 |
|-----------|----|----|----|----|
| Rare      | 0  | 1  | 3  | 9  |
| Occasional| 0  | 3  | 9  | 27 |
| Frequent  | 0  | 9  | 27 | 81 |

**Post-Mitigation Risk** = Pre-Risk × Coverage Adjustment Factor

Example: Deadline miss (S3, Occasional) detected with High coverage → 27 × 0.1 = 2.7

**Residual Risk Acceptable** if Post-Risk ≤ ASIL Threshold:
- ASIL A: ≤ 27
- ASIL B: ≤ 9
- ASIL C: ≤ 3
- ASIL D: ≤ 1

If residual risk exceeds threshold, mitigation must either increase detection coverage or add a secondary mechanism.

## Propagation Analysis

For each failure mode, trace the propagation chain from SWC-level effect to vehicle-level hazard:

**Example 1: ESC Deadline Miss (ASIL D)**
```
SWC: ESC Application (deadline miss)
→ Local Effect: Control loop not executed; wheel slip not regulated
→ Subsystem Effect: Wheel acceleration uncontrolled for 10-100 ms
→ Vehicle Effect: Temporary loss of traction; vehicle skid on low-friction surface
→ Severity: S3 (loss of steering/stability)
→ Detection: Window watchdog timer (TSC-SM04, 50 ms window)
→ Coverage: High (99%)
→ Residual Risk: 27 × 0.1 = 2.7 [UNACCEPTABLE for D threshold 1]
→ Mitigation: Reduce watchdog window to 20 ms (implies task period ≤ 10 ms)
```

**Example 2: CAN Stack Race Condition (ASIL B)**
```
SWC: CAN Service (race condition on TX buffer)
→ Local Effect: Two tasks write to CAN TX register simultaneously
→ Subsystem Effect: Frame corruption; wrong data transmitted
→ Vehicle Effect: Downstream actuators receive invalid command (e.g., steering angle reversed)
→ Severity: S3 (loss of steering control)
→ Detection: CRC + E2E protocol check in receiver; TSC-SM13
→ Coverage: Medium (90% — E2E misses single-bit corruption in CRC seed)
→ Residual Risk: 27 × 0.4 = 10.8 [UNACCEPTABLE for B threshold 9]
→ Mitigation: Add critical section (mutex) around TX register access (Hardware mechanism: atomic write)
```

## Detection Mechanisms & Evidence

| Mechanism | Typical Coverage | Evidence | SW Process Maturity |
|-----------|------------------|----------|---------------------|
| **Assertion** | 60-80% | Code review; static analysis rule coverage; unit test pass count | Design-phase |
| **Watchdog Timer** | 90-99% | HW specification + SW task period analysis; margin demonstration | Proven (embedded industry) |
| **Range Check** | 70-85% | Input specification + boundary value testing; acceptance test DC | Proven |
| **Control Flow Monitor** | 70-90% | Program-flow analysis (e.g., LLVM CFG); test coverage instrumentation | Analysis-dependent |
| **Sentinel / Marker** | 80-95% | Memory init + consistency check; periodic verification; test injection | Proven if periodic interval < task period |
| **Code Review** (architecture/design) | 40-70% | Peer review protocol + checklist adherence; multiple reviewers; traceability | Process-dependent |
| **Dual Redundancy** | 99%+ | Independent implementation; cross-check result; HW comparison logic | Cost-high, used for ASIL D only |

## Residual Risk Acceptance Criteria

1. **Per ASIL**: Each SWC's allocation determines the threshold. ASIL D SWCs require residual risk ≤ 1 for every failure mode.
2. **Per Safety Goal**: Aggregated residual risk across all failure modes mapping to a single Safety Goal must not exceed SG-level threshold (typically same as component threshold).
3. **Cross-SWC Propagation**: If a failure mode in SWC-A propagates to SWC-B, both must claim detection. If SWC-B is QM (threshold ∞), the failure is acceptable if SWC-A detects it. If both are ASIL D, both must detect the downstream effect.

## Verification Plan Hooks

For each failure mode, nominate a verification method:

| Method | Applicability | Effort | Evidence Quality |
|--------|---------------|----|---------|
| **Unit Test** (with fault injection) | Localized FM (arithmetic, state) | Low | High (DC% measurable) |
| **Integration Test** | Inter-SWC propagation | Medium | High (end-to-end observable) |
| **System Simulation** | Vehicle-level effects (propagation chains) | Medium | Medium (simulation fidelity dependent) |
| **Code Review** | Architecture/design rationale; race conditions | Low | Low-Medium (subjective) |
| **Static Analysis** | Arithmetic exceptions, stack depth, race conditions | Low | Medium (rule severity/precision) |
| **HILS / SILS** | Closed-loop safety mechanisms (watchdog, E2E) | High | High (realistic environment) |

Map each FM to at least one verification method. If no verification method is assigned, flag as open item.

## ISO 26262-6 Alignment

The SW FMEA drives requirements for ISO 26262-6 §7 (SW architecture metrics) and §8 (SW design verification):

- **Statement Coverage** (ISO 26262-6 Table 5): ASIL D requires > 90% statement coverage. Use SW FMEA to identify critical paths (deadline miss, illegal state) that must be covered.
- **Branch Coverage** (ISO 26262-6 Table 5): ASIL D recommends > 80% branch coverage. SW FMEA assertions (divide-by-zero checks, range validation) require branch paths to be tested.
- **Partition Isolation** (ISO 26262-6 Table 6): Race conditions and cross-partition data corruption require isolation mechanisms (MPU, inter-partition communication guards). SW FMEA failure mode enumeration justifies partition architecture.
- **Interface Integrity** (ISO 26262-6 §8.4.4): E2E protection (CRC, counter, timeout) on inter-partition/inter-SWC signals. SW FMEA failure mode "message corruption" drives E2E requirements.

## Review Checklist

Before sign-off:

- [ ] Every SWC has ≥ 1 failure mode enumerated
- [ ] Every failure mode has severity assigned (S0-S3) and justified
- [ ] Every failure mode has frequency assigned and defended
- [ ] Every failure mode has detection mechanism(s) allocated from TSC
- [ ] Every detection mechanism has coverage assigned (Low/Med/High) with evidence
- [ ] Residual risk calculated for every FM; green/yellow/red status assigned
- [ ] Residual risk ≤ ASIL threshold for all ASIL SWCs (QM threshold = ∞)
- [ ] Propagation paths traced to vehicle-level hazard for all S3 FMs
- [ ] Verification plan assigned for every FM (test method + owner)
- [ ] No open items (TBD) remain in detection mechanism or coverage columns
