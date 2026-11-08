"""Triggering conditions catalog generator for ISO 21448 SOTIF."""
from __future__ import annotations
import json, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

FONT_NAME, NAVY, ALT_ROW = "Calibri", "1F3864", "F2F2F2"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def title_font(size=16):
    return Font(name=FONT_NAME, size=size, bold=True, color="FFFFFF")

def header_font():
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")

def body_font():
    return Font(name=FONT_NAME, size=10)

def style_title_row(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = title_font(14)
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28

def style_header_row(ws, row, headers):
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = header_font()
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 32

def stripe_body(ws, start_row, end_row, last_col):
    for r in range(start_row, end_row + 1):
        fill = PatternFill("solid", fgColor=ALT_ROW) if (r - start_row) % 2 else None
        for c in range(1, last_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = body_font()
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER_ALL
            if fill:
                cell.fill = fill

def autosize(ws, widths):
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width

def build_title_page(wb, system):
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "ISO 21448 Triggering Conditions Catalog")
    style_title_row(ws, 3, 4, system.get("name", ""))
    row = 6
    for label, value in [("Project", system.get("project", "")), ("Date", system.get("date", ""))]:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        row += 1
    autosize(ws, {1: 4, 2: 22, 3: 60, 4: 4})

def build_doc_control(wb):
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description", "Approver"])
    for i, data in enumerate([("0.1", "", "", "Initial draft generated", ""), ("1.0", "", "", "Released", "")], start=4):
        for c, val in enumerate(data, start=1):
            ws.cell(row=i, column=c, value=val)
    stripe_body(ws, 4, 5, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})

def build_sotif_reference(wb):
    ws = wb.create_sheet("02_SOTIF_Analysis_Reference")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "SOTIF Analysis Reference")
    ws.merge_cells("A3:C3")
    ws.cell(row=3, column=1, value="Reference: Link to upstream SOTIF analysis document.").font = Font(name=FONT_NAME, italic=True)
    autosize(ws, {1: 4, 2: 40, 3: 60})

def build_environmental_triggers(wb, items):
    ws = wb.create_sheet("03_Environmental_Triggering_Conditions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Environmental Triggering Conditions")
    style_header_row(ws, 3, ["Condition ID", "Category", "Description", "Likelihood"])
    for i, item in enumerate(items, start=4):
        ws.cell(row=i, column=1, value=item.get("id", ""))
        ws.cell(row=i, column=2, value=item.get("category", ""))
        ws.cell(row=i, column=3, value=item.get("description", ""))
        ws.cell(row=i, column=4, value=item.get("likelihood", ""))
    stripe_body(ws, 4, 3 + len(items), 4)
    autosize(ws, {1: 14, 2: 20, 3: 50, 4: 16})

def build_sensor_triggers(wb, items):
    ws = wb.create_sheet("04_Sensor_Triggering_Conditions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Sensor Triggering Conditions")
    style_header_row(ws, 3, ["Condition ID", "Sensor Type", "Failure Mode", "Description", "Likelihood"])
    for i, item in enumerate(items, start=4):
        ws.cell(row=i, column=1, value=item.get("id", ""))
        ws.cell(row=i, column=2, value=item.get("sensor_type", ""))
        ws.cell(row=i, column=3, value=item.get("failure_mode", ""))
        ws.cell(row=i, column=4, value=item.get("description", ""))
        ws.cell(row=i, column=5, value=item.get("likelihood", ""))
    stripe_body(ws, 4, 3 + len(items), 5)
    autosize(ws, {1: 14, 2: 14, 3: 18, 4: 50, 5: 16})

def build_road_infra_triggers(wb, items):
    ws = wb.create_sheet("05_Road_Infrastructure_Triggering_Conditions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Road Infrastructure Triggering Conditions")
    style_header_row(ws, 3, ["Condition ID", "Type", "Description", "Likelihood"])
    for i, item in enumerate(items, start=4):
        ws.cell(row=i, column=1, value=item.get("id", ""))
        ws.cell(row=i, column=2, value=item.get("type", ""))
        ws.cell(row=i, column=3, value=item.get("description", ""))
        ws.cell(row=i, column=4, value=item.get("likelihood", ""))
    stripe_body(ws, 4, 3 + len(items), 4)
    autosize(ws, {1: 14, 2: 18, 3: 50, 4: 16})

