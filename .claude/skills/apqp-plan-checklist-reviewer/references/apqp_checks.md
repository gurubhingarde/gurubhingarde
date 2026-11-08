# APQP Plan Checklist — Check Definitions and Rationale

This document details each of the 32 checks run by the APQP Plan Checklist Reviewer skill, organized by tab (Confirmation Review, APQP Assessment, Verification Assessment) with rationale and confidence levels.

---

## Confirmation Review (14 doc-quality checks)

### CR-1: Document Structure
**Requirement**: Is the document structured in a clear manner?  
**Obligation**: Shall  
**Confidence**: High (count tabs)  
**Rationale**: APQP Plans should be organized into distinct logical sections for traceability and review. Minimum: 12 tabs (phases, gates, risks, schedule, team, characteristics, references).

### CR-2: Template
**Requirement**: Was the latest APQP template used?  
**Obligation**: Should  
**Confidence**: Low (subjective)  
**Rationale**: AIAG updates the APQP Manual periodically. Using the latest template ensures alignment with current best practices.

### CR-3: Searchable
**Requirement**: Does the document structure facilitate search?  
**Obligation**: Should  
**Confidence**: Medium (tab naming pattern)  
**Rationale**: Numbered tab names (0x_Section_Name) enable quick navigation and demonstrate organizational discipline.

### CR-4a: Title & Scope
**Requirement**: Does the title cover the scope?  
**Obligation**: Shall  
**Confidence**: Low (subjective)  
**Rationale**: Title must clearly identify what APQP Plan this is (project, program, supplier).

### CR-4b: Author & Approver
**Requirement**: Are author and approver listed?  
**Obligation**: Shall  
**Confidence**: High (presence check)  
**Rationale**: Accountability. Title page must identify responsible parties.

### CR-4c: Unique Revision
**Requirement**: Is there unique identification for each revision?  
**Obligation**: Shall  
**Confidence**: High (presence check)  
**Rationale**: Version control. Enables tracking of plan evolution.

### CR-4d: Change History
**Requirement**: Is there a change history available?  
**Obligation**: Shall  
**Confidence**: Medium (check for Document Control tab)  
**Rationale**: Audit trail. Stakeholders need to know what changed and why.

### CR-4e: Status
**Requirement**: Is the status of the APQP Plan provided?  
**Obligation**: Shall  
**Confidence**: High (presence check)  
**Rationale**: Status (Draft / In Review / Released) indicates approval state.

### CR-5: Current Revision Identifiable
**Requirement**: Is the current applicable revision clearly identifiable?  
**Obligation**: Shall  
**Confidence**: High (presence check)  
**Rationale**: Readers must know they have the current version.

### CR-6: Configuration Management
**Requirement**: Is the document under configuration and change management?  
**Obligation**: Shall  
**Confidence**: Low (external organizational process)  
**Rationale**: APQP Plans are living documents. They must be in version control (Git, Polarion, DOORS, etc.).

### CR-7: Header & Footer
**Requirement**: Are the header and footer updated?  
**Obligation**: Should  
**Confidence**: Low (requires visual inspection of workbook)  
**Rationale**: Headers/footers typically include document ID, revision, date. Helps printed copies stay identifiable.

### CR-8: Table of Contents
**Requirement**: Does the document contain a correct table of contents?  
**Obligation**: Shall  
**Confidence**: High (numbered tab naming indicates TOC-like structure)  
**Rationale**: Large documents need a road map. Numbered tabs serve this purpose.

### CR-9: References
**Requirement**: Does the Reference Table list all references?  
**Obligation**: Should  
**Confidence**: Medium (check for References tab)  
**Rationale**: APQP Plans cite AIAG Manual, IATF 16949, FMEA standards, Control Plan guidelines, OEM requirements. These must be listed.

### CR-10: Sections Complete
**Requirement**: Have all sections of the Work Product been completed?  
**Obligation**: Should  
**Confidence**: High (check for critical tabs)  
**Rationale**: Critical sections: Program Info, Team, Phases 1-5, Schedule, Gates. If key tabs missing → incomplete.

