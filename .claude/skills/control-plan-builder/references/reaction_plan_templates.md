# Reaction Plan Templates

## Overview

A reaction plan defines the operational sequence when a characteristic goes out of control. It answers: "If SPC signals drift, or inspection finds a defect, or gage fails, what do we do immediately?"

Every reaction plan must specify:
1. **Trigger** — what event initiates the reaction (e.g., "Xbar chart point outside UCL")
2. **Immediate Actions** — what happens in first 15–30 minutes (stop, sort, quarantine, notify)
3. **Investigation** — root cause determination (machine, tooling, material, setup, operator)
4. **Corrective Action** — engineering fix or process adjustment
5. **Verification** — how to confirm fix is effective before resuming
6. **Documentation** — incident log, root cause report, CAPA close-out
7. **Timeline** — when each step must be complete
8. **Owner/Escalation** — who decides each action, when to escalate

---

## Template 1: Stop Production & Quarantine

**Trigger:**
- SPC signal (point beyond 3σ, trend, etc.)
- Visual inspection finds non-conforming part
- Gage detects out-of-spec dimension
- Poka-yoke device activates (hard stop)

**Immediate Actions (0–15 min):**
1. Stop production at operation
2. Quarantine current run (from last in-control signal to present) in designated area
3. Tag parts "HOLD — UNDER INVESTIGATION"
4. Notify shift supervisor and quality engineer
5. Do NOT scrap or rework yet

**Root Cause Investigation (15 min – 2 hours):**
1. Verify gage is calibrated (check calibration date; if due, recalibrate)
2. Measure suspect parts from quarantine; determine % nonconforming
3. Inspect machine setup (clamps, tool wear, thermal, spindle TIR if applicable)
4. Review process parameters (temperature, pressure, speed, feed)
5. Check raw material batch (lot code) — did material lot change?
6. Interview operator (technique, environmental conditions, part ID)
7. Document findings in incident form

**Example Root Causes & Corrections:**
| Root Cause | Correction | Verification |
|---|---|---|
| Tool wear | Replace tool, return to position | Measure first 3 parts; all within spec |
| Temperature drift | Check heater/sensor, recalibrate | Run 5-min warm-up, measure temp, confirm stable |
| Setup error (wrong die) | Replace with correct die, re-clamp | First-piece check; measure 5 parts |
| Material batch bad | Verify batch traceability; notify supplier | 100% inspect current lot; inspect 10% of prior lot |
| Operator technique | Retraining, supervised restart | Auditor observes first 20 parts |

**Corrective Action (2–8 hours):**
1. Implement fix (tooling change, machine adjustment, material replacement, training)
2. Document in work order or maintenance log
3. Get supervisor sign-off on fix

**Verification (before restart):**
1. Run first-piece check: measure 5 parts; all in spec? YES → proceed; NO → repeat root cause
2. Run pilot: 20 parts on corrected process; measure every part or every 5th part
3. SPC chart for pilot: all points in control? If yes → proceed to restart; if no → hold, investigate
4. Quality engineer approval required before restarting full production

**Quarantine Decision:**
- **All parts conforming (100%):** Release to customer
- **Some parts nonconforming (< 10%):** 100% sort (inspect all, scrap bad)
- **High nonconformance (> 10%):** 100% rework (all parts reworked, 100% inspected) OR scrap + supplier escalation
- **Severity high (safety/regulatory):** scrap without rework; notify customer

**Documentation:**
```
Control Plan Reaction Log
Date/Time: [ISO datetime when signal detected]
Operation: [process step, machine, operator]
Characteristic: [char #, spec, what was found]
Trigger: [SPC signal / defect / gage / poka-yoke]
Quarantine volume: [# parts on hold, lot ID]
Root cause: [one-line summary]
Corrective action: [one-line summary, work order #]
Verification: [first-piece results, pilot results]
Restart approval: [supervisor name, quality engineer name]
Date/time restart: [ISO datetime]
Owner: [quality engineer name]
Follow-up CAPA (if needed): [yes/no, CAPA #]
```

**Timeline:**
- **0–15 min:** Stop, quarantine, notify
- **15 min – 2 hours:** Root cause investigation
- **2–8 hours:** Corrective action, verification, approval
- **8+ hours:** Restart production (if on same shift; else next shift)

