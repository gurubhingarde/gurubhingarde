"""
ASPICE Process Evidence Builder - generates evidence inventory for process assessment.

Usage:
    python generate_aspice_evidence.py <input.json> <output.xlsx>
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

def create_title_page(ws, process_info: dict[str, Any]) -> None:
    ws.merge_cells("A1:C1")
    ws.cell(1, 1, "Process Evidence Package").font = title_font(20)
    ws.cell(1, 1).fill = PatternFill("solid", fgColor=NAVY)
    ws.cell(1, 1).alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    row = 4
    for k, v in [
        ("Process ID", process_info.get("process_id", "")),
        ("Process Name", process_info.get("process_name", "")),
        ("Process Owner", process_info.get("owner", "")),
        ("Evidence Collection Period", process_info.get("period", "")),
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
    ws.cell(4, 3, "Process Owner")
    ws.cell(4, 4, "Initial")
    ws.cell(4, 5, "Draft")
    stripe_body(ws, 4, 4, 5)
    autosize(ws, {1: 12, 2: 12, 3: 20, 4: 20, 5: 12})


def create_description_tab(ws, process_info: dict[str, Any]) -> None:
    style_title_row(ws, 1, 2, "Process Description")

    row = 3
    for k, v in [
        ("Process Purpose", process_info.get("purpose", "")),
        ("Scope", process_info.get("scope", "")),
        ("Inputs", process_info.get("inputs", "")),
        ("Outputs", process_info.get("outputs", "")),
        ("Owner", process_info.get("owner", "")),
        ("Supporting Roles", process_info.get("roles", "")),
    ]:
        ws.cell(row, 1, k).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row, 2, v).alignment = Alignment(wrap_text=True)
        row += 1

    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 60


def create_bp_evidence_tab(ws, practices: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 5, "Base Practice (BP) Evidence Inventory")
    headers = ["BP ID", "BP Text", "Evidence Type", "Reference/Location", "Accessible"]
    style_header_row(ws, 3, headers)

    row = 4
    for bp in practices:
        ws.cell(row, 1, bp.get("bp_id", ""))
        ws.cell(row, 2, bp.get("text", "")).alignment = Alignment(wrap_text=True)
        ws.cell(row, 3, bp.get("evidence_type", ""))
        ws.cell(row, 4, bp.get("reference", "")).alignment = Alignment(wrap_text=True)
        ws.cell(row, 5, bp.get("accessible", "Y"))
        row += 1

    stripe_body(ws, 4, row - 1, 5)
    autosize(ws, {1: 10, 2: 25, 3: 18, 4: 30, 5: 12})


def create_gp_evidence_tab(ws, practices: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 6, "Generic Practice (GP) Evidence Inventory")
    headers = ["GP ID", "CL", "GP Text", "Evidence Type", "Reference/Location", "Accessible"]
    style_header_row(ws, 3, headers)

    row = 4
    for gp in practices:
        ws.cell(row, 1, gp.get("gp_id", ""))
        ws.cell(row, 2, gp.get("cl", ""))
        ws.cell(row, 3, gp.get("text", "")).alignment = Alignment(wrap_text=True)
        ws.cell(row, 4, gp.get("evidence_type", ""))
        ws.cell(row, 5, gp.get("reference", "")).alignment = Alignment(wrap_text=True)
        ws.cell(row, 6, gp.get("accessible", "Y"))
        row += 1

    stripe_body(ws, 4, row - 1, 6)
    autosize(ws, {1: 10, 2: 6, 3: 25, 4: 18, 5: 30, 6: 12})


def create_work_products_tab(ws, products: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 5, "Work Product References")
    headers = ["WP ID", "Type", "Location/Repository", "Version Control", "Owner"]
    style_header_row(ws, 3, headers)

    row = 4
    for prod in products:
        ws.cell(row, 1, prod.get("id", ""))
        ws.cell(row, 2, prod.get("type", ""))
        ws.cell(row, 3, prod.get("location", "")).alignment = Alignment(wrap_text=True)
        ws.cell(row, 4, prod.get("vc", ""))
        ws.cell(row, 5, prod.get("owner", ""))
        row += 1

    stripe_body(ws, 4, max(4, row - 1), 5)
    autosize(ws, {1: 10, 2: 15, 3: 30, 4: 20, 5: 15})


DEFAULT_METRIC_TEMPLATE = ["Cycle Time", "Defect Rate", "Completeness", "Compliance"]


def create_performance_tab(ws, records: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 5, "Process Performance Records")
    headers = ["Record ID", "Type", "Date", "Metrics/Findings", "Location"]
    style_header_row(ws, 3, headers)

    row = 4
    for rec in records:
        ws.cell(row, 1, rec.get("id", ""))
        ws.cell(row, 2, rec.get("type", ""))
        ws.cell(row, 3, rec.get("date", ""))
        ws.cell(row, 4, rec.get("findings", "")).alignment = Alignment(wrap_text=True)
        ws.cell(row, 5, rec.get("location", "")).alignment = Alignment(wrap_text=True)
        row += 1

    stripe_body(ws, 4, max(4, row - 1), 5)
    autosize(ws, {1: 12, 2: 18, 3: 12, 4: 30, 5: 25})


def create_quantitative_tab(ws, metrics: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 5, "Quantitative Process Performance (CL3+)")
    headers = ["Metric", "Period", "Value", "Target", "Status"]
    style_header_row(ws, 3, headers)

    row = 4
    if metrics:
        for m in metrics:
            ws.cell(row, 1, m.get("metric", ""))
            ws.cell(row, 2, m.get("period", ""))
            ws.cell(row, 3, m.get("value", ""))
            ws.cell(row, 4, m.get("target", ""))
            ws.cell(row, 5, m.get("status", ""))
            row += 1
    else:
        # No quantitative_metrics supplied: emit the CL3+ metric names as a
        # blank template for the assessor to fill in by hand.
        for metric in DEFAULT_METRIC_TEMPLATE:
            ws.cell(row, 1, metric)
            row += 1

    stripe_body(ws, 4, row - 1, 5)
    autosize(ws, {1: 20, 2: 15, 3: 12, 4: 12, 5: 12})


def create_improvement_tab(ws, improvements: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 4, "Process Improvement Log")
    headers = ["Improvement ID", "Description", "Implementation Date", "Impact"]
    style_header_row(ws, 3, headers)

    row = 4
    for imp in improvements:
        ws.cell(row, 1, imp.get("id", ""))
        ws.cell(row, 2, imp.get("description", "")).alignment = Alignment(wrap_text=True)
        ws.cell(row, 3, imp.get("date", ""))
        ws.cell(row, 4, imp.get("impact", "")).alignment = Alignment(wrap_text=True)
        row += 1

    stripe_body(ws, 4, max(4, row - 1), 4)
    autosize(ws, {1: 12, 2: 30, 3: 18, 4: 25})


def create_references_tab(ws) -> None:
    style_title_row(ws, 1, 2, "References")
    row = 3
    ws.cell(row, 1, "ASPICE PAM/PRM").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row, 2, "Process Assessment and Reference Models")
    autosize(ws, {1: 20, 2: 60})


# ============================================================================
# Main
# ============================================================================

def generate_evidence(input_json: str, output_xlsx: str) -> None:
    with open(input_json) as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    process_info = data.get("process", {})
    bp_list = data.get("base_practices", [])
    gp_list = data.get("generic_practices", [])
    wp_list = data.get("work_products", [])
    perf_list = data.get("performance_records", [])
    metric_list = data.get("quantitative_metrics", [])
    imp_list = data.get("improvements", [])

    tabs = [
        ("00_Title_Page", lambda ws: create_title_page(ws, process_info)),
        ("01_Document_Control", lambda ws: create_document_control(ws)),
        ("02_Process_Description", lambda ws: create_description_tab(ws, process_info)),
        ("03_BP_Evidence", lambda ws: create_bp_evidence_tab(ws, bp_list)),
        ("04_GP_Evidence", lambda ws: create_gp_evidence_tab(ws, gp_list)),
        ("05_Work_Products", lambda ws: create_work_products_tab(ws, wp_list)),
        ("06_Performance_Records", lambda ws: create_performance_tab(ws, perf_list)),
        ("07_Quantitative_Performance", lambda ws: create_quantitative_tab(ws, metric_list)),
        ("08_Improvement_Log", lambda ws: create_improvement_tab(ws, imp_list)),
        ("09_References", lambda ws: create_references_tab(ws)),
    ]

    for tab_name, creator in tabs:
        ws = wb.create_sheet(tab_name)
        creator(ws)

    wb.save(output_xlsx)
    print(json.dumps({
        "status": "ok",
        "tabs": len(tabs),
        "process": process_info.get("process_id", ""),
        "bp_count": len(bp_list),
        "gp_count": len(gp_list),
        "wp_count": len(wp_list),
        "performance_record_count": len(perf_list),
        "quantitative_metric_count": len(metric_list),
        "improvement_count": len(imp_list),
    }))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_aspice_evidence.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(1)
    generate_evidence(sys.argv[1], sys.argv[2])
