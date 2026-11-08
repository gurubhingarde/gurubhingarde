---
name: hara-builder
description: Generate an audit-ready ISO 26262 Hazard Analysis and Risk Assessment (HARA) workbook from an item definition and function list. Produces a multi-tab xlsx with assumptions, architecture boundary, the 14 malfunction guide words (M01-M14), operating environment, S/E/C reference tables, ASIL determination matrix, the Function-by-Malfunction safety-criticality filter, the full Cartesian HARA worksheet with auto-suggested S/E/C and formula-driven ASIL, a Safety Goals tab using the Prevent-the-hazard convention, and an FSC hand-off. Use this skill whenever the user mentions HARA, hazard analysis, ASIL determination, safety goal derivation, item definition, or ISO 26262 concept phase, even casual phrasings like 'I need the safety analysis for this ECU' or 'what is the ASIL for X'. Always use this skill instead of producing a freeform HARA in chat; the spreadsheet output is the deliverable analysts expect.
---

# HARA Builder

A Hazard Analysis and Risk Assessment (HARA) is the cornerstone of the ISO 26262 concept phase. This skill produces a complete, audit-ready HARA workbook by walking the analyst through item definition, function enumeration, and then doing the heavy mechanical work — building the Cartesian matrix of (function × malfunction × operating environment), auto-suggesting S/E/C ratings with rationale, computing ASIL via formula, and consolidating safety goals.

The skill is opinionated about **method**, not about **answers**. Every auto-suggested rating includes a rationale that the analyst is expected to challenge and refine. The ASIL is formula-driven so changing any S/E/C cell recomputes the result. The full Cartesian is preserved (including pruned/NSC rows) so the analysis is auditable end-to-end.

## When to use this skill

Use whenever the user wants to:
- Perform or update a HARA, hazard analysis, or hazard worksheet
- Determine ASILs for a system or item
- Derive safety goals from hazards
- Define safe states for an item
- Hand off concept-phase artifacts to the FSC author
- Build the documentation that supports an ISO 26262 concept-phase assessment

If the user only asks a conceptual ASIL question ("what's the ASIL of X?") and does not need a deliverable, you can answer from the reference docs without producing a workbook — but offer the workbook as the next step.

## Workflow

### Step 1 — Capture the item definition (interview)

Ask the user for these inputs in a small number of concise turns. Use the AskUserQuestion tool when present; otherwise just ask in chat. The minimum viable input:

1. **Item name and abbreviation** (e.g., "Electronic Stability Control / ESC")
2. **Project context** (project, doc ID, revision, date, author, approver)
3. **Scope description** — what the item does and explicitly does NOT do
4. **Functions** — list of item functions with a short description and a kinetic authority class. Kinetic authority is one of:
   - `high` — moves the vehicle longitudinally, laterally, or vertically with significant force
   - `medium` — modulates a high-authority actuator without owning it (e.g., torque request to powertrain ECU)
   - `low` — informational outputs (warning lamps, chimes, displays)
   - `none` — pure monitoring, no actuation
5. **External interfaces** (sensors in, actuators out, other ECUs)
6. **Assumptions** (vehicle class, market, driver, scope partitions like cybersecurity)
7. **Operating environment** — accept defaults from `references/operating_environments.md` unless the user wants to trim or add (e.g., highway-only items drop *off-road*; long-haul truck items add additional speed bands)

For the SC / NSC / NA classification of each (function × malfunction) pair, you can either let the script auto-suggest based on kinetic authority and adversarial-malfunction heuristics, or accept user-provided classifications. **Always offer the user a chance to review and override.** The SC filter is the most consequential analyst judgment in the whole HARA.

### Step 2 — Read the references

Before generating, read whichever of these are relevant to the open question:

- `references/malfunctions.md` — the 14 guide words, definitions, and the SC/NSC/NA filter heuristic. **Always read this on first invocation.**
- `references/severity_ais.md` — how to rate Severity against the AIS scale, including the speed-band heuristic.
- `references/exposure.md` — exposure rated against the OPERATIONAL SITUATION (not the hazard itself — this is the most common HARA mistake), with the location × weather lookup tables.
- `references/controllability.md` — controllability against the average driver, with reaction-time anchors.
- `references/asil_matrix.md` — the lookup table and the formula pattern used in the worksheet.
- `references/operating_environments.md` — default location and weather dimensions for the Cartesian expansion.
- `references/fsc_handoff.md` — what the FSC hand-off tab pre-populates and why.

### Step 3 — Build the input JSON

Construct an input JSON that conforms to the schema documented at the top of `scripts/generate_hara.py`. A worked example lives in `examples/sample_input_esc.json` — start from it for any ADAS/chassis item.

The schema is forgiving: omit any field you don't have and the script will auto-suggest sensible defaults. The mandatory fields are `item.name`, at least one entry in `functions`, and ideally the `function_malfunction_ratings` for the SC filter.

### Step 4 — Generate

Run from a shell that has Python, openpyxl, and (for formula recalc) LibreOffice available:

```bash
python scripts/generate_hara.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The first command produces the workbook and prints a JSON summary (function count, SC pair count, HARA row count, safety goal count). The second command evaluates the ASIL formulas so the file opens in Excel with computed values.

### Step 5 — Present and iterate

Present the resulting xlsx to the user and **explicitly call out what they should review**:

- The Function × Malfunction filter tab — does the SC/NSC/NA classification match their judgment?
- The HARA Worksheet — sample 5–10 rows and check the auto-suggested S/E/C and rationale. Do they hold up?
- The Safety Goals tab — does each safety goal correctly use the "Prevent <hazard>" form? Is the safe state appropriate?
- The FSC Hand-off tab — does the FSR pre-population make sense as a starting point?

When the user asks for changes, modify the input JSON and regenerate rather than editing the xlsx directly. The xlsx is a derived artifact — the JSON is the source of truth.

## Output structure (14 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Item, project, doc ID, revision, dates, approvers |
| 01 | Document Control | Revision history, distribution list |
| 02 | Assumptions | Vehicle, driver, market, lifecycle, scope-partition assumptions |
| 03 | Architecture Boundary | Item scope text, boundary diagram placeholder, external interface table |
| 04 | Functions | The item's functions with kinetic authority |
| 05 | Malfunctions | M01–M14 reference |
| 06 | Operating Environment | Locations × speed bands, weather/surface |
| 07 | Severity Reference | S0–S3 ↔ AIS bands |
| 08 | Exposure Reference | E0–E4 with operational-situation guidance (with the bold "exposure ≠ hazard frequency" reminder) |
| 09 | Controllability Reference | C0–C3 with reaction-time anchors |
| 10 | ASIL Matrix | The lookup table the HARA tab references |
| 11 | Function × Malfunction | The SC / NSC / NA filter; every (F × M) pair recorded |
| 12 | HARA Worksheet | The Cartesian: SC pairs × locations × weather, with formula-driven ASIL |
| 13 | Safety Goals | Consolidated SGs ("Prevent <hazard>") with safe states and worst-case ASIL |
| 14 | FSC Hand-off | Each SG with placeholder FSR rows, FTTI, allocation, decomposition |

## Auto-rating heuristics (and their limits)

The auto-suggester is implemented in Python in `generate_hara.py`. The heuristics:

- **Severity** — driven by the speed band of the location and the kinetic authority of the function. ≥100 km/h with a high-authority function defaults to S3; 60–100 km/h to S2; below 60 km/h to S1 unless the malfunction is adversarial (M03, M05, M07, M12) at moderate speed in which case S2.
- **Exposure** — combined location × weather, taking the rarer (lower) of the two default E values. The skill never rates E4 for combinations involving snow, ice, or fog.
- **Controllability** — a function of speed and whether the malfunction is adversarial. ≥100 km/h or adversarial-at-≥80 km/h defaults to C3; mid-speed defaults to C2.

These heuristics are **starting points, not answers**. The skill's value is the structured Cartesian + the rationale columns; the analyst's value is overriding the suggestions with project-specific judgment. When you (Claude) review the generated workbook, look for rows where the heuristic over- or under-estimates and propose specific overrides, then regenerate.

## Common pitfalls to flag for the user

1. **Conflating exposure with hazard frequency.** Exposure is about the operational situation. The probability of the failure itself is captured downstream by PMHF / FIT analysis. Re-read `references/exposure.md` if there's any doubt.
2. **Rating controllability for an expert driver.** The reference is the average non-expert driver. If the team's "everyone could just brake" intuition is doing the work, controllability is probably underrated.
3. **Dropping NSC rows from the worksheet.** The Function × Malfunction tab MUST show all 14 × N rows so reviewers can see what was considered. Pruning NSC rows is the most common audit finding.
4. **One safety goal per HARA row.** Wrong. Safety goals are consolidated by (function, hazard) — the worst-case ASIL across all environments governs. The Safety Goals tab does this consolidation automatically.
5. **Stopping at safety goals.** The FSC Hand-off tab is the bridge to the next phase. Even if you're not authoring the FSC today, having FTTI placeholders and FSR IDs assigned now saves rework.

## When the analyst pushes back on the heuristic

If the user says "this S rating is wrong" — do not argue. Add their override to the input JSON's `rating_overrides` array (keyed by function_id, malfunction_id, location_code, weather_code) and regenerate. The override flows into the worksheet with the user's rationale text preserved. If they want to change the suggester behavior more generally, edit the heuristic functions in `generate_hara.py` (`suggest_severity`, `suggest_exposure`, `suggest_controllability`) — but only after confirming with the user that the change should apply to all future HARAs.

## Files in this skill

```
hara-builder/
├── SKILL.md                                    # this file
├── scripts/
│   ├── generate_hara.py                        # main generator
│   ├── recalc.py                               # LibreOffice formula recalc
│   └── office/
│       └── soffice.py                          # LibreOffice helper (from xlsx skill)
├── references/
│   ├── malfunctions.md                         # M01–M14 + SC filter heuristic
│   ├── severity_ais.md                         # S0–S3 with AIS mapping + speed heuristic
│   ├── exposure.md                             # E0–E4 + the situation-vs-hazard-frequency note
│   ├── controllability.md                      # C0–C3 + reaction-time anchors
│   ├── asil_matrix.md                          # lookup table + formula pattern
│   ├── operating_environments.md               # Cartesian dimensions
│   └── fsc_handoff.md                          # what the FSC tab pre-populates
└── examples/
    └── sample_input_esc.json                   # full ESC example to clone for new items
```
