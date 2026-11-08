"""
Canonical checklist definitions and verification logic for Safety Plan.

Each check is a CheckDef with:
- id: row id (e.g. "1", "10")
- tab: output tab (CR / SPA / VA)
- section: section header
- requirement: requirement text
- obligation: "Shall" or "Should"
- verify: callable that returns CheckResult
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from safety_plan_probe import ProbedSafetyPlan


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    rating: str = ""              # FC / LC / PC / NO / NA / "" (pending)
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""          # High / Medium / Low


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
# Confirmation Review checks (14 doc-quality checks)
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedSafetyPlan) -> CheckResult:
    if len(p.sheet_names) >= 8:
        return CheckResult(
            rating="FC",
            finding=f"Safety Plan structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.sheet_names)} tabs; structure may be insufficient.",
        recommended_action="Add separate tabs for distinct concerns (roles, tailoring, work products, reviews, tools, schedule).",
        confidence="Medium",
    )


def cr_02_template(p: ProbedSafetyPlan) -> CheckResult:
    return draft(
        "Template version cannot be detected from xlsx content alone.",
        action="Confirm the latest applicable Safety Plan template was used at document creation.",
    )


def cr_03_searchable(p: ProbedSafetyPlan) -> CheckResult:
    if len(p.sheet_names) >= 5 and p.sheet_names[0].lower().startswith("0"):
        return CheckResult(
            rating="FC",
            finding="Document has structured tab naming (0x_Prefix_Name format); structured columns aid search.",
            page_section=f"Sheets: {p.sheet_names[0:3]}",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Tab naming not fully structured for navigation.",
        recommended_action="Use consistent tab naming (0x_Section_Name) and add cross-references.",
        confidence="Medium",
    )


def cr_04a_title_scope(p: ProbedSafetyPlan) -> CheckResult:
    if p.title:
        return draft(
            f"Title is: '{p.title}'. Reviewer to confirm it covers the document scope.",
            page_section="Title page row 2",
        )
    return CheckResult(
        rating="NO",
        finding="No title detected on the Title page.",
        recommended_action="Add a clear document title that reflects the scope.",
        confidence="High",
    )


def cr_04b_author_approver(p: ProbedSafetyPlan) -> CheckResult:
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
        finding=f"Missing on Title page: {', '.join(missing)}.",
        recommended_action=f"Populate {', '.join(missing)} field(s) on the Title page.",
        confidence="High",
    )


def cr_04c_unique_revision(p: ProbedSafetyPlan) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Revision='{p.revision}' is set on the Title page.",
            page_section="Title page Revision field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Revision field not populated on Title page.",
        recommended_action="Populate the Revision field; ensure each revision has a unique identifier.",
        confidence="High",
    )


def cr_04d_change_history(p: ProbedSafetyPlan) -> CheckResult:
    if p.is_safety_plan_builder_format:
        return CheckResult(
            rating="FC",
            finding="Safety-plan-builder format includes Document Control tab for revision history.",
            page_section="01_Document_Control",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Cannot verify revision history; assumes Document Control tab exists.",
        recommended_action="Ensure a populated revision history table exists on the Document Control tab.",
        confidence="Medium",
    )


def cr_04e_status(p: ProbedSafetyPlan) -> CheckResult:
    if p.status:
        return CheckResult(
            rating="FC",
            finding=f"Status='{p.status}' is set on the Title page.",
            page_section="Title page Status field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No work-product status field populated on the Title page.",
        recommended_action="Add a Status field (Draft / In Review / Released) to the Title page.",
        confidence="High",
    )


def cr_05_current_revision(p: ProbedSafetyPlan) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Current revision '{p.revision}' is identifiable on Title page.",
            page_section="Title page Revision field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Current revision is not identifiable.",
        recommended_action="Populate the Revision field on the Title page.",
        confidence="High",
    )


def cr_06_config_mgmt(p: ProbedSafetyPlan) -> CheckResult:
    return draft(
        "Configuration management is an organizational practice; cannot be verified from xlsx content.",
        action="Confirm the document is checked into the project's configuration-management system (e.g., Polarion, DOORS, Git).",
    )


def cr_07_header_footer(p: ProbedSafetyPlan) -> CheckResult:
    return draft(
        "Worksheet headers/footers cannot be reliably verified programmatically.",
        action="Open the workbook in Excel and confirm header/footer reflect current document ID and revision.",
    )


def cr_08_toc(p: ProbedSafetyPlan) -> CheckResult:
    if p.sheet_names and p.sheet_names[0].lower().startswith("0"):
        return CheckResult(
            rating="FC",
            finding="Document has numbered tabs (0x_Name format) that function as table of contents.",
            page_section=f"Sheet structure starting with '{p.sheet_names[0]}'",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No explicit Table of Contents tab detected.",
        recommended_action="Add a Table of Contents tab or use consistent numbered tab naming.",
        confidence="Medium",
    )


def cr_09_references(p: ProbedSafetyPlan) -> CheckResult:
    refs_sheet = next((s for s in p.sheet_names if "reference" in s.lower()), None)
    if refs_sheet:
        return draft(
            f"References-style content found on sheet '{refs_sheet}'. Reviewer to confirm completeness.",
            page_section=f"Sheet '{refs_sheet}'",
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated References tab detected.",
        recommended_action="Add a References tab citing ISO 26262, item definition, HARA, and related planning documents.",
        confidence="Medium",
    )


def cr_10_sections_complete(p: ProbedSafetyPlan) -> CheckResult:
    # Heuristic: check if major tabs are populated
    critical_tabs = ["02_Project_Info", "03_Roles_Responsibilities", "05_Work_Products", "06_Confirmation_Reviews"]
    present = sum(1 for t in critical_tabs if any(t.lower() in s.lower() for s in p.sheet_names))
    if present >= 3:
        return CheckResult(
            rating="FC",
            finding=f"Safety Plan has {present}/{len(critical_tabs)} critical sections populated.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {present}/{len(critical_tabs)} critical sections found.",
        recommended_action="Complete Project Info, Roles, Work Products, and Confirmation Reviews tabs.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Safety Plan Assessment checks (14 substantive per ISO 26262-2 §6)
# ---------------------------------------------------------------------------

def spa_01_fsm_assigned(p: ProbedSafetyPlan) -> CheckResult:
    # Check if any role has "FSM" or "Functional Safety Manager"
    fsm_roles = [r for r in p.roles if "fsm" in r.role.lower() or "functional safety manager" in r.role.lower()]
    if fsm_roles:
        return CheckResult(
            rating="FC",
            finding=f"Functional Safety Manager assigned: {fsm_roles[0].name} ({fsm_roles[0].role}).",
            page_section="03_Roles_Responsibilities",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No Functional Safety Manager role identified.",
        recommended_action="Assign a Functional Safety Manager and document in Roles & Responsibilities tab.",
        confidence="High",
    )


def spa_02_roles_defined(p: ProbedSafetyPlan) -> CheckResult:
    if len(p.roles) < 3:
        return CheckResult(
            rating="NO",
            finding=f"Only {len(p.roles)} roles defined; minimum roles (FSM, Project Mgr, HW/SW Leads) not visible.",
            recommended_action="Define and assign key roles: Functional Safety Manager, Project Manager, Hardware Lead, Software Lead.",
            confidence="High",
        )
    role_types = {r.role.lower() for r in p.roles}
    expected = {"fsm", "project manager", "hardware", "software"}
    found = sum(1 for exp in expected if any(exp in rt for rt in role_types))
    if found >= 3:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.roles)} roles defined including key leadership positions.",
            page_section="03_Roles_Responsibilities",
            confidence="High",
        )
    return CheckResult(
        rating="LC",
        finding=f"{len(p.roles)} roles defined; some key roles may be missing.",
        recommended_action="Ensure FSM, Project Manager, Hardware Lead, and Software Lead are assigned.",
        confidence="Medium",
    )


def spa_03_tailoring_justified(p: ProbedSafetyPlan) -> CheckResult:
    if not p.tailoring_decisions:
        return CheckResult(
            rating="FC",
            finding="No tailoring decisions (all clauses applicable); no justification required.",
            page_section="04_Tailoring",
            confidence="High",
        )
    # Count decisions with justification
    with_just = sum(1 for v in p.tailoring_decisions.values() if ":" in v and v.split(":")[1].strip())
    total = len(p.tailoring_decisions)
    if with_just == total:
        return CheckResult(
            rating="FC",
            finding=f"All {total} tailoring decisions justified.",
            page_section="04_Tailoring",
            confidence="High",
        )
    if with_just >= total * 0.8:
        return CheckResult(
            rating="LC",
            finding=f"{with_just}/{total} tailoring decisions have justification.",
            recommended_action=f"Add justification for {total - with_just} remaining tailoring decisions.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {with_just}/{total} tailoring decisions justified.",
        recommended_action="Add written justification for all 'Partial' or 'Not Applicable' decisions per ISO 26262-2:2018 clause 6.3.2.",
        confidence="High",
    )


def spa_04_work_products_listed(p: ProbedSafetyPlan) -> CheckResult:
    expected_wps = {"HARA", "FSC", "TSC", "FMEDA", "Safety Case"}
    found_wps = {wp.name for wp in p.work_products if wp.name}
    matched = sum(1 for exp in expected_wps if any(exp.lower() in name.lower() for name in found_wps))
    if len(p.work_products) >= 5 and matched >= 3:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.work_products)} work products listed; key WPs (HARA, FSC, TSC, etc.) present.",
            page_section="05_Work_Products",
            confidence="High",
        )
    if len(p.work_products) >= 3:
        return CheckResult(
            rating="LC",
            finding=f"{len(p.work_products)} work products listed.",
            recommended_action="Ensure HARA, Functional Safety Concept, Technical Safety Concept, and Safety Case are included.",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.work_products)} work products listed.",
        recommended_action="List all safety-relevant work products per ISO 26262-2:2018 clause 6.4.",
        confidence="High",
    )


def spa_05_wp_owner_assigned(p: ProbedSafetyPlan) -> CheckResult:
    without_owner = [wp for wp in p.work_products if not wp.owner]
    if not without_owner:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.work_products)} work products have an assigned owner.",
            page_section="05_Work_Products, Owner column",
            confidence="High",
        )
    rate = (len(p.work_products) - len(without_owner)) / len(p.work_products) if p.work_products else 0
    if rate >= 0.8:
        return CheckResult(
            rating="LC",
            finding=f"{len(p.work_products) - len(without_owner)}/{len(p.work_products)} WPs have owners.",
            recommended_action=f"Assign owners to {len(without_owner)} work products.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.work_products) - len(without_owner)}/{len(p.work_products)} work products have assigned owners.",
        recommended_action="Assign a responsible person/team to each work product.",
        confidence="High",
    )


def spa_06_wp_planned_date(p: ProbedSafetyPlan) -> CheckResult:
    without_date = [wp for wp in p.work_products if not wp.planned_date]
    if not without_date:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.work_products)} work products have planned dates.",
            page_section="05_Work_Products, Planned Date column",
            confidence="High",
        )
    rate = (len(p.work_products) - len(without_date)) / len(p.work_products) if p.work_products else 0
    if rate >= 0.9:
        return CheckResult(
            rating="LC",
            finding=f"{len(p.work_products) - len(without_date)}/{len(p.work_products)} WPs have planned dates.",
            recommended_action=f"Set planned delivery dates for {len(without_date)} work products.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.work_products) - len(without_date)}/{len(p.work_products)} work products have planned dates.",
        recommended_action="Define planned completion dates for all work products.",
        confidence="High",
    )


def spa_07_wp_asil_specified(p: ProbedSafetyPlan) -> CheckResult:
    without_asil = [wp for wp in p.work_products if not wp.target_asil]
    if not without_asil:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.work_products)} work products have target ASIL specified.",
            page_section="05_Work_Products, Target ASIL column",
            confidence="High",
        )
    rate = (len(p.work_products) - len(without_asil)) / len(p.work_products) if p.work_products else 0
    if rate >= 0.95:
        return CheckResult(
            rating="LC",
            finding=f"{len(p.work_products) - len(without_asil)}/{len(p.work_products)} WPs have ASIL.",
            recommended_action=f"Specify target ASIL for {len(without_asil)} work products.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.work_products) - len(without_asil)}/{len(p.work_products)} work products have target ASIL.",
        recommended_action="Specify the target ASIL for each work product per ISO 26262-2:2018 clause 6.4.1.",
        confidence="High",
    )


def spa_08_cr_planned_for_wp(p: ProbedSafetyPlan) -> CheckResult:
    wp_ids = {wp.wp_id for wp in p.work_products if wp.wp_id}
    cr_wp_ids = {cr.wp_id for cr in p.confirmation_reviews if cr.wp_id}
    uncovered = wp_ids - cr_wp_ids
    if not uncovered:
        return CheckResult(
            rating="FC",
            finding=f"All {len(wp_ids)} work products have confirmation reviews planned.",
            page_section="06_Confirmation_Reviews",
            confidence="High",
        )
    if len(uncovered) / len(wp_ids) <= 0.2:
        return CheckResult(
            rating="LC",
            finding=f"{len(wp_ids) - len(uncovered)}/{len(wp_ids)} work products have CRs planned.",
            recommended_action=f"Plan confirmation reviews for {len(uncovered)} work products.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(cr_wp_ids)} of {len(wp_ids)} work products have CRs planned.",
        recommended_action="Plan confirmation reviews for all safety-relevant work products per ISO 26262-2:2018 clause 6.4.7.",
        confidence="High",
    )


def spa_09_independence_asil_match(p: ProbedSafetyPlan) -> CheckResult:
    # Check CR independence levels match expected from ASIL
    asil_to_independence = {"D": "I3", "C": "I2", "B": "I1", "A": "I1", "QM": "none"}
    mismatches = []
    for cr in p.confirmation_reviews:
        # Find corresponding WP
        wp = next((w for w in p.work_products if w.wp_id == cr.wp_id), None)
        if wp and wp.target_asil and cr.required_independence:
            expected_ind = asil_to_independence.get(wp.target_asil.upper(), "?")
            if expected_ind != "?" and cr.required_independence != expected_ind:
                mismatches.append(f"WP {cr.wp_id}: ASIL {wp.target_asil} -> expected {expected_ind}, got {cr.required_independence}")

    if not mismatches:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.confirmation_reviews)} confirmation reviews have independence level matching ASIL.",
            page_section="06_Confirmation_Reviews",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"{len(mismatches)} CRs have independence mismatch with ASIL.",
        recommended_action="Align independence levels: ASIL D->I3, C->I2, A/B->I1. " + "; ".join(mismatches[:3]),
        confidence="High",
    )


def spa_10_tools_listed_with_tcl(p: ProbedSafetyPlan) -> CheckResult:
    without_tcl = [t for t in p.tools if not t.tcl]
    if not without_tcl:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.tools)} tools have TCL classification.",
            page_section="07_Tools, TCL column",
            confidence="High",
        )
    if len(p.tools) > 0 and len(without_tcl) / len(p.tools) <= 0.2:
        return CheckResult(
            rating="LC",
            finding=f"{len(p.tools) - len(without_tcl)}/{len(p.tools)} tools have TCL.",
            recommended_action=f"Classify {len(without_tcl)} tools per ISO 26262-8:2018 Clause 11.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.tools) - len(without_tcl)}/{len(p.tools)} tools have TCL classification.",
        recommended_action="Classify all tools with TCL0, TCL1, TCL2, or TCL3 per ISO 26262-8:2018 clause 11.",
        confidence="High",
    )


def spa_11_tool_qualification(p: ProbedSafetyPlan) -> CheckResult:
    tcl2_3_tools = [t for t in p.tools if t.tcl and t.tcl.upper() in ("TCL2", "TCL3")]
    if not tcl2_3_tools:
        return CheckResult(
            rating="FC",
            finding="No TCL2/TCL3 tools found; qualification not required.",
            page_section="07_Tools",
            confidence="High",
        )
    with_qual = [t for t in tcl2_3_tools if t.qualification_status]
    if len(with_qual) == len(tcl2_3_tools):
        return CheckResult(
            rating="FC",
            finding=f"All {len(tcl2_3_tools)} TCL2/TCL3 tools have qualification status documented.",
            page_section="07_Tools, Qualification Status column",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(with_qual)}/{len(tcl2_3_tools)} TCL2/TCL3 tools have qualification documented.",
        recommended_action="Document qualification status for all TCL2/TCL3 tools per ISO 26262-8:2018 clause 12.",
        confidence="High",
    )


def spa_12_anomaly_resolution(p: ProbedSafetyPlan) -> CheckResult:
    if "09_Anomaly_Resolution" in p.sheet_names or any("anomaly" in s.lower() for s in p.sheet_names):
        return draft(
            "Anomaly resolution process documented in a dedicated tab. Reviewer to verify completeness.",
            page_section="09_Anomaly_Resolution or similar",
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated Anomaly Resolution tab found.",
        recommended_action="Add an Anomaly Resolution tab describing detection, reporting, resolution, and closure processes.",
        confidence="Medium",
    )


def spa_13_schedule_milestones(p: ProbedSafetyPlan) -> CheckResult:
    if p.milestones and len(p.milestones) >= 3:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.milestones)} milestones defined in the Safety Plan schedule.",
            page_section="10_Schedule",
            confidence="High",
        )
    if p.milestones:
        return CheckResult(
            rating="LC",
            finding=f"Only {len(p.milestones)} milestones; more definition recommended.",
            recommended_action="Define additional milestones for work-product completions, reviews, and gate decisions.",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No milestones defined in the Schedule tab.",
        recommended_action="Add safety-critical milestones and delivery gates to the project schedule.",
        confidence="High",
    )


def spa_14_iso_references(p: ProbedSafetyPlan) -> CheckResult:
    refs_sheet = next((s for s in p.sheet_names if "reference" in s.lower()), None)
    if refs_sheet:
        return draft(
            f"References documented on sheet '{refs_sheet}'. Reviewer to verify ISO 26262 citations.",
            page_section=f"Sheet '{refs_sheet}'",
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated References tab found.",
        recommended_action="Add a References tab citing ISO 26262-1 through -10, item definition, HARA, and related standards.",
        confidence="Medium",
    )


# ---------------------------------------------------------------------------
# Verification Assessment (all external / pending)
# ---------------------------------------------------------------------------

def _va_external(label: str) -> CheckResult:
    return draft(
        f"{label} is governed by an external Verification Plan / Report — not in the Safety Plan xlsx.",
        action="Verify against the project's Verification Plan and Report documents.",
    )


def va_01_vp_compliance(p): return _va_external("Verification Plan ensuring compliance with Safety Plan")
def va_02_methods(p): return _va_external("Verification methods and tools specified")
def va_03_criteria(p): return _va_external("Pass/fail criteria defined for each verification activity")
def va_04_environment(p): return _va_external("Verification environment (lab, sim, vehicle) specified")
def va_05_anomaly(p): return _va_external("Anomaly handling process for verification deviations")
def va_06_regression(p): return _va_external("Regression testing strategy upon changes")


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
    verify: Callable[[ProbedSafetyPlan], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review
    CheckDef("1",  "CR", "Document Quality", "Is the document structured in a clear manner?", "Shall", cr_01_structured),
    CheckDef("2",  "CR", "Document Quality", "Was the latest template used when the document was created?", "Should", cr_02_template),
    CheckDef("3",  "CR", "Document Quality", "Does the document structure facilitate search for relevant information?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does the title cover the scope of the content?", "Shall", cr_04a_title_scope),
    CheckDef("4b", "CR", "Document Quality", "Are the author and approver(s) listed?", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Document Quality", "Is there a unique identification for each revision?", "Shall", cr_04c_unique_revision),
    CheckDef("4d", "CR", "Document Quality", "Is there a change history available?", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Quality", "Is the status of the work product provided?", "Shall", cr_04e_status),
    CheckDef("5",  "CR", "Document Quality", "Is the current applicable revision clearly identifiable?", "Shall", cr_05_current_revision),
    CheckDef("6",  "CR", "Document Quality", "Is the document under configuration and change management?", "Shall", cr_06_config_mgmt),
    CheckDef("7",  "CR", "Document Quality", "Are the header and footer updated?", "Should", cr_07_header_footer),
    CheckDef("8",  "CR", "Document Quality", "Does this document contain a correct table of contents?", "Shall", cr_08_toc),
    CheckDef("9",  "CR", "Document Quality", "Does the Reference Table list all references in the Work Product?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "Have all sections of the Work Product been completed?", "Should", cr_10_sections_complete),

    # Safety Plan Assessment
    CheckDef("1",  "SPA", "Planning Organization", "Is the Functional Safety Manager assigned and identified?", "Shall", spa_01_fsm_assigned),
    CheckDef("2",  "SPA", "Planning Organization", "Are roles and responsibilities defined for all key positions?", "Shall", spa_02_roles_defined),
    CheckDef("3",  "SPA", "Planning Tailoring", "Are tailoring justifications documented where applicable?", "Shall", spa_03_tailoring_justified),
    CheckDef("4",  "SPA", "Work Products", "Is the list of safety-relevant work products complete?", "Shall", spa_04_work_products_listed),
    CheckDef("5",  "SPA", "Work Products", "Does each work product have an assigned owner?", "Shall", spa_05_wp_owner_assigned),
    CheckDef("6",  "SPA", "Work Products", "Does each work product have a planned completion date?", "Shall", spa_06_wp_planned_date),
    CheckDef("7",  "SPA", "Work Products", "Does each work product have a target ASIL specified?", "Shall", spa_07_wp_asil_specified),
    CheckDef("8",  "SPA", "Confirmation Reviews", "Is confirmation review planned for every safety-relevant work product?", "Shall", spa_08_cr_planned_for_wp),
    CheckDef("9",  "SPA", "Confirmation Reviews", "Does confirmation review independence match required ASIL level?", "Shall", spa_09_independence_asil_match),
    CheckDef("10", "SPA", "Tools and Qualification", "Are all tools listed with TCL classification?", "Shall", spa_10_tools_listed_with_tcl),
    CheckDef("11", "SPA", "Tools and Qualification", "Is qualification status documented for TCL2/TCL3 tools?", "Shall", spa_11_tool_qualification),
    CheckDef("12", "SPA", "Process Definition", "Is the anomaly resolution process described?", "Shall", spa_12_anomaly_resolution),
    CheckDef("13", "SPA", "Schedule", "Are safety-critical schedule milestones defined?", "Shall", spa_13_schedule_milestones),
    CheckDef("14", "SPA", "References", "Are applicable ISO 26262 parts and standards referenced?", "Shall", spa_14_iso_references),

    # Verification Assessment
    CheckDef("1",  "VA", "Verification Planning", "Does the Verification Plan ensure compliance with Safety Plan?", "Shall", va_01_vp_compliance),
    CheckDef("2",  "VA", "Verification Planning", "Are verification methods and tools specified?", "Shall", va_02_methods),
    CheckDef("3",  "VA", "Verification Specification", "Are pass/fail criteria defined for each activity?", "Shall", va_03_criteria),
    CheckDef("4",  "VA", "Verification Specification", "Is the verification environment specified?", "Shall", va_04_environment),
    CheckDef("5",  "VA", "Verification Execution", "Is the anomaly handling process defined?", "Shall", va_05_anomaly),
    CheckDef("6",  "VA", "Verification Execution", "Is a regression testing strategy documented?", "Shall", va_06_regression),
]
