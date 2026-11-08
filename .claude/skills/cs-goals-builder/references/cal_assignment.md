# CAL (Cybersecurity Assurance Level) Assignment Criteria

Per ISO/SAE 21434, cybersecurity goals must be assigned a Cybersecurity Assurance Level (CAL) reflecting the stringency of controls required to meet the goal. CAL ranges from 1 (lightest assurance) to 4 (highest assurance).

## CAL Levels and Definitions

### CAL 4 — Highest Assurance Required

**Application**: Critical threat scenarios with severe safety and/or business impact.

**Characteristics**:
- Risk Value 5 (Critical) with severe safety consequences (e.g., loss of life, uncontrolled vehicle motion)
- Threat exploitability is high and impact is widespread
- Requires rigorous control design, implementation, and verification

**Examples**:
- Prevent unauthorized firmware modification (affects all safety-critical functions)
- Prevent secure boot bypass (allows arbitrary code execution)
- Prevent complete loss of steering/braking control via CAN message spoofing

**Control Activities**:
- Formal threat modeling and control design
- Code reviews and static analysis
- Penetration testing and adversarial assessment
- Cryptographic authentication (e.g., HMAC, digital signatures)
- Secure boot with immutable trust anchor
- Runtime integrity monitoring
- Incident response and forensics capability

---

### CAL 3 — High Assurance

**Application**: High-risk threat scenarios with significant safety or business impact.

**Characteristics**:
- Risk Value 4 with significant impact (e.g., partial loss of function, safety degradation)
- Moderate exploitability; impact is localized to specific assets or functions
- Requires systematic control design and verification

**Examples**:
- Prevent CAN message spoofing affecting brake commands
- Prevent calibration data tampering (affects safety thresholds)
- Prevent unauthorized OBD-II diagnostic session initiation

**Control Activities**:
- Documented threat analysis and control mapping
- Code review (peer review minimum)
- Automated testing (unit + integration)
- Message authentication (checksums, CRC)
- Session authentication (PINs, tokens)
- Logging and monitoring

---

### CAL 2 — Moderate Assurance

**Application**: Medium-risk threat scenarios with moderate safety or business impact.

**Characteristics**:
- Risk Value 3 with moderate impact (e.g., reduced performance, temporary unavailability)
- Lower exploitability; impact is limited to specific subsystems
- Requires basic control design and testing

**Examples**:
- Prevent debug interface unauthorized access (if debug mode has limited privilege)
- Prevent diagnostic session unauthorized access (diagnostic mode does not modify critical data)
- Prevent unauthorized sensor reading modification (non-critical telemetry)

**Control Activities**:
- Basic design documentation
- Testing against identified threats
- Simple access controls (role-based, default deny)
- Input validation
- Audit logging

---

### CAL 1 — Lower Assurance

**Application**: Low-risk threat scenarios with minimal safety or business impact.

**Characteristics**:
- Risk Value 1-2 with low impact (e.g., informational only, cosmetic)
- Exploitability is difficult or requires specific conditions
- Requires minimal formalized controls

**Examples**:
- Prevent unauthorized reading of non-critical parameters (e.g., odometer tampering if not used for warranty)
- Prevent unauthorized access to informational displays (non-safety text)

**Control Activities**:
- Basic input validation
- Standard software practices (e.g., buffer bounds checking)
- Configuration management

---

## CAL Assignment Heuristic

The cs-goals-builder applies the following auto-suggestion logic:

```
Risk Value 5 + Severe Safety Impact  → CAL 4
Risk Value 4                          → CAL 3
Risk Value 3                          → CAL 2
Risk Value 1-2                        → CAL 1
```

**Override Criteria** — Adjust CAL upward if:
- Exploit is public or well-known
- Multiple threat vectors converge on the same CSG
- CSG is a prerequisite for another high-CAL CSG

**Override Criteria** — Adjust CAL downward if:
- Exploitability is extremely high difficulty (e.g., requires physical access + advanced equipment)
- Safety impact is mitigated by other functions
- Market/competition does not demand higher assurance

## CAL Across Lifecycle

- **CSG Phase** — CSGs are assigned CAL; this is stable
- **CSC Phase** — CSCs derived from a CAL-X CSG inherit at least CAL-X
- **Architecture Phase** — Architectural components assigned CAL based on aggregated CSC CALs
- **Implementation Phase** — Implementation controls must achieve the allocated CAL
- **Verification Phase** — Verification activities increase in rigor with CAL

## Justification Template

Document each CSG's CAL assignment using this template:

> **[CSG_ID]: [CAL Assignment]**
>
> **Risk Context**: Risk Value = [X], Impact Rating = [Critical/High/Medium/Low]
>
> **Safety Impact**: [Description of consequence if threat is exploited]
>
> **Feasibility**: [Assessment of control implementation difficulty]
>
> **Justification**: [Specific reasoning for this CAL selection]
>
> **Evidence**: [References to TARA, design rationale, test plans, etc.]

Example:

> **CSG-001: CAL 4**
>
> **Risk Context**: Risk Value = 5 (Critical), Impact = Loss of steering control
>
> **Safety Impact**: Uncontrolled vehicle motion, potential loss of life
>
> **Feasibility**: Medium (requires secure boot, cryptographic auth, real-time monitoring)
>
> **Justification**: Risk Value 5 with catastrophic safety consequence mandates highest assurance.
>
> **Evidence**: TARA#THREAT-045, ISO/SAE 21434 Annex C (CAL assignment guidance)
