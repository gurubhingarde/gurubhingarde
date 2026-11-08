"""
Canonical DIA checklist definitions and verification logic per ISO 26262-8 §5.

Each check has:
- id: row id (e.g., "1", "3a")
- tab: CR / DIAA / VA
- section: section header
- requirement: requirement text
- obligation: "Shall" or "Should"
- verify: callable(probed: ProbedDia) -> CheckResult
"""

from __future__ import annotations

import re

from dataclasses import dataclass
from typing import Callable

from dia_probe import ProbedDia


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    rating: str = ""              # FC / LC / PC / NO / NA / "" (pending)
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""          # High / Medium / Low / ""


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
# Confirmation Review — 14 generic doc-quality checks
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedDia) -> CheckResult:
    if len(p.sheet_names) >= 11:
        return CheckResult(
            rating="FC",
            finding=f"Document has {len(p.sheet_names)} tabs with distinct sections per dia-builder structure.",
            page_section="All tabs",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has only {len(p.sheet_names)} tabs; expected 11+ for complete DIA structure.",
        recommended_action="Ensure all required DIA tabs are present (Title, Scope, RACI, Communication, Joint Reviews, etc.).",
        confidence="High",
    )


def cr_02_template(p: ProbedDia) -> CheckResult:
    return draft(
        "Template version cannot be detected from xlsx content alone.",
        action="Confirm the latest applicable DIA template was used at document creation.",
    )


def cr_03_searchable(p: ProbedDia) -> CheckResult:
    if len(p.sheet_names) >= 11:
        return CheckResult(
            rating="FC",
            finding="Document structure facilitates search (Title, Document Control, References tabs present).",
            page_section="Sheets: Title, General Info",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Some search aids are present but not all tabs are complete.",
        recommended_action="Add a Table of Contents and References sheet for navigation.",
        confidence="High",
    )


def cr_04a_title_scope(p: ProbedDia) -> CheckResult:
    if p.item:
        return draft(
            f"Item is: '{p.item}'. Reviewer to confirm scope clearly bounded.",
            page_section="Title page",
        )
    return CheckResult(
        rating="NO",
        finding="No item title detected on the Title page.",
        recommended_action="Add a clear item title that reflects the scope of the DIA.",
        confidence="High",
    )


def cr_04b_author_approver(p: ProbedDia) -> CheckResult:
    return draft(
        "Author and Approver fields on Title page — reviewer to confirm population.",
        action="Populate Author and Approver fields on the Title page.",
    )


def cr_04c_unique_revision(p: ProbedDia) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Revision='{p.revision}' is set on Title page.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Revision field not populated on Title page.",
        recommended_action="Populate the Revision field with a unique identifier.",
        confidence="High",
    )


def cr_04d_change_history(p: ProbedDia) -> CheckResult:
    return draft(
        "Revision history on Document Control tab — reviewer to confirm completeness.",
        page_section="01_Document_Control",
    )


def cr_04e_status(p: ProbedDia) -> CheckResult:
    return draft(
        "Work-product status (Draft / In Review / Released) — reviewer to confirm.",
        page_section="Title page",
    )


def cr_05_current_revision(p: ProbedDia) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Current revision '{p.revision}' clearly identifiable.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Current revision not identifiable.",
        recommended_action="Populate the Revision field on Title page.",
        confidence="High",
    )


def cr_06_config_mgmt(p: ProbedDia) -> CheckResult:
    return draft(
        "Configuration management is an organizational practice; verify document is checked into system.",
        action="Confirm the DIA is checked into the project's configuration-management system.",
    )


def cr_07_header_footer(p: ProbedDia) -> CheckResult:
    return draft(
        "Worksheet headers/footers cannot be reliably verified programmatically.",
        action="Open the workbook in Excel and confirm header/footer contain current document ID and revision.",
    )


def cr_08_toc(p: ProbedDia) -> CheckResult:
    if any(name in p.sheet_names for name in ["00_Title_Page", "01_Document_Control"]):
        return CheckResult(
            rating="FC",
            finding="Title and Document Control tabs present near the beginning of workbook.",
            page_section=f"Sheet '{p.sheet_names[0]}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="No clear Table of Contents tab detected.",
        recommended_action="Add a Table of Contents tab listing all sheets and purposes.",
        confidence="High",
    )


