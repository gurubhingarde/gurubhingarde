"""Traceability Matrix confirmation measures per ISO 26262, ISO 21434, IEEE 1012.

Rating vocabulary: FC / LC / PC / NO / NA.

Three classes of check live here and the `finding` text says which one produced
the rating, so nothing machine-unverified is presented as a machine verdict:

  * CONTENT   - read from the probed workbook and decided against a threshold
                (TM005-TM009). These can fail.
  * STRUCTURE - the required tab exists and carries rows. Presence only; it
                does not judge the content of the tab.
  * DRAFT     - not machine-verifiable from the workbook. Rated LC and labelled
                as an auto-suggest draft for the assessor to confirm or
                overturn. Previously these were an unlabelled hard-coded LC.
"""

from dataclasses import dataclass

OVERALL_THRESHOLD = 95.0
REQUIREMENT_THRESHOLD = 100.0
TEST_THRESHOLD = 95.0

DRAFT_NOTE = ("AUTO-SUGGEST DRAFT - not machine-verified from the workbook. "
              "Assessor must confirm or overturn this rating.")


@dataclass
class CheckResult:
    rating: str
    finding: str = ""
    evidence: str = ""


CHECKS = {
    "TM001": {"measure": "All stakeholder needs traced to requirements", "category": "Coverage"},
    "TM002": {"measure": "All requirements traced to test cases", "category": "Coverage"},
    "TM003": {"measure": "Bidirectional traceability established (forward)", "category": "Traceability"},
    "TM004": {"measure": "Bidirectional traceability established (backward)", "category": "Traceability"},
    "TM005": {"measure": "No orphan requirements identified", "category": "Orphans"},
    "TM006": {"measure": "No orphan test cases identified", "category": "Orphans"},
    "TM007": {"measure": "Overall coverage >= 95%", "category": "Metrics"},
    "TM008": {"measure": "Requirement coverage >= 100%", "category": "Metrics"},
    "TM009": {"measure": "Test coverage >= 95%", "category": "Metrics"},
    "TM010": {"measure": "Trace element IDs follow convention rules", "category": "Convention"},
    "TM011": {"measure": "Need-to-requirement links documented", "category": "Links"},
    "TM012": {"measure": "Requirement-to-test links documented", "category": "Links"},
    "TM013": {"measure": "Requirement-to-design links documented", "category": "Links"},
    "TM014": {"measure": "Gap identification report completed", "category": "Analysis"},
    "TM015": {"measure": "Coverage metrics calculated and reported", "category": "Analysis"},
    "TM016": {"measure": "Orphan identification report included", "category": "Analysis"},
    "TM017": {"measure": "Trace validation rules defined", "category": "Rules"},
    "TM018": {"measure": "Convention rules documented", "category": "Rules"},
    "TM019": {"measure": "Cross-references validated for accuracy", "category": "Quality"},
    "TM020": {"measure": "Trace quality metrics >= acceptance criteria", "category": "Quality"},
    "TM021": {"measure": "Design-to-code traceability established", "category": "Links"},
    "TM022": {"measure": "System/subsystem requirement levels properly allocated", "category": "Structure"},
    "TM023": {"measure": "Cybersecurity requirements traced (ISO 21434)", "category": "Links"},
    "TM024": {"measure": "Document control and version management clear", "category": "Control"},
    "TM025": {"measure": "Traceability report ready for audit/certification", "category": "Readiness"},
}

# check id -> tab that must be present for the structural check to pass
STRUCTURE_TABS = {
    "TM003": "Forward Traceability",
    "TM004": "Backward Traceability",
    "TM014": "Gap Identification",
    "TM016": "Coverage Analysis",
    "TM017": "Validation Rules",
    "TM018": "Trace Convention Rules",
    "TM024": "Document Control",
}


def _ids(orphans):
    return ", ".join(str(o.get("id", "")) for o in orphans if o.get("id"))


def evaluate_trace_matrix(probed) -> dict:
    """Evaluate Traceability Matrix against checks."""
    results = {}

    elements = getattr(probed, "elements", []) or []
    metrics = getattr(probed, "metrics", {}) or {}
    sheetnames = getattr(probed, "sheetnames", []) or []
    orphan_reqs = getattr(probed, "orphan_reqs", []) or []
    orphan_tests = getattr(probed, "orphan_tests", []) or []

    catalog_empty = not elements

    def metric_check(key, threshold, label):
        """Rate a coverage metric. Absent metric is NA, never FC."""
        if key not in metrics:
            return ("NA",
                    f"{label} is not reported on the Coverage Analysis tab; check not assessable.",
                    "CONTENT - metric absent")
        value = metrics[key]
        if value >= threshold:
            return ("FC", "", f"CONTENT - {label} = {value}% (threshold {threshold}%)")
        return ("NO",
                f"{label} is {value}%, below the required {threshold}%.",
                f"CONTENT - {label} = {value}%")

    for check_id in CHECKS:
        rating, finding, evidence = "LC", DRAFT_NOTE, "DRAFT"

        if check_id == "TM005":
            if catalog_empty:
                rating, finding, evidence = (
                    "NA",
                    "Trace Source Catalog is empty; orphan analysis is not assessable. "
                    "Absence of listed orphans is not evidence that none exist.",
                    "CONTENT - catalog empty",
                )
            elif orphan_reqs:
                rating, finding, evidence = (
                    "NO",
                    f"{len(orphan_reqs)} orphan requirement(s) on the Coverage Analysis tab: "
                    f"{_ids(orphan_reqs)}.",
                    f"CONTENT - {len(orphan_reqs)} orphan requirement rows",
                )
            else:
                rating, finding, evidence = ("FC", "", "CONTENT - no orphan requirement rows")

        elif check_id == "TM006":
            if catalog_empty:
                rating, finding, evidence = (
                    "NA",
                    "Trace Source Catalog is empty; orphan test analysis is not assessable.",
                    "CONTENT - catalog empty",
                )
            elif orphan_tests:
                rating, finding, evidence = (
                    "NO",
                    f"{len(orphan_tests)} orphan test case(s) on the Coverage Analysis tab: "
                    f"{_ids(orphan_tests)}.",
                    f"CONTENT - {len(orphan_tests)} orphan test rows",
                )
            else:
                rating, finding, evidence = ("FC", "", "CONTENT - no orphan test rows")

        elif check_id == "TM007":
            rating, finding, evidence = metric_check(
                "overall_coverage", OVERALL_THRESHOLD, "Overall coverage")

        elif check_id == "TM008":
            rating, finding, evidence = metric_check(
                "requirement_coverage", REQUIREMENT_THRESHOLD, "Requirement coverage")

        elif check_id == "TM009":
            rating, finding, evidence = metric_check(
                "test_coverage", TEST_THRESHOLD, "Test coverage")

        elif check_id in STRUCTURE_TABS:
            tab = STRUCTURE_TABS[check_id]
            if tab in sheetnames:
                rating, finding, evidence = (
                    "LC",
                    f"'{tab}' tab is present. Presence verified; content not machine-assessed.",
                    f"STRUCTURE - tab '{tab}' present",
                )
            else:
                rating, finding, evidence = (
                    "NO",
                    f"Required tab '{tab}' is absent from the workbook.",
                    f"STRUCTURE - tab '{tab}' absent",
                )

        results[check_id] = {
            "rating": rating,
            "finding": finding,
            "evidence": evidence,
        }

    return results
