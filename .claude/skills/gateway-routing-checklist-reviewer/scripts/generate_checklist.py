"""Gateway Routing Checklist Reviewer — orchestrator + xlsx writer with visual dashboard."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from gateway_probe import ProbedGateway, probe
from check_definitions import CHECKS, CheckResult
from dashboard import build_dashboard


FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
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


def build_title(wb, p):
    ws = wb.create_sheet("Title")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "Gateway Routing Checklist")
    style_title(ws, 3, 5, p.title or "(Gateway Routing Specification)")

    fields = [
        ("Document Under Review", Path(p.filepath).name),
        ("Review Date", str(date.today())),
        ("Author (Original)", p.author or "(Not specified)"),
        ("Approver (Original)", p.approver or "(Not specified)"),
        ("Revision", p.revision or "(Not specified)"),
    ]

    row = 5
    for label, value in fields:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

    autosize(ws, {1: 25, 2: 40})


def build_summary(wb, results):
    ws = wb.create_sheet("Summary", 1)
    style_title(ws, 1, 4, "Checklist Summary")

    ratings = Counter(r.rating for r in results)
    row = 3

    summary_data = [
        ("Fully Compliant (FC)", ratings.get("FC", 0), GREEN_OK),
        ("Partially Compliant (PC)", ratings.get("PC", 0), ORANGE_PARTIAL),
        ("Non-Compliant (NO)", ratings.get("NO", 0), RED_BAD),
        ("Not Applicable (NA)", ratings.get("NA", 0), GREY),
    ]

    for label, count, color in summary_data:
        cell_label = ws.cell(row=row, column=1, value=label)
        cell_label.font = Font(name=FONT_NAME, bold=True)
        cell_count = ws.cell(row=row, column=2, value=count)
        cell_count.fill = PatternFill("solid", fgColor=color)
        cell_count.font = Font(name=FONT_NAME, bold=True, size=12)
        cell_count.alignment = Alignment(horizontal="center", vertical="center")
        row += 1

    total_checks = len(results)
    fc_count = ratings.get("FC", 0)
    percent_pass = (fc_count / total_checks * 100) if total_checks > 0 else 0

    row += 1
    cell = ws.cell(row=row, column=1, value=f"Compliance: {percent_pass:.0f}% ({fc_count}/{total_checks})")
    cell.font = Font(name=FONT_NAME, bold=True, size=11)

    autosize(ws, {1: 30, 2: 12})


def build_checklist(wb, p, results):
    ws = wb.create_sheet("Checklist", 2)
    style_title(ws, 1, 6, "Detailed Checklist")

    headers = ["Check ID", "Finding", "Rating", "Page/Section", "Recommended Action", "Confidence"]
    style_header(ws, 2, headers)

    row = 3
    for i, result in enumerate(results, start=1):
        check_id = f"GR-{i:02d}"
        ws.cell(row=row, column=1, value=check_id).border = BORDER_ALL
        ws.cell(row=row, column=2, value=result.finding).border = BORDER_ALL
        cell_rating = ws.cell(row=row, column=3, value=result.rating)
        color_assessment(cell_rating, result.rating, "")
        ws.cell(row=row, column=4, value=result.page_section or "").border = BORDER_ALL
        ws.cell(row=row, column=5, value=result.recommended_action or "").border = BORDER_ALL
        ws.cell(row=row, column=6, value=result.confidence or "").border = BORDER_ALL
        ws.row_dimensions[row].height = 30
        row += 1

    autosize(ws, {1: 10, 2: 40, 3: 8, 4: 20, 5: 40, 6: 12})


def run_all_checks(p) -> list[CheckResult]:
    results = []
    for check_id, check_fn in CHECKS.items():
        result = check_fn(p)
        results.append(result)
    return results


def generate_checklist_workbook(filepath: str) -> Workbook:
    p = probe(filepath)
    results = run_all_checks(p)

    wb = Workbook()
    wb.remove(wb.active)

    build_title(wb, p)
    build_summary(wb, results)
    build_checklist(wb, p, results)
    build_dashboard(wb, p, results)

    return wb


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_checklist.py <gateway.xlsx> [output.xlsx]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path.replace(".xlsx", "_checklist.xlsx")

    wb = generate_checklist_workbook(input_path)
    wb.save(output_path)
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
