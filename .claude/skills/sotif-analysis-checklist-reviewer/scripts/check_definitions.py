"""
SOTIF Analysis checklist — 14 substantive checks per ISO 21448 §6 + 14 CR generic checks.
"""

from dataclasses import dataclass
from typing import Callable
from sotif_analysis_probe import ProbedSotifAnalysis


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


# Confirmation Review
def cr_01_structured(p: ProbedSotifAnalysis) -> CheckResult:
    if len(p.sheet_names) >= 7:
        return CheckResult(
            rating="FC",
            finding=f"Document structured into {len(p.sheet_names)} tabs.",
            confidence="Medium",
        )
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs; structure may lack clarity.", recommended_action="Add separate tabs for ODD, Performance, Insufficiencies, etc.", confidence="Medium")


def cr_02_template(p: ProbedSotifAnalysis) -> CheckResult:
    return draft("Template version cannot be detected from xlsx content alone.", action="Confirm latest SOTIF template used.")


def cr_03_searchable(p: ProbedSotifAnalysis) -> CheckResult:
    has_toc = any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3])
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_toc and has_ref:
        return CheckResult(rating="FC", finding="TOC and References tabs present.", confidence="Medium")
    return CheckResult(rating="PC", finding="Search aids incomplete.", recommended_action="Add TOC and References tabs.", confidence="Medium")


def cr_04_title_scope(p: ProbedSotifAnalysis) -> CheckResult:
    if p.title:
        return draft(f"Title: '{p.title}'. Reviewer confirm scope.", page_section="Title page")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add document title.", confidence="High")


def cr_05_author_approver(p: ProbedSotifAnalysis) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    return CheckResult(rating="NO", finding="Missing Author or Approver.", recommended_action="Populate Title page.", confidence="High")


def cr_06_revision(p: ProbedSotifAnalysis) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="No revision field.", recommended_action="Add unique revision identifier.", confidence="High")


def cr_07_status(p: ProbedSotifAnalysis) -> CheckResult:
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="No status field.", recommended_action="Add Status (Draft/Review/Released).", confidence="High")


def cr_08_toc(p: ProbedSotifAnalysis) -> CheckResult:
    if any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3]):
        return CheckResult(rating="FC", finding="TOC present.", confidence="Medium")
    return CheckResult(rating="PC", finding="No TOC detected.", recommended_action="Add TOC tab.", confidence="Medium")


def cr_09_references(p: ProbedSotifAnalysis) -> CheckResult:
    if any("reference" in s.lower() for s in p.sheet_names):
        return CheckResult(rating="FC", finding="References tab found.", confidence="Medium")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add References (ISO 21448, OEM standards).", confidence="Medium")


def cr_10_completion(p: ProbedSotifAnalysis) -> CheckResult:
    completion_score = (p.odd_defined and 0.3 or 0) + (p.performance_limitations_count > 0 and 0.2 or 0) + (p.functional_insufficiencies_count > 0 and 0.2 or 0) + (p.acceptance_criteria_count > 0 and 0.3 or 0)
    if completion_score >= 0.85:
        return CheckResult(rating="FC", finding="Major sections populated.", confidence="High")
    return CheckResult(rating="PC", finding=f"Completion ~{completion_score:.0%}.", recommended_action="Complete all major sections.", confidence="High")


def cr_11_layout(p: ProbedSotifAnalysis) -> CheckResult:
    return draft("Layout clarity subjective; review for readability.", action="Confirm headers, whitespace, and navigation aids.")


def cr_12_acronyms(p: ProbedSotifAnalysis) -> CheckResult:
    return draft("Acronym list presence cannot be detected programmatically.", action="Confirm glossary/acronym list present.")


def cr_13_revision_history(p: ProbedSotifAnalysis) -> CheckResult:
    doc_control = any("document" in s.lower() or "control" in s.lower() for s in p.sheet_names)
    if doc_control:
        return CheckResult(rating="FC", finding="Document Control tab found.", confidence="Medium")
    return CheckResult(rating="PC", finding="No Document Control/revision history tab.", recommended_action="Add revision history.", confidence="Medium")


