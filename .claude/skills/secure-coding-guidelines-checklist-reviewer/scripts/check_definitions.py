from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from sec_coding_probe import ProbedSecCoding

@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""

def draft(finding: str, page_section: str = "", action: str = "(Reviewer to verify)") -> CheckResult:
    return CheckResult(rating="", finding="(Auto-suggest) " + finding, page_section=page_section, recommended_action=action, confidence="Low")

def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, confidence="High")

def cr_01_structure(p: ProbedSecCoding) -> CheckResult:
    if len(p.sheet_names) >= 8: return CheckResult(rating="FC", finding=f"{len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Add more tabs.", confidence="Medium")

def cr_02_title(p: ProbedSecCoding) -> CheckResult:
    return CheckResult(rating="FC" if p.title else "NO", finding=f"Title: {p.title}" if p.title else "No title.", recommended_action="" if p.title else "Add title.", confidence="High")

def cr_03_author_approver(p: ProbedSecCoding) -> CheckResult:
    if p.author and p.approver: return CheckResult(rating="FC", finding=f"Author: {p.author}, Approver: {p.approver}", confidence="High")
    return CheckResult(rating="NO", finding="Missing author/approver.", recommended_action="Populate author/approver.", confidence="High")

def cr_04_revision(p: ProbedSecCoding) -> CheckResult:
    return CheckResult(rating="FC" if p.revision else "NO", finding=f"Revision: {p.revision}" if p.revision else "No revision.", recommended_action="" if p.revision else "Add revision.", confidence="High")

def cr_05_status(p: ProbedSecCoding) -> CheckResult:
    return CheckResult(rating="FC" if p.status else "NO", finding=f"Status: {p.status}" if p.status else "No status.", recommended_action="" if p.status else "Add status.", confidence="High")

def cr_06_docid(p: ProbedSecCoding) -> CheckResult:
    return CheckResult(rating="LC" if p.doc_id else "PC", finding=f"Doc ID: {p.doc_id}" if p.doc_id else "No doc ID.", recommended_action="" if p.doc_id else "Add unique doc ID.", confidence="High")

def cr_07_toc(p: ProbedSecCoding) -> CheckResult:
    return CheckResult(rating="FC" if "00_Title_Page" in p.sheet_names else "PC", finding="TOC present" if "00_Title_Page" in p.sheet_names else "No TOC.", confidence="High")

def cr_08_refs(p: ProbedSecCoding) -> CheckResult:
    refs = any("reference" in s.lower() for s in p.sheet_names)
    return CheckResult(rating="FC" if refs else "PC", finding="References tab present" if refs else "No references.", confidence="Medium")

def cr_09_assumptions(p: ProbedSecCoding) -> CheckResult:
    return draft("Assumptions and scope documented.", action="Verify assumptions section.")

def cr_10_hyperlinks(p: ProbedSecCoding) -> CheckResult:
    return draft("Cross-references support navigation.", action="Check cross-reference completeness.")

def cr_11_search(p: ProbedSecCoding) -> CheckResult:
    if len(p.sheet_names) > 5: return CheckResult(rating="LC", finding="Sufficient tab structure.", confidence="Medium")
    return CheckResult(rating="PC", finding="Limited search support.", recommended_action="Add more tabs.", confidence="Medium")

def cr_12_terminology(p: ProbedSecCoding) -> CheckResult:
    return draft("Glossary/abbreviations defined.", action="Ensure terminology documented.")

def cr_13_traceability(p: ProbedSecCoding) -> CheckResult:
    return draft("Guidelines should be traceable to CWE/CERT/MISRA.", action="Verify traceability.")

def cr_14_review(p: ProbedSecCoding) -> CheckResult:
    if p.author and p.approver: return CheckResult(rating="FC", finding="Review/approval personnel identified.", confidence="High")
    return CheckResult(rating="PC", finding="Review/approval unclear.", recommended_action="Add formal review fields.", confidence="Medium")

def fsa_01_scope(p: ProbedSecCoding) -> CheckResult:
    if p.scope_defined: return CheckResult(rating="FC", finding="Scope clearly defines codebase, language, target CAL.", confidence="Medium")
    return CheckResult(rating="NO", finding="No scope defined.", recommended_action="Define scope in 02_Scope tab.", confidence="High")

def fsa_02_rules_catalog(p: ProbedSecCoding) -> CheckResult:
    if p.coding_rules >= 30: return CheckResult(rating="FC", finding=f"Coding rules catalog: {p.coding_rules} rules (>= 30).", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.coding_rules} rules; min 30 typical.", recommended_action="Expand coding rules catalog.", confidence="High")

def fsa_03_cert_misra(p: ProbedSecCoding) -> CheckResult:
    cert_covered = any("cert" in s.lower() for s in p.sheet_names)
    misra_covered = any("misra" in s.lower() for s in p.sheet_names)
    if cert_covered or misra_covered: return CheckResult(rating="FC", finding="CERT/MISRA categories represented.", confidence="Medium")
    return CheckResult(rating="PC", finding="No explicit CERT/MISRA coverage.", recommended_action="Add CERT C / MISRA Amendment 1 rules.", confidence="Medium")

