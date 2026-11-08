"""SOTIF Validation & Verification strategy generator for ISO 21448."""
from __future__ import annotations
import json, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

FONT_NAME, NAVY, ALT_ROW = "Calibri", "1F3864", "F2F2F2"
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

def build_title_page(wb, system):
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "ISO 21448 SOTIF Validation & Verification Strategy")
    style_title_row(ws, 3, 4, system.get("name", ""))
    row = 6
    for label, value in [("Project", system.get("project", "")), ("Date", system.get("date", "")), ("Acceptance Criterion", system.get("acceptance_criterion", ""))]:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        row += 1
    autosize(ws, {1: 4, 2: 22, 3: 60, 4: 4})

def build_doc_control(wb):
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description", "Approver"])
    for i, data in enumerate([("0.1", "", "", "Initial V&V plan", ""), ("1.0", "", "", "Released", "")], start=4):
        for c, val in enumerate(data, start=1):
            ws.cell(row=i, column=c, value=val)
    stripe_body(ws, 4, 5, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})

def build_acceptance_criterion(wb, criterion):
    ws = wb.create_sheet("02_Acceptance_Criterion_Reference")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Acceptance Criterion Reference")
    style_header_row(ws, 3, ["Safety Goal ID", "Criterion", "Threshold", "Unit"])
    for i, item in enumerate(criterion, start=4):
        ws.cell(row=i, column=1, value=item.get("sg_id", ""))
        ws.cell(row=i, column=2, value=item.get("description", ""))
        ws.cell(row=i, column=3, value=item.get("threshold", ""))
        ws.cell(row=i, column=4, value=item.get("unit", ""))
    stripe_body(ws, 4, 3 + len(criterion), 4)
    autosize(ws, {1: 12, 2: 50, 3: 16, 4: 12})

def build_validation_methods(wb):
    ws = wb.create_sheet("03_Validation_Methods")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Validation Methods")
    style_header_row(ws, 3, ["Method", "Description", "Pros", "Cons", "Applicability"])
    methods = [
        ("Real-World Driving", "Natural exposure; fleet data collection", "High ecological validity", "Long timeline; many confounds", "Known Unsafe → Known Safe scenarios"),
        ("Simulation", "Controlled scenario reproduction", "Fast iteration; full reproducibility", "Correlation with real-world?", "Unknown Safe / Unknown Unsafe"),
        ("Proving Ground", "Closed-course repeatable scenarios", "Controlled; repeatable; safe", "Artificial; limited environmental coverage", "Transition scenarios"),
        ("HIL/SIL Testing", "Offline algorithm validation", "Fast; comprehensive coverage", "Requires test harness", "Algorithm edge cases"),
    ]
    for i, (name, desc, pros, cons, appl) in enumerate(methods, start=4):
        ws.cell(row=i, column=1, value=name)
        ws.cell(row=i, column=2, value=desc)
        ws.cell(row=i, column=3, value=pros)
        ws.cell(row=i, column=4, value=cons)
        ws.cell(row=i, column=5, value=appl)
    stripe_body(ws, 4, 7, 5)
    autosize(ws, {1: 18, 2: 35, 3: 35, 4: 35, 5: 40})

def build_scenario_coverage(wb, coverage):
    ws = wb.create_sheet("04_Scenario_Coverage_Plan")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Scenario Coverage Plan")
    style_header_row(ws, 3, ["Quadrant", "Scenario Count", "Mileage Target", "Validation Method", "Expected Duration", "Owner"])
    for i, item in enumerate(coverage, start=4):
        ws.cell(row=i, column=1, value=item.get("quadrant", ""))
        ws.cell(row=i, column=2, value=item.get("scenario_count", ""))
        ws.cell(row=i, column=3, value=item.get("mileage_target", ""))
        ws.cell(row=i, column=4, value=item.get("method", ""))
        ws.cell(row=i, column=5, value=item.get("duration", ""))
        ws.cell(row=i, column=6, value=item.get("owner", ""))
    stripe_body(ws, 4, 3 + len(coverage), 6)
    autosize(ws, {1: 16, 2: 14, 3: 16, 4: 18, 5: 18, 6: 14})

