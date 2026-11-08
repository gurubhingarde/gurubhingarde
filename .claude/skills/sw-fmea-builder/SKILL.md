---
name: sw-fmea-builder
description: Generate an audit-ready ISO 26262-9 section 8 + ISO 26262-6 sections 7-8 Software FMEA workbook. Enumerates failure modes per SW component type (Application/Service/Driver/Diagnostic), allocates detection mechanisms from TSC, applies qualitative risk scoring (severity x frequency x detection coverage), and derives residual risk acceptance per ASIL. Produces a comprehensive 12-tab workbook with component catalog, failure mode library, FMEA worksheet (editable detection coverage), propagation analysis, and verification hooks. Uses formula-driven risk scores so changes auto-update metrics. Always use this skill instead of producing a freeform SW FMEA in chat.
---

# SW FMEA Builder

The Software Failure Mode, Effects, and Diagnostic Analysis (FMEA) is the centerpiece of ISO 26262 Part 9 (Software level) safety analyses. It links every software failure mode to a safety goal through detection mechanisms and derives residual risk assessment per ASIL. Unlike hardware FMEA, SW FMEA is qualitative; it focuses on failure enumeration, propagation chains, and detectability rather than quantitative metrics (FIT, PMHF).

- **Failure Mode Taxonomy**: Per SW component type — Application (deadline miss, illegal state, divide-by-zero, NaN, stack overflow, config corruption), Service (race condition, deadlock, resource leak), Driver (register fault, interrupt miss, busy bit stuck), Diagnostic (false positive, false negative, priority inversion).
- **Risk Scoring**: Qualitative formula: Pre-mitigation risk = Severity (S0-S3, log scale) × Frequency (Rare/Occasional/Frequent). Detection coverage (Low/Med/High) reduces post-mitigation risk by factor (1.0/0.4/0.1). Residual risk acceptable if below ASIL threshold.
- **Detection Mechanisms**: Assertion, watchdog timer, control flow monitor, range check, sentinel, code review — each mapped to failure modes with claimed detection coverage.
- **Propagation Analysis**: SWC → output signal → downstream SWC → actuator → vehicle behavior. Traces each failure mode to its vehicle-level hazard.

## When to use this skill

Use whenever the user wants to:
- Conduct a software FMEA per ISO 26262-9 §8 + ISO 26262-6 §7-8
- Enumerate failure modes per SW component type and allocate detection mechanisms
- Calculate pre- and post-mitigation residual risk with qualitative scoring
- Verify that residual risk meets ASIL-specific thresholds
- Hand off a defensible SW safety analysis to auditors or OEMs

Pre-requisites:
- A TSC workbook (produced by tsc-builder) listing SW partitions and SW-TSRs
- A SW architecture JSON or xlsx (optional; if not provided, failure modes applied to TSC partitions directly)

## Workflow

### Step 1 — Prepare the SW FMEA input JSON

Gather SW component definitions and optional failure mode overrides in JSON:

```json
{
  "project": {"name", "doc_id", "revision", "date", "author", "approver", "target_asil"},
  "linked_tsc": "path/to/TSC.xlsx",
  "linked_sw_arch": "path/to/SW_Arch.xlsx (optional)",
  "target_asil": "D",
  "swcs_override": [
    {"id": "SWC01", "name": "ESC Application", "type": "Application", "partition_id": "P01", "asil": "D", "language": "C"},
    {"id": "SWC02", "name": "Watchdog Service", "type": "Service", "partition_id": "QM", "asil": "QM", "language": "C"}
  ],
  "failure_mode_overrides": [
    {"swc_id": "SWC01", "failure_mode": "deadline miss", "severity": "S3", "frequency": "Occasional", "detection": "Window watchdog", "coverage": "High", "mitigation": "Transition to safe state"}
  ]
}
```

### Step 2 — Read the reference materials (first use only)

Review:
- `references/methodology.md` — SW FMEA process: failure mode enumeration per SW type, severity/frequency/coverage scoring, residual risk acceptance per ASIL.
- `references/sw_failure_mode_library.md` — Comprehensive failure mode taxonomy by SW component type (Application, Service, Driver, Diagnostic) with typical local/subsystem/vehicle effects.
- `references/iso26262_part6_alignment.md` — How SW FMEA aligns with ISO 26262-6 Tables 5-6 (product metrics: statement coverage, branch coverage, LCSAJ, control flow) and SW architecture metrics (partition isolation, interface integrity).

### Step 3 — Read TSC and SW architecture, generate FMEA

```bash
python scripts/generate_sw_fmea.py <tsc.xlsx> <input.json> <output.xlsx> [<sw_arch.xlsx>]
python scripts/recalc.py <output.xlsx>
```

The generator:
- Reads SW partitions and SW-TSRs from TSC
- Optionally reads SW components from SW architecture xlsx for refinement
- Applies default failure mode library per component type (SWC_override to customize)
- Builds FMEA worksheet with formula-driven risk scores (severity × frequency × coverage adjustment)
- Populates propagation paths, detection mechanism summary, and coverage roll-up per Safety Goal
- Generates verification plan hooks linking each failure mode to a test method
- Colors residual risk red/yellow/green against ASIL thresholds

### Step 4 — Analyst review and iteration

1. **`03_SW_Component_Catalog`** — Confirm SWC IDs, names, types, and ASIL allocations. If using SW architecture xlsx, verify mapping is correct.
2. **`04_SW_Failure_Mode_Library`** — Review default failure mode list per component type (locked to ISO 26262-6 Table 5-6 taxonomy). If SWC type not listed, add via failure_mode_overrides in input JSON.
3. **`05_FMEA_Worksheet`** — The main analysis. For each (SWC × failure mode):
   - Verify severity and frequency per ASIL allocation and functional context
   - Update detection mechanism (assertion, watchdog, control flow monitor, range check, sentinel, code review, design review)
   - Update detection coverage (Low/Med/High) based on evidence (unit test, code analysis, design walkthrough)
   - Watch pre- and post-mitigation risk auto-recalculate as you edit inputs
   - If residual risk > ASIL threshold, either increase coverage or add secondary mechanism