def fsa_04_autosar(p: ProbedSecCoding) -> CheckResult:
    autosar = any("autosar" in s.lower() for s in p.sheet_names)
    return draft("AUTOSAR C++14 secure subset referenced if C++ in scope.") if not autosar else CheckResult(rating="LC", finding="AUTOSAR C++14 referenced.", confidence="Medium")

def fsa_05_cwe_coverage(p: ProbedSecCoding) -> CheckResult:
    if p.cwe_coverage >= 20: return CheckResult(rating="FC", finding=f"CWE Top 25 coverage: {p.cwe_coverage} CWEs mapped.", confidence="High")
    return CheckResult(rating="PC", finding=f"Limited CWE coverage ({p.cwe_coverage}).", recommended_action="Map all CWE Top 25 to addressing rules.", confidence="High")

def fsa_06_memory_safety(p: ProbedSecCoding) -> CheckResult:
    if p.memory_safety_rules > 0: return CheckResult(rating="FC", finding=f"Memory safety: {p.memory_safety_rules} rules (bounds/UAF/double-free).", confidence="High")
    return CheckResult(rating="NO", finding="No memory safety rules.", recommended_action="Add memory safety rules (bounds checking, UAF, double-free).", confidence="High")

def fsa_07_integer_safety(p: ProbedSecCoding) -> CheckResult:
    if p.integer_safety_rules > 0: return CheckResult(rating="FC", finding=f"Integer safety: {p.integer_safety_rules} rules (overflow/underflow/sign conversion).", confidence="High")
    return CheckResult(rating="NO", finding="No integer safety rules.", recommended_action="Add integer safety rules.", confidence="High")

def fsa_08_crypto_rules(p: ProbedSecCoding) -> CheckResult:
    if p.crypto_rules > 0:
        banned = any("md5" in r.lower() or "sha1" in r.lower() or "des" in r.lower() for r in [str(p.crypto_rules)])
        if not banned: return CheckResult(rating="FC", finding=f"Crypto: {p.crypto_rules} rules; no deprecated algorithms.", confidence="High")
        return CheckResult(rating="PC", finding=f"Crypto: {p.crypto_rules} rules; verify no MD5/SHA1/DES.", recommended_action="Ban deprecated algorithms (MD5, SHA1, DES, RC4).", confidence="Medium")
    return CheckResult(rating="NO", finding="No cryptography rules.", recommended_action="Add crypto rules (min key lengths, no deprecated algs).", confidence="High")

def fsa_09_auth_rules(p: ProbedSecCoding) -> CheckResult:
    if p.auth_rules > 0: return CheckResult(rating="FC", finding=f"Authentication/authorization: {p.auth_rules} rules (principle of least privilege).", confidence="High")
    return CheckResult(rating="PC", finding="Limited auth rules.", recommended_action="Add authentication/authorization rules.", confidence="High")

def fsa_10_logging_rules(p: ProbedSecCoding) -> CheckResult:
    if p.logging_rules > 0: return CheckResult(rating="FC", finding=f"Logging: {p.logging_rules} rules (no secrets/PII).", confidence="High")
    return CheckResult(rating="PC", finding="Limited logging rules.", recommended_action="Add logging rules forbidding secrets/PII.", confidence="High")

def fsa_11_string_io(p: ProbedSecCoding) -> CheckResult:
    if p.string_io_rules > 0: return CheckResult(rating="LC", finding=f"String/IO: {p.string_io_rules} rules.", confidence="High")
    return CheckResult(rating="PC", finding="No string/IO rules.", recommended_action="Add string/IO safety rules.", confidence="High")

def fsa_12_tool_config(p: ProbedSecCoding) -> CheckResult:
    if p.tool_configs > 0: return CheckResult(rating="FC", finding=f"Tool configs: {p.tool_configs} static analysis tools (Coverity/CodeSonar/Polyspace).", confidence="High")
    return CheckResult(rating="PC", finding="No tool configurations.", recommended_action="Provide tool configuration per Coverity/CodeSonar/Polyspace.", confidence="High")

def fsa_13_deviation_process(p: ProbedSecCoding) -> CheckResult:
    if p.deviation_process: return CheckResult(rating="FC", finding="Deviation process documented with approval workflow.", confidence="Medium")
    return CheckResult(rating="PC", finding="No deviation process.", recommended_action="Define deviation process with approval workflow.", confidence="High")

def fsa_14_standards_ref(p: ProbedSecCoding) -> CheckResult:
    refs = "11_References" in p.sheet_names or any("reference" in s.lower() for s in p.sheet_names)
    if refs: return CheckResult(rating="LC", finding="Standards references present.", confidence="Medium")
    return CheckResult(rating="PC", finding="No explicit standards references.", recommended_action="Reference ISO/SAE 21434, CERT, MISRA, CWE, AUTOSAR.", confidence="Medium")

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
def va_13_training(p): return va_01_external("Developer training")
def va_14_metrics(p): return va_01_external("Quality metrics and KPIs")

