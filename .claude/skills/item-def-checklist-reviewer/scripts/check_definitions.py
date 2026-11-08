"""
Canonical checklist definitions and verification logic for Item Definition.

Each check is a dict with keys:
- id: row id as it appears on the checklist
- tab: which output tab this check belongs to (CR / IDA / VA)
- section: section header text
- requirement: the requirement text
- obligation: "Shall" or "Should" (or "" for sub-rows)
- verify: callable(probed: ProbedItemDef) -> CheckResult
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from item_def_probe import ProbedItemDef


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


# Helper for "draft" results (subjective, low confidence)
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
# Verification functions — Confirmation Review (CR)
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedItemDef) -> CheckResult:
    if len(p.sheet_names) >= 8:
        return CheckResult(
            rating="FC",
            finding=f"Document is structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has only {len(p.sheet_names)} tabs; expected 11 (hara-builder format).",
        recommended_action="Ensure all required tabs are present: Title, Doc Control, Description, Functions, NFR, Boundary, Interfaces, Modes, Allocation, Assumptions, References.",
        confidence="Medium",
    )


def cr_02_template(p: ProbedItemDef) -> CheckResult:
    return draft(
        "Template version cannot be detected from xlsx content alone.",
        action="Confirm the latest Item Definition template was used.",
    )


def cr_03_searchable(p: ProbedItemDef) -> CheckResult:
    if p.sheet_names and len(p.sheet_names) > 5:
        return CheckResult(
            rating="FC",
            finding="Document has structured tabs and search aids; navigation is facilitated.",
            page_section=f"All {len(p.sheet_names)} tabs present",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Some search aids are present but may be incomplete.",
        recommended_action="Add Table of Contents tab and ensure all sections are clearly labeled.",
        confidence="Medium",
    )


def cr_04a_title_scope(p: ProbedItemDef) -> CheckResult:
    if p.title:
        return draft(
            f"Title is: '{p.title}'. Reviewer to confirm it adequately describes the Item.",
            page_section="Title page",
        )
    return CheckResult(
        rating="NO",
        finding="No title detected on the Title page.",
        recommended_action="Add a clear Item title that reflects scope and purpose.",
        confidence="High",
    )


def cr_04b_author_approver(p: ProbedItemDef) -> CheckResult:
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


def cr_04c_unique_revision(p: ProbedItemDef) -> CheckResult:
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
        recommended_action="Populate the Revision field with a unique identifier.",
        confidence="High",
    )


def cr_04d_change_history(p: ProbedItemDef) -> CheckResult:
    return draft(
        "Change history in Document Control tab cannot be verified from xlsx content.",
        action="Verify that Document Control tab contains revision history with dates and changes.",
    )


def cr_04e_status(p: ProbedItemDef) -> CheckResult:
    if p.status:
        return CheckResult(
            rating="FC",
            finding=f"Status='{p.status}' is populated on Title page.",
            page_section="Title page Status field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Status field not populated on Title page.",
        recommended_action="Populate Status field (e.g., Draft, For Review, Released).",
        confidence="High",
    )


def cr_05_current_rev(p: ProbedItemDef) -> CheckResult:
    return draft(
        "Current revision status cannot be verified from content.",
        action="Confirm that the Item Definition reflects the current revision and no newer version exists.",
    )


def cr_06_config_mgmt(p: ProbedItemDef) -> CheckResult:
    return draft(
        "Configuration management status cannot be verified from xlsx.",
        action="Confirm Item Definition is under configuration management (version control, baseline status, change log).",
    )


def cr_07_header_footer(p: ProbedItemDef) -> CheckResult:
    return draft(
        "Header/footer presence cannot be verified from xlsx content.",
        action="Verify that printed version includes header/footer with document ID, revision, date, page numbering.",
    )


def cr_08_toc(p: ProbedItemDef) -> CheckResult:
    return draft(
        "Table of Contents cannot be verified from xlsx.",
        action="Confirm a Table of Contents tab or section lists all major sections with tab references.",
    )


def cr_09_references(p: ProbedItemDef) -> CheckResult:
    if p.references and len(p.references) > 0:
        return CheckResult(
            rating="FC",
            finding=f"References tab contains {len(p.references)} reference(s).",
            page_section="10_References tab",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No references detected in the document.",
        recommended_action="Add a References tab citing applicable standards (ISO 26262, vehicle specs, safety plan).",
        confidence="High",
    )


def cr_10_sections_complete(p: ProbedItemDef) -> CheckResult:
    tabs_required = [
        "Title", "Doc Control", "Description", "Functions", "NFR",
        "Boundary", "Interfaces", "Modes", "Allocation", "Assumptions", "References"
    ]
    if len(p.sheet_names) >= 11:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sheet_names)} standard tabs are present.",
            page_section="All tabs",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.sheet_names)} tabs present; expected 11.",
        recommended_action="Ensure all required sections are present.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Verification functions — Item Definition Assessment (IDA)
# ---------------------------------------------------------------------------

def ida_01_scope_clear(p: ProbedItemDef) -> CheckResult:
    if p.scope and p.distinguishing_notes:
        return CheckResult(
            rating="FC",
            finding=f"Item scope is documented: '{p.scope}'. Distinguishing notes: '{p.distinguishing_notes}'.",
            page_section="02_Item_Description tab",
            confidence="High",
        )
    if p.scope:
        return CheckResult(
            rating="LC",
            finding=f"Item scope is documented but distinguishing notes may be incomplete.",
            page_section="02_Item_Description tab",
            recommended_action="Add distinguishing notes to clearly separate this Item from related Items.",
            confidence="Medium",
        )
    return CheckResult(
        rating="NO",
        finding="Item scope is not clearly documented.",
        recommended_action="Document the Item scope and boundaries in 02_Item_Description tab.",
        confidence="High",
    )


def ida_02_functions_enumerated(p: ProbedItemDef) -> CheckResult:
    if len(p.functions) > 0:
        non_empty = [f for f in p.functions if f.name and f.description]
        if len(non_empty) == len(p.functions):
            return CheckResult(
                rating="FC",
                finding=f"All {len(p.functions)} function(s) enumerated with descriptions.",
                page_section="03_Functions tab",
                confidence="High",
            )
        return CheckResult(
            rating="LC",
            finding=f"{len(non_empty)}/{len(p.functions)} functions have descriptions.",
            recommended_action="Complete descriptions for all functions.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No functions enumerated.",
        recommended_action="Document all Item functions in 03_Functions tab (ID, Name, Description).",
        confidence="High",
    )


def ida_03_nfr_captured(p: ProbedItemDef) -> CheckResult:
    if len(p.non_functional_requirements) > 0:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.non_functional_requirements)} non-functional requirement(s) captured.",
            page_section="04_Non_Functional_Requirements tab",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="No non-functional requirements captured.",
        recommended_action="Document non-functional requirements (performance, reliability, usability) in 04_NFR tab if applicable.",
        confidence="Medium",
    )


def ida_04_interfaces_specified(p: ProbedItemDef) -> CheckResult:
    if len(p.external_interfaces) > 0:
        with_direction = [i for i in p.external_interfaces if i.direction]
        with_counterpart = [i for i in p.external_interfaces if i.counterpart]
        if len(with_direction) == len(p.external_interfaces) and len(with_counterpart) == len(p.external_interfaces):
            return CheckResult(
                rating="FC",
                finding=f"All {len(p.external_interfaces)} external interfaces have direction and counterpart specified.",
                page_section="06_External_Interfaces tab",
                confidence="High",
            )
        return CheckResult(
            rating="LC",
            finding=f"{len(p.external_interfaces)} interface(s) present; {len(with_direction)} have direction, {len(with_counterpart)} have counterpart.",
            recommended_action="Ensure all interfaces specify direction (In/Out/BiDir) and counterpart system.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No external interfaces specified.",
        recommended_action="Document external interfaces in 06_External_Interfaces tab (ID, Interface, Counterpart, Direction, Data, Integrity).",
        confidence="High",
    )


def ida_05_modes_enumerated(p: ProbedItemDef) -> CheckResult:
    if len(p.operating_modes) > 0:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.operating_modes)} operating mode(s) enumerated.",
            page_section="07_Operating_Modes tab",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="No operating modes enumerated.",
        recommended_action="Document operating modes (normal, degraded, fault) in 07_Operating_Modes tab if applicable to Item.",
        confidence="Medium",
    )


def ida_06_allocation_specified(p: ProbedItemDef) -> CheckResult:
    if len(p.allocations) > 0 and len(p.functions) > 0:
        if len(p.allocations) >= len(p.functions):
            populated = [a for a in p.allocations if a.hw or a.sw or a.mech]
            if len(populated) == len(p.functions):
                return CheckResult(
                    rating="FC",
                    finding=f"All {len(p.functions)} function(s) have HW/SW/Mech allocation specified.",
                    page_section="08_Allocation_HW_SW_Mech tab",
                    confidence="High",
                )
            return CheckResult(
                rating="LC",
                finding=f"{len(populated)}/{len(p.functions)} allocations specified.",
                recommended_action="Complete HW/SW/Mech allocation for all functions.",
                confidence="High",
            )
    return CheckResult(
        rating="PC",
        finding="Allocation of functions to HW/SW/Mech not fully documented.",
        recommended_action="Document allocation in 08_Allocation_HW_SW_Mech tab for each function.",
        confidence="High",
    )


def ida_07_assumptions_documented(p: ProbedItemDef) -> CheckResult:
    if len(p.assumptions) > 0:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.assumptions)} assumption(s) documented (vehicle, driver, market, lifecycle).",
            page_section="09_Initial_Assumptions tab",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="No initial assumptions documented.",
        recommended_action="Document assumptions about vehicle context, driver, market, and lifecycle in 09_Initial_Assumptions tab.",
        confidence="High",
    )


def ida_08_distinguishable(p: ProbedItemDef) -> CheckResult:
    if p.distinguishing_notes:
        return CheckResult(
            rating="FC",
            finding=f"Item has distinguishing notes: '{p.distinguishing_notes}'.",
            page_section="02_Item_Description tab",
            confidence="High",
        )
    return CheckResult(
        rating="LC",
        finding="Distinguishing notes not populated; Item identity vs. neighbors may be unclear.",
        recommended_action="Add notes in 02_Item_Description that clarify how this Item differs from related Items.",
        confidence="High",
    )


def ida_09_standards_referenced(p: ProbedItemDef) -> CheckResult:
    if p.references and len(p.references) > 0:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.references)} reference(s) documented; standards are cited.",
            page_section="10_References tab",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No references to applicable standards present.",
        recommended_action="Add references to ISO 26262, vehicle specifications, and relevant standards in 10_References tab.",
        confidence="High",
    )


def ida_10_hara_ready(p: ProbedItemDef) -> CheckResult:
    # HARA readiness: has functions, boundary, assumptions
    ready_checks = [
        len(p.functions) > 0,
        len(p.boundary_in_items) > 0 or len(p.boundary_out_items) > 0,
        len(p.assumptions) > 0,
    ]
    if all(ready_checks):
        return CheckResult(
            rating="FC",
            finding="Item Definition is suitable input for HARA (functions present, boundary defined, assumptions documented).",
            page_section="03_Functions, 05_Boundary_Diagram, 09_Initial_Assumptions tabs",
            confidence="High",
        )
    missing = []
    if len(p.functions) == 0: missing.append("Functions")
    if len(p.boundary_in_items) == 0 and len(p.boundary_out_items) == 0: missing.append("Boundary")
    if len(p.assumptions) == 0: missing.append("Assumptions")
    return CheckResult(
        rating="PC",
        finding=f"Item Definition incomplete for HARA input. Missing: {', '.join(missing)}.",
        recommended_action="Complete the missing sections to enable HARA analysis.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Verification functions — Verification Assessment (VA)
# ---------------------------------------------------------------------------

def va_01_req_traceability(p: ProbedItemDef) -> CheckResult:
    return draft(
        "Requirement traceability matrix cannot be verified from Item Definition alone.",
        page_section="External: Design Specification / Test Plan",
        action="Confirm traceability matrix links each Item function to design requirements and test cases.",
    )


def va_02_design_adequacy(p: ProbedItemDef) -> CheckResult:
    return draft(
        "Design adequacy verification requires external design documents.",
        page_section="External: Design Specification",
        action="Reviewer to confirm design addresses all Item functions and non-functional requirements.",
    )


def va_03_test_coverage(p: ProbedItemDef) -> CheckResult:
    return draft(
        "Test coverage cannot be verified from Item Definition.",
        page_section="External: Test Plan / Test Report",
        action="Confirm test plan provides adequate coverage for all Item functions and edge cases.",
    )


# ---------------------------------------------------------------------------
# Check registry
# ---------------------------------------------------------------------------

class CheckDef:
    def __init__(self, id_: str, tab: str, section: str, requirement: str, obligation: str, verify: Callable):
        self.id = id_
        self.tab = tab
        self.section = section
        self.requirement = requirement
        self.obligation = obligation
        self.verify = verify


CHECKS = [
    # Confirmation Review (CR)
    CheckDef("1", "CR", "Document Structure", "Document is organized into distinct tabs covering Title, Doc Control, Description, Functions, NFR, Boundary, Interfaces, Modes, Allocation, Assumptions, and References.", "Shall", cr_01_structured),
    CheckDef("2", "CR", "Template Compliance", "Item Definition is based on the latest applicable template version.", "Should", cr_02_template),
    CheckDef("3", "CR", "Search Aids", "Document includes search aids (Table of Contents, References) for navigation.", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Title and Scope", "Item title clearly describes the Item and its scope.", "Shall", cr_04a_title_scope),
    CheckDef("4b", "CR", "Author and Approver", "Author and Approver are identified on the Title page.", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Revision Identification", "Revision is uniquely identified and tracked.", "Shall", cr_04c_unique_revision),
    CheckDef("4d", "CR", "Change History", "Change history is documented in the Document Control tab.", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Status", "Status (Draft, Released, etc.) is identified.", "Shall", cr_04e_status),
    CheckDef("5", "CR", "Current Revision", "The Item Definition reflects the current revision.", "Shall", cr_05_current_rev),
    CheckDef("6", "CR", "Configuration Management", "Item Definition is under configuration management.", "Shall", cr_06_config_mgmt),
    CheckDef("7", "CR", "Header and Footer", "Header and footer include document ID, revision, and page numbering.", "Should", cr_07_header_footer),
    CheckDef("8", "CR", "Table of Contents", "A Table of Contents is present for navigation.", "Should", cr_08_toc),
    CheckDef("9", "CR", "References", "Applicable standards and references are cited.", "Shall", cr_09_references),
    CheckDef("10", "CR", "Sections Complete", "All required sections are documented.", "Shall", cr_10_sections_complete),

    # Item Definition Assessment (IDA)
    CheckDef("1", "IDA", "Item Scope and Boundary", "Item scope is clearly described with distinguishing notes.", "Shall", ida_01_scope_clear),
    CheckDef("2", "IDA", "Item Scope and Boundary", "Functions are enumerated with sufficient detail (ID, Name, Description).", "Shall", ida_02_functions_enumerated),
    CheckDef("3", "IDA", "Requirements Specification", "Non-functional requirements are captured.", "Should", ida_03_nfr_captured),
    CheckDef("4", "IDA", "External Interfaces", "External interfaces are specified with direction and counterpart system.", "Shall", ida_04_interfaces_specified),
    CheckDef("5", "IDA", "Operating Modes", "Operating modes are enumerated (normal, degraded, fault).", "Should", ida_05_modes_enumerated),
    CheckDef("6", "IDA", "Function Allocation", "Functions are allocated to HW, SW, or mechanical implementations.", "Should", ida_06_allocation_specified),
    CheckDef("7", "IDA", "Initial Assumptions", "Initial assumptions are documented (vehicle, driver, market, lifecycle).", "Shall", ida_07_assumptions_documented),
    CheckDef("8", "IDA", "Item Scope and Boundary", "Item is distinguishable from related items via distinguishing notes.", "Shall", ida_08_distinguishable),
    CheckDef("9", "IDA", "Standards Compliance", "References to applicable ISO 26262 and vehicle standards are present.", "Shall", ida_09_standards_referenced),
    CheckDef("10", "IDA", "HARA Readiness", "Item Definition is suitable input for HARA (functions, boundary, assumptions present).", "Shall", ida_10_hara_ready),

    # Verification Assessment (VA)
    CheckDef("1", "VA", "Verification Planning", "Requirement traceability matrix links Item functions to design and test.", "Shall", va_01_req_traceability),
    CheckDef("2", "VA", "Verification Planning", "Design specification adequately addresses all Item functions.", "Shall", va_02_design_adequacy),
    CheckDef("3", "VA", "Verification Planning", "Test plan provides adequate coverage for Item functions and edge cases.", "Shall", va_03_test_coverage),
]
