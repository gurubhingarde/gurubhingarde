# CSR (Cybersecurity Requirement) Templates

This file contains canonical requirement wording for each combination of security property and architectural element. Use these as starting points; customize with specific signal names, algorithms, and timing parameters.

---

## Authentication CSRs

### Gateway/Router
**Template:**
> The item shall authenticate the source of {data/message name} received on {gateway name} using {mechanism: challenge-response/certificate/PSK} before forwarding or processing the message.

**Example (CAN Gateway):**
> The item shall authenticate the source of security-relevant CAN messages received on the main gateway using HMAC-SHA256 with per-ECU keys before forwarding.

---

### ECU/Processor
**Template:**
> The item shall authenticate all external commands and API calls to {ECU/processor name} using {mechanism: PSK/certificate/token} before executing the requested function.

**Example (OTA Agent):**
> The item shall authenticate all firmware update commands received by the OTA agent using RSA-2048 certificates before initiating flashing.

---

### Communication Channel
**Template:**
> The item shall verify the authenticity of {data name} transmitted on {channel name} using {mechanism: HMAC/signature} to prevent message injection.

**Example (CAN/Ethernet):**
> The item shall verify the authenticity of all diagnostic messages on the CAN bus using HMAC-SHA256 computed with a shared secret between gateway and ECU.

---

### Debug Interface
**Template:**
> The item shall authenticate all debug interface access requests to {interface name} using {mechanism: password/certificate/challenge} before granting debug privileges.

**Example (JTAG):**
> The item shall authenticate debug interface access to the main MCU via a challenge-response using a temporary access token before enabling trace or memory read.

---

## Authorization CSRs

### Gateway/Router
**Template:**
> The item shall verify that the source ECU has authorization to transmit {message class} on {gateway name} before forwarding based on {policy: whitelist/RBAC/message ID range}.

**Example (CAN Gateway):**
> The item shall maintain a whitelist of permitted message IDs per ECU on the CAN gateway and reject messages that violate the whitelist.

---

### ECU/Processor
**Template:**
> The item shall enforce role-based access control on {ECU name} and verify that the calling entity has the required privilege level before executing {function name}.

**Example (Secure Keystore):**
> The item shall enforce that only the OTA agent and firmware-verification module have authorization to invoke key-derivation functions on the secure key store.

---

### Debug Interface
**Template:**
> The item shall restrict debug interface access to {interface name} based on privilege level and deny sensitive operations (memory write, register modification, code injection) to unprivileged users.

**Example (JTAG):**
> The item shall enforce that only authenticated debug hosts with "admin" privilege can halt the processor; read-only access is permitted for authenticated users with "observer" privilege.

---

## Integrity CSRs

### Processor/ECU (Code/Firmware)
**Template:**
> The item shall verify the integrity of {code/firmware/configuration} loaded on {processor name} using {mechanism: CRC/HMAC/signature} prior to execution.

**Example (Firmware Verification):**
> The item shall compute and verify an SHA-256 hash of the entire application firmware before execution; if verification fails, the item shall revert to the previous known-good version.

---

### Memory/Data Store
**Template:**
> The item shall detect tampering of {data class} stored in {memory name} via {mechanism: CRC/HMAC/signature} and transition to a safe state on detection.

**Example (RAM Data Structure):**
> The item shall protect critical control structures in RAM using Hamming codes (SECDED) and detect multi-bit errors; upon detection, the item shall trigger a controlled shutdown.

---

### Key Store
**Template:**
> The item shall verify the integrity of stored keys in {key store name} using {mechanism: hash-chain/digital signature} to detect unauthorized modification.

**Example (Secure Enclave):**
> The item shall store key material in a tamper-resistant enclave and verify the integrity of the key hierarchy using a hash chain; if any key fails verification, the item shall erase all derived keys.

---

### Communication Channel
**Template:**
> The item shall verify the integrity of {message/packet} transmitted on {channel name} using {mechanism: CRC/HMAC/signature} and discard corrupted or modified messages.

**Example (CAN Bus):**
> The item shall compute an 8-byte HMAC-SHA256 trailer for all diagnostic messages on the CAN bus and verify the trailer before processing; messages with invalid HMACs shall be logged and discarded.

