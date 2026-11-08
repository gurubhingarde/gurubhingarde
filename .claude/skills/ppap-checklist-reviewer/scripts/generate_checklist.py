#!/usr/bin/env python3
"""
PPAP Checklist Reviewer orchestrator.

Usage:
    python generate_checklist.py <input_ppap.xlsx> <output_checklist.xlsx>
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from ppap_probe import probe
from check_definitions import CHECKS, CheckDef, CheckResult
from dashboard import build_dashboard


def _write_title_tab(ws, ppap_path: str, customer: str, supplier: str, part_name: str):
    """Write the Title tab."""
    ws.sheet_view.showGridLines = False
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=8)
    title = ws.cell(row=1, column=1, value="PPAP Checklist Reviewer")
    title.font = Font(name="Calibri", size=18, bold=True, color="FFFFFF")
    title.fill = PatternFill("solid", fgColor="1F3864")
    title.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32

    row = 3
    for label, value in [
        ("PPAP Package", Path(ppap_path).name),
        ("Customer", customer or "(not found)"),
        ("Supplier", supplier or "(not found)"),
        ("Part Name", part_name or "(not found)"),
        ("Generated", "Automatic"),
    ]:
        ws.cell(row=row, column=1, value=label).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

    for col in [1, 2]:
        ws.column_dimensions[get_column_letter(col)].width = 25


def _write_general_info_tab(ws):
    """Write the General Info tab (TOC and references)."""
    ws.sheet_view.showGridLines = False
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
    title = ws.cell(row=1, column=1, value="General Information")
    title.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    title.fill = PatternFill("solid", fgColor="1F3864")
    ws.row_dimensions[1].height = 22

    row = 3
    ws.cell(row=row, column=1, value="Contents").font = Font(bold=True, size=11)
    row += 1
    for tab_name in ["Title", "Summary", "Confirmation Review", "PPAP Assessment", "Verification Assessment"]:
        ws.cell(row=row, column=1, value=f"- {tab_name}")
        row += 1

    row += 2
    ws.cell(row=row, column=1, value="References").font = Font(bold=True, size=11)
    row += 1
    refs = [
        "AIAG PPAP Manual, 4th Edition",
        "ISO 9001:2015",
        "Customer-specific requirements",
    ]
    for ref in refs:
        ws.cell(row=row, column=1, value=f"- {ref}")
        row += 1

    ws.column_dimensions["A"].width = 50


def _write_guide_tab(ws):
    """Write the Guide tab (scoring guide)."""
    ws.sheet_view.showGridLines = False
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
    title = ws.cell(row=1, column=1, value="Scoring Guide")
    title.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    title.fill = PatternFill("solid", fgColor="1F3864")
    ws.row_dimensions[1].height = 22

    row = 3
    ratings = [
        ("FC", "Fully Compliant", "All requirements met; no discrepancies."),
        ("LC", "Largely Compliant", "Minor gaps; acceptable with minor corrective action."),
        ("PC", "Partially Compliant", "Significant gaps; must be addressed before submission."),
        ("NO", "Not Compliant", "Requirement not met; cannot proceed without resolution."),
        ("NA", "Not Applicable", "Requirement does not apply in this context."),
        ("PENDING", "Pending Review", "Requires subjective assessment by reviewer."),
    ]
    for code, label, desc in ratings:
        ws.cell(row=row, column=1, value=code).font = Font(bold=True, size=10)
        ws.cell(row=row, column=2, value=label)
        ws.cell(row=row, column=3, value=desc)
        row += 1

    for col in [1, 2, 3]:
        ws.column_dimensions[get_column_letter(col)].width = 20 if col == 1 else 35


def _write_summary_tab(ws, results: dict):
    """Write the Summary tab with dashboard and statistics."""
    dashboard_metrics = build_dashboard(ws, results, checklist_label="PPAP Checklist")
    return dashboard_metrics


def _write_checklist_tab(ws, tab_code: str, items: list[tuple[CheckDef, CheckResult]]):
    """Write a checklist tab (CR / PPAPA / VA)."""
    ws.sheet_view.showGridLines = False

    # Title
    title_text = {"CR": "Confirmation Review", "PPAPA": "PPAP Assessment", "VA": "Verification Assessment"}[tab_code]
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=7)
    title = ws.cell(row=1, column=1, value=title_text)
    title.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    title.fill = PatternFill("solid", fgColor="1F3864")
    ws.row_dimensions[1].height = 22

    # Headers
    headers = ["ID", "Obligation", "Requirement", "Rating", "Finding", "Recommended Action", "Confidence"]
    header_row = 2
    for ci, h in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=ci, value=h)
        cell.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="404040")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[header_row].height = 20

    # Rows
    current_section = ""
    row = header_row + 1
    thin_border = Border(left=Side(style="thin", color="BFBFBF"),
                         right=Side(style="thin", color="BFBFBF"),
                         top=Side(style="thin", color="BFBFBF"),
                         bottom=Side(style="thin", color="BFBFBF"))

    for check, result in items:
        # Section banner
        if check.section != current_section:
            current_section = check.section
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
            section_cell = ws.cell(row=row, column=1, value=current_section)
            section_cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            section_cell.fill = PatternFill("solid", fgColor="4472C4")
            ws.row_dimensions[row].height = 18
            row += 1

        # Check row
        ws.cell(row=row, column=1, value=check.id)
        ws.cell(row=row, column=2, value=check.obligation)
        ws.cell(row=row, column=3, value=check.requirement)

        rating_cell = ws.cell(row=row, column=4, value=result.rating or "—")
        rating_color = {
            "FC": "C6EFCE", "LC": "9DC3E6", "PC": "FFD966",
            "NO": "F8CBAD", "NA": "D0CECE", "": "FFFFFF"
        }.get(result.rating, "FFFFFF")
        rating_cell.fill = PatternFill("solid", fgColor=rating_color)
        rating_cell.font = Font(bold=True, size=10)

        ws.cell(row=row, column=5, value=result.finding)
        ws.cell(row=row, column=6, value=result.recommended_action)
        ws.cell(row=row, column=7, value=result.confidence or "")

        for c in range(1, 8):
            ws.cell(row=row, column=c).border = thin_border
            ws.cell(row=row, column=c).alignment = Alignment(vertical="top", wrap_text=True)

        ws.row_dimensions[row].height = max(30, len(result.finding) // 40 + 15)
        row += 1

    # Column widths
    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 50
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 50
    ws.column_dimensions["F"].width = 50
    ws.column_dimensions["G"].width = 12


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <input.xlsx> <output.xlsx>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    print(f"Probing PPAP package: {input_path}")
    ppap = probe(input_path)

    print("Running checks...")
    results = defaultdict(list)  # {tab_code: [(check_def, result), ...]}

    for check in CHECKS:
        result = check.verify(ppap)
        results[check.tab].append((check, result))

    # Generate output workbook
    wb = Workbook()
    wb.remove(wb.active)

    # Tab 1: Title
    print("Writing Title tab...")
    ws_title = wb.create_sheet("Title", 0)
    _write_title_tab(ws_title, str(input_path), ppap.customer, ppap.supplier, ppap.part_name)

    # Tab 2: General Info
    print("Writing General Info tab...")
    ws_info = wb.create_sheet("General Info", 1)
    _write_general_info_tab(ws_info)

    # Tab 3: Guide
    print("Writing Guide tab...")
    ws_guide = wb.create_sheet("Guide", 2)
    _write_guide_tab(ws_guide)

    # Tab 4: Summary (with dashboard)
    print("Writing Summary tab with dashboard...")
    ws_summary = wb.create_sheet("Summary", 3)
    metrics = _write_summary_tab(ws_summary, results)

    # Tabs 5-7: Checklist tabs
    for tab_code, label in [("CR", "Confirmation Review"), ("PPAPA", "PPAP Assessment"), ("VA", "Verification Assessment")]:
        print(f"Writing {label} tab...")
        ws = wb.create_sheet(label, len(wb.sheetnames))
        _write_checklist_tab(ws, tab_code, results[tab_code])

    # Save
    wb.save(output_path)
    print(f"\nChecklist saved: {output_path}")

    # Summary statistics
    all_results = []
    for tab_items in results.values():
        for check, result in tab_items:
            all_results.append((check, result))

    n_total = len(all_results)
    n_fc = sum(1 for _, r in all_results if r.rating == "FC")
    n_lc = sum(1 for _, r in all_results if r.rating == "LC")
    n_pc = sum(1 for _, r in all_results if r.rating == "PC")
    n_no = sum(1 for _, r in all_results if r.rating == "NO")
    n_na = sum(1 for _, r in all_results if r.rating == "NA")
    n_pending = sum(1 for _, r in all_results if r.rating == "")

    print(f"\nChecklistStatistics:")
    print(f"  Total items: {n_total}")
    print(f"  Fully Compliant (FC): {n_fc}")
    print(f"  Largely Compliant (LC): {n_lc}")
    print(f"  Partially Compliant (PC): {n_pc}")
    print(f"  Not Compliant (NO): {n_no}")
    print(f"  Not Applicable (NA): {n_na}")
    print(f"  Pending Review: {n_pending}")

    # Detailed findings
    print(f"\nOut-of-spec dimensional results: {sum(1 for d in ppap.dimensional_results if d.status == 'Out-of-Spec')}")
    print(f"Low-Cpk process capability: {sum(1 for pc in ppap.process_capability if pc.status == 'Low')}")
    print(f"High R&R MSA gages (>30%): {sum(1 for m in ppap.element8_msa_results if m['r_and_r_pct'] > 30)}")

    import json
    summary_json = {
        "total_checks": n_total,
        "ratings": {
            "FC": n_fc, "LC": n_lc, "PC": n_pc, "NO": n_no, "NA": n_na, "PENDING": n_pending
        },
        "compliance_pct": round((n_fc + n_lc) / max(1, n_total - n_na) * 100, 1),
        "major_findings": n_no,
        "out_of_spec_dims": sum(1 for d in ppap.dimensional_results if d.status == "Out-of-Spec"),
        "low_cpk_items": sum(1 for pc in ppap.process_capability if pc.status == "Low"),
    }
    print(f"\nJSON summary: {json.dumps(summary_json, indent=2)}")


if __name__ == "__main__":
    main()
