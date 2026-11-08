# Cybersecurity Control Catalog

## Hardware Security Modules (HSM)

**Purpose**: Secure storage and operations on sensitive cryptographic keys (root-of-trust, OTA signing keys, session master keys).

**Properties**:
- FIPS 140-2 Level 3 minimum certification
- Tamper-resistant packaging (potting, mesh)
- Secure key injection at manufacturing
- Support for AES, RSA, ECC, HMAC operations
- Random number generation (entropy source)

**Suppliers**: Entrust, Gemalto/Thales, Securosys, Luna HSM (network), SoftHSM (software-only for testing)

**Common use**: Off-board or on-board OTA signing, key derivation, secure session establishment

---

## Trusted Platform Module (TPM)

**Purpose**: Isolated execution environment for cryptographic operations on-device.

**Properties**:
- Secure key storage (shielded from main processor)
- Platform Configuration Registers (PCR) for boot measurement
- Attestation capabilities (quote signed by TPM)
- Support for AES, RSA, HMAC, SHA-2, ECC
- Specification: TPM 2.0 (ISO/IEC 11889)

**Variants**: Discrete TPM (separate IC, 33 MHz SPI clock), firmware TPM (software in secure coprocessor), integrated TPM (in SoC)

**Common use**: Secure boot chain, session key derivation, device attestation, firmware measurement

---

## Secure Elements (SE) and TEE Chips

**Purpose**: Dedicated secure coprocessor for cryptographic operations and secure storage.

**Common Types**:
- **ATECC608A** (Microchip): ECDSA P-256, SHA-256, HMAC, AES-128 (CCM)
- **SE050** (NXP): RSA-4096, ECC P-384, AES, SHA-384, Java Card
- **M2351** (Nuvoton): Cortex-M4 MCU with secure enclave, AES, RSA, ECC
- **STM32H7** with TrustZone-M: Dual-core, secure/non-secure partitioning

**Common use**: OTA key provisioning, secure boot validation, diagnostic authentication, edge HSM

---

## Cryptographic Algorithms

### Symmetric (Bulk Encryption)

| Algorithm | Key Length | Mode | Use Case |
|-----------|-----------|------|----------|
| **AES** | 128/192/256 bits | GCM, CBC, CTR | OTA, session encryption, data at rest |
| **ChaCha20** | 256 bits | Poly1305 | AEAD alternative (not NIST standard) |
| **Camellia** | 128/192/256 bits | GCM | ISO/IEC standard alternative |

**Recommendation**: AES-256-GCM for OTA and session encryption (FIPS approved, hardware acceleration available)

### Asymmetric (Key Exchange, Signing)

| Algorithm | Key Length | Use Case |
|-----------|-----------|----------|
| **RSA** | 2048/3072/4096 bits | OTA firmware signing, key transport |
| **ECDSA** | P-256/P-384/P-521 | OTA signing (preferred for embedded), session auth |
| **ECDH** | P-256/P-384/P-521 | Session key agreement, forward secrecy |
| **EdDSA** | Ed25519/Ed448 | Lightweight signing (RFC 8032) |

**Recommendation**: 
- ECDSA P-384 or RSA-4096 for firmware OTA (longer lifecycle)
- ECDH P-256 for session key agreement (faster, smaller keys)

### Hash Functions

| Algorithm | Output | Use Case |
|-----------|--------|----------|
| **SHA-256** | 256 bits | Integrity, certificates, firmware measurement |
| **SHA-384** | 384 bits | High-assurance applications, FIPS 140-3 |
| **SHA-512** | 512 bits | Long-term key derivation |
| **BLAKE2** | 256/512 bits | Fast hashing (non-NIST standard) |

**Recommendation**: SHA-256 or SHA-384 (FIPS approved, standardized in TLS 1.3)

### Message Authentication Codes (MAC)

| Algorithm | Key Length | Use Case |
|-----------|-----------|----------|
| **HMAC-SHA256** | 256 bits | Session authentication, CAN SecOC |
| **CMAC-AES** | 128/256 bits | CAN SecOC, lightweight MAC |
| **GHASH** | (implicit in AES-GCM) | Authenticated encryption (within GCM) |
| **Poly1305** | 256 bits | ChaCha20-Poly1305 AEAD |

**Recommendation**: HMAC-SHA256 for TLS, CMAC-AES for CAN (SecOC per AUTOSAR)

### Key Derivation Functions (KDF)

| Algorithm | Use Case |
|-----------|----------|
| **HKDF** (HMAC-based) | Per-purpose key derivation from root key |
| **KDF-COUNTER** (NIST SP 800-108) | FIPS-approved, used in TLS 1.2 |
| **PBKDF2** | Password-based key derivation (slow, for passphrases) |

