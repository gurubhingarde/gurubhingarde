"""
Control Plan Builder - generates an AIAG Production Control Plan xlsx from JSON input.

Usage:
    python generate_control_plan.py <input.json> <output.xlsx>

Produces 13 tabs:
  00_Title_Page, 01_Document_Control, 02_Header_Block, 03_Process_Reference,
  04_Control_Plan_Worksheet, 05_Special_Characteristics_Echo, 06_Measurement_System_Plan,
  07_Reaction_Plan_Library, 08_SPC_Method_Allocation, 09_Mistake_Proofing_Catalog,
  10_Audit_Plan, 11_Linkage_to_PFMEA, 12_References
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# ============================================================================
# Styling
# ============================================================================

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
LIGHT_GRAY = "F2F2F2"
WHITE = "FFFFFF"
RED = "FF0000"
ORANGE = "FFC000"
LIGHT_YELLOW = "FFFFCC"
GREEN = "C6EFCE"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color=WHITE)


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def title_font() -> Font:
    return Font(name=FONT_NAME, size=14, bold=True, color=WHITE)


def style_title_row(ws, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = title_font()
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
    ws.row_dimensions[row].height = 35


def style_data_row(ws, row: int, col: int, value: Any, special_class: str = None) -> None:
    cell = ws.cell(row=row, column=col, value=value)
    cell.font = body_font()
    cell.border = BORDER_ALL
    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # Color special characteristics by class
    if special_class == "Critical":
        cell.fill = PatternFill("solid", fgColor=RED)
        cell.font = Font(name=FONT_NAME, size=10, color=WHITE, bold=True)
    elif special_class == "Significant":
        cell.fill = PatternFill("solid", fgColor=ORANGE)
        cell.font = Font(name=FONT_NAME, size=10, color=WHITE)
    elif special_class == "Standard":
        cell.fill = PatternFill("solid", fgColor=LIGHT_YELLOW)


# ============================================================================
# Tab Builders
# ============================================================================

def build_title_page(ws, program: dict) -> None:
    """Title page with program info, approval lines, document ID, revision."""
    style_title_row(ws, 1, 6, "PRODUCTION CONTROL PLAN")

    row = 3
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    cell = ws.cell(row=row, column=1, value=f"Program: {program.get('name', '')}")
    cell.font = Font(name=FONT_NAME, size=12, bold=True)

    row = 5
    labels_values = [
        ("Part Name:", program.get("part_name", "")),
        ("Part Number:", program.get("part_number", "")),
        ("Control Plan Type:", program.get("control_plan_type", "Production")),
        ("Supplier:", program.get("supplier", "")),
        ("Customer:", program.get("customer", "")),
        ("Doc ID:", program.get("doc_id", "")),
        ("Revision:", program.get("revision", "A")),
        ("Date:", program.get("date", datetime.now().strftime("%Y-%m-%d"))),
    ]

    for label, value in labels_values:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        c1 = ws.cell(row=row, column=1, value=label)
        c1.font = Font(name=FONT_NAME, size=10, bold=True)

        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=6)
        c2 = ws.cell(row=row, column=3, value=value)
        c2.font = body_font()

        row += 1

    row += 2
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    cell = ws.cell(row=row, column=1, value="APPROVALS")
    cell.font = Font(name=FONT_NAME, size=11, bold=True)
    cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    row += 2
    approvals = [
        "Supplier Plant Manager",
        "Supplier Quality Manager",
        "Customer Engineering Approval",
        "Customer Quality Approval"
    ]
    for approval in approvals:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        c1 = ws.cell(row=row, column=1, value=approval)
        c1.font = body_font()

        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=4)
        c2 = ws.cell(row=row, column=3, value="")
        c2.border = Border(bottom=THIN)

        ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=6)
        c3 = ws.cell(row=row, column=5, value="Date:")
        c3.font = body_font()
        c3.alignment = Alignment(horizontal="right")

        row += 1

    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 15


def build_document_control(ws, program: dict, revision: str = "A") -> None:
    """Revision history and distribution."""
    style_title_row(ws, 1, 8, "DOCUMENT CONTROL")

    # Revision history
    row = 3
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
    cell = ws.cell(row=row, column=1, value="Revision History")
    cell.font = Font(name=FONT_NAME, size=11, bold=True)
    cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    row += 1
    headers = ["Revision", "Date", "Author", "Description", "Approval", "Date", "Notes", "Status"]
    style_header_row(ws, row, headers)

    row += 1
    rev_data = [revision, datetime.now().strftime("%Y-%m-%d"), "Control Plan Team",
                "Initial release", "", "", "", "Released"]
    for col, val in enumerate(rev_data, start=1):
        style_data_row(ws, row, col, val)

    for i in range(1, 9):
        ws.column_dimensions[get_column_letter(i)].width = 15


def build_header_block(ws, program: dict, core_team: list = None) -> None:
    """AIAG standard control plan header block."""
    style_title_row(ws, 1, 8, "HEADER INFORMATION")

    row = 3
    headers_info = [
        ("Control Plan Number:", program.get("doc_id", "")),
        ("Part Number:", program.get("part_number", "")),
        ("Part Name:", program.get("part_name", "")),
        ("Control Plan Type:", program.get("control_plan_type", "Production")),
        ("Date Original:", program.get("date", "")),
        ("Date Revised:", datetime.now().strftime("%Y-%m-%d")),
    ]

    for label, value in headers_info:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        c1 = ws.cell(row=row, column=1, value=label)
        c1.font = Font(name=FONT_NAME, size=10, bold=True)
        c1.fill = PatternFill("solid", fgColor=LIGHT_BLUE)

        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=6)
        c2 = ws.cell(row=row, column=3, value=value)
        c2.font = body_font()
        c2.border = BORDER_ALL

        row += 1

    row += 1
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    cell = ws.cell(row=row, column=1, value="CORE TEAM")
    cell.font = Font(name=FONT_NAME, size=11, bold=True)
    cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    row += 1
    team_headers = ["Role", "Name", "Organization", "Phone", "Email", "Signature"]
    style_header_row(ws, row, team_headers)

    for i, header in enumerate(team_headers, start=1):
        ws.column_dimensions[get_column_letter(i)].width = 18


def build_process_reference(ws, program: dict, process_steps: list = None) -> None:
    """Reference to upstream PFMEA, process flow, special characteristics."""
    style_title_row(ws, 1, 6, "PROCESS REFERENCE")

    row = 3
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    cell = ws.cell(row=row, column=1, value="Upstream Documents & References")
    cell.font = Font(name=FONT_NAME, size=11, bold=True)
    cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    row += 1
    ref_headers = ["Document Type", "Document ID", "Revision", "Status", "Notes", "Link"]
    style_header_row(ws, row, ref_headers)

    row += 1
    refs = [
        ["PFMEA", f"{program.get('part_number', '')}_PFMEA", "A", "Current", "Production FMEA", ""],
        ["Process Flow Diagram", f"{program.get('part_number', '')}_PFD", "A", "Current", "Manufacturing sequence", ""],
        ["Special Characteristics List", f"{program.get('part_number', '')}_SC", "A", "Current", "From PFMEA/drawing", ""],
    ]

    for ref in refs:
        for col, val in enumerate(ref, start=1):
            style_data_row(ws, row, col, val)
        row += 1

    for i in range(1, 7):
        ws.column_dimensions[get_column_letter(i)].width = 18


def build_control_plan_worksheet(ws, characteristics: list, gages: dict, reaction_plans: dict) -> None:
    """Main control plan worksheet per AIAG standard layout."""
    style_title_row(ws, 1, 15, "CONTROL PLAN WORKSHEET")

    row = 2
    headers = [
        "Part/Process #",
        "Process Name/Operation",
        "Machine/Device/Jig",
        "Char # (Drawing/Spec)",
        "Product/Process",
        "Spec/Tolerance",
        "Gage/Instrument",
        "Sample Size",
        "Sample Frequency",
        "Control Method",
        "Special Class",
        "Reaction Plan ID",
        "Reaction Plan Steps",
        "Owner",
        "Status"
    ]
    style_header_row(ws, row, headers)

    row = 3
    for char in characteristics:
        part_num = char.get("part_number", "")
        style_data_row(ws, row, 1, part_num)
        style_data_row(ws, row, 2, char.get("operation", ""))
        style_data_row(ws, row, 3, char.get("equipment", ""))
        style_data_row(ws, row, 4, char.get("char_number", ""))
        style_data_row(ws, row, 5, char.get("type", ""))
        style_data_row(ws, row, 6, char.get("specification", ""))
        style_data_row(ws, row, 7, char.get("gage_name", ""))
        style_data_row(ws, row, 8, char.get("sample_size", ""))
        style_data_row(ws, row, 9, char.get("sample_frequency", ""))
        style_data_row(ws, row, 10, char.get("control_method", ""))

        spec_class = char.get("special_class", "Standard")
        style_data_row(ws, row, 11, spec_class, special_class=spec_class)

        rp_id = char.get("reaction_plan_id", "")
        style_data_row(ws, row, 12, rp_id)

        rp_steps = reaction_plans.get(rp_id, {}).get("steps", "") if rp_id in reaction_plans else ""
        style_data_row(ws, row, 13, rp_steps)
        style_data_row(ws, row, 14, reaction_plans.get(rp_id, {}).get("owner", "") if rp_id in reaction_plans else "")
        style_data_row(ws, row, 15, "Active")

        row += 1

    for i in range(1, 16):
        ws.column_dimensions[get_column_letter(i)].width = 14


def build_special_characteristics_echo(ws, characteristics: list) -> None:
    """Read-only echo of special characteristics (Critical/Significant)."""
    style_title_row(ws, 1, 8, "SPECIAL CHARACTERISTICS")

    row = 2
    headers = ["Char #", "Name", "Type", "Spec/Tolerance", "Class", "OEM Convention", "PFMEA Link", "Priority"]
    style_header_row(ws, row, headers)

    row = 3
    for char in characteristics:
        spec_class = char.get("special_class", "Standard")
        if spec_class != "Standard":
            style_data_row(ws, row, 1, char.get("char_number", ""), special_class=spec_class)
            style_data_row(ws, row, 2, char.get("operation", ""), special_class=spec_class)
            style_data_row(ws, row, 3, char.get("type", ""), special_class=spec_class)
            style_data_row(ws, row, 4, char.get("specification", ""), special_class=spec_class)
            style_data_row(ws, row, 5, spec_class, special_class=spec_class)
            style_data_row(ws, row, 6, "Critical" if spec_class == "Critical" else "Significant", special_class=spec_class)
            style_data_row(ws, row, 7, char.get("pfmea_ref", ""), special_class=spec_class)
            style_data_row(ws, row, 8, "High" if spec_class == "Critical" else "Medium", special_class=spec_class)

            row += 1

    for i in range(1, 9):
        ws.column_dimensions[get_column_letter(i)].width = 16


def build_measurement_system_plan(ws, gages: list) -> None:
    """MSA plan per gage: type, R&R method, status."""
    style_title_row(ws, 1, 8, "MEASUREMENT SYSTEM ANALYSIS PLAN")

    row = 2
    headers = ["Gage ID", "Gage Name", "Type (V/A)", "R&R Method", "Target R&R %", "Planned Date", "Status", "Results"]
    style_header_row(ws, row, headers)

    row = 3
    for gage in gages:
        style_data_row(ws, row, 1, gage.get("id", ""))
        style_data_row(ws, row, 2, gage.get("name", ""))
        style_data_row(ws, row, 3, gage.get("type", "Variable"))
        style_data_row(ws, row, 4, gage.get("rr_method", "Gage R&R"))
        style_data_row(ws, row, 5, f"{gage.get('rr_target_pct', 30)}%")
        style_data_row(ws, row, 6, "")
        style_data_row(ws, row, 7, "Planned")
        style_data_row(ws, row, 8, "")

        row += 1

    for i in range(1, 9):
        ws.column_dimensions[get_column_letter(i)].width = 15


def build_reaction_plan_library(ws, reaction_plans: dict) -> None:
    """Standard reaction plans with detailed steps."""
    style_title_row(ws, 1, 6, "REACTION PLAN LIBRARY")

    row = 2
    headers = ["Plan ID", "Title", "Trigger", "Steps", "Owner", "Timeline"]
    style_header_row(ws, row, headers)

    row = 3
    for plan_id, plan in reaction_plans.items():
        style_data_row(ws, row, 1, plan_id)
        style_data_row(ws, row, 2, plan.get("title", ""))
        style_data_row(ws, row, 3, "Out of Control")
        style_data_row(ws, row, 4, plan.get("steps", ""))
        style_data_row(ws, row, 5, plan.get("owner", ""))
        style_data_row(ws, row, 6, plan.get("escalation", "Immediate"))

        row += 1

    for i in range(1, 7):
        ws.column_dimensions[get_column_letter(i)].width = 18


def build_spc_method_allocation(ws, spc_settings: list) -> None:
    """SPC chart types: Xbar-R, Xbar-S, p-chart, etc."""
    style_title_row(ws, 1, 8, "SPC METHOD ALLOCATION")

    row = 2
    headers = ["Characteristic", "Chart Type", "Subgroup Size", "Sampling Frequency", "Control Limit Source", "OOC Rules", "Reaction Plan", "Status"]
    style_header_row(ws, row, headers)

    row = 3
    for spc in spc_settings:
        style_data_row(ws, row, 1, spc.get("characteristic_id", ""))
        style_data_row(ws, row, 2, spc.get("chart_type", "Xbar-R"))
        style_data_row(ws, row, 3, spc.get("subgroup_size", 5))
        style_data_row(ws, row, 4, spc.get("sampling_frequency", "Every 20 parts"))
        style_data_row(ws, row, 5, "Calculated from initial production")
        style_data_row(ws, row, 6, spc.get("ooc_rules", "Nelson/Western Electric"))
        style_data_row(ws, row, 7, spc.get("reaction_plan_id", ""))
        style_data_row(ws, row, 8, "Active")

        row += 1

    for i in range(1, 9):
        ws.column_dimensions[get_column_letter(i)].width = 16


def build_mistake_proofing_catalog(ws, mistake_proofs: list) -> None:
    """Poka-yoke devices and verification."""
    style_title_row(ws, 1, 8, "MISTAKE-PROOFING (POKA-YOKE) CATALOG")

    row = 2
    headers = ["Device ID", "Characteristic Protected", "Type (Warning/Prevention)", "Test Method", "Audit Frequency", "Last Verified", "Status", "Owner"]
    style_header_row(ws, row, headers)

    row = 3
    for device in mistake_proofs:
        style_data_row(ws, row, 1, device.get("id", ""))
        style_data_row(ws, row, 2, device.get("characteristic", ""))
        style_data_row(ws, row, 3, device.get("type", "Prevention"))
        style_data_row(ws, row, 4, device.get("test_method", ""))
        style_data_row(ws, row, 5, device.get("audit_frequency", "Monthly"))
        style_data_row(ws, row, 6, "")
        style_data_row(ws, row, 7, "Active")
        style_data_row(ws, row, 8, device.get("owner", ""))

        row += 1

    for i in range(1, 9):
        ws.column_dimensions[get_column_letter(i)].width = 16


def build_audit_plan(ws, characteristics: list) -> None:
    """Layered process audit (LPA) hooks per characteristic."""
    style_title_row(ws, 1, 7, "AUDIT PLAN")

    row = 2
    headers = ["Characteristic", "Audit Frequency", "Audit Type", "Auditor Role", "Escalation Level", "Documentation", "Status"]
    style_header_row(ws, row, headers)

    row = 3
    for char in characteristics:
        if char.get("special_class") == "Critical":
            freq = "Weekly"
        elif char.get("special_class") == "Significant":
            freq = "Bi-weekly"
        else:
            freq = "Monthly"

        style_data_row(ws, row, 1, char.get("char_number", ""))
        style_data_row(ws, row, 2, freq)
        style_data_row(ws, row, 3, "Process Observation")
        style_data_row(ws, row, 4, "Quality Inspector")
        style_data_row(ws, row, 5, "Supervisor" if char.get("special_class") == "Critical" else "Lead")
        style_data_row(ws, row, 6, "Audit report")
        style_data_row(ws, row, 7, "Active")

        row += 1

    for i in range(1, 8):
        ws.column_dimensions[get_column_letter(i)].width = 16


def build_linkage_to_pfmea(ws, characteristics: list) -> None:
    """Cross-reference: Control Plan row → PFMEA failure mode."""
    style_title_row(ws, 1, 7, "LINKAGE TO PFMEA")

    row = 2
    headers = ["Control Plan Char #", "PFMEA Failure Mode", "Severity", "Occurrence", "Detection", "RPN", "Preventive Action", "Status"]
    style_header_row(ws, row, headers)

    row = 3
    for char in characteristics:
        style_data_row(ws, row, 1, char.get("char_number", ""))
        style_data_row(ws, row, 2, char.get("pfmea_failure_mode", ""))
        style_data_row(ws, row, 3, char.get("severity", ""))
        style_data_row(ws, row, 4, char.get("occurrence", ""))
        style_data_row(ws, row, 5, char.get("detection", ""))
        style_data_row(ws, row, 6, char.get("rpn", ""))
        style_data_row(ws, row, 7, char.get("preventive_action", ""))
        style_data_row(ws, row, 8, "Linked")

        row += 1

    for i in range(1, 8):
        ws.column_dimensions[get_column_letter(i)].width = 16


def build_references(ws, program: dict) -> None:
    """Control Plan references and standards."""
    style_title_row(ws, 1, 4, "REFERENCES & STANDARDS")

    row = 3
    refs = [
        ("AIAG Production Control Plan", "Handbook for multi-tier suppliers"),
        ("IATF 16949:2016", "Automotive quality management requirement"),
        ("PFMEA", f"{program.get('part_number', '')}_PFMEA"),
        ("Drawing & Specification", program.get("part_number", "")),
        ("ISO 13053-1", "Control charts — Guidance for construction, interpretation, and application"),
        ("ISO 7870-2", "SPC Xbar-R, Xbar-S, p-chart procedures"),
    ]

    for title, desc in refs:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        c1 = ws.cell(row=row, column=1, value=title)
        c1.font = Font(name=FONT_NAME, size=10, bold=True)

        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=4)
        c2 = ws.cell(row=row, column=3, value=desc)
        c2.font = body_font()

        row += 1

    for i in range(1, 5):
        ws.column_dimensions[get_column_letter(i)].width = 25


# ============================================================================
# Main Generator
# ============================================================================

def generate_control_plan(input_json: str, output_xlsx: str) -> dict:
    """Generate Control Plan xlsx from JSON input."""

    with open(input_json) as f:
        data = json.load(f)

    program = data.get("program", {})
    process_steps = data.get("process_steps", [])
    characteristics = data.get("characteristics", [])
    gages = data.get("gages", [])
    reaction_plans = {rp["id"]: rp for rp in data.get("reaction_plans", [])}
    spc_settings = data.get("spc_settings", [])
    mistake_proofs = data.get("mistake_proofing", [])

    # Build characteristic objects with enrichment
    enriched_chars = []
    for char in characteristics:
        enriched = dict(char)
        step = next((s for s in process_steps if s.get("step_id") == char.get("step_id")), {})
        enriched["operation"] = step.get("operation", "")
        enriched["equipment"] = step.get("equipment", "")
        enriched["part_number"] = program.get("part_number", "")

        gage = next((g for g in gages if g.get("id") == char.get("gage_id")), {})
        enriched["gage_name"] = gage.get("name", "")

        enriched_chars.append(enriched)

    # Create workbook with 13 tabs
    wb = Workbook()
    wb.remove(wb.active)

    tabs = [
        ("00_Title_Page", lambda ws: build_title_page(ws, program)),
        ("01_Document_Control", lambda ws: build_document_control(ws, program, program.get("revision", "A"))),
        ("02_Header_Block", lambda ws: build_header_block(ws, program, program.get("core_team", []))),
        ("03_Process_Reference", lambda ws: build_process_reference(ws, program, process_steps)),
        ("04_Control_Plan_Worksheet", lambda ws: build_control_plan_worksheet(ws, enriched_chars, {g["id"]: g for g in gages}, reaction_plans)),
        ("05_Special_Characteristics_Echo", lambda ws: build_special_characteristics_echo(ws, enriched_chars)),
        ("06_Measurement_System_Plan", lambda ws: build_measurement_system_plan(ws, gages)),
        ("07_Reaction_Plan_Library", lambda ws: build_reaction_plan_library(ws, reaction_plans)),
        ("08_SPC_Method_Allocation", lambda ws: build_spc_method_allocation(ws, spc_settings)),
        ("09_Mistake_Proofing_Catalog", lambda ws: build_mistake_proofing_catalog(ws, mistake_proofs)),
        ("10_Audit_Plan", lambda ws: build_audit_plan(ws, enriched_chars)),
        ("11_Linkage_to_PFMEA", lambda ws: build_linkage_to_pfmea(ws, enriched_chars)),
        ("12_References", lambda ws: build_references(ws, program)),
    ]

    for tab_name, builder in tabs:
        ws = wb.create_sheet(tab_name)
        builder(ws)

    wb.save(output_xlsx)

    # Count statistics
    critical_count = sum(1 for c in enriched_chars if c.get("special_class") == "Critical")
    significant_count = sum(1 for c in enriched_chars if c.get("special_class") == "Significant")
    standard_count = sum(1 for c in enriched_chars if c.get("special_class") == "Standard")

    return {
        "tabs": len(tabs),
        "characteristics": len(enriched_chars),
        "special_characteristics": {
            "critical": critical_count,
            "significant": significant_count,
            "standard": standard_count
        },
        "output": output_xlsx
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_control_plan.py <input.json> <output.xlsx>")
        sys.exit(1)

    result = generate_control_plan(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))
