"""CDD confirmation-measures checks."""

from __future__ import annotations

from dataclasses import dataclass

from cdd_probe import ProbedCDD


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding, page_section="", action="(Reviewer to verify and assess)"):
    return CheckResult(rating="", finding="(Auto-suggest) " + finding, page_section=page_section, recommended_action=action, confidence="Low")


def na(reason):
    return CheckResult(rating="NA", finding=reason, confidence="High")


# Confirmation Review (10 checks)

def cr_01_structured(p):
    if len(p.sheet_names) >= 8:
        return CheckResult(rating="FC", finding=f"Document has {len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Add structured sections.", confidence="Medium")


def cr_02_title(p):
    if p.title:
        return CheckResult(rating="FC", finding=f"Title: '{p.title}'.", confidence="High")
    return CheckResult(rating="NO", finding="No title.", recommended_action="Add title.", confidence="High")


def cr_03_doc_id(p):
    if p.doc_id:
        return CheckResult(rating="FC", finding=f"Doc ID: '{p.doc_id}'.", confidence="High")
    return CheckResult(rating="PC", finding="No doc ID.", recommended_action="Assign doc ID.", confidence="High")


def cr_04_revision(p):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision: '{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="No revision.", recommended_action="Populate revision.", confidence="High")


def cr_05_author_approver(p):
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author/Approver assigned.", confidence="High")
    missing = ([] if p.author else ["Author"]) + ([] if p.approver else ["Approver"])
    return CheckResult(rating="NO", finding=f"Missing: {', '.join(missing)}.", recommended_action=f"Assign {', '.join(missing)}.", confidence="High")


def cr_06_change_history(p):
    if p.revision_history_rows >= 1:
        return CheckResult(rating="FC", finding=f"Change history has {p.revision_history_rows} entries.", confidence="High")
    return CheckResult(rating="PC", finding="No change history.", recommended_action="Add revision history.", confidence="High")


def cr_07_document_control(p):
    if p.has_document_control:
        return CheckResult(rating="FC", finding="Document Control tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No Document Control tab.", recommended_action="Add Document Control tab.", confidence="Medium")


def cr_08_ecu_id(p):
    if len(p.sheet_names) > 2:
        return CheckResult(rating="FC", finding="ECU Identity tab present.", confidence="Medium")
    return CheckResult(rating="PC", finding="ECU Identity not identified.", recommended_action="Add ECU Identity tab.", confidence="Medium")


def cr_09_status_field(p):
    if p.status:
        return CheckResult(rating="FC", finding=f"Status: '{p.status}'.", confidence="High")
    return CheckResult(rating="PC", finding="Status not populated.", recommended_action="Add status field.", confidence="Medium")


def cr_10_references(p):
    if "References" in p.sheet_names:
        return CheckResult(rating="FC", finding="References tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add References tab.", confidence="Medium")


# CDD Assessment (12 checks)

def ca_01_sessions(p):
    if p.sessions >= 1:
        return CheckResult(rating="FC", finding=f"{p.sessions} session(s) defined.", confidence="High")
    return CheckResult(rating="NO", finding="No sessions defined.", recommended_action="Define at least default session.", confidence="High")


def ca_02_services(p):
    if p.services >= 5:
        return CheckResult(rating="FC", finding=f"{p.services} UDS services configured.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.services} services.", recommended_action="Verify service coverage per ISO 14229-1.", confidence="Medium")


def ca_03_diids(p):
    if p.diids >= 5:
        return CheckResult(rating="FC", finding=f"{p.diids} DIDs in catalog.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.diids} DIDs.", recommended_action="Verify DID coverage (0xF180-0xF18B mandatory).", confidence="Medium")


def ca_04_riids(p):
    if p.riids >= 1:
        return CheckResult(rating="FC", finding=f"{p.riids} RID(s) defined.", confidence="High")
    return CheckResult(rating="PC", finding="No RIDs defined.", recommended_action="Define routine identifiers if applicable.", confidence="Medium")


def ca_05_security_pairing(p):
    if p.security_levels >= 1:
        return CheckResult(rating="FC", finding=f"{p.security_levels} security level(s) configured.", confidence="High")
    return CheckResult(rating="PC", finding="No security levels.", recommended_action="Define security access levels.", confidence="Medium")


def ca_06_dtc_reference(p):
    if p.dtc_cross_ref:
        return CheckResult(rating="FC", finding=f"DTC catalog referenced: {p.dtc_cross_ref}.", confidence="High")
    return CheckResult(rating="PC", finding="No DTC cross-reference.", recommended_action="Link to source DTC catalog.", confidence="Medium")


