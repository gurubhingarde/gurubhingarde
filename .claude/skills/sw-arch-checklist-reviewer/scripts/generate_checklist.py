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
    cell.font = Font(name=FONT_NAME, bold=True, size=10)
    cell.alignment = Alignment(horizontal="center", vertical="center")


def build_title(wb, p: ProbedSwArch):
    ws = wb.create_sheet("Title")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "SW Architecture Checklist Reviewer")
    style_title(ws, 3, 5, p.title or "(SW Architecture title not detected)")
    row = 6
    for label, value in [("Project", p.project), ("Doc ID", p.doc_id), ("Title", "Checklist"), ("Revision", p.revision), ("Status", p.status or ""), ("Source", p.path), ("Generated", str(date.today())), ("Standard", "ISO 26262-6 §7"), ("Reviewer", "(assign)")]:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = Font(name=FONT_NAME, size=10)
        row += 1
    autosize(ws, {1: 4, 2: 26, 3: 70})


def build_general_info(wb):
    ws = wb.create_sheet("General Info")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 4, "General Information")
    style_section_banner(ws, 4, 4, "Tabs in this Checklist")
    style_header(ws, 5, ["Tab", "Purpose"])
    for i, (tab, purpose) in enumerate([("Title", "Architecture info"), ("General Info", "This tab"), ("Guide", "Ratings legend"), ("Summary", "Roll-up"), ("Confirmation Review", "14 doc checks"), ("SW Architecture Assessment", "12 arch checks"), ("Verification Assessment", "5 verification checks")], start=6):
        ws.cell(row=i, column=1, value=tab).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=i, column=2, value=purpose).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 3):
            ws.cell(row=i, column=c).border = BORDER_ALL
    autosize(ws, {1: 30, 2: 40})


def build_guide(wb):
    ws = wb.create_sheet("Guide")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 3, "How to Interpret This Checklist")
    style_section_banner(ws, 4, 3, "Rating Key")
    style_header(ws, 5, ["Rating", "Meaning"])
    for i, (rating, meaning) in enumerate([("FC", "Fully Compliant"), ("LC", "Low Confidence"), ("PC", "Partially Compliant"), ("NO", "Non-Compliant"), ("NA", "Not Applicable")], start=6):
        ws.cell(row=i, column=1, value=rating).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=i, column=2, value=meaning).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 3):
            ws.cell(row=i, column=c).border = BORDER_ALL
    autosize(ws, {1: 12, 2: 50})


def build_summary(wb, results):
    ws = wb.create_sheet("Summary")
    style_title(ws, 1, 3, "Summary")
    all_results = [r[1] for tab_results in results.values() for r in tab_results]
    counter = Counter([r.rating for r in all_results if r.rating])
    style_section_banner(ws, 3, 3, "Ratings Summary")
    style_header(ws, 4, ["Rating", "Count"])
    row = 5
    for rating in ["FC", "LC", "PC", "NO", "NA"]:
        ws.cell(row=row, column=1, value=rating).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=row, column=2, value=counter.get(rating, 0)).font = Font(name=FONT_NAME, size=10)
        for col in range(1, 3):
            ws.cell(row=row, column=col).border = BORDER_ALL
        row += 1
    autosize(ws, {1: 12, 2: 10})


def build_checklist_tab(wb, tab_name, results):
    ws = wb.create_sheet(tab_name)
    style_title(ws, 1, 6, tab_name)
    style_header(ws, 3, ["ID", "Section", "Requirement", "Obligation", "Assessment", "Finding"])
    row = 4
    for check_def, check_result in results:
        ws.cell(row=row, column=1, value=check_def.id).font = Font(name=FONT_NAME, size=9, bold=True)
        ws.cell(row=row, column=2, value=check_def.section).font = Font(name=FONT_NAME, size=9)
        ws.cell(row=row, column=3, value=check_def.requirement).font = Font(name=FONT_NAME, size=9)
        ws.cell(row=row, column=4, value=check_def.obligation).font = Font(name=FONT_NAME, size=8)
        cell = ws.cell(row=row, column=5, value=check_result.rating or "")
        color_assessment(cell, check_result.rating, check_def.obligation)
        ws.cell(row=row, column=6, value=check_result.finding).font = Font(name=FONT_NAME, size=8)
        for col in range(1, 7):
            ws.cell(row=row, column=col).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            ws.cell(row=row, column=col).border = BORDER_ALL
        ws.row_dimensions[row].height = 30
        row += 1
    autosize(ws, {1: 8, 2: 15, 3: 30, 4: 8, 5: 10, 6: 30})


def generate_checklist(sw_arch_xlsx, output_xlsx):
    print(f"[*] Probing: {sw_arch_xlsx}")
    p = probe(sw_arch_xlsx)
    print(f"[*] Running {len(CHECKS)} checks...")
    results = {}
    for check in CHECKS:
        if check.tab not in results:
            results[check.tab] = []
        check_result = check.verify(p)
        results[check.tab].append((check, check_result))
    print(f"[*] Building workbook...")
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
    summary = {"tabs": len(results), "total_checks": len(all_results), "ratings": dict(counter), "breakdown_by_tab": {tab: dict(Counter([r[1].rating for r in tab_results if r[1].rating])) for tab, tab_results in results.items()}}
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
