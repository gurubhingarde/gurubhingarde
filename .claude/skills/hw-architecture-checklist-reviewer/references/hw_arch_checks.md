# HW Architecture Checks Reference

## Overview

This document describes each of the 29 checks in the HW Architecture Checklist Reviewer. Checks are organized into three groups:

1. **Confirmation Review (CR)** — 12 generic document-quality checks per ISO 26262-8 §10
2. **HW Architecture Assessment (HWAA)** — 12 substantive HW architecture checks per ISO 26262-5 §7
3. **Verification Assessment (VA)** — 5 verification checks per ISO 26262-8 §9

---

## Confirmation Review (CR) — Document Quality & Configuration Management

| ID | Requirement | Obligation | What it Verifies |
|----|-------------|-----------|------------------|
| 1 | Is the document structured in a clear manner with distinct sections? | Shall | Document has 11+ tabs for clear organization (Title, General Info, Doc Control, PCB, Catalog, Safety Mechanisms, etc.). |
| 2 | Does the title cover the scope of the HW architecture? | Shall | Title page contains a document title that reflects HW architecture scope. Reviewer to confirm wording. |
| 3 | Are the author and approver listed? | Shall | Both Author and Approver fields populated on Title page with real names (not placeholders). |
| 4 | Is there a unique identification for each revision? | Shall | Revision field on Title page contains a unique identifier (e.g., "1.0", "A", "v20240101"). |
| 5 | Is the status of the work product provided? | Shall | Status field on Title page set to Draft, In Review, or Released. |
| 6 | Is a unique document identifier assigned? | Shall | Document ID field on Title page populated with unique project identifier. |
| 7 | Is the document under configuration and change management? | Shall | Document is checked into CM system (Git, Polarion, etc.). Requires organizational confirmation. |
| 8 | Does the document contain a table of contents or clear tab structure? | Shall | Title page present as first sheet; sheet names are self-describing. References tab present. |
| 9 | Is a References section included? | Should | Sheet "11_References" present with citations to ISO 26262-5, IC datasheets, TSC, HW-TSR documents. |
| 10 | Is a revision history maintained? | Should | Document Control tab contains revision history with dates, authors, and change descriptions. |
| 11 | Are headers and footers properly updated? | Should | Excel headers/footers reflect current doc ID and revision. Checked manually in Excel. |
| 12 | Have all major sections been completed? | Shall | HW Catalog, Power Architecture, Clock Architecture, and Common Cause Analysis all have content. |

---

## HW Architecture Assessment (HWAA) — ISO 26262-5 §7 Substantive Checks

| ID | Section | Requirement | Obligation | What it Verifies | Confidence |
|----|---------|-------------|-----------|------------------|------------|
| 1 | HW Elements & BOM | Is the HW Element Catalog populated (count > 0)? | Shall | Sheet "04_HW_Element_Catalog" contains at least one HW element row. Counts IC, discrete, passive, connector instances. | High |
| 2 | HW Elements & BOM | Does each HW element have supplier, part number, package, baseline FIT? | Shall | All HW elements have: supplier name, part/model number, package type (e.g., BGA, DIP), baseline FIT rate (e.g., 1.5 FIT). | High |
| 3 | HW Elements & BOM | Is safety qualification (AEC-Q100/Q101/Q200) recorded for ASIL-relevant elements? | Shall | ASIL-relevant HW elements have qualification standard recorded (e.g., "AEC-Q100 Grade 0"). | High |
| 4 | PCB & Power/Clock | Is PCB design documented with layers and area allocations? | Shall | Sheet "03_PCB_Design" populated with PCB layout specification: layer count, key area allocations (power planes, analog, digital regions). | High |
| 5 | PCB & Power/Clock | Are power rails documented with voltage, regulator, and monitoring? | Shall | Sheet "07_Power_Architecture" lists all power rails with: voltage (e.g., "5V", "3.3V"), regulator IC, monitoring threshold, fusing strategy. | High |
| 6 | PCB & Power/Clock | Are clock sources documented with monitoring and redundancy strategy? | Shall | Sheet "08_Clock_Architecture" lists all clock sources with: type (XTAL, RC, PLL), frequency, monitoring mechanism, redundancy strategy. | High |
| 7 | Traceability & Allocation | Is each HW element mapped to its TSC node (traceability)? | Shall | Sheet "04_HW_Element_Catalog" TSC_Node_ID column maps each HW element to a TSC node (e.g., "TSC_CPU", "TSC_Memory"). Enables traceability to HW-TSRs. | High |
| 8 | Traceability & Allocation | Are safety mechanisms allocated to HW elements with TSC references? | Shall | Sheet "05_Safety_Mechanism_Allocation" documents which HW elements implement which safety mechanisms, referenced back to TSC mechanisms with allocated ASIL. | High |
| 9 | Traceability & Allocation | Is the HW-SR Allocation Matrix complete (each HW-SR mapped to HW elements)? | Shall | Sheet "06_HW_SR_Allocation_Matrix" is a cross-reference (rows=HW-SRs, cols=HW-Elements). Shows which HW element(s) implement each HW-SR. | High |
| 10 | Common-Cause & Redundancy | Is common-cause failure analysis performed for redundant pairs? | Shall | Sheet "09_Common_Cause_Analysis" documents redundant element pairs and analyzes: shared power rail, shared package, shared PCB region, shared environmental zone. Marks each coupling as No, Yes-Mitigated, or Yes-Unmitigated. | High |
| 11 | BOM & Reliability | Is total system FIT computed from BOM for PMHF calculation? | Shall | Sheet "10_Bill_of_Materials" computes total BOM FIT by summing baseline FIT rates of all HW elements. Used in PMHF (Probabilistic Metric of Hazard) analysis. | High |
| 12 | Independence & Decomposition | Are independence requirements between FSC channels respected? | Shall | Independent FSC channels do not share power rails, clock sources, or fault domains. Requires design review; skill checks for TSC references. | Medium |

