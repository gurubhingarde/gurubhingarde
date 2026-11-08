---
name: pfmea-builder
description: Generate an AIAG-VDA Process FMEA (manufacturing-focused) workbook from a JSON input file. Analyzes manufacturing process steps (SMT placement, reflow, ICT, conformal coat, assembly) for failure modes, allocates severity/occurrence/detection ratings, and computes Action Priority using the standard AIAG-VDA lookup table. Produces a 13-tab workbook with title page, process flow analysis, failure mode enumeration, AP-ranked worksheet (color-coded H/M/L), special characteristics, and linkage to Control Plan. All AP cells auto-computed from S/O/D editable ratings per AIAG-VDA methodology. Always use this skill instead of producing a freeform PFMEA in chat.
---

# PFMEA Builder

The Process Failure Mode, Effects, and Analysis (PFMEA) is the manufacturing counterpart to DFMEA. It is the systematic tool that identifies potential failure modes in manufacturing process steps (e.g., SMT placement, reflow solder, ICT test, conformal coat, final assembly) and prioritizes corrective actions by severity, occurrence, and detection ratings. The PFMEA is required by AIAG-VDA, IATF 16949, and ISO/TS 16949 for every production process, and feeds directly into the Control Plan.

## When to use this skill

Use whenever you need to:
- Conduct a Process FMEA per AIAG-VDA Handbook (2019)
- Analyze manufacturing process steps for failure modes
- Rate failure modes by Severity (customer impact), Occurrence (defect frequency), Detection (inspection capability)
- Compute Action Priority from S/O/D using AIAG-VDA lookup table
- Identify special characteristics (SC) and control methods for high-priority failure modes
- Hand off a defensible process analysis to the Control Plan team

Prerequisites:
- A manufacturing process flow (sequence of steps, equipment, key characteristics)
- Process function requirements (what each step must accomplish)
- Identification of potential failure modes per process step (may be sourced from prior FMEAs, design DFMEA, pilot production, or failure history)

## Workflow

### Step 1 — Define the Manufacturing Process Flow

Gather process information in a JSON file. Include all significant steps from receipt of raw materials through final shipment. Each step specifies:
- Step ID (unique identifier, e.g., PST-01, PST-02)
- Step name (e.g., "PCB Receive & Inspection", "SMT Component Placement")
- Step type (Operation, Inspection, Move, Storage, Decision)
- Upstream and downstream steps (for traceability)
- Equipment used
- Key characteristics produced (electrical, dimensional, visual)
- Key parameters (temperature, timing, pressure)

Example for electronics manufacturing:
- PST-01: PCB Receive & Inspection
- PST-02: SMT Component Placement
- PST-03: Reflow Solder
- PST-04: Automated Optical Inspection (AOI)
- PST-05: ICT (In-Circuit Test)
- PST-06: Conformal Coat
- PST-07: Final Assembly
- PST-08: Functional Test (FCT)
- PST-09: Programming
- PST-10: Pack & Ship

### Step 2 — Define Process Functions and Characteristics

For each process step, specify:
- The function (what it must accomplish, e.g., "Place all resistors within tolerance and correct orientation")
- The requirement (specification or standard, e.g., "IPC-A-610 Class A")
- Product/process characteristics affected (e.g., "component placement accuracy", "solder joint quality")
- Special Characteristic flag (SC for safety/performance-critical, CC for customer-critical)

### Step 3 — Enumerate Failure Modes

For each process step, identify potential failure modes (how the step could fail to accomplish its function). Typical failure modes include:
- Wrong component placed or missing
- Component placed in wrong orientation
- Cold solder joint or bridge short
- Test failure (false negative)
- Labeling or serialization error
- Packaging damage

Record for each failure mode:
- Step ID (which process step)
- Failure mode description
- Failure effect on next operation (how it propagates downstream)
- Failure effect on end user (final impact if not caught)
- Severity rating (1-10, based on customer impact per AIAG-VDA table)
- Potential cause (root cause)
- Occurrence rating (1-10, based on defect frequency per AIAG-VDA table)
- Prevention control (design or process control that prevents the failure)
- Detection control (inspection method that catches the failure)
- Detection rating (1-10, based on capability of detection method per AIAG-VDA table)

### Step 4 — Generate the PFMEA Workbook

Use the generator to produce the workbook:

```bash
python scripts/generate_pfmea.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The generator:
- Creates 13 tabs (see Output structure below)
- Populates title page and document control
- Creates process flow diagram (table format) with step relationships
- Analyzes process functions and special characteristics
- Builds the main PFMEA worksheet with one row per failure mode
- Computes Action Priority from S/O/D using AIAG-VDA lookup table
- Color-codes AP cells: red for High (H), yellow for Medium (M), green for Low (L)
- Links failure modes to control methods and characteristics for Control Plan handoff
- Generates tracking tabs for open actions and lessons learned

### Step 5 — Review, Update, and Iterate

1. **Process Flow tab** — Verify that all process steps are identified, in correct sequence, with clear upstream/downstream links.
2. **Process Function Analysis tab** — Confirm that each function is clear, requirements are realistic, and special characteristics are properly flagged.
3. **PFMEA Worksheet (05)** — The main analysis tab. For each failure mode row:
   - Verify Severity rating reflects customer impact (higher if escapes to customer)
   - Verify Occurrence rating reflects defect frequency (based on pilot data, yield history, or baseline capability)
   - Verify Detection rating reflects inspection method capability (100% automated inspection = lower D, visual inspection = higher D)
   - Watch Action Priority auto-compute from S/O/D
4. **Special Characteristics tab** — Identify SCs (safety/performance) and CCs (customer requirements). Specify control methods (100% inspection, SPC, mistake-proofing).
5. **Summary Statistics tab** — Count high, medium, low priority items. If too many H-rated items, either (a) increase detection capability, (b) add prevention controls, or (c) escalate to design/process engineering.
6. **Action Plan Tracker tab** — Record recommended actions, owners, target dates, and completion status.
7. **Linkage to Control Plan tab** — Map each high-priority failure mode to its corresponding Control Plan control method and acceptance criteria. This is the formal handoff to manufacturing operations.

When satisfied, save the workbook and run `recalc.py` to confirm all formulas are clean.

## Output structure (13 tabs)

| Tab | Name | Purpose |
|-----|------|---------|
| 00 | Title Page | Program, process name, responsibility, model year, doc ID, team |
| 01 | Document Control | Revision history (prepared by, date, changes) |
| 02 | Header Block | AIAG-VDA standard header fields (system, process, flow chart ref, dates) |
| 03 | Process Flow | Table of all process steps: ID, name, type, upstream/downstream, equipment, characteristics, parameters |
| 04 | Process Function Analysis | Per step: function, requirement, characteristic, SC/CC flag |
| 05 | PFMEA Worksheet | Main tab, one row per failure mode. Columns: step, function, failure mode, effects (next op + end user), Severity, cause, Occurrence, prevention control, detection control, Detection, Action Priority (color-coded), recommended action, owner, status. Revised S/O/D/AP columns for tracking iterations. |
| 06 | Special Characteristics | Characteristics flagged SC or CC, classification, source step, recommended control method (100% inspect, SPC, poka-yoke), monitoring plan |
| 07 | Action Priority Lookup | AIAG-VDA static table: S x O x D -> AP (H/M/L). Reference for verification. |
| 08 | Action Plan Tracker | Recommended actions: description, owner, target date, status, % complete |
| 09 | Summary Statistics | Counts of failure modes by AP priority, total steps, total modes, completion % |
| 10 | Linkage to Control Plan | Cross-reference matrix: PFMEA failure mode + control method -> Control Plan characteristic + acceptance criteria |
| 11 | Lessons Learned Crossref | Links to prior PFMEAs, family studies, or similar processes; lessons to apply |
| 12 | References | AIAG-VDA Handbook, customer specs, related documents |

## Input JSON schema

```json
{
  "program": {
    "name": "ESC ECU Brake System",
    "process_name": "PCB Assembly and Test",
    "process_responsibility": "Manufacturing Engineering",
    "model_year": "2026",
    "doc_id": "PFMEA-ESC-001",
    "revision": "1.0",
    "date": "2026-04-29",
    "fmea_owner": "John Doe",
    "fmea_team": "John Doe, Jane Smith, Bob Johnson",
    "customer": "OEM",
    "company": "XYZ Electronics"
  },
  "process_flow": [
    {
      "step_id": "PST-01",
      "step_name": "PCB Receive and Inspection",
      "step_type": "Inspection",
      "upstream_step": "Supplier",
      "downstream_step": "PST-02",
      "equipment": "Visual inspection station",
      "key_characteristics": "PCB trace continuity, pad cleanliness",
      "key_parameters": "Visual standard per IPC-A-610"
    },
    {
      "step_id": "PST-02",
      "step_name": "SMT Component Placement",
      "step_type": "Operation",
      "upstream_step": "PST-01",
      "downstream_step": "PST-03",
      "equipment": "Pick-and-place machine",
      "key_characteristics": "Component placement accuracy, orientation",
      "key_parameters": "X/Y tolerance 0.1mm, rotation 0.5 deg"
    }
  ],
  "process_functions": [
    {
      "step_id": "PST-01",
      "function": "Verify PCB integrity before assembly",
      "requirement": "No trace damage, pad cleanliness Class A per IPC-A-610",
      "characteristic": "PCB trace continuity, pad cleanliness",
      "special_characteristic": "SC"
    },
    {
      "step_id": "PST-02",
      "function": "Place all components in correct position and orientation",
      "requirement": "IPC-A-610 Class A placement accuracy",
      "characteristic": "Component placement accuracy",
      "special_characteristic": "SC"
    }
  ],
  "failure_modes": [
    {
      "step_id": "PST-02",
      "process_step": "SMT Component Placement",
      "process_function": "Place all components in correct position and orientation",
      "failure_mode": "MCU placed in wrong orientation",
      "failure_effect_next_op": "Reflow solder will not achieve proper joint; component may be damaged",
      "failure_effect_end_user": "Device will not boot; likely warranty return",
      "severity": 8,
      "failure_cause": "Pick-and-place calibration lost or operator error",
      "occurrence": 4,
      "prevention_control": "Daily machine calibration, machine vision verification",
      "detection_control": "AOI (Automated Optical Inspection) before reflow",
      "detection": 2,
      "recommended_action": "Implement daily offset verification routine",
      "owner": "Manufacturing Engineering",
      "target_date": "2026-05-15",
      "status": "Open"
    },
    {
      "step_id": "PST-03",
      "process_step": "Reflow Solder",
      "process_function": "Melt solder and form reliable electrical/mechanical joints",
      "failure_mode": "Cold solder joint (insufficient wetting)",
      "failure_effect_next_op": "Joint may fail during vibration test; open circuit risk",
      "failure_effect_end_user": "Intermittent failures in field; difficult to diagnose",
      "severity": 8,
      "failure_cause": "Reflow oven temperature profile out of spec; solder paste dried",
      "occurrence": 3,
      "prevention_control": "Reflow profile monitoring (SPC), paste shelf-life control",
      "detection_control": "X-ray inspection (sample), cross-section analysis",
      "detection": 4,
      "recommended_action": "Implement continuous reflow monitoring and paste dating",
      "owner": "Manufacturing Engineering",
      "target_date": "2026-05-20",
      "status": "Open"
    }
  ]
}
```

## Files in this skill

```
pfmea-builder/
├── SKILL.md
├── scripts/
│   ├── generate_pfmea.py         # Main generator (input JSON -> output XLSX with 13 tabs)
│   ├── recalc.py                 # Recalculation helper (verify formulas, clean errors)
│   └── office/soffice.py + __init__.py
├── references/
│   ├── methodology.md            # AIAG-VDA PFMEA process and integration points
│   ├── process_step_taxonomy.md  # Typical PCB/electronics manufacturing steps
│   ├── aiag_vda_pfmea_severity_table.md
│   ├── aiag_vda_pfmea_occurrence_table.md
│   ├── aiag_vda_pfmea_detection_table.md
└── examples/
    └── sample_pfmea_input_esc.json    # ESC ECU PFMEA example
