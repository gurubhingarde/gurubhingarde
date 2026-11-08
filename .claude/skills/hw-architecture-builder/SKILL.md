---
name: hw-architecture-builder
description: Generate an audit-ready ISO 26262-5 §7 hardware architecture workbook from a TSC xlsx (system-level architecture) and a HW BOM JSON (detailed IC and PCB refinement). Produces 12-tab xlsx with board designs, HW element catalog, safety mechanism allocation, power architecture, clock architecture, common-cause analysis, bill of materials, and cross-reference matrices. Essential for bridging TSC (system safety mechanisms) into concrete HW design rules and FIT budgets. Use whenever the user mentions HW architecture, hardware design, bill of materials, PCB design, hardware elements, component allocation, power distribution, or clock distribution in an automotive safety context. Always use this skill instead of producing freeform HW architecture in chat.
---

# HW Architecture Builder

The Hardware Architecture (ISO 26262-5 §7) refines the system-level Technical Safety Concept (TSC) into concrete hardware components, PCBs, ICs, and passive elements. This skill automates the rote parts of HW architecture authoring — bill-of-materials generation, FIT rate compilation, safety mechanism mapping to real silicon, power and clock distribution analysis, and common-cause failure identification — leaving the analyst free to focus on physical design trade-offs and failure analysis detail.

## When to use this skill

Use whenever the user wants to:
- Refine TSC architecture into a detailed bill of materials (BOM)
- Map safety mechanisms to specific IC part numbers and packages
- Allocate hardware safety requirements (HW-SR) to board-level elements
- Define power rails, regulators, monitoring, isolation, and fusing
- Plan clock sources, distribution, and redundancy
- Conduct common-cause failure analysis on redundant pairs
- Compile FIT budgets per component and per safety function
- Hand off to layout, FMEDA, and ISO 26262-5 verification teams

Pre-requisite: a TSC workbook produced by `tsc-builder`. If the user does not have one, redirect them to `tsc-builder` first.

## Workflow

### Step 1 — Confirm the TSC input

Ask the user for the path to their TSC xlsx. The skill reads:
- `02_FSRs_From_FSC` — FSRs with allocated ASIL for traceability
- `03_System_Architecture` — preliminary HW components and SW partitions
- `05_TSR_Catalog` — HW-TSR and SW-TSR text
- `04_Safety_Mechanism_Catalog` — chosen safety mechanisms

### Step 2 — HW refinement interview

The TSC block diagram captures logical HW components (main MCU, daughter cards, sensor modules). The HW Architecture needs the next level: which **concrete ICs and passive elements** implement each component, on which **PCBs**, with what **power and clock domains**, and what **baseline FIT rates**.

Walk the user through:

For each PCB:
- `id` (PCB01, PCB02, …), `name`, `layers`, `dimensions (mm)`, `key_area_allocations` (main region, daughter connector, isolated analog section).

For each HW element (one IC, one discrete, one connector, etc.):
- `id` (HW-E-001, HW-E-002, …), `name`, `type` (MCU / Sensor IC / Actuator IC / Power IC / Discrete / Connector / Passive), `supplier`, `part_number`, `package`, `pin_count`, `baseline_fit` (FIT; from IEC 62380 or datasheet), `safety_qualification` (AEC-Q100/Q101/Q200), `tsc_node_id` (link back to TSC node), `pcb_id`, `power_rail`, `clock_source`, `notes`.

For each power rail:
- `rail` (12V_main, 5V_sensor_A, 3.3V_logic, …), `voltage`, `regulator_type` (linear / switching / isolated), `monitor` (OV/UV thresholds), `isolation_from` (other rails), `fusing`, `notes`.

For each clock source:
- `source` (XTAL_50MHz_A, RC_internal, PLL_from_50MHz_A, …), `frequency`, `monitor` (watchdog / jitter limits), `redundancy` (none / independent backup), `notes`.

Capture into a JSON file matching `examples/sample_hw_arch_input_esc.json`. The most consequential fields are `tsc_node_id` (links HW elements to TSC nodes) and `power_rail`/`clock_source` (enables common-cause analysis).

### Step 3 — Read the references on first use

Before generating, read whichever of these are relevant:
- `references/methodology.md` — what HW architecture refinement entails and the role of FIT rates, common-cause analysis, and power/clock architecture. **Always read on first invocation.**
- `references/iso26262_part5_clause7_mapping.md` — tab-to-clause mapping and verification rigor per ASIL.

### Step 4 — Generate

