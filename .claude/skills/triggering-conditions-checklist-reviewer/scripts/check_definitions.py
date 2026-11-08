"""
Triggering Conditions checklist — 12 substantive checks per ISO 21448 Annex B + 14 CR checks.
"""

from dataclasses import dataclass
from typing import Callable
from triggering_conditions_probe import ProbedTriggeringConditions


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


# Confirmation Review (generic doc quality)
def cr_01_structured(p: ProbedTriggeringConditions) -> CheckResult:
    if len(p.sheet_names) >= 6:
        return CheckResult(rating="FC", finding=f"Structured into {len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Organize by triggering condition category.", confidence="Medium")


def cr_02_title(p: ProbedTriggeringConditions) -> CheckResult:
    if p.title:
        return draft(f"Title: '{p.title}'. Reviewer confirm scope.")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add document title.", confidence="High")


def cr_03_author(p: ProbedTriggeringConditions) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    return CheckResult(rating="NO", finding="Missing Author or Approver.", recommended_action="Populate Title page.", confidence="High")


def cr_04_revision(p: ProbedTriggeringConditions) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="No revision.", recommended_action="Add unique revision ID.", confidence="High")


def cr_05_status(p: ProbedTriggeringConditions) -> CheckResult:
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="No status.", recommended_action="Add Status field.", confidence="High")


def cr_06_toc(p: ProbedTriggeringConditions) -> CheckResult:
    if any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3]):
        return CheckResult(rating="FC", finding="TOC present.", confidence="Medium")
    return CheckResult(rating="PC", finding="No TOC.", recommended_action="Add TOC.", confidence="Medium")


def cr_07_references(p: ProbedTriggeringConditions) -> CheckResult:
    if any("reference" in s.lower() for s in p.sheet_names):
        return CheckResult(rating="FC", finding="References tab found.", confidence="Medium")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add References.", confidence="Medium")


def cr_08_completion(p: ProbedTriggeringConditions) -> CheckResult:
    env_ok = p.environmental_conditions_count >= 3
    sensor_ok = p.sensor_conditions_count >= 3
    road_ok = p.road_conditions_count >= 2
    system_ok = p.system_state_conditions_count >= 2
    driver_ok = p.driver_state_conditions_count >= 2
    score = sum([env_ok, sensor_ok, road_ok, system_ok, driver_ok]) / 5
    if score >= 0.8:
        return CheckResult(rating="FC", finding=f"Major sections populated ({score:.0%}).", confidence="High")
    return CheckResult(rating="PC", finding=f"Completion ~{score:.0%}.", recommended_action="Complete all categories.", confidence="High")


def cr_09_layout(p: ProbedTriggeringConditions) -> CheckResult:
    return draft("Layout clarity subjective.", action="Confirm readability and organization.")


def cr_10_revision_history(p: ProbedTriggeringConditions) -> CheckResult:
    doc_control = any("document" in s.lower() or "control" in s.lower() for s in p.sheet_names)
    if doc_control:
        return CheckResult(rating="FC", finding="Document Control tab found.", confidence="Medium")
    return CheckResult(rating="PC", finding="No Document Control tab.", recommended_action="Add revision history.", confidence="Medium")


def cr_11_acronyms(p: ProbedTriggeringConditions) -> CheckResult:
    return draft("Acronym list presence cannot be detected.", action="Confirm glossary present.")


def cr_12_traceability(p: ProbedTriggeringConditions) -> CheckResult:
    if p.sotif_analysis_referenced:
        return CheckResult(rating="FC", finding="SOTIF Analysis referenced.", confidence="Medium")
    return CheckResult(rating="PC", finding="SOTIF Analysis not explicitly referenced.", recommended_action="Add reference to SOTIF Analysis.", confidence="Medium")


def cr_13_toc_correctness(p: ProbedTriggeringConditions) -> CheckResult:
    return draft("TOC accuracy subjective.", action="Verify TOC accuracy against actual tabs.")


def cr_14_headers(p: ProbedTriggeringConditions) -> CheckResult:
    return draft("Header/footer formatting not detectable.", action="Confirm header/footer updated in Excel.")


# Triggering Conditions Assessment (SOTIF-specific)
def fsa_01_sotif_referenced(p: ProbedTriggeringConditions) -> CheckResult:
    if p.sotif_analysis_referenced:
        return CheckResult(rating="FC", finding="SOTIF Analysis referenced.", confidence="Medium")
    return CheckResult(rating="PC", finding="SOTIF Analysis not referenced.", recommended_action="Reference SOTIF Analysis with version.", confidence="Medium")


