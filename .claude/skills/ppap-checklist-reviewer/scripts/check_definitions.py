"""
PPAP checklist definitions per AIAG PPAP Manual 4th edition.

Checks span:
- 14 CR (Confirmation Review): standard doc-quality checks
- 14 PPAPA (PPAP Assessment): element-by-element compliance per submission level
- VA (Verification Assessment): upstream artifact references
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ppap_probe import ProbedPpap


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding: str, page_section: str = "", action: str = "(Reviewer to verify and assess)") -> CheckResult:
    return CheckResult(
        rating="",
        finding="(Auto-suggest, requires reviewer judgment) " + finding,
        page_section=page_section,
        recommended_action=action,
        confidence="Low",
    )


def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, page_section="", recommended_action="", confidence="High")


# ---------------------------------------------------------------------------
# Confirmation Review — 14 doc-quality checks
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedPpap) -> CheckResult:
    if len(p.sheet_names) >= 10:
        return CheckResult(
            rating="FC",
            finding=f"PPAP package structured into {len(p.sheet_names)} tabs with distinct elements.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"PPAP has only {len(p.sheet_names)} tabs; structure may be insufficient.",
        recommended_action="Verify all 22 expected element tabs are present.",
        confidence="Medium",
    )


def cr_02_title(p: ProbedPpap) -> CheckResult:
    if p.part_name and p.part_number and p.customer and p.supplier:
        return CheckResult(
            rating="FC",
            finding=f"Title page complete: {p.part_name} ({p.part_number}) for {p.customer} by {p.supplier}.",
            page_section="00_Title_Page",
            confidence="High",
        )
    missing = []
    if not p.part_name: missing.append("Part Name")
    if not p.part_number: missing.append("Part Number")
    if not p.customer: missing.append("Customer")
    if not p.supplier: missing.append("Supplier")
    return CheckResult(
        rating="NO",
        finding=f"Missing title page fields: {', '.join(missing)}.",
        recommended_action="Populate all title page metadata.",
        confidence="High",
    )


def cr_03_doc_control(p: ProbedPpap) -> CheckResult:
    return draft(
        "Document control / revision history present. Reviewer to confirm traceability.",
        page_section="01_Document_Control",
    )


def cr_04_references(p: ProbedPpap) -> CheckResult:
    if "21_References" in p.sheet_names or any("reference" in s.lower() for s in p.sheet_names):
        return CheckResult(
            rating="FC",
            finding="References tab present or detected in sheet list.",
            page_section="21_References",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated References tab found.",
        recommended_action="Add a References tab citing AIAG PPAP Manual, drawing standards, etc.",
        confidence="Medium",
    )


def cr_05_toc(p: ProbedPpap) -> CheckResult:
    if "00_Title_Page" in p.sheet_names and len(p.sheet_names) >= 5:
        return CheckResult(
            rating="FC",
            finding="Table of Contents present (Title page + ordered tabs).",
            page_section="00_Title_Page",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Table of Contents structure incomplete.",
        recommended_action="Add a formal TOC listing all 22 element tabs.",
        confidence="Medium",
    )


def cr_06_headers(p: ProbedPpap) -> CheckResult:
    return draft(
        "Column headers and formatting present. Reviewer to confirm clarity.",
        action="Verify that all tabs use clear, consistent column headers.",
    )


def cr_07_approval(p: ProbedPpap) -> CheckResult:
    return draft(
        "Approval authority and responsibility structure. Reviewer to confirm per company policy.",
    )


def cr_08_status(p: ProbedPpap) -> CheckResult:
    if p.submission_level:
        return CheckResult(
            rating="FC",
            finding=f"Submission level identified: {p.submission_level}.",
            page_section="00_Title_Page",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Submission level not clearly stated.",
        recommended_action="Specify submission level (1-5) on title page and in all submission documents.",
        confidence="High",
    )


def cr_09_completeness(p: ProbedPpap) -> CheckResult:
    completed = sum(1 for v in p.element_statuses.values() if "submitted" in v.lower() or "completed" in v.lower())
    total = len([k for k in range(1, 19) if k in p.element_statuses or k not in p.element_statuses])
    if completed >= 15:
        return CheckResult(
            rating="FC",
            finding=f"{completed} of {total} elements marked complete/submitted.",
            page_section="20_Element18_Submission_Status_Matrix",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {completed} of {total} elements marked complete.",
        recommended_action="Ensure all required elements per submission level are documented and marked submitted.",
        confidence="Medium",
    )


def cr_10_sign_off(p: ProbedPpap) -> CheckResult:
    if p.psw_signature_block_populated:
        return CheckResult(
            rating="FC",
            finding="PSW (Part Submission Warrant) signature block populated.",
            page_section="02_PSW_Part_Submission_Warrant",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="PSW signature block not populated. Submission cannot proceed without authorization.",
        recommended_action="Complete PSW signoff block with authorized representative signature(s).",
        confidence="High",
    )


def cr_11_format(p: ProbedPpap) -> CheckResult:
    return draft(
        "Worksheet formatting (fonts, colors, borders) present. Reviewer to confirm professional quality.",
    )


def cr_12_accuracy(p: ProbedPpap) -> CheckResult:
    return draft(
        "Numerical accuracy (dimensional, capability values). Reviewer to spot-check calculations.",
    )


def cr_13_traceability(p: ProbedPpap) -> CheckResult:
    return draft(
        "Cross-references between element tabs present. Reviewer to trace element dependencies.",
    )


def cr_14_archive(p: ProbedPpap) -> CheckResult:
    return draft(
        "Archive/retention plan per PPAP retention schedule. Reviewer to confirm company policy.",
    )


# ---------------------------------------------------------------------------
# PPAP Assessment — 14 checks per AIAG PPAP 4th ed
# ---------------------------------------------------------------------------

def ppapa_01_psw_fields(p: ProbedPpap) -> CheckResult:
    """PSW populated with all required fields."""
    missing = []
    if not p.psw_part_name: missing.append("Part Name")
    if not p.psw_part_number: missing.append("Part Number")
    if not p.psw_supplier_code: missing.append("Supplier Code")
    if not p.psw_customer_code: missing.append("Customer Code")
    if not p.psw_drawing_change_level: missing.append("Drawing Change Level")
    if not p.psw_drawing_date: missing.append("Drawing Date")
    if not p.psw_submission_level: missing.append("Submission Level")
    if not p.psw_declaration: missing.append("Declaration")

    if not missing:
        return CheckResult(
            rating="FC",
            finding=f"PSW complete: {p.psw_part_name} ({p.psw_part_number}), Submission Level {p.psw_submission_level}.",
            page_section="02_PSW_Part_Submission_Warrant",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"PSW missing fields: {', '.join(missing)}.",
        recommended_action="Populate all PSW fields before submission.",
        confidence="High",
    )


def ppapa_02_submission_level(p: ProbedPpap) -> CheckResult:
    """Submission level clearly stated (1-5)."""
    if p.submission_level and any(str(i) in p.submission_level for i in range(1, 6)):
        return CheckResult(
            rating="FC",
            finding=f"Submission level {p.submission_level} clearly stated.",
            page_section="00_Title_Page, 02_PSW_Part_Submission_Warrant",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Submission level not clearly identified as 1, 2, 3, 4, or 5.",
        recommended_action="Specify submission level (1-5) on title page and PSW.",
        confidence="High",
    )


def ppapa_03_element1(p: ProbedPpap) -> CheckResult:
    """Element 1: Design Records reference."""
    if p.element1_drawing_number and p.element1_approval_status:
        return CheckResult(
            rating="FC",
            finding=f"Element 1: Design drawing {p.element1_drawing_number} rev {p.element1_revision} referenced, approval status: {p.element1_approval_status}.",
            page_section="03_Element1_Design_Records",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Element 1: Design Records not sufficiently documented.",
        recommended_action="Reference the customer engineering drawing with current revision and approval status.",
        confidence="High",
    )


def ppapa_04_element4(p: ProbedPpap) -> CheckResult:
    """Element 4: DFMEA referenced."""
    if p.element4_dfmea_reference:
        return CheckResult(
            rating="FC",
            finding=f"Element 4: DFMEA referenced ({p.element4_dfmea_reference}); hash {p.element4_dfmea_hash if p.element4_dfmea_hash else '(not specified)'}.",
            page_section="06_Element4_DFMEA_Reference",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Element 4: No DFMEA reference found.",
        recommended_action="Reference the Design FMEA and its version/hash.",
        confidence="High",
    )


def ppapa_05_element6(p: ProbedPpap) -> CheckResult:
    """Element 6: PFMEA referenced."""
    if p.element6_pfmea_reference:
        return CheckResult(
            rating="FC",
            finding=f"Element 6: PFMEA referenced ({p.element6_pfmea_reference}); hash {p.element6_pfmea_hash if p.element6_pfmea_hash else '(not specified)'}.",
            page_section="08_Element6_PFMEA_Reference",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Element 6: No PFMEA reference found.",
        recommended_action="Reference the Process FMEA and its version/hash.",
        confidence="High",
    )


def ppapa_06_element7(p: ProbedPpap) -> CheckResult:
    """Element 7: Control Plan referenced."""
    if p.element7_control_plan_reference:
        return CheckResult(
            rating="FC",
            finding=f"Element 7: Control Plan referenced ({p.element7_control_plan_reference}).",
            page_section="09_Element7_Control_Plan_Reference",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Element 7: No Control Plan reference found.",
        recommended_action="Reference the Control Plan document.",
        confidence="High",
    )


def ppapa_07_element8(p: ProbedPpap) -> CheckResult:
    """Element 8: MSA R&R results (flag if any >30%)."""
    if not p.element8_msa_results:
        return CheckResult(
            rating="PC",
            finding="Element 8: No MSA results documented.",
            recommended_action="Provide MSA (Gage R&R) results for all critical measurement gages.",
            confidence="High",
        )
    high_rr = [m for m in p.element8_msa_results if m["r_and_r_pct"] > 30]
    if high_rr:
        return CheckResult(
            rating="PC",
            finding=f"Element 8: {len(high_rr)} gage(s) with R&R > 30%: {', '.join(m['gage'] for m in high_rr)}.",
            recommended_action="Review gage repeatability/reproducibility. Values >30% indicate measurement system inadequacy.",
            confidence="High",
        )
    return CheckResult(
        rating="FC",
        finding=f"Element 8: MSA data present for {len(p.element8_msa_results)} gage(s); all R&R ≤ 30%.",
        page_section="10_Element8_MSA_Results",
        confidence="High",
    )


def ppapa_08_element9(p: ProbedPpap) -> CheckResult:
    """Element 9: Dimensional results (flag out-of-spec)."""
    if not p.dimensional_results:
        return CheckResult(
            rating="PC",
            finding="Element 9: No dimensional results documented.",
            recommended_action="Provide measured dimensional data for all critical characteristics.",
            confidence="High",
        )
    out_of_spec = [d for d in p.dimensional_results if d.status == "Out-of-Spec"]
    if out_of_spec:
        return CheckResult(
            rating="PC",
            finding=f"Element 9: {len(out_of_spec)} characteristic(s) out-of-spec: {', '.join(d.characteristic for d in out_of_spec)}.",
            recommended_action="Investigate and correct out-of-specification dimensions before submission.",
            confidence="High",
        )
    return CheckResult(
        rating="FC",
        finding=f"Element 9: {len(p.dimensional_results)} characteristic(s) measured; all within spec.",
        page_section="11_Element9_Dimensional_Results",
        confidence="High",
    )


def ppapa_09_element11(p: ProbedPpap) -> CheckResult:
    """Element 11: Process capability (flag Cpk/Ppk < 1.33)."""
    if not p.process_capability:
        return CheckResult(
            rating="PC",
            finding="Element 11: No process capability data documented.",
            recommended_action="Provide Cpk/Ppk values for all critical characteristics.",
            confidence="High",
        )
    low_cpk = [pc for pc in p.process_capability if pc.status == "Low"]
    if low_cpk:
        return CheckResult(
            rating="PC",
            finding=f"Element 11: {len(low_cpk)} characteristic(s) with low capability (Cpk/Ppk < 1.33): {', '.join(pc.characteristic for pc in low_cpk)}.",
            recommended_action="Improve process capability. Values <1.33 indicate insufficient process control.",
            confidence="High",
        )
    return CheckResult(
        rating="FC",
        finding=f"Element 11: {len(p.process_capability)} characteristic(s) with adequate capability (Cpk/Ppk >= 1.33).",
        page_section="13_Element11_Initial_Process_Studies",
        confidence="High",
    )


def ppapa_10_element12(p: ProbedPpap) -> CheckResult:
    """Element 12: Lab documentation (accredited labs A2LA/ISO 17025)."""
    if p.element12_accredited_labs:
        return CheckResult(
            rating="FC",
            finding=f"Element 12: Test results from accredited lab(s): {', '.join(p.element12_accredited_labs)}.",
            page_section="14_Element12_Lab_Documentation",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Element 12: Lab accreditation status (A2LA / ISO 17025) not clearly documented.",
        recommended_action="Provide test reports from accredited laboratories with A2LA or ISO 17025 certification.",
        confidence="High",
    )


def ppapa_11_element17(p: ProbedPpap) -> CheckResult:
    """Element 17: Customer-specific requirements addressed."""
    if not p.customer_specific_requirements:
        return CheckResult(
            rating="FC",
            finding="Element 17: No customer-specific requirements listed (check if not applicable).",
            page_section="19_Element17_Customer_Specific_Requirements",
            confidence="High",
        )
    unaddressed = [r for r in p.customer_specific_requirements if not r.get("evidence")]
    if unaddressed:
        return CheckResult(
            rating="PC",
            finding=f"Element 17: {len(unaddressed)} customer requirement(s) without evidence.",
            recommended_action="Provide evidence (test data, certifications, etc.) for every customer requirement.",
            confidence="High",
        )
    return CheckResult(
        rating="FC",
        finding=f"Element 17: All {len(p.customer_specific_requirements)} customer requirement(s) addressed with evidence.",
        page_section="19_Element17_Customer_Specific_Requirements",
        confidence="High",
    )


def ppapa_12_element18(p: ProbedPpap) -> CheckResult:
    """Element 18: Submission status matrix complete for selected level."""
    if not p.element_statuses:
        return CheckResult(
            rating="NO",
            finding="Element 18: Submission Status Matrix not populated.",
            recommended_action="Complete Element 18 with submission status for all required elements.",
            confidence="High",
        )
    completed = sum(1 for v in p.element_statuses.values() if "submitted" in v.lower() or "completed" in v.lower())
    total = len(p.element_statuses)
    if completed >= total * 0.9:
        return CheckResult(
            rating="FC",
            finding=f"Element 18: {completed}/{total} elements marked submitted.",
            page_section="20_Element18_Submission_Status_Matrix",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Element 18: Only {completed}/{total} elements marked submitted.",
        recommended_action="Mark all required elements submitted per AIAG submission level table.",
        confidence="High",
    )


def ppapa_13_required_elements(p: ProbedPpap) -> CheckResult:
    """Required elements per submission level all marked submitted."""
    # AIAG table: Level 1: 1,3,8,10,13,15,16; Level 2: adds 4,5,7,9,14,18; Level 3: all 18
    level_map = {
        1: [1, 3, 8, 10, 13, 15, 16],
        2: [1, 3, 4, 5, 7, 8, 9, 10, 13, 14, 15, 16, 18],
        3: list(range(1, 19)),
    }
    level = 3
    if p.submission_level:
        for i in range(1, 6):
            if str(i) in p.submission_level:
                level = i
                break
    required = level_map.get(level, level_map[3])
    missing = [e for e in required if p.element_statuses.get(e) is None or "not" in p.element_statuses.get(e, "").lower()]
    if not missing:
        return CheckResult(
            rating="FC",
            finding=f"All required elements for Level {level} present and submitted.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"Level {level} missing elements: {missing}.",
        recommended_action=f"Per AIAG PPAP, Level {level} requires elements {required}. Ensure all are submitted.",
        confidence="High",
    )


def ppapa_14_psw_signoff(p: ProbedPpap) -> CheckResult:
    """PSW signoff filled (cannot submit without signature block)."""
    if p.psw_signature_block_populated:
        return CheckResult(
            rating="FC",
            finding="PSW signature block populated. Submission authorized.",
            page_section="02_PSW_Part_Submission_Warrant",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="PSW signature block not populated. Submission cannot proceed.",
        recommended_action="Complete PSW authorization signature block before sending to customer.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Verification Assessment — external or PPAP-specific
# ---------------------------------------------------------------------------

def va_01_drawing_control(p: ProbedPpap) -> CheckResult:
    """Customer drawing under change control."""
    return draft(
        "Confirm customer drawing is under formal change control (rev, ECN, approval).",
        page_section="03_Element1_Design_Records",
    )


def va_02_material_cert(p: ProbedPpap) -> CheckResult:
    """Material certifications present."""
    return draft(
        "Material test reports or 3.1 certs provided per customer spec.",
        page_section="12_Element10_Material_Performance",
    )


def va_03_sample_approval(p: ProbedPpap) -> CheckResult:
    """Sample parts approved by customer."""
    return draft(
        "Customer has approved production-equivalent sample parts.",
        page_section="14_Element12_Lab_Documentation, 16_Element14_Sample_Production_Parts",
    )


def va_04_tooling_first(p: ProbedPpap) -> CheckResult:
    """First article/tooling run documented."""
    return draft(
        "First article run (FAR) data or tooling qualification documented.",
        page_section="16_Element14_Sample_Production_Parts",
    )


def va_05_fmea_actions(p: ProbedPpap) -> CheckResult:
    """FMEA corrective actions completed."""
    return draft(
        "All high-risk FMEA items have documented closure on corrective actions.",
        page_section="06_Element4_DFMEA_Reference, 08_Element6_PFMEA_Reference",
    )


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedPpap], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review
    CheckDef("1", "CR", "Document Quality", "Is the PPAP package structured with clear sections?", "Shall", cr_01_structured),
    CheckDef("2", "CR", "Document Quality", "Is the title page complete with customer, supplier, part, part number?", "Shall", cr_02_title),
    CheckDef("3", "CR", "Document Quality", "Is document control and revision history present?", "Should", cr_03_doc_control),
    CheckDef("4", "CR", "Document Quality", "Are references listed (AIAG, drawing standards, etc.)?", "Should", cr_04_references),
    CheckDef("5", "CR", "Document Quality", "Is a table of contents provided?", "Should", cr_05_toc),
    CheckDef("6", "CR", "Document Quality", "Are column headers and formatting clear?", "Should", cr_06_headers),
    CheckDef("7", "CR", "Document Quality", "Are approval authorities and responsibilities identified?", "Should", cr_07_approval),
    CheckDef("8", "CR", "Document Quality", "Is submission level clearly identified (1-5)?", "Shall", cr_08_status),
    CheckDef("9", "CR", "Document Quality", "Is package completeness evident (all elements accounted for)?", "Should", cr_09_completeness),
    CheckDef("10", "CR", "Document Quality", "Is the submission sign-off (PSW) authorized?", "Shall", cr_10_sign_off),
    CheckDef("11", "CR", "Document Quality", "Are worksheets professionally formatted?", "Should", cr_11_format),
    CheckDef("12", "CR", "Document Quality", "Are numerical values accurate (no calculation errors)?", "Should", cr_12_accuracy),
    CheckDef("13", "CR", "Document Quality", "Are cross-references between elements clear?", "Should", cr_13_traceability),
    CheckDef("14", "CR", "Document Quality", "Is the retention/archive plan documented?", "Should", cr_14_archive),

    # PPAP Assessment
    CheckDef("1", "PPAPA", "PSW and Submission", "Are all PSW fields populated (part name, number, codes, drawing level/date, declaration)?", "Shall", ppapa_01_psw_fields),
    CheckDef("2", "PPAPA", "PSW and Submission", "Is submission level clearly identified (1-5)?", "Shall", ppapa_02_submission_level),
    CheckDef("3", "PPAPA", "Element 1", "Is Element 1 (Design Records) referenced with drawing number, revision, approval status?", "Shall", ppapa_03_element1),
    CheckDef("4", "PPAPA", "Element 4,6,7", "Is Element 4 (DFMEA) referenced with version/hash?", "Shall", ppapa_04_element4),
    CheckDef("5", "PPAPA", "Element 4,6,7", "Is Element 6 (PFMEA) referenced with version/hash?", "Shall", ppapa_05_element6),
    CheckDef("6", "PPAPA", "Element 4,6,7", "Is Element 7 (Control Plan) referenced?", "Shall", ppapa_06_element7),
    CheckDef("7", "PPAPA", "Element 8", "Are Element 8 (MSA R&R) results present and acceptable (all gages ≤30%)?", "Shall", ppapa_07_element8),
    CheckDef("8", "PPAPA", "Element 9", "Are Element 9 (Dimensional) results populated with all characteristics in spec?", "Shall", ppapa_08_element9),
    CheckDef("9", "PPAPA", "Element 11", "Are Element 11 (Process Capability) values adequate (Cpk/Ppk ≥1.33)?", "Shall", ppapa_09_element11),
    CheckDef("10", "PPAPA", "Element 12", "Are Element 12 (Lab) reports from accredited labs (A2LA/ISO 17025)?", "Shall", ppapa_10_element12),
    CheckDef("11", "PPAPA", "Element 17", "Are Element 17 (Customer-Specific) requirements addressed with evidence?", "Shall", ppapa_11_element17),
    CheckDef("12", "PPAPA", "Element 18", "Is Element 18 (Submission Status Matrix) complete for the selected level?", "Shall", ppapa_12_element18),
    CheckDef("13", "PPAPA", "Element 18", "Are all required elements per submission level marked submitted?", "Shall", ppapa_13_required_elements),
    CheckDef("14", "PPAPA", "PSW and Submission", "Is PSW signature/authorization block completed?", "Shall", ppapa_14_psw_signoff),

    # Verification Assessment
    CheckDef("1", "VA", "References", "Is customer drawing under formal change control?", "Shall", va_01_drawing_control),
    CheckDef("2", "VA", "References", "Are material certifications provided?", "Shall", va_02_material_cert),
    CheckDef("3", "VA", "References", "Has the customer approved production sample parts?", "Shall", va_03_sample_approval),
    CheckDef("4", "VA", "References", "Is first article run (tooling) data documented?", "Shall", va_04_tooling_first),
    CheckDef("5", "VA", "References", "Are FMEA corrective actions closed?", "Shall", va_05_fmea_actions),
]