def build_real_world_plan(wb, rw):
    ws = wb.create_sheet("05_Real_World_Driving_Plan")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Real-World Driving Plan")
    style_header_row(ws, 3, ["Parameter", "Target Value", "Allocation", "Status", "Notes"])
    rows = [
        ("Cumulative Mileage", rw.get("cumulative_miles", ""), "Fleet vehicles", "", ""),
        ("Geographic Coverage", rw.get("geography", ""), "Multi-region", "", ""),
        ("Weather Distribution", rw.get("weather", ""), "Proportional to ODD", "", ""),
        ("Time-of-Day", rw.get("time_of_day", ""), "Day/night/dusk", "", ""),
    ]
    for i, (param, value, alloc, status, notes) in enumerate(rows, start=4):
        ws.cell(row=i, column=1, value=param)
        ws.cell(row=i, column=2, value=value)
        ws.cell(row=i, column=3, value=alloc)
        ws.cell(row=i, column=4, value=status)
        ws.cell(row=i, column=5, value=notes)
    stripe_body(ws, 4, 7, 5)
    autosize(ws, {1: 24, 2: 20, 3: 20, 4: 14, 5: 30})

def build_simulation_plan(wb, sim):
    ws = wb.create_sheet("06_Simulation_Plan")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Simulation Plan")
    style_header_row(ws, 3, ["Library / Source", "Scenario Count", "Simulator(s)", "Validation Status", "Coverage Gap"])
    for i, item in enumerate(sim, start=4):
        ws.cell(row=i, column=1, value=item.get("source", ""))
        ws.cell(row=i, column=2, value=item.get("scenario_count", ""))
        ws.cell(row=i, column=3, value=item.get("simulators", ""))
        ws.cell(row=i, column=4, value=item.get("validation_status", ""))
        ws.cell(row=i, column=5, value=item.get("coverage_gap", ""))
    stripe_body(ws, 4, 3 + len(sim), 5)
    autosize(ws, {1: 30, 2: 16, 3: 20, 4: 18, 5: 30})

def build_proving_ground_tests(wb, tests):
    ws = wb.create_sheet("07_Proving_Ground_Test_Cases")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Proving Ground Test Case Catalog")
    style_header_row(ws, 3, ["Test ID", "Scenario", "Pre-conditions", "Expected Behavior", "Pass/Fail Criteria", "Status", "Notes"])
    for i, item in enumerate(tests, start=4):
        ws.cell(row=i, column=1, value=item.get("test_id", ""))
        ws.cell(row=i, column=2, value=item.get("scenario", ""))
        ws.cell(row=i, column=3, value=item.get("preconditions", ""))
        ws.cell(row=i, column=4, value=item.get("expected_behavior", ""))
        ws.cell(row=i, column=5, value=item.get("criteria", ""))
        ws.cell(row=i, column=6, value=item.get("status", ""))
        ws.cell(row=i, column=7, value=item.get("notes", ""))
    stripe_body(ws, 4, 3 + len(tests), 7)
    autosize(ws, {1: 10, 2: 30, 3: 30, 4: 30, 5: 30, 6: 10, 7: 20})

def build_field_monitoring(wb, monitoring):
    ws = wb.create_sheet("08_Field_Monitoring_Plan")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Field Monitoring Plan (Post-Deployment)")
    style_header_row(ws, 3, ["Telemetry / Data Element", "Collection Rate", "Anomaly Detection Logic", "Alert Threshold", "Action"])
    for i, item in enumerate(monitoring, start=4):
        ws.cell(row=i, column=1, value=item.get("element", ""))
        ws.cell(row=i, column=2, value=item.get("rate", ""))
        ws.cell(row=i, column=3, value=item.get("logic", ""))
        ws.cell(row=i, column=4, value=item.get("threshold", ""))
        ws.cell(row=i, column=5, value=item.get("action", ""))
    stripe_body(ws, 4, 3 + len(monitoring), 5)
    autosize(ws, {1: 30, 2: 16, 3: 35, 4: 18, 5: 25})

