---
name: hsi-builder
description: Generate a contract-grade ISO 26262 Hardware-Software Interface (HSI) specification workbook from a TSC xlsx plus refinement JSON. Per ISO 26262-4 Section 6.4.6 and ISO 26262-5 Section 6.4.6, formalizes HW-SW signal contracts with register maps, timing budgets, failure modes, integrity methods, and C header definitions. Includes 11-tab workbook, cross-reference traceability, and standalone .h file. Use this skill whenever the user mentions HSI specification, hardware-software interface, signal integrity, register map, or needs to formally specify the signals crossing the HW-SW boundary. Always use this skill instead of producing a freeform HSI in chat.
---

# HSI Builder

The Hardware-Software Interface (HSI) is the **contract** between the HW and SW teams. It specifies every signal that crosses the boundary: encoding, timing, integrity protection, failure modes, initialization hand-shake, and traceability to safety requirements. This skill automates the rote aspects of HSI authoring—signal catalog generation, register map scaffolding, timing constraint propagation, and C header synthesis—leaving the analyst free to focus on the technical judgment that makes the interface robust.

## When to use this skill

Use whenever the user wants to:
- Formalize HSI signals from a TSC into a contract-grade specification
- Define register addresses, bit offsets, and memory-map layout for HSI signals
- Specify timing constraints (sample rate, max age, latency budget) per signal
- Choose and justify integrity protection methods (Parity, CRC, SECDED, Dual-channel)
- Scaffold failure modes and test cases for HSI signals
- Generate C struct definitions for embedded SW hand-off
- Ensure traceability from HSI signals back to FSRs and safety mechanisms
- Build the initialization and hand-shake protocol between HW and SW

Pre-requisite: A TSC workbook produced by `tsc-builder` with the `06_HSI_Specification` tab populated. If the user does not have one, redirect them to `tsc-builder` first.

## Workflow

### Step 1 — Confirm the TSC input

Ask the user for the path to their TSC xlsx. The skill reads:
- `06_HSI_Specification` — the HSI signals scaffold (one row per HW->SW diagnostic and SW->HW liveness signal)
- `00_Title_Page` and `01_Document_Control` — for context and project metadata

### Step 2 — Signal refinement interview

The TSC's HSI scaffold contains signal names, directions, mechanisms, and encoding hints. The HSI specification adds the next level of detail: which **HW registers** (if any) host each signal, **timing constraints** (sample rate, max age, latency budgets), **integrity methods** (Parity, CRC, SECDED, Dual-channel), and **validity bits** (companion signals confirming HW has written a fresh value).

For each major signal group (e.g., esc.diag.*, esc.live.*):
- Register address (e.g., 0x4001_0010), bit offset, access mode (R/RW/W), reset value.
- Sample rate (Hz), maximum age SW may consume (ms), latency HW->SW (ms), latency SW->HW (ms).
- Integrity method and DC% target (see references/integrity_protection_methods.md for guidance).
- Companion validity bit name (if not already in TSC).

Capture into a JSON file matching `examples/sample_hsi_refinement_esc.json`. The most consequential fields are register address and integrity method—without them, HW FMEDA and SW test planning cannot proceed.

### Step 3 — Read the references on first use

Before generating, read whichever of these are relevant:
- `references/methodology.md` — What the HSI captures; the 11-tab structure; validity bits and liveness counters; timing budget math. **Always read on first invocation.**
- `references/integrity_protection_methods.md` — Detailed comparison of Parity, CRC, SECDED, and Dual-channel; when to use each; implementation examples.

### Step 4 — Generate

```bash
python scripts/generate_hsi.py <tsc.xlsx> <refinement.json> <output.xlsx>
```

The generator produces:
- **11-tab HSI workbook** (output.xlsx) with signal catalog, register map, timing, failure modes, initialization, cross-reference, and test-case scaffolding.
- **C header file** (<output>_hsi.h) with auto-generated struct definitions for SW integration.

### Step 5 — Walk the user through the review

Review checkpoints in order:

1. **`00_Title_Page`** — confirm project ID, linked TSC, and linked HW architecture.
2. **`01_Document_Control`** — confirm revision tracking setup.
3. **`02_HSI_Signal_Catalog`** — the single source of truth. One row per signal: name, direction (HW->SW or SW->HW), data type, bit width, units, default value, encoding rules, integrity method, validity bit, allocated ASIL.
4. **`03_Register_Map`** — for memory-mapped signals: register address, bit offset, access mode, reset value, bit-field layout. Placeholder rows for signals without fixed addresses.
5. **`04_Timing_Specification`** — sample rate (Hz), max age (ms), latency budgets (HW->SW and SW->HW), detection time, settling time. Ensure FDTI + FRTI <= FTTI from the FSC.
6. **`05_Failure_Modes_and_Reactions`** — per signal: stuck-at, parity error, missing, late, out-of-range faults; detection method (BIST, periodic check, watchdog); SW reaction; HW fail-safe; target DC%.
7. **`06_Initialization_Sequence`** — HW BIST, register lock, supply monitor, SW startup checks, hand-shake protocol, timing, success conditions.
8. **`07_Cross_Reference`** — HSI signal -> FSR_ID -> TSR_ID -> Safety Mechanism -> ASIL. Enables impact analysis and verification mapping.
9. **`08_C_Header_Stub`** — preview of auto-generated C structs (full .h file on disk).
10. **`09_Test_Cases`** — per signal: nominal, stuck-at, parity, timeout, boundary scenarios. Basis for HW/SW integration and verification.
11. **`10_References`** — TSC, HW arch, ISO 26262 Parts 4 & 5 §6.4.6, AUTOSAR (if applicable), methodology.

When the user requests changes, edit the refinement JSON and regenerate. The xlsx is a derived artefact; the TSC + refinement JSON are the source of truth.

## Output structure (11 tabs + .h file)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | HSI doc ID, project, linked TSC and HW arch, methodology |
| 01 | Document Control | Revision history |
| 02 | HSI Signal Catalog | One row per signal: name, direction, data type, bit width, encoding, integrity, validity bit, allocated ASIL |
| 03 | Register Map | Memory-mapped signals: address, bit offset, access, reset, bit-field layout |
| 04 | Timing Specification | Sample rate, max age, latency budgets (HW->SW, SW->HW), detection time, settling time |
| 05 | Failure Modes and Reactions | Per-signal faults (stuck, parity, missing, late, OOR), detection, SW reaction, HW fail-safe, DC% |
| 06 | Initialization Sequence | HW BIST, register lock, supply monitor, SW startup, hand-shake protocol |
| 07 | Cross-Reference | HSI signal -> FSR -> TSR -> Mechanism -> ASIL traceability |
| 08 | C Header Stub | Auto-generated C struct preview (full .h file on disk) |
| 09 | Test Cases | Per-signal nominal, fault injection, boundary, timing edge cases |
| 10 | References | TSC, HW arch, ISO 26262-4/5, AUTOSAR, methodology |

Plus: `<output_basename>_hsi.h` — C struct definitions ready for SW compilation.

## Common pitfalls to flag

1. **Validity bit not paired with diagnostic signal.** HW asserts a diagnostic flag (e.g., `esc.diag.lockstep_mismatch`), but SW cannot distinguish "0 = no fault" from "0 = HW comms lost". Always add a companion `<signal>_valid` bit that SW reads first.
2. **Integrity method chosen without DC% evidence.** Default integrity method in the catalog is order-of-magnitude. Each signal needs an FMEDA-derived DC% before the HW verification case can close.
3. **Timing constraints not validated against FTTI.** The TSC specifies FTTI per FSR. The HSI must ensure FDTI + FRTI <= FTTI. If liveness counter period is 50 ms, SW cannot detect timeout faster than 50 ms.
4. **Register lock not mentioned in initialization.** Once the HSI registers are initialized, HW must lock them (set a lock bit) to prevent accidental SW overwrite. Lock persists until watchdog reset.
5. **C header generation skipped.** The .h file is not just a preview; it is the contract for SW integration. Ensure SW compiles against it; structure field offsets must match HW register layout.

## Files in this skill

```
hsi-builder/
├── SKILL.md
├── scripts/
│   ├── tsc_reader.py                       # extracts HSI signals from TSC xlsx
│   ├── generate_hsi.py                     # main generator (TSC xlsx + refinement JSON -> HSI xlsx + .h)
│   ├── recalc.py                           # (inherited from tsc-builder)
│   └── office/soffice.py                   # (inherited from tsc-builder)
├── references/
│   ├── methodology.md                      # what the HSI captures; 11-tab structure; validity bits; timing math
│   └── integrity_protection_methods.md     # Parity, CRC, SECDED, Dual-channel: when to use each
└── examples/
    └── sample_hsi_refinement_esc.json      # ESC HSI refinement to clone
```
