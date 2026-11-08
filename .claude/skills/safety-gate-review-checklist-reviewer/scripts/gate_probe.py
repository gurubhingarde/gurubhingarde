"""Probe and extract gate review data from xlsx."""

from typing import NamedTuple, List
from openpyxl import load_workbook


class ProbedGateReview(NamedTuple):
    gate_milestone: str
    project_name: str
    target_asil: str
    num_tabs: int
    has_entry_criteria: bool
    has_deliverable_inventory: bool
    has_exit_criteria: bool
    has_decision_record: bool


def probe(xlsx_path: str) -> ProbedGateReview:
    """Extract data from gate review workbook."""
    wb = load_workbook(xlsx_path)

    gate_milestone = ""
    project_name = ""
    target_asil = ""

    # Extract from title page
    if "Title Page" in wb.sheetnames:
        ws_title = wb["Title Page"]
        for row in ws_title.iter_rows(min_row=3, max_row=10, values_only=True):
            if row[0] == "Gate Milestone":
                gate_milestone = str(row[1] or "")
            elif row[0] == "Project Name":
                project_name = str(row[1] or "")
            elif row[0] == "Target ASIL":
                target_asil = str(row[1] or "")

    return ProbedGateReview(
        gate_milestone=gate_milestone,
        project_name=project_name,
        target_asil=target_asil,
        num_tabs=len(wb.sheetnames),
        has_entry_criteria="Entry Criteria Checklist" in wb.sheetnames,
        has_deliverable_inventory="Deliverable Inventory" in wb.sheetnames,
        has_exit_criteria="Exit Criteria" in wb.sheetnames,
        has_decision_record="Decision Record" in wb.sheetnames,
    )
