# SW Failure Mode Library — ISO 26262-6 §5 Product Metrics

This is the canonical SW failure mode taxonomy aligned with ISO 26262-6 Table 5-6 (product design metrics). Use this as the foundation for SW FMEA enumeration by SWC type.

## Application SWC (Real-Time Control Logic)

Typical context: ESC controller, LKAS steering, engine management, brake-by-wire.

### 1. Deadline Miss (Task Timeout)
- **Local Effect**: Real-time control loop not executed within required period. Sensor input stale; actuator command delayed.
- **Subsystem Effect**: Control algorithm uses outdated plant state. Feedback loop gain effectively infinite; system unstable or unresponsive.
- **Vehicle Effect**: Temporary loss of active safety function. E.g., ESC slips uncontrolled for 10-100 ms; LKAS steering angle lags vehicle trajectory.
- **Typical Severity**: S3 (loss of stability/steering)
- **Typical Frequency**: Occasional (if system fully loaded or task blocked by lower-priority task)
- **Detection Mechanisms**: Window watchdog timer (TSC-SM04), task scheduler instrumentation, cyclic redundancy checking of output
- **Evidence for Coverage**: Task period analysis (worst-case execution time + context switch overhead ≤ deadline margin); watchdog period set to 1.5× longest task period; test with profiler

### 2. Illegal State (FSM Violation)
- **Local Effect**: State machine enters undefined or erroneous state due to logic fault, race condition, or corrupted state variable.
- **Subsystem Effect**: Control decision tree produces unexpected command. E.g., state says "standby" but sends "engage" signal to actuator.
- **Vehicle Effect**: Unintended actuation or loss of function. Severity depends on state transition path.
- **Typical Severity**: S2-S3 (depends on which state is entered)
- **Typical Frequency**: Rare (if FSM design sound; occasional if high interrupt load)
- **Detection Mechanisms**: Assertion on state variable validity (state in valid set), control flow monitor, design review
- **Evidence for Coverage**: Code review with checklist covering all transitions; assertion pass rate in unit test; static analysis of state reachability

### 3. Divide-by-Zero / Arithmetic Exception
- **Local Effect**: Division by zero or integer overflow causes exception or incorrect result (e.g., NaN, saturation).
- **Subsystem Effect**: Subsequent calculations invalid. Output command may be stale or zero.
- **Vehicle Effect**: Loss of active control function; fallback to failsafe (e.g., cut power to motor).
- **Typical Severity**: S2 (loss of function with safe fallback)
- **Typical Frequency**: Occasional (if denominator data is sensor-dependent and can briefly be zero, e.g., wheel slip near singularity)
- **Detection Mechanisms**: Input range check before division (assert denominator ≠ 0), floating-point exception handler, type safety (avoid integer division if possible)
- **Evidence for Coverage**: Specification document with listed division operations; static analysis of denominator source; test boundary condition (denominator = 0.001)

### 4. NaN Propagation (Invalid Float State)
- **Local Effect**: Floating-point calculation produces NaN (e.g., sqrt(-1), 0/0); NaN spreads through filter/control loop.
- **Subsystem Effect**: Invalid output commands or divergent state estimates. Feedback loop may oscillate or diverge.
- **Vehicle Effect**: Loss of stability or accuracy. E.g., LKAS steering angle diverges; ESC traction control becomes erratic.
- **Typical Severity**: S2-S3 (uncontrolled vehicle behavior possible)
- **Typical Frequency**: Rare-Occasional (if input validation insufficient)
- **Detection Mechanisms**: Range check on intermediate results (assert output in expected range), NaN / infinity detection (e.g., `isnan()`, `isinf()`), watchdog on output signal
- **Evidence for Coverage**: Floating-point range specification per calculation; test with boundary inputs; static analysis or instrumentation to detect NaN operations

### 5. Stack Overflow / Heap Exhaustion
- **Local Effect**: Stack or heap allocation fails. Tasks cannot execute or memory corruption occurs.
- **Subsystem Effect**: Application hangs or crashes; safety mechanisms may also be disabled.
- **Vehicle Effect**: Loss of all active functions; fallback to mechanical default (e.g., steering center, brakes locked).
- **Typical Severity**: S3 (loss of all active control)
- **Typical Frequency**: Rare (if memory budget carefully managed)
- **Detection Mechanisms**: Static analysis of stack depth (compiler + manual review), heap allocation guards (allocator that prevents > 80% utilization), watchdog on CPU stall
- **Evidence for Coverage**: Stack trace analysis from worst-case call chain; heap watermark testing; heap exhaustion test case with sustained object allocation

