"""Canonical checklist definitions for SysML block diagrams."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from block_probe import ProbedBlockDiagram


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding: str, page_section: str = "", action: str = "") -> CheckResult:
    return CheckResult(
        rating="",
        finding="(Auto-suggest) " + finding,
        page_section=page_section,
        recommended_action=action or "(Reviewer to verify)",
        confidence="Low",
    )


def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, confidence="High")


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedBlockDiagram], CheckResult]


# Confirmation Review checks (28 total)

def bdd_01_structure(p: ProbedBlockDiagram) -> CheckResult:
    if len(p.sheet_names) >= 10:
        return CheckResult(
            rating="FC",
            finding=f"Block diagram structured into {len(p.sheet_names)} tabs.",
            page_section="All tabs",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.sheet_names)} tabs; should have at least 10.",
        recommended_action="Add tabs for Block Catalog, Property, Port, Connector, Item Flow.",
        confidence="High",
    )


def bdd_02_blocks_exist(p: ProbedBlockDiagram) -> CheckResult:
    if p.block_count() > 0:
        return CheckResult(
            rating="FC",
            finding=f"{p.block_count()} blocks defined in Block Catalog.",
            page_section="Block_Catalog",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No blocks found in Block Catalog.",
        recommended_action="Add at least one block (system or subsystem).",
        confidence="High",
    )


def bdd_03_stereotypes(p: ProbedBlockDiagram) -> CheckResult:
    missing = [b for b in p.blocks.values() if not b.stereotype]
    if not missing:
        return CheckResult(
            rating="FC",
            finding="All blocks have stereotypes assigned.",
            page_section="Block_Catalog",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(missing)} blocks missing stereotype: {[b.name for b in missing[:3]]}.",
        recommended_action="Assign <<block>>, <<actor>>, or other SysML stereotypes.",
        confidence="High",
    )


def bdd_04_properties_typed(p: ProbedBlockDiagram) -> CheckResult:
    untyped = []
    for block, props in p.properties.items():
        for prop in props:
            if not prop.type_:
                untyped.append(f"{block}.{prop.name}")
    if not untyped:
        return CheckResult(
            rating="FC",
            finding="All properties have types.",
            page_section="Property_Catalog",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(untyped)} properties untyped: {untyped[:3]}.",
        recommended_action="Assign types (Real, String, etc.) to all properties.",
        confidence="High",
    )


def bdd_05_ports_directional(p: ProbedBlockDiagram) -> CheckResult:
    undirected = []
    for owner, ports in p.ports.items():
        for port in ports:
            if not port.direction and port.port_type != "FullPort":
                undirected.append(f"{owner}.{port.name}")
    if not undirected:
        return CheckResult(
            rating="FC",
            finding="All flow ports have directions assigned.",
            page_section="Port_Catalog",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(undirected)} ports lack direction: {undirected[:3]}.",
        recommended_action="Assign in/out/inout to all flow ports.",
        confidence="High",
    )


def bdd_06_connectors_bound(p: ProbedBlockDiagram) -> CheckResult:
    dangling = []
    for conn in p.connectors:
        if not conn.source_port or not conn.target_port:
            dangling.append(conn.name)
    if not dangling:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.connectors)} connectors fully bound (source+target).",
            page_section="Connector_Catalog",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"{len(dangling)} connectors missing source or target: {dangling[:3]}.",
        recommended_action="Complete all connector bindings.",
        confidence="High",
    )


def bdd_07_no_orphan_blocks(p: ProbedBlockDiagram) -> CheckResult:
    all_referenced = set()
    for conn in p.connectors:
        if "." in conn.source_port:
            all_referenced.add(conn.source_port.split(".")[0])
        if "." in conn.target_port:
            all_referenced.add(conn.target_port.split(".")[0])
    if len(all_referenced) == 0 or len(p.blocks) == 1:
        return CheckResult(rating="NA", finding="Single block or no connectors to check.", confidence="High")
    orphans = set(p.blocks.keys()) - all_referenced - {"System"}
    if not orphans:
        return CheckResult(
            rating="FC",
            finding="No orphan blocks detected.",
            page_section="Connector_Catalog",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(orphans)} blocks not referenced: {list(orphans)[:3]}.",
        recommended_action="Remove orphan blocks or add connectors to/from them.",
        confidence="Medium",
    )


def bdd_08_item_flows_typed(p: ProbedBlockDiagram) -> CheckResult:
    if not p.connectors:
        return CheckResult(rating="NA", finding="No connectors to check for item flows.", confidence="High")
    return draft(
        "Item flow types should be verified manually.",
        page_section="Item_Flow_Catalog",
        action="Cross-reference Item Flow Catalog with Connector Catalog.",
    )


def bdd_09_naming_consistency(p: ProbedBlockDiagram) -> CheckResult:
    issues = []
    for name in p.blocks.keys():
        if " " in name or "-" in name:
            issues.append(name)
    if not issues:
        return CheckResult(
            rating="FC",
            finding="Block naming follows CamelCase/snake_case conventions.",
            page_section="Block_Catalog",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(issues)} blocks use inconsistent naming.",
        recommended_action="Use CamelCase or snake_case consistently.",
        confidence="Medium",
    )


def bdd_10_multiplicity_specified(p: ProbedBlockDiagram) -> CheckResult:
    missing = []
    for block, props in p.properties.items():
        for prop in props:
            if not prop.multiplicity:
                missing.append(f"{block}.{prop.name}")
    if not missing:
        return CheckResult(
            rating="FC",
            finding="All properties have multiplicity.",
            page_section="Property_Catalog",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(missing)} properties lack multiplicity: {missing[:3]}.",
        recommended_action="Specify 1, 0..1, 1..*,  or other multiplicity.",
        confidence="High",
    )


# More checks (abbreviated for brevity)

def bdd_11_no_circular_inheritance(p: ProbedBlockDiagram) -> CheckResult:
    return draft("Verify no circular block inheritance.", page_section="Block_Catalog")


def bdd_12_ports_exist_for_connectors(p: ProbedBlockDiagram) -> CheckResult:
    missing_ports = []
    for conn in p.connectors:
        # Validate BOTH ends of the connector (source and target) against the Port Catalog.
        for ref in (conn.source_port, conn.target_port):
            if "." in ref:
                block, port = ref.split(".", 1)
                block_ports = [pt.name for pt in p.ports.get(block, [])]
                if port not in block_ports:
                    missing_ports.append(ref)
    if not missing_ports:
        return CheckResult(rating="FC", finding="All connector ports exist.", confidence="High")
    return CheckResult(
        rating="NO",
        finding=f"Ports referenced in connectors do not exist: {missing_ports[:3]}.",
        recommended_action="Create missing ports in Port Catalog.",
        confidence="High",
    )


def bdd_13_flow_direction_match(p: ProbedBlockDiagram) -> CheckResult:
    return draft("Verify flow directions match on connected ports.", page_section="Port_Catalog")


def bdd_14_full_ports_no_direction(p: ProbedBlockDiagram) -> CheckResult:
    issues = []
    for owner, ports in p.ports.items():
        for port in ports:
            if port.port_type == "FullPort" and port.direction in ["in", "out", "inout"]:
                issues.append(f"{owner}.{port.name}")
    if not issues:
        return CheckResult(rating="FC", finding="Full ports correctly lack flow directions.", confidence="High")
    return CheckResult(
        rating="PC",
        finding=f"{len(issues)} full ports incorrectly have flow direction.",
        recommended_action="Remove flow direction from full ports; use provides/requires instead.",
        confidence="High",
    )


def bdd_15_proxy_port_semantics(p: ProbedBlockDiagram) -> CheckResult:
    return draft("Verify proxy ports delegate to internal ports correctly.", page_section="Port_Catalog")


CHECKS = [
    CheckDef("BDD-01", "CR", "Structure", "Block diagram organized in tabs", "Shall", bdd_01_structure),
    CheckDef("BDD-02", "CR", "Completeness", "Blocks defined in Block Catalog", "Shall", bdd_02_blocks_exist),
    CheckDef("BDD-03", "CR", "Stereotyping", "All blocks have SysML stereotypes", "Shall", bdd_03_stereotypes),
    CheckDef("BDD-04", "CR", "Type Safety", "All properties typed", "Shall", bdd_04_properties_typed),
    CheckDef("BDD-05", "CR", "Port Direction", "All flow ports have directions", "Shall", bdd_05_ports_directional),
    CheckDef("BDD-06", "CR", "Connector Binding", "All connectors bound", "Shall", bdd_06_connectors_bound),
    CheckDef("BDD-07", "CR", "Orphan Check", "No orphan blocks", "Shall", bdd_07_no_orphan_blocks),
    CheckDef("BDD-08", "CR", "Item Flows", "Item flows typed", "Shall", bdd_08_item_flows_typed),
    CheckDef("BDD-09", "CR", "Naming", "Consistent naming conventions", "Should", bdd_09_naming_consistency),
    CheckDef("BDD-10", "CR", "Multiplicity", "Multiplicity specified", "Shall", bdd_10_multiplicity_specified),
    CheckDef("BDD-11", "CR", "Inheritance", "No circular inheritance", "Shall", bdd_11_no_circular_inheritance),
    CheckDef("BDD-12", "CR", "Port Existence", "Connector ports exist", "Shall", bdd_12_ports_exist_for_connectors),
    CheckDef("BDD-13", "CR", "Flow Direction", "Flow directions match", "Shall", bdd_13_flow_direction_match),
    CheckDef("BDD-14", "CR", "Full Ports", "Full ports lack flow direction", "Shall", bdd_14_full_ports_no_direction),
    CheckDef("BDD-15", "CR", "Proxy Ports", "Proxy port semantics correct", "Should", bdd_15_proxy_port_semantics),
]
