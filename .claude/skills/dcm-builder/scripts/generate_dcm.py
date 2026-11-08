"""DCM Builder — generates ETAS DCM (Data Conservation) calibration values workbook from JSON input.

Usage:
    python generate_dcm.py <input.json> <output.xlsx>

Input JSON schema:
{
  "item": {name, variant, project, dataset_id, build_date, author, approver, company},
  "source_a2l": {file, version, date},
  "scalars": [{name, value, unit, physical_min, physical_max}],
  "curves": [{name, axis_ref, values, physical_min, physical_max}],
  "maps": [{name, x_axis_ref, y_axis_ref, values, physical_min, physical_max}],
  "axis_points": [{name, points, unit, physical_min, physical_max}],
  "value_blocks": [{name, members}]
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


# Style constants
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
    style_title(ws, 2, 6, "DCM Calibration Values Dataset")
    style_title(ws, 3, 6, item.get("name", "(Unnamed)"))

    row = 5
    for k, v in item.items():
        ws.cell(row=row, column=1, value=k).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=v)
        row += 1

    autosize(ws, {1: 20, 2: 40})


def build_document_control(wb):
    ws = wb.create_sheet("Document Control", 1)
    style_header(ws, 1, ["Revision", "Date", "Author", "Change Description", "Baseline", "Approved By"])
    ws.cell(row=2, column=1, value="1.0")
    ws.cell(row=2, column=2, value=str(date.today()))
    ws.cell(row=2, column=3, value="")
    ws.cell(row=2, column=4, value="Initial release")
    ws.cell(row=2, column=5, value="Baseline")
    ws.cell(row=2, column=6, value="")
    autosize(ws, {1: 12, 2: 12, 3: 15, 4: 30, 5: 12, 6: 15})


def build_source_a2l(wb, source):
    ws = wb.create_sheet("Source A2L Reference", 2)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 3, "Source A2L Document Reference")

    row = 3
    for k, v in source.items():
        ws.cell(row=row, column=1, value=k).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=v)
        row += 1

    autosize(ws, {1: 20, 2: 40})


def build_dataset_identity(wb, dataset):
    ws = wb.create_sheet("Dataset Identity", 3)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 3, "Dataset Identification")

    row = 3
    for k, v in dataset.items():
        ws.cell(row=row, column=1, value=k).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=v)
        row += 1

    autosize(ws, {1: 20, 2: 40})


def build_scalar_values(wb, scalars):
    ws = wb.create_sheet("Scalar Values", 4)
    headers = ["Name", "Value", "Unit", "Physical Min", "Physical Max", "Comment"]
    style_header(ws, 1, headers)

    for row, scalar in enumerate(scalars, start=2):
        ws.cell(row=row, column=1, value=scalar.get("name", ""))
        ws.cell(row=row, column=2, value=scalar.get("value", ""))
        ws.cell(row=row, column=3, value=scalar.get("unit", ""))
        ws.cell(row=row, column=4, value=scalar.get("physical_min", ""))
        ws.cell(row=row, column=5, value=scalar.get("physical_max", ""))
        ws.cell(row=row, column=6, value=scalar.get("comment", ""))

    autosize(ws, {i: 16 for i in range(1, 7)})


def build_curve_values(wb, curves):
    ws = wb.create_sheet("Curve Values", 5)
    headers = ["Name", "Axis Reference", "Value Count", "Physical Min", "Physical Max", "Comment"]
    style_header(ws, 1, headers)

    for row, curve in enumerate(curves, start=2):
        ws.cell(row=row, column=1, value=curve.get("name", ""))
        ws.cell(row=row, column=2, value=curve.get("axis_ref", ""))
        ws.cell(row=row, column=3, value=len(curve.get("values", [])))
        ws.cell(row=row, column=4, value=curve.get("physical_min", ""))
        ws.cell(row=row, column=5, value=curve.get("physical_max", ""))
        ws.cell(row=row, column=6, value=curve.get("comment", ""))

    autosize(ws, {i: 16 for i in range(1, 7)})


def build_map_values(wb, maps):
    ws = wb.create_sheet("Map Values", 6)
    headers = ["Name", "X-Axis Ref", "Y-Axis Ref", "X Count", "Y Count", "Physical Min", "Physical Max", "Comment"]
    style_header(ws, 1, headers)

    for row, map_item in enumerate(maps, start=2):
        ws.cell(row=row, column=1, value=map_item.get("name", ""))
        ws.cell(row=row, column=2, value=map_item.get("x_axis_ref", ""))
        ws.cell(row=row, column=3, value=map_item.get("y_axis_ref", ""))
        x_vals = map_item.get("values", [])
        y_count = len(x_vals) if x_vals else 0
        x_count = len(x_vals[0]) if x_vals and x_vals[0] else 0
        ws.cell(row=row, column=4, value=x_count)
        ws.cell(row=row, column=5, value=y_count)
        ws.cell(row=row, column=6, value=map_item.get("physical_min", ""))
        ws.cell(row=row, column=7, value=map_item.get("physical_max", ""))
        ws.cell(row=row, column=8, value=map_item.get("comment", ""))

    autosize(ws, {i: 14 for i in range(1, 9)})


def build_axis_points(wb, axes):
    ws = wb.create_sheet("Axis Point Values", 7)
    headers = ["Name", "Point Count", "Unit", "Physical Min", "Physical Max", "Comment"]
    style_header(ws, 1, headers)

    for row, axis in enumerate(axes, start=2):
        ws.cell(row=row, column=1, value=axis.get("name", ""))
        ws.cell(row=row, column=2, value=len(axis.get("points", [])))
        ws.cell(row=row, column=3, value=axis.get("unit", ""))
        ws.cell(row=row, column=4, value=axis.get("physical_min", ""))
        ws.cell(row=row, column=5, value=axis.get("physical_max", ""))
        ws.cell(row=row, column=6, value=axis.get("comment", ""))

    autosize(ws, {i: 16 for i in range(1, 7)})


def build_value_blocks(wb, blocks):
    ws = wb.create_sheet("Value Block", 8)
    headers = ["Block Name", "Member Count", "Members (JSON)", "Comment"]
    style_header(ws, 1, headers)

    for row, block in enumerate(blocks, start=2):
        ws.cell(row=row, column=1, value=block.get("name", ""))
        ws.cell(row=row, column=2, value=len(block.get("members", [])))
        ws.cell(row=row, column=3, value=json.dumps(block.get("members", [])))
        ws.cell(row=row, column=4, value=block.get("comment", ""))

    autosize(ws, {1: 18, 2: 14, 3: 50, 4: 30})


def build_comment_block(wb):
    ws = wb.create_sheet("Comment Block", 9)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 4, "Unit, Text, and Comment Metadata")

    row = 3
    ws.cell(row=row, column=1, value="Parameter").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row=row, column=2, value="Unit")
    ws.cell(row=row, column=3, value="Text")
    ws.cell(row=row, column=4, value="Comment")

    autosize(ws, {1: 20, 2: 15, 3: 30, 4: 40})


def build_validation_rules(wb):
    ws = wb.create_sheet("Validation Rules", 10)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 3, "DCM Validation Rules")

    rules = [
        "Every value within physical range (min <= value <= max).",
        "Axis points monotonically increasing.",
        "Map dimensions match source A2L axes.",
        "Units consistent across dataset.",
        "No NaN or missing required values.",
        "Dataset identity recorded (variant, build date).",
        "Baseline reference documented.",
        "Curve/Map interpolation compatible with A2L.",
        "Value counts match axis point counts.",
        "Dataset version matches source A2L version."
    ]

    for row, rule in enumerate(rules, start=3):
        ws.cell(row=row, column=1, value=f"V{row-2:02d}").font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=rule)

    autosize(ws, {1: 6, 2: 70})


def build_references(wb):
    ws = wb.create_sheet("References", 11)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 2, "References")

    refs = [
        ("ETAS DCM Format", "Data Conservation format for calibration value interchange"),
        ("ASAM MCD-2 MC", "Standard for calibration description (A2L)"),
        ("INCA", "ETAS Interactive Calibration Tool"),
        ("CANape", "Vector CANape Calibration Tool"),
        ("ATI Vision", "Vector ATI Vision Measurement and Test Tool"),
        ("XCP", "Universal Measurement and Calibration Protocol"),
        ("Baseline Traceability", "Link to approved baseline dataset reference")
    ]

    row = 3
    for name, desc in refs:
        ws.cell(row=row, column=1, value=name).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1

    autosize(ws, {1: 25, 2: 50})


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_dcm.py <input.json> <output.xlsx>")
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
    source = data.get("source_a2l", {})
    dataset = data.get("dataset_identity", {})
    scalars = data.get("scalars", [])
    curves = data.get("curves", [])
    maps = data.get("maps", [])
    axes = data.get("axis_points", [])
    blocks = data.get("value_blocks", [])

    build_title(wb, item)
    build_document_control(wb)
    build_source_a2l(wb, source)
    build_dataset_identity(wb, dataset)
    build_scalar_values(wb, scalars)
    build_curve_values(wb, curves)
    build_map_values(wb, maps)
    build_axis_points(wb, axes)
    build_value_blocks(wb, blocks)
    build_comment_block(wb)
    build_validation_rules(wb)
    build_references(wb)

    wb.save(output_path)
    print(f"DCM workbook generated: {output_path}")


if __name__ == "__main__":
    main()
