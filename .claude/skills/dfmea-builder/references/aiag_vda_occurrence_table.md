# AIAG-VDA Occurrence Table (1–10)

The Occurrence rating reflects how likely the *failure cause* is to occur within the design's lifetime or production run. It answers the question: "How frequently will this cause manifest?"

## Rating Scale

| Rating | Occurrence | Criteria | Example Timeframe / Probability |
|--------|------------|----------|-------------------------------|
| **10** | Very High; Almost Certain | The failure cause is almost certain to occur during design life or within product warranty period; virtually all units may be affected; no prevention or design margin prevents occurrence | - Manufacturing process is not controlled and defect rate is >50% - Design has zero margin; any component variation triggers failure - Supplier has poor track record (>10% defect rate for this cause) - Environmental stress (thermal cycling, vibration) guaranteed to exceed component rating in <1% of units' lives |
| **9** | High; Very Likely | Failure cause is very likely to occur; high probability of repeated failures; majority of fleet may experience at least one instance | - Supplier defect rate 5–10% for relevant process step - Design margin is marginal; typical component variation approaches stress level - Environmental condition occurs frequently (daily or weekly) during vehicle operation - Prior design iteration had >5% field failure rate for this cause |
| **8** | Moderately High | Failure cause will likely occur multiple times in a large production run or field fleet; noticeable failure rate expected | - Supplier defect rate 1–5% - Design margin is adequate but not generous; stress is within typical component tolerance but near limits - Environmental condition occurs regularly (monthly) - Similar design has experienced 1–5% field failure rate |
| **7** | Moderate | Failure cause is reasonably likely to occur; occasional failures expected but not widespread | - Supplier defect rate 0.5–1% - Design includes some margin but not substantial - Environmental condition occurs occasionally (few times per year) - Historical data shows similar failure in 0.1–1% of fleet |
| **6** | Moderately Low | Failure cause is unlikely but not impossible; field failures occur but are uncommon | - Supplier defect rate 0.1–0.5% - Design includes adequate margin; component stress well within specification with typical variation - Environmental condition is rare (annual event or less) - No known history but similar architecture has low rate (<0.1%) |
| **5** | Low | Failure cause is unlikely under normal conditions; few field failures expected | - Supplier defect rate <0.1% for critical process - Design margin is good; component stress significantly below worst-case specification - Environmental condition is very rare (multi-year event) - Design validation testing shows >10,000-unit-hour confidence with zero failures |
| **4** | Very Low | Failure cause is remote; field failures are not expected under normal conditions | - Supplier defect rate <0.01% (exceptional quality) - Design margin is conservative; component stress well below nominal specification - Environmental condition is extraordinary (10-year event) - Prior validation on similar design tested millions of hours with zero failures of this mode |
| **3** | Remote | Failure cause is unlikely to occur during vehicle lifetime unless multiple other failures or severe abuse occur | - Failure requires two or more independent component failures (e.g., sensor AND diagnostic detector fail) - Design includes redundancy or protective mechanisms - Extreme environmental abuse (extended operating beyond specification) required - No field history of this failure in prior generations |
| **2** | Very Remote | Failure cause is extremely unlikely; would require extraordinary circumstances or combination of failures | - Failure requires three or more independent failures or cascading breakdown - Protective mechanisms explicitly prevent cause - Environmental stress would have to exceed specification by >100% - No theoretical mechanism identified without detailed analysis |
| **1** | Almost Impossible | Failure cause is theoretically possible but no credible path to occur; virtually impossible to conceive of realistic scenario | - Would require simultaneous failure of redundant systems and protective circuits - Environmental abuse would be physically implausible or lethal to occupant - No design flaw; would require misuse contradicting all warnings and instructions - Previous validation testing found zero incidents across millions of operational hours |

## Guidance for Assessors

### Key Questions to Determine Occurrence

1. **What causes this failure?** Identify the root cause: design margin, component tolerance, manufacturing process capability, environmental stress, human error, supplier quality.

2. **Do I have data?** Supplier defect rates, field failure rates from similar designs, or test data are gold. Use them.

