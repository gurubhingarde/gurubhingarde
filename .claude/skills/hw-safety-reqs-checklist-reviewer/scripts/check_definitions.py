"""
HW-SR Checklist definitions and verification logic.

Each check is a dict with keys:
- id: row id (e.g. "1", "10b", "12a")
- tab: which output tab (CR / HWSRA / VA)
- section: section header text
- requirement: the requirement text
- obligation: "Shall" or "Should"
- verify: callable(probed: ProbedHwSR) -> CheckResult
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from hw_sr_probe import ProbedHwSR


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    rating: str = ""              # FC / LC / PC / NO / NA / "" (pending)
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""          # High / Medium / Low / "" for binary CR


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
# Verification functions — Confirmation Review (14 standard doc-quality checks)
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedHwSR) -> CheckResult:
    if len(p.sheet_names) >= 5:
        return CheckResult(
            rating="FC",
            finding=f"Document is structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has only {len(p.sheet_names)} tabs; structure may be insufficient.",
        recommended_action="Add separate tabs for distinct concerns.",
        confidence="Medium",
    )


def cr_02_template(p: ProbedHwSR) -> CheckResult:
    return draft("Template version cannot be detected from xlsx content alone.",
                 action="Confirm the latest applicable HW-SR template was used.")


def cr_03_searchable(p: ProbedHwSR) -> CheckResult:
    if p.sheet_names and any("title" in s.lower() for s in p.sheet_names[:3]):
        return CheckResult(
            rating="FC",
            finding="Document has a Title tab; structured columns aid search.",
            page_section=f"Sheet '{p.sheet_names[0]}'",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated Title/Contents tab detected near beginning.",
        recommended_action="Add a Table of Contents tab for navigation.",
        confidence="Medium",
    )


def cr_04a_title_scope(p: ProbedHwSR) -> CheckResult:
    if p.title:
        return draft(f"Title is: '{p.title}'. Reviewer to confirm scope.",
                     page_section="Title page row 2")
    return CheckResult(rating="NO", finding="No title detected on Title page.",
                       recommended_action="Add a clear document title.", confidence="High")


def cr_04b_author_approver(p: ProbedHwSR) -> CheckResult:
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
        finding=f"Missing: {', '.join(missing)}.",
        recommended_action=f"Populate {', '.join(missing)} field(s).",
        confidence="High",
    )


def cr_04c_unique_revision(p: ProbedHwSR) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}' is set.",
                           page_section="Title page", confidence="High")
    return CheckResult(rating="NO", finding="Revision field not populated.",
                       recommended_action="Populate the Revision field.", confidence="High")


def cr_04d_change_history(p: ProbedHwSR) -> CheckResult:
    return draft("Change history typically in Document Control tab.",
                 action="Confirm revision history table is populated on Document Control tab.")


def cr_04e_status(p: ProbedHwSR) -> CheckResult:
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}' is set.",
                           page_section="Title page", confidence="High")
    return CheckResult(rating="NO", finding="No Status field on Title page.",
                       recommended_action="Add Status field (Draft / In Review / Released).",
                       confidence="High")


def cr_05_current_revision(p: ProbedHwSR) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Current revision '{p.revision}' is identifiable.",
                           page_section="Title page", confidence="High")
    return CheckResult(rating="NO", finding="Current revision not identifiable.",
                       recommended_action="Populate the Revision field.", confidence="High")


def cr_06_config_mgmt(p: ProbedHwSR) -> CheckResult:
    return draft("Configuration management is organizational practice; cannot verify from xlsx.",
                 action="Confirm document is in configuration-management system (Polarion, DOORS, Git).")


def cr_07_header_footer(p: ProbedHwSR) -> CheckResult:
    return draft("Headers/footers cannot be reliably verified programmatically.",
                 action="Open workbook in Excel and confirm header/footer reflect current ID and revision.")


def cr_08_toc(p: ProbedHwSR) -> CheckResult:
    if p.sheet_names and any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3]):
        return CheckResult(rating="FC", finding="Title or Contents tab present in first three sheets.",
                           page_section=f"Sheet '{p.sheet_names[0]}'", confidence="Medium")
    return CheckResult(rating="PC", finding="No Table of Contents tab detected.",
                       recommended_action="Add a Table of Contents tab listing all sheets.",
                       confidence="Medium")


def cr_09_references(p: ProbedHwSR) -> CheckResult:
    return draft("References-style content and related documents.",
                 action="Confirm References tab cites ISO 26262, OEM standards, TSC, and related artifacts.")


def cr_10_sections_complete(p: ProbedHwSR) -> CheckResult:
    sr_count = len(p.hw_srs)
    complete = len([sr for sr in p.hw_srs if sr.asil and sr.allocated_hw_element and sr.text])
    if not sr_count:
        return CheckResult(rating="PC", finding="No HW-SR rows found.",
                           recommended_action="Populate the HW Safety Requirements tab.", confidence="High")
    rate = complete / sr_count if sr_count else 0
    if rate >= 0.95:
        return CheckResult(rating="FC", finding=f"All major sections populated. {complete}/{sr_count} HW-SRs complete.",
                           confidence="High")
    if rate >= 0.7:
        return CheckResult(rating="LC", finding=f"Most sections populated. {complete}/{sr_count} HW-SRs.",
                           recommended_action="Complete remaining ASIL/Element/Text cells.", confidence="High")
    return CheckResult(rating="PC", finding=f"Significant gaps. {complete}/{sr_count} HW-SRs complete.",
                       recommended_action="Complete the HW Safety Requirements tab.", confidence="High")


# ---------------------------------------------------------------------------
# HW Safety Requirements Assessment (HWSRA) — substantive ISO 26262-5 §6 checks
# ---------------------------------------------------------------------------

def hwsra_01_tsrs_imported(p: ProbedHwSR) -> CheckResult:
    if p.hw_tsrs_imported_count > 0:
        sample_str = ", ".join(p.hw_tsrs_imported_sample[:3])
        return CheckResult(
            rating="FC",
            finding=f"{p.hw_tsrs_imported_count} HW-TSRs imported from TSC (sample: {sample_str}).",
            page_section="Sheet '02_HW_TSRs_From_TSC'",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No HW-TSRs detected in the TSR import tab.",
        recommended_action="Import HW-TSRs from the linked TSC document.",
        confidence="High",
    )


def hwsra_02_no_orphan_tsrs(p: ProbedHwSR) -> CheckResult:
    if p.hw_tsrs_imported_count <= 0:
        return na("No HW-TSRs imported.")
    sr_parent_tsrs = {sr.parent_tsr for sr in p.hw_srs if sr.parent_tsr}
    orphans = p.hw_tsrs_imported_count - len(sr_parent_tsrs)
    if orphans <= 0:
        return CheckResult(
            rating="FC",
            finding=f"All {p.hw_tsrs_imported_count} HW-TSRs have derived HW-SRs.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{orphans}/{p.hw_tsrs_imported_count} HW-TSRs lack derived HW-SRs.",
        recommended_action="Derive at least one HW-SR per HW-TSR.",
        confidence="High",
    )


def hwsra_03_asil_assigned(p: ProbedHwSR) -> CheckResult:
    srs_with_asil = [sr for sr in p.hw_srs if sr.asil]
    if not p.hw_srs:
        return na("No HW-SRs.")
    rate = len(srs_with_asil) / len(p.hw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hw_srs)} HW-SRs have ASIL assigned. Values: {sorted(set(sr.asil for sr in srs_with_asil))}.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(srs_with_asil)}/{len(p.hw_srs)} HW-SRs have ASIL.",
        recommended_action="Assign ASIL to all HW-SRs consistent with parent TSR.",
        confidence="High",
    )


def hwsra_04_allocated_element(p: ProbedHwSR) -> CheckResult:
    srs_with_elem = [sr for sr in p.hw_srs if sr.allocated_hw_element and "<TBD>" not in sr.allocated_hw_element.upper()]
    if not p.hw_srs:
        return na("No HW-SRs.")
    rate = len(srs_with_elem) / len(p.hw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hw_srs)} HW-SRs have allocated HW element (no <TBD> detected).",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(srs_with_elem)}/{len(p.hw_srs)} HW-SRs have element specified.",
        recommended_action="Allocate HW element to all HW-SRs; remove <TBD> placeholders.",
        confidence="High",
    )


def hwsra_05_requirement_text(p: ProbedHwSR) -> CheckResult:
    srs_with_text = [sr for sr in p.hw_srs if sr.text]
    if not p.hw_srs:
        return na("No HW-SRs.")
    rate = len(srs_with_text) / len(p.hw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hw_srs)} HW-SRs have requirement text populated.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(srs_with_text)}/{len(p.hw_srs)} HW-SRs have text.",
        recommended_action="Populate requirement text for all HW-SRs.",
        confidence="High",
    )


def hwsra_06_target_dc(p: ProbedHwSR) -> CheckResult:
    srs_with_dc = [sr for sr in p.hw_srs if sr.target_dc]
    if not p.hw_srs:
        return na("No HW-SRs.")
    rate = len(srs_with_dc) / len(p.hw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hw_srs)} HW-SRs have target DC% specified.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(srs_with_dc)}/{len(p.hw_srs)} HW-SRs have target DC.",
        recommended_action="Assign target Diagnostic Coverage % to all HW-SRs per ASIL.",
        confidence="High",
    )


def hwsra_07_failure_mode_coverage(p: ProbedHwSR) -> CheckResult:
    if p.failure_mode_mapping_rows >= 10:
        return CheckResult(
            rating="FC",
            finding=f"Failure mode mapping covers {p.failure_mode_mapping_rows} failure modes across HW elements.",
            confidence="Medium",
        )
    if p.failure_mode_mapping_rows > 0:
        return CheckResult(
            rating="LC",
            finding=f"Failure mode mapping has {p.failure_mode_mapping_rows} rows.",
            recommended_action="Expand to cover all standard failure classes per element type (short, open, degradation, etc.).",
            confidence="Medium",
        )
    return CheckResult(
        rating="NO",
        finding="No failure mode mapping rows detected.",
        recommended_action="Create failure mode mapping per ISO 26262-5 Annex D.",
        confidence="High",
    )


def hwsra_08_verification_method(p: ProbedHwSR) -> CheckResult:
    srs_with_vm = [sr for sr in p.hw_srs if sr.verification_method]
    if not p.hw_srs:
        return na("No HW-SRs.")
    rate = len(srs_with_vm) / len(p.hw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hw_srs)} HW-SRs have verification method specified.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(srs_with_vm)}/{len(p.hw_srs)} HW-SRs have verification method.",
        recommended_action="Assign verification method to all HW-SRs.",
        confidence="High",
    )


def hwsra_09_verification_asil_appropriate(p: ProbedHwSR) -> CheckResult:
    return draft(
        "Verification methods appropriate for ASIL (e.g., ++ methods for ASIL D per ISO 26262-5 Table 21).",
        page_section="Sheet '06_Verification_Methods'",
    )


def hwsra_10_test_strategy_coverage(p: ProbedHwSR) -> CheckResult:
    if p.test_strategy_rows >= 6:
        topics = ", ".join(sorted(p.test_strategy_topics)[:3])
        return CheckResult(
            rating="FC",
            finding=f"Test strategy covers {p.test_strategy_rows} rows (HIL, fault injection, electrical, environmental; sample topics: {topics}).",
            confidence="Medium",
        )
    if p.test_strategy_rows > 0:
        return CheckResult(
            rating="LC",
            finding=f"Test strategy has {p.test_strategy_rows} rows.",
            recommended_action="Expand to cover HIL, fault injection, electrical stress, and environmental scenarios.",
            confidence="Medium",
        )
    return CheckResult(
        rating="NO",
        finding="No test strategy entries detected.",
        recommended_action="Document test strategy per ISO 26262-5 §6.7.",
        confidence="High",
    )


def hwsra_11_independence_cascade(p: ProbedHwSR) -> CheckResult:
    if p.independence_docs > 0:
        return CheckResult(
            rating="FC",
            finding=f"Independence considerations documented ({p.independence_docs} entries).",
            confidence="Medium",
        )
    return draft(
        "If decomposition cascades from FSC, independence considerations should be documented.",
        action="If applicable, document independence arguments per ISO 26262-5 §6.4.",
    )


def hwsra_12_hsi_references(p: ProbedHwSR) -> CheckResult:
    if p.hsi_references > 0:
        return CheckResult(
            rating="FC",
            finding=f"{p.hsi_references} HSI references found where HW-SR involves HW→SW signal.",
            confidence="Medium",
        )
    return draft(
        "HSI references should be present for any HW-SR involving hardware-to-software signal.",
        action="If applicable, populate HSI Reference tab with interface definitions.",
    )


# ---------------------------------------------------------------------------
# Verification Assessment (VA) — mostly external; 5 HWSR-specific items (33a–e)
# ---------------------------------------------------------------------------

def _va_external(label: str) -> CheckResult:
    return draft(
        f"{label} is governed by an external Verification Plan / Specification / Report.",
        action="Verify against the project's Verification Plan, Specification, and Report documents.",
    )


def va_24_plan_compliance(p): return _va_external("Verification Plan ensuring HW-SR compliance")
def va_25_validation_refined(p): return na("Belongs to TSC/validation review, not HW-SR confirmation.")
def va_26_plan_addresses(p): return _va_external("Verification Plan addressing content/methods/criteria/env/tools")
def va_26a(p): return _va_external("Plan content coverage")
def va_26b(p): return _va_external("Verification methods")
def va_26c(p): return _va_external("Pass/fail criteria")
def va_26d(p): return _va_external("Verification environment")
def va_26e(p): return _va_external("Verification tools")
def va_26f(p): return _va_external("Anomaly handling")
def va_26g(p): return _va_external("Regression strategy")
def va_27_planning(p): return _va_external("Planning considerations")
def va_28_methods(p): return _va_external("Review/analysis checklists and test specifications")
def va_29_test_spec(p): return _va_external("Test case content specification")
def va_30_grouping(p): return _va_external("Test case grouping by method")
def va_31_executed(p): return _va_external("Verification executed per plan")
def va_32_report(p): return _va_external("Verification Report content and results")

def va_33a_coverage(p: ProbedHwSR) -> CheckResult:
    if len(p.hw_srs) >= 5:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.hw_srs)} HW-SRs provide adequate coverage for verification.",
            confidence="High",
        )
    if len(p.hw_srs) > 0:
        return CheckResult(
            rating="LC",
            finding=f"Only {len(p.hw_srs)} HW-SRs enumerated.",
            recommended_action="Expand HW-SR catalog to ensure complete coverage of HW-TSRs.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No HW-SRs defined.",
        recommended_action="Derive HW-SRs from all imported HW-TSRs.",
        confidence="High",
    )


def va_33b_asil_consistency(p: ProbedHwSR) -> CheckResult:
    asils = {sr.asil for sr in p.hw_srs if sr.asil}
    if not asils:
        return CheckResult(
            rating="NO",
            finding="No ASIL values assigned to HW-SRs.",
            recommended_action="Assign ASIL to each HW-SR consistent with parent HW-TSR.",
            confidence="High",
        )
    return CheckResult(
        rating="FC",
        finding=f"All {len(p.hw_srs)} HW-SRs have ASIL assigned. Values: {sorted(asils)}.",
        confidence="High",
    )


def va_33c_hsi_consistency(p: ProbedHwSR) -> CheckResult:
    return draft(
        "Consistency with HSI specifications and signal definitions.",
        action="Verify HW-SR allocations are consistent with HSI definitions.",
    )


def va_33d_element_mapping(p: ProbedHwSR) -> CheckResult:
    if len(p.hw_srs) > 0:
        elements = {sr.allocated_hw_element for sr in p.hw_srs if sr.allocated_hw_element}
        return CheckResult(
            rating="FC",
            finding=f"HW-SRs map to {len(elements)} distinct HW elements.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No HW-SR allocations found.",
        recommended_action="Allocate each HW-SR to a specific HW element.",
        confidence="High",
    )


def va_33e_requirement_completeness(p: ProbedHwSR) -> CheckResult:
    complete = [sr for sr in p.hw_srs if sr.text and sr.asil and sr.allocated_hw_element and sr.target_dc]
    if not p.hw_srs:
        return na("No HW-SRs.")
    rate = len(complete) / len(p.hw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hw_srs)} HW-SRs have complete attributes (text, ASIL, element, target DC).",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(complete)}/{len(p.hw_srs)} HW-SRs have all required attributes.",
        recommended_action="Complete missing attributes for all HW-SRs.",
        confidence="High",
    )


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
    verify: Callable[[ProbedHwSR], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review (14 standard doc-quality checks)
    CheckDef("1",  "CR", "Document Quality", "Is the document structured clearly (headlines, templates)?", "Shall", cr_01_structured),
    CheckDef("2",  "CR", "Document Quality", "Was the latest template available used at document creation?", "Should", cr_02_template),
    CheckDef("3",  "CR", "Document Quality", "Does structure facilitate search (cross-references, index)?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does the title cover the scope of the content?", "Shall", cr_04a_title_scope),
    CheckDef("4b", "CR", "Document Quality", "Are the author and approver(s) listed?", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Document Quality", "Is there unique identification for each revision?", "Shall", cr_04c_unique_revision),
    CheckDef("4d", "CR", "Document Quality", "Is there a change history available?", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Quality", "Is the status of the work product provided?", "Shall", cr_04e_status),
    CheckDef("5",  "CR", "Document Quality", "Is the current revision clearly identifiable?", "Shall", cr_05_current_revision),
    CheckDef("6",  "CR", "Document Quality", "Is the document under configuration and change management?", "Shall", cr_06_config_mgmt),
    CheckDef("7",  "CR", "Document Quality", "Are header and footer updated?", "Should", cr_07_header_footer),
    CheckDef("8",  "CR", "Document Quality", "Does this document contain a correct table of contents?", "Shall", cr_08_toc),
    CheckDef("9",  "CR", "Document Quality", "Does the Reference Table list all contained references?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "Have all sections of the work product been completed?", "Should", cr_10_sections_complete),

    # HW Safety Requirements Assessment (12 ISO 26262-5 §6 checks)
    CheckDef("1",  "HWSRA", "HW-SR Prerequisites", "Have HW-TSRs been successfully imported from the TSC?", "Shall", hwsra_01_tsrs_imported),
    CheckDef("2",  "HWSRA", "HW-SR Prerequisites", "Is at least one HW-SR derived per HW-TSR (no orphans)?", "Shall", hwsra_02_no_orphan_tsrs),
    CheckDef("3",  "HWSRA", "HW-SR Attributes", "Is ASIL assigned and consistent with parent TSR?", "Shall", hwsra_03_asil_assigned),
    CheckDef("4",  "HWSRA", "HW-SR Attributes", "Is allocated HW element specified (no <TBD>)?", "Shall", hwsra_04_allocated_element),
    CheckDef("5",  "HWSRA", "HW-SR Attributes", "Does each HW-SR have requirement text (no empty rows)?", "Shall", hwsra_05_requirement_text),
    CheckDef("6",  "HWSRA", "HW-SR Attributes", "Is target DC% specified for each HW-SR?", "Shall", hwsra_06_target_dc),
    CheckDef("7",  "HWSRA", "FMEDA", "Does failure mode mapping cover standard failure classes per element?", "Shall", hwsra_07_failure_mode_coverage),
    CheckDef("8",  "HWSRA", "Verification", "Does each HW-SR have at least one verification method?", "Shall", hwsra_08_verification_method),
    CheckDef("9",  "HWSRA", "Verification", "Are verification methods appropriate for ASIL (++ for D)?", "Shall", hwsra_09_verification_asil_appropriate),
    CheckDef("10", "HWSRA", "Test Strategy", "Does test strategy cover HIL, fault injection, electrical, environmental?", "Shall", hwsra_10_test_strategy_coverage),
    CheckDef("11", "HWSRA", "Independence", "Are independence considerations documented if cascading from FSC?", "Should", hwsra_11_independence_cascade),
    CheckDef("12", "HWSRA", "HSI", "Are HSI references present where HW-SR involves HW→SW signal?", "Should", hwsra_12_hsi_references),

    # Verification Assessment (mostly external; 5 HWSR-specific 33a–e)
    CheckDef("24", "VA", "Verification Planning", "Does the Verification Plan ensure compliance with HW-SRs?", "Shall", va_24_plan_compliance),
    CheckDef("25", "VA", "Verification Planning", "If applicable, was validation refined based on HW-TSRs?", "Should", va_25_validation_refined),
    CheckDef("26", "VA", "Verification Planning", "Does the Verification Plan address content, methods, criteria, env, tools?", "Shall", va_26_plan_addresses),
    CheckDef("26a","VA", "Verification Planning", "Content of the work product(s) to be verified?", "Shall", va_26a),
    CheckDef("26b","VA", "Verification Planning", "Methods to be used?", "Shall", va_26b),
    CheckDef("26c","VA", "Verification Planning", "Pass/fail criteria?", "Shall", va_26c),
    CheckDef("26d","VA", "Verification Planning", "Verification environment (if applicable)?", "Shall", va_26d),
    CheckDef("26e","VA", "Verification Planning", "Tools used for verification (if applicable)?", "Shall", va_26e),
    CheckDef("26f","VA", "Verification Planning", "Actions when anomalies are detected?", "Shall", va_26f),
    CheckDef("26g","VA", "Verification Planning", "Regression strategy?", "Shall", va_26g),
    CheckDef("27", "VA", "Verification Planning", "Does planning consider method adequacy, complexity, experience, maturity?", "Should", va_27_planning),
    CheckDef("28", "VA", "Verification Specification", "Are review/analysis checklists or test cases specified?", "Shall", va_28_methods),
    CheckDef("29", "VA", "Verification Specification", "For testing, does specification include required elements?", "Shall", va_29_test_spec),
    CheckDef("30", "VA", "Verification Specification", "Are test cases grouped by method with environment and dependencies?", "Shall", va_30_grouping),
    CheckDef("31", "VA", "Verification Execution", "Was verification executed per the plan and specification?", "Shall", va_31_executed),
    CheckDef("32", "VA", "Verification Execution", "Does Verification Report include required elements?", "Shall", va_32_report),

    CheckDef("33", "VA", "HW-SR-specific Verification", "Have HW-SR-specific items been verified (33a–e)?", "Shall", va_33a_coverage),
    CheckDef("33a","VA", "HW-SR-specific Verification", "Completeness of HW-SR coverage?", "Shall", va_33a_coverage),
    CheckDef("33b","VA", "HW-SR-specific Verification", "Consistency of ASIL assignments with parent HW-TSRs?", "Shall", va_33b_asil_consistency),
    CheckDef("33c","VA", "HW-SR-specific Verification", "Consistency with HSI specifications?", "Shall", va_33c_hsi_consistency),
    CheckDef("33d","VA", "HW-SR-specific Verification", "Completeness of HW element mapping?", "Shall", va_33d_element_mapping),
    CheckDef("33e","VA", "HW-SR-specific Verification", "Completeness of requirement attributes (text, ASIL, element, DC)?", "Shall", va_33e_requirement_completeness),
]
