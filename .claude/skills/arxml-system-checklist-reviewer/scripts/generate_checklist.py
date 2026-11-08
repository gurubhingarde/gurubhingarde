"""ARXML System Checklist Reviewer — orchestrator + xlsx writer with dashboard."""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from arxml_probe import probe, ProbedARXML
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


def build_title(wb, p):
    ws = wb.create_sheet("Title")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "ARXML System Specification Checklist")
    style_title(ws, 3, 5, p.title or "(System title not detected)")
    fields = [
        ("Project", p.project),
        ("System Document ID", p.doc_id),
        ("Document Title", "ARXML System Specification Audit Checklist"),
        ("System Revision", p.revision),
        ("System Status", p.status or "(not detected)"),
        ("Source System", p.path),
        ("Checklist Generated", date.today().isoformat()),
        ("Standard", "AUTOSAR Classic Platform R22-11+"),
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
    style_section_banner(ws, 4, 4, "Tabs in this Checklist")
    style_header(ws, 5, ["Tab", "Purpose"])
    rows = [
        ("Title", "System being assessed and reviewer info"),
        ("General Info", "This tab — TOC and conventions"),
        ("Guide", "How to interpret ratings"),
        ("Summary", "Visual dashboard with KPIs and findings"),
        ("Confirmation Review", "Document-quality checks"),
        ("Technical Assessment", "ARXML-specific conformance checks"),
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
        "Each check has an Assessment column. Possible values: FC (Fully Conformant), LC (Largely), PC (Partially), NO (Not), NA (Not Applicable), or blank (pending).",
        "Findings show evidence the reviewer found in the source ARXML system workbook. Auto-suggested findings are marked and need human judgment.",
        "Recommended Actions suggest corrective steps. The checklist does NOT modify the source ARXML.",
        "Confidence: High = directly verified; Medium = inferred; Low = subjective.",
        "Obligation: Shall = mandatory; Should = recommended. NO on Shall = major non-conformance.",
        "Summary tab is a visual dashboard with KPI tiles, pie chart of compliance, bar chart by section.",
        "Acceptance requires no major non-conformances (NO on Shall) and all composition bindings complete.",
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
    style_title(ws, 2, 5, "Summary — Audit Dashboard")

    # KPI tiles
    total_checks = len(results)
    fc_count = sum(1 for r in results if r[1].rating == "FC")
    lc_count = sum(1 for r in results if r[1].rating == "LC")
    pc_count = sum(1 for r in results if r[1].rating == "PC")
    no_count = sum(1 for r in results if r[1].rating == "NO")
    na_count = sum(1 for r in results if r[1].rating == "NA")

    kpi_row = 4
    kpis = [
        ("Total Checks", total_checks, ""),
        ("Fully Conformant", fc_count, GREEN_OK),
        ("Partially Conformant", pc_count, ORANGE_PARTIAL),
        ("Not Conformant", no_count, RED_BAD),
        ("Not Applicable", na_count, GREY),
    ]

    for label, value, color in kpis:
        ws.cell(row=kpi_row, column=1, value=label).font = Font(name=FONT_NAME, bold=True, size=11)
        cell = ws.cell(row=kpi_row, column=2, value=value)
        cell.font = Font(name=FONT_NAME, bold=True, size=14)
        if color:
            cell.fill = PatternFill("solid", fgColor=color)
        kpi_row += 1

    # Findings table
    findings_row = kpi_row + 2
    style_section_banner(ws, findings_row, 5, "Key Findings")
    findings_row += 1

    style_header(ws, findings_row, ["Check", "Category", "Rating", "Finding", "Recommended Action"])
    findings_row += 1

    for check_def, result in results:
        if result.rating in ("NO", "PC"):
            ws.cell(row=findings_row, column=1, value=check_def.code).font = Font(name=FONT_NAME, size=10)
            ws.cell(row=findings_row, column=2, value=check_def.category).font = Font(name=FONT_NAME, size=10)
            cell = ws.cell(row=findings_row, column=3, value=result.rating)
            color_assessment(cell, result.rating, check_def.obligation)
            ws.cell(row=findings_row, column=4, value=result.finding).font = Font(name=FONT_NAME, size=10)
            ws.cell(row=findings_row, column=4).alignment = Alignment(wrap_text=True, vertical="top")
            ws.cell(row=findings_row, column=5, value=result.recommended_action).font = Font(name=FONT_NAME, size=10)
            ws.cell(row=findings_row, column=5).alignment = Alignment(wrap_text=True, vertical="top")
            for col in range(1, 6):
                ws.cell(row=findings_row, column=col).border = BORDER_ALL
            ws.row_dimensions[findings_row].height = 24
            findings_row += 1

    autosize(ws, {1: 10, 2: 16, 3: 8, 4: 50, 5: 40})


def build_confirmation_review(wb, results):
    ws = wb.create_sheet("Confirmation Review")

    style_header(ws, 1, ["Code", "Check", "Obligation", "Assessment", "Finding", "Recommended Action", "Confidence"])

    row = 2
    for check_def, result in results:
        if check_def.category == "Confirmation":
            ws.cell(row=row, column=1, value=check_def.code).font = Font(name=FONT_NAME, size=9)
            ws.cell(row=row, column=2, value=check_def.title).font = Font(name=FONT_NAME, size=9)
            ws.cell(row=row, column=3, value=check_def.obligation).font = Font(name=FONT_NAME, size=9)

            cell = ws.cell(row=row, column=4, value=result.rating)
            color_assessment(cell, result.rating, check_def.obligation)

            ws.cell(row=row, column=5, value=result.finding).font = Font(name=FONT_NAME, size=9)
            ws.cell(row=row, column=5).alignment = Alignment(wrap_text=True, vertical="top")

            ws.cell(row=row, column=6, value=result.recommended_action).font = Font(name=FONT_NAME, size=9)
            ws.cell(row=row, column=6).alignment = Alignment(wrap_text=True, vertical="top")

            ws.cell(row=row, column=7, value=result.confidence).font = Font(name=FONT_NAME, size=9)

            for col in range(1, 8):
                ws.cell(row=row, column=col).border = BORDER_ALL
            ws.row_dimensions[row].height = 28
            row += 1

    autosize(ws, {1: 8, 2: 20, 3: 12, 4: 8, 5: 35, 6: 35, 7: 10})


def build_technical_assessment(wb, results):
    ws = wb.create_sheet("Technical Assessment")

    style_header(ws, 1, ["Code", "Check", "Obligation", "Assessment", "Finding", "Recommended Action", "Confidence"])

    row = 2
    for check_def, result in results:
        if check_def.category == "Technical":
            ws.cell(row=row, column=1, value=check_def.code).font = Font(name=FONT_NAME, size=9)
            ws.cell(row=row, column=2, value=check_def.title).font = Font(name=FONT_NAME, size=9)
            ws.cell(row=row, column=3, value=check_def.obligation).font = Font(name=FONT_NAME, size=9)

            cell = ws.cell(row=row, column=4, value=result.rating)
            color_assessment(cell, result.rating, check_def.obligation)

            ws.cell(row=row, column=5, value=result.finding).font = Font(name=FONT_NAME, size=9)
            ws.cell(row=row, column=5).alignment = Alignment(wrap_text=True, vertical="top")

            ws.cell(row=row, column=6, value=result.recommended_action).font = Font(name=FONT_NAME, size=9)
            ws.cell(row=row, column=6).alignment = Alignment(wrap_text=True, vertical="top")

            ws.cell(row=row, column=7, value=result.confidence).font = Font(name=FONT_NAME, size=9)

            for col in range(1, 8):
                ws.cell(row=row, column=col).border = BORDER_ALL
            ws.row_dimensions[row].height = 28
            row += 1

    autosize(ws, {1: 8, 2: 20, 3: 12, 4: 8, 5: 35, 6: 35, 7: 10})


def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_checklist.py <arxml_system.xlsx> <output_checklist.xlsx>")
        sys.exit(1)

    source_file = sys.argv[1]
    output_file = sys.argv[2]

    if not Path(source_file).exists():
        print(f"Error: Source file {source_file} not found.")
        sys.exit(1)

    p = probe(source_file)

    # Run all checks
    results = []
    for check_def in CHECKS:
        try:
            result = check_def.checker(p)
        except Exception as e:
            result = CheckResult(rating="", finding=f"Check error: {e}", confidence="Low")
        results.append((check_def, result))

    # Build workbook
    wb = Workbook()
    if wb.sheetnames and wb.sheetnames[0] == "Sheet":
        wb.remove(wb.active)

    build_title(wb, p)
    build_general_info(wb)
    build_guide(wb)
    build_summary(wb, results, p.project or "System")
    build_confirmation_review(wb, results)
    build_technical_assessment(wb, results)

    wb.save(output_file)
    print(f"ARXML system checklist generated: {output_file}")


if __name__ == "__main__":
    main()
