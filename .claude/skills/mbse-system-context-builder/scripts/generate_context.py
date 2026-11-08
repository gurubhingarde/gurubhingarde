"""MBSE System Context Builder — generates 11-tab workbook."""

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
    style_title(ws, 2, 5, "MBSE System Context Workbook")
    system_name = data.get("system", {}).get("name", "System")
    style_title(ws, 3, 5, system_name)
    ws.cell(row=5, column=1, value="Created:").font = Font(bold=True)
    ws.cell(row=5, column=2, value=str(date.today()))

def build_actors(wb, data):
    ws = wb.create_sheet("Actor Inventory")
    ws.cell(row=1, column=1, value="Actor ID").font = Font(bold=True)
    ws.cell(row=1, column=2, value="Name").font = Font(bold=True)
    ws.cell(row=1, column=3, value="Type").font = Font(bold=True)
    ws.cell(row=1, column=4, value="Description").font = Font(bold=True)
    row = 2
    for actor in data.get("actors", []):
        ws.cell(row=row, column=1, value=actor.get("id", ""))
        ws.cell(row=row, column=2, value=actor.get("name", ""))
        ws.cell(row=row, column=3, value=actor.get("type", ""))
        ws.cell(row=row, column=4, value=actor.get("description", ""))
        row += 1

def build_interfaces(wb, data):
    ws = wb.create_sheet("External Interfaces")
    ws.cell(row=1, column=1, value="Interface ID").font = Font(bold=True)
    ws.cell(row=1, column=2, value="From").font = Font(bold=True)
    ws.cell(row=1, column=3, value="To").font = Font(bold=True)
    ws.cell(row=1, column=4, value="Direction").font = Font(bold=True)
    ws.cell(row=1, column=5, value="Description").font = Font(bold=True)
    row = 2
    for intf in data.get("interfaces", []):
        ws.cell(row=row, column=1, value=intf.get("id", ""))
        ws.cell(row=row, column=2, value=intf.get("from", ""))
        ws.cell(row=row, column=3, value=intf.get("to", ""))
        ws.cell(row=row, column=4, value=intf.get("direction", ""))
        ws.cell(row=row, column=5, value=intf.get("description", ""))
        row += 1

def build_use_cases(wb, data):
    ws = wb.create_sheet("Use Case Catalog")
    ws.cell(row=1, column=1, value="Use Case ID").font = Font(bold=True)
    ws.cell(row=1, column=2, value="Name").font = Font(bold=True)
    ws.cell(row=1, column=3, value="Primary Actor").font = Font(bold=True)
    ws.cell(row=1, column=4, value="Description").font = Font(bold=True)
    row = 2
    for uc in data.get("use_cases", []):
        ws.cell(row=row, column=1, value=uc.get("id", ""))
        ws.cell(row=row, column=2, value=uc.get("name", ""))
        ws.cell(row=row, column=3, value=uc.get("primary_actor", ""))
        ws.cell(row=row, column=4, value=uc.get("description", ""))
        row += 1

def build_scenarios(wb, data):
    ws = wb.create_sheet("Operational Scenarios")
    ws.cell(row=1, column=1, value="Scenario ID").font = Font(bold=True)
    ws.cell(row=1, column=2, value="Name").font = Font(bold=True)
    ws.cell(row=1, column=3, value="Description").font = Font(bold=True)
    row = 2
    for scenario in data.get("scenarios", []):
        ws.cell(row=row, column=1, value=scenario.get("id", ""))
        ws.cell(row=row, column=2, value=scenario.get("name", ""))
        ws.cell(row=row, column=3, value=scenario.get("description", ""))
        row += 1

def build_skeleton(wb):
    """Add stub tabs for boundary, needs, assumptions, etc."""
    for sheet_name in ["System Boundary Definition", "Stakeholder Needs", "Assumptions and Constraints",
                       "Validation Rules", "References", "Document Control", "System Identification"]:
        ws = wb.create_sheet(sheet_name)
        ws.cell(row=1, column=1, value=f"{sheet_name} (Placeholder)").font = Font(bold=True, size=11)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_context.py <input.json> [output.xlsx]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.with_suffix(".xlsx")

    with open(input_file) as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    build_title(wb, data)
    build_actors(wb, data)
    build_interfaces(wb, data)
    build_use_cases(wb, data)
    build_scenarios(wb, data)
    build_skeleton(wb)

    wb.save(output_file)
    print(f"Workbook saved to {output_file}")

if __name__ == "__main__":
    main()