**Escalation:**
- **Immediate:** Quality Engineer, Shift Supervisor
- **If > 10% nonconforming:** Plant Quality Manager, Material Review Board (MRB)
- **If customer impact likely:** Customer Quality Engineer, supplier account manager
- **If safety or regulatory:** Plant Manager, Legal, Regulatory Affairs

---

## Template 2: Containment & 100% Sort

**Trigger:**
- Medium-risk process signal (Xbar approaching limit, one point beyond 2σ)
- Visual inspection finds isolated nonconforming parts (< 5%)
- Process margin eroding (trend toward limit)

**Immediate Actions (0–15 min):**
1. Hold current lot (do NOT stop all production; other lines may continue)
2. Begin 100% inspection/sort of current lot
3. Notify quality engineer and line supervisor
4. Continue production with heightened sampling

**100% Inspection & Sorting:**
1. Measure/inspect ALL parts in current lot (from last good sample to present)
2. Accept: parts within spec → release to shipping
3. Reject: parts out of spec → quarantine for scrap or rework decision
4. Trend: record % defective; if > 5% → escalate to Template 1 (stop & investigate)

**Root Cause Investigation (2–8 hours, parallel to sorting):**
1. While sorting ongoing, investigate machine condition (gage calibration, setup, tool)
2. Check for any process parameter drift (temperature trending, pressure cycling)
3. Material lot check; review operator log

**Corrective Action (by end of shift or next day):**
- If investigation reveals preventive action needed (e.g., gage needs service, tool due for replacement), schedule and execute
- If no clear root cause but sorting revealed high nonconformance, increase audit frequency temporarily

**Verification:**
1. After sorting complete, resume normal SPC sampling
2. Run next 2 subgroups; confirm in control
3. Resume normal frequency

**Quarantine Decision:**
- Rejected parts: 100% rework (if simple fix, e.g., resize) + 100% re-inspect, OR scrap
- Record rework cost and root cause

**Documentation:**
```
Containment & Sort Log
Date/Time: [ISO datetime]
Lot ID: [part number, lot, serial range]
Trigger event: [SPC signal / inspection / trend]
Sort method: [visual / measurement / functional]
Results: Total inspected = [N]; Conforming = [N]; Nonconforming = [N] ([%])
Root cause (preliminary): [observation]
Corrective action: [if any]
Rework disposition: [scrap / rework / released as-is with approval]
Status: [complete; ready to resume normal control]
Owner: [quality engineer]
Date signed: [date]
```

**Timeline:**
- **0–30 min:** Stop lot, begin sort
- **30 min – 8 hours:** Sort + root cause investigation (parallel)
- **8–24 hours:** Corrective action (if needed), re-test, approval, resume

**Escalation:**
- **If > 10% nonconforming:** Material Review Board (MRB) for disposition decision
- **If delay > 4 hours:** Notify customer (may affect delivery)
- **If safety/regulatory risk:** escalate per Template 1

---

## Template 3: Supplier Escalation (Purchased Item)

**Trigger:**
- Incoming inspection rejects material from supplier
- Control plan detects high nonconformance from supplier component
- Supplier corrective action overdue

**Immediate Actions (0–30 min):**
1. Quarantine supplier material lot (do NOT use in production)
2. Contact supplier quality engineer (phone + email)
3. Notify Procurement; place supplier on watch status
4. Document part/lot/nonconformance in supplier scorecard

**Communication (30 min – 2 hours):**
1. **Supplier notification email template:**
   ```
   Supplier: [name]
   Part: [part number, supplier P/N]
   Lot: [lot ID, date code]
   Rejection criteria: [spec limit, visual defect, test failure]
   # Rejected: [count], % defective: [%]
   Requested Action: 100% incoming inspection of lot; root cause analysis within 24 hours
   Attachment: inspection data, photos if visual
   Expected response: [date/time, typically within 4 hours for critical items]
   Contact: [your name, phone, email]
   ```

2. Supplier conducts 100% incoming inspection on suspect lot
   - All parts measured/tested
   - Conforming parts released with MRB approval (after-the-fact acceptance)
   - Nonconforming parts scrapped or reworked by supplier (at supplier cost)