### 6. Configuration Corruption (Persistent State Loss)
- **Local Effect**: EEPROM/Flash parameters overwritten by stray write or logic error. Calibration data, safety thresholds, VIN, etc. lost or altered.
- **Subsystem Effect**: Vehicle operates with invalid configuration; thresholds may be unsafe (e.g., ABS threshold too low → wheels lock during braking).
- **Vehicle Effect**: Loss of correct behavior; potential uncontrolled actuation.
- **Typical Severity**: S2-S3 (depends on corrupted parameter)
- **Typical Frequency**: Rare (if write guards adequate)
- **Detection Mechanisms**: CRC check on config block (TSC-SM07), watchdog on write address range, design review of write accesses
- **Evidence for Coverage**: Specification of all write operations to persistent storage; CRC algorithm verification (e.g., polynomial proven per ISO 26262-6 §7); test with intentional bit flips

---

## Service SWC (OS, Protocol Stack, Middleware)

Typical context: CAN/LIN stack, OS scheduler, inter-partition communication, memory manager.

### 1. Missed Periodic Execution
- **Local Effect**: Service (e.g., CAN message transmit, diagnostic poll) callable but not invoked on its schedule. Event loses opportunity.
- **Subsystem Effect**: Downstream SWCs that depend on this service receive stale data or miss critical updates.
- **Vehicle Effect**: Loss of communication or diagnostic function. E.g., CAN transmit not sent; vehicle unable to report fault codes to external scanner.
- **Typical Severity**: S1-S2 (loss of non-critical or diagnostic function)
- **Typical Frequency**: Occasional (if system load unpredictable or scheduler not deterministic)
- **Detection Mechanisms**: Scheduler instrumentation (cyclic counter in each service invocation), watchdog on service interval, heartbeat signal (e.g., CAN periodic transmit with monitor)
- **Evidence for Coverage**: Scheduler design review + test with known load patterns; counter/timestamp logged per invocation; test with worst-case concurrent tasks

### 2. Race Condition (Shared Resource Contention)
- **Local Effect**: Two or more tasks access shared data (e.g., global variable, I/O register) without synchronization. Data corruption, inconsistent reads.
- **Subsystem Effect**: One SWC reads corrupted state from shared resource. Output command invalid.
- **Vehicle Effect**: Unpredictable control behavior; may result in unintended actuation.
- **Typical Severity**: S2-S3 (depends on shared data semantic; steering angle corruption = S3)
- **Typical Frequency**: Rare (if access window small, e.g., 32-bit atomic write on 32-bit CPU)
- **Detection Mechanisms**: Mutex / critical section (TSC-SM30), inter-partition communication guard, E2E protection on shared data (CRC + sequence counter if data passed between partitions)
- **Evidence for Coverage**: Code review identifying all shared data accesses; static analysis for missing locks (tools like ThreadSanitizer); race condition injection test with forced concurrent execution

### 3. Mutex Deadlock / Starvation
- **Local Effect**: Task acquires lock on Resource A, then tries to acquire lock on Resource B (held by Task B which holds lock on Resource A). Both tasks block indefinitely.
- **Subsystem Effect**: Tasks cannot progress. System appears hung.
- **Vehicle Effect**: Loss of active safety functions; system unresponsive.
- **Typical Severity**: S3 (loss of all active control)
- **Typical Frequency**: Rare (if lock discipline enforced; occasional under stress test)
- **Detection Mechanisms**: Watchdog on deadlock detection, lock ordering policy (design review to prevent circular waits), timeout on mutex acquire with exception handler
- **Evidence for Coverage**: Lock dependency graph analysis (tools like Promela / SPIN); stress test with many concurrent operations; code review enforcing lock order discipline

