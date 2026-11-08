# FSC Checks — by Category

## Confirmation Review (14 generic doc-quality checks)

Same set as HARA / TSC reviewers — title, author, approver, revision, change history, status, TOC, references, sections complete. Verified from the Title and Document Control tabs.

## Functional Safety Assessment (16 FSC substantive checks per ISO 26262-3 §8)

| # | Section | Requirement | Auto-fill |
|---|---------|-------------|-----------|
| 1 | Prerequisites | HARA available with safety goals derived | High (counts SGs) |
| 2 | Prerequisites | Item Definition referenced | Low (external) |
| 3 | Prerequisites | Preliminary architecture present | High (counts nodes) |
| 4 | FSR Derivation | At least one FSR per safety goal | High |
| 5 | FSR Derivation | Each FSR has inherited ASIL | High |
| 6 | Safe States | Safe states specified for every SG | High |
| 7 | Timing | FTTI specified for every FSR | High |
| 8 | Warning & Degradation | Warning/degradation strategies defined | Low (text inspection) |
| 9 | Architecture Allocation | Each FSR allocated to a node | High |
| 10 | ASIL Decomposition | Independence evidence cited per ISO 26262-9 §6 | High |
| 11 | FSC Verification | FSC compliance with safety goals | High (FTA top events match SG IDs) |
| 12 | FSC Verification | FSC consistency with preliminary architecture | High (cross-reference) |
| 13 | External Interfaces | Sensors / actuators / communication considered | High |
| 14 | Operating Modes | Start-up / normal / shutdown / fault modes considered | Low (drafted) |
| 15 | Verification Planning | Means of verification planned per FSR | Medium |
| 16 | TSC Hand-off | Hand-off prepared with FSR-to-TSR placeholders | High |

## Verification Assessment (34 checks)

29 are external (Verification Plan / Spec / Report). 5 are FSC-specific and auto-evaluated:

- **33a** — Completeness with regard to safety goals (every SG has FTA + FSRs)
- **33b** — Compliance with item definition (drafted; external)
- **33c** — Consistency with preliminary architectural design (cross-reference check)
- **33d** — Completeness of FSR coverage (every SG has ≥1 FSR)
- **33e** — Consistency of allocated ASILs with parent SGs (recompute and compare)

## Most valuable findings

When auditing an fsc-builder output, the highest-impact finding is usually FSA #10 (ASIL decomposition independence). The fsc-builder leaves Independence Evidence as `<TBD>` by design — the reviewer must document the analytical or design argument that justifies treating two channels as independent. This skill flags this gap clearly.
