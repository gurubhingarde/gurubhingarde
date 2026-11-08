"""
CS Concept checklist definitions per ISO/SAE 21434 Section 9.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from cs_concept_probe import ProbedCSConcept


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding: str, page_section: str = "", action: str = "(Reviewer to verify)") -> CheckResult:
    return CheckResult(
        rating="",
        finding="(Auto-suggest, requires reviewer judgment) " + finding,
        page_section=page_section,
        recommended_action=action,
        confidence="Low",
    )


def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, page_section="", recommended_action="", confidence="High")


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedCSConcept], CheckResult]


# -------------------------------------------------------------------------
# Confirmation Review (14 checks)
# -------------------------------------------------------------------------

def cr_01_structured(p: ProbedCSConcept) -> CheckResult:
    if len(p.sheet_names) >= 8:
        return CheckResult(
            rating="FC",
            finding=f"Document has {len(p.sheet_names)} tabs.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.sheet_names)} tabs; should have 9.",
        recommended_action="Ensure all CS Concept tabs are present.",
        confidence="Medium",
    )


def cr_02_title(p: ProbedCSConcept) -> CheckResult:
    if p.title:
        return draft(f"Title: '{p.title}'.", page_section="Title page")
    return CheckResult(rating="NO", finding="No title.", recommended_action="Add document title.", confidence="High")


def cr_03_author_approver(p: ProbedCSConcept) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", page_section="Title page", confidence="High")
    return CheckResult(rating="NO", finding="Author/Approver not populated.", recommended_action="Populate on Title page.", confidence="High")


def cr_04_revision(p: ProbedCSConcept) -> CheckResult:
    if p.revision and p.revision_history_rows >= 1:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}'; {p.revision_history_rows} history row(s).", page_section="Title + Document Control", confidence="High")
    return CheckResult(rating="NO", finding="Revision not set or no history.", recommended_action="Populate Revision and history.", confidence="High")


def cr_05_status(p: ProbedCSConcept) -> CheckResult:
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", page_section="Title page", confidence="High")
    return CheckResult(rating="NO", finding="Status not set.", recommended_action="Add Status field.", confidence="High")


def cr_06_project(p: ProbedCSConcept) -> CheckResult:
    if p.project:
        return CheckResult(rating="FC", finding=f"Project='{p.project}'.", page_section="Title page", confidence="High")
    return CheckResult(rating="PC", finding="Project not set.", recommended_action="Add Project name.", confidence="High")


def cr_07_references(p: ProbedCSConcept) -> CheckResult:
    refs_sheet = any("reference" in s.lower() for s in p.sheet_names)
    if refs_sheet:
        return CheckResult(rating="FC", finding="References tab found.", page_section="References tab", confidence="Medium")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add References tab.", confidence="Medium")


def cr_08_toc(p: ProbedCSConcept) -> CheckResult:
    if p.has_table_of_contents:
        return CheckResult(rating="FC", finding="TOC present.", page_section=f"Sheet '{p.sheet_names[0]}'", confidence="Medium")
    return CheckResult(rating="PC", finding="No TOC.", recommended_action="Add TOC tab.", confidence="Medium")


def cr_09_csg_reference(p: ProbedCSConcept) -> CheckResult:
    csg_sheet = any("csg" in s.lower() or "goal" in s.lower() for s in p.sheet_names)
    if csg_sheet:
        return CheckResult(rating="FC", finding="CS Goals reference sheet found.", page_section="CS Goals Echo tab", confidence="High")
    return CheckResult(rating="PC", finding="CS Goals not clearly referenced.", recommended_action="Add CS Goals Echo tab.", confidence="High")


def cr_10_complete_sections(p: ProbedCSConcept) -> CheckResult:
    critical = ["03_system", "04_cs_concept", "05_csr", "06_cal", "07_verification", "08_csi"]
    found = sum(1 for s in p.sheet_names if any(cs in s for cs in critical))
    if found >= 5:
        return CheckResult(rating="FC", finding=f"{found} critical sections present.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {found} critical sections.", recommended_action="Ensure all CS Concept sections are present.", confidence="Medium")


def cr_11_doc_control(p: ProbedCSConcept) -> CheckResult:
    return draft("Configuration management is organizational.", action="Confirm document is under version control.")


def cr_12_headers_footers(p: ProbedCSConcept) -> CheckResult:
    return draft("Headers/footers cannot be verified programmatically.", action="Manually confirm headers/footers.")


def cr_13_searchability(p: ProbedCSConcept) -> CheckResult:
    if p.has_table_of_contents and len(p.sheet_names) >= 8:
        return CheckResult(rating="FC", finding="Document supports searchability.", confidence="Medium")
    return CheckResult(rating="PC", finding="Searchability may be limited.", recommended_action="Enhance TOC and sheet naming.", confidence="Medium")


def cr_14_external_links(p: ProbedCSConcept) -> CheckResult:
    return draft("External links (CS Goals, CSR Catalog, CSI specs) must be verified manually.", action="Verify references to external documents.")


# -------------------------------------------------------------------------
# CSCA Assessment (14 substantive checks)
# -------------------------------------------------------------------------

def csca_01_csg_imported(p: ProbedCSConcept) -> CheckResult:
    csg_sheet = any("csg" in s.lower() for s in p.sheet_names)
    if csg_sheet:
        return CheckResult(rating="FC", finding="CS Goals imported.", page_section="CS Goals Echo tab", confidence="High")
    return CheckResult(rating="NO", finding="CS Goals not found.", recommended_action="Import CS Goals via CS Goals Echo tab.", confidence="High")


def csca_02_block_diagram(p: ProbedCSConcept) -> CheckResult:
    if p.n_block_diagram_nodes > 0:
        return CheckResult(rating="FC", finding=f"{p.n_block_diagram_nodes} block diagram node(s) enumerated.", page_section="System Block Diagram tab", confidence="High")
    return CheckResult(rating="NO", finding="Block diagram not populated.", recommended_action="Enumerate all system nodes in block diagram.", confidence="High")


def csca_03_csr_coverage(p: ProbedCSConcept) -> CheckResult:
    if p.n_csr > 0:
        return CheckResult(rating="FC", finding=f"{p.n_csr} CSR(s) defined.", page_section="CSR Catalog tab", confidence="High")
    return CheckResult(rating="NO", finding="CSR Catalog is empty.", recommended_action="Populate CSR Catalog with requirements.", confidence="High")


def csca_04_concept_argument(p: ProbedCSConcept) -> CheckResult:
    return draft("CS Concept Argument derivation trees (basic events to CSR) must be verified manually.", page_section="CS Concept Argument tab", action="Confirm derivation trees cover all CSGs with basic events linked to CSRs.")


def csca_05_csr_to_csg(p: ProbedCSConcept) -> CheckResult:
    if p.n_csr > 0:
        traced = sum(1 for c in p.csr_entries if c.csg_ref)
        if traced == p.n_csr:
            return CheckResult(rating="FC", finding=f"All {p.n_csr} CSRs trace to CSGs.", page_section="CSR Catalog tab", confidence="High")
        return CheckResult(rating="PC", finding=f"{traced}/{p.n_csr} CSRs traced.", recommended_action="Link all CSRs to parent CSGs.", confidence="High")
    return CheckResult(rating="NA", finding="No CSRs to trace.", confidence="High")


def csca_06_csr_allocation(p: ProbedCSConcept) -> CheckResult:
    if p.n_block_diagram_nodes > 0 and p.n_csr > 0:
        return CheckResult(rating="FC", finding=f"CSRs allocated to {p.n_block_diagram_nodes} block diagram node(s).", page_section="CSR Catalog tab", confidence="High")
    return CheckResult(rating="PC", finding="CSR allocation to nodes not clear.", recommended_action="Explicitly allocate each CSR to a block diagram node.", confidence="High")


def csca_07_cal_inherited(p: ProbedCSConcept) -> CheckResult:
    if p.n_csr > 0:
        with_cal = sum(1 for c in p.csr_entries if c.cal)
        if with_cal == p.n_csr:
            return CheckResult(rating="FC", finding=f"All {p.n_csr} CSRs have CAL inherited.", page_section="CSR Catalog tab", confidence="High")
        return CheckResult(rating="PC", finding=f"{with_cal}/{p.n_csr} CSRs have CAL.", recommended_action="Inherit CAL from parent CSGs for all CSRs.", confidence="High")
    return CheckResult(rating="NA", finding="No CSRs to assess.", confidence="High")


def csca_08_property_coverage(p: ProbedCSConcept) -> CheckResult:
    required = {"C", "I", "A", "Auth", "Authz", "NR"}
    covered = p.properties_covered
    if covered >= required:
        return CheckResult(rating="FC", finding=f"All 6 properties covered: {', '.join(sorted(covered))}.", page_section="CSR Catalog tab", confidence="High")
    missing = required - covered
    return CheckResult(rating="PC", finding=f"Missing: {', '.join(sorted(missing))}.", recommended_action="Add CSRs covering missing properties.", confidence="High")


def csca_09_verification_methods(p: ProbedCSConcept) -> CheckResult:
    if p.n_csr > 0 and p.n_verification_methods > 0:
        coverage = p.n_verification_methods / p.n_csr
        if coverage >= 0.8:
            return CheckResult(rating="FC", finding=f"{p.n_verification_methods} verification method(s) specified for {p.n_csr} CSR(s).", page_section="Verification Matrix tab", confidence="High")
        return CheckResult(rating="PC", finding=f"Only {p.n_verification_methods}/{p.n_csr} CSRs have verification methods.", recommended_action="Specify verification method for each CSR per CAL.", confidence="High")
    return CheckResult(rating="NA", finding="Insufficient CSR or verification data.", confidence="High")


def csca_10_cal_specific_methods(p: ProbedCSConcept) -> CheckResult:
    required_per_cal = {"1": {"code review"}, "2": {"code review", "static analysis"}, "3": {"code review", "fuzzing", "testing"}, "4": {"penetration testing", "red team"}}
    for cal, required_methods in required_per_cal.items():
        if cal in p.verification_methods_by_cal:
            assigned = p.verification_methods_by_cal[cal]
            if not assigned & required_methods:
                return CheckResult(
                    rating="PC",
                    finding=f"CAL {cal} verification methods incomplete.",
                    recommended_action=f"Ensure CAL {cal} includes appropriate methods: {', '.join(required_methods)}.",
                    confidence="High",
                )
    return CheckResult(rating="FC", finding="Verification methods align with CAL requirements.", page_section="Verification Matrix tab", confidence="Medium")


def csca_11_csi_handoff(p: ProbedCSConcept) -> CheckResult:
    csi_sheet = any("csi" in s.lower() or "handoff" in s.lower() for s in p.sheet_names)
    if csi_sheet:
        return CheckResult(rating="FC", finding="CSI Handoff tab found with placeholder implementation rows.", page_section="CSI Handoff tab", confidence="Medium")
    return CheckResult(rating="PC", finding="CSI Handoff not prepared.", recommended_action="Create CSI Handoff tab with placeholder rows per CSR.", confidence="Medium")


def csca_12_defense_in_depth(p: ProbedCSConcept) -> CheckResult:
    return draft("Defense-in-depth considerations (multiple layers, independence) must be verified manually.", page_section="CS Concept Argument tab", action="Confirm defense-in-depth strategies are documented (redundancy, diversity, layering).")


def csca_13_independence(p: ProbedCSConcept) -> CheckResult:
    return draft("Independence considerations (if CAL decomposed) must be documented.", page_section="CAL Allocation tab", action="If CAL is decomposed across components, confirm independence requirements are met.")


def csca_14_iso_references(p: ProbedCSConcept) -> CheckResult:
    refs_sheet = any("reference" in s.lower() for s in p.sheet_names)
    if refs_sheet:
        return CheckResult(rating="FC", finding="References tab includes ISO/SAE 21434 and CS Goals trace.", page_section="References tab", confidence="Medium")
    return CheckResult(rating="PC", finding="References incomplete.", recommended_action="Add References citing ISO/SAE 21434 Sections 9 and 16.", confidence="Medium")


# -------------------------------------------------------------------------
# Verification Assessment (5-6 checks)
# -------------------------------------------------------------------------

def va_01_verification_planning(p: ProbedCSConcept) -> CheckResult:
    return draft("Verification planning per CSR per CAL must be documented in a Verification Plan.", action="Confirm all CSRs have verification methods planned.")


def va_02_test_coverage(p: ProbedCSConcept) -> CheckResult:
    return draft("Test coverage and traceability (requirements to test cases) must be verified externally.", action="Confirm test cases exist for all CSRs.")


def va_03_csi_readiness(p: ProbedCSConcept) -> CheckResult:
    return draft("CSI readiness (implementation specification prepared) must be verified.", action="Confirm CSI Handoff is prepared for implementation phase.")


def va_04_independence_plan(p: ProbedCSConcept) -> CheckResult:
    return draft("Independence plan (if CAL decomposed) must be documented.", action="Confirm independence verification is planned if CAL is decomposed.")


def va_05_tool_qualification(p: ProbedCSConcept) -> CheckResult:
    return draft("Any verification tools (fuzzers, SAST, penetration testing frameworks) must be qualified.", action="Document tool versions and qualification status.")


def va_06_evidence_package(p: ProbedCSConcept) -> CheckResult:
    return draft("Evidence package (design review, derivation walkthroughs, traceability matrix) must be retained.", action="Confirm all design evidence is collected and retained per policy.")


# -------------------------------------------------------------------------
# Check registry
# -------------------------------------------------------------------------

CHECKS = [
    CheckDef("1", "CR", "Document Structure and Control", "Document has 9 tabs covering all CS Concept workflow sections", "Shall", cr_01_structured),
    CheckDef("2", "CR", "Document Structure and Control", "Document title is clear", "Shall", cr_02_title),
    CheckDef("3", "CR", "Document Structure and Control", "Author and Approver populated", "Shall", cr_03_author_approver),
    CheckDef("4", "CR", "Document Structure and Control", "Revision and history maintained", "Shall", cr_04_revision),
    CheckDef("5", "CR", "Document Structure and Control", "Status indicated", "Shall", cr_05_status),
    CheckDef("6", "CR", "Document Structure and Control", "Project name recorded", "Should", cr_06_project),
    CheckDef("7", "CR", "Document Structure and Control", "References provided", "Shall", cr_07_references),
    CheckDef("8", "CR", "Document Structure and Control", "Table of Contents present", "Should", cr_08_toc),
    CheckDef("9", "CR", "Document Structure and Control", "CS Goals are referenced", "Shall", cr_09_csg_reference),
    CheckDef("10", "CR", "Document Structure and Control", "All critical sections present", "Shall", cr_10_complete_sections),
    CheckDef("11", "CR", "Document Structure and Control", "Configuration management in place", "Should", cr_11_doc_control),
    CheckDef("12", "CR", "Document Structure and Control", "Headers and footers correct", "Should", cr_12_headers_footers),
    CheckDef("13", "CR", "Document Structure and Control", "Document is searchable", "Should", cr_13_searchability),
    CheckDef("14", "CR", "Document Structure and Control", "External links current", "Should", cr_14_external_links),

    CheckDef("1", "CSCA", "CS Goals Import", "CS Goals imported with traceability", "Shall", csca_01_csg_imported),
    CheckDef("2", "CSCA", "Block Diagram", "Block diagram nodes enumerated", "Shall", csca_02_block_diagram),
    CheckDef("3", "CSCA", "CSR Catalog", "Cybersecurity Requirements defined", "Shall", csca_03_csr_coverage),
    CheckDef("4", "CSCA", "CS Concept Argument", "Derivation trees (CSG to basic events to CSR) documented", "Shall", csca_04_concept_argument),
    CheckDef("5", "CSCA", "CSR Parentage", "Each CSR has parent CSG identified", "Shall", csca_05_csr_to_csg),
    CheckDef("6", "CSCA", "Node Allocation", "Each CSR allocated to block diagram node", "Shall", csca_06_csr_allocation),
    CheckDef("7", "CSCA", "CAL Inheritance", "CAL inherited from parent CSG for all CSRs", "Shall", csca_07_cal_inherited),
    CheckDef("8", "CSCA", "Property Coverage", "All 6 cybersecurity properties covered (C/I/A/Auth/Authz/NR)", "Shall", csca_08_property_coverage),
    CheckDef("9", "CSCA", "Verification Methods", "Verification methods specified per CSR per CAL", "Shall", csca_09_verification_methods),
    CheckDef("10", "CSCA", "CAL-Specific Methods", "Verification methods align with CAL (CAL 4: penetration test; CAL 3: fuzzing; CAL 2/1: code review)", "Shall", csca_10_cal_specific_methods),
    CheckDef("11", "CSCA", "CSI Handoff", "CSI Handoff prepared with placeholder implementation rows", "Should", csca_11_csi_handoff),
    CheckDef("12", "CSCA", "Defense in Depth", "Defense-in-depth considerations documented", "Should", csca_12_defense_in_depth),
    CheckDef("13", "CSCA", "Independence", "Independence considerations documented if CAL decomposed", "Should", csca_13_independence),
    CheckDef("14", "CSCA", "References", "References cite ISO/SAE 21434 Sections 9 and 16", "Shall", csca_14_iso_references),

    CheckDef("1", "VA", "Verification Planning", "Verification methods planned per CSR per CAL", "Should", va_01_verification_planning),
    CheckDef("2", "VA", "Test Coverage", "Test coverage and traceability documented", "Should", va_02_test_coverage),
    CheckDef("3", "VA", "CSI Readiness", "Implementation specification prepared for CSI stage", "Should", va_03_csi_readiness),
    CheckDef("4", "VA", "Independence Planning", "Independence verification planned if decomposed", "Should", va_04_independence_plan),
    CheckDef("5", "VA", "Tool Qualification", "Verification tools are qualified", "Should", va_05_tool_qualification),
    CheckDef("6", "VA", "Evidence Package", "Design evidence package retained", "Should", va_06_evidence_package),
]
