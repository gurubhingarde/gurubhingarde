# CWE Top 25 Vulnerability Mapping to Secure Coding Rules

The MITRE CWE (Common Weakness Enumeration) Top 25 lists the most dangerous software vulnerabilities. This document maps each to secure coding rules that prevent or mitigate them.

## CWE-787: Out-of-bounds Write

**Description**: Writing to memory outside the intended bounds; the most common critical vulnerability.

**Root Causes in Embedded C**:
- Buffer overflow in strcpy, sprintf, strcat (no bounds checking)
- Array indexing without bounds validation
- Off-by-one errors in loops
- Integer arithmetic leading to invalid array indices

**Addressing Rules**:
- **STR31-C**: Guarantee string storage has sufficient space and null terminator
- **BOUNDS-001**: Always perform array bounds checking before access
- **INT32-C**: Ensure integer operations do not overflow (prevents index calculation errors)
- **STR34-C**: Cast characters to unsigned char (prevents sign extension in indices)

**Example Prevention**:
```c
// Vulnerable: buffer overflow
char buf[10];
strcpy(buf, user_input); // no bounds check

// Compliant: use bounded function + bounds check
char buf[MAX_LEN];
if (strlen(user_input) < MAX_LEN) {
  strncpy(buf, user_input, MAX_LEN - 1);
  buf[MAX_LEN - 1] = '\0';
}
```

## CWE-79: Improper Neutralization of Input During Web Page Generation (Cross-site Scripting / XSS)

**Relevance to Embedded Automotive**: Low for traditional embedded systems; relevant for CAN/LIN nodes with web UIs or OTA update servers.

**Root Causes**:
- User input echoed to HTML/JavaScript without escaping
- Missing Content-Security-Policy headers

**Addressing Rules**:
- **INPUT-001**: Validate all untrusted input (length, type, range, format)
- **INPUT-002**: Do not use user input in format strings

## CWE-89: Improper Neutralization of Special Elements used in an SQL Command (SQL Injection)

**Relevance to Embedded Automotive**: Low for traditional ECU firmware; relevant for telematics and connected vehicle backends.

**Root Causes**:
- Constructing SQL queries by string concatenation
- Missing parameterized query support

**Addressing Rules**:
- **INPUT-001**: Validate all untrusted input
- **ENV30-C**: Do not call system() (which can be abused for command injection)

## CWE-416: Use After Free

**Description**: Accessing memory after it has been freed; a critical memory safety vulnerability.

**Root Causes in Embedded C**:
- Freeing a pointer, then dereferencing it later
- Freeing in one function, dereferencing in another (coordination failure)
- Double-free not caught

**Addressing Rules**:
- **MEM30-C**: Do not access freed memory; set pointers to NULL after free
- **MEM31-C**: Free dynamically allocated memory when no longer needed
- **BOUNDS-001**: Perform bounds checking (prevents invalid pointer dereference)

**Example Prevention**:
```c
// Vulnerable: use-after-free
char *ptr = malloc(size);
free(ptr);
int x = ptr->field; // UB

// Compliant: set to NULL after free
free(ptr);
ptr = NULL;
// check ptr != NULL before use
```

## CWE-190: Integer Overflow or Wraparound

**Description**: Integer arithmetic exceeds the maximum representable value, causing wraparound to negative or zero.

**Root Causes in Embedded**:
- Arithmetic in array size calculations without overflow check
- Integer accumulation (counters, timers) without saturation or overflow detection
- Sign conversion promoting negative to large positive

**Addressing Rules**:
- **INT32-C**: Ensure integer operations do not result in overflow
- **INT33-C**: Ensure integer underflow is prevented
- **INT34-C**: Do not shift by invalid amounts

**Example Prevention**:
```c
// Vulnerable: silent overflow
int result = a + b; // if a,b > INT_MAX/2, overflow silently

// Compliant: check before operation
if (a > INT_MAX - b) {
  // handle overflow: saturate, error, etc.
  result = INT_MAX;
} else {
  result = a + b;
}
```

## CWE-352: Cross-Site Request Forgery (CSRF)

**Relevance to Embedded**: Low for ECU firmware; relevant for telematics backends.

## CWE-434: Unrestricted Upload of File with Dangerous Type

**Relevance to Embedded**: Relevant for OTA update systems and configuration file upload.

**Addressing Rules**:
- **INPUT-001**: Validate all untrusted input (file type, size, format)
- **FIO32-C**: Do not perform operations on objects of unknown or incompatible type

## CWE-306: Missing Authentication for Critical Function

**Description**: Critical functions (firmware update, diagnostic, privilege change) lack authentication.

