"""Probe a V&V Execution Report xlsx and extract structured data."""

from dataclasses import dataclass, field
from openpyxl import load_workbook

@dataclass
class ProbedVVR:
    title: str = "V&V Execution Report"
    doc_id: str = "VVR-001"
    revision: str = "1.0"
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    blocked: int = 0
    defects: list = field(default_factory=list)
    pass_rate: float = 0.0

def probe_vvr(xlsx_path: str) -> ProbedVVR:
    """Extract metadata from V&V Execution Report xlsx."""
    try:
        wb = load_workbook(xlsx_path, data_only=True)
    except Exception as e:
        raise ValueError(f"Cannot open {xlsx_path}: {e}")

    probed = ProbedVVR()

    # Extract test execution summary
    if "Test Execution Summary" in wb.sheetnames:
        ws = wb["Test Execution Summary"]
        for row in ws.iter_rows(min_row=4, max_row=8, min_col=1, max_col=2, values_only=True):
            if row and row[0]:
                metric = str(row[0]).lower()
                val = row[1] if len(row) > 1 and row[1] else 0
                if "executed" in metric:
                    probed.total_tests = int(val) if val else 0
                elif "passed" in metric:
                    probed.passed = int(val) if val else 0
                elif "failed" in metric:
                    probed.failed = int(val) if val else 0
                elif "blocked" in metric:
                    probed.blocked = int(val) if val else 0

    if probed.total_tests > 0:
        probed.pass_rate = (probed.passed / probed.total_tests) * 100

    # Extract defects
    if "Defect Catalog" in wb.sheetnames:
        ws = wb["Defect Catalog"]
        for row in ws.iter_rows(min_row=2, max_row=500, min_col=1, max_col=7, values_only=True):
            if row and row[0]:
                probed.defects.append({
                    "id": row[0],
                    "title": row[1] if len(row) > 1 else "",
                    "severity": row[2] if len(row) > 2 else "",
                    "status": row[3] if len(row) > 3 else ""
                })

    return probed
