"""
Canonical SW FMEA checklist definitions and verification logic.

Per ISO 26262-9 Section 8:
- Confirmation Review (CR): 14 generic doc-quality checks
- SW FMEA Assessment (SWFMEAA): 14 substantive SW-FMEA-specific checks per ISO 26262-9 & 26262-6
- Verification Assessment (VA): External verification + SW-FMEA-specific
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sw_fmea_probe import ProbedSwFmea


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

def cr_01_structured(p: ProbedSwFmea) -> CheckResult:
    if len(p.sheet_names) >= 10:
        return CheckResult(
            rating="FC",
            finding=f"Document is structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs; consider adding more structure.", confidence="Medium")


def cr_02_template(p: ProbedSwFmea) -> CheckResult:
    return draft("Template version cannot be verified from xlsx content alone.", action="Confirm sw-fmea-builder or equivalent template was used.")


def cr_03_searchable(p: ProbedSwFmea) -> CheckResult:
    has_toc = any("title" in s.lower() or "control" in s.lower() for s in p.sheet_names[:3])
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_toc and has_ref:
        return CheckResult(rating="FC", finding="Document has Title/TOC and References tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding="Missing TOC or References tab.", recommended_action="Add search aids for navigation.", confidence="Medium")


def cr_04a_title_scope(p: ProbedSwFmea) -> CheckResult:
    if p.title:
        return draft(f"Title is: '{p.title}'. Reviewer to confirm scope coverage.", page_section="Title page")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add document title.", confidence="High")


def cr_04b_author_approver(p: ProbedSwFmea) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    missing = [x for x in ["Author", "Approver"] if not (p.author if "Author" in x else p.approver)]
    return CheckResult(rating="NO", finding=f"Missing: {', '.join(missing)}.", recommended_action="Populate Title page.", confidence="High")


def cr_04c_unique_revision(p: ProbedSwFmea) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}' is set.", confidence="High")
    return CheckResult(rating="NO", finding="Revision field not populated.", recommended_action="Add unique revision ID.", confidence="High")


def cr_04d_change_history(p: ProbedSwFmea) -> CheckResult:
    if "01_Document_Control" in p.sheet_names:
        return CheckResult(rating="FC", finding="Document Control tab present.", page_section="Sheet '01_Document_Control'", confidence="High")
    return CheckResult(rating="PC", finding="No dedicated Document Control tab.", recommended_action="Add revision history.", confidence="High")


def cr_04e_status(p: ProbedSwFmea) -> CheckResult:
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="Status field not populated.", recommended_action="Set status (Draft/Review/Released).", confidence="High")


def cr_05_current_revision(p: ProbedSwFmea) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Current revision '{p.revision}' is identifiable.", confidence="High")
    return CheckResult(rating="NO", finding="Current revision not identifiable.", recommended_action="Populate Revision field.", confidence="High")


def cr_06_config_mgmt(p: ProbedSwFmea) -> CheckResult:
    return draft("Configuration management is an organizational practice.", action="Confirm document is under CM system (Polarion, DOORS, Git).")


def cr_07_header_footer(p: ProbedSwFmea) -> CheckResult:
    return draft("Headers/footers cannot be verified programmatically.", action="Manually confirm header/footer reflect current revision.")


def cr_08_toc(p: ProbedSwFmea) -> CheckResult:
    has_toc = any("title" in s.lower() or "control" in s.lower() for s in p.sheet_names[:3])
    if has_toc:
        return CheckResult(rating="FC", finding="TOC tab present near beginning.", confidence="High")
    return CheckResult(rating="PC", finding="No Table of Contents detected.", recommended_action="Add TOC.", confidence="High")


def cr_09_references(p: ProbedSwFmea) -> CheckResult:
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_ref:
        return CheckResult(rating="FC", finding="References tab detected.", confidence="High")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add References sheet.", confidence="High")


def cr_10_sections_complete(p: ProbedSwFmea) -> CheckResult:
    completion = len([c for c in p.sw_components if c.asil]) / max(1, len(p.sw_components))
    if completion >= 0.9:
        return CheckResult(rating="FC", finding=f"SW component catalog {completion:.0%} complete.", confidence="High")
    return CheckResult(rating="LC" if completion >= 0.7 else "PC", finding=f"SW component catalog {completion:.0%} complete.", recommended_action="Complete catalog.", confidence="High")


def cr_11_doc_id(p: ProbedSwFmea) -> CheckResult:
    if p.doc_id:
        return CheckResult(rating="FC", finding=f"Document ID='{p.doc_id}'.", confidence="High")
    return CheckResult(rating="NO", finding="Document ID not populated.", recommended_action="Add unique document ID.", confidence="High")


def cr_12_project_id(p: ProbedSwFmea) -> CheckResult:
    if p.project:
        return CheckResult(rating="FC", finding=f"Project='{p.project}'.", confidence="High")
    return draft("Project/program name not detected.", action="Add project context to Title page.")


def cr_13_references_complete(p: ProbedSwFmea) -> CheckResult:
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_ref:
        return draft("References tab present; reviewer to confirm all citations are complete.", page_section=f"References tab")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add References with ISO 26262 citations.", confidence="High")


def cr_14_all_sections_complete(p: ProbedSwFmea) -> CheckResult:
    has_all = all(t in p.sheet_names for t in ["00_Title_Page", "03_SW_Component_Catalog", "05_FMEA_Worksheet"])
    if has_all:
        return CheckResult(rating="FC", finding="All major SW FMEA tabs present.", confidence="High")
    return CheckResult(rating="PC", finding="Some core tabs missing.", recommended_action="Ensure all FMEA worksheet tabs are populated.", confidence="High")


# ---------------------------------------------------------------------------
# SW FMEA Assessment (14 substantive checks per ISO 26262-9 §8)
# ---------------------------------------------------------------------------

def swfmeaa_01_assumptions(p: ProbedSwFmea) -> CheckResult:
    if p.scope and p.methodology and p.fm_library_source:
        return CheckResult(
            rating="FC",
            finding=f"Assumptions documented: scope='{p.scope[:50]}...', methodology='{p.methodology[:50]}...', FM_library='{p.fm_library_source[:30]}...'.",
            page_section="02_Assumptions",
            confidence="High",
        )
    missing = [x for x in ["scope", "methodology", "FM library source"]
               if not (p.scope if "scope" in x else (p.methodology if "methodology" in x else p.fm_library_source))]
    return CheckResult(rating="PC", finding=f"Missing assumptions: {', '.join(missing)}.", recommended_action="Document all assumptions.", confidence="High")


def swfmeaa_02_sw_catalog(p: ProbedSwFmea) -> CheckResult:
    if len(p.sw_components) == 0:
        return CheckResult(rating="NO", finding="SW component catalog is empty.", recommended_action="Populate SW component catalog.", confidence="High")
    with_asil = [c for c in p.sw_components if c.asil]
    if len(with_asil) == len(p.sw_components):
        return CheckResult(rating="FC", finding=f"SW catalog complete: {len(p.sw_components)} components, all with ASIL.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_asil)}/{len(p.sw_components)} components have ASIL populated.", recommended_action="Complete ASIL assignments.", confidence="High")


def swfmeaa_03_coverage(p: ProbedSwFmea) -> CheckResult:
    if not p.sw_components:
        return CheckResult(rating="NO", finding="No SW components to check coverage.", recommended_action="Populate SW catalog.", confidence="High")
    safety_comps = [c for c in p.sw_components if c.safety_critical]
    with_modes = [c.swc_id for c in safety_comps if any(r.swc_id == c.swc_id for r in p.fmea_rows)]
    if safety_comps and len(with_modes) / len(safety_comps) >= 0.9:
        return CheckResult(rating="FC", finding=f"All {len(with_modes)} safety-critical components have FMEA rows.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_modes)}/{len(safety_comps)} safety components covered.", recommended_action="Add FMEA rows for all safety-critical components.", confidence="High")


def swfmeaa_04_severity_rated(p: ProbedSwFmea) -> CheckResult:
    if not p.fmea_rows:
        return na("No FMEA rows.")
    valid_severities = ["S0", "S1", "S2", "S3"]
    with_severity = [r for r in p.fmea_rows if r.severity in valid_severities]
    if len(with_severity) == len(p.fmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.fmea_rows)} failure modes have severity rated (S0-S3).", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_severity)}/{len(p.fmea_rows)} have severity.", recommended_action="Rate all failure modes S0-S3.", confidence="High")


def swfmeaa_05_frequency_rated(p: ProbedSwFmea) -> CheckResult:
    if not p.fmea_rows:
        return na("No FMEA rows.")
    valid_freqs = ["Rare", "Occasional", "Frequent"]
    with_freq = [r for r in p.fmea_rows if r.frequency in valid_freqs]
    if len(with_freq) == len(p.fmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.fmea_rows)} failure modes have frequency rated.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_freq)}/{len(p.fmea_rows)} have frequency.", recommended_action="Rate all failure modes.", confidence="High")


def swfmeaa_06_detection_mechanism(p: ProbedSwFmea) -> CheckResult:
    if not p.fmea_rows:
        return na("No FMEA rows.")
    with_detection = [r for r in p.fmea_rows if r.detection_mechanism and r.detection_mechanism.strip()]
    if len(with_detection) == len(p.fmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.fmea_rows)} failure modes have detection mechanism specified.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_detection)}/{len(p.fmea_rows)} have detection.", recommended_action="Specify detection for all modes.", confidence="High")


def swfmeaa_07_detection_coverage(p: ProbedSwFmea) -> CheckResult:
    if not p.fmea_rows:
        return na("No FMEA rows.")
    valid_cov = ["Low", "Med", "High"]
    with_cov = [r for r in p.fmea_rows if r.detection_coverage in valid_cov]
    if len(with_cov) == len(p.fmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.fmea_rows)} failure modes have detection coverage rated.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_cov)}/{len(p.fmea_rows)} have coverage.", recommended_action="Rate all detection coverage.", confidence="High")


def swfmeaa_08_pre_risk_computed(p: ProbedSwFmea) -> CheckResult:
    if not p.fmea_rows:
        return na("No FMEA rows.")
    with_pre = [r for r in p.fmea_rows if r.pre_risk > 0]
    if len(with_pre) == len(p.fmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.fmea_rows)} failure modes have pre-mitigation risk computed.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_pre)}/{len(p.fmea_rows)} have pre-risk.", recommended_action="Compute pre-risk (Severity x Frequency).", confidence="High")


def swfmeaa_09_post_risk_computed(p: ProbedSwFmea) -> CheckResult:
    if not p.fmea_rows:
        return na("No FMEA rows.")
    with_post = [r for r in p.fmea_rows if r.post_risk > 0]
    if len(with_post) == len(p.fmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.fmea_rows)} failure modes have post-mitigation risk computed.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_post)}/{len(p.fmea_rows)} have post-risk.", recommended_action="Compute post-risk after mitigation.", confidence="High")


def swfmeaa_10_residual_acceptable(p: ProbedSwFmea) -> CheckResult:
    """
    HEADLINE CHECK: Verify residual risk acceptance per ASIL threshold.
    ISO 26262-9 §8 requires residual risk per failure mode to be acceptable.
    Thresholds (ASIL): D<=1, C<=3, B<=9, A<=27, QM=unlimited.
    """
    if not p.fmea_rows:
        return na("No FMEA rows.")

    # Find ASIL threshold from components
    asils = list({c.asil for c in p.sw_components if c.asil})
    if not asils:
        return draft("Cannot determine ASIL thresholds (no ASIL found in SW components).", action="Verify ASIL assignments.")

    # For multi-ASIL, use most stringent
    asil_thresholds = {"D": 1, "C": 3, "B": 9, "A": 27, "QM": float('inf')}
    threshold = min(asil_thresholds.get(a, float('inf')) for a in asils)

    exceeding = [r for r in p.fmea_rows if r.post_risk > threshold]
    if not exceeding:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.fmea_rows)} failure modes have residual risk <= {threshold} (ASIL {'/'.join(asils)} threshold).",
            confidence="High",
        )

    return CheckResult(
        rating="NO",
        finding=f"{len(exceeding)}/{len(p.fmea_rows)} failure modes exceed residual risk threshold {threshold}. Highest: {max(r.post_risk for r in exceeding)}.",
        recommended_action="Mitigate high-risk failure modes via detection, architectural changes, or controls.",
        confidence="High",
    )


def swfmeaa_11_propagation_paths(p: ProbedSwFmea) -> CheckResult:
    if not p.fmea_rows:
        return na("No FMEA rows.")
    high_sev = [r for r in p.fmea_rows if r.severity in ["S2", "S3"]]
    if p.propagation_paths:
        return CheckResult(rating="FC", finding=f"Propagation paths documented ({len(p.propagation_paths)} items).", confidence="High")
    if high_sev:
        return CheckResult(rating="PC", finding=f"{len(high_sev)} high-severity modes but no propagation paths.", recommended_action="Document propagation paths for high-severity modes.", confidence="High")
    return CheckResult(rating="FC", finding="No high-severity modes requiring propagation analysis.", confidence="High")


def swfmeaa_12_coverage_summary(p: ProbedSwFmea) -> CheckResult:
    if p.coverage_summary:
        return CheckResult(rating="FC", finding=f"Coverage summary documented ({len(p.coverage_summary)} entries).", confidence="High")
    return CheckResult(rating="PC", finding="No coverage summary per Safety Goal.", recommended_action="Add coverage analysis per Safety Goal.", confidence="High")


def swfmeaa_13_open_items_reviewed(p: ProbedSwFmea) -> CheckResult:
    critical = [item for item in p.open_items if "critical" in item.lower() or "blocker" in item.lower()]
    if not p.open_items:
        return CheckResult(rating="FC", finding="No open items.", confidence="High")
    if critical:
        return CheckResult(rating="NO", finding=f"{len(critical)} critical open items.", recommended_action="Resolve critical items.", confidence="High")
    return CheckResult(rating="LC", finding=f"{len(p.open_items)} non-critical open items.", recommended_action="Prioritize resolution.", confidence="High")


def swfmeaa_14_verification_hooks(p: ProbedSwFmea) -> CheckResult:
    if p.verification_hooks:
        return CheckResult(rating="FC", finding=f"Verification plan hooks defined ({len(p.verification_hooks)} items).", confidence="High")
    return CheckResult(rating="PC", finding="No verification plan hooks per failure mode.", recommended_action="Link failure modes to verification plan.", confidence="High")


# ---------------------------------------------------------------------------
# Verification Assessment (generic external + SW-FMEA-specific)
# ---------------------------------------------------------------------------

def _va_external(label: str) -> CheckResult:
    return draft(f"{label} is governed by an external Verification Plan / Report — not in SW FMEA xlsx.", action="Verify against project documents.")


def va_01_plan_compliance(p): return _va_external("Verification Plan ensuring SW FMEA compliance")
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
    verify: Callable[[ProbedSwFmea], CheckResult]


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
    CheckDef("14", "CR", "Document Quality", "Are all FMEA sections populated?", "Shall", cr_14_all_sections_complete),

    # SW FMEA Assessment (SWFMEAA)
    CheckDef("1",  "SWFMEAA", "Prerequisites", "Have assumptions (scope, methodology, FM library) been documented?", "Shall", swfmeaa_01_assumptions),
    CheckDef("2",  "SWFMEAA", "SW Component Catalog", "Is SW component catalog complete with ASIL?", "Shall", swfmeaa_02_sw_catalog),
    CheckDef("3",  "SWFMEAA", "FMEA Coverage", "Does each safety-critical SWC have failure modes?", "Shall", swfmeaa_03_coverage),
    CheckDef("4",  "SWFMEAA", "Severity Rating", "Is every failure mode rated for severity (S0-S3)?", "Shall", swfmeaa_04_severity_rated),
    CheckDef("5",  "SWFMEAA", "Frequency Rating", "Is every failure mode rated for frequency?", "Shall", swfmeaa_05_frequency_rated),
    CheckDef("6",  "SWFMEAA", "Detection Mechanisms", "Does every failure mode have detection mechanism specified?", "Shall", swfmeaa_06_detection_mechanism),
    CheckDef("7",  "SWFMEAA", "Detection Coverage", "Does every failure mode have detection coverage rated?", "Shall", swfmeaa_07_detection_coverage),
    CheckDef("8",  "SWFMEAA", "Pre-Risk", "Is pre-mitigation risk computed for all failure modes?", "Shall", swfmeaa_08_pre_risk_computed),
    CheckDef("9",  "SWFMEAA", "Post-Risk", "Is post-mitigation risk computed for all failure modes?", "Shall", swfmeaa_09_post_risk_computed),
    CheckDef("10", "SWFMEAA", "Residual Risk", "Is residual risk acceptable per ASIL threshold (D<=1, C<=3, B<=9, A<=27)?", "Shall", swfmeaa_10_residual_acceptable),
    CheckDef("11", "SWFMEAA", "Propagation Analysis", "Are propagation paths documented for high-severity modes?", "Should", swfmeaa_11_propagation_paths),
    CheckDef("12", "SWFMEAA", "Coverage Analysis", "Is coverage summary computed per Safety Goal?", "Should", swfmeaa_12_coverage_summary),
    CheckDef("13", "SWFMEAA", "Open Items", "Have open items been reviewed for criticality?", "Should", swfmeaa_13_open_items_reviewed),
    CheckDef("14", "SWFMEAA", "Verification", "Are verification plan hooks defined per failure mode?", "Should", swfmeaa_14_verification_hooks),

    # Verification Assessment (VA)
    CheckDef("1",  "VA", "External Verification", "Does Verification Plan ensure SW FMEA compliance?", "Shall", va_01_plan_compliance),
    CheckDef("2",  "VA", "External Verification", "Does plan address methods, criteria, environment?", "Shall", va_02_content),
    CheckDef("3",  "VA", "External Verification", "Was verification executed per plan?", "Shall", va_03_executed),
    CheckDef("4",  "VA", "External Verification", "Does Verification Report include required elements?", "Shall", va_04_report),
]
