# SW Safety Requirements Checklist — Check Definitions

## Summary

The SW-SR Checklist Reviewer runs 38 canonical checks grouped into three categories:

- **Confirmation Review (CR):** 14 doc-quality checks
- **SW Safety Requirements Assessment (SWSRA):** 12 ISO 26262-6 §6 substantive checks
- **Verification Assessment (VA):** 22 external checks + 5 SW-SR-specific items (33a–e)

Each check is defined by:
- **ID:** Unique identifier (e.g., "1", "4a", "33b")
- **Obligation:** "Shall" (hard requirement) or "Should" (best practice)
- **Requirement:** Human-readable statement
- **Verification Logic:** Algorithm to produce CheckResult (rating, finding, evidence, action, confidence)

---

## Confirmation Review (CR) — Document Quality

| ID | Obligation | Requirement | Rating Logic | Confidence |
|----|-----------|-------------|--------------|-----------|
| **1** | Shall | Document is structured clearly (headlines, templates) | FC if tabs >= 5; PC if < 5 | Medium |
| **2** | Should | Latest template available was used at document creation | Always draft (external) | Low |
| **3** | Should | Structure facilitates search (cross-references, index) | FC if Title tab in first 3; PC else | Medium |
| **4a** | Shall | Title covers the scope of the content | Draft if title exists; NO if missing | High |
| **4b** | Shall | Author and Approver(s) listed | FC if both; NO if either missing | High |
| **4c** | Shall | Unique identification for each revision | FC if Revision field set; NO else | High |
| **4d** | Shall | Change history available | Always draft (Document Control tab) | Low |
| **4e** | Shall | Status of the work product provided | FC if Status set; NO else | High |
| **5** | Shall | Current revision clearly identifiable | FC if Revision set; NO else | High |
| **6** | Shall | Document under configuration and change management | Always draft (organizational practice) | Low |
| **7** | Should | Header and footer updated | Always draft (requires manual inspection) | Low |
| **8** | Shall | Table of Contents present | FC if TOC/Contents tab in first 3; PC else | Medium |
| **9** | Should | Reference Table lists all references | Always draft (requires manual inspection) | Low |
| **10** | Should | All sections of the work product completed | FC if >= 95% of SRs have (asil, swc, text); LC if 70-94%; PC else | High |

---

## SW Safety Requirements Assessment (SWSRA) — ISO 26262-6 §6

| ID | Obligation | Requirement | Rating Logic | Confidence | Standard |
|----|-----------|-------------|--------------|-----------|----------|
| **1** | Shall | SW-TSRs successfully imported from TSC | FC if count > 0 with sample TSR IDs; NO else | High | 26262-6 §6.1 |
| **2** | Shall | At least one SW-SR derived per SW-TSR (no orphans) | FC if all TSRs have derived SRs; PC if gaps | High | 26262-6 §6.1 |
| **3** | Shall | ASIL assigned and consistent with parent TSR | FC if >= 99% of SRs have ASIL; PC else | High | 26262-6 §6.2 |
| **4** | Shall | Allocated SWC specified (no TBD) | FC if >= 99% have SWC (no TBD); PC else | High | 26262-6 §6.2 |
| **5** | Shall | Requirement text present (no empty rows) | FC if >= 99% have text; PC else | High | 26262-6 §6.2 |
| **6** | Shall | Target detection time specified | FC if >= 99% have detection time; PC else | High | 26262-6 §6.3 (timing budget) |
| **7** | Shall | Failure mode mapping covers standard SW failure modes | FC if count >= 10 (deadline miss, illegal state, divide-by-zero, data corruption); LC if 1-9; NO if 0 | Medium | 26262-6 §6.5 (FMEDA) |
| **8** | Shall | Each SW-SR has verification method | FC if >= 99% have method; PC else | High | 26262-6 §6.4 |
| **9** | Shall | Verification methods appropriate for ASIL (MC/DC for D per Tables 7–10) | Draft with Low confidence; reviewer verifies per 26262-6 Tables 7-10 | Low | 26262-6 §6.4 |
| **10** | Shall | Test strategy covers unit/integration/back-to-back/fault-injection | FC if >= 6 rows with diverse topics; LC if 1-5; NO if 0 | Medium | 26262-6 §6.6 |
| **11** | Should | Independence considerations documented (if cascading from TSC) | FC if count > 0; Draft else (if applicable) | Medium | 26262-6 §6.4 |
| **12** | Should | MISRA C:2012 mapping present for safety-relevant SRs | FC if count > 0; Draft else (if applicable) | Medium | 26262-6 Annex D |

**Key definitions:**
- **SW-TSR:** Technical Safety Requirement imported from TSC (parent requirement).
- **SW-SR:** Software Safety Requirement derived from SW-TSR (allocation target).
- **ASIL:** Automotive Safety Integrity Level (A, B, C, D).
- **SWC:** Software Component (allocation target for SW-SR).
- **Target detection time:** Required timeout/latency for detection of failure (part of timing budget).
- **Failure modes:** SW-specific failures (deadline miss, illegal state, divide-by-zero, array bounds, null pointer, data corruption, timing violation).
- **MC/DC:** Modified Condition/Decision Coverage (verification method; mandatory for ASIL D per 26262-6 Table 10).

---

## Verification Assessment (VA) — External + SW-SR-specific

