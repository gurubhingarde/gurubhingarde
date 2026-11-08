# PPAP Checks Reference

## Confirmation Review (CR) — 14 doc-quality checks

Document structure, completeness, and professional presentation.

### CR-1: Document Structure
Is the PPAP package structured with clear sections?
- **Checks:** Minimum of 10 tabs; distinct element sections (Title, PSW, Element 1, 3, 4, etc.).
- **Rating:** FC if ≥10 tabs; PC if fewer.

### CR-2: Title Page
Is the title page complete with customer, supplier, part name, part number?
- **Checks:** All four metadata fields populated.
- **Rating:** FC if all present; NO if any missing.

### CR-3: Document Control
Is document control and revision history present?
- **Checks:** 01_Document_Control tab with revision history table.
- **Rating:** Pending (requires reviewer verification).

### CR-4: References
Are references listed (AIAG PPAP Manual, drawing standards, etc.)?
- **Checks:** Dedicated References tab or reference list sheet.
- **Rating:** FC if present; PC if missing or incomplete.

### CR-5: Table of Contents
Is a table of contents provided?
- **Checks:** Title page and ordered sheet structure; optional formal TOC.
- **Rating:** FC if evident; PC if unclear.

### CR-6: Headers and Formatting
Are column headers and formatting clear?
- **Checks:** Column headers visible; consistent font/formatting.
- **Rating:** Pending (requires reviewer judgment).

### CR-7: Approval Authority
Are approval authorities and responsibilities identified?
- **Checks:** PSW signature block, company approval structure.
- **Rating:** Pending.

### CR-8: Submission Level
Is submission level clearly identified (1-5)?
- **Checks:** Submission level stated on title page and PSW.
- **Rating:** FC if clearly stated; NO if missing.

### CR-9: Completeness
Is package completeness evident (all elements accounted for)?
- **Checks:** Heuristic: ≥15 of 18 elements marked submitted.
- **Rating:** FC if ≥90% complete; PC if fewer.

### CR-10: Sign-off
Is the submission sign-off (PSW) authorized?
- **Checks:** PSW signature block populated.
- **Rating:** FC if filled; NO if blank (submission cannot proceed without this).

### CR-11: Worksheet Formatting
Are worksheets professionally formatted?
- **Checks:** Fonts, colors, borders, consistency.
- **Rating:** Pending.

### CR-12: Numerical Accuracy
Are numerical values accurate (no calculation errors)?
- **Checks:** Spot-check dimensional, R&R, and Cpk values for plausibility.
- **Rating:** Pending (requires reviewer spot-checking).

### CR-13: Cross-References
Are cross-references between elements clear?
- **Checks:** Element 4 → Element 6 → Element 7 → Element 8/9/11 traceability.
- **Rating:** Pending.

### CR-14: Retention Plan
Is the retention/archive plan documented?
- **Checks:** PPAP retention schedule per AIAG (typically 5-7 years).
- **Rating:** Pending.

---

## PPAP Assessment (PPAPA) — 14 element-specific checks per AIAG 4th ed

Compliance of each of the 18 submission elements per AIAG PPAP Manual 4th Edition.

### PPAPA-1: PSW Fields
Are all PSW fields populated (part name, number, codes, drawing level/date, declaration)?
- **Checks:** Part Name, Part Number, Supplier Code, Customer Code, Drawing Change Level, Drawing Date, Submission Level, Declaration.
- **Rating:** FC if all present; NO if any missing.
- **Impact:** High. Cannot submit without complete PSW.

### PPAPA-2: Submission Level
Is submission level clearly identified (1-5)?
- **Checks:** Submission level stated; triggers Element Requirements table.
- **Rating:** FC if clear; NO if missing.
- **Impact:** High. Determines which elements are required.

### PPAPA-3: Element 1 (Design Records)
Is Element 1 (Design Records) referenced with drawing number, revision, approval status?
- **Checks:** Customer engineering drawing number, revision, approval status (Released, In Review, etc.).
- **Rating:** FC if drawing number + approval status present; NO if missing.
- **Impact:** High. Foundation for product definition.

### PPAPA-4: Element 4 (DFMEA Reference)
Is Element 4 (Design FMEA) referenced with version/hash?
- **Checks:** DFMEA document reference, version or hash.
- **Rating:** FC if reference present; NO if missing.
- **Impact:** Medium. Demonstrates design-phase risk review.

### PPAPA-5: Element 6 (PFMEA Reference)
Is Element 6 (Process FMEA) referenced with version/hash?
- **Checks:** PFMEA document reference, version or hash.
- **Rating:** FC if reference present; NO if missing.
- **Impact:** Medium. Demonstrates process risk review.

### PPAPA-6: Element 7 (Control Plan Reference)
Is Element 7 (Control Plan) referenced?
- **Checks:** Control Plan document reference.
- **Rating:** FC if reference present; NO if missing.
- **Impact:** Medium. Links FMEA risks to production controls.

### PPAPA-7: Element 8 (MSA Results)
Are Element 8 (MSA R&R) results present and acceptable (all gages ≤30%)?
- **Checks:** Gage name, R&R % calculated or provided.
- **Flag:** Any gage with R&R > 30% (measurement system is inadequate).
- **Rating:** FC if all ≤30%; PC if any >30%; NO if no MSA data.
- **Impact:** High. Out-of-control gages → dimensional data unreliable.

