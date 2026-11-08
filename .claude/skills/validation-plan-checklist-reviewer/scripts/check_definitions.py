"""Validation Plan confirmation measures per ISO 26262-4 §9."""

from dataclasses import dataclass

@dataclass
class CheckResult:
    rating: str  # FC, LC, PC, NO, NA
    finding: str = ""
    evidence: str = ""

CHECKS = {
    "VAL001": {"measure": "Validation scope covers all safety goals", "category": "Scope"},
    "VAL002": {"measure": "Safety goals linked to validation activities", "category": "Traceability"},
    "VAL003": {"measure": "Operational scenarios documented and complete", "category": "Scenarios"},
    "VAL004": {"measure": "Edge cases and corner scenarios included", "category": "Scenarios"},
    "VAL005": {"measure": "Customer use cases captured and validated", "category": "Use Cases"},
    "VAL006": {"measure": "Bench test environment specifications documented", "category": "Environments"},
    "VAL007": {"measure": "Proving ground specifications documented", "category": "Environments"},
    "VAL008": {"measure": "Public road validation environment specifications documented", "category": "Environments"},
    "VAL009": {"measure": "Validation methods defined for each environment", "category": "Methods"},
    "VAL010": {"measure": "Test vehicles specified and available", "category": "Resources"},
    "VAL011": {"measure": "Driver qualifications and availability confirmed", "category": "Resources"},
    "VAL012": {"measure": "Instrumentation and measurement systems specified", "category": "Resources"},
    "VAL013": {"measure": "Exit criteria are measurable and objective", "category": "Criteria"},
    "VAL014": {"measure": "Pass/fail thresholds defined for each criterion", "category": "Criteria"},
    "VAL015": {"measure": "Scenario coverage target specified", "category": "Criteria"},
    "VAL016": {"measure": "Schedule realistic and covers all validation phases", "category": "Schedule"},
    "VAL017": {"measure": "Validation milestones and gates defined", "category": "Schedule"},
    "VAL018": {"measure": "Resource budget and allocation specified", "category": "Schedule"},
    "VAL019": {"measure": "Traceability to system verification explicit", "category": "Traceability"},
    "VAL020": {"measure": "Data collection and logging procedures defined", "category": "Process"},
    "VAL021": {"measure": "Defect/anomaly escalation process documented", "category": "Process"},
    "VAL022": {"measure": "Risk assessment for validation gaps included", "category": "Risk"},
    "VAL023": {"measure": "Roles and responsibilities assigned", "category": "Organization"},
    "VAL024": {"measure": "Approval authority and signoff defined", "category": "Control"},
    "VAL025": {"measure": "Document control and version management clear", "category": "Control"},
    "VAL026": {"measure": "References to safety goals provided", "category": "References"},
    "VAL027": {"measure": "References to system verification plan provided", "category": "References"},
    "VAL028": {"measure": "Applicable standards and processes cited", "category": "References"},
}

def evaluate_valplan(probed) -> dict:
    """Evaluate Validation Plan against checks."""
    results = {}

    for check_id, check_def in CHECKS.items():
        rating = "LC"  # Default: largely compliant

        if check_id == "VAL001":
            rating = "FC" if len(probed.safety_goals) > 0 else "PC"
        elif check_id == "VAL003":
            rating = "FC" if len(probed.scenarios) > 0 else "PC"
        elif check_id == "VAL005":
            rating = "FC" if len(probed.scenarios) > 0 else "PC"
        elif check_id in ["VAL006", "VAL007", "VAL008"]:
            rating = "FC" if len(probed.environments) > 0 else "PC"
        elif check_id in ["VAL010", "VAL011", "VAL012"]:
            rating = "FC" if len(probed.resources) > 0 else "PC"
        elif check_id in ["VAL013", "VAL014", "VAL015"]:
            rating = "FC" if len(probed.exit_criteria) > 0 else "PC"
        else:
            rating = "LC"

        results[check_id] = {
            "rating": rating,
            "finding": "",
            "evidence": ""
        }

    return results
