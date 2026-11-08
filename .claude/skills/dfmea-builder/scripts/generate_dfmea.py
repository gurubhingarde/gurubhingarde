"""
DFMEA Builder - generates an AIAG-VDA 2019 Design FMEA workbook from structured JSON input.

Usage:
    python generate_dfmea.py <input.json> <output.xlsx>

Produces 12 tabs:
  00_Title_Page, 01_Document_Control, 02_Header_Block, 03_Structure_Analysis,
  04_Function_Analysis, 05_DFMEA_Worksheet, 06_Special_Characteristics,
  07_Action_Priority_Lookup, 08_Action_Plan_Tracker, 09_DFMEA_Summary_Statistics,
  10_Lessons_Learned_Crossref, 11_References
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# ============================================================================
# Reference data — Severity/Occurrence/Detection ratings and AP lookup
# ============================================================================

SEVERITY_CRITERIA = {
    10: "Hazardous/Uncontrolled; potential loss of life",
    9: "Serious injury or vehicle control loss; safety critical",
    8: "Moderate degradation; occupant safety impact",
    7: "Moderate system malfunction; noticeable to customer",
    6: "Minor degradation; slight customer inconvenience",
    5: "Minor malfunction; minimal customer impact",
    4: "Very minor malfunction; barely noticeable",
    3: "Insignificant impact; user notices no difference",
    2: "No discernible effect",
    1: "No effect",
}

OCCURRENCE_CRITERIA = {
    10: "Very high - almost certain to occur during design life",
    9: "High - very likely to occur",
    8: "Moderately high",
    7: "Moderate",
    6: "Moderately low",
    5: "Low",
    4: "Very low",
    3: "Remote",
    2: "Very remote",
    1: "Almost impossible",
}

DETECTION_CRITERIA = {
    10: "Unlikely to detect; no prevention or detection method available",
    9: "Very low - design control unlikely to detect",
    8: "Low chance of detection",
    7: "Moderate-low chance of detection",
    6: "Moderate chance of detection",
    5: "Moderate-high chance of detection",
    4: "High chance of detection",
    3: "Very high chance of detection",
    2: "Almost certain detection",
    1: "Certain detection",
}

# AIAG-VDA AP Lookup Table (simplified rule-based)
# AP = H if (S>=9 OR (S>=7 AND O>=4) OR (S>=4 AND O>=7 AND D>=7))
#    = M if (S>=4 AND O>=4) OR (S>=7) OR (O>=7 AND D>=7)
#    = L otherwise
def compute_ap(s: int, o: int, d: int) -> str:
    """Compute Action Priority from S, O, D per AIAG-VDA Table P.1 (simplified)."""
    if s >= 9 or (s >= 7 and o >= 4) or (s >= 4 and o >= 7 and d >= 7):
        return "H"
    elif (s >= 4 and o >= 4) or s >= 7 or (o >= 7 and d >= 7):
        return "M"
    else:
        return "L"


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
ORANGE_MEDIUM = "FFE699"

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
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 32


def stripe_body(ws, start_row: int, end_row: int, last_col: int) -> None:
    for r in range(start_row, end_row + 1):
        fill = PatternFill("solid", fgColor=ALT_ROW) if (r - start_row) % 2 else None
        for c in range(1, last_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = body_font()
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER_ALL
            if fill:
                cell.fill = fill


def autosize(ws, widths: dict[int, int]) -> None:
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width


# ============================================================================
# Tab builders
# ============================================================================

def build_title_page(wb: Workbook, prog: dict) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 2, 4, "Design FMEA (DFMEA)")
    style_title_row(ws, 3, 4, prog.get("part_name", "Design"))

    fields = [
        ("Program Name", prog.get("name", "")),
        ("Part Name", prog.get("part_name", "")),
        ("Part Number", prog.get("part_number", "")),
        ("Model Year", prog.get("model_year", "")),
        ("Design Responsibility", prog.get("design_responsibility", "")),
        ("Design Owner", prog.get("design_owner", "")),
        ("Document ID", prog.get("doc_id", "")),
        ("Revision", prog.get("revision", "")),
        ("Date", prog.get("date", "")),
        ("Customer", prog.get("customer", "")),
        ("Company", prog.get("company", "")),
        ("FMEA Team", prog.get("fmea_team", "")),
        ("Methodology", "AIAG-VDA 2019 Edition (harmonized DFMEA)"),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1
    autosize(ws, {1: 4, 2: 28, 3: 60, 4: 4})


def build_doc_control(wb: Workbook) -> None:
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of change", "Approver"])
    for i, row_data in enumerate([
        ("0.1", "", "", "Initial DFMEA generated by dfmea-builder skill", ""),
        ("0.2", "", "", "Design team review and risk assessment", ""),
        ("1.0", "", "", "Released for production", ""),
    ], start=4):
        for c, v in enumerate(row_data, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 6, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_header_block(wb: Workbook, prog: dict) -> None:
    ws = wb.create_sheet("02_Header_Block")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "AIAG-VDA DFMEA Header Block")
    style_header_row(ws, 3, ["Field", "Value", "Notes", ""])

    fields = [
        ("Subject", prog.get("part_name", "Design")),
        ("Project Name", prog.get("name", "")),
        ("FMEA Owner", prog.get("design_owner", "")),
        ("Customer", prog.get("customer", "")),
        ("Model Year(s) / Program(s)", prog.get("model_year", "")),
        ("FMEA ID", prog.get("doc_id", "")),
        ("FMEA Continuous Improvement Status", "In Progress"),
        ("Design Responsibility", prog.get("design_responsibility", "")),
        ("Confidentiality", "Company Confidential"),
        ("FMEA Start Date", prog.get("date", "")),
        ("FMEA Last Revision Date", prog.get("date", "")),
    ]

    row = 4
    for label, value in fields:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, size=11, bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

    stripe_body(ws, 4, 3 + len(fields), 4)
    autosize(ws, {1: 28, 2: 50, 3: 30, 4: 4})


def build_structure_analysis(wb: Workbook, structure: list[dict]) -> None:
    ws = wb.create_sheet("03_Structure_Analysis")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Structure Analysis (System / Subsystem / Component)")
    style_header_row(ws, 3, ["Level", "ID", "Name", "Parent ID", "Function Reference"])

    row = 4
    for item in structure:
        ws.cell(row=row, column=1, value=item.get("level", "System"))
        ws.cell(row=row, column=2, value=item.get("id", ""))
        ws.cell(row=row, column=3, value=item.get("name", ""))
        ws.cell(row=row, column=4, value=item.get("parent", ""))
        ws.cell(row=row, column=5, value="")
        row += 1

    stripe_body(ws, 4, row - 1, 5)
    autosize(ws, {1: 14, 2: 12, 3: 26, 4: 14, 5: 20})


def build_function_analysis(wb: Workbook, functions: list[dict]) -> None:
    ws = wb.create_sheet("04_Function_Analysis")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Function Analysis (Function Tree)")
    style_header_row(ws, 3, ["Function ID", "Parent System/Subsystem", "Function Statement", "Requirement Reference", "ASIL/SC Reference"])

    row = 4
    for func in functions:
        ws.cell(row=row, column=1, value=func.get("id", ""))
        ws.cell(row=row, column=2, value=func.get("parent_id", ""))
        ws.cell(row=row, column=3, value=func.get("function_statement", ""))
        ws.cell(row=row, column=4, value=func.get("requirement_ref", ""))
        ws.cell(row=row, column=5, value=func.get("asil_ref", ""))
        row += 1

    stripe_body(ws, 4, row - 1, 5)
    autosize(ws, {1: 14, 2: 18, 3: 36, 4: 18, 5: 18})


def build_dfmea_worksheet(wb: Workbook, failure_modes: list[dict]) -> list[int]:
    """Main DFMEA worksheet per AIAG-VDA Step 5 (Risk Analysis)."""
    ws = wb.create_sheet("05_DFMEA_Worksheet")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 21, "DFMEA Worksheet (AIAG-VDA 7-Step Process, Steps 3-5)")

    headers = [
        "Item ID", "Focus Element", "Function", "Failure Mode (FM)",
        "Effect on Next Level (FE)", "Effect on End-User (Vehicle)",
        "Severity (1-10)", "Failure Cause (FC)", "Occurrence (1-10)",
        "Prevention Control (PC)", "Occurrence After PC (1-10)",
        "Detection Control (DC)", "Detection (1-10)",
        "Action Priority", "Recommended Action", "Owner", "Target Date",
        "Action Taken", "S/O/D After Action", "AP After Action", "Status"
    ]
    style_header_row(ws, 3, headers)

    fmea_rows = []
    row = 4

    for fm in failure_modes:
        s = fm.get("severity", 5)
        o = fm.get("occurrence", 5)
        d = fm.get("detection", 5)
        ap = compute_ap(s, o, d)

        ws.cell(row=row, column=1, value=fm.get("id", ""))
        ws.cell(row=row, column=2, value=fm.get("focus_element_id", ""))
        ws.cell(row=row, column=3, value=fm.get("function_id", ""))
        ws.cell(row=row, column=4, value=fm.get("failure_mode", ""))
        ws.cell(row=row, column=5, value=fm.get("failure_effect_next", ""))
        ws.cell(row=row, column=6, value=fm.get("failure_effect_user", ""))
        ws.cell(row=row, column=7, value=s)
        ws.cell(row=row, column=8, value=fm.get("failure_cause", ""))
        ws.cell(row=row, column=9, value=o)
        ws.cell(row=row, column=10, value=fm.get("prevention_control", ""))
        ws.cell(row=row, column=11, value=fm.get("occurrence_after_pc", o))
        ws.cell(row=row, column=12, value=fm.get("detection_control", ""))
        ws.cell(row=row, column=13, value=d)
        ws.cell(row=row, column=14, value=ap)
        ws.cell(row=row, column=15, value=fm.get("recommended_action", ""))
        ws.cell(row=row, column=16, value=fm.get("owner", ""))
        ws.cell(row=row, column=17, value=fm.get("target_date", ""))
        ws.cell(row=row, column=18, value="")
        ws.cell(row=row, column=19, value="")
        ws.cell(row=row, column=20, value="")
        ws.cell(row=row, column=21, value="")

        # Color AP cell based on value
        ap_cell = ws.cell(row=row, column=14)
        if ap == "H":
            ap_cell.fill = PatternFill("solid", fgColor=RED_BAD)
        elif ap == "M":
            ap_cell.fill = PatternFill("solid", fgColor=ORANGE_MEDIUM)
        else:
            ap_cell.fill = PatternFill("solid", fgColor=GREEN_OK)

        fmea_rows.append(row)
        row += 1

    stripe_body(ws, 4, row - 1, len(headers))
    ws.freeze_panes = "A4"
    autosize(ws, {
        1: 12, 2: 14, 3: 14, 4: 18, 5: 16, 6: 18, 7: 12, 8: 16,
        9: 12, 10: 16, 11: 14, 12: 16, 13: 12, 14: 12, 15: 20, 16: 12,
        17: 14, 18: 14, 19: 16, 20: 14, 21: 12
    })

    return fmea_rows


def build_special_characteristics(wb: Workbook) -> None:
    ws = wb.create_sheet("06_Special_Characteristics")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Special Characteristics (SC) Identified During DFMEA")
    style_header_row(ws, 3, ["Characteristic", "Classification", "Source FM ID", "Recommended Controls"])

    ws.cell(row=4, column=1, value="(Identified from high-severity failure modes)")
    ws.merge_cells(start_row=4, start_column=1, end_row=4, end_column=4)

    autosize(ws, {1: 28, 2: 22, 3: 16, 4: 40})


def build_ap_lookup_table(wb: Workbook) -> None:
    """AIAG-VDA Action Priority lookup table (S x O x D -> H/M/L)."""
    ws = wb.create_sheet("07_Action_Priority_Lookup")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 12, "Action Priority (AP) Lookup Table (AIAG-VDA)")

    # Build 3D lookup: S rows, O columns, D as separate sections
    row = 3
    for d in range(1, 11):
        ws.cell(row=row, column=1, value=f"Detection (D) = {d}").font = Font(bold=True)
        style_header_row(ws, row + 1, ["Severity \\ Occurrence"] + [str(o) for o in range(1, 11)])

        data_row = row + 2
        for s in range(1, 11):
            ws.cell(row=data_row, column=1, value=s)
            for o in range(1, 11):
                ap = compute_ap(s, o, d)
                cell = ws.cell(row=data_row, column=o + 1, value=ap)
                if ap == "H":
                    cell.fill = PatternFill("solid", fgColor=RED_BAD)
                elif ap == "M":
                    cell.fill = PatternFill("solid", fgColor=ORANGE_MEDIUM)
                else:
                    cell.fill = PatternFill("solid", fgColor=GREEN_OK)
            data_row += 1

        row = data_row + 2

    autosize(ws, {i: 8 for i in range(1, 12)})


def build_action_plan_tracker(wb: Workbook, failure_modes: list[dict]) -> None:
    ws = wb.create_sheet("08_Action_Plan_Tracker")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Action Plan Tracker (Gantt-style from DFMEA Actions)")
    style_header_row(ws, 3, ["Action ID", "FM Reference", "Action Description", "Owner", "Due Date", "Status", "Verified Date"])

    row = 4
    for fm in failure_modes:
        if fm.get("recommended_action"):
            ws.cell(row=row, column=1, value=fm.get("id", ""))
            ws.cell(row=row, column=2, value=fm.get("id", ""))
            ws.cell(row=row, column=3, value=fm.get("recommended_action", ""))
            ws.cell(row=row, column=4, value=fm.get("owner", ""))
            ws.cell(row=row, column=5, value=fm.get("target_date", ""))
            ws.cell(row=row, column=6, value="Open")
            ws.cell(row=row, column=7, value="")
            row += 1

    stripe_body(ws, 4, row - 1, 7)
    autosize(ws, {1: 12, 2: 14, 3: 40, 4: 14, 5: 14, 6: 12, 7: 14})


def build_summary_statistics(wb: Workbook, failure_modes: list[dict]) -> None:
    ws = wb.create_sheet("09_DFMEA_Summary_Statistics")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "DFMEA Summary Statistics")

    # Count by AP
    ap_high = sum(1 for fm in failure_modes if compute_ap(fm.get("severity", 5), fm.get("occurrence", 5), fm.get("detection", 5)) == "H")
    ap_medium = sum(1 for fm in failure_modes if compute_ap(fm.get("severity", 5), fm.get("occurrence", 5), fm.get("detection", 5)) == "M")
    ap_low = sum(1 for fm in failure_modes if compute_ap(fm.get("severity", 5), fm.get("occurrence", 5), fm.get("detection", 5)) == "L")

    style_header_row(ws, 3, ["Metric", "Count"])
    ws.cell(row=4, column=1, value="High Priority (AP=H) Items")
    ws.cell(row=4, column=2, value=ap_high)
    ws.cell(row=5, column=1, value="Medium Priority (AP=M) Items")
    ws.cell(row=5, column=2, value=ap_medium)
    ws.cell(row=6, column=1, value="Low Priority (AP=L) Items")
    ws.cell(row=6, column=2, value=ap_low)
    ws.cell(row=7, column=1, value="Total Failure Modes")
    ws.cell(row=7, column=2, value=len(failure_modes))

    stripe_body(ws, 4, 7, 2)
    autosize(ws, {1: 36, 2: 12})


def build_lessons_learned(wb: Workbook) -> None:
    ws = wb.create_sheet("10_Lessons_Learned_Crossref")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Lessons Learned & Family DFMEA Cross-Reference")
    style_header_row(ws, 3, ["Prior DFMEA / Document", "Relevant Failure Modes", "Lessons Applied", "Notes"])

    ws.cell(row=4, column=1, value="(Link to family DFMEA, prior design iterations, or similar products)")
    ws.merge_cells(start_row=4, start_column=1, end_row=4, end_column=4)

    autosize(ws, {1: 30, 2: 30, 3: 26, 4: 30})


def build_references(wb: Workbook) -> None:
    ws = wb.create_sheet("11_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References & Methodology")

    refs = [
        ("AIAG-VDA FMEA Handbook 2019", "Harmonized replacement for AIAG-4; Section P: Action Priority tables"),
        ("ISO 26262 Part 3", "Item definition and requirements specification"),
        ("OEM-Specific FMEA Requirements", "Customer-supplied checklists and expectations"),
        ("Related DFMEAs", "Family DFMEA, subsystem DFMEAs for integration"),
    ]

    row = 3
    for std, desc in refs:
        ws.cell(row=row, column=1, value=std).font = Font(bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1

    autosize(ws, {1: 40, 2: 80})


# ============================================================================
# Main generator
# ============================================================================

def generate(input_path: str, output_path: str) -> dict:
    with open(input_path) as f:
        data = json.load(f)

    prog = data.get("program", {})
    structure = data.get("structure", [])
    functions = data.get("functions", [])
    failure_modes = data.get("failure_modes", [])

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, prog)
    build_doc_control(wb)
    build_header_block(wb, prog)
    build_structure_analysis(wb, structure)
    build_function_analysis(wb, functions)
    fmea_rows = build_dfmea_worksheet(wb, failure_modes)
    build_special_characteristics(wb)
    build_ap_lookup_table(wb)
    build_action_plan_tracker(wb, failure_modes)
    build_summary_statistics(wb, failure_modes)
    build_lessons_learned(wb)
    build_references(wb)

    wb.active = 0
    wb.save(output_path)

    # Count AP distribution
    ap_h = sum(1 for fm in failure_modes if compute_ap(fm.get("severity", 5), fm.get("occurrence", 5), fm.get("detection", 5)) == "H")
    ap_m = sum(1 for fm in failure_modes if compute_ap(fm.get("severity", 5), fm.get("occurrence", 5), fm.get("detection", 5)) == "M")
    ap_l = sum(1 for fm in failure_modes if compute_ap(fm.get("severity", 5), fm.get("occurrence", 5), fm.get("detection", 5)) == "L")

    return {
        "output_path": output_path,
        "tabs": 12,
        "failure_modes": len(failure_modes),
        "ap_distribution": {"High": ap_h, "Medium": ap_m, "Low": ap_l},
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_dfmea.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    import json
    print(json.dumps(summary, indent=2))
