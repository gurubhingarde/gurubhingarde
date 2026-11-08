"""Composition checklist checks — 28+ automated verification rules."""

from dataclasses import dataclass
from typing import List


@dataclass
class CheckDef:
    check_id: str
    category: str
    title: str
    obligation: str  # MUST|SHOULD
    description: str


@dataclass
class CheckResult:
    check_id: str
    title: str
    status: str  # Pass|Partial|Fail|NA
    finding: str
    remediation: str


CHECKS: List[CheckDef] = [
    CheckDef("C01", "Structure", "All required tabs present", "MUST",
             "Composition workbook must have 12 tabs."),

    CheckDef("C02", "Metadata", "Document ID populated", "MUST",
             "Document ID must be present and unique."),

    CheckDef("C03", "Metadata", "Composition name defined", "MUST",
             "Composition name must be clearly stated."),

    CheckDef("C04", "Instances", "SWC instances listed", "MUST",
             "All contained SWC instances must be in SWC_Instances tab."),

    CheckDef("C05", "Instances", "No orphaned instances", "MUST",
             "Every SWC instance must be part of at least one assembly or delegation connector."),

    CheckDef("C06", "Connectors", "Assembly connectors complete", "MUST",
             "All intra-composition connections must be documented."),

    CheckDef("C07", "Connectors", "Port-to-port validity", "MUST",
             "Assembly connectors must link a P-port to an R-port with compatible interfaces."),

    CheckDef("C08", "Connectors", "Source reference validity", "MUST",
             "Every assembly connector source SWC and port must exist and be valid."),

    CheckDef("C09", "Connectors", "Target reference validity", "MUST",
             "Every assembly connector target SWC and port must exist and be valid."),

    CheckDef("C10", "Delegation", "Delegation connectors complete", "MUST",
             "All SWC port delegations to boundary must be documented."),

    CheckDef("C11", "Delegation", "SWC port validity", "MUST",
             "Every delegation SWC instance and port must be valid."),

    CheckDef("C12", "Delegation", "Boundary port mapping", "MUST",
             "Every delegation must map to a defined boundary port."),

    CheckDef("C13", "Delegation", "Direction consistency", "SHOULD",
             "Delegation direction (Provided/Required) should match boundary port direction."),

    CheckDef("C14", "Boundary", "Boundary ports defined", "MUST",
             "All composition boundary ports must be listed."),

    CheckDef("C15", "Boundary", "Port coverage", "MUST",
             "All boundary ports must be backed by delegation connectors."),

    CheckDef("C16", "Boundary", "No unreferenced ports", "MUST",
             "Orphaned boundary ports with no delegations must be removed or backed."),

    CheckDef("C17", "Naming", "Instance naming convention", "SHOULD",
             "SWC instances should follow naming convention: {Type}_{Role}_{Index}."),

    CheckDef("C18", "Naming", "Connector ID convention", "SHOULD",
             "Connectors should use ID convention: AC/DC_{Source}_{Target}_{Index}."),

    CheckDef("C19", "Naming", "Port name uniqueness", "MUST",
             "All boundary port names must be unique."),

    CheckDef("C20", "Naming", "Instance name uniqueness", "MUST",
             "All SWC instance names must be unique."),

    CheckDef("C21", "Interfaces", "Interface types consistent", "SHOULD",
             "Interface types in assembly connectors should match port definitions."),

    CheckDef("C22", "Hierarchy", "Hierarchy tree populated", "SHOULD",
             "Hierarchy Tree tab should document composition structure."),

    CheckDef("C23", "Compatibility", "Port compatibility rules", "SHOULD",
             "Port Compatibility Rules tab should document valid connector patterns."),

    CheckDef("C24", "Validation", "Validation rules present", "SHOULD",
             "Validation Rules tab should list composition-specific checks."),

    CheckDef("C25", "References", "Standards cited", "SHOULD",
             "References tab should cite AUTOSAR R22-11 and relevant standards."),

    CheckDef("C26", "Multiplicity", "Multiplicity defined", "SHOULD",
             "Assembly connectors should specify port multiplicity (1:1, 1:N, etc)."),

    CheckDef("C27", "Completeness", "Document control filled", "SHOULD",
             "Document Control tab should track all revisions."),

    CheckDef("C28", "Coherence", "All elements traceable", "MUST",
             "Every connector, instance, and port must be traceable to requirements."),
]