---

## Verification Assessment (VA) — ISO 26262-8 §9 Verification Checks

| ID | Section | Requirement | Obligation | What it Verifies | Confidence | Type |
|----|---------|-------------|-----------|------------------|------------|------|
| 1 | Verification Planning | Does verification plan address HW architecture validation methods? | Shall | External: Verification Plan / Specification document. Skill marks as Pending; reviewer verifies against project documents. | Low | External |
| 2 | Verification Environment | Is the verification test environment documented? | Shall | External: Verification Report documents test environment (HiL, bench, vehicle level, test tools, calibration data). | Low | External |
| 3 | Verification Criteria | Are pass/fail criteria for HW architecture verification defined? | Shall | External: Verification Plan specifies pass/fail criteria (e.g., "Power rail voltage within ±5%", "Clock jitter < 2%"). | Low | External |
| 4 | Verification Evidence | Are verification environment and tools documented? | Shall | External: Verification Report documents test tools, configurations, environment setup. | Low | External |
| 5 | Verification Evidence | Is compliance evidence complete and traceable to requirements? | Shall | External: Verification Report provides evidence that each HW element and safety mechanism meets its specification. Traceable to HW-TSRs. | Low | External |

---

## Check Execution Notes

### Confirmation Review
- Machine-verifiable checks (1, 3, 4, 5, 6, 8) get FC/NO with High confidence.
- Subjective checks (2, 7, 9, 10, 11) are drafted with Low confidence; reviewer provides judgment.
- Check 12 aggregates signals from HWAA checks to assess overall completeness.

### HW Architecture Assessment
- All 12 checks are largely machine-verifiable via xlsx content inspection.
- Checks 1–11 get FC/LC/PC/NO with High confidence based on presence and completeness of data.
- Check 12 (Independence) requires design review reasoning; skill provides Medium confidence based on TSC references.
- Typically 80–90% of items receive FC; gaps in 4–6 and 8–9 are common in early versions.

### Verification Assessment
- All 5 checks are external (refer to Verification Plan / Spec / Report).
- All 5 marked Pending by default; reviewer checks against project documents.
- Skill does not evaluate these until Verification Plan is available.

---

## Common Findings Patterns

| Pattern | Typical Cause | Recommended Action |
|---------|---------------|-------------------|
| Multiple CR items NO | Title page not fully filled out | Fill author, approver, status, revision, doc ID on Title page. |
| HWAA #1-2 PC/NO | Incomplete HW Element Catalog | Add all ICs, discretes, passives to catalog with supplier, part, package, FIT. |
| HWAA #3 PC/NO | Missing qualification data | Add AEC-Q100/Q101/Q200 qualification standards for ASIL-relevant elements. |
| HWAA #5-6 LC/PC | Power/Clock data sparse | Expand Power and Clock tabs with full voltage, regulator, monitor, and redundancy details. |
| HWAA #7-9 PC/NO | Missing traceability | Populate TSC_Node_ID, Safety_Mechanism_Allocation, and HW_SR_Allocation tabs. |
| HWAA #10 PC | Unmitigated CCFs | Either redesign to eliminate shared coupling or document mitigation (e.g., "separate packages, independent rails"). |
| VA items PENDING | Verification Plan not linked | Reference external Verification Plan in HW Architecture References tab. |

---

## Re-running the Skill

After updating the HW Architecture xlsx to address findings:

```bash
python scripts/generate_checklist.py <updated_hw_arch.xlsx> <new_checklist.xlsx>
```

The new checklist will reflect updated probe results. Compare old and new checklists to verify that addressed items moved from PC/NO to FC/LC.
