"""A2L Confirmation Review checks."""

from __future__ import annotations

from dataclasses import dataclass

from a2l_probe import ProbedA2L


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


def draft(finding, page_section="", action="(Reviewer to verify and assess)"):
    return CheckResult(rating="", finding="(Auto-suggest, requires reviewer judgment) " + finding, page_section=page_section, recommended_action=action, confidence="Low")


def na(reason):
    return CheckResult(rating="NA", finding=reason, confidence="High")


# Confirmation Review checks (14)
def cr_01_structured(p: ProbedA2L):
    if len(p.sheet_names) >= 10:
        return CheckResult(rating="FC", finding=f"Document is structured into {len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Add structured sections per A2L methodology.", confidence="Medium")


def cr_02_title(p: ProbedA2L):
    if p.title:
        return draft(f"Title detected: '{p.title}'. Reviewer to confirm scope coverage.", page_section="Title")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add a clear, descriptive title.", confidence="High")


def cr_03_author_approver(p: ProbedA2L):
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    missing = ([] if p.author else ["Author"]) + ([] if p.approver else ["Approver"])
    return CheckResult(rating="NO", finding=f"Missing on Title page: {', '.join(missing)}.", recommended_action=f"Populate {', '.join(missing)}.", confidence="High")


def cr_04_revision(p: ProbedA2L):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision tracked: {p.revision}.", confidence="High")
    return CheckResult(rating="NO", finding="No revision field.", recommended_action="Add unique revision number.", confidence="High")


def cr_05_document_control(p: ProbedA2L):
    if p.has_document_control:
        return CheckResult(rating="FC", finding="Document Control tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No Document Control tab.", recommended_action="Add change log and approval chain.", confidence="High")


def cr_06_characteristics_catalog(p: ProbedA2L):
    if p.characteristic_count > 0:
        return CheckResult(rating="FC", finding=f"Characteristic Catalog populated with {p.characteristic_count} items.", confidence="High")
    return CheckResult(rating="PC", finding="Characteristic Catalog empty or missing.", recommended_action="Populate with VALUE, CURVE, MAP definitions.", confidence="High")


def cr_07_measurements_catalog(p: ProbedA2L):
    if p.measurement_count > 0:
        return CheckResult(rating="FC", finding=f"Measurement Catalog contains {p.measurement_count} signals.", confidence="High")
    return CheckResult(rating="LC", finding="Measurement Catalog empty.", recommended_action="Add observable signals if applicable.", confidence="Medium")


def cr_08_conversion_methods(p: ProbedA2L):
    if p.conversion_method_count > 0:
        return CheckResult(rating="FC", finding=f"Conversion Methods tab contains {p.conversion_method_count} methods.", confidence="High")
    return CheckResult(rating="NO", finding="Conversion Methods tab empty.", recommended_action="Define LINEAR, RAT_FUNC, or other methods.", confidence="High")


def cr_09_axes_defined(p: ProbedA2L):
    if p.axis_count > 0:
        return CheckResult(rating="FC", finding=f"Axis Descriptions tab contains {p.axis_count} axes.", confidence="High")
    return CheckResult(rating="PC", finding="Axis Descriptions empty.", recommended_action="Define axes for CURVE/MAP characteristics.", confidence="High")


def cr_10_records_defined(p: ProbedA2L):
    if p.record_count > 0:
        return CheckResult(rating="FC", finding=f"Record Layouts tab contains {p.record_count} records.", confidence="High")
    return CheckResult(rating="LC", finding="Record Layouts empty.", recommended_action="Add record definitions for composite objects.", confidence="Medium")


def cr_11_functions_organized(p: ProbedA2L):
    if p.function_count > 0:
        return CheckResult(rating="FC", finding=f"Function Hierarchy contains {p.function_count} functions.", confidence="High")
    return CheckResult(rating="PC", finding="Function Hierarchy empty.", recommended_action="Organize characteristics into functions.", confidence="High")


def cr_12_groups_organized(p: ProbedA2L):
    if p.group_count > 0:
        return CheckResult(rating="FC", finding=f"Group Hierarchy contains {p.group_count} groups.", confidence="High")
    return CheckResult(rating="LC", finding="Group Hierarchy empty.", recommended_action="Organize functions into logical groups.", confidence="Medium")


