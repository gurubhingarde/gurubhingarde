---
name: change-impact-analysis-builder
description: Generate an audit-ready change impact analysis workbook per ISO 26262-8 Section 8 covering change classification, affected work product mapping across HARA, FSC, TSC, HW and SW requirements and tests, ASIL impact assessment, re-verification scope, and approval signatures for safety-relevant change requests.
---

# Change Impact Analysis Builder

ISO 26262-8 Clause 8 (Change Management) requires systematic analysis of the impact of each change request on affected work products and the determination of re-verification scope. This skill produces an audit-ready Change Impact Analysis workbook.

## When to use this skill

Use whenever the user wants to:
- Create or update a change impact analysis per ISO 26262-8 Clause 8
- Classify changes (minor/major/safety-impacting)
- Map affected work products across HARA, FSC, TSC, HW/SW requirements and tests
- Assess ASIL impact and re-verification scope
- Document approvals and implementation schedule
- Generate audit-ready change management documentation

## Workflow

### Step 1 — Capture change request

Ask for:

1. **Change Request ID and title**
2. **Change classification** (minor/major/safety-impacting)
3. **Affected work products** — list each with description of how change impacts it
4. **ASIL impact assessment** (no change, raises ASIL, lowers ASIL)
5. **Re-verification scope** (what needs to be re-tested/re-analyzed)

### Step 2 — Build input JSON

Create input.json conforming to the schema in `scripts/generate_cia.py`.

### Step 3 — Generate

```bash
python scripts/generate_cia.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

### Step 4 — Present

Display the output xlsx highlighting:
- The **Change Request Identity** tab — is the change clearly described?
- The **Change Classification** tab — is the classification justified?
- The **Affected Work Products Matrix** tab — are all affected WPs identified?
- The **ASIL Impact Assessment** tab — is the ASIL impact analyzed?
- The **Re-verification Scope** tab — is re-verification complete and planned?

## Output structure (10 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Change ID, title, project, requester, date |
| 01 | Document Control | Revision history |
| 02 | Change Request Identity | Full description, rationale, requesting party |
| 03 | Change Classification | Classification (minor/major/safety-impacting), justification |
| 04 | Affected Work Products Matrix | Rows per WP: name, impact type (modified/obsoleted/created), impact description |
| 05 | ASIL Impact Assessment | Original ASIL, modified ASIL, impact justification |
| 06 | Re-verification Scope | List of required re-verification activities |
| 07 | Re-validation Scope | List of required re-validation activities |
| 08 | Approval Block | Approver, signature, date, conditional approvals |
| 09 | References | ISO 26262-8 Clause 8, change control procedure |

## Files in this skill

```
change-impact-analysis-builder/
├── SKILL.md
├── scripts/
│   ├── generate_cia.py
│   ├── recalc.py
│   └── office/
├── references/
│   └── methodology.md
└── examples/
    └── sample_change_request.json
```
