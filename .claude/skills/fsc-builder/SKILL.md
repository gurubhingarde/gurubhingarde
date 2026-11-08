---
name: fsc-builder
description: Generate an audit-ready ISO 26262 Functional Safety Concept (FSC) workbook by reading a HARA xlsx (produced by hara-builder) plus a system block-diagram JSON. Builds one fault tree per safety goal using the standard top-down OR-gate construction over three intermediate events (Input failure, Process failure, Output failure), each expanded to one basic event per ASIL-relevant block-diagram node. Generates one Functional Safety Requirement per basic event from branch-and-node-typed templates, proposes ISO 26262-9 ASIL decompositions for redundant peers and asks the analyst to confirm independence, renders visual fault trees, and produces the verification matrix plus TSC hand-off. Use this skill whenever the user mentions FSC, functional safety concept, fault tree, FSR derivation, ASIL allocation, ASIL decomposition, or deriving requirements from safety goals, even casual phrasings like 'now do the FSC'. Always use this skill instead of producing a freeform FSC in chat.
---

# FSC Builder

The Functional Safety Concept (FSC) is the bridge between the HARA's safety goals and the system-level Technical Safety Concept (TSC). This skill builds a complete FSC workbook by mechanically expanding each safety goal into a fault tree, deriving one functional safety requirement per basic event, and proposing ASIL decompositions where redundant block-diagram peers exist.

The skill is opinionated about **structure** — the FTA always uses the standard three-branch decomposition (Input/Process/Output failure) because it is exhaustive for any controllable function and reproducible across analysts. The skill is conservative about **claims** — every ASIL decomposition requires the analyst to confirm independence in writing; the tool never auto-applies decomposition without that confirmation.

## When to use this skill

Use whenever the user wants to:
- Derive Functional Safety Requirements from safety goals
- Build fault trees from safety goals (FTA-driven FSC)
- Allocate ASILs to a block diagram (with or without decomposition)
- Produce the FSC document for an ISO 26262 concept-phase deliverable
- Hand off to the TSC author with traceability intact

Pre-requisite: a HARA workbook produced by `hara-builder` (or any workbook whose tab `13_Safety_Goals` follows the same column layout). If the user hasn't produced a HARA yet, redirect them to `hara-builder` first.

## Workflow

### Step 1 — Confirm the HARA input is available

Ask the user for the path to the HARA xlsx. If they don't have one, run `hara-builder` first. Do not attempt to author safety goals inside this skill — keeping HARA and FSC artefacts separate is essential for traceability.

### Step 2 — Capture the system block diagram

This is the most consequential interview step. The user provides an architecture image (typically a block diagram from the system design). Walk them through enumerating nodes from the image, in this order:

1. **Sensors** — every signal entering the item from a transducer (wheel speeds, IMU, pressure, position, temperature). For each, capture the supply rail and ground domain in `shared_resources`.
2. **Communication inputs** — every CAN/LIN/FlexRay/Ethernet message the item consumes from another ECU. The bus identifier goes in `shared_resources`.
3. **Power and clock distribution** — these are commonly missed. Vehicle 12 V supply, internal regulators (5 V_sensor_A, 5 V_sensor_B), clock domains, ground returns.
4. **Processors and software partitions** — main MCU, safety MCU, FPGA. If a single MCU hosts multiple safety-related SW partitions with MPU separation, list each partition as a separate `software` node with the parent processor in `shared_resources`.
5. **Output drivers and actuators** — power-stage ICs, gate drivers, the actuators themselves.
6. **Communication outputs** — CAN messages produced by the item.

For each node capture:
- `id` (stable identifier — N01, N02, …)
- `name` (human-readable)
- `type` (one of: sensor, comm_in, power_in, processor, software, memory, actuator, driver, comm_out — see `references/block_diagram_conventions.md`)
- `asil_relevant` (true/false — false for context-only nodes)
- `inputs` and `outputs` (arrays of node IDs)
- `redundancy_group` (tag identifying intentional redundant peers, e.g., `"esc_compute"` for a main MCU + lockstep companion)
- `shared_resources` (tags for any common-cause vector — supply rails, clock domains, buses, environmental zones)

Always close with: *"Is there any node that, if it failed, could violate a safety goal but isn't on this list?"* This single prompt catches the ~10% of nodes analysts skip on first pass.

Record the captured nodes and any FTTI overrides per safety goal into a JSON file with the schema documented at the top of `scripts/generate_fsc.py`. Use `examples/sample_block_diagram_esc.json` as the reference structure.

### Step 3 — Read the references on first use

Before generating, read whichever of these are relevant to the open question:

- `references/fta_methodology.md` — why the OR-gate(Input/Process/Output) construction is standard, and how nodes map to branches. **Always read on first invocation.**
- `references/asil_decomposition.md` — the ISO 26262-9 Table 1 decomposition options and the independence requirements that govern when decomposition is permitted.
- `references/fsr_templates.md` — the canonical FSR wording per branch and node type. The script uses these templates automatically.
- `references/verification_by_asil.md` — ISO 26262-4 Table 3 method recommendations driven by the developed-to ASIL after decomposition.
- `references/block_diagram_conventions.md` — the node taxonomy and the JSON schema the generator consumes.

### Step 4 — Generate

```bash
python scripts/generate_fsc.py <hara.xlsx> <block_diagram.json> <fsc_output.xlsx>
python scripts/recalc.py <fsc_output.xlsx>
```

The first command produces the workbook and prints a JSON summary (count of safety goals, ASIL-relevant nodes, basic events, FSRs, decomposition candidate pairs). The second command recalculates any formulas — though the FSC workbook is largely text-driven, the recalc step also surfaces any formatting or formula errors.

