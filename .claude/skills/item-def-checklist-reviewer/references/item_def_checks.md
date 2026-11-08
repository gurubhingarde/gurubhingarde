# Item Definition Checklist — Substantive Checks Reference

## Overview

The Item Definition Checklist comprises 24 checks split across three categories:
- **Confirmation Review (CR)** — 10 checks on document structure and quality (ISO 26262-8 §10)
- **Item Definition Assessment (IDA)** — 10 checks on substantive Item content (ISO 26262-3 §5)
- **Verification Assessment (VA)** — 3 checks on verification readiness (ISO 26262-8 §9)

## Confirmation Review (CR) — Document Quality Checks

### CR-1: Document Structure
- **Obligation:** Shall
- **Requirement:** Document is organized into distinct tabs
- **Confidence:** High — counts sheet tabs in workbook
- **What it checks:** Minimum of 8 tabs present (Title, Doc Control, Description, Functions, NFR, Boundary, Interfaces, Modes)
- **Pass criteria:** FC if ≥8 tabs; PC if fewer
- **Recommended action:** Add missing tabs per item-definition-builder template

### CR-2: Template Compliance
- **Obligation:** Should
- **Requirement:** Item Definition is based on latest applicable template
- **Confidence:** Low — cannot detect template version from xlsx
- **What it checks:** Drafts a finding for human review
- **Pass criteria:** Pending; reviewer confirms template version
- **Recommended action:** Confirm latest Item Definition template was used

### CR-3: Search Aids
- **Obligation:** Should
- **Requirement:** Document includes Table of Contents and References
- **Confidence:** Medium — checks for tab count and structure
- **What it checks:** Document has ≥5 tabs and structured layout
- **Pass criteria:** FC if good structure; PC if minimal
- **Recommended action:** Add Table of Contents tab for navigation

### CR-4a: Title and Scope
- **Obligation:** Shall
- **Requirement:** Item title clearly describes scope
- **Confidence:** Medium — checks that Title field is populated
- **What it checks:** Title cell on Title page is non-empty
- **Pass criteria:** Pending (human confirms adequacy); NO if missing
- **Recommended action:** Add descriptive Item title to Title page

### CR-4b: Author and Approver
- **Obligation:** Shall
- **Requirement:** Author and Approver are identified
- **Confidence:** High — checks Title page fields
- **What it checks:** Both Author and Approver fields are populated
- **Pass criteria:** FC if both present; NO if either missing
- **Recommended action:** Populate Author and Approver on Title page

### CR-4c: Revision Identification
- **Obligation:** Shall
- **Requirement:** Revision is uniquely identified
- **Confidence:** High — checks Revision field
- **What it checks:** Revision field is non-empty
- **Pass criteria:** FC if populated; NO if missing
- **Recommended action:** Populate Revision field with unique identifier

### CR-4d: Change History
- **Obligation:** Shall
- **Requirement:** Change history is documented
- **Confidence:** Low — cannot verify from xlsx content
- **What it checks:** Drafts a finding for human review
- **Pass criteria:** Pending; reviewer confirms Document Control tab has history
- **Recommended action:** Document revision history in 01_Document_Control

### CR-4e: Document Status
- **Obligation:** Shall
- **Requirement:** Status (Draft, Released, etc.) is identified
- **Confidence:** High — checks Status field
- **What it checks:** Status field is non-empty
- **Pass criteria:** FC if populated; NO if missing
- **Recommended action:** Populate Status field on Title page

### CR-5: Current Revision
- **Obligation:** Shall
- **Requirement:** Item Definition reflects current revision
- **Confidence:** Low — external knowledge required
- **What it checks:** Drafts a finding for human review
- **Pass criteria:** Pending; reviewer confirms this is the current version
- **Recommended action:** Confirm no newer version exists

### CR-6: Configuration Management
- **Obligation:** Shall
- **Requirement:** Item Definition is under configuration management
- **Confidence:** Low — external artifact (version control system)
- **What it checks:** Drafts a finding for human review
- **Pass criteria:** Pending; reviewer confirms Item is baselined and tracked
- **Recommended action:** Confirm Item Definition is in configuration management system

### CR-7: Header and Footer
- **Obligation:** Should
- **Requirement:** Printed version has header/footer with ID, revision, page numbers
- **Confidence:** Low — cannot verify from xlsx
- **What it checks:** Drafts a finding for human review
- **Pass criteria:** Pending; reviewer confirms when printing
- **Recommended action:** Add header/footer to printed version

### CR-8: Table of Contents
- **Obligation:** Should
- **Requirement:** Table of Contents lists sections with tab references
- **Confidence:** Low — cannot detect TOC from xlsx
- **What it checks:** Drafts a finding for human review
- **Pass criteria:** Pending; reviewer confirms TOC presence
- **Recommended action:** Add dedicated Table of Contents tab

### CR-9: References
- **Obligation:** Shall
- **Requirement:** Applicable standards and references are cited
- **Confidence:** High — checks 10_References tab
- **What it checks:** References tab has ≥1 entry
- **Pass criteria:** FC if references present; NO if missing
- **Recommended action:** Add References tab citing ISO 26262, vehicle specs, etc.

### CR-10: Sections Complete
- **Obligation:** Shall
- **Requirement:** All required sections are documented
- **Confidence:** High — counts tabs
- **What it checks:** ≥11 standard tabs present
- **Pass criteria:** FC if ≥11 tabs; PC if fewer
- **Recommended action:** Ensure all tabs (Title, Doc Control, Description, Functions, NFR, Boundary, Interfaces, Modes, Allocation, Assumptions, References) are present

---

