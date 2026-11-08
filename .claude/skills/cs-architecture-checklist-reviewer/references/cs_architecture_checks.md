# CS Architecture Assessment Checks

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

**13. Traceability Matrix**: Is CSR-to-element mapping shown?
- Evidence: 09_CSR_to_Element_Allocation tab.

**14. Review/Approval**: Are review and approval signatures/fields present?
- Evidence: Author and Approver populated.

## Functional Safety Assessment (14 checks)

**1. CS Element Catalog Populated**: Are security-relevant elements enumerated?
- Evidence: 03_CS_Element_Catalog row count >= 1.

**2. Supplier + Certification**: Do ASIL/CAL-relevant elements have supplier and certification data?
- Evidence: Supplier and Certification columns for ASIL/CAL rows.

**3. Approved Cryptographic Algorithms**: Are only approved algorithms used (no MD5, SHA1, DES, RC4)?
- Evidence: 04_Cryptographic_Inventory scanned for banned algorithms.

**4. Minimum Key Lengths**: Do crypto algorithms meet minimum key length requirements?
- Subjective; requires external specification review.

**5. Key Management Lifecycle**: Is key generation, storage, distribution, rotation, and destruction defined per key class?
- Evidence: 05_Key_Management populated.

**6. Secure Boot Chain**: Is root-of-trust identified and anti-rollback mechanism present?
- Evidence: 06_Secure_Boot_Chain tab content.

**7. Secure Communication**: Are communication channels documented with authentication, encryption, integrity, and replay protection?
- Evidence: 07_Secure_Communication row count and attributes.

**8. Access Control**: Are roles, privileges, and authentication factors documented?
- Evidence: 08_Access_Control populated.

**9. CSR-to-Element Allocation**: Is the allocation matrix complete (no orphan CSRs)?
- Evidence: 09_CSR_to_Element_Allocation coverage.

**10. Defense in Depth**: Are multiple protective layers defined per attack vector?
- Evidence: 10_Defense_in_Depth_Layers populated.

**11. Debug Interfaces**: Are debug interfaces disabled in production?
- Subjective; requires architectural specification review.

**12. Certificate Management**: Are expiry and renewal plans documented for crypto certificates?
- Subjective; requires external plan reference.

**13. HSM/Secure Element**: Is hardware security module or secure element usage justified for key storage?
- Subjective; requires security analysis.

**14. Standards References**: Are references to CS Concept, AUTOSAR, and applicable standards present?
- Evidence: 11_References tab or similar.

## Verification Assessment (14 checks)

**1–12. Verification Planning, Specification, Execution, Evaluation**: External artifact verification (refer to Verification Plan, Specification, and Report).

**13. Review/Approval**: Are reviewers qualified and independent?
- Evidence: Approver field and organizational independence.

**14. Quality Metrics**: Are KPIs and quality metrics tracked?
- Subjective; requires external dashboard or report reference.