**Root Causes**:
- No authentication at all
- Weak authentication (predictable tokens)
- Missing authorization check before privileged operation

**Addressing Rules**:
- **AUTH-001**: Use strong password hashing (bcrypt, scrypt)
- **AUTH-002**: Implement principle of least privilege; verify authorization before every privileged op
- **CRYPTO-001**: Use approved algorithms (for message authentication)

## CWE-502: Deserialization of Untrusted Data

**Relevance to Embedded**: Relevant for CAN message parsing, diagnostic protocols, firmware updates.

**Root Causes**:
- Parsing binary data without validation
- No integrity check (CRC, HMAC) on received data
- Malformed data triggers buffer overflow or code execution

**Addressing Rules**:
- **INPUT-001**: Validate all untrusted input (length, type, range, format)
- **MEM30-C**: Do not access freed memory
- **BOUNDS-001**: Perform array bounds checking
- **ERR32-C**: Detect and handle transmission errors (checksum failures)

## CWE-77: Improper Neutralization of Special Elements used in a Command ('Command Injection')

**Description**: User input used directly in OS command; attacker can inject shell metacharacters.

**Addressing Rules**:
- **ENV30-C**: Do not call system(); use exec family instead
- **INPUT-001**: Validate all untrusted input
- **INPUT-002**: Do not use user input in format strings

## CWE-476: NULL Pointer Dereference

**Description**: Dereferencing a pointer without checking for NULL.

**Root Causes**:
- malloc/calloc failure not checked
- Function returning NULL on error not validated
- Complex control flow making NULL paths invisible

**Addressing Rules**:
- **EXP33-C**: Do not read uninitialized variables (includes NULL pointers)
- **MEM30-C**: Do not access freed memory (set to NULL first)
- **ERR32-C**: Detect and handle standard library errors (malloc returns NULL on failure)

**Example Prevention**:
```c
// Vulnerable: NULL dereference
char *buf = malloc(size);
strcpy(buf, src); // buf could be NULL

// Compliant: check for NULL
char *buf = malloc(size);
if (buf == NULL) {
  // handle allocation failure
  return ERROR;
}
strcpy(buf, src);
```

## CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')

**Relevance to Embedded**: Relevant for file system access in telematics, update systems.

**Addressing Rules**:
- **INPUT-001**: Validate all untrusted input (file path format, length)
- **FIO32-C**: Do not perform operations on objects of unknown type

## CWE-269: Improper Handling of Missing, Insufficient, or Extraneous Privileges ('Privilege Escalation')

**Description**: Application grants more privileges than necessary, or fails to drop privileges after startup.

**Addressing Rules**:
- **AUTH-002**: Implement principle of least privilege
- **ENV33-C**: Do not call exit() from library functions; preserve control

## CWE-400: Uncontrolled Resource Consumption ('Denial of Service / Resource Exhaustion')

**Description**: Unbounded memory, CPU, or bandwidth allocation triggered by attacker input.

**Root Causes in Embedded**:
- Unbounded loop on untrusted input (no iteration limit)
- Unbounded memory allocation (no size check)
- Unbounded network message queue

**Addressing Rules**:
- **INPUT-001**: Validate all untrusted input (must include size/count bounds)
- **MEM35-C**: Allocate sufficient memory for object of given type (but not more)
- **ERR32-C**: Detect allocation failures

## CWE-639: Authorization Bypass Through User-Controlled Key

**Description**: Authorization decision relies on user-controlled data (e.g., user ID in JWT without signature verification).

**Addressing Rules**:
- **AUTH-002**: Implement principle of least privilege; verify authorization before every privileged op
- **CRYPTO-001**: Use approved algorithms for message authentication (HMAC, ECDSA)

## CWE-215: Information Exposure Through Debug Information

**Description**: Debug symbols, log messages, or error messages leak sensitive information (file paths, configuration, keys).

**Addressing Rules**:
- **LOG-002**: Never log secrets (passwords, keys, tokens, PII); sanitize logs before transmission
- **EXP33-C**: Do not read uninitialized variables (prevents leaking stack contents)

## CWE-668: Exposure of Resource to Wrong Sphere ('Information Exposure')

**Description**: Sensitive data (keys, credentials, PII) exposed to unprivileged users or external systems.

**Addressing Rules**:
- **LOG-002**: Never log secrets; sanitize logs
- **AUTH-001**: Never store plaintext passwords; use salted hashing
- **CRYPTO-001**: Approved algorithms for encryption
- **CRYPTO-002**: Minimum key lengths

## CWE-327: Use of a Broken or Risky Cryptographic Algorithm

**Description**: Code uses weak cryptographic algorithms (MD5, SHA-1, DES, RC4).

