---
name: hw-safety-reqs-builder
description: Generate an audit-ready ISO 26262-5 Section 6 Hardware Safety Requirements workbook by reading a TSC xlsx (produced by tsc-builder) and optional project metadata JSON. Per HW-TSR, derives one or more HW-SRs addressing specific failure modes, allocates to hardware elements, assigns verification methods, and scaffolds test strategies (HIL, fault injection, electrical, environmental). Also documents independence requirements when ASIL decomposition cascades. Produces a 10-tab excel workbook with title page, document control, HW-TSR import, HW-SR derivation, failure mode mapping, HSI reference, verification methods, test strategy, independence considerations, and references. Always use this skill instead of producing freeform HW safety requirements in chat.
---

# Hardware Safety Requirements Builder (ISO 26262-5 §6)

The Hardware Safety Requirements (HW-SRs) are the next step after the Technical Safety Concept (TSC). While TSC defines *what* safety mechanisms are deployed (range checks, ECC, watchdogs, etc.), HW-SRs define *how* the hardware implements those mechanisms in concrete, testable terms. This skill mechanises the derivation of HW-SRs from HW-TSRs, pairing each technical requirement with specific failure modes, diagnostic coverage targets, allocated hardware elements, and verification methods — leaving the analyst to refine project-specific details like element assignments and DC% refinement from FMEDA.

## When to use this skill

Use whenever the user wants to:
- Derive Hardware Safety Requirements from a TSC workbook
- Allocate HW-SRs to specific hardware components (MCU, sensor, driver IC, power stage)
- Specify failure mode coverage per HW-SR (stuck, drift, open, short, latch-up, etc.)
- Define diagnostic coverage targets and verification methods
- Scaffold test strategies (HIL, fault injection, electrical, environmental, accelerated life)
- Document independence requirements for ASIL decomposition at the hardware level
- Hand off to FMEDA, hardware metrics (SPFM/LFM), and ISO 26262-5 verification activities

Pre-requisite: a TSC workbook produced by `tsc-builder` with the `05_TSR_Catalog` tab populated. If the user does not have a TSC, redirect them to `tsc-builder` first.

## Workflow

### Step 1 — Confirm the TSC input

Ask the user for the path to their TSC xlsx. The skill reads:
- `05_TSR_Catalog` — the HW-TSRs and SW-TSRs to be refined into HW-SRs
- `00_Title_Page` and metadata for document control
- `03_System_Architecture` — hardware components and allocated nodes

### Step 2 — Project metadata and refinement interview

Ask for (or accept as JSON input):
- `project.name`, `doc_id`, `revision`, `date`, `author`, `approver`
- `linked_tsc` — path to the source TSC workbook
- `hw_sr_overrides` (optional) — per-HW-TSR customizations (alternative text, allocated element, mechanism refinement)

Capture into a JSON file matching `examples/sample_hw_sr_input_esc.json`.

### Step 3 — Read the references on first use

Before generating, read whichever of these are relevant:
- `references/methodology.md` — what HW-SRs are, how they differ from HW-TSRs, the template-based derivation approach. **Always read on first invocation.**
- `references/iso26262_part5_mapping.md` — how each generated tab maps to ISO 26262-5 Clause 6 requirements.

### Step 4 — Generate

```bash
python scripts/generate_hw_safety_reqs.py <tsc.xlsx> <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

### Step 5 — Walk the user through the review

Review checkpoints in order:

1. **`02_HW_TSRs_From_TSC`** — confirms the imported HW-TSRs match the TSC. If not, the TSC needs updating.
2. **`03_HW_Safety_Requirements`** — for each HW-TSR, one or more HW-SRs derived by template. Allocate to HW elements, refine DC% targets.
3. **`04_Failure_Mode_Mapping`** — which standard failure modes does each HW-SR address (stuck, drift, open, short, latch-up, etc.)? Mark coverage.
4. **`05_HSI_Reference`** — which HSI signals (from upstream HSI spec) are owned by HW for sensing, diagnostics, or liveness?
5. **`06_Verification_Methods`** — per HW-SR: electrical test, fault injection, environmental test, simulation, inspection — with recommendation level (++ or +) per allocated ASIL.
6. **`07_Test_Strategy`** — categories (HIL, fault injection, electrical characterization, environmental, accelerated life) and which HW-SRs each addresses.
7. **`08_Independence_Considerations`** — when ASIL decomposition cascades from FSC → TSC → HW, document the independence requirements that must hold at HW level.
8. **`09_References`** — TSC, FSC, HARA, applicable standards.

When the user requests changes, edit the input JSON and regenerate. The xlsx is a derived artefact; the TSC + input JSON are the source of truth.

## Output structure (10 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | HW-SR doc ID, project, dates, methodology statement |
| 01 | Document Control | Revision history |
| 02 | HW TSRs From TSC | Read-only echo with traceability |
| 03 | HW Safety Requirements | One or more HW-SRs per HW-TSR: text, allocated element, ASIL, target DC%, addressed failure modes |
| 04 | Failure Mode Mapping | Per HW-SR: which standard failure modes (stuck, drift, open, short, latch-up, etc.) it addresses |
| 05 | HSI Reference | Cross-reference: which HSI signals owned by HW per HW-SR |
| 06 | Verification Methods | Per HW-SR: methods (electrical, fault injection, environmental, simulation, inspection) with recommendation level per allocated ASIL |
| 07 | Test Strategy | Test categories and which HW-SRs each addresses |
| 08 | Independence Considerations | Independence requirements when decomposition cascades |
| 09 | References | TSC, FSC, HARA, applicable standards |

## HW-SR template per HW-TSR type

For an HW-TSR like "The HW shall implement Range / out-of-range check (SM10) on Wheel Speed Sensor FL with diagnostic coverage of at least 60-80%", derived HW-SRs might be:

1. **Sensing and input conditioning**
   - "The HW shall provide a 12-bit ADC channel for the FL wheel speed sensor signal with input range 0-5V and ±5% accuracy."
   
2. **Monitoring and detection**
   - "The HW shall implement a digital out-of-range comparator with thresholds set per calibration (default: 0-50 km/h) and assert fault flag upon detection within 1 sample (10 ms)."
   
3. **Diagnostic communication**
   - "The HW shall route the out-of-range fault flag to the safety MCU diagnostic input pin with parity integrity protection."

## Common pitfalls to flag

1. **Mechanism without allocation.** HW-SRs must name a specific hardware element (MCU pin, ADC channel, comparator, etc.). Generic requirements fail FMEDA.
2. **DC% target without FMEDA validation.** The template provides order-of-magnitude defaults; each HW-SR needs FMEDA analysis to confirm the actual achievable DC%.
3. **Independence not documented early.** When ASIL decomposition carries forward from FSC → TSC → HW, independence evidence must be prepared *before* hardware detailed design.
4. **Test strategy divorced from HW-SR coverage.** Every HW-SR must map to at least one test method and one test category. Dangling requirements = gaps in verification.

## Files in this skill

```
hw-safety-reqs-builder/
├── SKILL.md
├── scripts/
│   ├── generate_hw_safety_reqs.py    # main generator (TSC xlsx + input JSON → HW-SR xlsx)
│   ├── tsc_reader.py                 # TSC reader: extract HW-TSRs and arch
│   ├── recalc.py
│   └── office/soffice.py
├── references/
│   ├── methodology.md                # what HW-SRs are and how they refine HW-TSRs
│   └── iso26262_part5_mapping.md     # tab-to-clause mapping
└── examples/
    └── sample_hw_sr_input_esc.json   # ESC project metadata + refinement example
```
