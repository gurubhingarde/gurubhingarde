"""MBSE Model Architecture probing — extract structural metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook

@dataclass
class ProbedMBSE:
    file_path: str
    sheet_names: list[str] = field(default_factory=list)
    has_system_id: bool = False
    operational_scenario_count: int = 0
    system_function_count: int = 0
    logical_component_count: int = 0
    physical_component_count: int = 0
    has_traceability: bool = False
    title: str = ""
    author: str = ""

def probe(file_path: str) -> ProbedMBSE:
    """Load xlsx and extract metadata about MBSE model architecture."""
    p = ProbedMBSE(file_path=file_path)
    wb = load_workbook(file_path, data_only=True)
    p.sheet_names = wb.sheetnames

    # Check for title sheet
    if "Title" in p.sheet_names:
        ws = wb["Title"]
        p.title = ws.cell(3, 2).value or ""
        p.author = ws.cell(5, 2).value or ""

    # Count scenarios (Operational Analysis)
    if "Operational Analysis" in p.sheet_names:
        ws = wb["Operational Analysis"]
        p.operational_scenario_count = sum(1 for row in ws.iter_rows(min_row=3, values_only=True)
                                           if row[0])

    # Count functions (System Analysis)
    if "System Analysis" in p.sheet_names:
        ws = wb["System Analysis"]
        p.system_function_count = sum(1 for row in ws.iter_rows(min_row=3, values_only=True)
                                      if row[0])

    # Count logical components
    if "Logical Analysis" in p.sheet_names:
        ws = wb["Logical Analysis"]
        p.logical_component_count = sum(1 for row in ws.iter_rows(min_row=3, values_only=True)
                                        if row[0])

    # Count physical components
    if "Physical Analysis" in p.sheet_names:
        ws = wb["Physical Analysis"]
        p.physical_component_count = sum(1 for row in ws.iter_rows(min_row=3, values_only=True)
                                         if row[0])

    # Check traceability tab
    p.has_traceability = "Inter-Layer Traceability" in p.sheet_names

    return p