**Recommendation**: HKDF-SHA256 (fast, parallelizable, suitable for per-session keys)

---

## Communication Protocols

### TLS 1.3

**Purpose**: Secure channel establishment for OTA, diagnostics, remote services.

**Security Properties**:
- Perfect Forward Secrecy (PFS) via ECDH
- Mutual authentication via X.509 certificates or PSK
- Authenticated encryption (AES-GCM, ChaCha20-Poly1305)
- Mandatory record integrity (MAC over ciphertext)
- 0-RTT resumption (resumption tickets, PSK identity)

**Cipher Suites**:
- `TLS_AES_256_GCM_SHA384` (primary recommendation for OTA)
- `TLS_AES_128_GCM_SHA256` (acceptable, faster)
- `TLS_CHACHA20_POLY1305_SHA256` (alternative for embedded)

**Recommendations**:
- Enforce mutual certificate authentication
- Verify certificate revocation (OCSP stapling, CRL)
- 90-day key rotation (OTA signing key)
- 30-day session key rotation (if session resumption enabled)

### IPsec

**Purpose**: IP-level encryption for cellular or VPN links.

**Security Properties**:
- AH (Authentication Header) or ESP (Encapsulating Security Payload)
- Encryption: AES-GCM, AES-CBC
- Integrity: HMAC-SHA256, HMAC-SHA384
- IKEv2 key agreement (ECDH)

**Typical Use**: Vehicle-to-Cloud over LTE/5G with mutual authentication

### AUTOSAR SecOC (Secure Onboard Communication)

**Purpose**: Message-level authentication for CAN/CAN-FD frames.

**Security Properties**:
- CMAC-AES-128 over payload + freshness value
- Freshness: Monotonic counter or timestamp
- Per-ECU symmetric keys (derived from master key)

**Typical Use**: Safety-critical CAN messages (steering, braking) authenticated without encryption

---

## Secure Boot Technologies

### SHE (Secure Hardware Extension)

**Purpose**: Lightweight secure boot and key management for microcontrollers.

**Properties**:
- Immutable BootROM verifies Bootloader with OEM public key
- Bootloader verifies App image with second-stage key
- Anti-rollback via monotonic counter
- SHE-EXTEND: Measurement of App into secure counter (attestation)

**Suppliers**: NXP, STMicroelectronics, Infineon (AURIX)

### TrustZone-M (Arm)

**Purpose**: Secure/non-secure execution contexts on Cortex-M processors.

**Properties**:
- Hardware isolation of secure coprocessor
- Secure boot via Bootloader running in secure context
- Isolation of sensitive data (keys, cryptographic operations)
- Debug restrictions (debug only in secure context)

### UEFI Secure Boot (Automotive)

**Purpose**: Multi-stage boot verification on domain controllers with unified firmware ecosystem.

**Properties**:
- DB (allowed) and DBX (blacklist) signature databases
- Signature verification of bootloaders and kernel
- Rollback protection via version counters

---

## Access Control Enforcement

### Role-Based Access Control (RBAC)

| Role | Capabilities | Authentication |
|------|-------------|----------------|
| **Developer** | Debug via JTAG/SWD, firmware upload, key injection | Private dev certificate + passphrase |
| **OEM Service** | OTA update, diagnostic readout, limited key operations | Service certificate + 2FA |
| **Service Tech** | Diagnostic readout, no key operations | Tech ID card + PIN |
| **End User** | None (OTA automatic); no direct access | Vehicle unlock via NFC/BLE |

### Debug Disable

**Production Lockdown**:
- Debug ports (JTAG, SWD, UART, JTAG-like) disabled by fuses
- Secure boot verifies debug-disable state before loading App
- One-time unlock token (HMAC-SHA256 of HWID + timestamp), ~24-hour expiry
- Secure boot ROM rejects firmware modifications if debug unlocked

### Certificate Pinning

**Usage**: Prevent Man-in-the-Middle attacks on TLS:
- Embed issuer or leaf certificate public key hash in firmware
- Reject TLS connections to unpinned certificates
- Periodically refresh pinned certs via signed firmware update

---

## Intrusion Detection Systems (IDS)

### Network-Level

**Purpose**: Detect anomalous CAN, Ethernet, or wireless traffic.

**Capabilities**:
- Rate limiting per message type
- Signature-based detection (known attack patterns)
- Anomaly detection (statistical model of normal traffic)
- Tamper alerts (unexpected node activity)

### Host-Level

