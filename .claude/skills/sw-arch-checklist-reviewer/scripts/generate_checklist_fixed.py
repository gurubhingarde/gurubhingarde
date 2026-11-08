"""
SW Architecture Checklist Reviewer — generates completed checklist from any SW Architecture xlsx.

Usage:
    python generate_checklist.py <sw_arch.xlsx> <output_checklist.xlsx>
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from sw_arch_probe import ProbedSwArch, probe
from check_definitions import CHECKS, CheckDef, CheckResult
from dashboard import build_dashboard


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

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
    color_map = {
        "FC": GREEN_OK,
        "LC": "DAEEF3",
        "PC": ORANGE_PARTIAL,
        "NO": RED_BAD,
        "NA": GREY,
    }
    color = color_map.get(rating)
    if color:
        cell.fill = PatternFill("solid", fgColor=color)
    cell.font = Font(name=FONT_NAME, bold=True, size=10)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    if rating == "NO":
        cell.font = Font(name=FONT_NAME, bold=True, size=10, color="C00000")


def build_title(wb, p: ProbedSwArch):
    ws = wb.create_sheet("Title")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "SW Architecture Checklist Reviewer")
    style_title(ws, 3, 5, p.title or "(SW Architecture title not detected)")

    fields = [
        ("Project Number & Name", p.project),
        ("Document ID (SW Architecture)", p.doc_id),
        ("Document Title", "SW Architecture Checklist"),
        ("SW Architecture Revision", p.revision),
        ("SW Architecture Status", p.status or "(not detected)"),
        ("Source SW Architecture", p.path),
        ("Checklist Generated", date.today().isoformat()),
        ("Standard", "ISO 26262:2018 Part 6 (SW Architecture)"),
        ("Reviewer", "(to be assigned)"),
    ]
    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1
    autosize(ws, {1: 4, 2: 26, 3: 70, 4: 4, 5: 4})


def build_general_info(wb):
    ws = wb.create_sheet("General Info")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 4, "General Information")
    style_section_banner(ws, 4, 4, "Tabs in this Checklist")
    style_header(ws, 5, ["Tab", "Purpose"])
    rows = [
        ("Title", "SW Architecture being assessed and reviewer info"),
        ("General Info", "This tab"),
        ("Guide", "How to interpret ratings"),
        ("Summary", "Statistical roll-up with dashboard"),
        ("Confirmation Review", "14 doc-quality checks"),
        ("SW Architecture Assessment", "12 SW substantive checks"),
        ("Verification Assessment", "5 verification checks"),
    ]
    for i, (tab, purpose) in enumerate(rows, start=6):
        ws.cell(row=i, column=1, value=tab).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=i, column=2, value=purpose).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 3):
            ws.cell(row=i, column=c).border = BORDER_ALL
    autosize(ws, {1: 20, 2: 50})


def build_guide(wb):
    ws = wb.create_sheet("Guide")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "How to Interpret This Checklist")
    style_section_banner(ws, 4, 5, "Rating Key")
    rows = [
        ("FC", "Fully Compliant", "Requirement met"),
        ("LC", "Low Confidence", "Requirement met, limited evidence"),
        ("PC", "Partially Compliant", "Requirement partially met"),
        ("NO", "Non-Compliant", "Requirement not met"),
        ("NA", "Not Applicable", "Not applicable to this artifact"),
    ]
    style_header(ws, 5, ["Rating", "Status", "Meaning"])
    for i, (rating, status, meaning) in enumerate(rows, start=6):
        ws.cell(row=i, column=1, value=rating).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=i, column=2, value=status).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=i, column=3, value=meaning).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 4):
            ws.cell(row=i, column=c).border = BORDER_ALL
    autosize(ws, {1: 12, 2: 20, 3: 60, 4: 4, 5: 4})


def build_summary(wb, results):
    ws = wb.create_sheet("Summary")
    build_dashboard(ws, 1, results)


def build_checklist_tab(wb, tab_name, results):
    ws = wb.create_sheet(tab_name)
    style_title(ws, 1, 6, tab_name)
    style_header(ws, 3, ["Check ID", "Section", "Requirement", "Obligation", "Assessment", "Finding", "Recommended Action"])
    row = 4
    for check_def, check_result in results:
        ws.cell(row=row, column=1, value=check_def.id).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=row, column=2, value=check_def.section).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=row, column=3, value=check_def.requirement).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=row, column=4, value=check_def.obligation).font = Font(name=FONT_NAME, size=9)

        assessment_cell = ws.cell(row=row, column=5, value=check_result.rating or "")
        color_assessment(assessment_cell, check_result.rating, check_def.obligation)

        ws.cell(row=row, column=6, value=check_result.finding).font = Font(name=FONT_NAME, size=9)
        ws.cell(row=row, column=7, value=check_result.recommended_action).font = Font(name=FONT_NAME, size=9)

        for col in range(1, 8):
            ws.cell(row=row, column=col).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            ws.cell(row=row, column=col).border = BORDER_ALL
            if row % 2 == 0 and col in [6, 7]:
                ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

        ws.row_dimensions[row].height = 40
        row += 1

    autosize(ws, {1: 10, 2: 18, 3: 35, 4: 10, 5: 12, 6: 35, 7: 35})


def generate_checklist(sw_arch_xlsx, output_xlsx):
    print(f"[*] Probing SW Architecture: {sw_arch_xlsx}")
    p = probe(sw_arch_xlsx)

    print(f"[*] Running {len(CHECKS)} checks...")
    results = {}
    for check in CHECKS:
        if check.tab not in results:
            results[check.tab] = []
        check_result = check.verify(p)
        results[check.tab].append((check, check_result))

    print(f"[*] Building checklist workbook...")
    wb = Workbook()
    wb.remove(wb.active)

    build_title(wb, p)
    build_general_info(wb)
    build_guide(wb)
    build_summary(wb, results)

    for tab_name in ["Confirmation Review", "SW Architecture Assessment", "Verification Assessment"]:
        if tab_name in results:
            build_checklist_tab(wb, tab_name, results[tab_name])

    print(f"[*] Saving to: {output_xlsx}")
    wb.save(output_xlsx)

    all_results = [r[1] for tab_results in results.values() for r in tab_results]
    counter = Counter([r.rating for r in all_results if r.rating])

    summary = {
        "tabs": len(results),
        "total_checks": len(all_results),
        "ratings": dict(counter),
        "breakdown_by_tab": {
            tab: dict(Counter([r[1].rating for r in tab_results if r[1].rating]))
            for tab, tab_results in results.items()
        },
    }
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <sw_arch.xlsx> <output_checklist.xlsx>")
        sys.exit(1)

    sw_arch_xlsx = sys.argv[1]
    output_xlsx = sys.argv[2]

    if not Path(sw_arch_xlsx).exists():
        print(f"Error: {sw_arch_xlsx} not found")
        sys.exit(1)

    generate_checklist(sw_arch_xlsx, output_xlsx)
