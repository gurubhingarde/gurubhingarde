---
name: safety-gate-review-builder
description: Generate an audit-ready safety gate review record workbook for ISO 26262 and ISO 21434 phase-gate reviews capturing entry criteria, required deliverables, exit criteria, action items, and Go/Conditional/No-Go decisions for concept exit, system design exit, hardware exit, software exit, integration exit, validation exit, and release gates.
---

# Safety Gate Review Builder

Phase-gate reviews align to ISO 26262-2 milestones and ensure that all entry criteria are satisfied, required deliverables are complete, and exit criteria are met before progressing to the next development phase. This skill produces an audit-ready Gate Review Record workbook.

## When to use this skill

Use whenever the user wants to:
- Create or update a safety gate review record per ISO 26262-2 Clause 8.2
- Document entry criteria, deliverables, and exit criteria for any phase gate
- Capture gate decisions (Go/Conditional/No-Go) with justification
- Track action items and open risks discovered at the gate
- Generate audit-ready gate review documentation

## Workflow

### Step 1 — Identify the gate

Ask for:

1. **Gate milestone** (Concept Exit, System Design Exit, HW Exit, SW Exit, Integration Exit, Validation Exit, Release)
2. **Project name and document ID**
3. **Target ASIL**
4. **Gate scope** (which work products/activities are covered)

### Step 2 — Build input JSON

Create input.json conforming to the schema in `scripts/generate_gate.py`.

### Step 3 — Generate

```bash
python scripts/generate_gate.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

### Step 4 — Present

Display the output xlsx to the user highlighting:
- The **Entry Criteria Checklist** tab — are all entry criteria satisfied?
- The **Deliverable Inventory** tab — are all required work products present and complete?
- The **Exit Criteria** tab — are all exit criteria measurable and met?
- The **Decision Record** tab — is the gate decision (Go/Conditional/No-Go) documented and signed?

## Output structure (10 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Gate milestone, project, scope, ASIL, gate date |
| 01 | Document Control | Revision history |
| 02 | Gate Identification | Which milestone, scope, target ASIL, predecessors |
| 03 | Entry Criteria Checklist | Rows: criterion, satisfied (Y/N), evidence, reviewer |
| 04 | Deliverable Inventory | Required WPs per Safety Plan, present (Y/N), quality status |
| 05 | Exit Criteria | Measurable criteria per phase, met (Y/N), evidence |
| 06 | Action Items | Opened during gate, owner, due date, priority |
| 07 | Open Risks Reference | Link to open programmatic risks that may impact phase completion |
| 08 | Decision Record | Gate decision (Go/Conditional/No-Go), attendees, signatures |
| 09 | References | ISO 26262-2 Clause 8, phase tailoring, relevant standards |

## Files in this skill

```
safety-gate-review-builder/
├── SKILL.md
├── scripts/
│   ├── generate_gate.py
│   ├── recalc.py
│   └── office/
├── references/
│   ├── methodology.md
│   └── gate_criteria.md
└── examples/
    └── sample_gate_review.json
```