def fsa_02_environmental(p: ProbedTriggeringConditions) -> CheckResult:
    if p.environmental_conditions_count >= 5:
        return CheckResult(rating="FC", finding=f"{p.environmental_conditions_count} environmental conditions documented.", confidence="High")
    return CheckResult(rating="PC" if p.environmental_conditions_count >= 2 else "NO", finding=f"Only {p.environmental_conditions_count} environmental conditions.", recommended_action="Document weather, lighting, visibility, terrain, road conditions.", confidence="High")


def fsa_03_sensor(p: ProbedTriggeringConditions) -> CheckResult:
    if p.sensor_conditions_count >= 5:
        return CheckResult(rating="FC", finding=f"{p.sensor_conditions_count} sensor conditions documented.", confidence="High")
    return CheckResult(rating="PC" if p.sensor_conditions_count >= 2 else "NO", finding=f"Only {p.sensor_conditions_count} sensor conditions.", recommended_action="Document sensor degradation, noise, failure modes per sensor type.", confidence="High")


def fsa_04_road_infrastructure(p: ProbedTriggeringConditions) -> CheckResult:
    if p.road_conditions_count >= 3:
        return CheckResult(rating="FC", finding=f"{p.road_conditions_count} road infrastructure conditions documented.", confidence="High")
    return CheckResult(rating="PC" if p.road_conditions_count >= 1 else "NO", finding=f"Only {p.road_conditions_count} road infrastructure conditions.", recommended_action="Document lane markings, signs, surface, infrastructure state.", confidence="High")


def fsa_05_road_user(p: ProbedTriggeringConditions) -> CheckResult:
    if p.road_user_conditions_count >= 4:
        return CheckResult(rating="FC", finding=f"{p.road_user_conditions_count} road-user conditions documented.", confidence="High")
    return CheckResult(rating="PC" if p.road_user_conditions_count >= 1 else "NO", finding=f"Only {p.road_user_conditions_count} road-user conditions.", recommended_action="Document pedestrian, cyclist, vehicle behaviors.", confidence="High")


def fsa_06_system_state(p: ProbedTriggeringConditions) -> CheckResult:
    if p.system_state_conditions_count >= 4:
        return CheckResult(rating="FC", finding=f"{p.system_state_conditions_count} system-state conditions documented.", confidence="High")
    return CheckResult(rating="PC" if p.system_state_conditions_count >= 1 else "NO", finding=f"Only {p.system_state_conditions_count} system-state conditions.", recommended_action="Document ECU processing, latency, memory, resource constraints.", confidence="High")


def fsa_07_driver_state(p: ProbedTriggeringConditions) -> CheckResult:
    if p.driver_state_conditions_count >= 4:
        return CheckResult(rating="FC", finding=f"{p.driver_state_conditions_count} driver-state conditions documented.", confidence="High")
    return CheckResult(rating="PC" if p.driver_state_conditions_count >= 1 else "NO", finding=f"Only {p.driver_state_conditions_count} driver-state conditions.", recommended_action="Document attention, sobriety, skill, mode misuse.", confidence="High")


def fsa_08_combined_conditions(p: ProbedTriggeringConditions) -> CheckResult:
    if p.combined_conditions_count >= 5:
        method_text = f" ({p.combined_method})" if p.combined_method else ""
        return CheckResult(rating="FC", finding=f"{p.combined_conditions_count} combined conditions analyzed{method_text}.", confidence="High")
    if p.combined_conditions_count > 0:
        return CheckResult(rating="PC", finding=f"{p.combined_conditions_count} combined conditions. Coverage may be incomplete.", recommended_action="Analyze Cartesian or pairwise combinations per ISO 21448 Annex B.", confidence="High")
    return CheckResult(rating="NO", finding="No combined conditions analyzed.", recommended_action="Analyze interactions between single triggering conditions.", confidence="High")


def fsa_09_likelihood(p: ProbedTriggeringConditions) -> CheckResult:
    if p.likelihood_estimates >= p.environmental_conditions_count + p.sensor_conditions_count:
        return CheckResult(rating="FC", finding=f"{p.likelihood_estimates} likelihood estimates assigned.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.likelihood_estimates} likelihood estimates.", recommended_action="Assign likelihood (e.g., H/M/L or frequency) to each triggering condition.", confidence="High")


def fsa_10_detectability(p: ProbedTriggeringConditions) -> CheckResult:
    if p.detectability_estimates >= 5:
        return CheckResult(rating="FC", finding=f"{p.detectability_estimates} detectability estimates assigned.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.detectability_estimates} detectability estimates.", recommended_action="Assign detectability to each triggering condition.", confidence="High")


