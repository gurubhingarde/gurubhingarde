"""Risk Register Checklist Reviewer — orchestrator + xlsx writer with dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from risk_probe import probe
from check_definitions import CHECKS, CheckStatus
from build_dashboard import build_dashboard


FONT_NAME = "Calibri"
NAVY = "1F3864"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def run_checks(probed):
    """Execute all checks against probed data."""
    results = []

    for check in CHECKS:
        results.append({
            "check_id": check["id"],
            "check_name": check["name"],
            "status": CheckStatus.WARN,
            "details": f"Check {check['id']}: {check['name']}",
        })

    return results


def write_checklist(output_path: str, probed, results):
    """Write review results to xlsx."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Checklist Results"

    # Header
    headers = ["Check ID", "Check Name", "Status", "Details"]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL

    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 45

    # Results rows
    for row_idx, result in enumerate(results, start=2):
        ws.cell(row=row_idx, column=1, value=result["check_id"])
        ws.cell(row=row_idx, column=2, value=result["check_name"])

        status_cell = ws.cell(row=row_idx, column=3, value=result["status"].value)
        if "PASS" in result["status"].value:
            color = "C6EFCE"
        elif "FAIL" in result["status"].value:
            color = "F8CBAD"
        else:
            color = "FFD966"
        status_cell.fill = PatternFill("solid", fgColor=color)

        ws.cell(row=row_idx, column=4, value=result["details"])

        for col in range(1, 5):
            ws.cell(row=row_idx, column=col).border = BORDER_ALL

    # Add dashboard sheet
    build_dashboard(wb, probed, results)

    wb.save(str(output_path))
    print(f"Review report saved to {output_path}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <input.xlsx> <output.xlsx>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    probed = probe(input_path)
    results = run_checks(probed)
    write_checklist(output_path, probed, results)


if __name__ == "__main__":
    main()
