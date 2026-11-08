"""UDS service confirmation and technical checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from uds_probe import ProbedUDS


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding, page_section="", action="(Reviewer to verify and assess)"):
    return CheckResult(rating="", finding="(Auto-suggest, requires reviewer judgment) " + finding,
                      page_section=page_section, recommended_action=action, confidence="Low")


def na(reason):
    return CheckResult(rating="NA", finding=reason, confidence="High")


# =========================================================================
# Confirmation Review Checks (14 generic)
# =========================================================================

def cr_01_structured(p):
    if len(p.sheet_names) >= 10:
        return CheckResult(rating="FC", finding=f"Document is structured into {len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Ensure 13-tab structure.", confidence="Medium")


def cr_02_title(p):
    if p.title:
        return CheckResult(rating="FC", finding=f"Title: '{p.title}'.", confidence="High")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add ECU/system title.", confidence="High")


def cr_03_doc_id(p):
    if p.doc_id:
        return CheckResult(rating="FC", finding=f"Document ID: {p.doc_id}.", confidence="High")
    return CheckResult(rating="NO", finding="Document ID missing.", recommended_action="Populate doc_id field.", confidence="High")


def cr_04_revision(p):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision: {p.revision}.", confidence="High")
    return CheckResult(rating="NO", finding="Revision not set.", recommended_action="Set revision.", confidence="High")


def cr_05_author_approver(p):
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    missing = ([] if p.author else ["Author"]) + ([] if p.approver else ["Approver"])
    return CheckResult(rating="NO", finding=f"Missing: {', '.join(missing)}.", recommended_action=f"Populate {', '.join(missing)}.", confidence="High")


def cr_06_revision_history(p):
    if p.revision_history_rows >= 1:
        return CheckResult(rating="FC", finding=f"Revision history: {p.revision_history_rows} entries.", confidence="High")
    return CheckResult(rating="NO", finding="No revision history.", recommended_action="Add revision history.", confidence="High")


def cr_07_ecu_identity(p):
    if p.has_ecu_identity:
        return CheckResult(rating="FC", finding="ECU Diagnostic Identity tab present.", confidence="High")
    return CheckResult(rating="NO", finding="No ECU identity section.", recommended_action="Add ECU Diagnostic Identity tab.", confidence="High")


def cr_08_searchable(p):
    if len(p.sheet_names) >= 5:
        return CheckResult(rating="FC", finding="Document structure supports search.", confidence="Medium")
    return CheckResult(rating="PC", finding="Limited structure.", recommended_action="Expand document structure.", confidence="Medium")


def cr_09_references(p):
    return draft("References should cite ISO 14229-1:2020 standard.", action="Confirm ISO 14229-1 standards cited.")


def cr_10_config_mgmt(p):
    return draft("Configuration management status should be confirmed.", action="Verify CM integration.")


def cr_11_header_footer(p):
    return draft("Header/footer verification requires manual review in Excel.", action="Open workbook and verify headers/footers.")


def cr_12_sections_complete(p):
    if p.service_count > 0 and p.did_count > 0 and p.session_count > 0:
        return CheckResult(rating="FC", finding=f"Core sections complete: {p.service_count} services, {p.did_count} DIDs, {p.session_count} sessions.", confidence="High")
    return CheckResult(rating="PC", finding=f"Partial completion.", recommended_action="Complete all required sections.", confidence="High")


def cr_13_consistency(p):
    if p.service_count > 0 and p.nrc_count > 0:
        return CheckResult(rating="FC", finding=f"{p.service_count} services; {p.nrc_count} NRCs defined.", confidence="High")
    return CheckResult(rating="PC", finding="Incomplete service/NRC pairing.", recommended_action="Link services to negative response codes.", confidence="High")


def cr_14_approval_status(p):
    if p.status:
        return CheckResult(rating="FC", finding=f"Status: {p.status}.", confidence="High")
    return CheckResult(rating="NO", finding="Status field empty.", recommended_action="Set approval status.", confidence="High")


# =========================================================================
# Technical Assessment Checks (16 UDS-specific)
# =========================================================================

def tsa_01_ecu_identity(p):
    if p.logical_address and p.physical_address:
        return CheckResult(rating="FC", finding=f"Logical addr: {p.logical_address}; Physical addr: {p.physical_address}.", confidence="High")
    missing = ([] if p.logical_address else ["Logical"]) + ([] if p.physical_address else ["Physical"])
    return CheckResult(rating="PC", finding=f"Missing addressing: {', '.join(missing)}.", recommended_action="Populate all addressing fields.", confidence="High")


def tsa_02_service_inventory(p):
    if p.service_count >= 5:
        return CheckResult(rating="FC", finding=f"{p.service_count} services defined.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.service_count} services.", recommended_action="Define core UDS services (0x10, 0x22, 0x27, etc.).", confidence="High")


def tsa_03_session_definitions(p):
    if p.session_count >= 2:
        return CheckResult(rating="FC", finding=f"{p.session_count} session types defined: {', '.join(sorted(p.session_types))}.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.session_count} session.", recommended_action="Define default and extended session types.", confidence="High")


def tsa_04_did_coverage(p):
    if p.did_count >= 1:
        return CheckResult(rating="FC", finding=f"{p.did_count} DIDs in catalog.", confidence="High")
    return CheckResult(rating="PC", finding="No DIDs.", recommended_action="Populate DID Catalog.", confidence="High")


def tsa_05_did_uniqueness(p):
    if p.did_duplicates == 0:
        return CheckResult(rating="FC", finding=f"All {p.did_count} DIDs are unique.", confidence="High")
    return CheckResult(rating="NO", finding=f"{p.did_duplicates} duplicate DIDs detected.", recommended_action="Remove or rename duplicate DIDs.", confidence="High")


def tsa_06_rid_coverage(p):
    if p.rid_count >= 1:
        return CheckResult(rating="FC", finding=f"{p.rid_count} RIDs in catalog.", confidence="High")
    return CheckResult(rating="PC", finding="No RIDs.", recommended_action="Populate RID Catalog if routines supported.", confidence="Medium")


def tsa_07_rid_uniqueness(p):
    if p.rid_duplicates == 0:
        return CheckResult(rating="FC", finding=f"All {p.rid_count} RIDs are unique.", confidence="High")
    return CheckResult(rating="NO", finding=f"{p.rid_duplicates} duplicate RIDs detected.", recommended_action="Remove or rename duplicate RIDs.", confidence="High")


def tsa_08_security_levels(p):
    if p.security_levels >= 1:
        return CheckResult(rating="FC", finding=f"{p.security_levels} security access levels defined.", confidence="High")
    return CheckResult(rating="PC", finding="No security levels.", recommended_action="Define security levels for protected services.", confidence="Medium")


def tsa_09_security_pairing(p):
    if p.security_levels >= 1 and p.service_count >= 5:
        return CheckResult(rating="FC", finding="Security levels defined for protected services.", confidence="Medium")
    return CheckResult(rating="PC", finding="Incomplete security configuration.", recommended_action="Associate security levels with services.", confidence="Medium")


def tsa_10_nrc_completeness(p):
    if p.nrc_count >= 5:
        return CheckResult(rating="FC", finding=f"{p.nrc_count} negative response codes defined.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.nrc_count} NRCs.", recommended_action="Populate NRC catalog.", confidence="High")


def tsa_11_p2_timing(p):
    if p.p2_ms:
        try:
            p2_val = int(p.p2_ms.split("-")[0]) if "-" in p.p2_ms else int(p.p2_ms)
            if 50 <= p2_val <= 5000:
                return CheckResult(rating="FC", finding=f"P2 timeout: {p.p2_ms} ms (valid range 50-5000).", confidence="High")
            return CheckResult(rating="NO", finding=f"P2={p.p2_ms} ms out of range.", recommended_action="Set P2 to 50-5000 ms.", confidence="High")
        except ValueError:
            return CheckResult(rating="PC", finding=f"P2 format unclear: {p.p2_ms}.", recommended_action="Use numeric range (e.g., 50-100).", confidence="Medium")
    return CheckResult(rating="NO", finding="P2 timeout not defined.", recommended_action="Specify P2 timing.", confidence="High")


def tsa_12_p2_star_timing(p):
    if p.p2_star_ms:
        return CheckResult(rating="FC", finding=f"P2* (extended): {p.p2_star_ms} ms.", confidence="High")
    return CheckResult(rating="PC", finding="P2* timeout not specified.", recommended_action="Define extended P2* timeout.", confidence="Medium")


def tsa_13_s3_timing(p):
    if p.s3_ms:
        return CheckResult(rating="FC", finding=f"S3 (session timeout): {p.s3_ms} ms.", confidence="High")
    return CheckResult(rating="PC", finding="S3 timeout not specified.", recommended_action="Define session timeout (S3).", confidence="Medium")


def tsa_14_memory_layout(p):
    return draft("Memory programming layout should define flash address ranges and erase block sizes.", action="Populate Memory Programming Layout tab.")


def tsa_15_validation_rules(p):
    return draft("Input validation rules should constrain DIDs, RIDs, and timing parameters.", action="Review Validation Rules tab for completeness.")


def tsa_16_overall_readiness(p):
    all_present = (p.service_count > 0 and p.did_count > 0 and p.session_count >= 1 and
                   p.security_levels > 0 and p.nrc_count > 0)
    if all_present:
        return CheckResult(rating="FC", finding="All core UDS elements present.", confidence="High")
    return CheckResult(rating="PC", finding="Some core elements missing.", recommended_action="Complete missing sections.", confidence="High")


# =========================================================================
# Check Definitions
# =========================================================================

@dataclass
class CheckDef:
    code: str
    category: str
    title: str
    obligation: str
    checker: Callable[[ProbedUDS], CheckResult]


CHECKS: list[CheckDef] = [
    CheckDef("CR-01", "Confirmation", "Document Structure", "Should", cr_01_structured),
    CheckDef("CR-02", "Confirmation", "ECU Title", "Shall", cr_02_title),
    CheckDef("CR-03", "Confirmation", "Document ID", "Shall", cr_03_doc_id),
    CheckDef("CR-04", "Confirmation", "Revision Control", "Shall", cr_04_revision),
    CheckDef("CR-05", "Confirmation", "Author and Approver", "Shall", cr_05_author_approver),
    CheckDef("CR-06", "Confirmation", "Revision History", "Should", cr_06_revision_history),
    CheckDef("CR-07", "Confirmation", "ECU Identity", "Shall", cr_07_ecu_identity),
    CheckDef("CR-08", "Confirmation", "Searchability", "Should", cr_08_searchable),
    CheckDef("CR-09", "Confirmation", "Standards References", "Should", cr_09_references),
    CheckDef("CR-10", "Confirmation", "Configuration Management", "Should", cr_10_config_mgmt),
    CheckDef("CR-11", "Confirmation", "Header/Footer Info", "Should", cr_11_header_footer),
    CheckDef("CR-12", "Confirmation", "Sections Populated", "Shall", cr_12_sections_complete),
    CheckDef("CR-13", "Confirmation", "Internal Consistency", "Shall", cr_13_consistency),
    CheckDef("CR-14", "Confirmation", "Approval Status", "Shall", cr_14_approval_status),

    CheckDef("TA-01", "Technical", "ECU Diagnostic Identity", "Shall", tsa_01_ecu_identity),
    CheckDef("TA-02", "Technical", "Service Inventory", "Shall", tsa_02_service_inventory),
    CheckDef("TA-03", "Technical", "Session Definitions", "Shall", tsa_03_session_definitions),
    CheckDef("TA-04", "Technical", "DID Catalog", "Shall", tsa_04_did_coverage),
    CheckDef("TA-05", "Technical", "DID Uniqueness", "Shall", tsa_05_did_uniqueness),
    CheckDef("TA-06", "Technical", "RID Catalog", "Should", tsa_06_rid_coverage),
    CheckDef("TA-07", "Technical", "RID Uniqueness", "Shall", tsa_07_rid_uniqueness),
    CheckDef("TA-08", "Technical", "Security Access Levels", "Should", tsa_08_security_levels),
    CheckDef("TA-09", "Technical", "Security Service Pairing", "Should", tsa_09_security_pairing),
    CheckDef("TA-10", "Technical", "Negative Response Codes", "Should", tsa_10_nrc_completeness),
    CheckDef("TA-11", "Technical", "P2 Timing", "Shall", tsa_11_p2_timing),
    CheckDef("TA-12", "Technical", "P2* Extended Timing", "Should", tsa_12_p2_star_timing),
    CheckDef("TA-13", "Technical", "S3 Session Timeout", "Should", tsa_13_s3_timing),
    CheckDef("TA-14", "Technical", "Memory Programming Layout", "Should", tsa_14_memory_layout),
    CheckDef("TA-15", "Technical", "Validation Rules", "Should", tsa_15_validation_rules),
    CheckDef("TA-16", "Technical", "Overall Readiness", "Shall", tsa_16_overall_readiness),
]
