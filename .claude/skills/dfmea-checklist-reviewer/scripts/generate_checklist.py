"""
DFMEA Checklist Generator — orchestrator that produces a 7-tab audit-ready checklist.

Usage:
    python generate_checklist.py <input_dfmea.xlsx> <output_checklist.xlsx>
"""

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from dfmea_probe import probe
from check_definitions import CHECKS
from dashboard import build_dashboard


# Style constants
FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
GREEN_OK = "C6EFCE"
WARN_YELLOW = "FFF2CC"
RED_BAD = "F8CBAD"
ALT_ROW = "F2F2F2"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def _apply_header_style(cell, text):
    """Apply header styling to a cell."""
    cell.value = text
    cell.font = Font(name=FONT_NAME, size=10, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORDER_ALL


def generate_checklist(dfmea_path: str, output_path: str):
    """Generate 7-tab DFMEA checklist workbook."""
    # Probe the DFMEA
    p = probe(dfmea_path)

    # Run all checks
    results = defaultdict(list)  # tab -> [(check_def, check_result), ...]
    for check in CHECKS:
        result = check.verify(p)
        results[check.tab].append((check, result))

    # Create output workbook
    wb = Workbook()
    wb.remove(wb.active)

    # ---- Tab 1: Title ----
    ws_title = wb.create_sheet("Title", 0)
    ws_title.merge_cells("A1:D1")
    title_cell = ws_title.cell(row=1, column=1, value="DFMEA Checklist Reviewer")
    title_cell.font = Font(name=FONT_NAME, size=16, bold=True, color=NAVY)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws_title.row_dimensions[1].height = 28

    row = 3
    data = [
        ("DFMEA Title", p.title),
        ("Part Number", p.part_number),
        ("FMEA ID", p.fmea_id),
        ("Project", p.project_name),
        ("Design Responsibility", p.design_responsibility),
        ("Revision", p.revision),
        ("Status", p.status),
        ("Date", p.date),
        ("Checklist Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    ]
    for label, value in data:
        ws_title.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws_title.cell(row=row, column=2, value=value or "")
        row += 1

    ws_title.column_dimensions["A"].width = 25
    ws_title.column_dimensions["B"].width = 50

    # ---- Tab 2: General Info ----
    ws_info = wb.create_sheet("General Info", 1)
    row = 1
    ws_info.merge_cells(f"A{row}:C{row}")
    cell = ws_info.cell(row=row, column=1, value="DFMEA Checklist Overview")
    cell.font = Font(name=FONT_NAME, size=12, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    row += 2

    ws_info.cell(row=row, column=1, value="Tab Guide").font = Font(name=FONT_NAME, bold=True, size=11)
    row += 1
    tabs_guide = [
        ("Title", "DFMEA and reviewer information"),
        ("General Info", "This overview"),
        ("Guide", "How to interpret ratings and confidence levels"),
        ("Summary", "KPI tiles and findings dashboard"),
        ("Confirmation Review", "14 doc-quality checks (CR)"),
        ("DFMEA Assessment", "14 substantive DFMEA checks (DFMEAA)"),
        ("Verification Assessment", "4 external verification checks (VA)"),
    ]
    for tab, desc in tabs_guide:
        ws_info.cell(row=row, column=1, value=tab).font = Font(name=FONT_NAME, bold=True)
        ws_info.cell(row=row, column=2, value=desc)
        row += 1

    ws_info.column_dimensions["A"].width = 20
    ws_info.column_dimensions["B"].width = 60

    # ---- Tab 3: Guide ----
    ws_guide = wb.create_sheet("Guide", 2)
    ws_guide.merge_cells("A1:B1")
    guide_title = ws_guide.cell(row=1, column=1, value="Rating Guide and Definitions")
    guide_title.font = Font(name=FONT_NAME, size=12, bold=True, color="FFFFFF")
    guide_title.fill = PatternFill("solid", fgColor=NAVY)
    guide_title.alignment = Alignment(horizontal="center", vertical="center")

    row = 3
    ws_guide.cell(row=row, column=1, value="Rating").font = Font(name=FONT_NAME, bold=True)
    ws_guide.cell(row=row, column=2, value="Definition").font = Font(name=FONT_NAME, bold=True)
    row += 1

    ratings = [
        ("FC", "Fully Compliant — Requirement is satisfied and confirmed"),
        ("LC", "Largely Compliant — Minor gaps; acceptable with caveats"),
        ("PC", "Partially Compliant — Significant gaps; mitigation required"),
        ("NO", "Not Compliant — Requirement not met; blocker"),
        ("NA", "Not Applicable — Check does not apply to this DFMEA"),
        ("PENDING", "Under Review — Awaiting reviewer judgment"),
    ]
    for rating, definition in ratings:
        cell = ws_guide.cell(row=row, column=1, value=rating)
        cell.font = Font(name=FONT_NAME, bold=True)
        ws_guide.cell(row=row, column=2, value=definition)
        row += 1

    row += 1
    ws_guide.cell(row=row, column=1, value="Confidence Level").font = Font(name=FONT_NAME, bold=True, size=11)
    row += 1
    confidence_levels = [
        ("High", "Verified directly from worksheet content"),
        ("Medium", "Inferred with reasonable assurance"),
        ("Low/Draft", "Subjective; requires reviewer judgment; marked auto-suggest"),
    ]
    for level, desc in confidence_levels:
        cell = ws_guide.cell(row=row, column=1, value=level)
        cell.font = Font(name=FONT_NAME, bold=True)
        ws_guide.cell(row=row, column=2, value=desc)
        row += 1

    row += 1
    ws_guide.cell(row=row, column=1, value="Obligation Level").font = Font(name=FONT_NAME, bold=True, size=11)
    row += 1
    obligations = [
        ("Shall", "Mandatory per ISO 26262 / AIAG-VDA 2019"),
        ("Should", "Recommended best practice"),
    ]
    for obl, desc in obligations:
        cell = ws_guide.cell(row=row, column=1, value=obl)
        cell.font = Font(name=FONT_NAME, bold=True)
        ws_guide.cell(row=row, column=2, value=desc)
        row += 1

    ws_guide.column_dimensions["A"].width = 20
    ws_guide.column_dimensions["B"].width = 70

    # ---- Tab 4: Summary (with dashboard) ----
    ws_summary = wb.create_sheet("Summary", 3)
    summary_stats = build_dashboard(ws_summary, results, f"DFMEA: {p.title}", "DFMEA Confirmation Measures Checklist")

    # ---- Tabs 5-7: Confirmation Review, DFMEA Assessment, Verification Assessment ----
    tab_order = [
        ("CR", "Confirmation Review", 4),
        ("DFMEAA", "DFMEA Assessment", 5),
        ("VA", "Verification Assessment", 6),
    ]

    for tab_code, tab_label, tab_idx in tab_order:
        ws = wb.create_sheet(tab_label, tab_idx)

        # Header
        headers = ["Check#", "Obligation", "Requirement", "Rating", "Confidence", "Finding", "Recommended Action", "Page/Section"]
        for ci, h in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=ci, value=h)
            _apply_header_style(cell, h)
        ws.row_dimensions[1].height = 28

        row = 2
        items = results.get(tab_code, [])
        for check_def, check_result in items:
            ws.cell(row=row, column=1, value=check_def.id)
            ws.cell(row=row, column=2, value=check_def.obligation)
            ws.cell(row=row, column=3, value=check_def.requirement)

            rating_cell = ws.cell(row=row, column=4, value=check_result.rating)
            if check_result.rating == "FC":
                rating_cell.fill = PatternFill("solid", fgColor=GREEN_OK)
            elif check_result.rating == "NO":
                rating_cell.fill = PatternFill("solid", fgColor=RED_BAD)
            elif check_result.rating == "PC":
                rating_cell.fill = PatternFill("solid", fgColor=WARN_YELLOW)
            rating_cell.alignment = Alignment(horizontal="center")
            rating_cell.font = Font(name=FONT_NAME, bold=True)

            ws.cell(row=row, column=5, value=check_result.confidence)
            ws.cell(row=row, column=6, value=check_result.finding)
            ws.cell(row=row, column=7, value=check_result.recommended_action)
            ws.cell(row=row, column=8, value=check_result.page_section)

            for cc in range(1, 9):
                cell = ws.cell(row=row, column=cc)
                if cc not in (1, 2, 4, 5):
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                cell.border = BORDER_ALL
                if row % 2 == 0:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)

            row += 1

        # Column widths
        ws.column_dimensions["A"].width = 10
        ws.column_dimensions["B"].width = 12
        ws.column_dimensions["C"].width = 45
        ws.column_dimensions["D"].width = 10
        ws.column_dimensions["E"].width = 12
        ws.column_dimensions["F"].width = 60
        ws.column_dimensions["G"].width = 50
        ws.column_dimensions["H"].width = 20

    # Save workbook
    wb.save(output_path)

    # Print summary JSON
    high_pending = len([r for r in p.dfmea_rows if "H" in r.action_priority.upper() and r.status and "complete" not in r.status.lower()])
    ratings_dist = Counter()
    for tab, items in results.items():
        for _, result in items:
            ratings_dist[result.rating or "PENDING"] += 1

    summary = {
        "dfmea_title": p.title,
        "dfmea_id": p.fmea_id,
        "checklist_path": output_path,
        "tabs_created": 7,
        "total_checks": len(CHECKS),
        "total_failure_modes": p.total_failure_modes,
        "high_ap_count": p.high_ap_count,
        "high_ap_pending": high_pending,
        "medium_ap_count": p.medium_ap_count,
        "low_ap_count": p.low_ap_count,
        "ratings_distribution": dict(ratings_dist),
        "compliance_status": summary_stats["status"],
        "compliance_pct": round(summary_stats["compliance_pct"], 1),
        "major_issues": summary_stats["major"],
    }
    print(json.dumps(summary, indent=2))


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <input_dfmea.xlsx> <output_checklist.xlsx>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not Path(input_path).exists():
        print(f"Error: Input file {input_path} does not exist")
        sys.exit(1)

    generate_checklist(input_path, output_path)
    print(f"\nChecklist saved to: {output_path}")


if __name__ == "__main__":
    main()