### VA.1–VA.3 Planning & Specification (24–32)

| ID | Obligation | Requirement | Rating Logic | Confidence |
|----|-----------|-------------|--------------|-----------|
| **24** | Shall | Verification Plan ensures compliance with SW-SRs | Always draft (external Verification Plan doc) | Low |
| **25** | Should | Validation refined based on SW-TSRs (if applicable) | NA (belongs to TSC/validation review) | High |
| **26** | Shall | Verification Plan addresses content, methods, criteria, env, tools | Always draft (external plan doc) | Low |
| **26a** | Shall | Content of work product(s) to be verified | Always draft (external plan doc) | Low |
| **26b** | Shall | Methods to be used | Always draft (external plan doc) | Low |
| **26c** | Shall | Pass/fail criteria | Always draft (external plan doc) | Low |
| **26d** | Shall | Verification environment (if applicable) | Always draft (external plan doc) | Low |
| **26e** | Shall | Tools used for verification (if applicable) | Always draft (external plan doc) | Low |
| **26f** | Shall | Actions when anomalies are detected | Always draft (external plan doc) | Low |
| **26g** | Shall | Regression strategy | Always draft (external plan doc) | Low |
| **27** | Should | Planning considers method adequacy, complexity, experience, maturity | Always draft (external plan doc) | Low |
| **28** | Shall | Review/analysis checklists or test cases specified | Always draft (external Verification Spec) | Low |
| **29** | Shall | For testing, specification includes required elements | Always draft (external Verification Spec) | Low |
| **30** | Shall | Test cases grouped by method with environment and dependencies | Always draft (external Verification Spec) | Low |
| **31** | Shall | Verification executed per plan and specification | Always draft (external Verification Report) | Low |
| **32** | Shall | Verification Report includes required elements | Always draft (external Verification Report) | Low |

### VA.2 SW-SR-specific items (33a–e)

| ID | Obligation | Requirement | Rating Logic | Confidence |
|----|-----------|-------------|--------------|-----------|
| **33a** | Shall | Completeness of SW-SR coverage | FC if count >= 5; LC if 1-4; NO if 0 | High |
| **33b** | Shall | Consistency of ASIL assignments with parent SWs-TSRs | FC if all SRs have ASIL; NO if none | High |
| **33c** | Shall | Consistency with HSI specifications and signal definitions | Draft with Low confidence; reviewer verifies alignment with HSI | Low |
| **33d** | Shall | Completeness of SWC mapping | FC if distinct SWCs > 0; NO if 0 | High |
| **33e** | Shall | Completeness of requirement attributes (text, ASIL, SWC, detection time) | FC if >= 99% have all four attributes; PC else | High |

**Note:** VA 33a–e are the only VA checks that are SW-SR-specific and machine-verifiable. All other VA checks (24–32) are external and marked Pending awaiting manual verification against the project's Verification Plan and Report.

---

## Standard Tab Structure

SW-SR workbooks following sw-safety-reqs-builder format have 10 tabs:

| Tab # | Name | Content | Checks Reference |
|-------|------|---------|-------------------|
| 0 | 00_Title_Page | Title, author, approver, revision, status, project, linked TSC | CR 4a, 4b, 4c, 4e, 5 |
| 1 | 01_Document_Control | Change history, version control | CR 4d |
| 2 | 02_SW_TSRs_From_TSC | Imported SW-TSRs (parent requirements) | SWSRA 1, 2 |
| 3 | 03_SW_Safety_Requirements | SW-SR catalog (id, parent_tsr, asil, allocated_swc, text, target_detection_time, verification_method) | SWSRA 3–6, 8; VA 33a, 33b, 33d, 33e |
| 4 | 04_Failure_Mode_Mapping | Failure modes and their mapping to SRs | SWSRA 7 |
| 5 | 05_HSI_Reference | Hardware-Software Interface references | SWSRA 12 (implicit); VA 33c |
| 6 | 06_Verification_Methods_per_ASIL | Verification methods per ASIL level | SWSRA 9 |
| 7 | 07_MISRA_Mapping | MISRA C:2012 rule mappings | SWSRA 12 |
| 8 | 08_Test_Strategy | Test strategy (topics, approaches) | SWSRA 10 |
| 9 | 09_Independence_Considerations | Independence arguments (if cascading decomposition) | SWSRA 11 |

---

## Abbreviations & Terminology

- **CR:** Confirmation Review (document-quality checks)
- **SWSRA:** SW Safety Requirements Assessment (ISO 26262-6 §6 checks)
- **VA:** Verification Assessment (external + SW-SR-specific)
- **FC:** Fully Compliant (requirement met; evidence cited)
- **LC:** Largely Compliant (mostly met; minor gaps)
- **PC:** Partially Compliant (significant gaps; corrective action needed)
- **NO:** Not Compliant (requirement not met; blocker)
- **NA:** Not Applicable (requirement does not apply)
- **SW-TSR:** Technical Safety Requirement (from TSC; parent)
- **SW-SR:** Software Safety Requirement (derived from SW-TSR; allocation target)
- **SWC:** Software Component (functional partition)
- **ASIL:** Automotive Safety Integrity Level (A=QM, B, C, D=highest)
- **MC/DC:** Modified Condition/Decision Coverage (structural test method)
