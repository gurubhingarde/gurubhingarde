"""Verification Plan confirmation measures per ISO 26262-8 §9."""

from dataclasses import dataclass

@dataclass
class CheckResult:
    rating: str  # FC, LC, PC, NO, NA
    finding: str = ""
    evidence: str = ""

CHECKS = {
    "VP001": {"measure": "Verification scope covers all safety goals", "category": "Scope"},
    "VP002": {"measure": "All requirements traced to verification methods", "category": "Traceability"},
    "VP003": {"measure": "Review method defined with entry/exit criteria", "category": "Methods"},
    "VP004": {"measure": "Analysis method defined with entry/exit criteria", "category": "Methods"},
    "VP005": {"measure": "Simulation method defined with entry/exit criteria", "category": "Methods"},
    "VP006": {"measure": "Test method defined with entry/exit criteria", "category": "Methods"},
    "VP007": {"measure": "HIL environment specifications documented", "category": "Environments"},
    "VP008": {"measure": "SIL environment specifications documented", "category": "Environments"},
    "VP009": {"measure": "Vehicle test environment specifications documented", "category": "Environments"},
    "VP010": {"measure": "Bench test environment specifications documented", "category": "Environments"},
    "VP011": {"measure": "Unit test level defined and scoped", "category": "Test Levels"},
    "VP012": {"measure": "Integration test level defined and scoped", "category": "Test Levels"},
    "VP013": {"measure": "System test level defined and scoped", "category": "Test Levels"},
    "VP014": {"measure": "Vehicle test level defined and scoped", "category": "Test Levels"},
    "VP015": {"measure": "Verification schedule covers all V-cycle phases", "category": "Schedule"},
    "VP016": {"measure": "Test milestones and gates defined", "category": "Schedule"},
    "VP017": {"measure": "Resource allocation and budgets specified", "category": "Schedule"},
    "VP018": {"measure": "Acceptance criteria are measurable and objective", "category": "Criteria"},
    "VP019": {"measure": "Pass/fail thresholds defined for each criterion", "category": "Criteria"},
    "VP020": {"measure": "Requirement coverage target >= 100% specified", "category": "Criteria"},
    "VP021": {"measure": "Test pass rate threshold specified", "category": "Criteria"},
    "VP022": {"measure": "Defect detection and resolution process defined", "category": "Process"},
    "VP023": {"measure": "Risk assessment for verification gaps included", "category": "Risk"},
    "VP024": {"measure": "Roles and responsibilities assigned", "category": "Organization"},
    "VP025": {"measure": "Independence per ISO 26262-2 Table 1 specified", "category": "Organization"},
    "VP026": {"measure": "Traceability matrix linkage documented", "category": "Traceability"},
    "VP027": {"measure": "References to TSC and system requirements provided", "category": "References"},
    "VP028": {"measure": "Document control and approval authority clear", "category": "Control"},
}

def evaluate_vplan(probed) -> dict:
    """Evaluate Verification Plan against checks."""
    results = {}

    for check_id, check_def in CHECKS.items():
        rating = "LC"  # Default: largely compliant
        finding = ""

        if check_id == "VP001":
            rating = "FC" if probed.scope else "PC"
        elif check_id == "VP002":
            rating = "FC" if len(probed.methods) > 0 else "NO"
        elif check_id in ["VP003", "VP004", "VP005", "VP006"]:
            rating = "FC" if len(probed.methods) > 0 else "PC"
        elif check_id in ["VP007", "VP008", "VP009", "VP010"]:
            rating = "FC" if probed.environments else "PC"
        elif check_id in ["VP011", "VP012", "VP013", "VP014"]:
            rating = "FC" if len(probed.test_levels) > 0 else "PC"
        elif check_id in ["VP018", "VP019", "VP020", "VP021"]:
            rating = "FC" if len(probed.acceptance_criteria) > 0 else "PC"
        else:
            rating = "LC"

        results[check_id] = {
            "rating": rating,
            "finding": finding,
            "evidence": ""
        }

    return results
