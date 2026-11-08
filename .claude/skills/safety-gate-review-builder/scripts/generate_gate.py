"""Safety Gate Review — generates a multi-tab ISO 26262 gate review workbook from JSON.

Usage:
    python generate_gate.py <input.json> <output.xlsx>
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

GATES = ["Concept Exit", "System Design Exit", "HW Exit", "SW Exit", "Integration Exit", "Validation Exit", "Release"]


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


def style_data_row(ws, row, num_cols):
    for col in range(1, num_cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.border = BORDER_ALL
        if (row - 4) % 2 == 0:
            cell.fill = PatternFill("solid", fgColor="F2F2F2")


def build_title_page(wb, gate_info):
    ws = wb.active
    ws.title = "Title Page"
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title(ws, row, 3, "Safety Gate Review Record")

    row = 3
    ws.cell(row=row, column=1, value="Gate Milestone").font = Font(bold=True)
    ws.cell(row=row, column=2, value=gate_info.get("gate", ""))

    row += 1
    ws.cell(row=row, column=1, value="Project Name").font = Font(bold=True)
    ws.cell(row=row, column=2, value=gate_info.get("project_name", ""))

    row += 1
    ws.cell(row=row, column=1, value="Target ASIL").font = Font(bold=True)
    ws.cell(row=row, column=2, value=gate_info.get("target_asil", "D"))

    row += 1
    ws.cell(row=row, column=1, value="Gate Date").font = Font(bold=True)
    ws.cell(row=row, column=2, value=gate_info.get("gate_date", str(date.today())))

    row += 1
    ws.cell(row=row, column=1, value="Scope").font = Font(bold=True)
    ws.cell(row=row, column=2, value=gate_info.get("scope", ""))


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


def build_gate_identification(wb, gate_info):
    ws = wb.create_sheet("Gate Identification")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 40

    row = 1
    style_title(ws, row, 2, "Gate Identification")

    row = 3
    ws.cell(row=row, column=1, value="Milestone").font = Font(bold=True)
    ws.cell(row=row, column=2, value=gate_info.get("gate", ""))

    row += 1
    ws.cell(row=row, column=1, value="Target ASIL").font = Font(bold=True)
    ws.cell(row=row, column=2, value=gate_info.get("target_asil", ""))

    row += 1
    ws.cell(row=row, column=1, value="Scope").font = Font(bold=True)
    ws.cell(row=row, column=2, value=gate_info.get("scope", ""))

    row += 1
    ws.cell(row=row, column=1, value="Predecessor Gate").font = Font(bold=True)
    ws.cell(row=row, column=2, value=gate_info.get("predecessor", ""))


def build_entry_criteria(wb):
    ws = wb.create_sheet("Entry Criteria Checklist")

    headers = ["Criterion", "Satisfied", "Evidence", "Reviewer"]
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 35
    ws.column_dimensions["D"].width = 15

    row = 1
    style_title(ws, row, len(headers), "Entry Criteria Checklist")

    row = 3
    style_header(ws, row, headers)

    criteria = [
        "Previous gate closure approved",
        "All predecessor work products available",
        "Required resources assigned",
        "Safety Plan baseline established",
        "Team training completed",
    ]

    for idx, criterion in enumerate(criteria, start=4):
        ws.cell(row=idx, column=1, value=criterion)
        ws.cell(row=idx, column=2, value="")
        ws.cell(row=idx, column=3, value="")
        ws.cell(row=idx, column=4, value="")
        style_data_row(ws, idx, 4)


def build_deliverable_inventory(wb):
    ws = wb.create_sheet("Deliverable Inventory")

    headers = ["Work Product", "Present", "Status", "Owner"]
    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 15

    row = 1
    style_title(ws, row, len(headers), "Deliverable Inventory")

    row = 3
    style_header(ws, row, headers)

    wps = ["Safety Plan", "HARA", "FSC", "TSC", "Verification Plan", "Test Reports"]

    for idx, wp in enumerate(wps, start=4):
        ws.cell(row=idx, column=1, value=wp)
        ws.cell(row=idx, column=2, value="")
        ws.cell(row=idx, column=3, value="")
        ws.cell(row=idx, column=4, value="")
        style_data_row(ws, idx, 4)


def build_exit_criteria(wb):
    ws = wb.create_sheet("Exit Criteria")

    headers = ["Criterion", "Measurable", "Met", "Evidence"]
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 35

    row = 1
    style_title(ws, row, len(headers), "Exit Criteria")

    row = 3
    style_header(ws, row, headers)

    criteria = [
        "All deliverables complete and reviewed",
        "All entry criteria satisfied",
        "No open action items from entry",
        "Verification metrics met or documented",
        "Gate decision approved by management",
    ]

    for idx, criterion in enumerate(criteria, start=4):
        ws.cell(row=idx, column=1, value=criterion)
        ws.cell(row=idx, column=2, value="Yes")
        ws.cell(row=idx, column=3, value="")
        ws.cell(row=idx, column=4, value="")
        style_data_row(ws, idx, 4)


def build_action_items(wb):
    ws = wb.create_sheet("Action Items")

    headers = ["ID", "Action", "Owner", "Due Date", "Priority"]
    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 12

    row = 1
    style_title(ws, row, len(headers), "Action Items from Gate")

    row = 3
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="(Record actions identified during gate review)")
    ws.merge_cells(f"A{row}:E{row}")


def build_open_risks(wb):
    ws = wb.create_sheet("Open Risks Reference")

    headers = ["Risk ID", "Description", "Impact on Phase", "Owner"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 35
    ws.column_dimensions["D"].width = 15

    row = 1
    style_title(ws, row, len(headers), "Open Risks Reference")

    row = 3
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="(Link to open programmatic risks from risk register)")
    ws.merge_cells(f"A{row}:D{row}")


def build_decision_record(wb):
    ws = wb.create_sheet("Decision Record")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 40

    row = 1
    style_title(ws, row, 2, "Gate Decision Record")

    row = 3
    ws.cell(row=row, column=1, value="Gate Decision").font = Font(bold=True)
    ws.cell(row=row, column=2, value="").alignment = Alignment(wrap_text=True)

    row += 1
    ws.cell(row=row, column=1, value="(Select: Go / Conditional / No-Go)").font = Font(italic=True, size=9)

    row += 2
    ws.cell(row=row, column=1, value="Decision Rationale").font = Font(bold=True)
    ws.cell(row=row, column=2, value="")

    row += 2
    ws.cell(row=row, column=1, value="Gate Chair").font = Font(bold=True)
    ws.cell(row=row, column=2, value="")

    row += 1
    ws.cell(row=row, column=1, value="Signature").font = Font(bold=True)
    ws.cell(row=row, column=2, value="________________________")

    row += 2
    ws.cell(row=row, column=1, value="Attendees").font = Font(bold=True)
    ws.cell(row=row, column=2, value="").alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[row].height = 60


def build_references(wb):
    ws = wb.create_sheet("References")
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title(ws, row, 2, "References")

    row = 3
    ws.cell(row=row, column=1, value="ISO 26262-2:2018 Clause 8.2")
    ws.cell(row=row, column=2, value="Phase-gate requirements and milestone definitions")

    row += 1
    ws.cell(row=row, column=1, value="Safety Plan")
    ws.cell(row=row, column=2, value="Project baseline defining gate criteria and milestones")


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_gate.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with open(input_path) as f:
        gate_info = json.load(f)

    wb = Workbook()

    build_title_page(wb, gate_info)
    build_document_control(wb)
    build_gate_identification(wb, gate_info)
    build_entry_criteria(wb)
    build_deliverable_inventory(wb)
    build_exit_criteria(wb)
    build_action_items(wb)
    build_open_risks(wb)
    build_decision_record(wb)
    build_references(wb)

    wb.save(str(output_path))
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
