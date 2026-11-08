# SW Architecture Checklist — Detailed Check Catalog

## Confirmation Review Checks (14)

These checks focus on document quality, structure, and metadata per ISO 26262-8 §10.

### CR-01: Document Structure
**Requirement:** SW Architecture document shall be structured into distinct sections  
**Obligation:** Shall  
**Confidence:** Medium  
**Automated:** Yes

Document is expected to have 11+ distinct tabs/sheets covering title page, document control, component catalog, RTOS config, task scheduling, MPU partitioning, interfaces, safety mechanisms, MISRA targets, initialization, and references.

**FC Trigger:** >= 11 tabs found  
**PC Trigger:** < 11 tabs found

---

### CR-02: Title & Scope
**Requirement:** Document title shall identify the SW Architecture scope  
**Obligation:** Shall  
**Confidence:** Low  
**Automated:** No (drafted)

Title page should have a clear, descriptive title identifying the system and architecture scope (e.g., "ESC Software Architecture", "Autonomous Emergency Braking SW Architecture").

**FC Trigger:** Title detected and is descriptive  
**NO Trigger:** No title on Title page

---

### CR-03: Author & Approver
**Requirement:** Author and Approver shall be identified on Title page  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Both fields must be populated with names or identifiers. Independence per ISO 26262-2 is verified separately in CR-13.

**FC Trigger:** Both Author and Approver populated  
**NO Trigger:** One or both missing

---

### CR-04: Revision
**Requirement:** Document revision shall be tracked  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Revision field on Title page should contain version identifier (e.g., "1.0", "A", "Rev 2").

**FC Trigger:** Revision field populated  
**NO Trigger:** No revision detected

---

### CR-05: Status
**Requirement:** Document status shall be indicated  
**Obligation:** Should  
**Confidence:** High  
**Automated:** Yes

Status field (e.g., "Draft", "In Review", "Final") helps readers understand maturity.

**FC Trigger:** Status populated  
**PC Trigger:** Status not detected

---

### CR-06: Document ID & Project
**Requirement:** Document ID and Project shall be specified  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Document ID uniquely identifies the artifact within project/organizational context. Project name/number identifies the system.

**FC Trigger:** Both Doc ID and Project populated  
**NO Trigger:** One or both missing

---

### CR-07: Document Control
**Requirement:** Change history shall be maintained  
**Obligation:** Shall  
**Confidence:** Low  
**Automated:** No (drafted)

01_Document_Control tab should exist with change table showing date, version, author, and change description.

**FC Trigger:** 01_Document_Control tab present  
**PC Trigger:** Tab missing or incomplete

---

### CR-08: Table of Contents
**Requirement:** Table of contents shall be provided or tabs clearly labeled  
**Obligation:** Should  
**Confidence:** Low  
**Automated:** No (drafted)

Sheets should be numbered (00_, 01_, 02_, ...) and have descriptive names. Optional separate TOC tab.

**Trigger:** Reviewer to verify tab naming and order

---

### CR-09: References
**Requirement:** References section shall list normative and informative documents  
**Obligation:** Should  
**Confidence:** Low  
**Automated:** No (drafted)

11_References tab should cite ISO 26262 standard, TSC, Safety Plan, Functional Requirements, etc.

**Trigger:** Reviewer to verify References tab is complete

---

### CR-10: Glossary
**Requirement:** Glossary or terminology definitions shall be available  
**Obligation:** Should  
**Confidence:** Low  
**Automated:** No (drafted)

Either embedded in document or referenced from external glossary (e.g., project standards). Define SW Architecture terms (task, partition, ASIL, etc.).

**Trigger:** Reviewer to verify glossary exists

---

### CR-11: Formatting Consistency
**Requirement:** Formatting and presentation shall be consistent throughout  
**Obligation:** Should  
**Confidence:** Low  
**Automated:** No (drafted)

Fonts, colors, numbering style, table formats should be consistent across all tabs. Alignment, spacing, headers should follow template.

**Trigger:** Reviewer to assess formatting

---

