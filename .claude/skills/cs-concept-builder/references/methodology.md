# Cybersecurity Concept Derivation Methodology

## ISO/SAE 21434 §9.4.5 — Cybersecurity Concept

The Cybersecurity Concept (CS Concept) is the specification of Cybersecurity Requirements (CSRs) derived from the Cybersecurity Goals (CSGs) produced by the Threat Analysis and Risk Assessment (TARA) phase. Each CSR addresses one aspect of a goal and is allocated to one or more architectural elements (ECUs, gateways, communication channels, key stores, debug interfaces).

### Six Cybersecurity Requirement Categories

#### 1. **Authentication**
Ensures that the source (sender, initiator, accessor) of a command, signal, or access attempt is verified before processing.

**When triggered**: Any CSG related to "unauthorized entity receives access", "attacker impersonates legitimate system", "malware injects commands without verification".

**Requirement pattern**:
> The item shall authenticate the source of {signal/command/access} using {mechanism: PSK/Certificate/Challenge-Response} before processing.

**Mechanisms**: 
- Pre-Shared Key (PSK) with rotation policy
- Digital certificates (X.509) with CRL/OCSP revocation
- Challenge-response (HMAC, nonce-based)
- Biometric or multi-factor authentication (less common in embedded)

---

#### 2. **Authorization**
Ensures that an authenticated entity has the right to perform the requested action on the accessed resource.

**When triggered**: Any CSG related to "authorized entity performs unauthorized action", "privilege escalation", "lateral movement across domain boundaries".

**Requirement pattern**:
> The item shall verify that {entity} has authorization to {action} on {resource} prior to execution.

**Mechanisms**:
- Role-Based Access Control (RBAC) — roles tied to privilege levels
- Attribute-Based Access Control (ABAC) — flexible policy-based
- Access Control Lists (ACL) per function or data store
- Capability-based security (object carries its own permissions)

---

#### 3. **Integrity**
Ensures that data, firmware, or messages are not corrupted (intentionally or unintentionally) between creation and use.

**When triggered**: Any CSG related to "attacker modifies message payload", "firmware injection", "memory corruption via bit-flip".

**Requirement pattern**:
> The item shall verify the integrity of {data/firmware/message} using {mechanism: CRC/HMAC/Signature} prior to use or execution.

**Mechanisms**:
- CRC-16/32 — detects random bit-flips, not malicious modification
- HMAC-SHA256 — detects intentional modification if key is secret
- Digital signature (RSA-PSS, ECDSA) — detects tampering and proves origin
- Time-stamp tokens — add temporal binding

---

#### 4. **Confidentiality**
Ensures that sensitive data (keys, credentials, proprietary parameters) is not readable by unauthorized entities.

**When triggered**: Any CSG related to "attacker eavesdrops on sensitive data", "reverse-engineering via inspection", "key extraction from memory".

**Requirement pattern**:
> The item shall encrypt {data class} at rest/in transit using {algorithm: AES-128/256, RSA-2048+, ECC-P256} and manage keys via {key store mechanism}.

**Mechanisms**:
- AES-128/256 (block cipher, symmetric) — fast, proven, hardware acceleration common
- ECC (Elliptic Curve) — smaller keys than RSA, efficient for embedded
- TLS/DTLS — protocol-level confidentiality for channels
- Secure enclave or TPM — isolated key storage

---

#### 5. **Availability**
Ensures that critical functions remain operational despite intentional attack (DoS, resource exhaustion, fault injection).

**When triggered**: Any CSG related to "attacker disables critical function", "DoS attack overwhelms processor", "watchdog reset abuse".

**Requirement pattern**:
> The item shall maintain {function} available under {attack scenario} via {mitigation: rate limiting/redundancy/fail-safe/monitoring}.

**Mechanisms**:
- Rate limiting — limit message rate per sender
- Resource quotas — limit CPU/memory per task
- Redundancy — hot-standby, dual-channel with voting
- Fail-safe — graceful degradation if attack detected
- Anomaly detection — trigger mitigation on unusual pattern

---

#### 6. **Non-repudiation**
Ensures that an entity cannot deny having performed an action; creates an audit trail for forensics.

**When triggered**: Any CSG related to "attacker denies malicious action", "accountability requirement", "forensic investigation after incident".

**Requirement pattern**:
> The item shall log {event class} to a tamper-evident audit log retained for {duration}, with {timestamp/signature mechanism} to prove authenticity.

**Mechanisms**:
- Tamper-evident log (hash-chain, append-only storage)
- Signed log entries (each entry signed with private key)
- Time-stamping authority (TSA) integration — external time source
- Secure syslog (RFC5425) — TLS-encrypted central log

---

## CSR Allocation to Architecture

Each CSR is allocated to one or more **architectural elements**:

- **Gateway/Router** — authenticates inter-ECU messages, enforces authorization policies, encrypts over untrusted networks
- **ECU/Processor** — implements application-level security (auth for API calls, role checks, data encryption)
- **Memory/Data Store** — protects stored secrets via encryption, detects tampering via integrity checks
- **Key Store/HSM** — generates and protects cryptographic keys, never exposes private keys
- **Communication Channel** — encrypts and authenticates messages in flight
- **Debug Interface** — requires authentication before enabling, logs all debug access

---

## CAL (Cybersecurity Assurance Level) Inheritance

- Each CSG has a CAL (CAL-1, CAL-2, or CAL-3) assigned in TARA.
- Each CSR derived from that CSG inherits the CSG's CAL.
- If a single architectural element is allocated multiple CSRs with different CALs, the element's overall CAL is the maximum (CAL-3 dominates).

Recommended verification intensity per CAL:

| CAL | Verification Methods |
|-----|----------------------|
| CAL-1 | Informal review, manual walk-through |
| CAL-2 | Penetration testing, code review, fuzz testing |
| CAL-3 | Formal verification, dynamic analysis, red-team assessment, side-channel testing |

---

## CSR Derivation Checklist

For each CSG, ask:

1. **Who can access this asset?** → Authentication CSR
2. **Can they do what they're trying?** → Authorization CSR
3. **Has the data been tampered with?** → Integrity CSR
4. **Can unauthorized parties read it?** → Confidentiality CSR
5. **Does it work despite attack?** → Availability CSR
6. **Can we prove who did what?** → Non-repudiation CSR

Not all six apply to every goal; apply the ones that are relevant to the threat model.

---

## Fault Tree Analogy to HARA/FSC

In ISO 26262 FSC, each Safety Goal spawns a fault tree with "Violation of SG-XXX" as the top event, expanded via Input/Process/Output failure branches to basic events (one per node), then to FSRs.

In ISO/SAE 21434 CS Concept, each Cybersecurity Goal spawns a requirement-derivation tree with "Breach of CSG-XXX" as the violation event, expanded via the six security property branches (Auth/Authz/Integrity/Confidentiality/Availability/Non-rep) to CSRs per architectural element.

The structure mirrors FSC to maintain consistency across safety and security workflows.
