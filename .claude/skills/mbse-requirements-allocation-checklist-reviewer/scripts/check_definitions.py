"""MBSE Requirements Allocation checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from reqs_alloc_probe import ProbedReqsAlloc

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

def cr_01_catalog(p):
    if p.requirement_count >= 5:
        return fc(f"{p.requirement_count} requirements defined")
    if p.requirement_count > 0:
        return pc(f"Only {p.requirement_count} requirements", "Expand requirement hierarchy")
    return no("No requirements in catalog", "Populate Requirements Catalog tab")

def cr_02_hierarchy(p):
    if p.system_req_count > 0 and p.subsystem_req_count > 0:
        return fc(f"Hierarchy: {p.system_req_count} system + {p.subsystem_req_count} subsystem reqs")
    return pc("Incomplete hierarchy decomposition", "Add sub-system and component requirements")

def cr_03_allocation(p):
    if p.allocation_count >= p.requirement_count and p.requirement_count > 0:
        return fc(f"All {p.requirement_count} requirements allocated")
    if p.allocation_count > 0:
        return pc(f"{p.allocation_count}/{p.requirement_count} allocated", "Complete allocation matrix")
    return no("No allocations found", "Populate Allocation Matrix tab")

def cr_04_satisfy(p):
    if p.has_satisfy:
        return fc("Satisfy relationships tab present")
    return pc("No Satisfy relationships tab", "Create to document requirement satisfaction")

def cr_05_derive(p):
    if p.has_derive:
        return fc("Derive relationships tab present")
    return pc("No Derive relationships tab", "Document requirement derivation")

def cr_06_verify(p):
    if p.has_verify:
        return fc("Verify relationships tab present")
    return pc("No Verify relationships tab", "Define verification methods")

CHECKS = [
    CheckDef(id="CR01", tab="Catalog", section="Structure", requirement="Requirements populated", obligation="Must", func=cr_01_catalog),
    CheckDef(id="CR02", tab="Catalog", section="Hierarchy", requirement="Hierarchical decomposition", obligation="Must", func=cr_02_hierarchy),
    CheckDef(id="CR03", tab="Allocation", section="Coverage", requirement="All requirements allocated", obligation="Must", func=cr_03_allocation),
    CheckDef(id="CR04", tab="Relationships", section="Satisfy", requirement="Satisfy relationships defined", obligation="Should", func=cr_04_satisfy),
    CheckDef(id="CR05", tab="Relationships", section="Derive", requirement="Derive relationships defined", obligation="Should", func=cr_05_derive),
    CheckDef(id="CR06", tab="Relationships", section="Verify", requirement="Verify methods defined", obligation="Should", func=cr_06_verify),
]
