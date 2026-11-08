# FMEDA Checklist Reviewer — Methodology

## Scoring Conventions

| Rating | Meaning | Action Required |
|--------|---------|-----------------|
| **FC** | Fully Compliant | None; evidence verified from FMEDA |
| **LC** | Largely Compliant | Minor findings; review recommended action |
| **PC** | Partially Compliant | Significant gaps; corrective action needed |
| **NO** | Not Compliant | Major non-conformance; blocking issue |
| **NA** | Not Applicable | Requirement does not apply (noted) |
| **(blank)** | Pending Review | Subjective check requiring human judgment |

## Confidence Levels

- **High**: Evidence verified directly from xlsx content (e.g., "Author field populated" ✓)
- **Medium**: Inferred from xlsx with reasonable caveat (e.g., "HW catalog 95% complete")
- **Low** / **Draft**: Subjective or requires external artifact (e.g., "Mission profile consistent with vehicle program" — needs external Item Definition)

## Obligation Levels

- **Shall** (ISO 26262-5 mandatory): Failure to comply is a major non-conformance
- **Should** (ISO 26262-5 recommended): Failure is a minor non-conformance; justification may be acceptable

## Checklist Structure

### Tab 1: **Confirmation Review (CR)** — 14 generic doc-quality checks
Per ISO 26262-8 Section 10:
- Title, author, approver, revision, status
- Document structure, TOC, references
- Section completeness, configuration management

### Tab 2: **FMEDA Assessment (FMEDAA)** — 14 substantive FMEDA checks
Per ISO 26262-5 Section 8:
- Assumptions documented (mission, FIT source, environment)
- HW element catalog complete with FIT
- FMEDA worksheet coverage and distribution sum validation
- Failure mode classification and safety mechanism allocation
- **Metric targets**: SPFM ≥ target, LFM ≥ target, PMHF ≤ target (auto-verify)
- Open items, mission consistency, FIT source justification

### Tab 3: **Verification Assessment (VA)** — 4 external checks
Per ISO 26262-8 Section 9:
- Verification Plan compliance
- Test methods, criteria, environment
- Execution and reporting

## What This Skill Does

✓ **Auto-fills machine-verifiable checks** using content extraction and logic  
✓ **Reads computed metrics** (SPFM, LFM, PMHF) from FMEDA worksheet via openpyxl `data_only=True`  
✓ **Compares metrics against ISO 26262-5 targets** per ASIL (auto-PASS/FAIL for checks #8–10)  
✓ **Drafts subjective findings** for reviewer acceptance/refinement  
✓ **Renders visual dashboard** (pie chart, compliance bars, findings table)  
✓ **Does NOT modify source FMEDA** — all corrections go in Recommended Actions

## What This Skill Does NOT Do

✗ Verify external artifacts (Verification Plan, Test Reports) — those are Pending  
✗ Perform independent FMEDA analysis — it reviews the FMEDA xlsx for completeness  
✗ Validate vendor datasheets or FIT assumptions — that is engineering judgment  
✗ Enforce organization-specific extensions to ISO 26262 — scope is standard compliance

## When Acceptance Is Granted

FMEDA confirmation is complete when:
1. No **Shall** violations (CR, FMEDAA)
2. **Metric targets achieved**: SPFM ≥ target AND LFM ≥ target AND PMHF ≤ target
3. Reviewer confirms **subject checklist items** (mission profile alignment, FIT justification, etc.)
4. Verification Plan is in place (VA checklist Pending until external docs provided)

Per ISO 26262-2 Clause 6.4.7, confirmation review must be performed by an **independent person** (I1), **team** (I2), or **organizational unit** (I3) depending on ASIL.
