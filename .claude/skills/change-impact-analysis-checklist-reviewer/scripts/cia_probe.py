"""Probe CIA data from xlsx."""

from typing import NamedTuple
from openpyxl import load_workbook


class ProbedCIA(NamedTuple):
    change_id: str
    project_name: str
    num_tabs: int
    has_classification: bool
    has_affected_wps: bool
    has_reverif_scope: bool


def probe(xlsx_path: str) -> ProbedCIA:
    """Extract CIA data."""
    wb = load_workbook(xlsx_path)

    change_id = ""
    project_name = ""

    if "Title Page" in wb.sheetnames:
        ws = wb["Title Page"]
        for row in ws.iter_rows(min_row=3, max_row=8, values_only=True):
            if row[0] == "Change ID":
                change_id = str(row[1] or "")
            elif row[0] == "Project":
                project_name = str(row[1] or "")

    return ProbedCIA(
        change_id=change_id,
        project_name=project_name,
        num_tabs=len(wb.sheetnames),
        has_classification="Change Classification" in wb.sheetnames,
        has_affected_wps="Affected Work Products Matrix" in wb.sheetnames,
        has_reverif_scope="Re-verification Scope" in wb.sheetnames,
    )
