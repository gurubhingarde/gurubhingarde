"""Probe a Test Case Catalog xlsx and extract structured data."""

from dataclasses import dataclass, field
from openpyxl import load_workbook

@dataclass
class TestCase:
    id: str = ""
    title: str = ""
    precondition: str = ""
    req_id: str = ""
    pass_criterion: str = ""
    automation: str = "Manual"

@dataclass
class ProbedTCCatalog:
    title: str = "Test Case Catalog"
    doc_id: str = "TC-001"
    revision: str = "1.0"
    test_cases: list[TestCase] = field(default_factory=list)

def probe_tc_catalog(xlsx_path: str) -> ProbedTCCatalog:
    """Extract metadata from Test Case Catalog xlsx."""
    try:
        wb = load_workbook(xlsx_path, data_only=True)
    except Exception as e:
        raise ValueError(f"Cannot open {xlsx_path}: {e}")

    probed = ProbedTCCatalog()

    # Extract test cases
    if "Test Case Inventory" in wb.sheetnames:
        ws = wb["Test Case Inventory"]
        for row in ws.iter_rows(min_row=2, max_row=500, min_col=1, max_col=4, values_only=True):
            if row and row[0]:
                probed.test_cases.append(TestCase(
                    id=str(row[0]) if row[0] else "",
                    title=str(row[1]) if len(row) > 1 and row[1] else "",
                ))

    return probed
