---
name: control-plan-builder
description: Generate an AIAG Production Control Plan xlsx from JSON input. Produces 13-tab workbook with title, document control, header block, process reference, main control plan worksheet, special characteristics (Critical/Significant/Standard color-coded), measurement system analysis plan, reaction plan library, SPC method allocation, mistake-proofing catalog, audit plan, PFMEA linkage, and references. Outputs IATF 16949-compliant manufacturing control documentation. Use this skill whenever the user mentions Control Plan, AIAG control plan, production control document, or manufacturing process control.
---

# Control Plan Builder

A Production Control Plan (CP) is the AIAG-defined operational document required by IATF 16949. It defines how each manufacturing characteristic is controlled on the production line. The CP takes its inputs from the Production FMEA (process failure modes) and special characteristics list, and outputs to the manufacturing floor with clear control methods, reaction plans, and audit schedules.

This skill generates a complete, audit-ready Control Plan workbook by walking the user through program and process definition, then automating worksheet population, MSA planning, SPC allocation, mistake-proofing documentation, and PFMEA cross-linking.

## When to use this skill

Use whenever the user wants to:
- Create or update a Production Control Plan (Prototype, Pre-launch, or Production type)
- Allocate control methods (SPC, 100% inspection, mistake-proofing) to characteristics
- Define reaction plans for out-of-control conditions
- Plan measurement system analysis for gages
- Document audit schedules for special characteristics
- Link control plan rows to PFMEA failure modes and RPN
- Generate IATF 16949 compliant manufacturing documentation

If the user only asks conceptual questions about CP structure, you can answer from the reference docs — but offer the workbook as the next step.

## Workflow

### Step 1 — Capture program and process scope (interview)

Ask for these inputs:

1. **Program** — program name, part name, part number, control plan type (Prototype/Pre-launch/Production), supplier, customer, core team contacts, doc ID, revision
2. **Process Steps** — list of manufacturing operations: step ID, operation description, equipment/device/jig
3. **Characteristics** — one per row: characteristic number, process step, type (Product/Process), special class (Critical/Significant/Standard), specification/tolerance, gage ID, sample size/frequency, control method, reaction plan ID
4. **Gages** — gage ID, name, type (Variable/Attribute), R&R method (Gage R&R/Attribute Agreement), target R&R %
5. **Reaction Plans** — reaction plan ID, title, trigger, steps, owner, escalation
6. **SPC Settings** — per characteristic flagged for SPC: chart type (Xbar-R, Xbar-S, p, np, c, u), subgroup size, out-of-control rules
7. **Mistake-Proofing** — poka-yoke device ID, characteristic protected, type (warning/prevention), test method, audit frequency

The skill has sensible defaults — if the user provides program + characteristics, the workbook can be generated.

### Step 2 — Read the references

Before generating, skim these if relevant:

- `references/methodology.md` — Control Plan types, AIAG layout, integration with PFMEA + MSA
- `references/control_method_taxonomy.md` — SPC charts, 100% inspection, poka-yoke, audit-based control
- `references/reaction_plan_templates.md` — standard reaction plans

### Step 3 — Build the input JSON

Construct a JSON file conforming to the schema at the top of `scripts/generate_control_plan.py`. A worked example lives in `examples/sample_control_plan_input_esc.json` — start from it for any production CP.

### Step 4 — Generate

Run from a shell with Python and openpyxl:

```bash
python scripts/generate_control_plan.py <input.json> <output.xlsx>
```

### Step 5 — Present and iterate

Present the resulting xlsx and explicitly call out what the user should review:

- Title Page — program info, approvals, doc ID, revision correct?
- Control Plan Worksheet — characteristics, control methods, and reaction plans complete?
- Special Characteristics Echo — Critical/Significant characteristics highlighted and prioritized?
- Measurement System Plan — gages, R&R methods, and targets defined?
- SPC Method Allocation — chart types and control limits specified?
- Reaction Plan Library — clear, time-bound steps for each reaction plan?
- Linkage to PFMEA — all characteristics cross-linked to PFMEA failure modes?

