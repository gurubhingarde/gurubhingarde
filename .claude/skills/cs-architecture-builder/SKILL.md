---
name: cs-architecture-builder
description: Generate an audit-ready ISO/SAE 21434 Cybersecurity Architecture workbook from a CS Concept xlsx and a CS architecture JSON. Produces 12-tab xlsx with CSR catalog, cryptographic inventory, key management, secure boot chain, secure communication, access control, CSR-to-element allocation matrix, and defense-in-depth layers. Essential for bridging CSR allocations from system cybersecurity requirements into concrete security controls, cryptographic key plans, and HSM/secure element architectures. Use whenever the user mentions cybersecurity architecture, security controls, key management, secure boot, or cryptographic design in an automotive cybersecurity context. Always use this skill instead of producing freeform Cybersecurity Architecture in chat.
---

# CS Architecture Builder

The Cybersecurity Architecture (ISO/SAE 21434) refines the system-level Cybersecurity Concept into concrete security controls, cryptographic elements, key management policies, secure boot chains, and secure communication protocols. This skill automates the rote parts of CS architecture authoring—CSR and CAL mapping, cryptographic inventory compilation, key lifecycle planning, secure boot measurement chains, defense-in-depth layering, and control allocation matrices—leaving the analyst free to focus on threat-to-control mapping and security posture trade-offs.

## When to use this skill

Use whenever the user wants to:
- Refine Cybersecurity Concept CSRs into a detailed security control catalog
- Map CSRs to specific cryptographic algorithms and key management policies
- Define cryptographic inventory (AES, RSA, ECC, HMAC, SHA, etc.) with key lengths and modes
- Plan key generation, storage, rotation, and destruction lifecycle
- Specify secure boot chain: BootROM → Bootloader → Application with anti-rollback
- Define secure communication channels (TLS 1.3, IPsec, SecOC) per data flow
- Document access control roles, authentication factors, and privilege levels
- Allocate Cybersecurity Architecture Elements to CSRs (HSM, TPM, secure element, firewall, IDS, etc.)
- Conduct defense-in-depth analysis (perimeter, network, host, app, data layers)
- Hand off to integration, security testing, and ISO 21434 verification teams

Pre-requisite: a CS Concept workbook produced by cs-concept-builder. If the user does not have one, redirect them first.

## Workflow

### Step 1 — Confirm the CS Concept input

Ask for the path to the CS Concept xlsx. The skill reads the tabs cs-concept-builder emits:
- `05_CSR_Catalog` — Cybersecurity Requirements with parent CSG, CAL, branch, node, verification method
- `06_CAL_Allocation` — inherited CAL and CSR count per node
- `02_CS_Goals_Echo` — cybersecurity goals (threat, asset, CAL, driving TARA IDs), back-linked to the CSRs derived from each

Workbooks using the pre-2026-08 tab names (`02_CSRs_Catalog`, `03_CAL_Allocations`, `04_Threat_Mapping`) still load via fallback.

### Step 2 — CS refinement interview

The CS Concept captures logical CSRs and TARA levels. The CS Architecture needs the next level: which concrete security controls, cryptographic operations, and protective measures implement each CSR, on which elements, with what key management policy, and what defense-in-depth strategy.

For each CSR, gather:
- Allocated TARA level, linked threats, required security controls
- Cryptographic operations (AES-256-GCM, RSA-4096, ECDSA P-256, SHA-384, etc.)
- Key ID, purpose, key length, generation method, storage location (HSM/TPM/secure element/flash)
- Rotation policy (annual, per-session, per-boot), destruction method
- Secure communication channels (TLS 1.3, IPsec, SecOC, CAN-FD with MAC)
- Secure boot stages (BootROM signature check, Bootloader measurement, App verification, anti-rollback counter)
- Defense-in-depth layers (perimeter firewall, network IDS, host-based monitoring, app-level checks, encrypted data at rest)
- HSM/TPM certification level (FIPS 140-2, Common Criteria EAL, etc.)

