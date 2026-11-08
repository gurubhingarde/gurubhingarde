"""DCM Confirmation Review checks."""

from __future__ import annotations

from dataclasses import dataclass
from dcm_probe import ProbedDCM


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


# Confirmation Review (12)
def cr_01_title(p: ProbedDCM):
    if p.title:
        return draft(f"Title: '{p.title}'. Reviewer to confirm scope.", page_section="Title")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add clear dataset title.", confidence="High")


def cr_02_author_approver(p: ProbedDCM):
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    missing = ([] if p.author else ["Author"]) + ([] if p.approver else ["Approver"])
    return CheckResult(rating="NO", finding=f"Missing: {', '.join(missing)}.", recommended_action=f"Populate {', '.join(missing)}.", confidence="High")


def cr_03_revision(p: ProbedDCM):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision: {p.revision}.", confidence="High")
    return CheckResult(rating="NO", finding="No revision field.", recommended_action="Add unique revision number.", confidence="High")


def cr_04_variant(p: ProbedDCM):
    if p.variant:
        return CheckResult(rating="FC", finding=f"Variant recorded: {p.variant}.", confidence="High")
    return CheckResult(rating="PC", finding="Variant not specified.", recommended_action="Record calibration variant (e.g., Euro5, EPA).", confidence="High")


def cr_05_build_date(p: ProbedDCM):
    if p.build_date:
        return CheckResult(rating="FC", finding=f"Build date: {p.build_date}.", confidence="High")
    return CheckResult(rating="PC", finding="Build date missing.", recommended_action="Record dataset creation date.", confidence="High")


def cr_06_source_a2l(p: ProbedDCM):
    if p.has_source_a2l and p.source_a2l:
        return CheckResult(rating="FC", finding=f"Source A2L: {p.source_a2l}.", confidence="High")
    return CheckResult(rating="NO", finding="Source A2L Reference tab missing or empty.", recommended_action="Link to source A2L document and version.", confidence="High")


def cr_07_document_control(p: ProbedDCM):
    if p.has_document_control:
        return CheckResult(rating="FC", finding="Document Control tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No Document Control tab.", recommended_action="Add change log and baseline traceability.", confidence="High")


def cr_08_dataset_identity(p: ProbedDCM):
    if p.has_dataset_identity:
        return CheckResult(rating="FC", finding="Dataset Identity tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No Dataset Identity tab.", recommended_action="Record variant, build date, equipment ID.", confidence="High")


def cr_09_scalars(p: ProbedDCM):
    if p.scalar_count > 0:
        return CheckResult(rating="FC", finding=f"Scalar Values tab contains {p.scalar_count} items.", confidence="High")
    return CheckResult(rating="LC", finding="Scalar Values empty or missing.", recommended_action="Add FUNKTIONEN entries.", confidence="Medium")


def cr_10_curves(p: ProbedDCM):
    if p.curve_count > 0:
        return CheckResult(rating="FC", finding=f"Curve Values tab contains {p.curve_count} items.", confidence="High")
    return CheckResult(rating="LC", finding="Curve Values empty.", recommended_action="Add KENNLINIE entries if applicable.", confidence="Medium")


def cr_11_maps(p: ProbedDCM):
    if p.map_count > 0:
        return CheckResult(rating="FC", finding=f"Map Values tab contains {p.map_count} items.", confidence="High")
    return CheckResult(rating="LC", finding="Map Values empty.", recommended_action="Add KENNFELD entries if applicable.", confidence="Medium")


def cr_12_axes(p: ProbedDCM):
    if p.axis_point_count > 0:
        return CheckResult(rating="FC", finding=f"Axis Point Values tab contains {p.axis_point_count} items.", confidence="High")
    return CheckResult(rating="NO", finding="Axis Point Values empty.", recommended_action="Define STUETZSTELLENVERTEILUNG for all axes.", confidence="High")


# Value Validation (10)
def val_01_physical_range(p: ProbedDCM):
    if p.scalar_count > 0:
        return draft(f"Reviewer to verify all {p.scalar_count} scalar values within physical ranges.", action="Check min/max bounds.")
    return na("No scalars to validate.")


