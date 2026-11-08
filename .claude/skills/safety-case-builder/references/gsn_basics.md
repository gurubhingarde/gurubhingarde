# Goal Structuring Notation (GSN) Basics

Goal Structuring Notation is a graphical and textual language for expressing safety arguments. It was developed by Tim Kelly and John McDermid (University of York) and is widely used in aerospace, defense, and automotive safety cases.

## GSN Elements

### Goals (G)

A goal is a claim about a property of the system. Goals are the primary building blocks of a GSN argument.

**Example:**
- G1: "The item is acceptably safe for its intended use"
- G2.1: "Hazard H1 is adequately mitigated"
- G2.2: "Safety Goal SG-001 is satisfied"

Goals must be:
- Unambiguous
- Traceable to one or more evidence items
- Realistically achievable (not vague like "the system is good")

### Strategies (S)

A strategy is a reasoning approach that relates a goal to sub-goals or evidence. It explains *how* a goal is supported.

**Example:**
- S1.1: "By demonstrating that all hazards in the HARA are addressed by safety goals"
- S1.2: "By showing that all safety goals are allocated to technical measures and verified"
- S1.3: "By providing confirmation review records proving process integrity"

Strategies are directional: they point from a parent goal downward to sub-goals or evidence.

### Solutions / Evidence (E)

Evidence is the concrete artifact that supports a goal (via a strategy). It can be:
- A document (e.g., HARA workbook, FSC workbook)
- A test report or lab result
- A metric (e.g., FMEDA SPFM score >= 99%)
- A confirmation review record

**Example:**
- E1: "HARA workbook with 5 safety goals and allocated ASIL per goal"
- E2: "FSC workbook with functional safety requirements and decomposition DFA"
- E3: "FMEDA report: SPFM = 99.5%, LFM = 91.2%, PMHF = 8.3 FIT (meets ASIL D thresholds)"

### Contexts (C)

A context is the circumstance under which a goal applies. It sets the scope and boundary conditions.

**Example:**
- C1: "For vehicle program: Mid-Size Sedan 2027"
- C2: "Operating scenario: normal driving on paved roads, speeds 0–200 km/h"
- C3: "Target ASIL: D (highest level)"
- C4: "Operational environment: ambient temperature 0 °C to +60 °C"

Contexts constrain and clarify the scope of goals.

### Assumptions (A)

An assumption is a condition that must be true for the argument to hold, but is not directly within the scope of the safety case to verify.

**Example:**
- A1: "Vehicle electrical system is maintained per ISO 15118"
- A2: "Diagnostic tooling is calibrated per ISO 13849"
- A3: "Production manufacturing follows the approved control plan"

Assumptions are risk points: if an assumption is violated, the safety argument may not hold.

### Justifications (J)

A justification is the reason why a particular approach or evidence is adequate.

**Example:**
- J1: "HARA methodology per ISO 26262-3 Annex A is the industry standard for hazard analysis in automotive functional safety"
- J2: "DFA coupling factor checklist per ISO 26262-9 Section 7 is the approved method for verifying decomposition independence"
- J3: "MC/DC code coverage is required for ASIL D per ISO 26262-6 Section 9 and is the most rigorous structural coverage criterion"

Justifications explain *why* an evidence type is appropriate for the claim.

## Argument Structure Example

### Top-Level Claim (G1)

```
┌─────────────────────────────────────────────────────────────────┐
│ G1: The ESC ECU is acceptably safe for its intended use         │
│     in the Mid-Size Sedan 2027 program (ASIL D)                 │
└─────────────────────────────────────────────────────────────────┘
       ↓ (Strategy S1.1: Demonstrate HARA completeness)
       ↓ (Strategy S1.2: Demonstrate FSC adequacy)
       ↓ (Strategy S1.3: Demonstrate TSC adequacy)
       ↓ (Strategy S1.4: Demonstrate HW/SW verification)
       ↓ (Strategy S1.5: Demonstrate process integrity)
```

### Sub-Goals (G2.x) — One Per Safety Goal

```
G1
├─ G2.1: Safety Goal SG-001 (Loss of yaw rate control) is satisfied
│  ├─ G3.1.1: All FSRs from SG-001 are implemented (FSR-001, FSR-002, FSR-003)
│  │  ├─ E: FSC workbook
│  │  └─ E: TSC workbook with TSRs mapped to FSRs
│  ├─ G3.1.2: All mechanisms for SG-001 FSRs have adequate diagnostic coverage
│  │  ├─ E: FMEDA report: DC >= 99% for dual-core lockstep, watchdog, E2E
│  │  └─ J: DC >= 99% is required for ASIL D per ISO 26262-5 Table 4
│  └─ G3.1.3: All TSRs for SG-001 are verified by test
│     ├─ E: HIL test report: TSR-SW-001 branch coverage 97%
│     ├─ E: SIL test report: TSR-HW-001 diagnostic latency < FDTI budget
│     └─ J: Confirmation review approved the test plan and results
│
├─ G2.2: Safety Goal SG-002 (Sensor signal corruption) is satisfied
│  └─ [Similar structure with FSRs, mechanisms, FMEDA, tests]
│
└─ G2.3–G2.5: [Additional safety goals...]
```

