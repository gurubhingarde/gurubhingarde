"""SOTIF Validation Strategy — 12 substantive checks per ISO 21448 §10 + 14 CR checks"""

from dataclasses import dataclass
from typing import Callable
from sotif_validation_probe import ProbedValidationStrategy

@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""

def draft(finding: str, page_section: str = "", action: str = "(Reviewer to verify)") -> CheckResult:
    return CheckResult(rating="", finding="(Auto-suggest, requires reviewer judgment) " + finding, page_section=page_section, recommended_action=action, confidence="Low")

def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, page_section="", recommended_action="", confidence="High")

# Confirmation Review
def cr_01_structured(p: ProbedValidationStrategy) -> CheckResult:
    if len(p.sheet_names) >= 6:
        return CheckResult(rating="FC", finding=f"Structured into {len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Organize by validation method.", confidence="Medium")

def cr_02_title(p: ProbedValidationStrategy) -> CheckResult:
    if p.title:
        return draft(f"Title: '{p.title}'.")
    return CheckResult(rating="NO", finding="No title.", recommended_action="Add title.", confidence="High")

def cr_03_author(p: ProbedValidationStrategy) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    return CheckResult(rating="NO", finding="Missing Author or Approver.", recommended_action="Populate.", confidence="High")

def cr_04_revision(p: ProbedValidationStrategy) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="No revision.", recommended_action="Add.", confidence="High")

def cr_05_status(p: ProbedValidationStrategy) -> CheckResult:
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="No status.", recommended_action="Add.", confidence="High")

def cr_06_toc(p: ProbedValidationStrategy) -> CheckResult:
    if any("title" in s.lower() for s in p.sheet_names[:3]):
        return CheckResult(rating="FC", finding="TOC present.", confidence="Medium")
    return CheckResult(rating="PC", finding="No TOC.", recommended_action="Add.", confidence="Medium")

def cr_07_references(p: ProbedValidationStrategy) -> CheckResult:
    if any("reference" in s.lower() for s in p.sheet_names):
        return CheckResult(rating="FC", finding="References tab found.", confidence="Medium")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add.", confidence="Medium")

def cr_08_completion(p: ProbedValidationStrategy) -> CheckResult:
    completion = (p.validation_methods_count > 0 and 0.25 or 0) + (bool(p.real_world_mileage_target) and 0.25 or 0) + (p.simulation_library_cited and 0.25 or 0) + (p.proving_ground_tests > 0 and 0.25 or 0)
    if completion >= 0.8:
        return CheckResult(rating="FC", finding=f"Major sections populated ({completion:.0%}).", confidence="High")
    return CheckResult(rating="PC", finding=f"Completion ~{completion:.0%}.", recommended_action="Complete all methods.", confidence="High")

def cr_09_layout(p: ProbedValidationStrategy) -> CheckResult:
    return draft("Layout subjective.", action="Confirm readability.")

def cr_10_revision_history(p: ProbedValidationStrategy) -> CheckResult:
    if any("document" in s.lower() for s in p.sheet_names):
        return CheckResult(rating="FC", finding="Document Control found.", confidence="Medium")
    return CheckResult(rating="PC", finding="No Document Control.", recommended_action="Add.", confidence="Medium")

def cr_11_acronyms(p: ProbedValidationStrategy) -> CheckResult:
    return draft("Acronym list not detectable.", action="Confirm glossary present.")

def cr_12_traceability(p: ProbedValidationStrategy) -> CheckResult:
    if p.acceptance_criteria_referenced:
        return CheckResult(rating="FC", finding="Acceptance criteria referenced.", confidence="Medium")
    return CheckResult(rating="PC", finding="Acceptance criteria not referenced.", recommended_action="Reference.", confidence="Medium")

def cr_13_toc_accuracy(p: ProbedValidationStrategy) -> CheckResult:
    return draft("TOC accuracy subjective.", action="Verify accuracy.")

def cr_14_headers(p: ProbedValidationStrategy) -> CheckResult:
    return draft("Header/footer not detectable.", action="Confirm updated.")

