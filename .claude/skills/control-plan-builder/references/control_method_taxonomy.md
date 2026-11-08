# Control Method Taxonomy

## Overview

A control method is the operational technique used to detect whether a manufacturing characteristic has drifted out of its specification or tolerance. It answers: "How will we know if this characteristic is good or bad?"

Five main categories:

1. **SPC (Statistical Process Control)** — charting and analyzing variation over time
2. **100% Inspection** — measuring or testing every part
3. **Mistake-Proofing (Poka-Yoke)** — hardware/software design that prevents errors
4. **Audit-Based Control** — periodic process observation and trending
5. **Hybrid/Layered** — combination of above (most realistic for complex processes)

---

## 1. SPC (Statistical Process Control)

### Xbar-R Chart (Rational Subgrouping)

**When to use:**
- Continuous variable data (dimensions, time, pressure, temperature)
- Subgroup size 2–9 parts
- Subgroups collected at rational time intervals (e.g., every hour, every 50 parts)
- Goal: detect shifts in process mean and variation

**Chart Setup:**
- Xbar (subgroup average): Center line = grand average; UCL/LCL = X-bar ± 3σ_Xbar
- R (subgroup range): Center line = avg range; UCL = D4 × R-avg; LCL = D3 × R-avg
- Constants (D3, D4) depend on subgroup size n (tables in ISO 7870)

**Example:**
```
Operation: PCB component placement accuracy (X-axis)
Spec: 1.50 ± 0.05 mm (tolerance = 0.10 mm)
Subgroup size: 5 parts
Frequency: every 50 parts (hourly)
SPC Xbar-R Chart:
  Xbar UCL: 1.52, Center: 1.50, LCL: 1.48
  R UCL: 0.03, Center: 0.015, LCL: 0.00
Reaction if Xbar > UCL or R > UCL: Stop, adjust machine, run pilot, restart
```

**Control Limits Source:**
- Initial Production: Calculate from first 20–30 subgroups (if process in control)
- Engineering Study: Capability study from pilot/prototype runs
- Historical: If process stable > 6 months and no changes, use existing limits

**Out-of-Control Rules (Nelson, Western Electric):**
- 1 point beyond 3σ (outside UCL/LCL)
- 9 points in a row on same side of center
- 6 points in row steadily increasing or decreasing (trend)
- 14 points in row alternating up/down (oscillation)
- 2 out of 3 beyond 2σ (warning zone)
- 4 out of 5 beyond 1σ
- 15 points in row within 1σ of center (too tight, possible data problem)

**Sampling Frequency Guidance:**
- Critical SC: every 1–2 hours or 50–75 parts
- Significant SC: every 2–4 hours or 100–150 parts
- Standard: every 4–8 hours or 200+ parts

---

### Xbar-S Chart

**When to use:**
- Continuous variable data, same as Xbar-R
- Subgroup size > 9 (large subgroups)
- Unequal subgroup sizes (e.g., some samples 5 parts, some 10)
- S (sample std dev) is more efficient than R for large n

**Chart Setup:**
- Xbar: same as Xbar-R
- S: Center = avg sample std dev; UCL = B4 × S-avg; LCL = B3 × S-avg
- Constants (B3, B4) depend on subgroup size (tables in ISO 7870)

**Example:**
```
Operation: Solder reflow oven temperature profile
Spec: 250°C ± 5°C
Subgroup size: 12 thermocouples per batch
Frequency: every 4 hours
SPC Xbar-S Chart: same rules as Xbar-R
```

---

### p-Chart (Proportion Defective)