### Evidence Pointers

At the leaf of each branch, evidence is cited:

```
E1: HARA_ESC_2026_v1.0.xlsx
    - SG-001: Loss of yaw rate control (ASIL D, FTTI 100ms)
    - SG-002: Sensor signal corruption (ASIL C, FTTI 500ms)
    - ...

E2: FSC_ESC_2026_v2.0.xlsx
    - FSR-001: Yaw rate error detected within 100ms (→ SG-001)
    - FSR-002: Sensor plausibility check (→ SG-002)
    - ...
    - DFA: Dual-core lockstep coupling factors—all mitigated

E3: TSC_ESC_2026_v1.0.xlsx
    - TSR-HW-001: Dual-core lockstep on processor (DC 99.8%)
    - TSR-SW-001: Yaw rate computation with E2E protection (DC 99.5%)
    - HSI: Signal definitions for HW→SW diagnostic flags
    - Timing: FDTI = 50ms, FRTI = 50ms per FSR-001 FTTI 100ms

E4: FMEDA_ESC_2026_v1.0.xlsx
    - SPFM: 99.5% (target ASIL D >= 99%)—PASS
    - LFM: 91.2% (target ASIL D >= 90%)—PASS
    - PMHF: 8.3 FIT (target ASIL D < 10 FIT)—PASS

E5: Test Reports
    - SW_HIL_Test_Report_2026-04-20.pdf: Statement 97%, Branch 95%, MC/DC 92%
    - HW_SIL_Test_Report_2026-04-18.pdf: All TSR-HW-* verified
    - Integration_Test_Report_2026-04-25.pdf: E2E HSI signals validated

E6: Confirmation Review Records
    - HARA Review: Michael Chen (I2), 2026-02-15, Approved
    - FSC Review: Michael Chen (I2), 2026-03-01, Approved
    - TSC Review: Michael Chen (I2), 2026-03-22, Approved
    - FMEDA Review: Dr. Sarah Williams (I2), 2026-04-10, Approved

E7: Process Compliance
    - Safety Plan_ESC_2026_v1.0.pdf: Confirms ISO 26262-8 tool qualification
    - Tool_Qualification_Report_MATLAB.pdf: MATLAB Simulink TCL T3
```

## GSN Conventions in the Safety Case

In the safety-case-builder output:

1. **Tab 04 (Top_Claim)** presents G1 with context, justifications, and assumptions.
2. **Tab 05 (Safety_Goals_Argument)** summarizes G2.x (one per SG) with strategy and evidence pointers.
3. **Tab 06 (FSR_TSR_Traceability)** provides the SG→FSR→TSR→mechanism→metric chain (vertical traceability).
4. **Tab 12 (Argument_Diagram_Notes)** expands the text-based GSN tree showing the full hierarchical structure.
5. **Tabs 07–11** provide the evidence (FMEDA, SW verification, confirmation reviews, tools, open items).

Each row in the Safety Case is a node in the GSN tree; the links between rows (via SG_ID, FSR_ID, TSR_ID) form the argument structure.

## Creating a Formal GSN Diagram

The Safety Case generator produces a text-based GSN argument in Tab 12. If a formal GSN diagram is required, it can be created using:

- **draw.io** (free, web-based; export as PNG/PDF for embedding in docs)
- **Lucidchart** (commercial; good for large diagrams)
- **Graphviz** (text-based; good for version control)

The diagram should mirror the hierarchy in Tab 12:
- Goals (G1, G2.x, G3.x.y) as colored boxes
- Strategies (S1.x, S2.x) as diamond shapes
- Solutions/Evidence (E) as document icons
- Contexts (C), Assumptions (A), Justifications (J) as annotations on the relevant boxes

Once created, export to PNG and insert into the Safety Case (or create a separate document titled "GSN Argument Diagram" linked from the main Safety Case).

## Assessment Readiness

A well-formed GSN argument:
1. Has a clear top-level goal (G1) with context and justifications
2. Decomposes into specific sub-goals (one per major requirement or SG)
3. Each sub-goal is supported by a strategy and at least one evidence item
4. Evidence is concrete, traceable, and recent (not stale)
5. Assumptions are documented and their residual risk is accepted
6. All coupling and decomposition claims are justified by DFA or equivalent analysis

An assessor will verify that:
- No unsupported claims exist (every goal has evidence)
- No circular reasoning (e.g., claiming E1 proves G1 and G1 proves E1)
- Assumptions are realistic and managed
- Evidence is sufficient and appropriate for the claimed ASIL

A Safety Case that violates these principles will likely be rejected during formal assessment.