def cr_14_traceability(p: ProbedSotifAnalysis) -> CheckResult:
    if p.item_def_referenced:
        return CheckResult(rating="FC", finding="Item Definition referenced.", confidence="Medium")
    return CheckResult(rating="PC", finding="Item Definition reference not clear.", recommended_action="Explicitly reference Item Definition version.", confidence="Medium")


# Functional Safety Assessment (SOTIF-specific)
def fsa_01_item_def(p: ProbedSotifAnalysis) -> CheckResult:
    if p.item_def_referenced:
        return CheckResult(
            rating="FC",
            finding="Item Definition referenced in document.",
            confidence="Medium",
        )
    return CheckResult(rating="PC", finding="Item Definition not referenced.", recommended_action="Add reference to Item Definition with version.", confidence="Medium")


def fsa_02_odd_defined(p: ProbedSotifAnalysis) -> CheckResult:
    if p.odd_defined and (p.odd_scenery_rows + p.odd_environment_rows + p.odd_dynamic_rows + p.odd_driver_state_rows) >= 4:
        return CheckResult(
            rating="FC",
            finding=f"ODD defined with scenery, environment, dynamics, driver state. Total categories covered: {len([x for x in [p.odd_scenery_rows, p.odd_environment_rows, p.odd_dynamic_rows, p.odd_driver_state_rows] if x > 0])}.",
            confidence="High",
        )
    return CheckResult(rating="NO", finding="ODD not adequately defined.", recommended_action="Document ODD across all 4 dimensions (scenery, environment, dynamics, driver state).", confidence="High")


def fsa_03_performance_spec(p: ProbedSotifAnalysis) -> CheckResult:
    if p.performance_limitations_count >= 3:
        return CheckResult(
            rating="FC",
            finding=f"{p.performance_limitations_count} performance limitations documented per function.",
            confidence="High",
        )
    return CheckResult(rating="PC", finding=f"Only {p.performance_limitations_count} performance limitations documented.", recommended_action="Document performance limitations per function per ISO 21448 §6.2.2.", confidence="High")


def fsa_04_performance_limits(p: ProbedSotifAnalysis) -> CheckResult:
    if p.performance_limitations_count > 0:
        return CheckResult(
            rating="FC",
            finding=f"Performance limitations enumerated: {p.performance_limitations_count} entries.",
            confidence="High",
        )
    return CheckResult(rating="NO", finding="No performance limitations enumerated.", recommended_action="Identify and list all performance limitations per function.", confidence="High")


def fsa_05_insufficiencies(p: ProbedSotifAnalysis) -> CheckResult:
    if p.functional_insufficiencies_count >= 2:
        return CheckResult(
            rating="FC",
            finding=f"{p.functional_insufficiencies_count} functional insufficiencies cataloged.",
            confidence="High",
        )
    return CheckResult(rating="PC", finding=f"Only {p.functional_insufficiencies_count} insufficiencies. Coverage may be incomplete.", recommended_action="Catalog all functional insufficiencies per ISO 21448 §6.2.3.", confidence="High")


def fsa_06_triggering_conditions(p: ProbedSotifAnalysis) -> CheckResult:
    if p.triggering_conditions_count >= 10:
        return CheckResult(
            rating="FC",
            finding=f"{p.triggering_conditions_count} triggering conditions documented.",
            confidence="High",
        )
    return CheckResult(rating="PC", finding=f"Only {p.triggering_conditions_count} triggering conditions. Coverage incomplete.", recommended_action="Document per insufficiency per ISO 21448 §6.2.4.", confidence="High")


def fsa_07_triggering_categories(p: ProbedSotifAnalysis) -> CheckResult:
    required = {"environmental", "sensor", "road", "system", "driver"}
    found = set(p.triggering_by_category.keys())
    if len(found & required) >= 4:
        return CheckResult(
            rating="FC",
            finding=f"Triggering condition categories covered: {', '.join(sorted(found & required))}.",
            confidence="High",
        )
    return CheckResult(rating="PC", finding=f"Only {len(found & required)} of 5 standard categories covered.", recommended_action="Cover environmental, sensor, road, system-state, driver-state categories.", confidence="High")


