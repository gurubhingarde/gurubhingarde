"""Probe WP status rollup data from xlsx."""

from typing import NamedTuple
from openpyxl import load_workbook


class ProbedWPStatus(NamedTuple):
    project_name: str
    reporting_period: str
    num_tabs: int
    has_wp_rollup: bool
    has_critical_path: bool
    has_dependency_map: bool
    has_burndown: bool


def probe(xlsx_path: str) -> ProbedWPStatus:
    """Extract data from WP status rollup workbook."""
    wb = load_workbook(xlsx_path)

    project_name = ""
    reporting_period = ""

    if "Title Page" in wb.sheetnames:
        ws = wb["Title Page"]
        for row in ws.iter_rows(min_row=3, max_row=10, values_only=True):
            if row[0] == "Project Name":
                project_name = str(row[1] or "")
            elif row[0] == "Reporting Period":
                reporting_period = str(row[1] or "")

    return ProbedWPStatus(
        project_name=project_name,
        reporting_period=reporting_period,
        num_tabs=len(wb.sheetnames),
        has_wp_rollup="Work Product Roll-up" in wb.sheetnames,
        has_critical_path="Critical Path WPs" in wb.sheetnames,
        has_dependency_map="Dependency Map" in wb.sheetnames,
        has_burndown="Burndown Trend" in wb.sheetnames,
    )
