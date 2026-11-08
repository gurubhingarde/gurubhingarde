# Cybersecurity Assurance Level (CAL) 1–4

## Overview

CAL (Cybersecurity Assurance Level) defines the cybersecurity rigor required for a component or system. It balances threat model with cost and complexity.

Higher CAL = stronger attacker model, more rigorous defenses, higher engineering cost.

---

## CAL Levels

### CAL 1 — Defend Against Casual Hackers

**Target Threat Agent**: Casual hacker, script kiddie, well-known vulnerabilities

**Attacker Assumptions**:
- Layman-to-proficient skill level
- Public tools and documentation
- Opportunistic, not persistent
- <7 days elapsed time for attack
- Standard equipment

**Security Requirements**:
- Basic access control (password, PIN)
- Input validation and error handling
- No default credentials
- Firmware integrity verification (CRC)
- Logging of security events (basic)

**Not Required**:
- Cryptographic authentication (though recommended)
- Secure key storage
- Formal security analysis
- Extensive red-teaming

**Use Cases**:
- Infotainment systems (low safety risk)
- Non-critical diagnostic interfaces
- Convenience features (seat warmers, exterior lighting)
- Vehicle-to-phone connectivity

**Example Mitigations**:
- CAN message range checking
- OBD-II read/write restrictions
- Debug port disabled in production
- Firmware update signature verification (basic PKI)

**Risk Tolerance**:
- Accept Risk ≤ 5 (any feasibility + any impact)
- But Risk 5 still requires treatment (reduce or avoid)

---

### CAL 2 — Defend Against Skilled Attackers

**Target Threat Agent**: Skilled cybersecurity researcher, professional red-teamer, automotive enthusiast with tools

**Attacker Assumptions**:
- High skill level in cryptography, embedded systems, protocol analysis
- Custom tools; modified commercial tools
- Months of sustained effort
- Specialized equipment ($500–$10K)
- Access to leaked documentation or similar vehicles

**Security Requirements**:
- Cryptographic authentication on critical messages (HMAC, digital signatures)
- Encrypted storage and transmission of sensitive data
- Key management (key generation, storage, rotation)
- Access control and privilege separation
- Comprehensive security logging (tamper-evident)
- Security-focused code review (threat modeling, static analysis)
- Intrusion detection / anomaly monitoring
- Security advisories and patch management

**Not Required**:
- Formal verification (though beneficial)
- Hardware security module (unless keys involved)
- Nation-state-grade threat modeling
- Extended red-teaming by adversarial teams

**Use Cases**:
- Modern powertrains (fuel injection, transmission)
- Driver assistance (adaptive cruise, lane-keeping)
- Telematics and remote services
- OTA update infrastructure
- Non-safety-critical autonomous functions

**Example Mitigations**:
- AES-128 encryption for firmware, calibration, secrets
- HMAC-SHA256 on CAN messages (critical signals only)
- Challenge-response authentication for diagnostic access
- RSA-2048 code signing for firmware updates
- Rate limiting on authentication attempts
- Watchdog monitoring software integrity
- Secure boot with attestation

**Risk Tolerance**:
- Accept Risk ≤ 3 (without mitigation for Risk 3; reduce required)
- Risk 4–5 requires strong reduce or avoid
- Risk 2 acceptable with retain decision documented

---

### CAL 3 — Defend Against Organized Crime + Insiders

**Target Threat Agent**: Organized cybercrime, malicious insider, well-funded threat actor, multi-discipline red team

**Attacker Assumptions**:
- Expert-level expertise across multiple domains (crypto, firmware, hardware, supply chain)
- Months to years of planning
- Bespoke tools and specialized equipment ($10K–$100K)
- May have insider knowledge or supply-chain access
- Coordinated, persistent attack capability
- Access to similar systems for analysis

**Security Requirements**:
- All CAL 2 requirements PLUS:
- Hardware-backed cryptography (secure enclave, TPM, HSM)
- Advanced key management (HSM, secure provisioning, key escrow)
- Privilege separation and sandboxing (multiple execution contexts)
- Secure boot with code attestation
- Runtime integrity monitoring (code, data, configuration)
- Encrypted inter-component communication
- Supply-chain security (anti-counterfeiting, tamper detection)
- Formal threat modeling and red-team assessment
- Continuous security monitoring and incident response
- Secure development lifecycle (SDL) with strict code review
- Fuzzing, formal verification on critical paths
- Threat updates and zero-day response plan

**Not Required**:
- Military-grade formal verification (though encouraged for critical functions)
- Nation-state threat modeling
- Quantum-resistant cryptography (unless long-term data confidentiality critical)

**Use Cases**:
- Autonomous vehicles (collision avoidance, steering)
- Immobilizer and vehicle theft-deterrent
- High-value vehicle tracking and recovery
- Telematics with financial transactions (insurance, tolling)
- OTA update system (infrastructure)
- Vehicle access control (keyless entry, remote unlock)

**Example Mitigations**:
- ECC-384 or RSA-3072 for critical signing
- AES-256 for sensitive data at rest and in transit
- Secure enclave (e.g., ARM TrustZone) for key storage and cryptographic operations
- HMAC-SHA256 + timestamp on all CAN messages
- Hardware watchdog with secure reset
- Immobilizer secret in one-time programmable (OTP) memory
- Supply-chain integrity via cryptographic hash chain
- Continuous threat intelligence updates
- Incident response playbook with forensics capability

