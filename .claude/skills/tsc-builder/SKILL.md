---
name: tsc-builder
description: Generate an audit-ready ISO 26262 Technical Safety Concept (TSC) workbook by reading an FSC xlsx (produced by fsc-builder) plus a system architecture refinement JSON. Per FSR, proposes safety mechanisms from a curated catalog (lockstep, ECC, plausibility, watchdog, feedback, E2E), drafts paired HW-TSR and SW-TSR, pre-populates the HW-SW interface signals, splits FTTI into FDTI and FRTI budgets, scaffolds the system-level FMEA, generates DFA rows for every decomposition pair against the standard coupling factors, computes verification rigor by allocated ASIL, and emits HW and SW hand-off summaries. Also exports the system architecture as an editable draw.io file. Use this skill whenever the user mentions TSC, technical safety concept, TSR derivation, HSI, safety mechanism allocation, system FMEA, DFA, or FTTI budgets, even casual phrasings like 'now do the TSC'. Always use this skill instead of producing a freeform TSC in chat.
---

# TSC Builder

The Technical Safety Concept (TSC) is the bridge between the Functional Safety Concept (FSC) and the HW (ISO 26262-5) and SW (ISO 26262-6) work. It refines each FSR into HW-TSRs and SW-TSRs that are concrete enough to drive FMEDA, MISRA-compliant code, and HIL/SIL test plans. This skill mechanises the rote parts of TSC authoring — mechanism proposal, TSR drafting, HSI signal scaffolding, FMEA enumeration, DFA checklist generation, verification mapping — leaving the analyst free to focus on the project-specific judgment that actually moves the design forward.

## When to use this skill

Use whenever the user wants to:
- Refine FSRs into HW and SW Technical Safety Requirements
- Allocate safety mechanisms to architectural elements
- Define the HW-SW interface for diagnostics and liveness
- Build the timing budget (FTTI = FDTI + FRTI) per safety requirement
- Scaffold a system-level FMEA
- Run DFA against an ASIL decomposition claim
- Hand off to HW (Part 5) or SW (Part 6) teams with traceability intact

Pre-requisite: an FSC workbook produced by `fsc-builder`. If the user does not have one, redirect them to `fsc-builder` first.

## Workflow

### Step 1 — Confirm the FSC input

