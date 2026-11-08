---
name: autosar-swc-checklist-reviewer
description: Run a confirmation review on any AUTOSAR SWC specification xlsx, execute 30+ automated structural checks, and generate an audit-ready xlsx checklist report with visual dashboard. Use this skill when the user mentions autosar swc checklist reviewer.
---

# autosar-swc-checklist-reviewer

Run a confirmation review on any AUTOSAR SWC specification xlsx, execute 30+ automated structural checks, and generate an audit-ready xlsx checklist report with visual dashboard.

## Usage

Use this skill whenever the user wants to review, validate, or audit an AUTOSAR SWC specification workbook for completeness, consistency, and AUTOSAR R22-11 compliance.

## Inputs

Accepts an existing SWC specification xlsx workbook (e.g., from autosar-swc-builder).

## Output

Produces a checklist xlsx with:
- Summary metrics
- Check-by-check detailed findings (Pass / Partial / Fail / N/A)
- Visual dashboard (status gauge, category breakdown, risk heat map)
- Remediation guidance
- Cross-reference traceability

## Checks Include

Port coherence (every port has interface), runnable triggers (every runnable triggered by event), exclusive area usage, data type completeness, naming conventions, AUTOSAR compliance markers.

---

**Commands:**
- `/autosar-swc-checklist-reviewer <path-to-swc.xlsx>` — run full review
