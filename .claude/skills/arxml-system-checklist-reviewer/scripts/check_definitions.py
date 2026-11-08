"""ARXML system confirmation and technical checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from arxml_probe import ProbedARXML


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding, page_section="", action="(Reviewer to verify and assess)"):
    return CheckResult(rating="", finding="(Auto-suggest, requires reviewer judgment) " + finding,
                      page_section=page_section, recommended_action=action, confidence="Low")


def na(reason):
    return CheckResult(rating="NA", finding=reason, confidence="High")


# =========================================================================
# Confirmation Review Checks (14 generic)
# =========================================================================

def cr_01_structured(p):
    if len(p.sheet_names) >= 10:
        return CheckResult(rating="FC", finding=f"Document is structured into {len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Ensure 13-tab structure.", confidence="Medium")


def cr_02_title(p):
    if p.title:
        return CheckResult(rating="FC", finding=f"Title: '{p.title}'.", confidence="High")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add system title.", confidence="High")


def cr_03_doc_id(p):
    if p.doc_id:
        return CheckResult(rating="FC", finding=f"Document ID: {p.doc_id}.", confidence="High")
    return CheckResult(rating="NO", finding="Document ID missing.", recommended_action="Populate doc_id field.", confidence="High")


def cr_04_revision(p):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision: {p.revision}.", confidence="High")
    return CheckResult(rating="NO", finding="Revision not set.", recommended_action="Set revision.", confidence="High")


def cr_05_author_approver(p):
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    missing = ([] if p.author else ["Author"]) + ([] if p.approver else ["Approver"])
    return CheckResult(rating="NO", finding=f"Missing: {', '.join(missing)}.", recommended_action=f"Populate {', '.join(missing)}.", confidence="High")


def cr_06_revision_history(p):
    if p.revision_history_rows >= 1:
        return CheckResult(rating="FC", finding=f"Revision history: {p.revision_history_rows} entries.", confidence="High")
    return CheckResult(rating="NO", finding="No revision history.", recommended_action="Add revision history.", confidence="High")


def cr_07_system_header(p):
    if p.has_table_of_contents:
        return CheckResult(rating="FC", finding="System Header tab present.", confidence="Medium")
    return CheckResult(rating="PC", finding="System Header not detected.", recommended_action="Add System Header tab.", confidence="Medium")


def cr_08_toc_searchable(p):
    if p.has_table_of_contents:
        return CheckResult(rating="FC", finding="Document structure supports search.", confidence="Medium")
    return CheckResult(rating="PC", finding="TOC missing.", recommended_action="Add navigation tab.", confidence="Medium")


def cr_09_references(p):
    return draft("References section should cite AUTOSAR R22-11+ standard.", action="Confirm AUTOSAR standards cited.")


def cr_10_config_mgmt(p):
    return draft("Configuration management status should be confirmed.", action="Verify CM integration.")


def cr_11_header_footer(p):
    return draft("Header/footer verification requires manual review in Excel.", action="Open workbook and verify headers/footers.")


def cr_12_sections_complete(p):
    if p.ecu_count > 0 and p.signal_count > 0 and p.pdu_count > 0:
        return CheckResult(rating="FC", finding=f"Core sections complete: {p.ecu_count} ECUs, {p.signal_count} signals, {p.pdu_count} PDUs.", confidence="High")
    return CheckResult(rating="PC", finding=f"Partial completion.", recommended_action="Complete all required sections.", confidence="High")


def cr_13_consistency(p):
    if p.signal_to_pdu_map and p.pdu_to_frame_map:
        return CheckResult(rating="FC", finding="Signal-PDU-Frame composition chain verified.", confidence="High")
    return CheckResult(rating="PC", finding="Incomplete composition mapping.", recommended_action="Link all signals to PDUs and PDUs to frames.", confidence="High")


def cr_14_approval_status(p):
    if p.status:
        return CheckResult(rating="FC", finding=f"Status: {p.status}.", confidence="High")
    return CheckResult(rating="NO", finding="Status field empty.", recommended_action="Set approval status.", confidence="High")


# =========================================================================
# Technical Assessment Checks (16 ARXML-specific)
# =========================================================================

def tsa_01_ecu_instances(p):
    if p.ecu_count >= 1:
        return CheckResult(rating="FC", finding=f"{p.ecu_count} ECU instances defined.", confidence="High")
    return CheckResult(rating="NO", finding="No ECU instances.", recommended_action="Define at least one ECU.", confidence="High")


def tsa_02_signal_coverage(p):
    if p.signal_count >= 1:
        return CheckResult(rating="FC", finding=f"{p.signal_count} signals in catalog.", confidence="High")
    return CheckResult(rating="NO", finding="No signals defined.", recommended_action="Populate Signal Catalog.", confidence="High")


def tsa_03_pdu_coverage(p):
    if p.pdu_count >= 1:
        return CheckResult(rating="FC", finding=f"{p.pdu_count} PDUs in catalog.", confidence="High")
    return CheckResult(rating="NO", finding="No PDUs defined.", recommended_action="Populate PDU Catalog.", confidence="High")


def tsa_04_frame_coverage(p):
    if p.frame_count >= 1:
        return CheckResult(rating="FC", finding=f"{p.frame_count} frames in catalog.", confidence="High")
    return CheckResult(rating="NO", finding="No frames defined.", recommended_action="Populate Frame Catalog.", confidence="High")


def tsa_05_signal_to_pdu(p):
    if not p.signal_count:
        return na("No signals.")
    mapped = len(p.signal_to_pdu_map)
    coverage = mapped / max(1, p.signal_count)
    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"All {p.signal_count} signals mapped to PDUs.", confidence="High")
    return CheckResult(rating="PC", finding=f"{mapped}/{p.signal_count} signals mapped.", recommended_action="Map unmapped signals.", confidence="High")


def tsa_06_pdu_to_frame(p):
    if not p.pdu_count:
        return na("No PDUs.")
    mapped = len(p.pdu_to_frame_map)
    coverage = mapped / max(1, p.pdu_count)
    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"All {p.pdu_count} PDUs mapped to frames.", confidence="High")
    return CheckResult(rating="PC", finding=f"{mapped}/{p.pdu_count} PDUs mapped.", recommended_action="Map unmapped PDUs.", confidence="High")


def tsa_07_port_interfaces(p):
    if p.port_interface_count >= 1:
        return CheckResult(rating="FC", finding=f"{p.port_interface_count} port interfaces defined.", confidence="High")
    return CheckResult(rating="PC", finding="No port interfaces.", recommended_action="Define port interfaces for communication.", confidence="Medium")


def tsa_08_port_bindings(p):
    if p.composition_bindings == 0:
        return na("No composition bindings.")
    unbound_pct = (p.unbound_port_interfaces / max(1, p.composition_bindings)) * 100
    if unbound_pct <= 5:
        return CheckResult(rating="FC", finding=f"{p.composition_bindings} bindings; {unbound_pct:.0f}% unbound.", confidence="High")
    return CheckResult(rating="PC", finding=f"{p.unbound_port_interfaces} unbound bindings.", recommended_action="Bind unbound port interfaces.", confidence="High")


def tsa_09_ecu_mappings(p):
    if p.mapping_count >= 1:
        return CheckResult(rating="FC", finding=f"{p.mapping_count} system mappings defined.", confidence="High")
    return CheckResult(rating="PC", finding="No mappings.", recommended_action="Define ECU-to-ECU signal mappings.", confidence="Medium")


def tsa_10_ecu_pairs(p):
    if len(p.ecu_pairs) >= 1:
        return CheckResult(rating="FC", finding=f"{len(p.ecu_pairs)} ECU communication pairs.", confidence="High")
    return CheckResult(rating="PC", finding="No ECU pairs communicating.", recommended_action="Define inter-ECU communication.", confidence="Medium")


def tsa_11_composition_completeness(p):
    return draft(f"Composition refs: {p.composition_bindings} bindings detected.", action="Verify all SWC-port-interface bindings.")


def tsa_12_trigger_events(p):
    return draft("Trigger and event mappings require manual review for correctness.", action="Verify timing and event trigger constraints.")


def tsa_13_data_types(p):
    return draft("Data type definitions should align with AUTOSAR base types.", action="Confirm all signals use valid AUTOSAR types.")


def tsa_14_communication_stack(p):
    return draft("Communication connector protocols (CAN, LIN, etc.) should be defined.", action="Verify protocol selections and baudrates.")


def tsa_15_boundary_conditions(p):
    return draft("Signal value ranges and limits should be specified.", action="Populate min/max/default values in Signal Catalog.")


def tsa_16_overall_readiness(p):
    all_present = (p.ecu_count > 0 and p.signal_count > 0 and p.pdu_count > 0 and
                   p.frame_count > 0 and p.port_interface_count > 0)
    if all_present:
        return CheckResult(rating="FC", finding="All core ARXML elements present and interconnected.", confidence="High")
    return CheckResult(rating="PC", finding="Some core elements missing.", recommended_action="Complete missing sections.", confidence="High")


# =========================================================================
# Check Definitions
# =========================================================================

@dataclass
class CheckDef:
    code: str
    category: str
    title: str
    obligation: str
    checker: Callable[[ProbedARXML], CheckResult]


CHECKS: list[CheckDef] = [
    CheckDef("CR-01", "Confirmation", "Document Structure", "Should", cr_01_structured),
    CheckDef("CR-02", "Confirmation", "System Title", "Shall", cr_02_title),
    CheckDef("CR-03", "Confirmation", "Document ID", "Shall", cr_03_doc_id),
    CheckDef("CR-04", "Confirmation", "Revision Control", "Shall", cr_04_revision),
    CheckDef("CR-05", "Confirmation", "Author and Approver", "Shall", cr_05_author_approver),
    CheckDef("CR-06", "Confirmation", "Revision History", "Should", cr_06_revision_history),
    CheckDef("CR-07", "Confirmation", "System Scope Definition", "Should", cr_07_system_header),
    CheckDef("CR-08", "Confirmation", "Searchability", "Should", cr_08_toc_searchable),
    CheckDef("CR-09", "Confirmation", "Standards References", "Should", cr_09_references),
    CheckDef("CR-10", "Confirmation", "Configuration Management", "Should", cr_10_config_mgmt),
    CheckDef("CR-11", "Confirmation", "Header/Footer Info", "Should", cr_11_header_footer),
    CheckDef("CR-12", "Confirmation", "Sections Populated", "Shall", cr_12_sections_complete),
    CheckDef("CR-13", "Confirmation", "Internal Consistency", "Shall", cr_13_consistency),
    CheckDef("CR-14", "Confirmation", "Approval Status", "Shall", cr_14_approval_status),

    CheckDef("TA-01", "Technical", "ECU Instances", "Shall", tsa_01_ecu_instances),
    CheckDef("TA-02", "Technical", "Signal Catalog", "Shall", tsa_02_signal_coverage),
    CheckDef("TA-03", "Technical", "PDU Catalog", "Shall", tsa_03_pdu_coverage),
    CheckDef("TA-04", "Technical", "Frame Catalog", "Shall", tsa_04_frame_coverage),
    CheckDef("TA-05", "Technical", "Signal-to-PDU Mapping", "Shall", tsa_05_signal_to_pdu),
    CheckDef("TA-06", "Technical", "PDU-to-Frame Mapping", "Shall", tsa_06_pdu_to_frame),
    CheckDef("TA-07", "Technical", "Port Interfaces", "Should", tsa_07_port_interfaces),
    CheckDef("TA-08", "Technical", "Port Interface Bindings", "Should", tsa_08_port_bindings),
    CheckDef("TA-09", "Technical", "System Mappings", "Should", tsa_09_ecu_mappings),
    CheckDef("TA-10", "Technical", "ECU Communication Pairs", "Should", tsa_10_ecu_pairs),
    CheckDef("TA-11", "Technical", "Composition References", "Should", tsa_11_composition_completeness),
    CheckDef("TA-12", "Technical", "Trigger/Event Mappings", "Should", tsa_12_trigger_events),
    CheckDef("TA-13", "Technical", "Data Type Definitions", "Should", tsa_13_data_types),
    CheckDef("TA-14", "Technical", "Communication Stack", "Should", tsa_14_communication_stack),
    CheckDef("TA-15", "Technical", "Boundary Conditions", "Should", tsa_15_boundary_conditions),
    CheckDef("TA-16", "Technical", "Overall Readiness", "Shall", tsa_16_overall_readiness),
]