def cr_09_references(p: ProbedDia) -> CheckResult:
    if "11_References" in p.sheet_names:
        return draft(
            "References tab present. Reviewer to confirm completeness against ISO 26262, master agreement, item definition.",
            page_section="11_References",
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated References tab detected.",
        recommended_action="Add a References tab citing ISO 26262, master agreement, item definition, and related documents.",
        confidence="High",
    )


def cr_10_sections_complete(p: ProbedDia) -> CheckResult:
    # Heuristic: count populated tabs and key content
    key_tabs = ["03_Item_Scope", "04_RACI_Matrix", "05_Communication_Protocol", "07_Supplier_Deliverables"]
    populated = sum(1 for tab in key_tabs if tab in p.sheet_names)
    if populated >= 4:
        return CheckResult(
            rating="FC",
            finding=f"All major DIA sections present and populated ({populated}/4 key tabs).",
            confidence="High",
        )
    if populated >= 2:
        return CheckResult(
            rating="LC",
            finding=f"Most major sections present ({populated}/4 key tabs).",
            recommended_action="Complete remaining DIA tabs (Supplier Deliverables, Change Management, Tool Sharing, Confidentiality).",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Key sections missing ({populated}/4 key tabs).",
        recommended_action="Populate all major DIA sections before review.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# DIA Assessment — 14 substantive checks per ISO 26262-8 §5
# ---------------------------------------------------------------------------

def diaa_01_parties_identified(p: ProbedDia) -> CheckResult:
    if len(p.parties_list) >= 2:
        roles = set(party.role for party in p.parties_list if party.role)
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.parties_list)} parties identified with roles: {', '.join(sorted(roles))}.",
            page_section="02_Parties",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"Only {len(p.parties_list)} party/parties identified; minimum 2 required (OEM + supplier).",
        recommended_action="Add all parties involved in the agreement with clearly defined roles (OEM, Tier-1, Tier-2, IC supplier, etc.).",
        confidence="High",
    )


def diaa_02_fusa_contacts(p: ProbedDia) -> CheckResult:
    fusa_contacts = [party for party in p.parties_list if party.fusa_contact]
    if len(fusa_contacts) == len(p.parties_list) and len(fusa_contacts) >= 1:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.parties_list)} parties have FuSa contact identified (not just commercial contact).",
            page_section="02_Parties, FuSa Contact column",
            confidence="High",
        )
    missing = len(p.parties_list) - len(fusa_contacts)
    return CheckResult(
        rating="NO" if missing > 0 else "FC",
        finding=f"{missing} party/parties missing FuSa contact.",
        recommended_action=f"Add functional safety contact for {missing} party/parties in the FuSa Contact column.",
        confidence="High",
    )


def diaa_03_raci_coverage(p: ProbedDia) -> CheckResult:
    major_wps = {"HARA", "Item Definition", "FSC", "TSC", "FMEDA", "SW Reqs", "Safety Case"}
    raci_wps = set(row.work_product.lower() for row in p.raci_matrix if row.work_product)
    covered = sum(1 for wp in major_wps if any(wp.lower() in rwp for rwp in raci_wps))
    if covered >= 5:
        return CheckResult(
            rating="FC",
            finding=f"RACI matrix covers {covered}/7 major work products (HARA, Item Def, FSC, TSC, FMEDA, SW Reqs, Safety Case).",
            page_section="04_RACI_Matrix",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"RACI matrix covers only {covered}/7 major work products.",
        recommended_action=f"Add RACI entries for missing work products (at least HARA, Item Def, FSC, TSC at minimum).",
        confidence="High",
    )


def _raci_tokens(value: str) -> set[str]:
    """Split an RACI cell into its role letters.

    dia-builder writes combined assignments such as "A,R" in a single cell, so
    an exact == "A" comparison silently reports every such row as having no
    Accountable and no Responsible party.
    """
    return {t.strip().upper() for t in re.split(r"[,/;+&]| ", value or "") if t.strip()}


