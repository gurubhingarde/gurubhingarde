---
name: autosar-composition-checklist-reviewer
description: Run a confirmation review on any AUTOSAR Composition SWC specification xlsx, execute 28+ automated structural checks, and generate an audit-ready xlsx checklist report with visual dashboard. Use this skill when the user mentions autosar composition checklist reviewer.
---

# autosar-composition-checklist-reviewer

Run a confirmation review on any AUTOSAR Composition SWC specification xlsx, execute 28+ automated structural checks, and generate an audit-ready xlsx checklist report with visual dashboard.

## Usage

Use this skill whenever the user wants to review, validate, or audit an AUTOSAR Composition SWC specification workbook for architectural coherence, connector validity, and AUTOSAR R22-11 compliance.

## Inputs

Accepts an existing Composition SWC specification xlsx workbook (e.g., from autosar-composition-builder).

## Output

Produces a checklist xlsx with:
- Summary metrics and compliance percentage
- Check-by-check detailed findings (Pass / Partial / Fail / N/A)
- Visual dashboard with status gauge and findings table
- Remediation guidance

## Checks Include

SWC instance coverage (all referenced), assembly connector validity (P-port to R-port, compatible interfaces), delegation mapping (SWC ports to boundary), orphaned instance detection, naming convention compliance, port compatibility rules, hierarchy validation.

---

**Commands:**
- `/autosar-composition-checklist-reviewer <path-to-composition.xlsx>` — run full review
