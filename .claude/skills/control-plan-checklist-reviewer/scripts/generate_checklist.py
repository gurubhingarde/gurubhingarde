#!/usr/bin/env python3
"""
Control Plan Checklist Reviewer — Orchestrator
Generates 7-tab checklist xlsx from source Control Plan
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from control_plan_probe import probe
from check_definitions import CHECKS, CheckDef, CheckResult
import dashboard


def _norm(s) -> str:
    if s is None:
        return ""
    return str(s).strip()


THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
GREEN_OK = "C6EFCE"
YELLOW_WARN = "FFD966"
RED_BAD = "F8CBAD"
GREY = "D0CECE"


def _style_header(cell, bg_color=NAVY, text_color="FFFFFF"):
    cell.font = Font(name="Calibri", size=11, bold=True, color=text_color)
    cell.fill = PatternFill("solid", fgColor=bg_color)
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = BORDER_ALL


def _style_data_cell(cell, rating=""):
    cell.font = Font(name="Calibri", size=10)
    cell.border = BORDER_ALL
    cell.alignment = Alignment(vertical="top", wrap_text=True)
    if rating == "FC":
        cell.fill = PatternFill("solid", fgColor=GREEN_OK)
    elif rating == "NO":
        cell.fill = PatternFill("solid", fgColor=RED_BAD)
    elif rating == "PC":
        cell.fill = PatternFill("solid", fgColor=YELLOW_WARN)


def write_title_tab(ws, p, checklist_id):
    """Write Title tab."""
    ws.merge_cells("A1:G1")
    title = ws["A1"]
    title.value = "Control Plan Checklist Review"
    title.font = Font(name="Calibri", size=18, bold=True, color="FFFFFF")
    title.fill = PatternFill("solid", fgColor=NAVY)
    title.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    ws["A3"].value = "Source Control Plan:"
    ws["B3"].value = p.title or "(untitled)"

    ws["A4"].value = "Plan Number:"
    ws["B4"].value = p.control_plan_number or ""

    ws["A5"].value = "Plan Type:"
    ws["B5"].value = p.plan_type or ""

    ws["A6"].value = "Key Contact:"
    ws["B6"].value = p.key_contact or ""

    ws["A7"].value = "Checklist ID:"
    ws["B7"].value = checklist_id

    ws["A8"].value = "Generated:"
    ws["B8"].value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 40


def write_general_info_tab(ws):
    """Write General Info tab."""
    ws["A1"].value = "Control Plan Checklist Reviewer — Methodology"
    ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor=NAVY)

    row = 3
    ws[f"A{row}"].value = "Overview:"
    row += 1
    ws[f"A{row}"].value = "This checklist assesses Control Plan completeness per AIAG and IATF 16949 standards. It runs 36 checks across three categories: Confirmation Review (document quality), Control Plan Assessment (substantive requirements), and Verification Assessment (testing adequacy)."
    ws[f"A{row}"].alignment = Alignment(wrap_text=True)
    ws[f"A{row}"].font = Font(name="Calibri", size=10)
    row += 3

    ws[f"A{row}"].value = "Rating Scale:"
    ws[f"A{row}"].font = Font(bold=True)
    row += 1
    for rating, desc in [
        ("FC", "Fully Compliant — requirement met with high confidence"),
        ("LC", "Largely Compliant — minor gaps that do not affect overall compliance"),
        ("PC", "Partially Compliant — significant gaps requiring corrective action"),
        ("NO", "Not Compliant — critical gap that must be resolved"),
        ("NA", "Not Applicable — requirement does not apply to this control plan"),
        ("Pending", "Not yet assessed — requires reviewer judgment"),
    ]:
        ws[f"A{row}"].value = f"{rating}: {desc}"
        row += 1

    ws.column_dimensions["A"].width = 100


def write_guide_tab(ws):
    """Write Guide tab."""
    ws["A1"].value = "How to Use This Checklist"
    ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor=NAVY)

    row = 3
    ws[f"A{row}"].value = "Workflow:"
    ws[f"A{row}"].font = Font(bold=True)
    row += 1

    steps = [
        "1. Review the Title tab to confirm the correct Control Plan.",
        "2. Review the Summary tab for statistical roll-up and key findings.",
        "3. For Confirmation Review tab: resolve all NO ratings first, then address PC items.",
        "4. For Control Plan Assessment tab: these are the substantive checks per AIAG.",
        "5. For Verification Assessment tab: most items are external (Verification Plan); focus on Control-Plan-specific rows.",
        "6. For each Pending row, apply judgment and set Assessment value.",
        "7. For each NO/PC row, decide whether to update the source Control Plan and re-run.",
    ]

    for step in steps:
        ws[f"A{row}"].value = step
        row += 1

    ws.column_dimensions["A"].width = 100


def write_summary_tab(wb, results):
    """Write Summary tab with dashboard."""
    ws = wb["Summary"]
    dashboard.build_dashboard(
        ws,
        results,
        project_label="Control Plan Checklist Review",
        checklist_label="Control Plan",
    )


def write_checklist_tab(ws, tab_name, checks_and_results, results_dict):
    """Write one checklist tab (CR, CPA, or VA)."""
    ws.sheet_view.showGridLines = False

    # Header
    ws.merge_cells("A1:H1")
    title = ws["A1"]
    title.value = f"{tab_name} Checklist"
    title.font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    title.fill = PatternFill("solid", fgColor=NAVY)
    title.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    # Column headers
    headers = ["ID", "Section", "Requirement", "Obligation", "Assessment", "Finding", "Page Section", "Recommended Action"]
    for ci, h in enumerate(headers, start=1):
        cell = ws.cell(row=2, column=ci)
        cell.value = h
        _style_header(cell)
    ws.row_dimensions[2].height = 28

    row = 3
    current_section = None

    for check_def, check_result in checks_and_results:
        # Section banner
        if check_def.section != current_section:
            current_section = check_def.section
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
            banner = ws.cell(row=row, column=1, value=f"  {current_section}")
            banner.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            banner.fill = PatternFill("solid", fgColor=LIGHT_BLUE)
            ws.row_dimensions[row].height = 20
            row += 1

        # Data row
        ws.cell(row=row, column=1, value=check_def.id)
        ws.cell(row=row, column=2, value=check_def.section)
        ws.cell(row=row, column=3, value=check_def.requirement)
        ws.cell(row=row, column=4, value=check_def.obligation)

        rating_cell = ws.cell(row=row, column=5)
        rating_cell.value = check_result.rating
        if check_result.rating:
            _style_data_cell(rating_cell, check_result.rating)
            rating_cell.font = Font(name="Calibri", size=10, bold=True)
            rating_cell.alignment = Alignment(horizontal="center")

        ws.cell(row=row, column=6, value=check_result.finding)
        ws.cell(row=row, column=7, value=check_result.page_section)
        ws.cell(row=row, column=8, value=check_result.recommended_action)

        for cc in range(1, 9):
            _style_data_cell(ws.cell(row=row, column=cc), check_result.rating if cc == 5 else "")

        ws.row_dimensions[row].height = 40
        row += 1

    # Column widths
    for ci, w in enumerate([6, 18, 50, 10, 12, 40, 25, 50], start=1):
        ws.column_dimensions[get_column_letter(ci)].width = w


def generate_checklist(input_xlsx: str, output_xlsx: str):
    """Main orchestrator."""
    # Probe source
    p = probe(input_xlsx)

    # Initialize output workbook
    wb = Workbook()
    wb.remove(wb.active)

    # Title tab
    ws_title = wb.create_sheet("Title", 0)
    checklist_id = f"CP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    write_title_tab(ws_title, p, checklist_id)

    # General Info tab
    ws_info = wb.create_sheet("General Info", 1)
    write_general_info_tab(ws_info)

    # Guide tab
    ws_guide = wb.create_sheet("Guide", 2)
    write_guide_tab(ws_guide)

    # Summary tab (placeholder; will be populated with dashboard)
    ws_summary = wb.create_sheet("Summary", 3)

    # Run checks grouped by tab
    results: dict[str, list[tuple[CheckDef, CheckResult]]] = defaultdict(list)

    for check_def in CHECKS:
        result = check_def.verify(p)
        results[check_def.tab].append((check_def, result))

    # Write checklist tabs
    for tab_code in ["CR", "CPA", "VA"]:
        if tab_code in results:
            ws = wb.create_sheet(tab_code, 4 + ["CR", "CPA", "VA"].index(tab_code))
            write_checklist_tab(ws, tab_code, results[tab_code], results)

    # Write Summary tab with dashboard
    write_summary_tab(wb, results)

    # Save
    wb.save(output_xlsx)

    # Print summary
    stats = {}
    for tab, items in results.items():
        stats[tab] = {
            "FC": sum(1 for _, r in items if r.rating == "FC"),
            "LC": sum(1 for _, r in items if r.rating == "LC"),
            "PC": sum(1 for _, r in items if r.rating == "PC"),
            "NO": sum(1 for _, r in items if r.rating == "NO"),
            "NA": sum(1 for _, r in items if r.rating == "NA"),
            "PENDING": sum(1 for _, r in items if r.rating == ""),
        }

    summary = {
        "checklist_id": checklist_id,
        "source": p.title or "(untitled)",
        "n_characteristics": len(p.cp_worksheet_rows),
        "n_special_chars": len(p.special_characteristics),
        "tabs": stats,
    }

    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <input.xlsx> <output.xlsx>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        generate_checklist(input_file, output_file)
        print(f"\nChecklist written to: {output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
