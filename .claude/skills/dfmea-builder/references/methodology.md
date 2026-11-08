# AIAG-VDA FMEA Handbook 2019 — Design FMEA (DFMEA) Methodology

The AIAG-VDA FMEA Handbook (2019) is the harmonized replacement for AIAG-4, developed jointly by the Automotive Industry Action Group (AIAG) and the Verband der Automobilindustrie (VDA). It unifies design and process FMEA under a common 7-step framework and introduces the **Action Priority (AP)** method as a more transparent alternative to Risk Priority Number (RPN).

## 7-Step DFMEA Process

### Step 1: Planning & Preparation
Define the scope of the DFMEA (e.g., a subsystem, component, or function).
- Identify team members (design, manufacturing, supplier, customer representatives if needed)
- Set analysis boundaries and timeline
- Review design requirements, specifications, and relevant standards
- Output: Team charter, scope document, kickoff meeting

### Step 2: Structure Analysis
Create a hierarchical decomposition of the design from System → Subsystem → Component.
- System level: Overall product (e.g., "ESC ECU")
- Subsystem level: Major functional modules (e.g., "Sensing Module", "Computing Module", "Actuation Module")
- Component level: Individual parts and assemblies (e.g., "Wheel Speed Sensor", "Main MCU", "Brake Modulator Driver")
- Output: **Tab 03_Structure_Analysis** — hierarchical list with IDs, names, parent relationships

### Step 3: Function Analysis
Define the functional requirements and intent of each subsystem/component.
- Start with design intent: What is this subsystem supposed to do?
- Link to customer requirements and safety goals if applicable
- Create a function tree showing functional hierarchy and dependencies
- Example: "Monitor wheel speed" → "Acquire sensor signal" → "Convert analog to digital" → "Transmit CAN message"
- Output: **Tab 04_Function_Analysis** — function ID, parent system, function statement, requirement reference

### Step 4: Failure Analysis
Enumerate all potential failure modes for each function/component.
- **Failure Mode (FM)**: The way a function can fail (e.g., "Wheel speed signal loss", "Intermittent signal", "Inverted polarity")
- **Failure Effect (FE) on Next Level**: What happens to the subsystem or parent component if this failure occurs? (e.g., "Loss of speed feedback to main MCU")
- **Failure Effect on End-User / Vehicle**: Ultimate impact on customer or vehicle operation (e.g., "Potential loss of ESC function; safety critical")
- **Failure Cause (FC)**: The physical or design-related reason the failure mode can occur (e.g., "Connector corrosion", "PCB trace break", "Software timeout not implemented")
- Use library checklists, design review notes, supplier feedback, and prior FMEA history
- Output: **Tab 05_DFMEA_Worksheet** (columns 1–8): Item ID, Focus Element, Function, FM, Effect on Next Level, Effect on User, Failure Cause

### Step 5: Risk Analysis
Assess the severity of effects, likelihood of causes, and effectiveness of detection controls using three scales (each 1–10):

**Severity (S)** — How serious is the customer-facing effect?
- 10: Hazardous uncontrolled; potential loss of life
- 9: Serious injury or loss of vehicle control
- 8: Moderate degradation; occupant safety impact
- 7: Moderate system malfunction; noticeable to customer
- 6–5: Minor malfunctions; varying levels of inconvenience
- 4–3: Very minor effects; barely noticeable
- 1–2: Negligible or no effect

**Occurrence (O)** — How likely is the failure cause to occur?
- 10: Very high; almost certain during design life
- 9: High; very likely
- 6–8: Moderate range
- 3–5: Low to very low
- 1–2: Remote to almost impossible

**Detection (D)** — How likely is the failure to be detected *before reaching the customer*?
- 1–2: Almost certain detection (robust design test, 100% manufacturing inspection)
- 3–4: High chance (design review covers this, strong statistical evidence)
- 5–6: Moderate chance (dedicated test exists, but not foolproof)
- 7–8: Low chance (weak or indirect test; relies on second-order symptoms)
- 9–10: Very low or impossible detection (no test, hidden failure, latent)

**Action Priority (AP)** — Determined by lookup table (AIAG-VDA Table P.1), not RPN multiplication.

Simplified AP logic:
- **AP = H (High)** if (S≥9) OR (S≥7 AND O≥4) OR (S≥4 AND O≥7 AND D≥7)
- **AP = M (Medium)** if (S≥4 AND O≥4) OR (S≥7) OR (O≥7 AND D≥7)
- **AP = L (Low)** otherwise

This method prioritizes severity and recognizes that high-severity items always need attention, while low-severity items do not benefit from expensive controls.

Output: **Tab 05_DFMEA_Worksheet** (columns 7–14): S, O, D, Prevention Control, Detection Control, AP

### Step 6: Optimization
Plan and implement actions to reduce risk.
- **Prevention Control (PC)**: Design or manufacturing change to reduce the occurrence of the failure cause
  - Examples: Improved seal design, redundant component, early failure detection in validation test
