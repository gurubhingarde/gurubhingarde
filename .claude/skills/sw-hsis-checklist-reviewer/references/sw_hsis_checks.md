# SW HSI Specification Checks — Detailed Definitions

## Confirmation Review (CR) — 14 Document Quality Checks

### CR-1: Document Structure (Shall)
**Requirement**: Is the document structured in a clear manner?

**Verification**: Count tabs. SW HSI typically needs 10+ tabs (Title, Doc Control, Signal Catalog Echo, SW Handlers, Debounce, Fault Propagation, RTOS, Init Seq, Test Cases, References).

**Rating Guide**:
- **FC**: 10+ distinct, clearly labeled tabs
- **PC**: 6-9 tabs; some important sections missing
- **NO**: <5 tabs; poor organization

---

### CR-2: Template Version (Should)
**Requirement**: On creation date, was the latest template available used?

**Verification**: Cannot be auto-detected from xlsx. Draft finding; reviewer confirms.

---

### CR-3: Searchability (Should)
**Requirement**: Does document structure facilitate search (TOC, index, cross-references)?

**Verification**: Presence of Title/General Info tab + References tab.

**Rating Guide**:
- **FC**: Both TOC and References tabs present
- **PC**: One or neither present
- **NO**: Neither present

---

### CR-4a: Title & Scope (Shall)
**Requirement**: Does the title cover the scope of the content?

**Verification**: Title field populated on Title page. Reviewer confirms scope coverage.

---

### CR-4b: Author & Approver (Shall)
**Requirement**: Are author and approver(s) listed?

**Verification**: Both fields populated on Title page.

**Rating Guide**:
- **FC**: Both present
- **NO**: Either missing

---

### CR-4c: Unique Revision (Shall)
**Requirement**: Is there a unique identification for each revision?

**Verification**: Revision field on Title page is not empty.

---

### CR-4d: Change History (Shall)
**Requirement**: Is there a change history available?

**Verification**: Document Control tab has >=1 revision history row with non-empty revision column.

---

### CR-4e: Status (Shall)
**Requirement**: Is the status of the work product provided?

**Verification**: Status field on Title page populated (Draft, In Review, Released, etc.).

---

### CR-5: Current Revision Identifiable (Shall)
**Requirement**: Is the current applicable revision clearly identifiable?

**Verification**: Revision field on Title page.

---

### CR-6: Configuration Management (Shall)
**Requirement**: Is the document under configuration and change management?

**Verification**: Cannot be verified from xlsx alone. Draft finding; reviewer confirms CM system check-in.

---

### CR-7: Header & Footer (Should)
**Requirement**: Are the header and footer updated?

**Verification**: Cannot be reliably detected programmatically. Draft finding; reviewer checks in Excel.

---

### CR-8: Table of Contents (Shall)
**Requirement**: Does this document contain a correct table of contents?

**Verification**: Title, General Info, or Contents tab present in first 3 sheets.

---

### CR-9: References (Should)
**Requirement**: Does the Reference Table list all references?

**Verification**: References tab detected.

**Rating Guide**:
- **FC**: References tab present; reviewer confirms content
- **PC**: References tab missing or sparse
- **NO**: No references tab

---

### CR-10: Sections Complete (Should)
**Requirement**: Have all sections of the Work Product been completed?

**Verification**: Count populated tabs (Handler Catalog, Debounce, Fault Propagation, RTOS, Init Seq, Test Cases present) + signal completeness (>90% have direction, data type).

**Rating Guide**:
- **FC**: 4/5 content tabs + >90% signal completeness
- **LC**: 3/5 tabs + >70% signal completeness
- **PC**: <3/5 tabs or <70% signal completeness

---

## SW HSI Assessment (SWHSIA) — 12 Substantive Checks

### SWHSIA-1: HSI Signal Catalog Echo (Shall)
**Requirement**: Is the HSI signal catalog echoed from source HSI (count > 0)?

**Context**: SW HSI starts by echoing all signals from the source Hardware HSI Specification. This ensures all interface signals are considered.

**Verification**: Signal count in HSI Signal Catalog Echo tab.

**Rating Guide**:
- **FC**: >5 signals with direction, data type, owner
- **LC**: 1-5 signals; verify completeness
- **PC**: Empty or incomplete signals
- **NO**: No signals at all

