"""SysML State Machine Diagram builder - generates 11-tab xlsx."""

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

def main():
    parser = argparse.ArgumentParser(description="Generate SysML State Machine Diagram workbook")
    parser.add_argument("output", nargs="?", default="sysml_state_machine.xlsx")
    parser.add_argument("--title", default="Unnamed State Machine")
    args = parser.parse_args()

    wb = Workbook()
    ws = wb.active
    ws.title = "0_Title"
    ws.column_dimensions["A"].width = 60
    style_title(ws, 1, 4, "SysML State Machine Diagram")
    ws.cell(row=3, column=1, value="State Machine Name").font = Font(bold=True)
    ws.cell(row=3, column=2, value=args.title)
    ws.cell(row=4, column=1, value="Created").font = Font(bold=True)
    ws.cell(row=4, column=2, value=str(date.today()))

    for sheet_name in ["1_Document_Control", "2_State_Machine_Header", "3_State_Catalog", "4_Region_Catalog",
                        "5_Transition_Catalog", "6_Entry_Exit_Do_Behaviors", "7_Pseudo_States",
                        "8_Internal_Activities", "9_Validation_Rules", "10_References"]:
        wb.create_sheet(sheet_name)

    wb.save(args.output)
    print(f"State machine workbook saved to {args.output}")

if __name__ == "__main__":
    main()