- **Detection Control (DC)**: Test, inspection, or on-board diagnostic to catch the failure before delivery
  - Examples: CAN message timeout check, visual inspection, design analysis
- After action is implemented, re-estimate **Occurrence After PC** and **Detection After DC**
- Recalculate AP with new O and D values; if still high, may need additional controls or design change
- **Residual Risk**: Risk remaining after all actions are taken; must be accepted by team or escalated to engineering

Output: **Tab 05_DFMEA_Worksheet** (columns 15–21): Recommended Action, Owner, Target Date, Action Taken, S/O/D After Action, AP After Action, Status

Output: **Tab 08_Action_Plan_Tracker** — summarized action list with owner, due date, verification; typically filters for AP=H and AP=M only

### Step 7: Results & Documentation
Finalize and communicate the analysis.
- Sign off DFMEA: Technical lead, quality, safety, engineering manager
- Identify Special Characteristics (SCs) — design parameters or tolerances critical to prevent/detect failure modes; these feed into Design Verification and Manufacturing Control Plans
- Cross-reference prior DFMEAs and family FMEA for reuse of proven solutions
- Archive for audit trail (e.g., OEM request for evidence)
- Use lessons learned to improve future design iterations

Output: **Tab 06_Special_Characteristics** — SC ID, classification (Critical/Significant), linked failure mode, control strategy

Output: **Tab 10_Lessons_Learned_Crossref** — links to prior designs, family FMEA, generic FMEA

Output: **Tab 11_References** — AIAG-VDA 2019, ISO 26262 (if safety-relevant), OEM-specific FMEA requirements

## Function Tree (Step 3)

The function tree is the backbone of a rigorous DFMEA. Example for an ESC ECU:

```
ESC ECU (System-level function: Prevent unintended yaw rotation)
├── Monitor wheel speeds
│   ├── Acquire wheel speed sensor signal (LF, RF, LR, RR)
│   │   ├── Interface with sensor (0–5V analog)
│   │   ├── Filter noise and debounce
│   │   └── Validate signal range and plausibility
│   ├── Convert analog signals to digital (ADC)
│   └── Transmit to main MCU via SPI/CAN
├── Compute yaw rate and detect slip
│   ├── Calculate yaw rate from wheel speeds
│   ├── Compare to IMU yaw rate (detect sensor disagreement)
│   └── Determine if slip is occurring
├── Control brake modulator
│   ├── Send command to brake apply solenoid (LF, RF, LR, RR independently)
│   ├── Monitor pressure feedback
│   └── Validate solenoid actuation
└── Communicate with vehicle network (CAN)
    ├── Receive commands from main controller
    ├── Send status/diagnostics
    └── Detect and report link loss
```

Each node becomes a focus element for failure analysis. Example failure modes:

| Focus Element | Function | Failure Mode | Effect on Next Level | Effect on User |
|---|---|---|---|---|
| Wheel Speed Sensor (LF) | Acquire wheel speed | Signal loss | Main MCU loses LF feedback | Loss of ESC control; vehicle spins out |
| ADC | Convert analog to digital | Quantization error, stuck output | Wrong speed value fed to algorithm | Erratic brake apply; safety risk |
| Main MCU | Compute yaw rate | Lockstep fault (dual-core mismatch) undetected | Wrong yaw command sent to driver | Unintended brake apply; safety critical |
| Solenoid Driver | Apply brake | Stuck-on (always apply) | Constant brake pressure applied | Vehicle slows/stops; loss of control |

## Failure Chain

For each failure mode, trace the path from cause to user effect:

**Cause → Failure Mode → Effect (Local) → Effect (Next Level) → Effect (Vehicle)**

Example: "Solder joint crack in ADC → ADC stuck at max output → Main MCU reads incorrect speed (100 km/h when actual is 50) → Algorithm over-estimates slip → Excessive brake apply → Vehicle stops suddenly; occupant injury risk"

This chain justifies the Severity rating (S=9 in this case) and informs choice of detection controls (design review + functional test of ADC output over temperature range).

## AIAG-VDA vs. Classical RPN

| Aspect | RPN (Classic) | AIAG-VDA AP |
|---|---|---|
| **Calculation** | S × O × D (ranges 1–1000) | Lookup table (H/M/L) |
| **Priority Justification** | Higher RPN = higher priority | Severity dominates; captures design intent |
| **Sensitivity** | RPN can hide severity. E.g., S=10, O=1, D=1 → RPN=10 (looks low-risk) | S=10, O=1, D=1 → AP=H (correctly identifies high severity) |
| **Action Threshold** | Often arbitrary cutoff (e.g., RPN>100) | Clear categories: address all H items; assess M/L for cost/benefit |
| **Transparency** | Numbers feel objective but mask judgment | Logic-based rules make assumptions visible and auditable |

**Recommendation**: Use AIAG-VDA AP method. It is auditor-friendly, aligns with OEM expectations (most now require it), and better reflects design risk.