def ca_07_service_consistency(p):
    return draft("Service enable flags require manual verification.", action="Confirm all services have enabled field populated.")


def ca_08_did_access(p):
    return draft("Read/write access not machine-verifiable.", action="Confirm DID access modes per specifications.")


def ca_09_rid_controls(p):
    return draft("RID control types require verification.", action="Confirm all RIDs have control type assigned.")


def ca_10_communication_config(p):
    if "Communication Configuration" in p.sheet_names:
        return CheckResult(rating="FC", finding="Communication Configuration tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No Communication Configuration.", recommended_action="Add communication parameters.", confidence="Medium")


def ca_11_variant_inheritance(p):
    if p.variants > 0:
        return draft(f"{p.variants} variant(s) defined. Verify inheritance rules.", action="Check variant inheritance consistency.")
    return CheckResult(rating="NA", finding="No variants defined.", confidence="High")


def ca_12_traceability(p):
    return draft("CDD to specification traceability not verifiable.", action="Confirm CDD content traces to requirements.")


# Variant Assessment (6 checks)

def va_01_variant_count(p):
    if p.variants >= 1:
        return CheckResult(rating="FC", finding=f"{p.variants} variant(s) defined.", confidence="High")
    return CheckResult(rating="NA", finding="No variants (single ECU variant).", confidence="High")


def va_02_parent_child(p):
    if p.variants > 1:
        return draft("Parent-child relationships require verification.", action="Confirm inheritance hierarchy is consistent.")
    return CheckResult(rating="NA", finding="Single variant only.", confidence="High")


def va_03_variant_differences(p):
    if p.variants > 0:
        return draft("Variant differences not machine-verifiable.", action="Confirm all variant differences documented.")
    return CheckResult(rating="NA", finding="No variants.", confidence="High")


def va_04_did_variant_mapping(p):
    return draft("DID-to-variant mapping not verifiable.", action="Confirm DIDs properly assigned to variants.")


def va_05_service_variant_coverage(p):
    return draft("Service-to-variant assignment requires review.", action="Verify services available in each variant.")


def va_06_consistency_rules(p):
    return draft("Variant consistency rules not enforced.", action="Check that variant coding follows inheritance rules.")


CHECKS = [
    ("CR-01", "Document Structure", cr_01_structured, "Shall"),
    ("CR-02", "Title Present", cr_02_title, "Shall"),
    ("CR-03", "Document ID", cr_03_doc_id, "Shall"),
    ("CR-04", "Revision", cr_04_revision, "Shall"),
    ("CR-05", "Author/Approver", cr_05_author_approver, "Shall"),
    ("CR-06", "Change History", cr_06_change_history, "Should"),
    ("CR-07", "Document Control", cr_07_document_control, "Should"),
    ("CR-08", "ECU ID", cr_08_ecu_id, "Should"),
    ("CR-09", "Status Field", cr_09_status_field, "Should"),
    ("CR-10", "References", cr_10_references, "Should"),
    ("CA-01", "Sessions", ca_01_sessions, "Shall"),
    ("CA-02", "Services", ca_02_services, "Shall"),
    ("CA-03", "DIDs", ca_03_diids, "Shall"),
    ("CA-04", "RIDs", ca_04_riids, "Should"),
    ("CA-05", "Security Levels", ca_05_security_pairing, "Shall"),
    ("CA-06", "DTC Reference", ca_06_dtc_reference, "Should"),
    ("CA-07", "Service Consistency", ca_07_service_consistency, "Should"),
    ("CA-08", "DID Access", ca_08_did_access, "Should"),
    ("CA-09", "RID Controls", ca_09_rid_controls, "Should"),
    ("CA-10", "Communication Config", ca_10_communication_config, "Should"),
    ("CA-11", "Variant Inheritance", ca_11_variant_inheritance, "Should"),
    ("CA-12", "Traceability", ca_12_traceability, "Should"),
    ("VA-01", "Variant Count", va_01_variant_count, "Should"),
    ("VA-02", "Parent-Child", va_02_parent_child, "Should"),
    ("VA-03", "Variant Differences", va_03_variant_differences, "Should"),
    ("VA-04", "DID-Variant Mapping", va_04_did_variant_mapping, "Should"),
    ("VA-05", "Service Coverage", va_05_service_variant_coverage, "Should"),
    ("VA-06", "Consistency Rules", va_06_consistency_rules, "Should"),
]


class CheckDef:
    """Compatibility wrapper."""
    def __init__(self, check_id, name, func, obligation):
        self.check_id = check_id
        self.name = name
        self.func = func
        self.obligation = obligation
