# Methodology — Safety Case Checklist Reviewer

## Scoring Conventions

The checklist uses a six-level rating system for each check:

| Rating | Meaning | Typical Action |
|--------|---------|-----------------|
| **FC** | Fully Compliant | Requirement is met. No action required. |
| **LC** | Largely Compliant | Requirement is substantially met with minor gaps. Document the gaps; consider corrective actions. |
| **PC** | Partially Compliant | Requirement is partially met; significant gaps exist. Corrective action recommended before acceptance. |
| **NO** | Not Compliant | Requirement is not met. Corrective action required. |
| **NA** | Not Applicable | Requirement does not apply in this context. (E.g., "Tool Qualification" NA if no tools used.) |
| **—** (blank) | Pending Review | Subjective check or external artifact required; awaiting reviewer judgment. |

## Confidence Levels

Each check carries a Confidence assessment:

| Confidence | Basis |
|-----------|-------|
| **High** | Check is verified directly from the xlsx content (e.g., "Author field is populated with a non-placeholder name"). Machine-verifiable and deterministic. |
| **Medium** | Check is inferred from xlsx content with a reasonable caveat (e.g., "Safety goals are present; reviewer to confirm each aligns with HARA"). Heuristic or pattern-based. |
| **Low** | Check is subjective or depends on external artifacts (e.g., "Signoff blocks exist; reviewer to verify actual signatures or approval status"). Requires human judgment. |

## Obligation Levels

Checks are classified as **Shall** (mandatory) or **Should** (recommended):

| Obligation | Meaning |
|-----------|---------|
| **Shall** | Mandatory per ISO 26262-2 §6.5 or ISO 26262-8 §9. Non-compliance ("NO" rating) is a major non-conformance and blocks acceptance. |
| **Should** | Recommended best practice. Non-compliance is a minor issue; may be addressed through corrective actions or waived with documented justification. |

## Three Checklist Domains

### 1. Confirmation Review (CR) — Document Quality (14 checks)

Generic document-quality checks per ISO 26262-8 §10, applied to the Safety Case workbook:
- Structure, template compliance, title/author/status, TOC, references
- Completion of all major sections
- Configuration management and headers/footers

These are **primarily Should checks**; non-compliance indicates document hygiene issues but may not prevent Safety Case acceptance if substantive checks (SCA) pass.

### 2. Safety Case Assessment (SCA) — Argument Chain Verification (12 checks)

Substantive checks per ISO 26262-2 §6.5 verifying the argument chain is complete and traceable:
- Top claim stated with context and justifications
- Sub-claims per safety goal with ASIL assignment
- FSR-TSR traceability (no orphans)
- HW metrics (SPFM/LFM/PMHF) per safety goal
- SW verification status documented
- Tool qualification with TCL levels
- Confirmation review status and independence levels (must match ASIL)
- Open items risk-assessed and accepted
- Signoff blocks (FSM, PM, Assessor)
- References to linked artifacts (HARA, FSC, TSC, FMEDA)

These are **all Shall checks**. Non-compliance blocks Safety Case acceptance.

### 3. Verification Assessment (VA) — External Verification (5 checks)

Checks that rely on external verification documents (Verification Plan, test reports):
- Verification Plan exists and addresses all safety goals
- Verification methods and test cases specified
- Test results and pass/fail status documented
- Verification coverage of safety goals complete
- Argument chain traceability (FSR → HW metrics → SGs)

Most of these are Pending because they require review of documents outside the Safety Case xlsx.

## Auto-fill Rules

### Machine-Verifiable Checks

Checks marked **High Confidence** are verified algorithmically:
- Tab presence/absence (structure checks)
- Row counts and completeness percentages (sections completed)
- Cell population (author, status, revision fields)
- Keyword matching (e.g., "Qualified" in tool qualification status)

Result: FC, LC, PC, or NO based on exact content.

### Subjective Checks

Checks marked **Low Confidence** require reviewer judgment:
- Whether document scope is correctly covered by title
- Whether independent reviewers actually reviewed (signoff presence only; actual signatures not verifiable)
- Whether verification plan is adequate

Result: Drafted finding with "(Auto-suggest, requires reviewer judgment)" preface; Assessment left blank (—) pending reviewer's decision.

## Recommended Workflow

1. **Generate the checklist** from the Safety Case xlsx.
2. **Review the Summary tab** first to get the big picture (compliance %, major issues).
3. **Triage the Confirmation Review tab** — fix obvious doc-quality issues (missing title, author, revision).
4. **Focus on the Safety Case Assessment tab** — these are the substantive checks. Any PC or NO items require corrective action or documented waiver.
5. **Confirm the argument chain** — spot-check that top claim → safety goals → FSRs → HW metrics → SGs is traceable.
6. **Update the Safety Case** based on Recommended Actions.
7. **Re-run the checklist** to verify improvements.
8. **Mark each check** in the output checklist with the reviewer's final Assessment (FC, LC, PC, NO, or NA).

## What the Skill Does NOT Do

- **Does not modify the source Safety Case.** All corrective actions are recommendations; the analyst decides whether to update the Safety Case.
- **Does not verify external artifacts.** Verification Plans, test reports, HARA/FSC/TSC documents are assumed to exist and are not checked.
- **Does not sign off on behalf of the reviewer.** The skill is an audit tool, not a substitute for an independent confirmation review.
- **Does not verify actual compliance with ASIL requirements** (e.g., SPFM/LFM/PMHF numeric targets). The checklist verifies that values are populated and referenced; validators must verify correctness.

## Scoring Notes

- A Safety Case with all checks marked FC is "Fully Compliant" and ready for acceptance.
- A Safety Case with LC items is "Largely Compliant"; minor corrective actions or justifications are needed.
- A Safety Case with any SCA check marked NO is "Not Compliant" and blocks acceptance. CR checks marked NO are lower priority.
- Pending checks indicate missing information; the reviewer must make a judgment before final acceptance.