def fsa_08_hazardous_behaviors(p: ProbedSotifAnalysis) -> CheckResult:
    if p.hazardous_behaviors_count >= 5:
        return CheckResult(
            rating="FC",
            finding=f"{p.hazardous_behaviors_count} hazardous behaviors documented.",
            confidence="High",
        )
    return CheckResult(rating="PC", finding=f"Only {p.hazardous_behaviors_count} hazardous behaviors.", recommended_action="Document per (function × insufficiency × trigger).", confidence="High")


def fsa_09_scenario_quadrant(p: ProbedSotifAnalysis) -> CheckResult:
    if p.scenario_quadrant_classification:
        quad_count = len(p.scenario_quadrant_classification)
        unknown_unsafe = p.scenario_quadrant_classification.get("Unknown Unsafe", 0)
        return CheckResult(
            rating="FC" if quad_count == 4 else "LC",
            finding=f"Quadrant classification applied to {len(p.scenario_quadrant_classification)} scenario types. Unknown Unsafe: {unknown_unsafe}.",
            confidence="High",
        )
    return CheckResult(rating="NO", finding="Scenario quadrant classification not applied.", recommended_action="Classify scenarios as Known Safe / Known Unsafe / Unknown Safe / Unknown Unsafe.", confidence="High")


def fsa_10_acceptance_criterion(p: ProbedSotifAnalysis) -> CheckResult:
    if p.acceptance_criteria_count >= 3 and p.acceptance_measurable >= p.acceptance_criteria_count * 0.8:
        return CheckResult(
            rating="FC",
            finding=f"{p.acceptance_criteria_count} acceptance criteria; {p.acceptance_measurable} measurable.",
            confidence="High",
        )
    return CheckResult(rating="PC", finding=f"{p.acceptance_criteria_count} criteria; {p.acceptance_measurable} measurable.", recommended_action="Ensure all criteria are quantified per safety goal.", confidence="High")


def fsa_11_iso_21448(p: ProbedSotifAnalysis) -> CheckResult:
    if p.iso_21448_references >= 2:
        return CheckResult(
            rating="FC",
            finding=f"ISO 21448 referenced {p.iso_21448_references} times.",
            confidence="High",
        )
    return CheckResult(rating="PC", finding="Limited ISO 21448 citations.", recommended_action="Reference ISO 21448 Clause 6 throughout.", confidence="High")


def fsa_12_out_of_odd(p: ProbedSotifAnalysis) -> CheckResult:
    if p.out_of_odd_defined:
        return CheckResult(
            rating="FC",
            finding="Out-of-ODD behavior defined.",
            confidence="High",
        )
    return CheckResult(rating="PC", finding="Out-of-ODD behavior not explicitly documented.", recommended_action="Define behavior when ODD boundaries are crossed.", confidence="High")


def fsa_13_standards(p: ProbedSotifAnalysis) -> CheckResult:
    std_count = p.iso_21448_references + len(p.other_standards)
    if std_count >= 3:
        return CheckResult(
            rating="FC",
            finding=f"{std_count} applicable standards referenced.",
            confidence="Medium",
        )
    return CheckResult(rating="PC", finding=f"Only {std_count} standards referenced.", recommended_action="Reference ISO 21448, OEM requirements, applicable regulations.", confidence="Medium")


