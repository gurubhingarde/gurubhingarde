"""ASPICE Gap Analysis canonical checklist definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from aspice_gap_probe import ProbedGapAnalysis


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding: str, action: str = "(Reviewer to verify)") -> CheckResult:
    return CheckResult(
        rating="",
        finding="(Auto-suggest, requires reviewer judgment) " + finding,
        recommended_action=action,
        confidence="Low",
    )


def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, confidence="High")


def ga_01_current_state(p: ProbedGapAnalysis) -> CheckResult:
    if p.current_state_rows > 0:
        return CheckResult(
            rating="FC",
            finding=f"Current state echoed from Assessment ({p.current_state_rows} rows).",
            page_section="Current State tab",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Current state not documented.",
        recommended_action="Create Current State tab echoing Assessment results per process.",
        confidence="High",
    )


def ga_02_target_cl_justified(p: ProbedGapAnalysis) -> CheckResult:
    if p.target_cl_rows > 0:
        return CheckResult(
            rating="FC",
            finding=f"Target CL stated for {p.target_cl_rows} processes with justification.",
            page_section="Target / Goal tab",
            confidence="Medium",
        )
    return draft("Verify target CL per process is explicitly stated with business justification.")


def ga_03_gaps_mapped(p: ProbedGapAnalysis) -> CheckResult:
    if p.gap_rows >= 5:
        return CheckResult(
            rating="FC",
            finding=f"Gaps identified and mapped to PA/indicators ({p.gap_rows} gap rows).",
            page_section="Gap Analysis tab",
            confidence="High",
        )
    if p.gap_rows > 0:
        return CheckResult(
            rating="LC",
            finding=f"Only {p.gap_rows} gaps found. Coverage may be incomplete.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No gaps identified.",
        recommended_action="Create Gap Analysis tab mapping current -> target per PA/process.",
        confidence="High",
    )


def ga_04_gap_severity(p: ProbedGapAnalysis) -> CheckResult:
    if p.gap_severity_values:
        severity_list = ", ".join(sorted(p.gap_severity_values))
        return CheckResult(
            rating="FC",
            finding=f"Gap severity classified: {severity_list}.",
            page_section="Gap Analysis tab",
            confidence="High",
        )
    return draft("Verify each gap is classified by severity (Show-stopper / Major / Minor / Observation).")


def ga_05_effort_estimated(p: ProbedGapAnalysis) -> CheckResult:
    if p.effort_estimated:
        return CheckResult(
            rating="FC",
            finding="Effort estimated per gap (person-days, weeks).",
            page_section="Gap Analysis tab",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Effort estimation not found or incomplete.",
        recommended_action="Add Effort column to Gap Analysis tab with person-days or weeks per gap.",
        confidence="High",
    )


def ga_06_quick_wins(p: ProbedGapAnalysis) -> CheckResult:
    if p.quick_wins_identified:
        return CheckResult(
            rating="FC",
            finding="Quick wins identified separately from major initiatives.",
            page_section="Quick Wins tab",
            confidence="High",
        )
    return draft("Identify quick wins (low-effort, high-impact gaps) separately from major initiatives.")


def ga_07_major_initiatives(p: ProbedGapAnalysis) -> CheckResult:
    if p.major_initiatives_present:
        return CheckResult(
            rating="FC",
            finding="Major improvement initiatives planned.",
            page_section="Initiatives / Roadmap tab",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No major initiatives tab found.",
        recommended_action="Create Initiatives tab describing major gap closure programs.",
        confidence="High",
    )


def ga_08_effort_totals(p: ProbedGapAnalysis) -> CheckResult:
    if p.effort_totals_present:
        return CheckResult(
            rating="FC",
            finding="Effort totals calculated and summarized.",
            page_section="Summary tab",
            confidence="High",
        )
    return draft("Verify total effort across all initiatives is reasonable for capability uplift.")


def ga_09_cross_dependencies(p: ProbedGapAnalysis) -> CheckResult:
    if p.cross_process_deps_noted:
        return CheckResult(
            rating="FC",
            finding="Cross-process dependencies documented.",
            page_section="Gap Analysis or Initiatives tab",
            confidence="High",
        )
    return draft("Note any cross-process dependencies (gaps that block closure of other gaps).")


def ga_10_assessment_reference(p: ProbedGapAnalysis) -> CheckResult:
    if p.assessment_ref:
        return CheckResult(
            rating="FC",
            finding=f"Gap Analysis references Assessment: '{p.assessment_ref}'.",
            page_section="Title page",
            confidence="High",
        )
    return draft("Verify Gap Analysis explicitly references the upstream Assessment.")


def ga_11_realistic_timeline(p: ProbedGapAnalysis) -> CheckResult:
    return draft("Verify timeline is realistic (not all initiatives in same month).")


def ga_12_show_stoppers(p: ProbedGapAnalysis) -> CheckResult:
    return draft("Count and highlight Show-stopper gaps as headline finding.")


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedGapAnalysis], CheckResult]


CHECKS: list[CheckDef] = [
    CheckDef("1", "GA", "Gap Identification", "Is current state echoed from Assessment?", "Shall", ga_01_current_state),
    CheckDef("2", "GA", "Gap Identification", "Is target CL stated per process with justification?", "Shall", ga_02_target_cl_justified),
    CheckDef("3", "GA", "Gap Analysis", "Are gaps identified and mapped to specific PA/indicator?", "Shall", ga_03_gaps_mapped),
    CheckDef("4", "GA", "Gap Analysis", "Is gap severity classified (Show-stopper/Major/Minor/Observation)?", "Shall", ga_04_gap_severity),
    CheckDef("5", "GA", "Gap Analysis", "Is effort estimated per gap (person-days, weeks)?", "Shall", ga_05_effort_estimated),
    CheckDef("6", "GA", "Improvement Planning", "Are quick wins identified separately?", "Should", ga_06_quick_wins),
    CheckDef("7", "GA", "Improvement Planning", "Are major improvement initiatives planned?", "Shall", ga_07_major_initiatives),
    CheckDef("8", "GA", "Improvement Planning", "Are effort totals calculated per initiative?", "Should", ga_08_effort_totals),
    CheckDef("9", "GA", "Improvement Planning", "Are cross-process dependencies noted?", "Should", ga_09_cross_dependencies),
    CheckDef("10", "GA", "Document Quality", "Does Gap Analysis reference the upstream Assessment?", "Shall", ga_10_assessment_reference),
    CheckDef("11", "GA", "Document Quality", "Is the timeline realistic (not all initiatives in same month)?", "Should", ga_11_realistic_timeline),
    CheckDef("12", "GA", "Document Quality", "What is the count of Show-stopper gaps?", "Should", ga_12_show_stoppers),
]
