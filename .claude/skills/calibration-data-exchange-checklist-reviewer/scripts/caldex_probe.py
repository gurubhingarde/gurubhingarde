"""Calibration Data Exchange probe — extract data from agreement workbook."""

from __future__ import annotations

from dataclasses import dataclass, field
from openpyxl import load_workbook


@dataclass
class ProbedCALDEX:
    title: str = ""
    author: str = ""
    revision: str = ""
    sheet_names: list[str] = field(default_factory=list)

    parties_count: int = 0
    ownership_count: int = 0
    baseline_count: int = 0
    format_count: int = 0
    criteria_count: int = 0

    has_document_control: bool = False
    has_change_protocol: bool = False
    has_version_control: bool = False
    has_signoff: bool = False


def probe(workbook_path: str) -> ProbedCALDEX:
    wb = load_workbook(workbook_path, data_only=True)
    p = ProbedCALDEX(sheet_names=wb.sheetnames)

    if "Title" in wb.sheetnames:
        ws = wb["Title"]
        for row in ws.iter_rows(min_row=2, max_row=20, min_col=1, max_col=2, values_only=True):
            if not row[0]:
                continue
            key = str(row[0]).lower()
            val = row[1] or ""
            if "name" in key:
                p.title = str(val)
            elif "author" in key:
                p.author = str(val)
            elif "revision" in key:
                p.revision = str(val)

    p.has_document_control = "Document Control" in wb.sheetnames
    p.has_change_protocol = "Change Protocol" in wb.sheetnames
    p.has_version_control = "Version Control" in wb.sheetnames
    p.has_signoff = "Signoff Block" in wb.sheetnames

    if "Parties" in wb.sheetnames:
        ws = wb["Parties"]
        p.parties_count = max(0, ws.max_row - 3)

    if "Parameter Ownership Matrix" in wb.sheetnames:
        ws = wb["Parameter Ownership Matrix"]
        p.ownership_count = max(0, ws.max_row - 1)

    if "Baseline References" in wb.sheetnames:
        ws = wb["Baseline References"]
        p.baseline_count = max(0, ws.max_row - 1)

    if "Exchange Format Specification" in wb.sheetnames:
        ws = wb["Exchange Format Specification"]
        p.format_count = max(0, ws.max_row - 1)

    if "Acceptance Criteria" in wb.sheetnames:
        ws = wb["Acceptance Criteria"]
        p.criteria_count = max(0, ws.max_row - 1)

    wb.close()
    return p