Ask the user for the path to their FSC xlsx. The skill reads:
- `02_FSRs_From_FSC equivalent` (FSC's `05_FSR_Catalog`) — the FSRs to be refined
- `06_ASIL_Allocation` — to know each FSR's *allocated* (post-decomposition) ASIL
- `03_System_Block_Diagram` — to know the node taxonomy for FMEA scaffolding

### Step 2 — Architecture refinement interview

The FSC's block diagram captures conceptual nodes (sensors, processors, actuators). The TSC needs the next level of refinement: which **HW components** (PCBs, ICs, sensor modules) host those nodes, and which **SW partitions** (AUTOSAR SWCs, RTOS tasks, bare-metal modules) host the SW nodes. Walk the user through:

For each HW component:
- `id` (HW01, HW02, …), `name`, `part / vendor`, `allocated_nodes` (list of FSC node IDs hosted on this component), `power_domain`, `clock_domain`, `notes`.

For each SW partition:
- `id` (SP01, SP02, …), `name`, `hosted_on` (HW component ID), `allocated_nodes`, `rtos / OS`, `asil` (developed-to ASIL), `notes`.

Capture into a JSON file matching `examples/sample_architecture_esc.json`. The most consequential field is `allocated_nodes` — without it, downstream tabs cannot trace TSRs back to architectural elements.

### Step 3 — Read the references on first use

Before generating, read whichever of these are relevant:
- `references/safety_mechanism_catalog.md` — the catalog of mechanisms by branch and node type, with default DC% targets. **Always read on first invocation.**
- `references/hsi_specification.md` — what the HSI captures and the signal naming convention.
- `references/timing_budget.md` — FTTI = FDTI + FRTI math and allocation defaults.
- `references/system_fmea_method.md` — the failure-mode taxonomy and FTA cross-check.
- `references/dfa_method.md` — the ISO 26262-9 §7 coupling factor checklist.

### Step 4 — Generate

```bash
python scripts/generate_tsc.py <fsc.xlsx> <architecture.json> <tsc_output.xlsx>
python scripts/recalc.py <tsc_output.xlsx>
```

The generator produces the xlsx and an editable draw.io file alongside it (same basename, `.drawio` extension). Open the .drawio file in [draw.io desktop or web](https://app.diagrams.net) to refine the visual layout; export to PNG when polished and embed back into the xlsx via Excel's Insert → Picture (manual step — automatic round-trip requires the draw.io desktop CLI which needs a display).

### Step 5 — Walk the user through the review

Review checkpoints in order:

1. **`02_FSRs_From_FSC`** — confirm the imported FSRs match the FSC. If not, the FSC needs updating, not this workbook.
2. **`03_System_Architecture`** — confirm the HW components, SW partitions, and their `allocated_nodes` mappings.
3. **`04_Safety_Mechanism_Catalog`** — for each FSR, the skill proposes 1–3 candidate mechanisms; the first is marked `[primary]`. The analyst either accepts the primary or selects an alternative, then deletes the unchosen rows.
4. **`05_TSR_Catalog`** — review the generated HW-TSR and SW-TSR text. The wording is template-based; refine for project specifics (DC% targets, bus names, signal IDs).
5. **`06_HSI_Specification`** — every chosen mechanism produced one HW→SW diagnostic signal and one SW→HW liveness signal. Refine signal names per OEM convention; fill in detection/update timing.
6. **`07_Timing_Budget`** — review the 50/50 FDTI/FRTI default split. Tighten FDTI when the mechanism's own latency demands it; tighten FRTI when actuator response is slow.
7. **`08_System_FMEA`** — one row per (architecture node × failure-mode taxonomy). The analyst fills the Local/Subsystem/Vehicle Effect columns and the DC% from the FMEDA. Cross-check against the FSC's FTA — every Vehicle Effect classified as a hazard MUST appear as a basic event in the FTA, and vice versa.
8. **`09_DFA`** — for every decomposition pair, the skill creates rows against 12 coupling factors. The analyst marks each "No" or "Yes — mitigated by …" or "Yes — UNMITIGATED". Any unmitigated coupling invalidates the decomposition; the corresponding FSC row must revert to full inheritance.
9. **`10_Verification`** — methods recommended (++) per allocated ASIL. Confirmation review independence is auto-suggested by ASIL.
10. **`11_HW_Handoff`** / **`12_SW_Handoff`** — gate-ready summaries to hand to the HW and SW teams.

When the user requests changes, edit the architecture JSON and regenerate. The xlsx is a derived artefact; the FSC + architecture JSON are the source of truth.

## Output structure (12 tabs + draw.io file)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | TSC doc ID, project, dates, methodology statement |
| 01 | Document Control | Revision history |
| 02 | FSRs From FSC | Read-only echo with traceability |
| 03 | System Architecture | HW components + SW partitions with allocated_nodes |
| 04 | Safety Mechanism Catalog | 1–3 mechanism candidates per FSR; primary + alternatives |
| 05 | TSR Catalog | HW-TSR + SW-TSR per chosen mechanism |
| 06 | HSI Specification | Diagnostic + liveness signals per mechanism |
| 07 | Timing Budget | FTTI / FDTI / FRTI per FSR |
| 08 | System FMEA | (node × failure mode) scaffolded from taxonomy |
| 09 | DFA | (decomposition pair × coupling factor) scaffolded checklist |
| 10 | Verification | Recommended methods + confirmation review independence by allocated ASIL |
| 11 | HW Handoff | HW-TSR summary for ISO 26262-5 hand-off |
| 12 | SW Handoff | SW-TSR summary for ISO 26262-6 hand-off |

Plus: `<output_basename>.drawio` — editable architecture diagram opened in draw.io.

## Common pitfalls to flag

1. **Mechanism + reaction not paired.** Detection alone is not a safety mechanism. The TSC pairs every mechanism with the standard `Transition to safe state` reaction (SM30) by default; document any deviation.
2. **DC% claims without FMEDA evidence.** Default DC% in the catalog is order-of-magnitude. Each chosen mechanism needs an FMEDA-derived number before the safety case can cite it.
3. **HSI signals defined too late.** The HSI is the contract between HW and SW. Defining it during integration leads to expensive rework. The skill drafts it at TSC time so both teams start with the same picture.
4. **DFA treated as documentation.** DFA is a verification activity — every "No" answer needs an analytical or test argument behind it, not a hand-wave.
5. **Timing budget that ignores actuator response.** FRTI is end-to-end SW + actuator. If the actuator takes 80 ms to release, FRTI cannot be 30 ms even if the SW transitions in 5 ms.

## Files in this skill

```
tsc-builder/
├── SKILL.md
├── scripts/
│   ├── generate_tsc.py                         # main generator (FSC xlsx + arch JSON → TSC xlsx + .drawio)
│   ├── recalc.py
│   └── office/soffice.py
├── references/
│   ├── safety_mechanism_catalog.md
│   ├── hsi_specification.md
│   ├── timing_budget.md
│   ├── system_fmea_method.md
│   └── dfa_method.md
└── examples/
    └── sample_architecture_esc.json            # ESC architecture refinement to clone
```
