# Secure Coding Guidelines Methodology

## What are secure coding guidelines?

Secure coding guidelines are a set of rules, practices, and standards that developers follow to write code that is resistant to security vulnerabilities. Unlike functional safety guidelines (ISO 26262 MISRA C:2012), which focus on preventing failures from random hardware faults, secure coding guidelines focus on preventing exploitation by malicious actors or misuse of the software.

## Integration with ISO 21434 (Cybersecurity Engineering)

ISO 21434 Road vehicles Cybersecurity engineering defines a V-model for cybersecurity similar to ISO 26262 for functional safety:

1. **TARA** (Threat Analysis and Risk Assessment) — identifies security threats and allocates to vehicle/item levels
2. **CS Goals** (Cybersecurity Goals) — high-level safety/security targets ("encrypt all stored keys")
3. **CS Concept** (Cybersecurity Concept) — architecture-level mechanisms (HSM, TLS, mutual auth)
4. **CS Architecture** (Cybersecurity Architecture) — allocation to software/hardware components
5. **Secure Design** — implementation via secure coding guidelines, cryptographic protocols, etc.
6. **Verification & Validation** — static analysis, dynamic testing, penetration testing, audit

Secure coding guidelines implement the **Secure Design** level: they translate CS architectural decisions into enforceable code-level rules.

## Relationship to MISRA C:2012

MISRA C:2012 Amendment 1 (2016) added a security perspective to the original functional safety focus. Key additions:

- **Memory Safety**: bounds checking, no dynamic allocation in safety-critical code, stack canaries
- **Integer Safety**: overflow/underflow detection, sign conversion safety, bitwise operation validation
- **String/I-O Safety**: format string protection, buffer overflow prevention, input validation
- **Cryptography & Authentication**: approved algorithms, key length minimums, secure randomness

This skill combines:
1. Core MISRA C:2012 rules (functional safety focus)
2. MISRA Amendment 1 security additions
3. CERT C Secure Coding Standard (SEI Carnegie Mellon)
4. AUTOSAR C++14 secure coding subset
5. CWE Top 25 vulnerability mappings

## Rule categories and CWE mappings

### Memory Safety (CWE-119, CWE-416, CWE-415)

Rules ensuring safe memory access:
- Bounds checking before array/pointer access
- No use-after-free (free() followed by dereference)
- No double-free (free() called twice on same pointer)
- No buffer overflow (write beyond allocated size)
- Stack canary support (detect stack smashing)

Relevant CWEs:
- CWE-787: Out-of-bounds Write (buffer overflow)
- CWE-119: Improper Restriction of Operations within the Bounds of a Memory Buffer
- CWE-416: Use After Free
- CWE-415: Double Free

### Integer Safety (CWE-190, CWE-191, CWE-197)

Rules ensuring safe arithmetic:
- Overflow detection and prevention
- Underflow detection and prevention
- Safe shift operations (bounds check shift amount)
- Safe type conversions (sign extension, integer promotion)

Relevant CWEs:
- CWE-190: Integer Overflow or Wraparound
- CWE-191: Integer Underflow (Wrap or Wraparound)
- CWE-197: Numeric Errors

### String/I-O Safety (CWE-20, CWE-78, CWE-134)

Rules ensuring safe string and I/O operations:
- Format string protection (no user input as format string)
- Input validation (length, type, range, format)
- Input sanitization (remove/escape dangerous chars)
- Untrusted input handling

Relevant CWEs:
- CWE-20: Improper Input Validation
- CWE-134: Use of Externally-Controlled Format String
- CWE-78: Improper Neutralization of Special Elements used in an OS Command (Command Injection)

### Cryptography (CWE-327, CWE-326, CWE-338)

Rules ensuring secure cryptographic operations:
- Use only approved algorithms (AES, SHA-256, not MD5/DES/RC4)
- Minimum key lengths (AES >= 128 bits, RSA >= 2048 bits)
- Cryptographically secure PRNG (not srand/rand, use /dev/urandom or CSRNG)
- Constant-time implementations (side-channel resistance)
- Secure key storage (never plaintext, use HSM or secure enclave)

Relevant CWEs:
- CWE-327: Use of a Broken or Risky Cryptographic Algorithm
- CWE-326: Inadequate Encryption Strength
- CWE-338: Use of Cryptographically Weak Pseudo-Random Number Generator

### Authentication & Authorization (CWE-256, CWE-269, CWE-384)

Rules ensuring secure identity and access control:
- Password hashing (bcrypt, scrypt, PBKDF2; never plaintext)
- Privilege separation (run with minimum privileges, drop after startup)
- Principle of least privilege (grant only required access)
- Session management (secure tokens, HTTPS only)
- Access control enforcement (verify authorization before every privileged op)

Relevant CWEs:
- CWE-256: Plaintext Storage of Password
- CWE-269: Improper Handling of Insufficient, Missing, or Extraneous Privileges
- CWE-384: Session Fixation

### Logging & Audit (CWE-532, CWE-778)

Rules ensuring secure audit trails:
- Log all security-relevant events (authentication, authorization, privilege changes)
- Never log secrets (passwords, keys, tokens, PII)
- Protect log integrity (checksums, digital signatures)
- Retain logs (minimum 90 days; securely archive older)
- Audit trail immutability (append-only, no deletion)

Relevant CWEs:
- CWE-532: Insertion of Sensitive Information into Log File
- CWE-778: Insufficient Logging

## Rule severity levels

### Mandatory
Non-compliance is a security defect; no exceptions permitted. Examples:
- Do not use weak algorithms (CWE-327)
- Perform bounds checking (CWE-119)
- No use-after-free (CWE-416)

### Required
Non-compliance requires documented deviation and approval. Examples:
- Integer overflow detection
- Input validation scope

### Advisory
Recommended but may be overridden with rationale. Examples:
- Specific naming conventions
- Code organization preferences

## Tool-based enforcement

Static analysis tools (Coverity, CodeSonar, Polyspace) implement these rules via:

1. **Dataflow analysis** — track variable values and detect potential errors
2. **Control flow analysis** — analyze all execution paths for violations
3. **Taint analysis** — track untrusted data from source to use
4. **Memory safety analysis** — detect buffer overflows, use-after-free, etc.
5. **Proof techniques** — prove correctness of arithmetic, memory operations

## Deviation process

When a rule cannot be met (due to legacy code, performance constraints, 3rd-party libraries), a deviation/waiver is required:

1. **Request**: Developer submits justification (technical rationale, risk assessment, mitigation)
2. **Review**: Security Architect + Project Manager evaluate
3. **Approval**: Documented and time-limited (annual re-justification)
4. **Logging**: All deviations tracked in deviation register

This ensures accountability and prevents security guideline erosion over time.
