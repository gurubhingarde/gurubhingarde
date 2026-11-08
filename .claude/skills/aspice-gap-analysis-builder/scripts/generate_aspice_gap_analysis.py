"""
ASPICE Gap Analysis Builder - generates gap analysis from assessment + target CL definition.

Usage:
    python generate_aspice_gap_analysis.py <input.json> <output.xlsx>

The gap analysis is built entirely from <input.json> (config / processes / gaps).
A legacy 3-argument form is still accepted for backward compatibility:

    python generate_aspice_gap_analysis.py <assessment.xlsx> <input.json> <output.xlsx>

but the leading assessment workbook has never been read and is ignored with a
warning. Pass current capability levels via the `processes[].current_cl` field.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def title_font(size: int = 16) -> Font:
    return Font(name=FONT_NAME, size=size, bold=True, color="FFFFFF")


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def style_title_row(ws, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = title_font(14)
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
# Tab creators
# ============================================================================

def create_title_page(ws, config: dict[str, Any]) -> None:
    ws.merge_cells("A1:C1")
    ws.cell(1, 1, "ASPICE Gap Analysis").font = title_font(20)
    ws.cell(1, 1).fill = PatternFill("solid", fgColor=NAVY)
    ws.cell(1, 1).alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    row = 4
    for k, v in [
        ("Project", config.get("project_name", "")),
        ("Gap Analysis Date", config.get("date", "")),
        ("Gap Analysis Owner", config.get("owner", "")),
    ]:
        ws.cell(row, 1, k).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row, 2, v)
        row += 1

    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40


def create_document_control(ws, config: dict[str, Any]) -> None:
    style_title_row(ws, 1, 5, "Document Control")
    headers = ["Revision", "Date", "Author", "Change Description", "Status"]
    style_header_row(ws, 3, headers)
    ws.cell(4, 1, "1.0")
    ws.cell(4, 2, config.get("date", ""))
    ws.cell(4, 3, config.get("owner", ""))
    ws.cell(4, 4, "Initial Gap Analysis")
    ws.cell(4, 5, "Draft")
    stripe_body(ws, 4, 4, 5)
    autosize(ws, {1: 12, 2: 12, 3: 20, 4: 30, 5: 12})


def create_current_state_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 3, "Current State (assessed CL, from input JSON)")
    headers = ["Process ID", "Process Name", "Current CL"]
    style_header_row(ws, 3, headers)

    row = 4
    for proc in processes:
        ws.cell(row, 1, proc.get("process_id", ""))
        ws.cell(row, 2, proc.get("process_name", ""))
        ws.cell(row, 3, proc.get("current_cl", ""))
        row += 1

    stripe_body(ws, 4, row - 1, 3)
    autosize(ws, {1: 12, 2: 25, 3: 12})


def create_target_state_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 4, "Target State")
    headers = ["Process ID", "Current CL", "Target CL", "Justification"]
    style_header_row(ws, 3, headers)

    row = 4
    for proc in processes:
        ws.cell(row, 1, proc.get("process_id", ""))
        ws.cell(row, 2, proc.get("current_cl", ""))
        ws.cell(row, 3, proc.get("target_cl", ""))
        ws.cell(row, 4, proc.get("justification", "")).alignment = Alignment(wrap_text=True)
        row += 1

    stripe_body(ws, 4, row - 1, 4)
    autosize(ws, {1: 12, 2: 12, 3: 12, 4: 40})


def create_gaps_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 4, "Gaps per Process")
    headers = ["Process ID", "Current->Target", "Missing PAs", "Gap Description"]
    style_header_row(ws, 3, headers)

    row = 4
    for proc in processes:
        current = proc.get("current_cl", 0)
        target = proc.get("target_cl", 0)
        if isinstance(current, str):
            current = int(current) if current else 0
        if isinstance(target, str):
            target = int(target) if target else 0

        ws.cell(row, 1, proc.get("process_id", ""))
        ws.cell(row, 2, f"CL{current} -> CL{target}")
        ws.cell(row, 3, proc.get("missing_pas", ""))
        ws.cell(row, 4, proc.get("gap_description", "")).alignment = Alignment(wrap_text=True)
        row += 1

    stripe_body(ws, 4, row - 1, 4)
    autosize(ws, {1: 12, 2: 15, 3: 30, 4: 35})


def create_severity_tab(ws, gaps_summary: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 5, "Gap Severity Classification")
    headers = ["Gap ID", "Gap Description", "Severity", "Impact", "Mitigation"]
    style_header_row(ws, 3, headers)

    row = 4
    for gap in gaps_summary:
        ws.cell(row, 1, gap.get("id", ""))
        ws.cell(row, 2, gap.get("description", "")).alignment = Alignment(wrap_text=True)
        ws.cell(row, 3, gap.get("severity", ""))
        ws.cell(row, 4, gap.get("impact", ""))
        ws.cell(row, 5, gap.get("mitigation", "")).alignment = Alignment(wrap_text=True)
        row += 1

    stripe_body(ws, 4, max(4, row - 1), 5)
    autosize(ws, {1: 10, 2: 25, 3: 15, 4: 15, 5: 30})


def create_effort_tab(ws) -> None:
    style_title_row(ws, 1, 5, "Effort Estimation")
    headers = ["Gap ID", "Description", "Est. Effort (days)", "Elapsed Time (weeks)", "Resources"]
    style_header_row(ws, 3, headers)
    autosize(ws, {1: 10, 2: 25, 3: 18, 4: 18, 5: 20})


def create_quick_wins_tab(ws) -> None:
    style_title_row(ws, 1, 4, "Quick Wins")
    headers = ["Gap ID", "Description", "Effort (days)", "Impact"]
    style_header_row(ws, 3, headers)
    autosize(ws, {1: 10, 2: 30, 3: 15, 4: 20})


def create_major_initiatives_tab(ws) -> None:
    style_title_row(ws, 1, 5, "Major Improvement Initiatives")
    headers = ["Initiative ID", "Gaps Addressed", "Owner", "Timeline", "Budget"]
    style_header_row(ws, 3, headers)
    autosize(ws, {1: 12, 2: 30, 3: 15, 4: 15, 5: 15})


def create_references_tab(ws) -> None:
    style_title_row(ws, 1, 2, "References")
    row = 3
    refs = [
        ("ASPICE PAM v3.1", "Automotive SPICE Process Assessment Model"),
        ("ASPICE PAM v4.0", "Automotive SPICE Process Assessment Model v4.0"),
        ("ISO/IEC 33004", "Information technology Process assessment guidelines"),
    ]
    for ref_name, ref_desc in refs:
        ws.cell(row, 1, ref_name).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row, 2, ref_desc).alignment = Alignment(wrap_text=True)
        row += 1
    autosize(ws, {1: 20, 2: 60})


# ============================================================================
# Main
# ============================================================================

def generate_gap_analysis(input_json: str, output_xlsx: str) -> None:
    with open(input_json) as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    tabs = [
        ("00_Title_Page", lambda ws: create_title_page(ws, data.get("config", {}))),
        ("01_Document_Control", lambda ws: create_document_control(ws, data.get("config", {}))),
        ("02_Current_State", lambda ws: create_current_state_tab(ws, data.get("processes", []))),
        ("03_Target_State", lambda ws: create_target_state_tab(ws, data.get("processes", []))),
        ("04_Gaps", lambda ws: create_gaps_tab(ws, data.get("processes", []))),
        ("05_Gap_Severity", lambda ws: create_severity_tab(ws, data.get("gaps", []))),
        ("06_Effort_Estimation", lambda ws: create_effort_tab(ws)),
        ("07_Quick_Wins", lambda ws: create_quick_wins_tab(ws)),
        ("08_Major_Initiatives", lambda ws: create_major_initiatives_tab(ws)),
        ("09_References", lambda ws: create_references_tab(ws)),
    ]

    for tab_name, creator in tabs:
        ws = wb.create_sheet(tab_name)
        creator(ws)

    wb.save(output_xlsx)
    print(json.dumps({"status": "ok", "tabs": len(tabs), "processes": len(data.get("processes", []))}))


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 3:
        # Legacy form: <assessment.xlsx> <input.json> <output.xlsx>. The assessment
        # workbook has never been read by this generator; current CLs come from the
        # JSON `processes[].current_cl` field. Accepted, ignored, and warned about.
        print(
            "WARNING: the leading assessment workbook argument is ignored; "
            "current capability levels are read from <input.json> "
            "(processes[].current_cl). Use the 2-argument form: "
            "<input.json> <output.xlsx>",
            file=sys.stderr,
        )
        args = args[1:]
    if len(args) != 2:
        print(
            "Usage: python generate_aspice_gap_analysis.py <input.json> <output.xlsx>",
            file=sys.stderr,
        )
        sys.exit(1)
    generate_gap_analysis(args[0], args[1])
