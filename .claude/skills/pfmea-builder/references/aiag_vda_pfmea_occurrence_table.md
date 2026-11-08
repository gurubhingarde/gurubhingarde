# AIAG-VDA PFMEA Occurrence Rating Scale (1-10)

## How Likely Is the Failure Mode to Occur?

Occurrence rates the **frequency or probability** that the failure mode will occur during the production run (or mission life). It is based on design capability, process capability, or operator skill level. Higher = more likely to occur.

Occurrence should be estimated from **objective data** whenever possible (pilot yield, field failure history, capability studies, supplier data). Avoid pure guessing.

## Occurrence Scale (Defects Per Million Opportunities, DPMO, or PPM)

| Rating | Occurrence Level | DPMO / PPM | Failure Rate | Examples |
|--------|---|---|---|---|
| **1** | **Remote / Extremely Rare** | < 1 per million | < 1 : 1,000,000 | Inherent design margin so large that failure is virtually impossible. Supplier data shows flawless performance over years. |
| **2** | **Very Low** | 1 to 10 per million | 1 : 100,000 to 1 : 1,000,000 | Well-proven process or design; pilot data shows zero defects in large sample. Exceptional process capability (Cpk > 1.67). |
| **3** | **Low** | 10 to 50 per million | 1 : 20,000 to 1 : 100,000 | Mature process with good controls. Pilot yield > 99.5%. Cpk 1.33 to 1.67. |
| **4** | **Low / Moderate** | 50 to 100 per million | 1 : 10,000 to 1 : 20,000 | Stable process with adequate controls. Pilot yield 99% to 99.5%. Cpk 1.0 to 1.33. |
| **5** | **Moderate** | 100 to 500 per million | 1 : 2,000 to 1 : 10,000 | Mixed track record; some defects observed in pilot. Cpk 0.67 to 1.0. Process capability borderline; requires monitoring. |
| **6** | **Moderate / High** | 500 to 1,000 per million | 1 : 1,000 to 1 : 2,000 | Recurring defects in pilot; process capability weak. Cpk 0.33 to 0.67. Scrap/rework > 5% observed. |
| **7** | **High** | 1,000 to 5,000 per million | 1 : 200 to 1 : 1,000 | Process has chronic quality issues. Cpk < 0.33. Pilot scrap/rework 5-10%. Process not under statistical control. |
| **8** | **High / Very High** | 5,000 to 10,000 per million | 1 : 100 to 1 : 200 | Significant defects observed in pilot. Process centering way off. Scrap/rework > 10%. Capability study shows repeatable failures. |
| **9** | **Very High** | 10,000 to 100,000 per million | 1 : 10 to 1 : 100 | Widespread, recurring failures. Process in chaos. No effective controls. Expected to see 1-10% defect rate in production. |
| **10** | **Almost Certain** | > 100,000 per million | > 1 : 10 | Failure will almost surely occur in early production or pilot. Obvious design flaw or process incapable. Expected to see > 10% defect rate. |

---

## Guidance for Rating Selection

### Use Occurrence 1-2 When:
- **Design margin is huge**: Operating parameters are far from limits
- **Field history is perfect**: No failures reported in similar products or processes over many years/vehicles
- **Supplier data is excellent**: Supplier provides certification of high reliability (e.g., < 1 DPMO)
- **Process is mature and stable**: Cpk > 1.67, no variation observed in pilot
- **Example**: Resistor solder joint failure (if resistor properly selected and reflow process proven); passive component shorts (extremely rare in modern manufacturing)

### Use Occurrence 3-4 When:
- **Pilot yield is excellent**: > 99% (zero to few defects in 1,000 units)
- **Process capability study shows Cpk 1.0 to 1.67**: Good margin
- **Proven equipment and procedure**: Vendor-supplied equipment with proven uptime
- **Example**: Component placement accuracy (if pick-and-place machine is calibrated and maintained); solder joint quality (if reflow profile is proven)

### Use Occurrence 5-6 When:
- **Pilot data shows mixed results**: 99-99.5% yield; some rework observed
- **Process capability borderline**: Cpk 0.67 to 1.0 (approaching limit)
- **Recurring minor defects observed**: Same root cause seen multiple times during pilot
- **Operator skill varies**: Depends on training; some operators better than others
- **Example**: Manual assembly step (high operator dependency); solder paste printing (paste freshness, stencil maintenance critical)

