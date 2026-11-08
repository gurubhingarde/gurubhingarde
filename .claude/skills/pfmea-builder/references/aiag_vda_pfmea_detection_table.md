# AIAG-VDA PFMEA Detection Rating Scale (1-10)

## How Likely Is the Detection Control to Catch the Failure?

Detection rates the **capability of the inspection or test method** to catch the failure mode *before the product is shipped to the customer*. Lower rating = better detection capability (more likely to catch defects). This is the opposite of Severity and Occurrence, where higher = worse.

Detection is rated based on the **probability that a defect will be caught** and prevented from reaching the customer. If there is no inspection or test, Detection = 10.

## Detection Scale

| Rating | Detection Level | Inspection Method | Detection Probability | Examples |
|--------|---|---|---|---|
| **1** | **Almost Certain to Detect** | Automated 100% inspection with high sensitivity; redundant checks; impossible to miss | 99%+ probability defect is caught | Automated Optical Inspection (AOI) with 100% component and solder joint coverage; X-ray inspection 100% (all BGAs); electrical continuity test (shorts detection) 100% coverage; functional test with comprehensive coverage |
| **2** | **Very Likely to Detect** | Automated inspection with good coverage; some edge cases possible but rare | 95-99% probability | AOI with 95%+ coverage (a few nets not visible); electrical netlist check; test coverage > 95% |
| **3** | **Likely to Detect** | Automated inspection or structured test; some defects possible to miss but unlikely | 90-95% probability | X-ray sampling (AQL 1.0); probe test with 90% coverage; cross-section analysis (sample); thermal imaging (sample) |
| **4** | **Likely to Detect** | Combination of automated + manual inspection; most defects caught | 85-90% probability | AOI + manual visual inspection (two-person team); functional test with coverage gaps known but small |
| **5** | **Moderate** | Manual inspection with structured process or automated with known gaps | 70-85% probability | Visual inspection per IPC-A-610 standard (Class A / B); trained inspector; checksheet or visual standard; electrical test with limited coverage |
| **6** | **Moderate / Low** | Manual inspection without formal standard; high operator dependency | 60-70% probability | Visual inspection without formal standard or training; "eyeball" test; inexperienced operator; manual dimensional measurement without fixturing |
| **7** | **Low** | Inspection by untrained operator or process; limited sampling | 40-60% probability | Untrained operator visual inspection; random sampling (AQL 4.0); operator eye test without standard; informal "sign-off" |
| **8** | **Very Low** | Minimal or informal inspection; process capability not verified | 20-40% probability | Occasional visual look (not systematic); rare sampling; process not monitored; operator signs off without actually testing |
| **9** | **Very Low / Almost No Detection** | Inspection is known to be ineffective; test has known gaps | 10-20% probability | Test coverage is known to be < 50%; visual inspection in poor lighting; no sampling plan; known probe points missing |
| **10** | **Cannot Detect (or No Control)** | No inspection method exists; defect is undetectable in field; process not monitored | < 1% probability (essentially impossible to catch) | No test for this failure mode; hidden defects (internal solder joint in potted assembly); no inspection at all; defect only appears after weeks of operation (latent) |

---

## Guidance for Rating Selection

### Use Detection 1-2 When:
- **Automated 100% inspection exists**: AOI, X-ray, electrical test covers 100% of the risk
- **Inspection has proven sensitivity**: Historical data shows > 99% catch rate
- **Defect is obvious**: Impossible to miss (e.g., open circuit with electrical continuity test)
- **Redundant checks**: Multiple independent methods confirm the same thing
- **Example**: AOI 100% placement coverage with high-resolution camera; functional test with comprehensive test vectors; electrical short detection with 100% probe coverage

### Use Detection 3-4 When:
- **Good automated inspection with minor gaps**: AOI with > 90% coverage; some nets not visible
- **Combination of automated + manual**: Two-step inspection; first automated, second manual confirmation
- **Structured manual inspection process**: Visual inspection per formal standard (IPC-A-610); trained operator; pass/fail checklist
- **Statistical sampling with tight AQL**: AQL 1.0 sampling (very stringent)
- **Example**: AOI placement with 95% coverage plus manual spot-check of edge components; X-ray inspection with AQL 1.0 sampling of all BGAs; functional test covering 90% of requirements with known gaps listed

