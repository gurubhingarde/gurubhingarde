#!/usr/bin/env python3
"""
Generate K-Matrix checklist report from extracted data and validation checks.
"""

from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from kmatrix_probe import KMatrixProbe
from check_definitions import KMatrixValidator

NAVY = "1F4E78"
LIGHT_GRAY = "D9E1F2"
PASS_GREEN = "C6EFCE"
FAIL_RED = "FFC7CE"
WARN_YELLOW = "FFEB9C"
WHITE = "FFFFFF"

HEADER_FONT = Font(name="Calibri", size=14, bold=True, color=WHITE)
HEADER_FILL = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")

TABLE_HEADER_FONT = Font(name="Calibri", size=10, bold=True, color=WHITE)
TABLE_HEADER_FILL = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")

PASS_FILL = PatternFill(start_color=PASS_GREEN, end_color=PASS_GREEN, fill_type="solid")
FAIL_FILL = PatternFill(start_color=FAIL_RED, end_color=FAIL_RED, fill_type="solid")
WARN_FILL = PatternFill(start_color=WARN_YELLOW, end_color=WARN_YELLOW, fill_type="solid")

BORDER_THIN = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

def set_cell(ws, row, col, value, font=None, fill=None):
    """Set cell with styling."""
    cell = ws.cell(row=row, column=col)
    cell.value = value
    if font:
        cell.font = font
    if fill:
        cell.fill = fill
    cell.border = BORDER_THIN
    return cell

def merge_range(ws, start_row, start_col, end_row, end_col, value, font=HEADER_FONT, fill=HEADER_FILL):
    """Merge and style cells."""
    ws.merge_cells(start_row=start_row, start_column=start_col, end_row=end_row, end_column=end_col)
    cell = ws.cell(row=start_row, column=start_col)
    cell.value = value
    cell.font = font
    cell.fill = fill
    cell.border = BORDER_THIN
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

def generate_checklist(xlsx_path, output_path="kmatrix_checklist.xlsx"):
    """Generate K-Matrix checklist report."""

    # Extract data
    prober = KMatrixProbe(xlsx_path)
    extracted = prober.extract_all()

    # Validate
    validator = KMatrixValidator(extracted)
    checks = validator.run_all_checks()

    # Create workbook
    wb = Workbook()
    wb.remove(wb.active)

    # Summary sheet
    ws_summary = wb.create_sheet("Summary")
    ws_summary.column_dimensions["A"].width = 30
    ws_summary.column_dimensions["B"].width = 20

    merge_range(ws_summary, 1, 1, 2, 2, "K-MATRIX AUDIT REPORT")
    row = 4

    pass_count = sum(1 for c in checks if c["status"] == "PASS")
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")
    warn_count = sum(1 for c in checks if c["status"] == "WARNING")

    set_cell(ws_summary, row, 1, "Generated:", font=Font(bold=True))
    set_cell(ws_summary, row, 2, datetime.now().strftime("%Y-%m-%d %H:%M"))
    row += 1

    set_cell(ws_summary, row, 1, "Source File:", font=Font(bold=True))
    set_cell(ws_summary, row, 2, xlsx_path)
    row += 2

    set_cell(ws_summary, row, 1, "Total Checks:", font=Font(bold=True))
    set_cell(ws_summary, row, 2, len(checks))
    row += 1

    set_cell(ws_summary, row, 1, "Passed:", font=Font(bold=True, color="008000"))
    set_cell(ws_summary, row, 2, pass_count, fill=PASS_FILL)
    row += 1

    set_cell(ws_summary, row, 1, "Failed:", font=Font(bold=True, color="FF0000"))
    set_cell(ws_summary, row, 2, fail_count, fill=FAIL_FILL)
    row += 1

    set_cell(ws_summary, row, 1, "Warnings:", font=Font(bold=True, color="FFA500"))
    set_cell(ws_summary, row, 2, warn_count, fill=WARN_FILL)
    row += 2

    status = "PASS" if fail_count == 0 else "FAIL"
    set_cell(ws_summary, row, 1, "Overall Status:", font=Font(bold=True))
    fill = PASS_FILL if status == "PASS" else FAIL_FILL
    set_cell(ws_summary, row, 2, status, fill=fill)

    # Checks sheet
    ws_checks = wb.create_sheet("Validation Checks")
    ws_checks.column_dimensions["A"].width = 35
    ws_checks.column_dimensions["B"].width = 12
    ws_checks.column_dimensions["C"].width = 50

    merge_range(ws_checks, 1, 1, 2, 3, "VALIDATION CHECKS")

    row = 4
    headers = ["Check Name", "Status", "Details"]
    for col, header in enumerate(headers, 1):
        set_cell(ws_checks, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    for check in checks:
        name = check["name"]
        status = check["status"]
        details = check["details"]

        status_fill = PASS_FILL if status == "PASS" else (FAIL_FILL if status == "FAIL" else WARN_FILL)

        set_cell(ws_checks, row, 1, name)
        set_cell(ws_checks, row, 2, status, fill=status_fill)
        set_cell(ws_checks, row, 3, details)
        row += 1

    # Structure sheet
    ws_struct = wb.create_sheet("Structure")
    ws_struct.column_dimensions["A"].width = 15
    ws_struct.column_dimensions["B"].width = 15

    merge_range(ws_struct, 1, 1, 2, 2, "K-MATRIX STRUCTURE")

    row = 4
    set_cell(ws_struct, row, 1, "ECU Count:", font=Font(bold=True))
    set_cell(ws_struct, row, 2, len(extracted["ecus"]))
    row += 1

    set_cell(ws_struct, row, 1, "Message Count:", font=Font(bold=True))
    set_cell(ws_struct, row, 2, len(extracted["messages"]))
    row += 1

    set_cell(ws_struct, row, 1, "Signal Count:", font=Font(bold=True))
    set_cell(ws_struct, row, 2, len(extracted["signals"]))
    row += 1

    set_cell(ws_struct, row, 1, "Bus Count:", font=Font(bold=True))
    set_cell(ws_struct, row, 2, len(extracted["buses"]))
    row += 1

    set_cell(ws_struct, row, 1, "Routing Rules:", font=Font(bold=True))
    set_cell(ws_struct, row, 2, len(extracted["routing_rules"]))
    row += 3

    # ECU list
    set_cell(ws_struct, row, 1, "ECU List:", font=Font(bold=True))
    row += 1
    for ecu_id in sorted(extracted["ecus"].keys()):
        set_cell(ws_struct, row, 1, ecu_id)
        row += 1

    wb.save(output_path)
    print(f"Checklist generated: {output_path}")
    return output_path

if __name__ == "__main__":
    import sys
    xlsx_in = sys.argv[1] if len(sys.argv) > 1 else "kmatrix_output.xlsx"
    xlsx_out = sys.argv[2] if len(sys.argv) > 2 else "kmatrix_checklist.xlsx"
    generate_checklist(xlsx_in, xlsx_out)
