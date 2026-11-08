# Safety Plan Checklist Reviewer — Methodology

## Scoring Conventions

The skill produces five ratings per ISO 26262 confirmation-measures conventions:

| Rating | Definition | When to use |
|--------|-----------|-------------|
| **FC** (Fully Compliant) | All evidence verified; no gaps; high confidence. | Direct, unambiguous match against the requirement. Example: "All 5 roles with FSM assigned" |
| **LC** (Largely Compliant) | Most evidence present; minor gaps; medium confidence. | Substantial compliance with minor refinement needed. Example: "8 of 10 work products have owners assigned" |
| **PC** (Partially Compliant) | Some evidence present; significant gaps; medium confidence. | Compliance path clear but material work remains. Example: "Half of tailoring decisions have justifications" |
| **NO** (Not Compliant) | Evidence missing or directly contradicts requirement. | High-confidence gap that requires correction. Example: "No Functional Safety Manager assigned" |
| **NA** (Not Applicable) | Requirement does not apply to this Safety Plan. | Rare; only when a clause is explicitly excluded by tailoring. |
| **(blank)** | Pending human review; auto-fill was not possible. | Subjective judgment required; reviewer will assign. Example: "Configuration management is external" |

## Confidence Levels

Each auto-fill finding includes a Confidence level to indicate how much the reviewer should trust it without re-verification:

| Confidence | Basis | Example |
|------------|-------|---------|
| **High** | Directly verified from xlsx content; no interpretation. | "Author field equals 'Jane Doe'" (cell count, exact match) |
| **Medium** | Inferred from xlsx with reasonable caveat. | "Work products present; reviewer to check against Item Definition" (heuristic: ≥ 3 WPs named HARA, FSC, TSC) |
| **Low** | Subjective or requires external artifact to verify. | "Anomaly resolution process described" (requires human judgment on sufficiency); "Verification Plan addresses methods" (external document) |

## What This Skill Does

1. **Probes** the Safety Plan xlsx structure, extracting:
   - Title metadata (author, approver, revision, status)
   - Project info (project, item, target ASIL, vehicle programs, suppliers)
   - Roles list with independence levels
   - Tailoring decisions with justifications
   - Work products (name, owner, ASIL, dates, status)
   - Confirmation reviews (WP, required independence, assigned reviewer, planned date)
   - Tools list with TCL and qualification status
   - Milestones from the schedule

2. **Verifies** 34 canonical checks across three tabs:
   - **Confirmation Review (14 checks)**: Generic doc-quality (ISO 26262-8 §10) — title, author, revision, TOC, etc.
   - **Safety Plan Assessment (14 checks)**: Substantive planning per ISO 26262-2 §6 — roles, tailoring, work products, reviews, tools, schedule, references. **Check #9 (independence ↔ ASIL match) is highest-value.**
   - **Verification Assessment (6 checks)**: External verification plan compliance (ISO 26262-8 §9).

3. **Outputs** an audit-ready 7-tab xlsx with:
   - Title, General Info, Guide tabs (reference material)
   - Summary tab with visual dashboard (KPI tiles, charts, findings list)
   - Confirmation Review, Safety Plan Assessment, Verification Assessment tabs (detailed checklist)

4. **Does NOT**:
   - Modify the source Safety Plan
   - Make judgments about compliance without evidence
   - Audit external documents (Verification Plan, Item Definition, etc.)
   - Validate cross-references between Safety Plan and other artifacts

## Interpretation Guide

When reviewing the output checklist:

- **Shall vs. Should**: A "NO" rating on a Shall-obligation check is a major finding (blocks approval). A "NO" on a Should is a minor finding (recommend correction but does not block).

- **PENDING rows**: These are subjective or external checks where only human judgment suffices. Review the auto-suggested finding, accept or refine it, and set Assessment to FC/LC/PC/NO.

- **Page/Section cell**: Cites where in the source Safety Plan the evidence or gap was found. Use this to verify each finding directly.

- **Recommended Action cell**: Describes what to fix (if anything). The analyst decides whether to update the Safety Plan and re-run the skill.

## Independence Level ↔ ASIL Mapping (Check SPA-9)

The highest-value check is **Safety Plan Assessment #9: Does confirmation review independence match required ASIL level?**

ISO 26262-2 §6.4.7 requires confirmation reviews by:
- **I1** (a single independent person) for ASIL A/B
- **I2** (an independent team) for ASIL C
- **I3** (an independent organizational unit) for ASIL D

The skill auto-verifies this by comparing assigned independence to expected from ASIL:

| Target ASIL | Expected Independence | Notes |
|-------------|----------------------|-------|
| QM | None | No confirmation review required |
| A | I1 | Single person, independent from author |
| B | I1 | Single person, independent from author |
| C | I2 | Team or second opinion |
| D | I3 | Separate organizational unit |

If Safety Plan assigns I1 to an ASIL D work product, the skill reports NO (mismatch). This is machine-verifiable and high-confidence.

## Scoring Pitfalls to Avoid

1. **Checklist ≠ Confirmation Review**. This skill is a workbench, not the reviewer. ISO 26262-2 Clause 6.4.7 requires the confirmation review to be performed by an independent person/team/unit. The skill accelerates the review but does not replace it.

2. **Many Pending rows is normal**. Verification Assessment checks (#5–10) describe a Verification Plan / Report that lives outside the Safety Plan. Mark them Pending; the reviewer ticks them off against the project's separate verification documents.

3. **Auto-fill is best-effort**. If the probe does not detect a tab (e.g., a custom naming scheme), the checks may incorrectly report "NO" even if the Safety Plan is compliant. The probe is heuristic-based and works best on safety-plan-builder outputs.

4. **Format detection is conservative**. If the sheet is not in exact safety-plan-builder format (tabs 00_Title_Page, 01_Document_Control, etc.), the probe still runs but with lower confidence. Reviewer should verify.

## Next Steps After Checklist Review

1. Read the Summary tab for an executive view (KPI, compliance %, major issues).
2. Address all NO rows (major gaps); then all PC rows (partial compliance).
3. Update the source Safety Plan.
4. Re-run the skill: `python generate_checklist.py <updated_plan.xlsx> <new_checklist.xlsx>`
5. Compare new checklist to old one; confirm improvements.
6. Once all Shall checks are FC/LC and all Should checks are FC/LC/NA, the Safety Plan is ready for approval.
