"""Dashboard builder for checklist review."""

from openpyxl.styles import Alignment, Border, Font, PatternFill, Side


def build_dashboard(wb, probed, results):
    """Build visual dashboard sheet."""
    ws = wb.create_sheet("Dashboard", 0)

    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 20

    # Title
    ws.merge_cells("A1:B1")
    cell = ws.cell(row=1, column=1, value="Risk Register Review Dashboard")
    cell.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="1F3864")
    cell.alignment = Alignment(horizontal="center", vertical="center")

    # Summary counts
    row = 3
    pass_count = sum(1 for r in results if "PASS" in r["status"].value)
    fail_count = sum(1 for r in results if "FAIL" in r["status"].value)
    warn_count = sum(1 for r in results if "WARN" in r["status"].value)

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

    row += 1
    ws.cell(row=row, column=1, value="WARN").font = Font(bold=True, color="FF8C00")
    ws.cell(row=row, column=2, value=warn_count)
    ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor="FFD966")

    # Project info
    row = 9
    ws.cell(row=row, column=1, value="Project Name").font = Font(bold=True)
    ws.cell(row=row, column=2, value=probed.project_name)

    row += 1
    ws.cell(row=row, column=1, value="Document ID").font = Font(bold=True)
    ws.cell(row=row, column=2, value=probed.doc_id)

    row += 1
    ws.cell(row=row, column=1, value="Target ASIL").font = Font(bold=True)
    ws.cell(row=row, column=2, value=probed.target_asil)

    row += 1
    ws.cell(row=row, column=1, value="Number of Risks").font = Font(bold=True)
    ws.cell(row=row, column=2, value=len(probed.risks))

    row += 1
    high_risk_count = sum(1 for r in probed.risks if r.risk_score >= 12)
    ws.cell(row=row, column=1, value="High-Risk Items (score >=12)").font = Font(bold=True)
    ws.cell(row=row, column=2, value=high_risk_count)
    if high_risk_count > 0:
        ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor="FFD966")

    # Required structures
    row = 17
    ws.cell(row=row, column=1, value="Required Structures").font = Font(bold=True, size=12)

    row += 1
    structures = [
        ("Mitigation Plan", probed.has_mitigation_plan),
        ("Contingency Plan", probed.has_contingency_plan),
        ("Escalation Log", probed.has_escalation_log),
        ("Risk Trend", probed.has_trend_analysis),
    ]

    for struct_name, present in structures:
        ws.cell(row=row, column=1, value=struct_name)
        status = "Present" if present else "Missing"
        status_cell = ws.cell(row=row, column=2, value=status)
        if present:
            status_cell.fill = PatternFill("solid", fgColor="C6EFCE")
        else:
            status_cell.fill = PatternFill("solid", fgColor="F8CBAD")
        row += 1

    ws.row_dimensions[1].height = 28