## Item Definition Assessment (IDA) — Substantive Checks

### IDA-1: Item Scope and Boundary Clear
- **Obligation:** Shall
- **Requirement:** Item scope is clearly described with distinguishing notes
- **Confidence:** High — checks Scope and Distinguishing_Notes fields
- **What it checks:** Both Scope and Distinguishing_Notes are populated
- **Pass criteria:** FC if both present; LC if Scope present but notes missing; NO if Scope absent
- **Recommended action:** Add distinguishing notes to separate this Item from neighbors

### IDA-2: Functions Enumerated
- **Obligation:** Shall
- **Requirement:** Functions are enumerated with ID, Name, Description
- **Confidence:** High — counts Functions tab entries
- **What it checks:** Functions tab has ≥1 function with name and description
- **Pass criteria:** FC if all functions have descriptions; LC if some missing; NO if no functions
- **Recommended action:** Document all Item functions with complete descriptions

### IDA-3: Non-Functional Requirements Captured
- **Obligation:** Should
- **Requirement:** Non-functional requirements (performance, reliability, usability) documented
- **Confidence:** Medium — checks NFR tab presence
- **What it checks:** NFR tab has ≥1 entry
- **Pass criteria:** FC if NFRs present; PC if missing (may not apply to all Items)
- **Recommended action:** Add Non-Functional Requirements if applicable to Item

### IDA-4: External Interfaces Specified
- **Obligation:** Shall
- **Requirement:** Interfaces have direction and counterpart system identified
- **Confidence:** High — checks Interface Direction and Counterpart fields
- **What it checks:** All interfaces have non-empty Direction and Counterpart
- **Pass criteria:** FC if all specified; LC if incomplete; NO if missing
- **Recommended action:** Complete interface specification (direction, counterpart) in 06_External_Interfaces

### IDA-5: Operating Modes Enumerated
- **Obligation:** Should
- **Requirement:** Operating modes (normal, degraded, fault) are enumerated
- **Confidence:** Medium — checks Modes tab presence
- **What it checks:** Modes tab has ≥1 entry
- **Pass criteria:** FC if modes documented; PC if missing (may not apply)
- **Recommended action:** Add operating modes to 07_Operating_Modes if applicable

### IDA-6: HW/SW/Mech Allocation Specified
- **Obligation:** Should
- **Requirement:** Each function is allocated to HW, SW, or mechanical implementation
- **Confidence:** High — checks Allocation tab
- **What it checks:** Allocation tab entries match function count; HW/SW/Mech fields populated
- **Pass criteria:** FC if all allocated; LC if partial; PC if missing
- **Recommended action:** Complete allocation in 08_Allocation_HW_SW_Mech

### IDA-7: Initial Assumptions Documented
- **Obligation:** Shall
- **Requirement:** Assumptions about vehicle, driver, market, lifecycle are documented
- **Confidence:** High — checks Assumptions tab
- **What it checks:** Assumptions tab has ≥1 entry
- **Pass criteria:** FC if documented; PC if missing
- **Recommended action:** Add assumptions to 09_Initial_Assumptions (vehicle context, driver skills, lifecycle duration, market constraints)

### IDA-8: Item is Distinguishable
- **Obligation:** Shall
- **Requirement:** Item is clearly differentiated from related Items via distinguishing notes
- **Confidence:** High — checks Distinguishing_Notes field
- **What it checks:** Distinguishing notes populated
- **Pass criteria:** FC if notes present; LC if absent
- **Recommended action:** Add notes describing how this Item differs from neighboring Items

### IDA-9: Standards Referenced
- **Obligation:** Shall
- **Requirement:** References to applicable ISO 26262 and vehicle standards present
- **Confidence:** High — checks References tab
- **What it checks:** References tab has ≥1 entry citing standards
- **Pass criteria:** FC if standards cited; NO if missing
- **Recommended action:** Add references to ISO 26262 and applicable vehicle specifications

### IDA-10: HARA Ready
- **Obligation:** Shall
- **Requirement:** Item Definition is suitable as input for HARA (functions, boundary, assumptions present)
- **Confidence:** High — checks Functions, Boundary, and Assumptions tabs
- **What it checks:** All three content areas populated
- **Pass criteria:** FC if all three present; PC if one or more missing
- **Recommended action:** Complete Functions, Boundary/Interfaces, and Assumptions sections

---

## Verification Assessment (VA) — Verification Readiness Checks

### VA-1: Requirement Traceability Matrix
- **Obligation:** Shall
- **Requirement:** Traceability matrix links Item functions to design and test
- **Confidence:** Low — external artifact (Design Spec, Test Plan)
- **What it checks:** Drafts a finding for human review
- **Pass criteria:** Pending; reviewer confirms against Design Spec and Test Plan
- **Recommended action:** Create or verify traceability from Item functions to design requirements and test cases

### VA-2: Design Adequacy
- **Obligation:** Shall
- **Requirement:** Design specification adequately addresses all Item functions and NFRs
- **Confidence:** Low — external artifact (Design Spec)
- **What it checks:** Drafts a finding for human review
- **Pass criteria:** Pending; reviewer confirms Design Spec completeness
- **Recommended action:** Confirm Design Specification covers all Item functions and allocations

### VA-3: Test Coverage
- **Obligation:** Shall
- **Requirement:** Test plan provides adequate coverage for Item functions, edge cases, degraded modes
- **Confidence:** Low — external artifact (Test Plan, Test Report)
- **What it checks:** Drafts a finding for human review
- **Pass criteria:** Pending; reviewer confirms Test Plan comprehensiveness
- **Recommended action:** Confirm Test Plan covers normal, degraded, and fault operating modes
