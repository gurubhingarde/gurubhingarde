"""
Validation Strategy Checklist — 7-tab checklist from triggering-conditions.xlsx
Usage: python generate_checklist.py <input.xlsx> <output.xlsx>
"""

import json, sys
from collections import Counter
from datetime import date
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from sotif_validation_probe import probe, ProbedValidationStrategy
from check_definitions import CHECKS, CheckDef, CheckResult

try:
    from dashboard import build_dashboard
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
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
    cell.font = Font(name=FONT_NAME, bold=True, size=10, color=("C00000" if rating == "NO" else "000000"))
    cell.alignment = Alignment(horizontal="center", vertical="center")

def build_title(wb, p: ProbedValidationStrategy):
    ws = wb.create_sheet("Title")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "Validation Strategy Checklist")
    style_title(ws, 3, 5, p.title or "(Title not detected)")
    fields = [("Project", p.project), ("Document ID", p.doc_id), ("Revision", p.revision), ("Status", p.status or "(not detected)"), ("Generated", date.today().isoformat()), ("Standard", "ISO 21448 §10-11")]
    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1
    autosize(ws, {1: 4, 2: 26, 3: 70})

def build_general_info(wb):
    ws = wb.create_sheet("General Info")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 4, "General Information")
    rows = [("Title", "Checklist & reviewer info"), ("General Info", "TOC and conventions"), ("Guide", "Rating interpretation"), ("Summary", "Roll-up statistics"), ("Confirmation Review", "Doc-quality checks"), ("Validation Strategy Assessment", "Substantive checks")]
    style_header(ws, 5, ["Tab", "Purpose"])
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
    items = ["Assessment: FC/LC/PC/NO/NA/blank", "Findings: Evidence from source", "Page/Section: Location reference", "Recommended Actions: Corrective steps", "Confidence: High/Medium/Low", "Obligation: Shall/Should", "Summary recomputes when you update", "Reviewer applies final judgment"]
    for i, instr in enumerate(items, start=5):
        ws.cell(row=i, column=1, value=i - 4).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=i, column=2, value=instr).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 3):
            ws.cell(row=i, column=c).alignment = Alignment(vertical="top", wrap_text=True)
            ws.cell(row=i, column=c).border = BORDER_ALL
        ws.row_dimensions[i].height = 28
    autosize(ws, {1: 6, 2: 100})

def build_summary(wb, results, project_label=""):
    ws = wb.create_sheet("Summary")
    if DASHBOARD_AVAILABLE:
        try:
            build_dashboard(ws, results, project_label=project_label, checklist_label="Validation Strategy Checklist")
            return
        except Exception:
            pass
    style_title(ws, 2, 4, "Summary")
    row = 4
    for tab_name in ["CR", "VSA"]:
        if tab_name in results:
            style_section_banner(ws, row, 4, tab_name)
            row += 1
            counts = Counter(r.rating or "PENDING" for _, r in results[tab_name])
            for rating in ["FC", "LC", "PC", "NO", "PENDING"]:
                ws.cell(row=row, column=1, value=rating).font = Font(bold=True)
                ws.cell(row=row, column=2, value=counts.get(rating, 0))
                row += 1
    autosize(ws, {1: 15, 2: 10})

def build_review_tab(wb, sheet_name, tab_code, results):
    ws = wb.create_sheet(sheet_name)
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 8, sheet_name)
    style_header(ws, 4, ["ID", "Section", "Requirement", "Obligation", "Assessment", "Findings", "Page/Section", "Recommended Actions"])
    row = 5
    last_section = ""
    for c, r in results:
        if c.section != last_section:
            style_section_banner(ws, row, 8, c.section)
            row += 1
            last_section = c.section
        ws.cell(row=row, column=1, value=c.id).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=c.section).font = Font(name=FONT_NAME)
        ws.cell(row=row, column=3, value=c.requirement).font = Font(name=FONT_NAME)
        ws.cell(row=row, column=4, value=c.obligation).alignment = Alignment(horizontal="center")
        ws.cell(row=row, column=4).font = Font(name=FONT_NAME, bold=True, color=("C00000" if c.obligation == "Shall" else "9C5700"))
        cell = ws.cell(row=row, column=5, value=r.rating or "—")
        color_assessment(cell, r.rating, c.obligation)
        ws.cell(row=row, column=6, value=r.finding).font = Font(name=FONT_NAME)
        ws.cell(row=row, column=7, value=r.page_section).font = Font(name=FONT_NAME, italic=True, color="404040")
        ws.cell(row=row, column=8, value=r.recommended_action).font = Font(name=FONT_NAME)
        for cc in range(1, 9):
            ws.cell(row=row, column=cc).border = BORDER_ALL
            if cc != 5:
                ws.cell(row=row, column=cc).alignment = Alignment(vertical="top", wrap_text=True)
        row += 1
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:H{row - 1}"
    autosize(ws, {1: 8, 2: 24, 3: 60, 4: 12, 5: 12, 6: 60, 7: 30, 8: 50})

def generate(input_path: str, output_path: str) -> dict:
    p = probe(input_path)
    results = {"CR": [], "VSA": []}
    for c in CHECKS:
        try:
            r = c.verify(p)
        except Exception as exc:
            r = CheckResult(rating="", finding=f"(exception: {exc})", recommended_action="(Re-run)", confidence="Low")
        results[c.tab].append((c, r))

    wb = Workbook()
    wb.remove(wb.active)
    build_title(wb, p)
    build_general_info(wb)
    build_guide(wb)
    build_summary(wb, results, project_label=p.project or p.title or "")
    build_review_tab(wb, "Confirmation Review", "CR", results["CR"])
    build_review_tab(wb, "Validation Strategy Assessment", "VSA", results["VSA"])

    wb.active = 0
    wb.save(output_path)

    summary = {
        "input": input_path, "output": output_path,
        "checks_cr": len(results["CR"]), "checks_vsa": len(results["VSA"]),
        "ratings_cr": dict(Counter(r.rating or "PENDING" for _, r in results["CR"])),
        "ratings_vsa": dict(Counter(r.rating or "PENDING" for _, r in results["VSA"])),
    }
    return summary

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_checklist.py <input.xlsx> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