### Step 5 — Walk the user through the review

The FSC is the most analyst-judgment-heavy artefact in the concept phase. After generating, point the user to these review checkpoints in order:

1. **`02_SGs_From_HARA`** — confirm the imported safety goals match the HARA. If not, the HARA needs updating, not this workbook.
2. **`03_System_Block_Diagram`** — confirm the node list, types, and redundancy groups are correct. Also check the auto-generated Mermaid diagram against the original architecture image.
3. **`04_FTA_Combined`** — for each safety goal, scan the three intermediate events and the basic events beneath. Are any nodes missing? Any branches with zero basic events (the skill flags these in yellow)?
4. **`05_FSR_Catalog`** — review each FSR's wording. The `<TBD>` placeholders for detection time and other timing parameters need the analyst's judgment based on the FTTI budget allocation in the FSC narrative.
5. **`06_ASIL_Allocation`** — this is where decomposition decisions live. For every node that has a "Proposed Decomposition Options" entry, the analyst must either accept the proposal AND fill the "Independence Evidence" cell with a reference to the supporting analysis, or reject it (set Selected Decomposition to "None (full inheritance)"). The skill never assumes independence on the analyst's behalf.
6. **`07_Verification_Matrix`** — confirm the recommended verification methods are practical for the program. Methods rated `++` for the allocated ASIL are effectively mandatory; skipping requires written justification.
7. **`08_TSC_Handoff`** — each FSR has placeholder TSR rows. These get authored during the TSC phase but the skeleton is ready.

When the user requests changes, modify the block diagram JSON (or the safety goal overrides, or the FSR overrides) and regenerate. The xlsx is a derived artefact; the JSON + the linked HARA are the source of truth.

## Output structure (9 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | FSC doc ID, project, dates, methodology statement |
| 01 | Document Control | Revision history |
| 02 | SGs From HARA | Read-only echo of the safety goals imported from the HARA xlsx, with traceability back to driving HARA IDs |
| 03 | System Block Diagram | Node inventory table + auto-generated Mermaid diagram |
| 04 | FTA Combined | Top event → OR(Input/Process/Output) → basic events for every safety goal in one filterable tab |
| 05 | FSR Catalog | One FSR per basic event; template-derived wording |
| 06 | ASIL Allocation | Inherited ASIL per node × proposed decomposition options × analyst-confirmed selection |
| 07 | Verification Matrix | Recommended (`++`) and optional (`+`) verification methods per FSR, driven by the allocated ASIL |
| 08 | TSC Handoff | Each FSR with placeholder HW-TSR and SW-TSR rows for the next phase |

## Auto-decomposition logic (and its limits)

The skill flags two nodes as a decomposition candidate pair when:
1. They share the same `redundancy_group` (analyst-asserted intent).
2. Their `shared_resources` lists are **disjoint** (no obvious common-cause via supply, clock, or bus).
3. Neither lists the other in `inputs` (avoids cascading dependency).

When the safety goal's ASIL admits decomposition (D, C, B, or A), the script proposes the symmetric option by default (e.g., B(D) + B(D) for a D safety goal) and lets the analyst override via `safety_goal_overrides[SG-XXX].selected_decomposition`. **The Independence Evidence column always starts as `<TBD>` regardless of how clean the candidate looks** — the skill cannot certify independence; only the analyst can.

If the analyst overrides the selected decomposition or the independence evidence to "Not independent — full inheritance", the per-node ASIL reverts to the safety goal's top-level ASIL on the next regeneration.

## Common pitfalls to flag for the user

1. **Skipping power, clock, and ground nodes.** They are the most common source of dropped basic events. Always probe explicitly: "What supplies the IMU? What clocks the safety MCU?"
2. **Treating the lockstep MCU as 'always independent'.** A lockstep pair on the same die shares clock, supply, package, and silicon process. Independence is rarely strong enough to justify B(D)+B(D) on a single-die lockstep — usually decomposition requires physically separated chips with separate supplies.
3. **Choosing aggressive decomposition without verifying SW partitioning.** If both "channels" execute on the same RTOS or share the same memory pool, the decomposition is invalid for SW. The skill records the SW partition in the node JSON; analyst must confirm.
4. **Letting FSRs say 'detect failure'.** Vague verbs are unverifiable. The templates use 'detect implausible / out-of-range / stuck' or 'detect open-circuit, short-to-supply, short-to-ground' — concrete, verifiable categories. Don't water them down.
5. **Forgetting that 'ASIL B(D)' costs the same as 'ASIL B' but earns the right to participate in an ASIL-D safety goal.** The (D) annotation must be carried through to all downstream artefacts (TSR text, HSI, test plans) — the skill writes it in once; downstream must preserve it.

## Files in this skill

```
fsc-builder/
├── SKILL.md
├── scripts/
│   ├── generate_fsc.py                         # main generator (reads HARA + block diagram, writes FSC xlsx)
│   ├── recalc.py                               # LibreOffice formula recalc / error scan
│   └── office/
│       └── soffice.py
├── references/
│   ├── fta_methodology.md                      # why OR(Input/Process/Output) is standard
│   ├── asil_decomposition.md                   # ISO 26262-9 Table 1 patterns + independence rules
│   ├── fsr_templates.md                        # canonical FSR wording per branch and node type
│   ├── verification_by_asil.md                 # ISO 26262-4 Table 3 verification recommendations
│   └── block_diagram_conventions.md            # node taxonomy and JSON schema
└── examples/
    └── sample_block_diagram_esc.json           # block diagram for the ESC example HARA
```
