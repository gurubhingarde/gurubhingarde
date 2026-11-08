"""Validation Plan builder - generates ISO 26262-4 §9 multi-tab workbook."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def main(input_json: str, output_xlsx: str):
    try:
        with open(input_json) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_json} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

    wb = Workbook()
    wb.remove(wb.active)

    item = data.get("item", {})
    scope = data.get("scope_description", "Validation scope not provided")
    safety_goals = data.get("safety_goals", [])
    envs = data.get("validation_environments", [])
    scenarios = data.get("scenarios", [])
    methods = data.get("validation_methods", [])
    resources = data.get("resources", [])
    exit_criteria = data.get("exit_criteria", [])

    # Tab 1: Title
    ws = wb.create_sheet("Title")
    ws.merge_cells("A2:C2")
    c = ws["A2"]
    c.value = "Validation Plan"
    c.font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = Alignment(horizontal="center")

    row = 5
    for k, v in [("Project", item.get("project")), ("Item", item.get("name")),
                  ("Doc ID", item.get("doc_id")), ("Revision", item.get("revision")),
                  ("Author", item.get("author")), ("Date", item.get("date", date.today().isoformat()))]:
        ws.cell(row=row, column=1, value=k).font = Font(bold=True)
        ws.cell(row=row, column=2, value=v)
        row += 1

    # Tab 2: Document Control
    ws = wb.create_sheet("Document Control")
    ws["A1"] = "Validation Plan Document Control"
    ws["A1"].font = Font(size=14, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor=NAVY)
    ws.merge_cells("A1:D1")

    headers = ["Version", "Date", "Author", "Comment"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    ws.cell(row=4, column=1, value=item.get("revision", "1.0"))
    ws.cell(row=4, column=2, value=item.get("date", date.today().isoformat()))
    ws.cell(row=4, column=3, value=item.get("author", ""))
    ws.cell(row=4, column=4, value="Initial release")

    # Tab 3: Validation Scope
    ws = wb.create_sheet("Validation Scope")
    ws["A1"] = "Validation Scope"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:C1")

    ws["A3"] = "Item:"
    ws["B3"] = item.get("name", "")
    ws["A4"] = "Safety Goals:"
    ws["B4"] = len(safety_goals)
    ws["A6"] = "Scope Description:"
    ws["A7"] = scope
    ws["A7"].alignment = Alignment(wrap_text=True)
    ws.row_dimensions[7].height = 60

    # Tab 4: Validation Environments
    ws = wb.create_sheet("Validation Environments")
    ws["A1"] = "Validation Environments"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:C1")

    headers = ["Environment", "Description", "Location"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    for row_idx, env in enumerate(envs or [
        {"env": "Bench Test", "description": "Controlled lab environment", "location": "Facility"},
        {"env": "Proving Ground", "description": "Closed course testing", "location": "Test Track"},
        {"env": "Public Road", "description": "Real-world validation", "location": "Public Roads"}
    ], 4):
        ws.cell(row=row_idx, column=1, value=env.get("env", ""))
        ws.cell(row=row_idx, column=2, value=env.get("description", ""))
        ws.cell(row=row_idx, column=3, value=env.get("location", ""))

    # Tab 5: Scenario Catalog
    ws = wb.create_sheet("Scenario Catalog")
    ws["A1"] = "Validation Scenarios"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:D1")

    headers = ["Scenario ID", "Description", "Use Case", "Edge Case"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    for row_idx, scen in enumerate(scenarios or [], 4):
        ws.cell(row=row_idx, column=1, value=scen.get("id", ""))
        ws.cell(row=row_idx, column=2, value=scen.get("description", ""))
        ws.cell(row=row_idx, column=3, value=scen.get("use_case", ""))
        ws.cell(row=row_idx, column=4, value="Yes" if scen.get("edge_case") else "No")

    # Tab 6: Use Cases
    ws = wb.create_sheet("Use Cases")
    ws["A1"] = "Customer Use Cases"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:C1")

    row = 3
    ws.cell(row=row, column=1, value="Use Case").font = Font(bold=True)
    ws.cell(row=row, column=2, value="Safety Relevance").font = Font(bold=True)
    row += 1
    for uc in data.get("use_cases", []):
        ws.cell(row=row, column=1, value=uc.get("name", ""))
        ws.cell(row=row, column=2, value=uc.get("safety_relevance", ""))
        row += 1

    # Tab 7: Validation Methods
    ws = wb.create_sheet("Validation Methods")
    ws["A1"] = "Validation Methods"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:C1")

    headers = ["Method", "Applicability", "Notes"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    for row_idx, m in enumerate(methods or [], 4):
        ws.cell(row=row_idx, column=1, value=m.get("method", ""))
        ws.cell(row=row_idx, column=2, value=m.get("applicability", ""))

    # Tab 8: Schedule
    ws = wb.create_sheet("Schedule")
    ws["A1"] = "Validation Schedule"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:D1")

    headers = ["Phase", "Start", "End", "Activities"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    ws.cell(row=4, column=1, value="Bench Testing")
    ws.cell(row=4, column=2, value="M1")
    ws.cell(row=4, column=3, value="M3")
    ws.cell(row=5, column=1, value="Track Testing")
    ws.cell(row=5, column=2, value="M3")
    ws.cell(row=5, column=3, value="M5")

    # Tab 9: Resources
    ws = wb.create_sheet("Resources")
    ws["A1"] = "Resources and Equipment"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:C1")

    headers = ["Resource", "Quantity", "Specification"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    for row_idx, res in enumerate(resources or [], 4):
        ws.cell(row=row_idx, column=1, value=res.get("resource", ""))
        ws.cell(row=row_idx, column=2, value=res.get("quantity", ""))
        ws.cell(row=row_idx, column=3, value=res.get("specification", ""))

    # Tab 10: Exit Criteria and Signoff
    ws = wb.create_sheet("Exit Criteria")
    ws["A1"] = "Exit Criteria and Signoff"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:D1")

    headers = ["Criterion", "Measurement", "Threshold", "Status"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    for row_idx, crit in enumerate(exit_criteria or [], 4):
        ws.cell(row=row_idx, column=1, value=crit.get("criterion", ""))
        ws.cell(row=row_idx, column=2, value=crit.get("measurement", ""))
        ws.cell(row=row_idx, column=3, value=crit.get("threshold", ""))
        ws.cell(row=row_idx, column=4, value="Pending")

    # Tab 11: References
    ws = wb.create_sheet("References")
    ws["A1"] = "References"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:B1")

    refs = [
        ("ISO 26262-4:2018", "Item Level Validation"),
        ("Safety Goals Document", item.get("doc_id", "TBD")),
        ("System Verification Plan", "V-Plan cross-reference")
    ]
    row = 3
    for std, desc in refs:
        ws.cell(row=row, column=1, value=std).font = Font(bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1

    try:
        wb.save(output_xlsx)
        print(f"Validation Plan generated: {output_xlsx}")
    except Exception as e:
        print(f"Error saving workbook: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.json> <output.xlsx>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