def fsa_11_mitigation_high_risk(p: ProbedTriggeringConditions) -> CheckResult:
    high_risk_count = max(p.high_risk_conditions, 1)  # At least check for high-risk items
    if p.mitigation_strategies >= high_risk_count:
        return CheckResult(rating="FC", finding=f"Mitigation strategy per high-likelihood/low-detectability condition: {p.mitigation_strategies} strategies.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.mitigation_strategies} mitigation strategies for {high_risk_count} high-risk conditions.", recommended_action="Define mitigation per high-risk triggering condition.", confidence="High")


def fsa_12_iso_references(p: ProbedTriggeringConditions) -> CheckResult:
    if p.annex_b_coverage and p.iso_21448_references >= 2:
        return CheckResult(rating="FC", finding="ISO 21448 Annex B referenced with methodology clarity.", confidence="High")
    if p.iso_21448_references >= 1:
        return CheckResult(rating="LC", finding="ISO 21448 referenced but Annex B coverage unclear.", recommended_action="Explicitly reference ISO 21448 Annex B for category definitions and analysis methodology.", confidence="Medium")
    return CheckResult(rating="NO", finding="No ISO 21448 references.", recommended_action="Reference ISO 21448 Part 1 Annex B throughout.", confidence="High")


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedTriggeringConditions], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review
    CheckDef("1", "CR", "Document Quality", "Is the document clearly structured by triggering condition category?", "Shall", cr_01_structured),
    CheckDef("2", "CR", "Document Quality", "Does the title cover the scope?", "Shall", cr_02_title),
    CheckDef("3", "CR", "Document Quality", "Are author and approver listed?", "Shall", cr_03_author),
    CheckDef("4", "CR", "Document Quality", "Is there a unique revision identification?", "Shall", cr_04_revision),
    CheckDef("5", "CR", "Document Quality", "Is the status provided?", "Shall", cr_05_status),
    CheckDef("6", "CR", "Document Quality", "Is there a table of contents?", "Shall", cr_06_toc),
    CheckDef("7", "CR", "Document Quality", "Are references complete?", "Should", cr_07_references),
    CheckDef("8", "CR", "Document Quality", "Have all sections been completed?", "Should", cr_08_completion),
    CheckDef("9", "CR", "Document Quality", "Is the layout clear and professional?", "Should", cr_09_layout),
    CheckDef("10", "CR", "Document Quality", "Is revision history documented?", "Shall", cr_10_revision_history),
    CheckDef("11", "CR", "Document Quality", "Is there a glossary or acronym list?", "Should", cr_11_acronyms),
    CheckDef("12", "CR", "Document Quality", "Is there traceability to SOTIF Analysis?", "Shall", cr_12_traceability),
    CheckDef("13", "CR", "Document Quality", "Is the TOC accurate?", "Shall", cr_13_toc_correctness),
    CheckDef("14", "CR", "Document Quality", "Are header/footer updated?", "Should", cr_14_headers),

    # Triggering Conditions Assessment
    CheckDef("1", "TCA", "Prerequisites", "Is the SOTIF Analysis referenced with version?", "Shall", fsa_01_sotif_referenced),
    CheckDef("2", "TCA", "Triggering Conditions", "Are environmental triggering conditions (weather, lighting, road surface) documented?", "Shall", fsa_02_environmental),
    CheckDef("3", "TCA", "Triggering Conditions", "Are sensor triggering conditions (degradation, noise, failure) documented per sensor type?", "Shall", fsa_03_sensor),
    CheckDef("4", "TCA", "Triggering Conditions", "Are road infrastructure triggering conditions documented?", "Shall", fsa_04_road_infrastructure),
    CheckDef("5", "TCA", "Triggering Conditions", "Are other road-user triggering conditions documented?", "Shall", fsa_05_road_user),
    CheckDef("6", "TCA", "Triggering Conditions", "Are system-state triggering conditions documented?", "Shall", fsa_06_system_state),
    CheckDef("7", "TCA", "Triggering Conditions", "Are driver-state triggering conditions documented?", "Shall", fsa_07_driver_state),
    CheckDef("8", "TCA", "Analysis", "Are combined triggering conditions analyzed (Cartesian or pairwise)?", "Shall", fsa_08_combined_conditions),
    CheckDef("9", "TCA", "Estimates", "Does each triggering condition have a likelihood estimate?", "Shall", fsa_09_likelihood),
    CheckDef("10", "TCA", "Estimates", "Does each triggering condition have a detectability estimate?", "Shall", fsa_10_detectability),
    CheckDef("11", "TCA", "Mitigation", "Is there a mitigation strategy per high-likelihood/low-detectability condition?", "Shall", fsa_11_mitigation_high_risk),
    CheckDef("12", "TCA", "Standards", "Are ISO 21448 Annex B definitions and methodologies referenced?", "Shall", fsa_12_iso_references),
]
