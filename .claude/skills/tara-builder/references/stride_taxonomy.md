# STRIDE Threat Taxonomy for ISO/SAE 21434 TARA

## Overview

STRIDE provides six threat categories for systematically identifying cybersecurity threats. Use this taxonomy to label each threat scenario in the TARA worksheet.

## Threat Categories

### S — Spoofing (Impersonation)

**Definition**: Claiming to be someone or something you are not.

**Cybersecurity Properties at Risk**: Authenticity, Authorization

**Examples in Automotive**:
- Attacker forges CAN message claiming to be a trusted ECU
- Compromised ECU claims to be OEM server during firmware update
- Unauthorized diagnostic tool impersonates factory tester
- Replay old authenticated message as new command

**Attacker Actions**:
- Capture and replay messages
- Forge credentials or certificates
- Intercept and modify message headers
- Assume identity of legitimate node

**Indicators**:
- Message authentication missing or weak
- No identity verification on CAN/Ethernet
- Debug/service credentials hardcoded or shared

### T — Tampering (Unauthorized Modification)

**Definition**: Modifying something on disk, network, or memory without authorization.

**Cybersecurity Properties at Risk**: Integrity, Availability

**Examples in Automotive**:
- Attacker modifies ECU firmware image in storage
- CAN message content altered in transit (e.g., speed sensor data)
- Configuration file modified to disable safety checks
- Debug flag bit flipped in memory to unlock features

**Attacker Actions**:
- Write to unprotected flash memory
- Modify messages on the bus
- Corrupt calibration or configuration
- Patch executable code

**Indicators**:
- No integrity checking (CRC/HMAC) on data
- Writable flash without authentication
- No message signing on critical CAN signals
- In-memory secrets or flags unprotected

### R — Repudiation (Denial of Responsibility)

**Definition**: Claiming that you didn't do something, when in fact you did.

**Cybersecurity Properties at Risk**: Non-repudiation, Authenticity

**Examples in Automotive**:
- Attacker performs firmware downgrade, denies unauthorized modification
- Service technician deletes maintenance logs, claims malfunction didn't occur
- Hacker modifies DTC records to hide failures
- System cannot prove who made a configuration change

**Attacker Actions**:
- Delete audit logs or event records
- Clear diagnostic trouble codes
- Remove evidence of unauthorized access
- Forge or modify timestamps

**Indicators**:
- No event logging or audit trail
- Logs stored on same device being attacked
- No digital signatures on critical records
- Timestamps not validated or protected

### I — Information Disclosure (Privacy Breach)

**Definition**: Exposing information to people who shouldn't have access to it.

**Cybersecurity Properties at Risk**: Confidentiality, Privacy

**Examples in Automotive**:
- Attacker reads unencrypted firmware image to reverse-engineer
- Diagnostic data containing GPS location exposed over unencrypted channel
- Calibration data extracted from flash memory
- Cryptographic keys extracted from memory or storage
- Telematics credentials exposed in plaintext logs

**Attacker Actions**:
- Read unprotected flash or EEPROM
- Eavesdrop on CAN, LIN, or Ethernet messages
- Extract keys from debug interfaces (JTAG, SWD)
- Read memory dumps or crash logs

**Indicators**:
- No encryption on sensitive data at rest or in transit
- Debug ports accessible without authentication
- Firmware images publicly available
- Credentials or keys hardcoded or in plaintext

### D — Denial of Service (Availability Attack)

**Definition**: Preventing legitimate users from accessing the system or service.

**Cybersecurity Properties at Risk**: Availability, Functional Safety

**Examples in Automotive**:
- Attacker floods CAN bus with messages, overwhelming ECU
- Malicious code enters infinite loop, blocking other functions
- Firmware corrupted, preventing boot
- Key memory region overwritten, disabling critical function
- Repeated authentication failures lock out legitimate user
- Battery drained by malicious power consumption

**Attacker Actions**:
- Send resource-exhausting messages (CAN flood)
- Corrupt firmware or configuration
- Overwrite memory (stack overflow, buffer overflow)
- Consume CPU or battery resources
- Disable watchdog or reset mechanisms

**Indicators**:
- No rate limiting on message processing
- Buffer overflow vulnerabilities
- Watchdog not monitoring all critical code paths
- No resource quotas or prioritization
- Authentication not rate-limited

### E — Elevation of Privilege (Authorization Bypass)

**Definition**: Gaining higher-level access rights than authorized.

**Cybersecurity Properties at Risk**: Authorization, Authenticity

**Examples in Automotive**:
- Attacker exploits debug ECU to unlock restricted functions
- Malware escalates from application to bootloader context
- Buffer overflow allows writing to protected memory regions
- Weak password allows bypass of development mode lock
- Hardcoded service password enables admin access
- SQL injection or format string breaks access control

**Attacker Actions**:
- Exploit software vulnerabilities (buffer overflow, integer underflow)
- Guess or brute-force weak credentials
- Use default or shared credentials
- Exploit race conditions in privilege checks
- Desolder security chips or remove fuses

**Indicators**:
- Weak password policies
- Hardcoded credentials or default passwords
- No privilege separation (ring 0 only)
- Unvalidated user input processed with privileges
- Debug modes leave elevated privileges enabled

## Threat Agent Classification

Adjust feasibility rating based on threat agent type:

| Agent Type | Example | Expertise | Equipment | Cost | Timeline |
|------------|---------|-----------|-----------|------|----------|
| **Casual Hacker** | Script kiddie, hobbyist | Moderate | Public tools | Low | Months–Years |
| **Skilled Attacker** | Security researcher, red-teamer | High | Custom + standard | Medium | Weeks–Months |
| **Insider** | Disgruntled employee, service tech | Varies | Any (physical access) | Low | Days–Weeks |
| **Organized Crime** | Commercial fraud ring | Expert team | Bespoke tools | High | Days–Weeks |
| **Nation-State** | State-sponsored APT | Elite team | Proprietary + 0-days | Unlimited | Days |

## Mapping to ISO 26262 Hazard Categories

STRIDE complements functional safety by addressing threats at the cybersecurity layer:

- **Spoofing** → prevents hazards due to false identity
- **Tampering** → integrity checks for data, firmware, configuration
- **Repudiation** → audit trail for diagnostic and maintenance actions
- **Information Disclosure** → protects proprietary algorithms, calibration, keys
- **Denial of Service** → availability of safety-critical functions
- **Elevation of Privilege** → prevents unauthorized override of safety controls

## Usage in TARA Worksheet

For each asset and cybersecurity property:

1. Enumerate threat scenarios using STRIDE (6 categories)
2. For each scenario, identify threat agent type
3. Assign STRIDE category label
4. Describe how threat manifests (entry point, attack vector)
5. Rate impact and feasibility
6. Derive cybersecurity goal if Risk ≥ 3
