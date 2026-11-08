# ASIL Decomposition (ISO 26262-9, Clause 5)

## Why decomposition matters

ASIL decomposition lets a development team meet a high-ASIL safety goal by combining two redundant, independent elements developed to lower-but-coordinated ASILs. The economic value is significant: a function that would otherwise demand ASIL-D development effort across the entire chain may instead require two ASIL-B(D) channels, each cheaper and faster to qualify than a single ASIL-D channel — *provided* the independence claim holds.

The cost is rigour. Decomposition is only valid when the two elements are genuinely independent in:

- **Hardware path** — separate silicon, separate power supply rails, separate clocks, separate harnesses.
- **Software partition** — separate runtime, separate memory protection unit (MPU) regions, separate scheduling.
- **Common-cause susceptibility** — no shared sensor, no shared communication bus where loss of the bus disables both, no shared environmental condition that can take down both at once.

The skill's allocation logic flags candidate decompositions but never asserts independence — the analyst must confirm with documented evidence.

## Allowed decomposition patterns (ISO 26262-9, Table 1)

The notation `X(Y)` means "developed to ASIL X requirements, allocated as part of an ASIL-Y safety goal". The "(Y)" annotation must persist throughout development because it changes the verification rigour required of every artifact for that element.

### From ASIL D

| Decomposition          | Element 1 | Element 2 | Notes                                                              |
|------------------------|-----------|-----------|--------------------------------------------------------------------|
| `ASIL D + QM(D)`       | ASIL D    | QM(D)     | Useful when one channel must be developed to D but a checking channel can be QM. |
| `ASIL C(D) + ASIL A(D)`| ASIL C(D) | ASIL A(D) | Common pattern when the two channels have asymmetric criticality.  |
| `ASIL B(D) + ASIL B(D)`| ASIL B(D) | ASIL B(D) | Symmetric — most common for redundant lockstep / dual-MCU designs. |

### From ASIL C

| Decomposition          | Element 1 | Element 2 | Notes                                                              |
|------------------------|-----------|-----------|--------------------------------------------------------------------|
| `ASIL C + QM(C)`       | ASIL C    | QM(C)     |                                                                    |
| `ASIL B(C) + ASIL A(C)`| ASIL B(C) | ASIL A(C) |                                                                    |

### From ASIL B

| Decomposition          | Element 1 | Element 2 | Notes                                                              |
|------------------------|-----------|-----------|--------------------------------------------------------------------|
| `ASIL B + QM(B)`       | ASIL B    | QM(B)     |                                                                    |
| `ASIL A(B) + ASIL A(B)`| ASIL A(B) | ASIL A(B) |                                                                    |

### From ASIL A

| Decomposition          | Element 1 | Element 2 | Notes                                                              |
|------------------------|-----------|-----------|--------------------------------------------------------------------|
| `ASIL A + QM(A)`       | ASIL A    | QM(A)     | The QM(A) channel must still document the link to the ASIL A SG.   |

QM and ASIL combinations beyond these are not permitted. Decomposition cannot lower the highest ASIL on either side below the values shown.

## Independence requirements

ISO 26262-9 §6 governs the independence analysis that must accompany any decomposition. The skill captures the analyst's answers to these questions in the ASIL Allocation tab:

1. **Hardware independence** — Do the two elements share silicon, package, or PCB? Do they share supply rails? Do they share clock domains?
2. **Software independence** — Do they share an OS, a runtime, an MPU region, a scheduling kernel, a memory pool? Do they share a common library that performs safety-relevant computation?
3. **Sensor independence** — Do both elements consume the same sensor, or do they consume independent sensors that observe the same physical phenomenon (acceptable) versus the same sensor signal (not acceptable)?
4. **Communication independence** — Are status and command signals routed over independent buses, or do they share a CAN segment / SPI link?
5. **Environmental common cause** — Could a single environmental event (temperature excursion, EMI, supply transient) take down both elements simultaneously?

A "no" answer to any of these questions disqualifies the candidate decomposition unless a compensating safety mechanism is documented (e.g., supply diversification, watchdog cross-checks).

## Allocation recording in the worksheet

For each ASIL-relevant block diagram node, the ASIL Allocation tab records:

- **Inherited ASIL**: the safety goal's top-level ASIL (default).
- **Decomposition pattern selected**: one of the allowed patterns from the tables above, or "None (full inheritance)".
- **Companion node**: the redundant peer node when decomposition is applied.
- **Independence evidence**: free-text reference to the analysis document or argument that justifies the independence claim.
- **Resulting per-node ASIL**: the developed-to ASIL after decomposition, which drives downstream tool, process, and verification rigour.

## Default behaviour of the skill

By default, the skill propagates the safety goal's ASIL to every ASIL-relevant node in the chain (no decomposition). When two or more nodes share a `redundancy_group` in the input JSON AND have non-overlapping `shared_resources`, the skill proposes decomposition options for the analyst to confirm. The skill does not unilaterally apply decomposition because the independence claim is the analyst's responsibility, not the tool's.
