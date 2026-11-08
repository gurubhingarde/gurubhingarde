"""Change Impact Analysis — generates a multi-tab ISO 26262-8 change analysis workbook from JSON.

Usage:
    python generate_cia.py <input.json> <output.xlsx>
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


def build_title_page(wb, change_info):
    ws = wb.active
    ws.title = "Title Page"
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title(ws, row, 3, "Change Impact Analysis")

    row = 3
    ws.cell(row=row, column=1, value="Change ID").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("id", "CHG-001"))

    row += 1
    ws.cell(row=row, column=1, value="Change Title").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("title", ""))

    row += 1
    ws.cell(row=row, column=1, value="Project").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("project", ""))

    row += 1
    ws.cell(row=row, column=1, value="Requesting Party").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("requester", ""))

    row += 1
    ws.cell(row=row, column=1, value="Request Date").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("date", str(date.today())))


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
    ws.cell(row=row, column=3, value="Initial analysis")


def build_change_request_identity(wb, change_info):
    ws = wb.create_sheet("Change Request Identity")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 50

    row = 1
    style_title(ws, row, 2, "Change Request Identity")

    row = 3
    ws.cell(row=row, column=1, value="Change ID").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("id", ""))

    row += 1
    ws.cell(row=row, column=1, value="Change Title").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("title", ""))

    row += 2
    ws.cell(row=row, column=1, value="Description").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("description", ""))
    ws.row_dimensions[row].height = 60

    row += 2
    ws.cell(row=row, column=1, value="Rationale").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("rationale", ""))
    ws.row_dimensions[row].height = 45


def build_classification(wb, change_info):
    ws = wb.create_sheet("Change Classification")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 50

    row = 1
    style_title(ws, row, 2, "Change Classification")

    row = 3
    ws.cell(row=row, column=1, value="Classification").font = Font(bold=True)
    classification = change_info.get("classification", "major")
    ws.cell(row=row, column=2, value=classification)

    # Color by classification
    if classification == "safety-impacting":
        ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor=RED_BAD)
    elif classification == "major":
        ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor="FFD966")

    row += 2
    ws.cell(row=row, column=1, value="Justification").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("classification_reason", ""))
    ws.row_dimensions[row].height = 60


def build_affected_wps(wb, change_info):
    ws = wb.create_sheet("Affected Work Products Matrix")

    headers = ["Work Product", "Impact Type", "Impact Description"]
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 40

    row = 1
    style_title(ws, row, len(headers), "Affected Work Products Matrix")

    row = 3
    style_header(ws, row, headers)

    affected_wps = change_info.get("affected_wps", [])
    for idx, wp in enumerate(affected_wps, start=4):
        ws.cell(row=idx, column=1, value=wp.get("name", ""))
        ws.cell(row=idx, column=2, value=wp.get("impact_type", ""))
        ws.cell(row=idx, column=3, value=wp.get("impact_description", ""))


def build_asil_impact(wb, change_info):
    ws = wb.create_sheet("ASIL Impact Assessment")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 20

    row = 1
    style_title(ws, row, 2, "ASIL Impact Assessment")

    row = 3
    ws.cell(row=row, column=1, value="Original ASIL").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("original_asil", "D"))

    row += 1
    ws.cell(row=row, column=1, value="Modified ASIL").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("modified_asil", "D"))

    row += 2
    ws.cell(row=row, column=1, value="Impact Justification").font = Font(bold=True)
    ws.cell(row=row, column=2, value=change_info.get("asil_justification", ""))


def build_reverification_scope(wb, change_info):
    ws = wb.create_sheet("Re-verification Scope")

    headers = ["Activity", "Scope", "Owner", "Target Completion"]
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 15

    row = 1
    style_title(ws, row, len(headers), "Re-verification Scope")

    row = 3
    style_header(ws, row, headers)

    reverif_items = change_info.get("reverification_scope", [])
    for idx, item in enumerate(reverif_items, start=4):
        ws.cell(row=idx, column=1, value=item.get("activity", ""))
        ws.cell(row=idx, column=2, value=item.get("scope", ""))
        ws.cell(row=idx, column=3, value=item.get("owner", ""))
        ws.cell(row=idx, column=4, value=item.get("target_date", ""))


def build_revalidation_scope(wb, change_info):
    ws = wb.create_sheet("Re-validation Scope")

    headers = ["Activity", "Scope", "Owner", "Target Completion"]
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 15

    row = 1
    style_title(ws, row, len(headers), "Re-validation Scope")

    row = 3
    style_header(ws, row, headers)

    revalid_items = change_info.get("revalidation_scope", [])
    for idx, item in enumerate(revalid_items, start=4):
        ws.cell(row=idx, column=1, value=item.get("activity", ""))
        ws.cell(row=idx, column=2, value=item.get("scope", ""))
        ws.cell(row=idx, column=3, value=item.get("owner", ""))
        ws.cell(row=idx, column=4, value=item.get("target_date", ""))


def build_approval_block(wb):
    ws = wb.create_sheet("Approval Block")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 40

    row = 1
    style_title(ws, row, 2, "Approval Block")

    row = 3
    ws.cell(row=row, column=1, value="Safety Manager Approval").font = Font(bold=True)
    ws.cell(row=row, column=2, value="")

    row += 1
    ws.cell(row=row, column=1, value="Signature / Date").font = Font(bold=True)
    ws.cell(row=row, column=2, value="________________________")

    row += 2
    ws.cell(row=row, column=1, value="Change Board Approval").font = Font(bold=True)
    ws.cell(row=row, column=2, value="")

    row += 1
    ws.cell(row=row, column=1, value="Signature / Date").font = Font(bold=True)
    ws.cell(row=row, column=2, value="________________________")

    row += 2
    ws.cell(row=row, column=1, value="Conditional Approvals").font = Font(bold=True)
    ws.cell(row=row, column=2, value="").alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[row].height = 45


def build_references(wb):
    ws = wb.create_sheet("References")
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title(ws, row, 2, "References")

    row = 3
    ws.cell(row=row, column=1, value="ISO 26262-8:2018 Clause 8")
    ws.cell(row=row, column=2, value="Change Management requirements")


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_cia.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with open(input_path) as f:
        change_info = json.load(f)

    wb = Workbook()

    build_title_page(wb, change_info)
    build_document_control(wb)
    build_change_request_identity(wb, change_info)
    build_classification(wb, change_info)
    build_affected_wps(wb, change_info)
    build_asil_impact(wb, change_info)
    build_reverification_scope(wb, change_info)
    build_revalidation_scope(wb, change_info)
    build_approval_block(wb)
    build_references(wb)

    wb.save(str(output_path))
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
