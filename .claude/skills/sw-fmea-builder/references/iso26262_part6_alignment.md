# ISO 26262-6 Alignment — SW FMEA Integration with Product Metrics

## Overview

ISO 26262-6 specifies SW design requirements organized into three categories:

1. **Product Metrics** (§5): Structural code coverage and complexity measures (statement/branch/MCDC coverage, cyclomatic complexity, etc.)
2. **Architecture Metrics** (§6-7): Inter-component isolation, interface integrity, redundancy mechanisms
3. **Verification Metrics** (§8): Test coverage, traceability, design review completeness

The SW FMEA failure mode enumeration directly drives requirements in all three categories by identifying the specific control-flow paths, shared resources, and inter-component dependencies that must be verified and isolated.

## Product Metrics (ISO 26262-6 §5)

### Statement Coverage
- **Definition**: Percentage of executable statements executed by test suite. ISO 26262-6 Table 5 recommends ≥90% for ASIL D, ≥ 80% for ASIL C.
- **SW FMEA Link**: Failure modes like "illegal state" and "divide-by-zero" drive requirement to execute all code paths. Coverage excludes:
  - Unreachable code (dead code must be removed, not just skipped)
  - Error handlers for impossible conditions (but must exist for defensive coding)
- **Application**: For each SWC, calculate required statement coverage from failure modes:
  - Application with deadline miss, illegal state, divide-by-zero → all control paths must be covered
  - Service with missed periodic execution → all scheduler-dependent paths covered
  - Driver with register write fault → all initialization and update paths covered

### Branch Coverage
- **Definition**: Percentage of conditional branches taken in both true and false directions. ISO 26262-6 recommends ≥80% for ASIL D, ≥70% for ASIL C.
- **SW FMEA Link**: Defensive checks (assertions, range checks, state validity) introduce branches. Each branch must be tested:
  - `if (denominator != 0) { result = numerator / denominator; } else { result = safe_default; }` → both branches covered
  - `if (state_is_valid()) { execute_action(); }` → both branches covered (valid and invalid)
- **Application**: Identify all assertions and range checks in FMEA worksheet → coverage target.
  - High-severity failure mode (S3) with assertion → assertion failure path must be tested (error handler verification)

### MCDC Coverage (Modified Condition / Decision Coverage)
- **Definition**: Each condition in a compound boolean expression must independently affect the outcome at least once. Much stricter than branch coverage. ISO 26262-6 recommends ≥ 80% for ASIL D.
- **SW FMEA Link**: Safety-critical decision logic requires full MCDC:
  - `if (pressure > threshold1 AND temperature < threshold2 AND valve_open) { engage_brakes(); }`
  - All 3 conditions must be tested in combinations where each one independently flips the result
- **Application**: Identify multi-condition decision statements from FMEA:
  - CAN stack: `if (msg_id_valid AND crc_pass AND timestamp_recent) { process_msg(); }` → MCDC for E2E protection
  - Diagnostic: `if (sensor_bias > threshold AND consecutive_failures >= 3) { report_dtc(); }` → MCDC for false positive/negative mitigation

### Cyclomatic Complexity
- **Definition**: Number of independent code paths through a function. High complexity (>10) correlates with test difficulty. ISO 26262-6 recommends ≤10 for ASIL D, ≤15 for ASIL C.
- **SW FMEA Link**: Complexity indicates need for refactoring or additional verification:
  - If a function has 20 paths and SW FMEA identifies 15 failure modes covering those paths, 5 paths untested → refactor to reduce complexity
  - Service SWCs (scheduler, protocol handler) often have high complexity → requires MCDC coverage, not just branch
- **Application**: Per SWC type:
  - Application control loops: target ≤ 10 complexity; if > 10, identify untested paths in FMEA
  - Service/Driver: complexity often ≥ 15 due to state machines; MCDC mandatory for safety-critical paths

### Code Inspection / Style Violations
- **Definition**: Automatic checks for suspicious patterns (unreachable code, unused variables, missing null checks, etc.). Per ISO 26262-4, all findings must be reviewed and either fixed or justified.
- **SW FMEA Link**: Inspection findings often relate to failure modes:
  - Missing null check → potential divide-by-zero or illegal state
  - Dead code → indicates incomplete FSM or redundant path
  - Unreachable exception handler → indicates over-defensive coding or logic error
- **Application**: SW FMEA worksheet includes column for "inspection findings per FM" → inspections link to failure modes.

---

## Architecture Metrics (ISO 26262-6 §6-7)

### Partition Isolation (Memory Protection)
- **Definition**: SW partitions (QM, ASIL A, B, C, D) must be isolated such that failure in one partition cannot corrupt another. Enforced by MPU (memory protection unit) on most modern ECUs.
- **SW FMEA Link**: Race conditions, buffer overflows, and stack overflows are mitigated by partition isolation:
  - Race condition in Service SWC (CAN stack) → mitigation: separate partition + inter-partition communication guards
  - Stack overflow in Application SWC → mitigation: separate partition so stack overflow cannot corrupt QM partition heap
