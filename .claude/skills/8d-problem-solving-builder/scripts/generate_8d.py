"""
8D Problem Solving Builder — generates an 11-tab audit-ready workbook.

Usage:
    python generate_8d.py <input.json> <output.xlsx>

Input JSON schema:
{
  "problem": {id, customer, description, date_opened, owner, due_date},
  "team": [{name, role, expertise}],
  "is_is_not": {is, is_not, observed_effect, impact},
  "interim_containment": [{action, owner, due_date, verification}],
  "root_causes": [{cause, evidence, contributing_factors}],
  "corrective_actions": [{action, owner, due_date, verification_method}],
  "prevention": [{action_type, description}]
}
"""

import json
import sys
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

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def title_font(size=16):
    return Font(name=FONT_NAME, size=size, bold=True, color="FFFFFF")

def header_font():
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")

def body_font():
    return Font(name=FONT_NAME, size=10)

def style_title_row(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = title_font(14)
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28

def style_header_row(ws, row, headers):
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = header_font()
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 32

def stripe_body(ws, start_row, end_row, last_col):
    for r in range(start_row, end_row + 1):
        fill = PatternFill("solid", fgColor=ALT_ROW) if (r - start_row) % 2 else None
        for c in range(1, last_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = body_font()
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER_ALL
            if fill:
                cell.fill = fill

def autosize(ws, widths):
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width

def build_title_page(wb, problem):
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "8D Problem Solving Report")

    fields = [
        ("Problem ID", problem.get("id", "")),
        ("Customer", problem.get("customer", "")),
        ("Description", problem.get("description", "")),
        ("Date Opened", problem.get("date_opened", "")),
        ("Owner", problem.get("owner", "")),
        ("Target Close Date", problem.get("due_date", "")),
    ]

    row = 5
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        row += 1
    autosize(ws, {1: 4, 2: 22, 3: 60, 4: 4})

def build_doc_control(wb):
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 3, ["Revision", "Date", "Author", "Change", "Approver"])
    for i, row_data in enumerate([("0.1", "", "", "Initial 8D kickoff", ""), ("1.0", "", "", "Released", "")], start=4):
        for c, v in enumerate(row_data, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 5, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})

def build_d1_team(wb, team):
    ws = wb.create_sheet("02_D1_Establish_Team")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "D1. Establish Cross-Functional Team")
    style_header_row(ws, 3, ["Name", "Role", "Expertise", "Contact"])
    for i, member in enumerate(team, start=4):
        ws.cell(row=i, column=1, value=member.get("name", ""))
        ws.cell(row=i, column=2, value=member.get("role", ""))
        ws.cell(row=i, column=3, value=member.get("expertise", ""))
        ws.cell(row=i, column=4, value=member.get("contact", ""))
    if team:
        stripe_body(ws, 4, 3+len(team), 4)
    autosize(ws, {1: 20, 2: 14, 3: 30, 4: 30})

def build_d2_problem(wb, is_is_not):
    ws = wb.create_sheet("03_D2_Describe_Problem")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "D2. Describe the Problem (Is/Is-Not)")

    ws.cell(row=3, column=1, value="IS").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B3:C3")
    ws.cell(row=3, column=2, value=is_is_not.get("is", ""))

    ws.cell(row=4, column=1, value="IS NOT").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B4:C4")
    ws.cell(row=4, column=2, value=is_is_not.get("is_not", ""))

    ws.cell(row=6, column=1, value="Observed Effect").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B6:C6")
    ws.cell(row=6, column=2, value=is_is_not.get("observed_effect", ""))

    ws.cell(row=8, column=1, value="Impact").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B8:C8")
    ws.cell(row=8, column=2, value=is_is_not.get("impact", ""))
    autosize(ws, {1: 20, 2: 60, 3: 4})

def build_d3_containment(wb, containment):
    ws = wb.create_sheet("04_D3_Interim_Containment")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "D3. Interim Containment Actions")
    style_header_row(ws, 3, ["Action", "Owner", "Due Date", "Verification", "Status"])
    for i, action in enumerate(containment, start=4):
        ws.cell(row=i, column=1, value=action.get("action", ""))
        ws.cell(row=i, column=2, value=action.get("owner", ""))
        ws.cell(row=i, column=3, value=action.get("due_date", ""))
        ws.cell(row=i, column=4, value=action.get("verification", ""))
        ws.cell(row=i, column=5, value="Open")
    if containment:
        stripe_body(ws, 4, 3+len(containment), 5)
    autosize(ws, {1: 35, 2: 15, 3: 14, 4: 35, 5: 10})