def cr_13_memory_mapping(p: ProbedA2L):
    if p.memory_address_count > 0:
        return CheckResult(rating="FC", finding=f"Memory Address Mapping contains {p.memory_address_count} address ranges ({p.total_memory_bytes} bytes).", confidence="High")
    return CheckResult(rating="NO", finding="Memory Address Mapping empty.", recommended_action="Map all characteristics to ECU memory addresses.", confidence="High")


def cr_14_validation_rules(p: ProbedA2L):
    if p.has_validation_rules:
        return CheckResult(rating="FC", finding="Validation Rules tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No Validation Rules tab.", recommended_action="Add consistency and integrity checks.", confidence="High")


# A2L Object Completeness checks (8)
def obj_01_characteristic_types(p: ProbedA2L):
    types = [p.value_count, p.curve_count, p.map_count, p.axis_pts_count, p.val_blk_count]
    types_count = sum(1 for t in types if t > 0)
    if types_count >= 3:
        return CheckResult(rating="FC", finding=f"Multiple characteristic types present: VALUE={p.value_count}, CURVE={p.curve_count}, MAP={p.map_count}.", confidence="High")
    return CheckResult(rating="PC", finding=f"Limited characteristic type diversity ({types_count} types).", recommended_action="Verify characteristic types match ECU calibration structure.", confidence="High")


def obj_02_conversion_method_match(p: ProbedA2L):
    if p.conversion_method_count > 0 and p.characteristic_count > 0:
        ratio = p.conversion_method_count / max(1, p.characteristic_count)
        if ratio >= 0.5:
            return CheckResult(rating="FC", finding=f"Conversion methods defined ({p.conversion_method_count} methods for {p.characteristic_count} characteristics).", confidence="Medium")
    return CheckResult(rating="PC", finding="Conversion method count does not match characteristic count.", recommended_action="Ensure every characteristic has a conversion method.", confidence="Medium")


def obj_03_axis_coverage(p: ProbedA2L):
    curve_and_maps = p.curve_count + p.map_count
    if p.axis_count > 0 and curve_and_maps > 0:
        return CheckResult(rating="FC", finding=f"Axes defined for {p.curve_count} CURVEs and {p.map_count} MAPs.", confidence="High")
    return CheckResult(rating="PC", finding="Axis definitions may be incomplete.", recommended_action="Define axes for all CURVE and MAP characteristics.", confidence="High")


def obj_04_record_completeness(p: ProbedA2L):
    if p.val_blk_count > 0 and p.record_count > 0:
        return CheckResult(rating="FC", finding=f"Record Layouts support {p.val_blk_count} VAL_BLK characteristics.", confidence="High")
    return CheckResult(rating="LC", finding="Record count does not match VAL_BLK count.", recommended_action="Verify record definitions for composite objects.", confidence="Medium")


def obj_05_memory_allocation(p: ProbedA2L):
    if p.total_memory_bytes > 0 and p.characteristic_count > 0:
        return CheckResult(rating="FC", finding=f"Total memory allocated: {p.total_memory_bytes} bytes across {p.memory_address_count} ranges.", confidence="High")
    return CheckResult(rating="PC", finding="Memory allocation incomplete.", recommended_action="Assign addresses to all characteristics.", confidence="High")


def obj_06_function_coverage(p: ProbedA2L):
    if p.function_count > 0:
        return CheckResult(rating="FC", finding=f"Functions defined: {p.function_count}.", confidence="High")
    return CheckResult(rating="PC", finding="No functions defined.", recommended_action="Organize characteristics into named functions.", confidence="High")


def obj_07_group_structure(p: ProbedA2L):
    if p.group_count > 0:
        return CheckResult(rating="FC", finding=f"Group hierarchy defined: {p.group_count} groups.", confidence="High")
    return CheckResult(rating="LC", finding="No groups defined.", recommended_action="Create logical grouping hierarchy.", confidence="Medium")


