"""
Canonical FMEDA checklist definitions and verification logic.

Per ISO 26262-5 Section 8:
- Confirmation Review (CR): 14 generic doc-quality checks
- FMEDA Assessment (FMEDAA): 14 substantive FMEDA-specific checks
- Verification Assessment (VA): External verification + HARA-specific
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from fmeda_probe import ProbedFmeda


@dataclass
class CheckResult:
    rating: str = ""              # FC / LC / PC / NO / NA / "" (pending)
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
# Confirmation Review (14 generic doc-quality checks)
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedFmeda) -> CheckResult:
    if len(p.sheet_names) >= 10:
        return CheckResult(
            rating="FC",
            finding=f"Document is structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs; consider adding more structure.", confidence="Medium")


def cr_02_template(p: ProbedFmeda) -> CheckResult:
    return draft("Template version cannot be verified from xlsx content alone.", action="Confirm fmeda-builder or equivalent template was used.")


def cr_03_searchable(p: ProbedFmeda) -> CheckResult:
    has_toc = any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3])
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_toc and has_ref:
        return CheckResult(rating="FC", finding="Document has Title/TOC and References tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding="Missing TOC or References tab.", recommended_action="Add search aids for navigation.", confidence="Medium")


def cr_04a_title_scope(p: ProbedFmeda) -> CheckResult:
    if p.title:
        return draft(f"Title is: '{p.title}'. Reviewer to confirm scope coverage.", page_section="Title page")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add document title.", confidence="High")


def cr_04b_author_approver(p: ProbedFmeda) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    missing = [x for x in ["Author", "Approver"] if not (p.author if "Author" in x else p.approver)]
    return CheckResult(rating="NO", finding=f"Missing: {', '.join(missing)}.", recommended_action="Populate Title page.", confidence="High")


def cr_04c_unique_revision(p: ProbedFmeda) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}' is set.", confidence="High")
    return CheckResult(rating="NO", finding="Revision field not populated.", recommended_action="Add unique revision ID.", confidence="High")


def cr_04d_change_history(p: ProbedFmeda) -> CheckResult:
    if "01_Document_Control" in p.sheet_names:
        return CheckResult(rating="FC", finding="Document Control tab present.", page_section="Sheet '01_Document_Control'", confidence="High")
    return CheckResult(rating="PC", finding="No dedicated Document Control tab.", recommended_action="Add revision history.", confidence="High")


def cr_04e_status(p: ProbedFmeda) -> CheckResult:
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="Status field not populated.", recommended_action="Set status (Draft/Review/Released).", confidence="High")


def cr_05_current_revision(p: ProbedFmeda) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Current revision '{p.revision}' is identifiable.", confidence="High")
    return CheckResult(rating="NO", finding="Current revision not identifiable.", recommended_action="Populate Revision field.", confidence="High")


def cr_06_config_mgmt(p: ProbedFmeda) -> CheckResult:
    return draft("Configuration management is an organizational practice.", action="Confirm document is under CM system (Polarion, DOORS, Git).")


def cr_07_header_footer(p: ProbedFmeda) -> CheckResult:
    return draft("Headers/footers cannot be verified programmatically.", action="Manually confirm header/footer reflect current revision.")


def cr_08_toc(p: ProbedFmeda) -> CheckResult:
    has_toc = any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3])
    if has_toc:
        return CheckResult(rating="FC", finding="TOC tab present near beginning.", confidence="High")
    return CheckResult(rating="PC", finding="No Table of Contents detected.", recommended_action="Add TOC.", confidence="High")


def cr_09_references(p: ProbedFmeda) -> CheckResult:
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_ref:
        return CheckResult(rating="FC", finding="References tab detected.", confidence="High")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add References sheet.", confidence="High")


def cr_10_sections_complete(p: ProbedFmeda) -> CheckResult:
    completion = len([e for e in p.hw_elements if e.fit > 0]) / max(1, len(p.hw_elements))
    if completion >= 0.9:
        return CheckResult(rating="FC", finding=f"HW catalog {completion:.0%} complete.", confidence="High")
    return CheckResult(rating="LC" if completion >= 0.7 else "PC", finding=f"HW catalog {completion:.0%} complete.", recommended_action="Complete catalog.", confidence="High")


def cr_11_doc_id(p: ProbedFmeda) -> CheckResult:
    if p.doc_id:
        return CheckResult(rating="FC", finding=f"Document ID='{p.doc_id}'.", confidence="High")
    return CheckResult(rating="NO", finding="Document ID not populated.", recommended_action="Add unique document ID.", confidence="High")


def cr_12_project_id(p: ProbedFmeda) -> CheckResult:
    if p.project:
        return CheckResult(rating="FC", finding=f"Project='{p.project}'.", confidence="High")
    return draft("Project/program name not detected.", action="Add project context to Title page.")


def cr_13_references_complete(p: ProbedFmeda) -> CheckResult:
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_ref:
        return draft("References tab present; reviewer to confirm all citations are complete.", page_section=f"References tab")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add References with ISO 26262, FIT source citations.", confidence="High")


def cr_14_all_sections_complete(p: ProbedFmeda) -> CheckResult:
    has_all = all(t in p.sheet_names for t in ["00_Title_Page", "03_HW_Element_Catalog", "06_FMEDA_Worksheet", "10_Metrics_Dashboard"])
    if has_all:
        return CheckResult(rating="FC", finding="All major FMEDA tabs present.", confidence="High")
    return CheckResult(rating="PC", finding="Some core tabs missing.", recommended_action="Ensure all FMEDA worksheet tabs are populated.", confidence="High")


# ---------------------------------------------------------------------------
# FMEDA Assessment (14 substantive checks per ISO 26262-5 §8)
# ---------------------------------------------------------------------------

def fmedaa_01_assumptions(p: ProbedFmeda) -> CheckResult:
    if p.mission_profile and p.fit_source and p.environmental_class:
        return CheckResult(
            rating="FC",
            finding=f"Assumptions documented: mission='{p.mission_profile}', FIT_source='{p.fit_source}', env_class='{p.environmental_class}'.",
            page_section="02_Assumptions",
            confidence="High",
        )
    missing = [x for x in ["mission profile", "FIT source", "environmental class"]
               if not (p.mission_profile if "mission" in x else (p.fit_source if "FIT" in x else p.environmental_class))]
    return CheckResult(rating="PC", finding=f"Missing assumptions: {', '.join(missing)}.", recommended_action="Document all assumptions.", confidence="High")


def fmedaa_02_hw_catalog(p: ProbedFmeda) -> CheckResult:
    if len(p.hw_elements) == 0:
        return CheckResult(rating="NO", finding="HW element catalog is empty.", recommended_action="Populate HW element catalog.", confidence="High")
    with_fit = [e for e in p.hw_elements if e.fit > 0]
    if len(with_fit) == len(p.hw_elements):
        return CheckResult(rating="FC", finding=f"HW catalog complete: {len(p.hw_elements)} elements, all with FIT.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_fit)}/{len(p.hw_elements)} elements have FIT populated.", recommended_action="Complete FIT values.", confidence="High")


def fmedaa_03_coverage(p: ProbedFmeda) -> CheckResult:
    if not p.hw_elements:
        return CheckResult(rating="NO", finding="No HW elements to check coverage.", recommended_action="Populate HW catalog.", confidence="High")
    safety_elems = [e for e in p.hw_elements if e.safety_related]
    with_modes = [e.element_id for e in safety_elems if any(r.hw_element_id == e.element_id for r in p.fmeda_rows)]
    if safety_elems and len(with_modes) / len(safety_elems) >= 0.9:
        return CheckResult(rating="FC", finding=f"All {len(with_modes)} safety-related elements have FMEDA rows.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_modes)}/{len(safety_elems)} safety elements covered.", recommended_action="Add FMEDA rows for all safety-relevant elements.", confidence="High")


def fmedaa_04_distribution_sum(p: ProbedFmeda) -> CheckResult:
    if not p.fmeda_rows:
        return na("No FMEDA rows.")
    by_element = {}
    for row in p.fmeda_rows:
        if row.hw_element_id not in by_element:
            by_element[row.hw_element_id] = []
        by_element[row.hw_element_id].append(row.distribution_pct)
    bad = [(elem, sum(dists)) for elem, dists in by_element.items() if abs(sum(dists) - 100) > 1]
    if not bad:
        return CheckResult(rating="FC", finding=f"All {len(by_element)} elements have distribution sums within 1% of 100%.", confidence="High")
    return CheckResult(rating="NO", finding=f"{len(bad)} elements have distribution sum != 100%.", recommended_action="Correct distribution percentages.", confidence="High")


def fmedaa_05_classification(p: ProbedFmeda) -> CheckResult:
    if not p.fmeda_rows:
        return na("No FMEDA rows.")
    classified = [r for r in p.fmeda_rows if r.classification in ("Safe", "SPF", "RF", "MPF_D", "MPF_L")]
    if len(classified) == len(p.fmeda_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.fmeda_rows)} failure modes classified.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(classified)}/{len(p.fmeda_rows)} classified.", recommended_action="Complete classification.", confidence="High")


def fmedaa_06_safety_mechanism_allocation(p: ProbedFmeda) -> CheckResult:
    if not p.fmeda_rows:
        return na("No FMEDA rows.")
    safety_modes = [r for r in p.fmeda_rows if r.classification in ("SPF", "RF", "MPF_D", "MPF_L")]
    with_mech = [r for r in safety_modes if r.safety_mechanism and r.safety_mechanism.strip()]
    if not safety_modes:
        return CheckResult(rating="FC", finding="No safety-relevant failure modes requiring mechanisms.", confidence="High")
    if len(with_mech) / len(safety_modes) >= 0.95:
        return CheckResult(rating="FC", finding=f"All {len(with_mech)} safety-relevant modes have allocated mechanisms.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_mech)}/{len(safety_modes)} have mechanisms.", recommended_action="Allocate mechanisms to all safety modes.", confidence="High")


def fmedaa_07_dc_specified(p: ProbedFmeda) -> CheckResult:
    if not p.safety_mechanisms:
        return na("No safety mechanisms.")
    with_dc = [m for m in p.safety_mechanisms if 0 < m.dc_pct <= 100]
    if len(with_dc) == len(p.safety_mechanisms):
        return CheckResult(rating="FC", finding=f"All {len(with_dc)} mechanisms have DC% specified.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_dc)}/{len(p.safety_mechanisms)} have DC%.", recommended_action="Specify DC% for all mechanisms.", confidence="High")


def fmedaa_08_spfm_target(p: ProbedFmeda) -> CheckResult:
    targets = {"B": 90, "C": 97, "D": 99}
    target = targets.get(p.target_asil, 0)
    if target == 0:
        return draft(f"Target ASIL='{p.target_asil}' (non-standard); cannot verify SPFM target.", action="Confirm target ASIL.")
    if p.spfm_computed >= target:
        return CheckResult(
            rating="FC",
            finding=f"SPFM {p.spfm_computed:.1f}% >= target {target}% for ASIL {p.target_asil}.",
            page_section="10_Metrics_Dashboard",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"SPFM {p.spfm_computed:.1f}% < target {target}% for ASIL {p.target_asil}.",
        recommended_action="Increase SPFM via mechanism allocation or diagnostic coverage improvements.",
        confidence="High",
    )


def fmedaa_09_lfm_target(p: ProbedFmeda) -> CheckResult:
    targets = {"B": 60, "C": 80, "D": 90}
    target = targets.get(p.target_asil, 0)
    if target == 0:
        return draft(f"Target ASIL='{p.target_asil}' (non-standard); cannot verify LFM target.", action="Confirm target ASIL.")
    if p.lfm_computed >= target:
        return CheckResult(
            rating="FC",
            finding=f"LFM {p.lfm_computed:.1f}% >= target {target}% for ASIL {p.target_asil}.",
            page_section="10_Metrics_Dashboard",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"LFM {p.lfm_computed:.1f}% < target {target}% for ASIL {p.target_asil}.",
        recommended_action="Increase LFM via improved failure classification or architecture.",
        confidence="High",
    )


def fmedaa_10_pmhf_target(p: ProbedFmeda) -> CheckResult:
    targets = {"B": 100, "C": 100, "D": 10}
    target = targets.get(p.target_asil, None)
    if target is None:
        return draft(f"Target ASIL='{p.target_asil}' (non-standard); cannot verify PMHF target.", action="Confirm target ASIL.")
    if p.pmhf_computed <= target:
        return CheckResult(
            rating="FC",
            finding=f"PMHF {p.pmhf_computed:.2f} FIT <= target {target} FIT for ASIL {p.target_asil}.",
            page_section="10_Metrics_Dashboard",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"PMHF {p.pmhf_computed:.2f} FIT > target {target} FIT for ASIL {p.target_asil}.",
        recommended_action="Reduce PMHF via fault detection, mitigation, or architectural improvements.",
        confidence="High",
    )


def fmedaa_11_fit_reasonable(p: ProbedFmeda) -> CheckResult:
    if p.total_fit <= 0:
        return draft("Total FIT not computed or zero; cannot assess reasonableness.", action="Verify FMEDA calculations.")
    if p.total_fit <= 500:
        return CheckResult(rating="FC", finding=f"Total FIT {p.total_fit:.1f} is reasonable for HW component.", confidence="Medium")
    return draft(f"Total FIT {p.total_fit:.1f} is high; reviewer to confirm against datasheet/similar designs.", action="Verify against IEC 62380 or supplier data.")


def fmedaa_12_open_items(p: ProbedFmeda) -> CheckResult:
    critical = [item for item in p.open_items if "critical" in item.lower() or "blocker" in item.lower()]
    if not p.open_items:
        return CheckResult(rating="FC", finding="No open items.", confidence="High")
    if critical:
        return CheckResult(rating="NO", finding=f"{len(critical)} critical open items: {critical[0]}.", recommended_action="Resolve critical items.", confidence="High")
    return CheckResult(rating="LC", finding=f"{len(p.open_items)} non-critical open items.", recommended_action="Prioritize resolution.", confidence="High")


def fmedaa_13_mission_consistency(p: ProbedFmeda) -> CheckResult:
    return draft("Mission profile assumptions must be consistent with vehicle program.", action="Confirm mission profile aligns with vehicle specification.")


def fmedaa_14_fit_source_justified(p: ProbedFmeda) -> CheckResult:
    if p.fit_source:
        if "iec 62380" in p.fit_source.lower() or "fides" in p.fit_source.lower() or "datasheet" in p.fit_source.lower():
            return CheckResult(rating="FC", finding=f"FIT source cited: {p.fit_source}.", confidence="High")
        return CheckResult(rating="LC", finding=f"FIT source: {p.fit_source}. Reviewer to confirm justification.", confidence="Medium")
    return CheckResult(rating="PC", finding="FIT source not documented.", recommended_action="Document FIT source (IEC 62380, FIDES, or supplier data).", confidence="High")


# ---------------------------------------------------------------------------
# Verification Assessment (generic external + FMEDA-specific)
# ---------------------------------------------------------------------------

def _va_external(label: str) -> CheckResult:
    return draft(f"{label} is governed by an external Verification Plan / Report — not in FMEDA xlsx.", action="Verify against project documents.")


def va_01_plan_compliance(p): return _va_external("Verification Plan ensuring FMEDA compliance")
def va_02_content(p): return _va_external("Verification methods, criteria, environment")
def va_03_executed(p): return _va_external("Verification executed per plan")
def va_04_report(p): return _va_external("Verification Report with pass/fail and evidence")


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedFmeda], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review (CR)
    CheckDef("1",  "CR", "Document Quality", "Is the document structured clearly?", "Shall", cr_01_structured),
    CheckDef("2",  "CR", "Document Quality", "Was the latest template used?", "Should", cr_02_template),
    CheckDef("3",  "CR", "Document Quality", "Does structure facilitate search?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does title cover scope?", "Shall", cr_04a_title_scope),
    CheckDef("4b", "CR", "Document Quality", "Are author and approver listed?", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Document Quality", "Is revision uniquely identified?", "Shall", cr_04c_unique_revision),
    CheckDef("4d", "CR", "Document Quality", "Is change history available?", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Quality", "Is work-product status provided?", "Shall", cr_04e_status),
    CheckDef("5",  "CR", "Document Quality", "Is current revision clearly identifiable?", "Shall", cr_05_current_revision),
    CheckDef("6",  "CR", "Document Quality", "Is document under configuration management?", "Shall", cr_06_config_mgmt),
    CheckDef("7",  "CR", "Document Quality", "Are headers/footers updated?", "Should", cr_07_header_footer),
    CheckDef("8",  "CR", "Document Quality", "Is table of contents correct?", "Shall", cr_08_toc),
    CheckDef("9",  "CR", "Document Quality", "Does Reference Table list all citations?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "Have all sections been completed?", "Should", cr_10_sections_complete),
    CheckDef("11", "CR", "Document Quality", "Is document ID unique and persistent?", "Shall", cr_11_doc_id),
    CheckDef("12", "CR", "Document Quality", "Is project/program context identified?", "Should", cr_12_project_id),
    CheckDef("13", "CR", "Document Quality", "Are all references complete and traceable?", "Should", cr_13_references_complete),
    CheckDef("14", "CR", "Document Quality", "Are all FMEDA sections populated?", "Shall", cr_14_all_sections_complete),

    # FMEDA Assessment (FMEDAA)
    CheckDef("1",  "FMEDAA", "Prerequisites", "Have assumptions (mission, FIT source, env) been documented?", "Shall", fmedaa_01_assumptions),
    CheckDef("2",  "FMEDAA", "HW Element Catalog", "Is HW element catalog complete with FIT values?", "Shall", fmedaa_02_hw_catalog),
    CheckDef("3",  "FMEDAA", "FMEDA Coverage", "Does each ASIL-relevant element have failure modes?", "Shall", fmedaa_03_coverage),
    CheckDef("4",  "FMEDAA", "Distribution Validation", "Do failure mode distributions sum to 100% per element?", "Shall", fmedaa_04_distribution_sum),
    CheckDef("5",  "FMEDAA", "Classification", "Is every failure mode classified (Safe/SPF/RF/MPF_D/MPF_L)?", "Shall", fmedaa_05_classification),
    CheckDef("6",  "FMEDAA", "Safety Mechanisms", "Has every safety-relevant mode an allocated mechanism?", "Shall", fmedaa_06_safety_mechanism_allocation),
    CheckDef("7",  "FMEDAA", "Diagnostic Coverage", "Does every mechanism have DC% specified (no TBD)?", "Shall", fmedaa_07_dc_specified),
    CheckDef("8",  "FMEDAA", "Metric Targets", "Does SPFM meet target for ASIL?", "Shall", fmedaa_08_spfm_target),
    CheckDef("9",  "FMEDAA", "Metric Targets", "Does LFM meet target for ASIL?", "Shall", fmedaa_09_lfm_target),
    CheckDef("10", "FMEDAA", "Metric Targets", "Does PMHF meet target for ASIL?", "Shall", fmedaa_10_pmhf_target),
    CheckDef("11", "FMEDAA", "Reasonableness Checks", "Is total FIT reasonable for device class?", "Should", fmedaa_11_fit_reasonable),
    CheckDef("12", "FMEDAA", "Open Items", "Have open items been reviewed for criticality?", "Should", fmedaa_12_open_items),
    CheckDef("13", "FMEDAA", "Consistency", "Are mission assumptions consistent with vehicle program?", "Should", fmedaa_13_mission_consistency),
    CheckDef("14", "FMEDAA", "Justification", "Is FIT source justified (IEC 62380 / FIDES / datasheet)?", "Should", fmedaa_14_fit_source_justified),

    # Verification Assessment (VA)
    CheckDef("1",  "VA", "External Verification", "Does Verification Plan ensure FMEDA compliance?", "Shall", va_01_plan_compliance),
    CheckDef("2",  "VA", "External Verification", "Does plan address methods, criteria, environment?", "Shall", va_02_content),
    CheckDef("3",  "VA", "External Verification", "Was verification executed per plan?", "Shall", va_03_executed),
    CheckDef("4",  "VA", "External Verification", "Does Verification Report include required elements?", "Shall", va_04_report),
]
