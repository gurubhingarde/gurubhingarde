# HW-SR Checklist — Substantive Checks

## Confirmation Review (14 doc-quality checks)

| ID | Requirement | Source | Auto-fill? |
|----|-------------|--------|-----------|
| 1 | Document structured (headlines, templates) | ISO 26262-8 §10 | FC if ≥5 tabs; else PC |
| 2 | Latest template used at creation | ISO 26262-8 §10 | Draft (Low confidence) |
| 3 | Structure facilitates search (TOC, index) | ISO 26262-8 §10 | FC if TOC + References; else PC |
| 4a | Title covers scope | ISO 26262-8 §10 | Draft (Low) if title found; else NO |
| 4b | Author and approver listed | ISO 26262-8 §10 | FC if both; else NO |
| 4c | Unique revision identification | ISO 26262-8 §10 | FC if Revision field; else NO |
| 4d | Change history available | ISO 26262-8 §10 | Draft (Low) |
| 4e | Work product status provided | ISO 26262-8 §10 | FC if Status field; else NO |
| 5 | Current revision identifiable | ISO 26262-8 §10 | FC if Revision; else NO |
| 6 | Document under configuration management | ISO 26262-8 §10 | Draft (Low) |
| 7 | Header and footer updated | ISO 26262-8 §10 | Draft (Low) |
| 8 | Table of contents present | ISO 26262-8 §10 | FC if TOC tab in first 3; else PC |
| 9 | Reference table lists references | ISO 26262-8 §10 | Draft (Low) |
| 10 | All sections completed | ISO 26262-8 §10 | FC if ≥95% complete; LC if ≥70%; else PC |

---

## HW Safety Requirements Assessment (12 substantive checks)

| ID | Requirement | ISO 26262 § | Confidence | Auto-fill? |
|----|-------------|-------------|------------|-----------|
| 1 | HW-TSRs successfully imported from TSC (count > 0) | 26262-5 §6.2 | High | FC if count > 0; else NO |
| 2 | At least one HW-SR per HW-TSR (no orphans) | 26262-5 §6.2 | High | FC if all TSRs have ≥1 SR; else PC |
| 3 | ASIL assigned to each HW-SR; consistent with parent TSR | 26262-5 §6.3 | High | FC if 99% have ASIL; else PC |
| 4 | HW element allocated to each HW-SR (no <TBD>) | 26262-5 §6.3 | High | FC if 99% allocated; else PC |
| 5 | Requirement text present (no empty rows) | 26262-5 §6.3 | High | FC if 99% have text; else PC |
| 6 | Target DC% specified per HW-SR | 26262-5 §6.5 | High | FC if 99% have DC; else PC |
| 7 | Failure mode mapping covers standard classes per element type | 26262-5 Annex D | Medium | FC if ≥10 rows; LC if >0; else NO |
| 8 | ≥1 verification method per HW-SR | 26262-5 §6.6 | High | FC if 99% have method; else PC |
| 9 | Verification methods appropriate for ASIL (++ for D per Table 21) | 26262-5 §6.6 | Low | Draft (subjective) |
| 10 | Test strategy covers HIL, fault injection, electrical, environmental | 26262-5 §6.7 | Medium | FC if ≥6 rows; LC if >0; else NO |
| 11 | Independence considerations documented (if FSC cascades) | 26262-5 §6.4 | Medium | Draft or FC if > 0 docs |
| 12 | HSI references where HW-SR involves HW→SW signal | 26262-5 §6.2 | Medium | Draft or FC if > 0 refs |

---

## Verification Assessment (22 checks; 5 HW-SR-specific)

### External Checks (verified against Verification Plan, Spec, Report)

| ID | Item | Notes |
|----|------|-------|
| 24 | Verification Plan ensures HW-SR compliance | External |
| 25 | Validation refined based on HW-TSRs | External; TSC-related |
| 26 | Verification Plan addresses content, methods, criteria, env, tools, anomalies, regression | External |
| 26a–g | Plan content details | All External |
| 27 | Planning considers method adequacy, complexity, experience, maturity | External |
| 28 | Review/analysis checklists, simulation, or test cases specified | External |
| 29 | Test case specification includes required elements | External |
| 30 | Test cases grouped by method with env/dependencies/resources | External |
| 31 | Verification executed per plan | External |
| 32 | Verification Report includes required elements | External |

### HW-SR-Specific Checks (33a–e)

| ID | Requirement | Auto-fill? |
|----|-------------|-----------|
| 33a | **Completeness of HW-SR coverage** | FC if ≥5 SRs; LC if >0; else NO |
| 33b | **Consistency of ASIL with parent HW-TSRs** | FC if all have ASIL; else PC/NO |
| 33c | **Consistency with HSI specifications** | Draft (external: HSI doc) |
| 33d | **Completeness of HW element mapping** | FC if all SRs mapped; else PC/NO |
| 33e | **Completeness of requirement attributes** (text, ASIL, element, DC) | FC if ≥99%; else PC |

---

## How Checks Are Applied

### Count-Based Checks
- **ASIL assigned:** Count HW-SRs with non-empty ASIL column; compute %; threshold 99% → FC
- **Element allocated:** Count HW-SRs with non-empty, non-<TBD> HW element; threshold 99% → FC
- **Failure mode mapping:** Count rows in Failure Mode Mapping sheet; threshold ≥10 → FC

### Presence-Based Checks
- **HW-TSR import:** If count > 0 → FC; else NO
- **Verification method:** Count SRs with method ≥ 1; threshold 99% → FC

### Heuristic Checks
- **Test strategy:** Count rows in Test Strategy sheet; sample topics; threshold ≥6 → FC
- **Independence:** Count documentation rows; if > 0 → FC; else Draft
- **HSI references:** Count rows; if > 0 → FC; else Draft

### Subjective/External Checks
All marked with Low confidence and "(Auto-suggest, requires reviewer judgment)" prefix.

---

## Thresholds

| Metric | Threshold for FC | Threshold for LC | Below LC = PC |
|--------|------------------|------------------|--------------|
| Attribute completion (ASIL, element, text, DC) | ≥99% | ≥95% | <95% |
| Failure mode mapping rows | ≥10 | ≥1 | 0 |
| Test strategy rows | ≥6 | ≥1 | 0 |
| Section completion | ≥95% | ≥70% | <70% |

---

## References

- **ISO 26262-5:2018** — Product development at system level, hardware design & verification
  - Section 6: "Hardware requirements"
  - Section 6.2: "HW-SR catalog, TSR derivation"
  - Section 6.3: "ASIL, HW-element allocation"
  - Section 6.5: "Diagnostic coverage"
  - Section 6.6: "Verification methods"
  - Section 6.7: "Test strategy"
  - Annex D: "Failure mode classes"
  - Table 21: "Verification method adequacy per ASIL"

- **ISO 26262-8:2018** — Functional safety (confirmation review framework)
  - Section 10: "Confirmation review for HW"

- **ISO 26262-3:2018** — Concept phase (safety goals from HARA, architecture)
