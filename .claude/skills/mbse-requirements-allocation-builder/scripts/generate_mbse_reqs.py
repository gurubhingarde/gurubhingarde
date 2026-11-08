"""MBSE Requirements Allocation Builder — generates 11-tab workbook."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def style_title(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28

def build_title(wb, data):
    ws = wb.create_sheet("Title", 0)
    style_title(ws, 2, 5, "MBSE Requirements Allocation Matrix")
    system_name = data.get("system", {}).get("name", "System")
    style_title(ws, 3, 5, system_name)
    ws.cell(row=5, column=1, value="Created:").font = Font(bold=True)
    ws.cell(row=5, column=2, value=str(date.today()))

def build_catalog(wb, data):
    ws = wb.create_sheet("Requirements Catalog")
    ws.cell(row=1, column=1, value="Req ID").font = Font(bold=True)
    ws.cell(row=1, column=2, value="Level").font = Font(bold=True)
    ws.cell(row=1, column=3, value="Parent").font = Font(bold=True)
    ws.cell(row=1, column=4, value="Requirement Text").font = Font(bold=True)
    ws.cell(row=1, column=5, value="Priority").font = Font(bold=True)
    row = 2
    for req in data.get("requirements", []):
        ws.cell(row=row, column=1, value=req.get("id", ""))
        ws.cell(row=row, column=2, value=req.get("level", ""))
        ws.cell(row=row, column=3, value=req.get("parent", ""))
        ws.cell(row=row, column=4, value=req.get("text", ""))
        ws.cell(row=row, column=5, value=req.get("priority", "High"))
        row += 1

def build_allocation(wb, data):
    ws = wb.create_sheet("Allocation Matrix")
    ws.cell(row=1, column=1, value="Req ID").font = Font(bold=True)
    ws.cell(row=1, column=2, value="Allocated To").font = Font(bold=True)
    ws.cell(row=1, column=3, value="Allocation Type").font = Font(bold=True)
    row = 2
    for alloc in data.get("allocations", []):
        ws.cell(row=row, column=1, value=alloc.get("req_id", ""))
        ws.cell(row=row, column=2, value=alloc.get("target", ""))
        ws.cell(row=row, column=3, value=alloc.get("type", "realize"))
        row += 1

def build_skeleton(wb):
    """Add stub tabs for satisfaction, derivation, verification, etc."""
    for sheet_name in ["Decomposition Tree", "Satisfy Relationships", "Derive Relationships",
                       "Verify Relationships", "Coverage Analysis", "Validation Rules", "References",
                       "Document Control"]:
        ws = wb.create_sheet(sheet_name)
        ws.cell(row=1, column=1, value=f"{sheet_name} (Placeholder)").font = Font(bold=True, size=11)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_mbse_reqs.py <input.json> [output.xlsx]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.with_suffix(".xlsx")

    with open(input_file) as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    build_title(wb, data)
    build_catalog(wb, data)
    build_allocation(wb, data)
    build_skeleton(wb)

    wb.save(output_file)
    print(f"Workbook saved to {output_file}")

if __name__ == "__main__":
    main()
