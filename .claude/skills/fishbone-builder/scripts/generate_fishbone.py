"""
Fishbone Builder — generates a 12-tab cause-and-effect analysis workbook.

Usage:
    python generate_fishbone.py <input.json> <output.xlsx>

Input JSON schema:
{
  "effect": {statement, owner, date},
  "cause_categories": [
    {category_name, causes: [{cause, evidence, impact_level}]}
  ]
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

def build_title_page(wb, effect):
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "Fishbone (Ishikawa) Cause-and-Effect Analysis")

    fields = [
        ("Effect / Problem", effect.get("statement", "")),
        ("Owner", effect.get("owner", "")),
        ("Date", effect.get("date", "")),
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
    for i, row_data in enumerate([("0.1", "", "", "Initial fishbone brainstorm", ""), ("1.0", "", "", "Released", "")], start=4):
        for c, v in enumerate(row_data, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 5, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})

def build_effect_statement(wb, effect):
    ws = wb.create_sheet("02_Effect_Statement")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Effect Statement")

    ws.cell(row=3, column=1, value="Problem/Effect Description").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B3:C3")
    ws.cell(row=3, column=2, value=effect.get("statement", ""))
    ws.cell(row=3, column=2).alignment = Alignment(wrap_text=True, vertical="top")

    autosize(ws, {1: 20, 2: 60, 3: 4})

def build_cause_categories(wb, categories):
    ws = wb.create_sheet("03_Cause_Categories")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Cause Category Overview")
    style_header_row(ws, 3, ["Category", "Number of Causes", "Status"])

    for i, cat in enumerate(categories, start=4):
        num_causes = len(cat.get("causes", []))
        ws.cell(row=i, column=1, value=cat.get("category_name", ""))
        ws.cell(row=i, column=2, value=num_causes)
        ws.cell(row=i, column=3, value="Under investigation" if num_causes < 3 else "Complete")

    if categories:
        stripe_body(ws, 4, 3+len(categories), 3)
    autosize(ws, {1: 18, 2: 14, 3: 20})

def build_category_tabs(wb, categories):
    for cat in categories:
        cat_name = cat.get("category_name", "Unknown").replace("/", "_").replace(" ", "_")
        tab_name = f"04_{cat_name}"[:31]
        ws = wb.create_sheet(tab_name)
        ws.sheet_view.showGridLines = False
        style_title_row(ws, 1, 4, f"{cat_name.replace('_', ' ')} Causes")
        style_header_row(ws, 3, ["Cause", "Evidence", "Impact Level", "Validated"])

        causes = cat.get("causes", [])
        for i, cause in enumerate(causes, start=4):
            ws.cell(row=i, column=1, value=cause.get("cause", ""))
            ws.cell(row=i, column=2, value=cause.get("evidence", ""))
            ws.cell(row=i, column=3, value=cause.get("impact_level", ""))
            ws.cell(row=i, column=4, value="")

        if causes:
            stripe_body(ws, 4, 3+len(causes), 4)
        autosize(ws, {1: 30, 2: 35, 3: 12, 4: 12})

def build_mermaid_diagram(wb, effect, categories):
    ws = wb.create_sheet("11_Mermaid_Diagram")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Fishbone Diagram (Mermaid Code)")

    ws.cell(row=3, column=1, value="Mermaid Fishbone Visualization").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B3:C3")

    mermaid_code = "graph LR\n"
    mermaid_code += f"  Effect[\"{effect.get('statement', 'Effect')[:50]}...\"]\n"

    for cat in categories:
        cat_name = cat.get("category_name", "")
        causes = cat.get("causes", [])
        mermaid_code += f"  {cat_name.replace(' ', '_')}[{cat_name}]\n"
        for i, cause in enumerate(causes[:3]):
            cause_short = cause.get("cause", "")[:30]
            mermaid_code += f"  {cat_name.replace(' ', '_')} --> Cause{i}\n"
            mermaid_code += f"  Cause{i}[{cause_short}]\n"
        mermaid_code += f"  {cat_name.replace(' ', '_')} --> Effect\n"

    ws.merge_cells("B4:C20")
    cell = ws.cell(row=4, column=2, value=mermaid_code)
    cell.alignment = Alignment(wrap_text=True, vertical="top")
    autosize(ws, {1: 4, 2: 80, 3: 4})

def build_references(wb):
    ws = wb.create_sheet("12_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References")

    refs = [
        "Ishikawa, K. (1968). Guide to Quality Control. Asian Productivity Organization.",
        "Six Sigma and Lean Manufacturing: Quality Improvement Methods",
        "AIAG Statistical Process Control Reference Manual",
    ]

    for i, ref in enumerate(refs, start=3):
        ws.cell(row=i, column=1, value=f"• {ref}")
    autosize(ws, {1: 80, 2: 4})

def generate(input_path, output_path):
    with open(input_path) as f:
        data = json.load(f)

    effect = data.get("effect", {})
    categories = data.get("cause_categories", [])

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, effect)
    build_doc_control(wb)
    build_effect_statement(wb, effect)
    build_cause_categories(wb, categories)
    build_category_tabs(wb, categories)
    build_mermaid_diagram(wb, effect, categories)
    build_references(wb)

    wb.active = 0
    wb.save(output_path)

    total_causes = sum(len(cat.get("causes", [])) for cat in categories)
    return {
        "output_path": output_path,
        "tabs": 4 + len(categories) + 2,
        "categories": len(categories),
        "total_causes": total_causes,
    }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_fishbone.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