### Use Detection 5-6 When:
- **Manual visual inspection with training**: Operator trained per IPC-A-610 or similar; visual standard in place
- **Automated test with known gaps**: Electrical test covers most nets but some missing (known coverage < 90%)
- **Sampling without tight AQL**: AQL 2.5 or looser (standard inspection, not stringent)
- **Operator-dependent process**: Relies on individual skill; inconsistent results possible
- **Example**: Visual solder joint inspection per IPC-A-610 by trained operator; ICT test covering 85% of nodes; dimensional measurement with fixture but high repeatability variation

### Use Detection 7-8 When:
- **Untrained or informal inspection**: "Eyeball test" without standard or training
- **Minimal sampling**: Very few units inspected; loose AQL (> 4.0)
- **Process capability not verified**: No baseline data on how well the inspection works
- **No formal acceptance criteria**: "Looks OK" is the only standard
- **Example**: Untrained operator visual inspection without formal standard; random sampling of 1% (no statistical basis); informal "sign-off" without testing

### Use Detection 9-10 When:
- **No inspection method exists for this failure mode**: No test, no visual check, nothing
- **Defect is latent (only appears later in use)**: Hidden until customer starts using product; impossible to catch in manufacturing
- **Inspection is known to be ineffective**: Historical data shows > 80% of these defects escape
- **Test has known major gaps**: Coverage is < 50% and gaps are known
- **Example**: No inspection for internal solder void (if X-ray not used); hidden corrosion (only appears weeks later in moisture); firmware latent bug (only triggers in specific use case); test coverage only 30% for this failure mode

---

## Common Detection Methods & Their Ratings

### Automated Optical Inspection (AOI)
- **100% component coverage, high resolution**: Detection 1-2
- **95%+ coverage**: Detection 2-3
- **80-95% coverage**: Detection 3-5
- **< 80% coverage** (known blind spots): Detection 6-8

### X-ray Inspection
- **100% inspection of all BGAs**: Detection 1-2
- **100% BGA sample (AQL 1.0)**: Detection 2-3
- **AQL 2.5 sampling**: Detection 4-5
- **AQL 4.0 or loose sampling**: Detection 5-7

### Electrical In-Circuit Test (ICT)
- **Test coverage > 98%**: Detection 1-2
- **Test coverage 90-98%**: Detection 2-4
- **Test coverage 80-90%**: Detection 4-6
- **Test coverage 50-80%**: Detection 6-8
- **Test coverage < 50%**: Detection 8-10

### Functional Test (FCT)
- **Comprehensive test of all critical functions**: Detection 1-2
- **Most critical functions tested**: Detection 2-4
- **Key functions tested**: Detection 4-6
- **Basic test of limited functions**: Detection 6-8
- **No comprehensive functional test**: Detection 10

### Visual Inspection (Per IPC-A-610)
- **Trained inspector, formal standard, pass/fail checklist**: Detection 4-5
- **Operator trained, visual standard available**: Detection 5-6
- **Operator minimally trained, informal standard**: Detection 6-7
- **Untrained operator, no standard**: Detection 7-9
- **No visual inspection at all**: Detection 10

### Manual Dimensional Measurement
- **Fixture-based, calibrated gage, trained operator**: Detection 4-5
- **Hand tool measurement, basic training**: Detection 5-7
- **Hand tool, no training**: Detection 7-9

### Statistical Process Control (SPC)
- **Real-time SPC monitoring, tight limits**: Detection 2-4 (catches out-of-control before many defects made)
- **SPC with reasonable limits, monitored**: Detection 4-6
- **SPC collected but not actively monitored**: Detection 6-8

---

## Designing Detection Controls: Best Practices

### 1. **Prefer Automated Over Manual**
- Automation is consistent 24/7
- Manual inspection fatigues and inconsistent
- Use automated whenever possible (AOI, X-ray, electrical test)

