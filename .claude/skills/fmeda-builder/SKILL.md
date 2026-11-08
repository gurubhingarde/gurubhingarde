---
name: fmeda-builder
description: Generate an audit-ready ISO 26262-5 Hardware Safety Analysis (FMEDA + SPFM/LFM/PMHF metrics) workbook by reading a TSC xlsx and HW BOM JSON. Enumerates failure modes per HW element, allocates safety mechanisms from TSC, applies diagnostic coverage percentages, and derives safety metrics (SPFM, LFM, PMHF) with formula-driven recalculation. Produces a comprehensive 13-tab workbook with title page, element catalog, FMEDA worksheet (editable DC%), metric aggregation tabs (SPFM, LFM, PMHF) with pass/fail thresholds per ASIL, and a dashboard. Uses SUMIF and IF formulas throughout so changes to DC% or failure rates auto-update all downstream metrics. Always use this skill instead of producing a freeform FMEDA in chat.
---

# FMEDA Builder

The Failure Mode, Effects, and Diagnostic Analysis (FMEDA) is the centerpiece of ISO 26262 Part 5 (Hardware layer) safety analyses. It links every hardware failure mode to a safety goal through detection mechanisms and derives the three mandatory safety metrics:

- **SPFM** (Single-Point Failure Metric): Coverage of *undetected* failure modes. Target: 90% (ASIL B), 97% (C), 99% (D).
- **LFM** (Latent Fault Metric): Coverage of *latent* (undetected two-point) failures. Target: 60% (B), 80% (C), 90% (D).
- **PMHF** (Probabilistic Metric for Hardware Failures): Raw failure rate of undetected + residual faults. Target: <100 FIT (B/C), <10 FIT (D).

This skill automates the scaffolding and formula generation, leaving the analyst to focus on the two high-judgment tasks: (a) enumerating realistic failure modes per element type (guided by IEC 62380 / FIDES baselines) and (b) allocating safety mechanisms from the TSC with appropriate diagnostic coverage percentages (derived from FMEDA evidence, not wishful thinking).

## When to use this skill

Use whenever the user wants to:
- Conduct a hardware FMEDA per ISO 26262-5 §8
- Allocate failure modes and diagnostic mechanisms to HW elements
- Calculate SPFM, LFM, PMHF with automatic aggregation
- Verify that metrics meet ASIL-specific targets
- Hand off a defensible HW safety analysis to auditors or OEMs

Pre-requisites:
- A TSC workbook (produced by tsc-builder) listing chosen safety mechanisms with baseline DC%
- A HW BOM JSON (described below) with element definitions and FIT rates

## Workflow

### Step 1 — Prepare the HW BOM JSON

Gather hardware element definitions in a JSON file using this schema:

```json
{
  "project": {"name", "doc_id", "revision", "date", "author", "approver"},
  "linked_tsc": "path/to/TSC.xlsx",
  "linked_hw_arch": "path/to/HW_Arch.xlsx",
  "target_asil": "D",
  "mission_profile": {
    "operating_hours_per_year": 500,
    "lifetime_years": 15,
    "ambient_temp_c": 65
  },
  "hw_elements": [
    {"id": "HW-E-001", "name": "Main MCU", "type": "MCU", "fit": 100, "safety_related": true, "tsc_node_id": "N10"}
  ],
  "failure_mode_overrides": [
    {"hw_e_id": "HW-E-001", "failure_mode": "stuck-at", "distribution_pct": 0.3, "dc_pct": 99}
  ]
}
```

### Step 2 — Read the reference materials (first use only)

Review:
- `references/methodology.md` — FMEDA process: failure mode enumeration, classification (S/SPF/RF/MPF_D/MPF_L), aggregation math
- `references/failure_mode_libraries.md` — IEC 62380 default distributions per element type (MCU, sensor, driver, memory, power)
- `references/metrics_targets.md` — SPFM/LFM/PMHF formulae and ASIL-specific pass thresholds

### Step 3 — Read the TSC and generate FMEDA

