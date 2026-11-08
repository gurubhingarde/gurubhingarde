---
name: ppap-package-builder
description: Generate a complete AIAG Production Part Approval Process (PPAP) submission package workbook integrating upstream artifact references (DFMEA, PFMEA, Control Plan, MSA, dimensional data, process capability) into a structured 22-tab OEM-compliant submission. Automates the Part Submission Warrant (PSW) signoff block, submission level matrix (1-5), element status tracking, and cross-references all required evidence per IATF 16949 and AIAG baseline requirements. Use whenever a supplier must authorize serial production with a formally signed PPAP package.
---

# PPAP Package Builder

The Production Part Approval Process (PPAP) is the AIAG-defined supplier-to-OEM handoff that authorizes serial production of a part. This skill automates the assembly of all 18 PPAP elements (design records, DFMEA, PFMEA, control plan, MSA results, dimensional data, process capability studies, material certifications, and the critical Part Submission Warrant) into a complete, cross-referenced submission package ready for OEM evaluation.

## When to use this skill

Use whenever you need to:
- Build a complete PPAP submission package at any level (1-5)
- Assemble and cross-reference upstream artifacts (DFMEA, PFMEA, Control Plan, MSA workbooks)
- Generate the Part Submission Warrant (PSW) — the formal OEM approval document
- Track which elements are submitted vs retained per submission level
- Document supplier declaration and authorization for serial production
- Prepare an IATF 16949-compliant submission package

Pre-requisites: DFMEA and PFMEA workbooks (if available), Control Plan, MSA results, dimensional inspection data, and process capability studies. If you lack these upstream artifacts, generate them with the appropriate builder skills first.

## Workflow

### Step 1 — Gather upstream artifacts and prepare input JSON

Collect all available supporting documentation:
- Design records and drawings (with revisions)
- Engineering change orders (ECNs) and approvals
- Design FMEA (xlsx)
- Process FMEA (xlsx)
- Control Plan (xlsx)
- Measurement System Analysis results (xlsx, gage R&R data)
- First-piece dimensional inspection report
- Process capability studies (Cpk/Ppk per characteristic)
- Material certifications (RoHS, IMDS submission ID)
- Laboratory accreditations (A2LA, ISO 17025)

Capture into a JSON file matching the schema in `examples/sample_ppap_input_esc.json`:

```json
{
  "submission": {
    "customer", "supplier", "part_name", "part_number", "model_year",
    "supplier_code", "level" (1-5), "ppap_date", "psw_signoff_name",
    "psw_signoff_title", "psw_signoff_email"
  },
  "linked_artifacts": {
    "design_records", "dfmea", "pfmea", "control_plan", "msa_results",
    "imds_submission_id"
  },
  "engineering_changes": [{ecn_id, date, description, drawings_affected}],
  "dimensional_results": [{char_id, spec, tolerance, measured, in_spec}],
  "process_capability": [{char_id, cpk, ppk, sample_size, sample_period}],
  "customer_specific_requirements": [{id, requirement, evidence, status}]
}
```

### Step 2 — Understand submission levels

Read `references/submission_levels.md` to understand which elements are submitted vs retained:
- Level 1: PSW only (all support data retained at supplier)
- Level 2: PSW + samples + limited capability data
- Level 3: PSW + complete data package (most common; recommended default)
- Level 4: Customer-defined requirements
- Level 5: On-site review by OEM

### Step 3 — Generate the package