3. Supplier root cause analysis (due within 24 hours for Critical, 5 days for Standard)
   - Corrective action plan (specific fix, not just "increase inspection")
   - Implementation date
   - Verification method (test certificate, witness audit, etc.)

**Corrective Action:**
- **If material available:** 100% sort current lot; continue production (if sort timely)
- **If material unavailable:** Expedite replacement lot from supplier with immediate test certs
- **If chronic issue (> 2 occurrences in 6 months):** Schedule supplier plant audit, require TSC/MSA review

**Documentation:**
```
Supplier Quality Event
Date: [date]
Supplier: [name]
Part: [P/N, description]
Lot/Serial: [lot ID, date code]
Rejection reason: [spec, test, visual]
# Rejected: [count], % defective: [%]
Initial notification: [date/time sent]
Supplier response time: [hours to acknowledge]
Root cause (supplier): [statement from supplier]
Corrective action: [description + implementation date]
Verification: [method, date completed]
Follow-up audit: [yes/no; if yes, scheduled for [date]]
Status: [open / closed]
Owner: [buyer, quality engineer]
Date closed: [date]
```

**Timeline:**
- **0–30 min:** Quarantine, notify supplier
- **30 min – 4 hours:** Supplier acknowledgment
- **4–24 hours:** Supplier root cause + CAPA plan
- **24–48 hours:** Implementation + verification (if quick fix)
- **48 hours – 5 days:** Verification + close-out (if complex fix)

**Escalation:**
- **2nd occurrence in 6 months:** Escalate to Procurement; consider new supplier evaluation
- **3rd occurrence:** Require supplier to audit own process; possibly delist supplier
- **Safety issue:** Immediate escalation to VP Quality and customer

---

## Template 4: Process Adjustment & Restart (Tuning)

**Trigger:**
- SPC trend visible (e.g., 5 points drifting toward UCL, but not yet out)
- Gage 1st-piece check approaching limit (within 1σ of limit)
- Early warning from audit (machine shows wear, temperature slow drift)

**Immediate Actions (0–15 min):**
1. Do NOT stop; continue production with heightened observation
2. Notify shift supervisor; request process engineer visit
3. Prepare to adjust machine parameter (e.g., temperature setpoint, tool offset, feed rate)

**Process Engineer Assessment (15–45 min):**
1. Review SPC chart: confirm trend, estimate rate of change
2. Inspect machine: spindle TIR, tool wear, thermal stability
3. Check recent setup changes or maintenance work
4. Decide: adjust now or wait for end of shift?

**Adjustment (45 min – 2 hours):**
1. Small tuning adjustment to machine parameter (e.g., raise temperature by 2°C, offset tool by 0.02 mm)
2. Let machine stabilize (5–10 min warm-up or settling time)
3. Run 5–10 pilot parts; measure all; confirm adjustment effective

**Verification:**
1. Pilot parts all within spec and centered? → YES: resume normal production
2. Pilot parts still drifting? → Repeat adjustment or escalate to Template 1 (full root cause)

**Documentation (brief):**
```
SPC Tuning Log
Date/Time: [ISO datetime]
Characteristic: [char #]
Trigger: [trend / approach limit / 1st-piece]
Adjustment: [parameter, from value, to value]
Pilot results: [5 measurements, all in spec? YES/NO]
Engineer: [name], Date: [date]
```

**Timeline:**
- **0–15 min:** Notification
- **15–45 min:** Assessment
- **45 min – 2 hours:** Adjustment + pilot
- **2 hours:** Approval + resume

**Escalation:**
- If pilot fails → escalate to Template 1 (stop & investigate)
- If same adjustment needed > 2 times per day → investigate root cause (wear progression, setpoint drift)

---

## Template 5: Poka-Yoke Device Activation

**Trigger:**
- Hardware or software poka-yoke device detects invalid condition (e.g., wrong orientation jam, insufficient solder detected by machine vision)

**Immediate Actions (0–5 min):**
1. Operator notices jam, warning light, or audible alarm
2. Operator stops and calls supervisor
3. Part is held in fixture (not ejected, not sent to next station)