```bash
python scripts/generate_fmeda.py <tsc.xlsx> <hw_bom.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The generator:
- Reads chosen mechanisms + baseline DC% from the TSC
- Applies failure mode distributions per element type (IEC 62380 defaults, or user overrides)
- Builds the main FMEDA worksheet with formulas for λ, λ_SPF, λ_RF, λ_MPF_L so the analyst can update DC% and metrics auto-recalculate
- Populates SPFM/LFM/PMHF metric tabs with SUMIF aggregations
- Colors metrics red/yellow/green against ASIL targets
- Generates a dashboard tab with per-safety-goal roll-up

### Step 4 — Analyst review and iteration

1. **`03_HW_Element_Catalog`** — Confirm FIT rates match datasheet / supplier data. If using FIDES or supplier FIT, cite the source in Assumptions.
2. **`04_Failure_Mode_Library`** — Review default failure mode distributions (locked to IEC 62380; can override in JSON). If element type not listed, add it to the library or flag as TBD.
3. **`05_Safety_Mechanisms_From_TSC`** — Read-only echo of TSC mechanisms. Verify that every failure mode you enumerated in FMEDA is covered by at least one mechanism.
4. **`06_FMEDA_Worksheet`** — The main analysis tab. For each (element × failure mode):
   - Verify λ (=FIT × distribution %) is auto-computed
   - Update DC% based on FMEDA evidence (test, analysis, design review)
   - Watch λ_SPF and λ_RF auto-recalculate as you edit
   - Fill in "allocated mechanism" + "notes" columns
5. **`07-09_Metric_Calculations`** — Per safety goal, inspect SPFM/LFM/PMHF. Red = fail, yellow = caution, green = pass.
6. **`10_Metrics_Dashboard`** — Visual summary. If any metric is red, either (a) increase DC% for chosen mechanisms, (b) add a secondary mechanism, or (c) argue architectural mitigation (e.g., dual-core lockstep reduces lambda_SPF).
7. **`11_Open_Items`** — Auto-generated list of failure modes without claimed coverage or DC% < baseline. Address before sign-off.

When done, save + re-run `recalc.py` to confirm all formulas evaluate and no #REF/#DIV/0 errors remain.

## Output structure (13 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Project, doc ID, ASIL target, linked TSC/HW arch |
| 01 | Document Control | Revision history |
| 02 | Assumptions | Mission profile, FIT source (IEC/FIDES/supplier), environmental class |
| 03 | HW Element Catalog | Read-only echo of HW BOM (element ID, type, FIT, safety relevance) |
| 04 | Failure Mode Library | Default distributions per element type (IEC 62380) |
| 05 | Safety Mechanisms From TSC | Read-only echo of TSC mechanisms with baseline DC% |
| 06 | FMEDA Worksheet | ONE ROW PER (element × failure mode). Columns: FIT, distribution %, λ, safety-related, mechanism, **DC% (editable), λ_SPF (formula), λ_RF (formula), λ_MPF_L (formula), classification, notes** |
| 07 | SPFM Calculation | Per safety goal: SUM(λ_SPF + λ_RF) / SUM(λ_safety_related) with target + pass/fail |
| 08 | LFM Calculation | Per safety goal: SUM(λ_MPF_L) / (SUM(λ_safety_related) - SUM(λ_SPF + λ_RF)) with target + pass/fail |
| 09 | PMHF Calculation | Per safety goal: SUM(λ_SPF + λ_RF) in FIT with target + pass/fail |
| 10 | Metrics Dashboard | Visual roll-up per safety goal: SPFM/LFM/PMHF bar charts + status (green/yellow/red) |
| 11 | Open Items | Auto-generated list of uncovered failure modes + missing DC% evidence |
| 12 | References | Methodology, standard citations, FIT source evidence |

## Files in this skill

```
fmeda-builder/
├── SKILL.md
├── scripts/
│   ├── generate_fmeda.py                      # main generator (TSC xlsx + HW BOM JSON → FMEDA xlsx)
│   ├── tsc_reader.py                          # extracts safety mechanisms + baseline DC% from TSC
│   ├── recalc.py
│   └── office/soffice.py + __init__.py
├── references/
│   ├── methodology.md
│   ├── failure_mode_libraries.md
│   └── metrics_targets.md
└── examples/
    └── sample_fmeda_bom_esc.json              # ESC BOM with FIT rates to clone
```

## Common pitfalls to flag

1. **FIT rates without sourcing.** IEC 62380 baselines are order-of-magnitude; supplier datasheets are far more credible. Always cite the source.
2. **DC% claims without evidence.** "Assumed 95%" is not evidence. Support with test data, design analysis (e.g., parity coverage in a memory test), or operational experience.
3. **Forgetting residual faults.** A detected fault (λ_MPF_D) does NOT count as safe. Only safe (λ_S) and fully undetected (λ_SPF) faults count toward SPFM. Residual faults (λ_RF = λ × (1 - DC)) are the hidden risk.
4. **Mixing up PMHF units.** PMHF is in FIT (failures per 10^9 hours), not percentage. A target of <10 FIT for ASIL D is *very* stringent; it means the undetected + residual failure rate must be <10 billion-hour^-1.
5. **Latent fault isolation (LFM).** If a second fault occurs while the first is latent (undetected), it must trigger a safe state before the combination violates a safety goal. This is why LFM has separate targets — it's about SMvDU (Safe Fault Metric) paired with the architecture's diagnostic coverage of two-point faults.

## Key formulas (in `06_FMEDA_Worksheet`)

For each failure mode row:
- **λ** = FIT × (distribution % / 100)  [in FIT]
- **Classification** (formula):
  - If not safety-related → **S** (safe)
  - If allocated mechanism with DC% and DC% = 100 → **S** (safe due to detection)
  - Else if allocated mechanism → check DC%:
    - If DC% < 100 → **RF** (residual fault) — these contribute to PMHF but not as heavily as SPF
    - If no mechanism or DC% = 0 → **SPF** (single-point fault)
  - If allocated mechanism but covers multiple points → **MPF_D** (detected multipoint) or **MPF_L** (latent multipoint)

- **λ_SPF** = λ if (not safety_related OR classification = SPF) else 0
- **λ_RF** = λ × (1 - DC/100) if (safety_related AND classification = RF) else 0
- **λ_MPF_L** = λ × (1 - DC/100) if (safety_related AND classification = MPF_L) else 0

Metric roll-ups use SUMIF to aggregate by safety goal from the FMEDA worksheet.

