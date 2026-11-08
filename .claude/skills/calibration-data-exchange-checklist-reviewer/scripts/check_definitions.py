"""Calibration Data Exchange Confirmation Review checks."""

from __future__ import annotations

from dataclasses import dataclass
from caldex_probe import ProbedCALDEX


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str


def draft(finding, page_section="", action="(Reviewer to verify)"):
    return CheckResult(rating="", finding="(Auto-suggest) " + finding, page_section=page_section, recommended_action=action, confidence="Low")


def na(reason):
    return CheckResult(rating="NA", finding=reason, confidence="High")


# Agreement Structure (11)
def agr_01_title(p: ProbedCALDEX):
    if p.title:
        return draft(f"Title: '{p.title}'. Reviewer to confirm scope.", page_section="Title")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add clear agreement title.", confidence="High")


def agr_02_author(p: ProbedCALDEX):
    if p.author:
        return CheckResult(rating="FC", finding=f"Author: {p.author}.", confidence="High")
    return CheckResult(rating="PC", finding="Author not recorded.", recommended_action="Document author/initiator.", confidence="High")


def agr_03_revision(p: ProbedCALDEX):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision: {p.revision}.", confidence="High")
    return CheckResult(rating="NO", finding="No revision.", recommended_action="Add agreement version number.", confidence="High")


def agr_04_parties(p: ProbedCALDEX):
    if p.parties_count >= 2:
        return CheckResult(rating="FC", finding=f"Parties identified ({p.parties_count}).", confidence="High")
    return CheckResult(rating="NO", finding="Parties not identified.", recommended_action="Document OEM, Tier-1, Tier-2.", confidence="High")


def agr_05_ownership_matrix(p: ProbedCALDEX):
    if p.ownership_count > 0:
        return CheckResult(rating="FC", finding=f"Ownership matrix populated ({p.ownership_count} parameters).", confidence="High")
    return CheckResult(rating="NO", finding="Ownership matrix empty.", recommended_action="Define parameter ownership per characteristic.", confidence="High")


def agr_06_baseline_refs(p: ProbedCALDEX):
    if p.baseline_count > 0:
        return CheckResult(rating="FC", finding=f"Baseline References documented ({p.baseline_count} items).", confidence="High")
    return CheckResult(rating="PC", finding="Baseline References incomplete.", recommended_action="Document approved baseline snapshots.", confidence="High")


def agr_07_document_control(p: ProbedCALDEX):
    if p.has_document_control:
        return CheckResult(rating="FC", finding="Document Control tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No Document Control tab.", recommended_action="Add change log and version history.", confidence="High")


def agr_08_change_protocol(p: ProbedCALDEX):
    if p.has_change_protocol:
        return CheckResult(rating="FC", finding="Change Protocol defined.", confidence="High")
    return CheckResult(rating="NO", finding="No Change Protocol tab.", recommended_action="Document change approval process.", confidence="High")


def agr_09_roles_defined(p: ProbedCALDEX):
    return draft("Reviewer to verify roles and responsibilities are clearly defined for OEM and Tier-1.", action="Audit ownership matrix change rights columns.")


def agr_10_scope_clear(p: ProbedCALDEX):
    return draft("Reviewer to confirm agreement scope is clear (parameters covered, exclusions noted).", action="Verify against project scope statement.")


def agr_11_functional_safety(p: ProbedCALDEX):
    return draft("Reviewer to verify functional safety compliance (ISO 26262) requirements documented if applicable.", action="Check for safety-critical parameter flag or cross-reference.")


# Exchange & Acceptance (9)
def exch_01_formats(p: ProbedCALDEX):
    if p.format_count > 0:
        return CheckResult(rating="FC", finding=f"Exchange Formats specified ({p.format_count} formats).", confidence="High")
    return CheckResult(rating="NO", finding="Exchange formats not specified.", recommended_action="Define DCM, CDFX, PaCo usage.", confidence="High")