```bash
python scripts/generate_hw_architecture.py <tsc.xlsx> <hw_arch.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The generator produces the xlsx with all 12 tabs pre-populated. Tab 02 is a read-only echo of the TSC's architecture; tabs 03–11 refine it into board designs, IC catalogs, safety mappings, power/clock plans, and FIT budgets.

### Step 5 — Walk the user through the review

Review checkpoints in order:

1. **`00_Title_Page`** — confirm project, doc ID, revision, linked TSC.
2. **`01_Document_Control`** — track revision history.
3. **`02_TSC_Architecture_Echo`** — confirm the imported TSC nodes and HW components match expectations.
4. **`03_PCB_Design`** — review board dimensions, layers, key area allocations for main and daughter PCBs.
5. **`04_HW_Element_Catalog`** — one row per concrete HW element (IC, passive, connector). Verify part numbers, packages, pin counts, and baseline FIT rates.
6. **`05_Safety_Mechanism_Allocation`** — for each HW element, which safety mechanisms apply (e.g., lockstep, ECC, BIST, monitor), which TSC mechanism they implement, and allocated ASIL.
7. **`06_HW_SR_Allocation_Matrix`** — cross-reference matrix: HW-SR rows x HW-E columns. Mark which HW-SR is implemented by which elements.
8. **`07_Power_Architecture`** — power rails (voltage, regulator type, monitoring), fusing, isolation between rails. Identify common-cause risks (shared supply, shared regulator).
9. **`08_Clock_Architecture`** — clock sources (XTAL, RC, PLL), distribution tree, monitoring, redundancy strategy.
10. **`09_Common_Cause_Analysis`** — per redundant pair (lockstep cores, dual sensors, etc.), document shared rail, shared package, shared PCB region, shared environmental zone. Mark unmitigated couplings for FMEDA follow-up.
11. **`10_Bill_of_Materials`** — summary BOM with total FIT contribution per element type and per safety function.
12. **`11_References`** — TSC file path, datasheets, IEC 62380 / supplier FIT rate sources, applicable standards.

When the user requests changes, edit the input JSON and regenerate. The xlsx is a derived artifact; the TSC + HW architecture JSON are the source of truth.

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | HW Architecture doc ID, project, dates, linked TSC |
| 01 | Document Control | Revision history |
| 02 | TSC Architecture Echo | Read-only echo of TSC's HW components + SW partitions |
| 03 | PCB Design | Boards (main PCB, daughter PCBs), layers, dimensions, key area allocations |
| 04 | HW Element Catalog | Concrete IC + passive elements: ID, name, type, supplier, part, package, pin count, FIT rate, qualification |
| 05 | Safety Mechanism Allocation | Per HW element: which safety mechanisms apply, reference to TSC mechanism, allocated ASIL |
| 06 | HW SR Allocation Matrix | Cross-reference: HW-SR_ID rows x HW-E_ID columns; marks implementation |
| 07 | Power Architecture | Power rails, regulators, OV/UV monitoring, fusing, isolation between domains |
| 08 | Clock Architecture | Clock sources (XTAL, RC, PLL), distribution, monitoring, redundancy |
| 09 | Common Cause Analysis | Per redundant pair: shared rail, package, PCB region, zone; unmitigated couplings |
| 10 | Bill of Materials | Summary BOM: element type, total FIT per type, total FIT per safety function |
| 11 | References | TSC, datasheets, FIT sources, applicable standards |

## Common pitfalls to flag

1. **FIT rate sourcing gaps.** Baseline FIT in the HW Element Catalog must cite IEC 62380 or supplier datasheet. Order-of-magnitude estimates are acceptable at TSC time; FMEDA will refine.
2. **No power/clock coupling analysis.** Many field failures are not the part itself but shared supply or clock faults. The Power and Clock tabs catch these early.
3. **Isolated but drifting redundancy.** Redundant channels (e.g., dual MCUs) can drift apart over time or share a silent fault until disturbed. Common-Cause Analysis must capture environmental zones, thermal regions, and testability limits.
4. **FIT aggregation without failure mode granularity.** The BOM tab sums FIT; the FMEDA will allocate that FIT to individual failure modes. Do not hide the granularity here.
5. **Missing qualification evidence.** AEC-Q100/Q200 certs add confidence; include part numbers in the HW Element Catalog and cite datasheets in the References tab.

## Files in this skill

```
hw-architecture-builder/
├── SKILL.md
├── scripts/
│   ├── tsc_reader.py                           # extracts TSC architecture
│   ├── generate_hw_architecture.py              # main generator
│   ├── recalc.py
│   └── office/soffice.py
├── references/
│   ├── methodology.md                           # HW architecture refinement overview
│   └── iso26262_part5_clause7_mapping.md        # tab-to-clause mapping
└── examples/
    └── sample_hw_arch_input_esc.json            # ESC HW BOM input to clone
```
