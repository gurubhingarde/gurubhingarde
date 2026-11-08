---
name: cdd-builder
description: Generate an audit-ready CDD (CANdela Diagnostic Description) authoring workbook for Vector CANdela Studio covering ECU diagnostic specification, supported UDS services, DIDs, RIDs, DTCs, sessions, security levels, and routine controls used by Vector tooling for ECU diagnostic database authoring. Use this skill whenever the user mentions CDD, CANdela, CANdelaStudio, Vector diagnostic database, or CDD authoring.
---

# CDD Builder

Produces a complete, audit-ready CDD (CANdela Diagnostic Description) authoring workbook for Vector CANdela Studio. CDD captures the full diagnostic specification of an ECU in a format compatible with Vector's diagnostic database tools, including services, data identifiers, routine identifiers, DTCs, sessions, security access, and variant coding.

## When to use this skill

- Generate or update a CDD authoring workbook
- Prepare ECU diagnostic specification for Vector CANdela Studio import
- Document supported UDS services and DIDs per ISO 14229-1
- Define routine identifiers (RIDs) and control options
- Configure session structures and security access levels
- Specify variant coding for production ECU variants
- Create the diagnostic workbook prior to XML export

## Workflow

### Step 1 — Gather ECU diagnostic specification

Collect from your ECU design and system specification:

1. **ECU identity** — name, hardware/software version, supplier, market variants
2. **Services** — UDS services supported (10 01, 22, 2E, 31, 3D, 3E, etc.)
3. **DIDs** — data identifiers with read/write access, periodic reporting
4. **RIDs** — routine identifiers for system tests and diagnostics
5. **Sessions** — default session, programming session, extended diagnostic session
6. **Security access** — security levels, seed-key algorithms
7. **Variant coding** — production-line variants and their diagnostic differences

### Step 2 — Build input JSON

Construct an input JSON with ECU identity, service list, DID catalog, RID catalog, session configuration, and security levels. See `examples/sample_input.json` for a worked example.

```bash
python scripts/generate_cdd.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

### Step 3 — Review and iterate

Present the resulting xlsx and review:

- **ECU Identity tab** — hardware/software version, supplier, variant list
- **Session Catalog tab** — all session types defined with transitions
- **Service Inventory tab** — all supported services with bit settings
- **DID Catalog tab** — data identifier coverage, read/write permissions
- **RID Catalog tab** — routine tests, routing to safety/performance functions
- **Security Access tab** — levels paired correctly (request-seed, send-key)
- **Variant Coding tab** — inheritance and consistency across variants

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 0 | Title | ECU name, project, doc ID, revision, dates, approvers |
| 1 | Document Control | Revision history, distribution list |
| 2 | ECU Identity | Hardware/software version, supplier, market variants |
| 3 | Session Catalog | Default session, programming session, extended diagnostic session |
| 4 | Service Inventory | UDS services (10, 22, 2E, 31, 3D, 3E, etc.) with enabled flags |
| 5 | DID Catalog | Data identifiers with read/write access, periodic reporting |
| 6 | RID Catalog | Routine identifiers with start/stop/request options |
| 7 | DTC Cross-Reference | Link to source DTC catalog |
| 8 | Security Access Levels | Request-seed and send-key pairs per level |
| 9 | Variant Coding | Production-line variants and inheritance rules |
| 10 | Communication Configuration | Transport protocol, timing, addressing |
| 11 | References | Standards (ISO 14229-1, Vector CANdela) |

## Files in this skill

```
cdd-builder/
├── SKILL.md
├── scripts/
│   ├── generate_cdd.py
│   ├── recalc.py
│   └── office/soffice.py
└── examples/
    └── sample_input.json
```