### 4. Resource Leak (Memory or Handle Exhaustion)
- **Local Effect**: Task allocates resource (memory, file handle, socket) but fails to release. Leak accumulates over time.
- **Subsystem Effect**: After hours/days of operation, system runs out of memory or handles. New allocations fail.
- **Vehicle Effect**: System degrades; critical functions may fail to initialize. E.g., new CAN frame allocation fails; message lost.
- **Typical Severity**: S2 (loss of function after extended operation)
- **Typical Frequency**: Occasional (if application design has unbounded allocation)
- **Detection Mechanisms**: Static analysis for missing free/delete (tools like Clang analyzer, Valgrind), heap profiling, periodic memory report (memory used / total), watchdog on memory high-water mark
- **Evidence for Coverage**: All allocation points reviewed for corresponding release; heap profiling run for > 1 hour nominal operation; memory high-water mark < 80% of heap total

---

## Driver SWC (Peripheral Interface, HAL)

Typical context: CAN transceiver, PWM output, SPI communication, ADC input multiplexer, GPIO.

### 1. Incorrect Register Write
- **Local Effect**: Wrong value written to peripheral register (e.g., configuration, data, command). Peripheral enters wrong state or transmits wrong data.
- **Subsystem Effect**: Peripheral output incorrect. E.g., CAN node ID wrong → messages have wrong ID; PWM duty cycle off.
- **Vehicle Effect**: Downstream systems receive invalid command or data. E.g., steering angle command wrong → unintended lane change.
- **Typical Severity**: S2-S3 (depends on register function)
- **Typical Frequency**: Rare (if driver logic correct)
- **Detection Mechanisms**: Readback + compare (read register back and verify it matches write value), design review of register mapping, static analysis of register address calculation
- **Evidence for Coverage**: Readback implemented for all critical writes; test verifies readback matches expected value for each register; address calculation reviewed by 2nd engineer

### 2. Missed Interrupt (ISR Deferred)
- **Local Effect**: Interrupt request from peripheral (e.g., CAN message received, ADC conversion complete) occurs, but ISR not invoked soon enough. Event queue overflow or stale data.
- **Subsystem Effect**: Real-time event not processed. E.g., CAN receive frame lost; sensor reading dropped.
- **Vehicle Effect**: Loss of sensor data or communication; control loop uses stale state.
- **Typical Severity**: S2 (loss of real-time responsiveness)
- **Typical Frequency**: Occasional (if ISR nesting deep or task priority inversion high)
- **Detection Mechanisms**: ISR latency instrumentation (timestamp interrupt request vs. ISR entry), event queue overflow counter, watchdog on data freshness (if receive ISR has not fired in expected interval)
- **Evidence for Coverage**: ISR latency measurement on worst-case load; queue overflow test (simulate rapid events); latency < 10% of interrupt period

### 3. Stuck Busy Bit / Peripheral Timeout
- **Local Effect**: Peripheral returns "busy" status indefinitely (e.g., UART TX FIFO full, SPI transfer in progress). Driver waits forever.
- **Subsystem Effect**: Driver hangs; task cannot proceed. Downstream SWCs timeout waiting for response.
- **Vehicle Effect**: Loss of communication or sensor function.
- **Typical Severity**: S2 (loss of peripheral function)
- **Typical Frequency**: Rare (if peripheral hardware design sound)
- **Detection Mechanisms**: Timeout counter on busy-wait loops, watchdog on driver response time, peripheral self-test (TSC-SM18 for some drivers)
- **Evidence for Coverage**: Timeout value calculated from peripheral specification max delay × safety margin (typically 2× spec); test with peripheral simulator that hangs to verify timeout fires; timeout period < task deadline

### 4. Transmit Underrun / Receive Overrun
- **Local Effect**: DMA or FIFO boundary exceeded. TX underrun: peripheral continues transmitting when no data ready (sends garbage). RX overrun: incoming data overwrites unread buffer.
- **Subsystem Effect**: Frame corruption or data loss.
- **Vehicle Effect**: Corrupted message on bus → downstream node rejects or misinterprets.
- **Typical Severity**: S2 (data corruption, potentially recoverable with E2E protection)
- **Typical Frequency**: Occasional (if buffer sizing inadequate or DMA bandwidth limited)
- **Detection Mechanisms**: Buffer watermark monitoring (flag when < N bytes available before deadline), DMA error interrupt, E2E protection on transmitted/received data (TSC-SM13 catches corruption)
- **Evidence for Coverage**: Buffer size analysis per data rate and interrupt latency; watermark test with high-load scenario; E2E coverage for all critical frames

---

## Diagnostic SWC (On-Board Diagnostics, OBD, Health Monitor)

Typical context: DTC detection and reporting, self-test, fault logging, health status broadcast.

