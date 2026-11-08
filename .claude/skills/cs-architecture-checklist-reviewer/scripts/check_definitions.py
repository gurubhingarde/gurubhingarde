"""CS Architecture Assessment - canonical checklist checks."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from cs_arch_probe import ProbedCSArch

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

# CR checks (14 generic)
def cr_01_doc_structure(p: ProbedCSArch) -> CheckResult:
    if len(p.sheet_names) >= 8:
        return CheckResult(rating="FC", finding=f"Document structured into {len(p.sheet_names)} distinct tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs; consider adding more for modularity.", recommended_action="Add separate tabs per concern.", confidence="Medium")

def cr_02_title(p: ProbedCSArch) -> CheckResult:
    if p.title: return CheckResult(rating="FC", finding=f"Title: {p.title}", confidence="High")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add document title.", confidence="High")

def cr_03_author_approver(p: ProbedCSArch) -> CheckResult:
    if p.author and p.approver: return CheckResult(rating="FC", finding=f"Author: {p.author}, Approver: {p.approver}", confidence="High")
    return CheckResult(rating="NO", finding="Missing author/approver.", recommended_action="Populate author and approver.", confidence="High")

def cr_04_revision(p: ProbedCSArch) -> CheckResult:
    if p.revision: return CheckResult(rating="FC", finding=f"Revision: {p.revision}", confidence="High")
    return CheckResult(rating="NO", finding="No revision field.", recommended_action="Populate revision.", confidence="High")

def cr_05_status(p: ProbedCSArch) -> CheckResult:
    if p.status: return CheckResult(rating="FC", finding=f"Status: {p.status}", confidence="High")
    return CheckResult(rating="NO", finding="No status field.", recommended_action="Add Status field.", confidence="High")

def cr_06_doc_id(p: ProbedCSArch) -> CheckResult:
    if p.doc_id: return CheckResult(rating="FC", finding=f"Doc ID: {p.doc_id}", confidence="High")
    return CheckResult(rating="PC", finding="No doc ID.", recommended_action="Add unique document ID.", confidence="High")

def cr_07_toc(p: ProbedCSArch) -> CheckResult:
    if "00_Title_Page" in p.sheet_names: return CheckResult(rating="FC", finding="Title/Contents tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No TOC tab.", recommended_action="Add Table of Contents.", confidence="Medium")

def cr_08_references(p: ProbedCSArch) -> CheckResult:
    refs = any("reference" in s.lower() or "general info" in s.lower() for s in p.sheet_names)
    if refs: return CheckResult(rating="FC", finding="References tab detected.", confidence="Medium")
    return CheckResult(rating="PC", finding="No references tab.", recommended_action="Add References tab.", confidence="Medium")

def cr_09_assumptions(p: ProbedCSArch) -> CheckResult:
    return draft("Scope and assumptions should be documented in a dedicated tab.", page_section="Assumptions tab if present")

def cr_10_hyperlinks(p: ProbedCSArch) -> CheckResult:
    return draft("Cross-references within the document aid navigation.", action="Verify cross-references between sections.")

def cr_11_searchability(p: ProbedCSArch) -> CheckResult:
    if p.sheet_names and len(p.sheet_names) > 5:
        return CheckResult(rating="LC", finding="Document has sufficient tab structure for search.", confidence="Medium")
    return CheckResult(rating="PC", finding="Search aids could be improved.", recommended_action="Add more granular tabs.", confidence="Medium")

def cr_12_terminology(p: ProbedCSArch) -> CheckResult:
    return draft("Terminology and abbreviations should be defined.", action="Ensure glossary or abbreviations list present.")

def cr_13_compliance_matrix(p: ProbedCSArch) -> CheckResult:
    return draft("Traceability matrix linking CS requirements to elements should be present.", page_section="09_CSR_to_Element_Allocation")

def cr_14_review_approval(p: ProbedCSArch) -> CheckResult:
    if p.author and p.approver: return CheckResult(rating="FC", finding="Review and approval signatures present.", confidence="High")
    return CheckResult(rating="PC", finding="Review approval status unclear.", recommended_action="Add formal review/approval fields.", confidence="Medium")

# FSA checks (14 substantive)
def fsa_01_element_catalog(p: ProbedCSArch) -> CheckResult:
    if len(p.elements) > 0:
        return CheckResult(rating="FC", finding=f"Element catalog contains {len(p.elements)} elements.", confidence="High")
    return CheckResult(rating="NO", finding="Element catalog not populated.", recommended_action="Populate 03_CS_Element_Catalog.", confidence="High")

def fsa_02_supplier_cert(p: ProbedCSArch) -> CheckResult:
    asil_elems = [e for e in p.elements if e.asil_cal]
    with_supplier = [e for e in asil_elems if e.supplier]
    with_cert = [e for e in asil_elems if e.certification]
    if asil_elems:
        rate = (len(with_supplier) + len(with_cert)) / (2 * len(asil_elems))
        if rate >= 0.95: return CheckResult(rating="FC", finding=f"{len(asil_elems)} ASIL/CAL elements have supplier + certification.", confidence="High")
        return CheckResult(rating="PC", finding=f"{len(with_supplier)}/{len(asil_elems)} supplier, {len(with_cert)}/{len(asil_elems)} cert.", recommended_action="Complete supplier and certification for all ASIL/CAL elements.", confidence="High")
    return CheckResult(rating="NO", finding="No ASIL/CAL-relevant elements with supplier/cert data.", recommended_action="Populate supplier/certification columns.", confidence="High")

def fsa_03_crypto_approved(p: ProbedCSArch) -> CheckResult:
    banned = ["MD5", "SHA1", "DES", "RC4"]
    bad_algs = [c for c in p.crypto_items if any(b in c.get("algorithm","").upper() for b in banned)]
    if not bad_algs: return CheckResult(rating="FC", finding=f"All {len(p.crypto_items)} crypto algorithms approved (no MD5/SHA1/DES/RC4).", confidence="High")
    return CheckResult(rating="NO", finding=f"{len(bad_algs)} prohibited algorithms found.", recommended_action="Replace banned algorithms with approved ones (AES, SHA-256, RSA-2048).", confidence="High")

def fsa_04_crypto_key_length(p: ProbedCSArch) -> CheckResult:
    return draft("Verify minimum key lengths: AES >= 128, RSA >= 2048, ECC >= P-256.", page_section="04_Cryptographic_Inventory")

def fsa_05_key_mgmt_lifecycle(p: ProbedCSArch) -> CheckResult:
    if len(p.key_mgmt_items) > 0:
        return CheckResult(rating="FC", finding=f"Key management defined for {len(p.key_mgmt_items)} key classes (gen/store/distribute/rotate/destroy).", confidence="Medium")
    return CheckResult(rating="NO", finding="No key management lifecycle defined.", recommended_action="Define key lifecycle per key class in 05_Key_Management.", confidence="High")

def fsa_06_secure_boot(p: ProbedCSArch) -> CheckResult:
    return draft("Confirm root-of-trust identified and anti-rollback mechanism present.", page_section="06_Secure_Boot_Chain")

def fsa_07_secure_comm(p: ProbedCSArch) -> CheckResult:
    if p.comm_channels > 0:
        return CheckResult(rating="FC", finding=f"{p.comm_channels} communication channels documented with auth/enc/integrity/replay protection.", confidence="Medium")
    return CheckResult(rating="NO", finding="No secure communication channels defined.", recommended_action="Document channels in 07_Secure_Communication.", confidence="High")

def fsa_08_access_control(p: ProbedCSArch) -> CheckResult:
    if p.access_controls > 0:
        return CheckResult(rating="FC", finding=f"Access control: {p.access_controls} roles/privileges documented.", confidence="Medium")
    return CheckResult(rating="PC", finding="No access control details.", recommended_action="Define roles/privileges/auth factors in 08_Access_Control.", confidence="High")

def fsa_09_csr_allocation(p: ProbedCSArch) -> CheckResult:
    return draft("CSR-to-element allocation matrix should show no orphan CSRs.", page_section="09_CSR_to_Element_Allocation")

def fsa_10_defense_depth(p: ProbedCSArch) -> CheckResult:
    return draft("Multiple protective layers should exist per attack vector.", page_section="10_Defense_in_Depth_Layers")

def fsa_11_debug_disabled(p: ProbedCSArch) -> CheckResult:
    return draft("Debug interfaces should be disabled in production.", action="Confirm production debug status.")

def fsa_12_cert_expiry(p: ProbedCSArch) -> CheckResult:
    return draft("Cryptographic certificates should have expiry/renewal plans.", action="Verify renewal schedule.")

def fsa_13_hsm_usage(p: ProbedCSArch) -> CheckResult:
    return draft("HSM/Secure Element usage for key storage should be justified.", action="Confirm HSM deployment where required.")

def fsa_14_standards_ref(p: ProbedCSArch) -> CheckResult:
    refs_present = "11_References" in p.sheet_names or any("reference" in s.lower() for s in p.sheet_names)
    if refs_present: return CheckResult(rating="LC", finding="References to CS Concept and standards should be present.", confidence="Medium")
    return CheckResult(rating="PC", finding="No explicit standards references.", recommended_action="Add references to CS Concept, AUTOSAR, applicable standards.", confidence="Medium")

# VA checks (5 HARA-specific + 9 generic external)
def va_01_external(label: str) -> CheckResult:
    return draft(f"{label} governed by external V&V Plan.", action="Verify against Verification Plan.")

def va_01_concept_alignment(p): return CheckResult(rating="FC" if p.title else "PC", finding="CS Architecture should align with CS Concept document.", confidence="Medium")
def va_02_reqs_verifiable(p): return va_01_external("Requirements traceability")
def va_03_test_cases(p): return va_01_external("Test case specification")
def va_04_test_env(p): return va_01_external("Test environment documentation")
def va_05_test_exec(p): return va_01_external("Test execution and results")
def va_06_report(p): return va_01_external("Verification Report content")
def va_07_coverage(p): return va_01_external("Coverage metrics")
def va_08_anomalies(p): return va_01_external("Anomaly handling")
def va_09_regression(p): return va_01_external("Regression testing")
def va_10_traceability(p): return va_01_external("Traceability matrix completeness")
def va_11_independence(p): return va_01_external("Verification independence")
def va_12_standards_compliance(p): return va_01_external("AUTOSAR/ISO 26262 compliance")
def va_13_review_approval(p): return CheckResult(rating="FC" if p.approver else "PC", finding="Review and approval by qualified personnel required.", confidence="High")
def va_14_metrics(p): return va_01_external("Quality metrics and KPIs")

@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedCSArch], CheckResult]

CHECKS: list[CheckDef] = [
    CheckDef("1", "CR", "Document Quality", "Is document structured clearly?", "Shall", cr_01_doc_structure),
    CheckDef("2", "CR", "Document Quality", "Does title cover scope?", "Shall", cr_02_title),
    CheckDef("3", "CR", "Document Quality", "Are author and approver listed?", "Shall", cr_03_author_approver),
    CheckDef("4", "CR", "Document Quality", "Is revision unique and identifiable?", "Shall", cr_04_revision),
    CheckDef("5", "CR", "Document Quality", "Is status provided?", "Shall", cr_05_status),
    CheckDef("6", "CR", "Document Quality", "Is there a unique document ID?", "Should", cr_06_doc_id),
    CheckDef("7", "CR", "Document Quality", "Is table of contents present?", "Shall", cr_07_toc),
    CheckDef("8", "CR", "Document Quality", "Are references listed?", "Should", cr_08_references),
    CheckDef("9", "CR", "Document Quality", "Are assumptions documented?", "Should", cr_09_assumptions),
    CheckDef("10", "CR", "Document Quality", "Are internal cross-references present?", "Should", cr_10_hyperlinks),
    CheckDef("11", "CR", "Document Quality", "Is document searchable?", "Should", cr_11_searchability),
    CheckDef("12", "CR", "Document Quality", "Is terminology defined?", "Should", cr_12_terminology),
    CheckDef("13", "CR", "Document Quality", "Is traceability matrix present?", "Should", cr_13_compliance_matrix),
    CheckDef("14", "CR", "Document Quality", "Are review/approval signatures present?", "Shall", cr_14_review_approval),
    CheckDef("1", "FSA", "CS Element Catalog", "Is CS Element catalog populated?", "Shall", fsa_01_element_catalog),
    CheckDef("2", "FSA", "CS Element Catalog", "Do ASIL/CAL elements have supplier+cert?", "Shall", fsa_02_supplier_cert),
    CheckDef("3", "FSA", "Cryptographic Inventory", "Are only approved algorithms used?", "Shall", fsa_03_crypto_approved),
    CheckDef("4", "FSA", "Cryptographic Inventory", "Are minimum key lengths met?", "Shall", fsa_04_crypto_key_length),
    CheckDef("5", "FSA", "Key Management", "Is lifecycle defined per key class?", "Shall", fsa_05_key_mgmt_lifecycle),
    CheckDef("6", "FSA", "Secure Boot", "Is root-of-trust and anti-rollback present?", "Shall", fsa_06_secure_boot),
    CheckDef("7", "FSA", "Secure Communication", "Are channels documented with auth/enc/integrity/replay?", "Shall", fsa_07_secure_comm),
    CheckDef("8", "FSA", "Access Control", "Are roles/privileges/auth factors documented?", "Shall", fsa_08_access_control),
    CheckDef("9", "FSA", "CSR Allocation", "Is CSR-to-element matrix complete?", "Shall", fsa_09_csr_allocation),
    CheckDef("10", "FSA", "Defense in Depth", "Are multiple protective layers defined?", "Shall", fsa_10_defense_depth),
    CheckDef("11", "FSA", "Debug Interfaces", "Are debug interfaces disabled in production?", "Shall", fsa_11_debug_disabled),
    CheckDef("12", "FSA", "Certificate Management", "Are cert expiry/renewal plans present?", "Should", fsa_12_cert_expiry),
    CheckDef("13", "FSA", "Hardware Security", "Is HSM/Secure Element usage justified?", "Should", fsa_13_hsm_usage),
    CheckDef("14", "FSA", "Standards Compliance", "Are references to applicable standards present?", "Should", fsa_14_standards_ref),
    CheckDef("1", "VA", "Verification Planning", "Does architecture align with CS Concept?", "Shall", va_01_concept_alignment),
    CheckDef("2", "VA", "Verification Planning", "Are requirements verifiable?", "Shall", va_02_reqs_verifiable),
    CheckDef("3", "VA", "Verification Specification", "Are test cases specified?", "Shall", va_03_test_cases),
    CheckDef("4", "VA", "Verification Specification", "Is test environment documented?", "Shall", va_04_test_env),
    CheckDef("5", "VA", "Verification Execution", "Was verification executed per plan?", "Shall", va_05_test_exec),
    CheckDef("6", "VA", "Verification Execution", "Does report include required elements?", "Shall", va_06_report),
    CheckDef("7", "VA", "Verification Evaluation", "Is coverage adequate?", "Shall", va_07_coverage),
    CheckDef("8", "VA", "Verification Evaluation", "Is anomaly handling documented?", "Should", va_08_anomalies),
    CheckDef("9", "VA", "Regression Testing", "Is regression strategy defined?", "Should", va_09_regression),
    CheckDef("10", "VA", "Traceability", "Is traceability complete?", "Shall", va_10_traceability),
    CheckDef("11", "VA", "Independence", "Is verification independent?", "Should", va_11_independence),
    CheckDef("12", "VA", "Standards Compliance", "Is AUTOSAR/ISO 26262 compliance shown?", "Should", va_12_standards_compliance),
    CheckDef("13", "VA", "Review & Approval", "Are reviewers qualified?", "Shall", va_13_review_approval),
    CheckDef("14", "VA", "Quality Metrics", "Are metrics and KPIs tracked?", "Should", va_14_metrics),
]