3. **If no data, how does the cause arise?** 
   - Is it tied to a known manufacturing process? (Check capability, control limits, historical defect rate)
   - Is it a component tolerance stack-up? (Worst-case analysis: how often do components align badly?)
   - Is it environmental? (Operating temperature range, shock/vibration, humidity — how often does vehicle experience extremes?)
   - Is it a design margin issue? (Does stress exceed nominal rating? By how much? With what distribution?)

4. **Do I have design margin?** 
   - No margin (stress = rating) → O ≥ 7
   - Adequate margin (stress = 50–70% of rating) → O = 4–6
   - Conservative margin (stress = <30% of rating) → O ≤ 3

5. **Has this failure occurred in the field before?** Prior generations, competitor products, supplier experience. Use it.

### Likelihood Estimation Heuristics

- **Supplier Quality**: Assume O = 7 if supplier is unqualified or new. Reduce by 1–2 points if supplier is certified (ISO 9001, automotive Q-system). Reduce by 2–3 more if supplier has >10 years of flawless history for this part.

- **Manufacturing Process Capability (Cpk)**:
  - Cpk < 1.0 → O = 8–9 (process is out of control; high defect rate)
  - Cpk 1.0–1.33 → O = 6–7 (acceptable but marginal)
  - Cpk 1.33–1.67 → O = 4–5 (good process capability)
  - Cpk > 1.67 → O = 2–3 (excellent control)

- **Design Margin** (Stress Ratio = Stress / Rating):
  - Stress Ratio > 1.0 → O = 9–10 (immediate failure; design not viable)
  - Stress Ratio 0.8–1.0 → O = 7–9 (high risk)
  - Stress Ratio 0.5–0.8 → O = 5–7 (marginal)
  - Stress Ratio 0.3–0.5 → O = 3–5 (adequate margin)
  - Stress Ratio < 0.3 → O = 1–2 (conservative design)

- **Environmental Frequency**:
  - Daily → O = 8–9
  - Weekly → O = 6–7
  - Monthly → O = 4–5
  - Annually → O = 2–3
  - Multi-year event → O = 1

### Common Pitfalls

- **Confusing Severity with Occurrence**: A critical safety failure (S=10) may be extremely rare (O=1). Both ratings are correct. Do not reduce Severity because the failure is unlikely.
- **"We haven't seen it yet, so it's O=1"**: Absence of evidence is not evidence of absence. A new design without field history should use technical analysis (margin, tolerance, process capability) to estimate O, not default to O=1.
- **Optimism bias**: Assume worst case. If tolerance stack-up *could* go bad in 2% of units, that's O=6, not O=3. Validate with data.
- **Forgetting process variability**: Even a "Cpk 1.33" process will produce occasional defects. A single uncontrolled process step (e.g., potting, wave solder with no AOI) can drive O up significantly.

## Safety-Related Design Considerations

For DFMEA linked to ISO 26262:
- **ASIL D** items typically allocate Occurrence to causes that:
  - Have demonstrable low failure rate (<0.1% for primary components) OR
  - Are prevented by architecture (e.g., redundancy, dual-core lockstep) OR
  - Are detected with high coverage
- **ASIL C / B** items tolerate higher Occurrence if detection and mitigation are strong.

Example: Wheel speed sensor signal loss in ESC:
- **Failure Cause**: "Solder joint crack at sensor connector"
- **Occurrence Assessment**:
  - Wave solder process capability (Cpk 1.2) → base O = 6
  - Connector is potted (environmental protection) → reduce O by 1 → O = 5
  - Historical field data: 0.1% failure rate in similar design → O = 5 (aligned)
  - Conclusion: **O = 5** (low but not impossible)

Another example: Undetected lockstep mismatch in dual-core MCU:
- **Failure Cause**: "Bit flip in one core not caught by lockstep checker"
- **Occurrence Assessment**:
  - Bit flip rate per core ≈ 0.1 FIT (very rare) → base O = 1
  - Two independent cores must both experience bit flip without detection → compound probability much lower → **O = 1** is defensible
  - BUT if lockstep checker has coverage gap (e.g., doesn't check certain registers) → raise O to 2–3
  - Conclusion: **O = 1–2** depending on lockstep architecture and validation evidence
