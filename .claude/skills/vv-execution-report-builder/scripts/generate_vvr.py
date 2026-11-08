"""V&V Execution Report builder - generates ISO 26262-8 §9 test campaign report."""

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
    campaign = data.get("campaign", {})

    ws = wb.create_sheet("Title")
    ws.merge_cells("A2:C2")
    c = ws["A2"]
    c.value = "V&V Execution Report"
    c.font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = Alignment(horizontal="center")

    row = 5
    for k, v in [("Project", item.get("project")), ("Item", item.get("name")),
                  ("Report Date", campaign.get("date", date.today().isoformat()))]:
        ws.cell(row=row, column=1, value=k).font = Font(bold=True)
        ws.cell(row=row, column=2, value=v)
        row += 1

    ws = wb.create_sheet("Test Execution Summary")
    ws["A1"] = "Test Execution Summary"
    ws["A1"].font = Font(size=12, bold=True)

    ws = wb.create_sheet("Defect Catalog")
    ws["A1"] = "Defect Catalog"
    ws["A1"].font = Font(size=12, bold=True)

    ws = wb.create_sheet("Coverage Achieved")
    ws["A1"] = "Coverage Achievement"
    ws["A1"].font = Font(size=12, bold=True)

    ws = wb.create_sheet("Signoff")
    ws["A1"] = "Execution Report Signoff"
    ws["A1"].font = Font(size=14, bold=True)

    ws = wb.create_sheet("References")
    ws["A1"] = "References"
    ws["A1"].font = Font(size=14, bold=True)

    wb.save(output_xlsx)
    print(f"V&V Execution Report generated: {output_xlsx}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.json> <output.xlsx>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
