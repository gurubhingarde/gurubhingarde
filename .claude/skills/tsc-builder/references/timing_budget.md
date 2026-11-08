# Timing Budget — FTTI = FDTI + FRTI

## The basic equation

```
FTTI ≥ FDTI + FRTI
```

| Term | Meaning                                                                               |
|------|---------------------------------------------------------------------------------------|
| FTTI | Fault Tolerant Time Interval — maximum time from fault occurrence to safety goal violation. Set in HARA / FSC. |
| FDTI | Fault Detection Time Interval — time from fault occurrence to detection. Owned by HW + diagnostic SW. |
| FRTI | Fault Reaction Time Interval — time from detection to safe-state achievement. Owned by SW + actuator. |

If `FDTI + FRTI > FTTI`, the safety mechanism does not satisfy the safety requirement and either the mechanism must be made faster or the safe state must be reachable on a shorter path.

## Allocation defaults the TSC generator uses

When the analyst doesn't override, the generator splits the FTTI 50 / 50:
- FDTI = 50% of FTTI
- FRTI = 50% of FTTI

These are starting points, not answers. The analyst tightens FDTI when:
- The detection mechanism samples slower than the budget allows (e.g., a 100 ms plausibility check against a 50 ms FDTI budget — impossible).
- The fault propagates faster than expected (e.g., a hydraulic transient builds in 30 ms; FDTI must be < 30 ms even if FTTI is 200 ms).

The analyst tightens FRTI when:
- The actuator reaction is slow (e.g., a hydraulic valve takes 80 ms to release; FRTI must include that time).
- The safe state involves a sequence (e.g., warn driver → disable actuator → log DTC); FRTI must accommodate the whole sequence.

## Multi-stage safe state

Some safe states have intermediate states (degraded operation → warning → full disable). When this is the case, the TSC author breaks the FRTI into per-stage budgets and records each in the Timing Budget tab. The skill creates a single FRTI row per FSR by default; the analyst inserts stages as needed.

## Common pitfalls

1. **Treating FTTI as a contractual maximum.** It is the maximum allowed; aiming for half of it is good engineering practice because development hardware rarely matches the spec exactly.
2. **Missing the actuator reaction time.** The "SW transitions to safe state in 10 ms" claim is meaningless if the actuator takes 80 ms to release. FRTI is end-to-end, not just SW.
3. **Confusing FDTI with the polling interval.** FDTI is worst-case detection time, which usually equals 2× polling interval (one to miss the cycle the fault appeared in, one to catch it next cycle).
4. **Forgetting the diagnostic mechanism's own latency.** ECC takes a few cycles, plausibility takes one sample, lockstep takes one comparison cycle — these add to FDTI even when the detection method is "fast".