---

## APQP Assessment (12 substantive checks per AIAG APQP Manual + IATF 16949)

### APQPA-1: Program Manager & Quality Lead
**Requirement**: Is the Program Manager and Quality Lead assigned and identified?  
**Obligation**: Shall (AIAG §2.1, IATF 16949)  
**Confidence**: High (field presence)  
**Rationale**: Leadership accountability. APQP requires clear ownership. These roles drive the program and quality strategy.

### APQPA-2: Cross-Functional Team Complete
**Requirement**: Are roles and responsibilities defined for all key positions?  
**Obligation**: Shall (AIAG §2.2)  
**Confidence**: High (team roster with 4+ members and key roles: PM, QE, DE, Mfg, Supplier Quality)  
**Rationale**: APQP is cross-functional. Minimum team: Program Manager, Quality Engineer, Design Engineer, Manufacturing Engineer, Supplier Quality. Without this, key perspectives are missing.

### APQPA-3: Phase 1 Deliverables Complete
**Requirement**: Are Phase 1 deliverables complete (VOC, Business Case, Customer Requirements, Preliminary BOM)?  
**Obligation**: Shall (AIAG §3.1)  
**Confidence**: High (keyword matching on deliverable names)  
**Rationale**: Phase 1 is "Plan and Define." Must capture voice of customer, justify the project, document customer requirements, and identify preliminary components.

### APQPA-4: Phase 2 Includes Design FMEA
**Requirement**: Does Phase 2 include or reference Design FMEA?  
**Obligation**: Shall (AIAG §4.1)  
**Confidence**: High (deliverable name contains "dfmea" or "design fmea")  
**Rationale**: Phase 2 is "Product Design." DFMEA is a mandatory design analysis tool. Must be completed during phase 2 or referenced as external dependency.

### APQPA-5: Phase 3 Includes PFMEA & Control Plan
**Requirement**: Does Phase 3 include Process FMEA and Pre-launch Control Plan?  
**Obligation**: Shall (AIAG §5.1, §5.2)  
**Confidence**: High (deliverable names)  
**Rationale**: Phase 3 is "Process Design." PFMEA analyzes manufacturing risks. Control Plan documents process controls. Both mandatory.

### APQPA-6: Phase 4 Includes MSA & PPAP
**Requirement**: Does Phase 4 include Measurement System Analysis (MSA) and PPAP?  
**Obligation**: Shall (AIAG §6.1, §6.3)  
**Confidence**: High (deliverable names)  
**Rationale**: Phase 4 is "Product and Process Validation." MSA verifies measurement capability. PPAP (Production Part Approval Process) demonstrates manufacturing capability.

### APQPA-7: Phase 5 Feedback Process Defined
**Requirement**: Is Phase 5 feedback/lessons learned process defined?  
**Obligation**: Shall (AIAG §7)  
**Confidence**: High (presence of Phase 5 deliverables)  
**Rationale**: Phase 5 is "Feedback, Corrective Action, and Continuous Improvement." Defines how the team captures lessons and improves processes post-launch.

### APQPA-8: All 5 Gates Scheduled
**Requirement**: Are all 5 APQP gate reviews scheduled?  
**Obligation**: Shall (AIAG §2.3)  
**Confidence**: High (count gate reviews)  
**Rationale**: APQP defines 5 gates: Gate 0 (Design), 1 (Design Verify), 2 (Process), 3 (Validate), 4 (Launch). All must appear on Master Schedule.

### APQPA-9: Gate Exit Criteria Defined
**Requirement**: Does each gate have exit criteria defined?  
**Obligation**: Shall (AIAG §2.3)  
**Confidence**: High (presence of exit criteria field)  
**Rationale**: Gates without criteria are meaningless. Exit criteria make gate passage objective (e.g., "DFMEA complete," "Supplier PPAP approved").

