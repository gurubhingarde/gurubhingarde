"""DCM calibration values probe — extract structured data from DCM workbook."""

from __future__ import annotations

from dataclasses import dataclass, field
from openpyxl import load_workbook


@dataclass
class ProbedDCM:
    title: str = ""
    author: str = ""
    approver: str = ""
    revision: str = ""
    variant: str = ""
    build_date: str = ""
    source_a2l: str = ""
    baseline_ref: str = ""
    sheet_names: list[str] = field(default_factory=list)

    scalar_count: int = 0
    curve_count: int = 0
    map_count: int = 0
    axis_point_count: int = 0
    value_block_count: int = 0

    has_document_control: bool = False
    has_dataset_identity: bool = False
    has_source_a2l: bool = False
    has_validation_rules: bool = False


def probe(workbook_path: str) -> ProbedDCM:
    wb = load_workbook(workbook_path, data_only=True)
    p = ProbedDCM(sheet_names=wb.sheetnames)

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
            elif "approver" in key:
                p.approver = str(val)
            elif "revision" in key:
                p.revision = str(val)
            elif "variant" in key:
                p.variant = str(val)
            elif "build" in key:
                p.build_date = str(val)

    p.has_document_control = "Document Control" in wb.sheetnames
    p.has_dataset_identity = "Dataset Identity" in wb.sheetnames
    p.has_source_a2l = "Source A2L Reference" in wb.sheetnames
    p.has_validation_rules = "Validation Rules" in wb.sheetnames

    if "Scalar Values" in wb.sheetnames:
        ws = wb["Scalar Values"]
        p.scalar_count = max(0, ws.max_row - 1)

    if "Curve Values" in wb.sheetnames:
        ws = wb["Curve Values"]
        p.curve_count = max(0, ws.max_row - 1)

    if "Map Values" in wb.sheetnames:
        ws = wb["Map Values"]
        p.map_count = max(0, ws.max_row - 1)

    if "Axis Point Values" in wb.sheetnames:
        ws = wb["Axis Point Values"]
        p.axis_point_count = max(0, ws.max_row - 1)

    if "Value Block" in wb.sheetnames:
        ws = wb["Value Block"]
        p.value_block_count = max(0, ws.max_row - 1)

    if "Source A2L Reference" in wb.sheetnames:
        ws = wb["Source A2L Reference"]
        for row in ws.iter_rows(min_row=3, max_row=10, min_col=1, max_col=2, values_only=True):
            if not row[0]:
                continue
            key = str(row[0]).lower()
            val = row[1] or ""
            if "file" in key:
                p.source_a2l = str(val)

    wb.close()
    return p
