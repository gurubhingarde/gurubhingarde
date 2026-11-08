"""Dashboard for LL review."""

from openpyxl.styles import Font, PatternFill


def build_dashboard(wb, probed, results):
    """Build dashboard."""
    ws = wb.create_sheet("Dashboard", 0)
    ws.merge_cells("A1:B1")
    cell = ws.cell(row=1, column=1, value="Lessons Learned Dashboard")
    cell.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="1F3864")

    row = 3
    ws.cell(row=row, column=1, value="Project Name").font = Font(bold=True)
    ws.cell(row=row, column=2, value=probed.project_name)
