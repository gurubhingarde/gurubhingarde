"""SysML Requirement Diagram builder - generates 10-tab xlsx."""

import argparse
from datetime import date
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
NAVY_BORDER = Side(border_style="thin", color=NAVY)
BORDER_ALL = Border(left=NAVY_BORDER, right=NAVY_BORDER, top=NAVY_BORDER, bottom=NAVY_BORDER)

def style_title(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28

def style_header(ws, row, headers):
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 24

def style_data(ws, row, values, alt=False):
    fill = PatternFill("solid", fgColor=ALT_ROW) if alt else PatternFill()
    for col, val in enumerate(values, start=1):
        cell = ws.cell(row=row, column=col, value=val)
        cell.font = Font(name=FONT_NAME, size=10)
        cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        cell.fill = fill
        cell.border = BORDER_ALL

def main():
    parser = argparse.ArgumentParser(description="Generate SysML Requirement Diagram workbook")
    parser.add_argument("output", nargs="?", default="sysml_requirement_diagram.xlsx")
    parser.add_argument("--title", default="Unnamed System")
    parser.add_argument("--author", default="")
    args = parser.parse_args()

    wb = Workbook()
    ws = wb.active
    ws.title = "0_Title"
    ws.column_dimensions["A"].width = 60
    style_title(ws, 1, 4, "SysML Requirement Diagram")
    ws.cell(row=3, column=1, value="System Name").font = Font(bold=True)
    ws.cell(row=3, column=2, value=args.title)
    ws.cell(row=4, column=1, value="Created").font = Font(bold=True)
    ws.cell(row=4, column=2, value=str(date.today()))

    ws_dc = wb.create_sheet("1_Document_Control")
    ws_dc.column_dimensions["A"].width = 20
    ws_dc.column_dimensions["B"].width = 40
    style_title(ws_dc, 1, 4, "Document Control")
    style_header(ws_dc, 3, ["Field", "Value", "Notes", "Status"])
    data = [["System", args.title, "Requirements domain", ""], ["Version", "1.0", "Initial", "Draft"]]
    for i, row_data in enumerate(data, start=4):
        style_data(ws_dc, i, row_data, alt=(i % 2 == 0))

    ws_req = wb.create_sheet("3_Requirement_Catalog")
    ws_req.column_dimensions["A"].width = 15
    ws_req.column_dimensions["B"].width = 20
    ws_req.column_dimensions["C"].width = 50
    ws_req.column_dimensions["D"].width = 15
    style_title(ws_req, 1, 4, "Requirement Catalog")
    style_header(ws_req, 3, ["Req ID", "Kind", "Requirement Text", "Status"])
    data = [["REQ-001", "Functional", "System shall do X", "Active"], ["REQ-002", "Non-Functional", "System shall achieve Y", "Active"]]
    for i, row_data in enumerate(data, start=4):
        style_data(ws_req, i, row_data, alt=(i % 2 == 0))

    wb.create_sheet("2_Requirement_Set_Identity")
    wb.create_sheet("4_Containment_Hierarchy")
    wb.create_sheet("5_Derive_Relationships")
    wb.create_sheet("6_Satisfy_Relationships")
    wb.create_sheet("7_Verify_Relationships")
    wb.create_sheet("8_Refine_Copy_Relationships")
    wb.create_sheet("9_References")

    wb.save(args.output)
    print(f"Requirement diagram workbook saved to {args.output}")

if __name__ == "__main__":
    main()
