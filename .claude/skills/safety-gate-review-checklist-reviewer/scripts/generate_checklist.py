"""Gate Review Checklist Reviewer — orchestrator + xlsx writer with dashboard."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from gate_probe import probe
from check_definitions import CHECKS, CheckStatus


FONT_NAME = "Calibri"
NAVY = "1F3864"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def style_header(ws, row, headers):
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 36


def status_color(status):
    if "PASS" in status:
        return "C6EFCE"
    elif "FAIL" in status:
        return "F8CBAD"
    elif "WARN" in status:
        return "FFD966"
    return "D0CECE"


def run_checks(probed) -> list:
    """Execute checks against probed data."""
    results = []

    for check in CHECKS:
        check_id = check["id"]
        check_name = check["name"]

        # Simplified checks
        if "tab" in check_id.lower():
            status = CheckStatus.WARN
        elif probed.has_entry_criteria and "entry" in check_name.lower():
            status = CheckStatus.PASS
        elif probed.has_decision_record and "decision" in check_name.lower():
            status = CheckStatus.PASS
        else:
            status = CheckStatus.WARN

        results.append({
            "id": check_id,
            "name": check_name,
            "status": status,
            "details": f"Check {check_id}: {check_name}",
        })

    return results


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <input.xlsx> <output.xlsx>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    probed = probe(input_path)
    results = run_checks(probed)

    wb = Workbook()
    ws = wb.active
    ws.title = "Checklist Results"

    # Write checklist
    headers = ["Check ID", "Check Name", "Status", "Details"]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.border = BORDER_ALL

    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 45

    for row_idx, result in enumerate(results, start=2):
        ws.cell(row=row_idx, column=1, value=result["id"])
        ws.cell(row=row_idx, column=2, value=result["name"])
        status_cell = ws.cell(row=row_idx, column=3, value=result["status"].value)
        status_cell.fill = PatternFill("solid", fgColor=status_color(result["status"].value))
        ws.cell(row=row_idx, column=4, value=result["details"])

    # Add dashboard
    ws_dash = wb.create_sheet("Dashboard", 0)
    ws_dash.merge_cells("A1:B1")
    cell = ws_dash.cell(row=1, column=1, value="Gate Review Dashboard")
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)

    ws_dash.cell(row=3, column=1, value="Gate Milestone").font = Font(bold=True)
    ws_dash.cell(row=3, column=2, value=probed.gate_milestone)

    ws_dash.cell(row=4, column=1, value="Target ASIL").font = Font(bold=True)
    ws_dash.cell(row=4, column=2, value=probed.target_asil)

    wb.save(str(output_path))
    print(f"Review report saved to {output_path}")


if __name__ == "__main__":
    main()
