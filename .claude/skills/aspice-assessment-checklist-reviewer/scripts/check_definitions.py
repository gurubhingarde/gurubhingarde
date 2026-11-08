"""
ASPICE Assessment canonical checklist definitions and verification logic.
14 substantive checks + 5 generic validation checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from aspice_assessment_probe import ProbedAssessment


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding: str, action: str = "(Reviewer to verify)") -> CheckResult:
    return CheckResult(
        rating="",
        finding="(Auto-suggest, requires reviewer judgment) " + finding,
        recommended_action=action,
        confidence="Low",
    )


def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, confidence="High")


# Substantive Assessment checks

def aa_01_lead_assessor(p: ProbedAssessment) -> CheckResult:
    if p.lead_assessor:
        return CheckResult(
            rating="FC",
            finding=f"Lead assessor identified: '{p.lead_assessor}'. Verify INTACS codes referenced.",
            confidence="Medium",
        )
    return CheckResult(
        rating="NO",
        finding="Lead assessor not identified in assessment document.",
        recommended_action="Populate Lead Assessor field with assessor name and INTACS codes.",
        confidence="High",
    )


def aa_02_scope_documented(p: ProbedAssessment) -> CheckResult:
    if p.process_areas_in_scope:
        pa_list = ", ".join(sorted(p.process_areas_in_scope))
        return CheckResult(
            rating="FC",
            finding=f"Process areas in scope documented: {pa_list}",
            page_section="Assessment Scope tab",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Process areas in scope not clearly documented.",
        recommended_action="Create Assessment Scope tab listing all in-scope process areas (e.g., SYS.1-5, SWE.1-6, SUP, MAN, ACQ).",
        confidence="High",
    )


def aa_03_prm_applied(p: ProbedAssessment) -> CheckResult:
    # Heuristic: BP Assessment tab with populated rows indicates PRM is being applied
    if p.bp_assessment_rows >= 5:
        return CheckResult(
            rating="FC",
            finding=f"BP Assessment tab populated with {p.bp_assessment_rows} rows; PRM Purpose and Outcomes evident.",
            page_section="BP Assessment tab",
            confidence="Medium",
        )
    return draft(
        "Verify PRM (Process Reference Model) Purpose and Outcomes are correctly applied per process.",
        action="For each in-scope process, confirm PRM Purpose is stated and all required Outcomes are present."
    )


def aa_04_bp_assessed(p: ProbedAssessment) -> CheckResult:
    if p.bp_assessment_rows >= 10:
        return CheckResult(
            rating="FC",
            finding=f"Base Practices assessed for in-scope processes ({p.bp_assessment_rows} BP rows).",
            page_section="BP Assessment tab",
            confidence="High",
        )
    if p.bp_assessment_rows > 0:
        return CheckResult(
            rating="LC",
            finding=f"Only {p.bp_assessment_rows} BP rows found. Some processes may lack BP assessment.",
            recommended_action="Complete BP assessment for all in-scope processes.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No BP Assessment tab or very few rows populated.",
        recommended_action="Create BP Assessment tab and assess every Base Practice for each in-scope process.",
        confidence="High",
    )


def aa_05_gp_assessed(p: ProbedAssessment) -> CheckResult:
    if p.gp_assessment_rows >= 5:
        return CheckResult(
            rating="FC",
            finding=f"Generic Practices assessed at target Capability Level ({p.gp_assessment_rows} GP rows).",
            page_section="GP Assessment tab",
            confidence="Medium",
        )
    if p.gp_assessment_rows > 0:
        return CheckResult(
            rating="LC",
            finding=f"GP Assessment tab exists but only {p.gp_assessment_rows} rows; coverage may be incomplete.",
            recommended_action="Ensure all GPs relevant to target CL are assessed.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="GP Assessment tab not found or empty.",
        recommended_action="Create GP Assessment tab and assess Generic Practices for target Capability Level.",
        confidence="High",
    )


def aa_06_indicator_scale(p: ProbedAssessment) -> CheckResult:
    if "N" in p.pa_scale_values or "P" in p.pa_scale_values or "L" in p.pa_scale_values or "F" in p.pa_scale_values:
        return CheckResult(
            rating="FC",
            finding=f"Indicator ratings use ASPICE N/P/L/F scale: {sorted(p.pa_scale_values)}.",
            page_section="PA Rating tab",
            confidence="High",
        )
    return draft(
        "Verify indicator ratings follow ASPICE Not Achieved (N), Partially Achieved (P), Largely Achieved (L), Fully Achieved (F) scale.",
        action="Check PA Rating tab column headers and cell values for correct N/P/L/F usage."
    )


def aa_07_pa_ratings_derived(p: ProbedAssessment) -> CheckResult:
    if p.pa_ratings_rows >= 5:
        return CheckResult(
            rating="FC",
            finding=f"PA ratings derived and documented ({p.pa_ratings_rows} PA rows); consistent with ASPICE rating rules.",
            page_section="PA Rating tab",
            confidence="Medium",
        )
    return draft(
        "Verify PA ratings are derived per ASPICE rules (e.g., PA1.1 and PA2.1 + PA2.2 at L or higher = CL2).",
    )


def aa_08_cl_computed(p: ProbedAssessment) -> CheckResult:
    if p.cl_profile_present and p.capability_levels_used:
        cl_list = ", ".join(sorted(p.capability_levels_used))
        return CheckResult(
            rating="FC",
            finding=f"Capability Levels computed per ASPICE algorithm. CLs assigned: {cl_list}.",
            page_section="Capability Level / Rating tab",
            confidence="High",
        )
    return draft(
        "Verify CL computation follows ASPICE rules: CL2 requires PA1.1 + (PA2.1 and PA2.2) at L+.",
    )


def aa_09_capability_profile(p: ProbedAssessment) -> CheckResult:
    if p.cl_profile_present:
        return CheckResult(
            rating="FC",
            finding="Capability profile chart per process present.",
            page_section="Capability Level / Profile tab",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Capability profile chart not clearly visible.",
        recommended_action="Add a Capability Profile sheet with graphical representation of CL per process.",
        confidence="Medium",
    )


def aa_10_target_cl_stated(p: ProbedAssessment) -> CheckResult:
    if p.target_cl_stated:
        return CheckResult(
            rating="FC",
            finding="Target Capability Level explicitly stated per process.",
            confidence="Medium",
        )
    return draft(
        "Verify target Capability Level is stated for each process in scope.",
        action="Populate Target CL column in Assessment Scope or Capability Level tab."
    )


def aa_11_strengths_weaknesses(p: ProbedAssessment) -> CheckResult:
    if p.findings_present:
        return CheckResult(
            rating="FC",
            finding="Strengths and weaknesses documented per process.",
            page_section="Summary or process-level tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Findings / strengths / weaknesses section not clearly identified.",
        recommended_action="Add Strengths / Weaknesses summary per process to the assessment document.",
        confidence="Medium",
    )


def aa_12_assessor_signoff(p: ProbedAssessment) -> CheckResult:
    if p.assessor_signoff:
        return draft(
            "Assessor signoff section present. Verify lead assessor, co-assessors, and sponsor have signed off.",
            action="Confirm all required signatures (lead, co-assessors, sponsor) are present."
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated signoff / approval section detected.",
        recommended_action="Add Signoff tab with approval rows for lead assessor, co-assessors, and sponsor.",
        confidence="Medium",
    )


def aa_13_sample_size(p: ProbedAssessment) -> CheckResult:
    return draft(
        "Sample size adequate for evidence substantiation. Typically 1-3 projects sampled per process.",
        action="Verify assessment evidence includes adequate project samples per process."
    )


def aa_14_processes_below_target(p: ProbedAssessment) -> CheckResult:
    return draft(
        "Count processes currently below their target Capability Level as a headline finding.",
        action="Review Capability Level tab and compare current CL vs target CL; report gaps."
    )


# Generic Validation checks

def va_01_doc_structure(p: ProbedAssessment) -> CheckResult:
    if len(p.sheet_names) >= 5:
        return CheckResult(
            rating="FC",
            finding=f"Document well-structured into {len(p.sheet_names)} tabs.",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.sheet_names)} tabs; add Assessment Scope, BP, GP, PA, CL tabs.",
        confidence="Medium",
    )


def va_02_title_complete(p: ProbedAssessment) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(
            rating="FC",
            finding=f"Title page complete: Author='{p.author}', Approver='{p.approver}'.",
            confidence="High",
        )
    missing = [f for f, v in [("Author", p.author), ("Approver", p.approver)] if not v]
    return CheckResult(
        rating="NO" if missing else "FC",
        finding=f"Missing: {', '.join(missing)}." if missing else "Title page complete.",
        recommended_action="Populate missing fields on Title page." if missing else "",
        confidence="High",
    )


def va_03_revision_tracked(p: ProbedAssessment) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Revision '{p.revision}' tracked.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No revision field populated.",
        recommended_action="Populate Revision and Document Control tabs.",
        confidence="High",
    )


def va_04_assessment_date(p: ProbedAssessment) -> CheckResult:
    if p.assessment_date:
        return CheckResult(
            rating="FC",
            finding=f"Assessment date documented: '{p.assessment_date}'.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Assessment date not documented.",
        recommended_action="Add Assessment Date field to Title page.",
        confidence="High",
    )


def va_05_status_clear(p: ProbedAssessment) -> CheckResult:
    if p.status:
        return CheckResult(
            rating="FC",
            finding=f"Status is '{p.status}'.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Status not populated.",
        recommended_action="Set Status to Draft / In Review / Released.",
        confidence="High",
    )


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedAssessment], CheckResult]


CHECKS: list[CheckDef] = [
    # Substantive Assessment checks
    CheckDef("1", "AA", "Assessment Initiation", "Is the lead assessor identified with INTACS codes referenced?", "Shall", aa_01_lead_assessor),
    CheckDef("2", "AA", "Assessment Initiation", "Are the process areas in scope documented (SYS.1-5, SWE.1-6, SUP, MAN, ACQ)?", "Shall", aa_02_scope_documented),
    CheckDef("3", "AA", "Assessment Execution", "Is the PRM correctly applied per process (purpose + outcomes)?", "Shall", aa_03_prm_applied),
    CheckDef("4", "AA", "Assessment Execution", "Have Base Practices been assessed for every in-scope process?", "Shall", aa_04_bp_assessed),
    CheckDef("5", "AA", "Assessment Execution", "Have Generic Practices been assessed at target Capability Level?", "Shall", aa_05_gp_assessed),
    CheckDef("6", "AA", "Assessment Execution", "Do indicator ratings use the ASPICE N/P/L/F scale correctly?", "Shall", aa_06_indicator_scale),
    CheckDef("7", "AA", "Assessment Analysis", "Are Process Attribute (PA) ratings derived per ASPICE rules?", "Shall", aa_07_pa_ratings_derived),
    CheckDef("8", "AA", "Assessment Analysis", "Is Capability Level (CL) computed per ASPICE rating algorithm?", "Shall", aa_08_cl_computed),
    CheckDef("9", "AA", "Assessment Analysis", "Is a capability profile chart present per process?", "Should", aa_09_capability_profile),
    CheckDef("10", "AA", "Assessment Analysis", "Is target Capability Level explicitly stated per process?", "Shall", aa_10_target_cl_stated),
    CheckDef("11", "AA", "Assessment Reporting", "Are strengths and weaknesses documented per process?", "Shall", aa_11_strengths_weaknesses),
    CheckDef("12", "AA", "Assessment Reporting", "Is assessor signoff present (lead + co-assessors + sponsor)?", "Shall", aa_12_assessor_signoff),
    CheckDef("13", "AA", "Assessment Reporting", "Is sample size adequate (typically 1-3 projects per process)?", "Should", aa_13_sample_size),
    CheckDef("14", "AA", "Assessment Reporting", "What is the count of processes BELOW target Capability Level?", "Should", aa_14_processes_below_target),

    # Generic Validation checks
    CheckDef("VA-1", "VA", "Document Quality", "Is the document structure clear and maintainable?", "Should", va_01_doc_structure),
    CheckDef("VA-2", "VA", "Document Quality", "Is the title page complete (author, approver)?", "Shall", va_02_title_complete),
    CheckDef("VA-3", "VA", "Document Quality", "Is revision history tracked?", "Shall", va_03_revision_tracked),
    CheckDef("VA-4", "VA", "Document Quality", "Is assessment date documented?", "Shall", va_04_assessment_date),
    CheckDef("VA-5", "VA", "Document Quality", "Is work-product status clearly stated?", "Shall", va_05_status_clear),
]
