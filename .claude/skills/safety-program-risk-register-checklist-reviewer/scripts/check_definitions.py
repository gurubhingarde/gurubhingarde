"""Check definitions for safety program risk register audit."""

from enum import Enum
from typing import NamedTuple


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    NA = "N/A"


class CheckResult(NamedTuple):
    check_id: str
    check_name: str
    status: CheckStatus
    details: str
    evidence: str = ""


CHECKS = [
    {"id": "RR-C01", "name": "Risk ID uniqueness", "category": "Structure"},
    {"id": "RR-C02", "name": "Category assigned to all risks", "category": "Data Quality"},
    {"id": "RR-C03", "name": "Description non-empty and >10 chars", "category": "Data Quality"},
    {"id": "RR-C04", "name": "Likelihood values in range 1-5", "category": "Methodology"},
    {"id": "RR-C05", "name": "Impact values in range 1-5", "category": "Methodology"},
    {"id": "RR-C06", "name": "Risk score formula present", "category": "Methodology"},
    {"id": "RR-C07", "name": "Risk score calculation correct", "category": "Methodology"},
    {"id": "RR-C08", "name": "Owner assigned to all risks", "category": "Accountability"},
    {"id": "RR-C09", "name": "Owner field valid", "category": "Accountability"},
    {"id": "RR-C10", "name": "Status field populated", "category": "Data Quality"},
    {"id": "RR-C11", "name": "Target date future-dated or N/A", "category": "Schedule"},
    {"id": "RR-C12", "name": "Mitigation exists for open risks", "category": "Mitigation"},
    {"id": "RR-C13", "name": "Mitigation actions are specific", "category": "Mitigation"},
    {"id": "RR-C14", "name": "Mitigation owner assigned", "category": "Accountability"},
    {"id": "RR-C15", "name": "Contingency plan for high-risk items", "category": "Contingency"},
    {"id": "RR-C16", "name": "Contingency trigger criteria defined", "category": "Contingency"},
    {"id": "RR-C17", "name": "Escalation log populated", "category": "Escalation"},
    {"id": "RR-C18", "name": "Escalation reason documented", "category": "Escalation"},
    {"id": "RR-C19", "name": "Escalation authority recorded", "category": "Escalation"},
    {"id": "RR-C20", "name": "No duplicate risk descriptions", "category": "Quality"},
    {"id": "RR-C21", "name": "Risk category distribution appropriate", "category": "Quality"},
    {"id": "RR-C22", "name": "High-risk items have review schedule", "category": "Schedule"},
    {"id": "RR-C23", "name": "Trend analysis tab present with data", "category": "Trending"},
    {"id": "RR-C24", "name": "References section complete", "category": "Compliance"},
    {"id": "RR-C25", "name": "Document control history present", "category": "Control"},
]


def get_check_by_id(check_id: str):
    for check in CHECKS:
        if check["id"] == check_id:
            return check
    return None
