# Impact Rating Table — Severe / Major / Moderate / Negligible

## Overview

For each threat scenario, rate the worst-case impact across four dimensions:
- **Safety (S)**: Injury or fatality risk (mapped to ISO 26262 AIS severity)
- **Financial (F)**: Direct economic loss (repair costs, recalls, litigation)
- **Operational (Op)**: Service disruption, downtime, production loss
- **Privacy (Pr)**: Personal data exposure, regulatory fines (GDPR, state privacy laws)

**The overall impact for a threat scenario = maximum across all four dimensions.**

---

## Safety (S) — ISO 26262 Injury Severity Mapping

### Severe (S) — AIS 3–6 with ≥10% probability

**Definition**: Life-threatening or fatal injury highly probable.

**Indicators**:
- AIS 3–6 injury likely from hazard (serious injury/death)
- Loss of vehicle control at highway speed
- Unintended brake application at high speed
- Failure of steering or propulsion during critical maneuver
- Uncontrolled acceleration in dense traffic

**Examples**:
- Malicious steering input override at highway speed
- Firmware corruption disabling all brake function
- CAN injection causing opposite steering torque
- Denial of service on safety-critical sensor (ABS, ESC)

---

### Major (M) — AIS 3–6 <10% OR AIS 1–2 >10%

**Definition**: Severe to moderate injury credible; survival probable.

**Indicators**:
- Moderate injury (AIS 1–2) very likely OR
- Severe injury (AIS 3–6) with <10% probability
- Loss of control with some mitigation possible (partial brake, partial steering)
- Injury during parking maneuvers or low-speed collisions unlikely
- Injury during mid-speed driving credible

**Examples**:
- Unauthorized diagnostic data modification detected but not corrected
- Message replay attack on traction control (limited scenario)
- Unauthorized firmware update with performance degradation
- Calibration tampering reducing braking by 30%

---

### Moderate (Mo) — AIS 1–2 <10% OR AIS 0 with significant property damage

**Definition**: Light to moderate injury possible; minor property damage likely.

**Indicators**:
- Light injury (AIS 1–2) is possible but unlikely
- No life-threatening scenario
- Financial or operational harm significant
- Privacy breach without safety consequence

**Examples**:
- Unauthorized calibration change reducing fuel efficiency
- Diagnostic logs accessible but not safety-critical
- Information disclosure of non-critical configuration
- Temporary denial of service on convenience feature

---

### Negligible (N) — No safety impact, minimal operational/financial impact

**Definition**: No injury risk; loss minor or avoidable.

**Indicators**:
- No credible injury pathway
- Financial loss < $100, or easily avoidable
- Service disruption limited to non-critical feature
- No privacy exposure

**Examples**:
- Unauthorized read of public calibration constants
- Temporary UI glitch from malformed message
- Information disclosure of already-public data
- Single DTC set (driver alerted, function recovers)

---

## Financial (F) — Economic Loss

### Severe (S) — >$1M direct loss

**Definition**: Massive financial impact.

**Indicators**:
- Recall campaign required
- Legal liability or settlement
- Major component replacement
- Production shutdown
- Class-action risk

**Examples**:
- Malicious firmware bricking fleet of vehicles
- Unauthorized access enabling vehicle theft ring
- Tampering undetected, causing widespread failures
- Intellectual property theft (calibration, algorithms)

---

### Major (M) — $100K–$1M direct loss

**Definition**: Significant financial impact.

**Indicators**:
- Service campaign or warranty claims surge
- Regulatory fine or investigation
- Incident disclosure costs
- Remediation labor extensive

**Examples**:
- Denial of service requiring ECU replacement in 10K units
- Calibration corruption requiring field reprogramming
- Unauthorized firmware distribution affecting supply chain
- Data breach triggering regulatory response

---

### Moderate (Mo) — $10K–$100K direct loss

**Definition**: Manageable financial impact.

**Indicators**:
- Repair or replacement costs for subset of vehicles
- Incident response and investigation
- Software patch distribution

**Examples**:
- Information disclosure requiring customer notification
- Temporary service disruption costing logistics
- Unauthorized modification of non-critical parameter
- Single-ECU replacement cost × affected units

---

### Negligible (N) — <$10K direct loss

**Definition**: Minimal financial impact.

**Indicators**:
- Cost absorbed in normal operations
- No recall or campaign
- Minor remediation

