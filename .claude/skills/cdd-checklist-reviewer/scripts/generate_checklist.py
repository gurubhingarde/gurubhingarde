"""CDD Checklist Reviewer — orchestrator + xlsx writer with visual dashboard."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from cdd_probe import ProbedCDD, probe
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
    style_title(ws, 2, 5, "CDD Confirmation Measures Checklist")
    style_title(ws, 3, 5, p.title or "(CDD)")
    fields = [
        ("Project", p.project),
        ("CDD Document ID", p.doc_id),
        ("Revision", p.revision),
        ("Source CDD", p.path),
        ("Checklist Generated", date.today().isoformat()),
        ("Standard", "ISO 14229-1, Vector CANdela"),
        ("Reviewer", "(to be assigned)"),
    ]
    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1
    autosize(ws, {1: 4, 2: 26, 3: 80, 4: 4, 5: 4})


def build_general_info(wb):
    ws = wb.create_sheet("General Info")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 4, "General Information")
    style_header(ws, 5, ["Tab", "Purpose"])
    rows = [
        ("Title", "CDD being assessed"),
        ("General Info", "This tab — TOC"),
        ("Guide", "How to interpret ratings"),
        ("Summary", "Visual dashboard with charts"),
        ("Confirmation Review", "Doc-quality checks"),
        ("CDD Assessment", "Substantive CDD checks"),
        ("Variant Assessment", "Variant coding checks"),
    ]
    for i, (tab, purpose) in enumerate(rows, start=6):
        ws.cell(row=i, column=1, value=tab).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=i, column=2, value=purpose).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 3):
            ws.cell(row=i, column=c).alignment = Alignment(vertical="top", wrap_text=True)
            ws.cell(row=i, column=c).border = BORDER_ALL
    autosize(ws, {1: 30, 2: 80})


def build_guide(wb):
    ws = wb.create_sheet("Guide")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 3, "Guide — How to Use This Checklist")
    style_header(ws, 4, ["#", "Instruction"])
    items = [
        "Assessment column: FC (fully compliant), LC, PC (partially compliant), NO (non-conformance), NA (not applicable), or blank.",
        "Findings show evidence found in the source CDD.",
        "Recommended Actions contain corrective actions.",
        "Confidence: High = directly verified; Medium/Low = inferred/subjective.",
        "Obligation: Shall = mandatory; Should = recommended. NO on Shall = major finding.",
        "Summary tab shows visual dashboard with KPI tiles and charts.",
    ]
    for i, instr in enumerate(items, start=5):
        ws.cell(row=i, column=1, value=i - 4).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=i, column=2, value=instr).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 3):
            ws.cell(row=i, column=c).alignment = Alignment(vertical="top", wrap_text=True)
            ws.cell(row=i, column=c).border = BORDER_ALL
        ws.row_dimensions[i].height = 36
    autosize(ws, {1: 6, 2: 100})


def build_summary(wb, results, project_label):
    ws = wb.create_sheet("Summary")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 6, "Confirmation Measures Summary Dashboard")

    rating_counts = Counter(r[0].rating for r in results if r[0].rating)
    total_checks = len(results)
    major_no = sum(1 for r in results if r[0].rating == "NO" and r[3] == "Shall")

    row = 5
    for rating, count in [("FC", "Fully Compliant"), ("PC", "Partially Compliant"), ("NO", "Non-Conformance")]:
        ws.cell(row=row, column=1, value=count).font = Font(bold=True)
        ws.cell(row=row, column=2, value=rating_counts.get(rating, 0))
        row += 1

    ws.cell(row=row, column=1, value="Major Findings").font = Font(bold=True)
    ws.cell(row=row, column=2, value=major_no)

    autosize(ws, {1: 30, 2: 20})


def build_assessment_section(wb, section_title, results):
    ws = wb.create_sheet(section_title)
    style_title(ws, 2, 7, section_title)
    style_header(ws, 4, ["Check ID", "Check Name", "Assessment", "Finding", "Recommended Action", "Confidence", "Obligation"])

    row = 5
    for check_id, check_name, result, obligation in results:
        ws.cell(row=row, column=1, value=check_id).border = BORDER_ALL
        ws.cell(row=row, column=2, value=check_name).border = BORDER_ALL
        ws.cell(row=row, column=3, value=result.rating).border = BORDER_ALL
        color_assessment(ws.cell(row=row, column=3), result.rating, obligation)
        ws.cell(row=row, column=4, value=result.finding).border = BORDER_ALL
        ws.cell(row=row, column=4).alignment = Alignment(wrap_text=True)
        ws.cell(row=row, column=5, value=result.recommended_action).border = BORDER_ALL
        ws.cell(row=row, column=5).alignment = Alignment(wrap_text=True)
        ws.cell(row=row, column=6, value=result.confidence).border = BORDER_ALL
        ws.cell(row=row, column=6).alignment = Alignment(horizontal="center")
        ws.cell(row=row, column=7, value=obligation).border = BORDER_ALL
        ws.cell(row=row, column=7).alignment = Alignment(horizontal="center")
        ws.row_dimensions[row].height = 36
        row += 1

    autosize(ws, {1: 12, 2: 30, 3: 12, 4: 40, 5: 40, 6: 12, 7: 12})


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <cdd.xlsx> <output_checklist.xlsx>")
        sys.exit(1)

    source_path = sys.argv[1]
    output_path = Path(sys.argv[2])

    p = probe(source_path)

    results = []
    for check_id, check_name, check_func, obligation in CHECKS:
        try:
            result = check_func(p)
            results.append((check_id, check_name, result, obligation))
        except Exception as e:
            results.append((check_id, check_name, CheckResult(rating="", finding=str(e)), obligation))

    wb = Workbook()
    wb.remove(wb.active)

    build_title(wb, p)
    build_general_info(wb)
    build_guide(wb)
    build_summary(wb, results, p.project or "CDD")

    cr_results = [r for r in results if r[0].startswith("CR")]
    ca_results = [r for r in results if r[0].startswith("CA")]
    va_results = [r for r in results if r[0].startswith("VA")]

    build_assessment_section(wb, "Confirmation Review", cr_results)
    build_assessment_section(wb, "CDD Assessment", ca_results)
    build_assessment_section(wb, "Variant Assessment", va_results)

    wb.save(output_path)
    print(f"Checklist written to {output_path}")
    print(json.dumps({"status": "success", "checks_run": len(results), "output": str(output_path)}))


if __name__ == "__main__":
    main()
