# Safety Plan Methodology

## Purpose of a Safety Plan (ISO 26262-2, Clause 6)

A Functional Safety Plan is the management artifact that defines HOW a project will execute the functional safety lifecycle. It is the contract between the customer, the supplier, and the project team about:

1. Who is responsible for which safety activities (roles and responsibilities)
2. What work products will be delivered (requirements traceability, verification, validation)
3. When activities will be completed (schedule and milestones)
4. How confirmation independence will be ensured (reviewer assignments, organizational separation)
5. What tools and methods will be used (tooling, standards, processes)
6. What assumptions and constraints apply (tailoring, scope partitions)

The Safety Plan is NOT a technical document — it is a management and governance document. It is the first artifact reviewed by a functional safety assessor, because the entire safety case rests on demonstrable compliance with the plan.

## Structure: The 12 Tabs

### 00_Title_Page
- Project name, item, target ASIL
- Functional Safety Manager (FSM) name and contact
- Document ID, revision, date
- Vehicle programs, suppliers, key stakeholders

### 01_Document_Control
- Revision history and release dates
- Who approved each release, when, and for what purpose (e.g., "0.2 — Internal review", "1.0 — Released for FSC")

### 02_Project_Info
- Expanded project context (start date, planned FSC review date, etc.)
- Confirms alignment with the Title Page

### 03_Roles_and_Responsibilities
- Seven key roles (minimum): FSM, Project Manager, HW Lead, SW Lead, Confirmation Reviewer, Assessor, Customer Interface
- For each: name, organization, email, independence level
- The independence level documents who CAN review/approve work (same person? different team? different org unit?)

### 04_Tailoring
- ISO 26262 scope: which Parts (2–8) and clauses are applicable to this project
- Rows: each ISO 26262 part (or major clause)
- Columns: Applicable (Yes/No/Partial), Justification (e.g., "No SW changes — Part 6 inapplicable except verification of existing code")

### 05_Work_Products
- Master list of all deliverables across the entire functional safety lifecycle
- Rows: 25 default work products (HARA, FSC, TSC, verification reports, etc.)
- Columns: WP_ID, name, ISO reference clause, owner, target ASIL, planned completion date, actual completion date, status (Not Started, In Progress, Complete, Verified)
- The work product list is the basis for resource planning, schedule, and traceability to the Safety Plan

### 06_Confirmation_Reviews
- One row per work product (or per key review point)
- Columns: WP_ID, work product name, required independence level (auto-suggested based on target ASIL), assigned reviewer, planned review date, actual review date, status, notes
- **Auto-suggestion logic** (per ISO 26262-2 Table 1):
  - QM: no independence required (but often assigned for traceability)
  - ASIL A: I1 (different person)
  - ASIL B: I1 (different person)
  - ASIL C: I2 (different team)
  - ASIL D: I3 (different organisational unit)

### 07_Tools
- All tools used in the safety lifecycle (MATLAB/Simulink, version control, issue tracking, test automation, HDL synthesis, compilers, etc.)
- Columns: tool name, vendor, version, usage (e.g., "Control law design and simulation for SW requirements derivation"), TCL (Tool Confidence Level: TCL1/2/3 per ISO 26262-8 Clause 11), TCL rationale, qualification status
- **TCL classification** drives how much manual verification is required:
  - TCL1: tool output does NOT influence safety-critical decisions (e.g., GitLab for version control)
  - TCL2: tool output influences safety decisions; needs qualification or extensive manual verification (e.g., MATLAB for control law design)
  - TCL3: tool output is the only way to verify correctness; must be qualified or independently developed (e.g., formal verification tool)

### 08_Resources
- HW resources (test benches, hardware-in-the-loop rigs, emulators)
- SW tool licenses (MATLAB, Simulink, compilers, linkers, coverage tools)
- Lab equipment (oscilloscopes, network analyzers, CAN bus analyzers)
- Training plan (team upskilling in ISO 26262, tool training, process training)

### 09_Anomaly_Resolution
- Process description (placeholder): how the team will handle issues, change requests, non-conformances during safety lifecycle execution
- Anomaly tracker table: ID, raised by, date raised, description, severity (Minor/Major/Critical), owner, status, resolution notes
- Tracks defects in work products, process deviations, third-party findings (assessor findings, customer observations, etc.)

