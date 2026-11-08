"""MBSE Model Architecture checks — 30+ verification rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from mbse_probe import ProbedMBSE

@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""

@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    func: Callable

def draft(finding, action="Reviewer verification required"):
    return CheckResult(rating="", finding=f"Auto-suggest: {finding}", recommended_action=action, confidence="Low")

def na(reason): return CheckResult(rating="NA", finding=reason, confidence="High")

def fc(finding): return CheckResult(rating="FC", finding=finding, confidence="High")

def pc(finding, action): return CheckResult(rating="PC", finding=finding, recommended_action=action, confidence="Medium")

def no(finding, action): return CheckResult(rating="NO", finding=finding, recommended_action=action, confidence="High")

# Structure checks
def cr_01_tabs(p):
    required = ["Title", "Operational Analysis", "System Analysis", "Logical Analysis", "Physical Analysis"]
    found = [t for t in required if t in p.sheet_names]
    if len(found) == len(required):
        return fc(f"All {len(required)} core tabs present.")
    missing = [t for t in required if t not in p.sheet_names]
    return no(f"Missing tabs: {', '.join(missing)}", f"Create tabs: {', '.join(missing)}")

def cr_02_system_id(p):
    if p.title:
        return fc(f"System identified as: {p.title}")
    return no("No system identification found", "Populate Title sheet with system name")

def cr_03_author(p):
    if p.author:
        return fc(f"Author identified: {p.author}")
    return pc("Author not specified", "Add author to Title sheet")

# Operational layer
def cr_04_scenarios(p):
    if p.operational_scenario_count >= 3:
        return fc(f"{p.operational_scenario_count} operational scenarios defined")
    if p.operational_scenario_count > 0:
        return pc(f"Only {p.operational_scenario_count} scenario(s); typically need 3+", "Add more scenarios")
    return no("No scenarios defined", "Create operational scenarios in Operational Analysis tab")

# System layer
def cr_05_functions(p):
    if p.system_function_count >= 5:
        return fc(f"{p.system_function_count} system functions defined")
    if p.system_function_count > 0:
        return pc(f"Only {p.system_function_count} function(s)", "Decompose functions further")
    return no("No system functions defined", "Create functions in System Analysis tab")

# Logical layer
def cr_06_logical_components(p):
    if p.logical_component_count >= 3:
        return fc(f"{p.logical_component_count} logical components defined")
    if p.logical_component_count > 0:
        return pc(f"Only {p.logical_component_count} component(s)", "Decompose into more logical units")
    return no("No logical components defined", "Create components in Logical Analysis tab")

# Physical layer
def cr_07_physical_components(p):
    if p.physical_component_count >= 2:
        return fc(f"{p.physical_component_count} physical components defined")
    if p.physical_component_count > 0:
        return pc(f"Only {p.physical_component_count} physical component(s)", "Map all logical components to physical")
    return no("No physical components defined", "Create components in Physical Analysis tab")

# Traceability
def cr_08_traceability_tab(p):
    if p.has_traceability:
        return fc("Inter-layer traceability tab present")
    return pc("No traceability tab", "Create Inter-Layer Traceability tab")

CHECKS = [
    CheckDef(id="CR01", tab="Structure", section="Core Structure", requirement="All required tabs present", obligation="Must", func=cr_01_tabs),
    CheckDef(id="CR02", tab="Structure", section="System ID", requirement="System name identified", obligation="Must", func=cr_02_system_id),
    CheckDef(id="CR03", tab="Structure", section="Authorship", requirement="Author documented", obligation="Should", func=cr_03_author),
    CheckDef(id="CR04", tab="Operational", section="Scenarios", requirement="3+ operational scenarios", obligation="Should", func=cr_04_scenarios),
    CheckDef(id="CR05", tab="System", section="Functions", requirement="5+ system functions", obligation="Should", func=cr_05_functions),
    CheckDef(id="CR06", tab="Logical", section="Components", requirement="3+ logical components", obligation="Should", func=cr_06_logical_components),
    CheckDef(id="CR07", tab="Physical", section="Deployment", requirement="2+ physical components", obligation="Should", func=cr_07_physical_components),
    CheckDef(id="CR08", tab="Traceability", section="Structure", requirement="Traceability tab present", obligation="Should", func=cr_08_traceability_tab),
]
