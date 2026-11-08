"""
Control Plan Assessment checklist definitions.
Per AIAG Control Plan + IATF 16949.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from control_plan_probe import ProbedControlPlan


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


# ---------------------------------------------------------------------------
# Confirmation Review (14 doc-quality checks)
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedControlPlan) -> CheckResult:
    if len(p.sheet_names) >= 8:
        return CheckResult(
            rating="FC",
            finding=f"Document structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has only {len(p.sheet_names)} tabs.",
        recommended_action="Ensure all 12 standard tabs are present (Title, Document Control, Header Block, etc.)",
        confidence="High",
    )


def cr_02_template(p: ProbedControlPlan) -> CheckResult:
    if p.is_control_plan_builder_format:
        return CheckResult(
            rating="FC",
            finding="Control Plan follows AIAG standard tab structure.",
            confidence="High",
        )
    return draft("Confirm AIAG or OEM control plan template was used.")


def cr_03_searchable(p: ProbedControlPlan) -> CheckResult:
    if p.likely_title_sheet and p.sheet_names:
        return CheckResult(
            rating="FC",
            finding="Document begins with Title page; tab structure aids navigation.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Title tab or TOC not clearly present.",
        recommended_action="Add a Title page with document index.",
        confidence="High",
    )


def cr_04a_title_scope(p: ProbedControlPlan) -> CheckResult:
    if p.title:
        return draft(
            f"Title: '{p.title}'. Reviewer to confirm scope.",
            page_section="Title Page",
        )
    return CheckResult(
        rating="NO",
        finding="No title detected.",
        recommended_action="Add clear document title.",
        confidence="High",
    )


def cr_04b_contact_team(p: ProbedControlPlan) -> CheckResult:
    if p.key_contact and p.core_team:
        return CheckResult(
            rating="FC",
            finding=f"Key Contact and Core Team identified.",
            confidence="High",
        )
    missing = []
    if not p.key_contact: missing.append("Key Contact")
    if not p.core_team: missing.append("Core Team")
    return CheckResult(
        rating="NO",
        finding=f"Missing: {', '.join(missing)}",
        recommended_action=f"Populate {', '.join(missing)} in Header Block.",
        confidence="High",
    )


def cr_04c_approval(p: ProbedControlPlan) -> CheckResult:
    if p.customer_approval and p.supplier_approval:
        return CheckResult(
            rating="FC",
            finding="Customer and Supplier approvals documented.",
            confidence="High",
        )
    missing = []
    if not p.customer_approval: missing.append("Customer Approval")
    if not p.supplier_approval: missing.append("Supplier Approval")
    return CheckResult(
        rating="NO",
        finding=f"Missing: {', '.join(missing)}",
        recommended_action=f"Add {', '.join(missing)} sign-off dates.",
        confidence="High",
    )


def cr_05_plan_type(p: ProbedControlPlan) -> CheckResult:
    if p.plan_type:
        return CheckResult(
            rating="FC",
            finding=f"Plan Type specified: {p.plan_type}",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Plan Type not specified.",
        recommended_action="Specify whether this is Prototype, Pre-launch, or Production Control Plan.",
        confidence="High",
    )


def cr_06_revision_history(p: ProbedControlPlan) -> CheckResult:
    return draft("Confirm revision history is maintained in Document Control tab.", page_section="Document Control")


def cr_07_header_footer(p: ProbedControlPlan) -> CheckResult:
    return draft("Worksheet headers/footers should reflect current plan number and revision.", page_section="All worksheets")


def cr_08_references(p: ProbedControlPlan) -> CheckResult:
    return draft("References should cite PFMEA, procedures, and related documents.", page_section="References tab")


def cr_09_section_complete(p: ProbedControlPlan) -> CheckResult:
    if len(p.cp_worksheet_rows) > 0:
        return CheckResult(
            rating="FC",
            finding=f"Control Plan Worksheet populated with {len(p.cp_worksheet_rows)} characteristic rows.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Control Plan Worksheet is empty.",
        recommended_action="Populate the Control Plan Worksheet with at least one characteristic.",
        confidence="High",
    )


def cr_10_msa_plan(p: ProbedControlPlan) -> CheckResult:
    if len(p.msa_plans) > 0:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.msa_plans)} gages documented in MSA Plan.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="No MSA Plan entries found.",
        recommended_action="Add R&R targets for all measurement gages.",
        confidence="High",
    )


def cr_11_reaction_plan(p: ProbedControlPlan) -> CheckResult:
    if len(p.reaction_plans) > 0:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.reaction_plans)} Reaction Plans documented.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Reaction Plan Library not populated.",
        recommended_action="Document reaction plans for out-of-control conditions.",
        confidence="High",
    )


def cr_12_poka_yoke(p: ProbedControlPlan) -> CheckResult:
    if len(p.poka_yoke_catalog) > 0:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.poka_yoke_catalog)} mistake-proofing devices catalogued.",
            confidence="High",
        )
    return CheckResult(
        rating="LC",
        finding="No Poka-Yoke devices documented (may not be applicable to all processes).",
        recommended_action="Document any mistake-proofing or poka-yoke devices in use.",
        confidence="High",
    )


def cr_13_spc_doc(p: ProbedControlPlan) -> CheckResult:
    if len(p.spc_allocations) > 0:
        return CheckResult(
            rating="FC",
            finding=f"SPC method allocation documented for {len(p.spc_allocations)} characteristics.",
            confidence="High",
        )
    return CheckResult(
        rating="LC",
        finding="SPC Method Allocation not populated.",
        recommended_action="Document SPC control method for variable characteristics.",
        confidence="High",
    )


def cr_14_pfmea_linkage(p: ProbedControlPlan) -> CheckResult:
    return draft("Verify each high-AP PFMEA failure mode is addressed by a Control Plan characteristic.", page_section="Linkage to PFMEA")


# ---------------------------------------------------------------------------
# Control Plan Assessment (14 substantive checks per AIAG + IATF 16949)
# ---------------------------------------------------------------------------

def cpa_01_header_complete(p: ProbedControlPlan) -> CheckResult:
    fields = [p.control_plan_number, p.key_contact, p.core_team, p.customer_approval, p.supplier_approval]
    completed = sum(1 for f in fields if f)
    if completed >= 5:
        return CheckResult(
            rating="FC",
            finding="Header Block complete (plan number, contact, team, approvals).",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"Header Block incomplete ({completed}/5 fields).",
        recommended_action="Complete all Header Block fields.",
        confidence="High",
    )


def cpa_02_plan_type_specified(p: ProbedControlPlan) -> CheckResult:
    if p.plan_type and p.plan_type.lower() in ["prototype", "pre-launch", "production"]:
        return CheckResult(
            rating="FC",
            finding=f"Plan Type specified: {p.plan_type}",
            page_section="Header Block",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Plan Type not properly specified.",
        recommended_action="Specify Prototype, Pre-launch, or Production.",
        confidence="High",
    )


def cpa_03_process_steps(p: ProbedControlPlan) -> CheckResult:
    steps_populated = sum(1 for r in p.cp_worksheet_rows if r.process_step)
    if steps_populated == len(p.cp_worksheet_rows):
        return CheckResult(
            rating="FC",
            finding=f"All {steps_populated} rows have process step specified.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{steps_populated}/{len(p.cp_worksheet_rows)} rows have process step.",
        recommended_action="Specify process step for every characteristic.",
        confidence="High",
    )


def cpa_04_characteristics_defined(p: ProbedControlPlan) -> CheckResult:
    if not p.cp_worksheet_rows:
        return CheckResult(rating="NO", finding="No Control Plan rows.", recommended_action="Populate Control Plan Worksheet.")
    chars_with_spec = sum(1 for r in p.cp_worksheet_rows if r.spec_lower or r.spec_upper)
    if chars_with_spec == len(p.cp_worksheet_rows):
        return CheckResult(
            rating="FC",
            finding=f"All {chars_with_spec} characteristics have specification/tolerance.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{chars_with_spec}/{len(p.cp_worksheet_rows)} have spec/tolerance.",
        recommended_action="Specify upper and lower limits for every characteristic.",
        confidence="High",
    )


def cpa_05_measurement_technique(p: ProbedControlPlan) -> CheckResult:
    if not p.cp_worksheet_rows:
        return na("No Control Plan rows.")
    gages_defined = sum(1 for r in p.cp_worksheet_rows if r.gage)
    if gages_defined == len(p.cp_worksheet_rows):
        return CheckResult(
            rating="FC",
            finding=f"All {gages_defined} characteristics have measurement gage/technique.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{gages_defined}/{len(p.cp_worksheet_rows)} have gage defined.",
        recommended_action="Specify measurement gage/technique for every characteristic.",
        confidence="High",
    )


def cpa_06_sample_plan(p: ProbedControlPlan) -> CheckResult:
    if not p.cp_worksheet_rows:
        return na("No Control Plan rows.")
    sample_complete = sum(1 for r in p.cp_worksheet_rows if r.sample_size and r.sample_frequency)
    if sample_complete == len(p.cp_worksheet_rows):
        return CheckResult(
            rating="FC",
            finding=f"All characteristics have sample size and frequency.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{sample_complete}/{len(p.cp_worksheet_rows)} have sample plan.",
        recommended_action="Specify sample size and frequency.",
        confidence="High",
    )


def cpa_07_control_method(p: ProbedControlPlan) -> CheckResult:
    if not p.cp_worksheet_rows:
        return na("No Control Plan rows.")
    method_defined = sum(1 for r in p.cp_worksheet_rows if r.control_method)
    if method_defined == len(p.cp_worksheet_rows):
        return CheckResult(
            rating="FC",
            finding=f"All characteristics have control method (SPC/100%/poka-yoke/audit).",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{method_defined}/{len(p.cp_worksheet_rows)} have control method.",
        recommended_action="Specify control method for every characteristic.",
        confidence="High",
    )


def cpa_08_reaction_plan_ref(p: ProbedControlPlan) -> CheckResult:
    if not p.cp_worksheet_rows:
        return na("No Control Plan rows.")
    reaction_ref = sum(1 for r in p.cp_worksheet_rows if r.reaction_plan_id)
    if reaction_ref == len(p.cp_worksheet_rows):
        return CheckResult(
            rating="FC",
            finding=f"All characteristics reference a Reaction Plan.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{reaction_ref}/{len(p.cp_worksheet_rows)} reference Reaction Plan.",
        recommended_action="Link every characteristic to a Reaction Plan.",
        confidence="High",
    )


def cpa_09_special_characteristics(p: ProbedControlPlan) -> CheckResult:
    if len(p.special_characteristics) > 0:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.special_characteristics)} Special Characteristics echoed from PFMEA.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="No Special Characteristics sheet populated.",
        recommended_action="Echo Critical-to-Quality (CTQ) characteristics from PFMEA into Special Characteristics tab.",
        confidence="High",
    )


def cpa_10_msa_plan_complete(p: ProbedControlPlan) -> CheckResult:
    if not p.cp_worksheet_rows:
        return na("No Control Plan rows.")
    unique_gages = len(set(r.gage for r in p.cp_worksheet_rows if r.gage))
    msa_count = len(p.msa_plans)
    if msa_count >= unique_gages and all(m.r_and_r_target for m in p.msa_plans):
        return CheckResult(
            rating="FC",
            finding=f"MSA Plan exists for all {msa_count} gages with R&R targets.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"MSA Plan ({msa_count} gages) may be incomplete; R&R targets may be missing.",
        recommended_action="Ensure every gage has an MSA Plan with R&R study target.",
        confidence="High",
    )


def cpa_11_spc_allocation(p: ProbedControlPlan) -> CheckResult:
    if len(p.spc_allocations) > 0:
        return CheckResult(
            rating="FC",
            finding=f"SPC method allocation documented for {len(p.spc_allocations)} variable characteristics.",
            confidence="High",
        )
    return CheckResult(
        rating="LC",
        finding="SPC Method Allocation not populated.",
        recommended_action="Document SPC method (Xbar-R, Xbar-S, etc.) for variable characteristics.",
        confidence="High",
    )


def cpa_12_poka_yoke_verification(p: ProbedControlPlan) -> CheckResult:
    if len(p.poka_yoke_catalog) > 0:
        with_verify = sum(1 for py in p.poka_yoke_catalog if py.verification_method)
        if with_verify == len(p.poka_yoke_catalog):
            return CheckResult(
                rating="FC",
                finding=f"All {len(p.poka_yoke_catalog)} devices have verification method documented.",
                confidence="High",
            )
        return CheckResult(
            rating="PC",
            finding=f"{with_verify}/{len(p.poka_yoke_catalog)} devices have verification method.",
            recommended_action="Document verification method for every poka-yoke device.",
            confidence="High",
        )
    return CheckResult(rating="NA", finding="No Poka-Yoke devices in use.", confidence="High")


def cpa_13_reaction_plan_library(p: ProbedControlPlan) -> CheckResult:
    if not p.cp_worksheet_rows or not p.reaction_plans:
        return CheckResult(
            rating="PC",
            finding="Reaction Plan Library not fully populated.",
            recommended_action="Populate Reaction Plan Library with corrective actions for out-of-control conditions.",
            confidence="High",
        )
    # Check that referenced plans exist
    referenced_ids = set(r.reaction_plan_id for r in p.cp_worksheet_rows if r.reaction_plan_id)
    available_ids = set(rp.plan_id for rp in p.reaction_plans)
    if referenced_ids.issubset(available_ids):
        return CheckResult(
            rating="FC",
            finding=f"All referenced Reaction Plans ({len(available_ids)}) are documented.",
            confidence="High",
        )
    missing = referenced_ids - available_ids
    return CheckResult(
        rating="PC",
        finding=f"Reaction Plans referenced but not defined: {missing}",
        recommended_action="Define missing Reaction Plans in the library.",
        confidence="High",
    )


def cpa_14_pfmea_linkage(p: ProbedControlPlan) -> CheckResult:
    return draft("Verify each high-AP PFMEA failure mode has corresponding Control Plan row.", page_section="Linkage to PFMEA")


# ---------------------------------------------------------------------------
# Verification Assessment (3 generic + 5 Control-Plan-specific)
# ---------------------------------------------------------------------------

def va_completeness(p: ProbedControlPlan) -> CheckResult:
    return draft("Verify Verification Plan addresses testing of all characteristics against spec.", page_section="Verification Plan")


def va_methods(p: ProbedControlPlan) -> CheckResult:
    return draft("Confirm verification methods (testing, inspection, audit) are defined.", page_section="Verification Plan")


def va_results(p: ProbedControlPlan) -> CheckResult:
    return draft("Verify Verification Report documents pass/fail for each characteristic.", page_section="Verification Report")


def va_cp_01_control_effectiveness(p: ProbedControlPlan) -> CheckResult:
    return draft("Confirm control effectiveness (SPC performance, capability) is verified.", page_section="Verification Report")


def va_cp_02_gage_adequacy(p: ProbedControlPlan) -> CheckResult:
    if len(p.msa_plans) > 0:
        return CheckResult(
            rating="FC",
            finding=f"MSA Plan exists; gage adequacy should be verified by R&R study.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="No MSA Plan to verify gage adequacy.",
        recommended_action="Conduct measurement system study (GR&R) for each gage.",
        confidence="High",
    )


def va_cp_03_reaction_effectiveness(p: ProbedControlPlan) -> CheckResult:
    return draft("Verify Reaction Plans are tested and shown to be effective.", page_section="Verification Report")


def va_cp_04_special_char_control(p: ProbedControlPlan) -> CheckResult:
    if len(p.special_characteristics) > 0:
        return CheckResult(
            rating="FC",
            finding=f"Special Characteristics ({len(p.special_characteristics)}) controls should be independently verified.",
            confidence="High",
        )
    return CheckResult(rating="NA", finding="No Special Characteristics defined.", confidence="High")


def va_cp_05_poka_yoke_test(p: ProbedControlPlan) -> CheckResult:
    if len(p.poka_yoke_catalog) > 0:
        return CheckResult(
            rating="FC",
            finding=f"Poka-Yoke devices ({len(p.poka_yoke_catalog)}) should be functionally tested.",
            confidence="High",
        )
    return CheckResult(rating="NA", finding="No Poka-Yoke devices in use.", confidence="High")


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
    verify: Callable[[ProbedControlPlan], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review
    CheckDef("1", "CR", "Document Quality", "Is document structured with clear sections supporting maintainability?", "Shall", cr_01_structured),
    CheckDef("2", "CR", "Document Quality", "Was latest AIAG/OEM control plan template used?", "Should", cr_02_template),
    CheckDef("3", "CR", "Document Quality", "Does structure facilitate search (Title, TOC, References)?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does title cover the scope?", "Shall", cr_04a_title_scope),
    CheckDef("4b", "CR", "Document Quality", "Are Key Contact and Core Team listed?", "Shall", cr_04b_contact_team),
    CheckDef("4c", "CR", "Document Quality", "Are Customer and Supplier approvals documented?", "Shall", cr_04c_approval),
    CheckDef("5", "CR", "Document Quality", "Is Plan Type (Prototype/Pre-launch/Production) specified?", "Shall", cr_05_plan_type),
    CheckDef("6", "CR", "Document Quality", "Is revision history maintained?", "Should", cr_06_revision_history),
    CheckDef("7", "CR", "Document Quality", "Are headers/footers updated with current info?", "Should", cr_07_header_footer),
    CheckDef("8", "CR", "Document Quality", "Are references to PFMEA, procedures listed?", "Should", cr_08_references),
    CheckDef("9", "CR", "Document Quality", "Have all sections been completed?", "Should", cr_09_section_complete),
    CheckDef("10", "CR", "Document Quality", "Is MSA Plan tab populated?", "Should", cr_10_msa_plan),
    CheckDef("11", "CR", "Document Quality", "Is Reaction Plan Library tab populated?", "Should", cr_11_reaction_plan),
    CheckDef("12", "CR", "Document Quality", "Is Poka-Yoke Catalog populated where applicable?", "Should", cr_12_poka_yoke),
    CheckDef("13", "CR", "Document Quality", "Is SPC Method Allocation documented?", "Should", cr_13_spc_doc),
    CheckDef("14", "CR", "Document Quality", "Is there linkage to PFMEA failure modes?", "Should", cr_14_pfmea_linkage),

    # Control Plan Assessment
    CheckDef("1", "CPA", "Control Plan Header", "Is Header Block complete (number, contact, team, approvals, dates)?", "Shall", cpa_01_header_complete),
    CheckDef("2", "CPA", "Control Plan Header", "Is Plan Type specified (Prototype/Pre-launch/Production)?", "Shall", cpa_02_plan_type_specified),
    CheckDef("3", "CPA", "Worksheet Completeness", "Does each row link to a process step?", "Shall", cpa_03_process_steps),
    CheckDef("4", "CPA", "Worksheet Completeness", "Does each characteristic have spec/tolerance?", "Shall", cpa_04_characteristics_defined),
    CheckDef("5", "CPA", "Worksheet Completeness", "Does each characteristic have evaluation technique (gage)?", "Shall", cpa_05_measurement_technique),
    CheckDef("6", "CPA", "Worksheet Completeness", "Does each characteristic have sample size and frequency?", "Shall", cpa_06_sample_plan),
    CheckDef("7", "CPA", "Worksheet Completeness", "Does each characteristic have control method?", "Shall", cpa_07_control_method),
    CheckDef("8", "CPA", "Worksheet Completeness", "Does each characteristic reference a Reaction Plan?", "Shall", cpa_08_reaction_plan_ref),
    CheckDef("9", "CPA", "Special Characteristics", "Are Special Characteristics (CTQ) from PFMEA echoed with stricter controls?", "Shall", cpa_09_special_characteristics),
    CheckDef("10", "CPA", "Measurement System", "Does every gage have an MSA Plan with R&R target?", "Shall", cpa_10_msa_plan_complete),
    CheckDef("11", "CPA", "Statistical Control", "Is SPC method allocation documented for variable characteristics?", "Shall", cpa_11_spc_allocation),
    CheckDef("12", "CPA", "Mistake Proofing", "Do poka-yoke devices have verification method documented?", "Should", cpa_12_poka_yoke_verification),
    CheckDef("13", "CPA", "Reaction Plans", "Are all referenced Reaction Plans documented in the library?", "Shall", cpa_13_reaction_plan_library),
    CheckDef("14", "CPA", "PFMEA Linkage", "Does each high-AP PFMEA failure mode have Control Plan correspondence?", "Shall", cpa_14_pfmea_linkage),

    # Verification Assessment
    CheckDef("1", "VA", "Verification Planning", "Does Verification Plan address all characteristics?", "Shall", va_completeness),
    CheckDef("2", "VA", "Verification Planning", "Are verification methods (testing, inspection, audit) defined?", "Shall", va_methods),
    CheckDef("3", "VA", "Verification Results", "Does Verification Report document pass/fail for each characteristic?", "Shall", va_results),
    CheckDef("4", "VA", "Control Verification", "Is control effectiveness (SPC performance) verified?", "Should", va_cp_01_control_effectiveness),
    CheckDef("5", "VA", "Gage Adequacy", "Is gage adequacy verified by MSA/GR&R study?", "Shall", va_cp_02_gage_adequacy),
    CheckDef("6", "VA", "Reaction Plan Verification", "Are Reaction Plans tested and shown effective?", "Should", va_cp_03_reaction_effectiveness),
    CheckDef("7", "VA", "Special Characteristic Verification", "Are Special Characteristic controls independently verified?", "Should", va_cp_04_special_char_control),
    CheckDef("8", "VA", "Poka-Yoke Verification", "Are poka-yoke devices functionally tested?", "Should", va_cp_05_poka_yoke_test),
]
