# Verification Methods by ASIL (ISO 26262-4, Table 3 and Part 6)

The FSC must specify verification methods for each FSR. ISO 26262-4 §6 governs FSC verification at the system level; Part 6 §9 governs software-side verification. This skill records, per FSR, the recommended verification methods so the verification plan author has a starting point.

## Recommendation legend (ISO 26262 convention)

- `++` — highly recommended
- `+`  — recommended
- `o`  — no recommendation (neither for nor against)

## FSC verification methods (ISO 26262-4, Table 3)

| Method                          | ASIL A | ASIL B | ASIL C | ASIL D |
|---------------------------------|:------:|:------:|:------:|:------:|
| 1a. Walk-through                | ++     | ++     | +      | +      |
| 1b. Inspection                  | +      | ++     | ++     | ++     |
| 1c. Semi-formal verification    | +      | +      | ++     | ++     |
| 1d. Formal verification         | o      | +      | +      | ++     |
| 2a. Simulation                  | +      | +      | ++     | ++     |
| 2b. Prototype testing           | o      | +      | +      | ++     |

## When the skill records "Recommended methods"

For each FSR, the script writes the methods rated `++` for that FSR's ASIL into the **Verification Method** column (comma-separated). Methods rated `+` go into the **Optional Methods** column. Methods rated `o` are omitted.

Example for ASIL D:

- Verification Method: Inspection, Semi-formal verification, Formal verification, Simulation, Prototype testing
- Optional Methods: Walk-through

## Verification rigour by element ASIL after decomposition

If decomposition is applied (e.g., ASIL D → B(D) + B(D)), the verification rigour for each element follows the **(developed-to) ASIL**, not the original safety goal ASIL. The "(D)" annotation signals to the auditor that the requirement is part of an ASIL-D safety goal but is satisfied via two B-rigour channels.

The skill writes both ASILs in the Verification Matrix tab so the relationship is explicit:

- **SG ASIL** — the top-level ASIL the FSR contributes to.
- **Allocated ASIL** — the developed-to ASIL of the implementing element after decomposition.
- **Verification methods** — driven by the **Allocated ASIL**.

## Independent confirmation reviews

ISO 26262-2 §6.4.7 and Tables 1, 6, 7 govern the independence of confirmation reviews. The skill does not produce the confirmation review plan but flags in the Verification Matrix tab which artefacts require:

- **I1 independence** — different person.
- **I2 independence** — different team.
- **I3 independence** — different organisational unit.

For an ASIL-D FSC review, I3 is required for the FSC verification (ISO 26262-2 Table 1, row 1c). The skill prepopulates this in the Verification Matrix.

## Pitfalls to avoid

1. **Forgetting that "++" methods become mandatory for ASIL D in the audit context.** A skipped `++` method needs a documented justification.
2. **Assuming simulation alone covers prototype testing.** ISO 26262-4 distinguishes the two; for ASIL D both are `++`.
3. **Allocating verification rigour by SG ASIL when decomposition applies.** Use the developed-to ASIL after decomposition.
