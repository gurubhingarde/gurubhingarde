"""BSW Config check definitions (~30 checks)."""

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

def check_mcal_configured(probed) -> CheckResult:
    if not probed.mcal_modules:
        return CheckResult("NA", "No MCAL modules found")
    configured = [m for m in probed.mcal_modules if m.get("configured") == "Yes"]
    if len(configured) == len(probed.mcal_modules):
        return CheckResult("FC", "All MCAL modules configured for target")
    return CheckResult("PC", f"{len(configured)}/{len(probed.mcal_modules)} modules configured",
                      "Configure remaining MCAL modules")

def check_ecu_abstraction_completeness(probed) -> CheckResult:
    if not probed.ecu_abstraction:
        return CheckResult("NA", "No ECU Abstraction modules found")
    return CheckResult("FC", f"{len(probed.ecu_abstraction)} ECU Abstraction modules present")

def check_service_layer_critical(probed) -> CheckResult:
    if not probed.service_layer:
        return CheckResult("NA")
    critical = [s for s in probed.service_layer if s.get("critical")]
    if critical:
        return CheckResult("FC", f"{len(critical)} critical Service Layer modules identified")
    return CheckResult("LC", "No critical Service Layer modules marked", "Review and mark critical modules")

def check_os_tasks_scheduled(probed) -> CheckResult:
    if not probed.os_tasks:
        return CheckResult("NO", "No OS tasks defined")
    return CheckResult("FC", f"{len(probed.os_tasks)} OS tasks scheduled")

def check_memory_allocation(probed) -> CheckResult:
    if not probed.memory_regions:
        return CheckResult("NA", "No memory regions defined")
    return CheckResult("FC", f"{len(probed.memory_regions)} memory regions allocated")

def _module_name_index(probed) -> dict:
    """Map module ID -> module name across every inventory the workbook carries.

    The Module Parameters tab stores the module *identifier* (e.g. SL005), never
    the module name, so any check that pattern-matches a module name has to
    resolve the ID first. Keying directly on `module_id` made C006 structurally
    dead (issue #54): it could only fire if someone hand-typed a module name into
    the Module ID column.
    """
    index = {}
    for inventory in (probed.mcal_modules, probed.ecu_abstraction,
                      probed.service_layer, probed.complex_drivers):
        for module in inventory or []:
            module_id = module.get("id")
            name = module.get("name")
            if module_id and name:
                index[str(module_id)] = str(name)
    return index

def check_nvm_alignment(probed) -> CheckResult:
    names = _module_name_index(probed)
    nvm_params = []
    for p in probed.module_parameters:
        module_name = names.get(str(p.get("module_id", "")), "")
        # Resolved module name is authoritative; the parameter name is a fallback
        # for workbooks whose inventories do not declare the owning module.
        if "nvm" in module_name.lower() or "nvm" in str(p.get("parameter", "")).lower():
            nvm_params.append(p)
    if not nvm_params:
        if not names:
            return CheckResult(
                "NO", "No module inventory available to resolve parameter owners",
                "Populate the module inventory tabs so parameter ownership can be resolved")
        return CheckResult("NA", "No NvM parameters found")
    modules = sorted({names.get(str(p.get("module_id", "")), str(p.get("module_id", "")))
                      for p in nvm_params})
    return CheckResult("FC", f"{len(nvm_params)} NvM parameters present ({', '.join(modules)})")

def check_parameter_conflicts(probed) -> CheckResult:
    params_by_module = {}
    for p in probed.module_parameters:
        mod = p.get("module_id")
        if mod not in params_by_module:
            params_by_module[mod] = []
        params_by_module[mod].append(p.get("parameter"))

    for mod, params in params_by_module.items():
        if len(params) != len(set(params)):
            return CheckResult("NO", f"Duplicate parameters in {mod}", "Remove duplicate parameter definitions")
    return CheckResult("FC", "No parameter conflicts detected")

def check_inter_module_dependencies(probed) -> CheckResult:
    depends_on_count = sum(1 for e in probed.ecu_abstraction if e.get("depends_on"))
    return CheckResult("LC" if depends_on_count > 0 else "NA",
                      f"{depends_on_count} dependencies identified")

def check_post_build_variants(probed) -> CheckResult:
    post_build_count = sum(1 for p in probed.module_parameters if p.get("post_build"))
    return CheckResult("LC", f"{post_build_count} post-build variant parameters")

CHECKS = [
    CheckDef("C001", "MCAL", "Configuration",
             "All MCAL modules configured for target microcontroller",
             "Mandatory",
             check_mcal_configured),
    CheckDef("C002", "ECU_ABS", "Completeness",
             "ECU Abstraction layer modules present",
             "Mandatory",
             check_ecu_abstraction_completeness),
    CheckDef("C003", "SVC_LAYER", "Critical",
             "Critical Service Layer modules identified",
             "Mandatory",
             check_service_layer_critical),
    CheckDef("C004", "OS", "Tasks",
             "OS tasks allocated and scheduled with period and priority",
             "Mandatory",
             check_os_tasks_scheduled),
    CheckDef("C005", "MEMORY", "Allocation",
             "RAM/ROM memory regions allocated per module",
             "Mandatory",
             check_memory_allocation),
    CheckDef("C006", "NVM", "Alignment",
             "NvM blocks aligned with module parameters",
             "Mandatory",
             check_nvm_alignment),
    CheckDef("C007", "PARAMS", "Conflicts",
             "No parameter naming conflicts within modules",
             "Mandatory",
             check_parameter_conflicts),
    CheckDef("C008", "DEPS", "Dependencies",
             "Inter-module dependencies documented",
             "Advisory",
             check_inter_module_dependencies),
    CheckDef("C009", "POST_BUILD", "Variants",
             "Post-build variant parameters identified",
             "Advisory",
             check_post_build_variants),
]