```

## Common pitfalls to flag

1. **Severity without customer impact.** Severity rates how the end customer is affected. A defect caught 100% before shipment has low severity (customer never sees it). A defect that escapes and causes a warranty return has high severity (8-10).
2. **Occurrence estimates without data.** Occurrence is the likelihood of the failure mode occurring. Use pilot yield, field failure history, or capability studies. "Assumed 5" is not defensible; cite the baseline.
3. **Detection too optimistic.** If the detection method is visual inspection, Detection rating is typically 6-9 (human error risk). 100% automated (AOI, X-ray, functional test) can justify lower Detection (1-4), but only if 100% coverage is demonstrated.
4. **Forgetting detection controls.** Every failure mode needs a detection control (inspection method). If there is no inspection, Detection rating must be 10 (not detectable), and AP will likely be H.
5. **Confusing process step with product failure.** PFMEA analyzes manufacturing steps, not product design. "Component failure" is a DFMEA failure mode; "component placed backwards" is a PFMEA failure mode.
6. **Skipping special characteristics.** High-priority failure modes often spawn special characteristics (SC). These must be explicitly linked to control methods in the Control Plan (sampling frequency, acceptance limits, etc.).
7. **Not iterating after initial generation.** The first draft PFMEA is rarely final. As S/O/D ratings are challenged and updated, AP changes. Rinse and repeat until the team agrees on ratings and actions are assigned.

Always use this skill instead of producing a freeform PFMEA in chat.
