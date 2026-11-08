# CS Architecture Refinement Methodology

ISO/SAE 21434 Cybersecurity Architecture (clause 8) refines system-level Cybersecurity Requirements (CSRs) and Cyber Attack Levels (CALs) into concrete security controls, cryptographic operations, key management policies, secure boot chains, and defense-in-depth strategies.

## Architecture Layers

### 1. Security Controls Layer
Map each CSR to one or more CS Elements (hardware or logical security controls):
- **Hardware security modules (HSM)**: FIPS 140-2 Level 3, cryptographic key storage and operations
- **Trusted Platform Module (TPM)**: TrustZone, Secure Elements (SE), isolated crypto processor
- **Secure boot ROM**: Immutable root-of-trust, signature verification, anti-rollback
- **Firewall/IDS**: Network perimeter, intrusion detection, traffic filtering
- **Certificate Authority**: PKI hierarchy, key issuance and revocation
- **Key store**: Secure flash partitions, encrypted key databases
- **Debug disable**: Production lockdown, no JTAG/SWD/UART access

### 2. Cryptographic Inventory
For each cryptographic operation (signing, encryption, hashing, key agreement):
- Algorithm: AES-128/256 (block cipher), RSA-2048/4096 (asymmetric), ECC P-256/384/521 (elliptic curve), SHA-256/384/512 (hash), HMAC/CMAC (integrity), HKDF (key derivation)
- Mode: ECB (never for confidentiality), CBC, CTR, GCM (authenticated encryption), CBC-MAC, CMAC, GHASH
- Key length: 128/192/256 bits (AES), 2048/3072/4096 bits (RSA), P-256/384/521 (ECC)
- Lifecycle: generation, storage, distribution, rotation, destruction

### 3. Key Management
Per key class (OTA signing, session encryption, MAC verification, firmware authentication):
- **Generation**: On-device random (TPM/HSM), offline in KMS, pre-provisioning at manufacturing
- **Storage**: HSM, TPM, encrypted flash, secure enclave, certificate store
- **Rotation**: One-time-use (session keys), periodic (annual, per-deployment), event-triggered (key compromise)
- **Distribution**: Secure transport (TLS 1.3), key wrapping (AES-KW, RSA-OAEP), out-of-band provisioning
- **Destruction**: Secure erase (cryptographic erase, physical destruction), zeroization per NIST SP 800-88

### 4. Secure Boot Chain
Multi-stage verification from power-on to application execution:
1. **BootROM** (immutable, signed by OEM): Verify Bootloader signature
2. **Bootloader** (updatable, verified by ROM): Verify Application image, measure to Trusted Platform
3. **Application**: Execute with verified code, locked-down debug, attestation
- **Measurement chain**: Each stage hashes its successor and stores in PCR (Platform Configuration Register) or secure counter
- **Anti-rollback**: Monotonic counter per firmware version; reject older versions
- **Secure unlock**: HWID-locked provisioning, time-limited debug unlock, attestation challenge-response

### 5. Secure Communication
Per network channel (OTA, diagnostic, CAN, LIN, Ethernet):
- **Protocol**: TLS 1.3 (Wi-Fi), IPsec (cellular), SecOC (CAN-FD), custom PSK-HMAC
- **Authentication**: Mutual TLS with certificates, pre-shared keys (PSK), session tokens
- **Encryption**: AES-256-GCM mandatory for OTA and sensitive diagnostic
- **Integrity**: CMAC, HMAC, GHASH (authenticated encryption)
- **Replay protection**: Nonce, timestamp, monotonic counter (SecOC sequence number)
- **Session key derivation**: HKDF-SHA256, TLS PRF, or custom KDF

### 6. Access Control
Enforce least-privilege; granular roles per security domain:
- **Development**: Debug enabled, private keys accessible, logging disabled
- **Manufacturing**: Limited to OTA provisioning, key injection, secure boot ROM programming
- **Service**: Diagnostic over CAN/Ethernet, no firmware downgrade, audit trail mandatory
- **Customer**: No direct access; OEM controls all keys and updates
- **Authentication factors**: Multiple factors for sensitive operations (private key + passphrase, multi-party authorization)

### 7. Defense-in-Depth
Layered controls across attack surface:
- **Layer 1 (Perimeter)**: Firewall rules, MAC filtering, port restrictions
- **Layer 2 (Network)**: IDS, encrypted transport, rate limiting
- **Layer 3 (Host)**: OS hardening, secure boot, code signing, ASLR (if applicable)
- **Layer 4 (Application)**: Input validation, secure parsing, cryptographic checks, logging
- **Layer 5 (Data)**: Encryption at rest, key derivation, secure deletion

## Common Patterns

### OTA (Over-The-Air) Updates
- Firmware image signed by OEM private key (RSA-4096 or ECDSA P-384)
- TLS 1.3 handshake with mutual certificate authentication
- AES-256-GCM encryption of download stream
- Anti-rollback: Monotonic version counter checked before installation
- Roll-back protection: Secure boot rejects firmware versions older than current

### Session Encryption (e.g., Diagnostic)
- Session key negotiated via ECDH P-256 or PSK-HMAC
- AES-256-GCM for command/response encryption
- Session timeout and idle timeout (e.g., 10 minutes)
- Audit log: All commands, timestamps, initiator ID

### CAN Security (SecOC)
- CMAC-AES-128 over CAN message payload
- Freshness value (counter or timestamp) concatenated before MAC
- MAC receiver verifies counter monotonicity
- Secure boot key used to configure SecOC (root-of-trust)

### Multi-Stage Key Derivation
- Master key (root-of-trust) stored in HSM or TPM
- Per-purpose keys derived via HKDF-SHA256 with fixed info strings:
  - "OTA_SIGNING" → RSA private key seed
  - "SESSION_ENCRYPTION" → AES key
  - "DIAGNOSTIC_AUTH" → HMAC key
- Per-session keys derived from per-purpose key + nonce

## Threat-to-Control Mapping

Each CSR addresses one or more threats from the TARA (Threat Analysis and Risk Assessment):
- **Threat**: Firmware injection via OTA channel
  - **CSR**: Firmware image must be authenticated and encrypted
  - **Controls**: OTA signing (RSA-4096), TLS 1.3, AES-256-GCM, anti-rollback
  - **TARA Level**: TARA3 or TARA4 (critical)

- **Threat**: Debug port used for key extraction
  - **CSR**: Debug interface must be disabled in production
  - **Controls**: Secure boot enforces debug-disable, one-time unlock via provisioning
  - **TARA Level**: TARA4 (critical for key material)

- **Threat**: Man-in-the-middle on diagnostic channel
  - **CSR**: Diagnostic sessions must be authenticated and encrypted
  - **Controls**: Mutual TLS, session tokens, audit logging
  - **TARA Level**: TARA2 or TARA3

## Compliance Evidence

Cybersecurity Architecture is traceable to:
- System-level CSRs (from Cybersecurity Concept)
- Threat Analysis and Risk Assessment (TARA) results
- Hardware and Software Safety Requirements (if cross-domain)
- Security testing plan (penetration testing, cryptographic validation, secure boot verification)
- Integration and hardening plan (secure provisioning, key injection, final lock-down)

Verification includes:
- Design review (control adequacy, defense-in-depth coverage, key lifecycle completeness)
- Testing (cryptographic validation per FIPS 186-4, penetration testing, secure boot chain verification)
- Secure provisioning (HSM-based key generation, secure transport, tamper-evident packaging)