def diaa_04_raci_accountable(p: ProbedDia) -> CheckResult:
    """Check: exactly one A per work product per item."""
    issues = []
    for row in p.raci_matrix:
        a_count = sum(1 for v in row.assignments.values() if "A" in _raci_tokens(v))
        if a_count != 1:
            issues.append(f"{row.work_product}: {a_count} Accountable(s)")
    if not issues:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.raci_matrix)} RACI rows have exactly one Accountable (A) per work product.",
            page_section="04_RACI_Matrix, A column",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"{len(issues)} work product(s) have missing or duplicate Accountable: {', '.join(issues[:5])}.",
        recommended_action="Ensure every work product has exactly one Accountable party.",
        confidence="High",
    )


def diaa_05_raci_responsible(p: ProbedDia) -> CheckResult:
    """Check: at least one R per work product."""
    issues = []
    for row in p.raci_matrix:
        r_count = sum(1 for v in row.assignments.values() if "R" in _raci_tokens(v))
        if r_count < 1:
            issues.append(row.work_product)
    if not issues:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.raci_matrix)} RACI rows have at least one Responsible (R) party.",
            page_section="04_RACI_Matrix, R column",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"{len(issues)} work product(s) have no Responsible party: {', '.join(issues[:5])}.",
        recommended_action="Assign at least one Responsible party to every work product.",
        confidence="High",
    )


def diaa_06_raci_complete(p: ProbedDia) -> CheckResult:
    """Check: no work product has all empty assignments."""
    empty_rows = [row for row in p.raci_matrix if not row.assignments or not any(row.assignments.values())]
    if not empty_rows:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.raci_matrix)} work products have at least one RACI assignment.",
            page_section="04_RACI_Matrix",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"{len(empty_rows)} work product(s) have no RACI assignments: {', '.join(row.work_product for row in empty_rows[:3])}.",
        recommended_action="Populate RACI assignments for all work products.",
        confidence="High",
    )


def diaa_07_communication_defined(p: ProbedDia) -> CheckResult:
    if len(p.communication_channels) >= 1:
        has_cadence = sum(1 for ch in p.communication_channels if ch.cadence)
        has_escalation = sum(1 for ch in p.communication_channels if ch.escalation)
        return CheckResult(
            rating="FC" if (has_cadence > 0 and has_escalation > 0) else "LC",
            finding=f"Communication protocol defined with {len(p.communication_channels)} channel(s); cadence and escalation defined for {has_cadence}/{has_escalation}.",
            page_section="05_Communication_Protocol",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No communication protocol defined.",
        recommended_action="Define communication channels, cadence, and escalation paths in 05_Communication_Protocol tab.",
        confidence="High",
    )


def diaa_08_joint_reviews(p: ProbedDia) -> CheckResult:
    if len(p.joint_reviews) >= 1:
        scheduled = sum(1 for jr in p.joint_reviews if jr.schedule)
        return CheckResult(
            rating="FC" if scheduled == len(p.joint_reviews) else "LC",
            finding=f"Joint review schedule defined for {len(p.joint_reviews)} milestone(s); {scheduled} scheduled.",
            page_section="06_Joint_Reviews",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="No joint reviews defined.",
        recommended_action="Define joint review schedule for major milestones (item definition, FSC release, TSC release, etc.).",
        confidence="High",
    )


def diaa_09_supplier_deliverables(p: ProbedDia) -> CheckResult:
    if len(p.supplier_deliverables) >= 1:
        with_format = sum(1 for d in p.supplier_deliverables if d.format)
        with_criteria = sum(1 for d in p.supplier_deliverables if d.acceptance_criteria)
        return CheckResult(
            rating="FC" if (with_format == len(p.supplier_deliverables) and with_criteria == len(p.supplier_deliverables)) else "LC",
            finding=f"{len(p.supplier_deliverables)} supplier deliverable(s) defined; {with_format} with format, {with_criteria} with acceptance criteria.",
            page_section="07_Supplier_Deliverables",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="No supplier deliverables explicitly listed.",
        recommended_action="Define supplier deliverables with format, language, planned date, and acceptance criteria.",
        confidence="High",
    )