### PPAPA-8: Element 9 (Dimensional Results)
Are Element 9 (Dimensional) results populated with all characteristics in spec?
- **Checks:** Characteristic name, nominal, tolerance limits, measured value.
- **Flag:** Any characteristic out-of-spec (measured < lower tolerance or > upper tolerance).
- **Rating:** FC if all in spec; PC if any out-of-spec; NO if no dimensional data.
- **Impact:** High. Out-of-spec dims → parts do not meet customer requirements.

### PPAPA-9: Element 11 (Process Capability)
Are Element 11 (Process Capability) values adequate (Cpk/Ppk ≥1.33)?
- **Checks:** Characteristic name, Cpk and/or Ppk values.
- **Flag:** Any characteristic with Cpk or Ppk < 1.33 (low process capability).
- **Rating:** FC if all ≥1.33; PC if any <1.33; NO if no capability data.
- **Impact:** High. Low Cpk/Ppk → high defect rate risk.

### PPAPA-10: Element 12 (Lab Documentation)
Are Element 12 (Lab) reports from accredited labs (A2LA / ISO 17025)?
- **Checks:** Lab name, A2LA or ISO 17025 accreditation status.
- **Rating:** FC if accreditation evident; PC if lab name present but accreditation unclear; NO if no lab data.
- **Impact:** Medium. Accreditation ensures competency and traceability.

### PPAPA-11: Element 17 (Customer-Specific Requirements)
Are Element 17 (Customer-Specific) requirements addressed with evidence?
- **Checks:** Requirement text and evidence/test data for each customer requirement.
- **Rating:** FC if all requirements have evidence; PC if evidence missing; NO if no requirements listed.
- **Impact:** High. Customer requirements are non-negotiable.

### PPAPA-12: Element 18 (Submission Status Matrix)
Is Element 18 (Submission Status Matrix) complete for the selected level?
- **Checks:** Element status column populated (Submitted, Not Required, Not Applicable).
- **Rating:** FC if ≥90% of applicable elements marked; PC if <90%; NO if matrix absent.
- **Impact:** High. Provides checklist of all submission elements.

### PPAPA-13: Required Elements per Level
Are all required elements per submission level marked submitted?
- **Checks:** Level-to-element mapping per AIAG PPAP:
  - Level 1: 1, 3, 8, 10, 13, 15, 16 (7 elements)
  - Level 2: adds 4, 5, 7, 9, 14, 18 (13 elements)
  - Level 3: all 1-18 (18 elements)
- **Rating:** FC if all required elements present; NO if any required element missing.
- **Impact:** High. Non-compliance with level requirements = rejection.

### PPAPA-14: PSW Signature Block
Is PSW signature block completed?
- **Checks:** Authorized representative signature and date on PSW.
- **Rating:** FC if filled; NO if blank.
- **Impact:** Critical. Submission cannot proceed without authorization.

---

## Verification Assessment (VA) — 5 external reference checks

Confirmation that upstream artifacts exist and are current.

### VA-1: Drawing Under Change Control
Is the customer drawing under formal change control?
- **Checks:** Drawing number, revision, ECN/change log, approval authority.
- **Confidence:** Pending (requires access to customer drawing system).

### VA-2: Material Certifications
Are material certifications provided?
- **Checks:** Material test reports, 3.1 certs per ASTM/ISO.
- **Confidence:** Pending.

### VA-3: Sample Approval
Has the customer approved production sample parts?
- **Checks:** Customer sign-off on first article or pre-production sample.
- **Confidence:** Pending (requires email/document from customer).

### VA-4: FAR Data
Is first article run (tooling qualification) data documented?
- **Checks:** FAR report, tooling first-part report, or equivalent.
- **Confidence:** Pending.

### VA-5: FMEA Closure
Are FMEA corrective actions closed?
- **Checks:** DFMEA and PFMEA action items marked complete/verified.
- **Confidence:** Pending (requires access to FMEA documents).

---

## Headline findings to report to user

The skill automatically flags and summarizes these critical issues:

1. **Out-of-spec dimensional results:** Count and list of characteristics outside tolerance.
   - **Action required:** Investigate root cause (measurement error, material deviation, process drift). Correct and re-sample.

2. **Low process capability (Cpk/Ppk < 1.33):** Count and list of characteristics below threshold.
   - **Action required:** Improve process (tooling, process parameters, material control). Re-run process study.

3. **High MSA R&R (> 30%):** Count and list of gages above threshold.
   - **Action required:** Repair or replace gage. Re-run MSA.

4. **Missing PSW signature:** Submission cannot proceed.
   - **Action required:** Obtain authorized representative signature.

5. **Missing required elements per level:** Specific elements not marked submitted.
   - **Action required:** Obtain missing element and mark submitted.

---

## Integration with ppap-package-builder

The `ppap-package-builder` skill creates the PPAP xlsx with all 22 tabs and element references. The `ppap-checklist-reviewer` skill then reviews that output against the 33 checks in this reference document. The two skills work in tandem: builder → reviewer → feedback loop → re-run builder if needed.
