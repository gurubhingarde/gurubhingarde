---
name: calibration-data-exchange-checklist-reviewer
description: Run a confirmation review on any calibration data exchange agreement xlsx against 25 compliance checks. Generates audit-grade visual dashboard with KPI tiles, rating distribution, and recommended actions for OEM-Tier-1 calibration handoff agreements. Use this skill when the user mentions calibration data exchange checklist reviewer.
---

# calibration-data-exchange-checklist-reviewer

Run a confirmation review on any calibration data exchange agreement xlsx against 25 compliance checks. Generates audit-grade visual dashboard with KPI tiles, rating distribution, and recommended actions for OEM-Tier-1 calibration handoff agreements.

Use this skill when reviewing calibration data exchange agreements for clarity, coverage, and audit readiness.

## Output

Generates checklist reviewer xlsx with Summary tab and 3 detail tabs:

- **Summary** — KPI tiles (Total/Compliant/Pending/Issues), pie chart (FC/LC/PC/NO/NA), compliance bars
- **Agreement Structure** — 11 checks (document format, parties, ownership matrix)
- **Exchange & Acceptance** — 9 checks (formats, baseline, version control, acceptance criteria)
- **Signoff & Authority** — 5 checks (approvals, signoffs, authority documentation)

Rating scale: FC (Full Compliance), LC (Limited), PC (Partial), NO (Non-Compliance), NA (Not Applicable), Pending

## Usage

```bash
python generate_checklist.py <caldex_workbook.xlsx> <output_checklist.xlsx>
```

## Check Categories

**Agreement Structure (11 checks)**
- Document title and scope clear
- Parties identified (OEM, Tier-1, Tier-2)
- Parameter ownership matrix complete
- Baseline references documented
- Roles and responsibilities defined

**Exchange & Acceptance (9 checks)**
- Exchange formats specified (DCM, CDFX, PaCo)
- Change protocol documented
- Version control scheme defined
- Acceptance criteria measurable
- Unit consistency verified

**Signoff & Authority (5 checks)**
- OEM authorization collected
- Tier-1 authorization collected
- Change notification process defined
- Dispute resolution procedure documented
- Approval dates recorded

## References

See `references/caldex_checks.md` for detailed check definitions and acceptance criteria.
