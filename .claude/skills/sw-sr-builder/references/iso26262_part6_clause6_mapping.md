# ISO 26262-6 Clause 6 Mapping — SW-SR Workbook

## Overview

ISO 26262-6:2018 **Part 6: Product development at the software level** specifies requirements for software safety specification (Clause 6) and implementation (Clause 7). This mapping document traces how each tab in the SW-SR workbook satisfies the obligations of Clause 6.

---

## ISO 26262-6:2018, Clause 6 Requirements

### Clause 6.1 General Requirements
> "The software safety requirements shall be specified for the software level in order to ensure correct behavior of the system and the software."

**Workbook Implementation:**
- **Tab 00 (Title Page)**: Establishes context and traceability to TSC
- **Tab 03 (SW Safety Requirements)**: Primary specification of SW-SRs per TSR

### Clause 6.2 Specification of Software Safety Requirements
> "The specification of software safety requirements shall include:
> 
> a) the software safety requirements for each technical safety requirement;
> b) assignment of ASILs;
> c) interfaces to safety-critical functions;
> d) required coverage of software verification and validation methods;
> e) resource and scheduling constraints;
> f) safety-related documentation."

**Workbook Mapping:**

| Clause 6.2 Item | Workbook Tab(s) | Content |
|-----------------|-----------------|---------|
| (a) SW-SRs per TSR | Tab 02 (SW-TSRs), Tab 03 (SW-SRs) | Parent TSR and derived SW-SRs with full text |
| (b) ASIL assignment | Tab 03 (ASIL column), Tab 06 (Verification Methods per ASIL) | ASIL inherited from parent SW-TSR, propagated through verification |
| (c) Interfaces | Tab 05 (HSI Reference) | Signals consumed/produced, encoding, update rate, integrity |
| (d) Verification coverage | Tab 06 (Verification Methods per ASIL), Tab 08 (Test Strategy) | Methods per ASIL per ISO 26262-6 Tables 7–10; test categories |
| (e) Resource/scheduling | Tab 03 (Detection Time), Tab 08 (Test Strategy), Tab 09 (Independence) | Detection time budgets; task scheduling independence; decomposition evidence |
| (f) Safety documentation | Tab 10 (References), Tab 01 (Document Control) | Traceability to TSC, standards, and revision history |

---

## Tab-by-Tab Mapping

### Tab 00: Title Page
**ISO 26262-6:2018 Clause 6.2(f) — Safety-Related Documentation**

```
Requirement: "The specification of software safety requirements shall include 
             safety-related documentation."

Evidence:    - Project metadata (doc ID, revision, date, author, approver)
             - Linked TSC (source of truth for SW-TSRs)
             - Methodology statement (per-SW-TSR derivation approach)
             - Standard reference (ISO 26262-6, Clause 6)
```

### Tab 01: Document Control
**ISO 26262:2018 Part 8, Clause 5 (Functional Safety Management — Document Management)**

```
Requirement: "A document management process shall be implemented to manage 
             safety-related documents and to maintain the configuration of 
             the product during its lifetime."

Evidence:    - Revision history with dates, descriptions, and approvers
             - Traceability to source TSC version
             - Change log supporting audit trail
```

### Tab 02: SW-TSRs from TSC
**ISO 26262-6:2018 Clause 6.2(a) — Software Safety Requirements per TSR**

```
Requirement: "The software safety requirements shall be specified for 
             the software level in order to ensure correct behavior."

Evidence:    - Imported SW-TSRs from TSC (tsr_id, fsr_id, mechanism, text)
             - ASIL allocation inherited from TSC
             - Read-only echo ensures traceability back to source TSC
             - Failure modes addressed by each SW-TSR
```

**Verification:** Check that TSC version matches linked_tsc in project metadata.

### Tab 03: SW Safety Requirements
**ISO 26262-6:2018 Clause 6.2(a), (b), (c), (e) — Core SW-SR Specification**

```
Requirement: "The software safety requirements shall be specified... assignment 
             of ASILs... interfaces to safety-critical functions... resource 
             and scheduling constraints."

Evidence:    - SW-SR_ID: Unique identification per SW-TSR
             - Parent SW-TSR: Traceability to source technical requirement
             - ASIL: Propagated from TSR (color-coded per ISO convention)
             - Allocated SW Component: Specific task/module/function name
             - Requirement Text: Concrete, testable, implementation-independent
             - Addressed Failure Modes: Maps to Tab 04 (Failure Mode Mapping)
             - Target Detection Time: FDTI/FRTI allocation, justification in review
             - Verification Method: Cross-reference to Tab 06
```

**Verification:** 
- Each SW-SR must reference exactly one parent SW-TSR
- Allocated SW component must be resolvable in detailed software design
- Detection time must align with timing budget (sum across all SW-SRs ≤ FTTI)
- Verification method must match ASIL (from Tab 06)

### Tab 04: Failure Mode Mapping
**ISO 26262-6:2018 Clause 6.2(a) — Failure Mode Coverage**