### 10_Schedule
- Project milestones with target dates and dependency tracking
- Typical milestones: Project Kickoff, Item Definition Review, HARA Review, FSC Review, System Design Review, HW/SW Design Review, Verification Complete, FSC Sign-off, Release to Production
- Status column tracks progress (Open/In Progress/Closed)

### 11_References
- Standards: ISO 26262 parts 1–8 (typically all 8 parts are referenced even if some are tailored out)
- Customer-supplied documents: item definition, requirements specs, architecture standards
- Internal procedures: development process, verification methods, failure analysis procedures, change control process
- External standards: MISRA C:2012 (if applicable), AUTOSAR (if applicable), IEC 61508 (parent standard context)

## Key Relationships

### Tailoring ↔ Work Products
The Tailoring tab justifies which ISO 26262 clauses are applicable. The Work Products tab then enumerates the specific artifacts that satisfy those clauses. For example:
- Tailoring says "Part 6 (Software) inapplicable — no new SW"
- Work Products then does NOT list items like "SW Architecture", "SW Unit Design", "SW Unit Verification"

### Work Products ↔ Confirmation Reviews
Each row in Work Products has a corresponding row in Confirmation Reviews. The confirmation reviewer is responsible for verifying that the work product is complete, correct, and ready for the next phase.

### Roles ↔ Confirmation Reviews
The "Assigned Reviewer" in Confirmation Reviews must be selected from the pool of people in Roles and Responsibilities, and must meet the required independence level.

### Tools ↔ Resource Planning
The Tools tab identifies every tool used. The Resources tab then allocates licenses, hardware, and training to support their use.

## Audit Readiness Checklist

A well-formed Safety Plan should satisfy:

1. **Completeness**: All 12 tabs are present and populated (even if some are placeholders)
2. **Consistency**: Work Products and Confirmation Reviews have the same set of items; Roles match the "Assigned Reviewer" cells
3. **Traceability**: Each row in Work Products is linked to at least one ISO 26262 clause in the Tailoring tab
4. **Independence**: Each Confirmation Review row documents the required and assigned independence level
5. **Dates**: Schedule tab has realistic dates and dependencies; planned dates in Work Products match Schedule milestones
6. **Approvals**: Document Control tab shows review and approval signatures
7. **Tool Justification**: Every TCL3 tool has clear justification or qualification evidence documented

## Common Pitfalls

1. **Vague Roles**: Assigning "John" to 5 different roles without clarifying which person is actually responsible for each. Result: nothing gets done.
2. **Over-tailoring**: Marking clauses as "Inapplicable" without justification. Result: auditor flags it as missing scope.
3. **Stale Work Product List**: Copy-pasting a 25-item list from a previous project without removing irrelevant items. Result: confusion about what is actually being delivered.
4. **Independence Mismatch**: Assigning a reviewer who does not meet the required independence level (e.g., assigning the SW architect to review their own SW architecture). Result: audit finding.
5. **Undated Schedule**: Schedule tab with no dates. Result: project drifts, no objective measure of progress.
6. **Missing Tool TCL Justification**: Listing tools without explaining why each TCL level is chosen. Result: assessor questions every tool classification.

## When to Update the Safety Plan

Update the Safety Plan (and increment the revision):
- **Before each major review** (Item Definition, HARA, FSC, TSC, Design Reviews, Final Release)
  - Confirm that schedules are still realistic
  - Update work product status columns
  - Adjust resource allocations if needed
- **When scope changes** (new supplier, new tool, new ASIL target)
  - Revise Tailoring if necessary
  - Update Work Products and Confirmation Reviews
- **When roles change** (promotions, departures, reorganization)
  - Update Roles and Responsibilities and Confirmation Reviews to maintain independence
- **When anomalies are discovered** (failed test, tool issue)
  - Add to Anomaly Resolution tracker with owner and planned resolution
  - Adjust schedule if needed

A typical Safety Plan evolves through 2–5 revisions (0.1 → 0.2 → 0.3 → 1.0 release) before the FSC phase begins, and then freezes until post-release updates.
