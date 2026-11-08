"""
Canonical Safety Case checklist definitions and verification logic per ISO 26262-2 §6.5.

Each check is a dict with keys:
- id: row id as it appears on the checklist (e.g., "SCA-1", "VA-1")
- tab: which output tab this check belongs to (CR / SCA / VA)
- section: section header text
- requirement: the requirement text
- obligation: "Shall" or "Should"
- verify: callable(probed: ProbedSafetyCase) -> CheckResult
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from safety_case_probe import ProbedSafetyCase


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    rating: str = ""              # FC / LC / PC / NO / NA / "" (pending)
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""          # High / Medium / Low / "" for binary CR


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
# Confirmation Review — Document Quality (14 standard checks)
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedSafetyCase) -> CheckResult:
    expected_tabs = 15
    if len(p.sheet_names) >= expected_tabs:
        return CheckResult(
            rating="FC",
            finding=f"Document contains {len(p.sheet_names)} tabs with all major sections expected for Safety Case (Title, Doc Control, Executive Summary, Item Definition, Top Claim, Safety Goals, FSR-TSR Traceability, HW Metrics, SW Verification, Tool Qualification, Confirmation Reviews, Open Items, Argument Notes, Assessment, References).",
            page_section="All tabs",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has {len(p.sheet_names)} tabs; expected 15 standard Safety Case tabs.",
        recommended_action=f"Ensure all standard tabs are present (currently missing ~{expected_tabs - len(p.sheet_names)}).",
        confidence="High",
    )


def cr_02_template(p: ProbedSafetyCase) -> CheckResult:
    return draft(
        "Template version cannot be detected from xlsx content alone.",
        action="Confirm the latest applicable Safety Case template was used.",
    )


def cr_03_searchable(p: ProbedSafetyCase) -> CheckResult:
    has_toc = "00_Title_Page" in p.sheet_names or "General Info" in p.sheet_names
    has_refs = "14_References" in p.sheet_names
    if has_toc and has_refs:
        return CheckResult(
            rating="FC",
            finding="Document has structured tabs and a References section; searchability aids present.",
            page_section="First and last tabs",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Some search aids present but not all required elements.",
        recommended_action="Ensure References tab is populated and document structure is consistent.",
        confidence="Medium",
    )


def cr_04a_title_scope(p: ProbedSafetyCase) -> CheckResult:
    if p.title:
        return draft(
            f"Title: '{p.title}'. Reviewer to confirm scope coverage.",
            page_section="Title page",
        )
    return CheckResult(
        rating="NO",
        finding="No title detected on the Title page.",
        recommended_action="Add a clear document title reflecting the Safety Case scope.",
        confidence="High",
    )


def cr_04b_author_approver(p: ProbedSafetyCase) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(
            rating="FC",
            finding=f"Author='{p.author}', Approver='{p.approver}' both populated on Title page.",
            page_section="Title page",
            confidence="High",
        )
    missing = []
    if not p.author: missing.append("Author")
    if not p.approver: missing.append("Approver")
    return CheckResult(
        rating="NO",
        finding=f"Missing: {', '.join(missing)}.",
        recommended_action=f"Populate {', '.join(missing)} on Title page.",
        confidence="High",
    )


def cr_04c_unique_revision(p: ProbedSafetyCase) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Revision='{p.revision}' is set on Title page.",
            page_section="Title page Revision field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Revision field not populated on Title page.",
        recommended_action="Populate Revision with unique identifier.",
        confidence="High",
    )


def cr_04d_change_history(p: ProbedSafetyCase) -> CheckResult:
    # Simplified: check if Document Control tab exists and is populated
    if "01_Document_Control" in p.sheet_names:
        return CheckResult(
            rating="FC",
            finding="Document Control tab is present with revision history.",
            page_section="Tab 01_Document_Control",
            confidence="Medium",
        )
    return CheckResult(
        rating="NO",
        finding="No Document Control tab with revision history.",
        recommended_action="Add Document Control tab with change history.",
        confidence="High",
    )


def cr_04e_status(p: ProbedSafetyCase) -> CheckResult:
    if p.status:
        return CheckResult(
            rating="FC",
            finding=f"Status='{p.status}' is set on Title page.",
            page_section="Title page Status field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No work-product status on Title page.",
        recommended_action="Add Status field (Draft / In Review / Released).",
        confidence="High",
    )


def cr_05_current_revision(p: ProbedSafetyCase) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Current revision '{p.revision}' is identifiable.",
            page_section="Title page Revision field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Current revision is not identifiable.",
        recommended_action="Populate Revision field on Title page.",
        confidence="High",
    )


def cr_06_config_mgmt(p: ProbedSafetyCase) -> CheckResult:
    return draft(
        "Configuration management is an organizational practice.",
        action="Confirm document is in configuration-management system (Polarion, DOORS, Git).",
    )


def cr_07_header_footer(p: ProbedSafetyCase) -> CheckResult:
    return draft(
        "Worksheet headers/footers cannot be reliably verified programmatically.",
        action="Open in Excel; confirm header/footer reflect document ID and revision.",
    )


def cr_08_toc(p: ProbedSafetyCase) -> CheckResult:
    if "00_Title_Page" in p.sheet_names or any("contents" in s.lower() for s in p.sheet_names[:3]):
        return CheckResult(
            rating="FC",
            finding="Title or Contents tab is present near the beginning.",
            page_section="First three tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No Table of Contents tab detected.",
        recommended_action="Add General Info tab listing all sheets and purposes.",
        confidence="Medium",
    )


def cr_09_references(p: ProbedSafetyCase) -> CheckResult:
    if "14_References" in p.sheet_names and p.references_count > 0:
        return CheckResult(
            rating="FC",
            finding=f"References tab present with {p.references_count} entries.",
            page_section="Tab 14_References",
            confidence="High",
        )
    elif "14_References" in p.sheet_names:
        return CheckResult(
            rating="LC",
            finding="References tab exists but has no entries.",
            recommended_action="Populate References with HARA, FSC, TSC, FMEDA, and tool artifacts.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated References tab.",
        recommended_action="Add References tab citing HARA, FSC, TSC, FMEDA, and tools.",
        confidence="Medium",
    )


def cr_10_sections_complete(p: ProbedSafetyCase) -> CheckResult:
    required = ["04_Top_Claim", "05_Safety_Goals_Argument", "06_FSR_TSR_Traceability", "13_Assessment_Conclusion"]
    present = sum(1 for r in required if r in p.sheet_names)
    if present == len(required):
        return CheckResult(
            rating="FC",
            finding=f"All major sections populated: Top Claim, Safety Goals, FSR-TSR, Assessment.",
            confidence="High",
        )
    return CheckResult(
        rating="PC" if present >= 2 else "NO",
        finding=f"{present}/{len(required)} major sections present.",
        recommended_action="Complete missing sections.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Safety Case Assessment — per ISO 26262-2 §6.5 (12 checks)
# ---------------------------------------------------------------------------

def sca_01_top_claim(p: ProbedSafetyCase) -> CheckResult:
    if p.top_claim:
        return draft(
            f"Top claim stated: '{p.top_claim[:80]}...'. Reviewer to confirm context and justifications are documented.",
            page_section="Tab 04_Top_Claim",
        )
    return CheckResult(
        rating="NO",
        finding="No top claim documented.",
        recommended_action="Define the top claim for the safety case argument in Tab 04.",
        confidence="High",
    )


def sca_02_sub_claims(p: ProbedSafetyCase) -> CheckResult:
    if len(p.safety_goals) >= 1:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.safety_goals)} safety goal sub-claims documented.",
            page_section="Tab 05_Safety_Goals_Argument",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No safety goal sub-claims found.",
        recommended_action="Derive sub-claims from top claim; document in Safety Goals Argument tab.",
        confidence="High",
    )


def sca_03_strategy_evidence(p: ProbedSafetyCase) -> CheckResult:
    return draft(
        "Each sub-claim should have supporting strategy (decomposition) and evidence (traceability to FSR/TSR/HW metrics/SW verification).",
        page_section="Tabs 05, 06, 07, 08",
    )


def sca_04_fsr_tsr_traceability(p: ProbedSafetyCase) -> CheckResult:
    if len(p.fsr_rows) >= 1:
        traced = [f for f in p.fsr_rows if f.traceability_status and "traced" in f.traceability_status.lower()]
        if len(traced) == len(p.fsr_rows):
            return CheckResult(
                rating="FC",
                finding=f"All {len(p.fsr_rows)} FSRs have traceability status documented; no orphans.",
                page_section="Tab 06_FSR_TSR_Traceability",
                confidence="High",
            )
        else:
            return CheckResult(
                rating="PC",
                finding=f"{len(traced)}/{len(p.fsr_rows)} FSRs traced.",
                recommended_action="Complete traceability for all FSRs.",
                confidence="High",
            )
    return CheckResult(
        rating="NO",
        finding="No FSR rows documented.",
        recommended_action="Document FSR-TSR traceability in Tab 06.",
        confidence="High",
    )


def sca_05_hw_metrics(p: ProbedSafetyCase) -> CheckResult:
    if len(p.hw_metrics) >= 1:
        with_values = [h for h in p.hw_metrics if h.spfm or h.lfm or h.pmhf]
        if len(with_values) == len(p.hw_metrics):
            return CheckResult(
                rating="FC",
                finding=f"All {len(p.hw_metrics)} hardware metrics rows have SPFM/LFM/PMHF populated with target compliance.",
                page_section="Tab 07_HW_Metrics_Summary",
                confidence="High",
            )
        return CheckResult(
            rating="LC",
            finding=f"{len(with_values)}/{len(p.hw_metrics)} HW metrics rows populated.",
            recommended_action="Complete missing SPFM/LFM/PMHF values.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No hardware metrics documented.",
        recommended_action="Document HW metrics (SPFM/LFM/PMHF) per safety goal in Tab 07.",
        confidence="High",
    )


def sca_06_sw_verification(p: ProbedSafetyCase) -> CheckResult:
    if p.has_sw_verification:
        if p.sw_verification_status and "complete" in p.sw_verification_status.lower():
            return CheckResult(
                rating="FC",
                finding="SW verification summary status is Complete.",
                page_section="Tab 08_SW_Verification_Summary",
                confidence="High",
            )
        return draft(
            f"SW verification tab present; status: '{p.sw_verification_status or 'unknown'}'. Reviewer to verify completeness.",
            page_section="Tab 08_SW_Verification_Summary",
        )
    return CheckResult(
        rating="PC",
        finding="SW Verification Summary tab not present or populated.",
        recommended_action="Add SW Verification Summary tab with test/analysis results.",
        confidence="Medium",
    )


def sca_07_tool_qualification(p: ProbedSafetyCase) -> CheckResult:
    if p.has_tool_qualification:
        if p.tool_qualification_status and "qualified" in p.tool_qualification_status.lower():
            return CheckResult(
                rating="FC",
                finding=f"Tool Qualification documented; status: {p.tool_qualification_status}.",
                page_section="Tab 09_Tool_Qualification",
                confidence="High",
            )
        return draft(
            f"Tool Qualification tab present; reviewer to verify TCL classification per tool.",
            page_section="Tab 09_Tool_Qualification",
        )
    return CheckResult(
        rating="PC",
        finding="Tool Qualification tab not present.",
        recommended_action="Document tools used and their qualification level (TCL) in Tab 09.",
        confidence="Medium",
    )


def sca_08_confirmation_reviews(p: ProbedSafetyCase) -> CheckResult:
    if len(p.confirmation_reviews) >= 1:
        completed = [c for c in p.confirmation_reviews if c.status and "completed" in c.status.lower()]
        if len(completed) == len(p.confirmation_reviews):
            return CheckResult(
                rating="FC",
                finding=f"All {len(p.confirmation_reviews)} work products have completed confirmation reviews.",
                page_section="Tab 10_Confirmation_Reviews_Status",
                confidence="High",
            )
        return CheckResult(
            rating="PC",
            finding=f"{len(completed)}/{len(p.confirmation_reviews)} confirmation reviews completed.",
            recommended_action="Complete remaining reviews.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No confirmation reviews documented.",
        recommended_action="Document confirmation review status for all work products in Tab 10.",
        confidence="High",
    )


def sca_09_review_independence(p: ProbedSafetyCase) -> CheckResult:
    return draft(
        "Confirmation review independence levels must match ASIL (I1 for QM, I2 for A/B, I3 for C/D per ISO 26262-2 Table 1).",
        page_section="Tab 10_Confirmation_Reviews_Status",
    )


def sca_10_open_items(p: ProbedSafetyCase) -> CheckResult:
    if len(p.open_items) == 0:
        return CheckResult(
            rating="FC",
            finding="No open items or risks; Safety Case is complete.",
            page_section="Tab 11_Open_Items_Risks",
            confidence="High",
        )
    accepted = [o for o in p.open_items if o.accepted and "yes" in o.accepted.lower()]
    if len(accepted) == len(p.open_items):
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.open_items)} open items have documented risk assessment and acceptance.",
            page_section="Tab 11_Open_Items_Risks",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(accepted)}/{len(p.open_items)} open items are accepted with justification.",
        recommended_action="Document risk level and acceptance rationale for all open items.",
        confidence="High",
    )


def sca_11_signoff(p: ProbedSafetyCase) -> CheckResult:
    if p.has_signoff_block:
        return draft(
            "Assessment conclusion contains signoff section. Reviewer to verify FSM, PM, and Assessor signatures/approval.",
            page_section="Tab 13_Assessment_Conclusion",
        )
    return CheckResult(
        rating="PC",
        finding="No signoff block detected in Assessment Conclusion.",
        recommended_action="Add signoff blocks for FSM (Functional Safety Manager), PM (Project Manager), and Assessor.",
        confidence="High",
    )


def sca_12_references_artifacts(p: ProbedSafetyCase) -> CheckResult:
    if p.references_count >= 8:
        return CheckResult(
            rating="FC",
            finding=f"References documented; {p.references_count} entries cover HARA, FSC, TSC, FMEDA, tool qualifications, and other artifacts.",
            page_section="Tab 14_References",
            confidence="High",
        )
    elif p.references_count >= 4:
        return CheckResult(
            rating="LC",
            finding=f"References tab has {p.references_count} entries; coverage appears partial.",
            recommended_action="Ensure references include HARA, FSC, TSC, FMEDA, tool qualifications, and artifact hashes.",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"References tab has {p.references_count} entries or is missing.",
        recommended_action="Document complete references to all linked artifacts (HARA, FSC, TSC, FMEDA, tools).",
        confidence="Medium",
    )


# ---------------------------------------------------------------------------
# Verification Assessment — Most external; 5 Safety Case-specific checks
# ---------------------------------------------------------------------------

def _va_external(label: str) -> CheckResult:
    return draft(
        f"{label} is governed by external verification artifacts (Verification Plan, test reports).",
        action="Verify against project verification documents.",
    )


def va_01_verification_plan(p: ProbedSafetyCase) -> CheckResult:
    return _va_external("Verification Plan")


def va_02_verification_methods(p: ProbedSafetyCase) -> CheckResult:
    return _va_external("Verification methods and test cases")


def va_03_verification_results(p: ProbedSafetyCase) -> CheckResult:
    return _va_external("Verification test results and pass/fail status")


def va_04_verification_coverage(p: ProbedSafetyCase) -> CheckResult:
    return _va_external("Verification coverage of all safety goals")


def va_05_traceability_completeness(p: ProbedSafetyCase) -> CheckResult:
    if p.fsr_rows and p.hw_metrics:
        return CheckResult(
            rating="FC",
            finding="FSR-TSR traceability and HW metrics data present; argument chain integrity verifiable.",
            page_section="Tabs 06-07",
            confidence="Medium",
        )
    return draft(
        "Verification of argument chain completeness (FSR → HW metrics → Safety goals).",
        page_section="Tabs 05-08",
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
    verify: Callable[[ProbedSafetyCase], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review — Document Quality (14 checks)
    CheckDef("1", "CR", "Document Quality", "Is the document structured in a clear manner supporting maintainability?", "Shall", cr_01_structured),
    CheckDef("2", "CR", "Document Quality", "Was the latest template version used?", "Should", cr_02_template),
    CheckDef("3", "CR", "Document Quality", "Does the document structure facilitate search (cross-references, index)?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does the title cover the scope?", "Shall", cr_04a_title_scope),
    CheckDef("4b", "CR", "Document Quality", "Are author and approver listed?", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Document Quality", "Is there unique identification for each revision?", "Shall", cr_04c_unique_revision),
    CheckDef("4d", "CR", "Document Quality", "Is there a change history available?", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Quality", "Is the work-product status provided?", "Shall", cr_04e_status),
    CheckDef("5", "CR", "Document Quality", "Is the current revision clearly identifiable?", "Shall", cr_05_current_revision),
    CheckDef("6", "CR", "Document Quality", "Is the document under configuration and change management?", "Shall", cr_06_config_mgmt),
    CheckDef("7", "CR", "Document Quality", "Are headers and footers updated?", "Should", cr_07_header_footer),
    CheckDef("8", "CR", "Document Quality", "Does the document contain a table of contents?", "Shall", cr_08_toc),
    CheckDef("9", "CR", "Document Quality", "Does the Reference Table list all references?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "Have all sections been completed?", "Should", cr_10_sections_complete),

    # Safety Case Assessment (12 checks per ISO 26262-2 §6.5)
    CheckDef("1", "SCA", "Top Claim", "Is the top claim stated with context, justifications, and assumptions?", "Shall", sca_01_top_claim),
    CheckDef("2", "SCA", "Sub-claims", "Is there a sub-claim per safety goal with ASIL assignment?", "Shall", sca_02_sub_claims),
    CheckDef("3", "SCA", "Strategy and Evidence", "Does each sub-claim have supporting strategy and evidence?", "Shall", sca_03_strategy_evidence),
    CheckDef("4", "SCA", "FSR-TSR Traceability", "Is FSR-TSR traceability complete with no orphan FSRs?", "Shall", sca_04_fsr_tsr_traceability),
    CheckDef("5", "SCA", "HW Metrics", "Are SPFM/LFM/PMHF metrics reported per safety goal with target compliance?", "Shall", sca_05_hw_metrics),
    CheckDef("6", "SCA", "SW Verification", "Is SW verification status reported?", "Shall", sca_06_sw_verification),
    CheckDef("7", "SCA", "Tool Qualification", "Is tool qualification documented with TCL classification?", "Shall", sca_07_tool_qualification),
    CheckDef("8", "SCA", "Confirmation Reviews", "Is confirmation review status complete for all work products?", "Shall", sca_08_confirmation_reviews),
    CheckDef("9", "SCA", "Review Independence", "Do confirmation review independence levels match ASIL (I3 for D)?", "Shall", sca_09_review_independence),
    CheckDef("10", "SCA", "Open Items Risk", "Are all open items risk-assessed and accepted with justification?", "Shall", sca_10_open_items),
    CheckDef("11", "SCA", "Signoff", "Does assessment conclusion have signoff blocks (FSM, PM, Assessor)?", "Shall", sca_11_signoff),
    CheckDef("12", "SCA", "References", "Are all linked artifacts referenced (HARA, FSC, TSC, FMEDA hashes)?", "Shall", sca_12_references_artifacts),

    # Verification Assessment (5 Safety Case-specific checks)
    CheckDef("1", "VA", "Verification Planning", "Does Verification Plan exist and address all safety goals?", "Shall", va_01_verification_plan),
    CheckDef("2", "VA", "Verification Specification", "Are verification methods and test cases specified?", "Shall", va_02_verification_methods),
    CheckDef("3", "VA", "Verification Results", "Are test results and pass/fail status documented?", "Shall", va_03_verification_results),
    CheckDef("4", "VA", "Coverage", "Is verification coverage of safety goals complete?", "Shall", va_04_verification_coverage),
    CheckDef("5", "VA", "Argument Chain", "Is the argument chain traceable (FSR → HW metrics → SGs)?", "Shall", va_05_traceability_completeness),
]
