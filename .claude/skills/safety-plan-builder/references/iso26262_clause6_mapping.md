# ISO 26262-2 Clause 6 Mapping to Safety Plan Tabs

ISO 26262-2 (Management of Functional Safety) Clause 6 defines the activities and work products that constitute a functional safety plan. The 12-tab workbook maps directly to these clauses.

## Clause 6.2: Functional Safety Plan — Overall Approach (6.2.1–6.2.5)

### 6.2.1 General functional safety plan requirements

**Maps to:**
- **00_Title_Page** — establishes the scope, item name, target ASIL, and key stakeholders
- **02_Project_Info** — provides expanded context (vehicle programs, suppliers, key dates)
- **11_References** — lists standards and procedures that govern the plan

**What it covers:**
- The Safety Plan is the master control document for all safety activities
- It shall identify the safety lifecycle phases applicable to the item
- It shall identify the tools, methods, and organizational structure used to execute the safety lifecycle

### 6.2.2 Functional Safety Plan — Scope and assumptions

**Maps to:**
- **04_Tailoring** — explicitly states which ISO 26262 parts and clauses are applicable (Yes/No/Partial) and why
- **02_Project_Info** — project-level assumptions and constraints
- **11_References** — customer requirements, design standards, and scope documents

**What it covers:**
- Which phases of the safety lifecycle apply (concept, system design, HW design, SW design, production, etc.)
- Which assumptions are made (e.g., "only existing SW", "no new HW design")
- What scope partitions apply (e.g., cybersecurity handled separately under ISO/SAE 21434)

### 6.2.3 Functional Safety Plan — Roles and responsibilities

**Maps to:**
- **03_Roles_and_Responsibilities** — the primary artifact
- **06_Confirmation_Reviews** (Assigned Reviewer column) — documents who will review each work product

**What it covers:**
- Clear assignment of safety-related roles (Functional Safety Manager, Project Manager, HW Lead, SW Lead, Confirmation Reviewer, Assessor, Customer liaison)
- Name, organization, email for each person
- Independence level of each role (critical for confirmation activities)

### 6.2.4 Functional Safety Plan — Work products

**Maps to:**
- **05_Work_Products** — the master list of all deliverables
- **06_Confirmation_Reviews** — one row per work product, tracking review status

**What it covers:**
- Complete enumeration of work products (25 default items covering Parts 2–8)
- For each: unique ID, name, ISO reference clause, owner, target ASIL, planned and actual delivery dates, status (Not Started, In Progress, Complete, Verified)
- The work product list is the basis for traceability to ISO 26262 clauses

### 6.2.5 Functional Safety Plan — Confirmation measures and independence

**Maps to:**
- **06_Confirmation_Reviews** — the primary artifact
- **03_Roles_and_Responsibilities** (Independence Level column) — documents organizational separation

**What it covers:**
- Each safety-critical work product shall be reviewed by an independent person or team
- Required independence levels per ASIL (I1/I2/I3 per ISO 26262-2 Table 1):
  - ASIL A/B: I1 (different person)
  - ASIL C: I2 (different team)
  - ASIL D: I3 (different organisational unit)
- The Safety Plan documents: (1) which WPs require confirmation, (2) required independence level, (3) assigned reviewer, (4) confirmation completion status

## Clause 6.3: Verification and Validation Plan (6.3.1–6.3.7)

### 6.3 Verification and Validation — General approach

**Maps to:**
- **05_Work_Products** — includes "Verification and Validation Plan" as a work product
- **10_Schedule** — defines the time windows for verification activities
- **07_Tools** — lists test automation tools (TCL1/2/3 classification)

**What it covers:**
- Verification and validation strategy (unit test, integration test, system test, FMEA/FTA closure)
- Test environment setup and lab resources
- Tool qualification and coverage metrics
- Methods for demonstrating that safety goals are met

## Clause 6.4: Development and Design Planning (6.4.1–6.4.6)

### 6.4 Development and Design — Planning and tailoring

**Maps to:**
- **04_Tailoring** — defines which development and design phases apply (system, HW, SW)
- **05_Work_Products** — lists design work products (Architecture, Design Spec, Requirements Spec, FSC/TSC)
- **07_Tools** — lists design tools (MATLAB/Simulink for control design, HDL tools for HW, compilers for SW)
- **08_Resources** — allocates design team capacity, tool licenses, lab facilities

**What it covers:**
- System-level design methodology (MBSE, architecture blocks, interface definitions)
- Hardware design approach (architecture, component selection, FMEA)
- Software design approach (architecture, unit design, coding standards)
- Design reviews and gate criteria

