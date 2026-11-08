"""Probe LL data from xlsx."""

from typing import NamedTuple
from openpyxl import load_workbook


class ProbedLL(NamedTuple):
    project_name: str
    num_tabs: int
    has_lesson_catalog: bool
    has_distribution: bool
    has_application_tracker: bool


def probe(xlsx_path: str) -> ProbedLL:
    """Extract LL data."""
    wb = load_workbook(xlsx_path)

    project_name = ""

    if "Title Page" in wb.sheetnames:
        ws = wb["Title Page"]
        for row in ws.iter_rows(min_row=3, max_row=8, values_only=True):
            if row[0] == "Project Name":
                project_name = str(row[1] or "")

    return ProbedLL(
        project_name=project_name,
        num_tabs=len(wb.sheetnames),
        has_lesson_catalog="Lesson Catalog" in wb.sheetnames,
        has_distribution="Distribution Plan" in wb.sheetnames,
        has_application_tracker="Application Tracker" in wb.sheetnames,
    )
