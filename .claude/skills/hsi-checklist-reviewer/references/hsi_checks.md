# HSI Specification Checklist — Substantive Checks

## Confirmation Review (14 checks)

| ID | Requirement | Why | How Verified |
|----|-------------|-----|--------------|
| CR-1 | Document is structured in clear manner | Maintainability & understandability | Tab count ≥ 9; distinct sections present |
| CR-2 | Latest template was used on creation | Currency & completeness | Manual inspection (auto-skip) |
| CR-3 | Structure facilitates search (TOC, index) | Traceability & discoverability | TOC tab present + References tab present |
| CR-4a | Title covers the scope | Clarity of purpose | Title field populated; reviewer to verify scope |
| CR-4b | Author and approver(s) listed | Accountability & review trail | Both Author and Approver fields populated |
| CR-4c | Unique identification per revision | Version control | Revision field populated on Title page |
| CR-4d | Change history available | Traceability of edits | Document Control tab has ≥1 revision history row |
| CR-4e | Status of work product provided | Project state clarity | Status field populated (Draft/In Review/Released) |
| CR-5 | Current revision clearly identifiable | Avoids obsolescence | Current revision visibly marked |
| CR-6 | Document under CM | Configuration management | Manual verification (auto-skip) |
| CR-7 | Header and footer updated | Document identification | Manual inspection (auto-skip) |
| CR-8 | Table of contents present | Navigation & structure | TOC or Contents tab near start |
| CR-9 | Reference table lists all references | Traceability to standards | References tab present and populated |
| CR-10 | All sections completed | Completeness | Signal catalog ≥85% populated; timing/failure/test tabs populated |

## HSI Assessment (14 checks per ISO 26262-4/5)

### 1. HSI Signal Catalog Populated

**Requirement**: HSI signal catalog must contain all interface signals between HW and SW.

**Why**: Without enumeration of all signals, subsequent checks (direction, encoding, owner, protection, test cases) are impossible.

**Verification**: 
- ✓ FC: ≥5 signals detected in "02_HSI_Signal_Catalog" tab
- ✓ LC: 1–4 signals present; verify completeness
- ✗ NO: 0 signals; signal catalog is empty

**Recommended Action**: Populate the HSI Signal Catalog tab with all interface signals (inputs and outputs).

---

### 2. Signal Direction Specified

**Requirement**: Each signal must have direction defined (HW→SW, SW→HW, or bidirectional).

**Why**: Direction defines ownership boundaries and communication flow. Missing direction causes ambiguity in fault reaction assignment.

**Verification**:
- ✓ FC: ≥99% of signals have direction populated
- ✓ LC: 85–98% populated; minor gaps acceptable
- ✗ NO: <70% populated

**Recommended Action**: Specify HW→SW or SW→HW for each signal.

---

### 3. Bit Width / Encoding Specified

**Requirement**: Each signal must have data type and bit width (or encoding) specified.

**Why**: Encoding determines range, resolution, and interpretation. Required for timing budgets, test case design, and FIT calculations.

**Verification**:
- ✓ FC: All signals have bit_width AND data_type
- ✓ LC: ≥85% have encoding
- ✗ NO: <70% have encoding

**Recommended Action**: Populate Bit Width and Data Type columns for all signals.

---

### 4. Owner Identified

**Requirement**: Each signal must have owner (HW or SW) identified.

**Why**: Owner is responsible for signal quality, timing, and integrity. Ambiguity causes gaps in fault reaction design.

**Verification**:
- ✓ FC: All signals have owner (HW or SW)
- ✓ LC: ≥85% have owner
- ✗ NO: <70% have owner

**Recommended Action**: Identify owner for all signals.

---

### 5. Integrity Protection (Safety-Relevant Signals)

**Requirement**: Each safety-relevant signal (ASIL ≥ A) must have integrity protection mechanism.

