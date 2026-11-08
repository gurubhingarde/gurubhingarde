"""Generate SysML block diagram checklist from xlsx."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from block_probe import probe
from check_definitions import CHECKS
from dashboard import build_dashboard


FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"
ORANGE = "FFD966"
GREY = "D0CECE"
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
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 24


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_checklist.py <block_diagram.xlsx> [<output.xlsx>]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2] if len(sys.argv) > 2 else input_file.stem + "_checklist.xlsx")

    # Probe input
    probed = probe(input_file)

    # Run checks
    results = {}
    for check in CHECKS:
        try:
            result = check.verify(probed)
            if check.tab not in results:
                results[check.tab] = []
            results[check.tab].append((check, result))
        except Exception as e:
            print(f"Warning: Check {check.id} failed: {e}")

    # Build workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "0_Title"

    # Title tab
    style_title(ws, 1, 4, "SysML Block Diagram Checklist")
    ws.cell(row=3, column=1, value="Source File").font = Font(bold=True)
    ws.cell(row=3, column=2, value=str(input_file))
    ws.cell(row=4, column=1, value="Blocks Found").font = Font(bold=True)
    ws.cell(row=4, column=2, value=probed.block_count())
    ws.cell(row=5, column=1, value="Ports Found").font = Font(bold=True)
    ws.cell(row=5, column=2, value=probed.port_count())
    ws.cell(row=6, column=1, value="Connectors Found").font = Font(bold=True)
    ws.cell(row=6, column=2, value=probed.connector_count())

    # Confirmation Review tab
    ws_cr = wb.create_sheet("1_Confirmation_Review")
    ws_cr.column_dimensions["A"].width = 15
    ws_cr.column_dimensions["B"].width = 50
    ws_cr.column_dimensions["C"].width = 12
    ws_cr.column_dimensions["D"].width = 40

    style_title(ws_cr, 1, 4, "Confirmation Review")
    style_header(ws_cr, 3, ["Check ID", "Requirement", "Rating", "Finding"])

    row = 4
    for check, result in results.get("CR", []):
        rating_color = GREEN_OK if result.rating == "FC" else RED_BAD if result.rating == "NO" else ORANGE if result.rating == "PC" else GREY

        ws_cr.cell(row=row, column=1, value=check.id).fill = PatternFill("solid", fgColor=rating_color)
        ws_cr.cell(row=row, column=2, value=check.requirement)
        ws_cr.cell(row=row, column=3, value=result.rating).fill = PatternFill("solid", fgColor=rating_color)
        ws_cr.cell(row=row, column=4, value=result.finding)

        for col in range(1, 5):
            ws_cr.cell(row=row, column=col).border = BORDER_ALL
            ws_cr.cell(row=row, column=col).alignment = Alignment(wrap_text=True, vertical="top")

        ws_cr.row_dimensions[row].height = 40
        row += 1

    # Summary tab
    ws_summary = wb.create_sheet("2_Summary")
    ws_summary.column_dimensions["A"].width = 30
    ws_summary.column_dimensions["B"].width = 20

    style_title(ws_summary, 1, 2, "Summary")

    total_checks = sum(len(v) for v in results.values())
    fc_count = sum(1 for checks in results.values() for _, r in checks if r.rating == "FC")
    pc_count = sum(1 for checks in results.values() for _, r in checks if r.rating == "PC")
    no_count = sum(1 for checks in results.values() for _, r in checks if r.rating == "NO")

    ws_summary.cell(row=3, column=1, value="Total Checks").font = Font(bold=True)
    ws_summary.cell(row=3, column=2, value=total_checks)
    ws_summary.cell(row=4, column=1, value="Fully Compliant (FC)").font = Font(bold=True)
    ws_summary.cell(row=4, column=2, value=fc_count).fill = PatternFill("solid", fgColor=GREEN_OK)
    ws_summary.cell(row=5, column=1, value="Non-Compliant (NO)").font = Font(bold=True)
    ws_summary.cell(row=5, column=2, value=no_count).fill = PatternFill("solid", fgColor=RED_BAD)
    ws_summary.cell(row=6, column=1, value="Partially Compliant (PC)").font = Font(bold=True)
    ws_summary.cell(row=6, column=2, value=pc_count).fill = PatternFill("solid", fgColor=ORANGE)

    compliance_pct = (fc_count / total_checks * 100) if total_checks > 0 else 0
    ws_summary.cell(row=8, column=1, value="Compliance %").font = Font(bold=True)
    ws_summary.cell(row=8, column=2, value=f"{compliance_pct:.1f}%")

    wb.save(output_file)
    print(f"Checklist saved to {output_file}")


if __name__ == "__main__":
    main()