def build_acceptance_tracking(wb, tracking):
    ws = wb.create_sheet("09_Acceptance_Criterion_Tracking")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Acceptance Criterion Tracking")
    style_header_row(ws, 3, ["Safety Goal", "Criterion", "Target", "Cumulative Evidence", "Percentage Complete", "Status"])
    for i, item in enumerate(tracking, start=4):
        ws.cell(row=i, column=1, value=item.get("sg_id", ""))
        ws.cell(row=i, column=2, value=item.get("criterion", ""))
        ws.cell(row=i, column=3, value=item.get("target", ""))
        ws.cell(row=i, column=4, value=item.get("evidence", ""))
        ws.cell(row=i, column=5, value=item.get("pct_complete", ""))
        ws.cell(row=i, column=6, value=item.get("status", ""))
    stripe_body(ws, 4, 3 + len(tracking), 6)
    autosize(ws, {1: 12, 2: 40, 3: 18, 4: 30, 5: 16, 6: 12})

def build_open_items(wb, items):
    ws = wb.create_sheet("10_Open_Items")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Open Items / Deferred Validations")
    style_header_row(ws, 3, ["Item ID", "Description", "Impact", "Planned Resolution", "Target Date", "Owner"])
    for i, item in enumerate(items, start=4):
        ws.cell(row=i, column=1, value=item.get("id", ""))
        ws.cell(row=i, column=2, value=item.get("description", ""))
        ws.cell(row=i, column=3, value=item.get("impact", ""))
        ws.cell(row=i, column=4, value=item.get("resolution", ""))
        ws.cell(row=i, column=5, value=item.get("date", ""))
        ws.cell(row=i, column=6, value=item.get("owner", ""))
    stripe_body(ws, 4, 3 + len(items), 6)
    autosize(ws, {1: 10, 2: 40, 3: 20, 4: 30, 5: 14, 6: 14})

def build_references(wb):
    ws = wb.create_sheet("11_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References")
    for i, ref in enumerate(["ISO 21448:2022 Sections 10-11", "NHTSA pre-crash scenarios", "EuroNCAP test protocols", "ODD validation best practices"], start=3):
        ws.cell(row=i, column=1, value=ref)
    autosize(ws, {1: 4, 2: 80})

def generate(input_path, output_path):
    with open(input_path) as f:
        data = json.load(f)
    system = data.get("system", {})
    wb = Workbook()
    wb.remove(wb.active)
    build_title_page(wb, system)
    build_doc_control(wb)
    build_acceptance_criterion(wb, data.get("acceptance_criteria", []))
    build_validation_methods(wb)
    build_scenario_coverage(wb, data.get("scenario_coverage", []))
    build_real_world_plan(wb, data.get("real_world_driving", {}))
    build_simulation_plan(wb, data.get("simulation_plan", []))
    build_proving_ground_tests(wb, data.get("proving_ground_tests", []))
    build_field_monitoring(wb, data.get("field_monitoring", []))
    build_acceptance_tracking(wb, data.get("acceptance_tracking", []))
    build_open_items(wb, data.get("open_items", []))
    build_references(wb)
    wb.active = 0
    wb.save(output_path)
    return {
        "system": system.get("name", ""),
        "scenario_coverage_rows": len(data.get("scenario_coverage", [])),
        "test_cases": len(data.get("proving_ground_tests", [])),
        "monitoring_elements": len(data.get("field_monitoring", [])),
        "open_items": len(data.get("open_items", [])),
        "tabs": 12,
        "output_path": output_path,
    }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_sotif_validation.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
