"""Calibration Data Exchange Builder — generates OEM-Tier-1 calibration agreement from JSON.

Usage:
    python generate_caldex.py <input.json> <output.xlsx>

Input JSON schema:
{
  "item": {name, project, doc_id, revision, date, author, approver},
  "parties": {oem, tier1, tier2},
  "ownership": [{param_id, param_name, owner, change_rights, baseline_ref}],
  "baseline_refs": [{param_id, baseline_version, baseline_date}],
  "exchange_formats": [
    {format_name, file_extension, description, compatibility}
  ],
  "change_protocol": {approval_chain, notification, baseline_update_freq},
  "acceptance_criteria": [{criterion, measurable, owner}]
}
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
WHITE_TEXT = "FFFFFF"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def style_title(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color=WHITE_TEXT)
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header(ws, row, headers):
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = Font(name=FONT_NAME, size=10, bold=True, color=WHITE_TEXT)
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 24


def autosize(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = w


def build_title(wb, item):
    ws = wb.create_sheet("Title", 0)
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 6, "Calibration Data Exchange Agreement")
    style_title(ws, 3, 6, item.get("name", "(Unnamed)"))

    row = 5
    for k, v in item.items():
        ws.cell(row=row, column=1, value=k).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=v)
        row += 1

    autosize(ws, {1: 20, 2: 40})


def build_document_control(wb):
    ws = wb.create_sheet("Document Control", 1)
    style_header(ws, 1, ["Revision", "Date", "Author", "Change Description", "Approved By"])
    ws.cell(row=2, column=1, value="1.0")
    ws.cell(row=2, column=2, value=str(date.today()))
    ws.cell(row=2, column=3, value="")
    ws.cell(row=2, column=4, value="Initial release")
    ws.cell(row=2, column=5, value="")
    autosize(ws, {1: 12, 2: 12, 3: 15, 4: 30, 5: 15})


def build_parties(wb, parties):
    ws = wb.create_sheet("Parties", 2)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 3, "Contracting Parties")

    row = 3
    for role, name in parties.items():
        ws.cell(row=row, column=1, value=role).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=name)
        row += 1

    autosize(ws, {1: 20, 2: 40})


def build_ownership_matrix(wb, ownership):
    ws = wb.create_sheet("Parameter Ownership Matrix", 3)
    headers = ["Param ID", "Param Name", "Owner", "Change Rights", "Baseline Ref"]
    style_header(ws, 1, headers)

    for row, item in enumerate(ownership, start=2):
        ws.cell(row=row, column=1, value=item.get("param_id", ""))
        ws.cell(row=row, column=2, value=item.get("param_name", ""))
        ws.cell(row=row, column=3, value=item.get("owner", ""))
        ws.cell(row=row, column=4, value=item.get("change_rights", ""))
        ws.cell(row=row, column=5, value=item.get("baseline_ref", ""))

    autosize(ws, {i: 16 for i in range(1, 6)})


def build_baseline_refs(wb, baselines):
    ws = wb.create_sheet("Baseline References", 4)
    headers = ["Param ID", "Baseline Version", "Baseline Date", "Approved By"]
    style_header(ws, 1, headers)

    for row, item in enumerate(baselines, start=2):
        ws.cell(row=row, column=1, value=item.get("param_id", ""))
        ws.cell(row=row, column=2, value=item.get("baseline_version", ""))
        ws.cell(row=row, column=3, value=item.get("baseline_date", ""))
        ws.cell(row=row, column=4, value=item.get("approved_by", ""))

    autosize(ws, {i: 16 for i in range(1, 5)})


def build_exchange_formats(wb, formats):
    ws = wb.create_sheet("Exchange Format Specification", 5)
    headers = ["Format Name", "File Extension", "Description", "Compatibility"]
    style_header(ws, 1, headers)

    for row, fmt in enumerate(formats, start=2):
        ws.cell(row=row, column=1, value=fmt.get("format_name", ""))
        ws.cell(row=row, column=2, value=fmt.get("file_extension", ""))
        ws.cell(row=row, column=3, value=fmt.get("description", ""))
        ws.cell(row=row, column=4, value=fmt.get("compatibility", ""))

    autosize(ws, {1: 16, 2: 14, 3: 35, 4: 30})


def build_change_protocol(wb, protocol):
    ws = wb.create_sheet("Change Protocol", 6)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 3, "Calibration Data Change Protocol")

    row = 3
    for k, v in protocol.items():
        ws.cell(row=row, column=1, value=k).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=v)
        row += 1

    autosize(ws, {1: 25, 2: 50})


def build_version_control(wb):
    ws = wb.create_sheet("Version Control", 7)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 4, "Version Control Scheme")

    rules = [
        ("Versioning Format", "MAJOR.MINOR (e.g., 1.0, 1.1, 2.0)"),
        ("Baseline Tag", "Baseline versions tagged with date (e.g., BL_2024-05-01)"),
        ("Change History", "Every baseline change logged with reason and approver"),
        ("Rollback", "Previous baselines retained for 12 months"),
        ("Compatibility", "Tool compatibility matrix maintained"),
    ]

    row = 3
    for k, v in rules:
        ws.cell(row=row, column=1, value=k).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=v)
        row += 1

    autosize(ws, {1: 25, 2: 50})


def build_acceptance_criteria(wb, criteria):
    ws = wb.create_sheet("Acceptance Criteria", 8)
    headers = ["Criterion", "Measurable", "Owner", "Pass/Fail"]
    style_header(ws, 1, headers)

    for row, item in enumerate(criteria, start=2):
        ws.cell(row=row, column=1, value=item.get("criterion", ""))
        ws.cell(row=row, column=2, value=item.get("measurable", ""))
        ws.cell(row=row, column=3, value=item.get("owner", ""))
        ws.cell(row=row, column=4, value="")

    autosize(ws, {1: 30, 2: 40, 3: 16, 4: 12})


def build_signoff_block(wb):
    ws = wb.create_sheet("Signoff Block", 9)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 3, "Authorization and Signoff")

    row = 3
    signatories = [
        ("OEM Calibration Lead", "Name: ___________________  Date: ___________________"),
        ("OEM Manager", "Name: ___________________  Date: ___________________"),
        ("Tier-1 Calibration Lead", "Name: ___________________  Date: ___________________"),
        ("Tier-1 Manager", "Name: ___________________  Date: ___________________"),
    ]

    for title, line in signatories:
        ws.cell(row=row, column=1, value=title).font = Font(name=FONT_NAME, bold=True)
        row += 1
        ws.cell(row=row, column=1, value=line)
        row += 2

    autosize(ws, {1: 30})


def build_references(wb):
    ws = wb.create_sheet("References", 10)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 2, "References")

    refs = [
        ("ASAM MCD-2 MC", "A2L calibration description standard"),
        ("ETAS DCM", "Data Conservation format for parameter values"),
        ("CDFX", "Calibration Data Format eXchange (OEM proprietary)"),
        ("PaCo", "Parameter Control format (alternative interchange)"),
        ("ISO 26262", "Functional Safety — work flow and documentation control"),
    ]

    row = 3
    for name, desc in refs:
        ws.cell(row=row, column=1, value=name).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1

    autosize(ws, {1: 25, 2: 50})


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_caldex.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Error: Input file {input_path} not found")
        sys.exit(1)

    with open(input_path, 'r') as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    item = data.get("item", {})
    parties = data.get("parties", {})
    ownership = data.get("ownership", [])
    baselines = data.get("baseline_refs", [])
    formats = data.get("exchange_formats", [])
    protocol = data.get("change_protocol", {})
    criteria = data.get("acceptance_criteria", [])

    build_title(wb, item)
    build_document_control(wb)
    build_parties(wb, parties)
    build_ownership_matrix(wb, ownership)
    build_baseline_refs(wb, baselines)
    build_exchange_formats(wb, formats)
    build_change_protocol(wb, protocol)
    build_version_control(wb)
    build_acceptance_criteria(wb, criteria)
    build_signoff_block(wb)
    build_references(wb)

    wb.save(output_path)
    print(f"Calibration Data Exchange agreement generated: {output_path}")


if __name__ == "__main__":
    main()
