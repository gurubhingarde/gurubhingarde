"""
TARA checklist definitions and verification logic per ISO/SAE 21434.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from tara_probe import ProbedTara


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
    verify: Callable[[ProbedTara], CheckResult]


# -------------------------------------------------------------------------
# Confirmation Review (14 checks)
# -------------------------------------------------------------------------

def cr_01_structured(p: ProbedTara) -> CheckResult:
    if len(p.sheet_names) >= 10:
        return CheckResult(
            rating="FC",
            finding=f"Document has {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has only {len(p.sheet_names)} tabs; may lack sufficient structure.",
        recommended_action="Ensure all 13 TARA tabs are present per ISO/SAE 21434.",
        confidence="Medium",
    )


def cr_02_title(p: ProbedTara) -> CheckResult:
    if p.title:
        return draft(f"Title: '{p.title}'. Reviewer to confirm it covers the scope.", page_section="Title page")
    return CheckResult(
        rating="NO",
        finding="No title detected.",
        recommended_action="Add a document title on the Title page.",
        confidence="High",
    )


def cr_03_author_approver(p: ProbedTara) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(
            rating="FC",
            finding=f"Author='{p.author}', Approver='{p.approver}'.",
            page_section="Title page",
            confidence="High",
        )
    missing = []
    if not p.author:
        missing.append("Author")
    if not p.approver:
        missing.append("Approver")
    return CheckResult(
        rating="NO",
        finding=f"Missing: {', '.join(missing)}.",
        recommended_action=f"Populate {', '.join(missing)} on Title page.",
        confidence="High",
    )


def cr_04_revision(p: ProbedTara) -> CheckResult:
    if p.revision and p.revision_history_rows >= 1:
        return CheckResult(
            rating="FC",
            finding=f"Revision='{p.revision}'; Document Control has {p.revision_history_rows} history row(s).",
            page_section="Title page + Document Control tab",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Revision field not populated or no revision history detected.",
        recommended_action="Populate Revision and add history rows to Document Control.",
        confidence="High",
    )


def cr_05_status(p: ProbedTara) -> CheckResult:
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
        recommended_action="Add Status (Draft / In Review / Released) to Title page.",
        confidence="High",
    )


def cr_06_project(p: ProbedTara) -> CheckResult:
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
        recommended_action="Add Project name to Title page for traceability.",
        confidence="High",
    )


def cr_07_references(p: ProbedTara) -> CheckResult:
    refs_sheet = any("reference" in s.lower() for s in p.sheet_names)
    if refs_sheet:
        return CheckResult(
            rating="FC",
            finding="References tab found; should cite ISO/SAE 21434, UN R155, and related documents.",
            page_section="References tab",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No References tab detected.",
        recommended_action="Add References tab citing ISO/SAE 21434 and related standards.",
        confidence="Medium",
    )


def cr_08_toc(p: ProbedTara) -> CheckResult:
    if p.has_table_of_contents:
        return CheckResult(
            rating="FC",
            finding="Table of Contents or General Info tab present.",
            page_section=f"Sheet '{p.sheet_names[0]}'",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No TOC detected in first three sheets.",
        recommended_action="Add a Table of Contents or General Info tab.",
        confidence="Medium",
    )


def cr_09_assumptions(p: ProbedTara) -> CheckResult:
    if p.n_assumptions > 0:
        return CheckResult(
            rating="FC",
            finding=f"Assumptions sheet found with documented constraints.",
            page_section="Assumptions tab",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Assumptions may not be fully documented.",
        recommended_action="Ensure Assumptions tab includes scope, attacker model, and exclusions.",
        confidence="Medium",
    )


def cr_10_complete_sections(p: ProbedTara) -> CheckResult:
    critical_sheets = ["04_asset", "05_threat", "06_impact", "08_feasibility", "09_risk", "10_risk_treatment", "11_cybersecurity"]
    found = sum(1 for s in p.sheet_names if any(cs in s for cs in critical_sheets))
    if found >= 6:
        return CheckResult(
            rating="FC",
            finding=f"{found} critical sections populated.",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {found} of {len(critical_sheets)} critical sections found.",
        recommended_action="Ensure all TARA workflow tabs are present and populated.",
        confidence="Medium",
    )


def cr_11_doc_control(p: ProbedTara) -> CheckResult:
    return draft("Document control procedures are organizational; cannot verify from xlsx alone.", action="Confirm the TARA is under version control and configuration management.")


def cr_12_headers_footers(p: ProbedTara) -> CheckResult:
    return draft("Headers/footers cannot be reliably verified programmatically.", action="Manually confirm headers/footers reflect current document ID and revision.")


def cr_13_searchability(p: ProbedTara) -> CheckResult:
    if p.has_table_of_contents and len(p.sheet_names) >= 10:
        return CheckResult(
            rating="FC",
            finding="Document structure supports searchability via TOC and multiple tabs.",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Searchability may be limited.",
        recommended_action="Enhance TOC and sheet naming for ease of navigation.",
        confidence="Medium",
    )


def cr_14_external_links(p: ProbedTara) -> CheckResult:
    return draft("External links (Item Definition, specifications, compliance matrix) must be confirmed manually.", action="Verify references to external documents are current and accessible.")


# -------------------------------------------------------------------------
# TARAA Assessment (18 substantive checks)
# -------------------------------------------------------------------------

def taraa_01_asset_inventory(p: ProbedTara) -> CheckResult:
    if p.n_assets > 0:
        have_props = sum(1 for a in p.assets if a.cybersecurity_properties)
        return CheckResult(
            rating="FC" if have_props == p.n_assets else "LC",
            finding=f"Asset inventory: {p.n_assets} asset(s) listed; {have_props} have cybersecurity properties identified.",
            page_section="Asset Inventory tab",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Asset inventory is empty or not found.",
        recommended_action="Enumerate all assets in Item Description and populate Asset Inventory tab.",
        confidence="High",
    )


def taraa_02_stride_coverage(p: ProbedTara) -> CheckResult:
    stride_set = {s.upper() for s in p.stride_categories if s}
    required = {"S", "T", "R", "I", "D", "E"}
    if stride_set == required:
        return CheckResult(
            rating="FC",
            finding=f"All STRIDE categories represented: {', '.join(sorted(stride_set))}.",
            page_section="Threat Scenarios tab",
            confidence="High",
        )
    missing = required - stride_set
    return CheckResult(
        rating="PC" if len(missing) <= 2 else "NO",
        finding=f"STRIDE coverage incomplete. Missing: {', '.join(sorted(missing))}.",
        recommended_action=f"Add threat scenarios covering missing STRIDE categories.",
        confidence="High",
    )


def taraa_03_threat_impact_rated(p: ProbedTara) -> CheckResult:
    rated = sum(1 for t in p.threats if t.impact_s or t.impact_f or t.impact_o or t.impact_p)
    if rated == len(p.threats) and p.n_threats > 0:
        return CheckResult(
            rating="FC",
            finding=f"All {p.n_threats} threats have at least one impact dimension (SFOP) rated.",
            page_section="Impact Assessment tab",
            confidence="High",
        )
    if p.n_threats > 0:
        return CheckResult(
            rating="PC",
            finding=f"{rated} of {p.n_threats} threats have impact ratings.",
            recommended_action="Complete impact assessment (Safety, Financial, Operational, Privacy) for all threats.",
            confidence="High",
        )
    return CheckResult(rating="NA", finding="No threats to assess.", confidence="High")


def taraa_04_threat_feasibility_rated(p: ProbedTara) -> CheckResult:
    rated = sum(1 for t in p.threats if t.feasibility_rating)
    if rated == len(p.threats) and p.n_threats > 0:
        return CheckResult(
            rating="FC",
            finding=f"All {p.n_threats} threats have feasibility ratings.",
            page_section="Feasibility Rating tab",
            confidence="High",
        )
    if p.n_threats > 0:
        return CheckResult(
            rating="PC",
            finding=f"{rated} of {p.n_threats} threats have feasibility ratings.",
            recommended_action="Complete feasibility assessment for all threats using attack-potential factors.",
            confidence="High",
        )
    return CheckResult(rating="NA", finding="No threats to assess.", confidence="High")


def taraa_05_risk_value_computed(p: ProbedTara) -> CheckResult:
    rated = sum(1 for t in p.threats if t.risk_value)
    if rated == len(p.threats) and p.n_threats > 0:
        return CheckResult(
            rating="FC",
            finding=f"All {p.n_threats} threats have computed Risk Values.",
            page_section="Risk Determination tab",
            confidence="High",
        )
    if p.n_threats > 0:
        return CheckResult(
            rating="PC",
            finding=f"{rated} of {p.n_threats} threats have Risk Values.",
            recommended_action="Compute Risk Values for all threats (impact x feasibility).",
            confidence="High",
        )
    return CheckResult(rating="NA", finding="No threats to assess.", confidence="High")


def taraa_06_risk_distribution(p: ProbedTara) -> CheckResult:
    if not p.risk_values:
        return CheckResult(rating="NA", finding="No risk values to assess.", confidence="High")
    unique_vals = set(p.risk_values)
    if len(unique_vals) >= 2:
        return CheckResult(
            rating="FC",
            finding=f"Risk Value distribution is diverse: {', '.join(sorted(unique_vals))}.",
            page_section="Risk Determination tab",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Risk Values show limited distribution (all same: {unique_vals.pop()}).",
        recommended_action="Review impact and feasibility ratings; ensure differentiation is appropriate.",
        confidence="Medium",
    )


def taraa_07_treatment_assigned(p: ProbedTara) -> CheckResult:
    with_treatment = sum(1 for t in p.threats if t.treatment)
    if with_treatment == len(p.threats) and p.n_threats > 0:
        return CheckResult(
            rating="FC",
            finding=f"All {p.n_threats} threats have treatment decisions (Avoid/Reduce/Share/Retain).",
            page_section="Risk Treatment tab",
            confidence="High",
        )
    if p.n_threats > 0:
        return CheckResult(
            rating="PC",
            finding=f"{with_treatment} of {p.n_threats} threats have treatment decisions.",
            recommended_action="Assign treatment (Avoid/Reduce/Share/Retain) for all threats.",
            confidence="High",
        )
    return CheckResult(rating="NA", finding="No threats to treat.", confidence="High")


def taraa_08_high_risk_treatment(p: ProbedTara) -> CheckResult:
    high_risk_no_treatment = [t for t in p.threats if (t.risk_value and t.risk_value >= "3") and not t.treatment]
    headline = len(high_risk_no_treatment)
    if headline == 0:
        return CheckResult(
            rating="FC",
            finding="All high-risk scenarios (Risk >= 3) have treatment decisions.",
            page_section="Risk Treatment tab",
            confidence="High",
        )
    return CheckResult(
        rating="NO" if headline > 2 else "PC",
        finding=f"{headline} high-risk threat(s) lack treatment decisions.",
        recommended_action=f"Assign treatment decisions to {headline} high-risk scenario(s).",
        confidence="High",
    )


def taraa_09_csg_traceability(p: ProbedTara) -> CheckResult:
    if p.n_csg > 0 and p.n_threats > 0:
        traced = sum(1 for csg in p.cybersecurity_goals if csg.threat_ref)
        if traced == p.n_csg:
            return CheckResult(
                rating="FC",
                finding=f"All {p.n_csg} CSGs traced to threat scenarios.",
                page_section="Cybersecurity Goals tab",
                confidence="High",
            )
        return CheckResult(
            rating="PC",
            finding=f"{traced} of {p.n_csg} CSGs traced to threats.",
            recommended_action="Link all CSGs to source threat scenarios for traceability.",
            confidence="High",
        )
    return CheckResult(rating="NA", finding="Insufficient CSGs or threats for traceability check.", confidence="High")


def taraa_10_cal_assignment(p: ProbedTara) -> CheckResult:
    if p.n_csg > 0:
        with_cal = sum(1 for csg in p.cybersecurity_goals if csg.cal)
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
            recommended_action="Assign CAL (1-4) to all Cybersecurity Goals.",
            confidence="High",
        )
    return CheckResult(rating="NA", finding="No CSGs to assess.", confidence="High")


def taraa_11_attack_path_documented(p: ProbedTara) -> CheckResult:
    return draft("Attack path analysis requires visual inspection and external threat intelligence.", page_section="Attack Path Analysis tab", action="Confirm attack paths document entry point, vector, and propagation for all threats.")


def taraa_12_threat_agent_identified(p: ProbedTara) -> CheckResult:
    return draft("Threat agent identification (internal/external, attacker model) must be verified manually.", action="Confirm threat scenarios identify the attacker/threat agent type and capabilities.")


def taraa_13_assumptions_documented(p: ProbedTara) -> CheckResult:
    if any("assumption" in s.lower() for s in p.sheet_names):
        return CheckResult(
            rating="FC",
            finding="Assumptions tab present; should document scope, attacker model, excluded threats.",
            page_section="Assumptions tab",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Assumptions not clearly documented.",
        recommended_action="Add Assumptions tab covering scope, item boundaries, and attacker model.",
        confidence="Medium",
    )


def taraa_14_out_of_scope_noted(p: ProbedTara) -> CheckResult:
    return draft("Out-of-scope threats and assumptions must be explicitly documented.", action="Confirm the TARA explicitly lists threats that are excluded and why.")


def taraa_15_iso_references(p: ProbedTara) -> CheckResult:
    refs_sheet = any("reference" in s.lower() for s in p.sheet_names)
    if refs_sheet:
        return CheckResult(
            rating="FC",
            finding="References tab found; should cite ISO/SAE 21434 and UN R155.",
            page_section="References tab",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No References tab detected.",
        recommended_action="Add References tab citing ISO/SAE 21434 Sections 15-16 and UN R155.",
        confidence="Medium",
    )


def taraa_16_concept_handoff(p: ProbedTara) -> CheckResult:
    return draft("CS Concept Handoff preparation (placeholder CSR rows) must be verified manually.", page_section="All tabs", action="Confirm handoff to CS Concept stage is prepared with CSR placeholders.")


def taraa_17_independence_evidence(p: ProbedTara) -> CheckResult:
    return draft("Independence of threat analysis team must be documented outside the xlsx.", action="Confirm TARA was performed by independent team (I1/I2 per ISO/SAE 21434).")


def taraa_18_governance_review(p: ProbedTara) -> CheckResult:
    return draft("Governance and approval flow requires organizational verification.", action="Confirm TARA has been reviewed and approved per organizational procedures.")


# -------------------------------------------------------------------------
# Verification Assessment (external artifact checks, 5-6 listed)
# -------------------------------------------------------------------------

def va_01_threat_validation(p: ProbedTara) -> CheckResult:
    return draft("Threat validation against external threat intelligence (NIST, STRIDE databases) required.", action="Verify threat list against external threat models and attack taxonomies.")


def va_02_penetration_testing(p: ProbedTara) -> CheckResult:
    return draft("Penetration testing or red-team analysis required for CAL 3-4 scenarios.", action="Confirm penetration test results are available for high-CAL threats.")


def va_03_risk_acceptance(p: ProbedTara) -> CheckResult:
    return draft("Risk acceptance for Retain-decision threats must be documented and approved.", action="Confirm residual-risk acceptance is documented and signed off.")


def va_04_compliance_verification(p: ProbedTara) -> CheckResult:
    return draft("Compliance with UN R155 and OEM cybersecurity requirements must be verified.", action="Cross-reference TARA findings against compliance matrix.")


def va_05_tool_qualification(p: ProbedTara) -> CheckResult:
    return draft("Any automated threat-analysis or risk-scoring tools must be qualified.", action="Document tool versions, qualification status, and any limitations.")


def va_06_evidence_retention(p: ProbedTara) -> CheckResult:
    return draft("All evidence (interviews, threat workshops, technical analysis) must be retained.", action="Confirm evidence package is complete and retained per retention policy.")


# -------------------------------------------------------------------------
# Check registry
# -------------------------------------------------------------------------

CHECKS = [
    CheckDef("1", "CR", "Document Structure and Control", "Document has 10+ tabs covering all TARA workflow sections", "Shall", cr_01_structured),
    CheckDef("2", "CR", "Document Structure and Control", "Document title is clear and covers scope", "Shall", cr_02_title),
    CheckDef("3", "CR", "Document Structure and Control", "Author and Approver are populated", "Shall", cr_03_author_approver),
    CheckDef("4", "CR", "Document Structure and Control", "Revision number and history are maintained", "Shall", cr_04_revision),
    CheckDef("5", "CR", "Document Structure and Control", "Status (Draft/In Review/Released) is indicated", "Shall", cr_05_status),
    CheckDef("6", "CR", "Document Structure and Control", "Project name/ID is recorded", "Should", cr_06_project),
    CheckDef("7", "CR", "Document Structure and Control", "References to standards and related docs are provided", "Shall", cr_07_references),
    CheckDef("8", "CR", "Document Structure and Control", "Table of Contents or General Info tab is present", "Should", cr_08_toc),
    CheckDef("9", "CR", "Document Structure and Control", "Assumptions (scope, attacker model) are documented", "Shall", cr_09_assumptions),
    CheckDef("10", "CR", "Document Structure and Control", "All critical sections (Asset, Threat, Impact, Risk, CSG) are populated", "Shall", cr_10_complete_sections),
    CheckDef("11", "CR", "Document Structure and Control", "Configuration management and version control are in place", "Should", cr_11_doc_control),
    CheckDef("12", "CR", "Document Structure and Control", "Document headers and footers reflect current ID/revision", "Should", cr_12_headers_footers),
    CheckDef("13", "CR", "Document Structure and Control", "Document is searchable and navigable", "Should", cr_13_searchability),
    CheckDef("14", "CR", "Document Structure and Control", "Links to external artifacts (Item Def, specs) are current", "Should", cr_14_external_links),

    CheckDef("1", "TARAA", "Asset Inventory and Properties", "Asset inventory is complete; each asset has cybersecurity properties identified", "Shall", taraa_01_asset_inventory),
    CheckDef("2", "TARAA", "Threat Scenario Completeness", "Threat scenarios cover all STRIDE categories (S/T/R/I/D/E)", "Shall", taraa_02_stride_coverage),
    CheckDef("3", "TARAA", "Impact Assessment", "Each threat scenario has impact rated across SFOP (Safety/Financial/Operational/Privacy)", "Shall", taraa_03_threat_impact_rated),
    CheckDef("4", "TARAA", "Feasibility Assessment", "Each threat scenario has feasibility rated using attack-potential factors", "Shall", taraa_04_threat_feasibility_rated),
    CheckDef("5", "TARAA", "Risk Determination", "Risk Value computed for every threat scenario", "Shall", taraa_05_risk_value_computed),
    CheckDef("6", "TARAA", "Risk Determination", "Risk Value distribution is sensible (not all same rating)", "Should", taraa_06_risk_distribution),
    CheckDef("7", "TARAA", "Risk Treatment", "Each threat has treatment decision (Avoid/Reduce/Share/Retain)", "Shall", taraa_07_treatment_assigned),
    CheckDef("8", "TARAA", "Risk Treatment", "High-risk scenarios (Risk >= 3) have treatment decisions", "Shall", taraa_08_high_risk_treatment),
    CheckDef("9", "TARAA", "Cybersecurity Goals Traceability", "High-risk threats are traced to Cybersecurity Goals", "Shall", taraa_09_csg_traceability),
    CheckDef("10", "TARAA", "Cybersecurity Goals Traceability", "CAL assigned per Cybersecurity Goal", "Shall", taraa_10_cal_assignment),
    CheckDef("11", "TARAA", "Attack Path Analysis", "Attack paths documented (entry, vector, propagation) per threat", "Shall", taraa_11_attack_path_documented),
    CheckDef("12", "TARAA", "Threat Agent Identification", "Threat agent/attacker model identified per scenario", "Shall", taraa_12_threat_agent_identified),
    CheckDef("13", "TARAA", "Assumptions and Scope", "Assumptions documented (item scope, attacker model)", "Shall", taraa_13_assumptions_documented),
    CheckDef("14", "TARAA", "Assumptions and Scope", "Out-of-scope threats explicitly noted", "Should", taraa_14_out_of_scope_noted),
    CheckDef("15", "TARAA", "References", "References to ISO/SAE 21434 and UN R155 provided", "Shall", taraa_15_iso_references),
    CheckDef("16", "TARAA", "Handoff Readiness", "CS Concept Handoff prepared with placeholder CSR rows", "Should", taraa_16_concept_handoff),
    CheckDef("17", "TARAA", "Independence and Governance", "Evidence of independent threat analysis team", "Should", taraa_17_independence_evidence),
    CheckDef("18", "TARAA", "Independence and Governance", "Governance review and approval documented", "Should", taraa_18_governance_review),

    CheckDef("1", "VA", "External Threat Validation", "Threat validation against external threat intelligence", "Should", va_01_threat_validation),
    CheckDef("2", "VA", "Verification Methods", "Penetration testing/red-team results available for CAL 3-4", "Should", va_02_penetration_testing),
    CheckDef("3", "VA", "Risk Acceptance", "Residual risk acceptance documented and approved", "Should", va_03_risk_acceptance),
    CheckDef("4", "VA", "Compliance Verification", "Compliance with UN R155 and OEM requirements verified", "Should", va_04_compliance_verification),
    CheckDef("5", "VA", "Tool Qualification", "Threat analysis tools are qualified and documented", "Should", va_05_tool_qualification),
    CheckDef("6", "VA", "Evidence Retention", "Evidence package (interviews, workshops, analysis) is retained", "Should", va_06_evidence_retention),
]
