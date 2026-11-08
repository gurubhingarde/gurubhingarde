---
name: dtc-catalog-builder
description: Generate an audit-ready DTC catalog workbook per ISO 14229-1 and SAE J2012 covering all diagnostic trouble codes for an ECU including code definitions, status masks, snapshot data identifiers, extended data records, debounce algorithms, healing logic, and OBD relevance for production diagnostic systems. Use this skill whenever the user mentions DTC catalog, diagnostic trouble codes, fault codes, P codes, B codes, C codes, U codes, snapshot data, extended data records, or fault management catalog.
---

# DTC Catalog Builder

Produces a complete, audit-ready DTC (Diagnostic Trouble Code) catalog workbook per ISO 14229-1 and SAE J2012 specifications. Each DTC is documented with its 3-byte code format, status mask configuration, snapshot and extended data bindings, debounce and healing algorithms, and OBD-II mapping.

## When to use this skill

- Generate or update a DTC catalog for an ECU
- Document all Pxxxx, Bxxxx, Cxxxx, Uxxxx codes per SAE J2012
- Define status masks, debounce algorithms, and healing logic
- Configure snapshot DIDs and extended data records per DTC
- Map DTCs to OBD-II readiness monitors
- Prepare a DTC catalog for production diagnostic system development

## Workflow

### Step 1 — Gather DTC inventory

Collect from your ECU specification or fault management design:

1. **DTC code** — Pxxxx (powertrain), Bxxxx (body), Cxxxx (chassis), Uxxxx (network)
2. **Description** — concise fault definition
3. **Fault type** — ISO 14229-1 category (functional fault, permanent fault, intermittent fault, etc.)
4. **Severity** — OBD significance (critical, major, minor, info)
5. **Customer impact** — MIL trigger, limp-home mode, service required, etc.
6. **Debounce method** — counter-based, timer-based, or algorithmic
7. **Healing condition** — how the fault clears
8. **Snapshot DIDs** — data identifiers frozen at DTC set
9. **Extended data records** — fault history detail level

### Step 2 — Build input JSON

Construct an input JSON with DTC inventory, snapshot/extended data bindings, debounce catalog, and healing rules. See `examples/sample_input.json` for a worked example.

```bash
python scripts/generate_dtc.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

### Step 3 — Review and iterate

Present the resulting xlsx and review:

- **DTC Inventory tab** — code uniqueness, fault types, severity assignments
- **Status Mask Configuration tab** — all required bits (test failed, test incomplete, etc.) assigned
- **Snapshot/Extended Data tabs** — DID list completeness
- **Debounce Catalog tab** — algorithm coverage and counter/timer specs
- **OBD Mapping tab** — readiness monitor alignment for each OBD DTC

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 0 | Title | ECU name, project, doc ID, revision, dates, approvers |
| 1 | Document Control | Revision history, distribution list |
| 2 | ECU Identification | Hardware/software version, supplier, market/variant data |
| 3 | DTC Inventory | All codes with description, hex, fault type, severity, customer impact, MIL behavior |
| 4 | Snapshot DID Bindings | Per-DTC list of snapshot data identifiers and freeze conditions |
| 5 | Extended Data Records | Per-DTC extended data structure (fault count, aging counter, etc.) |
| 6 | Status Mask Configuration | Bit definitions per ISO 14229-1 (test failed, test incomplete, etc.) |
| 7 | Debounce Catalog | Counter-based and timer-based algorithms with parameters |
| 8 | Healing Logic | Per-DTC healing conditions and recovery paths |
| 9 | OBD Mapping | OBD-II codes, readiness monitors, emissions relevance |
| 10 | Test Conditions | Reference conditions for each DTC set/clear test |
| 11 | References | Standards (ISO 14229-1, SAE J2012, ISO 15031-6) |

## Files in this skill

```
dtc-catalog-builder/
├── SKILL.md
├── scripts/
│   ├── generate_dtc.py
│   ├── recalc.py
│   └── office/soffice.py
├── references/
│   ├── methodology.md
│   ├── dtc_format.md
│   └── iso_status_bits.md
└── examples/
    └── sample_input.json
```
