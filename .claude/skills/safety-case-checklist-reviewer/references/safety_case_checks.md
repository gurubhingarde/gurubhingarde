# Safety Case Checks — Detailed Definitions

## Confirmation Review — Document Quality (14 checks)

### CR-1: Document Structure
**Requirement:** Is the document structured in a clear manner supporting maintainability?
**Obligation:** Shall
**What it verifies:** The Safety Case workbook has organized tabs covering all major sections (Title, Doc Control, Executive Summary, Item Definition, Top Claim, Safety Goals, FSR-TSR, HW Metrics, SW Verification, Tool Qualification, Confirmation Reviews, Open Items, Argument Notes, Assessment, References).
**How it's checked:** Counts the number of sheets; expects 15 standard tabs.
**Confidence:** High

### CR-2: Template Version
**Requirement:** Was the latest template available used?
**Obligation:** Should
**What it verifies:** Document was created using a current Safety Case template (safety-case-builder or equivalent).
**How it's checked:** Cannot be verified from xlsx content alone. Reviewer must confirm.
**Confidence:** Low

### CR-3: Searchability
**Requirement:** Does the document structure facilitate search (cross-references, index)?
**Obligation:** Should
**What it verifies:** Title page and References tab are present to help navigation.
**How it's checked:** Looks for Title and References tabs.
**Confidence:** Medium

### CR-4a: Title Scope
**Requirement:** Does the title cover the scope of the content?
**Obligation:** Shall
**What it verifies:** A meaningful title is present on the Title page.
**How it's checked:** Extracts title from Title page metadata. Reviewer must confirm it reflects the Safety Case scope.
**Confidence:** Medium

### CR-4b: Author and Approver
**Requirement:** Are the author and approver listed?
**Obligation:** Shall
**What it verifies:** Title page includes Author and Approver fields populated with real names (not placeholders).
**How it's checked:** Extracts Author and Approver from Title page.
**Confidence:** High

### CR-4c: Unique Revision
**Requirement:** Is there unique identification for each revision?
**Obligation:** Shall
**What it verifies:** Revision field on Title page is populated with a version identifier (e.g., "1.0", "Draft A").
**How it's checked:** Extracts Revision from Title page.
**Confidence:** High

### CR-4d: Change History
**Requirement:** Is there a change history available?
**Obligation:** Shall
**What it verifies:** Document Control tab (Tab 01) exists and contains revision history entries.
**How it's checked:** Checks for Tab 01_Document_Control.
**Confidence:** Medium

### CR-4e: Status
**Requirement:** Is the work-product status provided?
**Obligation:** Shall
**What it verifies:** Title page includes a Status field (Draft, In Review, Released, etc.).
**How it's checked:** Extracts Status from Title page.
**Confidence:** High

### CR-5: Current Revision Identifiable
**Requirement:** Is the current applicable revision clearly identifiable?
**Obligation:** Shall
**What it verifies:** Current version of the Safety Case can be uniquely identified (same as CR-4c).
**How it's checked:** Extracts Revision from Title page.
**Confidence:** High

### CR-6: Configuration Management
**Requirement:** Is the document under configuration and change management?
**Obligation:** Shall
**What it verifies:** Document is managed in a version-control system or document repository.
**How it's checked:** Cannot be verified from xlsx content. Reviewer must confirm project practices.
**Confidence:** Low

### CR-7: Headers and Footers
**Requirement:** Are headers and footers updated?
**Obligation:** Should
**What it verifies:** Sheet headers/footers contain document ID and revision (if using Excel features).
**How it's checked:** Cannot be reliably checked programmatically. Reviewer opens in Excel to inspect.
**Confidence:** Low

### CR-8: Table of Contents
**Requirement:** Does the document contain a table of contents?
**Obligation:** Shall
**What it verifies:** Title or General Info tab is present to serve as navigation aid.
**How it's checked:** Looks for Title page tab or contents-like tab in first 3 sheets.
**Confidence:** Medium

### CR-9: References
**Requirement:** Does the Reference Table list all references?
**Obligation:** Should
**What it verifies:** Tab 14_References exists and is populated with citations to HARA, FSC, TSC, FMEDA, tools, etc.
**How it's checked:** Checks for Tab 14 and counts non-empty reference rows (expects 4+).
**Confidence:** Medium