def val_02_curve_range(p: ProbedDCM):
    if p.curve_count > 0:
        return draft(f"Reviewer to verify {p.curve_count} curve values are bounded and monotonic.", action="Audit KENNLINIE entries.")
    return na("No curves to validate.")


def val_03_map_dimensions(p: ProbedDCM):
    if p.map_count > 0:
        return draft(f"Reviewer to verify {p.map_count} map dimensions match axis references.", action="Confirm rows/cols vs axes.")
    return na("No maps to validate.")


def val_04_axis_monotonic(p: ProbedDCM):
    if p.axis_point_count > 0:
        return draft(f"Reviewer to verify all {p.axis_point_count} axis point vectors are strictly increasing.", action="Check monotonicity.")
    return na("No axes to validate.")


def val_05_value_blocks(p: ProbedDCM):
    if p.value_block_count > 0:
        return draft(f"Reviewer to verify {p.value_block_count} value block members are defined.", action="Cross-check member references.")
    return CheckResult(rating="LC", finding="No value blocks defined.", recommended_action="Add FESTWERTEBLOCK if applicable.", confidence="Medium")


def val_06_no_nan(p: ProbedDCM):
    return draft("Reviewer to verify no NaN or Inf values in numeric fields.", action="Scan all value columns.")


def val_07_unit_consistency(p: ProbedDCM):
    return draft("Reviewer to verify unit consistency across dataset.", action="Compare units in Scalar, Curve, Map, Axis tabs.")


def val_08_name_uniqueness(p: ProbedDCM):
    return draft("Reviewer to verify all parameter names are unique.", action="Check for duplicate names across tabs.")


def val_09_axis_size_match(p: ProbedDCM):
    if p.curve_count > 0 or p.map_count > 0:
        return draft("Reviewer to verify curve/map value counts match axis point counts.", action="Audit array dimensions.")
    return na("No curves/maps to validate.")


def val_10_data_type_valid(p: ProbedDCM):
    return draft("Reviewer to verify all numeric values are valid (no text in numeric fields).", action="Type check all value columns.")


# Baseline & Traceability (6)
def base_01_source_version(p: ProbedDCM):
    if p.has_source_a2l:
        return draft("Reviewer to confirm source A2L version is specified.", page_section="Source A2L Reference", action="Verify A2L version match.")
    return CheckResult(rating="NO", finding="Source A2L Reference tab missing.", recommended_action="Add source A2L document and version.", confidence="High")


def base_02_baseline_link(p: ProbedDCM):
    return draft("Reviewer to verify baseline reference is documented.", action="Confirm link to approved baseline dataset.", page_section="Document Control")


def base_03_change_history(p: ProbedDCM):
    if p.has_document_control:
        return draft("Reviewer to verify change history is recorded.", action="Audit revision log completeness.", page_section="Document Control")
    return CheckResult(rating="PC", finding="No Document Control tab.", recommended_action="Add change history tab.", confidence="High")


def base_04_approver(p: ProbedDCM):
    if p.approver:
        return CheckResult(rating="FC", finding=f"Approver documented: {p.approver}.", confidence="High")
    return CheckResult(rating="NO", finding="No approver documented.", recommended_action="Add approver name and signature.", confidence="High")


def base_05_dataset_version(p: ProbedDCM):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Dataset version: {p.revision}.", confidence="High")
    return CheckResult(rating="NO", finding="Dataset version not unique.", recommended_action="Assign unique version identifier.", confidence="High")


def base_06_equipment_id(p: ProbedDCM):
    return draft("Reviewer to verify equipment/vehicle ID is recorded.", action="Confirm ECU or test bench identifier in Dataset Identity.", page_section="Dataset Identity")


