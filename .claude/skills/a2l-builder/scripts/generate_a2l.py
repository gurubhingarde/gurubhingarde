"""A2L Builder — generates a multi-tab ASAM MCD-2 MC A2L authoring workbook from JSON input.

Usage:
    python generate_a2l.py <input.json> <output.xlsx>

Input JSON schema:
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "ecu_identity": {part_number, serial_prefix, build_date, hw_version, sw_version, memory_size},
  "memory_map": [{address, size, type, segment_name}],
  "characteristics": [
    {id, name, type, unit, min_val, max_val, default, conversion_method_ref}
  ],
  "measurements": [
    {id, name, signal, unit, min_val, max_val, source}
  ],
  "conversion_methods": [
    {id, type, description, params}  // type: LINEAR, RAT_FUNC, TAB_INTP, etc.
  ],
  "axes": [
    {id, name, type, unit, points, min_val, max_val}
  ],
  "records": [
    {id, name, members}   // members: list, or comma-separated string
  ],
  "functions": [
    {id, name, group, description}
  ],
  "groups": [
    {id, name, parent_id, members}   // members: list, or comma-separated string
  ]
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
    style_title(ws, 2, 6, "A2L Calibration Description")
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


def build_ecu_identity(wb, ecu):
    ws = wb.create_sheet("ECU Identity", 2)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 4, "ECU Identity and Memory Map")

    row = 3
    for k, v in ecu.items():
        ws.cell(row=row, column=1, value=k).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=v)
        row += 1

    autosize(ws, {1: 20, 2: 30})


def build_characteristic_catalog(wb, chars):
    ws = wb.create_sheet("Characteristic Catalog", 3)
    headers = ["ID", "Name", "Type", "Unit", "Min Value", "Max Value", "Default", "Conversion Method"]
    style_header(ws, 1, headers)

    for row, char in enumerate(chars, start=2):
        ws.cell(row=row, column=1, value=char.get("id", ""))
        ws.cell(row=row, column=2, value=char.get("name", ""))
        ws.cell(row=row, column=3, value=char.get("type", ""))
        ws.cell(row=row, column=4, value=char.get("unit", ""))
        ws.cell(row=row, column=5, value=char.get("min_val", ""))
        ws.cell(row=row, column=6, value=char.get("max_val", ""))
        ws.cell(row=row, column=7, value=char.get("default", ""))
        ws.cell(row=row, column=8, value=char.get("conversion_method_ref", ""))

    autosize(ws, {i: 18 for i in range(1, 9)})


def build_measurement_catalog(wb, meas):
    ws = wb.create_sheet("Measurement Catalog", 4)
    headers = ["ID", "Name", "Signal", "Unit", "Min Value", "Max Value", "Source"]
    style_header(ws, 1, headers)

    for row, m in enumerate(meas, start=2):
        ws.cell(row=row, column=1, value=m.get("id", ""))
        ws.cell(row=row, column=2, value=m.get("name", ""))
        ws.cell(row=row, column=3, value=m.get("signal", ""))
        ws.cell(row=row, column=4, value=m.get("unit", ""))
        ws.cell(row=row, column=5, value=m.get("min_val", ""))
        ws.cell(row=row, column=6, value=m.get("max_val", ""))
        ws.cell(row=row, column=7, value=m.get("source", ""))

    autosize(ws, {i: 16 for i in range(1, 8)})


def normalize_members(value):
    """Coerce a members field to a list.

    Callers supply either a real list of member names or a comma-separated
    string. Counting len() on the string form silently reports characters
    instead of members, so normalize before counting or serializing.
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [value]


def build_conversion_methods(wb, methods):
    ws = wb.create_sheet("Conversion Methods", 5)
    headers = ["ID", "Type", "Description", "Parameters"]
    style_header(ws, 1, headers)

    for row, method in enumerate(methods, start=2):
        ws.cell(row=row, column=1, value=method.get("id", ""))
        ws.cell(row=row, column=2, value=method.get("type", ""))
        ws.cell(row=row, column=3, value=method.get("description", ""))
        ws.cell(row=row, column=4, value=json.dumps(method.get("params", {})))

    autosize(ws, {1: 12, 2: 14, 3: 25, 4: 40})


def build_axis_descriptions(wb, axes):
    ws = wb.create_sheet("Axis Descriptions", 6)
    headers = ["ID", "Name", "Type", "Unit", "Point Count", "Min Value", "Max Value"]
    style_header(ws, 1, headers)

    for row, axis in enumerate(axes, start=2):
        ws.cell(row=row, column=1, value=axis.get("id", ""))
        ws.cell(row=row, column=2, value=axis.get("name", ""))
        ws.cell(row=row, column=3, value=axis.get("type", ""))
        ws.cell(row=row, column=4, value=axis.get("unit", ""))
        pts = axis.get("points", [])
        ws.cell(row=row, column=5, value=len(pts) if isinstance(pts, (list, tuple)) else pts)
        ws.cell(row=row, column=6, value=axis.get("min_val", ""))
        ws.cell(row=row, column=7, value=axis.get("max_val", ""))

    autosize(ws, {i: 16 for i in range(1, 8)})


