#!/usr/bin/env python3
"""PFMEA Checklist Generator — 7-tab audit checklist with dashboard."""

import sys
from pathlib import Path
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from pfmea_probe import probe, ProbedPfmea
import check_definitions as checks
from dashboard import build_dashboard

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
NAVY = "1F3864"

def _create_cell(ws, row, col, value, font=None, fill=None, alignment=None, border=None):
    cell = ws.cell(row=row, column=col, value=value)
    if font: cell.font = font
    if fill: cell.fill = fill
    if alignment: cell.alignment = alignment
    if border: cell.border = border
    return cell

def _build_title_tab(wb, p: ProbedPfmea):
    ws = wb.create_sheet("Title", 0)
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 50
    row = 1
    ws.merge_cells(f'A{row}:B{row}')
    _create_cell(ws, row, 1, "PFMEA Confirmation Checklist",
                 font=Font(name="Calibri", size=16, bold=True, color="FFFFFF"),
                 fill=PatternFill("solid", fgColor=NAVY))
    ws.row_dimensions[row].height = 28
    row = 3
    _create_cell(ws, row, 1, "PFMEA Title:", font=Font(bold=True))
    _create_cell(ws, row, 2, p.title)
    row += 1
    _create_cell(ws, row, 1, "Process:", font=Font(bold=True))
    _create_cell(ws, row, 2, p.process_name)
    row += 1
    _create_cell(ws, row, 1, "Part Number:", font=Font(bold=True))
    _create_cell(ws, row, 2, p.part_number)
    row += 1
    _create_cell(ws, row, 1, "Part Name:", font=Font(bold=True))
    _create_cell(ws, row, 2, p.part_name)
    row += 1
    _create_cell(ws, row, 1, "Revision:", font=Font(bold=True))
    _create_cell(ws, row, 2, p.revision)
    row += 1
    _create_cell(ws, row, 1, "Status:", font=Font(bold=True))
    _create_cell(ws, row, 2, p.status)
    row += 1
    _create_cell(ws, row, 1, "Author:", font=Font(bold=True))
    _create_cell(ws, row, 2, p.author)
    row += 1
    _create_cell(ws, row, 1, "Approver:", font=Font(bold=True))
    _create_cell(ws, row, 2, p.approver)

def _build_general_info_tab(wb, p: ProbedPfmea):
    ws = wb.create_sheet("General Info", 1)
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 50
    row = 1
    ws.merge_cells(f'A{row}:B{row}')
    _create_cell(ws, row, 1, "Checklist Table of Contents",
                 font=Font(name="Calibri", size=14, bold=True, color="FFFFFF"),
                 fill=PatternFill("solid", fgColor=NAVY))
    row = 3
    tabs = ["Title", "General Info", "Guide", "Summary", "Confirmation Review", "PFMEA Assessment", "Verification Assessment"]
    for i, tab in enumerate(tabs, start=1):
        _create_cell(ws, row, 1, f"Tab {i}:", font=Font(bold=True))
        _create_cell(ws, row, 2, tab)
        row += 1

def _build_guide_tab(wb):
    ws = wb.create_sheet("Guide", 2)
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 65
    row = 1
    ws.merge_cells(f'A{row}:B{row}')
    _create_cell(ws, row, 1, "Checklist Scoring Guide",
                 font=Font(name="Calibri", size=14, bold=True, color="FFFFFF"),
                 fill=PatternFill("solid", fgColor=NAVY))
    row = 3
    ratings = [
        ("FC", "Fully Compliant", "Requirement satisfied; no corrective action needed."),
        ("LC", "Largely Compliant", "Requirement substantially satisfied; minor gaps acceptable."),
        ("PC", "Partially Compliant", "Requirement partially satisfied; corrective action recommended."),
        ("NO", "Not Compliant", "Requirement not satisfied; must be corrected."),
        ("NA", "Not Applicable", "Requirement not applicable to this PFMEA."),
        ("(Pending)", "Pending Review", "Automated check suggests finding; requires reviewer judgment."),
    ]
    for rating, label, description in ratings:
        _create_cell(ws, row, 1, rating, font=Font(bold=True))
        _create_cell(ws, row, 2, f"{label}: {description}")
        row += 1

