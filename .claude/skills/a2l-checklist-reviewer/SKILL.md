---
name: a2l-checklist-reviewer
description: Run a confirmation review on any A2L calibration description xlsx against 30 ASAM MCD-2 MC v1.7 compliance checks. Generates audit-grade visual dashboard with rating distribution, findings summary, and recommended actions. Use this skill when the user mentions a2l checklist reviewer.
---

# a2l-checklist-reviewer

Run a confirmation review on any A2L calibration description xlsx against 30 ASAM MCD-2 MC v1.7 compliance checks. Generates audit-grade visual dashboard with rating distribution, findings summary, and recommended actions.

Use this skill when reviewing completed A2L workbooks for compliance, coverage, and audit readiness.

## Output

Generates checklist reviewer xlsx with tabs:

- **Summary** — KPI tiles (Total/Compliant/Pending/Issues), pie chart (FC/LC/PC/NO/NA), bar charts per section
- **Confirmation Review** — 14 structural checks (document format, metadata, tables, cross-references)
- **A2L Object Completeness** — 8 checks (all characteristic types, conversions, axes, records present)
- **Memory & Address Validation** — 5 checks (address ranges, overlap detection, segment layout)
- **Conversion Method Validation** — 3 checks (formula syntax, parameter consistency, unit match)

Rating scale:
- **FC** (Full Compliance) — Check passes; no action required
- **LC** (Limited Compliance) — Check mostly passes; minor clarification needed
- **PC** (Partial Compliance) — Check partially passes; significant work required
- **NO** (Non-Compliance) — Check fails; mandatory rework
- **NA** (Not Applicable) — Check not applicable to this document
- **Pending** — Reviewer judgment required

## Usage

```bash
python generate_checklist.py <a2l_workbook.xlsx> <output_checklist.xlsx>
```

## Check Categories

**Confirmation Review (14 checks)**
- Document structure and tab count
- Template version detection
- Title, author, approver, revision fields
- Document control log
- Searchability and cross-references

**A2L Object Completeness (8 checks)**
- Characteristic catalog coverage (VALUE, CURVE, MAP, AXIS_PTS, VAL_BLK)
- Measurement catalog populated
- Conversion methods defined for all characteristics
- Axis descriptions complete
- Record layouts match characteristic definitions

**Memory & Address Validation (5 checks)**
- All addresses within ECU memory bounds
- No overlapping address ranges
- Segment assignment consistent with type
- Address alignment per data type
- Size calculations match component definitions

**Conversion Method Validation (3 checks)**
- LINEAR parameters present and valid
- Rational function coefficients well-formed
- Unit consistency across characteristics and conversion methods

## References

See `references/a2l_checks.md` for detailed check definitions and acceptance criteria.
