"""
Item Definition Checklist Reviewer — generates a completed confirmation-measures checklist
from any Item Definition xlsx (best-effort).

Usage:
    python generate_checklist.py <item_def.xlsx> <output_checklist.xlsx>

Methodology:
- Probe the Item Definition content.
- Run each canonical checklist requirement with verification logic.
- For machine-verifiable checks: fill assessment, finding, page/section, and recommended action.
- For subjective checks: draft a finding marked Low confidence; reviewer accepts or edits.
- Write a 7-tab xlsx (Title, General Info, Guide, Summary, Confirmation Review, IDA, VA).
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

from item_def_probe import ProbedItemDef, probe
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

def build_title(wb, p: ProbedItemDef, output_path: str):
    ws = wb.create_sheet("Title")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "Item Definition Confirmation Measures Checklist")
    style_title(ws, 3, 5, p.title or "(Item title not detected)")

    fields = [
        ("Project Number & Name", p.project),
        ("Document ID (Item Definition)", p.doc_id),
        ("Document Title", "Confirmation Measures - Item Definition"),
        ("Item Revision", p.revision),
        ("Item Status", p.status or "(not detected)"),
        ("Source Item Definition", p.path),
        ("Checklist Generated", date.today().isoformat()),
        ("Standard", "ISO 26262:2018 Part 3 §5 (Item Definition)"),
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
        ("Title",                      "Item Definition being assessed and reviewer info"),
        ("General Info",               "This tab — TOC and document conventions"),
        ("Guide",                      "How to interpret ratings and use the checklist"),
        ("Summary",                    "Statistical roll-up of findings"),
        ("Confirmation Review",        "Generic doc-quality checks (ISO 26262-8 §10)"),
        ("Item Definition Assessment", "Item Definition substantive checks (ISO 26262-3 §5)"),
        ("Verification Assessment",    "Verification readiness checks (ISO 26262-8 §9)"),
    ]
    for i, (tab, purpose) in enumerate(rows, start=6):
        ws.cell(row=i, column=1, value=tab).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=i, column=2, value=purpose).font = Font(name=FONT_NAME, size=10)
        for c in range(1, 3):
            ws.cell(row=i, column=c).alignment = Alignment(vertical="top", wrap_text=True)
    autosize(ws, {1: 25, 2: 60})


def build_guide(wb):
    ws = wb.create_sheet("Guide")
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "How to Use This Checklist")
    row = 4

    sections = [
        ("Rating Scale", [
            ("FC", "Fully Compliant — requirement fully met, no gaps."),
            ("LC", "Largely Compliant — minor gaps, no impact on safety."),
            ("PC", "Partially Compliant — gaps with potential safety impact."),
            ("NO", "Not Compliant — significant gaps, safety impact likely."),
            ("NA", "Not Applicable — requirement does not apply."),
            ("—", "Pending — reviewer to assess (subjective checks)."),
        ]),
        ("Obligation Types", [
            ("Shall", "Mandatory requirement; NO rating is a major non-conformance."),
            ("Should", "Recommended requirement; NO rating is a minor non-conformance."),
        ]),
        ("Confidence Levels", [
            ("High", "Machine-verified from xlsx content (e.g., Author populated)."),
            ("Medium", "Inferred from content with caveat (e.g., functions present)."),
            ("Low", "Subjective or requires external artifact; marked for reviewer decision."),
        ]),
    ]

    for section_title, items in sections:
        style_section_banner(ws, row, 5, section_title)
        row += 1
        for label, desc in items:
            ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, bold=True, size=10)
            ws.cell(row=row, column=3, value=desc).font = Font(name=FONT_NAME, size=10)
            ws.cell(row=row, column=3).alignment = Alignment(wrap_text=True, vertical="top")
            row += 1
        row += 1

    autosize(ws, {1: 4, 2: 20, 3: 70, 4: 4, 5: 4})


def build_summary_tab(wb, results: dict) -> None:
    """Build Summary tab using dashboard module."""
    ws = wb.create_sheet("Summary")
    build_dashboard(ws, results, checklist_label="Item Definition Confirmation Measures Checklist")


def build_check_tab(wb, tab_name: str, tab_code: str, results: dict):
    """Build a checklist tab (CR / IDA / VA)."""
    ws = wb.create_sheet(tab_name)

    style_title(ws, 1, 8, f"{tab_name} — Confirmation Measures")
    row = 3

    # Group by section
    sections = {}
    for check_def, check_result in results.get(tab_code, []):
        if check_def.section not in sections:
            sections[check_def.section] = []
        sections[check_def.section].append((check_def, check_result))

    current_section = None
    for section in sorted(sections.keys()):
        items = sections[section]

        # Section banner
        if section != current_section:
            style_section_banner(ws, row, 8, section)
            row += 1
            current_section = section

        # Check rows in this section
        for check_def, check_result in items:
            # Header row for the check
            style_header(ws, row, ["ID", "Obligation", "Requirement", "Assessment", "Finding", "Page/Section", "Recommended Action", "Confidence"])
            row += 1

            # Data row
            ws.cell(row=row, column=1, value=check_def.id)
            ws.cell(row=row, column=2, value=check_def.obligation)
            ws.cell(row=row, column=3, value=check_def.requirement)

            rating_cell = ws.cell(row=row, column=4, value=check_result.rating)
            color_assessment(rating_cell, check_result.rating, check_def.obligation)

            ws.cell(row=row, column=5, value=check_result.finding)
            ws.cell(row=row, column=6, value=check_result.page_section)
            ws.cell(row=row, column=7, value=check_result.recommended_action)
            ws.cell(row=row, column=8, value=check_result.confidence)

            for col in range(1, 9):
                cell = ws.cell(row=row, column=col)
                if col != 4:
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                    cell.font = Font(name=FONT_NAME, size=10)
                cell.border = BORDER_ALL
            ws.row_dimensions[row].height = 60

            row += 1

    autosize(ws, {1: 8, 2: 12, 3: 35, 4: 12, 5: 50, 6: 20, 7: 30, 8: 12})


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def generate_checklist(input_path: str, output_path: str) -> dict:
    """Main orchestrator: probe, check, and generate checklist xlsx."""

    # Probe
    p = probe(input_path)

    # Run checks
    results = {}
    for tab_code in ["CR", "IDA", "VA"]:
        results[tab_code] = []

    for check_def in CHECKS:
        try:
            check_result = check_def.verify(p)
        except Exception as e:
            check_result = CheckResult(
                rating="",
                finding=f"Error during verification: {e}",
                page_section="",
                recommended_action="",
                confidence="Low",
            )

        tab_code = check_def.tab
        if tab_code not in results:
            results[tab_code] = []
        results[tab_code].append((check_def, check_result))

    # Build workbook
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    build_title(wb, p, output_path)
    build_general_info(wb)
    build_guide(wb)
    build_summary_tab(wb, results)
    build_check_tab(wb, "Confirmation Review", "CR", results)
    build_check_tab(wb, "Item Definition Assessment", "IDA", results)
    build_check_tab(wb, "Verification Assessment", "VA", results)

    # Save
    wb.save(output_path)

    # Summary for output
    summary = {
        "input": input_path,
        "output": output_path,
        "item_title": p.title,
        "item_id": p.doc_id,
        "tabs_created": ["Title", "General Info", "Guide", "Summary", "Confirmation Review", "Item Definition Assessment", "Verification Assessment"],
        "ratings_by_tab": {},
    }

    for tab_code in ["CR", "IDA", "VA"]:
        ratings = Counter(r.rating for _, r in results.get(tab_code, []))
        summary["ratings_by_tab"][tab_code] = dict(ratings)

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <input.xlsx> <output.xlsx>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    result = generate_checklist(input_file, output_file)
    print(json.dumps(result, indent=2))
