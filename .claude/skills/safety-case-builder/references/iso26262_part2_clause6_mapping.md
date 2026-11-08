# ISO 26262-2 Clause 6 — Safety Case Mapping

This document maps the 15 output tabs of the safety-case-builder skill to the specific requirements of ISO 26262-2:2018 Section 6 (Safety case).

## ISO 26262-2:6 Structure

ISO 26262-2 Section 6 defines the Safety Case requirements for the concept phase:

**6.2 – General**: The Safety Case shall provide a structured argument that the item is acceptably safe for its intended use.

**6.3 – Content**: The Safety Case shall include:
- An argument structure (GSN-compliant)
- All evidence from the HARA, FSC, TSC, V&V, confirmation activities
- Traceability from requirements to verification
- Assumptions and justifications
- Confirmation review records

**6.4 – Review and assessment**: The Safety Case shall be reviewed for completeness and assessed against the Safety Plan.

## Tab-to-Clause Mapping

| Tab # | Tab Name | Clause 6 Requirement | Content |
|-------|----------|----------------------|---------|
| 00 | Title_Page | 6.2 (Identity & Scope) | Project metadata, document ID, revision, company, vehicle program, target ASIL |
| 01 | Document_Control | 6.2 (Configuration Management) | Revision history, approval signatures, distribution list |
| 02 | Executive_Summary | 6.3.1 (High-Level Assertion) | Compliance statement: "Item is acceptably safe to ASIL X per ISO 26262" |
| 03 | Item_Definition_Reference | 6.3.2 (Operational Context) | Links to Item Definition; reiterates scope, boundary conditions, operational scenarios |
| 04 | Top_Claim | 6.3.3 (Top-Level Goal) | GSN Goal G1; claim that item is acceptably safe; context, justifications, assumptions |
| 05 | Safety_Goals_Argument | 6.3.4 (Sub-Claims) | GSN Goals G2.x (one per SG); strategy and evidence summary for each SG |
| 06 | FSR_TSR_Traceability | 6.3.5 (Requirements Traceability) | SG→FSR→TSR→mechanism→DC%→verification matrix; demonstrates allocation chain |
| 07 | HW_Metrics_Summary | 6.3.6 (HW Evidence) | SPFM, LFM, PMHF per SG from FMEDA; shows compliance with ASIL targets |
| 08 | SW_Verification_Summary | 6.3.6 (SW Evidence) | SW-TSR verification status; code coverage (statement, branch, MC/DC), MISRA compliance |
| 09 | Tool_Qualification | 6.3.7 (Process Evidence) | Tools used in development/verification; TCL classification per ISO 26262-8 Section 11 |
| 10 | Confirmation_Reviews_Status | 6.3.8 (Confirmation Activities) | Every confirmation review (work product, reviewer, independence level, date, status) |
| 11 | Open_Items_Risks | 6.3.9 (Residual Risks) | Outstanding actions and residual risks; owner, due date, justification for each |
| 12 | Argument_Diagram_Notes | 6.3.3-6.3.5 (Argument Structure) | Text-based GSN argument tree; claims, strategies, evidence pointers in hierarchical form |
| 13 | Assessment_Conclusion | 6.4 (Final Assessment) | Final compliance statement; signoff blocks for FSM, Project Manager, Assessor |
| 14 | References | 6.3 (Evidence Catalog) | All upstream artifacts (HARA, FSC, TSC, FMEDA, etc.) with paths, versions, standards |

## Detailed Requirements

### Tab 00 — Title_Page (Clause 6.2 — Identification)

**ISO Requirement 6.2.2:** "The safety case shall be identified by project, document ID, revision, date, and author."

**Fields to complete:**
- Project name (e.g., "Mid-Size Sedan 2027")
- Item name (e.g., "Electronic Stability Control ECU")
- Document ID (e.g., "SC-ESC-2026-001")
- Revision (e.g., "1.0")
- Date of issue
- Author / FSM name
- Target ASIL (e.g., "D")

### Tab 02 — Executive_Summary (Clause 6.3.1 — High-Level Assertion)

**ISO Requirement 6.3.1:** "The safety case shall include a high-level statement asserting that the item is acceptably safe."

