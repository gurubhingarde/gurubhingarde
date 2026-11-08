"""
SW FMEA Checklist Reviewer — generates a completed confirmation-measures checklist
from any SW FMEA xlsx (sw-fmea-builder outputs).

Usage:
    python generate_checklist.py <sw_fmea.xlsx> <output_checklist.xlsx>

Produces 7-tab checklist with auto-filled ratings, findings, and dashboard.
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

from sw_fmea_probe import ProbedSwFmea, probe
from check_definitions import CHECKS, CheckDef, CheckResult
from dashboard import build_dashboard


# ---------------------------------------------------------------------------
# Styling (reused from FMEDA)
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

def build_title(wb, p: ProbedSwFmea, output_path: str):
    ws = wb.create_sheet("Title")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "SW FMEA Confirmation Measures Checklist")
    style_title(ws, 3, 5, p.title or "(SW FMEA title not detected)")

    fields = [
        ("Project Number & Name", p.project),
        ("Document ID (SW FMEA)", p.doc_id),
        ("Document Title", "Confirmation Measures - SW FMEA"),
        ("SW FMEA Revision", p.revision),
        ("SW FMEA Status", p.status or "(not detected)"),
        ("Source SW FMEA", p.path),
        ("Checklist Generated", date.today().isoformat()),
        ("Standard", "ISO 26262:2018 Part 9 §8 (SW FMEA)"),
        ("Reviewer", "(to be assigned — independence per ISO 26262-2 Table 1)"),
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
        ("Title",                      "SW FMEA being assessed and reviewer info"),
        ("General Info",               "This tab — TOC and document conventions"),
        ("Guide",                      "How to interpret ratings and use the checklist"),
        ("Summary",                    "Statistical roll-up of findings with visual dashboard"),
        ("Confirmation Review",        "Generic doc-quality checks (ISO 26262-8 §10)"),
        ("SW FMEA Assessment",         "SW FMEA substantive checks (ISO 26262-9 §8)"),
        ("Verification Assessment",    "External verification checks"),
    ]
    for i, (tab, purpose) in enumerate(rows, start=6):
        ws.cell(row=i, column=1, value=tab).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=i, column=2, value=purpose).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 3):
            ws.cell(row=i, column=c).alignment = Alignment(vertical="top", wrap_text=True)
            ws.cell(row=i, column=c).border = BORDER_ALL
    style_section_banner(ws, 14, 4, "References")
    refs = [
        ("Ref-1", "ISO 26262:2018 Part 9 — Functional Safety, SW FMEA"),
        ("Ref-2", "ISO 26262:2018 Part 6 — Functional Safety, Product development at the software level"),
        ("Ref-3", "Source SW FMEA workbook — see Title tab"),
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
        "Assessment: FC=Fully Compliant, LC=Largely Compliant, PC=Partially Compliant, NO=Not Compliant, NA=Not Applicable, blank=Pending.",
        "Findings cells contain evidence from the SW FMEA. Cells marked '(Auto-suggest, requires reviewer judgment)' need human review.",
        "Page/Section cells reference where evidence lives in source SW FMEA for direct verification.",
        "Recommended Actions do NOT modify source SW FMEA; analyst decides whether to update and re-run.",
        "Confidence: High=directly verified from xlsx; Medium=inferred with caveat; Low=subjective/external artifact required.",
        "Obligation: Shall=mandatory; Should=recommended. NO on Shall is major non-conformance; on Should is minor.",
        "Summary tab rolls up counts from review tabs. Update Assessment cell and Summary recomputes.",
        "Residual risk acceptance: auto-verified per ASIL threshold (D<=1, C<=3, B<=9, A<=27) in Check #10 SW FMEA Assessment.",
        "Reviewer is responsible for final judgment per ISO 26262-2; auto-fill is an aid, not substitute. Confirm I1/I2/I3 independence.",
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
    build_dashboard(ws, results, project_label=project_label, checklist_label="SW FMEA Confirmation Measures")


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

def generate(sw_fmea_path: str, output_path: str) -> dict:
    p = probe(sw_fmea_path)

    results: dict[str, list[tuple[CheckDef, CheckResult]]] = {"CR": [], "SWFMEAA": [], "VA": []}
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
    build_summary(wb, results, project_label=p.project or p.title or "")
    build_review_tab(wb, "Confirmation Review", "CR", results["CR"])
    build_review_tab(wb, "SW FMEA Assessment", "SWFMEAA", results["SWFMEAA"])
    build_review_tab(wb, "Verification Assessment", "VA", results["VA"])

    wb.active = 0
    wb.save(output_path)

    # Count SWCs exceeding residual risk threshold
    swcs_exceeding_threshold = 0
    for row in p.fmea_rows:
        asils = list({c.asil for c in p.sw_components if c.asil})
        if asils:
            asil_thresholds = {"D": 1, "C": 3, "B": 9, "A": 27, "QM": float('inf')}
            threshold = min(asil_thresholds.get(a, float('inf')) for a in asils)
            if row.post_risk > threshold:
                swcs_exceeding_threshold += 1
                break  # Count once per SWC with exceeding modes

    summary = {
        "sw_fmea_input": sw_fmea_path,
        "checklist_output": output_path,
        "is_sw_fmea_builder_format": p.is_sw_fmea_builder_format,
        "n_sw_components": len(p.sw_components),
        "n_fmea_rows_probed": len(p.fmea_rows),
        "n_failure_modes_library": len(p.failure_modes_library),
        "n_detection_mechanisms": len(p.detection_mechanisms),
        "checks_by_tab": {tab: len(rows) for tab, rows in results.items()},
        "ratings_by_tab": {tab: dict(Counter(r.rating or "PENDING" for _, r in rows)) for tab, rows in results.items()},
        "swcs_exceeding_residual_threshold": swcs_exceeding_threshold,
    }
    return summary


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_checklist.py <sw_fmea.xlsx> <output_checklist.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
