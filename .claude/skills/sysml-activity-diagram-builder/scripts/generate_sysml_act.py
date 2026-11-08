"""SysML Activity Diagram builder - generates 11-tab xlsx."""

import argparse
from datetime import date
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

FONT_NAME = "Calibri"
NAVY = "1F3864"
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
    parser = argparse.ArgumentParser(description="Generate SysML Activity Diagram workbook")
    parser.add_argument("output", nargs="?", default="sysml_activity_diagram.xlsx")
    parser.add_argument("--title", default="Unnamed Activity")
    args = parser.parse_args()

    wb = Workbook()
    ws = wb.active
    ws.title = "0_Title"
    ws.column_dimensions["A"].width = 60
    style_title(ws, 1, 4, "SysML Activity Diagram")
    ws.cell(row=3, column=1, value="Activity Name").font = Font(bold=True)
    ws.cell(row=3, column=2, value=args.title)
    ws.cell(row=4, column=1, value="Created").font = Font(bold=True)
    ws.cell(row=4, column=2, value=str(date.today()))

    for sheet_name in ["1_Document_Control", "2_Activity_Header", "3_Action_Catalog", "4_Control_Flow_Catalog",
                        "5_Object_Flow_Catalog", "6_Decision_Merge_Nodes", "7_Fork_Join_Nodes", "8_Swim_Lanes",
                        "9_Pins_Parameters", "10_References"]:
        wb.create_sheet(sheet_name)

    wb.save(args.output)
    print(f"Activity diagram workbook saved to {args.output}")

if __name__ == "__main__":
    main()