```bash
python scripts/generate_ppap_package.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The generator produces a 22-tab xlsx with automatic submission level matrix, color-coded status tracking, and all cross-references.

### Step 4 — Review and customize

Work through the tabs in order:

1. **`00_Title_Page`** — Part metadata (name, number, model year, supplier code, submission level)
2. **`01_Document_Control`** — Revision tracking
3. **`02_PSW_Part_Submission_Warrant`** — AIAG PSW form with submission results matrix and authorized signoff block (the formal approval document)
4. **`03_Element1_Design_Records`** — Drawing references and approval status
5. **`04_Element2_Engineering_Changes`** — ECN log with customer notification status
6. **`05_Element3_Eng_Approval`** — Customer engineering sign-off
7. **`06_Element4_DFMEA_Reference`** — Design FMEA artifact reference with hash/revision
8. **`07_Element5_Process_Flow`** — Process flow diagram or table summary
9. **`08_Element6_PFMEA_Reference`** — Process FMEA artifact reference with hash/revision
10. **`09_Element7_Control_Plan_Reference`** — Control Plan reference and characteristic count
11. **`10_Element8_MSA_Results`** — Gage R&R, bias, linearity, stability per gage
12. **`11_Element9_Dimensional_Results`** — First-piece inspection data (spec, measured, in/out of spec)
13. **`12_Element10_Material_Performance`** — RoHS, IMDS, material test reports
14. **`13_Element11_Initial_Process_Studies`** — Cpk/Ppk per characteristic (must meet customer min, typically 1.67)
15. **`14_Element12_Lab_Documentation`** — Qualified lab accreditations (A2LA, ISO 17025)
16. **`15_Element13_Appearance_Approval`** — AAR if applicable
17. **`16_Element14_Sample_Production_Parts`** — Sample serial numbers and ship date
18. **`17_Element15_Master_Sample`** — Master sample location and retention period
19. **`18_Element16_Checking_Aids`** — Custom gages and fixtures with calibration status
20. **`19_Element17_Customer_Specific_Requirements`** — OEM-specific PPAP requirements checklist
21. **`20_Element18_Submission_Status_Matrix`** — Per-element status (Submitted/Retained/N/A) auto-filled per submission level
22. **`21_References`** — AIAG PPAP Manual, IATF 16949, OEM requirements

### Step 5 — Fill in and sign off

- Populate any `<TBD>` placeholder fields with project-specific data
- Verify all upstream artifact paths and file hashes are accurate
- Review dimensional results, MSA metrics, and process capability studies — all must pass OEM acceptance criteria
- Fill in and date the authorized signatory block on the PSW tab (tab 02)
- Mark Document Control revision as `1.0` when ready for submission
- Export to PDF and include in formal submission package to OEM

## Critical requirements

1. **Submission Level Matrix** — Tab 20 automatically populates "Required for Level" column based on selected level using AIAG 4th edition rules
2. **PSW Signoff Block** — Tab 02 includes formal declaration statement and authorized signature fields (supplier organization, signatory name/title, email, date)
3. **Color Coding** — Green for Submitted/Pass/Approved; Yellow for Pending; Red for Failed/Rejected
4. **File Hashes** — Compute SHA256 hash (first 16 chars) for all linked upstream artifacts to track versions and ensure reproducibility
5. **All 18 PPAP Elements** — Coverage per AIAG PPAP 4th edition baseline

## Common pitfalls

1. **Missing upstream artifacts.** Provide paths to DFMEA, PFMEA, Control Plan, and MSA workbooks to auto-populate tabs 06-10 with file hashes and summaries. Placeholders included if not available.
2. **Incomplete process capability.** All special characteristics must have Cpk >= customer minimum (typically 1.67 for critical features). Flag any that fall short as conditional approval or open items.
3. **Dimensional data missing.** First-piece inspection (Element 9) must include 100% dimensional check of critical characteristics with spec/tolerance/measured values. Empty inspection is a critical gap.
4. **Stale upstream versions.** If DFMEA, PFMEA, or Control Plan change after PPAP generation, regenerate immediately — hashes must match submission version.
5. **PSW not signed.** The Part Submission Warrant (tab 02) must be physically signed by authorized supplier representative before submission. Empty signature block blocks OEM approval.

## Files in this skill

```
ppap-package-builder/
├── SKILL.md
├── scripts/
│   ├── generate_ppap_package.py       # main generator (input.json → 22-tab xlsx)
│   ├── recalc.py
│   └── office/soffice.py
├── references/
│   ├── methodology.md                 # PPAP overview, when each element is required
│   ├── ppap_element_requirements.md   # detailed requirement per element
│   └── submission_levels.md           # Level 1-5 submission matrix (AIAG 4th ed)
└── examples/
    └── sample_ppap_input_esc.json     # ESC ECU PPAP package input (Level 3)
```

Always use this skill instead of producing a freeform PPAP package in chat.
