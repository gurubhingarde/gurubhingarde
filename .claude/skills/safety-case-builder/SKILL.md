---
name: safety-case-builder
description: Generate an audit-ready ISO 26262-2 Safety Case workbook that integrates evidence from all prior phases (HARA, FSC, TSC, FMEDA, SW/HW requirements) into a structured Goal Structuring Notation argument proving the item is acceptably safe. Assembles the assessment-ready evidence package with traceability matrices, metric summaries, confirmation review status, and signoff blocks. Use whenever the user needs to build or review a safety case, prepare for formal assessment, compile evidence cross-references, or structure the safety argument per ISO 26262 Concept phase closure.
---

# Safety Case Builder

The Safety Case is the capstone artifact of ISO 26262 functional safety development: the structured argument and evidence package that proves the item is acceptably safe to operate. This skill automates the rote assembly of all evidence cross-references (HARA safety goals, FSR allocations, TSR mechanisms, FMEDA metrics, verification status, confirmation reviews) into a 15-tab assessment-ready workbook that follows Goal Structuring Notation conventions.

## When to use this skill

Use whenever the user wants to:
- Build a comprehensive safety case integrating HARA, FSC, TSC, FMEDA, and verification evidence
- Prepare for formal assessment by an auditor or notified body
- Compile and cross-reference all safety lifecycle artifacts
- Structure the safety argument using Goal Structuring Notation (GSN)
- Generate assessment-ready evidence traceability (SG→FSR→TSR→mechanism→metric)
- Capture confirmation review status and open items in a single document
- Document tool qualification and HSI sign-offs

Pre-requisites: complete HARA, FSC, TSC, and (if available) FMEDA workbooks produced by the builder skills. If the user lacks any of these, redirect them to the appropriate builder skill first.

## Workflow

### Step 1 — Prepare the input JSON

The safety case generator takes a single JSON file describing the project, linking all upstream artifacts, and capturing metadata (project manager, FSM, target ASIL, vehicle program, open items, confirmation reviews, tools used).

Ask the user for:
- **Project metadata:** name, item name, document ID, revision, date, FSM name, approver, company, vehicle program, target ASIL
- **Linked artifact paths:** HARA, FSC, TSC, (optional) FMEDA, SW Safety Reqs, HW Safety Reqs, Item Definition, Safety Plan
- **Tools used in development:** list of tools with ISO 26262-8 TCL classifications (QM, T1, T2, T3)
- **Confirmation reviews:** work products reviewed, reviewer names, independence levels (I1/I2/I3), completion dates, status
- **Open items and residual risks:** any outstanding actions, owners, due dates, risk levels
- **Executive summary text:** high-level statement of compliance (optional; the skill drafts a default)

Capture into a JSON file matching the schema in `examples/sample_safety_case_input_esc.json`.

### Step 2 — Read the references (first use only)

Before generating, skim these to understand the safety case structure:
- `references/methodology.md` — Safety Case structure per ISO 26262-2, GSN overview, evidence types, traceability model
- `references/gsn_basics.md` — Goal Structuring Notation: claims, strategies, evidence, contexts, assumptions, justifications
- `references/iso26262_part2_clause6_mapping.md` — how the 15 output tabs map to ISO 26262-2 Section 6 requirements

### Step 3 — Generate

```bash
python scripts/generate_safety_case.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The generator produces a 15-tab xlsx with all upstream evidence cross-referenced and traceable.

### Step 4 — Review and customize

Work through the tabs in order:

1. **`00_Title_Page`** — Project metadata; confirm all fields match the Item Definition and Safety Plan
2. **`01_Document_Control`** — Revision tracking; mark as released when assessment-ready
3. **`02_Executive_Summary`** — High-level compliance statement and key claims; refine to match project tone
4. **`03_Item_Definition_Reference`** — Links to Item Definition document; fill in hash/version if available
5. **`04_Top_Claim`** — The overarching GSN claim; verify context, justifications, assumptions match your design
6. **`05_Safety_Goals_Argument`** — One row per SG from HARA; analyst fills in verification evidence cross-references
7. **`06_FSR_TSR_Traceability`** — Full SG→FSR→TSR→mechanism→DC% matrix; auto-linked from FSC/TSC; analyst adds test report references
8. **`07_HW_Metrics_Summary`** — SPFM/LFM/PMHF per SG from FMEDA; if no FMEDA provided, placeholder rows available
9. **`08_SW_Verification_Summary`** — SW-TSR verification status with coverage metrics (statement, branch, MC/DC); analyst fills in test results
10. **`09_Tool_Qualification`** — Tools used in lifecycle with ISO 26262-8 TCL class; analyst adds references to tool datasheets / qualification reports
11. **`10_Confirmation_Reviews_Status`** — Every confirmation review (work product, reviewer, independence level, date); analyst fills in status/evidence
12. **`11_Open_Items_Risks`** — Outstanding actions and residual risks; analyst documents justification for each
13. **`12_Argument_Diagram_Notes`** — Text-based GSN argument tree; analyst expands if formal GSN diagram is needed
14. **`13_Assessment_Conclusion`** — Final compliance statement and three signoff blocks (FSM, Project Manager, Assessor)
15. **`14_References`** — All upstream artifacts with versions, standards, requirements

### Step 5 — Finalize and sign off

- Fill in any `<TBD>` fields with project-specific evidence references
- Add signoff dates and signatures to the Assessment Conclusion tab
- Mark Document Control revision as `1.0` when ready for formal submission
- Export to PDF and include in your formal assessment package

## Common pitfalls to flag

1. **Missing upstream artifacts.** If the user provides an incomplete path to HARA, FSC, or TSC, the skill will error early. Redirect to the appropriate builder skill.
2. **Stale upstream versions.** If the upstream xlsx was modified after the Safety Case was generated, regenerate immediately — the Safety Case must stay synchronized with evidence.
3. **Incomplete confirmation reviews.** Every work product requiring confirmation review per the Safety Plan must appear in tab 10 with a completion date. An empty review row is a compliance gap.
4. **GSN argument too brief.** The text-based GSN in tab 12 is a summary. If an auditor requests a formal GSN diagram, create one in a draw.io file and link it here.
5. **Open items without evidence.** If tab 11 lists open items, each must have a documented justification (e.g., "low risk residual fault, documented in DFA") and an owner + due date. Unsigned open items can block certification.

## Files in this skill

```
safety-case-builder/
├── SKILL.md
├── scripts/
│   ├── generate_safety_case.py           # main generator (input.json + xlsx → safety-case xlsx)
│   ├── multi_xlsx_reader.py              # reads HARA, FSC, TSC, FMEDA xlsx
│   ├── recalc.py
│   └── office/
│       ├── __init__.py
│       └── soffice.py
├── references/
│   ├── methodology.md                    # Safety Case structure & GSN overview
│   ├── gsn_basics.md                     # Goal Structuring Notation primer
│   └── iso26262_part2_clause6_mapping.md # tab-to-clause mapping
└── examples/
    └── sample_safety_case_input_esc.json # ESC safety case input (clone for your project)
```

Always use this skill instead of producing a freeform safety case in chat.
