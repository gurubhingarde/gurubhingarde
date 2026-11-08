"""Check definitions for work product status rollup audit."""

from enum import Enum


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    NA = "N/A"


CHECKS = [
    {"id": "WP-C01", "name": "Every WP ID unique", "category": "Structure"},
    {"id": "WP-C02", "name": "Every WP has name assigned", "category": "Completeness"},
    {"id": "WP-C03", "name": "Every WP has owner assigned", "category": "Accountability"},
    {"id": "WP-C04", "name": "Every WP has due date assigned", "category": "Schedule"},
    {"id": "WP-C05", "name": "Every WP has ASIL assigned", "category": "Consistency"},
    {"id": "WP-C06", "name": "Percent complete values 0-100", "category": "Data Quality"},
    {"id": "WP-C07", "name": "Percent complete trending upward", "category": "Trending"},
    {"id": "WP-C08", "name": "Early completion marked correctly", "category": "Data Quality"},
    {"id": "WP-C09", "name": "Late WPs flagged with blocker", "category": "Risk Management"},
    {"id": "WP-C10", "name": "Dependencies form valid DAG", "category": "Methodology"},
    {"id": "WP-C11", "name": "Predecessor WPs identified", "category": "Completeness"},
    {"id": "WP-C12", "name": "Successor WPs identified", "category": "Completeness"},
    {"id": "WP-C13", "name": "Critical path WPs identified", "category": "Analysis"},
    {"id": "WP-C14", "name": "Zero-slack items have accelerated review", "category": "Risk Management"},
    {"id": "WP-C15", "name": "Phase inventory WP counts match rollup", "category": "Consistency"},
    {"id": "WP-C16", "name": "Aggregate percent complete formula correct", "category": "Methodology"},
    {"id": "WP-C17", "name": "Burndown trend populated", "category": "Trending"},
    {"id": "WP-C18", "name": "Risk linkage tab references open risks", "category": "Traceability"},
    {"id": "WP-C19", "name": "Risk-affected WPs have escalation flag", "category": "Risk Management"},
    {"id": "WP-C20", "name": "All phase milestones have scheduled reviews", "category": "Schedule"},
    {"id": "WP-C21", "name": "Incomplete WPs have mitigation plans", "category": "Risk Management"},
    {"id": "WP-C22", "name": "Blocker status consistency with risk register", "category": "Consistency"},
    {"id": "WP-C23", "name": "Owner assignments match project roster", "category": "Accountability"},
    {"id": "WP-C24", "name": "Dependencies properly sequenced", "category": "Methodology"},
    {"id": "WP-C25", "name": "Document control revision history present", "category": "Control"},
]
