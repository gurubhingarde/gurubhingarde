"""A2L Checklist Reviewer — orchestrator + xlsx writer with visual dashboard."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, PieChart, Reference

from a2l_probe import probe
from check_definitions import execute_checks, CHECKS
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
    style_title(ws, 2, 5, "A2L Confirmation Review Checklist")
    style_title(ws, 3, 5, p.title or "(A2L title not detected)")
    fields = [
        ("Author", p.author or "(Not recorded)"),
        ("Revision", p.revision or "(Not recorded)"),
        ("Review Date", str(date.today())),
        ("ECU Part Number", p.ecu_part_number or "(Not recorded)"),
    ]
    row = 5
    for k, v in fields:
        ws.cell(row=row, column=1, value=k).font = Font(name=FONT_NAME, bold=True, size=11)
        ws.cell(row=row, column=2, value=v)
        row += 1
    autosize(ws, {1: 20, 2: 40})


def build_checklist_detail(wb, results, check_defs_by_id):
    """Build detailed checklist tabs per section."""
    by_section = defaultdict(list)
    for check_id, check_def in check_defs_by_id.items():
        result = results.get(check_id)
        if result:
            by_section[check_def.section].append((check_id, check_def, result))

    section_tabs = {
        "Document Structure": "Confirmation Review",
        "Title & Metadata": "Confirmation Review",
        "Document Control": "Confirmation Review",
        "Catalog Completeness": "Confirmation Review",
        "Conversion Methods": "Confirmation Review",
        "Axis Definitions": "Confirmation Review",
        "Record Layouts": "Confirmation Review",
        "Function Hierarchy": "Confirmation Review",
        "Group Hierarchy": "Confirmation Review",
        "Memory Mapping": "Confirmation Review",
        "Validation Rules": "Confirmation Review",
        "Characteristic Types": "A2L Objects",
        "Functions": "A2L Objects",
        "Groups": "A2L Objects",
        "ECU Identity": "A2L Objects",
        "Address Bounds": "Memory Validation",
        "Address Overlap": "Memory Validation",
        "Alignment": "Memory Validation",
        "Size Consistency": "Memory Validation",
        "Memory Footprint": "Memory Validation",
        "Linear Parameters": "Conversion Methods",
        "Formula Syntax": "Conversion Methods",
        "Unit Consistency": "Conversion Methods",
    }

    for tab_name in set(section_tabs.values()):
        ws = wb.create_sheet(tab_name)
        style_header(ws, 1, ["Check ID", "Section", "Requirement", "Rating", "Finding", "Recommended Action", "Confidence"])
        row = 2
        for section, items in sorted(by_section.items()):
            if section_tabs.get(section) != tab_name:
                continue
            for check_id, check_def, result in items:
                ws.cell(row=row, column=1, value=check_id)
                ws.cell(row=row, column=2, value=section)
                ws.cell(row=row, column=3, value=check_def.requirement)
                cell_rating = ws.cell(row=row, column=4, value=result.rating)
                color_assessment(cell_rating, result.rating, check_def.obligation)
                ws.cell(row=row, column=5, value=result.finding)
                ws.cell(row=row, column=6, value=result.recommended_action)
                ws.cell(row=row, column=7, value=result.confidence)
                row += 1
        autosize(ws, {1: 10, 2: 16, 3: 28, 4: 8, 5: 35, 6: 30, 7: 11})


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <a2l_workbook.xlsx> <output.xlsx>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Error: Input file {input_path} not found")
        sys.exit(1)

    # Probe the A2L workbook
    p = probe(str(input_path))

    # Execute all checks
    results = execute_checks(p)

    # Create check definitions lookup
    check_defs_by_id = {c.id: c for c in CHECKS}

    # Create workbook
    wb = Workbook()
    wb.remove(wb.active)

    # Title sheet
    build_title(wb, p)

    # Build dashboard (Summary tab)
    build_dashboard(wb, results, check_defs_by_id)

    # Detail tabs per section
    build_checklist_detail(wb, results, check_defs_by_id)

    # Save
    wb.save(output_path)
    print(f"A2L checklist generated: {output_path}")


if __name__ == "__main__":
    main()