**Key statement template:**
"The [item name] has been developed in accordance with ISO 26262:2018 to ASIL [X]. All safety goals derived in the HARA are allocated to functional safety measures (FSC), refined to technical measures (TSC), and verified by [mechanism type]. Confirmation reviews are complete. The item is acceptably safe for integration into the [vehicle program]."

### Tabs 04–05 — Top_Claim & Safety_Goals_Argument (Clause 6.3.3-6.3.4 — Argument Structure)

**ISO Requirement 6.3.3:** "The safety case shall be structured as a goal-strategy-evidence hierarchy per Goal Structuring Notation or equivalent."

**GSN structure in safety-case-builder:**

```
Goal G1 (Top Claim): Item is acceptably safe
  ├─ Strategy S1.1: Demonstrate HARA completeness
  │  └─ Evidence E1: HARA workbook
  ├─ Strategy S1.2: Demonstrate FSC adequacy
  │  └─ Evidence E2: FSC workbook with DFA
  ├─ Strategy S1.3: Demonstrate TSC adequacy
  │  └─ Evidence E3: TSC workbook with mechanisms
  ├─ Strategy S1.4: Demonstrate HW/SW verification
  │  ├─ Evidence E4: FMEDA metrics
  │  ├─ Evidence E5: SW test reports
  │  └─ Evidence E6: Confirmation reviews
  └─ Strategy S1.5: Demonstrate process integrity
     └─ Evidence E7: Tool qualification records

[Sub-Goals G2.x — one per SG]
G2.1 (SG-001): Safety Goal is satisfied
  ├─ Strategy: By demonstrating all FSRs from SG-001 are verified
  └─ Evidence: FSC row for SG-001, TSC rows for linked FSRs, test reports
```

### Tab 06 — FSR_TSR_Traceability (Clause 6.3.5 — Requirements Traceability)

**ISO Requirement 6.3.5:** "The safety case shall demonstrate traceability from each safety goal to its allocated functional safety requirements, technical requirements, and verification evidence."

**Traceability chain:**
```
SG → FSR → TSR → Mechanism → DC% → Test Report → Completion Status
```

Every row in this tab is a link in the chain. A broken link (e.g., FSR without corresponding TSR) is a compliance gap.

### Tabs 07–08 — HW/SW Metrics (Clause 6.3.6 — Evidence Quality)

**ISO Requirement 6.3.6a (Hardware):** "For ASIL C/D items, the safety case shall include FMEDA-based metrics (SPFM, LFM, PMHF) meeting the target thresholds."

**Targets per ASIL:**
- ASIL A: SPFM >= 90%, LFM >= 60%
- ASIL B: SPFM >= 90%, LFM >= 60%
- ASIL C: SPFM >= 97%, LFM >= 80%
- ASIL D: SPFM >= 99%, LFM >= 90%, PMHF < 10 FIT (for many systems)

**ISO Requirement 6.3.6b (Software):** "For ASIL C/D items, the safety case shall include code coverage (structural and/or functional) and MISRA C compliance evidence."

**Targets per ASIL:**
- ASIL A: Statement coverage >= 80%
- ASIL B: Branch coverage >= 85%
- ASIL C: Branch coverage >= 95%
- ASIL D: MC/DC coverage >= 90% for critical logic, branch >= 95% overall, MISRA C:2012 compliance

### Tab 09 — Tool_Qualification (Clause 6.3.7 — Process Evidence)

**ISO Requirement 6.3.7:** "The safety case shall identify all tools used in the development and verification lifecycle and justify their tool confidence level (TCL) per ISO 26262-8 Section 11."

**Tool Confidence Levels (ISO 26262-8:11):**
- **QM:** Qualification not required (e.g., office software, documentation tools)
- **T1:** Potential for introducing errors (e.g., code generator without full coverage). Justification: tool manual + supplier data
- **T2:** Potential to detect errors but not with high confidence (e.g., compilers). Justification: TCL1 + qualification measures
- **T3:** Potential to not detect errors (e.g., advanced optimizing compiler, IDE). Justification: TCL2 + formal analysis + independent testing

Every tool in Tab 09 must have documented justification.

### Tab 10 — Confirmation_Reviews_Status (Clause 6.3.8 — Confirmation Activities)

**ISO Requirement 6.3.8:** "The safety case shall document confirmation reviews of all major work products per the Safety Plan, with evidence of reviewer independence."