**ISO 26262 Link**: Part 4, §6.4.6 — HSI Specification must enumerate all interface signals.

---

### SWHSIA-2: Handler Function Names (Shall)
**Requirement**: Does each signal have SW handler function name?

**Context**: Every HSI signal must be handled by a software function. The function name (e.g., `handle_wheel_speed_input()`) must be identified.

**Verification**: All rows in SW Handler Catalog have non-empty "Handler Function Name" column.

**Rating Guide**:
- **FC**: 100% of handlers have function names
- **LC**: 95-99% have names
- **PC**: 80-95% have names
- **NO**: <80% or no handlers

**ISO 26262 Link**: Part 6, §7.4 — Software Unit Design.

---

### SWHSIA-3: SWC Allocation (Shall)
**Requirement**: Is each handler allocated to a Software Component (SWC)?

**Context**: Handlers are organized into Software Components per SW Architecture. Each handler must belong to exactly one SWC.

**Verification**: All handlers have non-empty "Allocated SWC" column.

**Rating Guide**:
- **FC**: 100% allocated
- **PC**: 70-99% allocated
- **NO**: <70% or no allocations

**ISO 26262 Link**: Part 6, §7 — SW Design hierarchy (SWC -> Unit -> Function).

---

### SWHSIA-4: Calling RTOS Task (Shall)
**Requirement**: Is each handler's calling RTOS task identified?

**Context**: Handlers execute under RTOS task context (e.g., "SensorTask", "ControlTask"). Task determines execution rate, priority, and timing constraints.

**Verification**: All handlers have non-empty "Calling Task" column.

**Rating Guide**:
- **FC**: 100% have task assigned
- **PC**: 70-99% have task
- **NO**: <70% or no tasks

**ISO 26262 Link**: Part 6, §7.3 — RTOS Configuration and Task Design.

---

### SWHSIA-5: Max Execution Time (Shall)
**Requirement**: Does each handler have max execution time budget specified?

**Context**: Each handler has a WCET (Worst-Case Execution Time) that must be <=FRTI (Functional Requirements for Timing Interval). Used for schedulability analysis.

**Verification**: All handlers have non-empty "Max Execution Time" column (e.g., "2ms", "5000us").

**Rating Guide**:
- **FC**: 100% have execution budget
- **PC**: 70-99%
- **NO**: <70%

**ISO 26262 Link**: Part 6, §7.4.9 — Timing Analysis and Requirements.

---

### SWHSIA-6: Debounce Specified (Shall)
**Requirement**: Does each safety-relevant signal have debounce strategy?

**Context**: Safety-relevant signals (ASIL A/B/C/D, not QM) must be debounced to filter noise and slow transients before processing.

**Verification**: For each safety-relevant signal, a Debounce Strategy tab row exists.

**Rating Guide**:
- **FC**: 100% of safety signals have debounce
- **PC**: 70-99% have debounce
- **NO**: <70% or no debounce tab

**ISO 26262 Link**: Part 6, §7.4.11 — Input Debouncing for Safety-Relevant Signals.

---

### SWHSIA-7: Debounce Parameters Reasonable (Shall)
**Requirement**: Are debounce parameters reasonable (N-of-M with N>=2, time threshold sensible)?

**Context**: Debounce parameters must be validated:
- **N-of-M**: signal must be stable for N out of M consecutive samples. N should be >=2 (e.g., 2-of-3, 3-of-5).
- **Time threshold**: signal must hold value for X ms. Should be reasonable for signal's expected rise/fall time and noise window.

**Verification**: All debounce rows have N-of-M or time threshold populated.

**Rating Guide**:
- **FC**: All parameters present and appear reasonable (N>=2, time in sensible range)
- **Medium**: Parameters present; reviewer to verify against signal characteristics
- **PC**: Some parameters missing
- **NO**: No parameters specified

**ISO 26262 Link**: Part 6, §7.4.11 — Debounce Configuration.

---

### SWHSIA-8: Fault Propagation Trace (Shall)
**Requirement**: Does fault propagation map trace each signal fault to vehicle reaction?

**Context**: When a signal fails (stuck-0, stuck-1, incorrect encoding, timeout), the software must detect it and react appropriately (e.g., set error flag, trigger safe state). This is documented in Fault Propagation Maps.

**Verification**: Fault Propagation tab has rows covering signal name, failure mode, detection mechanism, vehicle reaction.