### CR-12: Cross-References
**Requirement:** Cross-references to TSC shall be present where applicable  
**Obligation:** Should  
**Confidence:** Medium  
**Automated:** Yes

Architecture document should reference Technical Safety Concept document (TSC) to ensure traceability of safety requirements.

**FC Trigger:** TSC references detected in sheet names or content  
**PC Trigger:** Limited or no TSC cross-references

---

### CR-13: Independence
**Requirement:** Author and Approver shall be independent per ISO 26262-2  
**Obligation:** Shall  
**Confidence:** Low  
**Automated:** No (drafted)

Independence determined by ASIL and organizational context per ISO 26262-2 Clause 6.4.7 (I1/I2/I3). Not verifiable from xlsx alone.

**Trigger:** Reviewer to verify independence per ISO 26262-2

---

### CR-14: Compliance Assertions
**Requirement:** Document shall assert compliance to ISO 26262-6 Part 7  
**Obligation:** Shall  
**Confidence:** Low  
**Automated:** No (drafted)

Title page or Document Control should state: "This SW Architecture is developed in accordance with ISO 26262:2018 Part 6 §7 (SW Architecture)."

**Trigger:** Reviewer to verify compliance assertion

---

## SW Architecture Assessment Checks (12)

These checks focus on technical completeness per ISO 26262-6 §7 SW Architecture.

### SWAA-01: SW Component Catalog
**Requirement:** SW Component Catalog shall be populated with all SW components  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Tab 03_SW_Component_Catalog must list all software components, drivers, modules, libraries, tasks with unique IDs.

**FC Trigger:** >= 1 component in catalog  
**NO Trigger:** Catalog empty or missing

---

### SWAA-02: ASIL Assignment
**Requirement:** Each SW component shall have ASIL assigned  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Every component row must have ASIL field populated with QM, ASIL A, ASIL B, ASIL C, or ASIL D.

**FC Trigger:** All components have ASIL value  
**NO Trigger:** 1+ components missing ASIL

---

### SWAA-03: Partition Mapping
**Requirement:** Each SW component shall be mapped to a partition or execution context  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Every component must be assigned to a logical partition (e.g., PARTITION_DIAGNOSTIC, PARTITION_SAFETY_CRITICAL, PARTITION_QM).

**FC Trigger:** All components mapped to partition  
**PC Trigger:** 1+ components not mapped

---

### SWAA-04: RTOS/OS Configuration
**Requirement:** RTOS/OS name, version, scheduling policy, and ASIL support shall be documented  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Tab 04_RTOS_OS_Configuration must specify:
- RTOS Name (e.g., VxWorks, FreeRTOS, custom RTOS)
- Version (e.g., 7.0, 10.4)
- Scheduling Policy (Rate-monotonic, Priority-based, etc.)
- ASIL Support (QM only, ASIL support certified, etc.)

**FC Trigger:** Name and Version populated  
**NO Trigger:** Missing or incomplete

---

### SWAA-05: Task Scheduling
**Requirement:** Task scheduling map shall define period, priority, and WCET for each task  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Tab 05_Task_Scheduling_Map must list all tasks with:
- Task ID and Name
- Priority
- Period (ms)
- WCET (Worst-Case Execution Time, ms)
- ASIL
- Partition assignment

**FC Trigger:** All tasks have WCET defined  
**PC Trigger:** 1+ tasks missing WCET

---

### SWAA-06: Schedulability
**Requirement:** Schedulability analysis shall confirm sum(WCET/Period) < 1.0 per priority  
**Obligation:** Shall  
**Confidence:** Low  
**Automated:** No (drafted)

For rate-monotonic scheduling, the utilization factor U = sum(WCET_i / Period_i) per priority level must be < 1.0 to guarantee schedulability. Reviewer must verify analysis was performed.

**Trigger:** Reviewer to verify schedulability analysis in external document

---

### SWAA-07: MPU Partitioning
**Requirement:** MPU memory partitioning shall be documented for ASIL-relevant components  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Tab 06_MPU_Memory_Partitioning must specify memory regions (base address, size, access permissions) for each partition, especially ASIL-relevant ones.