**Risk Tolerance**:
- Accept Risk ≤ 2 without mitigation
- Risk 3 requires reduce (or strong documentation + executive approval)
- Risk 4–5 requires avoid or extensive reduce with continuous monitoring
- Residual risk for Risk 3+ requires CSG (Cybersecurity Goal) with formal assessment

---

### CAL 4 — Defend Against Nation-State Actors

**Target Threat Agent**: Nation-state, advanced persistent threat (APT), well-funded state-sponsored group

**Attacker Assumptions**:
- Elite cybersecurity and hardware expertise (cryptanalysis, silicon reverse-engineering, exploit development)
- Years of preparation and sustained effort
- Unlimited budget and equipment
- 0-day vulnerabilities available
- Possibly supply-chain intercept capability
- Formal cryptanalysis teams
- Access to all released systems and documentation

**Security Requirements**:
- All CAL 3 requirements PLUS:
- Formal security verification and formal methods (theorem proving on critical paths)
- Post-quantum cryptography (if long-term confidentiality required)
- Secure hardware design (anti-tamper, secure enclave with side-channel resistance)
- Multi-layer defense (defense-in-depth across hardware, firmware, protocol, operations)
- Continuous formal threat modeling updates
- Independent formal security assessment (academic, third-party)
- Supply-chain integrity with end-to-end cryptographic verification
- Runtime anomaly detection with AI/ML (learning normal behavior)
- Secure decommissioning and key destruction protocols
- Coordinated vulnerability disclosure and patch management
- Forensic-capable logging (tamper-evident, distributed ledger)

**Not Required**:
- Quantum-resistant cryptography in deployed systems (unless 30-year confidentiality required)
- Custom silicon (unless hardware attack surface critical)

**Use Cases**:
- Military or critical infrastructure vehicles
- Autonomous vehicles for governments or VIPs
- Nuclear/power-plant control systems using vehicle tech
- High-value diplomatic/state vehicles
- Research into next-generation security (forward-looking only)

**Example Mitigations**:
- All ECC or RSA at maximum practical key length
- Hardware-based side-channel attack resistance (power, timing, EM)
- Secure enclave with formal side-channel analysis
- Multi-factor authentication (cryptographic + biometric)
- Distributed ledger logging (immutable audit trail)
- Formal proof of protocol correctness (CertiCrypt, Coq)
- Threat intelligence integration (real-time vulnerability feeds)
- Yearly independent red-team assessments
- Post-incident forensics and disclosure (transparent, academic publication)

**Risk Tolerance**:
- Accept Risk ≤ 1 without mitigation
- Risk 2+ requires formal risk assessment and mitigation plan
- Risk 3–5 requires avoid + formal approval + continuous monitoring
- All cybersecurity goals must have formal security proof

---

## CAL Selection Framework

Choose CAL based on:

1. **Item Criticality** (safety, financial, operational impact)
2. **Threat Model** (assumed attacker capability)
3. **Asset Value** (intellectual property, vehicle value, data sensitivity)
4. **Market / Regulation** (NHTSA guidance, regulatory requirements)

| Item Type | Safety Risk | CAL Typical |
|-----------|---|---|
| Convenience (seats, mirrors, audio) | None | CAL 1 |
| Non-critical comfort (climate, lighting) | Low | CAL 1–2 |
| Diagnostics & service tools | Low | CAL 2 |
| Powertrain (fuel, transmission) | High | CAL 2–3 |
| Chassis (steering, brakes) | Critical | CAL 3–4 |
| Autonomous functions | Critical | CAL 3–4 |
| Immobilizer & theft | Moderate–High | CAL 2–3 |
| OTA infrastructure | High | CAL 3 |
| Telematics (financial) | Moderate | CAL 2–3 |

---

## CAL Assignment in TARA Workbook

### Title Page
- Declare target CAL for the item (e.g., "CAL 2 — Defense against skilled attackers")
- Justify based on functional safety criticality and threat landscape

### Cybersecurity Goals (CSG) Tab
- Assign CAL to each CSG derived from Risk 3–5 scenarios
- CSGs for Risk 5 → typically CAL 3–4
- CSGs for Risk 3–4 → typically CAL 2–3
- CSGs for Risk 2 → typically CAL 1–2

### Risk Treatment Tab
- Use target item CAL to guide treatment selection (Avoid/Reduce/Share/Retain)
- Residual risk must be acceptable per CAL threshold
- Document CAL justification for each high-risk treatment decision

---

## Color Coding in Workbook

- **CAL 4**: Critical Red (#C00000)
- **CAL 3**: Orange (#F4B084)
- **CAL 2**: Yellow (#FFE699)
- **CAL 1**: Green (#C6EFCE)

Apply to CSG column in Cybersecurity Goals tab for quick visual identification of assurance level distribution.

---

## References

- ISO/SAE 21434:2021 — Cybersecurity for Road Vehicles, Clause 15 (TARA)
- NHTSA — Best Practices for Automotive Cybersecurity (2016)
- AUTOSAR — Secure Onboard Communication (SecOC)
- ETSI — Cybersecurity Standards for Connected Vehicles
