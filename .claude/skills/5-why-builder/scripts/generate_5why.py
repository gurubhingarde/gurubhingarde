"""
5-Why Builder — generates an 8-tab root cause analysis workbook.

Usage:
    python generate_5why.py <input.json> <output.xlsx>

Input JSON schema:
{
  "problem": {id, statement, owner, date},
  "why_tree": [
    {level, question, answer, branch_id, parent_branch}
  ],
  "root_causes": [{cause, evidence, contributing_factors}],
  "corrective_actions": [{root_cause_id, action, owner, target_date, verification_method}],
  "verification": [{action_id, metric, baseline, target, actual, decision}]
}
"""

import json
import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

FONT_NAME = "Calibri"
NAVY = "1F3864"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def header_font():
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")

def body_font():
    return Font(name=FONT_NAME, size=10)

def style_title_row(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
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
    style_title_row(ws, 2, 4, "5-Why Root Cause Analysis")

    fields = [
        ("Issue ID", problem.get("id", "")),
        ("Problem Statement", problem.get("statement", "")),
        ("Owner", problem.get("owner", "")),
        ("Date", problem.get("date", "")),
    ]

    row = 5
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(wrap_text=True, vertical="top")
        row += 1
    autosize(ws, {1: 4, 2: 22, 3: 60, 4: 4})

def build_doc_control(wb):
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 3, ["Revision", "Date", "Author", "Change", "Approver"])
    for i, row_data in enumerate([("0.1", "", "", "Initial 5-Why analysis", ""), ("1.0", "", "", "Released", "")], start=4):
        for c, v in enumerate(row_data, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 5, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})

def build_problem_statement(wb, problem):
    ws = wb.create_sheet("02_Problem_Statement")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Problem Statement")

    ws.cell(row=3, column=1, value="What is the problem?").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B3:C3")
    ws.cell(row=3, column=2, value=problem.get("statement", ""))

    ws.cell(row=5, column=1, value="Observed Effect").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B5:C5")
    ws.cell(row=5, column=2, value=problem.get("observed_effect", ""))

    ws.cell(row=7, column=1, value="Business Impact").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B7:C7")
    ws.cell(row=7, column=2, value=problem.get("impact", ""))
    autosize(ws, {1: 20, 2: 60, 3: 4})

def build_why_tree(wb, why_tree):
    ws = wb.create_sheet("03_5_Why_Tree")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "5-Why Hierarchical Tree")
    style_header_row(ws, 3, ["Level", "Question", "Answer", "Branch ID", "Parent Branch"])

    for i, item in enumerate(why_tree, start=4):
        ws.cell(row=i, column=1, value=item.get("level", ""))
        ws.cell(row=i, column=2, value=item.get("question", ""))
        ws.cell(row=i, column=3, value=item.get("answer", ""))
        ws.cell(row=i, column=4, value=item.get("branch_id", ""))
        ws.cell(row=i, column=5, value=item.get("parent_branch", ""))

    if why_tree:
        stripe_body(ws, 4, 3+len(why_tree), 5)
    autosize(ws, {1: 8, 2: 30, 3: 40, 4: 12, 5: 12})

def build_root_causes(wb, root_causes):
    ws = wb.create_sheet("04_Root_Causes_Identified")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Root Causes Identified")
    style_header_row(ws, 3, ["Root Cause", "Evidence", "Contributing Factors"])

    for i, rc in enumerate(root_causes, start=4):
        ws.cell(row=i, column=1, value=rc.get("cause", ""))
        ws.cell(row=i, column=2, value=rc.get("evidence", ""))
        ws.cell(row=i, column=3, value=rc.get("contributing_factors", ""))

    if root_causes:
        stripe_body(ws, 4, 3+len(root_causes), 3)
    autosize(ws, {1: 25, 2: 35, 3: 35})

def build_corrective_actions(wb, actions):
    ws = wb.create_sheet("05_Corrective_Actions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Corrective Actions")
    style_header_row(ws, 3, ["Root Cause ID", "Action", "Owner", "Target Date", "Verification Method", "Status"])

    for i, act in enumerate(actions, start=4):
        ws.cell(row=i, column=1, value=act.get("root_cause_id", ""))
        ws.cell(row=i, column=2, value=act.get("action", ""))
        ws.cell(row=i, column=3, value=act.get("owner", ""))
        ws.cell(row=i, column=4, value=act.get("target_date", ""))
        ws.cell(row=i, column=5, value=act.get("verification_method", ""))
        ws.cell(row=i, column=6, value="Open")

    if actions:
        stripe_body(ws, 4, 3+len(actions), 6)
    autosize(ws, {1: 14, 2: 35, 3: 15, 4: 14, 5: 30, 6: 10})

def build_verification(wb, verification):
    ws = wb.create_sheet("06_Verification_of_Effectiveness")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Post-Action Verification")
    style_header_row(ws, 3, ["Action ID", "Metric", "Baseline", "Target", "Actual", "Status", "Notes"])

    for i, v in enumerate(verification, start=4):
        ws.cell(row=i, column=1, value=v.get("action_id", ""))
        ws.cell(row=i, column=2, value=v.get("metric", ""))
        ws.cell(row=i, column=3, value=v.get("baseline", ""))
        ws.cell(row=i, column=4, value=v.get("target", ""))
        ws.cell(row=i, column=5, value=v.get("actual", ""))
        ws.cell(row=i, column=6, value=v.get("decision", ""))
        ws.cell(row=i, column=7, value="")

    if verification:
        stripe_body(ws, 4, 3+len(verification), 7)
    autosize(ws, {1: 12, 2: 20, 3: 14, 4: 14, 5: 14, 6: 10, 7: 30})

def build_references(wb):
    ws = wb.create_sheet("07_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References")

    refs = [
        "Ohno, T. (1988). Toyota Production System: Beyond Large-Scale Production.",
        "Taiichi Ohno - 5 Why Method (Toyota)",
        "Lean Manufacturing and Root Cause Analysis Best Practices",
    ]

    for i, ref in enumerate(refs, start=3):
        ws.cell(row=i, column=1, value=f"• {ref}")
    autosize(ws, {1: 70, 2: 4})

def generate(input_path, output_path):
    with open(input_path) as f:
        data = json.load(f)

    problem = data.get("problem", {})
    why_tree = data.get("why_tree", [])
    root_causes = data.get("root_causes", [])
    actions = data.get("corrective_actions", [])
    verification = data.get("verification", [])

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, problem)
    build_doc_control(wb)
    build_problem_statement(wb, problem)
    build_why_tree(wb, why_tree)
    build_root_causes(wb, root_causes)
    build_corrective_actions(wb, actions)
    build_verification(wb, verification)
    build_references(wb)

    wb.active = 0
    wb.save(output_path)

    return {
        "output_path": output_path,
        "tabs": 8,
        "why_levels": len(why_tree),
        "root_causes": len(root_causes),
        "corrective_actions": len(actions),
    }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_5why.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