**Resolution (5–30 min):**
1. Supervisor and process engineer assess part and fixture
2. Determine cause: operator error (wrong part orientation) vs. machine error (bad part feature, worn fixture)
3. Root cause:
   - **Operator error:** Reorient part correctly, release
   - **Bad part:** Remove, inspect, quarantine (send to rework/scrap decision)
   - **Worn fixture:** Tag fixture for maintenance, use backup fixture or tooling

**Verification:**
1. After first jam, run 5–10 pilot parts through fixture; all pass? → Resume
2. If jams repeat → escalate to process engineer for fixture maintenance

**Documentation:**
```
Poka-Yoke Event Log
Date/Time: [ISO datetime]
Device: [ID, type, characteristic protected]
Activation count: [# times activated today]
Root cause: [operator / part / fixture]
Action taken: [reorient / scrap / maintenance]
Engineer: [name], Date: [date]
```

**Timeline:**
- **0–5 min:** Detection, stop
- **5–30 min:** Assessment, correction
- **30 min – 1 hour:** Pilot, resume

**Escalation:**
- If > 5 activations per shift from same cause → investigate fixture maintenance schedule
- If activation due to bad incoming parts → escalate to supplier (Template 3)

---

## Selection Guide: Which Reaction Plan?

| **Control Method** | **Trigger** | **Recommended Reaction Template** |
|---|---|---|
| **SPC Xbar-R** | Point beyond 3σ | Template 1 (Stop & investigate) |
| **SPC Xbar-R** | Trend (6+ points up) | Template 4 (Adjust & verify) |
| **SPC p-chart** | p > UCL | Template 1 or 2 (depend on magnitude) |
| **100% Inspection** | Single defect | Template 2 (Containment sort) |
| **100% Inspection** | > 5% defective | Template 1 (Stop & investigate) |
| **Poka-Yoke Prevention** | Device jam/activation | Template 5 (Device assessment) |
| **Poka-Yoke Warning** | Light/alarm activated | Template 4 (Investigate, adjust if needed) |
| **Audit-Based** | Finding out-of-spec | Template 1 or 2 (depend on risk) |
| **Purchased Item** | Supplier lot rejected | Template 3 (Supplier escalation) |

---

## Cross-Functional Responsibility

| **Role** | **0–30 min** | **30 min – 4 hours** | **4–24 hours** |
|---|---|---|---|
| **Operator** | Stop, call supervisor, secure part | Assist engineer, retraining if needed | Resume (after approval) |
| **Shift Supervisor** | Acknowledge, quarantine, notify QE | Observe resolution, authorize sorting | Approve restart |
| **Quality Engineer** | Investigate, root cause hypothesis | Implement corrective action, pilot | Verification, close-out |
| **Process Engineer** | Assess machine, advise adjustment | Execute tuning or repairs | Witness pilot, document |
| **Plant Quality Manager** | Informed (if escalated) | MRB decision (if > 10% defective) | CAPA assignment, follow-up |
| **Supplier Quality** | — | — | Root cause analysis (Template 3) |

---

## Key Principles

1. **Speed:** First 30 minutes are critical. Containment must happen immediately to limit nonconforming parts shipped.
2. **Documentation:** Every event logged. Trending reveals systematic issues (e.g., Friday afternoon failures → fatigue/staffing issue).
3. **Ownership:** Each reaction step has a clear owner. No ambiguity ("someone should sort this lot").
4. **Escalation:** Clear authority level for each decision (operator → supervisor → quality → MRB).
5. **Learning:** Post-event review: Did root cause hypothesis prove correct? Is there a systemic fix (not just fix the symptom)?

---

## Metric: Reaction Effectiveness

Track per characteristic:
- **Detection time** — when signal occurred vs. when detected (goal: < 15 min for SPC, < 1 hour for audit)
- **Response time** — from detection to corrective action start (goal: < 2 hours)
- **Verification time** — from CA start to restart approval (goal: < 8 hours for critical)
- **Containment** — % of nonconforming parts caught before customer (goal: 100%)
- **Recurrence** — same root cause within 6 months (goal: zero)

These metrics drive process maturity and customer confidence.