### APQPA-10: Special Characteristics List Maintained
**Requirement**: Is the Special Characteristics (SC/CSC) list maintained?  
**Obligation**: Shall (IATF 16949 §8.3)  
**Confidence**: High (count of SC entries)  
**Rationale**: OEM requirements often identify critical or special characteristics. These must be tracked, controlled, and validated. Absence of this list is a compliance gap.

### APQPA-11: Risk Register Populated
**Requirement**: Is the Risk Register populated with identified risks and mitigations?  
**Obligation**: Shall (AIAG §2.5, IATF risk management)  
**Confidence**: High (risk count and mitigation presence)  
**Rationale**: APQP is a risk-driven process. Risks must be identified and mitigations defined. Empty risk register = inadequate planning.

### APQPA-12: Deliverable Ownership
**Requirement**: Does each deliverable have an assigned owner?  
**Obligation**: Shall (AIAG §3-7)  
**Confidence**: High (owner field presence)  
**Rationale**: Accountability. Every deliverable must have a responsible person/team. Unowned deliverables slip or are forgotten.

---

## Verification Assessment (6 external checks)

### VA-1: Pre-Production Launch Analysis
**Requirement**: Has Pre-Production Launch (PPL) analysis been completed and signed off?  
**Obligation**: Shall (AIAG §7.1)  
**Confidence**: Low (external document)  
**Rationale**: Before full production launch, the team must verify manufacturing readiness. PPL is the formal sign-off gate.

### VA-2: Supplier Manufacturing Capability
**Requirement**: Has the supplier demonstrated manufacturing capability?  
**Obligation**: Shall (IATF 16949 §8.4)  
**Confidence**: Low (external verification)  
**Rationale**: Capability is proven through pilot production, PPAP submission, and performance metrics.

### VA-3: Customer APQP Approval
**Requirement**: Has the customer approved the APQP Plan?  
**Obligation**: Shall (AIAG §1.2)  
**Confidence**: Low (external approval)  
**Rationale**: Customer must accept the program plan before execution. Approval letter or email required.

### VA-4: Prototype/Pilot Results
**Requirement**: Are prototype or pilot build results available and acceptable?  
**Obligation**: Shall (AIAG §4.1, §6.1)  
**Confidence**: Low (external test reports)  
**Rationale**: Prototypes validate design intent. Pilot production validates manufacturing process. Results must show no critical issues.

### VA-5: Field Service Quality Assurance Readiness
**Requirement**: Is Field Service Quality Assurance (FSQA) readiness confirmed?  
**Obligation**: Shall (AIAG §7.2)  
**Confidence**: Low (external FSQA checklist)  
**Rationale**: FSQA teams must be trained, field monitoring plans in place, and contingency processes ready for launch.

### VA-6: Quality Metrics & Reporting
**Requirement**: Are quality metrics and reporting processes defined?  
**Obligation**: Shall (IATF 16949 §8.2)  
**Confidence**: Low (external metrics dashboard)  
**Rationale**: Post-launch success is tracked through KPIs: defect rates, on-time delivery, customer satisfaction. Baseline metrics must be established.

---

## Summary Statistics

| Tab | # Checks | Confidence | Auto-fill rate |
|-----|----------|-----------|-----------------|
| Confirmation Review | 14 | High/Medium | ~70% |
| APQP Assessment | 12 | High/Medium | ~80% |
| Verification Assessment | 6 | Low | ~0% |
| **Total** | **32** | **Mixed** | **~50%** |

**Auto-fill rate** = percentage of checks that are not marked Pending. Low-confidence checks remain Pending for human review.

---

## Audit Trail & Continuous Improvement

Each time the APQP Plan is updated and the skill is re-run, you get a fresh checklist reflecting the current state. This enables:

1. **Gap closure tracking**: Monitor NO → PC → FC progression.
2. **Version comparison**: Compare two checklists to see what improved.
3. **Stakeholder communication**: Dashboard summary shows program readiness at a glance.
4. **Audit readiness**: Final FC checklist serves as audit evidence of APQP compliance.
