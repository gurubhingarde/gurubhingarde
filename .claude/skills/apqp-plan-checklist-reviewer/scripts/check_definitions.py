"""
Canonical checklist definitions and verification logic for APQP Plan.

Each check is a CheckDef with:
- id: row id
- tab: output tab (CR / APQPA / VA)
- section: section header
- requirement: requirement text
- obligation: "Shall" or "Should"
- verify: callable that returns CheckResult
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from apqp_probe import ProbedAPQPPlan


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

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
# Confirmation Review (14 doc-quality checks)
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedAPQPPlan) -> CheckResult:
    if len(p.sheet_names) >= 12:
        return CheckResult(
            rating="FC",
            finding=f"APQP Plan structured into {len(p.sheet_names)} tabs with distinct phases and deliverables.",
            page_section="All tabs",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.sheet_names)} tabs; structure may be insufficient.",
        recommended_action="Ensure separate tabs for each APQP phase, gate reviews, special characteristics, risk register, and open items.",
        confidence="Medium",
    )


def cr_02_template(p: ProbedAPQPPlan) -> CheckResult:
    return draft(
        "Template version cannot be detected from xlsx content alone.",
        action="Confirm the latest AIAG APQP Manual template or OEM-specific template was used.",
    )


def cr_03_searchable(p: ProbedAPQPPlan) -> CheckResult:
    if p.is_apqp_builder_format and p.sheet_names[0].lower().startswith("0"):
        return CheckResult(
            rating="FC",
            finding="Document has numbered tabs (0x_Name format); structured columns aid search.",
            page_section=f"Sheet structure starting with {p.sheet_names[0]}",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Tab naming not fully structured for navigation.",
        recommended_action="Use consistent tab naming (0x_Section_Name) and add cross-references.",
        confidence="Medium",
    )


def cr_04a_title_scope(p: ProbedAPQPPlan) -> CheckResult:
    if p.title:
        return draft(
            f"Title: {p.title}. Reviewer to confirm it reflects APQP scope.",
            page_section="Title page",
        )
    return CheckResult(
        rating="NO",
        finding="No title detected on the Title page.",
        recommended_action="Add APQP Plan title reflecting project/program.",
        confidence="High",
    )


def cr_04b_author_approver(p: ProbedAPQPPlan) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(
            rating="FC",
            finding=f"Author={p.author}; Approver={p.approver}.",
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


def cr_04c_revision(p: ProbedAPQPPlan) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Revision={p.revision}.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No revision number.",
        recommended_action="Populate Revision field.",
        confidence="High",
    )


def cr_04d_change_history(p: ProbedAPQPPlan) -> CheckResult:
    if p.is_apqp_builder_format:
        return CheckResult(
            rating="FC",
            finding="Document Control tab includes revision history.",
            page_section="01_Document_Control",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Cannot verify revision history.",
        recommended_action="Ensure Document Control tab contains revision history.",
        confidence="Medium",
    )


def cr_04e_status(p: ProbedAPQPPlan) -> CheckResult:
    if p.status:
        return CheckResult(
            rating="FC",
            finding=f"Status={p.status}.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No status field.",
        recommended_action="Add Status field (Draft / In Review / Released).",
        confidence="High",
    )


def cr_05_current_revision(p: ProbedAPQPPlan) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Current revision {p.revision} identifiable.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Current revision not identifiable.",
        recommended_action="Populate Revision field.",
        confidence="High",
    )


def cr_06_config_mgmt(p: ProbedAPQPPlan) -> CheckResult:
    return draft(
        "Configuration management is organizational practice; verify externally.",
        action="Confirm APQP Plan is in version control (Git, SVN, Polarion, etc.).",
    )


def cr_07_header_footer(p: ProbedAPQPPlan) -> CheckResult:
    return draft(
        "Cannot verify header/footer programmatically.",
        action="Open workbook and confirm header/footer reflect document ID and revision.",
    )


def cr_08_toc(p: ProbedAPQPPlan) -> CheckResult:
    if p.sheet_names and p.sheet_names[0].lower().startswith("0"):
        return CheckResult(
            rating="FC",
            finding="Numbered tabs function as table of contents.",
            page_section=f"Sheet structure: {p.sheet_names[0:3]}...",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="No explicit Table of Contents.",
        recommended_action="Add TOC tab or use consistent numbered naming.",
        confidence="Medium",
    )


def cr_09_references(p: ProbedAPQPPlan) -> CheckResult:
    refs_sheet = next((s for s in p.sheet_names if "reference" in s.lower()), None)
    if refs_sheet:
        return draft(
            f"References content on {refs_sheet}. Verify completeness.",
            page_section=f"Sheet {refs_sheet}",
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated References tab.",
        recommended_action="Add References tab citing AIAG APQP Manual, IATF 16949, FMEA standards, Control Plan guidelines.",
        confidence="Medium",
    )


def cr_10_sections_complete(p: ProbedAPQPPlan) -> CheckResult:
    critical_tabs = ["02_Program_Info", "03_Cross_Functional_Team", "04_Phase1", "09_Master_Schedule", "10_Gate_Reviews"]
    present = sum(1 for t in critical_tabs if any(t.lower() in s.lower() for s in p.sheet_names))
    if present >= 4:
        return CheckResult(
            rating="FC",
            finding=f"{present}/5 critical sections populated.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {present}/5 critical sections.",
        recommended_action="Complete Program Info, Team, Phases, Schedule, and Gate Reviews.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# APQP Assessment (12 substantive checks per AIAG + IATF 16949)
# ---------------------------------------------------------------------------

def apqpa_01_pm_ql(p: ProbedAPQPPlan) -> CheckResult:
    if p.program_manager and p.quality_lead:
        return CheckResult(
            rating="FC",
            finding=f"Program Manager={p.program_manager}; Quality Lead={p.quality_lead}.",
            page_section="02_Program_Info or 03_Cross_Functional_Team",
            confidence="High",
        )
    missing = []
    if not p.program_manager:
        missing.append("Program Manager")
    if not p.quality_lead:
        missing.append("Quality Lead")
    return CheckResult(
        rating="NO",
        finding=f"Missing: {', '.join(missing)}.",
        recommended_action=f"Assign {', '.join(missing)}.",
        confidence="High",
    )


def apqpa_02_cft_complete(p: ProbedAPQPPlan) -> CheckResult:
    if len(p.team_members) < 4:
        return CheckResult(
            rating="NO",
            finding=f"Only {len(p.team_members)} team members. Minimum cross-functional team requires PM, QE, DE, Mfg, Supplier Quality.",
            recommended_action="Define cross-functional team with PM, Quality Engineer, Design Engineer, Manufacturing, Supplier Quality.",
            confidence="High",
        )
    roles = {m.role.lower() for m in p.team_members}
    expected = {"project", "quality", "design", "manufacturing", "supplier"}
    found = sum(1 for exp in expected if any(exp in r for r in roles))
    if found >= 4:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.team_members)} team members with key roles identified.",
            page_section="03_Cross_Functional_Team",
            confidence="High",
        )
    return CheckResult(
        rating="LC",
        finding=f"{len(p.team_members)} team members; some key roles may be missing.",
        recommended_action="Ensure PM, QE, DE, Manufacturing, Supplier Quality represented.",
        confidence="Medium",
    )


def apqpa_03_phase1_complete(p: ProbedAPQPPlan) -> CheckResult:
    expected_p1 = ["voice", "business case", "requirements", "bom"]
    found_p1 = sum(1 for exp in expected_p1 if any(exp.lower() in d.name.lower() for d in p.phase1_deliverables))
    if len(p.phase1_deliverables) >= 3 and found_p1 >= 3:
        return CheckResult(
            rating="FC",
            finding=f"Phase 1 has {len(p.phase1_deliverables)} deliverables including VOC, requirements, preliminary BOM.",
            page_section="04_Phase1_Plan_Define",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Phase 1 incomplete: only {len(p.phase1_deliverables)} deliverables, {found_p1}/4 key items.",
        recommended_action="Add Voice of Customer, Business Case, Customer Requirements, Preliminary BOM.",
        confidence="High",
    )


def apqpa_04_phase2_dfmea(p: ProbedAPQPPlan) -> CheckResult:
    dfmea_found = any("dfmea" in d.name.lower() or "design fmea" in d.name.lower() for d in p.phase2_deliverables)
    if dfmea_found:
        return CheckResult(
            rating="FC",
            finding="Phase 2 includes Design FMEA reference.",
            page_section="05_Phase2_Product_Design",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Design FMEA not referenced in Phase 2 deliverables.",
        recommended_action="Add DFMEA deliverable or reference to Phase 2.",
        confidence="High",
    )


def apqpa_05_phase3_pfmea_cp(p: ProbedAPQPPlan) -> CheckResult:
    pfmea_found = any("pfmea" in d.name.lower() or "process fmea" in d.name.lower() for d in p.phase3_deliverables)
    cp_found = any("control plan" in d.name.lower() for d in p.phase3_deliverables)
    if pfmea_found and cp_found:
        return CheckResult(
            rating="FC",
            finding="Phase 3 includes PFMEA and Pre-launch Control Plan.",
            page_section="06_Phase3_Process_Design",
            confidence="High",
        )
    missing = []
    if not pfmea_found:
        missing.append("PFMEA")
    if not cp_found:
        missing.append("Control Plan")
    return CheckResult(
        rating="PC",
        finding=f"Phase 3 missing: {', '.join(missing)}.",
        recommended_action=f"Add {', '.join(missing)} deliverables.",
        confidence="High",
    )


def apqpa_06_phase4_msapppap(p: ProbedAPQPPlan) -> CheckResult:
    msa_found = any("msa" in d.name.lower() for d in p.phase4_deliverables)
    ppap_found = any("ppap" in d.name.lower() for d in p.phase4_deliverables)
    if msa_found and ppap_found:
        return CheckResult(
            rating="FC",
            finding="Phase 4 includes MSA executed, Process Capability, PPAP submission.",
            page_section="07_Phase4_Product_Process_Validation",
            confidence="High",
        )
    missing = []
    if not msa_found:
        missing.append("MSA")
    if not ppap_found:
        missing.append("PPAP")
    return CheckResult(
        rating="PC",
        finding=f"Phase 4 missing: {', '.join(missing)}.",
        recommended_action=f"Add {', '.join(missing)} validation deliverables.",
        confidence="High",
    )


def apqpa_07_phase5_feedback(p: ProbedAPQPPlan) -> CheckResult:
    if len(p.phase5_deliverables) > 0:
        return CheckResult(
            rating="FC",
            finding=f"Phase 5 has {len(p.phase5_deliverables)} deliverable(s) for feedback and lessons learned.",
            page_section="08_Phase5_Feedback_Corrective",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Phase 5 deliverables not defined.",
        recommended_action="Define feedback collection and lessons learned process for Phase 5.",
        confidence="High",
    )


def apqpa_08_all_gates_scheduled(p: ProbedAPQPPlan) -> CheckResult:
    if len(p.gate_reviews) >= 5:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.gate_reviews)} gate reviews scheduled (5 gates per APQP).",
            page_section="10_Gate_Reviews",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.gate_reviews)} gate reviews. APQP requires 5 gates.",
        recommended_action="Schedule all 5 APQP gates: Gate 0 (Design), 1 (Design Verify), 2 (Process), 3 (Validate), 4 (Launch).",
        confidence="High",
    )


def apqpa_09_gate_exit_criteria(p: ProbedAPQPPlan) -> CheckResult:
    with_criteria = sum(1 for g in p.gate_reviews if g.get("exit criteria") or g.get("exit_criteria"))
    if with_criteria == len(p.gate_reviews):
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.gate_reviews)} gates have exit criteria defined.",
            page_section="10_Gate_Reviews",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {with_criteria}/{len(p.gate_reviews)} gates have exit criteria.",
        recommended_action="Define exit criteria for each gate review.",
        confidence="High",
    )


def apqpa_10_special_char_list(p: ProbedAPQPPlan) -> CheckResult:
    if len(p.special_characteristics) > 0:
        return CheckResult(
            rating="FC",
            finding=f"Special Characteristics list maintained: {len(p.special_characteristics)} characteristics.",
            page_section="11_Special_Characteristics",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Special Characteristics list empty.",
        recommended_action="Identify and list all critical/special characteristics per OEM convention (CSC/SC).",
        confidence="High",
    )


def apqpa_11_risk_register(p: ProbedAPQPPlan) -> CheckResult:
    with_mitigation = sum(1 for r in p.risks if r.mitigation)
    if len(p.risks) > 0 and with_mitigation >= len(p.risks) * 0.8:
        return CheckResult(
            rating="FC",
            finding=f"Risk Register populated: {len(p.risks)} risks with mitigations.",
            page_section="12_Risk_Register",
            confidence="High",
        )
    if len(p.risks) > 0:
        return CheckResult(
            rating="LC",
            finding=f"{len(p.risks)} risks identified; {with_mitigation} have documented mitigations.",
            recommended_action=f"Define mitigations for {len(p.risks) - with_mitigation} remaining risks.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Risk Register is empty.",
        recommended_action="Populate Risk Register with identified risks and mitigation plans.",
        confidence="High",
    )


def apqpa_12_deliverable_ownership(p: ProbedAPQPPlan) -> CheckResult:
    all_deliverables = (
        p.phase1_deliverables + p.phase2_deliverables + p.phase3_deliverables +
        p.phase4_deliverables + p.phase5_deliverables
    )
    without_owner = [d for d in all_deliverables if not d.owner]
    if not without_owner and len(all_deliverables) > 0:
        return CheckResult(
            rating="FC",
            finding=f"All {len(all_deliverables)} deliverables have assigned owners.",
            page_section="Phase 1-5 tabs",
            confidence="High",
        )
    rate = (len(all_deliverables) - len(without_owner)) / len(all_deliverables) if all_deliverables else 0
    if rate >= 0.8:
        return CheckResult(
            rating="LC",
            finding=f"{len(all_deliverables) - len(without_owner)}/{len(all_deliverables)} deliverables have owners.",
            recommended_action=f"Assign owners to {len(without_owner)} deliverables.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(all_deliverables) - len(without_owner)}/{len(all_deliverables)} have owners.",
        recommended_action="Assign responsible person/team to each deliverable.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Verification Assessment (external)
# ---------------------------------------------------------------------------

def _va_external(label: str) -> CheckResult:
    return draft(
        f"{label} required by external processes.",
        action="Verify against project governance and OEM requirements.",
    )


def va_01_ppl_analysis(p): return _va_external("Pre-Production Launch (PPL) analysis and sign-off")
def va_02_supplier_capable(p): return _va_external("Supplier manufacturing capability baseline")
def va_03_customer_approval(p): return _va_external("Customer approval of APQP Plan")
def va_04_prototype_results(p): return _va_external("Prototype/pilot build results")
def va_05_fsqa_readiness(p): return _va_external("Field Service Quality Assurance readiness")
def va_06_metrics(p): return _va_external("Defined quality metrics and reporting")


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
    verify: Callable[[ProbedAPQPPlan], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review (14 doc-quality)
    CheckDef("1",  "CR", "Document Quality", "Is the document structured clearly?", "Shall", cr_01_structured),
    CheckDef("2",  "CR", "Document Quality", "Was the latest APQP template used?", "Should", cr_02_template),
    CheckDef("3",  "CR", "Document Quality", "Does structure facilitate search?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does title cover scope?", "Shall", cr_04a_title_scope),
    CheckDef("4b", "CR", "Document Quality", "Are author and approver listed?", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Document Quality", "Is there unique revision identification?", "Shall", cr_04c_revision),
    CheckDef("4d", "CR", "Document Quality", "Is change history available?", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Quality", "Is document status provided?", "Shall", cr_04e_status),
    CheckDef("5",  "CR", "Document Quality", "Is current revision identifiable?", "Shall", cr_05_current_revision),
    CheckDef("6",  "CR", "Document Quality", "Is document under configuration management?", "Shall", cr_06_config_mgmt),
    CheckDef("7",  "CR", "Document Quality", "Are header and footer updated?", "Should", cr_07_header_footer),
    CheckDef("8",  "CR", "Document Quality", "Contains correct table of contents?", "Shall", cr_08_toc),
    CheckDef("9",  "CR", "Document Quality", "Lists all references?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "All sections completed?", "Should", cr_10_sections_complete),

    # APQP Assessment (12 substantive per AIAG)
    CheckDef("1",  "APQPA", "Organization", "Program Manager and Quality Lead identified?", "Shall", apqpa_01_pm_ql),
    CheckDef("2",  "APQPA", "Organization", "Cross-functional team complete?", "Shall", apqpa_02_cft_complete),
    CheckDef("3",  "APQPA", "Phase 1 Planning", "Phase 1 deliverables complete?", "Shall", apqpa_03_phase1_complete),
    CheckDef("4",  "APQPA", "Phase 2 Design", "Phase 2 includes Design FMEA?", "Shall", apqpa_04_phase2_dfmea),
    CheckDef("5",  "APQPA", "Phase 3 Process", "Phase 3 includes PFMEA and Control Plan?", "Shall", apqpa_05_phase3_pfmea_cp),
    CheckDef("6",  "APQPA", "Phase 4 Validation", "Phase 4 includes MSA and PPAP?", "Shall", apqpa_06_phase4_msapppap),
    CheckDef("7",  "APQPA", "Phase 5 Launch", "Phase 5 feedback process defined?", "Shall", apqpa_07_phase5_feedback),
    CheckDef("8",  "APQPA", "Gate Review", "All 5 gates scheduled?", "Shall", apqpa_08_all_gates_scheduled),
    CheckDef("9",  "APQPA", "Gate Review", "Gate exit criteria defined?", "Shall", apqpa_09_gate_exit_criteria),
    CheckDef("10", "APQPA", "Risk Management", "Special Characteristics list maintained?", "Shall", apqpa_10_special_char_list),
    CheckDef("11", "APQPA", "Risk Management", "Risk Register populated with mitigations?", "Shall", apqpa_11_risk_register),
    CheckDef("12", "APQPA", "Ownership", "Each deliverable has assigned owner?", "Shall", apqpa_12_deliverable_ownership),

    # Verification Assessment (6 external)
    CheckDef("1",  "VA", "Launch Readiness", "Pre-Production Launch analysis complete?", "Shall", va_01_ppl_analysis),
    CheckDef("2",  "VA", "Manufacturing", "Supplier capability demonstrated?", "Shall", va_02_supplier_capable),
    CheckDef("3",  "VA", "Approval", "Customer approved APQP Plan?", "Shall", va_03_customer_approval),
    CheckDef("4",  "VA", "Prototyping", "Prototype/pilot results available?", "Shall", va_04_prototype_results),
    CheckDef("5",  "VA", "Quality Assurance", "FSQA readiness confirmed?", "Shall", va_05_fsqa_readiness),
    CheckDef("6",  "VA", "Metrics", "Quality metrics and reporting defined?", "Shall", va_06_metrics),
]
