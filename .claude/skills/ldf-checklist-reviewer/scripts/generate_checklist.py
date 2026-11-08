"""LDF Checklist Reviewer — orchestrator + xlsx writer with visual dashboard."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from ldf_probe import probe
from check_definitions import CHECKS, CheckDef, CheckResult
from dashboard import build_dashboard


FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"
ORANGE_PARTIAL = "FFD966"
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
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 36


def style_section_banner(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=11, bold=True, color="1F3864")
    cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row].height = 22


def autosize(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = w


def color_assessment(cell, rating, obligation):
    color_map = {"FC": GREEN_OK, "LC": "DAEEF3", "PC": ORANGE_PARTIAL, "NO": RED_BAD, "NA": GREY}
    color = color_map.get(rating)
    if color:
        cell.fill = PatternFill("solid", fgColor=color)
    cell.font = Font(name=FONT_NAME, bold=True, size=10, color="C00000" if rating == "NO" else "000000")
    cell.alignment = Alignment(horizontal="center", vertical="center")


def build_title(wb, ldf_path, probed):
    ws = wb.create_sheet("Title")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "LDF Confirmation Checklist")
    style_title(ws, 3, 5, probed.cluster_name or "(LDF title not detected)")
    fields = [
        ("Project", probed.project),
        ("LDF Document ID", probed.doc_id),
        ("Document Title", "LDF Specification - LIN Cluster Definition"),
        ("LDF Revision", probed.revision),
        ("LDF Status", probed.status or "(not detected)"),
        ("Source LDF", str(ldf_path)),
        ("Checklist Generated", date.today().isoformat()),
        ("Standard", "ISO 17987 / LIN 2.2A"),
        ("Reviewer", "(to be assigned)"),
    ]
    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1
    autosize(ws, {1: 4, 2: 26, 3: 80, 4: 4, 5: 4})


def build_findings(wb, probed, results_by_check):
    """Detailed findings tab."""
    ws = wb.create_sheet("Detailed Findings")

    style_title(ws, 1, 7, "LDF Confirmation Review - Detailed Findings")

    current_category = None
    row = 3

    for check in CHECKS:
        result = results_by_check.get(check.check_id, CheckResult())

        if check.category != current_category:
            style_section_banner(ws, row, 7, f"{check.category}")
            row += 1
            current_category = check.category

        style_header(ws, row, ["Check ID", "Description", "Rating", "Finding", "Recommended Action", "Confidence", "Page/Section"])
        row += 1

        cell_rating = ws.cell(row=row, column=3, value=result.rating)
        color_assessment(cell_rating, result.rating, None)

        ws.cell(row=row, column=1, value=check.check_id).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=check.description)
        ws.cell(row=row, column=4, value=result.finding).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(row=row, column=5, value=result.recommended_action).alignment = Alignment(wrap_text=True, vertical="top")
        ws.cell(row=row, column=6, value=result.confidence)
        ws.cell(row=row, column=7, value=result.page_section)

        ws.row_dimensions[row].height = 36
        row += 1

    autosize(ws, {1: 10, 2: 30, 3: 8, 4: 40, 5: 40, 6: 12, 7: 20})


def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_checklist.py <ldf.xlsx> <output.xlsx>")
        sys.exit(1)

    ldf_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not ldf_path.exists():
        print(f"Error: {ldf_path} not found.")
        sys.exit(1)

    probed = probe(ldf_path)

    # Run all checks
    results_by_check = {}
    for check in CHECKS:
        result = check.verify(probed)
        results_by_check[check.check_id] = result

    # Create workbook
    wb = Workbook()
    wb.remove(wb.active)

    build_title(wb, ldf_path, probed)
    build_dashboard(wb, results_by_check, CHECKS)
    build_findings(wb, probed, results_by_check)

    wb.save(output_path)
    print(f"Generated {output_path}")

    # Summary
    rating_counts = Counter(results_by_check.get(c.check_id, CheckResult()).rating for c in CHECKS)
    summary = {
        "ldf_path": str(ldf_path),
        "cluster_name": probed.cluster_name,
        "checks_total": len(CHECKS),
        "ratings": dict(rating_counts),
        "master_nodes": 1 if probed.master_node else 0,
        "slave_nodes": len(probed.slave_nodes),
        "frames": len(probed.frames),
        "signals": len(probed.signals),
        "schedules": len(probed.schedules),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
