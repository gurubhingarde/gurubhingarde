# AIAG-VDA Detection Table (1–10)

The Detection rating reflects the likelihood that a design review, analysis, testing, manufacturing inspection, or on-board diagnostic will catch the failure *before it reaches the customer*. It answers: "How likely is the failure to be detected in time to prevent harm?"

## Rating Scale

| Rating | Detection | Criteria | Evidence Examples |
|--------|-----------|----------|-------------------|
| **10** | Unlikely to Detect; No Prevention or Detection Method | No design control, test, inspection, or diagnostic in place; failure is latent (silent, undetectable without vehicle teardown or field failure); customer will be first to discover | - No design review of critical path - No testing of failure mode during validation - Silent failure with no on-board diagnostic (e.g., sensor signal corruption not cross-checked) - Manufacturing process has no inspection or automated test for this failure mode - Failure only manifests in rare use condition (extreme climate, years of operation) |
| **9** | Very Low Chance of Detection; Design Control Unlikely to Detect | Design review, analysis, or test exists but is weak or incomplete; high likelihood failure will escape to field | - Design review checklist does not explicitly cover this failure mode - Analytical method (e.g., thermal FEA) is rough; does not catch worst-case tolerance stack - Unit-level test passes but system-level integration test does not cover interaction - Manufacturing visual inspection is subjective; documented escapes of similar defects - On-board diagnostic exists but has holes; does not trigger in all failure scenarios |
| **8** | Low Chance of Detection | Design control (test, inspection, analysis) exists but is not comprehensive; failure could escape | - Design validation test covers nominal condition but not full tolerance stack or environmental extremes - Manufacturing inspection is automated but with <95% coverage - Design analysis is done (FEA, tolerance stack) but worst-case analysis not completed - On-board diagnostic exists; detects failure in >50% of scenarios but misses certain conditions |
| **7** | Moderate-Low Chance of Detection | Design control is reasonable but not robust; some reliance on fortunate detection | - Design validation testing covers most conditions but may miss one environmental stress (e.g., thermal cycling not fully characterized) - Manufacturing sampling plan inspects every 10th unit; some defects could escape - Design analysis is done but not independently reviewed - On-board diagnostic detects failure in ~60–70% of cases; some edge conditions not covered |
| **6** | Moderate Chance of Detection | Adequate design control; failure detection is probable but not certain | - Design validation testing is comprehensive (functional, environmental, tolerance) and documented; occasional edge cases possible - Manufacturing inspection is 100% on critical characteristic; statistical SPC in place - Design analysis (thermal, stress, tolerance stack) reviewed by independent expert - On-board diagnostic detects failure in >80% of scenarios; has been validated on similar platforms |
| **5** | Moderate-High Chance of Detection | Good design control in place; failure is likely to be detected but with some residual risk | - Design validation testing is comprehensive across all specified environments; includes accelerated life test (ALT) - Manufacturing inspection includes dimensional check (100%) plus functional test (sampling) - Design analysis independently peer-reviewed; worst-case and best-case bounds established - On-board diagnostic is field-proven on prior generation; detects failure in >90% of cases |
| **4** | High Chance of Detection | Strong design control; failure is very likely to be detected before reaching customer | - Design validation testing is extensive: functional (all modes), environmental (temperature, humidity, vibration per automotive standard), tolerance sweep, reliability (life test at 2–3× stress) - Manufacturing process is under statistical control (Cpk >1.33); 100% critical dimension inspection + 100% functional test - Design analysis is done with margin analysis; FEA validated against test data - On-board self-test executes on every startup or periodically; detects >95% of failure instances |
| **3** | Very High Chance of Detection | Robust design control; strong confidence failure will be caught | - Design validation is rigorous: exhaustive functional testing, environmental stress testing at 3–5× use condition, burn-in, design review with customer, independent audit - Manufacturing process has zero documented escapes for similar failure modes; SPC with Cpk >1.67 - Design margins are verified through analysis and test; sensitivity analysis confirms robustness - On-board self-test is real-time (not deferred); detects failure within seconds of occurrence; has redundant checks |
| **2** | Almost Certain Detection | Extremely robust control; failure is nearly impossible to miss | - Design validation includes customer beta testing; thousands of unit-hours in field-like conditions - Manufacturing process is validated with defect rate <0.01% and automated 100% inspection (machine vision, dimensional, functional) - Design margins are large (stress << rating); analyzed and tested across all foreseeable variation - On-board safety mechanism (e.g., watchdog timer, dual-core lockstep) catches failure *in the act* and triggers safe state |
| **1** | Certain Detection | Failsafe design; failure cannot escape to customer under any scenario | - Design is inherently safe (e.g., dual-core with real-time lockstep cross-check and immediate safe shutdown on mismatch) - Manufacturing process is under perfect control with zero known escapes across >1 million units; 100% non-destructive test with certified equipment - On-board safety mechanism is provably effective: tested, validated per ISO 26262, with metrics (diagnostic coverage, latency) documented - Failure is detected and remediated before any harm can occur (e.g., hydraulic lock prevents motion before sensor fails) |

## Guidance for Assessors

### Key Questions to Determine Detection

1. **What design controls exist?**
   - Design review? (Who? Checklist? Documented?)
   - Analysis? (FEA, tolerance stack, fault tree? Peer-reviewed?)
   - Testing? (Unit test? System test? Environmental? ALT?)
   - Manufacturing inspection? (100% or sampling? Automated or manual?)
   - On-board diagnostic? (Continuous or event-triggered? Coverage?)