**Examples**:
- Read-only access to public data
- Temporary denial of service on non-critical feature
- Single technician labor to investigate

---

## Operational (Op) — Service Disruption & Recall

### Severe (S) — Production halt or fleet-wide recall

**Definition**: Massive operational disruption.

**Indicators**:
- Manufacturing shutdown
- Fleet recall (>50K vehicles)
- Supply chain disruption
- Long-term unavailability

**Examples**:
- Firmware corruption affecting all units in production
- Malicious code preventing vehicle startup
- Denial of service on OTA update infrastructure
- Loss of telematics blocking remote diagnosis

---

### Major (M) — Significant recall or service campaign

**Definition**: Large-scale disruption.

**Indicators**:
- Regional recall (10K–50K vehicles)
- Service campaign with > 80% participation
- Dealer backlog or extended lead time
- Seasonal or temporary unavailability

**Examples**:
- Calibration error requiring reflashing
- Denial of service on feature affecting multiple vehicle versions
- Unauthorized modification detectable but not auto-correctable

---

### Moderate (Mo) — Limited service impact, minor campaign

**Definition**: Localized or temporary disruption.

**Indicators**:
- Single dealership or market affected
- Service campaign with <50% participation
- Workaround available
- Short lead time to fix

**Examples**:
- Diagnostic feature temporarily unavailable
- Single variant requires re-programming
- Temporary CAN message corruption (recovers with power cycle)

---

### Negligible (N) — No operational impact

**Definition**: No service disruption.

**Indicators**:
- No customer action required
- No recall or campaign
- Self-healing or user-workaround

**Examples**:
- Information disclosure (read-only)
- Single DTC cleared automatically
- Non-critical feature offline during upgrade

---

## Privacy (Pr) — Personal Data & Regulatory

### Severe (S) — Widespread personal data exposure or major regulatory violation

**Definition**: Massive privacy breach.

**Indicators**:
- PII exposure to unauthorized parties (SSN, date of birth, medical info)
- Location data exposed (thousands of trips)
- Regulatory fine >$1M (GDPR, CCPA, sector-specific)
- Media coverage and reputational damage

**Examples**:
- Telematics server breach exposing GPS history
- Calibration keys leaked enabling aftermarket tuning
- Diagnostic credentials exposed enabling unauthorized servicing
- Vehicle owner database accessible without authentication

---

### Major (M) — Significant personal data exposure or regulatory investigation

**Definition**: Serious privacy impact.

**Indicators**:
- PII of >1000 individuals exposed (name, email, address)
- Location data of subset exposed
- Regulatory investigation or preliminary fine
- Notification to affected parties required

**Examples**:
- Cloud service misconfiguration exposing user profiles
- Diagnostic upload containing location hints
- Diagnostic credentials shared across users
- Unauthorized read of user configuration preferences

---

### Moderate (Mo) — Limited personal data or internal regulatory response

**Definition**: Minor privacy concern.

**Indicators**:
- PII of <1000 individuals exposed
- Non-sensitive location data (e.g., home address already public)
- Internal audit or policy review triggered
- No external disclosure required

**Examples**:
- Unauthorized read of vehicle VIN (public on door)
- Diagnostic data containing time-of-use (aggregated)
- User preferences readable but not sold
- Service history accessible to unauthorized technician

---

### Negligible (N) — No personal data exposure

**Definition**: No privacy impact.

**Indicators**:
- No PII or location data
- Public data only
- No regulatory concern

**Examples**:
- Read-only access to publicly available vehicle data
- Diagnostic system version disclosure
- Non-identifying usage statistics

---

## Summary Table

| Dimension | Severe | Major | Moderate | Negligible |
|-----------|--------|-------|----------|-----------|
| **Safety** | AIS 3–6 ≥10% | AIS 3–6 <10% OR AIS 1–2 >10% | AIS 1–2 <10% OR S0 w/ property | No injury risk |
| **Financial** | >$1M loss | $100K–$1M | $10K–$100K | <$10K |
| **Operational** | Fleet recall ≥50K | Recall 10K–50K | Limited service impact | No disruption |
| **Privacy** | PII exposed widely OR $1M+ fine | PII of 1K+ exposed OR investigation | PII of <1K OR internal review | No PII exposure |

**Overall Impact Rating = Maximum across S, F, Op, Pr**
