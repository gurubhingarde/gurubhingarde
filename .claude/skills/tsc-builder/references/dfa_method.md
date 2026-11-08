# Dependent Failure Analysis (DFA) — ISO 26262-9 §7

## Why DFA matters

The ASIL decomposition argument in the FSC depends on the **independence** of the redundant elements. The DFA is the formal verification of that independence at the system level. Without it, a B(D)+B(D) decomposition is unverifiable and an assessor will reject the safety case.

DFA covers two failure classes:

1. **Common-cause failures** — a single root cause produces faults in multiple redundant elements simultaneously (loss of supply, EMI burst, software defect in shared library, environmental excursion).
2. **Cascading failures** — a fault in one element produces a fault in another element that should have been independent (driver stage failure that damages the supply rail of an unrelated MCU, software deadlock that blocks the watchdog refresh).

## DFA checklist (the rows the TSC generator pre-populates)

For each candidate-decomposition pair from the FSC, the TSC generator creates one DFA row per candidate failure-coupling factor. The analyst confirms or rejects each:

| Coupling factor                  | Question                                                                            | Mitigation when present                                  |
|----------------------------------|-------------------------------------------------------------------------------------|----------------------------------------------------------|
| Shared supply                    | Do both elements share a power rail or regulator?                                    | Add diversification, separate rails, separate regulators |
| Shared ground                    | Do both elements share a ground return path?                                        | Star ground, separate return                             |
| Shared clock                     | Do both elements share a clock source?                                              | Diverse clock domains, internal RC backup                |
| Shared bus                       | Do both elements depend on the same communication bus?                              | Diverse bus, redundant message path                      |
| Shared sensor                    | Do both elements consume the same sensor reading?                                   | Diverse sensors observing the same physics               |
| Shared memory                    | Do they share RAM, Flash, EEPROM regions?                                           | MPU partition, separate banks                            |
| Shared SW library                | Do they call the same safety-related library code?                                  | Independent implementations, diversified compilers       |
| Shared OS / scheduler            | Do they execute on the same RTOS instance?                                          | Hypervisor partition, separate cores with separate OS    |
| Shared environmental zone        | Are both physically co-located such that one event can damage both?                 | Separate PCB regions, separate enclosures                |
| Shared development team / process| Could a single design defect affect both?                                           | Independent design teams, formal review                  |
| Shared compiler / toolchain      | Could a tool fault affect both binaries?                                            | Diverse toolchains, tool qualification                   |
| Shared production / test process | Could a single manufacturing defect or test escape affect both?                     | Independent test, statistical sampling                   |

## DFA conclusion per pair

After the checklist, the analyst declares one of:

- **Independence demonstrated** — every relevant coupling factor either has no shared dependency or has a documented mitigation.
- **Mitigation in progress** — coupling exists; mitigation is planned and tracked as a safety-case open item.
- **Independence not demonstrated** — coupling cannot be eliminated; the decomposition is invalid and full ASIL inheritance must be applied.

## When DFA invalidates a decomposition

If the DFA concludes that the candidate pair is not independent, the per-node ASIL in the ASIL Allocation tab MUST revert to the SG's top-level ASIL. The TSC generator flags this back-propagation requirement as an open item in the FSC for the next regeneration; it does NOT silently update the FSC for the analyst.

## Common pitfalls

1. **Optimistic environmental assumptions.** Two MCUs in the same package share temperature, mechanical stress, and EMI exposure. "Different chips" is not enough; "different packages on different PCB regions with thermal isolation" is.
2. **Software diversity overstatement.** Two implementations written by the same team using the same patterns rarely diversify against design defects. True software diversity requires independent teams or formal proofs.
3. **Forgetting the test process.** A single test escape can ship the same bug to both channels. Consider sampling and independence in production verification.
4. **Confusing DFA with FMEA.** FMEA enumerates failure modes per element; DFA asks whether one event can take down multiple elements. They complement; one does not replace the other.
