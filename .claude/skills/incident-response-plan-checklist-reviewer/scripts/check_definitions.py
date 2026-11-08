from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from irp_probe import ProbedIRP

@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""

def draft(finding: str, page_section: str = "", action: str = "(Reviewer to verify)") -> CheckResult:
    return CheckResult(rating="", finding="(Auto-suggest, requires reviewer judgment) " + finding, page_section=page_section, recommended_action=action, confidence="Low")

def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, confidence="High")

def cr_01_structure(p: ProbedIRP) -> CheckResult:
    if len(p.sheet_names) >= 8: return CheckResult(rating="FC", finding=f"{len(p.sheet_names)} tabs structured logically.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Add more granular tabs.", confidence="Medium")

def cr_02_title(p: ProbedIRP) -> CheckResult:
    return CheckResult(rating="FC" if p.title else "NO", finding=f"Title: {p.title}" if p.title else "No title.", recommended_action="" if p.title else "Add title.", confidence="High")

def cr_03_author_approver(p: ProbedIRP) -> CheckResult:
    if p.author and p.approver: return CheckResult(rating="FC", finding=f"Author: {p.author}, Approver: {p.approver}", confidence="High")
    return CheckResult(rating="NO", finding="Missing author/approver.", recommended_action="Populate author/approver.", confidence="High")

def cr_04_revision(p: ProbedIRP) -> CheckResult:
    return CheckResult(rating="FC" if p.revision else "NO", finding=f"Revision: {p.revision}" if p.revision else "No revision.", recommended_action="" if p.revision else "Add revision.", confidence="High")

def cr_05_status(p: ProbedIRP) -> CheckResult:
    return CheckResult(rating="FC" if p.status else "NO", finding=f"Status: {p.status}" if p.status else "No status.", recommended_action="" if p.status else "Add status.", confidence="High")

def cr_06_docid(p: ProbedIRP) -> CheckResult:
    return CheckResult(rating="LC" if p.doc_id else "PC", finding=f"Doc ID: {p.doc_id}" if p.doc_id else "No doc ID.", recommended_action="" if p.doc_id else "Add unique doc ID.", confidence="High")

def cr_07_toc(p: ProbedIRP) -> CheckResult:
    return CheckResult(rating="FC" if "00_Title_Page" in p.sheet_names else "PC", finding="TOC present" if "00_Title_Page" in p.sheet_names else "No TOC.", confidence="High")

def cr_08_refs(p: ProbedIRP) -> CheckResult:
    refs = any("reference" in s.lower() for s in p.sheet_names)
    return CheckResult(rating="FC" if refs else "PC", finding="References tab present" if refs else "No references.", confidence="Medium")

def cr_09_assumptions(p: ProbedIRP) -> CheckResult:
    return draft("Assumptions and scope should be documented.", action="Verify assumptions section.")

def cr_10_hyperlinks(p: ProbedIRP) -> CheckResult:
    return draft("Cross-references support navigation.", action="Check cross-reference completeness.")

def cr_11_search(p: ProbedIRP) -> CheckResult:
    if len(p.sheet_names) > 5: return CheckResult(rating="LC", finding="Sufficient tab structure for search.", confidence="Medium")
    return CheckResult(rating="PC", finding="Limited search support.", recommended_action="Add more tabs.", confidence="Medium")

def cr_12_terminology(p: ProbedIRP) -> CheckResult:
    return draft("Glossary/abbreviations should be defined.", action="Ensure terminology documented.")

def cr_13_traceability(p: ProbedIRP) -> CheckResult:
    return draft("PSIRT process should be traceable through all phases.", action="Verify process traceability.")

def cr_14_review(p: ProbedIRP) -> CheckResult:
    if p.author and p.approver: return CheckResult(rating="FC", finding="Review/approval personnel identified.", confidence="High")
    return CheckResult(rating="PC", finding="Review/approval status unclear.", recommended_action="Add formal review fields.", confidence="Medium")

def fsa_01_psirt_roster(p: ProbedIRP) -> CheckResult:
    if p.psirt_members > 0: return CheckResult(rating="FC", finding=f"PSIRT roster: {p.psirt_members} members with 24/7 coverage defined.", confidence="High")
    return CheckResult(rating="NO", finding="PSIRT roster not populated.", recommended_action="Populate 02_PSIRT_Roster with 24/7 coverage.", confidence="High")

def fsa_02_triage_sla(p: ProbedIRP) -> CheckResult:
    if p.triage_severities > 0: return CheckResult(rating="FC", finding=f"{p.triage_severities} severity levels with SLAs defined.", confidence="High")
    return CheckResult(rating="NO", finding="No triage SLAs defined.", recommended_action="Define severity levels and SLAs.", confidence="High")