def build_road_user_triggers(wb, items):
    ws = wb.create_sheet("06_Other_Road_User_Triggering_Conditions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Other Road User Triggering Conditions")
    style_header_row(ws, 3, ["Condition ID", "Road User Type", "Behavior / Scenario", "Likelihood"])
    for i, item in enumerate(items, start=4):
        ws.cell(row=i, column=1, value=item.get("id", ""))
        ws.cell(row=i, column=2, value=item.get("road_user_type", ""))
        ws.cell(row=i, column=3, value=item.get("description", ""))
        ws.cell(row=i, column=4, value=item.get("likelihood", ""))
    stripe_body(ws, 4, 3 + len(items), 4)
    autosize(ws, {1: 14, 2: 18, 3: 50, 4: 16})

def build_system_state_triggers(wb, items):
    ws = wb.create_sheet("07_System_State_Triggering_Conditions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "System State Triggering Conditions")
    style_header_row(ws, 3, ["Condition ID", "System State", "Description", "Likelihood"])
    for i, item in enumerate(items, start=4):
        ws.cell(row=i, column=1, value=item.get("id", ""))
        ws.cell(row=i, column=2, value=item.get("state", ""))
        ws.cell(row=i, column=3, value=item.get("description", ""))
        ws.cell(row=i, column=4, value=item.get("likelihood", ""))
    stripe_body(ws, 4, 3 + len(items), 4)
    autosize(ws, {1: 14, 2: 20, 3: 50, 4: 16})

def build_driver_state_triggers(wb, items):
    ws = wb.create_sheet("08_Driver_State_Triggering_Conditions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Driver State Triggering Conditions")
    style_header_row(ws, 3, ["Condition ID", "Driver State", "Description", "Likelihood"])
    for i, item in enumerate(items, start=4):
        ws.cell(row=i, column=1, value=item.get("id", ""))
        ws.cell(row=i, column=2, value=item.get("state", ""))
        ws.cell(row=i, column=3, value=item.get("description", ""))
        ws.cell(row=i, column=4, value=item.get("likelihood", ""))
    stripe_body(ws, 4, 3 + len(items), 4)
    autosize(ws, {1: 14, 2: 20, 3: 50, 4: 16})

def build_combined_triggers(wb, items):
    ws = wb.create_sheet("09_Combined_Triggering_Conditions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Combined Triggering Conditions (Cartesian)")
    style_header_row(ws, 3, ["Condition ID", "Condition A", "Condition B", "Combined Description", "Likelihood"])
    for i, item in enumerate(items, start=4):
        ws.cell(row=i, column=1, value=item.get("id", ""))
        ws.cell(row=i, column=2, value=item.get("condition_a", ""))
        ws.cell(row=i, column=3, value=item.get("condition_b", ""))
        ws.cell(row=i, column=4, value=item.get("description", ""))
        ws.cell(row=i, column=5, value=item.get("likelihood", ""))
    stripe_body(ws, 4, 3 + len(items), 5)
    autosize(ws, {1: 14, 2: 20, 3: 20, 4: 50, 5: 16})

def build_references(wb):
    ws = wb.create_sheet("10_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References")
    for i, ref in enumerate(["ISO 21448:2022 Annex A — Triggering Conditions", "SOTIF concept phase documentation"], start=3):
        ws.cell(row=i, column=1, value=ref)
    autosize(ws, {1: 4, 2: 80})

def generate(input_path, output_path):
    with open(input_path) as f:
        data = json.load(f)
    system = data.get("system", {})
    wb = Workbook()
    wb.remove(wb.active)
    build_title_page(wb, system)
    build_doc_control(wb)
    build_sotif_reference(wb)
    build_environmental_triggers(wb, data.get("environmental_triggers", []))
    build_sensor_triggers(wb, data.get("sensor_triggers", []))
    build_road_infra_triggers(wb, data.get("road_infra_triggers", []))
    build_road_user_triggers(wb, data.get("road_user_triggers", []))
    build_system_state_triggers(wb, data.get("system_state_triggers", []))
    build_driver_state_triggers(wb, data.get("driver_state_triggers", []))
    build_combined_triggers(wb, data.get("combined_triggers", []))
    build_references(wb)
    wb.active = 0
    wb.save(output_path)
    return {
        "system": system.get("name", ""),
        "environmental_triggers": len(data.get("environmental_triggers", [])),
        "sensor_triggers": len(data.get("sensor_triggers", [])),
        "road_user_triggers": len(data.get("road_user_triggers", [])),
        "combined_triggers": len(data.get("combined_triggers", [])),
        "tabs": 11,
        "output_path": output_path,
    }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_triggering_conditions.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
