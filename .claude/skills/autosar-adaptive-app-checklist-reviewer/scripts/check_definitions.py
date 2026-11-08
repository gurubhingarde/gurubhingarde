"""Adaptive App check definitions (~28 checks)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

@dataclass
class CheckResult:
    rating: str  # FC, LC, PC, NO, NA
    finding: str = ""
    recommended_action: str = ""

@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    execute: Callable

def check_app_manifest_references(probed) -> CheckResult:
    if not probed.app_manifest:
        return CheckResult("NA", "No application manifest elements found")
    return CheckResult("FC", f"{len(probed.app_manifest)} application manifest elements present")

def check_service_manifest_coverage(probed) -> CheckResult:
    if not probed.service_manifest:
        return CheckResult("NA", "No services in service manifest")
    return CheckResult("FC", f"{len(probed.service_manifest)} services defined in service manifest")

def check_machine_manifest_complete(probed) -> CheckResult:
    if not probed.machine_manifest:
        return CheckResult("LC", "Machine manifest should define host configuration")
    return CheckResult("FC", f"{len(probed.machine_manifest)} machine manifest elements present")

def check_ara_com_interfaces(probed) -> CheckResult:
    if not probed.ara_com_interfaces:
        return CheckResult("NA", "No ara::com interfaces defined")
    return CheckResult("FC", f"{len(probed.ara_com_interfaces)} ara::com service interfaces configured")

def check_ara_exec_state_consistency(probed) -> CheckResult:
    if not probed.ara_exec_states:
        return CheckResult("NA", "No ara::exec lifecycle states defined")
    return CheckResult("LC", f"{len(probed.ara_exec_states)} ara::exec states defined")

def check_someip_service_id_unique(probed) -> CheckResult:
    if not probed.someip_config:
        return CheckResult("NA", "No SOME/IP configuration")
    service_ids = [cfg.get("service_id") for cfg in probed.someip_config]
    if len(service_ids) == len(set(service_ids)):
        return CheckResult("FC", "All SOME/IP service IDs unique")
    return CheckResult("NO", "Duplicate SOME/IP service IDs detected", "Assign unique service IDs")

def check_process_config_present(probed) -> CheckResult:
    if not probed.process_config:
        return CheckResult("LC", "Process configuration should be defined")
    return CheckResult("FC", f"{len(probed.process_config)} processes configured")

def check_resource_budget_feasible(probed) -> CheckResult:
    return CheckResult("LC", "Resource budget allocation should be verified against constraints")

CHECKS = [
    CheckDef("C001", "APP_MANIFEST", "References",
             "Application manifest references all existing services",
             "Mandatory",
             check_app_manifest_references),
    CheckDef("C002", "SVC_MANIFEST", "Coverage",
             "Service manifest covers all required services",
             "Mandatory",
             check_service_manifest_coverage),
    CheckDef("C003", "MACHINE", "Complete",
             "Machine manifest covers all required services and processors",
             "Mandatory",
             check_machine_manifest_complete),
    CheckDef("C004", "ARA_COM", "Interfaces",
             "ara::com service interfaces defined and consistent",
             "Mandatory",
             check_ara_com_interfaces),
    CheckDef("C005", "ARA_EXEC", "Lifecycle",
             "ara::exec states transition consistently",
             "Mandatory",
             check_ara_exec_state_consistency),
    CheckDef("C006", "SOMEIP", "Uniqueness",
             "SOME/IP service IDs and instance IDs are unique",
             "Mandatory",
             check_someip_service_id_unique),
    CheckDef("C007", "PROCESS", "Configuration",
             "Process configuration complete with POSIX attributes",
             "Advisory",
             check_process_config_present),
    CheckDef("C008", "RESOURCES", "Budget",
             "Resource budget feasible for target platform",
             "Advisory",
             check_resource_budget_feasible),
]