**When to use:**
- Attribute (go/no-go) data: pass/fail, good/bad, conforming/nonconforming
- Variable sample size (not required, but helpful for trends)
- Count defective parts per sample; chart as proportion (p = # defective / sample size)
- Goal: detect shift in defect rate

**Chart Setup:**
- Center line: p-bar (overall proportion defective across all samples)
- UCL: p-bar + 3 × sqrt[p-bar × (1 − p-bar) / n]
- LCL: p-bar − 3 × sqrt[p-bar × (1 − p-bar) / n]

**Example:**
```
Operation: In-Circuit Test (ICT) of PCB
Pass criterion: all nets powered, voltages within spec, no shorts
Sample: 100 boards per hour
p-bar (historical): 0.02 (2% failure rate)
UCL: 0.02 + 0.018 = 0.038 (3.8%)
LCL: 0.02 − 0.018 = 0.002 (0.2%)
Reaction if p > UCL: Stop line, investigate ICT program or PCB quality
```

**Sampling Frequency:**
- 100–500 parts per sample (smaller sample → wider limits)
- Frequency: 1–2 samples per shift, or end-of-shift

---

### np-Chart (Count of Defective)

**When to use:**
- Same as p-chart, but sample size is constant
- Plot count (# defective) instead of proportion
- Easier to interpret for operators (e.g., "0 defects found today" vs. "0.5% failure rate")

**Chart Setup:**
- Center line: np-bar = p-bar × n
- UCL: np-bar + 3 × sqrt[n × p-bar × (1 − p-bar)]
- LCL: np-bar − 3 × sqrt[n × p-bar × (1 − p-bar)]

**Example:**
```
Operation: 100% Visual Inspection (solder quality)
Sample size: 50 boards (constant)
Defects per sample (np-bar): 1.5
UCL: 1.5 + 2.5 = 4
LCL: 1.5 − 2.5 = 0 (set to 0; cannot be negative)
Reaction if # defects > 4: Stop, rework, root cause (re-solder, inspect for process drift)
```

---

### c-Chart (Count of Defects Per Unit)

**When to use:**
- Count defects (not parts) per unit of production
- Examples: # solder joints with voids per board, # dents per meter of tubing, # assembly errors per product
- Unit size is constant (e.g., always per board, per 10 meters)
- Goal: detect shift in defect rate

**Chart Setup:**
- Center line: c-bar (average count of defects per unit)
- UCL: c-bar + 3 × sqrt(c-bar)
- LCL: c-bar − 3 × sqrt(c-bar) [set to 0 if negative]

**Example:**
```
Operation: Automated solder inspection (AOI)
Unit: each PCB (1 board = 1 unit)
Defect: solder void, bridge, cold joint
c-bar: 0.8 defects per board
UCL: 0.8 + 2.4 = 3.2
LCL: 0.8 − 2.4 = 0 (set to 0)
Reaction if c > 3.2 per board: Rework solder, investigate reflow oven or paste recipe
```

---

### u-Chart (Defects Per Unit, Variable Opportunity)

**When to use:**
- Same as c-chart, but opportunity (unit size) can vary
- Examples: # defects per meter (may inspect different lengths), # errors per part (parts may have different complexity)
- Normalized to defects per standard unit

**Chart Setup:**
- u = c / n (count of defects / unit size for each sample)
- Center line: u-bar (average defects per unit)
- UCL: u-bar + 3 × sqrt(u-bar / n-bar)
- LCL: u-bar − 3 × sqrt(u-bar / n-bar) [set to 0 if negative]

**Example:**
```
Operation: Manual assembly (e.g., automotive harness)
Unit: each harness (length varies: 2–5 meters)
Defect: wrong connector, missing crimp, loose terminal
u-bar: 0.05 defects per meter (from historical data)
Sample 1: 50 defects in 800 meters → u = 50/800 = 0.0625
Sample 2: 30 defects in 600 meters → u = 30/600 = 0.05
UCL (Sample 1, n=800): 0.05 + 3 × sqrt(0.05/800) = 0.056
Reaction if u > UCL: Investigate assembly technique, provide retraining
```

---

## 2. 100% Inspection

### Visual Inspection

**When to use:**
- Characteristics with clear pass/fail criteria (color, finish, orientation, label)
- Process capability is poor (Cpk < 1.33) and mistake-proofing not available
- High customer sensitivity (e.g., exterior surface finish, branding)

**Setup:**
- Define acceptance criteria (photos, physical master, spec chart)
- Train inspector; rotate every 30–60 min to combat fatigue
- Lighting: at least 500 lux (standard industrial), shadow-free
- Second opinion: 10–20% re-inspection by second inspector (attribute agreement ≥ 90%)

**Control Logic:**
- Accept if characteristic within tolerance/spec
- Reject if out; quarantine and route to rework/scrap decision

**Example:**
```
Operation: PCB label application
Characteristic: label position (X, Y, orientation)
Spec: within 5 mm of design center, < 5° rotation
Method: visual inspection + ruler/protractor
Frequency: 100% (every board)
Acceptance: label straight, centered, readable
Rejection: label skewed, off-center, or torn
Reaction: rework (remove/reapply) or scrap if adhesive damaged
```

---

### Dimensional Measurement (100%)

**When to use:**
- Tight tolerances where process capability inadequate (Cpk < 1.33)
- Gage R&R is < 10% (acceptable for 100% sorting)
- Characteristic is critical (e.g., bearing bore, fuel injector needle)

**Gages Used:**
- Coordinate Measuring Machine (CMM) — high accuracy (0.5–2 µm)
- Digital caliper — acceptable accuracy (±0.01–0.05 mm)
- Height gauge, depth gauge, pin gauge
- Automated vision (AOI) — for PCB solder, component placement, optical defects

**Control Logic:**
- Measure each part; accept if within spec; reject if out
- Trend: If 3–5 consecutive parts near high or low limit → stop, adjust, run pilot
- Sampling efficiency: Measure first 5 parts (first-piece), then every 25th part, every hour, or end of shift (80/20 rule)

**Example:**
```
Operation: Drill hole for fastener (critical fit)
Characteristic: hole diameter
Spec: 6.0 ± 0.05 mm
Gage: CMM or digital caliper
Method: 100% measurement
Reaction if out: Stop drill, adjust, re-drill, measure rework
Control limit (+/−1σ from center): 6.0 ± 0.02 mm for early warning
```

---

### Functional Test (100%)

**When to use:**
- Pass/fail electrical or functionality test (ICT, FCT)
- Test result is definitive (part works or doesn't)
- Firmware version or configuration must match (100% verification)

**Common Tests:**
- **ICT (In-Circuit Test)** — powered board, measures component values, traces continuity, checks shorts
- **FCT (Functional Test)** — unit runs real application, outputs compared to spec
- **Burn-in** — parts powered at stress levels (elevated temperature, voltage) for duration (4–48 hrs) to detect early failures
- **Firmware verification** — read-back and CRC check of programmed code

**Control Logic:**
- Pass: part meets all test criteria; ship
- Fail: part rejected; rework if possible, else scrap
- Trend: If # of failures increasing → investigate test program, board quality, or components

**Example:**
```
Operation: Final electrical/firmware checkout
Characteristic: ECU powers up, firmware version correct, boot sequence complete
Spec: all tests pass, firmware CRC = 0x12AB
Method: 100% FCT + firmware read-back
Frequency: every board
Reaction if fail: Rework (re-program, re-solder) or scrap (if unrepairable); investigate root cause
Control: Maintain log of # failures per lot; if > 5% in lot → hold lot, investigate supplier
```

---

## 3. Mistake-Proofing (Poka-Yoke)

### Prevention (Hard Stop)

**How it works:**
- Design removes possibility of error by making wrong action impossible
- Examples:
  - Part holder has slot only for correct orientation (can't insert wrong)
  - Connector keyed to prevent backward insertion
  - Solder machine detects insufficient solder → halts, alerts operator
  - Fixturing allows only correct assembly sequence

**Verification:**
- Test method: attempt to cause error; verify system prevents it
- Test frequency: monthly or per process change
- Owner: manufacturing engineer + operator sign-off

**Cost/Benefit:**
- Cost: high (design, tooling, validation)
- Benefit: 100% prevention (if design correct); no ongoing operator skill needed

**Example:**
```
Operation: Component orientation (critical)
Characteristic: resistor orientation (polarity matters)
Mistake: operator inserts resistor backward
Poka-Yoke: feeder tape physically prevents wrong orientation; component only drops if correct
Verification: attempt to insert backward; verify jam/no-drop
Owner: assembly supervisor; tested monthly
```

### Warning (Visual/Audible Alert)

**How it works:**
- System detects condition approaching or past limit; alerts operator to act
- Does not stop; operator chooses action
- Examples:
  - Red light if temperature drifting high
  - Audible alarm if pressure out of band
  - Inspect-first indicator (flag) if first-piece out of spec

**Verification:**
- Test method: trigger alert condition; verify response (light, sound, message)
- Test frequency: weekly or per shift startup
- Owner: operator + maintenance; documented in shift log

**Cost/Benefit:**
- Cost: low (sensors, PLC logic, indicator)
- Benefit: operator intervention catches drift; helps, but not foolproof (depends on alertness)

**Example:**
```
Operation: Solder reflow oven temperature
Characteristic: peak temperature profile (should be 255–265°C)
Alert: yellow light if temp > 270°C; red if > 280°C
Reaction: yellow → investigate, continue if stable; red → stop, cool oven, adjust ramp
Test: weekly: set temp to 275°C, verify yellow light; set to 285°C, verify red light
Owner: operator + maintenance technician
```

---

## 4. Audit-Based Control (Layered Process Audit, LPA)

**How it works:**
- Supervisor/auditor periodically observes process, verifies setup/calibration, measures samples, reviews trends
- Not real-time detection, but proactive (detects drift before many nonconforming parts made)

**Frequency (per OEM):**
- **Critical SC:** weekly (or per-shift for high-volume)
- **Significant SC:** bi-weekly (or weekly)
- **Standard:** monthly (or quarterly)

**Audit Checklist:**
- Machine setup: correct die/tool/temperature/speed?
- Gage calibration: current and within error limits?
- First-piece check: measure first part each setup; compare to spec
- Periodic measurements: measure ~5 parts during run; plot on SPC chart
- Process observation: operator technique, environment (contamination, temperature)
- Documentation: SPC chart up to date? Maintenance log current? Part traceability?

**Control Decision:**
- All measurements in spec, setup correct, SPC chart in control → Continue
- Any measurement out spec or SPC signal → Stop run, sort suspect parts, root cause

**Example:**
```
Operation: PCB placement machine (CPM) for component X/Y
Characteristic: component placement accuracy (X, Y, theta)
Audit frequency: weekly (Critical SC)
Audit checklist:
  — CPM calibration (vision system) within ±0.05 mm (last done: [date])
  — Feeder position correct (observed: OK)
  — First-piece: X = 12.48 mm (spec 12.50 ± 0.10) ✓
  — Sample parts (5) collected at 2-hr intervals: all within spec ✓
  — SPC Xbar-R chart reviewed: no out-of-control signals ✓
  — Maintenance: last PM [date]; next due [date]
Auditor signature: [name], date [date]
Result: Process in control; continue operation
Reaction if out: Stop, root cause, pilot, restart
```

---

## 5. Hybrid/Layered Control

**Real-world process usually combines methods:**

### Example: Critical PCB Solder Quality

1. **Primary:** 100% Automated Optical Inspection (AOI) detects voids, bridges, cold joints
2. **Secondary:** Manual visual spot-check (10%) by inspector (attribute agreement with AOI ≥ 90%)
3. **Tertiary:** X-ray sampling (5%) for under-fill or void below meniscus
4. **Audit:** Weekly LPA checks AOI program, verifies calibration, reviews rework logs

### Example: Bearing Bore Diameter

1. **Primary:** SPC Xbar-R (subgroup of 5 every 2 hours) for process control
2. **Secondary:** 100% first-piece check after setup change
3. **Tertiary:** Periodic 100% dimensional sort if Xbar approaches limit
4. **Audit:** Weekly check machine spindle TIR, gage R&R, tool wear trending

---

## Transition Logic: When to Change Control Method

### SPC → 100% Inspection
- Cpk drops below 1.33 (process incapable)
- Repeated OOC signals (> 2 per week)
- Gage R&R exceeds 30% (SPC limits unreliable)
- Customer escalation or high scrap rate

### 100% → Poka-Yoke
- Inspection cost too high (labor, time, re-test)
- Defect still slipping through (inspector fatigue)
- Root cause is systematic (always same orientation, always same position)
- Engineering feasible and cost-effective

### Any → Audit-Based
- Process mature and stable (Cpk > 1.67, low OOC frequency)
- Shift from detection to prevention (periodic check + trending instead of real-time)
- Reduces cost while maintaining risk management

---

## Selection Criteria: Quick Reference

| **Situation** | **Recommended Method** |
|---|---|
| Continuous variable, high-volume, Cpk > 1.67 | SPC Xbar-R or Xbar-S |
| Go/no-go data, high-volume, pass rate stable | p-chart or u-chart |
| Cpk < 1.33 or high customer sensitivity | 100% inspection |
| Dimension critical, inspection cost prohibitive | Poka-yoke (if feasible) |
| Process mature, low risk, low volume | Audit-based |
| Safety-critical characteristic | SPC + 100% first-piece + audit |
| Firmware/software version must match | 100% verification (read-back CRC) |

Always verify gage R&R before SPC; verify process capability before 100%; verify poka-yoke design before automation.