**Independence levels per ISO 26262-4:5:**
- **I1:** Different person, same team
- **I2:** Different functional area (e.g., independent safety consultant for a concept-phase review)
- **I3:** External third party (notified body, accredited lab)

**Minimum confirmations for ASIL D:**
1. HARA completion: I2 minimum
2. FSC completion: I2 minimum
3. TSC completion: I2 minimum
4. HW design & FMEDA: I2 minimum
5. SW design & verification: I2 minimum

Missing any confirmation is a non-compliance.

### Tab 11 — Open_Items_Risks (Clause 6.3.9 — Residual Risks)

**ISO Requirement 6.3.9:** "The safety case shall document any residual risks or open items at the time of assessment, with justification and management plan."

**Each open item must include:**
- ID and clear description
- Risk level (Critical/High/Medium/Low)
- Owner and target completion date
- Justification (why it is acceptable to release despite the open item)

**Example:**
- "OI-001: SW verification coverage data pending integration test (Low risk). Owner: Alice Brown. Due: 2026-05-15. Justification: Preliminary HIL testing shows 97% statement coverage; integration test adds only final E2E validation and is not on critical path."

A **Critical** risk cannot block release; it must be escalated to the functional safety manager.

### Tab 12 — Argument_Diagram_Notes (Clause 6.3.3 — Argument Clarity)

**ISO Requirement 6.3.3:** "The safety case argument shall be clear, explicit, and traceable."

This tab documents the full GSN tree in text form (if a formal diagram diagram is not created). It shows:
- Top claim and context
- Sub-claims (one per SG)
- Strategies (how each claim is argued)
- Evidence pointers (file names, sheet names, row numbers)

Useful when the assessor needs to follow the complete argument path without referring to a separate visual diagram.

### Tab 13 — Assessment_Conclusion (Clause 6.4 — Final Assessment)

**ISO Requirement 6.4:** "The safety case shall conclude with a formal assessment statement signed by the functional safety manager and project manager, with recommendations for release."

**Signoff blocks:**
1. **Functional Safety Manager:** Certifies that the safety case is complete, the item is acceptably safe, and development followed the Safety Plan.
2. **Project Manager:** Certifies that the item is ready for integration.
3. **Assessor (Notified Body):** Approves the safety case for release to series production.

Each block must include: Name, date, signature.

### Tab 14 — References (Clause 6.3 — Evidence Catalog)

**ISO Requirement 6.3.2:** "The safety case shall reference all source documents and artifacts used to support the claims."

Minimum references:
- HARA workbook (path, version)
- FSC workbook (path, version)
- TSC workbook (path, version)
- FMEDA workbook (if applicable)
- SW verification reports (if applicable)
- Confirmation review records (paths or embedded)
- Tool qualification records
- Item Definition
- Safety Plan
- Applicable standards (ISO 26262 Parts 1–8, ISO 13849, etc.)

## Compliance Checklist

Before submitting the Safety Case for formal assessment, verify:

- [ ] Tab 00: All project metadata filled (name, ID, revision, date, FSM, approver, ASIL)
- [ ] Tab 01: Document Control revision marked `1.0`, signature block signed
- [ ] Tab 02: Executive Summary reflects actual project (item name, ASIL, vehicle program)
- [ ] Tab 03: Item Definition linked and key parameters echoed
- [ ] Tab 04: Top Claim is clear and unambiguous; context, justifications, assumptions documented
- [ ] Tab 05: One row per SG from HARA; strategy and evidence summary for each
- [ ] Tab 06: Every SG→FSR→TSR link present; no broken traceability chains
- [ ] Tab 07: SPFM, LFM, PMHF meet ASIL thresholds; no metrics marked as "TBD"
- [ ] Tab 08: All SW-TSRs have coverage data (or justified placeholder if not yet tested)
- [ ] Tab 09: All tools used listed with TCL justifications; no tools without qualification
- [ ] Tab 10: Every confirmation review (HARA, FSC, TSC, HW, SW) recorded with I-level and date
- [ ] Tab 11: Open items minimal; each has owner, due date, risk level, and justification
- [ ] Tab 12: Full GSN argument tree documented; all claims linked to strategies and evidence
- [ ] Tab 13: Assessment Conclusion filled; three signoff blocks completed and signed
- [ ] Tab 14: All upstream artifacts referenced with paths and versions

Once all items are checked, the Safety Case is ready for formal assessment.
