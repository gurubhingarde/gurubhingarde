---
name: apqp-plan-builder
description: Generate an audit-ready AIAG APQP 5-phase automotive quality planning master plan workbook. Produces a 15-tab xlsx covering program definition, cross-functional team, five APQP phases with deliverables, gate reviews, special characteristics, risks, and schedule per IATF 16949 supplier requirements. Use when the user mentions APQP, product quality planning, or automotive supplier planning.
---

# APQP Plan Builder

An Advanced Product Quality Planning (APQP) Master Plan is the cornerstone of automotive supplier quality management per IATF 16949. This skill produces a complete, audit-ready APQP workbook by capturing program context, defining the cross-functional team, structuring all five AIAG phases with standard deliverables, documenting gate review criteria, and tracking special characteristics, risks, and schedule.

The skill is opinionated about **structure and AIAG phases**, not **answers**. Every deliverable, gate review, and team member has a placeholder ready for your project-specific data. The five phases (Plan and Define, Product Design, Process Design, Product and Process Validation, Feedback and Assessment) auto-populate with standard AIAG deliverable checklists, which you customize per your supplier agreement.

## When to use this skill

Use whenever the user wants to:
- Create or update an APQP Master Plan per AIAG methodology for Tier-1 automotive suppliers
- Define program scope, customer, OEM, and key dates across the APQP 5-phase lifecycle
- Establish cross-functional team roles and phase ownership
- Document APQP deliverables per phase with owner and status tracking
- Define phase gate review criteria and exit conditions
- Capture special characteristics (SC), critical characteristics (CC), and control methods
- Build a risk register and open items tracker aligned with product development schedule
- Prepare for IATF 16949 assessment or PPAP submission

If the user only asks a conceptual APQP planning question and does not need a deliverable, you can answer from the reference docs — but offer the workbook as the next step.

## Workflow

### Step 1 — Capture the program definition

Ask for these inputs in concise turns. The minimum viable input:

1. **Program name and document ID** (e.g., "ESC Control Module APQP / APQ-ESC-001")
2. **Customer / OEM** (e.g., "Phoenix Motors")
3. **Part number and vehicle program** (e.g., "WS-4521-A, Falcon XLT 2027")
4. **Supplier company** and key dates (SOP, EOP, model year, peak volume)
5. **Program Manager, Quality Lead, Engineering Lead** names and contact info
6. **Cross-functional team** — roles (PM, QE, DE, Manufacturing, Supplier Quality, etc.) and phase ownership
7. **Phase deliverables overrides** — any custom APQP deliverables beyond AIAG standard (omit to use defaults)
8. **Milestones** — program kickoff, gate review dates, PPAP submission, production run @ rate, SOP
9. **Gate reviews** — phase exit criteria and planned review dates
10. **Special characteristics (SC/CC)** — critical-to-quality dimensions and functional parameters
11. **Program risks** — capacity, design complexity, schedule, supply chain, resource, and technical risks
12. **Open items** — action items from kickoff or previous reviews

### Step 2 — Read the reference docs

Before generating, read these if relevant to the open question:

- `references/methodology.md` — APQP purpose, 5-phase structure, when AIAG vs VDA applies
- `references/aiag_phase_deliverables.md` — complete deliverable checklist per phase from AIAG manual
- `references/gate_review_criteria.md` — gate review content and exit criteria per phase

### Step 3 — Build the input JSON

Construct a JSON file that conforms to the schema documented at the top of `scripts/generate_apqp_plan.py`. A worked example lives in `examples/sample_apqp_plan_input_esc.json` — start from it for any automotive supplier APQP.

The schema is forgiving: omit any field and the script auto-populates sensible defaults (e.g., AIAG standard deliverables per phase, generic team roles, 8-milestone schedule). The mandatory fields are `program.name` and `program.customer`.

### Step 4 — Generate

Run from a shell with Python and openpyxl:

