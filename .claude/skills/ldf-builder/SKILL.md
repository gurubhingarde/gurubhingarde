---
name: ldf-builder
description: Generate an audit-ready LIN Description File (LDF) workbook in ISO 17987 format capturing master/slave nodes, frames (unconditional/event-triggered/sporadic/diagnostic), signals, schedule tables, and node attributes per LIN 2.2A spec. Use this skill whenever the user mentions LDF, LIN bus, LIN node, schedule table, or LIN cluster definition. Always use this skill instead of producing freeform LDF notes in chat.
---

# LDF Builder

A LIN Description File (LDF) is the foundational specification document for a LIN (Local Interconnect Network) cluster per ISO 17987 and LIN 2.2A. This skill produces a complete, audit-ready LDF workbook by walking the analyst through cluster definition (master node, slave nodes), frame enumeration (unconditional, event-triggered, sporadic, diagnostic), signal allocation, schedule table design, and encoding type definition.

The skill is opinionated about **structure**, not **answers**. The workbook preserves all cluster metadata in a normalized, audit-ready format. Signal allocation, frame publisher/subscriber relationships, and schedule coverage are validated end-to-end.

## When to use this skill

Use whenever the user wants to:
- Define or document a LIN cluster
- Specify LDF nodes, frames, and signals
- Design LIN schedule tables
- Encode signals (physical/logical mapping)
- Document diagnostic signals and node attributes
- Build the specification that supports a LIN bus implementation or certification

If the user only asks a conceptual LIN question and does not need a deliverable, you can answer from reference docs without producing a workbook — but offer the workbook as the next step.

## Workflow

### Step 1 — Capture cluster definition (interview)

Gather inputs in concise turns. The minimum viable input:

1. **Cluster name and abbreviation** (e.g., "Seat Heater Control / SHC")
2. **Project context** (project, doc ID, revision, date, author, approver)
3. **LIN protocol version** — LIN 2.0, 2.1, or 2.2A (defaults to 2.2A)
4. **Baud rate** (1–20 kbps, typical 19.2)
5. **Master node** — name, identifier, timing parameters
6. **Slave nodes** — list with names, identifiers, and communication roles
7. **Frames** — unconditional (periodic), event-triggered, sporadic, diagnostic with length and period
8. **Signals** — name, frame, type (physical/logical), encoding, producers, consumers
9. **Schedule tables** — frame sequences and timing per operational mode
10. **Operating modes** — names and active schedule (e.g., "Idle", "Active Heating", "Diagnostics")

### Step 2 — Read the references

Before generating, read whichever are relevant:

- `references/methodology.md` — LIN cluster definition flow
- `references/ldf_conventions.md` — frame types, schedule timing, encoding types per LIN 2.2A

### Step 3 — Build the input JSON

Construct an input JSON conforming to the schema at the top of `scripts/generate_ldf.py`. A minimal example:

```json
{
  "cluster": {
    "name": "Seat Heater Control",
    "abbr": "SHC",
    "project": "Vehicle Comfort",
    "doc_id": "LDF-SHC-001",
    "revision": "1.0",
    "date": "2026-05-02",
    "author": "J. Doe",
    "approver": "Safety Team",
    "lin_version": "2.2A",
    "baud_rate_kbps": 19.2
  },
  "master_node": {
    "name": "Seat Controller",
    "identifier": "0x01"
  },
  "slave_nodes": [
    {"name": "Heater Left", "identifier": "0x10"},
    {"name": "Heater Right", "identifier": "0x11"}
  ],
  "frames": [
    {"id": "F01", "name": "Heat_Command", "type": "unconditional", "length": 8, "period_ms": 100, "publisher": "0x01"},
    {"id": "F02", "name": "Heat_Status", "type": "unconditional", "length": 8, "period_ms": 50, "publisher": "0x10"}
  ],
  "signals": [
    {"id": "S01", "name": "Heat_Level", "frame": "F01", "start_bit": 0, "length": 8, "type": "physical", "min": 0, "max": 255}
  ],
  "schedule_tables": [
    {"name": "Heating_Active", "mode": "Heating", "frames": [{"frame": "F01", "slot_ms": 0}, {"frame": "F02", "slot_ms": 50}]}
  ]
}
```

The schema is forgiving; omit any field and the script auto-suggests sensible defaults.

### Step 4 — Generate

Run from a shell with Python and openpyxl:

```bash
python scripts/generate_ldf.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The first command produces the workbook and prints a JSON summary. The second evaluates formulas.

### Step 5 — Present and iterate

Present the resulting xlsx and explicitly call out:

- The Cluster Header tab — baud rate, LIN version, timing parameters
- The Node Attributes tab — master/slave roles and communication capabilities
- The Frame Catalog — publisher/subscriber relationships
- The Schedule Tables — frame sequencing per mode
- The Signal Catalog — encoding completeness

When the user asks for changes, modify the input JSON and regenerate rather than editing the xlsx directly.

## Output structure (11 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Cluster, project, doc ID, revision, dates, approvers |
| 01 | Document Control | Revision history, distribution list |
| 02 | Cluster Header | LIN version, baud rate, timing parameters, bus configuration |
| 03 | Node Attributes | Master node, slave nodes, node roles, communication capabilities |
| 04 | Signal Catalog | All signals with encoding, min/max, type (physical/logical) |
| 05 | Frame Catalog | All frames (unconditional/event-triggered/sporadic/diagnostic) with publishers, subscribers, length, period |
| 06 | Schedule Tables | Frame sequences per operational mode with slot timing |
| 07 | Encoding Types | Physical/logical signal mapping, scaling, units |
| 08 | Diagnostic Signals | Diagnostic frames, services, signal definitions |
| 09 | Validation Rules | Baud rate range, frame length limits, schedule coverage checks |
| 10 | References | ISO 17987 / LIN 2.2A specification links |

## Files in this skill

```
ldf-builder/
├── SKILL.md                                    # this file
├── scripts/
│   ├── generate_ldf.py                         # main generator
│   ├── recalc.py                               # LibreOffice formula recalc
│   └── office/
│       ├── __init__.py
│       └── soffice.py                          # LibreOffice helper
├── references/
│   ├── methodology.md                          # LDF definition flow
│   └── ldf_conventions.md                      # frame types, encoding types
└── examples/
    └── sample_input_shc.json                   # seat heater control example
```
