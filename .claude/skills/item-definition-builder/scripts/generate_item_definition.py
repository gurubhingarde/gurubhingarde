"""
Item Definition Builder — generates a multi-tab ISO 26262-3 Item Definition workbook from JSON input.

Usage:
    python generate_item_definition.py <input.json> <output.xlsx>

Input JSON schema (see examples/sample_item_def_esc.json for a full example):
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "scope_description": str,
  "item_classification": "vehicle system | subsystem | component",
  "distinguishing_notes": str,
  "functions": [{id, name, description, criticality}],
  "non_functional_requirements": [{id, category, requirement, rationale}],
  "boundary": {in_item, out_item, adjacent_systems, notes},
  "external_interfaces": [{id, interface, counterpart, direction, data, integrity, notes}],
  "operating_modes": [{id, name, entry_conditions, exit_conditions, safety_relevant}],
  "allocations": [{function_id, type, rationale}],
  "assumptions": [{id, category, assumption, rationale}],
  "references": [{id, title, version}]
}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def title_font(size: int = 16) -> Font:
    return Font(name=FONT_NAME, size=size, bold=True, color="FFFFFF")


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def style_title_row(ws: Worksheet, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = title_font(14)
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header_row(ws: Worksheet, row: int, headers: list[str]) -> None:
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = header_font()
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 32


def stripe_body(ws: Worksheet, start_row: int, end_row: int, last_col: int) -> None:
    for r in range(start_row, end_row + 1):
        fill = PatternFill("solid", fgColor=ALT_ROW) if (r - start_row) % 2 else None
        for c in range(1, last_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = body_font()
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER_ALL
            if fill:
                cell.fill = fill


def autosize(ws: Worksheet, widths: dict[int, int]) -> None:
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, item: dict) -> None:
    ws = wb.create_sheet("00_Title_Page", 0)
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 2, 4, "Item Definition")
    style_title_row(ws, 3, 4, f"{item.get('name', '')} ({item.get('abbr', '')})")

    fields = [
        ("Project", item.get("project", "")),
        ("Document ID", item.get("doc_id", "")),
        ("Revision", item.get("revision", "")),
        ("Date", item.get("date", "")),
        ("Author", item.get("author", "")),
        ("Approver", item.get("approver", "")),
        ("Company", item.get("company", "")),
        ("Standard", "ISO 26262-3:2018, Clause 5 (Item Definition)"),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left")
        row += 1

    autosize(ws, {1: 4, 2: 22, 3: 60, 4: 4})


def build_document_control(wb: Workbook) -> None:
    ws = wb.create_sheet("01_Document_Control", 1)
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 5, "Document Control")

    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of change", "Approver"])
    placeholders = [
        ("0.1", "", "", "Initial draft generated by item-definition-builder skill", ""),
        ("0.2", "", "", "Internal review comments incorporated", ""),
        ("1.0", "", "", "Released for HARA", ""),
    ]
    for i, row_data in enumerate(placeholders, start=4):
        for col, val in enumerate(row_data, start=1):
            ws.cell(row=i, column=col, value=val)
    stripe_body(ws, 4, 4 + len(placeholders) - 1, 5)

    autosize(ws, {1: 4, 2: 15, 3: 15, 4: 20, 5: 30, 6: 20})


def build_item_description(wb: Workbook, item: dict, scope_desc: str, classification: str, distinguishing: str) -> None:
    ws = wb.create_sheet("02_Item_Description", 2)
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 4, "Item Description")

    row = 3
    ws.cell(row=row, column=1, value="Item Name").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    ws.cell(row=row, column=2, value=item.get("name", ""))
    row += 1

    ws.cell(row=row, column=1, value="Item Abbreviation").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    ws.cell(row=row, column=2, value=item.get("abbr", ""))
    row += 2

    ws.cell(row=row, column=1, value="Item Classification").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    ws.cell(row=row, column=2, value=classification or "")
    row += 2

    ws.cell(row=row, column=1, value="Scope Description").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    ws.cell(row=row, column=1).alignment = Alignment(vertical="top")
    ws.cell(row=row, column=2, value=scope_desc or "").alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[row].height = 60
    row += 3

    ws.cell(row=row, column=1, value="Distinguishing Notes").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    ws.cell(row=row, column=1).alignment = Alignment(vertical="top")
    ws.cell(row=row, column=2, value=distinguishing or "").alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[row].height = 60

    autosize(ws, {1: 24, 2: 60, 3: 4})


def build_functions(wb: Workbook, functions: list[dict]) -> None:
    ws = wb.create_sheet("03_Functions", 3)
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 4, "Functions")

    style_header_row(ws, 3, ["ID", "Function Name", "Description", "Criticality Hint"])
    for i, func in enumerate(functions, start=4):
        ws.cell(row=i, column=1, value=func.get("id", ""))
        ws.cell(row=i, column=2, value=func.get("name", ""))
        ws.cell(row=i, column=3, value=func.get("description", ""))
        ws.cell(row=i, column=4, value=func.get("criticality", ""))
    stripe_body(ws, 4, 4 + len(functions) - 1, 4)

    autosize(ws, {1: 8, 2: 20, 3: 40, 4: 20, 5: 4})


def build_non_functional_requirements(wb: Workbook, nfr: list[dict]) -> None:
    ws = wb.create_sheet("04_Non_Functional_Requirements", 4)
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 4, "Non-Functional Requirements")

    style_header_row(ws, 3, ["ID", "Category", "Requirement", "Rationale"])
    for i, req in enumerate(nfr, start=4):
        ws.cell(row=i, column=1, value=req.get("id", ""))
        ws.cell(row=i, column=2, value=req.get("category", ""))
        ws.cell(row=i, column=3, value=req.get("requirement", ""))
        ws.cell(row=i, column=4, value=req.get("rationale", ""))
    stripe_body(ws, 4, 4 + len(nfr) - 1, 4)

    autosize(ws, {1: 8, 2: 18, 3: 30, 4: 30, 5: 4})


def build_boundary_diagram(wb: Workbook, boundary: dict) -> None:
    ws = wb.create_sheet("05_Boundary_Diagram", 5)
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 4, "Boundary Diagram")

    row = 3
    ws.cell(row=row, column=1, value="Boundary Notes").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    ws.cell(row=row, column=1).alignment = Alignment(vertical="top")
    ws.cell(row=row, column=2, value=boundary.get("notes", "")).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[row].height = 50
    row += 3

    ws.cell(row=row, column=1, value="IN the Item").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    row += 1
    for item_in in boundary.get("in_item", []):
        ws.cell(row=row, column=2, value=item_in)
        row += 1
    row += 1

    ws.cell(row=row, column=1, value="OUT of Item").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    row += 1
    for item_out in boundary.get("out_item", []):
        ws.cell(row=row, column=2, value=item_out)
        row += 1
    row += 1

    ws.cell(row=row, column=1, value="Adjacent Systems").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    row += 1
    for sys in boundary.get("adjacent_systems", []):
        ws.cell(row=row, column=2, value=sys)
        row += 1

    autosize(ws, {1: 24, 2: 60, 3: 4})


def build_external_interfaces(wb: Workbook, interfaces: list[dict]) -> None:
    ws = wb.create_sheet("06_External_Interfaces", 6)
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 7, "External Interfaces")

    style_header_row(ws, 3, ["ID", "Interface Name", "Counterpart System", "Direction", "Data/Signal", "Integrity Protection", "Notes"])
    for i, intf in enumerate(interfaces, start=4):
        ws.cell(row=i, column=1, value=intf.get("id", ""))
        ws.cell(row=i, column=2, value=intf.get("interface", ""))
        ws.cell(row=i, column=3, value=intf.get("counterpart", ""))
        ws.cell(row=i, column=4, value=intf.get("direction", ""))
        ws.cell(row=i, column=5, value=intf.get("data", ""))
        ws.cell(row=i, column=6, value=intf.get("integrity", ""))
        ws.cell(row=i, column=7, value=intf.get("notes", ""))
    stripe_body(ws, 4, 4 + len(interfaces) - 1, 7)

    autosize(ws, {1: 8, 2: 18, 3: 18, 4: 12, 5: 15, 6: 15, 7: 20, 8: 4})


def build_operating_modes(wb: Workbook, modes: list[dict]) -> None:
    ws = wb.create_sheet("07_Operating_Modes", 7)
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 5, "Operating Modes")

    style_header_row(ws, 3, ["ID", "Mode Name", "Entry Conditions", "Exit Conditions", "Safety Relevant"])
    for i, mode in enumerate(modes, start=4):
        ws.cell(row=i, column=1, value=mode.get("id", ""))
        ws.cell(row=i, column=2, value=mode.get("name", ""))
        ws.cell(row=i, column=3, value=mode.get("entry_conditions", ""))
        ws.cell(row=i, column=4, value=mode.get("exit_conditions", ""))
        ws.cell(row=i, column=5, value=mode.get("safety_relevant", ""))
    stripe_body(ws, 4, 4 + len(modes) - 1, 5)

    autosize(ws, {1: 8, 2: 18, 3: 20, 4: 20, 5: 15, 6: 4})


def build_allocation(wb: Workbook, allocations: list[dict]) -> None:
    ws = wb.create_sheet("08_Allocation_HW_SW_Mech", 8)
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 4, "Hardware / Software / Mechanical Allocation")

    style_header_row(ws, 3, ["Function ID", "Allocation Type", "Rationale"])
    for i, alloc in enumerate(allocations, start=4):
        ws.cell(row=i, column=1, value=alloc.get("function_id", ""))
        ws.cell(row=i, column=2, value=alloc.get("type", ""))
        ws.cell(row=i, column=3, value=alloc.get("rationale", ""))
    stripe_body(ws, 4, 4 + len(allocations) - 1, 3)

    autosize(ws, {1: 14, 2: 20, 3: 45, 4: 4})


def build_assumptions(wb: Workbook, assumptions: list[dict]) -> None:
    ws = wb.create_sheet("09_Initial_Assumptions", 9)
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 4, "Initial Assumptions")

    style_header_row(ws, 3, ["ID", "Category", "Assumption", "Rationale"])
    for i, assum in enumerate(assumptions, start=4):
        ws.cell(row=i, column=1, value=assum.get("id", ""))
        ws.cell(row=i, column=2, value=assum.get("category", ""))
        ws.cell(row=i, column=3, value=assum.get("assumption", ""))
        ws.cell(row=i, column=4, value=assum.get("rationale", ""))
    stripe_body(ws, 4, 4 + len(assumptions) - 1, 4)

    autosize(ws, {1: 8, 2: 18, 3: 35, 4: 30, 5: 4})


def build_references(wb: Workbook, references: list[dict]) -> None:
    ws = wb.create_sheet("10_References", 10)
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 3, "References")

    style_header_row(ws, 3, ["ID", "Title", "Version"])
    for i, ref in enumerate(references, start=4):
        ws.cell(row=i, column=1, value=ref.get("id", ""))
        ws.cell(row=i, column=2, value=ref.get("title", ""))
        ws.cell(row=i, column=3, value=ref.get("version", ""))
    stripe_body(ws, 4, 4 + len(references) - 1, 3)

    autosize(ws, {1: 8, 2: 40, 3: 15, 4: 4})


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def load_input(input_file: str) -> dict:
    with open(input_file, "r") as f:
        return json.load(f)


def generate_workbook(data: dict) -> Workbook:
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    item = data.get("item", {})
    build_title_page(wb, item)
    build_document_control(wb)
    build_item_description(
        wb,
        item,
        data.get("scope_description", ""),
        data.get("item_classification", ""),
        data.get("distinguishing_notes", ""),
    )
    build_functions(wb, data.get("functions", []))
    build_non_functional_requirements(wb, data.get("non_functional_requirements", []))
    build_boundary_diagram(wb, data.get("boundary", {}))
    build_external_interfaces(wb, data.get("external_interfaces", []))
    build_operating_modes(wb, data.get("operating_modes", []))
    build_allocation(wb, data.get("allocations", []))
    build_assumptions(wb, data.get("assumptions", []))
    build_references(wb, data.get("references", []))

    return wb


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_item_definition.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        data = load_input(input_file)
        wb = generate_workbook(data)
        wb.save(output_file)

        summary = {
            "status": "success",
            "output_file": output_file,
            "tabs_created": len(wb.sheetnames),
            "tab_names": wb.sheetnames,
            "functions_count": len(data.get("functions", [])),
            "interfaces_count": len(data.get("external_interfaces", [])),
            "operating_modes_count": len(data.get("operating_modes", [])),
            "assumptions_count": len(data.get("assumptions", [])),
        }

        print(json.dumps(summary, indent=2))

    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
