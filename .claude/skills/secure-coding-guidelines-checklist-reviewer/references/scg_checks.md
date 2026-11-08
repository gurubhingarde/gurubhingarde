# Secure Coding Guidelines Assessment Checks

## Confirmation Review (14 checks)

**1. Document Structure**: Is the document organized in a clear, logical manner supporting maintainability?
- Evidence: Sheet names and organization.

**2. Title**: Does the title clearly cover the scope?
- Evidence: Title page field extraction.

**3. Author/Approver**: Are responsible personnel identified?
- Evidence: Author and Approver fields on title page.

**4. Revision**: Is each revision uniquely identified?
- Evidence: Revision field populated.

**5. Status**: Is document status (Draft/Review/Released) provided?
- Evidence: Status field on title page.

**6. Document ID**: Is there a unique document identifier?
- Evidence: Doc ID field extracted.

**7. Table of Contents**: Is a TOC present for navigation?
- Evidence: Title or General Info tab presence.

**8. References**: Are all references listed?
- Evidence: References tab or similar.

**9. Assumptions**: Are scope and assumptions documented?
- Evidence: Assumptions or Scope tab presence.

**10. Cross-References**: Do internal hyperlinks support navigation?
- Subjective; reviewer judgment required.

**11. Searchability**: Can information be located efficiently?
- Evidence: Tab structure and header organization.

**12. Terminology**: Are terms and abbreviations defined?
- Evidence: Glossary or abbreviations section.

**13. Traceability**: Is each rule traced to CERT/MISRA/CWE source?
- Evidence: Cross-references in coding rules catalog.

**14. Review/Approval**: Are review and approval signatures/fields present?
- Evidence: Author and Approver populated.

## Secure Coding Guidelines Assessment (14 checks)

**1. Scope Definition**: Does scope define codebase, language, target CAL/ASIL, and environment?
- Evidence: 02_Scope populated with language, target CAL, environment (embedded, cloud, mobile).

**2. Rules Catalog**: Does coding rules catalog contain >= 30 rules?
- Evidence: 03_Coding_Rules_Catalog row count >= 30.

**3. CERT/MISRA Coverage**: Are CERT C and MISRA Amendment 1 rules mapped?
- Evidence: References to CERT ID (e.g., MEM31-C) and MISRA rule numbers in rules catalog.

**4. AUTOSAR C++14**: If C++ in scope, are AUTOSAR C++14 rules referenced?
- Subjective; requires AUTOSAR rule mapping if C++ language selected.

**5. CWE Top 25 Mapping**: Are CWE Top 25 items mapped to coding rules (>= 20 covered)?
- Evidence: 10_CWE_Top25_Coverage row count >= 20.

**6. Memory Safety Rules**: Are bounds checking, use-after-free, double-free, buffer overflow rules defined?
- Evidence: 04_Memory_Safety_Rules row count >= 4.

**7. Integer Safety Rules**: Are overflow, underflow, sign conversion, bit manipulation rules defined?
- Evidence: 05_Integer_Safety_Rules row count >= 4.

**8. String/IO Safety Rules**: Are string bounds, null termination, format string rules defined?
- Evidence: 06_String_IO_Rules row count >= 3.

**9. Cryptography Rules**: Are only approved algorithms (no MD5, SHA1, DES, RC4) and key management rules defined?
- Evidence: 07_Cryptography_Rules row count >= 3, banned algorithms absent.

**10. Authentication Rules**: Are principle of least privilege and credential management rules defined?
- Evidence: 08_Authentication_Authorization_Rules row count >= 2.

**11. Logging Rules**: Are rules ensuring no secrets/PII logged defined?
- Evidence: 09_Logging_Audit_Rules row count >= 2, sensitive data exclusion rules.

**12. Tool Configuration**: Are Coverity, CodeSonar, or Polyspace rules/configs documented?
- Evidence: 11_Tool_Configuration row count >= 1, tool names listed.

**13. Deviation Process**: Is deviation/exception process documented (approval, tracking)?
- Evidence: 12_Deviation_Process populated with exception procedure.

**14. Standards References**: Are references to CERT C, MISRA, AUTOSAR, CWE, and applicable standards present?
- Evidence: References tab or similar.

## Verification Assessment (14 checks)

**1–12. Verification Planning, Specification, Execution, Evaluation**: External artifact verification (refer to Verification Plan, Specification, and Report).

**13. Review/Approval**: Are reviewers qualified and independent?
- Evidence: Approver field and organizational independence.

**14. Quality Metrics**: Are KPIs and quality metrics tracked?
- Subjective; requires external dashboard or report reference.
