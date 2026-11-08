"""
PFMEA Builder - generates AIAG-VDA Process FMEA workbook from manufacturing input JSON.

Usage:
    python generate_pfmea.py <input.json> <output.xlsx>

Produces 13 tabs:
  00_Title_Page, 01_Document_Control, 02_Header_Block, 03_Process_Flow,
  04_Process_Function_Analysis, 05_PFMEA_Worksheet, 06_Special_Characteristics,
  07_Action_Priority_Lookup, 08_Action_Plan_Tracker, 09_PFMEA_Summary_Statistics,
  10_Linkage_to_Control_Plan, 11_Lessons_Learned_Crossref, 12_References
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# ============================================================================
# Styling
# ============================================================================

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"
ORANGE = "F4B084"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def style_title_row(ws, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header_row(ws, row: int, headers: list[str]) -> None:
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = header_font()
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 22


def style_body_cell(cell, is_alt_row: bool = False, is_formula: bool = False, is_ap_high: bool = False, is_ap_med: bool = False) -> None:
    cell.font = body_font()
    cell.border = BORDER_ALL
    if is_ap_high:
        cell.fill = PatternFill("solid", fgColor=RED_BAD)
    elif is_ap_med:
        cell.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    elif is_formula:
        cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)
    elif is_alt_row:
        cell.fill = PatternFill("solid", fgColor=ALT_ROW)


# ============================================================================
# AP Lookup Table (AIAG-VDA)
# ============================================================================

def get_ap(s: int, o: int, d: int) -> str:
    """
    Compute Action Priority from S/O/D using AIAG-VDA matrix.
    Returns 'H' (High), 'M' (Medium), or 'L' (Low).
    Based on Risk Priority Score thresholds (not raw S*O*D).
    """
    # AIAG-VDA simplified approach: use thresholds on combined score
    # S * O as the primary risk, then adjusted by D
    base_score = s * o

    if base_score >= 70:  # Very high risk
        if d <= 3:
            return "H"
        elif d <= 6:
            return "M"
        else:
            return "M"
    elif base_score >= 50:  # High risk
        if d <= 2:
            return "H"
        elif d <= 5:
            return "M"
        else:
            return "L"
    elif base_score >= 30:  # Moderate risk
        if d <= 3:
            return "M"
        elif d <= 6:
            return "L"
        else:
            return "L"
    elif base_score >= 20:  # Low-moderate risk
        if d <= 2:
            return "M"
        else:
            return "L"
    else:
        return "L"


# ============================================================================
# Tab generators
# ============================================================================

def make_title_page(wb, program: dict) -> None:
    ws = wb.create_sheet("00_Title_Page", 0)
    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 60

    row = 1
    style_title_row(ws, row, 2, "AIAG-VDA PROCESS FMEA")
    row += 2

    data = [
        ("Program Name", program.get("name", "TBD")),
        ("Process Name", program.get("process_name", "TBD")),
        ("Process Responsibility", program.get("process_responsibility", "TBD")),
        ("Model Year", program.get("model_year", "TBD")),
        ("Document ID", program.get("doc_id", "TBD")),
        ("Revision", program.get("revision", "1.0")),
        ("Date", program.get("date", datetime.now().strftime("%Y-%m-%d"))),
        ("FMEA Owner", program.get("fmea_owner", "TBD")),
        ("FMEA Team", program.get("fmea_team", "TBD")),
        ("Customer", program.get("customer", "TBD")),
        ("Company", program.get("company", "TBD")),
    ]

    for label, value in data:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, size=11, bold=True)
        ws.cell(row=row, column=2, value=value).font = body_font()
        row += 1


def make_document_control(wb) -> None:
    ws = wb.create_sheet("01_Document_Control", 1)
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 50

    headers = ["Revision", "Date", "Author", "Change Summary"]
    style_header_row(ws, 1, headers)

    # Sample revision history
    row = 2
    data = [
        ["1.0", datetime.now().strftime("%Y-%m-%d"), "FMEA Team", "Initial release"],
    ]
    for i, record in enumerate(data):
        for col, val in enumerate(record, start=1):
            cell = ws.cell(row=row, column=col, value=val)
            style_body_cell(cell, is_alt_row=(i % 2 == 0))
        row += 1


def make_header_block(wb) -> None:
    ws = wb.create_sheet("02_Header_Block", 2)
    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 60

    row = 1
    style_title_row(ws, row, 2, "AIAG-VDA PFMEA Standard Header")
    row += 2

    headers_info = [
        "SYSTEM / COMPONENT",
        "PROCESS STEP ANALYZED",
        "PROCESS FLOW CHART PAGE",
        "PREP DATE",
        "FMEA REVIEW DATE",
        "RESPONSIBLE FUNCTION",
    ]

    for label in headers_info:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, size=11, bold=True)
        ws.cell(row=row, column=2, value="")
        row += 1


def make_process_flow(wb, process_flow: list) -> None:
    ws = wb.create_sheet("03_Process_Flow", 3)

    headers = ["Step ID", "Step Name", "Step Type", "Upstream Step", "Downstream Step",
               "Equipment", "Key Characteristics", "Key Parameters"]

    col_widths = [10, 20, 15, 15, 15, 20, 25, 25]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    style_header_row(ws, 1, headers)

    row = 2
    for i, step in enumerate(process_flow):
        data = [
            step.get("step_id", ""),
            step.get("step_name", ""),
            step.get("step_type", ""),
            step.get("upstream_step", ""),
            step.get("downstream_step", ""),
            step.get("equipment", ""),
            step.get("key_characteristics", ""),
            step.get("key_parameters", ""),
        ]
        for col, val in enumerate(data, start=1):
            cell = ws.cell(row=row, column=col, value=val)
            style_body_cell(cell, is_alt_row=(i % 2 == 0))
        row += 1


def make_process_functions(wb, process_functions: list) -> None:
    ws = wb.create_sheet("04_Process_Function_Analysis", 4)

    headers = ["Step ID", "Function", "Requirement", "Product/Process Characteristic", "Special Char (SC/CC)"]

    col_widths = [12, 25, 25, 30, 12]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    style_header_row(ws, 1, headers)

    row = 2
    for i, func in enumerate(process_functions):
        data = [
            func.get("step_id", ""),
            func.get("function", ""),
            func.get("requirement", ""),
            func.get("characteristic", ""),
            func.get("special_characteristic", ""),
        ]
        for col, val in enumerate(data, start=1):
            cell = ws.cell(row=row, column=col, value=val)
            style_body_cell(cell, is_alt_row=(i % 2 == 0))
        row += 1


def make_pfmea_worksheet(wb, failure_modes: list, process_flow: list) -> None:
    ws = wb.create_sheet("05_PFMEA_Worksheet", 5)

    headers = [
        "Step ID", "Process Step", "Process Function", "Failure Mode",
        "Failure Effect (Next Op)", "Failure Effect (End User)", "Severity",
        "Failure Cause", "Occurrence", "Prevention Control", "Detection Control", "Detection",
        "Action Priority", "Recommended Action", "Responsibility", "Target Date",
        "Actions Taken", "Revised S", "Revised O", "Revised D", "Revised AP", "Status"
    ]

    col_widths = [10, 15, 15, 18, 18, 18, 8, 15, 8, 15, 15, 8, 10, 18, 15, 12, 15, 8, 8, 8, 10, 10]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    style_header_row(ws, 1, headers)

    row = 2
    for i, fm in enumerate(failure_modes):
        s = int(fm.get("severity", 5))
        o = int(fm.get("occurrence", 5))
        d = int(fm.get("detection", 5))

        # Compute AP from S/O/D
        ap_value = get_ap(s, o, d)

        # Determine AP color
        is_high = (ap_value == "H")
        is_med = (ap_value == "M")

        data = [
            fm.get("step_id", ""),
            fm.get("process_step", ""),
            fm.get("process_function", ""),
            fm.get("failure_mode", ""),
            fm.get("failure_effect_next_op", ""),
            fm.get("failure_effect_end_user", ""),
            s,
            fm.get("failure_cause", ""),
            o,
            fm.get("prevention_control", ""),
            fm.get("detection_control", ""),
            d,
            ap_value,
            fm.get("recommended_action", ""),
            fm.get("owner", ""),
            fm.get("target_date", ""),
            fm.get("actions_taken", ""),
            "",  # Revised S (editable)
            "",  # Revised O (editable)
            "",  # Revised D (editable)
            "",  # Revised AP (formula)
            fm.get("status", "Open"),
        ]

        for col, val in enumerate(data, start=1):
            cell = ws.cell(row=row, column=col, value=val)

            # Highlight AP column
            if col == 13:  # AP column
                style_body_cell(cell, is_ap_high=is_high, is_ap_med=is_med)
            else:
                style_body_cell(cell, is_alt_row=(i % 2 == 0))

        row += 1


def make_special_characteristics(wb) -> None:
    ws = wb.create_sheet("06_Special_Characteristics", 6)

    headers = ["Characteristic", "Classification", "Source Step", "Recommended Control Method", "Monitoring Plan"]
    col_widths = [20, 20, 15, 25, 25]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    style_header_row(ws, 1, headers)

    # Sample SCs
    sample_scs = [
        ["Component Placement Accuracy", "SC", "SMT Placement", "Visual Inspection + AOI", "100% AOI check"],
        ["Solder Joint Quality", "SC", "Reflow", "AOI + X-ray sampling", "Statistical SPC"],
        ["Test Coverage", "CC", "ICT Test", "Functional test vector update", "Test log review"],
    ]

    for i, sc in enumerate(sample_scs):
        for col, val in enumerate(sc, start=1):
            cell = ws.cell(row=i+2, column=col, value=val)
            style_body_cell(cell, is_alt_row=(i % 2 == 0))


def make_ap_lookup(wb) -> None:
    ws = wb.create_sheet("07_Action_Priority_Lookup", 7)

    ws.merge_cells("A1:D1")
    title = ws.cell(row=1, column=1, value="AIAG-VDA Action Priority Lookup (S x O x D)")
    title.font = Font(name=FONT_NAME, size=12, bold=True)

    ws.cell(row=3, column=1, value="Severity").font = Font(name=FONT_NAME, size=10, bold=True)
    ws.cell(row=3, column=2, value="Occurrence").font = Font(name=FONT_NAME, size=10, bold=True)
    ws.cell(row=3, column=3, value="Detection").font = Font(name=FONT_NAME, size=10, bold=True)
    ws.cell(row=3, column=4, value="Action Priority").font = Font(name=FONT_NAME, size=10, bold=True)

    row = 4
    # Generate all S/O/D combinations (1-10)
    for s in range(1, 11):
        for o in range(1, 11):
            for d in range(1, 11):
                ws.cell(row=row, column=1, value=s)
                ws.cell(row=row, column=2, value=o)
                ws.cell(row=row, column=3, value=d)
                ap = get_ap(s, o, d)
                ap_cell = ws.cell(row=row, column=4, value=ap)

                # Color AP cells
                if ap == "H":
                    ap_cell.fill = PatternFill("solid", fgColor=RED_BAD)
                elif ap == "M":
                    ap_cell.fill = PatternFill("solid", fgColor=WARN_YELLOW)
                else:
                    ap_cell.fill = PatternFill("solid", fgColor=GREEN_OK)

                row += 1


def make_action_plan_tracker(wb) -> None:
    ws = wb.create_sheet("08_Action_Plan_Tracker", 8)

    headers = ["Action ID", "Description", "Owner", "Target Date", "Status", "% Complete", "Completion Date"]
    col_widths = [12, 25, 15, 15, 12, 12, 15]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    style_header_row(ws, 1, headers)


def make_summary_statistics(wb, failure_modes: list) -> None:
    ws = wb.create_sheet("09_PFMEA_Summary_Statistics", 9)

    ws.column_dimensions["A"].width = 35
    ws.column_dimensions["B"].width = 15

    row = 1
    style_title_row(ws, row, 2, "PFMEA Summary Statistics")
    row += 2

    # Count by AP
    high_count = sum(1 for fm in failure_modes
                     if get_ap(int(fm.get("severity", 5)),
                              int(fm.get("occurrence", 5)),
                              int(fm.get("detection", 5))) == "H")
    med_count = sum(1 for fm in failure_modes
                    if get_ap(int(fm.get("severity", 5)),
                             int(fm.get("occurrence", 5)),
                             int(fm.get("detection", 5))) == "M")
    low_count = sum(1 for fm in failure_modes
                    if get_ap(int(fm.get("severity", 5)),
                             int(fm.get("occurrence", 5)),
                             int(fm.get("detection", 5))) == "L")

    stats = [
        ("Total Failure Modes", len(failure_modes)),
        ("High Priority (H)", high_count),
        ("Medium Priority (M)", med_count),
        ("Low Priority (L)", low_count),
        ("Total Process Steps", len(set(fm.get("step_id", "") for fm in failure_modes))),
    ]

    for label, value in stats:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, size=11, bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1


def make_linkage_to_control_plan(wb) -> None:
    ws = wb.create_sheet("10_Linkage_to_Control_Plan", 10)

    headers = ["PFMEA Step ID", "Failure Mode", "Control Plan Characteristic", "Control Method", "Acceptance Criteria"]
    col_widths = [15, 20, 25, 25, 25]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    style_header_row(ws, 1, headers)

    ws.cell(row=2, column=1, value="(Populated during Control Plan generation)")


def make_lessons_learned(wb) -> None:
    ws = wb.create_sheet("11_Lessons_Learned_Crossref", 11)

    headers = ["Reference Source", "Relevant Failure Mode", "Lessons Learned", "Application to Current PFMEA"]
    col_widths = [20, 25, 30, 30]
    for i, w in enumerate(col_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    style_header_row(ws, 1, headers)


def make_references(wb) -> None:
    ws = wb.create_sheet("12_References", 12)
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title_row(ws, row, 1, "References & Standards")
    row += 2

    refs = [
        "AIAG-VDA FMEA Handbook (2019)",
        "ISO/TS 16949:2016 - Automotive Quality Management",
        "IATF 16949:2016 - Automotive Technical Standard",
        "Customer Technical Specifications (if applicable)",
        "Related DFMEA Documents",
        "Prior PFMEA Family Studies",
    ]

    for ref in refs:
        ws.cell(row=row, column=1, value=f"• {ref}")
        row += 1


# ============================================================================
# Main generator
# ============================================================================

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_pfmea.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: Input file {input_file} not found")
        sys.exit(1)

    with open(input_file, "r") as f:
        data = json.load(f)

    program = data.get("program", {})
    process_flow = data.get("process_flow", [])
    process_functions = data.get("process_functions", [])
    failure_modes = data.get("failure_modes", [])

    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    make_title_page(wb, program)
    make_document_control(wb)
    make_header_block(wb)
    make_process_flow(wb, process_flow)
    make_process_functions(wb, process_functions)
    make_pfmea_worksheet(wb, failure_modes, process_flow)
    make_special_characteristics(wb)
    make_ap_lookup(wb)
    make_action_plan_tracker(wb)
    make_summary_statistics(wb, failure_modes)
    make_linkage_to_control_plan(wb)
    make_lessons_learned(wb)
    make_references(wb)

    wb.save(str(output_file))
    print(f"Generated {output_file} with {len(wb.sheetnames)} tabs")
    print(f"Process steps: {len(process_flow)}")
    print(f"Failure modes: {len(failure_modes)}")


if __name__ == "__main__":
    main()