**FC Trigger:** MPU regions defined for all ASIL components  
**PC Trigger:** Limited MPU regions or missing ASIL partitions

---

### SWAA-08: Inter-Component Interfaces
**Requirement:** All inter-component interfaces shall specify type and integrity protection  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Tab 07_Inter_Component_Interfaces must document:
- Source and destination components
- Interface type (Signal, Message, Shared Memory, etc.)
- Integrity protection (Checksum, CRC, none, etc.)
- ASIL allocation

**FC Trigger:** All interfaces have integrity protection specified  
**PC Trigger:** 1+ interfaces missing protection spec

---

### SWAA-09: Safety Mechanisms
**Requirement:** Safety mechanism allocation shall be documented per ASIL  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Tab 08_Safety_Mechanism_Allocation must allocate safety mechanisms (fault detection, fault confinement, recovery) to each ASIL-relevant component.

**FC Trigger:** Safety mechanisms allocated  
**PC Trigger:** Missing or incomplete allocation

---

### SWAA-10: MISRA Compliance
**Requirement:** MISRA C:2012 compliance targets shall be specified  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Tab 09_MISRA_Compliance_Targets must define compliance targets per component or global policy (e.g., "Mandatory rules 100% compliant, Required rules 90% compliant with waivers").

**FC Trigger:** MISRA targets defined  
**PC Trigger:** Tab empty or missing

---

### SWAA-11: Initialization
**Requirement:** Initialization sequence shall be documented  
**Obligation:** Shall  
**Confidence:** High  
**Automated:** Yes

Tab 10_Initialization_Sequence must list startup steps in order, including hardware init, bootloader, OS init, application init, task creation.

**FC Trigger:** >= 1 initialization step documented  
**PC Trigger:** Tab empty or missing

---

### SWAA-12: TSC Integration
**Requirement:** Technical Safety Concept references shall be integrated  
**Obligation:** Should  
**Confidence:** Medium  
**Automated:** Yes

Architecture should reference TSC document and trace safety requirements to architecture components.

**FC Trigger:** TSC reference tabs detected  
**PC Trigger:** Limited or no TSC integration

---

## Verification Assessment Checks (5)

These checks reference external Verification artifacts per ISO 26262-8 §9.

### VA-01: SW Component Coverage
**Requirement:** Verification Plan shall cover all SW components with SW-TSR traceability  
**Obligation:** Shall  
**Confidence:** Low  
**Automated:** No (drafted)

Each SW component must have corresponding test cases or test procedures in Verification Plan / Test Specification / Test Report.

**Trigger:** Reviewer to verify against Verification Plan

---

### VA-02: MPU Isolation Testing
**Requirement:** MPU isolation shall be verified for all ASIL-relevant partitions  
**Obligation:** Shall  
**Confidence:** Low  
**Automated:** No (drafted)

Verification Plan must include tests confirming that ASIL partitions are isolated from QM partitions (no unintended access, no shared resources without protection).

**Trigger:** Reviewer to verify against Verification Report

---

### VA-03: Scheduling Verification
**Requirement:** Task scheduling and priority inversion handling shall be tested  
**Obligation:** Shall  
**Confidence:** Low  
**Automated:** No (drafted)

Test cases must verify that tasks meet deadline requirements and that priority inversion (if applicable) is mitigated.

**Trigger:** Reviewer to verify test coverage

---

### VA-04: Interface Verification
**Requirement:** All inter-component interfaces shall have integration test coverage  
**Obligation:** Shall  
**Confidence:** Low  
**Automated:** No (drafted)

Integration tests must verify all inter-component communications: signals sent/received correctly, integrity protection functions (checksum, CRC) validated, timeouts handled.

**Trigger:** Reviewer to verify test specification

---

### VA-05: MISRA Verification
**Requirement:** MISRA C:2012 compliance shall be verified or waived per component  
**Obligation:** Shall  
**Confidence:** Low  
**Automated:** No (drafted)

Verification method must be specified: static analysis tool (e.g., Polyspace), manual review, or waiver with justification. Evidence must be in Verification Report.

**Trigger:** Reviewer to verify against Verification Report
