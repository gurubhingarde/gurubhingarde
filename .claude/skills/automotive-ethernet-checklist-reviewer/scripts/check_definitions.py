"""Automotive Ethernet Network checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from autoeth_probe import ProbedAutoEth


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding, page_section="", action="(Reviewer to verify and assess)"):
    return CheckResult(rating="", finding="(Auto-suggest) " + finding, page_section=page_section, recommended_action=action, confidence="Low")


def na(reason): return CheckResult(rating="NA", finding=reason, confidence="High")


# Configuration Review
def cr_01_structure(p):
    if len(p.sheet_names) >= 9:
        return CheckResult(rating="FC", finding=f"Document structured into {len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Add structured sections.", confidence="Medium")


def cr_02_network_name(p):
    if p.network_name:
        return CheckResult(rating="FC", finding=f"Network identified as '{p.network_name}'.", confidence="High")
    return CheckResult(rating="NO", finding="Network name not detected.", recommended_action="Add clear network identification.", confidence="High")


def cr_03_revision(p):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="Revision not populated.", recommended_action="Populate Revision field.", confidence="High")


def cr_04_topology(p):
    if p.switches:
        return CheckResult(rating="FC", finding=f"Network topology with {len(p.switches)} switch(es) defined.", confidence="High")
    return CheckResult(rating="NO", finding="No network topology found.", recommended_action="Define all switches and links.", confidence="High")


def cr_05_vlan_config(p):
    if p.vlans:
        return CheckResult(rating="FC", finding=f"{len(p.vlans)} VLANs configured.", confidence="High")
    return CheckResult(rating="NO", finding="No VLAN configuration found.", recommended_action="Define VLAN segmentation.", confidence="High")


def cr_06_service_catalog(p):
    if p.services:
        return CheckResult(rating="FC", finding=f"{len(p.services)} SOME/IP services in catalog.", confidence="High")
    return CheckResult(rating="NO", finding="No SOME/IP service catalog found.", recommended_action="Define all services.", confidence="High")


def cr_07_doc_control(p):
    if p.revision_history_rows >= 1:
        return CheckResult(rating="FC", finding=f"Revision history has {p.revision_history_rows} rows.", confidence="High")
    return CheckResult(rating="NO", finding="No revision history.", recommended_action="Add revision history.", confidence="High")


def cr_08_status(p):
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="No status field.", recommended_action="Add Status field.", confidence="High")


# Technical Assessment
def ta_01_vlan_consistency(p):
    if not p.vlans:
        return na("No VLANs.")
    vlan_ids = [v.get("vlan_id") for v in p.vlans]
    if len(vlan_ids) == len(set(vlan_ids)):
        return CheckResult(rating="FC", finding=f"All {len(p.vlans)} VLAN IDs are unique.", confidence="High")
    return CheckResult(rating="NO", finding="Duplicate VLAN IDs detected.", recommended_action="Ensure all VLAN IDs are unique.", confidence="High")


def ta_02_someip_provider_consumer(p):
    if not p.services:
        return na("No services.")
    services_complete = [s for s in p.services if s.get("provider") and s.get("consumers")]
    coverage = len(services_complete) / len(p.services)
    if coverage >= 0.95:
        return CheckResult(rating="FC", finding=f"All {len(p.services)} services have provider and consumer(s).", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(services_complete)}/{len(p.services)} services fully mapped.", recommended_action="Assign provider and consumer for each service.", confidence="High")


def ta_03_avb_streams_defined(p):
    if not p.avb_streams:
        return CheckResult(rating="NA", finding="No AVB streams. Best-effort traffic only.", confidence="High")
    return CheckResult(rating="FC", finding=f"{len(p.avb_streams)} AVB streams reserved.", confidence="High")


def ta_04_multicast_allocation(p):
    if not p.multicast_groups:
        return CheckResult(rating="NA", finding="No multicast groups defined.", confidence="Medium")
    complete = [m for m in p.multicast_groups if m.get("sources") and m.get("listeners")]
    if len(complete) == len(p.multicast_groups):
        return CheckResult(rating="FC", finding=f"All {len(p.multicast_groups)} multicast groups fully specified.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(complete)}/{len(p.multicast_groups)} multicast groups complete.", recommended_action="Define sources and listeners for all groups.", confidence="High")


# Validation Assessment
def va_01_bandwidth_budget(p):
    if not p.avb_streams:
        return draft("Bandwidth budget calculation requires AVB stream list.", action="Verify aggregate bandwidth <= link capacity.")
    total_avb = sum([s.get("bandwidth", 0) for s in p.avb_streams])
    # Assume 1Gbps nominal capacity
    if total_avb <= 800:  # Leave 200 Mbps for best-effort
        return CheckResult(rating="FC", finding=f"Total AVB bandwidth {total_avb}Mbps is within budget.", confidence="Medium")
    return CheckResult(rating="NO", finding=f"Total AVB bandwidth {total_avb}Mbps exceeds 800Mbps budget.", recommended_action="Reduce AVB reservations or upgrade link speeds.", confidence="Medium")


def va_02_mac_uniqueness(p):
    if not p.services:
        return na("No services.")
    service_ids = [s.get("service_id") for s in p.services]
    if len(service_ids) == len(set(service_ids)):
        return CheckResult(rating="FC", finding=f"All {len(p.services)} service IDs are unique.", confidence="High")
    return CheckResult(rating="NO", finding="Duplicate service IDs detected.", recommended_action="Ensure all service IDs are globally unique.", confidence="High")


def va_03_vlan_isolation(p):
    if not p.vlans:
        return na("No VLANs.")
    isolated = [v for v in p.vlans if v.get("isolate")]
    if isolated:
        return CheckResult(rating="FC", finding=f"{len(isolated)} VLAN(s) configured with isolation.", confidence="High")
    return draft("No VLAN isolation configured; traffic crossing domains may be unintended.", action="Review VLAN isolation requirements per safety criticality.")


def va_04_multicast_reachability(p):
    if not p.multicast_groups:
        return na("No multicast groups.")
    complete = [m for m in p.multicast_groups if m.get("sources") and m.get("listeners")]
    if len(complete) == len(p.multicast_groups):
        return CheckResult(rating="FC", finding="All multicast groups have reachability.", confidence="Medium")
    return CheckResult(rating="PC", finding="Some multicast groups may lack full reachability.", recommended_action="Verify IGMP snooping configuration per switch.", confidence="Medium")


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedAutoEth], CheckResult]


CHECKS: list[CheckDef] = [
    # Configuration Review
    CheckDef("1",  "CR", "Document Structure", "Is the configuration structured clearly?", "Shall", cr_01_structure),
    CheckDef("2",  "CR", "Network Identity", "Is the network clearly identified?", "Shall", cr_02_network_name),
    CheckDef("3",  "CR", "Versioning", "Is configuration revision documented?", "Shall", cr_03_revision),
    CheckDef("4",  "CR", "Topology", "Is network topology defined?", "Shall", cr_04_topology),
    CheckDef("5",  "CR", "VLAN Config", "Are VLANs configured?", "Shall", cr_05_vlan_config),
    CheckDef("6",  "CR", "Service Catalog", "Is a SOME/IP service catalog present?", "Shall", cr_06_service_catalog),
    CheckDef("7",  "CR", "Document Control", "Is revision history present?", "Shall", cr_07_doc_control),
    CheckDef("8",  "CR", "Status Field", "Is configuration status documented?", "Shall", cr_08_status),

    # Technical Assessment
    CheckDef("1",  "TA", "VLAN Management", "Are all VLAN IDs unique and consistent?", "Shall", ta_01_vlan_consistency),
    CheckDef("2",  "TA", "SOME/IP Services", "Does every service have provider(s) and consumer(s)?", "Shall", ta_02_someip_provider_consumer),
    CheckDef("3",  "TA", "AVB Allocation", "Are AVB streams (reserved bandwidth) allocated?", "Should", ta_03_avb_streams_defined),
    CheckDef("4",  "TA", "Multicast Routing", "Are multicast groups fully specified?", "Should", ta_04_multicast_allocation),

    # Validation Assessment
    CheckDef("1",  "VA", "Bandwidth Budget", "Does total AVB traffic fit within link budget?", "Shall", va_01_bandwidth_budget),
    CheckDef("2",  "VA", "Service Uniqueness", "Are all service IDs globally unique?", "Shall", va_02_mac_uniqueness),
    CheckDef("3",  "VA", "VLAN Isolation", "Are safety-critical VLANs isolated from best-effort?", "Should", va_03_vlan_isolation),
    CheckDef("4",  "VA", "Multicast Reach", "Can all multicast listeners reach their sources?", "Shall", va_04_multicast_reachability),
]
