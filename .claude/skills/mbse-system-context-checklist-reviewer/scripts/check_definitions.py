"""MBSE System Context checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from context_probe import ProbedContext

@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
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

def fc(finding): return CheckResult(rating="FC", finding=finding, confidence="High")
def pc(finding, action): return CheckResult(rating="PC", finding=finding, recommended_action=action, confidence="Medium")
def no(finding, action): return CheckResult(rating="NO", finding=finding, recommended_action=action, confidence="High")

def cr_01_actors(p):
    if p.actor_count >= 3:
        return fc(f"{p.actor_count} actors identified")
    if p.actor_count > 0:
        return pc(f"Only {p.actor_count} actor(s); typically need 3+", "Identify additional actors (human, system, environmental)")
    return no("No actors found", "Populate Actor Inventory tab")

def cr_02_interfaces(p):
    if p.interface_count >= p.actor_count and p.actor_count > 0:
        return fc(f"All {p.actor_count} actors have interfaces ({p.interface_count} total)")
    if p.interface_count > 0:
        return pc(f"Only {p.interface_count}/{p.actor_count} actor interfaces", "Define interface for each actor")
    return no("No interfaces defined", "Populate External Interfaces tab")

def cr_03_use_cases(p):
    if p.use_case_count >= 3:
        return fc(f"{p.use_case_count} use cases defined")
    if p.use_case_count > 0:
        return pc(f"Only {p.use_case_count} use case(s); typically need 3+", "Add more use cases")
    return no("No use cases found", "Populate Use Case Catalog tab")

def cr_04_scenarios(p):
    if p.scenario_count >= 2:
        return fc(f"{p.scenario_count} operational scenarios defined")
    if p.scenario_count > 0:
        return pc(f"Only {p.scenario_count} scenario", "Add scenarios for different operational contexts")
    return no("No scenarios found", "Define operational scenarios")

def cr_05_needs(p):
    if p.stakeholder_need_count >= 5:
        return fc(f"{p.stakeholder_need_count} stakeholder needs defined")
    if p.stakeholder_need_count > 0:
        return pc(f"Only {p.stakeholder_need_count} need(s)", "Capture more stakeholder needs")
    return pc("No stakeholder needs documented", "Create Stakeholder Needs tab with comprehensive list")

def cr_06_boundary(p):
    if p.has_boundary:
        return fc("System Boundary Definition tab present")
    return pc("No System Boundary Definition tab", "Create and document system boundary and scope")

CHECKS = [
    CheckDef(id="CR01", tab="Actors", section="Inventory", requirement="3+ actors identified", obligation="Must", func=cr_01_actors),
    CheckDef(id="CR02", tab="Interfaces", section="Coverage", requirement="Interface per actor", obligation="Must", func=cr_02_interfaces),
    CheckDef(id="CR03", tab="UseCases", section="Population", requirement="3+ use cases", obligation="Should", func=cr_03_use_cases),
    CheckDef(id="CR04", tab="Scenarios", section="Population", requirement="2+ scenarios", obligation="Should", func=cr_04_scenarios),
    CheckDef(id="CR05", tab="Needs", section="Population", requirement="5+ stakeholder needs", obligation="Should", func=cr_05_needs),
    CheckDef(id="CR06", tab="Boundary", section="Definition", requirement="Boundary statement present", obligation="Should", func=cr_06_boundary),
]