def obj_08_ecu_identity(p: ProbedA2L):
    if p.ecu_part_number:
        return CheckResult(rating="FC", finding=f"ECU identity recorded: {p.ecu_part_number}.", confidence="High")
    return draft("ECU part number not detected. Reviewer to confirm ECU identity is recorded.", page_section="ECU Identity")


# Memory & Address Validation checks (5)
def mem_01_address_bounds(p: ProbedA2L):
    if p.memory_address_count > 0:
        return draft(f"Found {p.memory_address_count} address assignments. Reviewer to verify all are within ECU memory bounds.", action="Audit address ranges against ECU datasheet.")
    return CheckResult(rating="NA", finding="No memory mapping to validate.", confidence="High")


def mem_02_address_overlap(p: ProbedA2L):
    return draft("Reviewer to check for overlapping address ranges in Memory Address Mapping tab.", action="Calculate range intersections; flag any overlaps.")


def mem_03_segment_alignment(p: ProbedA2L):
    return draft("Reviewer to verify address alignment matches data type (byte-aligned for 8-bit, etc.).", action="Confirm alignment per ASAM standard.")


def mem_04_size_consistency(p: ProbedA2L):
    if p.characteristic_count > 0:
        return draft(f"Size calculations for {p.characteristic_count} characteristics need verification.", action="Audit byte counts match data types and array dimensions.")
    return CheckResult(rating="NA", finding="No characteristics to validate.", confidence="High")


def mem_05_memory_summary(p: ProbedA2L):
    if p.total_memory_bytes > 0:
        return CheckResult(rating="FC", finding=f"Total memory footprint: {p.total_memory_bytes} bytes.", confidence="High")
    return CheckResult(rating="PC", finding="Memory footprint unclear.", recommended_action="Sum all size columns in Memory Address Mapping.", confidence="High")


# Conversion Method Validation checks (3)
def conv_01_linear_params(p: ProbedA2L):
    if p.conversion_method_count > 0:
        return draft("Reviewer to verify LINEAR method parameters (a, b) are properly defined for all applicable characteristics.", action="Check each LINEAR method entry.")
    return CheckResult(rating="NA", finding="No conversion methods to validate.", confidence="High")


def conv_02_formula_syntax(p: ProbedA2L):
    if p.conversion_method_count > 0:
        return draft("Reviewer to inspect FORMULA methods for correct algebraic syntax and variable references.", action="Audit formula expressions in Conversion Methods tab.")
    return CheckResult(rating="NA", finding="No conversion methods to validate.", confidence="High")


def conv_03_unit_consistency(p: ProbedA2L):
    if p.characteristic_count > 0 and p.conversion_method_count > 0:
        return draft("Reviewer to verify unit consistency between Characteristic Catalog and Conversion Methods.", action="Cross-check units per characteristic type.")
    return CheckResult(rating="NA", finding="Insufficient data to validate.", confidence="High")


