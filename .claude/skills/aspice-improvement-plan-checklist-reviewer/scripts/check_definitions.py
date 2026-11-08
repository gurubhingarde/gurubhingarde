"""ASPICE Improvement Plan canonical checklist definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from aspice_improvement_probe import ProbedImprovementPlan

@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""

def draft(finding: str, action: str = "(Reviewer to verify)") -> CheckResult:
    return CheckResult(rating="", finding="(Auto-suggest, requires reviewer judgment) " + finding, recommended_action=action, confidence="Low")

def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, confidence="High")

def ia_01_scope(p: ProbedImprovementPlan) -> CheckResult:
    if p.program_scope_clear:
        return CheckResult(rating="FC", finding="Improvement program scope clearly defined.", confidence="High")
    return CheckResult(rating="NO", finding="Program scope not clearly documented.", recommended_action="Create Scope section defining improvement program boundaries.", confidence="High")

def ia_02_sponsor(p: ProbedImprovementPlan) -> CheckResult:
    if p.sponsor and p.target_completion_date:
        return CheckResult(rating="FC", finding=f"Sponsor: '{p.sponsor}', Target completion: '{p.target_completion_date}'.", confidence="High")
    return draft("Verify sponsor is named and target completion date is set.")

def ia_03_gaps_addressed(p: ProbedImprovementPlan) -> CheckResult:
    if p.initiative_rows >= 5:
        return CheckResult(rating="FC", finding=f"Each gap from upstream addressed by an initiative ({p.initiative_rows} initiatives).", page_section="Initiatives tab", confidence="High")
    return draft("Verify each gap from Gap Analysis is mapped to an improvement initiative.")

def ia_04_initiative_owner(p: ProbedImprovementPlan) -> CheckResult:
    if p.has_owners and p.initiatives_without_owner == 0:
        return CheckResult(rating="FC", finding="Each initiative has an owner assigned.", confidence="High")
    return CheckResult(rating="NO" if p.initiatives_without_owner > 3 else "PC", finding=f"{p.initiatives_without_owner} initiatives lack an owner.", recommended_action="Assign an owner and milestones to each initiative.", confidence="High")

def ia_05_milestones(p: ProbedImprovementPlan) -> CheckResult:
    if p.has_milestones:
        return CheckResult(rating="FC", finding="Initiatives have milestones defined.", confidence="High")
    return CheckResult(rating="PC", finding="Milestones not fully populated.", recommended_action="Add milestone dates and deliverables to each initiative.", confidence="High")

def ia_06_budget(p: ProbedImprovementPlan) -> CheckResult:
    if p.has_budget:
        return CheckResult(rating="FC", finding="Resources and budget allocated per initiative.", confidence="High")
    return draft("Verify budget and resource allocation are documented per initiative.")

def ia_07_roadmap(p: ProbedImprovementPlan) -> CheckResult:
    if p.roadmap_present:
        return CheckResult(rating="FC", finding="Roadmap timeline defined (Gantt-style).", page_section="Roadmap / Timeline tab", confidence="High")
    return CheckResult(rating="PC", finding="No dedicated roadmap/timeline tab.", recommended_action="Create roadmap showing initiative sequence and dependencies.", confidence="High")

def ia_08_risks(p: ProbedImprovementPlan) -> CheckResult:
    if p.risks_documented:
        return CheckResult(rating="FC", finding="Risks to improvement program documented with mitigations.", page_section="Risk tab", confidence="High")
    return draft("Document risks to improvement program success and mitigation strategies.")

def ia_09_kpis(p: ProbedImprovementPlan) -> CheckResult:
    if p.kpis_defined:
        return CheckResult(rating="FC", finding="KPIs defined to measure improvement progress.", page_section="KPI / Metrics tab", confidence="High")
    return CheckResult(rating="PC", finding="KPIs not explicitly defined.", recommended_action="Define KPIs for tracking improvement program progress.", confidence="High")

def ia_10_communication(p: ProbedImprovementPlan) -> CheckResult:
    if p.stakeholder_comm_plan:
        return CheckResult(rating="FC", finding="Stakeholder communication plan defined.", page_section="Communication tab", confidence="High")
    return draft("Define stakeholder communication plan for improvement initiatives.")

def ia_11_pilot(p: ProbedImprovementPlan) -> CheckResult:
    if p.pilot_plan:
        return CheckResult(rating="FC", finding="Pilot project plan defined (if applicable).", page_section="Pilot tab", confidence="High")
    return draft("If applicable, define pilot project plan for testing improvements.")

def ia_12_timeline_realistic(p: ProbedImprovementPlan) -> CheckResult:
    return draft("Verify timeline is realistic (not all initiatives in same month; appropriate spacing for resource availability).")

@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedImprovementPlan], CheckResult]

CHECKS: list[CheckDef] = [
    CheckDef("1", "IA", "Program Planning", "Is improvement program scoped clearly?", "Shall", ia_01_scope),
    CheckDef("2", "IA", "Program Planning", "Are sponsor and target completion date defined?", "Shall", ia_02_sponsor),
    CheckDef("3", "IA", "Program Planning", "Is each gap from upstream addressed by an initiative?", "Shall", ia_03_gaps_addressed),
    CheckDef("4", "IA", "Initiative Definition", "Does each initiative have an owner assigned?", "Shall", ia_04_initiative_owner),
    CheckDef("5", "IA", "Initiative Definition", "Are milestones defined for each initiative?", "Shall", ia_05_milestones),
    CheckDef("6", "IA", "Initiative Definition", "Are resources and budget allocated?", "Should", ia_06_budget),
    CheckDef("7", "IA", "Planning and Execution", "Is roadmap timeline defined (Gantt-style)?", "Shall", ia_07_roadmap),
    CheckDef("8", "IA", "Planning and Execution", "Are risks and mitigations documented?", "Should", ia_08_risks),
    CheckDef("9", "IA", "Planning and Execution", "Are KPIs defined to measure progress?", "Shall", ia_09_kpis),
    CheckDef("10", "IA", "Planning and Execution", "Is stakeholder communication plan defined?", "Should", ia_10_communication),
    CheckDef("11", "IA", "Planning and Execution", "Is pilot project plan defined (if applicable)?", "Should", ia_11_pilot),
    CheckDef("12", "IA", "Planning and Execution", "Is the timeline realistic (not all initiatives in same month)?", "Should", ia_12_timeline_realistic),
]
