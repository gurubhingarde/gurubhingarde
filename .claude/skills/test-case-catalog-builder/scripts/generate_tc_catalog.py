"""Test Case Catalog builder - generates ISO 26262 compliant test case workbook."""

from __future__ import annotations

import json
import sys
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"

def main(input_json: str, output_xlsx: str):
    with open(input_json) as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    item = data.get("item", {})
    test_cases = data.get("test_cases", [])

    ws = wb.create_sheet("Title")
    ws.merge_cells("A2:C2")
    c = ws["A2"]
    c.value = "Test Case Catalog"
    c.font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = Alignment(horizontal="center")

    row = 5
    for k, v in [("Project", item.get("project")), ("Item", item.get("name")),
                  ("Doc ID", item.get("doc_id"))]:
        ws.cell(row=row, column=1, value=k).font = Font(bold=True)
        ws.cell(row=row, column=2, value=v)
        row += 1

    ws = wb.create_sheet("Test Cases")
    for col, h in enumerate(["ID", "Title", "Status"], 1):
        ws.cell(row=1, column=col, value=h).font = Font(bold=True)

    for row_idx, tc in enumerate(test_cases or [], 2):
        ws.cell(row=row_idx, column=1, value=tc.get("id", ""))
        ws.cell(row=row_idx, column=2, value=tc.get("title", ""))
        ws.cell(row=row_idx, column=3, value=tc.get("status", "Draft"))

    ws = wb.create_sheet("References")
    ws["A1"] = "References"
    ws["A1"].font = Font(size=14, bold=True)

    wb.save(output_xlsx)
    print(f"Test Case Catalog generated: {output_xlsx}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.json> <output.xlsx>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
