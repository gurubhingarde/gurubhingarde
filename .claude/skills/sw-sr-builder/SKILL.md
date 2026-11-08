---
name: sw-sr-builder
description: Generate an audit-ready ISO 26262-6 Clause 6 Software Safety Requirements workbook by reading a TSC xlsx and optional project metadata JSON. Per SW-TSR, derives one or more SW-SRs addressing specific failure modes, allocates to SW components, assigns verification methods, and scaffolds test strategies (unit, integration, back-to-back, fault injection, requirements coverage). Also documents independence requirements when ASIL decomposition cascades. Produces an 11-tab excel workbook with title page, document control, SW-TSR import, SW-SR derivation, failure mode mapping, HSI reference, verification methods, MISRA mapping, test strategy, independence considerations, and references. Always use this skill instead of producing freeform SW safety requirements in chat.
---

# Software Safety Requirements Builder (ISO 26262-6 §6)

The Software Safety Requirements (SW-SRs) are the next step after the Technical Safety Concept (TSC). While TSC defines *what* safety mechanisms are deployed (diagnostic monitoring, watchdog, ECC, message authentication, etc.), SW-SRs define *how* the software implements those mechanisms in concrete, testable, verifiable terms. This skill mechanises the derivation of SW-SRs from SW-TSRs, pairing each technical requirement with specific failure modes, target detection times, allocated software components, and verification methods — leaving the analyst to refine project-specific details like component assignments and test coverage from architecture review.

## When to use this skill

Use whenever the user wants to:
- Derive Software Safety Requirements from a TSC workbook
- Allocate SW-SRs to specific software components (tasks, modules, functions, state machines)
- Specify failure mode coverage per SW-SR (deadline miss, illegal state, divide-by-zero, stack overflow, mutex deadlock, ECC violation, etc.)
- Define detection time targets and verification methods (code review, static analysis, MC/DC, fault injection)
- Scaffold test strategies (unit test, integration test, back-to-back, fault injection, requirements traceability)
- Document independence requirements for ASIL decomposition at the software level
- Hand off to detailed software design, code review, unit test planning, and ISO 26262-6 verification activities

Pre-requisite: a TSC workbook produced by tsc-builder with the 05_TSR_Catalog tab populated and SW-TSRs identified. If the user does not have a TSC, redirect them to tsc-builder first.

## Workflow

### Step 1 — Confirm the TSC input

Ask the user for the path to their TSC xlsx. The skill reads:
- 05_TSR_Catalog — the SW-TSRs to be refined into SW-SRs
- 00_Title_Page and metadata for document control
- 03_System_Architecture — software partitions and their allocation
- 06_HSI_Specification — signals consumed and produced by software

### Step 2 — Project metadata and refinement interview

Ask for (or accept as JSON input):
- project.name, doc_id, revision, date, author, approver
- linked_tsc — path to the source TSC workbook
- sw_sr_overrides (optional) — per-SW-TSR customizations (alternative text, allocated component, detection time refinement)

Capture into a JSON file matching examples/sample_sw_sr_input_esc.json.

### Step 3 — Read the references on first use

Before generating, read whichever of these are relevant:
- references/methodology.md — what SW-SRs are, how they differ from SW-TSRs, the template-based derivation approach. Always read on first invocation.
- references/iso26262_part6_clause6_mapping.md — how each generated tab maps to ISO 26262-6 Clause 6 requirements.
- references/misra_compliance.md — MISRA C:2012 brief reference for coding standards.

### Step 4 — Generate

