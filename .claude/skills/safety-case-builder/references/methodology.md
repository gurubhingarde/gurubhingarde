# Safety Case Methodology — ISO 26262-2 Section 6

## What is a Safety Case?

A Safety Case is the structured argument and supporting evidence that the item is acceptably safe for its intended use within the defined operational context. Per ISO 26262-2:6, it is the capstone deliverable of the concept phase, integrating all evidence from the hazard analysis, functional safety concept, technical safety concept, hardware design, software design, verification, and confirmation activities into a single coherent argument that can withstand independent assessment.

## Structure: Goal Structuring Notation (GSN)

The Safety Case is organized using Goal Structuring Notation (GSN), a visual and textual convention for expressing safety arguments. The key elements are:

### Top-Level Claim (Goal G1)

**Claim:** "The item is acceptably safe for its intended use within the defined operational context."

**Context:**
- Vehicle program (e.g., "Mid-Size Sedan 2027")
- Target ASIL (e.g., "D")
- Operational scope (driving modes, speed ranges, terrain)

**Justifications:**
- HARA identifies all hazards and derives safety goals
- FSC allocates safety goals to functional and technical measures
- TSC refines to HW and SW technical requirements
- Verification and validation confirm all requirements met
- Confirmation reviews ensure development process integrity

### Sub-Claims (Goals G2.x) — One Per Safety Goal

For each safety goal SG-i:

**Claim:** "Safety Goal SG-i is satisfied."

**Context:**
- Hazard or set of hazards that SG-i addresses
- ASIL allocated to SG-i
- Operational scenario and severity rating

**Strategy:**
- "By demonstrating that all Functional Safety Requirements (FSRs) derived from SG-i are implemented and verified"

**Evidence:** Links to FSC, TSC, FMEDA, test reports demonstrating each FSR is met.

### Strategies (Sn.x) — How Claims are Supported

Each claim is argued through one or more strategies. For the top claim:

1. **S1.1:** Demonstrate that the HARA is complete and all hazards are addressed by safety goals
   - Evidence: HARA workbook, confirmation review record

2. **S1.2:** Demonstrate that FSC safety goal allocations are adequate and decompositions are justified
   - Evidence: FSC workbook, decomposition arguments, DFA analyses, confirmation review

3. **S1.3:** Demonstrate that TSC technical requirements (TSRs) are adequate for each FSR
   - Evidence: TSC workbook, traceability matrix (FSR→TSR), confirmation review

4. **S1.4:** Demonstrate that HW and SW implementations meet their respective TSRs
   - Evidence: FMEDA (HW metrics), SW test reports (coverage, MISRA compliance), confirmation review

5. **S1.5:** Demonstrate that all development processes were followed per the Safety Plan
   - Evidence: Confirmation review records, tool qualification, V&V status

### Evidence (En.x.y) — Artifacts and Test Reports

Each strategy is supported by evidence:

- **E1:** HARA workbook: Safety goals (SG-001, …, SG-n) with hazards, ASIL, FTTI
- **E2:** FSC workbook: Functional Safety Requirements (FSR-001, …, FSR-m) with allocations, decomposition arguments, DFA
- **E3:** TSC workbook: Technical Safety Requirements (TSR-HW-*, TSR-SW-*) with mechanisms, traceability, timing budgets
- **E4:** FMEDA workbook: HW failure modes with diagnostic coverage, SPFM/LFM/PMHF metrics
- **E5:** SW verification reports: Code coverage (statement, branch, MC/DC), MISRA compliance, test results
- **E6:** Confirmation review records: Independent reviews of HARA, FSC, TSC, HW design, SW design, V&V
- **E7:** Tool qualification records: Justification of tool TCL classifications per ISO 26262-8

## Traceability Model

The Safety Case traces evidence from top to bottom:

```
Top Claim (Item is acceptably safe)
  ↓
Sub-Claim per SG (SG-001, …, SG-n are satisfied)
  ↓
FSRs allocated to each SG (FSR-001, …, FSR-m)
  ↓
TSRs allocated to each FSR (TSR-HW-*, TSR-SW-*)
  ↓
Mechanisms (E2E, lockstep, watchdog, …) with DC%
  ↓
HW/SW designs + FMEDA metrics + test results
```

Every row in the safety case (one per SG, or one per FSR) must be traceable downward to evidence (test report, FMEDA metric, diagnostic coverage, code coverage) and upward to the top claim.

## Confirmation Reviews

Per ISO 26262-4 Section 5, confirmation reviews are independence-based checks at each major phase:

- **I1 (Least stringent):** Reviewed by a different person within the same team
- **I2 (Medium):** Reviewed by someone from a different functional area (e.g., independent safety consultant)
- **I3 (Most stringent):** Reviewed by external third party or notified body

For ASIL D items, confirmation reviews are mandatory at:
1. HARA completion (typically I2)
2. FSC completion (typically I2)
3. TSC completion (typically I2)
4. HW design and FMEDA (typically I2)
5. SW design and verification (typically I2)

The Safety Case tab "Confirmation Reviews Status" lists every review, reviewer, independence level, and completion date. Missing reviews or insufficient independence is a compliance gap.

## Decomposition Justification

When a single safety requirement is decomposed into multiple independent sub-requirements (e.g., one SG allocated to two nodes with different mechanisms), the Safety Case must document:

1. **Decomposition strategy:** e.g., "Dual-core lockstep monitors processor; watchdog monitors software."
2. **Dependent Failure Analysis (DFA):** A checklist verifying that no shared failure mode can violate both requirements simultaneously (e.g., no shared supply, no shared clock, no shared compiler).
3. **Confirmation review:** DFA results reviewed and approved.

Unmitigated coupling factors invalidate the decomposition; the requirement must revert to full inheritance (single ASIL D mechanism).

## Open Items and Residual Risks

At the time of assessment, there may be outstanding work (e.g., integration testing not yet complete). The Safety Case documents these as:

- **Open Items:** Work in progress with a target completion date and assigned owner
- **Residual Risks:** Known failure modes or design choices accepted with documented justification (e.g., "Minor diagnostic latency, acceptable per FMEDA sensitivity analysis")

Each open item must have:
- Clear description
- Risk level (Critical/High/Medium/Low)
- Owner and due date
- Justification (if residual risk)

An open item that blocks compliance cannot be released. A residual risk must be accepted by a senior stakeholder (FSM, Project Manager) and documented.

## Assessment Readiness Checklist

Before submitting the Safety Case for formal assessment:

1. All 15 tabs are complete and consistent
2. HARA, FSC, TSC, FMEDA, and test reports are the latest versions and linked correctly
3. Every SG has at least one FSR and one mechanism
4. Every FSR is traced to at least one TSR and one test result
5. FMEDA metrics (SPFM, LFM, PMHF) meet target ASIL thresholds
6. Confirmation reviews for all major phases are complete and documented
7. DFA analyses for all decompositions are complete and unmitigated
8. Open items are minimal (none blocking) and have documented justification
9. Signoff blocks are filled (FSM, Project Manager, Assessor)
10. Document Control revision is marked `1.0` and document is locked for baseline

Once these checks pass, the Safety Case is ready for submission to the OEM, Notified Body, or functional safety assessor.
