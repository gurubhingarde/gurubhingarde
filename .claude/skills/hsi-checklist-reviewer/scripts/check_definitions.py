"""
HSI Specification checklist definitions and verification logic per ISO 26262-4 §6.4.6 and §6.4.7.

Checks organized into:
- Confirmation Review (CR): 14 generic doc-quality checks
- HSI Assessment (HSIA): 14 substantive HSI-specific checks
- Verification Assessment (VA): 5 HARA-specific checks
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from hsi_probe import ProbedHsi


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    rating: str = ""              # FC / LC / PC / NO / NA / "" (pending)
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""          # High / Medium / Low


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
# Verification functions — Confirmation Review
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedHsi) -> CheckResult:
    if len(p.sheet_names) >= 9:
        return CheckResult(
            rating="FC",
            finding=f"Document is structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has {len(p.sheet_names)} tabs; HSI spec typically requires 10+.",
        recommended_action="Ensure all standard HSI tabs present (Title, Doc Control, Signal Catalog, Register Map, Timing, Failure Modes, Init Sequence, Cross-Reference, Test Cases, References).",
        confidence="Medium",
    )


def cr_02_template(p: ProbedHsi) -> CheckResult:
    return draft(
        "Template version cannot be detected from xlsx content alone.",
        action="Confirm the latest applicable HSI Specification template was used.",
    )


def cr_03_searchable(p: ProbedHsi) -> CheckResult:
    if p.has_table_of_contents and p.likely_references_sheet:
        return CheckResult(
            rating="FC",
            finding="Document has a Title/Contents tab and a References tab.",
            page_section=f"Sheet '{p.sheet_names[0]}'",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Some search aids present but not all (TOC and Reference list).",
        recommended_action="Add a Table of Contents and References sheet.",
        confidence="Medium",
    )


def cr_04a_title_scope(p: ProbedHsi) -> CheckResult:
    if p.title:
        return draft(
            f"Title detected: '{p.title}'. Reviewer to confirm scope coverage.",
            page_section="Title page",
        )
    return CheckResult(
        rating="NO",
        finding="No title detected on Title page.",
        recommended_action="Add a clear document title.",
        confidence="High",
    )


def cr_04b_author_approver(p: ProbedHsi) -> CheckResult:
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
        recommended_action=f"Populate {', '.join(missing)} field(s) on Title page.",
        confidence="High",
    )


def cr_04c_unique_revision(p: ProbedHsi) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Revision='{p.revision}' populated on Title page.",
            page_section="Title page Revision field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Revision field not populated.",
        recommended_action="Populate the Revision field.",
        confidence="High",
    )


def cr_04d_change_history(p: ProbedHsi) -> CheckResult:
    if p.revision_history_rows >= 1:
        return CheckResult(
            rating="FC",
            finding=f"Document Control tab contains {p.revision_history_rows} revision history row(s).",
            page_section=f"Sheet '{p.likely_doc_control_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No revision history rows detected.",
        recommended_action="Add a populated revision history table to Document Control tab.",
        confidence="High",
    )


def cr_04e_status(p: ProbedHsi) -> CheckResult:
    if p.status:
        return CheckResult(
            rating="FC",
            finding=f"Status='{p.status}' populated on Title page.",
            page_section="Title page Status field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No work-product status field populated.",
        recommended_action="Add a Status field (Draft / In Review / Released) to Title page.",
        confidence="High",
    )


def cr_05_current_revision(p: ProbedHsi) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Current revision '{p.revision}' is identifiable.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Current revision is not identifiable.",
        recommended_action="Populate the Revision field on Title page.",
        confidence="High",
    )


def cr_06_config_mgmt(p: ProbedHsi) -> CheckResult:
    return draft(
        "Configuration management is an organizational practice; cannot be verified from xlsx content.",
        action="Confirm the document is checked into the project's configuration-management system.",
    )


def cr_07_header_footer(p: ProbedHsi) -> CheckResult:
    return draft(
        "Worksheet headers/footers cannot be reliably verified programmatically.",
        action="Open in Excel and confirm header/footer reflect current document ID and revision.",
    )


def cr_08_toc(p: ProbedHsi) -> CheckResult:
    if p.has_table_of_contents:
        return CheckResult(
            rating="FC",
            finding="A Title or Contents tab is present in first three sheets.",
            page_section=f"Sheet '{p.sheet_names[0]}'",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No Table of Contents tab detected near beginning.",
        recommended_action="Add a Table of Contents tab listing all sheets and their purposes.",
        confidence="Medium",
    )


def cr_09_references(p: ProbedHsi) -> CheckResult:
    if p.likely_references_sheet:
        return draft(
            f"References tab found: '{p.likely_references_sheet}'. Reviewer to confirm completeness.",
            page_section=f"Sheet '{p.likely_references_sheet}'",
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated References tab detected.",
        recommended_action="Add References tab citing ISO 26262, related documents, and architectural assumptions.",
        confidence="Medium",
    )


def cr_10_sections_complete(p: ProbedHsi) -> CheckResult:
    signal_complete = len([s for s in p.hsi_signals if s.direction and s.data_type and s.owner])
    signal_rate = signal_complete / max(1, len(p.hsi_signals))
    register_present = len(p.register_map_rows) > 0
    timing_present = len(p.timing_rows) > 0
    failure_present = len(p.failure_mode_rows) > 0
    test_present = len(p.test_case_rows) > 0

    completed = sum([register_present, timing_present, failure_present, test_present])
    if completed >= 3 and signal_rate >= 0.9:
        return CheckResult(
            rating="FC",
            finding=f"Major sections populated. {completed}/4 content tabs complete; signal catalog {signal_rate:.0%} complete.",
            confidence="High",
        )
    if completed >= 2 and signal_rate >= 0.7:
        return CheckResult(
            rating="LC",
            finding=f"Most sections populated. {completed}/4 tabs; signals {signal_rate:.0%} complete.",
            recommended_action="Complete remaining signal catalog and content sections.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Incomplete. {completed}/4 tabs populated; signals {signal_rate:.0%}.",
        recommended_action="Complete all HSI specification tabs before review.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Verification functions — HSI Assessment (HSIA)
# ---------------------------------------------------------------------------

def hsia_1_signals_populated(p: ProbedHsi) -> CheckResult:
    if len(p.hsi_signals) >= 5:
        return CheckResult(
            rating="FC",
            finding=f"HSI signal catalog populated with {len(p.hsi_signals)} signals.",
            page_section=f"Sheet '{p.likely_signal_catalog_sheet}'",
            confidence="High",
        )
    if len(p.hsi_signals) > 0:
        return CheckResult(
            rating="LC",
            finding=f"Only {len(p.hsi_signals)} signals defined; verify coverage.",
            recommended_action="Review signal catalog completeness against architecture.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Signal catalog is empty.",
        recommended_action="Populate the HSI Signal Catalog tab with all interface signals.",
        confidence="High",
    )


def hsia_2_signal_direction(p: ProbedHsi) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    with_direction = [s for s in p.hsi_signals if s.direction]
    rate = len(with_direction) / len(p.hsi_signals)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hsi_signals)} signals have direction specified (HW->SW or SW->HW).",
            page_section=f"Sheet '{p.likely_signal_catalog_sheet}', Direction column",
            confidence="High",
        )
    return CheckResult(
        rating="PC" if rate < 0.8 else "LC",
        finding=f"{len(with_direction)}/{len(p.hsi_signals)} signals have direction.",
        recommended_action="Specify HW->SW or SW->HW direction for all signals.",
        confidence="High",
    )


def hsia_3_encoding_specified(p: ProbedHsi) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    with_encoding = [s for s in p.hsi_signals if s.bit_width or s.data_type]
    rate = len(with_encoding) / len(p.hsi_signals)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All signals have bit width / encoding specified.",
            page_section=f"Sheet '{p.likely_signal_catalog_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_encoding)}/{len(p.hsi_signals)} signals have encoding.",
        recommended_action="Specify bit width and data type for all signals.",
        confidence="High",
    )


def hsia_4_owner_identified(p: ProbedHsi) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    with_owner = [s for s in p.hsi_signals if s.owner]
    rate = len(with_owner) / len(p.hsi_signals)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All signals have owner identified (HW or SW).",
            page_section=f"Sheet '{p.likely_signal_catalog_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_owner)}/{len(p.hsi_signals)} have owner.",
        recommended_action="Identify owner (HW or SW) for all signals.",
        confidence="High",
    )


def hsia_5_integrity_protection(p: ProbedHsi) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    safety_signals = [s for s in p.hsi_signals if s.asil and s.asil not in ("QM", "—")]
    if not safety_signals:
        return CheckResult(rating="FC", finding="No safety-relevant signals; check vacuously satisfied.", confidence="High")
    with_integrity = [s for s in safety_signals if s.integrity_protection]
    rate = len(with_integrity) / len(safety_signals)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(safety_signals)} safety-relevant signals have integrity protection (Parity/CRC/SECDED/Dual-channel).",
            page_section=f"Sheet '{p.likely_signal_catalog_sheet}', Integrity Protection column",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_integrity)}/{len(safety_signals)} safety-relevant signals have integrity protection.",
        recommended_action="Specify integrity protection mechanism for all safety-relevant signals.",
        confidence="High",
    )


def hsia_6_validity_liveness(p: ProbedHsi) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    safety_signals = [s for s in p.hsi_signals if s.asil and s.asil not in ("QM", "—")]
    if not safety_signals:
        return CheckResult(rating="FC", finding="No safety-relevant signals; check vacuously satisfied.", confidence="High")
    with_validity = [s for s in safety_signals if s.validity_bit]
    rate = len(with_validity) / len(safety_signals)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(safety_signals)} safety-relevant signals have validity bit or liveness counter.",
            page_section=f"Sheet '{p.likely_signal_catalog_sheet}', Validity Bit column",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_validity)}/{len(safety_signals)} have validity indicator.",
        recommended_action="Add validity bit or liveness counter for all safety-relevant signals.",
        confidence="High",
    )


def hsia_7_fsr_traceability(p: ProbedHsi) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    with_fsr = [s for s in p.hsi_signals if s.linked_fsr]
    rate = len(with_fsr) / len(p.hsi_signals)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All signals have linked FSR_ID for traceability.",
            page_section=f"Sheet '{p.likely_signal_catalog_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_fsr)}/{len(p.hsi_signals)} signals linked to FSR.",
        recommended_action="Link all signals to FSR (Functional Safety Requirement) for traceability.",
        confidence="High",
    )


def hsia_8_timing_specified(p: ProbedHsi) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    if len(p.timing_rows) >= len(p.hsi_signals) * 0.8:
        return CheckResult(
            rating="FC",
            finding=f"Timing specification rows cover {len(p.timing_rows)} signals.",
            page_section=f"Sheet '{p.likely_timing_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.timing_rows)} timing rows for {len(p.hsi_signals)} signals.",
        recommended_action="Specify sample rate, max age, and latency budget for all signals.",
        confidence="High",
    )


def hsia_9_failure_modes_documented(p: ProbedHsi) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    if len(p.failure_mode_rows) >= len(p.hsi_signals):
        return CheckResult(
            rating="FC",
            finding=f"{len(p.failure_mode_rows)} failure mode rows documented.",
            page_section=f"Sheet '{p.likely_failure_modes_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.failure_mode_rows)} failure mode rows for {len(p.hsi_signals)} signals.",
        recommended_action="Document failure modes and reactions for all signals.",
        confidence="High",
    )


def hsia_10_sw_reaction_specified(p: ProbedHsi) -> CheckResult:
    if not p.failure_mode_rows:
        return CheckResult(rating="NO", finding="No failure mode rows found.", recommended_action="Add failure modes.", confidence="High")
    with_reaction = [f for f in p.failure_mode_rows if f.reaction]
    rate = len(with_reaction) / len(p.failure_mode_rows)
    if rate >= 0.95:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.failure_mode_rows)} failure mode rows have SW reaction specified.",
            page_section=f"Sheet '{p.likely_failure_modes_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_reaction)}/{len(p.failure_mode_rows)} have SW reaction.",
        recommended_action="Specify SW reaction for all failure modes.",
        confidence="High",
    )


def hsia_11_init_sequence(p: ProbedHsi) -> CheckResult:
    if p.init_sequence:
        return draft(
            f"Initialization sequence documented: {p.init_sequence}. Reviewer to verify HW BIST and SW startup checks.",
            page_section=f"Sheet '{p.likely_init_seq_sheet}'",
        )
    return CheckResult(
        rating="NO",
        finding="No Initialization Sequence tab found.",
        recommended_action="Add Initialization Sequence tab with HW BIST and SW startup check procedures.",
        confidence="High",
    )


def hsia_12_xref_coverage(p: ProbedHsi) -> CheckResult:
    if p.xref_table:
        return draft(
            f"Cross-reference table present: {p.xref_table}. Reviewer to verify signal coverage and no orphans.",
            page_section=f"Sheet '{p.likely_xref_sheet}'",
        )
    return CheckResult(
        rating="PC",
        finding="No Cross-Reference tab detected.",
        recommended_action="Add Cross-Reference tab covering all signals (no orphans).",
        confidence="High",
    )


def hsia_13_test_cases_defined(p: ProbedHsi) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    if len(p.test_case_rows) >= len(p.hsi_signals):
        return CheckResult(
            rating="FC",
            finding=f"{len(p.test_case_rows)} test cases defined (nominal, fault injection, boundary, timing).",
            page_section=f"Sheet '{p.likely_test_cases_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.test_case_rows)} test cases for {len(p.hsi_signals)} signals.",
        recommended_action="Define test cases (nominal, fault injection, boundary, timing) for all signals.",
        confidence="High",
    )


def hsia_14_asil_allocation(p: ProbedHsi) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    safety_signals = [s for s in p.hsi_signals if s.asil and s.asil not in ("QM", "—")]
    if len(safety_signals) > 0 and len(safety_signals) / len(p.hsi_signals) >= 0.05:
        return CheckResult(
            rating="FC",
            finding=f"ASIL allocation verified: {len(safety_signals)} safety-relevant signals identified and allocated.",
            page_section=f"Sheet '{p.likely_signal_catalog_sheet}'",
            confidence="High",
        )
    return draft(
        f"{len(safety_signals)} signals have ASIL >= A. Reviewer to confirm completeness of safety allocation.",
        page_section=f"Sheet '{p.likely_signal_catalog_sheet}'",
    )


# ---------------------------------------------------------------------------
# Verification Assessment — 5 HARA-specific items
# ---------------------------------------------------------------------------

def va_1_register_map_coverage(p: ProbedHsi) -> CheckResult:
    if len(p.register_map_rows) >= 8:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.register_map_rows)} register map rows; comprehensive HW memory layout.",
            confidence="High",
        )
    return draft(
        f"Register map has {len(p.register_map_rows)} rows. Reviewer to confirm against HW architecture specification.",
    )


def va_2_timing_budget_adequacy(p: ProbedHsi) -> CheckResult:
    if len(p.timing_rows) > 0:
        with_latency = [t for t in p.timing_rows if t.latency_budget]
        if len(with_latency) >= len(p.timing_rows) * 0.8:
            return CheckResult(
                rating="FC",
                finding=f"Latency budgets specified for {len(with_latency)}/{len(p.timing_rows)} signals.",
                confidence="High",
            )
        return draft(
            f"Timing specification incomplete. {len(with_latency)}/{len(p.timing_rows)} have latency budgets. Reviewer to verify adequacy.",
        )
    return CheckResult(rating="NO", finding="No timing specification rows.", recommended_action="Populate Timing Specification tab.", confidence="High")


def va_3_mcu_hsi_consistency(p: ProbedHsi) -> CheckResult:
    return draft(
        "Consistency between MCU HSI specification and HW architecture cannot be verified from xlsx alone.",
        action="Confirm HSI specification aligns with MCU datasheet and hardware design documents.",
    )


def va_4_signal_integrity_verification(p: ProbedHsi) -> CheckResult:
    return draft(
        "Integrity protection mechanisms must be verified against TSC test cases and safety mechanisms specification.",
        action="Cross-reference with TSC Test Cases and Safety Mechanisms tabs.",
    )


def va_5_diagnostics_strategy(p: ProbedHsi) -> CheckResult:
    return draft(
        "Diagnostics and error handling strategy for HSI faults should be verified against FTA and safety architecture.",
        action="Review against FMEA, FSC, and TSC for completeness of fault reaction.",
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
    verify: Callable[[ProbedHsi], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review
    CheckDef("1",  "CR", "Document Quality", "Is the document structured in a clear manner?", "Shall", cr_01_structured),
    CheckDef("2",  "CR", "Document Quality", "On creation date, was the latest template available used?", "Should", cr_02_template),
    CheckDef("3",  "CR", "Document Quality", "Does document structure facilitate search (TOC, index, cross-references)?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does the title cover the scope of the content?", "Shall", cr_04a_title_scope),
    CheckDef("4b", "CR", "Document Quality", "Are the author and approver(s) listed?", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Document Quality", "Is there a unique identification for each revision?", "Shall", cr_04c_unique_revision),
    CheckDef("4d", "CR", "Document Quality", "Is there a change history available?", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Quality", "Is the status of the work product provided?", "Shall", cr_04e_status),
    CheckDef("5",  "CR", "Document Quality", "Is the current applicable revision clearly identifiable?", "Shall", cr_05_current_revision),
    CheckDef("6",  "CR", "Document Quality", "Is the document under configuration and change management?", "Shall", cr_06_config_mgmt),
    CheckDef("7",  "CR", "Document Quality", "Are the header and footer updated?", "Should", cr_07_header_footer),
    CheckDef("8",  "CR", "Document Quality", "Does this document contain a correct table of contents?", "Shall", cr_08_toc),
    CheckDef("9",  "CR", "Document Quality", "Does the Reference Table list all references?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "Have all sections of the Work Product been completed?", "Should", cr_10_sections_complete),

    # HSI Assessment
    CheckDef("1",  "HSIA", "HSI Signal Catalog", "Is the HSI signal catalog populated (count > 0)?", "Shall", hsia_1_signals_populated),
    CheckDef("2",  "HSIA", "Signal Attributes", "Does each signal have direction specified (HW->SW or SW->HW)?", "Shall", hsia_2_signal_direction),
    CheckDef("3",  "HSIA", "Signal Attributes", "Does each signal have bit width / encoding specified?", "Shall", hsia_3_encoding_specified),
    CheckDef("4",  "HSIA", "Signal Attributes", "Is each signal owner identified (HW or SW)?", "Shall", hsia_4_owner_identified),
    CheckDef("5",  "HSIA", "Integrity and Safety", "Do safety-relevant signals have integrity protection (Parity/CRC/SECDED/Dual-channel)?", "Shall", hsia_5_integrity_protection),
    CheckDef("6",  "HSIA", "Integrity and Safety", "Do safety-relevant signals have companion validity bit or liveness counter?", "Shall", hsia_6_validity_liveness),
    CheckDef("7",  "HSIA", "Traceability", "Does each signal have linked FSR_ID for traceability?", "Shall", hsia_7_fsr_traceability),
    CheckDef("8",  "HSIA", "Timing", "Does each signal have timing specification (sample rate, max age, latency)?", "Shall", hsia_8_timing_specified),
    CheckDef("9",  "HSIA", "Failure Modes", "Does each signal have failure modes documented?", "Shall", hsia_9_failure_modes_documented),
    CheckDef("10", "HSIA", "Failure Modes", "Does each signal have SW reaction specified for fault scenarios?", "Shall", hsia_10_sw_reaction_specified),
    CheckDef("11", "HSIA", "Initialization", "Is initialization sequence documented (HW BIST + SW startup checks)?", "Shall", hsia_11_init_sequence),
    CheckDef("12", "HSIA", "Cross-Reference", "Does cross-reference table cover all signals (no orphans)?", "Shall", hsia_12_xref_coverage),
    CheckDef("13", "HSIA", "Test Cases", "Are test cases defined per signal (nominal, fault, boundary, timing)?", "Shall", hsia_13_test_cases_defined),
    CheckDef("14", "HSIA", "ASIL", "Is ASIL allocated to each safety-relevant signal?", "Shall", hsia_14_asil_allocation),

    # Verification Assessment
    CheckDef("1",  "VA", "HSI Verification", "Register map completeness with respect to MCU memory layout?", "Shall", va_1_register_map_coverage),
    CheckDef("2",  "VA", "HSI Verification", "Timing budget adequacy (sample rate, max age, latency)?", "Shall", va_2_timing_budget_adequacy),
    CheckDef("3",  "VA", "HSI Verification", "Consistency between MCU HSI and hardware architecture specification?", "Shall", va_3_mcu_hsi_consistency),
    CheckDef("4",  "VA", "HSI Verification", "Verification of signal integrity mechanisms against TSC test cases?", "Shall", va_4_signal_integrity_verification),
    CheckDef("5",  "VA", "HSI Verification", "Diagnostics and error handling strategy for HSI faults?", "Shall", va_5_diagnostics_strategy),
]