**Why**: ISO 26262-5 §6.4.6.7 requires protection against undetected failures. Mechanisms: Parity, CRC, SECDED, Dual-channel.

**Verification**:
- ✓ FC: All ASIL≥A signals have integrity protection populated
- ✓ LC: ≥85% protected
- ✗ NO: <70% protected

**Recommended Action**: Specify Parity, CRC, SECDED, or Dual-channel for each safety-relevant signal.

---

### 6. Validity Bit / Liveness Counter

**Requirement**: Each safety-relevant signal must have validity bit or liveness counter.

**Why**: Detects signal absence or staleness. Required for timeout detection and asynchronous communication validation.

**Verification**:
- ✓ FC: All ASIL≥A signals have validity indicator
- ✓ LC: ≥85% have validity
- ✗ NO: <70% have validity

**Recommended Action**: Add validity bit or liveness counter for each safety-relevant signal.

---

### 7. FSR Traceability

**Requirement**: Each signal must be linked to a Functional Safety Requirement (FSR_ID).

**Why**: Traceability from safety goals → FSC → TSC → HSI. Missing links break the assurance chain.

**Verification**:
- ✓ FC: All signals have linked FSR_ID
- ✓ LC: ≥85% linked
- ✗ NO: <70% linked

**Recommended Action**: Link all signals to FSR identifiers for traceability.

---

### 8. Timing Specification

**Requirement**: Each signal must have timing specification: sample rate, max age, and latency budget.

**Why**: Timing determines real-time behavior, deadline miss fault rates, and achievability of safety mechanisms.

**Verification**:
- ✓ FC: ≥80% of signals covered in Timing Specification tab with all three timing attributes
- ✓ LC: ≥60% covered
- ✗ NO: <50% covered

**Recommended Action**: Populate Timing Specification tab with sample rate, max age, and latency budget per signal.

---

### 9. Failure Modes Documented

**Requirement**: Each signal must have failure modes identified (stuck high/low, timeout, corruption, etc.).

**Why**: Failure mode enumeration is the foundation for test case design and fault reaction specification.

**Verification**:
- ✓ FC: ≥80% of signals have failure mode rows
- ✓ LC: ≥60% have failure modes
- ✗ NO: <50% have failure modes

**Recommended Action**: Enumerate failure modes for all signals in Failure Modes & Reactions tab.

---

### 10. SW Reaction Specified

**Requirement**: Each failure mode must have corresponding SW reaction (detection, handling, safe state transition).

**Why**: Reaction specification closes the loop from detection to safe state. Missing reactions leave hazards unmitigated.

**Verification**:
- ✓ FC: ≥95% of failure mode rows have reaction populated
- ✓ LC: ≥80% have reactions
- ✗ NO: <70% have reactions

**Recommended Action**: Specify SW reaction for all failure modes (error handling, logging, safe state entry).

---

### 11. Initialization Sequence

**Requirement**: Initialization sequence must be documented (HW BIST, SW startup checks).

**Why**: Initialization is the first touchpoint for safety. Missing sequence documentation is a major gap.

**Verification**:
- ✓ FC: Initialization Sequence tab present with documented HW BIST + SW startup checks
- ✗ NO: No Initialization Sequence tab

**Recommended Action**: Add Initialization Sequence tab documenting HW BIST procedures and SW startup validation.

---

### 12. Cross-Reference Table

**Requirement**: Cross-reference table must cover all signals with no orphans.

**Why**: Cross-reference ensures traceability between signal catalog, register map, timing, test cases, and failure modes. Orphans are undocumented signals.

**Verification**:
- ✓ FC: Cross-Reference tab present; all signals listed
- ✗ NO: No Cross-Reference tab or significant gaps

**Recommended Action**: Add Cross-Reference tab ensuring every signal in catalog appears in all subsequent tabs.

---

### 13. Test Cases Defined

**Requirement**: Test cases must be defined per signal (nominal, fault injection, boundary, timing).

