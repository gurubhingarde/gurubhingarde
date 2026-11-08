---
name: cs-goals-builder
description: Generate an audit-ready ISO/SAE 21434 Cybersecurity Goals workbook from a TARA xlsx. Derives high-level security objectives from threat scenarios, assigns CAL (Cybersecurity Assurance Level 1-4), produces multi-tab workbook with CSG definition, CAL justification, asset mapping, and CSC handoff. Auto-suggests CAL based on risk value and impact; supports refinement JSON for custom CSG text and ownership. Use whenever the user mentions cybersecurity goals, threat-to-goal derivation, CAL assignment, or needs to hand off to security architecture phase. Always use this skill instead of producing freeform CSGs in chat.
---

# CS Goals Builder

Cybersecurity Goals (CSGs) are high-level security objectives derived from the threat scenarios identified in Threat Analysis and Risk Assessment (TARA). They follow the same conceptual pattern as safety goals in ISO 26262 HARA but address intentional threats rather than accidental failures.

The CS Goals Builder produces an audit-ready workbook translating TARA threat scenarios into formal CSGs, each assigned a Cybersecurity Assurance Level (CAL 1-4) and tied to a specific asset and cybersecurity property (Confidentiality, Integrity, Authenticity, Authorization, Non-Repudiation, Availability).

## When to use this skill

Use whenever the user wants to:
- Derive cybersecurity goals from a completed TARA
- Assign CAL (Cybersecurity Assurance Level) to threat scenarios
- Map CSGs to assets and cybersecurity properties
- Define the baseline for cybersecurity control (CSC) development
- Hand off to the Cybersecurity Concept phase
- Create audit-ready CSG documentation per ISO/SAE 21434 Concept Phase

If the user only asks a conceptual CAL question and does not need a deliverable, you can answer from the reference docs without producing a workbook — but offer the workbook as the next step.

## Workflow

### Step 1 — Prepare the TARA input

The prerequisite is a completed TARA xlsx containing high-risk threat scenarios. The builder reads:
- **Tab 11_Cybersecurity_Goals** if present (preferred; use as-is if already defined)
- **Tab 09_Risk_Determination** if no CSG tab (derives CSGs from Risk Value >= 3 rows)

The TARA must include:
- Threat scenario IDs and descriptions
- Asset affected by each threat
- Risk Value (1-5 scale)

### Step 2 — Optional: Create refinement JSON

If you want to override auto-suggested CSG text, adjust CAL assignments, or assign ownership, create a refinement JSON following the schema at the top of `scripts/generate_cs_goals.py`:

```json
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver},
  "target_cal": "CAL 3",
  "csg_refinements": [
      {threat_scenario_id, refined_goal_text, cal_adjust}
  ],
  "csg_overrides": [
      {csg_id, asset, property, owner}
  ]
}
```

A worked example lives in `examples/sample_cs_goals_input_esc.json` — start from it for any automotive item. The refinement JSON is optional; omit it and the script will auto-generate CSG text and CAL from TARA.

### Step 3 — Generate

Run from a shell with Python and openpyxl available:

```bash
cd /path/to/cs-goals-builder

# Minimal: TARA only (auto-generates CSG text and CAL)
python scripts/generate_cs_goals.py tara.xlsx output_goals.xlsx

# With refinement: apply custom CSG text and ownership
python scripts/generate_cs_goals.py tara.xlsx refinement.json output_goals.xlsx

# Then recalculate formulas if needed
python scripts/recalc.py output_goals.xlsx
```

The script produces JSON summary (tab count, CSG count, CAL distribution) and writes the workbook.

### Step 4 — Present and iterate

Review the resulting workbook and focus the user on:

- **03_Cybersecurity_Goals tab** — Does each CSG correctly capture the threat in "Prevent <X>" form? Is the property (C/I/A/Auth/Authz/NR) correct?
- **04_CAL_Determination tab** — Does the auto-suggested CAL reflect the risk and safety impact? Adjust if project context differs.
- **02_TARA_Echo tab** — Verify imported threat scenarios match your TARA.
- **06_CS_Concept_Handoff tab** — Pre-populated with CSG-to-CSC placeholder rows for the next phase.

When the user asks for changes, modify the refinement JSON and regenerate rather than editing the xlsx directly. The xlsx is a derived artifact — the JSON is the source of truth.