- **Application**: For each failure mode in FMEA worksheet, check if mitigation relies on partition isolation:
  - If yes, cite partition boundary in "Mitigation" column
  - Verification plan must include partition isolation test (e.g., intentional buffer overflow in one partition, verify no effect on adjacent partition)

### Interface Integrity (End-to-End Protection)
- **Definition**: All inter-component and inter-partition data transfers must be protected against corruption and loss. Mechanisms include CRC, sequence counter, timeout (E2E protocol per ISO 13400).
- **SW FMEA Link**: Many failure modes involve data corruption across interfaces:
  - "Race condition → corrupted CAN TX frame" → mitigation: E2E protection (CRC + counter) on received message
  - "Receive overrun → lost sensor reading" → mitigation: E2E timeout (if sensor reading not received in 100 ms, assume fault)
  - "Message ordering error" → mitigation: sequence counter ensures out-of-order detection
- **Application**: FMEA worksheet column "Detection Mechanism" includes E2E options (TSC-SM13):
  - All inter-partition critical data must have E2E specified
  - E2E coverage (CRC algorithm + sequence counter) must meet ISO 26262-6 Table 6 requirements for ASIL

### Redundancy & Voting
- **Definition**: For ASIL D, dual or triple redundancy with voting can reduce failure mode severity. E.g., dual sensor with cross-check.
- **SW FMEA Link**: Some failure modes can be downgraded (S3 → S2) if redundancy architecture covers:
  - "False negative (missed fault)" → S3 if single sensor, S1 if dual sensor with plausibility check
  - "Sensor corruption" → S3 if single sensor, S2 if dual with voting + driver self-test (TSC-SM18)
- **Application**: FMEA worksheet column "Mitigation" can reference redundant sensor or cross-check:
  - If redundancy claimed, note voter implementation location (SWC ID, partition)
  - Verification plan must include voter failure test (one sensor stuck, voter must reject)

### Memory Safety (No Buffer Overflows, Stack Underflow)
- **Definition**: Languages like C have no automatic bounds checking. Buffer overflow is undefined behavior; can corrupt arbitrary memory.
- **SW FMEA Link**: Failure mode "stack overflow" requires architecture mitigation:
  - Stack partitioning: each task has isolated stack in separate MPU region
  - Stack depth analysis: compile-time analysis of all call chains; ensure max depth < partition size
  - Runtime checks: stack canary or guard page to detect overflow attempt
- **Application**: For "stack overflow" failure mode:
  - Severity: S3 (crash)
  - Mitigation: stack partitioning + depth analysis + guard page
  - Verification: worst-case call chain analysis (automated + manual review); stack utilization profiling ≤ 80%

---

## Verification Metrics (ISO 26262-6 §8)

### Test Coverage (Unit, Integration, System)
- **Definition**: Percentage of code exercised by test, with emphasis on testing error handling (assertions, exceptions, boundary conditions).
- **SW FMEA Link**: Each failure mode must be verified by at least one test:
  - Deadline miss → unit test with forced delay injection; watchdog fires
  - Divide-by-zero → unit test with denominator = 0; assert / error handler invoked
  - Race condition → integration test with concurrent task access; CRC detects corruption
- **Application**: FMEA worksheet column "Verification Plan Hooks" specifies test method per FM.
  - Unit test methods link to component-level verification
  - Integration test methods link to inter-component verification
  - System tests link to vehicle-level propagation scenarios

### Design Review Completeness
- **Definition**: Critical design decisions (architecture, algorithms, error handling) must be reviewed by qualified personnel (different from designer). ISO 26262-4 requires design review of:
  - Safety requirements & traceability
  - Architecture & decomposition
  - Critical algorithms & state machines
  - All error handling & defensive code
- **SW FMEA Link**: Design review findings often identify missing or inadequate failure mode mitigation:
  - Review identifies: "CAN transmit does not use mutex" → SW FMEA failure mode "race condition" flagged as unmitigated
  - Review confirms: "Watchdog window = 50 ms < task deadline 40 ms margin" → SW FMEA coverage marked "High"
- **Application**: FMEA worksheet row "Mitigation" references design review evidence:
  - E.g., "Race condition mitigated by mutex; verified in design review on 2024-01-15 by Jane Smith"
  - Verification plan column links to design review completion (check Design Review tab in Safety Plan)

### Traceability (Requirements → Design → Test → Verification)
- **Definition**: Every SW requirement must trace to:
  - Design elements (functions, modules, data structures)
  - Test cases (unit, integration, system)
  - Verification evidence (code coverage, code review, test results)
- **SW FMEA Link**: Failure modes drive requirements via TSC SW-TSRs:
  - TSC SW-TSR-001: "Deadline miss shall be detected and reported via watchdog"
  - SW FMEA row: SWC01, Deadline miss, S3, detection = watchdog, coverage = High
  - Trace: SW-TSR-001 → SWC01 watchdog logic → unit test for watchdog fire → test result ✓
- **Application**: FMEA worksheet includes columns for parent FSR (functional safety requirement) and verification plan:
  - Parent FSR = link to TSC / FSC safety goal
  - Verification plan = link to Test Plan / Design Review evidence
  - Generate traceability matrix from FMEA → requirements → tests

