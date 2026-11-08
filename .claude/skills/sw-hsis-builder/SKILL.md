---
name: sw-hsis-builder
description: Generate a contract-grade ISO 26262-6 Software-side Hardware-Software Interface Specification workbook from an HSI xlsx plus refinement JSON. Per ISO 26262-6 Section 7 and alignment with ISO 26262-4 Section 6.4.6, formalizes SW-side handler contracts with debouncing strategies, fault propagation, RTOS integration, and C header definitions. Includes 11-tab workbook, handler catalog, timing budgets, test cases, and standalone .h file. Use this skill whenever the user mentions software-side HSI, handler implementation, debouncing, fault propagation, RTOS task allocation, or needs to formally specify how SW processes signals from the HW-SW boundary. Always use this skill instead of producing a freeform SW-side HSI in chat.
---

# SW-HSI Builder

The Software-side Hardware-Software Interface (SW-HSI) is the **contract** between the HW-SW interface and the embedded software system. It specifies every signal handler: debouncing strategy, execution timing, RTOS task allocation, maximum latency budget, fault propagation to dependent SWCs, and test coverage. This skill automates the rote aspects of SW-HSI authoring—handler catalog generation, debounce parameter calculation, RTOS scheduling integration, and C header synthesis—leaving the analyst free to focus on the technical judgment that makes the implementation robust.

## When to use this skill

Use whenever the user wants to:
- Formalize handler functions for HSI signals from an HW-side HSI specification
- Define and justify debouncing strategies (N-of-M, time-based, hysteresis, leaky-bucket)
- Allocate signal handlers to specific software components (SWCs) and RTOS tasks
- Calculate execution time budgets and verify latency constraints
- Map fault detection to fault flag propagation through dependent SWCs
- Build the SW-side initialization protocol (register reads, self-test calls, watchdog startup)
- Generate C function declarations for embedded SW integration
- Ensure test coverage for nominal operation, fault injection, boundary conditions, and timing edge cases
- Document RTOS task scheduling and signal handler invocation frequency
- Coordinate with HW-side HSI and SW architecture specifications

Pre-requisite: An HSI workbook produced by hsi-builder with the 02_HSI_Signal_Catalog, 04_Timing_Specification, and 05_Failure_Modes_and_Reactions tabs. Optionally: a SW architecture xlsx specifying SWCs and RTOS tasks. If the user does not have an HSI, redirect them to hsi-builder first.

## Workflow

### Step 1 — Confirm the HSI and SW architecture inputs

Ask the user for the path to their HSI xlsx (HW-side) and optionally their SW architecture xlsx. The skill reads the HSI for signal definitions, timing constraints, and failure modes. The SW arch (if provided) constrains which SWCs and tasks are available for handler allocation.

### Step 2 — Handler allocation and debounce interview

The HSI specifies signals and timing budgets. The SW-HSI adds the next level of detail: which **SWC and RTOS task** process each signal, what **debounce method** protects against noise, the **maximum execution time** allowed per handler, and **fault propagation paths** to dependent SWCs.

For each major signal group (e.g., esc.diag.*, esc.live.*):
- Software component (SWC) responsible for handler (e.g., SWC04 = Safety Monitor).
- RTOS task that calls the handler and its period (e.g., T02 = Diag_50ms, period 50 ms).
- Debounce method: N-of-M filter (e.g., 3-of-5), time-based persistence, hysteresis, or leaky-bucket.
- Debounce parameters (N, M, time threshold, hysteresis band).
- Maximum execution time budget (us) and actual worst-case time (us).
- Fault propagation: from handler detection → fault flag set → which dependent SWCs read the flag → vehicle reaction (e.g., Request Limp Home).

Capture into a JSON file matching examples/sample_sw_hsis_refinement_esc.json. The most consequential fields are SWC allocation, RTOS task, debounce method, and max_exec_us.

### Step 3 — Read the references on first use

Before generating, read whichever of these are relevant:
- references/methodology.md — What the SW-HSI captures; the 11-tab structure; debouncing rationale; fault propagation chains; RTOS scheduling. Always read on first invocation.
- references/debouncing_patterns.md — Detailed comparison of N-of-M filter, time-based, hysteresis, and leaky-bucket; when to use each; false-positive risk; parameter selection.

### Step 4 — Generate

```bash
python scripts/generate_sw_hsis.py <hsi.xlsx> <refinement.json> <output.xlsx>
```

The generator produces:
- 11-tab SW-HSI workbook (output.xlsx) with signal handler catalog, debounce strategies, RTOS integration, fault propagation chains, initialization sequence, and test cases.
- C header file (<output>_sw_handlers.h) with auto-generated handler function declarations.

### Step 5 — Walk the user through the review

Review checkpoints in order:

1. **00_Title_Page** — confirm project ID, linked HSI, and linked SW architecture.
2. **01_Document_Control** — confirm revision tracking setup.
3. **02_HSI_Signal_Catalog_Echo** — read-only echo from HW-side HSI; one row per signal: name, direction (HW->SW or SW->HW), encoding, ASIL.
4. **03_SW_Handler_Catalog** — the single source of truth for SW side. Per signal: handler function name, allocated SWC, calling RTOS task, call frequency (every tick / event-driven / on-demand), max execution time budget (us), return type (e.g., fault_status_t).
5. **04_Debounce_Strategy_per_Signal** — per safety signal: debounce method (N-of-M / persistence-time / hysteresis / leaky-bucket), parameters, rationale, false-positive risk percentage, validation approach.
6. **05_Fault_Propagation_Maps** — per signal fault: detection point (which handler) → fault flag set → propagation path through dependent SWCs → vehicle reaction (e.g., Request Limp Home). Text-based chain.
7. **06_RTOS_Integration** — per signal: which RTOS task processes this signal, task period (ms), task priority, latency from signal arrival to handler execution (ms), jitter budget (ms).
8. **07_Init_Sequence_SW_Side** — SW startup sequence: phase, SWCs activated, HSI register reads (init values), self-test handler calls, fault behavior on init failure. Coordinate with HW-side init from hsi-builder.
9. **08_Test_Cases** — per signal handler: nominal operation test, fault injection test, boundary/edge test, timing edge case test (worst-case latency, jitter), integration test with dependent SWCs.
10. **09_C_Header_Stub** — generated C header preview with handler function declarations (read-only); full .h file on disk.
11. **10_References** — linked HSI (HW-side), SW architecture, ISO 26262-6, RTOS documentation.

When the user requests changes, edit the refinement JSON and regenerate. The xlsx is a derived artefact; the HSI + refinement JSON are the source of truth.

## Output structure (11 tabs + .h file)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | SW-HSI doc ID, project, linked HSI and SW arch, methodology |
| 01 | Document Control | Revision history |
| 02 | HSI Signal Catalog Echo | Read-only echo of signals from HW-side HSI (name, direction, encoding, ASIL) |
| 03 | SW Handler Catalog | Per signal: handler function name, allocated SWC, calling RTOS task, frequency, max execution time, return type |
| 04 | Debounce Strategy | Per signal: method (N-of-M / time / hysteresis / leaky-bucket), parameters, rationale, false-positive risk |
| 05 | Fault Propagation Maps | Per signal fault: detection → flag set → SWC propagation → reaction chain |
| 06 | RTOS Integration | Per signal: RTOS task, period, priority, latency (ms), jitter budget |
| 07 | Init Sequence SW Side | SW startup: phase, SWCs activated, register reads, self-test calls, fault behavior |
| 08 | Test Cases | Per handler: nominal, fault injection, boundary, timing edge case, integration |
| 09 | C Header Stub | Auto-generated C header preview (full .h file on disk) |
| 10 | References | Linked HSI, SW arch, ISO 26262-6, RTOS docs |

Plus: <output_basename>_sw_handlers.h — C function declarations ready for SW compilation.

## Common pitfalls to flag

1. **Debounce method chosen without false-positive risk analysis.** Default debounce method is N-of-M. Each method has different latency and false-positive trade-offs. Validate against false-positive percentage budget and FTTI.
2. **RTOS task allocation not validated against timing budget.** If a signal handler is allocated to a task with period 50 ms, but FTTI is 10 ms, the handler cannot meet the deadline. Cross-check all allocations.
3. **Fault propagation chain not traced to vehicle reaction.** A fault detected in one SWC must propagate through dependent SWCs and trigger a vehicle-level reaction (e.g., Limp Home). Incomplete chains leave gaps in safety coverage.
4. **Initialization sequence does not coordinate with HW-side.** SW startup reads HSI registers; HW must have locked them after init. Document the hand-shake protocol and timing.
5. **Test cases incomplete for edge conditions.** Every debounce method has edge cases: time-based needs maximum jitter test, N-of-M needs boundary (N-1 and N+1), hysteresis needs oscillation test. Test planning is critical.

## Files in this skill

```
sw-hsis-builder/
├── SKILL.md
├── scripts/
│   ├── hsi_reader.py                        # extracts HSI signal catalog from hsi-builder xlsx
│   ├── generate_sw_hsis.py                  # main generator (HSI xlsx + refinement JSON -> SW-HSI xlsx + .h)
│   ├── recalc.py                            # (inherited from tsc-builder)
│   └── office/soffice.py                    # (inherited from tsc-builder)
├── references/
│   ├── methodology.md                       # what the SW-HSI captures; 11-tab structure; debouncing; fault propagation
│   └── debouncing_patterns.md               # N-of-M, time-based, hysteresis, leaky-bucket comparison
└── examples/
    └── sample_sw_hsis_refinement_esc.json   # ESC SW-HSI refinement to clone
```
