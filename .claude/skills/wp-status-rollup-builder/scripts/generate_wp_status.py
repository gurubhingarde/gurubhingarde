"""WP Status Rollup — generates a multi-tab ISO 26262 status workbook from JSON.

Usage:
    python generate_wp_status.py <input.json> <output.xlsx>
"""

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
RED_BAD = "F8CBAD"
ORANGE_PARTIAL = "FFD966"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


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
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 36


def style_data_row(ws, row, num_cols, color=None):
    for col in range(1, num_cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.border = BORDER_ALL
        if color:
            cell.fill = PatternFill("solid", fgColor=color)
        elif (row - 4) % 2 == 0:
            cell.fill = PatternFill("solid", fgColor="F2F2F2")


def build_title_page(wb, project_info):
    ws = wb.active
    ws.title = "Title Page"
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title(ws, row, 3, "Work Product Status Rollup")

    row = 3
    ws.cell(row=row, column=1, value="Project Name").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project_info.get("name", ""))

    row += 1
    ws.cell(row=row, column=1, value="Reporting Period").font = Font(bold=True)
    ws.cell(row=row, column=2, value=f"{project_info.get('period_start', '')} to {project_info.get('period_end', '')}")

    row += 1
    ws.cell(row=row, column=1, value="Report Date").font = Font(bold=True)
    ws.cell(row=row, column=2, value=str(date.today()))

    row += 1
    ws.cell(row=row, column=1, value="Safety Manager").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project_info.get("safety_manager", ""))

    row += 1
    ws.cell(row=row, column=1, value="Target ASIL").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project_info.get("target_asil", "D"))


def build_document_control(wb):
    ws = wb.create_sheet("Document Control")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 50

    row = 1
    style_title(ws, row, 3, "Document Control")

    row = 3
    headers = ["Revision", "Date", "Summary"]
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="1.0")
    ws.cell(row=row, column=2, value=str(date.today()))
    ws.cell(row=row, column=3, value="Initial release")


def build_reporting_period(wb, project_info):
    ws = wb.create_sheet("Reporting Period")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 40

    row = 1
    style_title(ws, row, 2, "Reporting Period")

    row = 3
    ws.cell(row=row, column=1, value="Period Start").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project_info.get("period_start", ""))

    row += 1
    ws.cell(row=row, column=1, value="Period End").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project_info.get("period_end", ""))

    row += 1
    ws.cell(row=row, column=1, value="Work Products Reported").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project_info.get("wp_count", 0))

    row += 1
    ws.cell(row=row, column=1, value="Status As Of").font = Font(bold=True)
    ws.cell(row=row, column=2, value=str(date.today()))


def build_phase_inventory(wb, wps):
    ws = wb.create_sheet("Lifecycle Phase Inventory")

    headers = ["Phase", "WP Count", "Complete %", "At Risk Count"]
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 15

    row = 1
    style_title(ws, row, len(headers), "Lifecycle Phase Inventory")

    row = 3
    style_header(ws, row, headers)

    phases = {
        "Concept": sum(1 for w in wps if w.get("phase") == "Concept"),
        "System": sum(1 for w in wps if w.get("phase") == "System"),
        "Hardware": sum(1 for w in wps if w.get("phase") == "Hardware"),
        "Software": sum(1 for w in wps if w.get("phase") == "Software"),
        "Integration": sum(1 for w in wps if w.get("phase") == "Integration"),
        "Validation": sum(1 for w in wps if w.get("phase") == "Validation"),
    }

    for idx, (phase_name, count) in enumerate(phases.items(), start=4):
        ws.cell(row=idx, column=1, value=phase_name)
        ws.cell(row=idx, column=2, value=count)
        ws.cell(row=idx, column=3, value="")
        ws.cell(row=idx, column=4, value="")
        style_data_row(ws, idx, 4)


def build_wp_rollup(wb, wps):
    ws = wb.create_sheet("Work Product Roll-up")

    headers = ["WP ID", "Name", "Owner", "% Complete", "Due Date", "ASIL", "Dependencies", "Blocker"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 30
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 12
    ws.column_dimensions["F"].width = 8
    ws.column_dimensions["G"].width = 20
    ws.column_dimensions["H"].width = 10

    row = 1
    style_title(ws, row, len(headers), "Work Product Roll-up")

    row = 3
    style_header(ws, row, headers)

    for idx, wp in enumerate(wps, start=4):
        ws.cell(row=idx, column=1, value=wp.get("id", ""))
        ws.cell(row=idx, column=2, value=wp.get("name", ""))
        ws.cell(row=idx, column=3, value=wp.get("owner", ""))
        ws.cell(row=idx, column=4, value=wp.get("complete_pct", 0))
        ws.cell(row=idx, column=5, value=wp.get("due_date", ""))
        ws.cell(row=idx, column=6, value=wp.get("asil", ""))
        ws.cell(row=idx, column=7, value=wp.get("dependencies", ""))
        ws.cell(row=idx, column=8, value=wp.get("blocker", "No"))

        color = None
        if wp.get("complete_pct", 0) >= 100:
            color = GREEN_OK
        elif wp.get("complete_pct", 0) < 50:
            color = RED_BAD
        elif wp.get("blocker") == "Yes":
            color = ORANGE_PARTIAL

        style_data_row(ws, idx, len(headers), color=color)


def build_critical_path(wb):
    ws = wb.create_sheet("Critical Path WPs")

    headers = ["WP ID", "Name", "Slack", "Impact If Late"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 35

    row = 1
    style_title(ws, row, len(headers), "Critical Path Work Products")

    row = 3
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="(Identify WPs with zero slack/on critical path)")
    ws.merge_cells(f"A{row}:D{row}")


def build_dependency_map(wb, wps):
    ws = wb.create_sheet("Dependency Map")

    headers = ["From WP", "To WP (Predecessor)", "Dependency Type"]
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 25

    row = 1
    style_title(ws, row, len(headers), "Dependency Map")

    row = 3
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="(Build DAG of WP dependencies)")
    ws.merge_cells(f"A{row}:C{row}")


def build_burndown(wb):
    ws = wb.create_sheet("Burndown Trend")

    headers = ["Reporting Period", "% Complete (Aggregate)"]
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 20

    row = 1
    style_title(ws, row, len(headers), "Burndown Trend")

    row = 3
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="(Track % complete over time)")
    ws.merge_cells(f"A{row}:B{row}")


def build_risk_linkage(wb):
    ws = wb.create_sheet("Risk Linkage")

    headers = ["Risk ID", "Affected WP", "Impact on Schedule"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 35

    row = 1
    style_title(ws, row, len(headers), "Risk Linkage to WPs")

    row = 3
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="(Link to open programmatic risks affecting WP completion)")
    ws.merge_cells(f"A{row}:C{row}")


def build_references(wb):
    ws = wb.create_sheet("References")
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title(ws, row, 2, "References")

    row = 3
    ws.cell(row=row, column=1, value="ISO 26262-2:2018")
    ws.cell(row=row, column=2, value="Program management and planning requirements")


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_wp_status.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with open(input_path) as f:
        data = json.load(f)

    project_info = data.get("project", {})
    wps = data.get("work_products", [])

    wb = Workbook()

    build_title_page(wb, project_info)
    build_document_control(wb)
    build_reporting_period(wb, project_info)
    build_phase_inventory(wb, wps)
    build_wp_rollup(wb, wps)
    build_critical_path(wb)
    build_dependency_map(wb, wps)
    build_burndown(wb)
    build_risk_linkage(wb)
    build_references(wb)

    wb.save(str(output_path))
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