```bash
python scripts/generate_sw_safety_reqs.py <tsc.xlsx> <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

### Step 5 — Walk the user through the review

Review checkpoints in order:

1. **02_SW_TSRs_From_TSC** — confirms the imported SW-TSRs match the TSC. If not, the TSC needs updating.
2. **03_SW_Safety_Requirements** — for each SW-TSR, one or more SW-SRs derived by template. Allocate to SW components, refine detection times.
3. **04_Failure_Mode_Mapping** — which standard failure modes does each SW-SR address (deadline miss, illegal state, divide-by-zero, stack overflow, mutex deadlock, ECC error, etc.)? Mark coverage.
4. **05_HSI_Reference** — which HSI signals (from upstream HSI spec) are consumed/produced by SW for each SW-SR?
5. **06_Verification_Methods** — per SW-SR: code review, static analysis, control flow analysis, data flow analysis, MC/DC, fault injection — with recommendation level (++ or +) per allocated ASIL.
6. **07_MISRA_Mapping** — per SW-SR: relevant MISRA C:2012 rule categories (no dynamic memory, no recursion, bounded loops, pointer use restrictions).
7. **08_Test_Strategy** — categories (unit test, integration, back-to-back, fault injection, requirements coverage) and which SW-SRs each addresses.
8. **09_Independence_Considerations** — when ASIL decomposition cascades from TSC → SW, document the independence requirements that must hold at SW level.
9. **10_References** — TSC, MISRA C:2012, applicable standards.

When the user requests changes, edit the input JSON and regenerate. The xlsx is a derived artefact; the TSC + input JSON are the source of truth.

## Output structure (11 tabs)

| Tab | Purpose |
|-----|---------|
| 00 | Title Page: SW-SR doc ID, project, dates, methodology statement |
| 01 | Document Control: Revision history |
| 02 | SW TSRs From TSC: Read-only echo with traceability |
| 03 | SW Safety Requirements: One or more SW-SRs per SW-TSR, text, allocated component, ASIL, target detection time, addressed failure modes |
| 04 | Failure Mode Mapping: Per SW-SR, which standard SW failure modes (deadline miss, illegal state, etc.) it addresses |
| 05 | HSI Reference: Cross-reference which HSI signals consumed/produced by SW per SW-SR |
| 06 | Verification Methods: Per SW-SR, methods (review, static analysis, control/data flow, MC/DC, fault injection) with recommendation level per ASIL |
| 07 | MISRA Mapping: Per SW-SR, relevant MISRA C:2012 rule categories (dynamic memory, recursion, loops, etc.) |
| 08 | Test Strategy: Test categories and which SW-SRs each addresses |
| 09 | Independence Considerations: Independence requirements when decomposition cascades |
| 10 | References: TSC, MISRA C:2012, applicable standards |

## SW-SR template per SW-TSR mechanism category

For an SW-TSR like "The SW shall consume diagnostic flag, debounce, command safe state within FRTI", derived SW-SRs might be:

1. **Sampling and capture**
   - "The SW shall sample the diagnostic flag signal every {period_ms} ms and buffer samples."

2. **Debouncing and confirmation**
   - "The SW shall debounce the diagnostic flag with {N_consecutive} consecutive samples to filter transients."

3. **Reaction and safe state**
   - "The SW shall command {safe_state} within {FRTI_ms} ms of confirmed fault detection."

For monitoring requirements (plausibility checks):
- "The SW shall continuously evaluate {monitored_value} against {threshold} per cycle."
- "The SW shall declare fault if {monitored_value} deviates by greater than {tolerance} for greater than {persistence_ms} ms."

## Common pitfalls to flag

1. **Mechanism without allocation.** SW-SRs must name a specific software component (task, module, state machine). Generic requirements fail architecture review.
2. **Detection time without timing budget justification.** The template provides order-of-magnitude defaults; each SW-SR needs allocation analysis to confirm FDTI + FRTI budgets fit.
3. **Independence not documented early.** When ASIL decomposition carries forward from TSC → SW, independence evidence must be prepared *before* detailed design.
4. **Test strategy divorced from SW-SR coverage.** Every SW-SR must map to at least one test method and one test category. Dangling requirements = gaps in verification.

## Files in this skill

```
sw-sr-builder/
├── SKILL.md
├── scripts/
│   ├── generate_sw_safety_reqs.py    # main generator (TSC xlsx + input JSON → SW-SR xlsx)
│   ├── tsc_reader.py                 # TSC reader: extract SW-TSRs and arch
│   ├── recalc.py
│   └── office/soffice.py
├── references/
│   ├── methodology.md                # what SW-SRs are and how they refine SW-TSRs
│   ├── iso26262_part6_clause6_mapping.md  # tab-to-clause mapping
│   └── misra_compliance.md           # MISRA C:2012 brief reference
└── examples/
    └── sample_sw_sr_input_esc.json   # ESC project metadata + refinement example
```