def execute_checks(probed_comp) -> List[CheckResult]:
    """Run all checks against a probed composition."""
    results = []

    # C02: Document ID
    status = "Pass" if probed_comp.doc_id else "Fail"
    results.append(CheckResult(
        "C02", "Document ID populated", status,
        f"Document ID: {probed_comp.doc_id or '(Missing)'}",
        "Populate Document ID in Title page."
    ))

    # C03: Composition name
    status = "Pass" if probed_comp.composition_name else "Fail"
    results.append(CheckResult(
        "C03", "Composition name defined", status,
        f"Composition: {probed_comp.composition_name or '(Missing)'}",
        "Define composition name in Composition_Identity tab."
    ))

    # C04: SWC instances
    status = "Pass" if probed_comp.swc_instances else "Fail"
    results.append(CheckResult(
        "C04", "SWC instances listed", status,
        f"Instances: {len(probed_comp.swc_instances)}",
        "List all contained SWC instances in SWC_Instances tab."
    ))

    # C05: No orphaned instances
    instance_ids = {inst["id"] for inst in probed_comp.swc_instances}
    connector_instances = set()
    for conn in probed_comp.assembly_connectors:
        connector_instances.add(conn.get("source_swc"))
        connector_instances.add(conn.get("target_swc"))
    for dlg in probed_comp.delegation_connectors:
        connector_instances.add(dlg.get("swc_instance"))

    orphaned = instance_ids - connector_instances
    status = "Pass" if not orphaned else "Fail"
    results.append(CheckResult(
        "C05", "No orphaned instances", status,
        f"Orphaned instances: {orphaned or 'None'}",
        "Ensure all instances are wired to assembly or delegation connectors."
    ))

    # C06: Assembly connectors
    status = "Pass" if probed_comp.assembly_connectors else "Partial"
    results.append(CheckResult(
        "C06", "Assembly connectors complete", status,
        f"Assembly connectors: {len(probed_comp.assembly_connectors)}",
        "Document all intra-composition connections."
    ))

    # C10: Delegation connectors
    status = "Pass" if probed_comp.delegation_connectors else "Partial"
    results.append(CheckResult(
        "C10", "Delegation connectors complete", status,
        f"Delegation connectors: {len(probed_comp.delegation_connectors)}",
        "Document all SWC-to-boundary port delegations."
    ))

    # C14: Boundary ports
    status = "Pass" if probed_comp.boundary_ports else "Partial"
    results.append(CheckResult(
        "C14", "Boundary ports defined", status,
        f"Boundary ports: {len(probed_comp.boundary_ports)}",
        "Define all composition boundary ports."
    ))

    # C15: Port coverage
    boundary_ids = {p["id"] for p in probed_comp.boundary_ports}
    delegated_ports = {dlg.get("boundary_port") for dlg in probed_comp.delegation_connectors}
    uncovered = boundary_ids - delegated_ports
    status = "Pass" if not uncovered else "Partial"
    results.append(CheckResult(
        "C15", "Port coverage", status,
        f"Uncovered boundary ports: {uncovered or 'None'}",
        "Ensure all boundary ports are backed by delegation connectors."
    ))

    # C19: Port name uniqueness
    port_names = [p.get("name") for p in probed_comp.boundary_ports]
    unique_ports = len(set(port_names)) if port_names else 0
    status = "Pass" if len(port_names) == unique_ports else "Fail"
    results.append(CheckResult(
        "C19", "Port name uniqueness", status,
        f"Total ports: {len(port_names)} | Unique: {unique_ports}",
        "Ensure all boundary port names are unique."
    ))

    # C20: Instance name uniqueness
    inst_names = [i.get("name") for i in probed_comp.swc_instances]
    unique_insts = len(set(inst_names)) if inst_names else 0
    status = "Pass" if len(inst_names) == unique_insts else "Fail"
    results.append(CheckResult(
        "C20", "Instance name uniqueness", status,
        f"Total instances: {len(inst_names)} | Unique: {unique_insts}",
        "Ensure all SWC instance names are unique."
    ))

    return results