def fsa_03_detection(p: ProbedIRP) -> CheckResult:
    if p.detection_sources > 0: return CheckResult(rating="FC", finding=f"{p.detection_sources} detection sources documented.", confidence="High")
    return CheckResult(rating="PC", finding="Limited detection sources.", recommended_action="Expand detection sources.", confidence="Medium")

def fsa_04_response_stages(p: ProbedIRP) -> CheckResult:
    if p.response_stages >= 6: return CheckResult(rating="FC", finding=f"{p.response_stages} response stages (Detect/Triage/Contain/Eradicate/Recover/Post-mortem).", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.response_stages} stages defined.", recommended_action="Define all 6 response workflow stages.", confidence="High")

def fsa_05_disclosure(p: ProbedIRP) -> CheckResult:
    if p.disclosure_policy: return CheckResult(rating="FC", finding="Coordinated disclosure policy with embargo period defined.", confidence="Medium")
    return CheckResult(rating="NO", finding="No disclosure policy.", recommended_action="Define coordinated disclosure policy.", confidence="High")

def fsa_06_ota(p: ProbedIRP) -> CheckResult:
    if p.oui_workflow: return CheckResult(rating="FC", finding="OTA patch workflow with gates and rollback plan documented.", confidence="Medium")
    return CheckResult(rating="PC", finding="Limited OTA patch workflow detail.", recommended_action="Define OTA workflow with rollback.", confidence="High")

def fsa_07_regulatory(p: ProbedIRP) -> CheckResult:
    if p.regulatory_notifs >= 4: return CheckResult(rating="FC", finding=f"{p.regulatory_notifs} regulatory notification types (UN R155 72h, ENISA, NHTSA, JAMA).", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.regulatory_notifs} notification types.", recommended_action="Add UN R155, ENISA, NHTSA, JAMA notification procedures.", confidence="High")

def fsa_08_customer_comms(p: ProbedIRP) -> CheckResult:
    if p.customer_comms > 0: return CheckResult(rating="FC", finding=f"{p.customer_comms} customer communication templates/procedures.", confidence="High")
    return CheckResult(rating="PC", finding="Limited customer communication plan.", recommended_action="Define customer communication playbook.", confidence="High")

def fsa_09_post_incident(p: ProbedIRP) -> CheckResult:
    if p.post_incident: return CheckResult(rating="FC", finding="Post-incident review template and process defined.", confidence="Medium")
    return CheckResult(rating="PC", finding="No post-incident review process.", recommended_action="Define post-incident review procedure.", confidence="High")

def fsa_10_templates(p: ProbedIRP) -> CheckResult:
    if p.templates >= 3: return CheckResult(rating="FC", finding=f"{p.templates} communication templates (researcher ack, CVE notice, customer bulletin).", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.templates} templates.", recommended_action="Provide at least 3 templates.", confidence="High")

def fsa_11_psirt_lead(p: ProbedIRP) -> CheckResult:
    return draft("PSIRT lead and backup should be identified.", action="Confirm PSIRT leadership.")

def fsa_12_legal_comms(p: ProbedIRP) -> CheckResult:
    return draft("PSIRT roster should include Legal and Communications representatives.", action="Verify Legal/Comms representation.")

def fsa_13_cvss(p: ProbedIRP) -> CheckResult:
    return draft("CVSS thresholds should be mapped to severity levels.", action="Confirm CVSS mapping.")

def fsa_14_standards(p: ProbedIRP) -> CheckResult:
    return draft("References to ISO/SAE 21434 and FIRST.org PSIRT framework should be present.", action="Verify standards references.")

def va_01_external(label):
    return draft(f"{label} - external V&V Plan.", action="Verify against Verification Plan.")

def va_01_planning(p): return va_01_external("Verification planning")
def va_02_specs(p): return va_01_external("Verification specifications")
def va_03_testing(p): return va_01_external("Test case definition")
def va_04_execution(p): return va_01_external("Test execution")
def va_05_report(p): return va_01_external("Verification Report")
def va_06_coverage(p): return va_01_external("Coverage metrics")
def va_07_anomalies(p): return va_01_external("Anomaly handling")
def va_08_regression(p): return va_01_external("Regression testing")
def va_09_traceability(p): return va_01_external("Traceability matrix")
def va_10_independence(p): return va_01_external("Verification independence")
def va_11_standards(p): return va_01_external("Standards compliance")
def va_12_roles(p): return CheckResult(rating="FC" if p.approver else "PC", finding="Qualified reviewers assigned" if p.approver else "Reviewers not assigned.", confidence="High")
def va_13_training(p): return va_01_external("PSIRT team training")
def va_14_metrics(p): return va_01_external("Quality metrics and KPIs")

@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedIRP], CheckResult]

