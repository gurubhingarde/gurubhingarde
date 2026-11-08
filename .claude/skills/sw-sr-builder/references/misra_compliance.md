# MISRA C:2012 Quick Reference for SW Safety Contexts

## Overview

MISRA C:2012 (Motor Industry Software Reliability Association) provides guidelines for the use of the C programming language in critical systems. It specifies 143 rules and directives to reduce defects and improve code reliability. This guide focuses on rules most commonly applied in functional safety (ISO 26262) software development.

---

## Rule Categories for Safety-Critical Software

### 1. Pointer Use and Memory Management

**Issue:** Uncontrolled pointer arithmetic and dynamic memory allocation create opportunities for buffer overflow, use-after-free, and memory corruption.

**Applicable MISRA Rules:**
- **Rule 8.13**: Pass `const` qualifiers for read-only parameters
- **Rule 9.1**: Initialize variables at declaration
- **Rule 9.2**: Ensure array subscripts are within bounds (static analysis verifiable)
- **Rule 12.3**: No side effects in condition expressions (prevents pointer increment in loop condition)
- **Rule 18.1**: No dereferencing of null pointers (add safety checks before all dereferences)
- **Rule 18.2**: No subtraction of pointers (risk of out-of-bounds calculation)
- **Rule 18.4**: No dynamic object sizes (use fixed-size arrays, statically verifiable)

**Safety Context:**
```c
// VIOLATION: Dynamic memory allocation prohibited in ASIL-C/D
uint8_t *buffer = malloc(1024);

// COMPLIANT: Static allocation, bounded size
#define BUFFER_SIZE 1024
uint8_t buffer[BUFFER_SIZE];
for (int i = 0; i < BUFFER_SIZE; i++) {
    buffer[i] = ...;  // Verifiably in bounds
}
```

---

### 2. Function and Control Flow

**Issue:** Unreachable code, missing return statements, implicit conversions, and implicit control flow mask defects.

**Applicable MISRA Rules:**
- **Rule 2.1**: Do not use restricted characters in comments or strings
- **Rule 2.2**: No code that cannot be reached
- **Rule 2.3**: Functions should not be declared but not defined
- **Rule 6.1**: Functions should return a value of the appropriate type (no implicit return)
- **Rule 14.1**: All if-else statements must be clearly closed (no ambiguous dangling else)
- **Rule 14.2**: All loops must have a controlling condition (no infinite loops without break)
- **Rule 14.3**: Controlling expressions must be loop-invariant (no dynamic loop termination)
- **Rule 15.3**: Any label shall be at block scope
- **Rule 16.1**: Functions shall have external linkage and single exit point (or be static)
- **Rule 16.3**: Function must not call itself (no recursion)
- **Rule 16.4**: Function with const return shall not return addressable object

**Safety Context:**
```c
// VIOLATION: Implicit recursion risk
int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}

// COMPLIANT: Iterative, loop-bounded, single exit
uint32_t factorial(uint8_t n) {
    uint32_t result = 1;
    for (uint8_t i = 2; i <= n && i <= 20; i++) {  // Bounded loop
        result *= i;
        if (result > MAX_UINT32) break;  // Overflow guard
    }
    return result;
}
```

---

### 3. Type Conversions and Implicit Casts

**Issue:** Implicit or unsafe type conversions (e.g., float → int, int → uint8_t) can cause data loss, sign change, or overflow.

**Applicable MISRA Rules:**
- **Rule 10.1**: Operands of an operator should have compatible types (no implicit conversion)
- **Rule 10.2**: The value of an expression shall not be implicitly converted to a different type
- **Rule 10.3**: The type of an expression shall not be implicitly converted to a different type
- **Rule 10.4**: Both operands of an operator should have the same type (avoid promotion)
- **Rule 10.6**: Composite expressions should not be cast to a different essential type

**Safety Context:**
```c
// VIOLATION: Implicit int → uint8_t conversion, possible truncation
int16_t sensor_reading = read_sensor();
uint8_t scaled = sensor_reading / 100;  // Loses sign, truncates range

// COMPLIANT: Explicit bounds check + cast
int16_t sensor_reading = read_sensor();
if (sensor_reading >= 0 && sensor_reading <= 25500) {
    uint8_t scaled = (uint8_t)(sensor_reading / 100);  // Explicit cast
} else {
    // Handle out-of-range error
}
```

---

### 4. Integer Overflow and Underflow

**Issue:** Arithmetic operations on integers without bounds checking can overflow, violating safety assumptions.

**Applicable MISRA Rules:**
- **Rule 12.1**: Operands of arithmetic operators should not lead to loss of precision
- **Rule 12.2**: Right-hand operand of shift operator should be less than operand width
- **Rule 12.4**: Evaluation order of operands in relational operators should be consistent

