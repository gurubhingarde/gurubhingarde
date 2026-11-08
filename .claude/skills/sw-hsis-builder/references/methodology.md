# SW-HSI Methodology

The Software-side Hardware-Software Interface (SW-HSI) specification formalizes how embedded software processes signals from the hardware-software boundary and propagates fault detection through software architecture.

## What the SW-HSI Captures

The SW-HSI is the **second contract** in the safety-critical signal path:
1. **HW-side HSI** (hsi-builder) specifies every signal crossing the boundary: register address, encoding, integrity protection, timing budget, failure modes.
2. **SW-HSI** (this skill) specifies how software implements handlers for those signals: debouncing strategy, RTOS task allocation, execution time budget, fault propagation to dependent SWCs.

The SW-HSI ensures that every signal:
- Is processed by exactly one SWC handler at a defined RTOS task rate.
- Is protected against noise via a documented debounce method (N-of-M, time-based, hysteresis, or leaky-bucket).
- Has a bounded execution time and can be scheduled within RTOS timing constraints.
- Propagates detected faults through dependent SWCs to vehicle-level reactions (e.g., Limp Home).
- Is tested for nominal operation, fault injection, boundary conditions, and timing edge cases.

## 11-Tab Structure

### Tab 00 — Title Page
Document metadata: project name, SW-HSI doc ID, revision, author, linked HSI and SW architecture, standards and methodology.

### Tab 01 — Document Control
Revision history. Tracks changes to the SW-HSI as handlers are allocated and debouncing strategies are refined.

### Tab 02 — HSI Signal Catalog Echo
Read-only echo of signals from the HW-side HSI. Ensures both teams have the same signal definitions. One row per signal: name, direction (HW->SW or SW->HW), data type, bit width, encoding, ASIL.

### Tab 03 — SW Handler Catalog
**The single source of truth for SW side.** Per signal: handler function name (e.g., `esc_handle_lockstep_mismatch`), allocated SWC (e.g., SWC04), RTOS task (e.g., T02), call frequency (every tick / event-driven / on-demand), max execution time budget (us), return type (e.g., `fault_status_t`).

### Tab 04 — Debounce Strategy per Signal
Per safety signal: debounce method (N-of-M / time-based persistence / hysteresis / leaky-bucket), parameters (e.g., 3-of-5 for N-of-M), rationale (why this method for this signal), false-positive risk percentage, validation approach.

### Tab 05 — Fault Propagation Maps
Per signal fault: detection point (which handler) → fault flag set (global or SWC-local) → propagation path through dependent SWCs → vehicle-level reaction (e.g., Request Limp Home, disable actuator). Text-based chain.

### Tab 06 — RTOS Integration
Per signal: RTOS task ID (e.g., T02_Diag_50ms), task period (ms), task priority, latency from signal arrival to handler execution (ms), jitter budget (ms). Cross-check with FTTI and FDTI budgets.

### Tab 07 — Init Sequence SW Side
SW startup sequence: phase (pre-RTOS, RTOS startup, normal operation), SWCs activated, HSI register reads and init values, self-test handler calls (e.g., `hsi_selftest_validity_bits()`), fault behavior on init failure.

### Tab 08 — Test Cases
Per signal handler: nominal operation test, fault injection test (stuck-at), boundary/edge test (min/max values), timing edge case test (maximum latency + jitter), integration test (dependent SWCs). Row per test type.

### Tab 09 — C Header Stub
Auto-generated C header preview. Shows handler function declarations with Doxygen comments (SWC allocation, task, debounce strategy, max execution time). Full .h file is on disk.

### Tab 10 — References
Linked documents (HSI, SW architecture, RTOS docs), standards (ISO 26262-6 §7, ISO 26262-4 §6.4.6), and reference docs included in the skill.

## Debouncing Rationale

Every safety signal must be protected against noise, transients, and clock jitter. The choice of debounce method depends on:
- **Signal domain** (digital vs. analog, sampled by HW vs. SW).
- **Noise characteristics** (Gaussian, impulse, continuous).
- **FTTI (Fault Tolerance Time Interval)** budget. Debouncing adds latency; must not exceed FDTI + FRTI.
- **False-positive risk budget.** Stricter requirements (ASIL D) demand lower false-positive %, requiring more samples or longer time windows.
- **Computational cost.** N-of-M filters require O(N) memory; time-based requires timers; hysteresis requires state.

See `references/debouncing_patterns.md` for detailed comparison and parameter selection guidance.

## Fault Propagation Chains

A fault detected in one handler must propagate to dependent SWCs and trigger a vehicle-level reaction. The SW-HSI documents this chain for every signal fault:

Example (ESC lockstep mismatch):
```
Detection:   esc_handle_lockstep_mismatch() detects fault, sets FAULT_ESC_LOCKSTEP_MISMATCH
Propagation: Safety Monitor reads FAULT_ESC_LOCKSTEP_MISMATCH every 50ms in T02_Diag
             → Sets FAULT_SYSTEM_SAFE_STATE (block actuator commands)
             → Notifies Vehicle Control SWC (request Limp Home)
Vehicle:     Vehicle Control enters Limp Home mode (speed-limited steering)
```

Every signal handler must have a documented propagation chain. Incomplete chains create gaps in safety coverage.

## RTOS Scheduling Constraints

Each handler is allocated to an RTOS task (periodic or event-driven). The SW-HSI cross-checks:
- **Task period vs. FTTI.** If a signal handler runs in a task with period 50 ms, it cannot detect faults faster than 50 ms. Ensure task period <= FTTI - debounce_time.
- **Task priority vs. latency budget.** If the handler task is low-priority and can be preempted by higher-priority tasks, the worst-case latency may exceed the budget. Model worst-case preemption time.
- **Jitter budget.** RTOS scheduling introduces jitter (variation in execution time). Leave headroom in the latency budget: latency_budget >= handler_execution_time + jitter.

Cross-check these constraints when allocating handlers to RTOS tasks.

## Initialization Sequence

The SW-side initialization sequence must coordinate with the HW-side:

1. **Pre-RTOS (HW in safe state, SW not yet running):**
   - HW completes BIST, locks HSI registers, asserts ready flag.
   - SW starts up, reads HSI register lock state and validity bit state, confirms HW ready.

2. **RTOS Startup:**
   - SW initializes handler state (debounce filters, liveness counters, fault flags).
   - SW calls self-test handlers (e.g., `hsi_selftest_validity_bits()`) to verify HSI register state.
   - If any self-test fails, SW requests safe state (watchdog reset or safe shutdown).

3. **Normal Operation:**
   - Handlers run on schedule (periodic or event-driven).
   - Fault flags propagate through SWCs to vehicle-level reactions.

The SW-HSI documents this sequence and identifies failure modes at each phase (e.g., "HW BIST failed" → "SW detects HW not ready" → "Request safe state").

## Cross-Reference Traceability

Each signal handler traces back to:
- **HSI signal** (name, direction, ASIL, encoding).
- **Failure modes** (stuck-at, parity error, missing, late, out-of-range) from HW-side HSI.
- **Debounce strategy** (method, parameters, false-positive risk).
- **RTOS task** (task ID, period, priority, latency budget).
- **Dependent SWCs** (which SWCs read the fault flag).
- **Vehicle reaction** (Limp Home, disable actuator, request safe state).
- **Test cases** (nominal, fault injection, boundary, timing edge case, integration).

This traceability enables impact analysis: if a timing constraint changes, trace through all affected handlers and test cases.
