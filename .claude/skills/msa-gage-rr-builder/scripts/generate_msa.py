"""
MSA Gauge R&R Builder — generates a 12-tab audit-ready workbook per AIAG MSA 4th edition.

Usage:
    python generate_msa.py <input.json> <output.xlsx>

Input JSON schema:
{
  "gage": {id, characteristic, make, model, calibration_date, resolution, range, units, operators: [...]},
  "study_design": {num_parts, num_operators, num_trials, randomization_scheme},
  "raw_data": [
    {part_id, operator, trial, measurement_value}
  ],
  "attribute_study": [
    {part_id, reference_standard, operator_1_rating, operator_2_rating, ...}
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
RED_BAD = "F8CBAD"

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

def build_title_page(wb, gage):
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "Measurement System Analysis (Gauge R&R)")
    style_title_row(ws, 3, 4, f"Characteristic: {gage.get('characteristic', '')}")

    fields = [
        ("Gage ID", gage.get("id", "")),
        ("Make/Model", f"{gage.get('make', '')} {gage.get('model', '')}"),
        ("Calibration Date", gage.get("calibration_date", "")),
        ("Resolution", gage.get("resolution", "")),
        ("Range", gage.get("range", "")),
        ("Units", gage.get("units", "")),
        ("Study Type", "Variable Gauge R&R (ANOVA Method)"),
        ("Standard", "AIAG Measurement Systems Analysis, 4th Edition"),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        row += 1
    autosize(ws, {1: 4, 2: 22, 3: 60, 4: 4})

def build_doc_control(wb):
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 3, ["Revision", "Date", "Author", "Change", "Approver"])
    for i, row_data in enumerate([("0.1", "", "", "Initial GRR study", ""), ("1.0", "", "", "Released", "")], start=4):
        for c, v in enumerate(row_data, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 5, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})

def build_gage_info(wb, gage):
    ws = wb.create_sheet("02_Gage_Information")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Gage Information")
    style_header_row(ws, 3, ["Parameter", "Value", "Notes"])

    info = [
        ("Gage ID", gage.get("id", "")),
        ("Make", gage.get("make", "")),
        ("Model", gage.get("model", "")),
        ("Calibration Date", gage.get("calibration_date", "")),
        ("Resolution", gage.get("resolution", "")),
        ("Range", gage.get("range", "")),
        ("Units", gage.get("units", "")),
    ]

    for i, (param, value) in enumerate(info, start=4):
        ws.cell(row=i, column=1, value=param)
        ws.cell(row=i, column=2, value=value)
        ws.cell(row=i, column=3, value="")

    stripe_body(ws, 4, 3+len(info), 3)
    autosize(ws, {1: 22, 2: 30, 3: 40})

def build_study_design(wb, design):
    ws = wb.create_sheet("03_Study_Design")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Study Design Parameters")

    ws.cell(row=3, column=1, value="Number of Parts").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=3, column=2, value=design.get("num_parts", 10))

    ws.cell(row=4, column=1, value="Number of Operators").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=4, column=2, value=design.get("num_operators", 3))

    ws.cell(row=5, column=1, value="Number of Trials per Part").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=5, column=2, value=design.get("num_trials", 3))

    ws.cell(row=6, column=1, value="Total Measurements").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=6, column=2, value=f"=B3*B4*B5")

    autosize(ws, {1: 30, 2: 12, 3: 4})

def build_raw_data(wb, raw_data):
    ws = wb.create_sheet("04_Raw_Data_Variable")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Raw Data - Variable Gauge R&R")
    style_header_row(ws, 3, ["Part ID", "Operator", "Trial", "Measurement", "Notes"])

    for i, row_data in enumerate(raw_data, start=4):
        ws.cell(row=i, column=1, value=row_data.get("part_id", ""))
        ws.cell(row=i, column=2, value=row_data.get("operator", ""))
        ws.cell(row=i, column=3, value=row_data.get("trial", ""))
        ws.cell(row=i, column=4, value=row_data.get("measurement_value", ""))
        ws.cell(row=i, column=5, value="")

    if raw_data:
        stripe_body(ws, 4, 3+len(raw_data), 5)
    autosize(ws, {1: 12, 2: 14, 3: 10, 4: 14, 5: 30})

def build_anova_calculations(wb):
    ws = wb.create_sheet("05_Crossed_ANOVA_Calculations")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "ANOVA Analysis (Operator × Part)")
    style_header_row(ws, 3, ["Parameter", "Value", "Formula/Notes"])

    params = [
        ("Repeatability (EV - Equipment Variation)", "", "=STDEV(Range) * 5.15 / 1.128"),
        ("Reproducibility (AV - Appraiser Variation)", "", "=SQRT(AV_calc) * 5.15"),
        ("Total Gauge R&R", "", "=SQRT(EV^2 + AV^2)"),
        ("Part-to-Part Variation", "", "=STDEV(Part_means) * 5.15"),
        ("Total Variation", "", "=SQRT((R&R)^2 + (P2P)^2)"),
        ("Gauge R&R %", "", "=100 * (R&R / Total)"),
    ]

    for i, (param, _, formula) in enumerate(params, start=4):
        ws.cell(row=i, column=1, value=param)
        ws.cell(row=i, column=2, value="")
        ws.cell(row=i, column=3, value=formula)

    stripe_body(ws, 4, 3+len(params), 3)
    autosize(ws, {1: 36, 2: 12, 3: 40})

def build_results_summary(wb):
    ws = wb.create_sheet("06_Variable_Results_Summary")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "R&R Results Summary and Acceptance")

    ws.cell(row=3, column=1, value="GRR %").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row=3, column=2, value="")

    ws.cell(row=4, column=1, value="Number of Distinct Categories (ndc)").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row=4, column=2, value="")

    ws.cell(row=6, column=1, value="Acceptance Criteria (AIAG)").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    style_header_row(ws, 7, ["Criterion", "Result", "Status"])

    criteria = [
        ("GRR % < 10%", "", ""),
        ("GRR % < 30%", "", ""),
        ("ndc >= 5", "", ""),
    ]

    for i, (crit, result, _) in enumerate(criteria, start=8):
        ws.cell(row=i, column=1, value=crit)
        ws.cell(row=i, column=2, value=result)
        ws.cell(row=i, column=3, value="")

    autosize(ws, {1: 40, 2: 12, 3: 12, 4: 4})

def build_attribute_agreement(wb, attribute_data):
    ws = wb.create_sheet("07_Attribute_Agreement")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Attribute Agreement Analysis (Cohen Kappa)")
    style_header_row(ws, 3, ["Part", "Reference", "Op1", "Op2", "Op3"])

    for i, row_data in enumerate(attribute_data, start=4):
        ws.cell(row=i, column=1, value=row_data.get("part_id", ""))
        ws.cell(row=i, column=2, value=row_data.get("reference_standard", ""))
        ws.cell(row=i, column=3, value=row_data.get("operator_1", ""))
        ws.cell(row=i, column=4, value=row_data.get("operator_2", ""))
        ws.cell(row=i, column=5, value=row_data.get("operator_3", ""))

    if attribute_data:
        stripe_body(ws, 4, 3+len(attribute_data), 5)
    autosize(ws, {1: 12, 2: 14, 3: 10, 4: 10, 5: 10})

def build_bias_linearity(wb):
    ws = wb.create_sheet("08_Bias_Linearity")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Bias and Linearity Study")
    style_header_row(ws, 3, ["Reference Value", "Measured Value", "Bias (Error)", "% Linearity"])

    autosize(ws, {1: 16, 2: 16, 3: 14, 4: 14})

def build_acceptance_decision(wb):
    ws = wb.create_sheet("09_Acceptance_Decision")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Acceptance Decision and Recommendations")

    ws.cell(row=3, column=1, value="Overall Gage Status").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=3, column=2, value="ACCEPT / REJECT / CONDITIONAL")

    ws.cell(row=5, column=1, value="Rationale").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B5:C5")

    ws.cell(row=8, column=1, value="Recommendations").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B8:C8")

    autosize(ws, {1: 30, 2: 60, 3: 4})

def build_action_items(wb):
    ws = wb.create_sheet("10_Action_Items")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Action Items")
    style_header_row(ws, 3, ["Action", "Owner", "Due Date", "Priority", "Status"])

    autosize(ws, {1: 35, 2: 15, 3: 14, 4: 12, 5: 10})

def build_references(wb):
    ws = wb.create_sheet("11_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References")

    refs = [
        "AIAG Measurement Systems Analysis (MSA), 4th Edition",
        "ISO 5725 - Accuracy (trueness and precision) of measurement methods and results",
        "IATF 16949 Process Approach Section",
    ]

    for i, ref in enumerate(refs, start=3):
        ws.cell(row=i, column=1, value=f"• {ref}")
    autosize(ws, {1: 80, 2: 4})

def generate(input_path, output_path):
    with open(input_path) as f:
        data = json.load(f)

    gage = data.get("gage", {})
    design = data.get("study_design", {})
    raw_data = data.get("raw_data", [])
    attribute_data = data.get("attribute_study", [])

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, gage)
    build_doc_control(wb)
    build_gage_info(wb, gage)
    build_study_design(wb, design)
    build_raw_data(wb, raw_data)
    build_anova_calculations(wb)
    build_results_summary(wb)
    build_attribute_agreement(wb, attribute_data)
    build_bias_linearity(wb)
    build_acceptance_decision(wb)
    build_action_items(wb)
    build_references(wb)

    wb.active = 0
    wb.save(output_path)

    return {
        "output_path": output_path,
        "tabs": 12,
        "raw_data_points": len(raw_data),
        "attribute_samples": len(attribute_data),
    }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_msa.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