def _build_check_tab(wb, tab_name, check_results, tab_index):
    ws = wb.create_sheet(tab_name, tab_index)
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 35
    ws.column_dimensions['C'].width = 50
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 35
    ws.column_dimensions['F'].width = 12
    row = 1
    headers = ["ID", "Requirement", "Finding", "Rating", "Recommended Action", "Confidence"]
    for col, header in enumerate(headers, start=1):
        _create_cell(ws, row, col, header,
                     font=Font(bold=True, color="FFFFFF"),
                     fill=PatternFill("solid", fgColor=NAVY),
                     alignment=Alignment(horizontal="center", vertical="center", wrap_text=True),
                     border=BORDER_ALL)
    ws.row_dimensions[1].height = 30
    for check_def, check_result in check_results:
        row += 1
        _create_cell(ws, row, 1, check_def.id, border=BORDER_ALL)
        _create_cell(ws, row, 2, check_def.requirement, border=BORDER_ALL)
        _create_cell(ws, row, 3, check_result.finding, border=BORDER_ALL, alignment=Alignment(wrap_text=True))
        rating_color = {"FC": "C6EFCE", "LC": "9DC3E6", "PC": "FFC000", "NO": "F8CBAD", "NA": "E0E0E0"}.get(check_result.rating, "FFFFFF")
        _create_cell(ws, row, 4, check_result.rating,
                     fill=PatternFill("solid", fgColor=rating_color),
                     alignment=Alignment(horizontal="center"),
                     border=BORDER_ALL)
        _create_cell(ws, row, 5, check_result.recommended_action, border=BORDER_ALL, alignment=Alignment(wrap_text=True))
        _create_cell(ws, row, 6, check_result.confidence, border=BORDER_ALL)
        ws.row_dimensions[row].height = max(15, len(check_result.finding) // 50 * 15)

def generate_checklist(input_xlsx: str, output_xlsx: str):
    p = probe(input_xlsx)
    print(f"Probed PFMEA: {p.title} (Rev. {p.revision})")
    print(f"  Process: {p.process_name}")
    print(f"  Part: {p.part_number} / {p.part_name}")
    print(f"  Tabs: {len(p.sheet_names)}")
    print(f"  Process Flow Steps: {len(p.process_flow_steps)}")
    print(f"  Process Functions: {len(p.process_functions)}")
    print(f"  PFMEA Rows: {len(p.pfmea_rows)}")
    print(f"  Special Characteristics: {len(p.special_characteristics)}")
    print(f"  Action Plan Items: {len(p.action_plan_items)}")
    print(f"  Control Plan Linkages: {len(p.control_plan_linkages)}")
    print(f"  High-AP Items: {p.high_ap_count}, Completed: {p.completed_actions}")
    
    wb = Workbook()
    wb.remove(wb.active)
    
    _build_title_tab(wb, p)
    _build_general_info_tab(wb, p)
    _build_guide_tab(wb)
    
    cr_checks = [
        (checks.CheckDef("CR-01", "CR", "Doc Quality", "Document is properly structured", "Shall"), checks.cr_01_structured(p)),
        (checks.CheckDef("CR-02", "CR", "Doc Quality", "AIAG-VDA template used", "Should"), checks.cr_02_template(p)),
        (checks.CheckDef("CR-03", "CR", "Doc Quality", "Document searchable (TOC/Ref)", "Should"), checks.cr_03_searchable(p)),
        (checks.CheckDef("CR-04a", "CR", "Doc Quality", "Title and scope defined", "Shall"), checks.cr_04a_title_scope(p)),
        (checks.CheckDef("CR-04b", "CR", "Doc Quality", "Author and approver documented", "Shall"), checks.cr_04b_author_approver(p)),
        (checks.CheckDef("CR-04c", "CR", "Doc Quality", "Unique revision ID", "Shall"), checks.cr_04c_unique_revision(p)),
        (checks.CheckDef("CR-04d", "CR", "Doc Quality", "Change history logged", "Should"), checks.cr_04d_change_history(p)),
        (checks.CheckDef("CR-04e", "CR", "Doc Quality", "Status identified", "Shall"), checks.cr_04e_status(p)),
        (checks.CheckDef("CR-05", "CR", "Doc Quality", "Current revision identifiable", "Shall"), checks.cr_05_current_revision(p)),
        (checks.CheckDef("CR-06", "CR", "Doc Quality", "Configuration management", "Should"), checks.cr_06_config_mgmt(p)),
        (checks.CheckDef("CR-07", "CR", "Doc Quality", "Headers/footers current", "Should"), checks.cr_07_header_footer(p)),
        (checks.CheckDef("CR-08", "CR", "Doc Quality", "Table of Contents present", "Should"), checks.cr_08_toc(p)),
        (checks.CheckDef("CR-09", "CR", "Doc Quality", "References documented", "Should"), checks.cr_09_references(p)),
        (checks.CheckDef("CR-14", "CR", "Doc Quality", "All sections complete", "Shall"), checks.cr_14_all_sections_complete(p)),
    ]
    
    pfmeaa_checks = [
        (checks.CheckDef("PFMEA-01", "PFMEAA", "Completeness", "Header block complete", "Shall"), checks.pfmeaa_01_header_block(p)),
        (checks.CheckDef("PFMEA-02", "PFMEAA", "Completeness", "Process flow chart populated", "Shall"), checks.pfmeaa_02_process_flow(p)),
        (checks.CheckDef("PFMEA-03", "PFMEAA", "Completeness", "Process functions identified", "Shall"), checks.pfmeaa_03_process_functions(p)),
        (checks.CheckDef("PFMEA-04", "PFMEAA", "Completeness", "PFMEA rows complete", "Shall"), checks.pfmeaa_04_pfmea_worksheet_complete(p)),
        (checks.CheckDef("PFMEA-05", "PFMEAA", "Assessment", "S/O/D ratings 1-10", "Shall"), checks.pfmeaa_05_sod_ratings(p)),
        (checks.CheckDef("PFMEA-06", "PFMEAA", "Assessment", "AP computed S*O*D", "Shall"), checks.pfmeaa_06_ap_computed(p)),
        (checks.CheckDef("PFMEA-07", "PFMEAA", "Containment", "High-AP items have actions", "Shall"), checks.pfmeaa_07_high_ap_actions(p)),
        (checks.CheckDef("PFMEA-08", "PFMEAA", "Containment", "Actions have owner and due date", "Shall"), checks.pfmeaa_08_action_plan_ownership(p)),
        (checks.CheckDef("PFMEA-09", "PFMEAA", "Control", "Special characteristics for high-S", "Should"), checks.pfmeaa_09_special_characteristics(p)),
        (checks.CheckDef("PFMEA-10", "PFMEAA", "Control", "Control plan linkage documented", "Shall"), checks.pfmeaa_10_control_plan_linkage(p)),
        (checks.CheckDef("PFMEA-11", "PFMEAA", "Completeness", "Process steps traceability", "Shall"), checks.pfmeaa_11_process_step_traceability(p)),
        (checks.CheckDef("PFMEA-12", "PFMEAA", "Completeness", "Lessons learned cross-referenced", "Should"), checks.pfmeaa_12_lessons_learned(p)),
        (checks.CheckDef("PFMEA-13", "PFMEAA", "Traceability", "DFMEA cross-link", "Should"), checks.pfmeaa_13_dfmea_cross_link(p)),
        (checks.CheckDef("PFMEA-14", "PFMEAA", "Closure", "High-AP completion tracked", "Shall"), checks.pfmeaa_14_high_ap_completion(p)),
    ]
    
    va_checks = [
        (checks.CheckDef("VA-01", "VA", "Verification", "Verification Plan compliance", "Should"), checks.va_01_plan_compliance(p)),
        (checks.CheckDef("VA-02", "VA", "Verification", "Verification methods/samples", "Should"), checks.va_02_methods(p)),
        (checks.CheckDef("VA-03", "VA", "Verification", "Verification executed", "Should"), checks.va_03_executed(p)),
        (checks.CheckDef("VA-04", "VA", "Verification", "Verification Report", "Should"), checks.va_04_report(p)),
    ]
    
    summary_ws = wb.create_sheet("Summary", 3)
    results_dict = {"CR": cr_checks, "PFMEAA": pfmeaa_checks, "VA": va_checks}
    build_dashboard(summary_ws, results_dict, project_label=f"{p.project} - {p.process_name}", checklist_label="PFMEA Checklist")
    
    _build_check_tab(wb, "Confirmation Review", cr_checks, 4)
    _build_check_tab(wb, "PFMEA Assessment", pfmeaa_checks, 5)
    _build_check_tab(wb, "Verification Assessment", va_checks, 6)
    
    wb.save(output_xlsx)
    print(f"\nChecklist written to: {output_xlsx}")
    print(f"Tabs: {len(wb.sheetnames)}")
    
    all_checks = cr_checks + pfmeaa_checks + va_checks
    ratings_count = {}
    for _, result in all_checks:
        rating = result.rating or "Pending"
        ratings_count[rating] = ratings_count.get(rating, 0) + 1
    
    print("\nRating Distribution:")
    for rating in ["FC", "LC", "PC", "NO", "NA", "Pending"]:
        count = ratings_count.get(rating, 0)
        if count > 0:
            print(f"  {rating}: {count}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 generate_checklist.py <input.xlsx> <output.xlsx>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    generate_checklist(input_file, output_file)
