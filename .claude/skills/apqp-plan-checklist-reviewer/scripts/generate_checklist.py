"""
APQP Plan Checklist Reviewer — generates a completed checklist from APQP Plan xlsx.

Usage:
    python generate_checklist.py <apqp_plan.xlsx> <output_checklist.xlsx>

Methodology:
- Probe APQP Plan content (works on apqp-plan-builder format and others).
- Run each canonical checklist requirement with project-specific verification logic.
- Write a 7-tab xlsx (Title, General Info, Guide, Summary, Confirmation Review, APQPA, VA).
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

from apqp_probe import ProbedAPQPPlan, probe
from check_definitions import CHECKS, CheckDef, CheckResult
from dashboard import build_dashboard


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title(wb, p: ProbedAPQPPlan, output_path: str):
    ws = wb.create_sheet("Title")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "APQP Plan Checklist Reviewer")
    style_title(ws, 3, 5, p.title or "(APQP Plan title not detected)")

    fields = [
        ("Project Number & Name", p.project or "(not detected)"),
        ("Program", p.program or "(not detected)"),
        ("Supplier", p.supplier or "(not detected)"),
        ("Customer", p.customer or "(not detected)"),
        ("Document Title", "APQP Plan Confirmation Measures Checklist"),
        ("Revision", p.revision or "(not detected)"),
        ("Status", p.status or "(not detected)"),
        ("Source APQP Plan", p.path),
        ("Checklist Generated", date.today().isoformat()),
        ("Standard", "AIAG APQP Manual + IATF 16949 requirements"),
        ("Reviewer", "(to be assigned — per organizational roles)"),
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
        ("Title",                      "APQP Plan being assessed and reviewer info"),
        ("General Info",               "This tab — TOC and document conventions"),
        ("Guide",                      "How to interpret ratings and use the checklist"),
        ("Summary",                    "Statistical roll-up of findings"),
        ("Confirmation Review",        "14 doc-quality checks"),
        ("APQP Assessment",            "12 substantive checks per AIAG APQP Manual"),
        ("Verification Assessment",    "6 verification/launch checks (external)"),
    ]
    for i, (tab, purpose) in enumerate(rows, start=6):
        ws.cell(row=i, column=1, value=tab).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=i, column=2, value=purpose).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 3):
            ws.cell(row=i, column=c).alignment = Alignment(vertical="top", wrap_text=True)
            ws.cell(row=i, column=c).border = BORDER_ALL
    style_section_banner(ws, 14, 4, "References")
    refs = [
        ("Ref-1", "AIAG APQP Manual (Advanced Product Quality Planning)"),
        ("Ref-2", "IATF 16949:2016 — Automotive Quality Management System"),
        ("Ref-3", "Source APQP Plan workbook — see Title tab"),
    ]
    style_header(ws, 15, ["ID", "Title"])
    for i, (rid, rtitle) in enumerate(refs, start=16):
        ws.cell(row=i, column=1, value=rid).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=i, column=2, value=rtitle).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 3):
            ws.cell(row=i, column=c).border = BORDER_ALL
    autosize(ws, {1: 30, 2: 80})


def build_guide(wb):
    ws = wb.create_sheet("Guide")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 3, "Guide — How to Use This Checklist")
    style_header(ws, 4, ["#", "Instruction"])
    items = [
        "Assessment column values: FC (Fully Compliant), LC (Largely Compliant), PC (Partially Compliant), NO (Not Compliant), NA (Not Applicable), blank (pending).",
        "Findings: Evidence the auto-reviewer found. Cells marked '(Auto-suggest)' need human judgment.",
        "Page/Section: References location in source APQP Plan.",
        "Recommended Actions: Corrective actions for non-compliances. Does NOT modify source.",
        "Confidence: High=verified; Medium=inferred; Low=subjective or external.",
        "Obligation: Shall=mandatory; Should=recommended. NO on Shall is major issue.",
        "The Summary tab rolls up counts by rating.",
        "Reviewer is responsible for final judgment per organizational authority.",
    ]
    for i, instr in enumerate(items, start=5):
        ws.cell(row=i, column=1, value=i - 4).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=i, column=2, value=instr).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 3):
            ws.cell(row=i, column=c).alignment = Alignment(vertical="top", wrap_text=True)
            ws.cell(row=i, column=c).border = BORDER_ALL
        ws.row_dimensions[i].height = 36
    autosize(ws, {1: 6, 2: 100})


def build_summary(wb, results: dict[str, list[tuple[CheckDef, CheckResult]]], project_label: str = ""):
    ws = wb.create_sheet("Summary")
    build_dashboard(ws, results, project_label=project_label, checklist_label="APQP Plan Checklist Reviewer")


def build_review_tab(wb, sheet_name, tab_code, results: list[tuple[CheckDef, CheckResult]]):
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
    autosize(ws, {1: 8, 2: 24, 3: 60, 4: 12, 5: 12, 6: 60, 7: 30, 8: 50})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(apqp_plan_path: str, output_path: str) -> dict:
    p = probe(apqp_plan_path)

    results: dict[str, list[tuple[CheckDef, CheckResult]]] = {"CR": [], "APQPA": [], "VA": []}
    for c in CHECKS:
        try:
            r = c.verify(p)
        except Exception as exc:
            r = CheckResult(rating="", finding=f"(check raised exception: {exc})", recommended_action="(Re-run after fixing data)", confidence="Low")
        results[c.tab].append((c, r))

    wb = Workbook()
    wb.remove(wb.active)

    build_title(wb, p, output_path)
    build_general_info(wb)
    build_guide(wb)
    build_summary(wb, results, project_label=p.project or p.program or p.title or "")
    build_review_tab(wb, "Confirmation Review", "CR", results["CR"])
    build_review_tab(wb, "APQP Assessment", "APQPA", results["APQPA"])
    build_review_tab(wb, "Verification Assessment", "VA", results["VA"])

    wb.active = 0
    wb.save(output_path)

    summary = {
        "apqp_plan_input": apqp_plan_path,
        "checklist_output": output_path,
        "is_apqp_builder_format": p.is_apqp_builder_format,
        "n_team_members": len(p.team_members),
        "n_phase1_deliverables": len(p.phase1_deliverables),
        "n_phase2_deliverables": len(p.phase2_deliverables),
        "n_phase3_deliverables": len(p.phase3_deliverables),
        "n_phase4_deliverables": len(p.phase4_deliverables),
        "n_phase5_deliverables": len(p.phase5_deliverables),
        "n_gate_reviews": len(p.gate_reviews),
        "n_risks": len(p.risks),
        "checks_by_tab": {tab: len(rows) for tab, rows in results.items()},
        "ratings_by_tab": {tab: dict(Counter(r.rating or "PENDING" for _, r in rows)) for tab, rows in results.items()},
    }
    return summary


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_checklist.py <apqp_plan.xlsx> <output_checklist.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