# Validation Strategy Assessment
def fsa_01_acceptance_criterion(p: ProbedValidationStrategy) -> CheckResult:
    if p.acceptance_criteria_referenced:
        return CheckResult(rating="FC", finding="Acceptance criterion referenced from SOTIF Analysis.", confidence="Medium")
    return CheckResult(rating="NO", finding="Acceptance criterion not referenced.", recommended_action="Reference from SOTIF Analysis.", confidence="High")

def fsa_02_methods(p: ProbedValidationStrategy) -> CheckResult:
    method_count = sum([bool(p.real_world_mileage_target), p.simulation_library_cited, p.proving_ground_tests > 0, p.field_monitoring_defined])
    if method_count >= 4:
        return CheckResult(rating="FC", finding=f"All validation methods covered (real-world, simulation, proving ground, field).", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {method_count}/4 validation methods covered.", recommended_action="Cover real-world, simulation, proving ground, and field monitoring.", confidence="High")

def fsa_03_real_world_mileage(p: ProbedValidationStrategy) -> CheckResult:
    if p.real_world_mileage_target:
        return CheckResult(rating="FC", finding=f"Real-world mileage target stated: {p.real_world_mileage_target}.", confidence="High")
    return CheckResult(rating="NO", finding="Real-world mileage target not stated.", recommended_action="State fleet mileage target.", confidence="High")

def fsa_04_fleet_coverage(p: ProbedValidationStrategy) -> CheckResult:
    if p.fleet_coverage_defined:
        return CheckResult(rating="FC", finding="Geographic, weather, and temporal distribution defined for fleet.", confidence="High")
    return CheckResult(rating="PC", finding="Fleet coverage distribution not fully defined.", recommended_action="Define geographic, weather, and time-of-day distribution.", confidence="High")

def fsa_05_simulation_library(p: ProbedValidationStrategy) -> CheckResult:
    if p.simulation_library_cited:
        return CheckResult(rating="FC", finding="Simulation scenario library cited (NHTSA/EuroNCAP/custom).", confidence="High")
    return CheckResult(rating="NO", finding="No simulation library cited.", recommended_action="Cite NHTSA, EuroNCAP, or custom library.", confidence="High")

def fsa_06_simulation_correlation(p: ProbedValidationStrategy) -> CheckResult:
    if p.simulation_correlation:
        return CheckResult(rating="FC", finding="Simulation correlation with real-world validated.", confidence="High")
    return CheckResult(rating="PC", finding="Simulation correlation not documented.", recommended_action="Document validation of sim vs. real-world.", confidence="High")

def fsa_07_proving_ground(p: ProbedValidationStrategy) -> CheckResult:
    if p.proving_ground_tests >= 10:
        return CheckResult(rating="FC", finding=f"{p.proving_ground_tests} proving ground test cases with pass/fail criteria.", confidence="High")
    return CheckResult(rating="PC" if p.proving_ground_tests > 0 else "NO", finding=f"Only {p.proving_ground_tests} test cases.", recommended_action="Expand proving ground test catalog.", confidence="High")

def fsa_08_field_monitoring(p: ProbedValidationStrategy) -> CheckResult:
    if p.field_monitoring_defined:
        return CheckResult(rating="FC", finding="Field monitoring telemetry plan defined.", confidence="High")
    return CheckResult(rating="NO", finding="No field monitoring plan.", recommended_action="Define telemetry, logging, and monitoring strategy.", confidence="High")

def fsa_09_acceptance_tracking(p: ProbedValidationStrategy) -> CheckResult:
    if p.acceptance_tracking_present:
        return CheckResult(rating="FC", finding="Acceptance criterion tracking shows current vs. target status.", confidence="High")
    return CheckResult(rating="PC", finding="Acceptance tracking not explicitly documented.", recommended_action="Add acceptance criterion tracking tab.", confidence="High")

def fsa_10_coverage_gaps(p: ProbedValidationStrategy) -> CheckResult:
    if p.coverage_gaps_noted:
        return CheckResult(rating="FC", finding="Coverage gaps explicitly noted.", confidence="High")
    return CheckResult(rating="PC", finding="Coverage gaps not explicitly documented.", recommended_action="Note and justify any coverage gaps.", confidence="High")

def fsa_11_statistical_significance(p: ProbedValidationStrategy) -> CheckResult:
    if p.statistical_significance:
        return CheckResult(rating="FC", finding="Statistical significance of validation evidence justified.", confidence="High")
    return CheckResult(rating="PC", finding="Statistical justification not documented.", recommended_action="Justify statistical confidence in validation results.", confidence="High")

def fsa_12_iso_references(p: ProbedValidationStrategy) -> CheckResult:
    if p.iso_21448_references >= 3:
        return CheckResult(rating="FC", finding=f"ISO 21448 §10-11 referenced {p.iso_21448_references} times.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.iso_21448_references} ISO 21448 references.", recommended_action="Reference ISO 21448 §10-11 throughout.", confidence="High")

@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedValidationStrategy], CheckResult]

