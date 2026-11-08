# SW-HSIS-Builder Skill

Complete Software-side Hardware-Software Interface specification builder per ISO 26262-6 Section 7.

## Quick Start

```bash
python scripts/generate_sw_hsis.py <hsi.xlsx> <refinement.json> <output.xlsx>
```

Inputs:
- `<hsi.xlsx>` — HW-side HSI workbook (from hsi-builder skill)
- `<refinement.json>` — Handler allocation and debounce strategy (see examples/)

Outputs:
- `<output>.xlsx` — 11-tab SW-HSI specification workbook
- `<output>_sw_handlers.h` — C header file with handler declarations

## Files

- `SKILL.md` — Skill frontmatter, workflow, 11-tab structure
- `scripts/hsi_reader.py` — Extracts signal catalog from HW-side HSI
- `scripts/generate_sw_hsis.py` — Main generator (xlsx + C header)
- `references/methodology.md` — SW-HSI structure and fault propagation rationale
- `references/debouncing_patterns.md` — N-of-M, time-based, hysteresis, leaky-bucket comparison
- `examples/sample_sw_hsis_refinement_esc.json` — ESC handler allocation template

## Output Workbook Structure (11 Tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Document metadata |
| 01 | Document Control | Revision history |
| 02 | HSI Signal Catalog Echo | Read-only signal definitions |
| 03 | SW Handler Catalog | Handler function names, SWC allocation, RTOS task |
| 04 | Debounce Strategy | Per signal: method, parameters, rationale |
| 05 | Fault Propagation Maps | Detection → flag → SWC chain → vehicle reaction |
| 06 | RTOS Integration | Task scheduling, latency, jitter budget |
| 07 | Init Sequence SW Side | SW startup protocol coordination with HW |
| 08 | Test Cases | Nominal, fault injection, boundary, timing edge cases |
| 09 | C Header Stub | Preview of handler declarations |
| 10 | References | Linked documents and standards |

## Refinement JSON Format

See `examples/sample_sw_hsis_refinement_esc.json` for full schema.

Key fields:
- `handler_overrides[].signal_name` — HSI signal name
- `handler_overrides[].handler` — SW handler function name
- `handler_overrides[].swc` — Software component ID
- `handler_overrides[].task` — RTOS task ID
- `handler_overrides[].debounce` — Method (N-of-M / time-based / hysteresis / leaky-bucket)
- `handler_overrides[].debounce_params` — Parameters (e.g., "3-of-5")
- `handler_overrides[].max_exec_us` — Maximum execution time (microseconds)

## Standards

- ISO 26262:2018 Part 6, Section 7 — Software implementation (debouncing, fault handling, RTOS)
- ISO 26262:2018 Part 4, Section 6.4.6 — Technical safety concept (HSI specification)
