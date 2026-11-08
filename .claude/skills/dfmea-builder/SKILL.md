---
name: dfmea-builder
description: Generate an audit-ready AIAG-VDA 2019 Design FMEA workbook from structured JSON input. Implements the 7-step process with Function Analysis, Failure Analysis, Risk Analysis using Severity/Occurrence/Detection ratings, and Action Priority (High/Medium/Low) lookup table instead of RPN multiplication. Produces 12-tab workbook with Structure Analysis, Function tree, main DFMEA worksheet (analyst-editable S/O/D with AP auto-computed), Action Plan Tracker, Special Characteristics, and Lessons Learned cross-reference. Uses color-coded AP cells (red=High, orange=Medium, green=Low) for risk visualization. Always use this skill instead of producing a freeform DFMEA in chat.
---

# DFMEA Builder

The Design FMEA (DFMEA) is the systematic analysis of potential failure modes in a design's functions, causes, effects, and the strategies to prevent, detect, or mitigate them. The AIAG-VDA 2019 edition replaces classical RPN (Severity × Occurrence × Detection) with a more transparent **Action Priority (AP)** approach based on a lookup table, recognizing that not all risk combinations are equally important.

## When to use this skill

Use this skill whenever the user wants to:
- Conduct a Design FMEA per AIAG-VDA 2019 harmonized methodology
- Analyze design failure modes, causes, effects, and customer impact
- Allocate risk mitigation strategies (prevention controls, detection controls)
- Identify Special Characteristics (SCs) for design and manufacturing control
- Generate a structured, auditable DFMEA workbook for OEM submission
- Track actions and their closure with residual risk assessment

## Workflow

### Step 1 — Prepare the DFMEA Input JSON

Gather design structure, functions, and failure modes in JSON format:

```json
{
  "program": {
    "name": "ESC ECU Design Rev C",
    "part_name": "Electronic Stability Control ECU",
    "part_number": "ESC-ECU-001",
    "model_year": "2027",
    "design_owner": "Controls Team",
    "doc_id": "DFMEA-ESC-001",
    "revision": "1.0",
    "date": "2025-04-29",
    "fmea_team": "Controls, Electrical, Systems",
    "customer": "OEM XYZ",
    "company": "Supplier Corp"
  },
  "structure": [
    {"id": "SYS-001", "level": "System", "name": "ESC ECU", "parent": null},
    {"id": "SS-001", "level": "Subsystem", "name": "Sensing Module", "parent": "SYS-001"}
  ],
  "functions": [
    {"id": "F001", "parent_id": "SYS-001", "function_statement": "Monitor wheel speed", "requirement_ref": "REQ-001"}
  ],
  "failure_modes": [
    {
      "id": "FM001",
      "focus_element_id": "SS-001",
      "function_id": "F001",
      "failure_mode": "Wheel speed sensor signal loss",
      "failure_effect_next": "Loss of vehicle speed feedback to main MCU",
      "failure_effect_user": "Potential loss of ESC function; safety critical",
      "severity": 9,
      "failure_cause": "Connector corrosion or wiring break",
      "occurrence": 4,
      "prevention_control": "Sealed connector design, potted connections",
      "detection_control": "CAN message timeout detection, on-board diagnostics",
      "detection": 8,
      "recommended_action": "Increase connector sealing specification and validate",
      "owner": "Electrical Lead",
      "target_date": "2025-06-30"
    }
  ]
}
```

### Step 2 — Understand the AIAG-VDA 7-Step Process

The DFMEA follows this structure:

1. **Planning & Preparation** — Define scope, team, schedule
2. **Structure Analysis** — System → Subsystem → Component hierarchy (Tab 03)
3. **Function Analysis** — Functional requirements and function tree (Tab 04)
4. **Failure Analysis** — Enumerate failure modes, causes, effects (Tab 05)
5. **Risk Analysis** — Severity (1–10), Occurrence (1–10), Detection (1–10), Action Priority lookup (Tab 05)
6. **Optimization** — Action planning, residual risk after mitigation (Tab 08)
7. **Results Documentation** — Sign-off, lessons learned (Tabs 10–11)

### Step 3 — Generate the DFMEA

