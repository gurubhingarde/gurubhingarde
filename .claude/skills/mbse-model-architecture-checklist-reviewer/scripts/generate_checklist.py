"""MBSE Model Architecture Checklist Reviewer — orchestrator + xlsx writer."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from mbse_probe import ProbedMBSE, probe
from check_definitions import CHECKS, CheckDef, CheckResult
from dashboard import build_dashboard

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"
ORANGE_PARTIAL = "FFD966"
GREY = "D0CECE"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def style_title(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28

def build_title(wb, p):
    ws = wb.create_sheet("Title")
    style_title(ws, 2, 6, "MBSE Model Architecture Checklist")
    ws.cell(row=5, column=1, value="Review Date:").font = Font(bold=True)
    ws.cell(row=5, column=2, value=str(date.today()))
    ws.cell(row=6, column=1, value="Total Checks:").font = Font(bold=True)
    ws.cell(row=6, column=2, value=len(CHECKS))

def build_summary(wb, results):
    ws = wb.create_sheet("Summary", 1)
    build_dashboard(ws, {"CR": results})  # dashboard expects {tab: [(check, result)]}

def build_findings(wb, results):
    ws = wb.create_sheet("Detailed Findings")
    ws.cell(row=1, column=1, value="Check ID").font = Font(bold=True)
    ws.cell(row=1, column=2, value="Category").font = Font(bold=True)
    ws.cell(row=1, column=3, value="Requirement").font = Font(bold=True)
    ws.cell(row=1, column=4, value="Rating").font = Font(bold=True)
    ws.cell(row=1, column=5, value="Finding").font = Font(bold=True)
    row = 2
    for check_def, check_result in sorted(results, key=lambda x: x[0].id):
        ws.cell(row=row, column=1, value=check_def.id)
        ws.cell(row=row, column=2, value=check_def.tab)
        ws.cell(row=row, column=3, value=check_def.requirement)
        ws.cell(row=row, column=4, value=check_result.rating)
        ws.cell(row=row, column=5, value=check_result.finding)
        row += 1

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_checklist.py <mbse_model.xlsx> [output.xlsx]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.with_stem(input_file.stem + "_checklist")

    p = probe(str(input_file))
    results = [(check_def, check_def.func(p)) for check_def in CHECKS]

    wb = Workbook()
    wb.remove(wb.active)
    build_title(wb, p)
    build_summary(wb, results)
    build_findings(wb, results)
    wb.save(output_file)
    print(f"Checklist saved to {output_file}")

if __name__ == "__main__":
    main()