**Purpose**: Monitor on-device resource usage (CPU, memory, bus traffic).

**Capabilities**:
- Watchdog (processor reset on timeout)
- Fault injection detection (glitch attacks)
- Memory integrity checking (XOR, Hamming code)
- Differential power analysis (DPA) detection

---

## Certificate Management

### PKI Hierarchy

**Typical structure**:
- **Root CA**: Offline, airgapped; signs intermediate CAs
- **Intermediate CA**: Signing CA; issues OTA signing or TLS server certs
- **Leaf Certs**: OTA signing (firmware signing key), TLS server (backend service), device certs (mutual TLS)

### Certificate Lifecycle

| Phase | Duration | Action |
|-------|----------|--------|
| Issuance | N/A | CSR from HSM/TPM, CA signs, deploy to device |
| Active | 1-3 years | Used for signing or TLS handshakes |
| Renewal | 30 days before expiry | New certificate issued and staged |
| Revocation | Immediate (compromise) | Certificate added to CRL, OCSP staple, or pushed via OTA |
| Destruction | N/A | Private key zeroized; certificate archived |

### OCSP Stapling (for TLS)

**Purpose**: Reduce latency of certificate revocation checks.

**Mechanism**: Server queries OCSP responder offline; includes stapled response (signed by OCSP responder) in TLS handshake.

---

## Attestation

### Hardware Attestation (via TPM)

**Process**:
1. Backend server sends random nonce
2. Device TPM generates quote over PCR values + nonce
3. Device returns quote + AIK (Attestation Identity Key) certificate signed by TPM vendor
4. Server verifies quote signature and compares PCR values to expected baseline

**Use**: Verify firmware integrity, detect unauthorized code execution

### Software Attestation (Code Signing)

**Process**:
1. Firmware image signed by OEM private key (RSA-4096 or ECDSA P-384)
2. Signature included in firmware metadata
3. Bootloader verifies signature before running App

---

## Encryption at Rest

### Flash Encryption (Whole-Disk)

**Technology**: Hardware cipher (AES-128 CTR mode) transparently encrypts/decrypts all flash reads/writes.

**Key Management**: Per-device key (unique or derived from secure root).

**Limitation**: Does not protect keys stored in the same flash; use secure enclave or external HSM.

### Database Encryption

**Technology**: Application-level encryption of sensitive fields (keys, credentials, PII).

**Key Management**: Master key from HSM; per-record keys derived via HKDF-SHA256.

---

## Fuzzing and Testing Infrastructure

### Black-Box Fuzzing

**Purpose**: Automated discovery of parsing bugs, memory corruption, denial-of-service.

**Tools**: AFL, libFuzzer, Jazzer (Java), with ASAN (AddressSanitizer) and UBSan (Undefined Behavior Sanitizer).

**Target**: OTA parser, diagnostic protocol parser, crypto library API.

### Cryptographic Validation

**Standards**: FIPS 140-3, NIST CAVP (Cryptographic Algorithm Validation Program).

**Procedure**:
- Test vectors for known test cases
- Stress tests (large inputs, edge cases)
- Performance benchmarks (throughput, latency)
- Compliance validation (standard compliance, no deviations)

---

## Deployment and Provisioning

### Secure OTA Provisioning Flow

1. **Device Identification**: IMEI, VIN, public key fingerprint
2. **TLS Handshake**: Mutual certificate authentication with backend
3. **Firmware Staging**: Encrypted download (AES-256-GCM), signature verification (RSA-4096 or ECDSA P-384)
4. **Version Check**: Anti-rollback verification (device monotonic counter vs. image version)
5. **Installation**: Atomic flash programming with backup fallback
6. **Verification**: Post-install secure boot confirms version, triggers attestation
7. **Cleanup**: Erase temporary buffers, zeroize session keys

### Key Injection at Manufacturing

1. **Secure HSM**: OEM HSM generates per-device root key in secure enclave
2. **Temporary Channel**: Encrypted via AES-KW (key wrap) with manufacturing master key
3. **Device Reception**: Bootloader receives wrapped key, unwraps in secure boot ROM, stores in secure enclave
4. **Verification**: Secure boot confirms key integrity before enabling OTA

---

## Common Compliance Standards

- **FIPS 140-3**: Hardware/software cryptographic module validation (Level 2/3 for HSMs)
- **Common Criteria**: EAL5+ for high-assurance security functions
- **NIST SP 800-56A**: ECDH key agreement protocol
- **NIST SP 800-88**: Guidelines for media sanitization (key zeroization)
- **ISO 11770**: Key management standards
- **AUTOSAR SecOC**: CAN message authentication (ISO 13849)
