---
name: sw-arch-builder
description: Generate an audit-ready ISO 26262-6 Section 7 software architecture workbook from a TSC xlsx (system-level architecture) and a SW architecture JSON (component decomposition, task scheduling, partitioning). Produces 12-tab xlsx with SW component catalog, RTOS configuration, task scheduling, memory partitioning, inter-component interfaces, safety mechanism allocation, MISRA compliance targets, and initialization sequence. Essential for bridging TSC (system safety requirements) into concrete SW design rules testable in implementation. Use whenever the user mentions SW architecture, software design, task scheduling, memory partitioning, component decomposition, or safety mechanisms in an automotive safety context. Always use this skill instead of producing freeform SW architecture in chat.
---

# SW Architecture Builder

The Software Architecture (ISO 26262-6 Section 7) refines the system-level Technical Safety Concept (TSC) into concrete software components, real-time tasks, memory partitions, and inter-component interfaces. This skill automates the rote parts of SW architecture authoring — component catalog generation, task scheduling analysis, partition isolation definition, interface documentation, safety mechanism mapping, and MISRA compliance tracking — leaving the analyst free to focus on design trade-offs and safety analysis detail.

## When to use this skill

Use whenever the user wants to:
- Refine TSC architecture into detailed SW components (SWCs)
- Define real-time task scheduling and allocation
- Plan memory partitioning and fault isolation
- Document inter-component interfaces and data contracts
- Map safety mechanisms to concrete SWCs
- Set MISRA C:2012 compliance targets per component
- Plan software initialization sequence
- Hand off to SW implementation and verification teams

Pre-requisite: a TSC workbook produced by `tsc-builder`. If the user does not have one, redirect them to `tsc-builder` first.

## Workflow

### Step 1 — Confirm the TSC input

Ask the user for the path to their TSC xlsx. The skill reads:
- `02_FSRs_From_FSC` — FSRs with allocated ASIL for traceability
- `03_System_Architecture` — SW partitions from system decomposition
- `04_Safety_Mechanism_Catalog` — safety mechanisms chosen at system level
- `05_TSR_Catalog` — SW-TSR text and allocation to mechanisms

### Step 2 — SW architecture interview

The TSC identifies logical SW partitions and safety mechanisms. The SW Architecture needs the next level: which concrete SW components (SWCs) implement each partition, what real-time tasks schedule them, how memory is isolated, and what interfaces connect them.

Walk the user through:

For each Software Component (SWC):
- `id` (SWC01, SWC02, …), `name`, `type` (Application / Service / Driver / Diagnostic), `language` (C / C++ / AUTOSAR), `partition` (which TSC partition houses it), `asil` (allocated from FSR or SW-TSR), `misra_scope` (Required / Advisory / Mandatory), `mechanisms` (which safety mechanisms it implements).

For each real-time Task:
- `id` (T01, T02, …), `name`, `period` (ms), `priority`, `wcet` (worst-case execution time, ms), `swcs` (which SWCs execute in this task), `deadline` (typically equals period).

For each Memory Region (MPU / virtual memory):
- `region_id`, `base_addr`, `size`, `access` (R / W / RW / RX), `partition` or `swc` (which partition/component), `fault_behavior` (fault handler, reset, state machine).

For each Inter-Component Interface:
- `from_swc`, `to_swc`, `name`, `type` (data / event / RTE port / CAN / SPI), `payload`, `integrity_protection` (CRC / E2E / observer), `synchronous` (yes/no), `error_handling`.

Capture into a JSON file matching `examples/sample_sw_arch_input_esc.json`. The most consequential fields are `swcs` (component decomposition), `tasks` (scheduling), `mpu_regions` (isolation), and `interfaces` (data contracts).

### Step 3 — Read the references on first use

Before generating, read whichever of these are relevant:
- `references/methodology.md` — what SW architecture refinement entails and the role of component decomposition, task scheduling, memory isolation, and safety mechanisms. **Always read on first invocation.**
- `references/iso26262_part6_clause7_mapping.md` — tab-to-clause mapping and requirements per ASIL.

### Step 4 — Generate

