"""MBSE Model Architecture Builder — generates a 12-tab ARCADIA workbook."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
GREEN_OK = "C6EFCE"
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
    style_title(ws, 2, 4, "MBSE Model Architecture Workbook")
    system_name = data.get("system", {}).get("name", "System")
    style_title(ws, 3, 4, system_name)
    ws.cell(row=5, column=1, value="System Abbreviation:").font = Font(bold=True)
    ws.cell(row=5, column=2, value=data.get("system", {}).get("abbr", ""))
    ws.cell(row=6, column=1, value="Created:").font = Font(bold=True)
    ws.cell(row=6, column=2, value=str(date.today()))
    ws.row_dimensions[1].height = 8

def build_operational_analysis(wb, data):
    ws = wb.create_sheet("Operational Analysis")
    ws.cell(row=1, column=1, value="Operational Analysis Layer").font = Font(bold=True, size=12)
    ws.cell(row=2, column=1, value="Scenarios")
    for i, scenario in enumerate(data.get("operational_scenarios", []), start=3):
        ws.cell(row=i, column=1, value=scenario.get("id", ""))
        ws.cell(row=i, column=2, value=scenario.get("name", ""))
        ws.cell(row=i, column=3, value=scenario.get("description", ""))

def build_system_analysis(wb, data):
    ws = wb.create_sheet("System Analysis")
    ws.cell(row=1, column=1, value="System Analysis Layer").font = Font(bold=True, size=12)
    ws.cell(row=2, column=1, value="Function ID")
    ws.cell(row=2, column=2, value="Function Name")
    ws.cell(row=2, column=3, value="Description")
    for i, func in enumerate(data.get("system_functions", []), start=3):
        ws.cell(row=i, column=1, value=func.get("id", ""))
        ws.cell(row=i, column=2, value=func.get("name", ""))
        ws.cell(row=i, column=3, value=func.get("description", ""))

def build_logical_analysis(wb, data):
    ws = wb.create_sheet("Logical Analysis")
    ws.cell(row=1, column=1, value="Logical Analysis Layer").font = Font(bold=True, size=12)
    ws.cell(row=2, column=1, value="Component ID")
    ws.cell(row=2, column=2, value="Component Name")
    ws.cell(row=2, column=3, value="Description")
    for i, comp in enumerate(data.get("logical_components", []), start=3):
        ws.cell(row=i, column=1, value=comp.get("id", ""))
        ws.cell(row=i, column=2, value=comp.get("name", ""))
        ws.cell(row=i, column=3, value=comp.get("description", ""))

def build_physical_analysis(wb, data):
    ws = wb.create_sheet("Physical Analysis")
    ws.cell(row=1, column=1, value="Physical Analysis Layer").font = Font(bold=True, size=12)
    ws.cell(row=2, column=1, value="Component ID")
    ws.cell(row=2, column=2, value="Component Name")
    ws.cell(row=2, column=3, value="Technology/Deployment")
    for i, comp in enumerate(data.get("physical_components", []), start=3):
        ws.cell(row=i, column=1, value=comp.get("id", ""))
        ws.cell(row=i, column=2, value=comp.get("name", ""))
        ws.cell(row=i, column=3, value=comp.get("deployment", ""))

def build_skeleton(wb):
    """Add stub tabs for traceability, viewpoints, conventions."""
    for sheet_name in ["Inter-Layer Traceability", "Viewpoint Inventory", "Modeling Conventions",
                       "Validation Rules", "References", "Document Control", "System Identification"]:
        ws = wb.create_sheet(sheet_name)
        ws.cell(row=1, column=1, value=f"{sheet_name} (Placeholder)").font = Font(bold=True, size=11)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_mbse_model.py <input.json> [output.xlsx]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.with_suffix(".xlsx")

    with open(input_file) as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    build_title(wb, data)
    build_operational_analysis(wb, data)
    build_system_analysis(wb, data)
    build_logical_analysis(wb, data)
    build_physical_analysis(wb, data)
    build_skeleton(wb)

    wb.save(output_file)
    print(f"Workbook saved to {output_file}")

if __name__ == "__main__":
    main()
