"""Dashboard builder for WP status rollup review."""

from openpyxl.styles import Font, PatternFill, Alignment


def build_dashboard(wb, probed, results):
    """Build visual dashboard sheet."""
    ws = wb.create_sheet("Dashboard", 0)

    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 20

    ws.merge_cells("A1:B1")
    cell = ws.cell(row=1, column=1, value="WP Status Rollup Dashboard")
    cell.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="1F3864")
    cell.alignment = Alignment(horizontal="center", vertical="center")

    row = 3
    pass_count = sum(1 for r in results if "PASS" in r.get("status", ""))
    fail_count = sum(1 for r in results if "FAIL" in r.get("status", ""))

    ws.cell(row=row, column=1, value="Total Checks").font = Font(bold=True)
    ws.cell(row=row, column=2, value=len(results))

    row += 1
    ws.cell(row=row, column=1, value="PASS").font = Font(bold=True, color="008000")
    ws.cell(row=row, column=2, value=pass_count)
    ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor="C6EFCE")

    row += 1
    ws.cell(row=row, column=1, value="FAIL").font = Font(bold=True, color="FF0000")
    ws.cell(row=row, column=2, value=fail_count)
    ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor="F8CBAD")

    row = 9
    ws.cell(row=row, column=1, value="Project Name").font = Font(bold=True)
    ws.cell(row=row, column=2, value=probed.project_name)

    row += 1
    ws.cell(row=row, column=1, value="Reporting Period").font = Font(bold=True)
    ws.cell(row=row, column=2, value=probed.reporting_period)

    ws.row_dimensions[1].height = 28