**Safety Context:**
```c
// VIOLATION: Unchecked multiplication can overflow
uint16_t result = count * scale;  // If count and scale are both large, overflow

// COMPLIANT: Bounds check before operation
uint16_t multiply_safe(uint16_t a, uint16_t b) {
    if (a != 0 && b > (UINT16_MAX / a)) {
        return UINT16_MAX;  // Saturate on overflow
    }
    return a * b;
}
```

---

### 5. Loop Iteration Bounds

**Issue:** Unbounded or dynamically-controlled loops prevent static analysis of task execution time.

**Applicable MISRA Rules:**
- **Rule 14.2**: Loop iterations must have a fixed upper bound or loop-variant expression
- **Rule 14.3**: Loop controlling expression must be loop-invariant (not modified inside loop)
- **Rule 14.4**: Loop variable must be a simple scalar, not modified except in loop expression

**Safety Context:**
```c
// VIOLATION: Loop count depends on data (input), not verifiable statically
void process_buffer(uint8_t *data, uint8_t *end) {
    while (data != end) {  // Depends on input data, could be unbounded
        process_element(*data++);
    }
}

// COMPLIANT: Loop count bounded by constant, statically verifiable
#define MAX_BUFFER_SIZE 256
void process_buffer(uint8_t *data, uint16_t size) {
    uint16_t count = (size < MAX_BUFFER_SIZE) ? size : MAX_BUFFER_SIZE;
    for (uint16_t i = 0; i < count; i++) {  // Static bound, verifiable
        process_element(data[i]);
    }
}
```

---

### 6. Global Variables and Static Scope

**Issue:** Global variables introduce shared state, race conditions, and coupling. Static scope limits visibility and reduces coupling.

**Applicable MISRA Rules:**
- **Rule 8.5**: An object with external linkage shall be declared in one, and only one, file
- **Rule 8.8**: An external object or function shall be declared in one and only one file
- **Rule 8.9**: An object with file scope shall not be accessed from outside its translation unit
- **Rule 8.10**: An inline function shall be declared with static storage class qualifier
- **Rule 8.11**: Tentative definitions should be avoided

**Safety Context:**
```c
// VIOLATION: Global variable, shared across all code, race condition risk
uint32_t fault_counter = 0;

void increment_fault() {
    fault_counter++;  // Unprotected read-modify-write, not atomic
}

// COMPLIANT: Static scope, accessed only through controlled function, atomic operation
static uint32_t fault_counter = 0;

void increment_fault(void) {
    // In real code, protect with mutex or atomic operation
    __disable_irq();
    fault_counter++;
    __enable_irq();
}

// Getter function for controlled access
uint32_t get_fault_count(void) {
    uint32_t count;
    __disable_irq();
    count = fault_counter;
    __enable_irq();
    return count;
}
```

---

### 7. Volatile and Restricted Qualifiers

**Issue:** Volatility and restrictions ensure compiler respects hardware behavior and safety constraints.

**Applicable MISRA Rules:**
- **Rule 8.13**: Pass `const` for read-only function parameters
- **Rule 8.14**: Restrict use of `const` for type qualifiers (to prevent const-ness violations)
- **Rule 8.16**: Function parameters should be declared with named parameters (not variadic)
- **Rule 11.1**: Avoid casts that remove `const` or `volatile` qualifiers

**Safety Context:**
```c
// VIOLATION: Hardware register accessed without volatile, compiler may optimize reads
#define WDOG_KICK_ADDR ((volatile uint32_t *)0x40000000)
uint32_t read_once = *WDOG_KICK_ADDR;
uint32_t read_again = *WDOG_KICK_ADDR;
if (read_once != read_again) { ... }  // Optimization may elide second read

// COMPLIANT: Volatile keyword forces read each time, const for read-only
static volatile const uint32_t * const wdog_reg = (volatile uint32_t *)0x40000000;
uint32_t read_once = *wdog_reg;
uint32_t read_again = *wdog_reg;  // Guaranteed separate read
```

---

### 8. Indirect Function Calls

**Issue:** Function pointers introduce dynamic dispatch, complicating verification and enabling code injection attacks.

**Applicable MISRA Rules:**
- **Rule 16.2**: Functions should not call themselves (no recursion or via function pointers)
- **Rule 16.3**: External functions shall not call internal functions
- **Rule 17.1**: The features of the C standard library should not be used (e.g., qsort, bsearch via function pointers)
- **Rule 20.11**: Do not use standard library functions that call function pointers (e.g., signal, atexit)

