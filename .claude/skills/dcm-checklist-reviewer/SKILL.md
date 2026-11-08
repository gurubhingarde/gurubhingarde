---
name: dcm-checklist-reviewer
description: Run a confirmation review on any DCM calibration values xlsx against 28 ETAS DCM format compliance checks. Generates audit-grade visual dashboard with KPI tiles, rating distribution, and recommended actions. Use this skill when the user mentions dcm checklist reviewer.
---

# dcm-checklist-reviewer

Run a confirmation review on any DCM calibration values xlsx against 28 ETAS DCM format compliance checks. Generates audit-grade visual dashboard with KPI tiles, rating distribution, and recommended actions.

Use this skill when reviewing DCM datasets for compliance, baseline traceability, and audit readiness.

## Output

Generates checklist reviewer xlsx with Summary tab and 4 detail tabs:

- **Summary** — KPI tiles (Total/Compliant/Pending/Issues), pie chart (FC/LC/PC/NO/NA), compliance bars
- **Confirmation Review** — 12 structural checks (document format, metadata, catalogs present)
- **Value Validation** — 10 checks (physical ranges, monotonicity, completeness)
- **Baseline & Traceability** — 6 checks (source A2L reference, baseline link, approval)

Rating scale: FC (Full Compliance), LC (Limited), PC (Partial), NO (Non-Compliance), NA (Not Applicable), Pending

## Usage

```bash
python generate_checklist.py <dcm_workbook.xlsx> <output_checklist.xlsx>
```

## Check Categories

**Confirmation Review (12 checks)**
- Document structure and completeness
- Title, author, approver, revision fields
- Dataset identity (variant, build date) documented
- Source A2L reference present
- Baseline link established

**Value Validation (10 checks)**
- All scalars within physical ranges
- Curve values monotonic and bounded
- Map value dimensions match axes
- Axis points strictly increasing
- Value blocks reference defined scalars
- No NaN/Inf values present
- Unit consistency across dataset

**Baseline & Traceability (6 checks)**
- Source A2L version specified
- Baseline reference documented
- Change history recorded
- Approver documented
- Dataset version unique
- Equipment/vehicle ID recorded

## References

See `references/dcm_checks.md` for detailed check definitions and acceptance criteria.
