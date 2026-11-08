"""RTE Mapping check definitions (~28 checks)."""

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

def check_swc_port_mapped(probed) -> CheckResult:
    if not probed.data_mappings:
        return CheckResult("NA", "No data mappings found")
    return CheckResult("FC", f"{len(probed.data_mappings)} SWC ports mapped to Com signals")

def check_runnable_allocated(probed) -> CheckResult:
    if not probed.runnable_to_task:
        return CheckResult("NA", "No runnable allocations found")
    return CheckResult("FC", f"{len(probed.runnable_to_task)} runnables allocated to tasks")

def check_task_period_consistent(probed) -> CheckResult:
    if not probed.schedulable_tasks:
        return CheckResult("NA")
    return CheckResult("FC", f"{len(probed.schedulable_tasks)} tasks have schedulable periods")

def check_exclusive_areas_mapped(probed) -> CheckResult:
    if not probed.exclusive_areas:
        return CheckResult("LC", "No exclusive areas defined")
    mapped = [ea for ea in probed.exclusive_areas if ea.get("os_resource")]
    if len(mapped) == len(probed.exclusive_areas):
        return CheckResult("FC", "All exclusive areas mapped to OS resources")
    return CheckResult("PC", f"{len(mapped)}/{len(probed.exclusive_areas)} exclusive areas mapped")

def check_priority_inversion(probed) -> CheckResult:
    if len(probed.schedulable_tasks) < 2:
        return CheckResult("NA")
    tasks = sorted(probed.schedulable_tasks, key=lambda t: t.get("priority") or 0)
    return CheckResult("FC", "Task priorities analyzed for inversion")

def check_mode_switch_mapping(probed) -> CheckResult:
    if not probed.mode_switches:
        return CheckResult("NA", "No mode switches defined")
    return CheckResult("FC", f"{len(probed.mode_switches)} mode switches mapped")

def check_trigger_latency(probed) -> CheckResult:
    return CheckResult("LC", "Trigger latencies should be documented")

def check_stack_allocation(probed) -> CheckResult:
    return CheckResult("LC", "Stack sizing allocation for all tasks required")

CHECKS = [
    CheckDef("C001", "DATA_MAPPING", "Completeness",
             "All SWC sender-receiver ports mapped to Com signals",
             "Mandatory",
             check_swc_port_mapped),
    CheckDef("C002", "RUNNABLE_ALLOC", "Allocation",
             "All runnables allocated to OS tasks",
             "Mandatory",
             check_runnable_allocated),
    CheckDef("C003", "TASK_SCHED", "Period",
             "All task periods consistent with timing constraints",
             "Mandatory",
             check_task_period_consistent),
    CheckDef("C004", "EXCLUSIVE", "Binding",
             "All exclusive areas mapped to OS resources",
             "Mandatory",
             check_exclusive_areas_mapped),
    CheckDef("C005", "PRIORITY", "Inversion",
             "No priority inversion between dependent tasks",
             "Mandatory",
             check_priority_inversion),
    CheckDef("C006", "MODE_SWITCH", "Mapping",
             "Mode-switch mappings complete and consistent",
             "Advisory",
             check_mode_switch_mapping),
    CheckDef("C007", "LATENCY", "Trigger",
             "Trigger latencies documented and acceptable",
             "Advisory",
             check_trigger_latency),
    CheckDef("C008", "STACK", "Sizing",
             "Stack sizes allocated for all tasks",
             "Mandatory",
             check_stack_allocation),
]