**Rating Guide**:
- **FC**: 100% of signals have fault propagation rows with all columns
- **PC**: 70-99% covered or incomplete
- **NO**: <70% or no tab

**ISO 26262 Link**: Part 4, §6.4.6 — TSC Requirements; Part 6, §7.4.12 — Fault Detection & Reaction.

---

### SWHSIA-9: RTOS Integration (Shall)
**Requirement**: Is RTOS integration documented (task name, priority, period, signals)?

**Context**: RTOS tasks are configured with:
- Task name (identifier)
- Priority (scheduling priority, e.g., 10)
- Period (execution rate, e.g., 10ms)
- Signals processed (which HSI signals this task handles)

**Verification**: RTOS Integration tab exists with >0 rows, all tasks have name, priority, period.

**Rating Guide**:
- **FC**: >=1 task documented with all fields
- **PC**: Partial RTOS documentation
- **NO**: No RTOS Integration tab

**ISO 26262 Link**: Part 6, §7.3 — RTOS Configuration.

---

### SWHSIA-10: Latency Within FRTI (Shall)
**Requirement**: Is latency from signal arrival to handler execution within FRTI budget?

**Context**: FRTI (Functional Requirements for Timing Interval) is the maximum allowable time from sensor input arrival to vehicle control action. Latency includes:
1. Signal acquisition by hardware
2. RTOS scheduling delay
3. Handler execution time
4. Control output calculation and actuator command

**Verification**: Requires cross-check with:
- Handler execution times (SWHSIA-5)
- RTOS task periods (SWHSIA-9)
- Control output delay
- FRTI defined in SW Architecture Specification

**Rating Guide**:
- **FC**: All handler latencies + task periods < FRTI
- **Medium**: Timing analysis required; reviewer to verify
- **PC**: Some latencies unknown
- **NO**: FRTI not defined or latencies exceed it

**ISO 26262 Link**: Part 6, §7.4.9 — Timing Analysis and Requirements.

---

### SWHSIA-11: Init Sequence Coordinated (Shall)
**Requirement**: Is SW initialization sequence coordinated with HW BIST sequence?

**Context**: At power-up or reset:
1. Hardware executes Built-In Self-Test (BIST) to verify memory, CPU, peripherals
2. Software startup initializes drivers, data structures, timers
3. Order and timing must be coordinated to ensure HW ready before SW uses it

**Verification**: Init Sequence SW Side tab has rows documenting steps, with HW BIST references.

**Rating Guide**:
- **FC**: Init sequence documented with HW BIST cross-references
- **Medium**: Sequence present; reviewer to verify HW coordination
- **PC**: Sequence partial or HW references missing
- **NO**: No Init Sequence tab

**ISO 26262 Link**: Part 6, §7.4 — Software Unit Design; Part 5, §7.4 — HW Init & BIST.

---

### SWHSIA-12: Test Cases Comprehensive (Shall)
**Requirement**: Are test cases defined per handler (nominal, fault, boundary, timing)?

**Context**: Each handler must have test cases covering:
- **Nominal**: normal input values, expected output
- **Fault injection**: signal faults (stuck-0, stuck-1, corrupt), expected error handling
- **Boundary**: edge values (min, max, transitions)
- **Timing**: handler called faster/slower than expected, priority inversions

**Verification**: Test Cases tab has >=1 test per handler, covering different test types.

**Rating Guide**:
- **FC**: 100% of handlers have multiple test cases (nominal, fault, boundary, timing)
- **LC**: 100% have at least nominal + fault
- **PC**: 70-99% have tests or incomplete coverage
- **NO**: <70% or no Test Cases tab

**ISO 26262 Link**: Part 6, §7.2 — Software Unit Verification and Testing.

---

## Verification Assessment (VA) — 5 External Verification Checks

### VA-1: Signal Integrity Protection (Shall)
**Requirement**: Are safety-relevant signals protected (Parity/CRC/SECDED)?

**Context**: Safety-relevant signals must have error detection capability. Common methods:
- **Parity bit**: single-bit error detection
- **CRC**: cyclic redundancy check for multi-byte signals
- **SECDED**: single-error-correction, double-error-detection
- **Dual-channel**: redundant transmission

**Verification**: Cross-check with Integrity Protection column in HSI Signal Catalog Echo.