**Safety Context:**
```c
// VIOLATION: Function pointer dispatch, non-verifiable call target
typedef void (*cmd_handler_t)(uint8_t *data);
static cmd_handler_t command_handlers[] = { cmd_start, cmd_stop, cmd_reset };

void dispatch_command(uint8_t cmd_id, uint8_t *data) {
    if (cmd_id < ARRAY_SIZE(command_handlers)) {
        (*command_handlers[cmd_id])(data);  // Call target not statically verifiable
    }
}

// COMPLIANT: Direct switch-case dispatch, fully verifiable
void dispatch_command(uint8_t cmd_id, uint8_t *data) {
    switch (cmd_id) {
        case CMD_START:
            cmd_start(data);
            break;
        case CMD_STOP:
            cmd_stop(data);
            break;
        case CMD_RESET:
            cmd_reset(data);
            break;
        default:
            // Error handling
            break;
    }
}
```

---

## ASIL-Based MISRA Strictness

### ASIL-A (Minimal Safety)
Recommended MISRA rules: Core + essential pointer rules
- Rule 8.13 (const parameters)
- Rule 9.2 (array bounds)
- Rule 14.2 (loop bounds)
- Rule 16.3 (no recursion)

### ASIL-B (Moderate Safety)
Recommended MISRA rules: All of ASIL-A + type safety
- Rule 10.1 (type compatibility)
- Rule 10.4 (same type operands)
- Rule 12.1 (no loss of precision)
- Rule 8.9 (static scope)

### ASIL-C (High Safety)
Recommended MISRA rules: All of ASIL-B + control flow + conversions
- Rule 14.3 (loop-invariant control)
- Rule 10.2, 10.3, 10.6 (all implicit conversions)
- Rule 2.2 (no unreachable code)
- Rule 8.5 (single declaration)

### ASIL-D (Highest Safety)
Recommended MISRA rules: All of ASIL-C + no indirect calls + global isolation
- Rule 16.2 (no indirect function calls)
- Rule 17.1 (no standard library function pointers)
- Rule 8.8, 8.10, 8.11 (linkage discipline)
- Rule 18.1, 18.2, 18.4 (pointer restrictions)

---

## Example: Diagnostic Flag Monitoring (SW-TSR Example)

**SW-TSR:** "The software shall sample the wheel speed sensor diagnostic flag every 10 ms, debounce with 5 consecutive samples, and command motor neutral within 100 ms."

**SW-SRs (derived):**

1. **TSR-001-SR-01:** Sampling and buffering
2. **TSR-001-SR-02:** Debounce counter and state machine
3. **TSR-001-SR-03:** Safe-state command

**Applicable MISRA Rules (ASIL-C):**

| SW-SR | MISRA Rule | Guidance | Verification |
|-------|-----------|----------|--------------|
| SR-01 | Rule 8.13 | Pass buffer pointer as `const` when reading | Code review: parameter list |
| SR-01 | Rule 9.2 | Buffer index `i` must be `i < BUFFER_SIZE` | Static analysis: loop bound checking |
| SR-01 | Rule 10.1 | Flag type (bool, uint8_t) must match comparison | Code review: type mismatch |
| SR-02 | Rule 14.2 | Debounce loop must have fixed iteration count (5 samples) | Code review: loop bounds |
| SR-02 | Rule 14.3 | Debounce counter must be loop-invariant (not modified inside loop body) | Static analysis: data flow |
| SR-02 | Rule 8.9 | Debounce state (counter) as static scope, not global | Code review: scope audit |
| SR-03 | Rule 16.1 | Safe-state command function has single exit point | Code review: control flow diagram |
| SR-03 | Rule 16.3 | No recursion in safe-state handler (ISR context) | Code review: call graph |
| SR-03 | Rule 12.1 | Timing calculation (e.g., countdown register) avoids overflow | Code review: arithmetic bounds |

---

## Quick Audit Checklist

Before code review of SW-SRs:

- [ ] No `malloc()`, `free()`, or `calloc()` (Rule 8.19)
- [ ] All function parameters that are read-only marked `const` (Rule 8.13)
- [ ] All variables initialized at declaration (Rule 9.1)
- [ ] All array accesses statically verifiable in bounds (Rule 9.2)
- [ ] No implicit type conversions (Rule 10.1, 10.2, 10.3)
- [ ] No unreachable code (Rule 2.2)
- [ ] All loops have static iteration bounds (Rule 14.2, 14.3)
- [ ] No function recursion (Rule 16.3)
- [ ] No function pointers (Rule 16.2)
- [ ] All global state is static scope + mutex/ISR protected (Rule 8.9, Rule 8.5)
- [ ] No unsafe casts removing `const` or `volatile` (Rule 11.1)
- [ ] All arithmetic checked for overflow (Rule 12.1)

---

## References

- **MISRA C:2012** — Guidelines for the use of the C language in critical systems (Motor Industry Software Reliability Association, 2012)
- **MISRA C:2012 Amendment 2** — Additional guidance on embedded systems (2018)
- **ISO 26262-6:2018** — Product development at the software level, Clause 7 (Implementation of software safety requirements)
- **AUTOSAR AP Release 4.x** — AUTOSAR Adaptive Platform, inherits MISRA C:2012