## Clause 6.5: Production and Operation Planning (6.5.1–6.5.6)

### 6.5 Production and Operation — Procedure and resource planning

**Maps to:**
- **05_Work_Products** — includes "Production Plan" and "Modification Procedure" as work products
- **08_Resources** — manufacturing resources, test equipment, training
- **10_Schedule** — production milestones and ramp timelines

**What it covers:**
- Manufacturing and quality control procedures
- Failure detection and diagnosis (on-board diagnostics, fault management)
- Field service and modification procedures
- Decommissioning or end-of-life procedures

## Clause 6.6: Supporting Processes (6.6.1–6.6.10)

### 6.6.1 Configuration Management

**Maps to:**
- **07_Tools** (Version Control) — typically "GitLab" or equivalent with TCL1 classification
- **09_Anomaly_Resolution** — tracks configuration baselines and change requests

### 6.6.2 Change Management

**Maps to:**
- **09_Anomaly_Resolution** — anomaly tracker for change requests and non-conformances

### 6.6.3 Deviations and Waivers

**Maps to:**
- **09_Anomaly_Resolution** — documents deviations from the Safety Plan or standard

### 6.6.4 Safety Assessment and Audit

**Maps to:**
- **03_Roles_and_Responsibilities** (Assessor role) — identifies the functional safety assessor
- **06_Confirmation_Reviews** — confirmation review assignments and completion status

### 6.6.5 Functional Safety Assessment Planning

**Maps to:**
- **10_Schedule** — assessment review dates and milestones
- **11_References** — safety assessment procedures and criteria

### 6.6.6 Tool Evaluation

**Maps to:**
- **07_Tools** — TCL classification and qualification status for each tool per ISO 26262-8 Clause 11

### 6.6.7 Training and Competence

**Maps to:**
- **08_Resources** (Training Plan) — identifies training needs and planned completion dates
- **03_Roles_and_Responsibilities** — confirms that each person has required competence in ISO 26262 and project-specific tools/methods

### 6.6.8 Procedures and Quality Measures

**Maps to:**
- **11_References** — internal procedures (development process, verification methods, FMEA/FTA procedures)

### 6.6.9 Problem Resolution

**Maps to:**
- **09_Anomaly_Resolution** — formal anomaly tracker for issues, root cause, and closure

### 6.6.10 Plan Modification

**Maps to:**
- **01_Document_Control** — revision history and approval signatures for Safety Plan updates

## Traceability Summary

| ISO 26262-2 Clause | Tab(s) |
|---|---|
| 6.2.1 Overall approach | 00_Title_Page, 02_Project_Info, 11_References |
| 6.2.2 Scope and assumptions | 04_Tailoring, 02_Project_Info, 11_References |
| 6.2.3 Roles and responsibilities | 03_Roles_and_Responsibilities, 06_Confirmation_Reviews |
| 6.2.4 Work products | 05_Work_Products, 06_Confirmation_Reviews |
| 6.2.5 Confirmation measures and independence | 06_Confirmation_Reviews, 03_Roles_and_Responsibilities |
| 6.3 Verification and Validation | 05_Work_Products, 10_Schedule, 07_Tools |
| 6.4 Development and Design | 04_Tailoring, 05_Work_Products, 07_Tools, 08_Resources |
| 6.5 Production and Operation | 05_Work_Products, 08_Resources, 10_Schedule |
| 6.6.1–6.6.10 Supporting Processes | 07_Tools, 09_Anomaly_Resolution, 03_Roles_and_Responsibilities, 10_Schedule, 11_References, 08_Resources, 01_Document_Control |

## How to Use This Mapping

When an assessor or reviewer asks "where is your plan for [XYZ activity]?", use this mapping to locate the relevant tab(s):

- **Example 1:** "How will you ensure confirmation reviewer independence?"
  - Answer: See **06_Confirmation_Reviews** (Required Independence column, auto-suggested per ASIL) and **03_Roles_and_Responsibilities** (Independence Level column).

- **Example 2:** "Which design activities apply to this project?"
  - Answer: See **04_Tailoring** (which ISO 26262 parts are applicable) and **05_Work_Products** (which design artifacts will be delivered).

- **Example 3:** "How will you qualify the MATLAB tool?"
  - Answer: See **07_Tools** (MATLAB listed with TCL classification and qualification status column).

- **Example 4:** "What is the verification strategy?"
  - Answer: See **05_Work_Products** (lists "Verification and Validation Plan" as a deliverable), **10_Schedule** (verification milestones), and **07_Tools** (test and coverage tools with TCL).