CHECKS = [
    CheckDef("CR.01", "Confirmation Review", "Title & Metadata", "Clear title present", "MUST"),
    CheckDef("CR.02", "Confirmation Review", "Title & Metadata", "Author and approver documented", "MUST"),
    CheckDef("CR.03", "Confirmation Review", "Title & Metadata", "Revision number recorded", "MUST"),
    CheckDef("CR.04", "Confirmation Review", "Dataset Identity", "Variant specified", "SHOULD"),
    CheckDef("CR.05", "Confirmation Review", "Dataset Identity", "Build date recorded", "SHOULD"),
    CheckDef("CR.06", "Confirmation Review", "Source Reference", "Source A2L documented", "MUST"),
    CheckDef("CR.07", "Confirmation Review", "Document Control", "Document Control tab present", "SHOULD"),
    CheckDef("CR.08", "Confirmation Review", "Dataset Identity", "Dataset Identity tab present", "SHOULD"),
    CheckDef("CR.09", "Confirmation Review", "Value Catalogs", "Scalar Values populated", "SHOULD"),
    CheckDef("CR.10", "Confirmation Review", "Value Catalogs", "Curve Values present", "SHOULD"),
    CheckDef("CR.11", "Confirmation Review", "Value Catalogs", "Map Values present", "SHOULD"),
    CheckDef("CR.12", "Confirmation Review", "Axes", "Axis Point Values defined", "MUST"),
    CheckDef("VAL.01", "Value Validation", "Physical Range", "All values within bounds", "MUST"),
    CheckDef("VAL.02", "Value Validation", "Curve Validation", "Curve values monotonic", "MUST"),
    CheckDef("VAL.03", "Value Validation", "Map Validation", "Map dimensions match axes", "MUST"),
    CheckDef("VAL.04", "Value Validation", "Axis Validation", "Axis points strictly increasing", "MUST"),
    CheckDef("VAL.05", "Value Validation", "Block Validation", "Value block members defined", "SHOULD"),
    CheckDef("VAL.06", "Value Validation", "Data Quality", "No NaN or Inf values", "MUST"),
    CheckDef("VAL.07", "Value Validation", "Unit Consistency", "Units consistent across dataset", "MUST"),
    CheckDef("VAL.08", "Value Validation", "Name Uniqueness", "Parameter names unique", "MUST"),
    CheckDef("VAL.09", "Value Validation", "Array Dimensions", "Value counts match axes", "MUST"),
    CheckDef("VAL.10", "Value Validation", "Data Type", "All numeric values valid", "MUST"),
    CheckDef("BASE.01", "Baseline & Traceability", "Source A2L", "Source A2L version specified", "MUST"),
    CheckDef("BASE.02", "Baseline & Traceability", "Baseline Link", "Baseline reference documented", "MUST"),
    CheckDef("BASE.03", "Baseline & Traceability", "Change History", "Change history recorded", "SHOULD"),
    CheckDef("BASE.04", "Baseline & Traceability", "Approvals", "Approver documented", "MUST"),
    CheckDef("BASE.05", "Baseline & Traceability", "Version Control", "Dataset version unique", "MUST"),
    CheckDef("BASE.06", "Baseline & Traceability", "Equipment ID", "Equipment/vehicle ID recorded", "SHOULD"),
]


def execute_checks(p: ProbedDCM) -> dict[str, CheckResult]:
    return {
        "CR.01": cr_01_title(p),
        "CR.02": cr_02_author_approver(p),
        "CR.03": cr_03_revision(p),
        "CR.04": cr_04_variant(p),
        "CR.05": cr_05_build_date(p),
        "CR.06": cr_06_source_a2l(p),
        "CR.07": cr_07_document_control(p),
        "CR.08": cr_08_dataset_identity(p),
        "CR.09": cr_09_scalars(p),
        "CR.10": cr_10_curves(p),
        "CR.11": cr_11_maps(p),
        "CR.12": cr_12_axes(p),
        "VAL.01": val_01_physical_range(p),
        "VAL.02": val_02_curve_range(p),
        "VAL.03": val_03_map_dimensions(p),
        "VAL.04": val_04_axis_monotonic(p),
        "VAL.05": val_05_value_blocks(p),
        "VAL.06": val_06_no_nan(p),
        "VAL.07": val_07_unit_consistency(p),
        "VAL.08": val_08_name_uniqueness(p),
        "VAL.09": val_09_axis_size_match(p),
        "VAL.10": val_10_data_type_valid(p),
        "BASE.01": base_01_source_version(p),
        "BASE.02": base_02_baseline_link(p),
        "BASE.03": base_03_change_history(p),
        "BASE.04": base_04_approver(p),
        "BASE.05": base_05_dataset_version(p),
        "BASE.06": base_06_equipment_id(p),
    }