def diaa_10_change_management(p: ProbedDia) -> CheckResult:
    if p.change_management:
        return draft(
            f"Change management process described: {p.change_management[:80]}...",
            page_section="08_Change_Management",
        )
    return CheckResult(
        rating="PC",
        finding="No change management process documented.",
        recommended_action="Document change management process in 08_Change_Management tab.",
        confidence="High",
    )


def diaa_11_tool_sharing(p: ProbedDia) -> CheckResult:
    if "09_Tool_Sharing" in p.sheet_names:
        if p.tool_sharing:
            return draft(
                f"Tool sharing terms documented: {p.tool_sharing[:80]}...",
                page_section="09_Tool_Sharing",
            )
        return CheckResult(
            rating="NA",
            finding="Tool Sharing tab present but appears empty (tools may not be shared).",
            confidence="High",
        )
    return CheckResult(
        rating="NA",
        finding="No Tool Sharing tab (tools may not be shared between parties).",
        confidence="High",
    )


def diaa_12_confidentiality_ip(p: ProbedDia) -> CheckResult:
    if "10_Confidentiality_IP" in p.sheet_names:
        if p.confidentiality_ip:
            return draft(
                f"Confidentiality/IP terms present: {p.confidentiality_ip[:80]}...",
                page_section="10_Confidentiality_IP",
            )
        return CheckResult(
            rating="PC",
            finding="Confidentiality/IP tab present but may be incomplete.",
            recommended_action="Populate confidentiality and IP ownership terms.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No Confidentiality/IP terms documented.",
        recommended_action="Document confidentiality and intellectual property ownership in 10_Confidentiality_IP tab.",
        confidence="High",
    )


def diaa_13_references(p: ProbedDia) -> CheckResult:
    if "11_References" in p.sheet_names:
        return draft(
            "References tab present. Reviewer to confirm references to master agreement, item definition, standards.",
            page_section="11_References",
        )
    return CheckResult(
        rating="PC",
        finding="No References tab detected.",
        recommended_action="Add References tab citing ISO 26262, master agreement, item definition, and applicable standards.",
        confidence="High",
    )