**Why**: Test cases are the evidence that HSI works as specified. Missing test cases are a major gap in verification.

**Verification**:
- ✓ FC: ≥80% of signals have test cases covering nominal, fault, boundary, and timing scenarios
- ✓ LC: ≥60% have test cases
- ✗ NO: <50% have test cases

**Recommended Action**: Define test cases for all signals covering nominal operation, fault injection (stuck high/low, timeout, corruption), boundary values, and timing edge cases.

---

### 14. ASIL Allocation

**Requirement**: ASIL must be allocated to each safety-relevant signal.

**Why**: ASIL drives verification stringency, protection mechanism selection, and independence level. Missing allocation leaves safety level undefined.

**Verification**:
- ✓ FC: All safety-relevant signals (identified via traceability from FSC) have ASIL (A, B, C, or D)
- ✓ LC: ≥85% have ASIL
- ✗ NO: <70% have ASIL

**Recommended Action**: Allocate ASIL to each safety-relevant signal based on FSC and traceability.

---

## Verification Assessment (5 HSI-Specific Checks)

| ID | Requirement | Why | Verification |
|----|-------------|-----|--------------|
| VA-1 | Register map completeness | MCU memory layout coverage | Manual review against architecture; typically ≥8 registers |
| VA-2 | Timing budget adequacy | Latencies must be achievable | Manual review against system architecture & MCU datasheet |
| VA-3 | Consistency with HW architecture | Alignment with design | Cross-reference with architecture document (external) |
| VA-4 | Integrity mechanisms verified | Protection adequacy | Cross-reference with TSC test cases and safety mechanisms |
| VA-5 | Diagnostics strategy | Fault detection & reaction completeness | Cross-reference with FTA, safety mechanisms, and DIA |

---

## Scoring Examples

### Example 1: Largely Compliant Signal Catalog (LC)

**Check**: HSIA #2 (Signal Direction)

Signal catalog has 42 signals.
- 40 signals have direction specified
- 2 signals have blank direction field

**Calculation**: 40/42 = 95.2%

**Result**: ✓ LC (> 85% but < 99%)

**Recommended Action**: "Specify direction for the 2 remaining signals: SignalX (currently blank) and SignalY (currently blank)."

---

### Example 2: Partially Compliant Failure Modes (PC)

**Check**: HSIA #9 (Failure Modes Documented)

Signal catalog has 42 signals.
Failure Modes & Reactions tab has 18 rows.

**Calculation**: 18/42 = 42.9% coverage

**Result**: ✗ PC (< 70%)

**Recommended Action**: "Document failure modes for 24 additional signals. Current coverage: 18/42 signals (43%). Target: ≥80%."

---

### Example 3: Fully Compliant Integrity Protection (FC)

**Check**: HSIA #5 (Integrity Protection)

Safety-relevant signals (ASIL ≥ A): 8 signals
All 8 have integrity_protection field populated (values: "CRC", "SECDED", "Parity", etc.)

**Result**: ✓ FC

**Finding**: "All 8 safety-relevant signals have integrity protection specified (CRC: 3, SECDED: 4, Parity: 1)."

---

## Key Metrics for Success

| Metric | Target | Threshold for Acceptance |
|--------|--------|--------------------------|
| Overall Compliance % | ≥90% | ≥70% |
| Signal Catalog Completeness | ≥95% | ≥85% |
| Safety-Relevant Signal Coverage | 100% | ≥90% |
| Test Case Coverage | ≥80% of signals | ≥60% of signals |
| NO Findings (major) | 0 | ≤1 (with mitigation) |
| Pending Items | 0 | ≤20% (with reviewer decision) |

---

## Reference

- ISO 26262-4:2018 §6.4.6 — HSI specification requirements
- ISO 26262-5:2018 §6.4.6 — Integrity protection and signal validation
- ISO 26262-8:2018 §7 & §10 — Confirmation measures and verification
