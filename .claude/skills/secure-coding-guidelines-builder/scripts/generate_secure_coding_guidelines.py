"""
Secure Coding Guidelines Generator — generates a multi-tab ISO 21434-aligned workbook
with secure coding rules (CERT C, MISRA Amendment 1, AUTOSAR C++14) and CWE Top 25 mappings.

Usage:
    python generate_secure_coding_guidelines.py <input.json> <output.xlsx>

Pipeline:
- Read project metadata from input JSON (project, code_base, CAL, language, standards)
- Load secure coding rules from canonical database (CERT C categories, MISRA Amendment 1, AUTOSAR)
- Scaffold memory/integer/string safety rules, cryptography, authentication/authorization, logging
- Generate CWE Top 25 coverage mapping
- Pre-populate tool configuration (Coverity, CodeSonar, Polyspace)
- Document deviation/waiver process
- Output 14-tab xlsx workbook with complete traceability

See references/ for methodology and CWE mappings.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# ---------------------------------------------------------------------------
# Canonical secure coding rules database
# ---------------------------------------------------------------------------

SECURE_CODING_RULES = [
    # CERT C rules (declarations & expressions)
    {"rule_id": "DCL30-C", "source": "CERT C", "category": "Declarations", "severity": "Required",
     "cwe": "CWE-570", "text": "Declare objects with appropriate storage classes and linkage",
     "rationale": "Prevent unintended side effects from global state; restrict visibility to minimum required.",
     "example_compliant": "static int internal_counter = 0;", "example_noncompliant": "int counter; // global"},

    {"rule_id": "EXP30-C", "source": "CERT C", "category": "Expressions", "severity": "Mandatory",
     "cwe": "CWE-690", "text": "Do not depend on the order of evaluation of subexpressions",
     "rationale": "Avoid undefined behavior from side effects; ensure deterministic results.",
     "example_compliant": "int a = f(); int b = g(); int c = a + b;",
     "example_noncompliant": "int c = f() + g(); // order undefined"},

    # CERT C rules (integers)
    {"rule_id": "INT32-C", "source": "CERT C", "category": "Integers", "severity": "Mandatory",
     "cwe": "CWE-190", "text": "Ensure that integer operations do not result in overflow",
     "rationale": "Integer overflow is undefined behavior and can be exploited for arbitrary code execution.",
     "example_compliant": "if (a > INT_MAX - b) { /* handle overflow */ }",
     "example_noncompliant": "int result = a + b; // no bounds check"},

    {"rule_id": "INT33-C", "source": "CERT C", "category": "Integers", "severity": "Mandatory",
     "cwe": "CWE-191", "text": "Ensure that integer operations on signed operands do not result in underflow",
     "rationale": "Integer underflow is undefined behavior and can cause unexpected program behavior.",
     "example_compliant": "if (a < INT_MIN + b) { /* handle underflow */ }",
     "example_noncompliant": "int result = a - b; // no bounds check"},

    {"rule_id": "INT34-C", "source": "CERT C", "category": "Integers", "severity": "Required",
     "cwe": "CWE-197", "text": "Do not shift an expression by a negative number of bits or by greater than or equal to the width of the expression",
     "rationale": "Shifting by invalid amounts is undefined behavior; results are unpredictable.",
     "example_compliant": "if (shift_amount >= 0 && shift_amount < 32) result = a << shift_amount;",
     "example_noncompliant": "int result = a << -1; // undefined"},

    # CERT C rules (strings)
    {"rule_id": "STR31-C", "source": "CERT C", "category": "Strings", "severity": "Mandatory",
     "cwe": "CWE-119", "text": "Guarantee that storage for strings has sufficient space for character data and the null terminator",
     "rationale": "Buffer overflow is one of the most exploitable vulnerabilities in C; null terminator is essential.",
     "example_compliant": "char buf[100]; strncpy(buf, src, 99); buf[99] = '\\0';",
     "example_noncompliant": "char buf[10]; strcpy(buf, very_long_string); // overflow"},

    {"rule_id": "STR34-C", "source": "CERT C", "category": "Strings", "severity": "Mandatory",
     "cwe": "CWE-134", "text": "Cast characters to unsigned char before converting to larger integer sizes",
     "rationale": "Sign extension of char to int can cause incorrect results in range checks.",
     "example_compliant": "if ((unsigned char)c == 255) { /* ... */ }",
     "example_noncompliant": "if (c == 255) { /* may be wrong if c is signed */ }"},

    # CERT C rules (memory)
    {"rule_id": "MEM30-C", "source": "CERT C", "category": "Memory", "severity": "Mandatory",
     "cwe": "CWE-416", "text": "Do not access freed memory",
     "rationale": "Use-after-free is a critical vulnerability; freed memory may be reallocated or contain stale data.",
     "example_compliant": "free(ptr); ptr = NULL; /* only use ptr after reassignment */",
     "example_noncompliant": "free(ptr); int x = ptr->field; // use-after-free"},

    {"rule_id": "MEM34-C", "source": "CERT C", "category": "Memory", "severity": "Mandatory",
     "cwe": "CWE-415", "text": "Only free memory allocated dynamically",
     "rationale": "Freeing stack or static memory is undefined behavior; prevents double-free.",
     "example_compliant": "void *ptr = malloc(size); free(ptr);",
     "example_noncompliant": "int arr[10]; free(arr); // stack memory"},

    # MISRA C:2012 Amendment 1 (security focus)
    {"rule_id": "MISRA-C-2012-1.2", "source": "MISRA C:2012 Amendment 1", "category": "Memory",
     "severity": "Required", "cwe": "CWE-121", "text": "No dynamic memory allocation in safety-critical regions",
     "rationale": "Dynamic allocation is non-deterministic; may fail at runtime and be exploited.",
     "example_compliant": "/* use static allocation only */",
     "example_noncompliant": "void *ptr = malloc(size); // in safety-critical region"},

    {"rule_id": "MISRA-C-2012-5.1", "source": "MISRA C:2012 Amendment 1", "category": "Integers",
     "severity": "Mandatory", "cwe": "CWE-192", "text": "External identifiers shall be distinct (avoid truncation)",
     "rationale": "Prevent confusion between similar identifiers; improves code clarity and reduces mutation risk.",
     "example_compliant": "/* use unique, descriptive names */",
     "example_noncompliant": "int very_long_identifier_1; int very_long_identifier_2; // may collide"},

    # AUTOSAR C++14 (security subset)
    {"rule_id": "AUTOSAR-A0-4-2", "source": "AUTOSAR C++14", "category": "Declarations",
     "severity": "Required", "cwe": "CWE-400", "text": "Type conversion operators shall not be used",
     "rationale": "Explicit casts are safer; implicit conversions can hide errors.",
     "example_compliant": "int x = static_cast<int>(f);",
     "example_noncompliant": "(int)f; // C-style cast"},

    # Cryptography rules
    {"rule_id": "CRYPTO-001", "source": "AUTOSAR + CERT", "category": "Cryptography",
     "severity": "Mandatory", "cwe": "CWE-327", "text": "Do not use weak cryptographic algorithms (MD5, SHA-1, DES, RC4, DES3)",
     "rationale": "These algorithms have known attacks and should not be used in new designs.",
     "example_compliant": "/* use SHA-256, AES-256 */",
     "example_noncompliant": "MD5(data, ...) // weak"},

    {"rule_id": "CRYPTO-002", "source": "AUTOSAR + CERT", "category": "Cryptography",
     "severity": "Mandatory", "cwe": "CWE-326", "text": "Use cryptographic keys of minimum length 128 bits (AES) or 2048 bits (RSA)",
     "rationale": "Short keys are vulnerable to brute-force attacks.",
     "example_compliant": "/* AES key length >= 128 bits */",
     "example_noncompliant": "/* AES key length = 64 bits */"},

    {"rule_id": "CRYPTO-003", "source": "AUTOSAR + CERT", "category": "Cryptography",
     "severity": "Mandatory", "cwe": "CWE-338", "text": "Use approved random number generators (PRNG); do not use srand(time(NULL))",
     "rationale": "Weak RNG leads to predictable keys and initialization vectors (IVs).",
     "example_compliant": "/* use /dev/urandom or CSRNG */",
     "example_noncompliant": "srand(time(NULL)); // weak"},

    # Authentication & Authorization
    {"rule_id": "AUTH-001", "source": "AUTOSAR + CERT", "category": "Authentication",
     "severity": "Mandatory", "cwe": "CWE-256", "text": "Never store plaintext passwords; use salted, iterated hashing (bcrypt, scrypt, PBKDF2)",
     "rationale": "Plaintext passwords are exploitable; weak hashing allows offline brute-force.",
     "example_compliant": "/* use bcrypt with cost >= 12 */",
     "example_noncompliant": "strcpy(password_db, plaintext); // plaintext storage"},

    {"rule_id": "AUTH-002", "source": "AUTOSAR + CERT", "category": "Authorization",
     "severity": "Required", "cwe": "CWE-269", "text": "Implement principle of least privilege; minimize access rights for each component",
     "rationale": "Limit the blast radius of a compromise; reduce attack surface.",
     "example_compliant": "/* grant only required permissions */",
     "example_noncompliant": "/* grant admin access to all tasks */"},

    # Logging & Audit
    {"rule_id": "LOG-001", "source": "AUTOSAR + CERT", "category": "Logging",
     "severity": "Required", "cwe": "CWE-778", "text": "Log all security-relevant events (authentication, authorization, privilege changes, errors)",
     "rationale": "Audit trail enables detection and forensics of security incidents.",
     "example_compliant": "log('User %s granted privilege %s', user, priv);",
     "example_noncompliant": "/* no logging */"},

    {"rule_id": "LOG-002", "source": "AUTOSAR + CERT", "category": "Logging",
     "severity": "Mandatory", "cwe": "CWE-532", "text": "Never log secrets (passwords, keys, tokens, PII); sanitize logs before transmission",
     "rationale": "Secrets in logs are easily compromised; PII exposure violates privacy regulations.",
     "example_compliant": "log('Password hash: %s', hash);",
     "example_noncompliant": "log('Password: %s', plaintext); // secret exposure"},

    # Input validation
    {"rule_id": "INPUT-001", "source": "CERT C", "category": "Strings",
     "severity": "Mandatory", "cwe": "CWE-20", "text": "Validate all untrusted input (length, type, range, format)",
     "rationale": "Unvalidated input is the root of many attacks (injection, buffer overflow).",
     "example_compliant": "if (strlen(input) <= MAX_LEN && validate_format(input)) { process(input); }",
     "example_noncompliant": "process(user_input); // no validation"},

    {"rule_id": "INPUT-002", "source": "CERT C", "category": "Strings",
     "severity": "Mandatory", "cwe": "CWE-78", "text": "Do not use user input in format strings; use format string literals",
     "rationale": "Format string vulnerabilities allow reading/writing arbitrary memory.",
     "example_compliant": "printf('%s', user_input);",
     "example_noncompliant": "printf(user_input); // format string vulnerability"},

    # Memory safety (bounds)
    {"rule_id": "BOUNDS-001", "source": "CERT C", "category": "Memory",
     "severity": "Mandatory", "cwe": "CWE-119", "text": "Always perform array bounds checking before access",
     "rationale": "Out-of-bounds access is a critical vulnerability; can corrupt memory or leak secrets.",
     "example_compliant": "if (index < array_size) { value = array[index]; }",
     "example_noncompliant": "value = array[index]; // no bounds check"},
]

CWE_TOP25 = [
    ("CWE-787", "Out-of-bounds Write", "Buffer overflow, stack overflow"),
    ("CWE-79", "Improper Neutralization of Input During Web Page Generation", "XSS (not typical for embedded)"),
    ("CWE-89", "Improper Neutralization of Special Elements used in an SQL Command", "SQL injection (not typical for embedded)"),
    ("CWE-416", "Use After Free", "Use-after-free vulnerability"),
    ("CWE-190", "Integer Overflow or Wraparound", "Integer overflow"),
    ("CWE-352", "Cross-Site Request Forgery (CSRF)", "CSRF (not typical for embedded)"),
    ("CWE-434", "Unrestricted Upload of File with Dangerous Type", "Arbitrary file upload"),
    ("CWE-306", "Missing Authentication for Critical Function", "Authentication bypass"),
    ("CWE-502", "Deserialization of Untrusted Data", "Object injection"),
    ("CWE-77", "Improper Neutralization of Special Elements used in a Command", "Command injection"),
    ("CWE-476", "NULL Pointer Dereference", "Null pointer dereference"),
    ("CWE-22", "Improper Limitation of a Pathname to a Restricted Directory", "Path traversal"),
    ("CWE-269", "Improper Handling of Missing, Insufficient, or Extraneous Privileges", "Privilege escalation"),
    ("CWE-400", "Uncontrolled Resource Consumption", "DoS via resource exhaustion"),
    ("CWE-639", "Authorization Bypass Through User-Controlled Key", "Authorization bypass"),
    ("CWE-215", "Information Exposure Through Debug Information", "Debug info exposure"),
    ("CWE-668", "Exposure of Resource to Wrong Sphere", "Information exposure"),
    ("CWE-327", "Use of a Broken or Risky Cryptographic Algorithm", "Weak cryptography"),
    ("CWE-131", "Incorrect Calculation of Buffer Size", "Buffer size miscalculation"),
    ("CWE-326", "Inadequate Encryption Strength", "Weak encryption key"),
    ("CWE-338", "Use of Cryptographically Weak Pseudo-Random Number Generator", "Weak PRNG"),
    ("CWE-521", "Weak Password Requirements", "Weak password policy"),
    ("CWE-426", "Untrusted Search Path", "Directory search vulnerability"),
    ("CWE-427", "Uncontrolled Search Path Element", "Path manipulation"),
    ("CWE-636", "Not Controlling Generated Code", "Code generation vulnerability"),
]

STATIC_ANALYSIS_TOOLS = [
    "Coverity (Synopsys)", "CodeSonar (GrammaTech)", "Polyspace (MathWorks)",
    "Clang Static Analyzer", "Splint"
]

TOOL_RULE_PACKS = {
    "Coverity (Synopsys)": {
        "rule_pack": "CWE Top 25, CERT C, MISRA C:2012",
        "key_checkers": "BUFFER_SIZE, INTEGER_OVERFLOW, USE_AFTER_FREE, RESOURCE_LEAK, MISSING_LOCK",
        "false_positive_policy": "Review CWE-415/416 high-confidence reports; requires manual triage for low-confidence",
        "baseline_setup": "Enable CERT C ruleset; disable low-confidence checks in integration environment"
    },
    "CodeSonar (GrammaTech)": {
        "rule_pack": "CERT C, MISRA C:2012, CWE Top 25",
        "key_checkers": "UNREACHABLE, EMPTY_BLOCK, UNINITIALIZED_VARIABLE, RACE_CONDITION, NULL_DEREF",
        "false_positive_policy": "Suppress only after code review; document suppression in deviation log",
        "baseline_setup": "Initialize baseline with legacy suppressions; report only new issues in CI"
    },
    "Polyspace (MathWorks)": {
        "rule_pack": "MISRA C:2012, CERT C, ISO 26262 subset",
        "key_checkers": "OVERFLOW, DIVIDE_BY_ZERO, OUT_OF_BOUNDS, UNINITIALIZED, DEAD_CODE",
        "false_positive_policy": "Use Polyspace proof and assumption mechanisms; document all overrides",
        "baseline_setup": "Run in full analysis mode; enable environment models for embedded targets"
    },
}

# ---------------------------------------------------------------------------
# Generator functions
# ---------------------------------------------------------------------------

def create_workbook(project: dict) -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = "00_Title_Page"
    return wb

def add_title_page(ws, project: dict):
    """Tab 0: Title page"""
    ws.append(["SECURE CODING GUIDELINES"])
    ws.append(["ISO 21434 Embedded Automotive Software Security"])
    ws.append([])
    ws.append(["Project:", project.get("name", "N/A")])
    ws.append(["Document ID:", project.get("doc_id", "N/A")])
    ws.append(["Revision:", project.get("revision", "1.0")])
    ws.append(["Date:", project.get("date", datetime.now().strftime("%Y-%m-%d"))])
    ws.append(["Author:", project.get("author", "N/A")])
    ws.append(["Approver:", project.get("approver", "N/A")])
    ws.append([])
    ws.append(["Code Base:", project.get("code_base", "N/A")])
    ws.append(["Language:", project.get("language", "C/C++")])
    ws.append(["CAL:", project.get("cal", "N/A")])
    ws.append(["Applicable Standards:", ", ".join(project.get("applicable_standards", ["CERT C"]))])

def add_document_control(wb, project: dict):
    """Tab 1: Document Control"""
    ws = wb.create_sheet("01_Document_Control")
    ws.append(["Revision", "Date", "Author", "Change Description"])
    ws.append([project.get("revision", "1.0"), datetime.now().strftime("%Y-%m-%d"),
               project.get("author", "N/A"), "Initial release"])

def add_scope(wb, project: dict):
    """Tab 2: Scope"""
    ws = wb.create_sheet("02_Scope")
    ws.append(["Scope Item", "Details"])
    ws.append(["Code Base", project.get("code_base", "N/A")])
    ws.append(["Language", project.get("language", "C/C++")])
    ws.append(["Target CAL", project.get("cal", "A/B/C/D")])
    ws.append(["Applicable Guidelines", ", ".join(project.get("applicable_standards", ["CERT C"]))])
    ws.append(["Static Analysis Tools", ", ".join(project.get("static_analysis_tools", STATIC_ANALYSIS_TOOLS[:1]))])
    ws.append(["Excluded Code", "Third-party libraries (if separately governed)"])

def add_coding_rules_catalog(wb):
    """Tab 3: Coding Rules Catalog"""
    ws = wb.create_sheet("03_Coding_Rules_Catalog")
    headers = ["Rule_ID", "Source", "Category", "Severity", "CWE", "Rule Text", "Rationale", "Compliant Example", "Non-Compliant Example"]
    ws.append(headers)

    severity_colors = {
        "Mandatory": "FF0000",  # red
        "Required": "FFA500",   # orange
        "Advisory": "FFFF00",   # yellow
    }

    for rule in SECURE_CODING_RULES:
        ws.append([
            rule["rule_id"],
            rule["source"],
            rule["category"],
            rule["severity"],
            rule["cwe"],
            rule["text"],
            rule["rationale"],
            rule["example_compliant"],
            rule["example_noncompliant"],
        ])
        # Color severity cell
        severity_cell = ws.cell(row=ws.max_row, column=4)
        severity_cell.fill = PatternFill(start_color=severity_colors.get(rule["severity"], "FFFFFF"), fill_type="solid")

def add_memory_safety_rules(wb):
    """Tab 4: Memory Safety Rules"""
    ws = wb.create_sheet("04_Memory_Safety_Rules")
    ws.append(["Memory Safety Rule", "Requirement", "CWE"])
    memory_rules = [
        ("Bounds Checking", "Always perform array/pointer bounds checking before access", "CWE-119"),
        ("No Use-After-Free", "Do not access freed memory; set pointers to NULL after free", "CWE-416"),
        ("No Double-Free", "Free each allocation exactly once; check for prior free", "CWE-415"),
        ("No Buffer Overflow", "Ensure buffer sizes accommodate all writes including null terminator", "CWE-119"),
        ("Stack Canaries", "Enable stack canary protection to detect buffer overflow on stack", "CWE-674"),
    ]
    for rule, req, cwe in memory_rules:
        ws.append([rule, req, cwe])

def add_integer_safety_rules(wb):
    """Tab 5: Integer Safety Rules"""
    ws = wb.create_sheet("05_Integer_Safety_Rules")
    ws.append(["Integer Safety Rule", "Requirement", "CWE"])
    integer_rules = [
        ("Overflow Detection", "Detect and handle integer overflow in arithmetic operations", "CWE-190"),
        ("Underflow Detection", "Detect and handle integer underflow in arithmetic operations", "CWE-191"),
        ("Sign Conversion Safety", "Carefully convert between signed and unsigned integers", "CWE-195"),
        ("Shift Safety", "Validate shift amounts; only shift by 0..width-1", "CWE-197"),
        ("Wraparound Prevention", "Prevent modular arithmetic from masking errors", "CWE-193"),
    ]
    for rule, req, cwe in integer_rules:
        ws.append([rule, req, cwe])

def add_string_io_rules(wb):
    """Tab 6: String/I-O Rules"""
    ws = wb.create_sheet("06_String_IO_Rules")
    ws.append(["String/I-O Rule", "Requirement", "CWE"])
    string_rules = [
        ("Format String Safety", "Never pass user input as format string; use format literals", "CWE-134"),
        ("Buffer Overflow Prevention", "Use bounded string functions (strncpy, snprintf, not strcpy/sprintf)", "CWE-119"),
        ("Untrusted Input Validation", "Validate length, type, range, format of all untrusted input", "CWE-20"),
        ("Null Termination", "Ensure strings are properly null-terminated in all code paths", "CWE-170"),
        ("Input Sanitization", "Remove or escape dangerous characters from user input", "CWE-78"),
    ]
    for rule, req, cwe in string_rules:
        ws.append([rule, req, cwe])

def add_cryptography_rules(wb):
    """Tab 7: Cryptography Rules"""
    ws = wb.create_sheet("07_Cryptography_Rules")
    ws.append(["Cryptography Rule", "Requirement", "CWE"])
    crypto_rules = [
        ("Approved Algorithms", "Use only approved algorithms (AES-256, SHA-256, not MD5/DES/RC4)", "CWE-327"),
        ("Key Length Minimums", "AES key >= 128 bits; RSA key >= 2048 bits; ECC >= 256 bits", "CWE-326"),
        ("Random Number Generation", "Use cryptographically secure RNG (/dev/urandom, CSRNG, not srand)", "CWE-338"),
        ("Side-Channel Resistance", "Use constant-time algorithms for crypto operations", "CWE-208"),
        ("Key Storage", "Never store keys in plaintext; use secure key storage mechanisms", "CWE-321"),
    ]
    for rule, req, cwe in crypto_rules:
        ws.append([rule, req, cwe])

def add_auth_rules(wb):
    """Tab 8: Authentication/Authorization Rules"""
    ws = wb.create_sheet("08_Authentication_Authorization_Rules")
    ws.append(["Authentication/Authorization Rule", "Requirement", "CWE"])
    auth_rules = [
        ("Password Hashing", "Use salted, iterated hashing (bcrypt cost >= 12, scrypt, PBKDF2)", "CWE-256"),
        ("Session Management", "Implement secure session tokens; use HTTPS for transmission", "CWE-384"),
        ("Privilege Separation", "Run with minimum required privileges; drop privileges after startup", "CWE-269"),
        ("Principle of Least Privilege", "Grant only required access rights per component/user", "CWE-276"),
        ("Access Control Enforcement", "Verify authorization before every privileged operation", "CWE-639"),
    ]
    for rule, req, cwe in auth_rules:
        ws.append([rule, req, cwe])

def add_logging_rules(wb):
    """Tab 9: Logging/Audit Rules"""
    ws = wb.create_sheet("09_Logging_Audit_Rules")
    ws.append(["Logging/Audit Rule", "Requirement", "CWE"])
    logging_rules = [
        ("Security Event Logging", "Log all authentication, authorization, privilege changes, errors", "CWE-778"),
        ("Secret Non-Exposure", "Never log passwords, keys, tokens, or PII; sanitize before transmission", "CWE-532"),
        ("Log Integrity", "Protect logs from tampering; use checksums or digital signatures", "CWE-434"),
        ("Log Retention", "Retain audit logs for minimum 90 days; securely archive older logs", "CWE-683"),
        ("Audit Trail Immutability", "Make logs append-only; prevent deletion or modification", "CWE-269"),
    ]
    for rule, req, cwe in logging_rules:
        ws.append([rule, req, cwe])

def add_cwe_top25_coverage(wb):
    """Tab 10: CWE Top 25 Coverage"""
    ws = wb.create_sheet("10_CWE_Top25_Coverage")
    ws.append(["CWE ID", "Vulnerability Name", "Description", "Addressing Rules"])

    cwe_to_rules = {
        "CWE-787": ["BOUNDS-001", "STR31-C", "INPUT-001"],
        "CWE-416": ["MEM30-C", "BOUNDS-001"],
        "CWE-190": ["INT32-C", "INT34-C"],
        "CWE-327": ["CRYPTO-001"],
        "CWE-326": ["CRYPTO-002"],
        "CWE-338": ["CRYPTO-003"],
        "CWE-256": ["AUTH-001"],
        "CWE-269": ["AUTH-002"],
        "CWE-778": ["LOG-001"],
        "CWE-532": ["LOG-002"],
        "CWE-20": ["INPUT-001", "INPUT-002"],
        "CWE-134": ["INPUT-002"],
    }

    for cwe_id, name, desc in CWE_TOP25:
        rules = ", ".join(cwe_to_rules.get(cwe_id, ["See rules catalog"]))
        ws.append([cwe_id, name, desc, rules])

def add_tool_configuration(wb, project: dict):
    """Tab 11: Tool Configuration"""
    ws = wb.create_sheet("11_Tool_Configuration")
    ws.append(["Static Analysis Tool", "Rule Pack", "Key Checkers", "False-Positive Policy", "Baseline Setup"])

    tools = project.get("static_analysis_tools", STATIC_ANALYSIS_TOOLS[:1])
    for tool in tools:
        config = TOOL_RULE_PACKS.get(tool, {})
        ws.append([
            tool,
            config.get("rule_pack", "N/A"),
            config.get("key_checkers", "N/A"),
            config.get("false_positive_policy", "N/A"),
            config.get("baseline_setup", "N/A"),
        ])

def add_deviation_process(wb):
    """Tab 12: Deviation Process"""
    ws = wb.create_sheet("12_Deviation_Process")
    ws.append(["Deviation Process Element", "Description"])
    ws.append(["Who Can Request", "Development lead; review by Security Architect"])
    ws.append(["Justification Required", "Technical rationale, risk assessment, mitigation strategy"])
    ws.append(["Approval Authority", "Security Architect + Project Manager"])
    ws.append(["Approval Timeline", "Within 5 business days"])
    ws.append(["Documentation", "Deviation Request Form with rule ID, scope, justification, end date"])
    ws.append(["Review Frequency", "Quarterly; escalate if risk increases"])
    ws.append(["Expiration", "Deviations are time-limited; re-justify annually"])
    ws.append(["Deviation Log Location", "shared_repo/deviations/secure_coding_deviations.xlsx"])

def add_references(wb):
    """Tab 13: References"""
    ws = wb.create_sheet("13_References")
    ws.append(["Reference", "URL / Location"])
    references = [
        ("CERT C Secure Coding Standard", "https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard"),
        ("MISRA C:2012 (Amendment 1)", "https://www.misra.org.uk/"),
        ("AUTOSAR Secure Coding Guidelines", "https://www.autosar.org/"),
        ("CWE: Common Weakness Enumeration", "https://cwe.mitre.org/"),
        ("CWE Top 25 Most Dangerous Software Weaknesses", "https://cwe.mitre.org/top25/"),
        ("OWASP Top 10 / OWASP Secure Coding Practices", "https://owasp.org/"),
        ("ISO 21434: Road vehicles Cybersecurity engineering", "ISO standard"),
        ("ISO 26262: Functional Safety (Part 6: Product development)", "ISO standard"),
    ]
    for ref, url in references:
        ws.append([ref, url])

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_secure_coding_guidelines.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Read input JSON
    with open(input_file, "r") as f:
        project = json.load(f)

    # Create workbook
    wb = create_workbook(project)
    ws = wb.active
    ws.title = "00_Title_Page"
    add_title_page(ws, project)

    # Add all tabs
    add_document_control(wb, project)
    add_scope(wb, project)
    add_coding_rules_catalog(wb)
    add_memory_safety_rules(wb)
    add_integer_safety_rules(wb)
    add_string_io_rules(wb)
    add_cryptography_rules(wb)
    add_auth_rules(wb)
    add_logging_rules(wb)
    add_cwe_top25_coverage(wb)
    add_tool_configuration(wb, project)
    add_deviation_process(wb)
    add_references(wb)

    # Save workbook
    wb.save(output_file)
    print(f"Generated: {output_file}")
    print(f"Tabs: {len(wb.sheetnames)}")
    print(f"Rules: {len(SECURE_CODING_RULES)}")
    print(f"Severity distribution: Mandatory={sum(1 for r in SECURE_CODING_RULES if r['severity']=='Mandatory')}, Required={sum(1 for r in SECURE_CODING_RULES if r['severity']=='Required')}, Advisory={sum(1 for r in SECURE_CODING_RULES if r['severity']=='Advisory')}")

if __name__ == "__main__":
    main()
