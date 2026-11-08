# TARA Checklist Reviewer — Methodology

## Purpose

This skill produces an audit-ready confirmation-measures checklist for any ISO/SAE 21434 TARA workbook. The checklist follows ISO/SAE 21434 Sections 15-16 (Threat Analysis and Risk Assessment) and UN R155 cybersecurity requirements.

## Scoring conventions

| Code | Meaning |
|------|---------|
| FC   | Fully Compliant — no gaps |
| LC   | Largely Compliant — minor gaps |
| PC   | Partially Compliant — potential impact |
| NO   | Not Compliant — significant gaps |
| NA   | Not Applicable — not relevant |
| —    | Pending — reviewer to assess |

## Auto-fill confidence

- **High** — Verified directly from xlsx (e.g., "Are assets enumerated?")
- **Medium** — Inferred with caveat (e.g., "STRIDE coverage represented")
- **Low / draft** — Subjective or requires external artifact; marked "(Auto-suggest, requires reviewer judgment)"

## What the skill does NOT do

- Does not modify the source TARA xlsx
- Does not render binding compliance judgments (requires independent reviewer per ISO/SAE 21434)
- Does not verify external threat intelligence or penetration testing results

## Tabs in output

1. **Title** — TARA metadata and reviewer assignment
2. **General Info** — TOC and references
3. **Guide** — How to use the checklist
4. **Summary** — Dashboard with statistics and Findings list
5. **Confirmation Review** — 14 doc-quality checks (metadata, structure, references)
6. **TARAA Assessment** — 18 substantive checks (asset inventory, threat scenarios, risk assessment, CSG traceability)
7. **Verification Assessment** — 6 external-artifact checks (threat validation, penetration testing, risk acceptance, compliance)