def build_d4_root_cause(wb, root_causes):
    ws = wb.create_sheet("05_D4_Root_Cause_Analysis")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "D4. Root Cause Analysis")
    style_header_row(ws, 3, ["Root Cause", "Evidence", "Contributing Factors"])
    for i, rc in enumerate(root_causes, start=4):
        ws.cell(row=i, column=1, value=rc.get("cause", ""))
        ws.cell(row=i, column=2, value=rc.get("evidence", ""))
        ws.cell(row=i, column=3, value=rc.get("contributing_factors", ""))
    if root_causes:
        stripe_body(ws, 4, 3+len(root_causes), 3)
    autosize(ws, {1: 25, 2: 35, 3: 35})

def build_d5_corrective(wb, actions):
    ws = wb.create_sheet("06_D5_Permanent_Corrective_Actions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "D5. Permanent Corrective Actions")
    style_header_row(ws, 3, ["Action", "Owner", "Due Date", "Verification Method", "Status"])
    for i, act in enumerate(actions, start=4):
        ws.cell(row=i, column=1, value=act.get("action", ""))
        ws.cell(row=i, column=2, value=act.get("owner", ""))
        ws.cell(row=i, column=3, value=act.get("due_date", ""))
        ws.cell(row=i, column=4, value=act.get("verification_method", ""))
        ws.cell(row=i, column=5, value="Open")
    if actions:
        stripe_body(ws, 4, 3+len(actions), 5)
    autosize(ws, {1: 35, 2: 15, 3: 14, 4: 30, 5: 10})

def build_d6_implementation(wb):
    ws = wb.create_sheet("07_D6_Implement_Corrective_Actions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "D6. Implementation Tracker")
    style_header_row(ws, 3, ["Action ID", "Target Date", "Actual Date", "Status", "Evidence"])
    autosize(ws, {1: 12, 2: 14, 3: 14, 4: 12, 5: 30})

def build_d7_prevention(wb, prevention):
    ws = wb.create_sheet("08_D7_Prevent_Recurrence")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "D7. Systemic Prevention Measures")
    style_header_row(ws, 3, ["Type", "Description"])
    for i, item in enumerate(prevention, start=4):
        ws.cell(row=i, column=1, value=item.get("action_type", ""))
        ws.cell(row=i, column=2, value=item.get("description", ""))
    if prevention:
        stripe_body(ws, 4, 3+len(prevention), 2)
    autosize(ws, {1: 18, 2: 60})

def build_d8_recognition(wb):
    ws = wb.create_sheet("09_D8_Recognize_Team")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "D8. Team Recognition and Closure")

    ws.cell(row=3, column=1, value="Closure Approval").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=3, column=2, value="(Approver signature)")

    ws.cell(row=4, column=1, value="Closure Date").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=4, column=2, value="")

    ws.cell(row=6, column=1, value="Team Recognition").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=6, column=2, value="(Document team contributions and recognition)")
    autosize(ws, {1: 20, 2: 50})

def build_references(wb):
    ws = wb.create_sheet("10_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References")

    refs = [
        "Ford 8D Problem Solving Handbook",
        "IATF 16949 Quality Management Requirements",
        "ISO 14971 - Risk Management",
    ]

    for i, ref in enumerate(refs, start=3):
        ws.cell(row=i, column=1, value=f"• {ref}")
    autosize(ws, {1: 50, 2: 4})

def generate(input_path, output_path):
    with open(input_path) as f:
        data = json.load(f)

    problem = data.get("problem", {})
    team = data.get("team", [])
    is_is_not = data.get("is_is_not", {})
    containment = data.get("interim_containment", [])
    root_causes = data.get("root_causes", [])
    actions = data.get("corrective_actions", [])
    prevention = data.get("prevention", [])

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, problem)
    build_doc_control(wb)
    build_d1_team(wb, team)
    build_d2_problem(wb, is_is_not)
    build_d3_containment(wb, containment)
    build_d4_root_cause(wb, root_causes)
    build_d5_corrective(wb, actions)
    build_d6_implementation(wb)
    build_d7_prevention(wb, prevention)
    build_d8_recognition(wb)
    build_references(wb)

    wb.active = 0
    wb.save(output_path)

    return {
        "output_path": output_path,
        "tabs": 11,
        "team_size": len(team),
        "containment_actions": len(containment),
        "root_causes": len(root_causes),
        "corrective_actions": len(actions),
    }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_8d.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
