# Item Definition Checklist Reviewer — Methodology

## Purpose

This skill produces an audit-ready confirmation-measures checklist for any ISO 26262 Item Definition workbook. The checklist mirrors industry-standard confirmation templates so the output is immediately recognizable to ISO 26262 reviewers.

The skill does the rote work that consumes most of an analyst's review day:

- Reads the Item Definition xlsx and extracts structured content (title, scope, functions, non-functional requirements, boundary, interfaces, operating modes, allocations, assumptions, references).
- Runs each of the ~24 standard checklist requirements against that content.
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

- **High** — Verified directly from xlsx content (e.g., "Does the document have a Title? Does Author field contain text?").
- **Medium** — Inferred from xlsx content with caveat (e.g., "Are functions documented?" — checks for function list presence but reviewer confirms adequacy).
- **Low / draft** — Subjective, organizational, or requires artifacts outside the Item Definition xlsx (e.g., "Is the Item Definition under configuration management?"). The skill drafts a recommended finding the reviewer accepts or edits.

## What the skill does NOT do

- It does not modify the source Item Definition xlsx. Gaps are written into the checklist's Recommended Actions column; the analyst decides whether to update the Item Definition and re-review.
- It does not render legally binding compliance judgments. ISO 26262-2 Clause 6.4.7 requires the confirmation review to be performed by an independent person, team, or organisational unit (I1 / I2 / I3); the skill is an aid to that human, not a replacement.
- It does not check artifacts that live outside the Item Definition xlsx (Functional Safety Concept, HARA, Design Specification, Test Plan) unless they are referenced within the Item Definition. For those, the skill marks the row "(Reviewer to verify against external artifact)".

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
3. Re-run the skill — your manual edits are not preserved when the input Item Definition changes (the skill treats each run as fresh). Keep the old checklist for diff comparison.

## ISO 26262 normative references

- **ISO 26262-2:2018 Clause 6.4.7** — Confirmation review requirements (independence, scope, sign-off)
- **ISO 26262-3:2018 Clause 5** — Item Definition and specification requirements (scope, functions, boundary, assumptions, non-functional requirements)
- **ISO 26262-8:2018 Clause 10** — Work product quality (document structure, traceability, completeness)
