"""Gateway Routing confirmation checks."""

from __future__ import annotations

from dataclasses import dataclass
from gateway_probe import ProbedGateway


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
    if len(p.sheet_names) >= 8:
        return CheckResult(rating="FC", finding=f"Document structured into {len(p.sheet_names)} tabs.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs; missing recommended sections.", recommended_action="Add Gateway ECU, Source/Dest Bus, Routing Table, Latency Budget, Security tabs.", confidence="High")

def check_02_title(p):
    if p.title:
        return CheckResult(rating="FC", finding=f"Title: '{p.title}'.", confidence="High")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add a clear gateway specification title.", confidence="High")

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

def check_06_gateway_ecu(p):
    if p.has_gateway_ecu and p.gateway_id:
        return CheckResult(rating="FC", finding=f"Gateway ECU Definition present. ID: '{p.gateway_id}'.", confidence="High")
    return CheckResult(rating="NO", finding="Gateway ECU Definition tab missing or empty.", recommended_action="Add Gateway ECU Definition with ID, name, type, platform.", confidence="High")

def check_07_source_buses(p):
    if p.has_source_buses and p.source_bus_count > 0:
        return CheckResult(rating="FC", finding=f"Source Bus Inventory present with {p.source_bus_count} bus(es).", confidence="High")
    return CheckResult(rating="NO", finding="Source Bus Inventory tab missing or empty.", recommended_action="Add all source buses (CAN, LIN, Ethernet, etc.).", confidence="High")

def check_08_dest_buses(p):
    if p.has_dest_buses and p.dest_bus_count > 0:
        return CheckResult(rating="FC", finding=f"Destination Bus Inventory present with {p.dest_bus_count} bus(es).", confidence="High")
    return CheckResult(rating="NO", finding="Destination Bus Inventory tab missing or empty.", recommended_action="Add all destination buses.", confidence="High")

def check_09_routing_table(p):
    if p.has_routing_table and p.route_count > 0:
        return CheckResult(rating="FC", finding=f"Routing Table present with {p.route_count} route(s).", confidence="High")
    return CheckResult(rating="NO", finding="Routing Table tab missing or empty.", recommended_action="Define all signal/PDU/frame routes between buses.", confidence="High")

def check_10_latency_budget(p):
    if p.has_latency_budget:
        return CheckResult(rating="FC", finding="Latency Budget tab present.", confidence="High")
    return CheckResult(rating="PC", finding="Latency Budget tab missing.", recommended_action="Add per-route latency budgets.", confidence="Medium")

def check_11_security_rules(p):
    if p.has_security_rules and p.rule_count > 0:
        return CheckResult(rating="FC", finding=f"Security/Firewall Rules present with {p.rule_count} rule(s).", confidence="High")
    return CheckResult(rating="PC", finding="Security/Firewall Rules tab missing or empty.", recommended_action="Add inter-domain routing restrictions.", confidence="High")

def check_12_source_dest_mapping(p):
    orphan_routes = 0
    for route_id, route in p.routes.items():
        src = route.get("source_bus", "")
        dst = route.get("dest_bus", "")
        if not src or src not in p.source_buses:
            orphan_routes += 1
        if not dst or dst not in p.dest_buses:
            orphan_routes += 1

    if orphan_routes == 0:
        return CheckResult(rating="FC", finding="All routes map to valid source/dest buses.", confidence="High")
    return CheckResult(rating="NO", finding=f"{orphan_routes} orphan route(s) detected.", recommended_action="Verify all routes reference valid buses.", confidence="High")

def check_13_all_routes_have_signals(p):
    empty_signal_routes = sum(1 for r in p.routes.values() if not r.get("signal_ids"))
    if empty_signal_routes == 0:
        return CheckResult(rating="FC", finding=f"All {p.route_count} routes have signal/PDU IDs.", confidence="High")
    return CheckResult(rating="NO", finding=f"{empty_signal_routes} route(s) missing signal/PDU IDs.", recommended_action="Populate signal IDs for all routes.", confidence="High")

def check_14_latency_compliance(p):
    if p.has_latency_budget:
        return draft(f"Latency budgets specified for {p.route_count} route(s). Verify all <= 100ms.", action="Review Latency Budget tab for compliance with system requirements.")
    return na("Latency Budget tab not present.")

def check_15_firewall_enforcement(p):
    denied_rules = sum(1 for r in p.rules.values() if not r.get("allowed"))
    if denied_rules > 0:
        return CheckResult(rating="FC", finding=f"{denied_rules} firewall rules restrict unauthorized routing.", confidence="High")
    return draft("No explicit deny rules found. Verify default-deny posture.", action="Add firewall rules for untrusted inter-domain routes.")

def check_16_no_formula_errors(p):
    if p.error_cells == 0:
        return CheckResult(rating="FC", finding="No formula errors (#VALUE!, #DIV/0!, etc.).", confidence="High")
    return CheckResult(rating="NO", finding=f"{p.error_cells} formula error(s) detected.", recommended_action="Fix formulas in Latency Budget and other tabs.", confidence="High")

def check_17_protocol_consistency(p):
    all_protocols = set()
    for bus in p.source_buses.values():
        all_protocols.add(bus.get("protocol", ""))
    for bus in p.dest_buses.values():
        all_protocols.add(bus.get("protocol", ""))

    if all(proto in ["CAN", "CAN FD", "LIN", "FlexRay", "Ethernet"] for proto in all_protocols if proto):
        return CheckResult(rating="FC", finding=f"Protocols recognized: {', '.join(all_protocols)}.", confidence="High")
    return draft(f"Unrecognized protocol(s): {all_protocols}.", action="Use standard protocol names.")

