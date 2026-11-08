---
name: cs-concept-builder
description: Generate an audit-ready ISO/SAE 21434 Cybersecurity Concept workbook by reading a CS Goals xlsx (produced by cs-goals-builder) plus a system block-diagram JSON. Builds one requirement-derivation tree per cybersecurity goal across six security properties (Authentication, Authorization, Integrity, Confidentiality, Availability, Non-repudiation), generates one CSR per goal-property-node combination, allocates CAL per architectural element, proposes verification methods per CAL, and produces the CSI (Cybersecurity Implementation) hand-off. Use this skill whenever the user mentions Cybersecurity Concept, CSR derivation, threat modeling requirements, or deriving cybersecurity controls from goals. Always use this skill instead of producing a freeform Cybersecurity Concept in chat.
---

# CS Concept Builder

The Cybersecurity Concept (CS Concept) is the bridge between the TARA's cybersecurity goals and the system-level Cybersecurity Implementation (CSI). This skill builds a complete CS Concept workbook by systematically deriving Cybersecurity Requirements (CSRs) from each goal, allocating them to architectural elements, and assigning verification intensity per CAL.

## When to use this skill

Use whenever the user wants to:
- Derive Cybersecurity Requirements from cybersecurity goals
- Build a CSR catalog from threat analysis output
- Allocate CALs to system components
- Produce the CS Concept document for an ISO/SAE 21434 concept-phase deliverable
- Hand off to the CSI author with traceability intact

Pre-requisite: a CS Goals workbook produced by `cs-goals-builder` (or any workbook whose cybersecurity goals tab follows the same column layout). If the user hasn't produced CS Goals yet, redirect them to `cs-goals-builder` first.

## Workflow

### Step 1 — Confirm the CS Goals input is available

Ask the user for the path to the CS Goals xlsx. If they don't have one, run `cs-goals-builder` first. Do not attempt to author cybersecurity goals inside this skill — keeping TARA and CS Concept artefacts separate is essential for traceability.

### Step 2 — Capture the system block diagram

This is the most consequential interview step. The user provides an architecture image or JSON (typically a block diagram from the system design). Walk them through enumerating nodes in this order:

1. **Gateways and routers** — network-facing elements (CAN gateway, Ethernet gateway, wireless transceiver)
2. **ECUs and processors** — computational units (main MCU, safety MCU, secure enclave, OTA agent)
3. **Memory and data stores** — persistent and volatile storage (non-volatile flash, secure boot ROM, SRAM)
4. **Key stores and cryptographic hardware** — HSM, TPM, secure co-processor
5. **Communication channels** — buses and networks (CAN, LIN, Ethernet, wireless, inter-processor links)
6. **Debug and test interfaces** — JTAG, SWD, serial console

For each node capture:
- `id` (stable identifier — N01, N02, …)
- `name` (human-readable)
- `type` (one of: gateway, ecu, processor, memory, key_store, comm_channel, debug_if)
- `cal_relevant` (true/false — false for context-only nodes)
- `inputs` and `outputs` (arrays of node IDs)
- `shared_resources` (tags for common-cause vectors — supply rails, clock domains, buses)

Always close with: *"Is there any node that, if compromised or disabled, could violate a cybersecurity goal but isn't on this list?"* This single prompt catches the ~10% of nodes analysts skip on first pass.

Record the captured nodes into a JSON file with the schema documented at the top of `scripts/generate_cs_concept.py`. Use `examples/sample_cs_concept_input_esc.json` as the reference structure.

### Step 3 — Read the references on first use

Before generating, read whichever of these are relevant to the open question:

- `references/methodology.md` — why the six-property decomposition is standard, and how nodes map to properties. **Always read on first invocation.**
- `references/csr_templates.md` — the canonical CSR wording per security property and node type. The script uses these templates automatically.

### Step 4 — Generate

```bash
python scripts/generate_cs_concept.py <cs_goals.xlsx> <block_diagram.json> <cs_concept_output.xlsx>
python scripts/recalc.py <cs_concept_output.xlsx>
```

The first command produces the workbook and prints a JSON summary (count of CSGs, CAL-relevant nodes, CSRs generated, CAL distribution). The second command recalculates any formulas and surfaces formatting errors.

### Step 5 — Walk the user through the review

The CS Concept systematically allocates security properties to architectural elements. After generating, point the user to these review checkpoints in order:

1. **`02_CS_Goals_Echo`** — confirm the imported cybersecurity goals match the TARA output. If not, the TARA needs updating, not this workbook.
2. **`03_System_Block_Diagram`** — confirm the node list, types, and shared resources are correct. Are any elements missing? Any debug ports overlooked?
3. **`05_CSR_Catalog`** — review each CSR's wording. The `<TBD>` placeholders (mechanism, algorithm, duration) need the analyst's judgment based on the threat model and architectural constraints.
4. **`06_CAL_Allocation`** — confirm that each node's inherited CAL reflects its security criticality. If a node is allocated multiple CSRs from different CSGs, its CAL is the maximum.
5. **`07_Verification_Matrix`** — confirm the recommended verification methods are practical for the program. Methods rated `++` for the allocated CAL are effectively mandatory; skipping requires written justification.
6. **`08_CSI_Handoff`** — each CSR has placeholder CSI requirement rows. These get authored during the CSI phase but the skeleton is ready.

When the user requests changes, modify the block diagram JSON (or add new cybersecurity goals, or override the CSR allocation) and regenerate. The xlsx is a derived artefact; the JSON + the linked CS Goals are the source of truth.

## Output structure (10 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | CS Concept doc ID, project, dates, methodology statement |
| 01 | Document Control | Revision history |
| 02 | CS Goals Echo | Read-only echo of the cybersecurity goals imported from the CS Goals xlsx |
| 03 | System Block Diagram | Node inventory table (ECUs, gateways, memory, key stores, debug interfaces) |
| 04 | CS Concept Argument | One derivation tree per CSG across six properties; basic events per node |
| 05 | CSR Catalog | One CSR per goal-property-node combination; template-derived wording |
| 06 | CAL Allocation | Inherited CAL per node based on allocated CSRs |
| 07 | Verification Matrix | Recommended verification methods per CSR, driven by allocated CAL |
| 08 | CSI Handoff | Each CSR with placeholder cybersecurity implementation requirement rows |
| 09 | References | Normative references to ISO/SAE 21434 and input artefacts |

## CSR derivation logic

For each cybersecurity goal (CSG):
1. Identify the threat actor, threat vector, and target asset.
2. For each CAL-relevant node in the block diagram, determine which of the six security properties are relevant to defending against the threat:
   - **Authentication** — Does the attacker impersonate or forge identity?
   - **Authorization** — Does the attacker escalate privilege or access unauthorized functions?
   - **Integrity** — Does the attacker modify messages or firmware in flight or at rest?
   - **Confidentiality** — Does the attacker eavesdrop or reverse-engineer?
   - **Availability** — Does the attacker disable critical functions?
   - **Non-repudiation** — Must we prove who performed a security-critical action?
3. For each relevant property-node pair, instantiate the CSR template with the node name, mechanism, and algorithm.
4. Allocate the CSG's CAL to the CSR.
5. Recommend verification methods based on CAL.

## Common pitfalls to flag for the user

1. **Skipping debug interfaces.** Debug ports (JTAG, SWD, serial console) are prime attack vectors if not authenticated. Always enumerate them and allocate CSRs.
2. **Forgetting key management CSRs.** If cryptographic keys are involved, ensure there are CSRs for key generation, storage, rotation, and revocation. Key store nodes are typically CAL-3 (highest CAL).
3. **Conflating authentication and authorization.** Authentication proves identity; authorization grants permission. A CSR should do one or the other, not both.
4. **Over-specifying mechanisms.** Don't mandate a specific algorithm (e.g., "AES-256") if "AES-128 or stronger" would suffice. Leave flexibility in CSI unless the threat model demands specificity.
5. **Forgetting non-repudiation for audit-critical actions.** Firmware updates, configuration changes, and privilege grants should be logged and signed. Without non-repudiation CSRs, forensics are impossible.

## Files in this skill

```
cs-concept-builder/
├── SKILL.md
├── scripts/
│   ├── generate_cs_concept.py                   # main generator (reads CS Goals + block diagram, writes CS Concept xlsx)
│   ├── cs_goals_reader.py                       # extracts cybersecurity goals from cs-goals-builder xlsx
│   ├── recalc.py                                # LibreOffice formula recalc / error scan
│   └── office/
│       └── soffice.py
├── references/
│   ├── methodology.md                           # why six-property decomposition is standard
│   └── csr_templates.md                         # canonical CSR wording per property and node type
└── examples/
    └── sample_cs_concept_input_esc.json         # block diagram for ESC example
```
