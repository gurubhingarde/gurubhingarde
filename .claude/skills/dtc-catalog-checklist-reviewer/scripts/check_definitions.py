"""DTC Catalog confirmation-measures checks."""

from __future__ import annotations

from dataclasses import dataclass

from dtc_probe import ProbedDTC


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
    if len(p.sheet_names) >= 7:
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
        return CheckResult(rating="FC", finding="ECU Identification tab present.", confidence="Medium")
    return CheckResult(rating="PC", finding="ECU Identification not identified.", recommended_action="Add ECU ID tab.", confidence="Medium")


def cr_09_status_field(p):
    if p.status:
        return CheckResult(rating="FC", finding=f"Status: '{p.status}'.", confidence="High")
    return CheckResult(rating="PC", finding="Status not populated.", recommended_action="Add status field.", confidence="Medium")


def cr_10_references(p):
    if "References" in p.sheet_names:
        return CheckResult(rating="FC", finding="References tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add References tab.", confidence="Medium")


# DTC Assessment (15 checks)

def ta_01_dtc_count(p):
    if p.dtc_count > 0:
        return CheckResult(rating="FC", finding=f"{p.dtc_count} DTCs defined.", confidence="High")
    return CheckResult(rating="NO", finding="No DTCs found.", recommended_action="Add DTC inventory.", confidence="High")


def ta_02_unique_codes(p):
    if len(p.dtc_codes) == len(set(p.dtc_codes)):
        return CheckResult(rating="FC", finding="All DTC codes are unique.", confidence="High")
    duplicates = len(p.dtc_codes) - len(set(p.dtc_codes))
    return CheckResult(rating="NO", finding=f"{duplicates} duplicate codes found.", recommended_action="Remove duplicates.", confidence="High")


def ta_03_code_format(p):
    valid_prefix = sum(1 for c in p.dtc_codes if c and c[0] in "PBCU")
    if valid_prefix == len(p.dtc_codes):
        return CheckResult(rating="FC", finding="All codes have valid P/B/C/U prefix.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(p.dtc_codes) - valid_prefix} codes have invalid prefix.", recommended_action="Check code format per SAE J2012.", confidence="High")


def ta_04_fault_types(p):
    return draft("Fault types not machine-verifiable from xlsx.", action="Review DTC Inventory tab for type consistency.")


def ta_05_severity(p):
    return draft("Severity ratings require reviewer judgment.", action="Confirm severity per ISO 14229-1.")


def ta_06_customer_impact(p):
    return draft("Customer impact mapping requires review.", action="Verify customer impact assignments.")


def ta_07_status_mask_bits(p):
    if p.status_mask_bits >= 4:
        return CheckResult(rating="FC", finding=f"{p.status_mask_bits} status mask bits configured.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.status_mask_bits} bits configured.", recommended_action="Add all required status mask bits per ISO 14229-1.", confidence="High")


def ta_08_debounce_coverage(p):
    if len(p.debounce_algorithms) > 0:
        return CheckResult(rating="FC", finding=f"{len(p.debounce_algorithms)} debounce algorithms defined.", confidence="High")
    return CheckResult(rating="PC", finding="No debounce algorithms.", recommended_action="Define debounce algorithms.", confidence="Medium")


def ta_09_healing_logic(p):
    if p.healing_logic_coverage >= 0.9:
        return CheckResult(rating="FC", finding=f"{int(p.healing_logic_coverage * 100)}% of DTCs have healing logic.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {int(p.healing_logic_coverage * 100)}% healing coverage.", recommended_action="Specify healing conditions for all DTCs.", confidence="High")


def ta_10_snapshot_diag(p):
    if p.snapshot_bindings_count >= p.dtc_count * 0.8:
        return CheckResult(rating="FC", finding=f"{p.snapshot_bindings_count} snapshot bindings.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {p.snapshot_bindings_count} snapshot bindings.", recommended_action="Define snapshot DIDs for all DTCs.", confidence="Medium")


def ta_11_extended_data(p):
    if p.extended_data_count > 0:
        return CheckResult(rating="FC", finding=f"{p.extended_data_count} extended data records.", confidence="High")
    return CheckResult(rating="PC", finding="No extended data records.", recommended_action="Define extended data structure.", confidence="Medium")


def ta_12_mal_function_id(p):
    return draft("Malfunction IDs not machine-verifiable.", action="Confirm all DTCs linked to malfunction IDs.")


def ta_13_test_conditions(p):
    return draft("Test conditions coverage not auto-verifiable.", action="Verify set/clear conditions documented.")


def ta_14_consistency(p):
    return draft("Cross-tab consistency requires manual review.", action="Check DTC references across all tabs.")


def ta_15_traceability(p):
    return draft("Traceability to source standards not verifiable.", action="Confirm DTCs trace to ECU spec.")


# OBD Assessment (5 checks)

def oa_01_obd_mapping(p):
    if p.obd_mappings > 0:
        return CheckResult(rating="FC", finding=f"{p.obd_mappings} OBD mappings.", confidence="High")
    return CheckResult(rating="PC", finding="No OBD mappings.", recommended_action="Map DTCs to OBD-II codes.", confidence="Medium")


def oa_02_readiness_monitor(p):
    return draft("Readiness monitor assignment not machine-verifiable.", action="Confirm each OBD DTC has monitor type.")


def oa_03_emissions_relevance(p):
    return draft("Emissions relevance classification requires review.", action="Verify emissions-related DTCs marked correctly.")


def oa_04_obd_compliance(p):
    return draft("OBD-II compliance per ISO 15031-6 not verifiable.", action="Confirm OBD mapping per standard.")


def oa_05_monitor_coverage(p):
    return draft("All required monitors (0xF180-0xF18B) not verifiable.", action="Check OBD DID coverage per ISO 14229.")


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
    ("TA-01", "DTC Count", ta_01_dtc_count, "Shall"),
    ("TA-02", "Unique Codes", ta_02_unique_codes, "Shall"),
    ("TA-03", "Code Format", ta_03_code_format, "Shall"),
    ("TA-04", "Fault Types", ta_04_fault_types, "Should"),
    ("TA-05", "Severity", ta_05_severity, "Should"),
    ("TA-06", "Customer Impact", ta_06_customer_impact, "Should"),
    ("TA-07", "Status Masks", ta_07_status_mask_bits, "Shall"),
    ("TA-08", "Debounce Algorithms", ta_08_debounce_coverage, "Shall"),
    ("TA-09", "Healing Logic", ta_09_healing_logic, "Shall"),
    ("TA-10", "Snapshot DIDs", ta_10_snapshot_diag, "Should"),
    ("TA-11", "Extended Data", ta_11_extended_data, "Should"),
    ("TA-12", "Malfunction IDs", ta_12_mal_function_id, "Should"),
    ("TA-13", "Test Conditions", ta_13_test_conditions, "Should"),
    ("TA-14", "Consistency", ta_14_consistency, "Should"),
    ("TA-15", "Traceability", ta_15_traceability, "Should"),
    ("OA-01", "OBD Mapping", oa_01_obd_mapping, "Should"),
    ("OA-02", "Readiness Monitor", oa_02_readiness_monitor, "Should"),
    ("OA-03", "Emissions Relevance", oa_03_emissions_relevance, "Should"),
    ("OA-04", "OBD Compliance", oa_04_obd_compliance, "Should"),
    ("OA-05", "Monitor Coverage", oa_05_monitor_coverage, "Should"),
]


class CheckDef:
    """Compatibility wrapper."""
    def __init__(self, check_id, name, func, obligation):
        self.check_id = check_id
        self.name = name
        self.func = func
        self.obligation = obligation