---

## Integration Workflow: SW FMEA → ISO 26262-6 Requirements

### Phase 1: Failure Mode Enumeration (SW FMEA §5 in skill)
Identify failure modes per SWC type. Link to:
- **Product metrics** (statement/branch coverage targets per severity)
- **Architecture** (partition isolation, E2E protection required)
- **Verification** (test methods per FM)

### Phase 2: Design Review (SW FMEA §6-7)
Review SWC architecture for isolation and interface integrity:
- Does architecture partition QM from ASIL? YES → isolation FM risk mitigated
- Does critical inter-partition data use E2E? YES → race condition / corruption risk mitigated
- Are shared resources protected by mutex? YES → deadlock/starvation FM risk mitigated

### Phase 3: Code Metrics Calculation (SW FMEA verification columns)
- Measure statement/branch/MCDC coverage per SWC
- Target coverage per ASIL:
  - ASIL D SWC with S3 failure modes → ≥90% statement, ≥80% branch, ≥80% MCDC
  - ASIL B SWC with S2 failure modes → ≥80% statement, ≥70% branch
  - QM SWC → no coverage target
- Flag if coverage < target → design complexity reduction or additional test required

### Phase 4: Verification Evidence Collection (SW FMEA "Verification Plan Hooks" tab)
For each failure mode:
1. Run unit test (fault injection) → measure coverage of error handler
2. Run integration test (multi-task) → verify inter-component isolation
3. Run system test → verify vehicle-level mitigation (e.g., watchdog cuts power to motor)
4. Code review → sign-off on design rationale and error handling completeness

### Phase 5: Traceability & Sign-Off
Generate traceability matrix:
```
SW-TSR-001 "Deadline miss detected"
  → FMEA row: SWC01, Deadline miss, S3, Watchdog, High coverage
  → Requirement: Watchdog window ≤ 50 ms
  → Design: Task period 40 ms, context switch < 5 ms, margin = 5 ms ✓
  → Test: Unit test watchdog fire with delay injection ✓
  → Code review: Watchdog reset in task exit handler; no missed window ✓
  → Status: VERIFIED
```

---

## Example: LKAS Steering Control SWC

**SWC**: LKAS_Controller (Application type, ASIL D)

**Failure Modes** (from SW FMEA):
1. Deadline miss (S3): control loop not executed
2. Illegal state (S3): FSM enters wrong steering state
3. Divide-by-zero (S2): steering angle calculation fails

**Product Metrics** (ISO 26262-6 §5):
- Statement Coverage: ≥90% (ASIL D requirement)
  - Covers: normal steering path, timeout path, error recovery path, FSM all states
  - Exclude: unreachable code, simulator-only paths
- Branch Coverage: ≥80%
  - Covers: all assert conditions in steering algorithm, boundary checks on sensor inputs
- MCDC Coverage: ≥80%
  - Covers: steering angle decision: `if (raw_angle_valid AND magnitude < 100deg AND rate_check_pass) { apply_steering; }`
  - All 3 conditions must be tested independently

**Architecture Metrics** (ISO 26262-6 §6-7):
- Partition: Dedicated ASIL D partition (separate from QM HMI)
- Interface: Sensor input via E2E protected message (CRC + counter); steering output via dual watchdog timers
- Redundancy: Dual steering angle sensor with cross-check (disagreement > 2° → error)

**Verification Metrics** (ISO 26262-6 §8):
- Unit tests: 15 tests for deadline miss (watchdog fire), illegal state (FSM coverage), divide-by-zero (denominator boundary)
- Integration tests: 5 tests for E2E protection, dual sensor voting, cross-partition isolation
- System tests: 3 tests for vehicle-level steering response, watchdog reaction (safe state)
- Code review: Design review by lead architect; test case review by QA
- Traceability: All 3 failure modes ↔ design elements ↔ test cases ↔ code coverage metrics

**Sign-Off**:
```
SW FMEA Worksheet:
  SWC: LKAS_Controller, Deadline miss, S3, Watchdog (High), Residual risk = 27 × 0.1 = 2.7 [FAIL for D]
  → Action: Reduce watchdog window to 20 ms (implies context switch < 2 ms)
  → Retry: Residual risk now = 27 × 0.05 = 1.35 [FAIL for D]
  → Action: Add secondary mechanism (dual monitoring + CPU clock monitor)
  → Retry: Dual detection → coverage = 99.5% (×0.005) → residual risk = 27 × 0.005 = 0.135 [PASS for D]
  → Verification: Dual watchdog test + clock monitor test in HILS
  → Status: ACCEPTED
```

---

## References

- ISO 26262-6:2018 §5: Product design metrics (statement/branch/MCDC coverage, cyclomatic complexity)
- ISO 26262-6:2018 §6: SW architecture & design (partition isolation, redundancy, error handling)
- ISO 26262-6:2018 §7-8: SW verification & quality assurance (design review, test strategy, traceability)
- DO-178C (avionics): Parallel standard with similar product/architecture/verification metrics; strategies transferable
