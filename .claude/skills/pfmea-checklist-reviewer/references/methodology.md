# PFMEA Checklist Methodology

## Scoring Framework

The checklist uses a 6-level rating system applied to each check:

| Rating | Definition | Severity | Next Action |
|--------|-----------|----------|-------------|
| **FC** (Fully Compliant) | Requirement fully satisfied; evidence clear and complete. | None | No action required. Requirement verified. |
| **LC** (Largely Compliant) | Requirement substantially satisfied; minor gaps acceptable. | Minor | Document rationale for gaps; minor corrective actions optional. |
| **PC** (Partially Compliant) | Requirement partially satisfied; significant gaps present. | Moderate | Corrective action recommended; document plan. |
| **NO** (Not Compliant) | Requirement not satisfied; critical gap. | Major | Corrective action mandatory; must resolve before release. |
| **NA** (Not Applicable) | Requirement does not apply to this PFMEA context. | None | No action; correctly marked as out-of-scope. |
| **(Pending)** | Skill suggests finding; human judgment required. | TBD | Reviewer accepts, refines, or overrides auto-generated draft. |

## Obligation Levels

Each check is tagged with an obligation:

- **Shall** (Mandatory): Non-compliance is a critical gap. Must achieve FC/LC/NA for release sign-off.
- **Should** (Best Practice): Compliance strongly encouraged but non-compliance is acceptable if justified.

## Confidence Levels

Every result includes a confidence indicator:

| Confidence | Method | Examples |
|------------|--------|----------|
| **High** | Direct verification from xlsx content | "Header block complete"; "All S/O/D populated 1-10"; "27 high-AP items traced to Control Plan" |
| **Medium** | Inferred from partial data or structure | "Process flow chart 90% complete (9/10 steps have equipment)"; "Author identified but approver missing" |
| **Low** | Subjective or requires external context | "(Auto-suggest) High-S items adequately covered by special characteristics and process controls" |

Low-confidence findings always start with "(Auto-suggest, requires reviewer judgment)" so the reviewer recognizes they must apply domain knowledge.

## What This Skill Does

1. **Extracts PFMEA content** from xlsx (via `pfmea_probe.py`):
   - Metadata (title, revision, author, approver)
   - Header block (part number, part name, process name, date)
   - Process flow steps (step ID, type, equipment, characteristics)
   - Process functions (function ID, description per step)
   - PFMEA worksheet rows (FM, FE, S/O/D, cause, controls, AP)
   - Special characteristics (linked to high-S items)
   - Action plan items (ID, action, responsible, due date, status)
   - Control plan linkage (FM -> control method -> sample size)

2. **Runs 32 canonical checks** across three categories:
   - **Confirmation Review (14 checks)**: Generic doc-quality (AIAG-VDA Handbook Section 4)
   - **PFMEA Assessment (14 checks)**: AIAG-VDA 2019 specific (Handbook Section 5)
   - **Verification Assessment (4 checks)**: External verification alignment

3. **Produces 7-tab checklist** with visual dashboard:
   - Title page, TOC, interpretation guide
   - Summary with KPI tiles, compliance %, findings list
   - Three check result tabs (CR, PFMEA, VA)

4. **Does NOT modify source PFMEA**: All recommended actions stay in the checklist. Analyst decides whether to update the PFMEA and re-run.

## What This Skill Does NOT Do

- **Does not grade the PFMEA as a whole.** Each check is independent; "Rejected" status requires NO items with "Shall" obligation.
- **Does not assess Control Plan adequacy.** Control methods in PFMEA are mapped to Control Plan, but sampling sizes and verification methods are assumed documented elsewhere.
- **Does not validate severity ratings against industry standards.** S/O/D are assumed reasonable by the team; the skill only verifies they are present and in range 1-10.
- **Does not assess process capability.** Occurrence ratings assume team judgment based on process history; the skill only verifies numeric values.
- **Does not modify the source PFMEA.** All corrective actions are recommended in the checklist; the analyst updates the PFMEA and re-runs to confirm closure.

## Typical Review Workflow

1. **Analyst generates PFMEA** using `pfmea-builder` (or equivalent AIAG-VDA template).
2. **Analyst runs checklist reviewer** with `python scripts/generate_checklist.py <pfmea.xlsx> <checklist.xlsx>`.
3. **Reviewer opens checklist** and works through tabs in order:
   - Title: Verify correct PFMEA is being assessed.
   - Summary: Read KPI tiles and findings list for high-level status.
   - Confirmation Review: Focus on NO and PC items; decide whether to ask for rework.
   - PFMEA Assessment: Focus on S/O/D ratings, AP computation, high-AP closure — the core validations.
   - Verification Assessment: Note which items require external evidence (Control Plan, Verification Report).
4. **Reviewer marks findings** as accepted/overridden in the checklist.
5. **If NO items found**: Analyst updates PFMEA and re-runs checklist.
6. **When all items FC/LC/NA or justified PC**: Checklist is signed by reviewer and attached to design release package.

## Design Assumptions

- **PFMEA follows AIAG & VDA Handbook 2019 structure.** Tabs are named per convention; probe logic looks for standard headers.
- **Header block identifies part/process.** Part number, name, process name are in dedicated tab or inline metadata.
- **Process flow chart is populated.** Every significant manufacturing step has an entry.
- **Process functions are documented.** Each step has one or more functions (e.g., "Assemble bracket to frame").
- **S/O/D ratings are on a scale of 1-10.** Severity and Occurrence are subjective; Detection is based on current controls.
- **Action Priority = S*O*D** (or is pre-calculated and stored in AP column).
- **High-AP items (AP >= 100) drive action plans.** Low-AP items may have no corrective actions.
- **Control Plan is separate document** (not in PFMEA xlsx); linkage tab references FM to control methods.
- **Verification Plan is separate document** (e.g., PPAP, design review); VA checks are "Pending" until evidence is provided.

## Recommended Reading

- **AIAG & VDA FMEA Handbook, 4th Edition (2019)**
- **Control Plan development (AIAG APQP guide)**
- **Lessons Learned and risk management history from prior programs**
