"""
Safety Plan Builder — generates a multi-tab ISO 26262-2 §6 Safety Plan workbook.

Usage:
    python generate_safety_plan.py <input.json> <output.xlsx>

Input JSON schema:
{
  "project": {name, doc_id, revision, date, fsm_name, fsm_email, company, target_asil, vehicle_programs, suppliers},
  "roles": [{name, role, organization, email, independence_level}],
  "tailoring": [{clause, applicable, justification}],
  "work_products": [{wp_id, name, iso_reference, owner, target_asil, planned_date, actual_date, status}],
  "tools": [{name, vendor, version, usage, tcl, tcl_rationale, qualification_status}],
  "milestones": [{id, name, target_date, predecessors, status, notes}]
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


# ---------------------------------------------------------------------------
# Styling helpers (match hara-builder palette)
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"

THIN = Side(border_style="thin", color="BFBFBF")
MEDIUM = Side(border_style="medium", color="404040")
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


# ---------------------------------------------------------------------------
# Independence lookup per ASIL (ISO 26262-2 Table 1)
# ---------------------------------------------------------------------------

INDEPENDENCE_BY_ASIL = {
    "QM": "None",
    "A": "I1",
    "B": "I1",
    "C": "I2",
    "D": "I3",
}


def get_suggested_independence(asil: str) -> str:
    """Return suggested independence level for a target ASIL."""
    return INDEPENDENCE_BY_ASIL.get(asil, "I1")


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, data: dict) -> None:
    """00_Title_Page — Project info, FSM, schedule overview."""
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False

    proj = data.get("project", {})

    style_title_row(ws, 2, 4, "Safety Plan")
    style_title_row(ws, 3, 4, f"ISO 26262-2, Section 6")

    fields = [
        ("Project", proj.get("name", "")),
        ("Document ID", proj.get("doc_id", "")),
        ("Revision", proj.get("revision", "")),
        ("Date", proj.get("date", "")),
        ("Functional Safety Manager", proj.get("fsm_name", "")),
        ("FSM Email", proj.get("fsm_email", "")),
        ("Company", proj.get("company", "")),
        ("Target ASIL", proj.get("target_asil", "")),
        ("Vehicle Programs", proj.get("vehicle_programs", "")),
        ("Key Suppliers", proj.get("suppliers", "")),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1

    autosize(ws, {1: 4, 2: 26, 3: 60, 4: 4})


def build_document_control(wb: Workbook) -> None:
    """01_Document_Control — Revision history."""
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 5, "Document Control")

    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of Change", "Approver"])
    placeholders = [
        ("0.1", "", "", "Initial draft", ""),
        ("0.2", "", "", "Internal review", ""),
        ("1.0", "", "", "Released", ""),
    ]
    for i, row_data in enumerate(placeholders, start=4):
        for col, val in enumerate(row_data, start=1):
            ws.cell(row=i, column=col, value=val)
    stripe_body(ws, 4, 4 + len(placeholders) - 1, 5)
    autosize(ws, {1: 12, 2: 12, 3: 18, 4: 30, 5: 18})


def build_project_info(wb: Workbook, data: dict) -> None:
    """02_Project_Info — Project name, item, ASIL, programs, suppliers, key dates."""
    ws = wb.create_sheet("02_Project_Info")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 4, "Project Information")

    proj = data.get("project", {})

    row = 3
    fields = [
        ("Project Name", proj.get("name", "")),
        ("Document ID", proj.get("doc_id", "")),
        ("Item Name / Abbreviation", ""),
        ("Target ASIL", proj.get("target_asil", "")),
        ("Vehicle Programs", proj.get("vehicle_programs", "")),
        ("Key Suppliers", proj.get("suppliers", "")),
        ("Project Start Date", ""),
        ("Planned Release Date", ""),
        ("Planned FSC Review Date", ""),
    ]

    for label, value in fields:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

    autosize(ws, {1: 30, 2: 50})


def build_roles_responsibilities(wb: Workbook, data: dict) -> None:
    """03_Roles_Responsibilities — RACI table with FSM, PM, HW Lead, SW Lead, CR, Assessor, Customer."""
    ws = wb.create_sheet("03_Roles_Responsibilities")

    style_title_row(ws, 1, 5, "Roles and Responsibilities")

    headers = ["Name", "Role", "Organization", "Email", "Independence Level"]
    style_header_row(ws, 3, headers)

    roles = data.get("roles", [])

    # Add standard role placeholders if not provided
    if not roles:
        roles = [
            {"name": "", "role": "Functional Safety Manager", "organization": "", "email": "", "independence_level": ""},
            {"name": "", "role": "Project Manager", "organization": "", "email": "", "independence_level": ""},
            {"name": "", "role": "HW Lead", "organization": "", "email": "", "independence_level": ""},
            {"name": "", "role": "SW Lead", "organization": "", "email": "", "independence_level": ""},
            {"name": "", "role": "Confirmation Reviewer", "organization": "", "email": "", "independence_level": ""},
            {"name": "", "role": "Assessor", "organization": "", "email": "", "independence_level": ""},
            {"name": "", "role": "Customer Interface", "organization": "", "email": "", "independence_level": ""},
        ]

    for i, role in enumerate(roles, start=4):
        ws.cell(row=i, column=1, value=role.get("name", ""))
        ws.cell(row=i, column=2, value=role.get("role", ""))
        ws.cell(row=i, column=3, value=role.get("organization", ""))
        ws.cell(row=i, column=4, value=role.get("email", ""))
        ws.cell(row=i, column=5, value=role.get("independence_level", ""))

    stripe_body(ws, 4, 4 + len(roles) - 1, 5)
    autosize(ws, {1: 20, 2: 25, 3: 20, 4: 25, 5: 20})


def build_tailoring(wb: Workbook, data: dict) -> None:
    """04_Tailoring — Per ISO 26262 part/clause: Applicable (Yes/No/Partial), Justification."""
    ws = wb.create_sheet("04_Tailoring")

    style_title_row(ws, 1, 3, "Tailoring of ISO 26262 Activities")

    headers = ["ISO 26262 Clause / Part", "Applicable (Yes/No/Partial)", "Justification"]
    style_header_row(ws, 3, headers)

    tailoring = data.get("tailoring", [])
    if not tailoring:
        # Default clauses from Part 2–8
        tailoring = [
            {"clause": "Part 2 (Management of Functional Safety)", "applicable": "Yes", "justification": ""},
            {"clause": "Part 3 (Concept Phase)", "applicable": "Yes", "justification": ""},
            {"clause": "Part 4 (Product Development at System Level)", "applicable": "Yes", "justification": ""},
            {"clause": "Part 5 (Product Development at Hardware Level)", "applicable": "Yes", "justification": ""},
            {"clause": "Part 6 (Product Development at Software Level)", "applicable": "Yes", "justification": ""},
            {"clause": "Part 7 (Production, Operation, Service, Decommissioning)", "applicable": "Partial", "justification": ""},
            {"clause": "Part 8 (Functional Safety Analysis and Proof Test)", "applicable": "Yes", "justification": ""},
        ]

    for i, item in enumerate(tailoring, start=4):
        ws.cell(row=i, column=1, value=item.get("clause", ""))
        ws.cell(row=i, column=2, value=item.get("applicable", ""))
        ws.cell(row=i, column=3, value=item.get("justification", ""))

    stripe_body(ws, 4, 4 + len(tailoring) - 1, 3)
    autosize(ws, {1: 50, 2: 25, 3: 50})


def build_work_products(wb: Workbook, data: dict) -> None:
    """05_Work_Products — Master list: WP_ID, name, ISO ref, owner, ASIL, planned date, actual date, status."""
    ws = wb.create_sheet("05_Work_Products")

    style_title_row(ws, 1, 8, "Work Products")

    headers = ["WP_ID", "Work Product Name", "ISO 26262 Reference", "Owner", "Target ASIL", "Planned Date", "Actual Date", "Status"]
    style_header_row(ws, 3, headers)

    work_products = data.get("work_products", [])
    for i, wp in enumerate(work_products, start=4):
        ws.cell(row=i, column=1, value=wp.get("wp_id", ""))
        ws.cell(row=i, column=2, value=wp.get("name", ""))
        ws.cell(row=i, column=3, value=wp.get("iso_reference", ""))
        ws.cell(row=i, column=4, value=wp.get("owner", ""))
        ws.cell(row=i, column=5, value=wp.get("target_asil", ""))
        ws.cell(row=i, column=6, value=wp.get("planned_date", ""))
        ws.cell(row=i, column=7, value=wp.get("actual_date", ""))
        ws.cell(row=i, column=8, value=wp.get("status", "Not Started"))

    stripe_body(ws, 4, 4 + len(work_products) - 1, 8)
    autosize(ws, {1: 10, 2: 30, 3: 25, 4: 18, 5: 12, 6: 14, 7: 14, 8: 16})


def build_confirmation_reviews(wb: Workbook, data: dict) -> None:
    """06_Confirmation_Reviews — WP_ID, work product, required independence, reviewer, planned/actual date, status, notes."""
    ws = wb.create_sheet("06_Confirmation_Reviews")

    style_title_row(ws, 1, 8, "Confirmation Reviews")

    headers = ["WP_ID", "Work Product", "Required Independence (per ASIL)", "Assigned Reviewer", "Planned Date", "Actual Date", "Status", "Notes"]
    style_header_row(ws, 3, headers)

    work_products = data.get("work_products", [])
    for i, wp in enumerate(work_products, start=4):
        ws.cell(row=i, column=1, value=wp.get("wp_id", ""))
        ws.cell(row=i, column=2, value=wp.get("name", ""))
        # Auto-suggest independence based on target ASIL
        asil = wp.get("target_asil", "QM")
        independence = get_suggested_independence(asil)
        ws.cell(row=i, column=3, value=independence)
        ws.cell(row=i, column=4, value="")  # Assigned reviewer
        ws.cell(row=i, column=5, value="")  # Planned date
        ws.cell(row=i, column=6, value="")  # Actual date
        ws.cell(row=i, column=7, value="Not Started")
        ws.cell(row=i, column=8, value="")  # Notes

    stripe_body(ws, 4, 4 + len(work_products) - 1, 8)
    autosize(ws, {1: 10, 2: 25, 3: 22, 4: 20, 5: 14, 6: 14, 7: 14, 8: 25})


def build_tools(wb: Workbook, data: dict) -> None:
    """07_Tools — Tool name, vendor, version, usage, TCL, TCL rationale, qualification status."""
    ws = wb.create_sheet("07_Tools")

    style_title_row(ws, 1, 7, "Tools")

    headers = ["Tool Name", "Vendor", "Version", "Usage in Safety Lifecycle", "TCL", "TCL Rationale", "Qualification Status"]
    style_header_row(ws, 3, headers)

    tools = data.get("tools", [])
    for i, tool in enumerate(tools, start=4):
        ws.cell(row=i, column=1, value=tool.get("name", ""))
        ws.cell(row=i, column=2, value=tool.get("vendor", ""))
        ws.cell(row=i, column=3, value=tool.get("version", ""))
        ws.cell(row=i, column=4, value=tool.get("usage", ""))
        ws.cell(row=i, column=5, value=tool.get("tcl", ""))
        ws.cell(row=i, column=6, value=tool.get("tcl_rationale", ""))
        ws.cell(row=i, column=7, value=tool.get("qualification_status", ""))

    stripe_body(ws, 4, 4 + len(tools) - 1, 7)
    autosize(ws, {1: 22, 2: 15, 3: 12, 4: 28, 5: 10, 6: 30, 7: 20})


def build_resources(wb: Workbook) -> None:
    """08_Resources — HW resources, SW tools licenses, lab equipment, training plan."""
    ws = wb.create_sheet("08_Resources")

    style_title_row(ws, 1, 3, "Resources")

    headers = ["Resource Category", "Description", "Status"]
    style_header_row(ws, 3, headers)

    categories = [
        ("Hardware Resources", "", ""),
        ("Software Tool Licenses", "", ""),
        ("Lab Equipment", "", ""),
        ("Training Plan", "", ""),
    ]
    for i, (cat, desc, status) in enumerate(categories, start=4):
        ws.cell(row=i, column=1, value=cat)
        ws.cell(row=i, column=2, value=desc)
        ws.cell(row=i, column=3, value=status)

    stripe_body(ws, 4, 4 + len(categories) - 1, 3)
    autosize(ws, {1: 25, 2: 50, 3: 15})


def build_anomaly_resolution(wb: Workbook) -> None:
    """09_Anomaly_Resolution — Process description + anomaly tracker."""
    ws = wb.create_sheet("09_Anomaly_Resolution")

    style_title_row(ws, 1, 7, "Anomaly Resolution Process")

    # Process description placeholder
    ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=7)
    ws.cell(row=3, column=1, value="Process Description: Placeholder for anomaly resolution procedure.").font = Font(name=FONT_NAME, size=10, italic=True)

    # Tracker table
    headers = ["ID", "Raised By", "Date Raised", "Description", "Severity", "Owner", "Status", "Resolution"]
    style_header_row(ws, 5, headers)

    placeholders = [
        ("A01", "", "", "", "Minor", "", "Open", ""),
        ("A02", "", "", "", "Major", "", "In Progress", ""),
    ]
    for i, row_data in enumerate(placeholders, start=6):
        for col, val in enumerate(row_data, start=1):
            ws.cell(row=i, column=col, value=val)

    stripe_body(ws, 6, 6 + len(placeholders) - 1, 8)
    autosize(ws, {1: 10, 2: 15, 3: 14, 4: 25, 5: 12, 6: 15, 7: 14, 8: 25})


def build_schedule(wb: Workbook, data: dict) -> None:
    """10_Schedule — Milestones table: ID, name, target date, predecessors, status, notes."""
    ws = wb.create_sheet("10_Schedule")

    style_title_row(ws, 1, 6, "Project Schedule")

    headers = ["Milestone ID", "Milestone Name", "Target Date", "Predecessors", "Status", "Notes"]
    style_header_row(ws, 3, headers)

    milestones = data.get("milestones", [])
    if not milestones:
        milestones = [
            {"id": "M01", "name": "Project Kickoff", "target_date": "", "predecessors": "", "status": "Open", "notes": ""},
            {"id": "M02", "name": "Design Review", "target_date": "", "predecessors": "M01", "status": "Open", "notes": ""},
            {"id": "M03", "name": "Verification Complete", "target_date": "", "predecessors": "M02", "status": "Open", "notes": ""},
            {"id": "M04", "name": "FSC Review", "target_date": "", "predecessors": "M03", "status": "Open", "notes": ""},
        ]

    for i, milestone in enumerate(milestones, start=4):
        ws.cell(row=i, column=1, value=milestone.get("id", ""))
        ws.cell(row=i, column=2, value=milestone.get("name", ""))
        ws.cell(row=i, column=3, value=milestone.get("target_date", ""))
        ws.cell(row=i, column=4, value=milestone.get("predecessors", ""))
        ws.cell(row=i, column=5, value=milestone.get("status", "Open"))
        ws.cell(row=i, column=6, value=milestone.get("notes", ""))

    stripe_body(ws, 4, 4 + len(milestones) - 1, 6)
    autosize(ws, {1: 14, 2: 25, 3: 14, 4: 20, 5: 12, 6: 25})


def build_references(wb: Workbook) -> None:
    """11_References — Standards, customer docs, internal procedures."""
    ws = wb.create_sheet("11_References")

    style_title_row(ws, 1, 3, "References")

    headers = ["Reference", "Title", "Notes"]
    style_header_row(ws, 3, headers)

    references = [
        ("ISO 26262-1:2018", "Functional Safety — Part 1: Concepts and Definitions", ""),
        ("ISO 26262-2:2018", "Functional Safety — Part 2: Management of Functional Safety", ""),
        ("ISO 26262-3:2018", "Functional Safety — Part 3: Concept Phase", ""),
        ("ISO 26262-4:2018", "Functional Safety — Part 4: Product Development at System Level", ""),
        ("ISO 26262-5:2018", "Functional Safety — Part 5: Product Development at Hardware Level", ""),
        ("ISO 26262-6:2018", "Functional Safety — Part 6: Product Development at Software Level", ""),
        ("ISO 26262-7:2018", "Functional Safety — Part 7: Production, Operation, Service, Decommissioning", ""),
        ("ISO 26262-8:2018", "Functional Safety — Part 8: Functional Safety Analysis and Proof Test", ""),
        ("Customer Document", "", ""),
        ("Internal Procedure", "", ""),
    ]

    for i, (ref, title, notes) in enumerate(references, start=4):
        ws.cell(row=i, column=1, value=ref)
        ws.cell(row=i, column=2, value=title)
        ws.cell(row=i, column=3, value=notes)

    stripe_body(ws, 4, 4 + len(references) - 1, 3)
    autosize(ws, {1: 25, 2: 50, 3: 30})


def main() -> None:
    """Generate Safety Plan workbook from JSON input."""
    if len(sys.argv) != 3:
        print("Usage: python generate_safety_plan.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: input file not found: {input_file}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    # Build all 12 tabs in order
    build_title_page(wb, data)
    build_document_control(wb)
    build_project_info(wb, data)
    build_roles_responsibilities(wb, data)
    build_tailoring(wb, data)
    build_work_products(wb, data)
    build_confirmation_reviews(wb, data)
    build_tools(wb, data)
    build_resources(wb)
    build_anomaly_resolution(wb)
    build_schedule(wb, data)
    build_references(wb)

    wb.save(str(output_file))
    print(f"Safety Plan generated: {output_file}")
    print(f"Tabs: {len(wb.sheetnames)} — {', '.join(wb.sheetnames)}")


if __name__ == "__main__":
    main()