CHECKS: list[CheckDef] = [
    CheckDef("1", "CR", "Document Quality", "Is document structured clearly?", "Shall", cr_01_structure),
    CheckDef("2", "CR", "Document Quality", "Is title present?", "Shall", cr_02_title),
    CheckDef("3", "CR", "Document Quality", "Are author/approver listed?", "Shall", cr_03_author_approver),
    CheckDef("4", "CR", "Document Quality", "Is revision identified?", "Shall", cr_04_revision),
    CheckDef("5", "CR", "Document Quality", "Is status provided?", "Shall", cr_05_status),
    CheckDef("6", "CR", "Document Quality", "Is document ID unique?", "Should", cr_06_docid),
    CheckDef("7", "CR", "Document Quality", "Is TOC present?", "Shall", cr_07_toc),
    CheckDef("8", "CR", "Document Quality", "Are references listed?", "Should", cr_08_refs),
    CheckDef("9", "CR", "Document Quality", "Are assumptions documented?", "Should", cr_09_assumptions),
    CheckDef("10", "CR", "Document Quality", "Are cross-references present?", "Should", cr_10_hyperlinks),
    CheckDef("11", "CR", "Document Quality", "Is searchability supported?", "Should", cr_11_search),
    CheckDef("12", "CR", "Document Quality", "Is terminology defined?", "Should", cr_12_terminology),
    CheckDef("13", "CR", "Document Quality", "Is traceability clear?", "Should", cr_13_traceability),
    CheckDef("14", "CR", "Document Quality", "Are review/approval present?", "Shall", cr_14_review),
    CheckDef("1", "IRP", "PSIRT Organization", "Is PSIRT roster populated with 24/7 coverage?", "Shall", fsa_01_psirt_roster),
    CheckDef("2", "IRP", "Triage Classification", "Are severity levels with SLAs defined?", "Shall", fsa_02_triage_sla),
    CheckDef("3", "IRP", "Detection & Intake", "Are detection sources documented?", "Shall", fsa_03_detection),
    CheckDef("4", "IRP", "Response Workflow", "Are all 6 response stages defined?", "Shall", fsa_04_response_stages),
    CheckDef("5", "IRP", "Coordinated Disclosure", "Is disclosure policy with embargo documented?", "Shall", fsa_05_disclosure),
    CheckDef("6", "IRP", "OTA Patch Workflow", "Is OTA workflow with rollback plan defined?", "Shall", fsa_06_ota),
    CheckDef("7", "IRP", "Regulatory Notifications", "Are UN R155, ENISA, NHTSA, JAMA covered?", "Shall", fsa_07_regulatory),
    CheckDef("8", "IRP", "Customer Communications", "Are communication templates/procedures defined?", "Shall", fsa_08_customer_comms),
    CheckDef("9", "IRP", "Post-Incident Review", "Is post-incident review process documented?", "Shall", fsa_09_post_incident),
    CheckDef("10", "IRP", "Communication Templates", "Are at least 3 templates provided?", "Should", fsa_10_templates),
    CheckDef("11", "IRP", "PSIRT Leadership", "Is PSIRT lead and backup identified?", "Should", fsa_11_psirt_lead),
    CheckDef("12", "IRP", "PSIRT Composition", "Does PSIRT include Legal and Communications?", "Should", fsa_12_legal_comms),
    CheckDef("13", "IRP", "CVSS Mapping", "Are CVSS thresholds mapped to severity?", "Should", fsa_13_cvss),
    CheckDef("14", "IRP", "Standards References", "Are ISO/SAE 21434 and FIRST.org referenced?", "Should", fsa_14_standards),
    CheckDef("1", "VA", "Verification Planning", "Is verification plan adequate?", "Shall", va_01_planning),
    CheckDef("2", "VA", "Verification Planning", "Are specifications complete?", "Shall", va_02_specs),
    CheckDef("3", "VA", "Verification Specification", "Are test cases defined?", "Shall", va_03_testing),
    CheckDef("4", "VA", "Verification Specification", "Is test environment configured?", "Shall", va_04_execution),
    CheckDef("5", "VA", "Verification Execution", "Was verification executed per plan?", "Shall", va_05_report),
    CheckDef("6", "VA", "Verification Execution", "Does report include required content?", "Shall", va_06_coverage),
    CheckDef("7", "VA", "Verification Evaluation", "Is coverage adequate?", "Shall", va_07_anomalies),
    CheckDef("8", "VA", "Verification Evaluation", "Is anomaly handling documented?", "Should", va_08_regression),
    CheckDef("9", "VA", "Regression Testing", "Is regression strategy defined?", "Should", va_09_traceability),
    CheckDef("10", "VA", "Traceability", "Is traceability complete?", "Shall", va_10_independence),
    CheckDef("11", "VA", "Independence", "Is verification independent?", "Should", va_11_standards),
    CheckDef("12", "VA", "Review & Approval", "Are qualified reviewers assigned?", "Shall", va_12_roles),
    CheckDef("13", "VA", "Training & Competency", "Is PSIRT team training documented?", "Should", va_13_training),
    CheckDef("14", "VA", "Quality Metrics", "Are KPIs tracked?", "Should", va_14_metrics),
]
