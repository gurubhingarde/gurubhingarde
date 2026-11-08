# FSC Checklist Reviewer — Methodology

## Purpose

Audit-ready confirmation-measures checklist for any ISO 26262 Functional Safety Concept (FSC) xlsx. Mirrors the TOMCO confirmation-measures format with a visual dashboard summary.

## Scoring

| Code | Meaning |
|------|---------|
| FC | Fully Compliant — no gaps |
| LC | Largely Compliant — minor gaps |
| PC | Partially Compliant — gaps with safety potential |
| NO | Not Compliant |
| NA | Not Applicable |
| —  | Pending reviewer judgment |

NO on Shall = major non-conformance; NO on Should = minor non-conformance.

## Auto-fill confidence

- **High** — Verified directly from xlsx content
- **Medium** — Inferred with caveat
- **Low** — Subjective or external artifact required (drafted, prefixed "(Auto-suggest, requires reviewer judgment)")

## Source-of-truth principle

The skill never modifies the source FSC. Gaps land in the Recommended Actions column. The analyst decides whether to update the FSC and re-run.