2. **Is the control *before* customer delivery?** A test that finds the failure in warranty is better than field failure, but still impacts customer. A design review that prevents it before prototype is best. D=1–3 if caught before production; D=4–6 if caught in manufacturing; D=7–10 if discovered by customer or only detectable in field.

3. **What is the evidence for detection effectiveness?** 
   - Data (prior field data, test results, supplier SPC)? Use it.
   - No data? Assume worst case.

4. **Is the failure mode actually *detectable*?** Some failures are inherently silent (e.g., software timing drift that causes rare race condition). If you cannot detect it, D=9–10 by definition.

### Detection Control Maturity Levels

**Design Phase Controls** (highest impact):
- **D=1–3**: Robust design review covering failure mode explicitly; design is inherently resistant (margins, redundancy); analysis with independent peer review
- **D=4–5**: Design review by team; analysis done but not independently reviewed; some margin exists
- **D=6–7**: Design review per checklist; analysis available but cursory; margins not explicitly quantified
- **D=8–10**: Limited design review; analysis missing or incomplete; design margins not verified

**Validation/Testing Controls**:
- **D=1–3**: Comprehensive validation testing (functional, environmental, ALT, tolerance sweep, customer beta) with zero escapes of this failure mode
- **D=4–5**: Good validation testing; covers primary use cases and environments
- **D=6–7**: Basic validation; covers nominal conditions; may miss edge cases
- **D=8–10**: Limited testing; validation plan does not address this failure mode

**Manufacturing Controls** (catch after design is locked):
- **D=1–3**: 100% functional test with real-time feedback; statistical process control (SPC) with Cpk >1.67; zero historical escapes
- **D=4–5**: Sampling or AQL inspection; SPC with Cpk >1.33; occasional escapes but low rate
- **D=6–7**: 100% dimensional check on critical characteristic; sampling on others
- **D=8–10**: Visual inspection only (subjective); no automated test; loose process control

**On-Board Diagnostics** (last line of defense):
- **D=1–3**: Real-time self-test; covers >95% of failure modes; detects and responds immediately (safe state); validated per ISO 26262
- **D=4–5**: Periodic self-test (every startup or hour); covers 80–95% of modes; response is within minutes
- **D=6–7**: Self-test on request; covers 60–80%; user must interpret fault code
- **D=8–10**: No self-test; user relies on customer complaint

### Common Pitfalls

- **Assuming design review = detection**. A design review is valuable, but unless it is *exhaustive* and the failure mode is *explicitly on the checklist*, don't rate D too low. Many design reviews are cursory. A failure mode not mentioned in the review → D ≥ 6.

- **Confusing "testing exists" with "testing is effective"**. A test that finds this failure mode in 30% of cases is not very effective. D=7–8, not D=3. Require evidence (failure injection, sensitivity analysis) of test effectiveness.

- **Overestimating on-board diagnostic effectiveness**. A CAN message timeout check is good, but only catches *communication loss*, not sensor corruption (e.g., stuck output). Link diagnostic coverage to actual failure modes. If 3 out of 5 failure modes are detected, D ≈ 6–7, not D=2.

- **Assuming manufacturing test = foolproof**. Automated tests can fail too (bad fixture, calibration drift, test escapes). Unless you have historical data proving >99.9% catch rate, cap D at 4–5 for manufacturing controls alone.

- **Forgetting latent failures**. A failure that doesn't manifest until field use (e.g., solder crack that develops over thermal cycles) is hard to catch. Even with 100% manufacturing test, if the defect is dormant, D ≥ 7.

## Safety-Related Design Considerations

For DFMEA linked to ISO 26262 Functional Safety:
- **ASIL D** items typically require **Detection = 1–5** (robust controls with field-proven or analytically validated coverage)
- **ASIL C** items: Detection = 2–7 (good controls; some design margin)
- **ASIL B** items: Detection = 3–8 (reasonable controls; design not marginal)

The idea is that high-safety items must be *well-detected* to avoid reaching the customer in a latent fault state.

Example: Wheel speed sensor signal loss in ESC:
- **Failure Mode**: "Wheel speed = 0"
- **Detection Assessment**:
  - Design review: Covered explicitly in design FMEA ✓
  - Analysis: Electrical schematic review, connector rated for environment ✓
  - Testing: Functional test includes CAN timeout detection; accelerated vibration test (connectors tested to 20G) ✓
  - Manufacturing: 100% potting of connector; automated dimensional check ✓
  - On-board: CAN message timeout triggers diagnostic code (DTC) within 100 ms ✓
  - **Conclusion**: **D = 3–4** (multiple layers of control; robust but not failsafe; sensor could still degrade gradually)

Another example: Undetected lockstep mismatch (dual-core MCU):
- **Failure Mode**: "Bit flip in core A not caught by core B cross-check"
- **Detection Assessment**:
  - Design review: Dual-core lockstep explicitly specified; checker logic reviewed ✓
  - Analysis: Fault Injection Analysis (FIA) run; coverage of critical registers quantified ✓
  - Testing: EMC testing (ESD, conducted RF) to stress MCU; no lockstep errors observed ✓
  - Manufacturing: No specific test (bit flip is random); burn-in at elevated temperature ✓
  - On-board: Lockstep checker runs every cycle; mismatch triggers safe state immediately ✓
  - **Conclusion**: **D = 2–3** (failsafe design with on-board detection, but residual risk from bit flip not caught by checker; FIA may show coverage gap)