def check_18_transformation_rules(p):
    transformed_routes = sum(1 for r in p.routes.values() if r.get("transformation", "None") != "None")
    if transformed_routes > 0:
        return draft(f"{transformed_routes} route(s) include signal transformations. Verify correctness.", action="Review Signal Transformation rules for accuracy.")
    return CheckResult(rating="FC", finding="No signal transformations; direct routing.", confidence="High")

def check_19_latency_allocations(p):
    if p.route_count > 0:
        routes_with_latency = sum(1 for r in p.routes.values() if r.get("latency_ms") is not None)
        if routes_with_latency == p.route_count:
            return CheckResult(rating="FC", finding=f"All {p.route_count} routes have latency allocations.", confidence="High")
        return CheckResult(rating="PC", finding=f"Only {routes_with_latency}/{p.route_count} routes have latency.", recommended_action="Populate latency for all routes.", confidence="High")
    return na("No routes defined.")

def check_20_cross_domain_security(p):
    cross_domain_routes = sum(1 for r in p.routes.values() if r.get("source_bus") != r.get("dest_bus"))
    if cross_domain_routes > 0:
        return draft(f"{cross_domain_routes} cross-domain route(s). Verify security rules allow routing.", action="Confirm firewall rules permit these inter-domain routes.")
    return CheckResult(rating="FC", finding="No cross-domain routing; intra-bus only.", confidence="High")

def check_21_doc_control(p):
    if p.has_doc_control:
        return CheckResult(rating="FC", finding="Document Control tab present.", confidence="High")
    return CheckResult(rating="PC", finding="Document Control tab missing.", recommended_action="Add Document Control tab.", confidence="High")

def check_22_gateway_performance(p):
    return draft("Gateway performance limits (throughput, latency, CPU) should be specified.", page_section="Recommendations", action="Add performance validation section if needed.")

def check_23_diagnostic_routing(p):
    if "Diagnostic Routing" in p.sheet_names:
        return CheckResult(rating="FC", finding="Diagnostic Routing tab present.", confidence="High")
    return draft("Diagnostic Routing tab missing. Consider adding UDS/OBD routing rules.", action="Optionally add Diagnostic Routing tab.")

def check_24_recommendations(p):
    return draft("Engineering recommendations provided. Verify alignment with routing design.", page_section="Recommendations", action="Review recommended actions.")

def check_25_references(p):
    return draft("References/AUTOSAR compliance documented. Verify standards cited.", page_section="References", action="Confirm AUTOSAR and internal methodology references.")

def check_26_traceability(p):
    return draft("Signal/PDU/Frame IDs should be traceable across all tabs.", action="Verify consistent naming across Routing Table, Latency Budget, and Security tabs.")

def check_27_gateway_load_impact(p):
    return draft("Gateway CPU/load impact of routing should be analyzed.", action="Estimate processing load per route; verify gateway capacity.")

def check_28_audit_readiness(p):
    fc_count = sum(1 for check_fn in [check_01_structured, check_02_title, check_03_author, check_04_approver, check_05_revision, check_06_gateway_ecu, check_07_source_buses, check_08_dest_buses, check_09_routing_table, check_10_latency_budget, check_11_security_rules, check_12_source_dest_mapping, check_13_all_routes_have_signals, check_14_latency_compliance, check_15_firewall_enforcement, check_16_no_formula_errors, check_17_protocol_consistency, check_18_transformation_rules, check_19_latency_allocations, check_20_cross_domain_security, check_21_doc_control, check_22_gateway_performance, check_23_diagnostic_routing, check_24_recommendations, check_25_references, check_26_traceability, check_27_gateway_load_impact] if check_fn(p).rating == "FC")
    if fc_count >= 20:
        return CheckResult(rating="FC", finding=f"Audit-ready: {fc_count}/28 checks passing.", confidence="High")
    return draft(f"Audit readiness: {fc_count}/28 checks. Address highlighted gaps.", action="Remediate NO and PC findings.")


CHECKS = {
    "01_structured": check_01_structured,
    "02_title": check_02_title,
    "03_author": check_03_author,
    "04_approver": check_04_approver,
    "05_revision": check_05_revision,
    "06_gateway_ecu": check_06_gateway_ecu,
    "07_source_buses": check_07_source_buses,
    "08_dest_buses": check_08_dest_buses,
    "09_routing_table": check_09_routing_table,
    "10_latency_budget": check_10_latency_budget,
    "11_security_rules": check_11_security_rules,
    "12_source_dest_mapping": check_12_source_dest_mapping,
    "13_all_routes_have_signals": check_13_all_routes_have_signals,
    "14_latency_compliance": check_14_latency_compliance,
    "15_firewall_enforcement": check_15_firewall_enforcement,
    "16_no_formula_errors": check_16_no_formula_errors,
    "17_protocol_consistency": check_17_protocol_consistency,
    "18_transformation_rules": check_18_transformation_rules,
    "19_latency_allocations": check_19_latency_allocations,
    "20_cross_domain_security": check_20_cross_domain_security,
    "21_doc_control": check_21_doc_control,
    "22_gateway_performance": check_22_gateway_performance,
    "23_diagnostic_routing": check_23_diagnostic_routing,
    "24_recommendations": check_24_recommendations,
    "25_references": check_25_references,
    "26_traceability": check_26_traceability,
    "27_gateway_load_impact": check_27_gateway_load_impact,
    "28_audit_readiness": check_28_audit_readiness,
}