### 1. False Positive (Nuisance DTC)
- **Local Effect**: Fault detection logic triggers when no real fault exists. E.g., sensor noise interpreted as component failure.
- **Subsystem Effect**: Fault code logged and reported. Technician repairs non-existent fault.
- **Vehicle Effect**: Unnecessary service visits; customer dissatisfaction. Not a direct safety risk, but impacts fleet availability.
- **Typical Severity**: S0-S1 (no safety risk; customer impact only)
- **Typical Frequency**: Occasional (if detection threshold not properly tuned)
- **Detection Mechanisms**: Threshold hysteresis, multi-sample confirmation (e.g., fault must be present for 3 consecutive samples), noise filtering before threshold comparison
- **Evidence for Coverage**: Threshold derivation per spec (e.g., sensor noise margin + fault magnitude margin); multi-sample count justified; test with noise injection (white/colored) below threshold

### 2. False Negative (Missed Fault)
- **Local Effect**: Real fault exists but detection logic does not trigger. Component failure unmasked.
- **Subsystem Effect**: Fault goes undiagnosed. Subsequent failure modes in downstream components.
- **Vehicle Effect**: Loss of function or uncontrolled behavior when coupled with another failure.
- **Typical Severity**: S1-S3 (depends on fault semantic; undetected loss of brake pressure = S3)
- **Typical Frequency**: Rare (if detection logic sound)
- **Detection Mechanisms**: Self-test / built-in test (TSC-SM18 for some components), dual-threshold or statistical test (e.g., chi-square test for sensor bias), cross-check with redundant sensor
- **Evidence for Coverage**: Fault simulation test (inject known fault, verify DTC raised); self-test coverage analysis (% of detectable faults caught by built-in test); dual-sensor coverage specification

### 3. Priority Inversion (DTC Order Wrong)
- **Local Effect**: Multiple faults detected; reported in wrong priority order. E.g., secondary fault reported before root cause.
- **Subsystem Effect**: Technician debugs secondary symptom first; root cause missed.
- **Vehicle Effect**: Unplanned downtime; fault not resolved.
- **Typical Severity**: S0-S1 (diagnostic impact only)
- **Typical Frequency**: Rare (if DTC priority matrix correct)
- **Detection Mechanisms**: Design review of DTC priority mapping, DTC matrix documentation, diagnostic manual review
- **Evidence for Coverage**: DTC priority matrix agreed by systems engineering + diagnostics team; test with multi-fault scenario; DTC order verified against matrix

### 4. Log Corruption / Rollover
- **Local Effect**: Diagnostic log (freeze frame, DTC history) overwritten or lost due to EEPROM write error or buffer overflow.
- **Subsystem Effect**: Diagnostic history unavailable. Technician cannot trace fault pattern.
- **Vehicle Effect**: Delayed root cause analysis; warranty claim disputes.
- **Typical Severity**: S0 (no direct safety risk; diagnostic/business impact)
- **Typical Frequency**: Rare (if log management sound)
- **Detection Mechanisms**: CRC on diagnostic log block (TSC-SM07), log fullness counter (prevent unlimited accumulation), test with forced write errors
- **Evidence for Coverage**: CRC polynomial verified; log buffer size specification (total entries, rotation policy); test with log-full condition to verify graceful rollover or halt

---

## Selecting Failure Modes for Your SWC

1. **Identify SWC Type**: Classify each component as Application, Service, Driver, or Diagnostic based on function.
2. **Apply Default Library**: Use failure modes listed above. If SWC has mixed responsibilities (e.g., Application + Diagnostic), enumerate modes from both categories.
3. **Review for Local Context**: Adjust severity/frequency based on:
   - Functional criticality (e.g., steering = S3; mirror = S0)
   - Real-time constraints (e.g., deadline miss = S3 if control loop; S1 if data logging)
   - Redundancy & mitigation architecture (e.g., dual sensor can mitigate sensor failure from S3 → S1)
4. **Override in Input JSON**: For SWCs with non-standard failure modes or project-specific risk, use `failure_mode_overrides` in input JSON.

---

## References

- ISO 26262-6:2018 §5: Product design metrics (statement coverage, branch coverage, etc.)
- ISO 26262-6:2018 §6-8: SW architecture, design, verification (implements mitigation for enumerated modes)
- AIAG Automotive Safety Handbook, Chapter 5: Software FMEA (practical examples for automotive SW)