# Define all checks
CHECKS = [
    CheckDef("CR.01", "Confirmation Review", "Document Structure", "Document structured into logical tabs", "SHOULD"),
    CheckDef("CR.02", "Confirmation Review", "Title & Metadata", "Document has clear title", "MUST"),
    CheckDef("CR.03", "Confirmation Review", "Title & Metadata", "Author and approver documented", "MUST"),
    CheckDef("CR.04", "Confirmation Review", "Title & Metadata", "Revision number recorded", "MUST"),
    CheckDef("CR.05", "Confirmation Review", "Document Control", "Change log and approval chain present", "SHOULD"),
    CheckDef("CR.06", "Confirmation Review", "Catalog Completeness", "Characteristic Catalog populated", "MUST"),
    CheckDef("CR.07", "Confirmation Review", "Catalog Completeness", "Measurement Catalog present", "SHOULD"),
    CheckDef("CR.08", "Confirmation Review", "Conversion Methods", "Conversion Methods defined", "MUST"),
    CheckDef("CR.09", "Confirmation Review", "Axis Definitions", "Axes defined for lookups", "SHOULD"),
    CheckDef("CR.10", "Confirmation Review", "Record Layouts", "Record structures defined", "SHOULD"),
    CheckDef("CR.11", "Confirmation Review", "Function Hierarchy", "Functions organized", "MUST"),
    CheckDef("CR.12", "Confirmation Review", "Group Hierarchy", "Groups organized", "SHOULD"),
    CheckDef("CR.13", "Confirmation Review", "Memory Mapping", "Memory addresses assigned", "MUST"),
    CheckDef("CR.14", "Confirmation Review", "Validation Rules", "Validation rules present", "SHOULD"),
    CheckDef("OBJ.01", "A2L Objects", "Characteristic Types", "Multiple characteristic types present", "SHOULD"),
    CheckDef("OBJ.02", "A2L Objects", "Conversion Methods", "Every characteristic has conversion method", "MUST"),
    CheckDef("OBJ.03", "A2L Objects", "Axis Coverage", "Axes defined for CURVE and MAP", "MUST"),
    CheckDef("OBJ.04", "A2L Objects", "Record Layouts", "Records match VAL_BLK definitions", "SHOULD"),
    CheckDef("OBJ.05", "A2L Objects", "Memory Allocation", "Memory allocated to all characteristics", "MUST"),
    CheckDef("OBJ.06", "A2L Objects", "Functions", "Functions defined", "MUST"),
    CheckDef("OBJ.07", "A2L Objects", "Groups", "Group hierarchy defined", "SHOULD"),
    CheckDef("OBJ.08", "A2L Objects", "ECU Identity", "ECU part number recorded", "SHOULD"),
    CheckDef("MEM.01", "Memory Validation", "Address Bounds", "All addresses within ECU memory", "MUST"),
    CheckDef("MEM.02", "Memory Validation", "Address Overlap", "No overlapping address ranges", "MUST"),
    CheckDef("MEM.03", "Memory Validation", "Alignment", "Addresses properly aligned", "MUST"),
    CheckDef("MEM.04", "Memory Validation", "Size Consistency", "Size calculations match definitions", "MUST"),
    CheckDef("MEM.05", "Memory Validation", "Memory Footprint", "Total memory footprint calculated", "SHOULD"),
    CheckDef("CONV.01", "Conversion Methods", "Linear Parameters", "LINEAR method parameters valid", "MUST"),
    CheckDef("CONV.02", "Conversion Methods", "Formula Syntax", "FORMULA expressions well-formed", "SHOULD"),
    CheckDef("CONV.03", "Conversion Methods", "Unit Consistency", "Units consistent across methods", "MUST"),
]


def execute_checks(p: ProbedA2L) -> dict[str, CheckResult]:
    """Run all checks and return results keyed by check ID."""
    return {
        "CR.01": cr_01_structured(p),
        "CR.02": cr_02_title(p),
        "CR.03": cr_03_author_approver(p),
        "CR.04": cr_04_revision(p),
        "CR.05": cr_05_document_control(p),
        "CR.06": cr_06_characteristics_catalog(p),
        "CR.07": cr_07_measurements_catalog(p),
        "CR.08": cr_08_conversion_methods(p),
        "CR.09": cr_09_axes_defined(p),
        "CR.10": cr_10_records_defined(p),
        "CR.11": cr_11_functions_organized(p),
        "CR.12": cr_12_groups_organized(p),
        "CR.13": cr_13_memory_mapping(p),
        "CR.14": cr_14_validation_rules(p),
        "OBJ.01": obj_01_characteristic_types(p),
        "OBJ.02": obj_02_conversion_method_match(p),
        "OBJ.03": obj_03_axis_coverage(p),
        "OBJ.04": obj_04_record_completeness(p),
        "OBJ.05": obj_05_memory_allocation(p),
        "OBJ.06": obj_06_function_coverage(p),
        "OBJ.07": obj_07_group_structure(p),
        "OBJ.08": obj_08_ecu_identity(p),
        "MEM.01": mem_01_address_bounds(p),
        "MEM.02": mem_02_address_overlap(p),
        "MEM.03": mem_03_segment_alignment(p),
        "MEM.04": mem_04_size_consistency(p),
        "MEM.05": mem_05_memory_summary(p),
        "CONV.01": conv_01_linear_params(p),
        "CONV.02": conv_02_formula_syntax(p),
        "CONV.03": conv_03_unit_consistency(p),
    }
