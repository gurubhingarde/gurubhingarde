# Risk Determination Matrix — Impact × Feasibility Lookup

## Risk Value Scoring

Risk Value ranges from 1 (minimal) to 5 (critical):

| Risk | Level | Color | Treatment Priority |
|------|-------|-------|-------------------|
| **5** | Critical | Red | Avoid or Reduce (mandatory) |
| **4** | High | Orange | Reduce (strong) or Avoid |
| **3** | Medium | Yellow | Reduce or Share (evaluate both) |
| **2** | Low | Light Green | Share or Retain (acceptable with conditions) |
| **1** | Minimal | Dark Green | Retain (document acceptance) |

---

## Risk Matrix: Impact × Feasibility

**Lookup Table**: Find the intersection of Impact (rows) and Feasibility (columns).

```
              Feasibility
           Very Low   Low   Medium   High
           --------  -----  ------  ------
Negligible    1      2       2       3
Moderate      2      3       3       5
Major         3      4       5       5
Severe        4      5       5       5
```

### Reading the Matrix

**Example 1**: Severe Impact + Very Low Feasibility
- Location: Row "Severe", Column "Very Low"
- **Risk Value = 4** (High)
- Treatment: Reduce feasibility or impact; retain only after residual-risk review

**Example 2**: Major Impact + High Feasibility  
- Location: Row "Major", Column "High"
- **Risk Value = 5** (Critical)
- Treatment: Avoid or reduce mandatory

**Example 3**: Moderate Impact + Low Feasibility
- Location: Row "Moderate", Column "Low"
- **Risk Value = 3** (Medium)
- Treatment: Evaluate reduce or share; may retain with CAL justification

---

## Risk Value Interpretation

### Risk 5 — Critical

**When**: Major or Severe impact + Any feasibility, OR Moderate impact + Medium/High feasibility

**Mandatory Actions**:
- Avoid (eliminate threat via design change) OR
- Reduce (implement multiple mitigations to lower feasibility and/or impact)
- Document threat and residual risk; obtain approvals
- Implement continuous monitoring/detection

**Examples**:
- Tampered firmware (Severe Impact + Medium Feasibility)
- CAN message injection enabling unintended acceleration (Major Impact + High Feasibility)
- Debug interface bypass enabling code injection (Major Impact + Medium Feasibility)

**Cybersecurity Goal Derivation**: Required for all Risk 5 scenarios
- Format: "Prevent <threat description>"
- Assign CAL 3 or 4 (depending on target assurance level)

---

### Risk 4 — High

**When**: Severe impact + Low/Medium/High feasibility, OR Major impact + Very Low/Low feasibility

**Mandatory Actions**:
- Strong recommendation to Reduce (implement mitigations)
- Avoid if cost-effective
- Retain only with executive approval and continuous monitoring

**Examples**:
- Firmware tampering (Severe Impact + Low Feasibility) → reduce via integrity checks
- Denial of service on non-critical function (Major Impact + Very Low Feasibility) → document and accept if CAL 1

**Cybersecurity Goal Derivation**: Recommended for Risk 4 with moderate/high CAL targets
- Assign CAL 2–3

---

### Risk 3 — Medium

**When**: Major impact + Very Low feasibility, OR Moderate impact + Low/Medium feasibility, OR any Negligible + High feasibility

**Acceptable Actions**:
- Reduce (most cost-effective path)
- Share (warning label, user training, contractual transfer)
- Retain (document residual risk; accept if CAL 1/2)

**Examples**:
- Information disclosure of non-critical calibration (Moderate Impact + Low Feasibility) → Share via restricted distribution
- Temporary DTC logging error (Moderate Impact + High Feasibility) → Reduce via input validation
- Repudiation of diagnostic actions (Moderate Impact + Medium Feasibility) → Share via audit logging

**Cybersecurity Goal Derivation**: Optional, depending on item criticality and CAL target
- Assign CAL 1–2 if implemented

---

### Risk 2 — Low

