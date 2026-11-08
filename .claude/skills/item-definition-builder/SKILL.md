---
name: item-definition-builder
description: Produce an audit-ready ISO 26262-3 Item Definition workbook from structured data. 11-tab xlsx captures scope, functions, boundary, interfaces, operating modes, allocations, and assumptions. Use this skill whenever the user needs to document a safety-critical item definition, vehicle system specification, or building block for HARA.
---

# Item Definition Builder

An Item Definition is the foundation of the ISO 26262 concept phase. This skill produces a complete, audit-ready Item Definition workbook by guiding you through scope capture, functional enumeration, boundary clarification, external interface documentation, and assumption recording.

The skill combines structured data capture with professional xlsx layout. Every tab is designed to map directly to ISO 26262-3 Clause 5 sub-clauses, so the resulting workbook is immediately audit-ready.

## When to use this skill

Use whenever the user wants to:
- Document a new safety-critical item or vehicle system
- Define the scope, boundary, and interfaces of an automotive component
- Enumerate functions and non-functional requirements for an item
- Record assumptions about vehicle, driver, and operating environment
- Create the artifact that feeds the HARA (Hazard Analysis and Risk Assessment)
- Build the documentation foundation for ISO 26262 concept-phase assessment

## Workflow

### Step 1 — Capture the item definition (interview)

Ask the user for these inputs in a small number of concise turns:

1. **Item identity** — name, abbreviation, project, doc ID, revision, date, author, approver
2. **Scope and classification** — what the item does, item type (vehicle system / subsystem / component), distinguishing notes vs neighboring items
3. **Functions** — list of item functions with ID, name, description, and criticality hint (informs the HARA function list)
4. **Non-functional requirements** — performance, environmental, regulatory, market constraints
5. **Boundary diagram** — what is IN the item, what is OUT, adjacent systems, boundary notes
6. **External interfaces** — sensor/actuator/ECU connections with ID, counterpart system, direction, data type, integrity protection
7. **Operating modes** — Off, Init, Standby, Active, Degraded, Fault modes with entry/exit conditions and safety relevance
8. **Hardware / Software / Mechanical allocation** — which functions are allocated to HW, SW, or mechanical subsystems
9. **Initial assumptions** — vehicle class, driver, market, lifecycle scope, cybersecurity partitions, other-item assumptions
10. **References** — standards, related documents (HARA placeholder), regulations

### Step 2 — Read the references

Before generating, read:

- `references/methodology.md` — what an Item Definition contains and why it matters to HARA
- `references/iso26262_clause5_mapping.md` — how the 11 tabs map to ISO 26262-3 Clause 5 requirements

### Step 3 — Build the input JSON

Construct an input JSON conforming to the schema in `scripts/generate_item_definition.py`. A worked example lives in `examples/sample_item_def_esc.json`.

The schema is forgiving: omit any field you don't have and the script defaults to empty. Mandatory fields are `item.name`, at least one entry in `functions`, and ideally `scope_description`.

### Step 4 — Generate

Run from a shell with Python and openpyxl:

```bash
python scripts/generate_item_definition.py <input.json> <output.xlsx>
```

The command produces the workbook and prints a JSON summary (tab count, function count, interface count).

### Step 5 — Present and iterate

Present the resulting xlsx to the user and call out what to review:

- The Item Description tab — does the scope statement clearly define the item boundary?
- The Functions tab — does the function list match the user's mental model? Criticality hints will inform the HARA's function list.
- The Boundary Diagram tab — are IN/OUT/Adjacent System lists complete and unambiguous?
- The External Interfaces tab — do signal/data types and integrity protections align with the system architecture?
- The Operating Modes tab — do mode transitions and safety relevance classifications make sense?
- The Allocations tab — is the HW/SW/Mech split clear and defensible?
- The Assumptions tab — are all constraints and vehicle/driver/lifecycle assumptions explicit?

When the user asks for changes, modify the input JSON and regenerate. The xlsx is a derived artifact; the JSON is the source of truth.

## Output structure (11 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Item name, project, doc ID, revision, dates, approvers |
| 01 | Document Control | Revision history, distribution list |
| 02 | Item Description | Scope, classification, distinguishing notes |
| 03 | Functions | Function ID, name, description, criticality hints |
| 04 | Non-Functional Requirements | Performance, environmental, regulatory, market constraints |
| 05 | Boundary Diagram | Text and structured list of IN/OUT/Adjacent systems |
| 06 | External Interfaces | Interface ID, counterpart, direction, data, integrity, notes |
| 07 | Operating Modes | Mode ID, name, entry/exit conditions, safety relevance |
| 08 | Allocation HW/SW/Mech | Function ID × allocation type (HW/SW/Mech/Mix) + rationale |
| 09 | Initial Assumptions | Vehicle, driver, market, lifecycle, other-item assumptions |
| 10 | References | Standards, related documents, regulations |

## Files in this skill

```
item-definition-builder/
├── SKILL.md                                    # this file
├── scripts/
│   ├── generate_item_definition.py             # main generator
│   ├── recalc.py                               # LibreOffice formula recalc (shared)
│   └── office/
│       ├── soffice.py                          # LibreOffice helper (shared)
│       └── __init__.py
├── references/
│   ├── methodology.md                          # Item Definition purpose and structure
│   └── iso26262_clause5_mapping.md             # Tab-to-clause mapping
└── examples/
    └── sample_item_def_esc.json                # sample ESC item definition
```