## Output structure (8 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Item, project, doc ID, revision, dates |
| 01 | Document Control | Revision history, approval |
| 02 | TARA Echo | Read-only import of threat scenarios for traceability |
| 03 | Cybersecurity Goals | One row per CSG: ID, threat ref, asset, goal text, CAL, property, owner |
| 04 | CAL Determination | Risk value, impact rating, CAL justification per CSG |
| 05 | Asset to CSG Map | Cross-reference matrix: assets vs. CSGs protecting them |
| 06 | CS Concept Handoff | Each CSG with placeholder CSC requirement rows for next phase |
| 07 | References | Normative references (ISO/SAE 21434, TARA, CAL definitions) |

## Cybersecurity property derivation

Every CSG is stated against one cybersecurity property. The property is **not**
carried on the TARA's `11_Cybersecurity_Goals` tab — it is implied by the STRIDE
category recorded per scenario on `05_Threat_Scenarios`, and the reader resolves
it by scenario ID using this mapping:

| STRIDE category | Cybersecurity property |
|---|---|
| Spoofing | Authentication |
| Tampering | Integrity |
| Repudiation | Non-repudiation |
| Information Disclosure | Confidentiality |
| Denial of Service | Availability |
| Elevation of Privilege | Authorization |

Precedence, highest first:

1. `property` on a `csg_overrides` entry in the refinement JSON — explicit analyst intent always wins.
2. The STRIDE mapping above.
3. `Not Determined` — written when the TARA has no `05_Threat_Scenarios` tab, the
   scenario is absent from it, or its STRIDE cell is empty or unrecognised. The
   builder warns on stderr in the first and last cases. It does **not** substitute
   a default property: a goal labelled with a property the TARA never claimed is
   worse than one visibly marked undetermined, because `cs-concept-builder` fans
   one CSR per goal *per property* and would inherit the invention.

Check the derived column in `03_Cybersecurity_Goals`; correct any row via a
`csg_overrides` entry rather than editing the xlsx.

## CAL auto-suggestion heuristic

The script applies:

- Risk Value 5 + Severe Safety Impact → **CAL 4**
- Risk Value 4 + Significant Impact → **CAL 3**
- Risk Value 3 + Moderate Impact → **CAL 2**
- Risk Value 1-2 + Low Impact → **CAL 1**

Suggestions appear in 04_CAL_Determination with rationale. Override in refinement JSON if project context warrants.

## CSG naming and structure

All CSGs follow the **Prevent <Threat>** pattern:
- Prevent unauthorized firmware modification
- Prevent CAN message spoofing affecting brake commands
- Prevent calibration data tampering
- Prevent debug interface unauthorized access

Each CSG is tied to:
- **Asset** (Firmware, CAN Bus, Sensor, etc.)
- **Cybersecurity Property** (Confidentiality, Integrity, Authenticity, Authorization, Non-Repudiation, Availability)
- **CAL** (1-4, color-coded in worksheet)
- **Ownership** (team responsible for CSC development)

## Common pitfalls to flag

1. **Not filtering for high-risk threats.** CSGs only address Risk Value >= 3; lower-value threats may not warrant formal goals.
2. **Over-specifying in CSG text.** CSGs are what to prevent, not how. Save implementation details for the CSC phase.
3. **Assigning CAL without justification.** Always document why a CSG received its CAL in 04_CAL_Determination.
4. **Stopping at CSGs.** The 06_CS_Concept_Handoff tab is the bridge to the next phase; CSG ownership and preliminary CSC mapping should be assigned now.

## Files in this skill

```
cs-goals-builder/
├── SKILL.md                                    # this file
├── scripts/
│   ├── generate_cs_goals.py                    # main generator
│   ├── tara_reader.py                          # TARA xlsx parser
│   ├── recalc.py                               # LibreOffice formula recalc
│   └── office/
│       ├── soffice.py                          # LibreOffice helper
│       └── __init__.py
├── references/
│   ├── methodology.md                          # CSG derivation from TARA
│   └── cal_assignment.md                       # CAL 1-4 criteria per ISO/SAE 21434
├── examples/
│   └── sample_cs_goals_input_esc.json          # ESC example (clone for new items)
```

## Key concepts

- **TARA** — Threat Analysis and Risk Assessment (input; identifies threats and risk values)
- **CSG** — Cybersecurity Goal (high-level security objective)
- **CAL** — Cybersecurity Assurance Level (1-4; rigor of required controls)
- **CSC** — Cybersecurity Control (technical requirement, derived from CSG; product of next phase)
- **Property** — Cybersecurity property protected (C/I/A/Auth/Authz/NR)

---

Always use this skill instead of producing freeform cybersecurity goals in chat.
