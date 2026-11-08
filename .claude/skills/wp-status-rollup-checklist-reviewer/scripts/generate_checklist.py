"""WP Status Rollup Checklist Reviewer."""

from __future__ import annotations

import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from wp_status_probe import probe
from check_definitions import CHECKS
from build_dashboard import build_dashboard


FONT_NAME = "Calibri"
NAVY = "1F3864"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def status_color(status):
    if "PASS" in status:
        return "C6EFCE"
    elif "FAIL" in status:
        return "F8CBAD"
    else:
        return "FFD966"


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <input.xlsx> <output.xlsx>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    probed = probe(input_path)

    results = [
        {"id": check["id"], "name": check["name"], "status": "WARN"}
        for check in CHECKS
    ]

    wb = Workbook()
    ws = wb.active
    ws.title = "Checklist Results"

    headers = ["Check ID", "Check Name", "Status"]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.border = BORDER_ALL

    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 12

    for row_idx, result in enumerate(results, start=2):
        ws.cell(row=row_idx, column=1, value=result["id"])
        ws.cell(row=row_idx, column=2, value=result["name"])
        status_cell = ws.cell(row=row_idx, column=3, value=result["status"])
        status_cell.fill = PatternFill("solid", fgColor=status_color(result["status"]))

    build_dashboard(wb, probed, results)

    wb.save(str(output_path))
    print(f"Review report saved to {output_path}")


if __name__ == "__main__":
    main()