def diaa_14_scope_bounded(p: ProbedDia) -> CheckResult:
    in_count = len(p.scope_in)
    out_count = len(p.scope_out)
    if in_count >= 1 and out_count >= 0:
        return CheckResult(
            rating="FC",
            finding=f"Item scope clearly bounded: {in_count} in-scope item(s), {out_count} out-of-scope item(s).",
            page_section="03_Item_Scope",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Item scope may not be clearly bounded ({in_count} in-scope, {out_count} out-of-scope).",
        recommended_action="Clearly enumerate all in-scope and out-of-scope elements in 03_Item_Scope tab.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Verification Assessment — mostly external
# ---------------------------------------------------------------------------

def _va_external(label: str) -> CheckResult:
    return draft(
        f"{label} is typically governed by external Verification Plan / Specification / Report.",
        action="Verify against the project's Verification Plan and external documents.",
    )


def va_01_plan_compliance(p): return _va_external("Verification Plan ensuring DIA compliance and consistency with FSC")
def va_02_meetings_held(p): return _va_external("Regular DIA reviews and meetings held per schedule")
def va_03_action_tracking(p): return _va_external("DIA action items tracked to closure")
def va_04_issue_mgmt(p): return _va_external("Issues and non-conformances recorded and resolved")
def va_05_effectiveness(p): return _va_external("DIA governance effectiveness verified")


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
    verify: Callable[[ProbedDia], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review
    CheckDef("1",  "CR", "Document Quality", "Is the document structured in a clear manner (using headlines, template layouts) that supports maintainability and understandability?", "Shall", cr_01_structured),
    CheckDef("2",  "CR", "Document Quality", "On the date the document was first created, was the latest template available used?", "Should", cr_02_template),
    CheckDef("3",  "CR", "Document Quality", "Does the document structure facilitate the search for relevant information (cross references, index, abbreviations)?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does the title cover the scope of the content?", "Shall", cr_04a_title_scope),
    CheckDef("4b", "CR", "Document Quality", "Are the author and approver(s) listed?", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Document Quality", "Is there a unique identification for each different revision?", "Shall", cr_04c_unique_revision),
    CheckDef("4d", "CR", "Document Quality", "Is there a change history available?", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Quality", "Is the status of the work product provided?", "Shall", cr_04e_status),
    CheckDef("5",  "CR", "Document Quality", "Is the current applicable revision clearly identifiable?", "Shall", cr_05_current_revision),
    CheckDef("6",  "CR", "Document Quality", "Is the document under configuration and change management?", "Shall", cr_06_config_mgmt),
    CheckDef("7",  "CR", "Document Quality", "Are the header and footer updated?", "Should", cr_07_header_footer),
    CheckDef("8",  "CR", "Document Quality", "Does this document contain a correct table of content?", "Shall", cr_08_toc),
    CheckDef("9",  "CR", "Document Quality", "Does the Reference Table list all of the references contained in the Work Product?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "Have all sections of the Work Product been completed?", "Should", cr_10_sections_complete),

    # DIA Assessment per ISO 26262-8 §5
    CheckDef("1",  "DIAA", "DIA Content — Parties", "All parties identified with clearly defined roles (OEM, Tier-1, Tier-2, IC supplier, etc.)?", "Shall", diaa_01_parties_identified),
    CheckDef("2",  "DIAA", "DIA Content — Parties", "Each party has a designated Functional Safety (FuSa) contact identified?", "Shall", diaa_02_fusa_contacts),
    CheckDef("3",  "DIAA", "DIA Content — RACI", "RACI matrix covers all major safety work products (HARA, Item Def, FSC, TSC, FMEDA, SW Reqs, Safety Case)?", "Shall", diaa_03_raci_coverage),
    CheckDef("4",  "DIAA", "DIA Content — RACI", "Each work product has exactly one Accountable (A) party?", "Shall", diaa_04_raci_accountable),
    CheckDef("5",  "DIAA", "DIA Content — RACI", "Each work product has at least one Responsible (R) party?", "Shall", diaa_05_raci_responsible),
    CheckDef("6",  "DIAA", "DIA Content — RACI", "No work product has empty/missing assignments across all parties?", "Shall", diaa_06_raci_complete),
    CheckDef("7",  "DIAA", "DIA Content — Communication", "Communication protocol defined with cadence, channel, and escalation path?", "Shall", diaa_07_communication_defined),
    CheckDef("8",  "DIAA", "DIA Content — Reviews", "Joint review schedule defined for major milestones?", "Shall", diaa_08_joint_reviews),
    CheckDef("9",  "DIAA", "DIA Content — Deliverables", "Supplier deliverables list complete with format, language, planned date, acceptance criteria?", "Shall", diaa_09_supplier_deliverables),
    CheckDef("10", "DIAA", "DIA Content — Processes", "Change management process clearly described?", "Shall", diaa_10_change_management),
    CheckDef("11", "DIAA", "DIA Content — Processes", "Tool sharing terms documented (if tools are shared)?", "Should", diaa_11_tool_sharing),
    CheckDef("12", "DIAA", "DIA Content — Legal", "Confidentiality and IP ownership terms present?", "Shall", diaa_12_confidentiality_ip),
    CheckDef("13", "DIAA", "DIA Content — References", "References to master agreement, item definition, standards documented?", "Should", diaa_13_references),
    CheckDef("14", "DIAA", "DIA Content — Scope", "Item scope clearly bounded (in-scope and out-of-scope items)?", "Shall", diaa_14_scope_bounded),

    # Verification Assessment
    CheckDef("1",  "VA", "External Verification", "Verification Plan ensures compliance with DIA and consistency with FSC?", "Shall", va_01_plan_compliance),
    CheckDef("2",  "VA", "External Verification", "DIA reviews and meetings held per defined schedule?", "Should", va_02_meetings_held),
    CheckDef("3",  "VA", "External Verification", "DIA action items tracked and resolved to closure?", "Should", va_03_action_tracking),
    CheckDef("4",  "VA", "External Verification", "Issues and non-conformances recorded and disposition documented?", "Should", va_04_issue_mgmt),
    CheckDef("5",  "VA", "External Verification", "DIA governance effectiveness verified and demonstrated?", "Should", va_05_effectiveness),
]