def exch_02_version_control(p: ProbedCALDEX):
    if p.has_version_control:
        return CheckResult(rating="FC", finding="Version Control scheme defined.", confidence="High")
    return CheckResult(rating="PC", finding="No Version Control tab.", recommended_action="Add versioning and baseline tagging rules.", confidence="High")


def exch_03_acceptance_criteria(p: ProbedCALDEX):
    if p.criteria_count > 0:
        return CheckResult(rating="FC", finding=f"Acceptance Criteria documented ({p.criteria_count} criteria).", confidence="High")
    return CheckResult(rating="PC", finding="Acceptance Criteria incomplete.", recommended_action="Define measurable acceptance conditions.", confidence="High")


def exch_04_unit_consistency(p: ProbedCALDEX):
    return draft("Reviewer to verify unit consistency rules documented across all calibration parameters.", action="Audit Acceptance Criteria for unit alignment requirement.")


def exch_05_baseline_snapshot(p: ProbedCALDEX):
    return draft("Reviewer to verify baseline snapshots are complete and immutable.", action="Check Baseline References completeness and date-tagging.")


def exch_06_metadata_retention(p: ProbedCALDEX):
    return draft("Reviewer to verify metadata retention policy documented (12+ months baseline history).", action="Confirm Version Control retention rules.")


def exch_07_file_validation(p: ProbedCALDEX):
    return draft("Reviewer to verify file validation rules (format compatibility, checksums) documented.", action="Add validation rules to Exchange Format tab.")


def exch_08_multi_variant(p: ProbedCALDEX):
    return draft("Reviewer to verify multi-variant support defined if applicable (Euro5, EPA, etc.).", action="Check Exchange Format Specification for variant handling.")


def exch_09_tool_compatibility(p: ProbedCALDEX):
    return draft("Reviewer to verify tool compatibility matrix (INCA, CANape, ATI Vision) documented.", action="Add tooling compatibility to Exchange Formats.")


# Signoff & Authority (5)
def sign_01_oem_signoff(p: ProbedCALDEX):
    if p.has_signoff:
        return draft("Reviewer to verify OEM signoff block is populated with authorized signatures.", page_section="Signoff Block", action="Confirm OEM Lead and Manager signatures.")
    return CheckResult(rating="NO", finding="No Signoff Block tab.", recommended_action="Add OEM and Tier-1 signoff fields.", confidence="High")


def sign_02_tier1_signoff(p: ProbedCALDEX):
    if p.has_signoff:
        return draft("Reviewer to verify Tier-1 signoff block is populated with authorized signatures.", page_section="Signoff Block", action="Confirm Tier-1 Lead and Manager signatures.")
    return na("No signoff fields found.")


def sign_03_approval_dates(p: ProbedCALDEX):
    return draft("Reviewer to verify approval dates recorded for all signoffs.", action="Check Signoff Block for date fields populated.")


def sign_04_dispute_resolution(p: ProbedCALDEX):
    return draft("Reviewer to verify dispute resolution procedure documented.", action="Audit Change Protocol for escalation process.")


def sign_05_change_notification(p: ProbedCALDEX):
    if p.has_change_protocol:
        return draft("Reviewer to verify change notification process defined (timing, recipients).", page_section="Change Protocol", action="Audit notification timeline and distribution list.")
    return CheckResult(rating="PC", finding="Change notification process unclear.", recommended_action="Document notification requirements.", confidence="High")


