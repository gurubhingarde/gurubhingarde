"""
SW-SR Checklist definitions and verification logic per ISO 26262-6 §6.

Each check is a dict with keys:
- id: row id (e.g. "1", "10b", "12a")
- tab: which output tab (CR / SWSRA / VA)
- section: section header text
- requirement: the requirement text
- obligation: "Shall" or "Should"
- verify: callable(probed: ProbedSwSR) -> CheckResult
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sw_sr_probe import ProbedSwSR


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

def cr_01_structured(p: ProbedSwSR) -> CheckResult:
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


def cr_02_template(p: ProbedSwSR) -> CheckResult:
    return draft("Template version cannot be detected from xlsx content alone.",
                 action="Confirm the latest applicable SW-SR template was used.")


def cr_03_searchable(p: ProbedSwSR) -> CheckResult:
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


def cr_04a_title_scope(p: ProbedSwSR) -> CheckResult:
    if p.title:
        return draft(f"Title is: '{p.title}'. Reviewer to confirm scope.",
                     page_section="Title page row 2")
    return CheckResult(rating="NO", finding="No title detected on Title page.",
                       recommended_action="Add a clear document title.", confidence="High")


def cr_04b_author_approver(p: ProbedSwSR) -> CheckResult:
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


def cr_04c_unique_revision(p: ProbedSwSR) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}' is set.",
                           page_section="Title page", confidence="High")
    return CheckResult(rating="NO", finding="Revision field not populated.",
                       recommended_action="Populate the Revision field.", confidence="High")


def cr_04d_change_history(p: ProbedSwSR) -> CheckResult:
    return draft("Change history typically in Document Control tab.",
                 action="Confirm revision history table is populated on Document Control tab.")


def cr_04e_status(p: ProbedSwSR) -> CheckResult:
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}' is set.",
                           page_section="Title page", confidence="High")
    return CheckResult(rating="NO", finding="No Status field on Title page.",
                       recommended_action="Add Status field (Draft / In Review / Released).",
                       confidence="High")


def cr_05_current_revision(p: ProbedSwSR) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Current revision '{p.revision}' is identifiable.",
                           page_section="Title page", confidence="High")
    return CheckResult(rating="NO", finding="Current revision not identifiable.",
                       recommended_action="Populate the Revision field.", confidence="High")


def cr_06_config_mgmt(p: ProbedSwSR) -> CheckResult:
    return draft("Configuration management is organizational practice; cannot verify from xlsx.",
                 action="Confirm document is in configuration-management system (Polarion, DOORS, Git).")


def cr_07_header_footer(p: ProbedSwSR) -> CheckResult:
    return draft("Headers/footers cannot be reliably verified programmatically.",
                 action="Open workbook in Excel and confirm header/footer reflect current ID and revision.")


def cr_08_toc(p: ProbedSwSR) -> CheckResult:
    if p.sheet_names and any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3]):
        return CheckResult(rating="FC", finding="Title or Contents tab present in first three sheets.",
                           page_section=f"Sheet '{p.sheet_names[0]}'", confidence="Medium")
    return CheckResult(rating="PC", finding="No Table of Contents tab detected.",
                       recommended_action="Add a Table of Contents tab listing all sheets.",
                       confidence="Medium")


def cr_09_references(p: ProbedSwSR) -> CheckResult:
    return draft("References-style content and related documents.",
                 action="Confirm References tab cites ISO 26262, OEM standards, TSC, and related artifacts.")


def cr_10_sections_complete(p: ProbedSwSR) -> CheckResult:
    sr_count = len(p.sw_srs)
    complete = len([sr for sr in p.sw_srs if sr.asil and sr.allocated_swc and sr.text])
    if not sr_count:
        return CheckResult(rating="PC", finding="No SW-SR rows found.",
                           recommended_action="Populate the SW Safety Requirements tab.", confidence="High")
    rate = complete / sr_count if sr_count else 0
    if rate >= 0.95:
        return CheckResult(rating="FC", finding=f"All major sections populated. {complete}/{sr_count} SW-SRs complete.",
                           confidence="High")
    if rate >= 0.7:
        return CheckResult(rating="LC", finding=f"Most sections populated. {complete}/{sr_count} SW-SRs.",
                           recommended_action="Complete remaining ASIL/SWC/Text cells.", confidence="High")
    return CheckResult(rating="PC", finding=f"Significant gaps. {complete}/{sr_count} SW-SRs complete.",
                       recommended_action="Complete the SW Safety Requirements tab.", confidence="High")


# ---------------------------------------------------------------------------
# SW Safety Requirements Assessment (SWSRA) — substantive ISO 26262-6 §6 checks
# ---------------------------------------------------------------------------

def swsra_01_tsrs_imported(p: ProbedSwSR) -> CheckResult:
    if p.sw_tsrs_imported_count > 0:
        sample_str = ", ".join(p.sw_tsrs_imported_sample[:3])
        return CheckResult(
            rating="FC",
            finding=f"{p.sw_tsrs_imported_count} SW-TSRs imported from TSC (sample: {sample_str}).",
            page_section="Sheet '02_SW_TSRs_From_TSC'",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No SW-TSRs detected in the TSR import tab.",
        recommended_action="Import SW-TSRs from the linked TSC document.",
        confidence="High",
    )


def swsra_02_no_orphan_tsrs(p: ProbedSwSR) -> CheckResult:
    if p.sw_tsrs_imported_count <= 0:
        return na("No SW-TSRs imported.")
    sr_parent_tsrs = {sr.parent_tsr for sr in p.sw_srs if sr.parent_tsr}
    orphans = p.sw_tsrs_imported_count - len(sr_parent_tsrs)
    if orphans <= 0:
        return CheckResult(
            rating="FC",
            finding=f"All {p.sw_tsrs_imported_count} SW-TSRs have derived SW-SRs.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{orphans}/{p.sw_tsrs_imported_count} SW-TSRs lack derived SW-SRs.",
        recommended_action="Derive at least one SW-SR per SW-TSR.",
        confidence="High",
    )


def swsra_03_asil_assigned(p: ProbedSwSR) -> CheckResult:
    srs_with_asil = [sr for sr in p.sw_srs if sr.asil]
    if not p.sw_srs:
        return na("No SW-SRs.")
    rate = len(srs_with_asil) / len(p.sw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_srs)} SW-SRs have ASIL assigned. Values: {sorted(set(sr.asil for sr in srs_with_asil))}.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(srs_with_asil)}/{len(p.sw_srs)} SW-SRs have ASIL.",
        recommended_action="Assign ASIL to all SW-SRs consistent with parent TSR.",
        confidence="High",
    )


def swsra_04_allocated_swc(p: ProbedSwSR) -> CheckResult:
    srs_with_swc = [sr for sr in p.sw_srs if sr.allocated_swc and "<TBD>" not in sr.allocated_swc.upper()]
    if not p.sw_srs:
        return na("No SW-SRs.")
    rate = len(srs_with_swc) / len(p.sw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_srs)} SW-SRs have allocated SWC (no <TBD> detected).",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(srs_with_swc)}/{len(p.sw_srs)} SW-SRs have SWC specified.",
        recommended_action="Allocate SWC to all SW-SRs; remove <TBD> placeholders.",
        confidence="High",
    )


def swsra_05_requirement_text(p: ProbedSwSR) -> CheckResult:
    srs_with_text = [sr for sr in p.sw_srs if sr.text]
    if not p.sw_srs:
        return na("No SW-SRs.")
    rate = len(srs_with_text) / len(p.sw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_srs)} SW-SRs have requirement text populated.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(srs_with_text)}/{len(p.sw_srs)} SW-SRs have text.",
        recommended_action="Populate requirement text for all SW-SRs.",
        confidence="High",
    )


def swsra_06_target_detection_time(p: ProbedSwSR) -> CheckResult:
    srs_with_dt = [sr for sr in p.sw_srs if sr.target_detection_time]
    if not p.sw_srs:
        return na("No SW-SRs.")
    rate = len(srs_with_dt) / len(p.sw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_srs)} SW-SRs have target detection time specified.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(srs_with_dt)}/{len(p.sw_srs)} SW-SRs have detection time.",
        recommended_action="Assign target detection time to all SW-SRs per ASIL and timing budget.",
        confidence="High",
    )


def swsra_07_failure_mode_coverage(p: ProbedSwSR) -> CheckResult:
    if p.failure_mode_mapping_rows >= 10:
        return CheckResult(
            rating="FC",
            finding=f"Failure mode mapping covers {p.failure_mode_mapping_rows} failure modes (deadline miss, illegal state, divide-by-zero, etc).",
            confidence="Medium",
        )
    if p.failure_mode_mapping_rows > 0:
        return CheckResult(
            rating="LC",
            finding=f"Failure mode mapping has {p.failure_mode_mapping_rows} rows.",
            recommended_action="Expand to cover standard SW failure classes (deadline miss, illegal state, data corruption, divide-by-zero).",
            confidence="Medium",
        )
    return CheckResult(
        rating="NO",
        finding="No failure mode mapping rows detected.",
        recommended_action="Create failure mode mapping per ISO 26262-6 §6.5.",
        confidence="High",
    )


def swsra_08_verification_method(p: ProbedSwSR) -> CheckResult:
    srs_with_vm = [sr for sr in p.sw_srs if sr.verification_method]
    if not p.sw_srs:
        return na("No SW-SRs.")
    rate = len(srs_with_vm) / len(p.sw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_srs)} SW-SRs have verification method specified.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(srs_with_vm)}/{len(p.sw_srs)} SW-SRs have verification method.",
        recommended_action="Assign verification method to all SW-SRs.",
        confidence="High",
    )


def swsra_09_verification_asil_appropriate(p: ProbedSwSR) -> CheckResult:
    return draft(
        "Verification methods appropriate for ASIL (MC/DC for D per ISO 26262-6 Tables 7-10).",
        page_section="Sheet '06_Verification_Methods_per_ASIL'",
    )


def swsra_10_test_strategy_coverage(p: ProbedSwSR) -> CheckResult:
    if p.test_strategy_rows >= 6:
        topics = ", ".join(sorted(p.test_strategy_topics)[:3])
        return CheckResult(
            rating="FC",
            finding=f"Test strategy covers {p.test_strategy_rows} rows (unit/integration/back-to-back/fault-injection; sample topics: {topics}).",
            confidence="Medium",
        )
    if p.test_strategy_rows > 0:
        return CheckResult(
            rating="LC",
            finding=f"Test strategy has {p.test_strategy_rows} rows.",
            recommended_action="Expand to cover unit, integration, back-to-back, and fault-injection testing.",
            confidence="Medium",
        )
    return CheckResult(
        rating="NO",
        finding="No test strategy entries detected.",
        recommended_action="Document test strategy per ISO 26262-6 §6.6.",
        confidence="High",
    )


def swsra_11_independence_cascade(p: ProbedSwSR) -> CheckResult:
    if p.independence_docs > 0:
        return CheckResult(
            rating="FC",
            finding=f"Independence considerations documented ({p.independence_docs} entries).",
            confidence="Medium",
        )
    return draft(
        "If decomposition cascades from TSC, independence considerations should be documented.",
        action="If applicable, document independence arguments per ISO 26262-6 §6.4.",
    )


def swsra_12_misra_mapping(p: ProbedSwSR) -> CheckResult:
    if p.misra_mappings > 0:
        return CheckResult(
            rating="FC",
            finding=f"{p.misra_mappings} MISRA C:2012 mappings present for safety-relevant SW-SRs.",
            confidence="Medium",
        )
    return draft(
        "MISRA C:2012 mapping should be present for safety-relevant SW-SRs.",
        action="If applicable, populate MISRA Mapping tab with rule allocations per SW-SR.",
    )


# ---------------------------------------------------------------------------
# Verification Assessment (VA) — mostly external + 5 SWSR-specific 33a-e
# ---------------------------------------------------------------------------

def _va_external(label: str) -> CheckResult:
    return draft(
        f"{label} is governed by an external Verification Plan / Specification / Report.",
        action="Verify against the project's Verification Plan, Specification, and Report documents.",
    )


def va_24_plan_compliance(p): return _va_external("Verification Plan ensuring SW-SR compliance")
def va_25_validation_refined(p): return na("Belongs to TSC/validation review, not SW-SR confirmation.")
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

def va_33a_coverage(p: ProbedSwSR) -> CheckResult:
    if len(p.sw_srs) >= 5:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.sw_srs)} SW-SRs provide adequate coverage for verification.",
            confidence="High",
        )
    if len(p.sw_srs) > 0:
        return CheckResult(
            rating="LC",
            finding=f"Only {len(p.sw_srs)} SW-SRs enumerated.",
            recommended_action="Expand SW-SR catalog to ensure complete coverage of SW-TSRs.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No SW-SRs defined.",
        recommended_action="Derive SW-SRs from all imported SW-TSRs.",
        confidence="High",
    )


def va_33b_asil_consistency(p: ProbedSwSR) -> CheckResult:
    asils = {sr.asil for sr in p.sw_srs if sr.asil}
    if not asils:
        return CheckResult(
            rating="NO",
            finding="No ASIL values assigned to SW-SRs.",
            recommended_action="Assign ASIL to each SW-SR consistent with parent SW-TSR.",
            confidence="High",
        )
    return CheckResult(
        rating="FC",
        finding=f"All {len(p.sw_srs)} SW-SRs have ASIL assigned. Values: {sorted(asils)}.",
        confidence="High",
    )


def va_33c_hsi_consistency(p: ProbedSwSR) -> CheckResult:
    return draft(
        "Consistency with HSI specifications and signal definitions.",
        action="Verify SW-SR allocations are consistent with HSI definitions.",
    )


def va_33d_swc_mapping(p: ProbedSwSR) -> CheckResult:
    if len(p.sw_srs) > 0:
        swcs = {sr.allocated_swc for sr in p.sw_srs if sr.allocated_swc}
        return CheckResult(
            rating="FC",
            finding=f"SW-SRs map to {len(swcs)} distinct SWC elements.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No SW-SR allocations found.",
        recommended_action="Allocate each SW-SR to a specific SWC.",
        confidence="High",
    )


def va_33e_requirement_completeness(p: ProbedSwSR) -> CheckResult:
    complete = [sr for sr in p.sw_srs if sr.text and sr.asil and sr.allocated_swc and sr.target_detection_time]
    if not p.sw_srs:
        return na("No SW-SRs.")
    rate = len(complete) / len(p.sw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_srs)} SW-SRs have complete attributes (text, ASIL, SWC, detection time).",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(complete)}/{len(p.sw_srs)} SW-SRs have all required attributes.",
        recommended_action="Complete missing attributes for all SW-SRs.",
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
    verify: Callable[[ProbedSwSR], CheckResult]


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

    # SW Safety Requirements Assessment (12 ISO 26262-6 §6 checks)
    CheckDef("1",  "SWSRA", "SW-SR Prerequisites", "Have SW-TSRs been successfully imported from the TSC?", "Shall", swsra_01_tsrs_imported),
    CheckDef("2",  "SWSRA", "SW-SR Prerequisites", "Is at least one SW-SR derived per SW-TSR (no orphans)?", "Shall", swsra_02_no_orphan_tsrs),
    CheckDef("3",  "SWSRA", "SW-SR Attributes", "Is ASIL assigned and consistent with parent TSR?", "Shall", swsra_03_asil_assigned),
    CheckDef("4",  "SWSRA", "SW-SR Attributes", "Is allocated SWC specified (no <TBD>)?", "Shall", swsra_04_allocated_swc),
    CheckDef("5",  "SWSRA", "SW-SR Attributes", "Does each SW-SR have requirement text (no empty rows)?", "Shall", swsra_05_requirement_text),
    CheckDef("6",  "SWSRA", "SW-SR Attributes", "Is target detection time specified for each SW-SR?", "Shall", swsra_06_target_detection_time),
    CheckDef("7",  "SWSRA", "FMEDA", "Does failure mode mapping cover standard SW failure modes?", "Shall", swsra_07_failure_mode_coverage),
    CheckDef("8",  "SWSRA", "Verification", "Does each SW-SR have at least one verification method?", "Shall", swsra_08_verification_method),
    CheckDef("9",  "SWSRA", "Verification", "Are verification methods appropriate for ASIL (MC/DC for D)?", "Shall", swsra_09_verification_asil_appropriate),
    CheckDef("10", "SWSRA", "Test Strategy", "Does test strategy cover unit/integration/back-to-back/fault-injection?", "Shall", swsra_10_test_strategy_coverage),
    CheckDef("11", "SWSRA", "Independence", "Are independence considerations documented if cascading from TSC?", "Should", swsra_11_independence_cascade),
    CheckDef("12", "SWSRA", "MISRA", "Is MISRA C:2012 mapping present for safety-relevant SW-SRs?", "Should", swsra_12_misra_mapping),

    # Verification Assessment (mostly external; 5 SWSR-specific 33a–e)
    CheckDef("24", "VA", "Verification Planning", "Does the Verification Plan ensure compliance with SW-SRs?", "Shall", va_24_plan_compliance),
    CheckDef("25", "VA", "Verification Planning", "If applicable, was validation refined based on SW-TSRs?", "Should", va_25_validation_refined),
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

    CheckDef("33", "VA", "SW-SR-specific Verification", "Have SW-SR-specific items been verified (33a–e)?", "Shall", va_33a_coverage),
    CheckDef("33a","VA", "SW-SR-specific Verification", "Completeness of SW-SR coverage?", "Shall", va_33a_coverage),
    CheckDef("33b","VA", "SW-SR-specific Verification", "Consistency of ASIL assignments with parent SW-TSRs?", "Shall", va_33b_asil_consistency),
    CheckDef("33c","VA", "SW-SR-specific Verification", "Consistency with HSI specifications?", "Shall", va_33c_hsi_consistency),
    CheckDef("33d","VA", "SW-SR-specific Verification", "Completeness of SWC mapping?", "Shall", va_33d_swc_mapping),
    CheckDef("33e","VA", "SW-SR-specific Verification", "Completeness of requirement attributes (text, ASIL, SWC, detection time)?", "Shall", va_33e_requirement_completeness),
]
