# HARA Checklist Reviewer — Methodology

## Purpose

This skill produces an audit-ready confirmation-measures checklist for any ISO 26262 HARA workbook. The checklist mirrors the TOMCO HARA confirmation template (an industry-standard format used by automotive functional-safety assessors) so the output is immediately recognizable to ISO 26262 reviewers.

The skill does the rote work that consumes most of an analyst's review day:

- Reads the HARA xlsx and extracts the structured content (item, functions, malfunctions, hazardous events, S/E/C ratings, ASILs, safety goals, safe states).
- Runs each of the ~50 standard checklist requirements against that content.
- For machine-verifiable checks, fills in the rating, evidence finding, page/section reference, and (when applicable) recommended corrective action.
- For subjective checks, drafts a finding and marks it for human review.
- Computes the Summary tab statistics from the per-row results.

## Scoring conventions (per ISO 26262 confirmation-measure practice)

| Code | Meaning                                                     |
|------|-------------------------------------------------------------|
| FC   | Fully Compliant — no gaps                                   |
| LC   | Largely Compliant — minor gaps, no impact on safety         |
| PC   | Partially Compliant — gaps with potential safety impact     |
| NO   | Not Compliant — significant gaps, safety impact likely      |
| NA   | Not Applicable — requirement does not apply to this item    |
| —    | Blank / pending — reviewer to assess (subjective check)     |

For the Confirmation Review tab (generic doc-quality checks) the assessment is binary YES / NO (mapped internally to FC / NO). A "NO" rating on a Shall requirement is a major non-conformance; on a Should requirement, minor.

## Auto-fill confidence (Hybrid mode)

Every check is tagged with one of:

- **High** — Verified directly from xlsx content (e.g., "Does each row have an S rating?").
- **Medium** — Inferred from xlsx content with caveat (e.g., "Are operational situations documented?" — checks for environment columns but the analyst confirms relevance).
- **Low / draft** — Subjective, organizational, or requires artifacts outside the HARA xlsx (e.g., "Is the document under configuration management?"). The skill drafts a recommended finding the reviewer accepts or edits.

## What the skill does NOT do

- It does not modify the source HARA xlsx. Gaps are written into the checklist's Recommended Actions column; the analyst decides whether to update the HARA and re-review.
- It does not render legally binding compliance judgments. ISO 26262-2 Clause 6.4.7 requires the confirmation review to be performed by an independent person, team, or organisational unit (I1 / I2 / I3); the skill is an aid to that human, not a replacement.
- It does not check artifacts that live outside the HARA xlsx (item definition, FSC, verification report) unless they are referenced in the HARA. For those, the skill marks the row "(Reviewer to verify against external artifact)".

## How auto-fill rates feed the Summary tab

The Summary tab statistics are computed from the per-row Assessment values in the three review tabs:

- Total Items = count of rows with Obligation in {Shall, Should} on each tab
- Number of Non-conformances = count of rows with Assessment = NO
- Number of Major Issues = count of NO rows where Obligation = Shall
- Number of Minor Issues = count of NO rows where Obligation = Should
- Number of Partially Compliant = count of PC rows
- Number of Largely Compliant = count of LC rows
- Number of Fully Compliant = count of FC rows
- Unfilled in CL = count of rows where Assessment is blank or "—"

## When the auto-fill is wrong

The skill is opinionated about *method* and conservative about *judgment*. If the auto-fill rates a check FC and the reviewer disagrees:

1. Review the Findings cell — does the cited evidence actually demonstrate compliance?
2. If not, change the Assessment to PC or NO and add a corrective-action note in Recommended Actions.
3. Re-run the skill — your manual edits are preserved when the input HARA changes (the Findings/Assessment columns are merged on FSR_ID match).

(Manual-edit preservation is not implemented in v0.1; the analyst should treat re-runs as fresh starts. See the SKILL.md for the recommended workflow.)
