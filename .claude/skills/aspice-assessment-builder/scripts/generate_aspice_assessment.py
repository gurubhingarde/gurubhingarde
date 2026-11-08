"""
ASPICE Assessment Builder - generates a multi-tab ASPICE PAM v3.1/v4.0 process assessment workbook.

Usage:
    python scripts/generate_aspice_assessment.py <input.json> <output.xlsx>

Input JSON schema:
{
  "project": {name, doc_id, revision, date, assessor_name, lead_assessor_name, customer, sponsor, aspice_version},
  "scope": {process_areas: [SYS.1, SYS.2, ..., SWE.1, ..., SUP.1, ...], scope_description},
  "processes": [
    {
      "process_id": "SYS.1",
      "process_name": "System Concept",
      "purpose": "...",
      "outcomes": ["...", "..."],
      "base_practices": [
        {bp_id: "BP1", text: "...", evidence: "...", rating: "N|P|L|F"}
      ],
      "generic_practices": [
        {gp_id: "GP1", cl: 2, text: "...", evidence: "...", rating: "N|P|L|F"}
      ]
    }
  ]
}
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
from openpyxl.worksheet.table import Table, TableStyleInfo


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
# Tab 00: Title Page
# ============================================================================

def create_title_page(ws, proj: dict[str, Any]) -> None:
    ws.merge_cells("A1:C1")
    ws.cell(1, 1, "ASPICE Process Assessment").font = title_font(20)
    ws.cell(1, 1).fill = PatternFill("solid", fgColor=NAVY)
    ws.cell(1, 1).alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    row = 4
    for k, v in [
        ("Project", proj.get("name", "")),
        ("Document ID", proj.get("doc_id", "")),
        ("Revision", proj.get("revision", "")),
        ("Assessment Date", proj.get("date", "")),
        ("Assessor", proj.get("assessor_name", "")),
        ("Lead Assessor", proj.get("lead_assessor_name", "")),
        ("Customer/Sponsor", proj.get("customer", "")),
        ("ASPICE Version", proj.get("aspice_version", "v3.1")),
    ]:
        ws.cell(row, 1, k).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row, 2, v)
        row += 1

    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40


# ============================================================================
# Tab 01: Document Control
# ============================================================================

def create_document_control(ws, proj: dict[str, Any]) -> None:
    style_title_row(ws, 1, 5, "Document Control")

    headers = ["Revision", "Date", "Author", "Change Description", "Status"]
    style_header_row(ws, 3, headers)

    ws.cell(4, 1, "1.0")
    ws.cell(4, 2, proj.get("date", datetime.now().strftime("%Y-%m-%d")))
    ws.cell(4, 3, proj.get("assessor_name", ""))
    ws.cell(4, 4, "Initial Assessment")
    ws.cell(4, 5, "Draft")

    stripe_body(ws, 4, 4, 5)
    autosize(ws, {1: 12, 2: 12, 3: 20, 4: 30, 5: 12})


# ============================================================================
# Tab 02: Assessment Scope
# ============================================================================

def create_scope_tab(ws, scope: dict[str, Any]) -> None:
    style_title_row(ws, 1, 3, "Assessment Scope")

    ws.cell(3, 1, "Process Areas in Scope:").font = Font(name=FONT_NAME, bold=True)

    row = 4
    for pa in scope.get("process_areas", []):
        ws.cell(row, 1, pa)
        row += 1

    ws.cell(row + 2, 1, "Scope Description:").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row + 3, 1, scope.get("scope_description", "")).alignment = Alignment(wrap_text=True)

    ws.column_dimensions["A"].width = 40


# ============================================================================
# Tab 03: Process Reference Model
# ============================================================================

def create_prm_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 5, "Process Reference Model (PRM)")

    headers = ["Process ID", "Process Name", "Purpose", "Outcomes", "Owner"]
    style_header_row(ws, 3, headers)

    row = 4
    for proc in processes:
        ws.cell(row, 1, proc.get("process_id", ""))
        ws.cell(row, 2, proc.get("process_name", ""))
        ws.cell(row, 3, proc.get("purpose", "")).alignment = Alignment(wrap_text=True)
        outcomes_text = "; ".join(proc.get("outcomes", []))
        ws.cell(row, 4, outcomes_text).alignment = Alignment(wrap_text=True)
        ws.cell(row, 5, proc.get("owner", ""))
        row += 1

    stripe_body(ws, 4, row - 1, 5)
    autosize(ws, {1: 12, 2: 20, 3: 30, 4: 35, 5: 15})


# ============================================================================
# Tab 04: Process Assessment Model (PAM)
# ============================================================================

def create_pam_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 6, "Process Assessment Model (PAM) - Base Practices & Generic Practices")

    headers = ["Process ID", "BP/GP ID", "Type", "Capability Level", "Text", "Owner"]
    style_header_row(ws, 3, headers)

    row = 4
    for proc in processes:
        proc_id = proc.get("process_id", "")

        for bp in proc.get("base_practices", []):
            ws.cell(row, 1, proc_id)
            ws.cell(row, 2, bp.get("bp_id", ""))
            ws.cell(row, 3, "BP")
            ws.cell(row, 4, "")
            ws.cell(row, 5, bp.get("text", "")).alignment = Alignment(wrap_text=True)
            ws.cell(row, 6, proc.get("owner", ""))
            row += 1

        for gp in proc.get("generic_practices", []):
            ws.cell(row, 1, proc_id)
            ws.cell(row, 2, gp.get("gp_id", ""))
            ws.cell(row, 3, f"GP (CL{gp.get('cl', '')})")
            ws.cell(row, 4, f"CL{gp.get('cl', '')}")
            ws.cell(row, 5, gp.get("text", "")).alignment = Alignment(wrap_text=True)
            ws.cell(row, 6, proc.get("owner", ""))
            row += 1

    stripe_body(ws, 4, row - 1, 6)
    autosize(ws, {1: 12, 2: 10, 3: 12, 4: 12, 5: 40, 6: 15})


# ============================================================================
# Tab 05: BP Assessment per Process
# ============================================================================

def create_bp_assessment_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 6, "Base Practice (BP) Assessment per Process")

    headers = ["Process ID", "BP ID", "BP Text", "Evidence", "Rating (N/P/L/F)", "Assessor Notes"]
    style_header_row(ws, 3, headers)

    row = 4
    for proc in processes:
        proc_id = proc.get("process_id", "")
        for bp in proc.get("base_practices", []):
            ws.cell(row, 1, proc_id)
            ws.cell(row, 2, bp.get("bp_id", ""))
            ws.cell(row, 3, bp.get("text", "")).alignment = Alignment(wrap_text=True)
            ws.cell(row, 4, bp.get("evidence", "")).alignment = Alignment(wrap_text=True)
            ws.cell(row, 5, bp.get("rating", ""))
            ws.cell(row, 6, "")
            row += 1

    stripe_body(ws, 4, row - 1, 6)
    autosize(ws, {1: 12, 2: 10, 3: 30, 4: 30, 5: 15, 6: 20})


# ============================================================================
# Tab 06: GP Assessment per Process
# ============================================================================

def create_gp_assessment_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 7, "Generic Practice (GP) Assessment per Process")

    headers = ["Process ID", "GP ID", "CL", "GP Text", "Evidence", "Rating (N/P/L/F)", "Assessor Notes"]
    style_header_row(ws, 3, headers)

    row = 4
    for proc in processes:
        proc_id = proc.get("process_id", "")
        for gp in proc.get("generic_practices", []):
            ws.cell(row, 1, proc_id)
            ws.cell(row, 2, gp.get("gp_id", ""))
            ws.cell(row, 3, f"CL{gp.get('cl', '')}")
            ws.cell(row, 4, gp.get("text", "")).alignment = Alignment(wrap_text=True)
            ws.cell(row, 5, gp.get("evidence", "")).alignment = Alignment(wrap_text=True)
            ws.cell(row, 6, gp.get("rating", ""))
            ws.cell(row, 7, "")
            row += 1

    stripe_body(ws, 4, row - 1, 7)
    autosize(ws, {1: 12, 2: 10, 3: 6, 4: 30, 5: 30, 6: 15, 7: 20})


# ============================================================================
# Tab 07: Process Attribute Rating
# ============================================================================

def create_pa_rating_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 5, "Process Attribute (PA) Rating")

    headers = ["Process ID", "PA ID", "PA Name", "Evidence Indicators", "PA Rating (N/P/L/F)"]
    style_header_row(ws, 3, headers)

    row = 4
    pa_mapping = [
        ("PA1.1", "Process Performance"),
        ("PA2.1", "Performance Management"),
        ("PA2.2", "Work Product Management"),
        ("PA3.1", "Process Definition"),
        ("PA3.2", "Process Deployment"),
        ("PA4.1", "Process Measurement"),
        ("PA4.2", "Process Control"),
        ("PA5.1", "Process Innovation"),
        ("PA5.2", "Process Optimization"),
    ]

    for proc in processes:
        proc_id = proc.get("process_id", "")
        for pa_id, pa_name in pa_mapping:
            ws.cell(row, 1, proc_id)
            ws.cell(row, 2, pa_id)
            ws.cell(row, 3, pa_name)
            ws.cell(row, 4, "")
            ws.cell(row, 5, "")
            row += 1

    stripe_body(ws, 4, row - 1, 5)
    autosize(ws, {1: 12, 2: 10, 3: 25, 4: 40, 5: 15})


# ============================================================================
# Tab 08: Capability Level per Process
# ============================================================================

def create_cl_rating_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 5, "Capability Level (CL) per Process")

    headers = ["Process ID", "Process Name", "Achieved CL (0-5)", "Target CL", "Gap Analysis"]
    style_header_row(ws, 3, headers)

    row = 4
    for proc in processes:
        ws.cell(row, 1, proc.get("process_id", ""))
        ws.cell(row, 2, proc.get("process_name", ""))
        ws.cell(row, 3, "")
        ws.cell(row, 4, "")
        ws.cell(row, 5, "")
        row += 1

    stripe_body(ws, 4, row - 1, 5)
    autosize(ws, {1: 12, 2: 25, 3: 15, 4: 12, 5: 30})


# ============================================================================
# Tab 09: Capability Profile
# ============================================================================

def create_capability_profile_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 3, "Capability Profile - Summary")

    ws.cell(3, 1, "Process ID").font = Font(name=FONT_NAME, bold=True)
    ws.cell(3, 2, "Achieved CL").font = Font(name=FONT_NAME, bold=True)
    ws.cell(3, 3, "Target CL").font = Font(name=FONT_NAME, bold=True)

    row = 4
    for proc in processes:
        ws.cell(row, 1, proc.get("process_id", ""))
        ws.cell(row, 2, "")
        ws.cell(row, 3, "")
        row += 1

    stripe_body(ws, 4, row - 1, 3)
    autosize(ws, {1: 15, 2: 15, 3: 15})


# ============================================================================
# Tab 10: Strengths & Weaknesses
# ============================================================================

def create_strengths_weaknesses_tab(ws, processes: list[dict[str, Any]]) -> None:
    style_title_row(ws, 1, 3, "Strengths & Weaknesses per Process")

    headers = ["Process ID", "Strengths Observed", "Weaknesses Observed"]
    style_header_row(ws, 3, headers)

    row = 4
    for proc in processes:
        ws.cell(row, 1, proc.get("process_id", ""))
        ws.cell(row, 2, "")
        ws.cell(row, 3, "")
        row += 1

    stripe_body(ws, 4, row - 1, 3)
    autosize(ws, {1: 12, 2: 40, 3: 40})


# ============================================================================
# Tab 11: Assessor Signoff
# ============================================================================

def create_signoff_tab(ws, proj: dict[str, Any]) -> None:
    style_title_row(ws, 1, 3, "Assessor Sign-off")

    row = 4
    ws.cell(row, 1, "Lead Assessor Name:").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row, 2, proj.get("lead_assessor_name", ""))
    row += 2

    ws.cell(row, 1, "Lead Assessor Signature:").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row, 2, "_" * 40)
    row += 1
    ws.cell(row, 1, "Date:").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row, 2, "")
    row += 3

    ws.cell(row, 1, "Sponsor/Customer Name:").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row, 2, proj.get("customer", ""))
    row += 2

    ws.cell(row, 1, "Sponsor/Customer Signature:").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row, 2, "_" * 40)
    row += 1
    ws.cell(row, 1, "Date:").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row, 2, "")

    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40


# ============================================================================
# Tab 12: References
# ============================================================================

def create_references_tab(ws) -> None:
    style_title_row(ws, 1, 2, "References")

    row = 3
    refs = [
        ("ASPICE PAM v3.1", "Automotive SPICE Process Assessment Model v3.1"),
        ("ASPICE PAM v4.0", "Automotive SPICE Process Assessment Model v4.0"),
        ("ASPICE PRM v3.1", "Automotive SPICE Process Reference Model v3.1"),
        ("ASPICE PRM v4.0", "Automotive SPICE Process Reference Model v4.0"),
        ("intacs", "International Automotive Competency Specification (Assessor Certification)"),
        ("ISO/IEC 33004", "Information technology Process assessment guidelines"),
    ]

    for ref_name, ref_desc in refs:
        ws.cell(row, 1, ref_name).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row, 2, ref_desc).alignment = Alignment(wrap_text=True)
        row += 1

    autosize(ws, {1: 20, 2: 60})


# ============================================================================
# Main generator
# ============================================================================

def generate_assessment(input_json: str, output_xlsx: str) -> None:
    with open(input_json) as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    tabs = [
        ("00_Title_Page", lambda ws: create_title_page(ws, data.get("project", {}))),
        ("01_Document_Control", lambda ws: create_document_control(ws, data.get("project", {}))),
        ("02_Assessment_Scope", lambda ws: create_scope_tab(ws, data.get("scope", {}))),
        ("03_Process_Reference_Model", lambda ws: create_prm_tab(ws, data.get("processes", []))),
        ("04_Process_Assessment_Model", lambda ws: create_pam_tab(ws, data.get("processes", []))),
        ("05_BP_Assessment", lambda ws: create_bp_assessment_tab(ws, data.get("processes", []))),
        ("06_GP_Assessment", lambda ws: create_gp_assessment_tab(ws, data.get("processes", []))),
        ("07_PA_Rating", lambda ws: create_pa_rating_tab(ws, data.get("processes", []))),
        ("08_Capability_Level", lambda ws: create_cl_rating_tab(ws, data.get("processes", []))),
        ("09_Capability_Profile", lambda ws: create_capability_profile_tab(ws, data.get("processes", []))),
        ("10_Strengths_Weaknesses", lambda ws: create_strengths_weaknesses_tab(ws, data.get("processes", []))),
        ("11_Assessor_Signoff", lambda ws: create_signoff_tab(ws, data.get("project", {}))),
        ("12_References", lambda ws: create_references_tab(ws)),
    ]

    for tab_name, creator in tabs:
        ws = wb.create_sheet(tab_name)
        creator(ws)

    wb.save(output_xlsx)
    print(json.dumps({"status": "ok", "tabs": len(tabs), "processes": len(data.get("processes", []))}))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_aspice_assessment.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(1)
    generate_assessment(sys.argv[1], sys.argv[2])
