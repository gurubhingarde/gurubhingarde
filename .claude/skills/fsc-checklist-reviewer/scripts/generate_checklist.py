"""FSC Checklist Reviewer — orchestrator + xlsx writer with visual dashboard."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from fsc_probe import ProbedFSC, probe
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


def build_title(wb, p: ProbedFSC):
    ws = wb.create_sheet("Title")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "FSC Confirmation Measures Checklist")
    style_title(ws, 3, 5, p.title or "(FSC title not detected)")
    fields = [
        ("Project", p.project),
        ("FSC Document ID", p.doc_id),
        ("Document Title", "Confirmation Measures - FSC (Functional Safety Concept)"),
        ("FSC Revision", p.revision),
        ("FSC Status", p.status or "(not detected)"),
        ("Source FSC", p.path),
        ("Linked HARA", p.linked_hara or "(not detected)"),
        ("Checklist Generated", date.today().isoformat()),
        ("Standard", "ISO 26262:2018 Part 3 §8 (FSC) and Part 8 §9 (verification)"),
        ("Reviewer", "(to be assigned — independence per ISO 26262-2 Table 1)"),
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
        ("Title", "FSC being assessed and reviewer info"),
        ("General Info", "This tab — TOC and document conventions"),
        ("Guide", "How to interpret ratings"),
        ("Summary", "Visual dashboard with charts and findings"),
        ("Confirmation Review", "Generic doc-quality checks (ISO 26262-8 §10)"),
        ("Functional Safety Assessment", "FSC substantive checks (ISO 26262-3 §8)"),
        ("Verification Assessment", "FSC verification checks (ISO 26262-8 §9 and FSC-specific)"),
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
        "Each check has an Assessment column. Possible values: FC (Fully Compliant), LC (Largely Compliant), PC (Partially Compliant), NO (Not Compliant), NA (Not Applicable), or blank (pending reviewer judgment).",
        "Findings cells contain evidence the auto-reviewer found in the source FSC. Cells marked '(Auto-suggest, requires reviewer judgment)' need a human pass.",
        "Recommended Actions cells contain corrective actions for any non-compliances. They do NOT modify the source FSC — the analyst decides whether to fix the FSC and re-run.",
        "Confidence: High = directly verified; Medium = inferred with caveat; Low = subjective or external artifact required.",
        "Obligation: Shall = mandatory; Should = recommended. NO on a Shall = major non-conformance.",
        "Summary tab is a visual dashboard with KPI tiles, pie chart of rating distribution, bar chart of compliance % by tab, stacked bar of section-level breakdown, and a findings table.",
        "Acceptance of the FSC requires that no major non-conformances remain and that ASIL decomposition (if applied) is supported by documented independence evidence per ISO 26262-9 §6.",
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
    build_dashboard(ws, results, project_label=project_label, checklist_label="FSC Confirmation Measures")


def build_review_tab(wb, sheet_name, tab_code, results):
    ws = wb.create_sheet(sheet_name)
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 8, sheet_name)
    style_header(ws, 4, ["ID", "Section", "Requirement", "Obligation", "Assessment", "Findings", "Page/Section in FSC", "Recommended Actions"])

    row = 5
    last_section = ""
    for c, r in results:
        if c.section != last_section:
            style_section_banner(ws, row, 8, c.section)
            row += 1
            last_section = c.section
        ws.cell(row=row, column=1, value=c.id).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=row, column=2, value=c.section).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=row, column=3, value=c.requirement).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=row, column=4, value=c.obligation).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=row, column=4).font = Font(name=FONT_NAME, size=10, bold=True, color=("C00000" if c.obligation == "Shall" else "9C5700"))
        cell = ws.cell(row=row, column=5, value=r.rating or "—")
        color_assessment(cell, r.rating, c.obligation)
        ws.cell(row=row, column=6, value=r.finding).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=row, column=7, value=r.page_section).font = Font(name=FONT_NAME, size=10, italic=True, color="404040")
        ws.cell(row=row, column=8, value=r.recommended_action).font = Font(name=FONT_NAME, size=10)

        for cc in range(1, 9):
            ws.cell(row=row, column=cc).border = BORDER_ALL
            if cc != 5:
                cell = ws.cell(row=row, column=cc)
                cell.alignment = Alignment(vertical="top", wrap_text=True)
        row += 1

    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:H{row - 1}"
    autosize(ws, {1: 8, 2: 26, 3: 60, 4: 12, 5: 12, 6: 60, 7: 30, 8: 50})


def generate(fsc_path: str, output_path: str) -> dict:
    p = probe(fsc_path)
    results: dict[str, list] = {"CR": [], "FSA": [], "VA": []}
    for c in CHECKS:
        try:
            r = c.verify(p)
        except Exception as exc:
            r = CheckResult(rating="", finding=f"(check raised exception: {exc})", recommended_action="(Re-run after fixing data)", confidence="Low")
        results[c.tab].append((c, r))

    wb = Workbook()
    wb.remove(wb.active)
    build_title(wb, p)
    build_general_info(wb)
    build_guide(wb)
    build_summary(wb, results, project_label=p.project or p.title or "")
    build_review_tab(wb, "Confirmation Review", "CR", results["CR"])
    build_review_tab(wb, "Functional Safety Assessment", "FSA", results["FSA"])
    build_review_tab(wb, "Verification Assessment", "VA", results["VA"])
    wb.active = 0
    wb.save(output_path)

    return {
        "fsc_input": fsc_path,
        "checklist_output": output_path,
        "is_fsc_builder_format": p.is_fsc_builder_format,
        "n_safety_goals": len(p.safety_goals),
        "n_fsrs": len(p.fsrs),
        "n_allocations": len(p.allocations),
        "n_decompositions": sum(1 for a in p.allocations if a.decomposition and "None" not in a.decomposition),
        "checks_by_tab": {tab: len(rows) for tab, rows in results.items()},
        "ratings_by_tab": {tab: dict(Counter(r.rating or "PENDING" for _, r in rows)) for tab, rows in results.items()},
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_checklist.py <fsc.xlsx> <output_checklist.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
