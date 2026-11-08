# TSC Checks — by Category

## Confirmation Review (14 generic doc-quality)

Same set as HARA / FSC reviewers — title, author, approver, revision, change history, status, TOC, references, sections complete.

## Technical Safety Assessment (15 substantive checks per ISO 26262-4)

| # | Section | Requirement | Auto-fill |
|---|---------|-------------|-----------|
| 1 | Prerequisites | FSC available with FSRs derived | High (counts FSRs) |
| 2 | Architecture | Refined into HW components + SW partitions | High |
| 3 | TSR Derivation | HW-TSR per FSR | High |
| 4 | TSR Derivation | SW-TSR per FSR | High |
| 5 | TSR Allocation | Each TSR allocated to HW/SW element | High |
| 6 | Safety Mechanisms | Primary mechanism chosen per FSR | High |
| 7 | Safety Mechanisms | DC% targets specified | Medium (catalog defaults need FMEDA) |
| 8 | HW-SW Interface | HSI specified for safety mechanisms | High |
| 9 | Timing Budget | FTTI split into FDTI + FRTI | High |
| 10 | System FMEA | Performed per ISO 26262-9 §8 | Medium |
| 11 | DFA | Performed for each decomposed pair | High |
| 12 | Verification Planning | Methods specified per TSR | High |
| 13 | HW Hand-off | Prepared for ISO 26262-5 | High |
| 14 | SW Hand-off | Prepared for ISO 26262-6 | High |
| 15 | ASIL Consistency | TSR allocated ASIL ≤ parent FSR ASIL (decomposition lowers; never raises) | High |

## Verification Assessment (34 checks)

29 are external (Verification Plan / Spec / Report). 5 are TSC-specific and auto-evaluated:

- **33a** — Completeness with regard to FSRs (every FSR addressed)
- **33b** — Compliance with FSC (linked-FSC reference present)
- **33c** — Consistency with system architecture (FSR-referenced nodes appear in HW/SW allocation)
- **33d** — Completeness of TSR coverage
- **33e** — Consistency of allocated ASILs

## Most valuable findings on a tsc-builder output

- **DC% targets** (TSA #7) — usually rated PC because the catalog defaults must be refined after FMEDA evidence is available. The reviewer's action: replace catalog defaults with measured values.
- **DFA populated** (TSA #11) — the tsc-builder scaffolds DFA rows but leaves Coupling Present and Mitigation as `<TBD>`. The reviewer must populate these for every decomposed pair.
- **System FMEA** (TSA #10) — the scaffold is auto-generated; the reviewer fills Local/Subsystem/Vehicle Effect columns and the DC% from FMEDA.