```bash
python scripts/generate_apqp_plan.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The first command produces the workbook. The second command recalculates any formulas so the file opens in Excel with computed values.

### Step 5 — Present and iterate

Present the resulting xlsx to the user and **explicitly call out what they should review**:

- The **Program Information** tab — customer, OEM, part number, key dates correct?
- The **Cross-Functional Team** tab — team roles and phase ownership defined?
- The **Phase 1–5 Deliverables** tabs — do the AIAG standard deliverables fit your supplier agreement, or do you need to add/remove items?
- The **Gate Reviews** tab — are the phase gate exit criteria specific to your program?
- The **Special Characteristics** tab — are all critical-to-quality and regulatory characteristics captured?
- The **Master Schedule** tab — are milestone dates and dependencies realistic?
- The **Risk Register** tab — are the top program risks identified and mitigations assigned?

When the user asks for changes, modify the input JSON and regenerate rather than editing the xlsx directly. The xlsx is a derived artifact — the JSON is the source of truth.

## Output structure (15 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Program name, customer, part number, doc ID, signatories (PM, QE Lead, DE Lead) |
| 01 | Document Control | Revision history and distribution record |
| 02 | Program Info | Customer, OEM, vehicle program, model year, SOP/EOP, volume, contract value |
| 03 | Cross-Functional Team | Team roster: name, role, department, phases responsible |
| 04 | Phase 1 Deliverables | Plan and Define Program: VOC, business case, customer requirements, preliminary BOM/flow, design goals, SC list |
| 05 | Phase 2 Deliverables | Product Design and Development: DFMEA, DFA/DFM, DVP&R, design reviews, prototype build, supplier APQP cascaded |
| 06 | Phase 3 Deliverables | Process Design and Development: packaging specs, process flow, PFMEA, control plan, MSA plan, PPC plan |
| 07 | Phase 4 Deliverables | Product and Process Validation: trial run, MSA executed, PPC data, PPAP, production validation, quality sign-off |
| 08 | Phase 5 Deliverables | Feedback and Assessment: variation reduction, customer satisfaction, lessons learned, corrective actions |
| 09 | Master Schedule | Gantt-style milestones: ID, name, phase, planned/actual date, predecessors, status |
| 10 | Gate Reviews | Phase gate review schedule: gate ID, phase exit, planned date, exit criteria, status |
| 11 | Special Characteristics | SC/CC list: ID, characteristic, type (SC/CC), source (CTQ/CSL/regulatory), control method |
| 12 | Risk Register | Program risks: ID, description, likelihood, impact, mitigation, owner |
| 13 | Open Items Tracker | Action items: ID, description, owner, due date, status |
| 14 | References | Standards (AIAG APQP, PPAP, FMEA; IATF 16949), customer/internal procedures |

## AIAG Standard Deliverables (per phase)

The script provides a complete default deliverable list aligned with AIAG APQP manual 2nd edition:

**Phase 1 (Plan and Define Program):** 9 deliverables — VOC, business case, customer requirements review, preliminary BOM, process flow, design goals, reliability targets, SC list, kickoff gate review

**Phase 2 (Product Design and Development):** 9 deliverables — DFMEA, DFA/DFM, DVP&R, design reviews, engineering drawings, finalized SC, supplier APQP cascade, prototype build, design gate review

**Phase 3 (Process Design and Development):** 10 deliverables — packaging specs, process flow chart, floor plan, characteristics matrix, PFMEA, pre-launch control plan, process instructions, MSA plan, PPC plan, process gate review

**Phase 4 (Product and Process Validation):** 9 deliverables — production trial run, MSA executed, preliminary PPC, production validation testing, PPAP submission, production control plan, production @ rate, quality sign-off, production gate review

**Phase 5 (Feedback and Assessment):** 6 deliverables — reduced variation, customer satisfaction monitoring, delivery/service performance, lessons learned, corrective actions, feedback gate review

When the user customizes the deliverable list, modify the input JSON's `phase_deliverables_overrides` and regenerate.

## Files in this skill

```
apqp-plan-builder/
├── SKILL.md                                    # this file
├── scripts/
│   ├── generate_apqp_plan.py                   # main generator
│   ├── recalc.py                               # LibreOffice formula recalc
│   └── office/
│       ├── soffice.py                          # LibreOffice helper
│       └── __init__.py
├── references/
│   ├── methodology.md                          # APQP purpose, 5-phase structure, AIAG vs VDA
│   ├── aiag_phase_deliverables.md              # complete deliverable checklist per phase
│   └── gate_review_criteria.md                 # gate review content and exit criteria
└── examples/
    └── sample_apqp_plan_input_esc.json         # full ESC example to clone
```

Always use this skill instead of producing a freeform APQP plan in chat.