**Addressing Rules**:
- **CRYPTO-001**: Do not use weak algorithms (MD5, SHA-1, DES, RC4); use AES-256, SHA-256
- **CRYPTO-002**: Use minimum key lengths (AES >= 128 bits, RSA >= 2048 bits)

## CWE-131: Incorrect Calculation of Buffer Size

**Description**: Buffer size calculated incorrectly, leading to overflow on data write.

**Root Causes**:
- Off-by-one error (forgetting null terminator)
- Integer overflow in size calculation
- Wrong variable used in allocation

**Addressing Rules**:
- **STR31-C**: Guarantee string storage has sufficient space for null terminator
- **INT32-C**: Ensure integer operations do not overflow (size calculations)
- **MEM35-C**: Allocate sufficient memory for object of given type

## CWE-326: Inadequate Encryption Strength

**Description**: Encryption key is too short to resist brute-force attack.

**Addressing Rules**:
- **CRYPTO-002**: Use minimum key lengths (AES >= 128 bits, RSA >= 2048 bits, ECC >= 256 bits)

## CWE-338: Use of Cryptographically Weak Pseudo-Random Number Generator

**Description**: PRNG is not cryptographically secure; attackers can predict outputs (e.g., srand(time(NULL))).

**Addressing Rules**:
- **CRYPTO-003**: Use approved RNG (CSRNG, /dev/urandom); do not use srand/rand

## CWE-521: Weak Password Requirements

**Description**: Passwords lack minimum length, complexity, or strength requirements.

**Addressing Rules**:
- **AUTH-001**: Use strong hashing (bcrypt cost >= 12, scrypt, PBKDF2)
- **AUTH-002**: Implement principle of least privilege; require strong initial credentials

## CWE-426: Untrusted Search Path

**Description**: Code loads libraries from untrusted directories, enabling privilege escalation.

**Relevance to Embedded**: Lower risk in firmware; relevant for application loaders and plugin systems.

## CWE-427: Uncontrolled Search Path Element

**Relevance to Embedded**: Similar to CWE-426.

## CWE-636: Not Controlling Generated Code

**Relevance to Embedded**: Relevant for code generation tools, model-based design.

---

## Summary Table

| CWE ID | Category | Embedded Relevance | Key Addressing Rules |
|--------|----------|-------------------|----------------------|
| CWE-787 | Memory/Buffer | **CRITICAL** | STR31-C, BOUNDS-001, INT32-C |
| CWE-79 | Web/XSS | Low (web UI only) | INPUT-001, INPUT-002 |
| CWE-89 | SQL Injection | Low (DB backend only) | INPUT-001 |
| CWE-416 | Use-After-Free | **CRITICAL** | MEM30-C, MEM31-C |
| CWE-190 | Integer Overflow | **CRITICAL** | INT32-C, INT33-C |
| CWE-352 | CSRF | Low (web/HTTP only) | AUTH-002 |
| CWE-434 | File Upload | Medium (OTA) | INPUT-001, FIO32-C |
| CWE-306 | Missing Auth | Medium | AUTH-001, AUTH-002 |
| CWE-502 | Deserialization | Medium (CAN/proto) | INPUT-001, ERR32-C |
| CWE-77 | Command Injection | Medium | ENV30-C, INPUT-001 |
| CWE-476 | NULL Deref | High | EXP33-C, MEM30-C, ERR32-C |
| CWE-22 | Path Traversal | Medium (files) | INPUT-001, FIO32-C |
| CWE-269 | Privilege Escalation | Medium | AUTH-002 |
| CWE-400 | Resource Exhaustion | Medium | INPUT-001 |
| CWE-639 | Auth Bypass | High | AUTH-002, CRYPTO-001 |
| CWE-215 | Debug Info Leak | Medium | LOG-002, EXP33-C |
| CWE-668 | Info Exposure | High | LOG-002, AUTH-001, CRYPTO-001 |
| CWE-327 | Weak Crypto | **CRITICAL** | CRYPTO-001 |
| CWE-131 | Buffer Size Error | High | STR31-C, INT32-C |
| CWE-326 | Weak Key | **CRITICAL** | CRYPTO-002 |
| CWE-338 | Weak RNG | **CRITICAL** | CRYPTO-003 |
| CWE-521 | Weak Password | Medium | AUTH-001 |
| CWE-426 | Search Path | Low | (filesystem access control) |
| CWE-427 | Search Path Element | Low | (filesystem access control) |
| CWE-636 | Generated Code | Low | (code gen tool control) |

**CRITICAL**: These CWEs require mandatory secure coding rules with zero exceptions.