CHECKS = [
    CheckDef("AGR.01", "Agreement Structure", "Title & Scope", "Clear title and scope present", "MUST"),
    CheckDef("AGR.02", "Agreement Structure", "Authorship", "Author/initiator documented", "SHOULD"),
    CheckDef("AGR.03", "Agreement Structure", "Versioning", "Revision number recorded", "MUST"),
    CheckDef("AGR.04", "Agreement Structure", "Parties", "OEM and Tier-1 identified", "MUST"),
    CheckDef("AGR.05", "Agreement Structure", "Ownership", "Parameter ownership matrix complete", "MUST"),
    CheckDef("AGR.06", "Agreement Structure", "Baselines", "Baseline references documented", "MUST"),
    CheckDef("AGR.07", "Agreement Structure", "Document Control", "Change log present", "SHOULD"),
    CheckDef("AGR.08", "Agreement Structure", "Change Protocol", "Change approval process defined", "MUST"),
    CheckDef("AGR.09", "Agreement Structure", "Roles", "Roles and responsibilities clear", "SHOULD"),
    CheckDef("AGR.10", "Agreement Structure", "Scope Clarity", "Agreement scope clearly bounded", "MUST"),
    CheckDef("AGR.11", "Agreement Structure", "Functional Safety", "Safety requirements documented if applicable", "SHOULD"),
    CheckDef("EXCH.01", "Exchange & Acceptance", "Exchange Formats", "Exchange formats specified (DCM, CDFX, PaCo)", "MUST"),
    CheckDef("EXCH.02", "Exchange & Acceptance", "Version Control", "Version control scheme defined", "MUST"),
    CheckDef("EXCH.03", "Exchange & Acceptance", "Acceptance Criteria", "Acceptance criteria measurable and complete", "MUST"),
    CheckDef("EXCH.04", "Exchange & Acceptance", "Unit Consistency", "Unit consistency rules documented", "MUST"),
    CheckDef("EXCH.05", "Exchange & Acceptance", "Baseline Snapshot", "Baseline snapshots immutable and traceable", "MUST"),
    CheckDef("EXCH.06", "Exchange & Acceptance", "Metadata Retention", "Data retention policy defined (12+ months)", "SHOULD"),
    CheckDef("EXCH.07", "Exchange & Acceptance", "File Validation", "File validation and checksums defined", "SHOULD"),
    CheckDef("EXCH.08", "Exchange & Acceptance", "Multi-Variant", "Multi-variant support defined if applicable", "SHOULD"),
    CheckDef("EXCH.09", "Exchange & Acceptance", "Tool Compatibility", "Tool compatibility matrix documented", "SHOULD"),
    CheckDef("SIGN.01", "Signoff & Authority", "OEM Signoff", "OEM authorization signatures collected", "MUST"),
    CheckDef("SIGN.02", "Signoff & Authority", "Tier-1 Signoff", "Tier-1 authorization signatures collected", "MUST"),
    CheckDef("SIGN.03", "Signoff & Authority", "Approval Dates", "Approval dates recorded for all signoffs", "MUST"),
    CheckDef("SIGN.04", "Signoff & Authority", "Dispute Resolution", "Dispute resolution procedure documented", "SHOULD"),
    CheckDef("SIGN.05", "Signoff & Authority", "Change Notification", "Change notification process defined", "MUST"),
]


def execute_checks(p: ProbedCALDEX) -> dict[str, CheckResult]:
    return {
        "AGR.01": agr_01_title(p),
        "AGR.02": agr_02_author(p),
        "AGR.03": agr_03_revision(p),
        "AGR.04": agr_04_parties(p),
        "AGR.05": agr_05_ownership_matrix(p),
        "AGR.06": agr_06_baseline_refs(p),
        "AGR.07": agr_07_document_control(p),
        "AGR.08": agr_08_change_protocol(p),
        "AGR.09": agr_09_roles_defined(p),
        "AGR.10": agr_10_scope_clear(p),
        "AGR.11": agr_11_functional_safety(p),
        "EXCH.01": exch_01_formats(p),
        "EXCH.02": exch_02_version_control(p),
        "EXCH.03": exch_03_acceptance_criteria(p),
        "EXCH.04": exch_04_unit_consistency(p),
        "EXCH.05": exch_05_baseline_snapshot(p),
        "EXCH.06": exch_06_metadata_retention(p),
        "EXCH.07": exch_07_file_validation(p),
        "EXCH.08": exch_08_multi_variant(p),
        "EXCH.09": exch_09_tool_compatibility(p),
        "SIGN.01": sign_01_oem_signoff(p),
        "SIGN.02": sign_02_tier1_signoff(p),
        "SIGN.03": sign_03_approval_dates(p),
        "SIGN.04": sign_04_dispute_resolution(p),
        "SIGN.05": sign_05_change_notification(p),
    }
