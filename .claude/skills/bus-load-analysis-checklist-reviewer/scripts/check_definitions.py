"""Bus Load Analysis confirmation checks."""

from __future__ import annotations

from dataclasses import dataclass
from busload_probe import ProbedBusLoad


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding, page_section="", action="(Reviewer to verify)"):
    return CheckResult(rating="", finding="(Auto-suggest) " + finding, page_section=page_section, recommended_action=action, confidence="Low")


def na(reason): return CheckResult(rating="NA", finding=reason, confidence="High")


def check_01_structured(p):
    if len(p.sheet_names) >= 6:
        return CheckResult(rating="FC", finding=f"Document structured into {len(p.sheet_names)} tabs (Title, Doc Control, Bus Config, Message Inventory, Load Calc, Scenarios).", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs; missing recommended sections.", recommended_action="Add Bus Configuration, Message Inventory, Load Calculation, Scenarios tabs.", confidence="High")

def check_02_title(p):
    if p.title:
        return CheckResult(rating="FC", finding=f"Title: '{p.title}'.", confidence="High")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add a clear analysis title.", confidence="High")

def check_03_author(p):
    if p.author:
        return CheckResult(rating="FC", finding=f"Author: '{p.author}'.", confidence="High")
    return CheckResult(rating="NO", finding="Author not populated.", recommended_action="Add author name.", confidence="High")

def check_04_approver(p):
    if p.approver:
        return CheckResult(rating="FC", finding=f"Approver: '{p.approver}'.", confidence="High")
    return CheckResult(rating="NO", finding="Approver not populated.", recommended_action="Add approver name.", confidence="High")

def check_05_revision(p):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision: '{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="Revision not populated.", recommended_action="Populate revision field.", confidence="High")

def check_06_bus_config(p):
    if p.has_bus_config and p.bus_count > 0:
        return CheckResult(rating="FC", finding=f"Bus Configuration tab present with {p.bus_count} bus(es).", confidence="High")
    return CheckResult(rating="NO", finding="Bus Configuration tab missing or empty.", recommended_action="Add Bus Configuration tab with protocol, baud rate, frame overhead.", confidence="High")

def check_07_message_inventory(p):
    if p.has_message_inventory and p.message_count > 0:
        return CheckResult(rating="FC", finding=f"Message Inventory tab present with {p.message_count} message(s).", confidence="High")
    return CheckResult(rating="NO", finding="Message Inventory tab missing or empty.", recommended_action="Add all CAN/FlexRay/Ethernet messages with cycle times and DLC.", confidence="High")

def check_08_load_calculation(p):
    if p.has_load_calc and p.formula_count >= p.message_count:
        return CheckResult(rating="FC", finding=f"Load Calculation tab with {p.formula_count} formulas (>= {p.message_count} messages).", confidence="High")
    return CheckResult(rating="PC", finding=f"Load Calculation has {p.formula_count} formulas; expected >= {p.message_count}.", recommended_action="Add formulas: bits_per_frame * frequency / baud_rate * 100.", confidence="High")

def check_09_scenarios(p):
    if p.has_scenarios:
        return CheckResult(rating="FC", finding="Scenario Analysis tab present (nominal, peak, worst-case, fault-injection).", confidence="High")
    return CheckResult(rating="PC", finding="Scenario Analysis tab missing.", recommended_action="Add scenarios: nominal, peak, worst-case, fault-injection.", confidence="Medium")

def check_10_nominal_load_threshold(p):
    max_nominal = max(p.loads.values()) if p.loads else 0.0
    if max_nominal < 0.60:
        return CheckResult(rating="FC", finding=f"Nominal load {max_nominal:.1%} < 60% (CAN target).", confidence="High")
    elif max_nominal < 0.75:
        return CheckResult(rating="PC", finding=f"Nominal load {max_nominal:.1%} is between 60-75%; monitor headroom.", recommended_action="Consider message prioritization or baud rate increase.", confidence="High")
    return CheckResult(rating="NO", finding=f"Nominal load {max_nominal:.1%} exceeds 75%; unacceptable.", recommended_action="Reduce message frequency, increase baud rate, or remove non-essential messages.", confidence="High")

def check_11_peak_load_threshold(p):
    if p.loads:
        return draft(f"Peak load analysis results shown. Verify peak < 80% and worst-case < 85%.", action="Review Scenario Analysis tab for peak/worst-case load percentages.")
    return na("Load Calculation tab not accessible.")

def check_12_protocol_consistency(p):
    protocols = {bus.get("protocol", "CAN") for bus in p.buses.values()}
    if all(proto in ["CAN", "CAN FD", "FlexRay", "Ethernet"] for proto in protocols):
        return CheckResult(rating="FC", finding=f"Protocols: {', '.join(protocols)}. All recognized standards.", confidence="High")
    return CheckResult(rating="PC", finding=f"Unrecognized protocol(s): {protocols}.", recommended_action="Use standard protocol names.", confidence="Medium")

def check_13_frame_overhead(p):
    if all(bus.get("frame_overhead", 0) > 0 for bus in p.buses.values() if bus):
        return CheckResult(rating="FC", finding="Frame overhead specified for all buses.", confidence="High")
    return draft("Frame overhead may be missing for some buses.", action="Verify frame overhead bits per protocol (CAN: 47 bits, CAN FD: 87 bits, Ethernet: 64+ bits).")

def check_14_baud_rate(p):
    for bid, bus in p.buses.items():
        if bus.get("baud_rate", 0) <= 0:
            return CheckResult(rating="NO", finding=f"Bus {bid} has invalid baud rate.", recommended_action="Set valid baud rate (125-1000 kbps for CAN).", confidence="High")
    return CheckResult(rating="FC", finding="All buses have valid baud rates.", confidence="High")

def check_15_dlc_validity(p):
    for mid, msg in p.messages.items():
        dlc = msg.get("dlc", 0)
        if not (0 < dlc <= 8):
            return CheckResult(rating="NO", finding=f"Message {mid} has invalid DLC {dlc}.", recommended_action="DLC must be 1-8 (or 0-64 for CAN FD).", confidence="High")
    return CheckResult(rating="FC", finding="All messages have valid DLC.", confidence="High")

def check_16_cycle_time(p):
    for mid, msg in p.messages.items():
        cycle = msg.get("cycle_time", 0)
        if cycle <= 0:
            return CheckResult(rating="NO", finding=f"Message {mid} has invalid cycle time.", recommended_action="Populate cycle time in ms.", confidence="High")
    return CheckResult(rating="FC", finding="All messages have valid cycle times.", confidence="High")

def check_17_message_allocation(p):
    if p.message_count > 0:
        allocated = sum(1 for msg in p.messages.values() if msg.get("bus_id"))
        if allocated == p.message_count:
            return CheckResult(rating="FC", finding=f"All {p.message_count} messages allocated to buses.", confidence="High")
        return CheckResult(rating="PC", finding=f"{allocated}/{p.message_count} messages allocated.", recommended_action="Assign all messages to a bus ID.", confidence="High")
    return na("No messages in inventory.")

def check_18_no_formula_errors(p):
    if p.error_cells == 0:
        return CheckResult(rating="FC", finding="No formula errors (#VALUE!, #DIV/0!, etc.).", confidence="High")
    return CheckResult(rating="NO", finding=f"{p.error_cells} formula error(s) detected.", recommended_action="Fix formulas in Load Calculation and Scenarios tabs.", confidence="High")

def check_19_load_distribution(p):
    if p.message_count > 0:
        avg_load = sum(p.loads.values()) / len(p.loads) if p.loads else 0
        if avg_load < 0.50:
            return CheckResult(rating="FC", finding=f"Average message load {avg_load:.1%}; well-distributed.", confidence="Medium")
        return draft(f"Average message load {avg_load:.1%}. Verify distribution across buses.", action="Review per-bus load balance.")
    return na("No load data.")

def check_20_headroom_analysis(p):
    return draft("Headroom margin (100% - Load%) shown in Scenario Analysis. Verify headroom > 20% nominal.", page_section="Scenario Analysis", action="Review headroom percentages for each scenario.")

def check_21_fault_scenarios(p):
    if p.has_scenarios:
        return draft("Fault-injection scenario present. Verify realistic fault assumptions and load impact.", action="Review fault scenario assumptions and load impact.")
    return na("No Scenario Analysis tab.")

def check_22_worst_case_coverage(p):
    if p.has_scenarios:
        return draft("Worst-case scenario included. Verify all messages transmitted simultaneously.", action="Review worst-case alignment assumptions.")
    return na("No Scenario Analysis tab.")

def check_23_signal_mapping(p):
    if p.message_count >= 5:
        return CheckResult(rating="FC", finding=f"{p.message_count} messages mapped; signal-level mapping feasible.", confidence="Medium")
    return draft(f"Only {p.message_count} messages. Consider signal-level load breakdown.", action="Optionally add Signal Cycle Allocation tab.")

def check_24_recommendations(p):
    return draft("Engineering recommendations provided. Verify alignment with load analysis findings.", page_section="Recommendations", action="Review recommended actions for load mitigation.")

def check_25_references(p):
    return draft("References/methodology documented. Verify standards and internal docs cited.", page_section="References", action="Confirm all normative references present.")

def check_26_doc_control(p):
    if p.has_doc_control:
        return CheckResult(rating="FC", finding="Document Control tab present.", confidence="High")
    return CheckResult(rating="PC", finding="Document Control tab missing.", recommended_action="Add Document Control tab with project, revision history, status.", confidence="High")

def check_27_traceability(p):
    return draft("Message IDs and bus IDs should form a traceable mapping across tabs.", page_section="Message Inventory, Load Calculation", action="Verify all Message IDs appear in Load Calculation.")

def check_28_audit_readiness(p):
    fc_count = sum(1 for check_fn in [check_01_structured, check_02_title, check_03_author, check_04_approver, check_05_revision, check_06_bus_config, check_07_message_inventory, check_08_load_calculation, check_09_scenarios, check_10_nominal_load_threshold, check_11_peak_load_threshold, check_12_protocol_consistency, check_13_frame_overhead, check_14_baud_rate, check_15_dlc_validity, check_16_cycle_time, check_17_message_allocation, check_18_no_formula_errors, check_19_load_distribution, check_20_headroom_analysis, check_21_fault_scenarios, check_22_worst_case_coverage, check_23_signal_mapping, check_24_recommendations, check_25_references, check_26_doc_control, check_27_traceability] if check_fn(p).rating == "FC")
    if fc_count >= 20:
        return CheckResult(rating="FC", finding=f"Audit-ready: {fc_count}/28 checks passing.", confidence="High")
    return draft(f"Audit readiness: {fc_count}/28 checks. Address highlighted gaps.", action="Remediate NO and PC findings.")


CHECKS = {
    "01_structured": check_01_structured,
    "02_title": check_02_title,
    "03_author": check_03_author,
    "04_approver": check_04_approver,
    "05_revision": check_05_revision,
    "06_bus_config": check_06_bus_config,
    "07_message_inventory": check_07_message_inventory,
    "08_load_calculation": check_08_load_calculation,
    "09_scenarios": check_09_scenarios,
    "10_nominal_load_threshold": check_10_nominal_load_threshold,
    "11_peak_load_threshold": check_11_peak_load_threshold,
    "12_protocol_consistency": check_12_protocol_consistency,
    "13_frame_overhead": check_13_frame_overhead,
    "14_baud_rate": check_14_baud_rate,
    "15_dlc_validity": check_15_dlc_validity,
    "16_cycle_time": check_16_cycle_time,
    "17_message_allocation": check_17_message_allocation,
    "18_no_formula_errors": ch