When the user asks for changes, modify the input JSON and regenerate.

## Output structure (13 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Program name, part, control plan type, supplier, customer, doc ID, approval lines |
| 01 | Document Control | Revision history and distribution |
| 02 | Header Block | AIAG standard header: control plan number, key contact, core team, dates, approvals |
| 03 | Process Reference | Links to upstream PFMEA, process flow diagram, special characteristics list |
| 04 | Control Plan Worksheet | Main AIAG worksheet: characteristics, spec/tolerance, gage, sample size/frequency, control method, reaction plan |
| 05 | Special Characteristics Echo | Read-only list of Critical/Significant characteristics per OEM convention |
| 06 | Measurement System Plan | Per gage: R&R method, target %, planned date, status |
| 07 | Reaction Plan Library | Standard reaction plans with detailed steps: stop production, quarantine, 100% sort, supplier escalation |
| 08 | SPC Method Allocation | Per characteristic flagged for SPC: chart type (Xbar-R, etc.), subgroup size, control limits, OOC rules |
| 09 | Mistake-Proofing Catalog | Poka-yoke devices: type, test method, audit frequency, owner |
| 10 | Audit Plan | Layered process audit (LPA): frequency per special class (Critical weekly, Significant bi-weekly, Standard monthly) |
| 11 | Linkage to PFMEA | Cross-reference matrix: CP characteristic → PFMEA failure mode → S/O/D → RPN |
| 12 | References | AIAG Control Plan, IATF 16949, ISO 7870 SPC, drawing/spec references |

## Color coding

- Special Characteristic **Critical** = Red (high-priority control)
- Special Characteristic **Significant** = Orange (medium-priority control)
- Special Characteristic **Standard** = Light yellow (routine control)

## Control method taxonomy

- **SPC (Statistical Process Control)** — Xbar-R (variables), Xbar-S (variables with unequal subgroups), p-chart (go/no-go), np-chart (attribute count), c-chart (defect count), u-chart (defect per unit)
- **100% Inspection** — visual, dimensional, functional test (100% ICT, FCT, etc.)
- **Mistake-Proofing (Poka-Yoke)** — prevention (stops process if characteristic out) or warning (alerts operator)
- **Audit-Based Control** — layered process audit per LPA frequency

## Standard reaction plans

1. **Stop Production & Quarantine** — Immediate halt, sort last batch, root cause, rework/scrap decision
2. **Containment & 100% Sort** — Hold current lot, 100% inspection/sorting, corrective action
3. **Supplier Escalation** — Notify supplier (if purchased item), hold further supply, expedite response
4. **Process Adjustment & Restart** — Adjust machine/gage/setup, confirm with pilot parts, resume production

## Sample Control Plan

The ESC ECU Production CP (in `examples/sample_control_plan_input_esc.json`) includes 8 process steps and 15 characteristics: PCB component placement accuracy (X/Y/theta, SPC Xbar-R), solder joint quality (visual + ICT, 100% inspection), FCT test pass/fail (100%), firmware version (attribute, 100% audit), label correctness (poka-yoke + audit). Critical characteristics (placement, solder) are audited weekly; Significant (FCT, firmware) bi-weekly; Standard (label) monthly.

## Files in this skill

```
control-plan-builder/
├── SKILL.md                                      # this file
├── scripts/
│   ├── generate_control_plan.py                  # main generator (13 tabs)
│   ├── recalc.py                                 # LibreOffice formula recalc
│   └── office/
│       ├── __init__.py
│       └── soffice.py                            # LibreOffice helper
├── references/
│   ├── methodology.md                            # Control Plan types, AIAG layout, PFMEA integration
│   ├── control_method_taxonomy.md                # SPC, 100%, poka-yoke, audit control methods
│   └── reaction_plan_templates.md                # standard reaction plans, escalation rules
└── examples/
    └── sample_control_plan_input_esc.json        # sample ESC ECU production CP input
```

Always use this skill instead of producing a freeform Control Plan in chat.