**When**: Moderate impact + Very Low feasibility, OR Negligible impact + Low/Medium feasibility

**Acceptable Actions**:
- Share (disseminate warning, user education, contract terms)
- Retain (document; accept in normal operations)
- Reduce only if cost-effective

**Examples**:
- Information disclosure of public firmware version (Negligible Impact + High Feasibility) → Share via FAQ
- Telematics data delay due to network congestion (Moderate Impact + Very Low Feasibility) → Retain; document SLA

**Cybersecurity Goal Derivation**: Not typically required
- Not critical unless part of larger threat chain

---

### Risk 1 — Minimal

**When**: Negligible impact + Very Low/Low feasibility

**Action**: Retain
- Accept risk without special mitigation
- Document in TARA worksheet for completeness
- Monitor for threat evolution

**Examples**:
- Unauthorized read of VIN (already on door) → Negligible Impact + Very Low (reverse-engineering) = Risk 1
- Repudiation of maintenance schedule (Negligible Impact) → Risk 1

---

## Risk Treatment Decision Framework

For each threat scenario (once Risk Value computed):

### Step 1: Determine Target CAL (Cybersecurity Assurance Level)

| CAL | Scope | Risk Tolerance |
|-----|-------|---|
| **4** | Prevent nation-state threats | Risk ≤ 2; Avoid/Reduce mandatory |
| **3** | Prevent organized crime + insider | Risk ≤ 3; Reduce strong |
| **2** | Prevent skilled attacker | Risk ≤ 4; Reduce/Share balanced |
| **1** | Prevent casual attacker | Risk ≤ 5; Share/Retain acceptable |

### Step 2: Select Treatment

| Risk | CAL 4 | CAL 3 | CAL 2 | CAL 1 |
|-----|--------|--------|--------|--------|
| **5** | Avoid | Avoid/Reduce | Reduce | Reduce/Share |
| **4** | Reduce | Reduce | Reduce/Share | Share/Retain |
| **3** | Reduce/Share | Reduce/Share | Share/Retain | Retain |
| **2** | Reduce/Share | Share/Retain | Retain | Retain |
| **1** | Retain | Retain | Retain | Retain |

### Step 3: Implement & Validate

For **Avoid**:
- Design change eliminating threat
- Example: Disable debug interface on production ECU

For **Reduce**:
- Lower feasibility (add detection, access control, encryption)
- Lower impact (isolate function, add redundancy)
- Example: Add HMAC authentication to firmware; encrypt calibration data

For **Share**:
- Transfer risk via contract, warning, insurance
- Mitigation responsibility moved to user/operator
- Example: Publish security advisory; document safe operation

For **Retain**:
- Accept residual risk
- Requires executive sign-off
- Implement continuous monitoring
- Example: Accept debug port vulnerability if debug port physically access-locked

### Step 4: Document Residual Risk

**Question**: Is residual risk acceptable given CAL target?

- **Yes**: Approve treatment; document in Risk Treatment tab
- **No**: Iterate to stronger mitigation; re-rate feasibility/impact; confirm Risk Value acceptable

---

## Example Threat Scenarios

### Scenario A: Firmware Tampering via Serial Debug Port

**Threat**: Attacker writes malicious code to FLASH via JTAG/SWD debug port.

**Impact Rating**:
- Safety: Severe (could disable all safety functions)
- Financial: Severe (recall of all units)
- Operational: Severe (production halt)
- Privacy: Negligible
- **Overall: Severe**

**Feasibility Rating**:
- Elapsed Time: Weeks (medium expertise for custom exploit)
- Expertise: Proficient
- Knowledge: Restricted (some OEM docs leaked, but debug protocol proprietary)
- Opportunity: Low (requires physical access + service connection)
- Equipment: Specialized ($2K debugger + software)
- **Overall: Low** (worst factor is opportunity)

**Risk Value**: Severe + Low → **Risk 4** (High)

**Treatment (CAL 3 target)**:
- **Decision: Reduce**
- **Mitigations**:
  1. Disable JTAG/SWD on production devices (secure boot fuse)
  2. Add cryptographic authentication to flash writes
  3. Implement code signing and verification