### Use Occurrence 7-9 When:
- **Pilot yield < 99%**: 5-10% or higher defect rate observed
- **Process capability study shows Cpk < 0.67**: Weak; process may be centering off
- **Chronic quality issues**: Same defect observed repeatedly despite multiple fix attempts
- **No effective controls in place**: Inspection or SPC missing; process not monitored
- **Equipment unreliability**: Frequent downtime or maintenance issues
- **Example**: Manual hand-soldering of fine-pitch components (high defect rate without expert operators); coating spray process (coverage highly variable); programming with inadequate test coverage (false passes expected)

### Use Occurrence 10 When:
- **Failure is virtually certain in early production**: Pilot shows widespread failures
- **Design is obviously flawed**: No reasonable way it can work as specified
- **Process is completely incapable**: Equipment broken or absent; procedure undefined
- **Example**: Attempting to place 0.3mm pitch BGA with visual inspection only (will fail 100% of the time); attempting to program MCU with corrupted firmware (will fail on every unit)

---

## Data Sources for Occurrence Rating

### 1. **Pilot Production Yield**
- Conduct pilot run of 300-500 units (statistically representative)
- Track scrap and rework by failure mode
- Calculate % defective = (# defects) / (# units) × 100
- If 1 failure observed in 500 units → 0.2% = 2,000 DPMO → **Rating 5-6**

### 2. **Process Capability Study (Cpk)**
- Measure process output (e.g., component placement accuracy, solder joint height, temperature profile)
- Compare against specification limits
- Calculate Cpk = (min(USL - μ, μ - LSL)) / (3σ)
- Cpk > 1.67 → **Rating 1-2**
- Cpk 1.33-1.67 → **Rating 3-4**
- Cpk 1.0-1.33 → **Rating 4-5**
- Cpk 0.67-1.0 → **Rating 5-6**
- Cpk < 0.33 → **Rating 7-10**

### 3. **Field Failure History**
- Review prior products with similar process steps
- Calculate failure rate: (# failures / total units sold) × 1,000,000 = FPMH or FPMY
- Example: 50 failures in 100,000 units shipped → 500 DPMO → **Rating 6**

### 4. **Supplier Data**
- Request supplier DPMO or AQL rating for components
- Semiconductor datasheets provide failure rate (FPMH or FIT = failures per 10^9 hours)
- Example: MCU supplier reports 100 FIT over 10-year life → extrapolate to production

### 5. **Engineering Judgment**
- If no objective data exists, team must estimate based on:
  - Process complexity (simple = low O, complex = high O)
  - Operator skill required (manual = higher O, automated = lower O)
  - Environmental sensitivity (temperature, humidity, ESD control)
  - Repeatability of setup (fixture repeatability, calibration stability)

---

## Examples: ESC ECU Assembly

| Failure Mode | Occurrence Basis | Data | Rating | Justification |
|---|---|---|---|---|
| MCU placed backwards | Pilot experience | 0 defects in 500 units; AOI 100% catch | **2** | Pick-and-place vision system is reliable; rare human error |
| Cold solder joint | Process capability | Reflow oven Cpk = 0.8; pilot yield 98% | **6** | Borderline process; some defects expected; needs tighter control |
| Wrong resistor value in kit | Supplier history | Component dispensing system 99.8% accurate | **3** | Mature supplier with proven dispensing logic; rare errors |
| Trace bridge (solder short) | Pilot data | 2 defects in 500 units solder paste printing; solder paste quality varies | **5** | Paste freshness and stencil aperture are variable; moderate risk |
| Missing capacitor | Operator skill | Manual placement; operator turnover high | **7** | High dependency on operator attention; no mistake-proofing |
| Firmware wrong version | Programming procedure | Formal loader + checksum verification; zero defects in prior builds | **1** | Automated with verification; virtually impossible to load wrong version |
| Labeling mistake | Printer reliability | Label printer sometimes jams; label adhesive occasionally fails | **6** | Equipment reliability marginal; some labels fail to apply |
| Connector not fully seated | Assembly procedure | Mechanical assembly procedure clear; trained operators | **4** | Well-trained team; good fixture design; low error rate expected |
| Conformal coat coverage gaps | Spray process | Spray booth humidity/temperature variable; coverage varies 90-98% | **7** | Process highly variable; no 100% inspection; gaps expected |
| ICT test false pass | Test program | Test coverage 92%; some net not probed | **8** | Test gaps known; defects expected to escape; high risk |

---

## Iterating Occurrence After Production Launch

After production ramps up:
1. Track actual defect rates by failure mode
2. Update Occurrence ratings as real data arrives
3. Adjust control methods if actual O is higher than projected
4. Example: If cold solder joints occur at 1.5% rate in early production (15,000 DPMO), update O from 6 to 9 and trigger immediate action (reflow profile tightening, SPC implementation, 100% X-ray inspection)

**Always use the most recent production data to keep PFMEA current.**
