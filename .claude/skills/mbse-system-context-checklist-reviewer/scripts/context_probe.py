"""MBSE System Context probing — extract metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook

@dataclass
class ProbedContext:
    file_path: str
    sheet_names: list[str] = field(default_factory=list)
    actor_count: int = 0
    interface_count: int = 0
    use_case_count: int = 0
    scenario_count: int = 0
    stakeholder_need_count: int = 0
    has_boundary: bool = False
    title: str = ""
    author: str = ""

def probe(file_path: str) -> ProbedContext:
    """Load xlsx and extract system context metadata."""
    p = ProbedContext(file_path=file_path)
    wb = load_workbook(file_path, data_only=True)
    p.sheet_names = wb.sheetnames

    if "Title" in p.sheet_names:
        ws = wb["Title"]
        p.title = ws.cell(3, 2).value or ""
        p.author = ws.cell(5, 2).value or ""

    if "Actor Inventory" in p.sheet_names:
        ws = wb["Actor Inventory"]
        p.actor_count = sum(1 for row in ws.iter_rows(min_row=2, values_only=True) if row[0])

    if "External Interfaces" in p.sheet_names:
        ws = wb["External Interfaces"]
        p.interface_count = sum(1 for row in ws.iter_rows(min_row=2, values_only=True) if row[0])

    if "Use Case Catalog" in p.sheet_names:
        ws = wb["Use Case Catalog"]
        p.use_case_count = sum(1 for row in ws.iter_rows(min_row=2, values_only=True) if row[0])

    if "Operational Scenarios" in p.sheet_names:
        ws = wb["Operational Scenarios"]
        p.scenario_count = sum(1 for row in ws.iter_rows(min_row=2, values_only=True) if row[0])

    if "Stakeholder Needs" in p.sheet_names:
        ws = wb["Stakeholder Needs"]
        p.stakeholder_need_count = sum(1 for row in ws.iter_rows(min_row=2, values_only=True) if row[0])

    p.has_boundary = "System Boundary Definition" in p.sheet_names

    return p