Capture into a JSON file matching examples/sample_cs_arch_input_esc.json.

### Step 3 — Read the references

Before generating:
- `references/methodology.md` — CS architecture refinement, defense-in-depth, secure boot, key management overview. Always read on first invocation.
- `references/cs_control_catalog.md` — Control library (HSM, TPM, secure element, MAC, AES, RSA, ECC, secure boot, attestation, IDS, etc.)

### Step 4 — Generate

```bash
python scripts/generate_cs_architecture.py <cs_concept.xlsx> <cs_arch.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The generator produces the xlsx with all 12 tabs pre-populated. Tab 02 is a read-only echo of CSRs; tabs 03-11 refine into control catalogs, cryptographic inventories, key management, secure boot chains, communication protocols, and defense-in-depth strategies.

### Step 5 — Review checkpoints

1. **`00_Title_Page`** — confirm project, doc ID, linked CS Concept
2. **`01_Document_Control`** — revision history
3. **`02_CS_Concept_Echo`** — imported CSRs, CAL, branch, allocated node
4. **`03_CS_Element_Catalog`** — concrete security controls (HSM, TPM, secure element, firewall, IDS, key store, cert authority, secure boot ROM)
5. **`04_Cryptographic_Inventory`** — per operation: algorithm, key length, mode, lifecycle
6. **`05_Key_Management`** — per key class: ID, purpose, generation, storage, rotation, destruction
7. **`06_Secure_Boot_Chain`** — boot stages, measurement chain, root-of-trust, anti-rollback policy
8. **`07_Secure_Communication`** — per channel: protocol, authentication, encryption, integrity, replay protection
9. **`08_Access_Control`** — roles, privileges, authentication factors per role
10. **`09_CSR_to_Element_Allocation`** — cross-reference matrix: CSR rows x CS Element columns
11. **`10_Defense_in_Depth_Layers`** — per attack vector: layer 1-5 controls
12. **`11_References`** — CS Concept path, standards, control library

When the user requests changes, edit the input JSON and regenerate. The xlsx is a derived artifact; the CS Concept + CS architecture JSON are the source of truth.

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | CS Architecture doc ID, project, dates, linked CS Concept |
| 01 | Document Control | Revision history |
| 02 | CS Concept Echo | Read-only echo of CSRs: branch, CAL, requirement text, allocated node |
| 03 | CS Element Catalog | Security controls: ID, name, type, supplier, part number, certification |
| 04 | Cryptographic Inventory | Per operation: algorithm, key length, mode, lifecycle (gen/storage/rotation/destruction) |
| 05 | Key Management | Per key class: ID, purpose, generation, storage, rotation policy, destruction |
| 06 | Secure Boot Chain | Boot stages, measurements, root-of-trust, anti-rollback, secure unlock |
| 07 | Secure Communication | Per channel: protocol, auth, encryption, integrity, replay protection |
| 08 | Access Control | Roles, privileges, authentication factors, privilege escalation controls |
| 09 | CSR to Element Allocation | Cross-reference: CSR_ID rows x CS-E_ID columns; marks implementation |
| 10 | Defense in Depth Layers | Per attack vector: layer 1 (perimeter), 2 (network), 3 (host), 4 (app), 5 (data) |
| 11 | References | CS Concept, standards, control catalog, cryptographic sources |

## Files in this skill

```
cs-architecture-builder/
├── SKILL.md
├── scripts/
│   ├── cs_concept_reader.py              # extracts CSRs and CAL from CS Concept xlsx
│   ├── generate_cs_architecture.py       # main generator
│   ├── recalc.py
│   └── office/soffice.py
├── references/
│   ├── methodology.md                    # CS architecture refinement overview
│   └── cs_control_catalog.md             # control library (HSM, TPM, crypto, IDS, etc.)
└── examples/
    └── sample_cs_arch_input_esc.json     # ESC CS architecture input to clone
```