4. **`06_Detection_Mechanisms_Summary`** — Per mechanism, inspect count of failure modes covered and average detection coverage. Red = immature, needs evidence. Green = well-justified.
5. **`07_Propagation_Paths`** — Verify failure mode chains to vehicle hazard. If unclear, add notes in FMEA worksheet.
6. **`08_Coverage_Summary`** — Per Safety Goal, inspect count of failure modes and count detected. If coverage < 80%, flag as open item.
7. **`09_Open_Items`** — Auto-generated list of failure modes without claimed detection or with residual risk > ASIL threshold. Address before sign-off.

When done, save + re-run `recalc.py` to confirm all formulas evaluate and no #VALUE/#DIV/0/#REF errors remain.

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Project, doc ID, ASIL target, linked TSC/SW arch |
| 01 | Document Control | Revision history |
| 02 | Assumptions | Scope, methodology (qualitative), failure mode library source, SW process maturity |
| 03 | SW Component Catalog | Read-only echo of SWCs (ID, name, type, partition, ASIL, language) |
| 04 | SW Failure Mode Library | Default failure modes per component type (Application/Service/Driver/Diagnostic) |
| 05 | FMEA Worksheet | ONE ROW PER (SWC × failure mode). Columns: SWC, failure mode, local/subsystem/vehicle effects, parent FSR/SG, severity (S0-S3), frequency (Rare/Occasional/Frequent), **pre-mitigation risk (formula), detection mechanism (editable), detection coverage (Low/Med/High, editable), post-mitigation risk (formula), residual risk acceptable (Y/N), mitigation strategy, notes** |
| 06 | Detection Mechanisms Summary | Per mechanism (watchdog, assertion, range check, control flow, monitor, etc.): count of FM covered, avg coverage, maturity status |
| 07 | Propagation Paths | Per failure mode: text chain from SWC through partition, signal, downstream SWC, actuator, to vehicle behavior. Severity rolled up. |
| 08 | Coverage Summary | Per Safety Goal: count of failure modes, count detected, total residual risk, status (acceptable/needs work) |
| 09 | Open Items | Auto-generated list of uncovered failure modes, mechanisms with low coverage, TBD items |
| 10 | Verification Plan Hooks | Per failure mode: recommended test method (unit test, fault injection, code review, simulation), expected result, owner |
| 11 | References | Methodology, standard citations (ISO 26262-9, ISO 26262-6), AIAG SW FMEA handbook |

## Files in this skill

```
sw-fmea-builder/
├── SKILL.md
├── scripts/
│   ├── generate_sw_fmea.py                 # main generator (TSC xlsx + JSON → SW FMEA xlsx)
│   ├── tsc_reader.py                       # extracts SW partitions + components from TSC / SW arch
│   ├── recalc.py                           # formula recalculation (inherited)
│   └── office/soffice.py + __init__.py     # LibreOffice integration
├── references/
│   ├── methodology.md                      # SW FMEA process: failure enumeration, scoring, residual risk
│   ├── sw_failure_mode_library.md          # Comprehensive taxonomy per SWC type (ISO 26262-6 Table 5-6)
│   └── iso26262_part6_alignment.md         # Alignment with ISO 26262-6 §7-8: product & architecture metrics
└── examples/
    └── sample_sw_fmea_input_esc.json       # ESC SW FMEA input with SWC overrides to clone
```

## Common pitfalls to flag

1. **Severity without functional context.** S3 assumes a safety goal violation (e.g., loss of steering). Justify severity in notes column or escalate to safety goal owner.
2. **Detection coverage claims without evidence.** "Assumed 95% coverage" is not evidence. Support with unit test DC calculation (statement/branch/MCDC %), code review protocol (e.g., static analysis rule coverage), or design analysis (e.g., watchdog period vs. task deadline margin).
3. **Forgetting residual risk.** Detection coverage < 100% leaves undetected faults. Post-mitigation risk = pre-risk × (1 - coverage %). A failure mode with high severity but 90% coverage still contributes 10% residual risk.
4. **Mixing severity and frequency.** Severity is inherent to the failure (e.g., loss of steering = S3). Frequency is how often it occurs in operation. Do not conflate; use both in scoring.
5. **No propagation analysis.** A deadline miss in one SWC may not affect the vehicle if the downstream partition is decoupled. Trace propagation paths carefully.

## Key formulas (in `05_FMEA_Worksheet`)

For each failure mode row:
- **Severity** = S0 (0), S1 (1), S2 (3), S3 (9) — log scale to weight high severity
- **Frequency** = Rare (1), Occasional (3), Frequent (9) — operational likelihood
- **Pre-mitigation risk** = Severity × Frequency [range 0-81]
- **Detection Coverage** = Low (×1.0), Medium (×0.4), High (×0.1) — factor applied to post-mitigation
- **Post-mitigation risk** = Pre-risk × Coverage factor [formula]
- **Residual Risk Acceptable** = Post-risk ≤ ASIL threshold (A=27, B=9, C=3, D=1)

Example: Deadline miss in ASIL-D SWC, severity S3, frequency Occasional, detected with High coverage → pre = 9 × 3 = 27, post = 27 × 0.1 = 2.7. Residual risk 2.7 > D threshold (1) → NOT ACCEPTABLE. Either increase coverage to very-high (×0.05) or add secondary mechanism.
