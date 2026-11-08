"""
CS Goals checklist definitions per ISO/SAE 21434 Section 16.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from cs_goals_probe import ProbedCSGoals


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding: str, page_section: str = "", action: str = "(Reviewer to verify)") -> CheckResult:
    return CheckResult(
        rating="",
        finding="(Auto-suggest, requires reviewer judgment) " + finding,
        page_section=page_section,
        recommended_action=action,
        confidence="Low",
    )


def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, page_section="", recommended_action="", confidence="High")


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedCSGoals], CheckResult]


# -------------------------------------------------------------------------
# Confirmation Review (14 checks)
# -------------------------------------------------------------------------

def cr_01_structured(p: ProbedCSGoals) -> CheckResult:
    if len(p.sheet_names) >= 6:
        return CheckResult(
            rating="FC",
            finding=f"Document has {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has only {len(p.sheet_names)} tabs.",
        recommended_action="Ensure all 7 CS Goals tabs are present.",
        confidence="Medium",
    )


def cr_02_title(p: ProbedCSGoals) -> CheckResult:
    if p.title:
        return draft(f"Title: '{p.title}'. Reviewer to confirm scope.", page_section="Title page")
    return CheckResult(
        rating="NO",
        finding="No title detected.",
        recommended_action="Add document title on Title page.",
        confidence="High",
    )


def cr_03_author_approver(p: ProbedCSGoals) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(
            rating="FC",
            finding=f"Author='{p.author}', Approver='{p.approver}'.",
            page_section="Title page",
            confidence="High",
        )
    missing = [x for x in ["Author", "Approver"] if (x == "Author" and not p.author) or (x == "Approver" and not p.approver)]
    return CheckResult(
        rating="NO",
        finding=f"Missing: {', '.join(missing)}.",
        recommended_action=f"Populate {', '.join(missing)} on Title page.",
        confidence="High",
    )


def cr_04_revision(p: ProbedCSGoals) -> CheckResult:
    if p.revision and p.revision_history_rows >= 1:
        return CheckResult(
            rating="FC",
            finding=f"Revision='{p.revision}'; {p.revision_history_rows} history row(s).",
            page_section="Title page + Document Control tab",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Revision not populated or no history.",
        recommended_action="Populate Revision and add history to Document Control.",
        confidence="High",
    )


def cr_05_status(p: ProbedCSGoals) -> CheckResult:
    if p.status:
        return CheckResult(
            rating="FC",
            finding=f"Status='{p.status}'.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Status field not populated.",
        recommended_action="Add Status (Draft/In Review/Released) to Title page.",
        confidence="High",
    )


def cr_06_project(p: ProbedCSGoals) -> CheckResult:
    if p.project:
        return CheckResult(
            rating="FC",
            finding=f"Project='{p.project}'.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Project field not populated.",
        recommended_action="Add Project name to Title page.",
        confidence="High",
    )


def cr_07_references(p: ProbedCSGoals) -> CheckResult:
    refs_sheet = any("reference" in s.lower() for s in p.sheet_names)
    if refs_sheet:
        return CheckResult(
            rating="FC",
            finding="References tab found.",
            page_section="References tab",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No References tab detected.",
        recommended_action="Add References tab citing ISO/SAE 21434 and TARA.",
        confidence="Medium",
    )


def cr_08_toc(p: ProbedCSGoals) -> CheckResult:
    if p.has_table_of_contents:
        return CheckResult(
            rating="FC",
            finding="TOC or General Info tab present.",
            page_section=f"Sheet '{p.sheet_names[0]}'",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No TOC detected.",
        recommended_action="Add Table of Contents tab.",
        confidence="Medium",
    )


def cr_09_tara_reference(p: ProbedCSGoals) -> CheckResult:
    tara_sheet = any("tara" in s.lower() for s in p.sheet_names)
    if tara_sheet and p.n_tara_echo > 0:
        return CheckResult(
            rating="FC",
            finding=f"TARA Echo tab present with {p.n_tara_echo} threat row(s).",
            page_section="TARA Echo tab",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="TARA import or echo not fully captured.",
        recommended_action="Ensure TARA threats are imported/echoed in TARA Echo tab.",
        confidence="High",
    )


def cr_10_complete_sections(p: ProbedCSGoals) -> CheckResult:
    critical = ["03_cybersecurity", "04_cal", "05_asset", "06_concept"]
    found = sum(1 for s in p.sheet_names if any(cs in s for cs in critical))
    if found >= 3:
        return CheckResult(
            rating="FC",
            finding=f"{found} critical sections present.",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {found} of {len(critical)} critical sections.",
        recommended_action="Ensure Cybersecurity Goals, CAL Determination, Asset Mapping, and Concept Handoff tabs are present.",
        confidence="Medium",
    )


def cr_11_doc_control(p: ProbedCSGoals) -> CheckResult:
    return draft("Configuration management is organizational.", action="Confirm the CS Goals document is under version control.")


def cr_12_headers_footers(p: ProbedCSGoals) -> CheckResult:
    return draft("Headers/footers cannot be verified programmatically.", action="Manually confirm headers/footers reflect current doc ID and revision.")


def cr_13_searchability(p: ProbedCSGoals) -> CheckResult:
    if p.has_table_of_contents and len(p.sheet_names) >= 6:
        return CheckResult(
            rating="FC",
            finding="Document supports searchability via TOC and multiple tabs.",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Searchability may be limited.",
        recommended_action="Enhance TOC and sheet naming.",
        confidence="Medium",
    )


def cr_14_external_links(p: ProbedCSGoals) -> CheckResult:
    return draft("External links (TARA, Item Definition, CSR catalog) must be verified manually.", action="Verify references to external documents are current.")


# -------------------------------------------------------------------------
# CSGA Assessment (12 substantive checks)
# -------------------------------------------------------------------------

def csga_01_tara_imported(p: ProbedCSGoals) -> CheckResult:
    if p.n_tara_echo > 0:
        traced = sum(1 for t in p.tara_threats if t.csg_ref)
        return CheckResult(
            rating="FC" if traced == p.n_tara_echo else "LC",
            finding=f"{p.n_tara_echo} TARA threats imported; {traced} traced to CSGs.",
            page_section="TARA Echo tab",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="TARA threats not imported or not found.",
        recommended_action="Import high-risk threats from TARA TARA Echo tab.",
        confidence="High",
    )


def csga_02_high_risk_traced(p: ProbedCSGoals) -> CheckResult:
    high_risk = [t for t in p.tara_threats if t.risk_value and t.risk_value >= "3"]
    if not high_risk:
        return CheckResult(rating="NA", finding="No high-risk threats to trace.", confidence="High")
    traced = sum(1 for t in high_risk if t.csg_ref)
    if traced == len(high_risk):
        return CheckResult(
            rating="FC",
            finding=f"All {len(high_risk)} high-risk threats traced to CSGs.",
            page_section="TARA Echo tab",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{traced} of {len(high_risk)} high-risk threats traced.",
        recommended_action=f"Link remaining {len(high_risk) - traced} high-risk threat(s) to CSGs.",
        confidence="High",
    )


def csga_03_csg_count(p: ProbedCSGoals) -> CheckResult:
    if p.n_csg > 0:
        return CheckResult(
            rating="FC",
            finding=f"{p.n_csg} Cybersecurity Goal(s) defined.",
            page_section="Cybersecurity Goals tab",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No CSGs found.",
        recommended_action="Define Cybersecurity Goals for each high-risk threat.",
        confidence="High",
    )


def csga_04_csg_naming(p: ProbedCSGoals) -> CheckResult:
    if p.n_csg > 0:
        named = sum(1 for c in p.csg_entries if "prevent" in c.csg_text.lower() or "protect" in c.csg_text.lower())
        if named >= p.n_csg * 0.8:
            return CheckResult(
                rating="FC",
                finding=f"CSG naming convention ('Prevent/Protect <threat>') used for {named}/{p.n_csg}.",
                page_section="Cybersecurity Goals tab",
                confidence="Medium",
            )
        return CheckResult(
            rating="LC",
            finding=f"Only {named}/{p.n_csg} CSGs follow naming convention.",
            recommended_action="Use 'Prevent <threat>' or 'Protect <asset>' naming for all CSGs.",
            confidence="Medium",
        )
    return CheckResult(rating="NA", finding="No CSGs to assess.", confidence="High")


def csga_05_cal_assigned(p: ProbedCSGoals) -> CheckResult:
    if p.n_csg > 0:
        with_cal = sum(1 for c in p.csg_entries if c.cal)
        if with_cal == p.n_csg:
            return CheckResult(
                rating="FC",
                finding=f"All {p.n_csg} CSGs have CAL assigned.",
                page_section="Cybersecurity Goals tab",
                confidence="High",
            )
        return CheckResult(
            rating="PC",
            finding=f"{with_cal} of {p.n_csg} CSGs have CAL.",
            recommended_action="Assign CAL (1-4) to all CSGs.",
            confidence="High",
        )
    return CheckResult(rating="NA", finding="No CSGs to assess.", confidence="High")


def csga_06_cal_sensible(p: ProbedCSGoals) -> CheckResult:
    if not p.cal_distribution:
        return CheckResult(rating="NA", finding="No CAL assignments to assess.", confidence="High")
    if len(p.cal_distribution) >= 2:
        return CheckResult(
            rating="FC",
            finding=f"CAL distribution diverse: {dict(p.cal_distribution)}.",
            page_section="Cybersecurity Goals tab",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"CAL distribution limited: {dict(p.cal_distribution)}.",
        recommended_action="Review CAL assignments; ensure differentiation is justified.",
        confidence="Medium",
    )


def csga_07_property_coverage(p: ProbedCSGoals) -> CheckResult:
    required_props = {"C", "I", "A", "Auth", "Authz", "NR"}
    covered = p.properties_covered
    if covered >= required_props:
        return CheckResult(
            rating="FC",
            finding=f"All 6 cybersecurity properties covered: {', '.join(sorted(covered))}.",
            page_section="Cybersecurity Goals tab",
            confidence="High",
        )
    missing = required_props - covered
    return CheckResult(
        rating="PC" if len(missing) <= 2 else "NO",
        finding=f"Property coverage incomplete. Missing: {', '.join(sorted(missing))}.",
        recommended_action=f"Add CSGs covering missing properties.",
        confidence="High",
    )


def csga_08_asset_mapping_coverage(p: ProbedCSGoals) -> CheckResult:
    if p.n_asset_csg_mappings > 0:
        return CheckResult(
            rating="FC",
            finding=f"{p.n_asset_csg_mappings} asset-to-CSG mapping row(s) documented.",
            page_section="Asset to CSG Map tab",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Asset-to-CSG mapping not documented.",
        recommended_action="Map high-value assets to protecting CSGs.",
        confidence="High",
    )


def csga_09_cal_justification(p: ProbedCSGoals) -> CheckResult:
    return draft("CAL justification (per attack potential and business criticality) must be verified manually.", page_section="CAL Determination tab", action="Confirm CAL assignment rationale is documented for each CSG.")


def csga_10_owner_assigned(p: ProbedCSGoals) -> CheckResult:
    if p.n_csg > 0:
        with_owner = sum(1 for c in p.csg_entries if c.owner)
        if with_owner == p.n_csg:
            return CheckResult(
                rating="FC",
                finding=f"All {p.n_csg} CSGs have owner assigned.",
                page_section="Cybersecurity Goals tab",
                confidence="High",
            )
        return CheckResult(
            rating="PC",
            finding=f"{with_owner} of {p.n_csg} CSGs have owner.",
            recommended_action="Assign responsible owner to each CSG.",
            confidence="High",
        )
    return CheckResult(rating="NA", finding="No CSGs to assess.", confidence="High")


def csga_11_concept_handoff(p: ProbedCSGoals) -> CheckResult:
    handoff_sheet = any("concept" in s.lower() or "handoff" in s.lower() for s in p.sheet_names)
    if handoff_sheet:
        return CheckResult(
            rating="FC",
            finding="CS Concept Handoff tab found; should have placeholder CSR rows.",
            page_section="CS Concept Handoff tab",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="CS Concept Handoff preparation not documented.",
        recommended_action="Prepare Concept Handoff tab with placeholder CSR rows per CSG.",
        confidence="Medium",
    )


def csga_12_residual_risk(p: ProbedCSGoals) -> CheckResult:
    return draft("Residual risk acceptance must be documented and approved.", action="Confirm residual risk acceptance is recorded per CSG or overall.")


# -------------------------------------------------------------------------
# Verification Assessment (5-6 checks)
# -------------------------------------------------------------------------

def va_01_verification_planning(p: ProbedCSGoals) -> CheckResult:
    return draft("Verification planning for each CSG must be documented in a separate Verification Plan.", action="Confirm verification methods are planned for each CSG per CAL.")


def va_02_external_review(p: ProbedCSGoals) -> CheckResult:
    return draft("External security review or threat modeling validation may be required for high-CAL CSGs.", action="Confirm threat modeling is validated against external threat intelligence.")


def va_03_csr_catalog_ready(p: ProbedCSGoals) -> CheckResult:
    return draft("Cybersecurity Requirements (CSR) catalog must be prepared for CS Concept stage.", action="Confirm CSR catalog structure is ready for population from CS Concept.")


def va_04_independence(p: ProbedCSGoals) -> CheckResult:
    return draft("Independence of CSG definition team should be documented.", action="Confirm CSG derivation was performed by independent team.")


def va_05_governance(p: ProbedCSGoals) -> CheckResult:
    return draft("Governance and approval of CS Goals must be documented.", action="Confirm CS Goals have been reviewed and approved per organizational procedures.")


def va_06_traceability_matrix(p: ProbedCSGoals) -> CheckResult:
    return draft("Traceability matrix (TARA -> CSG -> CSI) should be prepared for audit trail.", action="Prepare and maintain traceability matrix linking TARA threats to CSI implementation.")


# -------------------------------------------------------------------------
# Check registry
# -------------------------------------------------------------------------

CHECKS = [
    CheckDef("1", "CR", "Document Structure and Control", "Document has 7 tabs covering all CS Goals workflow sections", "Shall", cr_01_structured),
    CheckDef("2", "CR", "Document Structure and Control", "Document title is clear and covers scope", "Shall", cr_02_title),
    CheckDef("3", "CR", "Document Structure and Control", "Author and Approver are populated", "Shall", cr_03_author_approver),
    CheckDef("4", "CR", "Document Structure and Control", "Revision number and history are maintained", "Shall", cr_04_revision),
    CheckDef("5", "CR", "Document Structure and Control", "Status (Draft/In Review/Released) is indicated", "Shall", cr_05_status),
    CheckDef("6", "CR", "Document Structure and Control", "Project name/ID is recorded", "Should", cr_06_project),
    CheckDef("7", "CR", "Document Structure and Control", "References to standards and related docs are provided", "Shall", cr_07_references),
    CheckDef("8", "CR", "Document Structure and Control", "Table of Contents or General Info tab is present", "Should", cr_08_toc),
    CheckDef("9", "CR", "Document Structure and Control", "TARA threats are imported or echoed in document", "Shall", cr_09_tara_reference),
    CheckDef("10", "CR", "Document Structure and Control", "All critical sections (CSG, CAL, Asset Mapping, Concept Handoff) are present", "Shall", cr_10_complete_sections),
    CheckDef("11", "CR", "Document Structure and Control", "Configuration management and version control are in place", "Should", cr_11_doc_control),
    CheckDef("12", "CR", "Document Structure and Control", "Document headers and footers reflect current ID/revision", "Should", cr_12_headers_footers),
    CheckDef("13", "CR", "Document Structure and Control", "Document is searchable and navigable", "Should", cr_13_searchability),
    CheckDef("14", "CR", "Document Structure and Control", "Links to external artifacts (TARA, CSR Catalog) are current", "Should", cr_14_external_links),

    CheckDef("1", "CSGA", "TARA Traceability", "TARA threats are imported with high-risk threats traced to CSGs", "Shall", csga_01_tara_imported),
    CheckDef("2", "CSGA", "TARA Traceability", "High-risk threats (Risk >= 3) are traced to CSGs", "Shall", csga_02_high_risk_traced),
    CheckDef("3", "CSGA", "Cybersecurity Goals Definition", "At least one CSG per high-risk threat scenario", "Shall", csga_03_csg_count),
    CheckDef("4", "CSGA", "Cybersecurity Goals Definition", "Each CSG uses 'Prevent <threat>' or similar convention", "Shall", csga_04_csg_naming),
    CheckDef("5", "CSGA", "CAL Assignment", "CAL assigned per Cybersecurity Goal", "Shall", csga_05_cal_assigned),
    CheckDef("6", "CSGA", "CAL Assignment", "CAL distribution is sensible and justifiable", "Should", csga_06_cal_sensible),
    CheckDef("7", "CSGA", "Property Coverage", "All 6 cybersecurity properties covered (C/I/A/Auth/Authz/NR)", "Shall", csga_07_property_coverage),
    CheckDef("8", "CSGA", "Asset to CSG Mapping", "High-value assets are mapped to protecting CSGs", "Shall", csga_08_asset_mapping_coverage),
    CheckDef("9", "CSGA", "CAL Determination", "CAL determination justification provided per CSG", "Shall", csga_09_cal_justification),
    CheckDef("10", "CSGA", "Governance and Roles", "Goal owner assigned per CSG", "Should", csga_10_owner_assigned),
    CheckDef("11", "CSGA", "Handoff Readiness", "CS Concept Handoff prepared with placeholder CSR rows", "Should", csga_11_concept_handoff),
    CheckDef("12", "CSGA", "Risk Acceptance", "Residual risk acceptance documented", "Should", csga_12_residual_risk),

    CheckDef("1", "VA", "Verification Planning", "Verification methods planned for each CSG per CAL", "Should", va_01_verification_planning),
    CheckDef("2", "VA", "External Review", "Threat modeling validated against external intelligence", "Should", va_02_external_review),
    CheckDef("3", "VA", "CSR Catalog Readiness", "Cybersecurity Requirements catalog structure prepared", "Should", va_03_csr_catalog_ready),
    CheckDef("4", "VA", "Independence", "CSG derivation performed by independent team", "Should", va_04_independence),
    CheckDef("5", "VA", "Governance and Approval", "CS Goals reviewed and approved per procedures", "Should", va_05_governance),
    CheckDef("6", "VA", "Traceability", "Traceability matrix (TARA-CSG-CSI) prepared for audit", "Should", va_06_traceability_matrix),
]