- **Residual Risk**: Risk 2 (Severe impact reduced; feasibility still Low due to reverse-engineering required)
- **Acceptable**: Yes (Risk 2 at CAL 3 is within tolerance)

---

### Scenario B: CAN Message Spoofing (Fake Speed Signal)

**Threat**: Attacker injects forged CAN message claiming to be wheel-speed sensor, causing ESC/ABS to malfunction.

**Impact Rating**:
- Safety: Major (loss of traction control at highway speed; injury probable but not certain)
- Financial: Major ($250K–$2M depending on recall scope)
- Operational: Major (recall 10K+ units)
- Privacy: Negligible
- **Overall: Major**

**Feasibility Rating**:
- Elapsed Time: Days (CAN protocol well-documented; exploit PoCs public)
- Expertise: Layman (script kiddie with CAN tools)
- Knowledge: Public (CAN protocol in ISO standards; vehicle eCU IDs reverse-engineered)
- Opportunity: High (CAN bus always accessible with physical access to OBD-II port)
- Equipment: Standard ($50 ELM327 adapter)
- **Overall: High** (all factors High/Medium)

**Risk Value**: Major + High → **Risk 5** (Critical)

**Treatment (CAL 3 target)**:
- **Decision: Avoid or Reduce** (mandatory)
- **Options**:
  1. **Avoid**: Eliminate CAN messages; use more secure transport (Ethernet with security)
  2. **Reduce** (preferred, lower cost):
     - Add HMAC/digital signature to critical CAN messages
     - Implement message authentication at application layer
     - Add plausibility checks (reject physically impossible speed changes)
     - Implement timeout + fallback to safe state
- **Residual Risk**: Risk 2 (after HMAC + authentication, feasibility drops to Medium; residual risk acceptable)
- **Cybersecurity Goal**: CSG-001: "Prevent unauthorized speed sensor signal spoofing via CAN" (CAL 3)

---

### Scenario C: Information Disclosure — Firmware Reverse-Engineering

**Threat**: Attacker extracts firmware image from ECU, reverse-engineers proprietary algorithm.

**Impact Rating**:
- Safety: Negligible (information disclosure doesn't directly harm safety)
- Financial: Major (IP theft; competitors access calibration)
- Operational: Moderate (intellectual property now public; aftermarket tuning enabled)
- Privacy: Negligible
- **Overall: Major** (financial impact governs)

**Feasibility Rating**:
- Elapsed Time: Months (sophisticated reverse-engineering)
- Expertise: Expert (PhD-level)
- Knowledge: Critical (firmware fully closed, encrypted)
- Opportunity: Low (requires extended access to physical device)
- Equipment: Multiple bespoke ($100K+ lab)
- **Overall: Very Low** (worst factor is elapsed time + knowledge)

**Risk Value**: Major + Very Low → **Risk 3** (Medium)

**Treatment (CAL 2 target)**:
- **Decision: Share or Reduce**
- **Options**:
  1. **Share**: Accept disclosure risk; implement legal/contractual protections (DMCA, patent, trade secret)
  2. **Reduce**:
     - Encrypt firmware at rest
     - Implement secure boot + code obfuscation
     - Add anti-tampering (watchdog on memory access)
- **Residual Risk**: Risk 2–3 (depending on mitigation depth)
- **Decision**: Share (most cost-effective; IP protected by law)
- **Cybersecurity Goal**: Not required (Risk 3 at CAL 2 acceptable without CSG)

---

## Color-Coded Risk Visualization

Workbook uses color-coding in Risk Determination tab:

- **Risk 5**: Critical Red (#C00000)
- **Risk 4**: Orange (#F4B084)
- **Risk 3**: Yellow (#FFE699)
- **Risk 2**: Light Green (#C6EFCE)
- **Risk 1**: Dark Green (#92D050)

Use conditional formatting or manual color assignment to highlight risk zones for quick visual scanning.