### 2. **Layer Multiple Detection Methods (Defense in Depth)**
- Use both automated (AOI) and manual (visual check) for highest confidence
- Automated catches systematic issues; manual catches exceptions
- Example: AOI 100% + sample X-ray + electrical test = Detection 1-2

### 3. **Make Inspection 100% if Severity is High**
- High severity (8-10) failure modes should have 100% inspection
- Sampling is only acceptable if severity is low-to-moderate (< 7)
- Example: Critical firmware programming must have 100% checksum verification (Detection 1), not sampling

### 4. **Know Your Test Coverage**
- For electrical / functional tests, formally document coverage percentage
- Use coverage metrics: (# testable nodes / total nodes) × 100
- If coverage < 80%, acknowledge the gap and plan for additional inspection (e.g., AOI)

### 5. **Training Matters for Manual Inspection**
- Untrained operator = Detection 8-9 (ineffective)
- Trained operator with standard = Detection 4-5 (acceptable)
- Trained operator + equipment + checklist = Detection 3-4 (good)

### 6. **Avoid False Security**
- Do NOT claim Detection 2 for a test that has never been validated
- Do NOT assume manual inspection is reliable without baseline data
- Cite evidence: pilot data, supplier certification, test report, historical performance

---

## Examples: ESC ECU Assembly

| Failure Mode | Detection Control | Coverage / Evidence | Rating | Justification |
|---|---|---|---|---|
| MCU placed backwards | AOI 100% rotation check | AOI reports orientation on all ICs | **1** | Automated, 100% coverage, high sensitivity to rotation angle |
| Cold solder joint | X-ray AQL 1.0 + AOI wet | AOI covers solder joints; X-ray samples every lot with AQL 1.0 | **3** | Layered: AOI catches obvious; X-ray confirms internal quality via sampling |
| Wrong resistor value | Visual inspection + BOM check | Two-person verification; BOM database check | **4** | Structured manual + database; high likelihood to catch; still some operator dependency |
| Trace bridge (short) | ICT electrical test | Test coverage 98% of nets; known blind spots on 2 power traces | **4** | Automated electrical test; high coverage; minor gaps known and accepted |
| Missing capacitor | AOI + visual | AOI detects missing component; manual backup visual | **2** | Automated 100% + manual confirmation; very unlikely to miss |
| Firmware wrong version | Checksum verification + BOM | Automated bootloader checksum; programming software logs version; BOM cross-check | **1** | Automated verification; impossible to pass checksum with wrong code; version logged |
| Connector not fully seated | Mechanical insertion force test | Insertion force gage checks seating depth during assembly | **3** | Automated mechanical test; high reliability; rare false positives |
| Solder bridge between traces | AOI 100% coverage | AOI resolution detects < 0.3mm bridging; 100% coverage | **2** | Automated high-resolution; 100% coverage; very likely to detect |
| Conformal coat missing coverage | Visual inspection (sample 10%) | Operator visual inspection per IPC-A-610; 10% sampling | **6** | Manual visual; sampling only; operator dependent; moderate confidence |
| Test gap (ICT missed net) | Functional test | FCT exercises power supply; if short is present, supply fails; FCT detects | **5** | Second-line detection via functional test; catches power-critical defects; some gaps possible |

---

## Integration with Action Priority

Remember:
- **Severity** = how bad if it reaches customer (1-10)
- **Occurrence** = how likely to occur (1-10)
- **Detection** = how likely to catch it (1-10, where 10 = cannot catch)

**Action Priority = AIAG-VDA lookup(S, O, D)**

If Detection rating is high (detection method is weak), AP will be high (more urgent action needed). Improvement actions typically focus on:
1. **Reducing Occurrence** (process improvement, design change)
2. **Increasing Detection** (add/enhance inspection, test coverage)
3. **Reducing Severity** (design mitigation, warning light)

Always cite evidence when claiming low Detection (good inspection). "Assumed 80% coverage" is not evidence.
