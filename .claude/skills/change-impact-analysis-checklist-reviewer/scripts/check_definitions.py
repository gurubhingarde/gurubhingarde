"""Check definitions for change impact analysis audit."""

from enum import Enum


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    NA = "N/A"


CHECKS = [
    {"id": "CIA-C01", "name": "Change ID unique and valid", "category": "Structure"},
    {"id": "CIA-C02", "name": "Change title clear and descriptive", "category": "Clarity"},
    {"id": "CIA-C03", "name": "Requesting party identified", "category": "Accountability"},
    {"id": "CIA-C04", "name": "Request date recorded", "category": "Control"},
    {"id": "CIA-C05", "name": "Change description complete", "category": "Completeness"},
    {"id": "CIA-C06", "name": "Change classification assigned", "category": "Classification"},
    {"id": "CIA-C07", "name": "Classification justification documented", "category": "Justification"},
    {"id": "CIA-C08", "name": "All potentially affected WPs identified", "category": "Completeness"},
    {"id": "CIA-C09", "name": "Impact type assigned to each WP", "category": "Data Quality"},
    {"id": "CIA-C10", "name": "Impact description specific", "category": "Clarity"},
    {"id": "CIA-C11", "name": "Original ASIL assigned", "category": "Consistency"},
    {"id": "CIA-C12", "name": "Modified ASIL assigned", "category": "Analysis"},
    {"id": "CIA-C13", "name": "ASIL impact justification documented", "category": "Justification"},
    {"id": "CIA-C14", "name": "No unjustified ASIL increases", "category": "Rigor"},
    {"id": "CIA-C15", "name": "Re-verification activities defined", "category": "Planning"},
    {"id": "CIA-C16", "name": "Re-verification scope measurable", "category": "Methodology"},
    {"id": "CIA-C17", "name": "Re-verification owner assigned", "category": "Accountability"},
    {"id": "CIA-C18", "name": "Re-verification target date assigned", "category": "Schedule"},
    {"id": "CIA-C19", "name": "Re-validation activities defined", "category": "Planning"},
    {"id": "CIA-C20", "name": "Re-validation scope clear", "category": "Clarity"},
    {"id": "CIA-C21", "name": "Re-validation owner assigned", "category": "Accountability"},
    {"id": "CIA-C22", "name": "Re-validation target date assigned", "category": "Schedule"},
    {"id": "CIA-C23", "name": "Safety Manager approval with signature", "category": "Authority"},
    {"id": "CIA-C24", "name": "Change Board approval captured", "category": "Authority"},
    {"id": "CIA-C25", "name": "Conditional approvals documented", "category": "Control"},
]