### CR-10: Sections Completed
**Requirement:** Have all sections been completed?
**Obligation:** Should
**What it verifies:** All major sections (Top Claim, Safety Goals, FSR-TSR, Assessment) are present and populated.
**How it's checked:** Verifies presence and population of Tabs 04, 05, 06, 13.
**Confidence:** High

---

## Safety Case Assessment (12 checks per ISO 26262-2 §6.5)

### SCA-1: Top Claim
**Requirement:** Is the top claim stated with context, justifications, and assumptions?
**Obligation:** Shall
**What it verifies:** The root claim of the Safety Case (e.g., "The item meets all ASIL D safety goals") is explicitly documented in Tab 04_Top_Claim.
**How it's checked:** Extracts top claim text from Tab 04. Reviewer confirms context and supporting justifications are documented.
**Confidence:** Medium

### SCA-2: Sub-claims (Safety Goals)
**Requirement:** Is there a sub-claim per safety goal with ASIL assignment?
**Obligation:** Shall
**What it verifies:** Each safety goal from the HARA is represented as a sub-claim in Tab 05_Safety_Goals_Argument with its ASIL.
**How it's checked:** Counts rows in Tab 05 with SG_ID and ASIL populated.
**Confidence:** High

### SCA-3: Strategy and Evidence
**Requirement:** Does each sub-claim have supporting strategy and evidence?
**Obligation:** Shall
**What it verifies:** Each safety goal sub-claim includes a strategy (decomposition into FSRs/TSRs, HW/SW design, verification) and links to supporting evidence.
**How it's checked:** Checks for description/claim text in Tab 05 and linked rows in Tabs 06 (FSR-TSR) and 07 (HW metrics).
**Confidence:** Medium

### SCA-4: FSR-TSR Traceability
**Requirement:** Is FSR-TSR traceability complete with no orphan FSRs?
**Obligation:** Shall
**What it verifies:** All Functional Safety Requirements (FSRs) derived from safety goals are documented in Tab 06_FSR_TSR_Traceability and traced to at least one safety goal (no orphans).
**How it's checked:** Counts FSR rows in Tab 06 and checks traceability_status field (must indicate "Traced" or similar).
**Confidence:** High

### SCA-5: HW Metrics
**Requirement:** Are SPFM/LFM/PMHF metrics reported per safety goal with target compliance?
**Obligation:** Shall
**What it verifies:** Tab 07_HW_Metrics_Summary contains hardware metrics (Single-Point Fault Metric, Latent Fault Metric, Probabilistic Metric of Hazard-causing Failure) for each safety goal ASIL with target values documented.
**How it's checked:** Counts rows in Tab 07 with SG_ID and at least one metric (SPFM/LFM/PMHF) populated. Checks for target compliance statement.
**Confidence:** High

### SCA-6: SW Verification
**Requirement:** Is SW verification status reported?
**Obligation:** Shall
**What it verifies:** Tab 08_SW_Verification_Summary exists and documents the status of SW testing/analysis for each safety goal.
**How it's checked:** Checks for Tab 08 presence and extracts status field (expects "Complete" or similar).
**Confidence:** Medium

### SCA-7: Tool Qualification
**Requirement:** Is tool qualification documented with TCL classification?
**Obligation:** Shall
**What it verifies:** Tab 09_Tool_Qualification lists each tool used in the Safety Case (HARA tool, FSC tool, verification tool, etc.) and documents its Tool Confidence Level (TCL: TQL1, TQL2, TQL3).
**How it's checked:** Checks for Tab 09 presence and extracts tool status/TCL fields.
**Confidence:** Medium

### SCA-8: Confirmation Reviews
**Requirement:** Is confirmation review status complete for all work products?
**Obligation:** Shall
**What it verifies:** Tab 10_Confirmation_Reviews_Status documents that each work product (HARA, FSC, TSC, FMEDA, Safety Case itself) has been reviewed and approved.
**How it's checked:** Counts review rows in Tab 10 with status "Completed" or "Approved".
**Confidence:** High