CHECKS: list[CheckDef] = [
    CheckDef("1", "CR", "Document Quality", "Is the document clearly structured?", "Shall", cr_01_structured),
    CheckDef("2", "CR", "Document Quality", "Does the title cover scope?", "Shall", cr_02_title),
    CheckDef("3", "CR", "Document Quality", "Are author and approver listed?", "Shall", cr_03_author),
    CheckDef("4", "CR", "Document Quality", "Is there unique revision ID?", "Shall", cr_04_revision),
    CheckDef("5", "CR", "Document Quality", "Is status provided?", "Shall", cr_05_status),
    CheckDef("6", "CR", "Document Quality", "Is there a TOC?", "Shall", cr_06_toc),
    CheckDef("7", "CR", "Document Quality", "Are references complete?", "Should", cr_07_references),
    CheckDef("8", "CR", "Document Quality", "Have all sections been completed?", "Should", cr_08_completion),
    CheckDef("9", "CR", "Document Quality", "Is layout clear?", "Should", cr_09_layout),
    CheckDef("10", "CR", "Document Quality", "Is revision history documented?", "Shall", cr_10_revision_history),
    CheckDef("11", "CR", "Document Quality", "Is there a glossary?", "Should", cr_11_acronyms),
    CheckDef("12", "CR", "Document Quality", "Is acceptance criterion referenced?", "Shall", cr_12_traceability),
    CheckDef("13", "CR", "Document Quality", "Is TOC accurate?", "Shall", cr_13_toc_accuracy),
    CheckDef("14", "CR", "Document Quality", "Are header/footer updated?", "Should", cr_14_headers),

    CheckDef("1", "VSA", "Prerequisites", "Is acceptance criterion referenced from SOTIF Analysis?", "Shall", fsa_01_acceptance_criterion),
    CheckDef("2", "VSA", "Validation Methods", "Do validation methods cover real-world, simulation, proving ground, field?", "Shall", fsa_02_methods),
    CheckDef("3", "VSA", "Real-World Driving", "Is mileage target stated for real-world driving?", "Shall", fsa_03_real_world_mileage),
    CheckDef("4", "VSA", "Real-World Driving", "Is geographic, weather, temporal distribution defined for fleet?", "Shall", fsa_04_fleet_coverage),
    CheckDef("5", "VSA", "Simulation", "Is simulation scenario library cited (NHTSA/EuroNCAP/custom)?", "Shall", fsa_05_simulation_library),
    CheckDef("6", "VSA", "Simulation", "Is simulation correlation with real-world validated?", "Shall", fsa_06_simulation_correlation),
    CheckDef("7", "VSA", "Proving Ground", "Is proving ground test catalog with pass/fail criteria documented?", "Shall", fsa_07_proving_ground),
    CheckDef("8", "VSA", "Field Monitoring", "Is field monitoring telemetry plan defined?", "Shall", fsa_08_field_monitoring),
    CheckDef("9", "VSA", "Acceptance Tracking", "Is acceptance criterion tracking shown (current vs. target)?", "Shall", fsa_09_acceptance_tracking),
    CheckDef("10", "VSA", "Coverage Analysis", "Are coverage gaps explicitly noted?", "Shall", fsa_10_coverage_gaps),
    CheckDef("11", "VSA", "Statistical Justification", "Is statistical significance of validation evidence justified?", "Shall", fsa_11_statistical_significance),
    CheckDef("12", "VSA", "Standards", "Are ISO 21448 §10-11 referenced?", "Shall", fsa_12_iso_references),
]
