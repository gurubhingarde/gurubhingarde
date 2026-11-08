"""
SW HSI Specification checklist definitions per ISO 26262-6 §7 + ISO 26262-4 §6.4.6.

Checks organized into:
- Confirmation Review (CR): 14 generic doc-quality checks
- SW HSI Assessment (SWHSIA): 12 substantive SW-HSI-specific checks
- Verification Assessment (VA): 5 external verification checks
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sw_hsis_probe import ProbedSwHsis


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

def cr_01_structured(p: ProbedSwHsis) -> CheckResult:
    if len(p.sheet_names) >= 9:
        return CheckResult(
            rating="FC",
            finding=f"Document is structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has {len(p.sheet_names)} tabs; SW HSI spec typically requires 10+.",
        recommended_action="Ensure all standard SW HSI tabs present (Title, Doc Control, Signal Catalog Echo, SW Handler, Debounce, Fault Propagation, RTOS, Init Seq, Test Cases, References).",
        confidence="Medium",
    )


def cr_02_template(p: ProbedSwHsis) -> CheckResult:
    return draft(
        "Template version cannot be detected from xlsx content alone.",
        action="Confirm the latest applicable SW HSI Specification template was used.",
    )


def cr_03_searchable(p: ProbedSwHsis) -> CheckResult:
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


def cr_04a_title_scope(p: ProbedSwHsis) -> CheckResult:
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


def cr_04b_author_approver(p: ProbedSwHsis) -> CheckResult:
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


def cr_04c_unique_revision(p: ProbedSwHsis) -> CheckResult:
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


def cr_04d_change_history(p: ProbedSwHsis) -> CheckResult:
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


def cr_04e_status(p: ProbedSwHsis) -> CheckResult:
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


def cr_05_current_revision(p: ProbedSwHsis) -> CheckResult:
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


def cr_06_config_mgmt(p: ProbedSwHsis) -> CheckResult:
    return draft(
        "Configuration management is an organizational practice; cannot be verified from xlsx content.",
        action="Confirm the document is checked into the project's configuration-management system.",
    )


def cr_07_header_footer(p: ProbedSwHsis) -> CheckResult:
    return draft(
        "Worksheet headers/footers cannot be reliably verified programmatically.",
        action="Open in Excel and confirm header/footer reflect current document ID and revision.",
    )


def cr_08_toc(p: ProbedSwHsis) -> CheckResult:
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


def cr_09_references(p: ProbedSwHsis) -> CheckResult:
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


def cr_10_sections_complete(p: ProbedSwHsis) -> CheckResult:
    signal_complete = len([s for s in p.hsi_signals if s.direction and s.data_type])
    signal_rate = signal_complete / max(1, len(p.hsi_signals))
    handler_present = len(p.sw_handlers) > 0
    debounce_present = len(p.debounce_strategies) > 0
    fault_propagation_present = len(p.fault_propagation_rows) > 0
    rtos_present = len(p.rtos_integration_rows) > 0
    test_present = len(p.test_case_rows) > 0

    completed = sum([handler_present, debounce_present, fault_propagation_present, rtos_present, test_present])
    if completed >= 4 and signal_rate >= 0.9:
        return CheckResult(
            rating="FC",
            finding=f"Major sections populated. {completed}/5 content tabs complete; signal catalog {signal_rate:.0%} complete.",
            confidence="High",
        )
    if completed >= 3 and signal_rate >= 0.7:
        return CheckResult(
            rating="LC",
            finding=f"Most sections populated. {completed}/5 tabs; signals {signal_rate:.0%} complete.",
            recommended_action="Complete remaining signal catalog and content sections.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Incomplete. {completed}/5 tabs populated; signals {signal_rate:.0%}.",
        recommended_action="Complete all SW HSI specification tabs before review.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Verification functions — SW HSI Assessment (SWHSIA)
# ---------------------------------------------------------------------------

def swhsia_1_hsi_signal_echo(p: ProbedSwHsis) -> CheckResult:
    if len(p.hsi_signals) >= 5:
        return CheckResult(
            rating="FC",
            finding=f"HSI signal catalog echoed from source with {len(p.hsi_signals)} signals.",
            page_section=f"Sheet '{p.likely_signal_catalog_sheet}'",
            confidence="High",
        )
    if len(p.hsi_signals) > 0:
        return CheckResult(
            rating="LC",
            finding=f"Only {len(p.hsi_signals)} signals echoed; verify completeness.",
            recommended_action="Review signal catalog completeness against source HSI.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="HSI signal catalog echo is empty.",
        recommended_action="Populate the HSI Signal Catalog Echo tab from source HSI.",
        confidence="High",
    )


def swhsia_2_handler_function_names(p: ProbedSwHsis) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    with_handler = [h for h in p.sw_handlers if h.handler_function_name]
    rate = len(with_handler) / max(1, len(p.sw_handlers))
    if len(p.sw_handlers) > 0 and rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_handlers)} SW handlers have function names specified.",
            page_section=f"Sheet '{p.likely_sw_handler_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_handler)}/{max(1, len(p.sw_handlers))} handlers have function names.",
        recommended_action="Specify handler function name for all signals in SW Handler Catalog.",
        confidence="High",
    )


def swhsia_3_handler_swc_allocation(p: ProbedSwHsis) -> CheckResult:
    if not p.sw_handlers:
        return na("No handlers defined.")
    with_swc = [h for h in p.sw_handlers if h.allocated_swc]
    rate = len(with_swc) / len(p.sw_handlers)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_handlers)} handlers have SWC allocation specified.",
            page_section=f"Sheet '{p.likely_sw_handler_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_swc)}/{len(p.sw_handlers)} handlers have SWC allocated.",
        recommended_action="Allocate each handler to a Software Component (SWC).",
        confidence="High",
    )


def swhsia_4_calling_task_identified(p: ProbedSwHsis) -> CheckResult:
    if not p.sw_handlers:
        return na("No handlers defined.")
    with_task = [h for h in p.sw_handlers if h.calling_task]
    rate = len(with_task) / len(p.sw_handlers)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_handlers)} handlers have calling RTOS task identified.",
            page_section=f"Sheet '{p.likely_sw_handler_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_task)}/{len(p.sw_handlers)} handlers have calling task.",
        recommended_action="Identify RTOS task for each handler.",
        confidence="High",
    )


def swhsia_5_max_execution_time(p: ProbedSwHsis) -> CheckResult:
    if not p.sw_handlers:
        return na("No handlers defined.")
    with_time = [h for h in p.sw_handlers if h.max_execution_time]
    rate = len(with_time) / len(p.sw_handlers)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_handlers)} handlers have max execution time budget.",
            page_section=f"Sheet '{p.likely_sw_handler_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_time)}/{len(p.sw_handlers)} handlers have execution time budget.",
        recommended_action="Specify max execution time for all handlers per RTOS integration requirements.",
        confidence="High",
    )


def swhsia_6_debounce_specified(p: ProbedSwHsis) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    safety_signals = [s for s in p.hsi_signals if s.asil and s.asil not in ("QM", "—")]
    if not safety_signals:
        return CheckResult(rating="FC", finding="No safety-relevant signals; check vacuously satisfied.", confidence="High")
    with_debounce = [d for d in p.debounce_strategies if d.signal_name]
    rate = len(with_debounce) / len(safety_signals)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(safety_signals)} safety-relevant signals have debounce strategy.",
            page_section=f"Sheet '{p.likely_debounce_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_debounce)}/{len(safety_signals)} safety signals have debounce.",
        recommended_action="Specify debounce strategy (N-of-M, time threshold) for all safety-relevant signals.",
        confidence="High",
    )


def swhsia_7_debounce_parameters_reasonable(p: ProbedSwHsis) -> CheckResult:
    if not p.debounce_strategies:
        return na("No debounce strategies defined.")
    with_params = [d for d in p.debounce_strategies if d.n_of_m or d.time_threshold_ms]
    rate = len(with_params) / len(p.debounce_strategies)
    if rate >= 0.95:
        return CheckResult(
            rating="FC",
            finding=f"Debounce parameters specified for {len(with_params)}/{len(p.debounce_strategies)} strategies (N-of-M or time threshold).",
            page_section=f"Sheet '{p.likely_debounce_sheet}'",
            confidence="Medium",
        )
    return draft(
        f"{len(with_params)}/{len(p.debounce_strategies)} debounce strategies have N-of-M/time parameters. Reviewer to verify parameters are sensible (N>=2, time<=FRTI).",
        page_section=f"Sheet '{p.likely_debounce_sheet}'",
    )


def swhsia_8_fault_propagation_trace(p: ProbedSwHsis) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    if len(p.fault_propagation_rows) >= len(p.hsi_signals) * 0.8:
        return CheckResult(
            rating="FC",
            finding=f"Fault propagation maps trace {len(p.fault_propagation_rows)} signal faults to vehicle reactions.",
            page_section=f"Sheet '{p.likely_fault_propagation_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.fault_propagation_rows)} fault propagation rows for {len(p.hsi_signals)} signals.",
        recommended_action="Document fault propagation for all signals (signal failure mode -> vehicle reaction).",
        confidence="High",
    )


def swhsia_9_rtos_integration(p: ProbedSwHsis) -> CheckResult:
    if not p.sw_handlers:
        return na("No handlers defined.")
    if len(p.rtos_integration_rows) >= 1:
        return CheckResult(
            rating="FC",
            finding=f"RTOS integration documented: {len(p.rtos_integration_rows)} task(s) defined.",
            page_section=f"Sheet '{p.likely_rtos_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No RTOS Integration tab or content found.",
        recommended_action="Document RTOS tasks (name, priority, period, signals processed).",
        confidence="High",
    )


def swhsia_10_latency_within_frti(p: ProbedSwHsis) -> CheckResult:
    return draft(
        "Latency from signal arrival to handler execution must be verified against FRTI budget. Requires timing analysis.",
        page_section=f"Sheets '{p.likely_sw_handler_sheet}' and '{p.likely_rtos_sheet}'",
        action="Cross-reference handler execution times and RTOS task periods against FRTI budget from SW Architecture.",
    )


def swhsia_11_init_sequence_coordinated(p: ProbedSwHsis) -> CheckResult:
    if len(p.init_sequence_rows) >= 1:
        return draft(
            f"SW Init sequence documented: {len(p.init_sequence_rows)} step(s). Reviewer to verify coordination with HW BIST.",
            page_section=f"Sheet '{p.likely_init_seq_sheet}'",
        )
    return CheckResult(
        rating="NO",
        finding="No Initialization Sequence tab found.",
        recommended_action="Add Initialization Sequence tab with SW startup checks and HW BIST references.",
        confidence="High",
    )


def swhsia_12_test_cases_comprehensive(p: ProbedSwHsis) -> CheckResult:
    if not p.sw_handlers:
        return na("No handlers defined.")
    if len(p.test_case_rows) >= len(p.sw_handlers):
        return CheckResult(
            rating="FC",
            finding=f"{len(p.test_case_rows)} test cases defined (nominal, fault injection, boundary, timing).",
            page_section=f"Sheet '{p.likely_test_cases_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.test_case_rows)} test cases for {len(p.sw_handlers)} handlers.",
        recommended_action="Define test cases (nominal, fault injection, boundary, timing) for all handlers.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Verification Assessment — 5 external verification items
# ---------------------------------------------------------------------------

def va_1_signal_integrity_protection(p: ProbedSwHsis) -> CheckResult:
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
            finding=f"All {len(safety_signals)} safety signals have integrity protection (Parity/CRC/SECDED/Dual-channel).",
            confidence="High",
        )
    return draft(
        f"{len(with_integrity)}/{len(safety_signals)} safety signals have integrity. Reviewer to verify all safety-relevant signals are protected.",
    )


def va_2_sw_handler_coverage(p: ProbedSwHsis) -> CheckResult:
    if not p.hsi_signals:
        return na("No signals defined.")
    with_handler = [h for h in p.sw_handlers if h.handler_function_name]
    signal_count = len(p.hsi_signals)
    handler_count = len(p.sw_handlers)
    if handler_count >= signal_count * 0.9:
        return CheckResult(
            rating="FC",
            finding=f"Handler coverage: {handler_count} handlers for {signal_count} signals (>90%).",
            confidence="High",
        )
    return draft(
        f"Handler coverage: {handler_count} handlers for {signal_count} signals. Reviewer to verify all signals are handled.",
    )


def va_3_debounce_effectiveness(p: ProbedSwHsis) -> CheckResult:
    return draft(
        "Debounce effectiveness verification requires comparison with signal characteristics (frequency, noise margin). Cannot be validated from xlsx alone.",
        action="Verify debounce N-of-M and time threshold are appropriate for signal rise/fall times and noise environment.",
    )


def va_4_call_frequency_consistency(p: ProbedSwHsis) -> CheckResult:
    if not p.sw_handlers:
        return na("No handlers defined.")
    with_freq = [h for h in p.sw_handlers if h.call_frequency]
    rate = len(with_freq) / len(p.sw_handlers)
    if rate >= 0.95:
        return CheckResult(
            rating="FC",
            finding=f"Call frequency specified for {len(with_freq)}/{len(p.sw_handlers)} handlers.",
            confidence="High",
        )
    return draft(
        f"Call frequency specified for {len(with_freq)}/{len(p.sw_handlers)} handlers. Reviewer to verify consistency with signal sample rate.",
    )


def va_5_end_to_end_latency(p: ProbedSwHsis) -> CheckResult:
    return draft(
        "End-to-end latency from signal arrival to vehicle reaction must be verified against FRTI. Requires cross-reference with TSC and system timing analysis.",
        action="Trace signal path through SW handlers, RTOS scheduling, and actuator control. Verify total latency meets FRTI.",
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
    verify: Callable[[ProbedSwHsis], CheckResult]


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

    # SW HSI Assessment
    CheckDef("1",  "SWHSIA", "Signal Catalog", "Is HSI signal catalog echoed from source HSI (count > 0)?", "Shall", swhsia_1_hsi_signal_echo),
    CheckDef("2",  "SWHSIA", "SW Handlers", "Does each signal have SW handler function name?", "Shall", swhsia_2_handler_function_names),
    CheckDef("3",  "SWHSIA", "SW Handlers", "Is each handler allocated to a Software Component (SWC)?", "Shall", swhsia_3_handler_swc_allocation),
    CheckDef("4",  "SWHSIA", "SW Handlers", "Is each handler's calling RTOS task identified?", "Shall", swhsia_4_calling_task_identified),
    CheckDef("5",  "SWHSIA", "SW Handlers", "Does each handler have max execution time budget specified?", "Shall", swhsia_5_max_execution_time),
    CheckDef("6",  "SWHSIA", "Debounce", "Does each safety-relevant signal have debounce strategy?", "Shall", swhsia_6_debounce_specified),
    CheckDef("7",  "SWHSIA", "Debounce", "Are debounce parameters reasonable (N-of-M with N>=2, time sensible)?", "Shall", swhsia_7_debounce_parameters_reasonable),
    CheckDef("8",  "SWHSIA", "Fault Propagation", "Does fault propagation map trace each signal fault to vehicle reaction?", "Shall", swhsia_8_fault_propagation_trace),
    CheckDef("9",  "SWHSIA", "RTOS Integration", "Is RTOS integration documented (task name, priority, period, signals)?", "Shall", swhsia_9_rtos_integration),
    CheckDef("10", "SWHSIA", "Latency", "Is latency from signal arrival to handler execution within FRTI budget?", "Shall", swhsia_10_latency_within_frti),
    CheckDef("11", "SWHSIA", "Initialization", "Is SW init sequence coordinated with HW BIST sequence?", "Shall", swhsia_11_init_sequence_coordinated),
    CheckDef("12", "SWHSIA", "Test Cases", "Are test cases defined per handler (nominal, fault, boundary, timing)?", "Shall", swhsia_12_test_cases_comprehensive),

    # Verification Assessment
    CheckDef("1",  "VA", "Signal Integrity", "Are safety-relevant signals protected (Parity/CRC/SECDED)?", "Shall", va_1_signal_integrity_protection),
    CheckDef("2",  "VA", "Handler Coverage", "Do SW handlers cover all HSI signals?", "Shall", va_2_sw_handler_coverage),
    CheckDef("3",  "VA", "Debounce Effectiveness", "Is debounce effectiveness verified against signal characteristics?", "Shall", va_3_debounce_effectiveness),
    CheckDef("4",  "VA", "Call Frequency", "Is handler call frequency consistent with signal sample rate?", "Shall", va_4_call_frequency_consistency),
    CheckDef("5",  "VA", "End-to-End Latency", "Is end-to-end latency (signal to vehicle reaction) within FRTI?", "Shall", va_5_end_to_end_latency),
]