**Rating Guide**:
- **FC**: All safety signals have integrity mechanism
- **PC**: 70-99% protected
- **NO**: <70% or no protection

**ISO 26262 Link**: Part 6, §7.4.13 — Data Integrity and Signal Encoding.

---

### VA-2: Handler Coverage (Shall)
**Requirement**: Do SW handlers cover all HSI signals?

**Context**: Every HSI signal must have a corresponding handler. Orphaned signals (not handled) indicate incomplete specification.

**Verification**: Count signals without handler > 0 or handler count / signal count.

**Rating Guide**:
- **FC**: 100% of signals handled (or 90%+)
- **LC**: 80-90% covered
- **PC**: 70-80% covered
- **NO**: <70% covered

**ISO 26262 Link**: Part 6, §7.4 — Software Unit Design.

---

### VA-3: Debounce Effectiveness (Shall)
**Requirement**: Is debounce effectiveness verified against signal characteristics?

**Context**: Debounce N and time threshold must match signal rise/fall time, noise environment, and acceptable latency. For example:
- A noisy sensor with 100us rise time needs minimum debounce time > 100us
- A 100Hz signal sampled at 1kHz can use N-of-M with M=10

**Verification**: Requires cross-check with:
- Signal frequency / sample rate
- Hardware noise margin spec
- FRTI constraints

**Rating Guide**:
- **Medium**: Debounce parameters present; reviewer to verify against noise specs
- **PC**: Parameters missing or unrealistic
- **NO**: No debounce or parameters invalid

**ISO 26262 Link**: Part 6, §7.4.11 — Debounce Implementation.

---

### VA-4: Call Frequency Consistency (Shall)
**Requirement**: Is handler call frequency consistent with signal sample rate?

**Context**: Handler call frequency must be >= signal sample rate to avoid aliasing or missed samples.
- Signal sample rate = frequency at which hardware provides new data
- Handler call frequency = frequency at which software processes data

Example: If wheel-speed sensor produces 100 samples/second, handler must be called at least 100 times/second.

**Verification**: Cross-check:
- Signal sample rate (from HSI Signal Catalog or HW HSI)
- Handler call frequency (SWHSIA-2, Call Frequency column)

**Rating Guide**:
- **FC**: 100% of handlers called at >= signal sample rate
- **Medium**: Frequencies documented; reviewer to verify aliasing risk
- **PC**: Some frequencies unknown
- **NO**: Handler call < signal sample rate

**ISO 26262 Link**: Part 4, §6.4.6 — HSI Specification requirements for sample rates.

---

### VA-5: End-to-End Latency (Shall)
**Requirement**: Is end-to-end latency (signal to vehicle reaction) within FRTI?

**Context**: Total latency from sensor input to actuator output must be <=FRTI. Path includes:
1. Sensor hardware delay
2. HSI transmission delay (CAN, LIN, shared memory, etc.)
3. RTOS scheduling delay
4. Handler execution time
5. Control calculation
6. Actuator command transmission
7. Actuator response time

**Verification**: Requires integration with TSC and system timing analysis.

**Rating Guide**:
- **Medium**: Sub-latencies documented; reviewer to trace end-to-end path
- **PC**: Some latencies missing
- **NO**: FRTI not met or latency unknown

**ISO 26262 Link**: Part 4, §6.4.6 and Part 6, §7.4.9 — Timing Requirements.

---

## Summary: Typical Gaps Found

1. **Signal without handler** → Add to SW Handler Catalog
2. **Handler without SWC** → Allocate to SWC in SW Architecture
3. **Handler without calling task** → Add RTOS task to RTOS Integration tab
4. **Safety signal without debounce** → Add Debounce Strategy row
5. **Debounce without N-of-M or time threshold** → Specify parameters
6. **Signal without fault propagation** → Add Fault Propagation Maps row
7. **Fault without vehicle reaction** → Specify reaction (e.g., "Trigger error handler, report DTC, limp home")
8. **Handler without max execution time** → Analyze WCET, add budget
9. **No RTOS Integration tab** → Document tasks and signal assignments
10. **No Test Cases** → Create test matrix (nominal, fault, boundary, timing)
11. **No Init Sequence** → Document HW BIST and SW startup coordination
12. **Missing Title, Author, Approver, Revision** → Complete Title page metadata