### SCA-9: Review Independence
**Requirement:** Do confirmation review independence levels match ASIL?
**Obligation:** Shall
**What it verifies:** Reviewer independence levels are appropriate per ISO 26262-2 Table 1 (I1 for QM/A, I2 for B, I3 for C/D).
**How it's checked:** Checks Tab 10 for reviewer independence field values and compares to ASIL.
**Confidence:** Medium

### SCA-10: Open Items Risk Assessment
**Requirement:** Are all open items risk-assessed and accepted with justification?
**Obligation:** Shall
**What it verifies:** Tab 11_Open_Items_Risks documents any outstanding issues and confirms they have been evaluated for risk impact and accepted (with documented rationale) before Safety Case acceptance.
**How it's checked:** Counts open item rows in Tab 11 with risk_level and accepted="Yes" populated.
**Confidence:** High

### SCA-11: Signoff Block
**Requirement:** Does assessment conclusion have signoff blocks (FSM, PM, Assessor)?
**Obligation:** Shall
**What it verifies:** Tab 13_Assessment_Conclusion contains signoff sections for Functional Safety Manager, Project Manager, and independent Assessor to confirm their roles and approval.
**How it's checked:** Looks for signoff/approved keywords in Tab 13. Reviewer verifies actual signatures or approval status.
**Confidence:** Medium

### SCA-12: References to Artifacts
**Requirement:** Are all linked artifacts referenced (HARA, FSC, TSC, FMEDA hashes)?
**Obligation:** Shall
**What it verifies:** Tab 14_References lists all source documents and work products referenced in the Safety Case with document IDs, revision, and hash/checksum (if applicable) for traceability.
**How it's checked:** Counts reference rows in Tab 14 (expects 8+ covering HARA, FSC, TSC, FMEDA, Item Def, Verification Plan, tools, etc.).
**Confidence:** Medium

---

## Verification Assessment (5 Safety Case-specific checks)

### VA-1: Verification Plan
**Requirement:** Does Verification Plan exist and address all safety goals?
**Obligation:** Shall
**What it verifies:** A Verification Plan document exists (external to the Safety Case xlsx) that lists all safety goals and defines how each will be tested or analyzed.
**How it's checked:** Marked Pending; requires review of external Verification Plan document.
**Confidence:** Low (external)

### VA-2: Verification Methods
**Requirement:** Are verification methods and test cases specified?
**Obligation:** Shall
**What it verifies:** The Verification Plan and test specifications define verification methods (test, simulation, review, analysis) and specific test cases for each safety goal.
**How it's checked:** Marked Pending; requires review of external Verification Specification and test documents.
**Confidence:** Low (external)

### VA-3: Verification Results
**Requirement:** Are test results and pass/fail status documented?
**Obligation:** Shall
**What it verifies:** A Verification Report exists documenting the results of all planned tests/analyses with pass/fail status and any anomalies.
**How it's checked:** Marked Pending; requires review of external Verification Report.
**Confidence:** Low (external)

### VA-4: Coverage
**Requirement:** Is verification coverage of safety goals complete?
**Obligation:** Shall
**What it verifies:** Every safety goal is verified (tested or analyzed) with documented evidence of pass/compliance.
**How it's checked:** Marked Pending; requires traceability matrix matching safety goals to test cases and results.
**Confidence:** Low (external)

### VA-5: Argument Chain Traceability
**Requirement:** Is the argument chain traceable (FSR → HW metrics → SGs)?
**Obligation:** Shall
**What it verifies:** The Safety Case documentation provides complete traceability from FSRs through HW verification metrics back to safety goals, confirming the argument chain is intact.
**How it's checked:** Checks for FSR rows in Tab 06 and HW metric rows in Tab 07; verifies cross-references exist.
**Confidence:** Medium

---

## Scoring Summary

| Tab | # Checks | Obligation | Typical Gateway |
|-----|----------|-----------|-----------------|
| CR | 14 | 9 Shall, 5 Should | Minor issue if NC; does not block acceptance by itself |
| SCA | 12 | All Shall | MAJOR GATE: Any NC blocks acceptance |
| VA | 5 | All Shall | Pending is normal (external docs); Pending checks reviewed against Verification Report |

A Safety Case may achieve acceptance with:
- CR: Mostly FC/LC, minor gaps acceptable
- SCA: All FC or LC; any NO item requires corrective action or documented waiver
- VA: Pending checks reviewed externally; test results must show all safety goals verified
