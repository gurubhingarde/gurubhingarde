# Incident Response Plan Assessment Checks

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

**13. Traceability**: Is IRP process flow documented end-to-end?
- Evidence: Detection → Response → Disclosure → OTA workflow.

**14. Review/Approval**: Are review and approval signatures/fields present?
- Evidence: Author and Approver populated.

## Incident Response Plan Assessment (14 checks)

**1. PSIRT Roster**: Does PSIRT have >= 5 members with 24/7 coverage defined?
- Evidence: 02_PSIRT_Roster populated with role, contact, availability.

**2. Triage Classification**: Are severity levels defined with SLAs (e.g., Critical < 4h, High < 24h)?
- Evidence: 03_Triage_Classification row count >= 3, SLA columns.

**3. Detection Sources**: Are detection sources enumerated (CVE, bug bounty, internal scan, third-party)?
- Evidence: 04_Detection_Sources row count >= 2.

**4. Response Stages**: Are all 6 stages defined (Detect, Triage, Contain, Eradicate, Recover, Post-mortem)?
- Evidence: 05_Response_Workflow row count >= 6.

**5. Coordinated Disclosure**: Is coordinated disclosure policy documented with embargo periods?
- Evidence: 06_Coordinated_Disclosure_Policy populated with researcher notification SLA, embargo duration.

**6. OTA Patch Workflow**: Is OTA patch workflow defined with rollback and regression testing?
- Evidence: 07_OTA_Patch_Workflow with staging → QA → prod steps and rollback procedure.

**7. Regulatory Notification**: Are regulatory notifications defined for UN R155 72h, ENISA, NHTSA, JAMA?
- Evidence: 08_Regulatory_Notifications row count >= 3, regulatory body names.

**8. Customer Communication**: Are customer communication templates/procedures documented?
- Evidence: 09_Customer_Communications row count >= 2, template examples.

**9. Post-Incident Review**: Is post-incident review process documented (timeline, attendees, metrics)?
- Evidence: 10_Post_Incident_Review populated with procedure, RCA, lessons learned template.

**10. Communication Templates**: Are >= 3 templates present (researcher ack, CVE notice, customer bulletin)?
- Evidence: 11_Communication_Templates row count >= 3, template samples.

**11. PSIRT Lead**: Is a named PSIRT lead identified with escalation authority?
- Subjective; requires organizational structure verification.

**12. Legal Review**: Is legal team involved in disclosure and communication review?
- Subjective; requires legal sign-off evidence.

**13. CVSS Scoring**: Is CVSS v3.1 or later used consistently for severity assessment?
- Subjective; requires scoring methodology reference.

**14. Standards References**: Are references to FIRST.org, ISO/SAE 21434, and applicable standards present?
- Evidence: References tab or similar.

## Verification Assessment (14 checks)

**1–12. Verification Planning, Specification, Execution, Evaluation**: External artifact verification (refer to Verification Plan, Specification, and Report).

**13. Review/Approval**: Are reviewers qualified and independent?
- Evidence: Approver field and organizational independence.

**14. Quality Metrics**: Are KPIs and quality metrics tracked?
- Subjective; requires external dashboard or report reference.
