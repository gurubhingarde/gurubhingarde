"""MBSE Requirements Allocation probing — extract metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook

@dataclass
class ProbedReqsAlloc:
    file_path: str
    sheet_names: list[str] = field(default_factory=list)
    requirement_count: int = 0
    system_req_count: int = 0
    subsystem_req_count: int = 0
    component_req_count: int = 0
    allocation_count: int = 0
    has_satisfy: bool = False
    has_derive: bool = False
    has_verify: bool = False
    title: str = ""
    author: str = ""

def probe(file_path: str) -> ProbedReqsAlloc:
    """Load xlsx and extract requirements allocation metadata."""
    p = ProbedReqsAlloc(file_path=file_path)
    wb = load_workbook(file_path, data_only=True)
    p.sheet_names = wb.sheetnames

    if "Title" in p.sheet_names:
        ws = wb["Title"]
        p.title = ws.cell(3, 2).value or ""
        p.author = ws.cell(5, 2).value or ""

    if "Requirements Catalog" in p.sheet_names:
        ws = wb["Requirements Catalog"]
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                p.requirement_count += 1
                level = row[1]
                if level == "system":
                    p.system_req_count += 1
                elif level == "subsystem":
                    p.subsystem_req_count += 1
                elif level == "component":
                    p.component_req_count += 1

    if "Allocation Matrix" in p.sheet_names:
        ws = wb["Allocation Matrix"]
        p.allocation_count = sum(1 for row in ws.iter_rows(min_row=2, values_only=True) if row[0])

    p.has_satisfy = "Satisfy Relationships" in p.sheet_names
    p.has_derive = "Derive Relationships" in p.sheet_names
    p.has_verify = "Verify Relationships" in p.sheet_names

    return p
