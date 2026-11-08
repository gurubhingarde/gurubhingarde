"""Check definitions for lessons learned register audit."""

from enum import Enum


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    NA = "N/A"


CHECKS = [
    {"id": "LL-C01", "name": "Lesson ID unique", "category": "Structure"},
    {"id": "LL-C02", "name": "Lesson source identified", "category": "Completeness"},
    {"id": "LL-C03", "name": "Lesson summary clear and concise", "category": "Clarity"},
    {"id": "LL-C04", "name": "Root cause analysis documented", "category": "Analysis"},
    {"id": "LL-C05", "name": "Root cause is actionable and specific", "category": "Rigor"},
    {"id": "LL-C06", "name": "Corrective action defined", "category": "Completeness"},
    {"id": "LL-C07", "name": "Corrective action is specific and measurable", "category": "Rigor"},
    {"id": "LL-C08", "name": "Corrective action owner assigned", "category": "Accountability"},
    {"id": "LL-C09", "name": "Corrective action has target completion date", "category": "Schedule"},
    {"id": "LL-C10", "name": "Best practice recommended", "category": "Learning"},
    {"id": "LL-C11", "name": "Best practice is generalizable", "category": "Applicability"},
    {"id": "LL-C12", "name": "Applicability scope defined", "category": "Clarity"},
    {"id": "LL-C13", "name": "Distribution target identified", "category": "Communication"},
    {"id": "LL-C14", "name": "Distribution delivery method specified", "category": "Planning"},
    {"id": "LL-C15", "name": "Distribution target completion date assigned", "category": "Schedule"},
    {"id": "LL-C16", "name": "Application tracker populated", "category": "Completeness"},
    {"id": "LL-C17", "name": "Application context documented", "category": "Clarity"},
    {"id": "LL-C18", "name": "Application date recorded", "category": "Control"},
    {"id": "LL-C19", "name": "Effectiveness assessment documented", "category": "Review"},
    {"id": "LL-C20", "name": "Effectiveness assessment is quantitative if possible", "category": "Rigor"},
    {"id": "LL-C21", "name": "High-impact lessons tracked across organization", "category": "Learning"},
    {"id": "LL-C22", "name": "Lessons are categorized", "category": "Organization"},
    {"id": "LL-C23", "name": "Trend analysis populated", "category": "Analysis"},
    {"id": "LL-C24", "name": "Effectiveness review schedule established", "category": "Planning"},
    {"id": "LL-C25", "name": "Document control revision history present", "category": "Control"},
]
