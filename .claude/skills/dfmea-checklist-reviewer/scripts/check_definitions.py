"""
Canonical DFMEA checklist definitions per AIAG-VDA 2019 and ISO 26262-3.

- Confirmation Review (CR): 14 generic doc-quality checks
- DFMEA Assessment (DFMEAA): 14 substantive DFMEA-specific checks
- Verification Assessment (VA): External verification
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from dfmea_probe import ProbedDfmea


@dataclass
class CheckResult:
    rating: str = ""              # FC / LC / PC / NO / NA / "" (pending)
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
# Confirmation Review (14 generic doc-quality checks)
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedDfmea) -> CheckResult:
    if len(p.sheet_names) >= 10:
        return CheckResult(
            rating="FC",
            finding=f"Document is structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="High",
        )
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs; AIAG-VDA recommends 12+.", confidence="High")


def cr_02_template(p: ProbedDfmea) -> CheckResult:
    if p.is_dfmea_builder_format:
        return CheckResult(rating="FC", finding="AIAG-VDA 2019 template detected.", confidence="High")
    return draft("Template version cannot be verified from xlsx content alone.", action="Confirm AIAG-VDA 2019 template was used.")


def cr_03_searchable(p: ProbedDfmea) -> CheckResult:
    has_toc = any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3])
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_toc and has_ref:
        return CheckResult(rating="FC", finding="Document has Title and References tabs.", confidence="High")
    return CheckResult(rating="PC", finding="Missing TOC or References tab.", recommended_action="Add search aids.", confidence="High")


def cr_04a_title_scope(p: ProbedDfmea) -> CheckResult:
    if p.title:
        return draft(f"Title: '{p.title}'. Reviewer to confirm scope coverage.", page_section="Title page")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add document title.", confidence="High")


def cr_04b_author_approver(p: ProbedDfmea) -> CheckResult:
    if p.fmea_owner:
        return CheckResult(rating="FC", finding=f"FMEA Owner: '{p.fmea_owner}'.", confidence="High")
    return CheckResult(rating="NO", finding="FMEA Owner not identified.", recommended_action="Assign FMEA owner.", confidence="High")


def cr_04c_unique_revision(p: ProbedDfmea) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision: '{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="Revision not populated.", recommended_action="Add unique revision ID.", confidence="High")


def cr_04d_change_history(p: ProbedDfmea) -> CheckResult:
    if "01_Document_Control" in p.sheet_names:
        return CheckResult(rating="FC", finding="Document Control tab present.", page_section="01_Document_Control", confidence="High")
    return CheckResult(rating="PC", finding="No Document Control tab.", recommended_action="Add revision history.", confidence="High")


def cr_04e_status(p: ProbedDfmea) -> CheckResult:
    if p.status:
        return CheckResult(rating="FC", finding=f"Status: '{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="Status field not populated.", recommended_action="Set status (Draft/Review/Released).", confidence="High")


def cr_05_current_revision(p: ProbedDfmea) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Current revision '{p.revision}' is identifiable.", confidence="High")
    return CheckResult(rating="NO", finding="Current revision not identifiable.", recommended_action="Populate Revision field.", confidence="High")


def cr_06_config_mgmt(p: ProbedDfmea) -> CheckResult:
    return draft("Configuration management is an organizational practice.", action="Confirm document is under CM system.")


def cr_07_header_footer(p: ProbedDfmea) -> CheckResult:
    return draft("Headers/footers cannot be verified programmatically.", action="Manually confirm headers/footers.")


def cr_08_toc(p: ProbedDfmea) -> CheckResult:
    has_toc = any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3])
    if has_toc:
        return CheckResult(rating="FC", finding="TOC or General Info tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No TOC detected.", recommended_action="Add TOC.", confidence="High")


def cr_09_references(p: ProbedDfmea) -> CheckResult:
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_ref:
        return CheckResult(rating="FC", finding="References tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add References sheet.", confidence="High")


def cr_10_sections_complete(p: ProbedDfmea) -> CheckResult:
    n_elems = len(p.system_elements) + len(p.subsystem_elements) + len(p.component_elements)
    if n_elems > 0:
        return CheckResult(rating="FC", finding=f"Structure Analysis has {n_elems} elements.", confidence="High")
    return CheckResult(rating="PC", finding="Structure Analysis appears incomplete.", recommended_action="Populate element hierarchy.", confidence="High")


def cr_11_doc_id(p: ProbedDfmea) -> CheckResult:
    if p.fmea_id:
        return CheckResult(rating="FC", finding=f"FMEA ID: '{p.fmea_id}'.", confidence="High")
    return CheckResult(rating="NO", finding="FMEA ID not populated.", recommended_action="Add unique FMEA identifier.", confidence="High")


def cr_12_project_id(p: ProbedDfmea) -> CheckResult:
    if p.project_name:
        return CheckResult(rating="FC", finding=f"Project: '{p.project_name}'.", confidence="High")
    return draft("Project name not detected.", action="Add project context.")


def cr_13_references_complete(p: ProbedDfmea) -> CheckResult:
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_ref:
        return draft("References tab present; reviewer to confirm AIAG-VDA 2019 Handbook is cited.", page_section="References tab")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add References with AIAG-VDA citation.", confidence="High")


def cr_14_all_sections_complete(p: ProbedDfmea) -> CheckResult:
    has_all = all(t in p.sheet_names for t in ["00_Title_Page", "03_Structure_Analysis", "05_DFMEA_Worksheet"])
    if has_all:
        return CheckResult(rating="FC", finding="All core DFMEA tabs present.", confidence="High")
    return CheckResult(rating="PC", finding="Some core tabs missing.", recommended_action="Ensure AIAG-VDA structure.", confidence="High")


# ---------------------------------------------------------------------------
# DFMEA Assessment (14 substantive checks per AIAG-VDA 2019)
# ---------------------------------------------------------------------------

def dfmeaa_01_header_block(p: ProbedDfmea) -> CheckResult:
    if p.subject and p.fmea_owner and p.fmea_id:
        return CheckResult(
            rating="FC",
            finding=f"Header block complete: subject='{p.subject}', owner='{p.fmea_owner}', ID='{p.fmea_id}'.",
            page_section="02_Header_Block",
            confidence="High",
        )
    missing = [x for x in ["subject", "FMEA owner", "FMEA ID"]
               if not (p.subject if "subject" in x else (p.fmea_owner if "owner" in x else p.fmea_id))]
    return CheckResult(rating="PC", finding=f"Missing header fields: {', '.join(missing)}.", recommended_action="Complete header block.", confidence="High")


def dfmeaa_02_structure_populated(p: ProbedDfmea) -> CheckResult:
    n_sys = len(p.system_elements)
    n_sub = len(p.subsystem_elements)
    n_comp = len(p.component_elements)
    if n_sys > 0 and (n_sub > 0 or n_comp > 0):
        return CheckResult(rating="FC", finding=f"Structure: {n_sys} systems, {n_sub} subsystems, {n_comp} components.", confidence="High")
    return CheckResult(rating="PC", finding="Structure Analysis incomplete.", recommended_action="Populate system/subsystem/component hierarchy.", confidence="High")


def dfmeaa_03_function_analysis_populated(p: ProbedDfmea) -> CheckResult:
    if len(p.functions) > 0:
        return CheckResult(rating="FC", finding=f"Function Analysis: {len(p.functions)} functions documented.", confidence="High")
    return CheckResult(rating="PC", finding="Function Analysis appears empty.", recommended_action="Document all system functions.", confidence="High")


def dfmeaa_04_dfmea_worksheet_rows(p: ProbedDfmea) -> CheckResult:
    if len(p.dfmea_rows) == 0:
        return CheckResult(rating="NO", finding="DFMEA Worksheet has no failure mode rows.", recommended_action="Populate DFMEA worksheet.", confidence="High")
    with_fm = [r for r in p.dfmea_rows if r.failure_mode]
    with_fe = [r for r in p.dfmea_rows if r.failure_effect]
    with_cause = [r for r in p.dfmea_rows if r.failure_cause]
    complete = min(len(with_fm) / len(p.dfmea_rows), len(with_fe) / len(p.dfmea_rows), len(with_cause) / len(p.dfmea_rows))
    if complete >= 0.95:
        return CheckResult(rating="FC", finding=f"All {len(p.dfmea_rows)} rows have FM/FE/Cause populated.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_fm)}/{len(p.dfmea_rows)} rows complete.", recommended_action="Ensure all rows have FM/FE/Cause.", confidence="High")


def dfmeaa_05_severity_rated(p: ProbedDfmea) -> CheckResult:
    if not p.dfmea_rows:
        return na("No DFMEA rows.")
    with_s = [r for r in p.dfmea_rows if 1 <= r.severity <= 10]
    if len(with_s) == len(p.dfmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.dfmea_rows)} failure modes have Severity (1-10).", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_s)}/{len(p.dfmea_rows)} have Severity rated.", recommended_action="Rate all severity values 1-10.", confidence="High")


def dfmeaa_06_occurrence_rated(p: ProbedDfmea) -> CheckResult:
    if not p.dfmea_rows:
        return na("No DFMEA rows.")
    with_o = [r for r in p.dfmea_rows if 1 <= r.occurrence <= 10]
    if len(with_o) == len(p.dfmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.dfmea_rows)} failure modes have Occurrence (1-10).", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_o)}/{len(p.dfmea_rows)} have Occurrence rated.", recommended_action="Rate all occurrence values 1-10.", confidence="High")


def dfmeaa_07_detection_rated(p: ProbedDfmea) -> CheckResult:
    if not p.dfmea_rows:
        return na("No DFMEA rows.")
    with_d = [r for r in p.dfmea_rows if 1 <= r.detection <= 10]
    if len(with_d) == len(p.dfmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.dfmea_rows)} failure modes have Detection (1-10).", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_d)}/{len(p.dfmea_rows)} have Detection rated.", recommended_action="Rate all detection values 1-10.", confidence="High")


def dfmeaa_08_action_priority(p: ProbedDfmea) -> CheckResult:
    if not p.dfmea_rows:
        return na("No DFMEA rows.")
    with_ap = [r for r in p.dfmea_rows if r.action_priority]
    if len(with_ap) == len(p.dfmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.dfmea_rows)} failure modes have Action Priority assigned.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_ap)}/{len(p.dfmea_rows)} have AP assigned.", recommended_action="Ensure AP is computed for all rows.", confidence="High")


def dfmeaa_09_high_ap_actions(p: ProbedDfmea) -> CheckResult:
    if p.high_ap_count == 0:
        return CheckResult(rating="FC", finding="No High-AP items pending action.", confidence="High")
    with_action = [r for r in p.dfmea_rows if "H" in r.action_priority.upper() and r.recommended_action]
    if len(with_action) == p.high_ap_count:
        return CheckResult(rating="FC", finding=f"All {p.high_ap_count} High-AP items have recommended actions.", confidence="High")
    return CheckResult(rating="NO", finding=f"{p.high_ap_count} High-AP items; {len(with_action)} have actions assigned.", recommended_action="Assign actions to all High-AP items.", confidence="High")


def dfmeaa_10_action_plan_owner_duedate(p: ProbedDfmea) -> CheckResult:
    if not p.action_items:
        return na("No action items in tracker.")
    with_owner = [a for a in p.action_items if a.owner]
    with_due = [a for a in p.action_items if a.due_date]
    if len(with_owner) == len(p.action_items) and len(with_due) == len(p.action_items):
        return CheckResult(rating="FC", finding=f"All {len(p.action_items)} actions have owner and due date.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_owner)}/{len(p.action_items)} have owner, {len(with_due)} have due date.", recommended_action="Complete owner and due-date fields.", confidence="High")


def dfmeaa_11_special_chars(p: ProbedDfmea) -> CheckResult:
    high_sev_modes = [r for r in p.dfmea_rows if r.severity >= 8]
    if not high_sev_modes:
        return CheckResult(rating="FC", finding="No high-severity failure modes requiring special characteristics.", confidence="High")
    if len(p.special_characteristics) > 0:
        return CheckResult(rating="FC", finding=f"Special Characteristics identified: {len(p.special_characteristics)} items.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(high_sev_modes)} high-severity modes found; {len(p.special_characteristics)} SCs identified.", recommended_action="Identify SCs for severity >= 8 modes.", confidence="High")


def dfmeaa_12_lessons_learned(p: ProbedDfmea) -> CheckResult:
    has_lessons = any("lesson" in s.lower() for s in p.sheet_names)
    if has_lessons:
        return CheckResult(rating="FC", finding="Lessons Learned tab present.", confidence="High")
    return draft("Lessons Learned cross-reference missing.", action="Document prior DFMEA reuse and lessons.")


def dfmeaa_13_references_aiag_vda(p: ProbedDfmea) -> CheckResult:
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_ref:
        return draft("References tab present; reviewer to confirm AIAG-VDA 2019 Handbook is cited.", page_section="References")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add AIAG-VDA 2019 citation.", confidence="High")


def dfmeaa_14_high_ap_pending(p: ProbedDfmea) -> CheckResult:
    """Headline metric: count of high-AP items without completed actions."""
    pending = [r for r in p.dfmea_rows if "H" in r.action_priority.upper() and r.status and "complete" not in r.status.lower()]
    if pending:
        return CheckResult(
            rating="NO",
            finding=f"HEADLINE: {len(pending)} High-AP items pending completion.",
            recommended_action=f"Track and close all {len(pending)} pending high-priority actions.",
            confidence="High",
        )
    return CheckResult(rating="FC", finding="No High-AP items pending.", confidence="High")


# ---------------------------------------------------------------------------
# Verification Assessment (external verification)
# ---------------------------------------------------------------------------

def _va_external(label: str) -> CheckResult:
    return draft(f"{label} is governed by external Verification Plan/Report.", action="Verify against project Verification Plan.")


def va_01_plan_compliance(p): return _va_external("Verification Plan ensuring DFMEA compliance")
def va_02_content(p): return _va_external("Verification methods, criteria, environment")
def va_03_executed(p): return _va_external("Verification executed per plan")
def va_04_report(p): return _va_external("Verification Report with evidence")


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedDfmea], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review (CR)
    CheckDef("1",  "CR", "Document Quality", "Is document structured clearly?", "Shall", cr_01_structured),
    CheckDef("2",  "CR", "Document Quality", "Was AIAG-VDA 2019 template used?", "Should", cr_02_template),
    CheckDef("3",  "CR", "Document Quality", "Does structure facilitate search?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does title cover scope?", "Shall", cr_04a_title_scope),
    CheckDef("4b", "CR", "Document Quality", "Is FMEA owner identified?", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Document Quality", "Is revision uniquely identified?", "Shall", cr_04c_unique_revision),
    CheckDef("4d", "CR", "Document Quality", "Is change history available?", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Quality", "Is work-product status provided?", "Shall", cr_04e_status),
    CheckDef("5",  "CR", "Document Quality", "Is current revision clearly identifiable?", "Shall", cr_05_current_revision),
    CheckDef("6",  "CR", "Document Quality", "Is document under configuration management?", "Shall", cr_06_config_mgmt),
    CheckDef("7",  "CR", "Document Quality", "Are headers/footers updated?", "Should", cr_07_header_footer),
    CheckDef("8",  "CR", "Document Quality", "Is table of contents correct?", "Shall", cr_08_toc),
    CheckDef("9",  "CR", "Document Quality", "Does Reference Table list all citations?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "Have all sections been completed?", "Should", cr_10_sections_complete),
    CheckDef("11", "CR", "Document Quality", "Is FMEA ID unique and persistent?", "Shall", cr_11_doc_id),
    CheckDef("12", "CR", "Document Quality", "Is project context identified?", "Should", cr_12_project_id),
    CheckDef("13", "CR", "Document Quality", "Are all references complete?", "Should", cr_13_references_complete),
    CheckDef("14", "CR", "Document Quality", "Are all DFMEA sections populated?", "Shall", cr_14_all_sections_complete),

    # DFMEA Assessment (DFMEAA)
    CheckDef("1",  "DFMEAA", "Header Block", "Is header block complete (subject, owner, ID)?", "Shall", dfmeaa_01_header_block),
    CheckDef("2",  "DFMEAA", "Structure", "Is structure analysis populated?", "Shall", dfmeaa_02_structure_populated),
    CheckDef("3",  "DFMEAA", "Functions", "Is function analysis populated?", "Shall", dfmeaa_03_function_analysis_populated),
    CheckDef("4",  "DFMEAA", "DFMEA Worksheet", "Are DFMEA rows complete (FM/FE/Cause)?", "Shall", dfmeaa_04_dfmea_worksheet_rows),
    CheckDef("5",  "DFMEAA", "Risk Assessment", "Is Severity rated 1-10 for all failure modes?", "Shall", dfmeaa_05_severity_rated),
    CheckDef("6",  "DFMEAA", "Risk Assessment", "Is Occurrence rated 1-10 for all failure modes?", "Shall", dfmeaa_06_occurrence_rated),
    CheckDef("7",  "DFMEAA", "Risk Assessment", "Is Detection rated 1-10 for all failure modes?", "Shall", dfmeaa_07_detection_rated),
    CheckDef("8",  "DFMEAA", "Risk Assessment", "Is Action Priority computed for all modes?", "Shall", dfmeaa_08_action_priority),
    CheckDef("9",  "DFMEAA", "Action Planning", "Do all High-AP items have recommended actions?", "Shall", dfmeaa_09_high_ap_actions),
    CheckDef("10", "DFMEAA", "Action Tracking", "Does Action Plan have owner and due date?", "Shall", dfmeaa_10_action_plan_owner_duedate),
    CheckDef("11", "DFMEAA", "Special Characteristics", "Are special characteristics identified?", "Should", dfmeaa_11_special_chars),
    CheckDef("12", "DFMEAA", "Learning", "Are lessons learned documented?", "Should", dfmeaa_12_lessons_learned),
    CheckDef("13", "DFMEAA", "References", "Is AIAG-VDA 2019 Handbook referenced?", "Should", dfmeaa_13_references_aiag_vda),
    CheckDef("14", "DFMEAA", "Headline", "How many High-AP items are pending closure?", "Shall", dfmeaa_14_high_ap_pending),

    # Verification Assessment (VA)
    CheckDef("1",  "VA", "External Verification", "Does Verification Plan ensure DFMEA compliance?", "Shall", va_01_plan_compliance),
    CheckDef("2",  "VA", "External Verification", "Does plan address methods, criteria, environment?", "Shall", va_02_content),
    CheckDef("3",  "VA", "External Verification", "Was verification executed per plan?", "Shall", va_03_executed),
    CheckDef("4",  "VA", "External Verification", "Does Report include results and evidence?", "Shall", va_04_report),
]