def build_record_layouts(wb, records):
    ws = wb.create_sheet("Record Layouts", 7)
    headers = ["ID", "Name", "Member Count", "Members (JSON)"]
    style_header(ws, 1, headers)

    for row, rec in enumerate(records, start=2):
        ws.cell(row=row, column=1, value=rec.get("id", ""))
        ws.cell(row=row, column=2, value=rec.get("name", ""))
        members = normalize_members(rec.get("members"))
        ws.cell(row=row, column=3, value=len(members))
        ws.cell(row=row, column=4, value=json.dumps(members))

    autosize(ws, {1: 12, 2: 20, 3: 14, 4: 50})


def build_function_hierarchy(wb, functions):
    ws = wb.create_sheet("Function Hierarchy", 8)
    headers = ["ID", "Name", "Group", "Description"]
    style_header(ws, 1, headers)

    for row, func in enumerate(functions, start=2):
        ws.cell(row=row, column=1, value=func.get("id", ""))
        ws.cell(row=row, column=2, value=func.get("name", ""))
        ws.cell(row=row, column=3, value=func.get("group", ""))
        ws.cell(row=row, column=4, value=func.get("description", ""))

    autosize(ws, {1: 12, 2: 20, 3: 16, 4: 40})


def build_group_hierarchy(wb, groups):
    ws = wb.create_sheet("Group Hierarchy", 9)
    headers = ["ID", "Name", "Parent ID", "Member Count"]
    style_header(ws, 1, headers)

    for row, grp in enumerate(groups, start=2):
        ws.cell(row=row, column=1, value=grp.get("id", ""))
        ws.cell(row=row, column=2, value=grp.get("name", ""))
        ws.cell(row=row, column=3, value=grp.get("parent_id", ""))
        ws.cell(row=row, column=4, value=len(normalize_members(grp.get("members"))))

    autosize(ws, {i: 16 for i in range(1, 5)})


def build_memory_address_mapping(wb, memory_map):
    ws = wb.create_sheet("Memory Address Mapping", 10)
    headers = ["Address (Hex)", "Size (Bytes)", "Type", "Segment Name", "Content"]
    style_header(ws, 1, headers)

    for row, mem in enumerate(memory_map, start=2):
        ws.cell(row=row, column=1, value=mem.get("address", ""))
        ws.cell(row=row, column=2, value=mem.get("size", ""))
        ws.cell(row=row, column=3, value=mem.get("type", ""))
        ws.cell(row=row, column=4, value=mem.get("segment_name", ""))
        ws.cell(row=row, column=5, value=mem.get("content", ""))

    autosize(ws, {1: 16, 2: 14, 3: 12, 4: 20, 5: 30})


def build_validation_rules(wb):
    ws = wb.create_sheet("Validation Rules", 11)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 3, "A2L Validation Rules")

    rules = [
        "Every characteristic must reference a valid conversion method.",
        "Every CURVE or MAP must reference valid X and Y axes.",
        "All axis points must be monotonically increasing.",
        "Record layouts must not exceed ECU memory boundary.",
        "No overlapping memory address ranges.",
        "All references (axis, conversion, function, group) must be defined.",
        "Conversion method parameters must be valid for the method type.",
        "Units must be consistent across related parameters.",
        "All names must follow ASAM naming conventions.",
        "Document control fields must be populated."
    ]

    for row, rule in enumerate(rules, start=3):
        ws.cell(row=row, column=1, value=f"V{row-2:02d}").font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=rule)

    autosize(ws, {1: 6, 2: 70})


def build_references(wb):
    ws = wb.create_sheet("References", 12)
    ws.sheet_view.showGridLines = False
    style_title(ws, 1, 2, "References")

    refs = [
        ("ASAM MCD-2 MC v1.7", "ASAM Standard for Calibration Description Format"),
        ("INCA", "ETAS Interactive Calibration Tool"),
        ("CANape", "Vector CANape Calibration Tool"),
        ("ATI Vision", "Vector ATI Vision Measurement Tool"),
        ("XCP", "Universal Measurement and Calibration Protocol"),
        ("CCP", "CAN Calibration Protocol"),
        ("ETK", "ETAS Tooling Kit")
    ]

    row = 3
    for name, desc in refs:
        ws.cell(row=row, column=1, value=name).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1

    autosize(ws, {1: 25, 2: 50})


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_a2l.py <input.json> <output.xlsx>")
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
    ecu = data.get("ecu_identity", {})
    chars = data.get("characteristics", [])
    meas = data.get("measurements", [])
    methods = data.get("conversion_methods", [])
    axes = data.get("axes", [])
    records = data.get("records", [])
    functions = data.get("functions", [])
    groups = data.get("groups", [])
    memory_map = data.get("memory_map", [])

    build_title(wb, item)
    build_document_control(wb)
    build_ecu_identity(wb, ecu)
    build_characteristic_catalog(wb, chars)
    build_measurement_catalog(wb, meas)
    build_conversion_methods(wb, methods)
    build_axis_descriptions(wb, axes)
    build_record_layouts(wb, records)
    build_function_hierarchy(wb, functions)
    build_group_hierarchy(wb, groups)
    build_memory_address_mapping(wb, memory_map)
    build_validation_rules(wb)
    build_references(wb)

    wb.save(output_path)
    print(f"A2L workbook generated: {output_path}")


if __name__ == "__main__":
    main()