@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedSecCoding], CheckResult]

CHECKS: list[CheckDef] = [
    CheckDef("1", "CR", "Document Quality", "Is document structured?", "Shall", cr_01_structure),
    CheckDef("2", "CR", "Document Quality", "Is title present?", "Shall", cr_02_title),
    CheckDef("3", "CR", "Document Quality", "Author/approver listed?", "Shall", cr_03_author_approver),
    CheckDef("4", "CR", "Document Quality", "Revision identified?", "Shall", cr_04_revision),
    CheckDef("5", "CR", "Document Quality", "Status provided?", "Shall", cr_05_status),
    CheckDef("6", "CR", "Document Quality", "Document ID unique?", "Should", cr_06_docid),
    CheckDef("7", "CR", "Document Quality", "TOC present?", "Shall", cr_07_toc),
    CheckDef("8", "CR", "Document Quality", "References listed?", "Should", cr_08_refs),
    CheckDef("9", "CR", "Document Quality", "Assumptions documented?", "Should", cr_09_assumptions),
    CheckDef("10", "CR", "Document Quality", "Cross-references present?", "Should", cr_10_hyperlinks),
    CheckDef("11", "CR", "Document Quality", "Searchability supported?", "Should", cr_11_search),
    CheckDef("12", "CR", "Document Quality", "Terminology defined?", "Should", cr_12_terminology),
    CheckDef("13", "CR", "Document Quality", "Traceability clear?", "Should", cr_13_traceability),
    CheckDef("14", "CR", "Document Quality", "Review/approval present?", "Shall", cr_14_review),
    CheckDef("1", "SCG", "Scope & Rules", "Is scope clearly defined?", "Shall", fsa_01_scope),
    CheckDef("2", "SCG", "Scope & Rules", "Coding rules catalog populated?", "Shall", fsa_02_rules_catalog),
    CheckDef("3", "SCG", "CERT/MISRA", "CERT C categories represented?", "Shall", fsa_03_cert_misra),
    CheckDef("4", "SCG", "CERT/MISRA", "AUTOSAR C++14 referenced?", "Should", fsa_04_autosar),
    CheckDef("5", "SCG", "CWE Coverage", "CWE Top 25 mapped?", "Shall", fsa_05_cwe_coverage),
    CheckDef("6", "SCG", "Memory Safety", "Memory safety rules present?", "Shall", fsa_06_memory_safety),
    CheckDef("7", "SCG", "Integer Safety", "Integer safety rules present?", "Shall", fsa_07_integer_safety),
    CheckDef("8", "SCG", "Cryptography", "Crypto rules present?", "Shall", fsa_08_crypto_rules),
    CheckDef("9", "SCG", "Authentication", "Auth/authz rules present?", "Shall", fsa_09_auth_rules),
    CheckDef("10", "SCG", "Logging & Audit", "Logging rules present?", "Shall", fsa_10_logging_rules),
    CheckDef("11", "SCG", "String/IO", "String/IO rules present?", "Should", fsa_11_string_io),
    CheckDef("12", "SCG", "Tool Configuration", "Tool configs provided?", "Shall", fsa_12_tool_config),
    CheckDef("13", "SCG", "Deviation Process", "Deviation process documented?", "Should", fsa_13_deviation_process),
    CheckDef("14", "SCG", "Standards", "Standards references present?", "Should", fsa_14_standards_ref),
    CheckDef("1", "VA", "Verification Planning", "Verification plan adequate?", "Shall", va_01_planning),
    CheckDef("2", "VA", "Verification Planning", "Specifications complete?", "Shall", va_02_specs),
    CheckDef("3", "VA", "Verification Specification", "Test cases defined?", "Shall", va_03_testing),
    CheckDef("4", "VA", "Verification Specification", "Test environment configured?", "Shall", va_04_execution),
    CheckDef("5", "VA", "Verification Execution", "Verification executed?", "Shall", va_05_report),
    CheckDef("6", "VA", "Verification Execution", "Report adequate?", "Shall", va_06_coverage),
    CheckDef("7", "VA", "Verification Evaluation", "Coverage adequate?", "Shall", va_07_anomalies),
    CheckDef("8", "VA", "Verification Evaluation", "Anomaly handling documented?", "Should", va_08_regression),
    CheckDef("9", "VA", "Regression Testing", "Regression strategy defined?", "Should", va_09_traceability),
    CheckDef("10", "VA", "Traceability", "Traceability complete?", "Shall", va_10_independence),
    CheckDef("11", "VA", "Independence", "Verification independent?", "Should", va_11_standards),
    CheckDef("12", "VA", "Review & Approval", "Qualified reviewers assigned?", "Shall", va_12_roles),
    CheckDef("13", "VA", "Training", "Developer training documented?", "Should", va_13_training),
    CheckDef("14", "VA", "Quality Metrics", "KPIs tracked?", "Should", va_14_metrics),
]
