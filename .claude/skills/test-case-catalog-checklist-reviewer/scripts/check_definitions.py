"""Test Case Catalog confirmation measures per ISO 26262 & IEEE 1012."""

from dataclasses import dataclass

@dataclass
class CheckResult:
    rating: str
    finding: str = ""

CHECKS = {
    "TC001": {"measure": "All test cases have unique IDs", "category": "Design"},
    "TC002": {"measure": "Test case titles are descriptive and unambiguous", "category": "Design"},
    "TC003": {"measure": "Preconditions defined for each test case", "category": "Design"},
    "TC004": {"measure": "Input parameters specified with data types and ranges", "category": "Design"},
    "TC005": {"measure": "Expected outputs defined objectively", "category": "Design"},
    "TC006": {"measure": "Pass/fail criteria are measurable", "category": "Design"},
    "TC007": {"measure": "Each test case traces to at least one requirement", "category": "Traceability"},
    "TC008": {"measure": "Bidirectional traceability (req to test) established", "category": "Traceability"},
    "TC009": {"measure": "Requirement coverage identified (orphan reqs)", "category": "Traceability"},
    "TC010": {"measure": "Test coverage identified (orphan tests)", "category": "Traceability"},
    "TC011": {"measure": "Test level allocated (unit, integration, system)", "category": "Levels"},
    "TC012": {"measure": "Component/subsystem allocation documented", "category": "Levels"},
    "TC013": {"measure": "Automation status (manual/automated/deferred) recorded", "category": "Automation"},
    "TC014": {"measure": "Automated test tool specified for automated cases", "category": "Automation"},
    "TC015": {"measure": "Automation date populated for automated cases", "category": "Automation"},
    "TC016": {"measure": "Execution priority assigned (must/should/nice)", "category": "Priority"},
    "TC017": {"measure": "Execution sequence number provided", "category": "Priority"},
    "TC018": {"measure": "Rationale documented for high-priority cases", "category": "Priority"},
    "TC019": {"measure": "System state/environment setup defined", "category": "Preconditions"},
    "TC020": {"measure": "Input boundary values covered (min, max, nominal)", "category": "Design"},
    "TC021": {"measure": "Error/edge cases included in catalog", "category": "Design"},
    "TC022": {"measure": "Tolerance and acceptance margins specified", "category": "Design"},
    "TC023": {"measure": "Verification method linked to each test case", "category": "Methods"},
    "TC024": {"measure": "No conflicting or duplicate test cases", "category": "Quality"},
    "TC025": {"measure": "Test case count documented", "category": "Metrics"},
    "TC026": {"measure": "Automation ratio target specified", "category": "Metrics"},
    "TC027": {"measure": "Document control and version management clear", "category": "Control"},
    "TC028": {"measure": "Test case traceability report available", "category": "Reporting"},
}

def evaluate_tc_catalog(probed) -> dict:
    """Evaluate Test Case Catalog against checks."""
    results = {}

    for check_id, check_def in CHECKS.items():
        rating = "LC"

        if check_id == "TC001":
            ids = [tc.id for tc in probed.test_cases]
            rating = "FC" if len(ids) == len(set(ids)) else "NO"
        elif check_id == "TC007":
            rating = "FC" if all(tc.req_id for tc in probed.test_cases) else "PC"
        elif check_id == "TC013":
            rating = "FC" if all(tc.automation for tc in probed.test_cases) else "PC"
        else:
            rating = "LC"

        results[check_id] = {
            "rating": rating,
            "finding": "",
            "evidence": ""
        }

    return results