---

## Confidentiality CSRs

### At Rest (Stored Data)
**Template:**
> The item shall encrypt {data class} at rest in {storage element} using {algorithm: AES-128-CBC/GCM, ECC-P256} and manage encryption keys via a secure key store.

**Example (Stored Configuration):**
> The item shall encrypt sensitive vehicle parameters (VIN, calibration, owner data) at rest in non-volatile memory using AES-128-GCM with keys derived from the device root key.

---

### In Transit (Network)
**Template:**
> The item shall encrypt {data class} in transit on {channel: CAN/Ethernet/wireless} using {algorithm: TLS-ECDHE, AES-256-GCM} to prevent eavesdropping.

**Example (Diagnostic Over IP):**
> The item shall encrypt all UDS (Unified Diagnostic Services) traffic over Ethernet using TLS 1.3 with ECDHE-ECDSA and AES-256-GCM to prevent eavesdropping on proprietary parameters.

---

### Key Material
**Template:**
> The item shall protect cryptographic keys in {key store name} using {mechanism: secure enclave/HSM/cryptographic binding} and never expose private keys to unverified code.

**Example (Private Key Storage):**
> The item shall store private keys only in a secure processing environment (SPE) and ensure that key material is never written to unencrypted memory or external storage.

---

## Availability CSRs

### DoS/Resource Exhaustion
**Template:**
> The item shall defend {function name} against denial-of-service attacks on {component name} by implementing {mitigation: rate limiting/resource quota/anomaly detection} and maintaining availability under {attack scenario}.

**Example (CAN Message Flooding):**
> The item shall implement rate limiting on the CAN gateway to drop messages from a sender if they exceed 1000 msg/s; the gateway shall remain operational and process legitimately-timed messages from other ECUs.

---

### Fault Injection / Physical Attack
**Template:**
> The item shall maintain integrity and availability of {critical function} despite fault-injection attacks via {mitigation: redundancy/monitoring/fail-safe} and transition to a safe state if attack is detected.

**Example (Watchdog Protection):**
> The item shall implement a hardware watchdog with an independent reset circuit; the watchdog timer shall be periodically refreshed by secure firmware and trigger a fail-safe reset if not refreshed within 100 ms, preventing watchdog reset abuse.

---

## Non-Repudiation CSRs

### Audit Logging
**Template:**
> The item shall log {event class: security-relevant event, configuration change, privileged action} to a tamper-evident audit log on {logging element} retained for {duration: 90 days / 6 months / 2 years}.

**Example (Firmware Update Audit):**
> The item shall log all firmware update requests, including timestamp, source, firmware hash, and result (success/failure) to an append-only audit log; log entries shall be cryptographically signed with a per-session key and retained for 1 year.

---

### Integrity of Audit Trail
**Template:**
> The item shall protect the audit log from tampering via {mechanism: hash-chain/digital signature/tamper-evident storage} to ensure that log entries cannot be modified without detection.

**Example (Hash-Chained Log):**
> The item shall use a SHA-256 hash chain for the audit log; each new entry includes a hash of the previous entry, making retroactive modification detectable. The log shall be periodically signed with a long-term key and uploaded to a secure backend.

---

## Implementation Notes

1. **Placeholders** like `<TBD>`, `{mechanism}`, `{algorithm}` must be filled in during the Cybersecurity Implementation (CSI) phase. Do not leave empty.

2. **Measurability**: Every CSR must be verifiable. Avoid vague words like "protect", "secure", "robust". Be specific: "encrypt using AES-128-GCM", "authenticate using HMAC-SHA256", "verify CRC", "detect within 10 ms".

3. **Allocation**: Each CSR must clearly state which architectural element implements it. If multiple elements share responsibility, create separate CSRs.

4. **CAL Justification**: Higher-CAL CSRs require more rigorous verification. Ensure the verification plan in CSI matches the allocated CAL.

5. **Cross-Cutting Concerns**: Some CSRs (e.g., logging) may affect multiple layers. Specify which layer is primary and coordinate with other CSRs to avoid redundancy or gaps.
