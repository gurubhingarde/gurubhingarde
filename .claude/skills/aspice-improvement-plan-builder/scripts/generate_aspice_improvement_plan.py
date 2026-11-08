"""
ASPICE Improvement Plan Builder - generates improvement roadmap from gap analysis.

Usage:
    python generate_aspice_improvement_plan.py <input.json> <output.xlsx>

The improvement plan is built entirely from <input.json> (config / processes /
initiatives). A legacy 3-argument form is still accepted for backward
compatibility:

    python generate_aspice_improvement_plan.py <gap_analysis.xlsx> <input.json> <output.xlsx>

but the leading gap-analysis workbook has never been read and is ignored with a
warning. Pass gap rows via the `processes` field, which populates the
02_Gaps_From_Analysis echo tab.
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
# Tabs
# ============================================================================

def create_title_page(ws, config: dict[str, Any]) -> None:
    ws.merge_cells("A1:C1")
    ws.cell(1, 1, "ASPICE Improvement Plan").font = title_font(20)
    ws.cell(1, 1).fill = PatternFill("solid", fgColor=NAVY)
    ws.cell(1, 1).alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    row = 4
    for k, v in [
        ("Improvement Program", config.get("program_name", "")),
        ("Sponsor", config.get("sponsor", "")),
        ("Target Completion Date", config.get("target_date", "")),
        ("Program Manager", config.get("program_manager", "")),
    ]:
        ws.cell(row, 1, k).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row, 2, v)
        row += 1

    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40


def create_document_control(ws) -> None:
    style_title_row(ws, 1, 5, "Document Control")
    headers = ["Revision", "Date", "Author", "Change", "Status"]
    style_header_row(ws, 3, headers)
    ws.cell(4, 1, "1.0")
    ws.cell(4, 2, datetime.now().strftime("%Y-%m-%d"))
    ws.cell(4, 3, "Program Manager")
    ws.cell(4, 4, "Initial Plan")
    ws.cell(4, 5, "Draft")
    stripe_body(ws, 4, 4, 5)
    autosize(ws, {1: 12, 2: 12, 3: 20, 4: 20, 5: 12})


def create_gaps_echo_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 3, "Gaps from Gap Analysis")
    headers = ["Process ID", "Gap Description", "Target CL"]
    style_header_row(ws, 3, headers)
    row = 4
    for proc in processes:
        ws.cell(row, 1, proc.get("process_id", ""))
        ws.cell(row, 2, proc.get("gap_description", "")).alignment = Alignment(wrap_text=True)
        ws.cell(row, 3, proc.get("target_cl", ""))
        row += 1
    stripe_body(ws, 4, row - 1, 3)
    autosize(ws, {1: 12, 2: 40, 3: 12})


def create_initiatives_tab(ws, initiatives: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 6, "Improvement Initiatives")
    headers = ["Initiative ID", "Name", "Gaps Addressed", "Owner", "Duration (months)", "Budget"]
    style_header_row(ws, 3, headers)
    row = 4
    for init in initiatives:
        ws.cell(row, 1, init.get("id", ""))
        ws.cell(row, 2, init.get("name", ""))
        ws.cell(row, 3, init.get("gaps", ""))
        ws.cell(row, 4, init.get("owner", ""))
        ws.cell(row, 5, init.get("duration", ""))
        ws.cell(row, 6, init.get("budget", ""))
        row += 1
    stripe_body(ws, 4, max(4, row - 1), 6)
    autosize(ws, {1: 12, 2: 20, 3: 25, 4: 15, 5: 15, 6: 12})


def create_roadmap_tab(ws) -> None:
    style_title_row(ws, 1, 14, "Improvement Roadmap (Gantt-style Timeline)")
    headers = ["Initiative"] + [f"M{i}" for i in range(1, 13)]
    style_header_row(ws, 3, headers)
    autosize(ws, {1: 20, **{i: 6 for i in range(2, 14)}})


def create_resources_tab(ws) -> None:
    style_title_row(ws, 1, 5, "Resources and Budget")
    headers = ["Initiative ID", "Resource Type", "Quantity/Cost", "Timeline", "Status"]
    style_header_row(ws, 3, headers)
    autosize(ws, {1: 12, 2: 18, 3: 18, 4: 15, 5: 15})


def create_risks_tab(ws) -> None:
    style_title_row(ws, 1, 6, "Risk Register")
    headers = ["Risk ID", "Risk Description", "Likelihood", "Impact", "Mitigation", "Owner"]
    style_header_row(ws, 3, headers)
    autosize(ws, {1: 10, 2: 30, 3: 12, 4: 12, 5: 30, 6: 15})


def create_kpis_tab(ws) -> None:
    style_title_row(ws, 1, 5, "KPIs for Improvement Tracking")
    headers = ["KPI", "Baseline", "Target", "Current", "Status"]
    style_header_row(ws, 3, headers)
    row = 4
    for kpi_name in ["Processes at CL2+", "Processes at CL3+", "Training Hours", "Defect Rate", "Lead Time"]:
        ws.cell(row, 1, kpi_name)
        ws.cell(row, 2, "")
        ws.cell(row, 3, "")
        ws.cell(row, 4, "")
        ws.cell(row, 5, "")
        row += 1
    stripe_body(ws, 4, row - 1, 5)
    autosize(ws, {1: 20, 2: 12, 3: 12, 4: 12, 5: 12})


def create_communication_tab(ws) -> None:
    style_title_row(ws, 1, 5, "Stakeholder Communication Plan")
    headers = ["Audience", "Message", "Channel", "Frequency", "Owner"]
    style_header_row(ws, 3, headers)
    autosize(ws, {1: 20, 2: 30, 3: 20, 4: 15, 5: 15})


def create_pilot_tab(ws) -> None:
    style_title_row(ws, 1, 4, "Pilot Project Plan")
    headers = ["Pilot Aspect", "Scope", "Success Criteria", "Learnings to Scale"]
    style_header_row(ws, 3, headers)
    autosize(ws, {1: 20, 2: 25, 3: 30, 4: 30})


def create_references_tab(ws) -> None:
    style_title_row(ws, 1, 2, "References")
    row = 3
    ws.cell(row, 1, "ASPICE PAM/PRM").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row, 2, "Process Assessment and Reference Models")
    row += 1
    ws.cell(row, 1, "ISO/IEC 33004").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row, 2, "Process assessment guidelines")
    autosize(ws, {1: 20, 2: 60})


# ============================================================================
# Main
# ============================================================================

def generate_improvement_plan(input_json: str, output_xlsx: str) -> None:
    with open(input_json) as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    tabs = [
        ("00_Title_Page", lambda ws: create_title_page(ws, data.get("config", {}))),
        ("01_Document_Control", lambda ws: create_document_control(ws)),
        ("02_Gaps_From_Analysis", lambda ws: create_gaps_echo_tab(ws, data.get("processes", []))),
        ("03_Initiatives", lambda ws: create_initiatives_tab(ws, data.get("initiatives", []))),
        ("04_Roadmap", lambda ws: create_roadmap_tab(ws)),
        ("05_Resources_Budget", lambda ws: create_resources_tab(ws)),
        ("06_Risk_Register", lambda ws: create_risks_tab(ws)),
        ("07_KPIs", lambda ws: create_kpis_tab(ws)),
        ("08_Communication", lambda ws: create_communication_tab(ws)),
        ("09_Pilot_Plan", lambda ws: create_pilot_tab(ws)),
        ("10_References", lambda ws: create_references_tab(ws)),
    ]

    for tab_name, creator in tabs:
        ws = wb.create_sheet(tab_name)
        creator(ws)

    wb.save(output_xlsx)
    print(json.dumps({"status": "ok", "tabs": len(tabs), "initiatives": len(data.get("initiatives", []))}))


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 3:
        # Legacy form: <gap_analysis.xlsx> <input.json> <output.xlsx>. The gap-analysis
        # workbook has never been read by this generator; gap rows come from the JSON
        # `processes` field. Accepted, ignored, and warned about.
        print(
            "WARNING: the leading gap-analysis workbook argument is ignored; "
            "gap rows are read from <input.json> (processes). "
            "Use the 2-argument form: <input.json> <output.xlsx>",
            file=sys.stderr,
        )
        args = args[1:]
    if len(args) != 2:
        print(
            "Usage: python generate_aspice_improvement_plan.py <input.json> <output.xlsx>",
            file=sys.stderr,
        )
        sys.exit(1)
    generate_improvement_plan(args[0], args[1])