```
Requirement: "The software safety requirements shall be specified to address 
             failure modes and their detection."

Evidence:    - Rows: Individual SW-SRs
             - Columns: Standard failure modes (deadline miss, illegal state, 
                       divide-by-zero, stack overflow, mutex deadlock, ECC error, 
                       message loss, etc.)
             - Marks (X): SW-SR explicitly addresses that failure mode
             - Coverage analysis: Identify any unaddressed failure modes requiring 
                                 additional SW-SRs or architectural changes
```

**Verification:**
- [ ] All identified failure modes are marked against at least one SW-SR
- [ ] No SW-SRs are dangling (each row has at least one mark)
- [ ] Failure mode categories align with software subsystem types (monitoring, control, communication, memory, diagnostic)

### Tab 05: HSI Reference
**ISO 26262-6:2018 Clause 6.2(c) — Interfaces to Safety-Critical Functions**

```
Requirement: "The software safety requirements shall include... interfaces 
             to safety-critical functions [and HSI signals]."

Evidence:    - SW-SR_ID: Traceability to source requirement
             - Signal Direction: Input (sensor data), Output (control command), 
                               or Diagnostic (flag/status)
             - HSI Signal Name: From TSC 06_HSI_Specification (e.g., esc.sw.diag_flag_01)
             - Encoding: Binary, multi-bit, integer, IEEE float, CAN message, etc.
             - Update Rate: Frequency of signal availability (ms or cycle-based)
             - Integrity Protection: Parity, CRC, Timestamp, ECC, E2E protection
```

**Verification:**
- [ ] All input signals have encoding and update rate specified
- [ ] All output signals have integrity protection specified
- [ ] Signal names match HSI Specification tab in source TSC
- [ ] Update rates are consistent with detection time targets

### Tab 06: Verification Methods per ASIL
**ISO 26262-6:2018 Clause 6.2(d) — Required Coverage of Verification Methods**

```
Requirement: "The specification of software safety requirements shall 
             include required coverage of software verification and 
             validation methods."

Evidence:    - SW-SR_ID: Traceability
             - ASIL: Allocated ASIL (determines mandatory methods per Table 7-10)
             - Methods: Review/Walkthrough, Static Analysis, Control Flow Analysis, 
                       Data Flow Analysis, MC/DC, Fault Injection
             - Marks: ++ = strongly recommended; + = acceptable supplementary

Methods per ASIL (ISO 26262-6 Tables 7-10):
  ASIL-A:  Review/Inspection (++)
  ASIL-B:  Review (++), Static analysis (+)
  ASIL-C:  Review (++), Static analysis (++), Control/Data flow (++), MC/DC (+)
  ASIL-D:  Review (++), Static analysis (++), Control/Data flow (++), 
           MC/DC (++), Fault injection (++)
```

**Verification:**
- [ ] Every SW-SR has at least one method marked per allocated ASIL
- [ ] All ++ methods are included in test plan (not deferred)
- [ ] Justification exists for any omitted ++ method (with risk assessment)
- [ ] Methods are mapped to specific test cases / code review sections in detailed design

### Tab 07: MISRA Mapping
**ISO 26262-6:2018 Clause 7.2 (Implementation) — Coding Standards**

```
Requirement: "The software shall be implemented in a way that is consistent 
             with the software architectural design and the software safety 
             requirements. MISRA C:2012 is commonly applied."

Evidence:    - SW-SR_ID: Traceability
             - MISRA Category: Rule group (e.g., "No dynamic memory", 
                             "No function pointers", "Bounded loops")
             - Applicable Rules: Specific rule IDs (e.g., Rule 8.13, Rule 10.1)
             - Notes: Implementation guidance, exceptions, justifications
```

**Verification:**
- [ ] MISRA rules are resolvable and implementable (not conflicting)
- [ ] Rule selection justifies ASIL (stricter rules for ASIL-D vs. ASIL-A)
- [ ] Code review checklist includes MISRA rule verification per Tab 07

### Tab 08: Test Strategy
**ISO 26262-6:2018 Clause 6.2(d) and 7.3 (V&V) — Verification Methods at V&V Level**

```
Requirement: "The software shall be verified to ensure that the software 
             safety requirements have been met. V&V activities shall include 
             unit testing, integration testing, system testing, and functional 
             safety verification."

Evidence:    - Test Category: Unit test (gtest/cmocka), Integration (HIL/SIL), 
                            Back-to-back, Fault injection, Requirements coverage
             - Description: Purpose and scope of each test category
             - Applicable SW-SRs: Which SRs each category addresses
             - Test Specification: Reference to test plan / test case ID
             - Acceptance Criteria: Pass/fail metrics (coverage %, error detection rate)
             - Owner: Responsibility assignment for execution and reporting
```