```bash
python scripts/generate_sw_architecture.py <tsc.xlsx> <sw_arch.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The generator produces the xlsx with all 12 tabs pre-populated. Tab 02 is a read-only echo of the TSC's architecture; tabs 03–11 refine it into component catalogs, scheduling maps, partition plans, interface specifications, mechanism allocations, and MISRA targets.

### Step 5 — Walk the user through the review

Review checkpoints in order:

1. **`00_Title_Page`** — confirm project, doc ID, revision, linked TSC.
2. **`01_Document_Control`** — track revision history.
3. **`02_TSC_Architecture_Echo`** — confirm the imported TSC partitions and FSRs match expectations.
4. **`03_SW_Component_Catalog`** — one row per SWC. Verify names, types, partition assignments, ASIL allocations, and MISRA scope.
5. **`04_RTOS_OS_Configuration`** — OS name, version, scheduling policy, tick rate, MPU support. Confirm OS ASIL and interrupt latency budget.
6. **`05_Task_Scheduling_Map`** — verify task periods, priorities, WCETs, allocations. Check rate-monotonic feasibility for preemptive schedules.
7. **`06_MPU_Memory_Partitioning`** — review memory regions, base addresses, sizes, access rights, fault behavior. Verify ASIL isolation (no mixing).
8. **`07_Inter_Component_Interfaces`** — check all message contracts: from/to SWCs, payload, integrity protection, synchronous/async, error handling.
9. **`08_Safety_Mechanism_Allocation`** — for each SWC, verify which safety mechanisms apply and which TSRs they implement.
10. **`09_MISRA_Compliance_Targets`** — confirm compliance tool, target violation counts (Required = 0, Advisory = policy-dependent), deviation process.
11. **`10_Initialization_Sequence`** — review boot phases, BIST coverage, SWC activation order, fault behaviors.
12. **`11_References`** — TSC file path, MISRA spec, AUTOSAR docs, project FSC/FSR references.

When the user requests changes, edit the input JSON and regenerate. The xlsx is a derived artifact; the TSC + SW architecture JSON are the source of truth.

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | SW Architecture doc ID, project, dates, linked TSC |
| 01 | Document Control | Revision history |
| 02 | TSC Architecture Echo | Read-only echo of TSC's SW partitions and FSRs |
| 03 | SW Component Catalog | Concrete SWCs: ID, name, type, language, partition, ASIL, MISRA scope |
| 04 | RTOS OS Configuration | OS name, version, scheduling policy, tick rate, MPU, ASIL, interrupt latency |
| 05 | Task Scheduling Map | Tasks: ID, name, period, priority, WCET, allocated SWCs, deadline, rate-monotonic check |
| 06 | MPU Memory Partitioning | Memory regions: ID, base addr, size, access, partition, ASIL isolation, fault behavior |
| 07 | Inter Component Interfaces | From/To SWCs, interface name, type, payload, integrity protection, synchronous, error handling |
| 08 | Safety Mechanism Allocation | Per SWC: allocated mechanisms, mechanism IDs, allocated TSRs, ASIL, notes |
| 09 | MISRA Compliance Targets | Per SWC: MISRA scope, Required/Advisory violation targets, tool, deviation process |
| 10 | Initialization Sequence | Boot phases: duration, SWCs activated, BIST run, fault behavior, next phase |
| 11 | References | TSC, FSC, MISRA spec, AUTOSAR, tool documentation |

## Common pitfalls to flag

1. **Missing task-to-SWC allocation.** Every SWC must execute in at least one task. Orphan SWCs will not run.
2. **Unverified task scheduling.** Rate-monotonic analysis must show Σ(WCET_i / Period_i) ≤ 0.693 for preemptive priority-based schedules. Ignore this at your peril; latency violations cause safety mechanism failures.
3. **Partition isolation without explicit error handling.** MPU fault on illegal access must invoke a documented handler. Vague "halt" or "reset" is not acceptable for ASIL D.
4. **Interface contracts without error cases.** Every interface must document: what happens on timeout, data stale, CRC mismatch, out-of-range. "Error handler" is not a specification.
5. **MISRA deviations not traced to FMEA.** Every deviation (unchecked cast, pointer arithmetic, global variable) must appear in the system FMEA with failure mode consequence analysis.
6. **Mechanism allocation without confidence analysis.** Simply listing a mechanism (e.g., "watchdog refresh") does not prove it will catch the fault. Reference the TSC mechanism DC (diagnostic coverage) and FMEA detection analysis.

## Files in this skill

```
sw-arch-builder/
├── SKILL.md
├── scripts/
│   ├── tsc_reader.py                           # extracts TSC architecture context
│   ├── generate_sw_architecture.py              # main generator
│   ├── recalc.py
│   └── office/soffice.py
├── references/
│   ├── methodology.md                           # SW architecture refinement overview
│   └── iso26262_part6_clause7_mapping.md        # tab-to-clause mapping
└── examples/
    └── sample_sw_arch_input_esc.json            # ESC SW architecture input to clone
```
