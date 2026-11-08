---
name: dbc-builder
description: Generate an audit-ready DBC specification workbook from a CAN database definition. Produces an 11-tab xlsx capturing ECU inventory, message catalog with IDs and DLC, signal definitions with bit positions/length/byte order/scaling/units/value tables, message-signal allocation, network topology, and validation rules per CAN 2.0A/2.0B and ISO 11898. Use this skill whenever the user mentions DBC, CAN database, Vector DBC, communication matrix for CAN, message catalog, signal catalog, or CAN message specification, even in casual phrasings like "document our CAN signals" or "audit the message catalog". Always use this skill instead of producing freeform DBC notes in chat.
---

# DBC Builder

A DBC (CAN database) file is the authoritative specification of a Controller Area Network. This skill produces a complete, audit-ready DBC workbook by transforming a JSON definition into an 11-tab xlsx that captures all aspects of a CAN network: ECUs, messages with identifiers and frame types, signals with bit positions and encoding, multiplexing structure, value tables, and traceability.

The workbook is designed for ISO 11898 and AUTOSAR Communication module compliance audits. Every signal's location and encoding is explicitly documented so that implementation teams can generate DBC files and code-generation tools can validate against the specification.

## When to use this skill

Use whenever the user wants to:
- Document a CAN network or database
- Create a DBC specification from a JSON definition
- Audit or specify message and signal allocation
- Define signal encoding (scaling, offset, value tables)
- Capture multiplexed signal groups
- Hand off a communication specification to firmware or network analysis teams
- Build the documentation supporting ISO 11898 or AUTOSAR compliance

If the user only asks a conceptual question about CAN (e.g., "what is a DLC?") you can answer from the reference docs without producing a workbook — but offer the workbook as the next step.

## Workflow

### Step 1 — Capture the network definition (interview)

Ask the user for these inputs in a small number of concise turns. The minimum viable input:

1. **Project context** (project, doc ID, revision, date, author, approver, company)
2. **Network name and scope** — what ECUs, what CAN controllers (CAN 2.0A, 2.0B, CAN FD awareness)
3. **ECU list** — node names, manufacturers, software versions
4. **Messages** — for each message: identifier (11-bit or 29-bit), DLC, cycle time, sender ECU, frame type (standard/extended)
5. **Signals** — for each signal: name, bit start, bit length, byte order (little-endian/big-endian), scale, offset, min, max, unit, receivers, multiplexor indicator
6. **Value tables** — enumerations for signals with discrete values (e.g., gear position)
7. **Multiplexing** — which signals are multiplexed and by which multiplexor signal

The script will accept JSON and auto-suggest defaults for optional fields. The mandatory fields are at least one message and at least one signal.

### Step 2 — Read the references

Before generating, read these if relevant:

- `references/methodology.md` — explains DBC structure and the 11-tab layout
- `references/dbc_conventions.md` — signal encoding, byte order, multiplexing, J1939 awareness

### Step 3 — Build the input JSON

Construct an input JSON that conforms to the schema documented at the top of `scripts/generate_dbc.py`. 

The schema is forgiving: omit any field you don't have and the script will auto-suggest sensible defaults. The mandatory fields are at least one entry in `messages` and at least one in `signals`.

### Step 4 — Generate

Run from a shell that has Python and openpyxl available:

```bash
python scripts/generate_dbc.py <input.json> <output.xlsx>
```

The command produces the workbook and prints a JSON summary (message count, signal count, ECU count).

### Step 5 — Present and iterate

Present the resulting xlsx to the user and **explicitly call out what they should review**:

- The Message Catalog tab — are all message IDs correct and unique? Do cycle times and DLCs match your intent?
- The Signal Catalog tab — sample 5–10 signals and verify bit position, byte order, scale/offset, units.
- The Signal-to-Message Mapping tab — do the signal receivers match the message senders?
- The Value Tables tab — are enumerations correct for state signals?
- The Message-Signal Mapping tab — check that multiplexed groups are correct.

When the user asks for changes, modify the input JSON and regenerate rather than editing the xlsx directly. The xlsx is a derived artifact — the JSON is the source of truth.

## Output structure (11 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Project, doc ID, revision, approvers |
| 01 | Document Control | Revision history, distribution list |
| 02 | ECU Inventory | Node names, manufacturers, software versions |
| 03 | Message Catalog | Message ID (hex), name, DLC, cycle time, sender, frame type, signal count |
| 04 | Signal Catalog | Signal ID, name, bit start, bit length, byte order, type, scale, offset, min, max, unit, receivers |
| 05 | Signal-to-Message Mapping | Each signal's parent message and bit position |
| 06 | Value Tables | Discrete value enumerations for signals |
| 07 | Signal Group Definitions | Multiplexor signals and their multiplexed groups |
| 08 | Network Topology | ECU connections and message flow |
| 09 | Validation Rules | Consistency checks (e.g., signal fits within DLC, no bit overlap) |
| 10 | References | CAN 2.0A/2.0B, ISO 11898, AUTOSAR references |

## Files in this skill

```
dbc-builder/
├── SKILL.md                                    # this file
├── scripts/
│   ├── generate_dbc.py                         # main generator
│   ├── recalc.py                               # LibreOffice formula recalc (if needed)
│   └── office/
│       └── soffice.py                          # LibreOffice helper (from xlsx skill)
├── references/
│   ├── methodology.md                          # DBC structure and workbook layout
│   └── dbc_conventions.md                      # signal encoding, byte order, multiplexing
└── examples/
    └── sample_input_can.json                   # full example to clone for new projects
```

## Common pitfalls to flag for the user

1. **Mixing CAN 2.0A (11-bit) and 2.0B (29-bit) IDs.** Frame type must be consistent.
2. **Signal bit overlap.** Two signals assigned to the same bits will fail validation.
3. **Multiplexor not included in signal list.** Multiplexor signals must be explicitly defined.
4. **Missing value tables.** State signals without enumerations will be flagged.
5. **DLC too small for signal payload.** Validation detects if a signal's bit end exceeds the DLC.