```bash
python scripts/generate_dfmea.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The generator:
- Reads structure (system/subsystem/component), functions, and failure modes from JSON
- Builds 12-tab workbook with AIAG-VDA header block, structure and function trees
- Creates main DFMEA worksheet with all 7-step columns
- Populates Action Priority (AP) from S/O/D using AIAG-VDA Table P.1 lookup logic (H=High, M=Medium, L=Low)
- Colors AP cells: red for H, orange for M, green for L
- Generates Action Plan Tracker filtered from high/medium-priority items
- Includes Special Characteristics identification tab
- Provides Lessons Learned and cross-reference tab for family DFMEA alignment

### Step 4 — Analyst Review and Iteration

1. **03_Structure_Analysis** — Verify system/subsystem/component hierarchy matches design architecture
2. **04_Function_Analysis** — Confirm function statements reflect design intent and link to safety requirements
3. **05_DFMEA_Worksheet** — Main analysis. For each failure mode:
   - **Severity (1–10)** — See reference table; 9–10 are safety-critical, 7–8 are major degradation
   - **Occurrence (1–10)** — How likely is the cause to occur? Edit if you have failure rate data or design changes
   - **Detection (1–10)** — Can the design's built-in tests or manufacturing processes catch this failure before it reaches the customer?
   - **Action Priority** — Auto-computed from S/O/D. Red (High) requires immediate action; Medium and Low are tracked in action plan
4. **06_Special_Characteristics** — Identify design parameters and tolerances critical to prevent or detect failure modes
5. **08_Action_Plan_Tracker** — Capture owner, due date, and verification of closure for all medium/high-priority actions
6. **09_DFMEA_Summary_Statistics** — Review count of H/M/L items; if too many High, revisit design or add stronger controls

When done, save and re-run `recalc.py` to ensure all formulas and fill colors update correctly.

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Program, part name, part number, design owner, FMEA team |
| 01 | Document Control | Revision history |
| 02 | Header Block | AIAG-VDA standard header: subject, project, FMEA owner, customer, model years, FMEA ID, confidentiality, dates |
| 03 | Structure Analysis | System / Subsystem / Component hierarchy (AIAG-VDA Step 2) |
| 04 | Function Analysis | Function tree with requirement references (AIAG-VDA Step 3) |
| 05 | DFMEA Worksheet | Main analysis: FM → effect → cause → S/O/D → AP → action (AIAG-VDA Steps 4–5) |
| 06 | Special Characteristics | SCs identified from high-severity failure modes; classification and controls |
| 07 | Action Priority Lookup | AIAG-VDA Table P.1: S × O × D → H/M/L with color coding |
| 08 | Action Plan Tracker | Gantt-style tracker for medium/high-priority actions; owner, due date, status |
| 09 | DFMEA Summary Statistics | Count and distribution of AP=H/M/L items |
| 10 | Lessons Learned & Crossref | Links to prior DFMEAs, family DFMEA, similar designs for reuse of solutions |
| 11 | References | AIAG-VDA 2019 methodology, ISO 26262 (if safety-related), OEM requirements |

## Key formulas and logic

**Action Priority (AP)** is determined by the AIAG-VDA simplified rule:
- **AP = High** if (S >= 9) OR (S >= 7 AND O >= 4) OR (S >= 4 AND O >= 7 AND D >= 7)
- **AP = Medium** if (S >= 4 AND O >= 4) OR (S >= 7) OR (O >= 7 AND D >= 7)
- **AP = Low** otherwise

This approach recognizes that severity drives priority. A single very severe failure (S=10) is always High-priority, even if occurrence is low. Conversely, a low-severity item (S≤3) is always Low-priority regardless of occurrence or detection, because the customer impact is negligible.

## Files in this skill

```
dfmea-builder/
├── SKILL.md
├── scripts/
│   ├── generate_dfmea.py                     # main generator (JSON → DFMEA xlsx)
│   ├── recalc.py
│   └── office/soffice.py + __init__.py
├── references/
│   ├── methodology.md
│   ├── aiag_vda_severity_table.md
│   ├── aiag_vda_occurrence_table.md
│   ├── aiag_vda_detection_table.md
│   └── action_priority_table.md
└── examples/
    └── sample_dfmea_input_esc.json          # ESC ECU example to clone
```

## Common pitfalls to avoid

1. **Confusing Severity with Occurrence.** Severity is what happens if the failure occurs (e.g., loss of life = S=10). Occurrence is how often the cause is likely to happen (e.g., manufacturing defect in 1 of 100 units = O=5). They are independent.

2. **Unrealistic Detection ratings.** A design test or on-board diagnostic can only detect a failure if (a) the failure actually produces a detectable symptom, and (b) the test is always run before the customer sees the failure. "Assumed 100% detection" without evidence is a red flag.

3. **Forgetting the function tree.** Don't just enumerate failure modes arbitrarily. Start with the design's stated functions (e.g., "monitor wheel speed"). Then ask: what are the ways this function can fail? This ensures you don't miss critical modes and you trace effects correctly.

4. **Mixing up Action Priority.** AP is not a formula like RPN. It is a table lookup that prioritizes by severity first. A failure with S=9, O=1, D=1 is AP=High because severity dominates. A failure with S=3, O=10, D=10 is AP=Low because low severity has low customer impact.

5. **Not tracking actions.** DFMEA is only useful if you close the loop. Every recommended action must have an owner, due date, and verification of closure. Untracked items are ignored.
