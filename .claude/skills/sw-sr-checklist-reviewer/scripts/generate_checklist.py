"""
SW Safety Requirements Checklist Reviewer — generates completed confirmation-measures checklist.

Usage:
    python generate_checklist.py <sw_sr.xlsx> <output_checklist.xlsx>

Methodology:
- Probe the SW-SR xlsx content.
- Run each canonical checklist requirement with verification logic.
- For machine-verifiable checks: fill assessment, finding, section, and action.
- For subjective checks: draft marked Low confidence.
- Write 7-tab xlsx (Title, General Info, Guide, Summary, Confirmation Review, SWSRA, VA).
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from sw_sr_probe import ProbedSwSR, probe
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
# Tab writers
# ---------------------------------------------------------------------------

def write_title_tab(wb, probed):
    ws = wb.create_sheet("Title", 0)
    style_title(ws, 1, 4, "SW Safety Requirements Checklist")
    ws.row_dimensions[2].height = 30

    r = 3
    ws.cell(row=r, column=1, value="Document Being Assessed")
    ws.cell(row=r, column=2, value=probed.title or "(No title detected)")
    r += 1
    ws.cell(row=r, column=1, value="Document ID")
    ws.cell(row=r, column=2, value=probed.doc_id or "—")
    r += 1
    ws.cell(row=r, column=1, value="Revision")
    ws.cell(row=r, column=2, value=probed.revision or "—")
    r += 1
    ws.cell(row=r, column=1, value="Status")
    ws.cell(row=r, column=2, value=probed.status or "—")
    r += 1
    ws.cell(row=r, column=1, value="Author")
    ws.cell(row=r, column=2, value=probed.author or "—")
    r += 1
    ws.cell(row=r, column=1, value="Approver")
    ws.cell(row=r, column=2, value=probed.approver or "—")
    r += 1
    ws.cell(row=r, column=1, value="Project")
    ws.cell(row=r, column=2, value=probed.project or "—")
    r += 1
    ws.cell(row=r, column=1, value="Linked TSC")
    ws.cell(row=r, column=2, value=probed.linked_tsc or "—")
    r += 2

    ws.cell(row=r, column=1, value="Checklist Generated")
    ws.cell(row=r, column=2, value=str(date.today()))
    r += 1
    ws.cell(row=r, column=1, value="Format Detected")
    ws.cell(row=r, column=2, value="sw-safety-reqs-builder" if probed.is_sw_sr_builder_format else "best-effort")

    autosize(ws, {1: 20, 2: 40, 3: 12, 4: 12})


def write_general_info_tab(wb, probed):
    ws = wb.create_sheet("General Info", 1)
    style_title(ws, 1, 3, "SW-SR Checklist — Contents & References")

    r = 3
    ws.cell(row=r, column=1, value="Tab")
    ws.cell(row=r, column=2, value="Purpose")
    style_header(ws, r, ["Tab", "Purpose"])

    tabs = [
        ("Title", "Document title, metadata, revision"),
        ("General Info", "Checklist overview, tab guide, references"),
        ("Guide", "How to interpret ratings, confidence, iteration workflow"),
        ("Summary", "Dashboard with KPIs, status, findings"),
        ("Confirmation Review", "14 doc-quality checks per ISO 26262-8 10"),
        ("SWSRA", "12 SW-SR assessment checks per ISO 26262-6 6"),
        ("VA", "22 verification checks; 5 SW-SR-specific items 33a-e"),
    ]
    for tab_name, purpose in tabs:
        r += 1
        ws.cell(row=r, column=1, value=tab_name)
        ws.cell(row=r, column=2, value=purpose)

    r += 2
    ws.cell(row=r, column=1, value="References")
    style_header(ws, r, ["References"])

    refs = [
        "ISO 26262-6:2018 - Software development requirements and techniques",
        "ISO 26262-8:2018 - Guidelines on ISO 26262",
        "sw-sr-builder — SW Safety Requirements specification generator",
        "sw-fmea-builder — SW FMEA specification generator",
    ]
    for ref in refs:
        r += 1
        ws.cell(row=r, column=1, value=ref)

    autosize(ws, {1: 35, 2: 60})


def write_guide_tab(wb):
    ws = wb.create_sheet("Guide", 2)
    style_title(ws, 1, 3, "Checklist Interpretation Guide")

    r = 3
    ws.cell(row=r, column=1, value="Rating")
    ws.cell(row=r, column=2, value="Meaning")
    style_header(ws, r, ["Rating", "Meaning"])

    ratings = [
        ("FC", "Fully Compliant: Requirement met; evidence cited."),
        ("LC", "Largely Compliant: Requirement mostly met; minor gaps."),
        ("PC", "Partially Compliant: Significant gaps; corrective action required."),
        ("NO", "Not Compliant: Requirement not met; blocker or major gap."),
        ("NA", "Not Applicable: Requirement does not apply to this document."),
        ("(blank)", "Pending Review: Subjective item requiring human judgment."),
    ]
    for rating, meaning in ratings:
        r += 1
        ws.cell(row=r, column=1, value=rating)
        ws.cell(row=r, column=2, value=meaning)

    r += 2
    ws.cell(row=r, column=1, value="Confidence")
    ws.cell(row=r, column=2, value="Explanation")
    style_header(ws, r, ["Confidence", "Explanation"])

    confidence = [
        ("High", "Verified directly from spreadsheet data (counts, presence/absence)."),
        ("Medium", "Inferred from spreadsheet with caveat; reviewer judgment advised."),
        ("Low", "Subjective or external; marked (Auto-suggest, requires reviewer judgment)."),
    ]
    for conf, expl in confidence:
        r += 1
        ws.cell(row=r, column=1, value=conf)
        ws.cell(row=r, column=2, value=expl)

    r += 2
    ws.cell(row=r, column=1, value="Workflow")
    style_header(ws, r, ["Workflow"])

    workflow = [
        "Step 1: Open Title tab. Confirm the SW-SR being assessed is the right one.",
        "Step 2: Review Summary tab. Focus on KC (key compliance) and findings (PC, NO items).",
        "Step 3: Walk Confirmation Review tab. Address NO and Pending rows.",
        "Step 4: Walk SWSRA tab. Address PC and NO findings; these are substantive gaps.",
        "Step 5: Walk VA tab. Most items are external Verification Plan items; mark Pending as planned.",
        "Step 6: For each Pending row, reviewer accepts finding or refines assessment.",
        "Step 7: Update source SW-SR xlsx if required, re-run to produce fresh checklist.",
    ]
    for step in workflow:
        r += 1
        ws.cell(row=r, column=1, value=step)
        ws.cell(row=r, column=1).alignment = Alignment(wrap_text=True)

    autosize(ws, {1: 25, 2: 70})


def write_tab_content(wb, tab_code, checks_and_results, tab_index):
    """Write a single checklist tab (CR / SWSRA / VA)."""
    ws = wb.create_sheet(f"{tab_code}", tab_index)

    # Group by section
    by_section = defaultdict(list)
    for check_def, check_result in checks_and_results:
        by_section[check_def.section].append((check_def, check_result))

    headers = ["ID", "Obligation", "Requirement", "Assessment", "Finding", "Page / Section", "Recommended Action", "Confidence"]
    style_header(ws, 1, headers)

    row = 2
    for section, items in sorted(by_section.items()):
        style_section_banner(ws, row, len(headers), section)
        row += 1

        for check_def, check_result in items:
            ws.cell(row=row, column=1, value=check_def.id)
            ws.cell(row=row, column=2, value=check_def.obligation)
            ws.cell(row=row, column=3, value=check_def.requirement)

            rating_cell = ws.cell(row=row, column=4, value=check_result.rating or "")
            color_assessment(rating_cell, check_result.rating, check_def.obligation)

            ws.cell(row=row, column=5, value=check_result.finding)
            ws.cell(row=row, column=6, value=check_result.page_section)
            ws.cell(row=row, column=7, value=check_result.recommended_action)
            ws.cell(row=row, column=8, value=check_result.confidence)

            for col in range(1, 9):
                cell = ws.cell(row=row, column=col)
                if col != 4:
                    cell.font = Font(name=FONT_NAME, size=10)
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                cell.border = BORDER_ALL

            row += 1

    autosize(ws, {1: 8, 2: 10, 3: 50, 4: 12, 5: 40, 6: 25, 7: 35, 8: 12})


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def main(sw_sr_xlsx: str, output_xlsx: str):
    probed = probe(sw_sr_xlsx)

    # Run all checks
    results_by_tab = defaultdict(list)
    for check_def in CHECKS:
        check_result = check_def.verify(probed)
        results_by_tab[check_def.tab].append((check_def, check_result))

    # Create workbook
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    # Write tabs
    write_title_tab(wb, probed)
    write_general_info_tab(wb, probed)
    write_guide_tab(wb)

    # Summary tab with dashboard
    ws_summary = wb.create_sheet("Summary", 3)
    build_dashboard(ws_summary, results_by_tab,
                   project_label=probed.project or "",
                   checklist_label="SW Safety Requirements Checklist")

    # Checklist tabs
    write_tab_content(wb, "Confirmation Review", results_by_tab["CR"], 4)
    write_tab_content(wb, "SWSRA", results_by_tab["SWSRA"], 5)
    write_tab_content(wb, "VA", results_by_tab["VA"], 6)

    # Save
    wb.save(output_xlsx)

    # Summary statistics
    all_results = []
    for tab, items in results_by_tab.items():
        for c, r in items:
            all_results.append((tab, c, r))

    stats = {
        "total_checks": len(all_results),
        "tabs": {
            "CR": len(results_by_tab["CR"]),
            "SWSRA": len(results_by_tab["SWSRA"]),
            "VA": len(results_by_tab["VA"]),
        },
        "ratings": {
            "FC": sum(1 for _, _, r in all_results if r.rating == "FC"),
            "LC": sum(1 for _, _, r in all_results if r.rating == "LC"),
            "PC": sum(1 for _, _, r in all_results if r.rating == "PC"),
            "NO": sum(1 for _, _, r in all_results if r.rating == "NO"),
            "NA": sum(1 for _, _, r in all_results if r.rating == "NA"),
            "PENDING": sum(1 for _, _, r in all_results if r.rating in ("", None)),
        },
    }

    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <sw_sr.xlsx> <output_checklist.xlsx>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
