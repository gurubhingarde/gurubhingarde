"""Safety Program Risk Register — generates a multi-tab ISO 26262 Risk Register workbook from JSON input.

Usage:
    python generate_risk_register.py <input.json> <output.xlsx>

Input JSON schema:
{
  "project": {name, doc_id, target_asil},
  "reporting_period": {start, end},
  "risks": [
    {id, category, description, owner, likelihood (1-5), impact (1-5),
     mitigation, contingency, status, target_date}
  ]
}
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"
GREY = "D0CECE"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

RISK_CATEGORIES = ["resource", "tool", "supplier", "schedule", "compliance", "scope", "other"]


def style_title(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header(ws, row, headers):
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 36


def style_data_row(ws, row, num_cols, alt=False):
    fill_color = ALT_ROW if alt else "FFFFFF"
    for col in range(1, num_cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill = PatternFill("solid", fgColor=fill_color)
        cell.border = BORDER_ALL


def build_title_page(wb, project, reporting_period):
    ws = wb.active
    ws.title = "Title Page"
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title(ws, row, 3, "Safety Program Risk Register")

    row = 3
    ws.cell(row=row, column=1, value="Project Name").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project.get("name", ""))

    row += 1
    ws.cell(row=row, column=1, value="Document ID").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project.get("doc_id", "RR-001"))

    row += 1
    ws.cell(row=row, column=1, value="Target ASIL").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project.get("target_asil", "D"))

    row += 1
    ws.cell(row=row, column=1, value="Reporting Period").font = Font(bold=True)
    ws.cell(row=row, column=2, value=f"{reporting_period.get('start', '')} to {reporting_period.get('end', '')}")

    row += 1
    ws.cell(row=row, column=1, value="Document Date").font = Font(bold=True)
    ws.cell(row=row, column=2, value=str(date.today()))

    row += 1
    ws.cell(row=row, column=1, value="Revision").font = Font(bold=True)
    ws.cell(row=row, column=2, value="1.0")


def build_document_control(wb):
    ws = wb.create_sheet("Document Control")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 50

    row = 1
    style_title(ws, row, 3, "Document Control")

    row = 3
    headers = ["Revision", "Date", "Author", "Summary"]
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="1.0")
    ws.cell(row=row, column=2, value=str(date.today()))
    ws.cell(row=row, column=3, value="FSM")
    ws.cell(row=row, column=4, value="Initial release")
    style_data_row(ws, row, 4)


def build_risk_register(wb, risks):
    ws = wb.create_sheet("Risk Catalog")

    headers = ["Risk ID", "Category", "Description", "Likelihood", "Impact", "Risk Score", "Owner", "Status", "Target Date"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 35
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 10
    ws.column_dimensions["F"].width = 12
    ws.column_dimensions["G"].width = 12
    ws.column_dimensions["H"].width = 12
    ws.column_dimensions["I"].width = 12

    row = 1
    style_title(ws, row, len(headers), "Risk Catalog")

    row = 3
    style_header(ws, row, headers)

    row = 4
    for idx, risk in enumerate(risks):
        ws.cell(row=row, column=1, value=risk.get("id", f"R{idx+1:02d}"))
        ws.cell(row=row, column=2, value=risk.get("category", ""))
        ws.cell(row=row, column=3, value=risk.get("description", ""))
        ws.cell(row=row, column=4, value=risk.get("likelihood", 3))
        ws.cell(row=row, column=5, value=risk.get("impact", 3))

        # Risk score formula
        ws.cell(row=row, column=6, value=f"=D{row}*E{row}")

        ws.cell(row=row, column=7, value=risk.get("owner", ""))
        ws.cell(row=row, column=8, value=risk.get("status", "Open"))
        ws.cell(row=row, column=9, value=risk.get("target_date", ""))

        style_data_row(ws, row, len(headers), alt=(idx % 2 == 1))
        row += 1


def build_mitigation_plan(wb, risks):
    ws = wb.create_sheet("Mitigation Plan")

    headers = ["Risk ID", "Mitigation Action", "Owner", "Target Completion", "Status"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 12

    row = 1
    style_title(ws, row, len(headers), "Mitigation Plan")

    row = 3
    style_header(ws, row, headers)

    row = 4
    for idx, risk in enumerate(risks):
        ws.cell(row=row, column=1, value=risk.get("id", f"R{idx+1:02d}"))
        ws.cell(row=row, column=2, value=risk.get("mitigation", ""))
        ws.cell(row=row, column=3, value=risk.get("owner", ""))
        ws.cell(row=row, column=4, value=risk.get("target_date", ""))
        ws.cell(row=row, column=5, value="In Progress")

        style_data_row(ws, row, len(headers), alt=(idx % 2 == 1))
        row += 1


def build_contingency_plan(wb, risks):
    ws = wb.create_sheet("Contingency Plan")

    headers = ["Risk ID", "Contingency Action", "Trigger Criteria", "Decision Owner"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 35
    ws.column_dimensions["D"].width = 15

    row = 1
    style_title(ws, row, len(headers), "Contingency Plan")

    row = 3
    style_header(ws, row, headers)

    row = 4
    for idx, risk in enumerate(risks):
        ws.cell(row=row, column=1, value=risk.get("id", f"R{idx+1:02d}"))
        ws.cell(row=row, column=2, value=risk.get("contingency", ""))
        ws.cell(row=row, column=3, value=f"If {risk.get('id')} exceeds score threshold")
        ws.cell(row=row, column=4, value=risk.get("owner", ""))

        style_data_row(ws, row, len(headers), alt=(idx % 2 == 1))
        row += 1


def build_risk_trend(wb):
    ws = wb.create_sheet("Risk Trend")

    headers = ["Risk ID", "Reporting Period", "Risk Score", "Trend"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 12

    row = 1
    style_title(ws, row, len(headers), "Risk Trend Analysis")

    row = 3
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="(Track historical risk scores over reporting periods)")
    ws.merge_cells(f"A{row}:D{row}")


def build_escalation_log(wb):
    ws = wb.create_sheet("Escalation Log")

    headers = ["Date", "Risk ID", "Escalation Reason", "Escalated To", "Resolution"]
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 35
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 25

    row = 1
    style_title(ws, row, len(headers), "Escalation Log")

    row = 3
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="(Add escalation events as risks exceed thresholds)")
    ws.merge_cells(f"A{row}:E{row}")


def build_references(wb):
    ws = wb.create_sheet("References")
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title(ws, row, 2, "References")

    row = 3
    ws.cell(row=row, column=1, value="Standard").font = Font(bold=True)
    ws.cell(row=row, column=2, value="Source")

    row = 4
    references = [
        ("ISO 26262-2:2018", "Management of functional safety — Clause 7: Program risk management"),
        ("ISO 21434:2021", "Cybersecurity specification — Risk management approach"),
        ("Risk Category Definitions", "Permitted values: " + ", ".join(RISK_CATEGORIES)),
        ("Scoring Convention", "Risk Score = Likelihood (1-5) x Impact (1-5); 1-4 Low, 5-12 Medium, 15-25 High"),
    ]

    for ref_title, ref_source in references:
        ws.cell(row=row, column=1, value=ref_title)
        ws.cell(row=row, column=2, value=ref_source)
        row += 1


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_risk_register.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with open(input_path) as f:
        data = json.load(f)

    project = data.get("project", {})
    reporting_period = data.get("reporting_period", {"start": "", "end": ""})
    risks = data.get("risks", [])

    wb = Workbook()

    build_title_page(wb, project, reporting_period)
    build_document_control(wb)
    build_risk_register(wb, risks)
    build_mitigation_plan(wb, risks)
    build_contingency_plan(wb, risks)
    build_risk_trend(wb)
    build_escalation_log(wb)
    build_references(wb)

    wb.save(str(output_path))
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
