# CERT C Secure Coding Standard — Categories

The CERT C Secure Coding Standard (Carnegie Mellon SEI) organizes rules by category. This skill draws from all categories with emphasis on embedded automotive context.

## DCL — Declarations and Initialization

Rules for declaring and initializing variables, ensuring proper scope, storage class, and initialization.

| Rule | Title | Severity | Context |
|------|-------|----------|---------|
| DCL30-C | Declare objects with appropriate storage classes and linkage | Required | Prevent unintended global state; restrict visibility |
| DCL39-C | Avoid information leakage when passing structures across trust boundaries | Mandatory | Ensure sensitive data in structs is not leaked |
| DCL41-C | Do not declare variables inside a switch statement before the first case label | Advisory | Code organization; prevent undefined behavior |

## EXP — Expressions

Rules for safe expression evaluation, avoiding side effects, and ensuring deterministic behavior.

| Rule | Title | Severity | Context |
|------|-------|----------|---------|
| EXP30-C | Do not depend on the order of evaluation of subexpressions | Mandatory | Avoid undefined behavior from side effects |
| EXP32-C | Do not access volatile objects through nonvolatile references | Required | Ensure hardware register semantics |
| EXP33-C | Do not read uninitialized variables | Mandatory | Prevent undefined behavior and information leakage |

## INT — Integers

Rules for safe integer arithmetic, preventing overflow, underflow, and sign-conversion issues.

| Rule | Title | Severity | Context |
|------|-------|----------|---------|
| INT32-C | Ensure that integer operations do not result in overflow | Mandatory | Prevent undefined behavior (CWE-190) |
| INT33-C | Ensure that integer operations on signed operands do not result in underflow | Mandatory | Prevent undefined behavior (CWE-191) |
| INT34-C | Do not shift an expression by a negative number of bits or by greater than or equal to the width of the expression | Mandatory | Ensure shift is well-defined (CWE-197) |
| INT35-C | Use intmax_t or uintmax_t for formatted I/O on programmer-defined integer types | Required | Ensure correct printf/scanf format specifiers |

## STR — Strings

Rules for safe string handling, preventing buffer overflows and format string vulnerabilities.

| Rule | Title | Severity | Context |
|------|-------|----------|---------|
| STR31-C | Guarantee that storage for strings has sufficient space for character data and the null terminator | Mandatory | Prevent buffer overflow (CWE-119) |
| STR32-C | Do not pass a non-string-literal format string to a formatted output function | Mandatory | Prevent format string vulnerability (CWE-134) |
| STR34-C | Cast characters to unsigned char before converting to larger integer sizes | Required | Prevent sign extension errors |
| STR38-C | Do not confuse narrow and wide character strings and functions | Required | Ensure character encoding consistency |

## MEM — Memory Management

Rules for safe memory allocation, deallocation, and pointer usage, preventing use-after-free and double-free.

| Rule | Title | Severity | Context |
|------|-------|----------|---------|
| MEM30-C | Do not access freed memory | Mandatory | Prevent use-after-free vulnerability (CWE-416) |
| MEM31-C | Free dynamically allocated memory when no longer needed | Mandatory | Prevent memory leaks |
| MEM34-C | Only free memory allocated dynamically | Mandatory | Prevent double-free on stack/static memory (CWE-415) |
| MEM35-C | Allocate sufficient memory for an object of a given type | Required | Prevent buffer overflow via incorrect allocation |

## FIO — File I/O

Rules for safe file operations, input validation, and resource management.

| Rule | Title | Severity | Context |
|------|-------|----------|---------|
| FIO32-C | Do not perform operations on objects of unknown or incompatible type | Required | Ensure file type safety |
| FIO34-C | Distinguish between characters read from a file and EOF | Required | Correctly handle end-of-file |
| FIO37-C | Do not assume that fgets() or fgetws() returns a newline-terminated string | Required | Handle unterminated lines correctly |

## ENV — Environment

Rules for safe interaction with the operating system environment.

| Rule | Title | Severity | Context |
|------|-------|----------|---------|
| ENV30-C | Do not call system() | Mandatory | Prevent command injection (CWE-78); use exec family |
| ENV33-C | Do not call exit() in a function that might be invoked by a library | Required | Preserve application control; use return instead |
| ENV34-C | Do not rely on ordering of return values from getenv() | Required | Ensure environment variable consistency |

## SIG — Signals

Rules for safe signal handling, avoiding race conditions in signal handlers.

| Rule | Title | Severity | Context |
|------|-------|----------|---------|
| SIG30-C | Call only asynchronous-safe functions within signal handlers | Mandatory | Prevent undefined behavior and race conditions |
| SIG34-C | Do not call signal() from within interruptible signal handlers | Required | Prevent recursion and undefined behavior |

## ERR — Error Handling

Rules for safe error handling, detecting and reporting failures correctly.

| Rule | Title | Severity | Context |
|------|-------|----------|---------|
| ERR30-C | Set errno to zero before calling a library function known to fail and check errno after the call | Mandatory | Ensure error detection (CWE-390) |
| ERR32-C | Detect and handle standard library errors | Mandatory | Handle malloc, fopen, read failures correctly |
| ERR33-C | Detect and handle transmission errors | Required | Validate checksums, detect corruption |

## Summary

These 27 core CERT C rules (Mandatory + Required) map to:
- **Memory Safety**: MEM30, MEM31, MEM34, MEM35 (use-after-free, double-free, buffer overflow)
- **Integer Safety**: INT32, INT33, INT34, INT35 (overflow, underflow, shift safety)
- **String/I-O Safety**: STR31, STR32, STR34, STR38, FIO32, FIO34, FIO37 (format strings, bounds, EOF)
- **Input Validation**: STR32 (no format strings), ENV30 (no system()), ERR32 (detect errors)
- **Error Handling**: ERR30, ERR32, ERR33 (errno, standard errors, transmission errors)
- **Declarations/Expressions**: DCL30, EXP30, EXP33 (scope, order of evaluation, uninitialized)
- **Signals/Environment**: SIG30, SIG34, ENV30, ENV33, ENV34 (signal safety, no system, exit)

When combined with MISRA Amendment 1 cryptography and authentication rules, this forms a comprehensive secure coding guideline for embedded automotive software.