**Verification:**
- [ ] Each SW-SR is covered by at least one test category
- [ ] Unit tests verify individual functions / components
- [ ] Integration tests verify inter-task communication and timing
- [ ] Back-to-back tests verify implementation vs. reference model (floating point, rounding, etc.)
- [ ] Fault injection tests verify error detection and handling (deadline, ECC, deadlock, etc.)
- [ ] Requirements coverage achieves traceability (100% of SW-SRs → test cases)

### Tab 09: Independence Considerations
**ISO 26262-9:2018 Clause 7 (Dependent Failure Analysis) — Independence for Decomposition**

```
Requirement: "When ASIL decomposition is applied, independence between 
             decomposed channels or components shall be demonstrated at 
             the software level."

Evidence:    - Decomposition Pair: e.g., "Channel A vs. Channel B" or 
                                "SG_Main vs. SG_Redundant"
             - Coupling Factor: Shared resource (compilation unit, memory, task, 
                               interrupt, toolchain, team)
             - Coupling Present: Yes/No analysis
             - Mitigation: How independence is achieved (separate .c file, 
                          separate RAM block, separate code review)
             - Evidence: Documentation, static analysis, FMEDA row reference
             - Status: Verified/Pending/At Risk
```

**Verification:**
- [ ] All decomposition pairs from TSC are listed
- [ ] All coupling factors from ISO 26262-9 Clause 7 are considered
- [ ] Mitigations are concrete and verifiable (not "reviewed by different team")
- [ ] Evidence (code review checklist, static analysis rules, FMEDA) is cross-referenced
- [ ] No coupling present in any factor, or mitigations are proven effective

### Tab 10: References
**ISO 26262:2018 General — Traceability and Baseline Control**

```
Requirement: "All work products shall be traceable to source requirements 
             and upstream standards."

Evidence:    - Linked TSC: Version/date of source TSC workbook
             - ISO 26262-6:2018: Citation of standard clauses
             - ISO 26262-9:2018: Citation for independence requirements
             - MISRA C:2012: Citation of coding standards
             - Additional references: Project-specific standards, guidelines, tools
```

**Verification:**
- [ ] Linked TSC version is current and matches project baseline
- [ ] All standards are current (2018 edition or later for ISO 26262)
- [ ] Reference URLs / document paths are valid and accessible
- [ ] Change history documented when references are updated

---

## Cross-Functional Traceability Matrix

```
FSR (from HARA → FSC)
    ↓
FSC → ASIL allocation + decomposition
    ↓
TSC → TSR Catalog (HW-TSRs, SW-TSRs)
    ↓
    ├─→ HW-SRs (hw-safety-reqs-builder)
    └─→ SW-SRs ← *This workbook*
            ↓
        Detailed SW Design
            ↓
        Code Review (per Tab 07 MISRA)
            ↓
        Unit Test (per Tab 08)
            ↓
        Integration Test (per Tab 08)
            ↓
        Fault Injection Test (per Tab 08)
            ↓
        Requirements Coverage (per Tab 08)
            ↓
        Functional Safety Verification Report
            ↓
        ISO 26262 Audit
```

---

## Quality Assurance Checklist

Before releasing SW-SR workbook:

### Content Completeness
- [ ] All SW-TSRs from Tab 02 have corresponding SW-SRs in Tab 03
- [ ] All SW-SRs have parent TSR, allocated component, and detection time
- [ ] All failure modes in Tab 04 are addressed by at least one SW-SR
- [ ] All HSI signals in Tab 05 are reconciled with TSC HSI Specification
- [ ] All verification methods in Tab 06 match ASIL requirements (ISO 26262-6 Tables 7-10)
- [ ] All MISRA rules in Tab 07 are applicable and non-conflicting
- [ ] All SW-SRs are covered by test strategy in Tab 08
- [ ] All decomposition pairs have independence evidence in Tab 09

### Traceability
- [ ] Backward traceability: Each SW-SR traces to exactly one SW-TSR
- [ ] Forward traceability: Each SW-SR is allocatable to a software component
- [ ] Requirement status: No orphaned or dangling SW-SRs
- [ ] Version control: Document control (Tab 01) is current

### Formality
- [ ] All text is passive voice, declarative ("shall", not "should")
- [ ] All requirements are testable (not vague or aspirational)
- [ ] All "<TBD>" fields are resolved in review
- [ ] No conflicting requirements within or across tabs

### Risk Management
- [ ] High-risk SW-SRs (ASIL-C, ASIL-D) have detailed verification methods
- [ ] Fault injection coverage identified for all diagnostic SW-SRs
- [ ] Independence evidence strong for all decomposed components
- [ ] All high-complexity SW-SRs (e.g., state machines, scheduling) have code review plans

---

## References

- **ISO 26262-6:2018** — Product development at the software level, Clause 6 (Specification of software safety requirements)
- **ISO 26262-6:2018** — Product development at the software level, Clause 7 (Implementation of software safety requirements)
- **ISO 26262-9:2018** — Functional Safety Management, Clause 7 (Dependent failure analysis)
- **MISRA C:2012** — Guidelines for the use of the C language in critical systems