def fsa_14_unknown_unsafe(p: ProbedSotifAnalysis) -> CheckResult:
    unknown_unsafe_count = p.scenario_quadrant_classification.get("Unknown Unsafe", 0)
    if unknown_unsafe_count == 0:
        return CheckResult(rating="FC", finding="No Unknown Unsafe scenarios pending.", confidence="High")
    return CheckResult(
        rating="PC" if unknown_unsafe_count <= 3 else "NO",
        finding=f"{unknown_unsafe_count} Unknown Unsafe scenarios identified.",
        recommended_action="Evaluate mitigation or acceptance justification for each Unknown Unsafe scenario.",
        confidence="High",
    )


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedSotifAnalysis], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review
    CheckDef("1", "CR", "Document Quality", "Is the document structured in a clear manner supporting maintainability?", "Shall", cr_01_structured),
    CheckDef("2", "CR", "Document Quality", "Was the latest template used at document creation?", "Should", cr_02_template),
    CheckDef("3", "CR", "Document Quality", "Does the document facilitate search (TOC, index)?", "Should", cr_03_searchable),
    CheckDef("4", "CR", "Document Quality", "Does the title cover document scope?", "Shall", cr_04_title_scope),
    CheckDef("5", "CR", "Document Quality", "Are author and approver listed?", "Shall", cr_05_author_approver),
    CheckDef("6", "CR", "Document Quality", "Is there a unique revision identification?", "Shall", cr_06_revision),
    CheckDef("7", "CR", "Document Quality", "Is the status of the work product provided?", "Shall", cr_07_status),
    CheckDef("8", "CR", "Document Quality", "Does the document contain a table of contents?", "Shall", cr_08_toc),
    CheckDef("9", "CR", "Document Quality", "Does the Reference table list all references?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "Have all sections been completed?", "Should", cr_10_completion),
    CheckDef("11", "CR", "Document Quality", "Is the layout clear and professional?", "Should", cr_11_layout),
    CheckDef("12", "CR", "Document Quality", "Is there a glossary or acronym list?", "Should", cr_12_acronyms),
    CheckDef("13", "CR", "Document Quality", "Is revision history documented?", "Shall", cr_13_revision_history),
    CheckDef("14", "CR", "Document Quality", "Is there traceability to Item Definition?", "Shall", cr_14_traceability),

    # Functional Safety Assessment (SOTIF-specific)
    CheckDef("1", "FSA", "Item Definition and ODD", "Is the Item Definition referenced with version?", "Shall", fsa_01_item_def),
    CheckDef("2", "FSA", "Item Definition and ODD", "Is ODD defined across all four dimensions (scenery, environment, dynamics, driver state)?", "Shall", fsa_02_odd_defined),
    CheckDef("3", "FSA", "Performance and Insufficiencies", "Is functional performance specification documented per function?", "Shall", fsa_03_performance_spec),
    CheckDef("4", "FSA", "Performance and Insufficiencies", "Are performance limitations enumerated per function?", "Shall", fsa_04_performance_limits),
    CheckDef("5", "FSA", "Performance and Insufficiencies", "Are functional insufficiencies cataloged per function?", "Shall", fsa_05_insufficiencies),
    CheckDef("6", "FSA", "Triggering Conditions", "Are triggering conditions documented per insufficiency?", "Shall", fsa_06_triggering_conditions),
    CheckDef("7", "FSA", "Triggering Conditions", "Do triggering conditions cover standard categories (environmental, sensor, road, system, driver)?", "Shall", fsa_07_triggering_categories),
    CheckDef("8", "FSA", "Hazardous Behaviors", "Are hazardous behaviors documented per (function × insufficiency × trigger)?", "Shall", fsa_08_hazardous_behaviors),
    CheckDef("9", "FSA", "Scenario Classification", "Is scenario quadrant classification applied (Known Safe/Unsafe, Unknown Safe/Unsafe)?", "Shall", fsa_09_scenario_quadrant),
    CheckDef("10", "FSA", "Acceptance Criteria", "Is a quantified acceptance criterion stated per safety goal?", "Shall", fsa_10_acceptance_criterion),
    CheckDef("11", "FSA", "Standards and References", "Are ISO 21448 and applicable standards referenced?", "Shall", fsa_11_iso_21448),
    CheckDef("12", "FSA", "Out-of-ODD Behavior", "Is out-of-ODD behavior defined (what happens at ODD boundaries)?", "Shall", fsa_12_out_of_odd),
    CheckDef("13", "FSA", "Standards and References", "Are multiple applicable standards cited?", "Should", fsa_13_standards),
    CheckDef("14", "FSA", "Scenario Analysis", "Are Unknown Unsafe scenarios identified and pending mitigation?", "Shall", fsa_14_unknown_unsafe),
]
