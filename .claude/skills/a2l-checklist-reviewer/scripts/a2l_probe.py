"""A2L Calibration Description probe — extract structured data from A2L workbook."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openpyxl import load_workbook


@dataclass
class ProbedA2L:
    """Structured extraction from A2L workbook."""
    title: str = ""
    author: str = ""
    approver: str = ""
    revision: str = ""
    ecu_part_number: str = ""
    sheet_names: list[str] = field(default_factory=list)
    has_table_of_contents: bool = False

    # Catalog counts
    characteristic_count: int = 0
    measurement_count: int = 0
    conversion_method_count: int = 0
    axis_count: int = 0
    record_count: int = 0
    function_count: int = 0
    group_count: int = 0

    # Characteristic type breakdown
    value_count: int = 0
    curve_count: int = 0
    map_count: int = 0
    axis_pts_count: int = 0
    val_blk_count: int = 0

    # Memory info
    memory_address_count: int = 0
    total_memory_bytes: int = 0

    # Validation
    has_document_control: bool = False
    has_validation_rules: bool = False
    has_references: bool = False


def probe(workbook_path: str) -> ProbedA2L:
    """Extract A2L metadata from workbook."""
    wb = load_workbook(workbook_path, data_only=True)
    p = ProbedA2L(sheet_names=wb.sheetnames)

    # Title sheet
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
            elif "part" in key:
                p.ecu_part_number = str(val)

    # Document Control
    p.has_document_control = "Document Control" in wb.sheetnames

    # Validation Rules tab
    p.has_validation_rules = "Validation Rules" in wb.sheetnames

    # References tab
    p.has_references = "References" in wb.sheetnames

    # Characteristic Catalog
    if "Characteristic Catalog" in wb.sheetnames:
        ws = wb["Characteristic Catalog"]
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=3, max_col=3, values_only=True):
            if not row[0]:
                continue
            typ = str(row[0]).upper()
            p.characteristic_count += 1
            if "VALUE" in typ:
                p.value_count += 1
            elif "CURVE" in typ:
                p.curve_count += 1
            elif "MAP" in typ:
                p.map_count += 1
            elif "AXIS_PTS" in typ or "AXIS" in typ:
                p.axis_pts_count += 1
            elif "VAL_BLK" in typ or "BLOCK" in typ:
                p.val_blk_count += 1

    # Measurement Catalog
    if "Measurement Catalog" in wb.sheetnames:
        ws = wb["Measurement Catalog"]
        p.measurement_count = max(0, ws.max_row - 1)

    # Conversion Methods
    if "Conversion Methods" in wb.sheetnames:
        ws = wb["Conversion Methods"]
        p.conversion_method_count = max(0, ws.max_row - 1)

    # Axis Descriptions
    if "Axis Descriptions" in wb.sheetnames:
        ws = wb["Axis Descriptions"]
        p.axis_count = max(0, ws.max_row - 1)

    # Record Layouts
    if "Record Layouts" in wb.sheetnames:
        ws = wb["Record Layouts"]
        p.record_count = max(0, ws.max_row - 1)

    # Function Hierarchy
    if "Function Hierarchy" in wb.sheetnames:
        ws = wb["Function Hierarchy"]
        p.function_count = max(0, ws.max_row - 1)

    # Group Hierarchy
    if "Group Hierarchy" in wb.sheetnames:
        ws = wb["Group Hierarchy"]
        p.group_count = max(0, ws.max_row - 1)

    # Memory Address Mapping
    if "Memory Address Mapping" in wb.sheetnames:
        ws = wb["Memory Address Mapping"]
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=2, values_only=True):
            if not row[0]:
                continue
            p.memory_address_count += 1
            try:
                size = int(row[1]) if row[1] else 0
                p.total_memory_bytes += size
            except (ValueError, TypeError):
                pass

    wb.close()
    return p
