"""Check definitions for safety gate review audit."""

from enum import Enum


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    NA = "N/A"


CHECKS = [
    {"id": "GR-C01", "name": "Gate milestone identified and valid", "category": "Structure"},
    {"id": "GR-C02", "name": "Target ASIL assigned and consistent", "category": "Consistency"},
    {"id": "GR-C03", "name": "Gate scope clearly defined", "category": "Structure"},
    {"id": "GR-C04", "name": "Predecessor gate referenced", "category": "Traceability"},
    {"id": "GR-C05", "name": "Entry criteria checklist complete", "category": "Completeness"},
    {"id": "GR-C06", "name": "Entry criteria satisfied status recorded", "category": "Data Quality"},
    {"id": "GR-C07", "name": "Entry criteria evidence documented", "category": "Evidence"},
    {"id": "GR-C08", "name": "Entry criteria reviewers assigned", "category": "Accountability"},
    {"id": "GR-C09", "name": "All entry criteria evidenced with sign-off", "category": "Authority"},
    {"id": "GR-C10", "name": "Deliverable inventory complete per Safety Plan", "category": "Completeness"},
    {"id": "GR-C11", "name": "All required work products listed", "category": "Completeness"},
    {"id": "GR-C12", "name": "All deliverables marked present/absent", "category": "Data Quality"},
    {"id": "GR-C13", "name": "Deliverable quality status assigned", "category": "Data Quality"},
    {"id": "GR-C14", "name": "Deliverable owners identified", "category": "Accountability"},
    {"id": "GR-C15", "name": "Exit criteria defined per phase", "category": "Completeness"},
    {"id": "GR-C16", "name": "Exit criteria measurable", "category": "Methodology"},
    {"id": "GR-C17", "name": "Exit criteria met status documented", "category": "Data Quality"},
    {"id": "GR-C18", "name": "Exit criteria evidence provided", "category": "Evidence"},
    {"id": "GR-C19", "name": "Action items from gate recorded", "category": "Completeness"},
    {"id": "GR-C20", "name": "Action items have owner and due date", "category": "Accountability"},
    {"id": "GR-C21", "name": "High-priority action items identified", "category": "Risk Management"},
    {"id": "GR-C22", "name": "Open risks linked and acknowledged", "category": "Risk Management"},
    {"id": "GR-C23", "name": "Gate decision recorded", "category": "Authority"},
    {"id": "GR-C24", "name": "Gate decision rationale documented", "category": "Evidence"},
    {"id": "GR-C25", "name": "Gate chair and attendees signatures captured", "category": "Authority"},
]
