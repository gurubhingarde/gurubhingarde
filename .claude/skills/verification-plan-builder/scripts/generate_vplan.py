"""Verification Plan builder - generates ISO 26262-8 §9 multi-tab workbook."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
GREEN_OK = "C6EFCE"
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
    scope = data.get("scope_description", "Verification scope not provided")
    methods = data.get("verification_methods", [])
    envs = data.get("environments", {})
    levels = data.get("test_levels", [])
    schedule = data.get("schedule", [])
    criteria = data.get("acceptance_criteria", [])

    # Tab 1: Title
    ws = wb.create_sheet("Title")
    ws.merge_cells("A2:C2")
    c = ws["A2"]
    c.value = "Verification Plan"
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
    ws["A1"] = "Verification Plan Document Control"
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

    # Tab 3: Verification Scope
    ws = wb.create_sheet("Verification Scope")
    ws["A1"] = "Verification Scope"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:C1")

    ws["A3"] = "Item:"
    ws["B3"] = item.get("name", "")
    ws["A4"] = "Safety Integrity Level:"
    ws["B4"] = item.get("abbr", "")
    ws["A6"] = "Scope Description:"
    ws["A7"] = scope
    ws["A7"].alignment = Alignment(wrap_text=True)
    ws.row_dimensions[7].height = 60

    # Tab 4: Verification Strategy
    ws = wb.create_sheet("Verification Strategy")
    ws["A1"] = "Verification Strategy"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:D1")

    headers = ["Method", "Applicability", "Lifecycle Phase", "Notes"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    for row_idx, m in enumerate(methods, 4):
        ws.cell(row=row_idx, column=1, value=m.get("method", ""))
        ws.cell(row=row_idx, column=2, value=m.get("applicability", ""))
        ws.cell(row=row_idx, column=3, value=m.get("level", ""))

    # Tab 5: Method Allocation per Requirement
    ws = wb.create_sheet("Method Allocation")
    ws["A1"] = "Verification Method Allocation per Requirement"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:F1")

    headers = ["Req ID", "Title", "Review", "Analysis", "Simulation", "Test"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    reqs = data.get("requirements", [])
    for row_idx, r in enumerate(reqs, 4):
        ws.cell(row=row_idx, column=1, value=r.get("id", ""))
        ws.cell(row=row_idx, column=2, value=r.get("title", ""))
        for col in [3, 4, 5, 6]:
            ws.cell(row=row_idx, column=col, value="X")

    # Tab 6: Environment Definitions
    ws = wb.create_sheet("Environments")
    ws["A1"] = "Verification Environments"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:C1")

    row = 3
    for env_type in ["hil", "sil", "vehicle", "bench"]:
        env_data = envs.get(env_type, {})
        ws.cell(row=row, column=1, value=env_type.upper()).font = Font(bold=True, size=11)
        ws.merge_cells(f"A{row}:C{row}")
        row += 1
        ws.cell(row=row, column=1, value=f"Description: {env_data.get('desc', 'TBD')}")
        ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True)
        row += 1
        ws.cell(row=row, column=1, value=f"Tools: {env_data.get('tools', 'TBD')}")
        row += 2

    # Tab 7: Test Levels
    ws = wb.create_sheet("Test Levels")
    ws["A1"] = "Test Levels and Coverage"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:C1")

    headers = ["Level", "Description", "Scope"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    for row_idx, lv in enumerate(levels or [
        {"level": "Unit", "description": "Individual code modules", "scope": "Component"},
        {"level": "Integration", "description": "Integrated subsystems", "scope": "Subsystem"},
        {"level": "System", "description": "Full system behavior", "scope": "System"},
        {"level": "Vehicle", "description": "End-to-end validation", "scope": "Vehicle"}
    ], 4):
        ws.cell(row=row_idx, column=1, value=lv.get("level", ""))
        ws.cell(row=row_idx, column=2, value=lv.get("description", ""))
        ws.cell(row=row_idx, column=3, value=lv.get("scope", ""))

    # Tab 8: Schedule
    ws = wb.create_sheet("Schedule")
    ws["A1"] = "Verification Schedule"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:D1")

    headers = ["Phase", "Start", "End", "Activities"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    for row_idx, ph in enumerate(schedule or [{"phase": "Planning", "start": "M1", "end": "M2", "activities": "Define scope"}], 4):
        ws.cell(row=row_idx, column=1, value=ph.get("phase", ""))
        ws.cell(row=row_idx, column=2, value=ph.get("start", ""))
        ws.cell(row=row_idx, column=3, value=ph.get("end", ""))
        ws.cell(row=row_idx, column=4, value=ph.get("activities", ""))

    # Tab 9: Roles and Responsibilities
    ws = wb.create_sheet("Roles")
    ws["A1"] = "Roles and Responsibilities"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:C1")

    headers = ["Role", "Responsibility", "Name"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    roles = ["Test Lead", "Test Engineer", "QA Reviewer", "Approver"]
    for row_idx, role in enumerate(roles, 4):
        ws.cell(row=row_idx, column=1, value=role)
        ws.cell(row=row_idx, column=2, value="TBD")
        ws.cell(row=row_idx, column=3, value="TBD")

    # Tab 10: Acceptance Criteria
    ws = wb.create_sheet("Acceptance Criteria")
    ws["A1"] = "Verification Acceptance Criteria"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:D1")

    headers = ["Criterion", "Measurement", "Pass Threshold", "Status"]
    for col, h in enumerate(headers, 1):
        ws.cell(row=3, column=col, value=h).font = Font(bold=True)
        ws.cell(row=3, column=col).fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    for row_idx, crit in enumerate(criteria or [
        {"criterion": "Requirement Coverage", "measurement": "% of requirements verified", "pass_threshold": ">= 100%"},
        {"criterion": "Test Pass Rate", "measurement": "% tests passed", "pass_threshold": ">= 95%"}
    ], 4):
        ws.cell(row=row_idx, column=1, value=crit.get("criterion", ""))
        ws.cell(row=row_idx, column=2, value=crit.get("measurement", ""))
        ws.cell(row=row_idx, column=3, value=crit.get("pass_threshold", ""))
        ws.cell(row=row_idx, column=4, value="Pending")

    # Tab 11: References
    ws = wb.create_sheet("References")
    ws["A1"] = "References and Applicable Standards"
    ws["A1"].font = Font(size=14, bold=True)
    ws.merge_cells("A1:B1")

    refs = [
        ("ISO 26262-8:2018", "Section 9: Verification"),
        ("IEEE 1012:2017", "Software Verification and Validation"),
        ("ISO 26262-4:2018", "System Level Requirements"),
        ("Project Requirements", item.get("doc_id", "TBD"))
    ]
    row = 3
    for std, desc in refs:
        ws.cell(row=row, column=1, value=std).font = Font(bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1

    try:
        wb.save(output_xlsx)
        print(f"Verification Plan generated: {output_xlsx}")
    except Exception as e:
        print(f"Error saving workbook: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.json> <output.xlsx>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
