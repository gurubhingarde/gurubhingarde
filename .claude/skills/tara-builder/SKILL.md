---
name: tara-builder
description: Generate an audit-ready ISO/SAE 21434 Clause 15 Threat Analysis and Risk Assessment (TARA) workbook from threat scenarios and feasibility ratings. Produces a 13-tab xlsx with assumptions, asset inventory, STRIDE threat catalog, impact/feasibility analysis, risk determination matrix, treatment decisions, and derived cybersecurity goals. Use this skill whenever the user mentions TARA, threat analysis, ISO/SAE 21434, cybersecurity risk assessment, attack scenarios, or threat modeling for automotive items, even casual phrasings like 'I need the cyber risk assessment' or 'what are the threats to this ECU'. Always use this skill instead of producing freeform TARA analysis in chat; the spreadsheet output is the audit-ready deliverable security teams expect.
---

# TARA Builder

TARA (Threat Analysis and Risk Assessment) per ISO/SAE 21434 Clause 15 is the cybersecurity analog of HARA. It identifies threats, rates their impact and attack feasibility, determines risk via a lookup matrix, and specifies treatment decisions (Avoid/Reduce/Share/Retain) per Cybersecurity Assurance Level (CAL).

This skill produces a complete, audit-ready TARA workbook by walking the analyst through asset identification, STRIDE-based threat enumeration, impact and feasibility rating, and treatment selection. Every rating includes rationale; all formulas are formula-driven so changes recompute risk instantly.

## When to Use This Skill

Use whenever the user wants to:
- Perform or update a TARA, threat analysis, or cybersecurity risk assessment
- Identify threats to a vehicle item or system (ECU, gateway, telematics, OTA)
- Rate threat impact across Safety, Financial, Operational, Privacy dimensions
- Assess attack feasibility based on elapsed time, expertise, knowledge, opportunity, equipment
- Determine risk via Impact × Feasibility lookup
- Derive cybersecurity goals from high-risk threats
- Select risk treatment (Avoid, Reduce, Share, Retain) per CAL target
- Build the documentation that supports an ISO/SAE 21434 compliance assessment

If the user only asks a conceptual question ("what's a STRIDE threat?") and does not need a deliverable, you can answer from reference docs without producing a workbook — but offer the workbook as the next step.

## Workflow

### Step 1 — Capture the Item and Scope (Interview)

Ask the user for these inputs in a small number of turns. Use the AskUserQuestion tool when present; otherwise just ask in chat. Minimum viable input:

1. **Item name and abbreviation** (e.g., "Electronic Stability Control / ESC")
2. **Project context** (project, doc ID, revision, date, author, approver)
3. **Target Cybersecurity Assurance Level (CAL)** — one of 1, 2, 3, 4 per ISO/SAE 21434
4. **Scope description** — what the item is, what it does, and explicitly what it does NOT do
5. **Cyber-relevant interfaces** — CAN, OBD-II, OTA, debug ports, wireless, telematics
6. **Assumptions** — attacker model, environmental constraints, development/supply-chain scope
7. **Assets** — firmware, calibration, keys, credentials, sensor data, configuration, DTCs

For the SC / NSC classification of each (asset × STRIDE threat), you can either let the script auto-suggest based on asset type and cybersecurity property, or accept user-provided threat scenarios. **Always offer the user a chance to review and override.** The threat scenario filter is the most consequential analyst judgment in the whole TARA.

### Step 2 — Read the References

Before generating, read whichever of these are relevant to the open question:

- `references/methodology.md` — the 7-step TARA process per ISO/SAE 21434. **Always read this on first invocation.**
- `references/stride_taxonomy.md` — STRIDE threat categories (Spoofing, Tampering, Repudiation, Info Disclosure, Denial of Service, Elevation of Privilege) with examples and threat agent classification.
- `references/impact_rating_table.md` — how to rate Impact across Safety (AIS), Financial, Operational, Privacy using Severe / Major / Moderate / Negligible.
- `references/feasibility_rating_table.md` — how to rate Attack Feasibility using five factors (Elapsed Time, Expertise, Knowledge, Opportunity, Equipment) with lookups.
- `references/risk_determination_matrix.md` — the Impact × Feasibility lookup table producing Risk Value 1–5, with treatment guidance per CAL.
- `references/cal_levels.md` — CAL 1–4 definitions, threat models, and use cases.

### Step 3 — Build the Input JSON

Construct an input JSON that conforms to the schema documented at the top of `scripts/generate_tara.py`. A worked example (ESC ECU with 15 threat scenarios) lives in `examples/sample_tara_input_esc.json` — start from it for any ADAS/powertrain/body item.

The schema is forgiving: omit any field you don't have and the script will auto-suggest sensible defaults. The mandatory fields are `item.name`, `target_cal`, at least one entry in `assets`, and ideally at least one entry in `threat_scenarios`.

### Step 4 — Generate

Run from a shell that has Python and openpyxl available:

```bash
python scripts/generate_tara.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The first command produces the workbook and prints a JSON summary (asset count, threat scenario count, high-risk scenario count, risk distribution). The second command evaluates any formulas so the file opens in Excel with computed values.

### Step 5 — Present and Iterate

Present the resulting xlsx to the user and **explicitly call out what they should review**:

- The **Asset Inventory tab** — does the list of assets (firmware, calibration, keys, credentials, sensor data) match their understanding?
- The **Threat Scenarios tab** — does the STRIDE enumeration cover all major attack surface? Are threat agents (casual hacker, skilled attacker, insider, organized crime, nation-state) correctly classified?
- The **Impact Assessment tab** — sample 5–10 rows and check the Severe / Major / Moderate / Negligible ratings across Safety, Financial, Operational, Privacy. Do they hold up? Is worst-case impact accurate?
- The **Feasibility Rating tab** — verify the five-factor scoring (Elapsed Time, Expertise, Knowledge, Opportunity, Equipment) produces the correct overall feasibility rating (Very Low / Low / Medium / High).
- The **Risk Determination tab** — spot-check Risk Values (1–5) from Impact × Feasibility. Spot-check color coding (red = critical, orange = high, yellow = medium, green = low).
- The **Cybersecurity Goals tab** — does each Risk ≥ 3 scenario produce a well-formed CSG ("Prevent <threat>")? Is CAL assignment appropriate?
- The **Risk Treatment tab** — does each risk mitigation strategy (Avoid/Reduce/Share/Retain) match the CAL target and residual risk acceptance?

When the user asks for changes, modify the input JSON and regenerate rather than editing the xlsx directly. The xlsx is a derived artifact — the JSON is the source of truth.

## Output Structure (13 Tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Item, project, doc ID, revision, dates, approver, target CAL |
| 01 | Document Control | Revision history, distribution list |
| 02 | Assumptions | Attacker model, environment, scope-partition assumptions |
| 03 | Item Description | Item scope, cyber-relevant interfaces (CAN, OBD-II, OTA, debug) |
| 04 | Asset Inventory | Asset ID, name, location, type, cybersecurity properties (C/I/A/Auth/Authz/NR) |
| 05 | Threat Scenarios | Scenario ID, asset, STRIDE category, threat description, threat agent |
| 06 | Impact Assessment | Per scenario: Impact rating across Safety / Financial / Operational / Privacy (each Severe/Major/Moderate/Negligible), worst-case impact, rationale |
| 07 | Attack Path Analysis | Per scenario: entry point, attack vector (physical/local/adjacent/network), preconditions, propagation steps, exit point |
| 08 | Feasibility Rating | Per scenario: Elapsed Time (days/weeks/months/year+), Expertise, Knowledge, Opportunity, Equipment. Feasibility (Very Low/Low/Medium/High) via lookup |
| 09 | Risk Determination | Per scenario: Impact × Feasibility → Risk Value 1–5 via lookup table. Color-coded (red 5, orange 4, yellow 3, green 2–1) |
| 10 | Risk Treatment | Per scenario: Treatment decision (Avoid/Reduce/Share/Retain), rationale, residual risk acceptable Y/N, owner, target date |
| 11 | Cybersecurity Goals | High-Risk (Risk ≥ 3) scenarios → CSGs using "Prevent <threat>" convention. Assigned CAL per risk value |
| 12 | References | ISO/SAE 21434, STRIDE, standards, related methodologies |

## Auto-rating Heuristics (and Their Limits)

TARA auto-rating is limited. The skill requires user-supplied Impact and Feasibility ratings in the JSON; it does NOT auto-suggest. The principle: every rating must be explicit and justified in the worksheet.

However, the JSON schema is permissive: if a threat scenario lacks impact and feasibility data, the generator will assign default "Moderate" / "Medium" and warn the user. **Always review and override defaults.**

## Common Pitfalls to Flag for the User

1. **Confusing threat severity with hazard severity.** TARA assesses cyber attacks (attacker capability); HARA assesses failures (driver reaction). A "Major" impact threat might have an "Easy" feasibility if the attacker has physical OBD-II access.

2. **Underrating attacker capability.** Default threat model assumes skilled attacker with 3+ months and standard equipment. If the threat is to a connected telematics system, assume network-accessible attacks (High feasibility).

3. **Missing assets.** Firmware, calibration, keys, credentials, and sensor data are distinct assets with different cybersecurity properties. Omitting keys or credentials is common but fatal to TARA completeness.

4. **One treatment per risk.** Wrong. Risk 5 may require multiple mitigations (crypto + access control + detection). Risk treatment is a strategy, not a single action. Document all mitigations in the rationale column.

5. **Stopping at risk determination.** CSG derivation is the bridge to the next phase (Cybersecurity Concept, CSR development). Risk ≥ 3 scenarios MUST produce CSGs.

6. **CAL assignment mismatch.** CAL 4 items cannot retain Risk ≥ 2; CAL 1 items can retain Risk ≤ 5. Verify CAL target and treatment alignment on the Risk Treatment tab.

## When the Analyst Challenges a Rating

If the user says "this Impact is wrong" or "this Feasibility doesn't match our threat model" — do not argue. Add their override to the input JSON (impact_ratings, feasibility_ratings, risk_overrides arrays) and regenerate. The override flows into the worksheet with the user's rationale preserved.

If they want to change the heuristic more generally (e.g., "all CAL 3 items must have Risk ≤ 2"), modify the risk_overrides array to enforce the policy across multiple scenarios, then regenerate.

## Files in This Skill

```
tara-builder/
├── SKILL.md                                    # this file
├── scripts/
│   ├── generate_tara.py                        # main generator (openpyxl, STRIDE, Risk lookup)
│   ├── recalc.py                               # LibreOffice formula recalc
│   └── office/
│       ├── soffice.py                          # LibreOffice helper
│       └── __init__.py
├── references/
│   ├── methodology.md                          # 7-step TARA process per ISO/SAE 21434
│   ├── stride_taxonomy.md                      # STRIDE threat categories + threat agent classification
│   ├── impact_rating_table.md                  # Severe/Major/Moderate/Negligible across S/F/Op/Pr
│   ├── feasibility_rating_table.md             # Five-factor scoring (Elapsed Time, Expertise, Knowledge, Opportunity, Equipment)
│   ├── risk_determination_matrix.md            # Impact × Feasibility lookup → Risk Value 1–5
│   └── cal_levels.md                           # CAL 1–4 definitions + use cases
└── examples/
    └── sample_tara_input_esc.json              # ESC ECU example with 15 threat scenarios
```

Always use this skill instead of producing a freeform TARA in chat.
