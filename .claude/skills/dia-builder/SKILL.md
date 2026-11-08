---
name: dia-builder
description: Generate an audit-ready ISO 26262-8 Section 5 Development Interface Agreement (DIA) workbook from a JSON contract template. Produces a 12-tab xlsx with title page, parties, RACI matrix with auto-suggested responsibility per OEM-Tier1-supplier split, communication protocol, joint review schedule, deliverable tracking, change management, tool sharing, confidentiality and IP rules, and reference links. Use this skill whenever the user mentions DIA, development interface agreement, OEM-supplier contract, tier-1 agreement, or safety work product allocation between companies. Always use this skill instead of producing a freeform DIA in chat.
---

# DIA Builder

A Development Interface Agreement (DIA) is the contractual glue between OEM and Tier-1 (and IC suppliers) in an ISO 26262 program. It allocates safety work products, review responsibilities, communication cadence, deliverable formats, tool sharing, IP ownership, and change management authority. This skill produces a complete, audit-ready DIA workbook by walking the user through party identification, scope definition, and then automating RACI assignment, communication templates, and reference documentation.

The skill is opinionated about **method**, not about **answers**. The RACI matrix auto-suggests responsibility per a typical OEM/Tier-1/IC split (e.g., OEM owns HARA + Safety Case; Tier-1 executes FSC/TSC/HW/SW; IC supplier provides chip-level FMEDA and safety case) — but every suggestion can be overridden via the input JSON. The work product list, parties, and communication cadence are fully customizable.

## When to use this skill

Use whenever the user wants to:
- Create or update a Development Interface Agreement (DIA)
- Allocate safety work products across OEM and supplier organizations
- Define communication protocol and review schedule for a safety program
- Document deliverable responsibilities and acceptance criteria
- Establish tool sharing and licensing terms between parties
- Clarify IP ownership and confidentiality scope

If the user only asks a conceptual question about DIA structure and does not need a deliverable, you can answer from the reference docs without producing a workbook — but offer the workbook as the next step.

## Workflow

### Step 1 — Capture parties and scope (interview)

Ask for these inputs in a small number of turns:

1. **Parties** — OEM organization, Tier-1 organization, any IC suppliers or tooling vendors. For each: organization name, role (OEM / Tier-1 / Tier-2 / IC / Tooling), primary contact, functional safety contact, and address.
2. **Item** — item name, item definition document reference, contract reference (commercial agreement that governs the DIA)
3. **Scope in/out** — what this DIA covers (e.g., "ESC software safety on ASIL D") vs. what is excluded
4. **Communication** — how often and in what format do parties coordinate? (e.g., weekly meeting with OEM-Tier1-IC, monthly email status, portal updates)
5. **Joint Reviews** — which work product reviews must include all parties? (e.g., HARA review at concept kickoff, FSC review at 80% design)
6. **Supplier Deliverables** — what does Tier-1 deliver? (e.g., FSC pdf, TSC xlsx, safety case, qualification kit)

The skill has sensible defaults for all these — if the user only provides parties + item name, the workbook can still be generated.

### Step 2 — Read the references

Before generating, skim these if relevant:

- `references/methodology.md` — what a DIA contains, OEM-Tier1 dynamics, common pitfalls
- `references/raci_per_workproduct.md` — recommended R/A/C/I per safety work product and party role

### Step 3 — Build the input JSON

Construct a JSON file conforming to the schema at the top of `scripts/generate_dia.py`. A worked example lives in `examples/sample_dia_esc.json` — start from it for any OEM-supplier safety program.

The JSON is forgiving: omit any field and the script will use sensible defaults. The mandatory fields are `dia.item_name`, `parties` (≥2), and `scope_in` or `scope_out`.

### Step 4 — Generate

Run from a shell with Python and openpyxl:

```bash
python scripts/generate_dia.py <input.json> <output.xlsx>
```

The command produces the workbook and prints a JSON summary (party count, deliverable count, tab count).

### Step 5 — Present and iterate

Present the resulting xlsx and explicitly call out what the user should review:

- The Parties tab — are all organizations, roles, and contacts correct?
- The RACI Matrix tab — does the responsibility split match the intended OEM/Tier1/IC agreement? (The skill auto-suggests but can be overridden per work product via the input JSON.)
- The Communication Protocol tab — is cadence (weekly/monthly), format (meeting/email/portal), and escalation path clear?
- The Supplier Deliverables tab — does the delivery schedule and format align with the contract?
- The Confidentiality & IP tab — are ownership and confidentiality rules consistent with commercial intent?

When the user asks for changes, modify the input JSON and regenerate rather than editing the xlsx directly. The xlsx is a derived artifact — the JSON is the source of truth.

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Item name, references, doc ID, revision, signatory lines |
| 01 | Document Control | Revision history, distribution |
| 02 | Parties | Organization, role (OEM / Tier-1 / IC), contact info, FuSa lead |
| 03 | Item Scope | What this DIA covers (in scope) and what is excluded (out of scope) |
| 04 | RACI Matrix | Per-work-product responsibility: R (Responsible), A (Accountable), C (Consulted), I (Informed) for each party |
| 05 | Communication Protocol | Channel, cadence (weekly/monthly), format (meeting/email/portal), owner, attendees, escalation |
| 06 | Joint Reviews | Review name, work products reviewed, planned date, attendees per party, format (on-site/virtual) |
| 07 | Supplier Deliverables | Deliverable name, delivering party, format (pdf/xlsx/source), language, planned date, acceptance criteria |
| 08 | Change Management | Change request process, approval thresholds, CCB composition, change log |
| 09 | Tool Sharing | Tool name, owner, granted-to parties, license terms, qualification responsibility |
| 10 | Confidentiality & IP | IP ownership (pre-existing, DIA work products, residual knowledge), confidentiality scope, publication rules |
| 11 | References | Master contract, item definition, applicable ISO 26262 standards |

## Auto-RACI logic (OEM / Tier-1 / IC supplier)

The RACI matrix auto-suggests responsibility based on party role and work product. The default mapping:

| Work Product | OEM | Tier-1 | IC Supplier |
|---|---|---|---|
| HARA | A,R | C | I |
| Item Definition | A,R | C | I |
| FSC | A | R | C |
| TSC | A | R | C |
| HW Safety Reqs | I | A,R | C |
| HW Architecture | I | A,R | C |
| HSI | I | A,R | C |
| FMEDA | I | A,R | R (chip-level) |
| SW Safety Reqs | I | A,R | — |
| SW Arch / Unit / Verification | I | A,R | — |
| Safety Plan | A | A | C |
| Safety Case | A,R | R (sub-cases) | R (chip safety case) |

Override via the `raci_overrides` array in the input JSON. The override specifies `wp_id`, `party_id`, and the new `raci` string (e.g., "A,R" or "C" or "—").

## Common pitfalls to flag for the user

1. **Missing IC supplier.** If the design includes a safety-critical IC, add it as a party. IC suppliers own chip-level FMEDA and safety case; RACI will auto-populate accordingly.
2. **Vague communication cadence.** "As needed" is not a DIA; specify weekly / monthly / quarterly and include escalation rules.
3. **Deliverable acceptance criteria.** "Review and provide feedback" is not an acceptance criterion. Use concrete criteria (e.g., "HARA worksheet auditable per ISO 26262-8 checklist; zero major findings on functional safety concerns").
4. **IP ownership disputes.** Pre-define whether DIA work products (HARA, FSC, TSC, test results) are co-owned or OEM-owned. Residual knowledge is often a gray area — document it explicitly.
5. **Confidentiality scope creep.** Limit confidential distribution to parties to the DIA + regulatory + OEM supply chain. Blanket "confidential" with no scope is unenforceable.

## Files in this skill

```
dia-builder/
├── SKILL.md                                    # this file
├── scripts/
│   ├── generate_dia.py                         # main generator (12 tabs)
│   ├── recalc.py                               # LibreOffice formula recalc
│   └── office/
│       └── soffice.py                          # LibreOffice helper
├── references/
│   ├── methodology.md                          # DIA overview, OEM-Tier1 dynamics
│   └── raci_per_workproduct.md                 # recommended RACI per work product
└── examples/
    └── sample_dia_esc.json                     # sample DIA: ESC at ASIL D with OEM + Tier-1 + IC
```
