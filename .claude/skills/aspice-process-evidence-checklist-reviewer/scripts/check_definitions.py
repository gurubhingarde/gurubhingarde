"""ASPICE Process Evidence canonical checklist definitions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from aspice_evidence_probe import ProbedProcessEvidence

@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""

def draft(finding: str, action: str = "(Reviewer to verify)") -> CheckResult:
    return CheckResult(rating="", finding="(Auto-suggest, requires reviewer judgment) " + finding, recommended_action=action, confidence="Low")

def pe_01_process_desc(p: ProbedProcessEvidence) -> CheckResult:
    if p.process_desc_present:
        return CheckResult(rating="FC", finding="Process description complete (purpose, scope, inputs, outputs, owner).", confidence="High")
    return CheckResult(rating="NO", finding="No process description found.", recommended_action="Create Process Description tab with purpose, scope, inputs, outputs, owner.", confidence="High")

def pe_02_bp_evidence(p: ProbedProcessEvidence) -> CheckResult:
    if p.bp_evidence_rows >= 5:
        return CheckResult(rating="FC", finding=f"BP evidence inventory complete ({p.bp_evidence_rows} rows with document references).", confidence="High")
    return draft("Verify every Base Practice has document reference in evidence inventory.")

def pe_03_gp_evidence(p: ProbedProcessEvidence) -> CheckResult:
    if p.gp_evidence_rows >= 3:
        return CheckResult(rating="FC", finding=f"GP evidence inventory complete per CL ({p.gp_evidence_rows} rows).", confidence="High")
    return draft("Verify every Generic Practice per target CL has document reference.")

def pe_04_doc_references(p: ProbedProcessEvidence) -> CheckResult:
    if p.bp_evidence_rows > 0 and p.gp_evidence_rows > 0:
        return draft("Verify document references resolve (path/record/query) and accessibility is populated (Y/N).")
    return CheckResult(rating="NO", finding="Evidence inventory incomplete.", confidence="High")

def pe_05_work_products(p: ProbedProcessEvidence) -> CheckResult:
    if p.work_products_rows >= 3:
        return CheckResult(rating="FC", finding=f"Work products inventoried with version control ({p.work_products_rows} items).", confidence="High")
    return draft("Ensure work products are inventoried with version control references.")

def pe_06_perf_records(p: ProbedProcessEvidence) -> CheckResult:
    if p.perf_records_present:
        return CheckResult(rating="FC", finding="Process performance records present (review minutes, action logs).", confidence="High")
    return draft("Add process performance records (reviews, actions) to evidence package.")

def pe_07_quant_metrics(p: ProbedProcessEvidence) -> CheckResult:
    if p.metrics_present:
        return CheckResult(rating="FC", finding="Quantitative performance metrics present for CL3+ processes.", confidence="High")
    return draft("For CL3+ target, include quantitative performance metrics (schedule, defect density, effort).")

def pe_08_improv_log(p: ProbedProcessEvidence) -> CheckResult:
    if p.improv_log_present:
        return CheckResult(rating="FC", finding="Process improvement log shows continuous improvement (CL3+).", confidence="High")
    return draft("Add process improvement log documenting changes over assessment window.")

def pe_09_evidence_current(p: ProbedProcessEvidence) -> CheckResult:
    if p.evidence_current:
        return CheckResult(rating="FC", finding="Evidence is current (within assessment evidence collection window).", confidence="Medium")
    return draft("Verify all evidence is within assessment window (typically 12 months).")

def pe_10_evidence_accessible(p: ProbedProcessEvidence) -> CheckResult:
    if p.evidence_accessible:
        return CheckResult(rating="FC", finding="Evidence is accessible to assessor (locations documented).", confidence="Medium")
    return draft("Ensure all referenced evidence locations are accessible to assessor; document access method.")

def pe_11_cross_refs(p: ProbedProcessEvidence) -> CheckResult:
    if p.cross_refs_present:
        return CheckResult(rating="FC", finding="Cross-references between work products and BPs present.", confidence="High")
    return draft("Add cross-references linking work products to supporting Base Practices.")

def pe_12_process_owner(p: ProbedProcessEvidence) -> CheckResult:
    if p.process_owner:
        return CheckResult(rating="FC", finding=f"Process owner identified: '{p.process_owner}' and contactable.", confidence="High")
    return CheckResult(rating="NO", finding="Process owner not identified.", recommended_action="Identify and document process owner contact information.", confidence="High")

def pe_13_sample_quality(p: ProbedProcessEvidence) -> CheckResult:
    return draft("Review sample evidence for quality (completeness, accuracy, traceability).")

def pe_14_assessment_plan_ref(p: ProbedProcessEvidence) -> CheckResult:
    return draft("Verify evidence package references the upstream Assessment Plan.")

@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedProcessEvidence], CheckResult]

CHECKS: list[CheckDef] = [
    CheckDef("1", "PE", "Process Documentation", "Is process description complete (purpose, scope, inputs, outputs, owner)?", "Shall", pe_01_process_desc),
    CheckDef("2", "PE", "Evidence Inventory", "Is BP evidence inventory complete (every BP has document reference)?", "Shall", pe_02_bp_evidence),
    CheckDef("3", "PE", "Evidence Inventory", "Is GP evidence inventory complete (every GP per CL has reference)?", "Shall", pe_03_gp_evidence),
    CheckDef("4", "PE", "Evidence Inventory", "Do document references resolve and is accessibility documented?", "Shall", pe_04_doc_references),
    CheckDef("5", "PE", "Work Products", "Are work products inventoried with version control reference?", "Shall", pe_05_work_products),
    CheckDef("6", "PE", "Process Performance", "Are process performance records present (reviews, actions)?", "Shall", pe_06_perf_records),
    CheckDef("7", "PE", "Process Performance", "Are quantitative performance metrics present for CL3+ processes?", "Should", pe_07_quant_metrics),
    CheckDef("8", "PE", "Process Improvement", "Does process improvement log show continuous improvement (CL3+)?", "Should", pe_08_improv_log),
    CheckDef("9", "PE", "Evidence Timeliness", "Is evidence current (within assessment evidence collection window)?", "Shall", pe_09_evidence_current),
    CheckDef("10", "PE", "Evidence Access", "Is evidence accessible to the assessor (locations documented)?", "Shall", pe_10_evidence_accessible),
    CheckDef("11", "PE", "Cross-References", "Are there cross-references between work products and BPs?", "Should", pe_11_cross_refs),
    CheckDef("12", "PE", "Document Quality", "Is process owner identified and contactable?", "Shall", pe_12_process_owner),
    CheckDef("13", "PE", "Document Quality", "Is sample evidence reviewed for quality?", "Should", pe_13_sample_quality),
    CheckDef("14", "PE", "Document Quality", "Does evidence package reference the Assessment Plan?", "Should", pe_14_assessment_plan_ref),
]
