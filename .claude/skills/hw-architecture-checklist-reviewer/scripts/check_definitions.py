"""
Canonical HW Architecture checklist definitions and verification logic.

Each check has:
- id: row id (CR/HWAA/VA tabs)
- tab: which output tab
- section: section header
- requirement: the requirement text
- obligation: "Shall" or "Should" (or "")
- verify: callable(probed: ProbedHwArch) -> CheckResult
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from hw_arch_probe import ProbedHwArch


@dataclass
class CheckResult:
    rating: str = ""  # FC / LC / PC / NO / NA / "" (pending)
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""  # High / Medium / Low / "" for binary CR


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
# Confirmation Review (generic doc-quality, 14 checks)
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedHwArch) -> CheckResult:
    if len(p.sheet_names) >= 11:
        return CheckResult(
            rating="FC",
            finding=f"Document is structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has only {len(p.sheet_names)} tabs; expect 11+ for HW arch.",
        recommended_action="Verify all required tabs are present.",
        confidence="Medium",
    )


def cr_02_title_scope(p: ProbedHwArch) -> CheckResult:
    if p.title:
        return draft(
            f"Title is: '{p.title}'. Reviewer to confirm it covers HW architecture scope.",
            page_section="Title page row 2",
        )
    return CheckResult(
        rating="NO",
        finding="No title detected on the Title page.",
        recommended_action="Add a clear document title reflecting HW architecture scope.",
        confidence="High",
    )


def cr_03_author_approver(p: ProbedHwArch) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(
            rating="FC",
            finding=f"Author='{p.author}', Approver='{p.approver}' both populated.",
            page_section="Title page",
            confidence="High",
        )
    missing = []
    if not p.author: missing.append("Author")
    if not p.approver: missing.append("Approver")
    return CheckResult(
        rating="NO",
        finding=f"Missing on Title page: {', '.join(missing)}.",
        recommended_action=f"Populate {', '.join(missing)} field(s).",
        confidence="High",
    )


def cr_04_revision(p: ProbedHwArch) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Revision='{p.revision}' is set on Title page.",
            page_section="Title page Revision field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Revision field not populated on Title page.",
        recommended_action="Populate the Revision field with unique identifier per release.",
        confidence="High",
    )


def cr_05_status(p: ProbedHwArch) -> CheckResult:
    if p.status:
        return CheckResult(
            rating="FC",
            finding=f"Status='{p.status}' is set on Title page.",
            page_section="Title page Status field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No work-product status field populated on Title page.",
        recommended_action="Add a Status field (Draft / In Review / Released) to Title page.",
        confidence="High",
    )


def cr_06_doc_id(p: ProbedHwArch) -> CheckResult:
    if p.doc_id:
        return CheckResult(
            rating="FC",
            finding=f"Document ID='{p.doc_id}' is present.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Document ID not identified on Title page.",
        recommended_action="Assign a unique document identifier.",
        confidence="High",
    )


def cr_07_config_mgmt(p: ProbedHwArch) -> CheckResult:
    return draft(
        "Configuration management is organizational; cannot verify from xlsx alone.",
        action="Confirm document is checked into your project's CM system (e.g., Git, Polarion).",
    )


def cr_08_references(p: ProbedHwArch) -> CheckResult:
    if "11_References" in p.sheet_names:
        return CheckResult(
            rating="FC",
            finding="References tab present; verify completeness manually.",
            page_section="Sheet '11_References'",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated References tab detected.",
        recommended_action="Add References tab citing ISO 26262-5, IC datasheets, TSC, HW-TSRs.",
        confidence="Medium",
    )


def cr_09_toc(p: ProbedHwArch) -> CheckResult:
    if p.sheet_names and any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3]):
        return CheckResult(
            rating="FC",
            finding="Title page present at start; structured sheet names support navigation.",
            page_section=f"Sheet '{p.sheet_names[0]}'",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Title page not at start or no clear table of contents.",
        recommended_action="Ensure Title page is first; add content overview.",
        confidence="Medium",
    )


def cr_10_revision_history(p: ProbedHwArch) -> CheckResult:
    return draft(
        "Check Document Control tab for revision history presence and completeness.",
        page_section="Sheet '01_Document_Control'",
    )


def cr_11_header_footer(p: ProbedHwArch) -> CheckResult:
    return draft(
        "Worksheet headers/footers cannot be reliably verified programmatically.",
        action="Open workbook in Excel; confirm header/footer reflect current doc ID and revision.",
    )


def cr_12_sections_complete(p: ProbedHwArch) -> CheckResult:
    catalog_complete = len(p.hw_elements) > 0
    power_complete = len(p.power_rails) > 0
    clock_complete = len(p.clock_sources) > 0
    cca_complete = len(p.common_cause_rows) > 0

    if catalog_complete and power_complete and clock_complete and cca_complete:
        return CheckResult(
            rating="FC",
            finding="All major sections populated: HW catalog, power rails, clock sources, CCA.",
            confidence="High",
        )
    missing = []
    if not catalog_complete: missing.append("HW Catalog")
    if not power_complete: missing.append("Power Architecture")
    if not clock_complete: missing.append("Clock Architecture")
    if not cca_complete: missing.append("Common Cause Analysis")

    return CheckResult(
        rating="PC",
        finding=f"Missing sections: {', '.join(missing)}.",
        recommended_action="Complete all architectural sections before approval.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# HW Architecture Assessment (HWAA, 12 substantive checks per ISO 26262-5 §7)
# ---------------------------------------------------------------------------

def hwaa_01_catalog_populated(p: ProbedHwArch) -> CheckResult:
    if len(p.hw_elements) > 0:
        return CheckResult(
            rating="FC",
            finding=f"HW Element Catalog populated with {len(p.hw_elements)} elements.",
            page_section="Sheet '04_HW_Element_Catalog'",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="HW Element Catalog is empty.",
        recommended_action="Document all IC, discrete, passive, and connector elements.",
        confidence="High",
    )


def hwaa_02_element_attributes(p: ProbedHwArch) -> CheckResult:
    if not p.hw_elements:
        return na("No HW elements.")
    missing = []
    for elem in p.hw_elements:
        if not elem.supplier:
            missing.append(f"{elem.hw_element_id}: no supplier")
        if not elem.part_number:
            missing.append(f"{elem.hw_element_id}: no part number")
        if not elem.package:
            missing.append(f"{elem.hw_element_id}: no package")
        if not elem.baseline_fit:
            missing.append(f"{elem.hw_element_id}: no baseline FIT")

    if not missing:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hw_elements)} elements have supplier, part, package, baseline FIT.",
            page_section="Sheet '04_HW_Element_Catalog'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(missing)} element attributes missing.",
        recommended_action="Complete supplier, part number, package, baseline FIT for all elements.",
        confidence="High",
    )


def hwaa_03_qualification(p: ProbedHwArch) -> CheckResult:
    if not p.hw_elements:
        return na("No HW elements.")
    with_qual = [e for e in p.hw_elements if e.qualification]
    if len(with_qual) == len(p.hw_elements):
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hw_elements)} ASIL-relevant elements have qualification recorded.",
            page_section="Sheet '04_HW_Element_Catalog', Qualification column",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_qual)}/{len(p.hw_elements)} elements have qualification (AEC-Q100/Q101/Q200).",
        recommended_action="Document safety qualification for all ASIL-relevant elements.",
        confidence="High",
    )


def hwaa_04_pcb_design(p: ProbedHwArch) -> CheckResult:
    if p.pcb_design_rows > 0:
        return CheckResult(
            rating="FC",
            finding=f"PCB design documented with {p.pcb_design_rows} design rows.",
            page_section="Sheet '03_PCB_Design'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="PCB design section sparse or missing.",
        recommended_action="Document PCB layers, key area allocations (power, analog, digital regions).",
        confidence="High",
    )


def hwaa_05_power_documented(p: ProbedHwArch) -> CheckResult:
    if len(p.power_rails) > 0:
        all_complete = all(
            r.voltage and r.regulator and r.monitor for r in p.power_rails
        )
        if all_complete:
            return CheckResult(
                rating="FC",
                finding=f"All {len(p.power_rails)} power rails documented with voltage, regulator, monitor.",
                page_section="Sheet '07_Power_Architecture'",
                confidence="High",
            )
        return CheckResult(
            rating="LC",
            finding=f"{len(p.power_rails)} power rails found; some missing voltage/regulator/monitor detail.",
            recommended_action="Specify voltage, regulator IC, and monitoring strategy for each rail.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No power rails documented.",
        recommended_action="Document all power rails with voltage, regulator, and monitoring.",
        confidence="High",
    )


def hwaa_06_clock_documented(p: ProbedHwArch) -> CheckResult:
    if len(p.clock_sources) > 0:
        with_monitor = [c for c in p.clock_sources if c.monitor]
        if len(with_monitor) == len(p.clock_sources):
            return CheckResult(
                rating="FC",
                finding=f"All {len(p.clock_sources)} clock sources documented with monitor and redundancy.",
                page_section="Sheet '08_Clock_Architecture'",
                confidence="High",
            )
        return CheckResult(
            rating="LC",
            finding=f"{len(p.clock_sources)} clock sources found; monitoring detail incomplete.",
            recommended_action="Document monitor and redundancy strategy for each clock source.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No clock sources documented.",
        recommended_action="Document clock sources with type, frequency, monitoring, redundancy.",
        confidence="High",
    )


def hwaa_07_hw_element_traceability(p: ProbedHwArch) -> CheckResult:
    if not p.hw_elements:
        return na("No HW elements.")
    with_tsc = [e for e in p.hw_elements if e.tsc_node_id]
    if len(with_tsc) == len(p.hw_elements):
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hw_elements)} elements traced to TSC nodes.",
            page_section="Sheet '04_HW_Element_Catalog', TSC Node ID column",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(with_tsc)}/{len(p.hw_elements)} elements have TSC node mapping.",
        recommended_action="Map each HW element to its corresponding TSC node for traceability.",
        confidence="High",
    )


def hwaa_08_safety_mechanisms(p: ProbedHwArch) -> CheckResult:
    if len(p.safety_mechanism_allocs) > 0:
        return CheckResult(
            rating="FC",
            finding=f"Safety mechanism allocation documented for {len(p.safety_mechanism_allocs)} mechanisms.",
            page_section="Sheet '05_Safety_Mechanism_Allocation'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Safety mechanism allocation section sparse or missing.",
        recommended_action="Document all HW safety mechanisms with TSC references and allocated ASIL.",
        confidence="High",
    )


def hwaa_09_hwsr_allocation(p: ProbedHwArch) -> CheckResult:
    if p.hw_sr_allocation_rows > 10:
        return CheckResult(
            rating="FC",
            finding=f"HW-SR Allocation Matrix populated with {p.hw_sr_allocation_rows} requirement rows.",
            page_section="Sheet '06_HW_SR_Allocation_Matrix'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"HW-SR Allocation Matrix sparse ({p.hw_sr_allocation_rows} rows).",
        recommended_action="Complete HW-SR allocation matrix mapping each HW-SR to implementing elements.",
        confidence="High",
    )


def hwaa_10_common_cause(p: ProbedHwArch) -> CheckResult:
    if len(p.common_cause_rows) > 0:
        unmitigated = [r for r in p.common_cause_rows if "unmitigated" in r.mitigation_status.lower()]
        if unmitigated:
            return CheckResult(
                rating="PC",
                finding=f"CCA identified {len(unmitigated)} unmitigated common-cause couplings.",
                recommended_action="Mitigate unmitigated common-cause failures via design changes.",
                confidence="High",
            )
        return CheckResult(
            rating="FC",
            finding=f"Common-cause analysis performed for {len(p.common_cause_rows)} redundant pairs; no unmitigated couplings.",
            page_section="Sheet '09_Common_Cause_Analysis'",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No common-cause failure analysis documented.",
        recommended_action="Perform CCA on all redundant element pairs (shared rail/package/zone).",
        confidence="High",
    )


def hwaa_11_bom_fit(p: ProbedHwArch) -> CheckResult:
    if p.bom_total_fit:
        try:
            fit_val = float(p.bom_total_fit.split()[0]) if p.bom_total_fit else 0
            if fit_val > 0:
                return CheckResult(
                    rating="FC",
                    finding=f"BOM total FIT computed: {p.bom_total_fit}.",
                    page_section="Sheet '10_Bill_of_Materials'",
                    confidence="High",
                )
        except:
            pass
    return CheckResult(
        rating="PC",
        finding="BOM total FIT not computed or present.",
        recommended_action="Calculate total system FIT from element baseline FITs for PMHF analysis.",
        confidence="High",
    )


def hwaa_12_independence(p: ProbedHwArch) -> CheckResult:
    return draft(
        "Independence requirements between decomposed FSC channels cannot be verified from xlsx alone.",
        action="Confirm via design review that independent channels do not share power rails, clock sources, or fault domains.",
    )


# ---------------------------------------------------------------------------
# Verification Assessment (VA)
# ---------------------------------------------------------------------------

def va_external(label: str) -> CheckResult:
    return draft(
        f"{label} governed by external Verification Plan / Specification / Report.",
        action="Verify against project Verification Plan and Report documents.",
    )


def va_01_external(p): return va_external("Verification methods")
def va_02_external(p): return va_external("Test environment")
def va_03_external(p): return va_external("Pass/fail criteria")
def va_04_external(p): return va_external("Verification environment documentation")
def va_05_external(p): return va_external("Compliance evidence")


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedHwArch], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review
    CheckDef("1",  "CR", "Document Quality", "Is the document structured in a clear manner with distinct sections?", "Shall", cr_01_structured),
    CheckDef("2",  "CR", "Document Quality", "Does the title cover the scope of the HW architecture?", "Shall", cr_02_title_scope),
    CheckDef("3",  "CR", "Document Quality", "Are the author and approver listed?", "Shall", cr_03_author_approver),
    CheckDef("4",  "CR", "Document Quality", "Is there a unique identification for each revision?", "Shall", cr_04_revision),
    CheckDef("5",  "CR", "Document Quality", "Is the status of the work product provided?", "Shall", cr_05_status),
    CheckDef("6",  "CR", "Document Quality", "Is a unique document identifier assigned?", "Shall", cr_06_doc_id),
    CheckDef("7",  "CR", "Document Quality", "Is the document under configuration and change management?", "Shall", cr_07_config_mgmt),
    CheckDef("8",  "CR", "Document Quality", "Does the document contain a table of contents or clear tab structure?", "Shall", cr_08_references),
    CheckDef("9",  "CR", "Document Quality", "Is a References section included?", "Should", cr_09_toc),
    CheckDef("10", "CR", "Document Quality", "Is a revision history maintained?", "Should", cr_10_revision_history),
    CheckDef("11", "CR", "Document Quality", "Are headers and footers properly updated?", "Should", cr_11_header_footer),
    CheckDef("12", "CR", "Document Quality", "Have all major sections been completed?", "Shall", cr_12_sections_complete),

    # HW Architecture Assessment
    CheckDef("1",  "HWAA", "HW Elements and BOM", "Is the HW Element Catalog populated (count > 0)?", "Shall", hwaa_01_catalog_populated),
    CheckDef("2",  "HWAA", "HW Elements and BOM", "Does each HW element have supplier, part number, package, baseline FIT?", "Shall", hwaa_02_element_attributes),
    CheckDef("3",  "HWAA", "HW Elements and BOM", "Is safety qualification (AEC-Q100/Q101/Q200) recorded for ASIL-relevant elements?", "Shall", hwaa_03_qualification),
    CheckDef("4",  "HWAA", "PCB and Power/Clock Architecture", "Is PCB design documented with layers and area allocations?", "Shall", hwaa_04_pcb_design),
    CheckDef("5",  "HWAA", "PCB and Power/Clock Architecture", "Are power rails documented with voltage, regulator, and monitoring?", "Shall", hwaa_05_power_documented),
    CheckDef("6",  "HWAA", "PCB and Power/Clock Architecture", "Are clock sources documented with monitoring and redundancy strategy?", "Shall", hwaa_06_clock_documented),
    CheckDef("7",  "HWAA", "Traceability and Allocation", "Is each HW element mapped to its TSC node (traceability)?", "Shall", hwaa_07_hw_element_traceability),
    CheckDef("8",  "HWAA", "Traceability and Allocation", "Are safety mechanisms allocated to HW elements with TSC references?", "Shall", hwaa_08_safety_mechanisms),
    CheckDef("9",  "HWAA", "Traceability and Allocation", "Is the HW-SR Allocation Matrix complete (each HW-SR mapped to HW elements)?", "Shall", hwaa_09_hwsr_allocation),
    CheckDef("10", "HWAA", "Common-Cause and Redundancy", "Is common-cause failure analysis performed for redundant pairs?", "Shall", hwaa_10_common_cause),
    CheckDef("11", "HWAA", "BOM and Reliability", "Is total system FIT computed from BOM for PMHF calculation?", "Shall", hwaa_11_bom_fit),
    CheckDef("12", "HWAA", "Independence and Decomposition", "Are independence requirements between FSC channels respected?", "Shall", hwaa_12_independence),

    # Verification Assessment
    CheckDef("1",  "VA", "Verification Planning", "Does verification plan address HW architecture validation methods?", "Shall", va_01_external),
    CheckDef("2",  "VA", "Verification Environment", "Is the verification test environment documented?", "Shall", va_02_external),
    CheckDef("3",  "VA", "Verification Criteria", "Are pass/fail criteria for HW architecture verification defined?", "Shall", va_03_external),
    CheckDef("4",  "VA", "Verification Evidence", "Are verification environment and tools documented?", "Shall", va_04_external),
    CheckDef("5",  "VA", "Verification Evidence", "Is compliance evidence complete and traceable to requirements?", "Shall", va_05_external),
]
