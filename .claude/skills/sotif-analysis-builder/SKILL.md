---
name: sotif-analysis-builder
description: Generate an audit-ready ISO 21448 SOTIF (Safety of the Intended Functionality) analysis workbook for ADAS/AV systems. Produces 12-tab xlsx covering item definition, ODD (Operational Design Domain), performance limitations, functional insufficiencies, triggering conditions, hazardous behaviors, scenario classification (Known Safe/Unsafe, Unknown Safe/Unsafe quadrants), and acceptance criteria per safety goal. Use this skill whenever analyzing scenarios where functions perform as designed but design is insufficient (sensor blinding, edge cases, algorithm limits) as distinct from random hardware faults (ISO 26262).
---

# SOTIF Analysis Builder

ISO 21448 addresses hazards from performance limitations of the intended functionality — the gap between specification and reality. This skill produces a structured analysis workbook for ADAS/AV systems: item definition, ODD scope, sensor/algorithm limitations, triggering conditions that expose insufficiencies, resulting hazardous vehicle behaviors, 4-quadrant scenario classification, and quantified acceptance criteria.

## When to use this skill

Use whenever analyzing ADAS/AV systems and the user wants to:
- Map the Operational Design Domain (ODD) where the system is supposed to work
- Enumerate performance limitations (sensor range, latency, algorithm edge cases)
- Identify functional insufficiencies (what the function cannot do despite correct design)
- Document triggering conditions (environmental, sensor, road user, system state) that cause insufficiency
- Classify scenarios as Known Safe / Known Unsafe / Unknown Safe / Unknown Unsafe
- Quantify residual risk acceptance criterion (e.g., unintended behavior rate <1e-7 per hour)

If the user describes hazards from random hardware failures use ISO 26262 (hara-builder) instead.

## Workflow

### Step 1 — Capture SOTIF scope (interview)

Ask for these inputs in concise turns:

1. **Target system** (AEB, LKAS, LCA, etc.) with abbreviation
2. **System functions** — list with descriptions (e.g., forward collision detection, autonomous emergency brake)
3. **Kinetic authority** per function (high/medium/low/none)
4. **Operational Design Domain (ODD)** — where the system is intended to operate:
   - **Scenery**: road type (highway, urban, rural), surfaces, geography
   - **Environment**: weather (dry, wet, snow, fog), lighting (day, night, dusk), visibility
   - **Dynamic elements**: other road users (cars, trucks, motorcycles, pedestrians, cyclists)
   - **Driver state**: alertness, handoff expectations
5. **Performance limitations per function** — sensor range, latency, algorithm confidence thresholds, known failure modes
6. **Acceptance criterion** — quantified safety goal (e.g., probability of unintended behavior < 1e-7 per operating hour)

### Step 2 — Read references

Before generating:
- `references/iso21448_clauses.md` — overview of §6 concept, §5 scenario taxonomy
- `references/methodology.md` — how to structure ODD, insufficiency root causes, quadrant logic

### Step 3 — Build input JSON

Construct input conforming to schema in `scripts/generate_sotif_analysis.py`. Example in `examples/sample_sotif_input_aeb.json`.

Minimal fields: system name, functions, ODD definition, performance limitations, insufficiencies, acceptance criteria.

### Step 4 — Generate

```bash
python scripts/generate_sotif_analysis.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

### Step 5 — Present and iterate

Present workbook. Highlight for review:
- ODD Definition tab — does it match system intent?
- Performance Limitations — complete enumeration?
- Triggering Conditions × Functional Insufficiencies matrix — coverage?
- Scenario Classification — are quadrant assignments defensible?
- Acceptance Criterion — is threshold achievable and justified?

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | System, project, doc ID, target functions |
| 01 | Document Control | Revision history |
| 02 | Item Definition Reference | Upstream item definition link + functions in scope |
| 03 | Functional Perf Spec | Per function: intended behavior, performance envelope, ODD constraints |
| 04 | ODD Definition | Scenery, environment, dynamic elements, driver state |
| 05 | Performance Limitations | Sensor range, latency, algorithm edge cases per function |
| 06 | Functional Insufficiencies | Algorithmic, sensor, actuator, system gaps |
| 07 | Triggering Conditions | Environmental, sensor, road user, system state, driver state, combined |
| 08 | Hazardous Behavior Catalog | (Function × Insufficiency × Triggering Condition) → hazardous vehicle behavior |
| 09 | Scenario Quadrants | Per scenario: Known Safe / Known Unsafe / Unknown Safe / Unknown Unsafe |
| 10 | Acceptance Criterion | Quantified target per safety goal |
| 11 | References | ISO 21448 clauses, NHTSA resources |

Always use this skill instead of producing a freeform SOTIF analysis in chat.
