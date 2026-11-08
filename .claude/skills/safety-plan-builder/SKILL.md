---
name: safety-plan-builder
description: Generate an audit-ready ISO 26262-2 Section 6 Safety Plan workbook. Produces a 12-tab xlsx defining project scope, roles, ASIL targets, work products, confirmation review assignments with auto-suggested independence levels, tools, resources, anomalies, schedule, and references. Use when the user mentions Safety Plan, safety planning, or ISO 26262 management phase.
---

# Safety Plan Builder

A Safety Plan is the cornerstone of ISO 26262-2 Clause 6 (Management of Functional Safety). This skill produces a complete, audit-ready Safety Plan workbook by capturing project context, defining roles, tailoring applicable clauses, enumerating work products across all parts of the standard, assigning confirmation reviewers with independence levels auto-suggested per ASIL, cataloging tools with TCL classification, and tracking milestones.

The skill is opinionated about **structure**, not **answers**. Every role, work product, and tool has a placeholder ready for your project-specific data. The Confirmation Reviews tab auto-suggests independence levels (I1/I2/I3) based on the target ASIL per ISO 26262-2 Table 1, so reviewers match the required rigor.

## When to use this skill

Use whenever the user wants to:
- Create or update a functional safety plan per ISO 26262-2 Section 6
- Define roles and responsibilities for a safety-critical project
- Plan work products across concept, system, hardware, and software phases
- Assign confirmation reviewers with correct independence levels
- Catalog tools and justify their TCL classification
- Build the documentation that supports an ISO 26262 management-phase assessment

If the user only asks a conceptual planning question and does not need a deliverable, you can answer from the reference docs — but offer the workbook as the next step.

## Workflow

### Step 1 — Capture the project definition

Ask for these inputs in concise turns. The minimum viable input:

1. **Project name and document ID** (e.g., "Project Phoenix ESC Safety Plan / SPL-ESC-001")
2. **Target ASIL** (A, B, C, or D)
3. **Functional Safety Manager** name and email
4. **Vehicle programs** this item applies to
5. **Key suppliers** involved in the lifecycle
6. **Roles** — FSM, Project Manager, HW Lead, SW Lead, Confirmation Reviewer, Assessor, Customer interface
7. **Work products** — list of HARA, FSC, TSC, verification artifacts, etc. (the script provides defaults for 25 items covering Parts 2–8)
8. **Tools** — MATLAB/Simulink, GitLab, Polarion, test frameworks, etc. (include vendor, version, TCL classification)
9. **Key milestones** — project kickoff, design review, verification, FSC sign-off, release

### Step 2 — Read the reference docs

Before generating, read these if relevant to the open question:

- `references/methodology.md` — what a Safety Plan contains and why
- `references/iso26262_clause6_mapping.md` — how the 12 tabs map to Clause 6 sub-clauses
- `references/independence_levels.md` — I1/I2/I3 confirmation independence per ASIL (ISO 26262-2 Table 1)

### Step 3 — Build the input JSON

Construct a JSON file that conforms to the schema documented at the top of `scripts/generate_safety_plan.py`. A worked example lives in `examples/sample_safety_plan_esc.json` — start from it for any ADAS/chassis item.

The schema is forgiving: omit any field and the script auto-populates sensible defaults (e.g., standard clause tailoring, role templates, milestone stubs). The mandatory fields are `project.name` and `project.target_asil`.

### Step 4 — Generate

Run from a shell with Python and openpyxl:

```bash
python scripts/generate_safety_plan.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The first command produces the workbook. The second command recalculates any formulas so the file opens in Excel with computed values.

### Step 5 — Present and iterate

Present the resulting xlsx to the user and **explicitly call out what they should review**:

- The **Roles and Responsibilities** tab — does the independence level column match your team structure?
- The **Confirmation Reviews** tab — are the auto-suggested independence levels correct for your ASIL?
- The **Work Products** tab — do the 25 default work products align with your item scope, or do you need to add/remove items?
- The **Tools** tab — is the TCL classification (TCL1/2/3) justified for each tool per ISO 26262-8 Clause 11?
- The **Tailoring** tab — are there any clauses that should be marked "Partial" or "No" due to scope constraints?
- The **Schedule** tab — are the milestone dependencies and target dates realistic?

When the user asks for changes, modify the input JSON and regenerate rather than editing the xlsx directly. The xlsx is a derived artifact — the JSON is the source of truth.

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Project name, FSM, document ID, target ASIL, vehicle programs, suppliers |
| 01 | Document Control | Revision history and release record |
| 02 | Project Info | Summary of project context, key dates |
| 03 | Roles & Responsibilities | RACI table: FSM, PM, HW/SW leads, confirmation reviewer, assessor, customer; independence levels |
| 04 | Tailoring | Per ISO 26262 part/clause: Applicable (Yes/No/Partial) with justification |
| 05 | Work Products | Master list (25 items): WP_ID, name, ISO ref, owner, target ASIL, planned/actual dates, status |
| 06 | Confirmation Reviews | One row per WP: required independence (auto-suggested per ASIL), assigned reviewer, dates, status, notes |
| 07 | Tools | Tool name, vendor, version, usage, TCL classification (TCL1/2/3), TCL rationale, qualification status |
| 08 | Resources | HW resources, SW tool licenses, lab equipment, training plan |
| 09 | Anomaly Resolution | Anomaly tracker: ID, raised by, description, severity, owner, status, resolution |
| 10 | Schedule | Milestones: ID, name, target date, predecessors, status, notes |
| 11 | References | Standards (ISO 26262 parts 1–8), customer docs, internal procedures |

## Auto-suggested independence (ISO 26262-2 Table 1)

The Confirmation Reviews tab auto-populates the required independence level based on the work product's target ASIL:

| Target ASIL | Required Independence |
|---|---|
| QM | None (but recommended for traceability) |
| A | I1 (different person) |
| B | I1 (different person) |
| C | I2 (different team) |
| D | I3 (different organisational unit) |

The analyst is expected to verify that the assigned reviewer meets or exceeds this independence requirement.

## Work product categories (25 default items)

The script provides a complete default work product list covering ISO 26262 Parts 2–8:

**Part 2 (Management):**
- Safety Plan, Functional Safety Concept, Verification and Validation Plan, Development Plan, Project Plan

**Part 3 (Concept):**
- Item Definition, HARA, Safety Goals, Functional Safety Concept, FSC Review Report

**Part 4 (System):**
- System Architecture, Technical Safety Concept, TSC Review Report, System Verification Plan

**Part 5 (Hardware):**
- HW Architecture, HW Design Specification, FMEDA, HW Integration Test Plan, HW Verification Report

**Part 6 (Software):**
- SW Architecture, SW Unit Design Specification, SW Unit Verification, SW Integration Test Plan, SW Verification Report

**Part 7 (Production):**
- Production Plan, Modification Procedure, Service Data

**Part 8 (Analysis):**
- Functional Safety Analysis, Proof Test Report

When the user customizes the work product list, modify the input JSON and regenerate.

## Files in this skill

```
safety-plan-builder/
├── SKILL.md                                    # this file
├── scripts/
│   ├── generate_safety_plan.py                 # main generator
│   ├── recalc.py                               # LibreOffice formula recalc
│   └── office/
│       ├── soffice.py                          # LibreOffice helper
│       └── __init__.py
├── references/
│   ├── methodology.md                          # Safety Plan purpose and contents
│   ├── iso26262_clause6_mapping.md             # how tabs map to Clause 6
│   └── independence_levels.md                  # I1/I2/I3 per ASIL + justification
└── examples/
    └── sample_safety_plan_esc.json             # full ESC example to clone
```
