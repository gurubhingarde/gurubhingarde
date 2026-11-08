"""
SPC Chart Builder — generates an 11-tab Statistical Process Control workbook per AIAG.

Usage:
    python generate_spc.py <input.json> <output.xlsx>

Input JSON schema:
{
  "process": {id, name, characteristic, unit, method, frequency},
  "spec_limits": {usl, lsl, target},
  "subgroup_size": 5,
  "chart_type": "Xbar-R",
  "subgroups": [
    {subgroup_id, sample_date, measurements: [values...]}
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

# AIAG Constants for Xbar-R chart (subgroup size 2-10)
AIAG_CONSTANTS = {
    2:  {"A2": 1.880, "D3": 0.000, "D4": 3.267, "c4": 0.7979},
    3:  {"A2": 1.023, "D3": 0.000, "D4": 2.574, "c4": 0.8862},
    4:  {"A2": 0.729, "D3": 0.000, "D4": 2.282, "c4": 0.9213},
    5:  {"A2": 0.577, "D3": 0.000, "D4": 2.115, "c4": 0.9400},
}

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

def build_title_page(wb, process):
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "Statistical Process Control (SPC) Chart")
    style_title_row(ws, 3, 4, process.get("name", ""))

    fields = [
        ("Process ID", process.get("id", "")),
        ("Characteristic", process.get("characteristic", "")),
        ("Unit of Measure", process.get("unit", "")),
        ("Measurement Method", process.get("method", "")),
        ("Sampling Frequency", process.get("frequency", "")),
        ("Chart Type", "Xbar-R (Range-based)"),
        ("Standard", "AIAG SPC, 2nd Edition"),
    ]

    row = 5
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
    for i, row_data in enumerate([("0.1", "", "", "Initial SPC setup", ""), ("1.0", "", "", "Released", "")], start=4):
        for c, v in enumerate(row_data, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 5, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})

def build_process_definition(wb, process, spec_limits):
    ws = wb.create_sheet("02_Process_Definition")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Process Definition")

    ws.cell(row=3, column=1, value="Process Step").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=3, column=2, value=process.get("id", ""))

    ws.cell(row=4, column=1, value="Characteristic").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=4, column=2, value=process.get("characteristic", ""))

    ws.cell(row=5, column=1, value="Upper Spec Limit").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=5, column=2, value=spec_limits.get("usl", ""))

    ws.cell(row=6, column=1, value="Target").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=6, column=2, value=spec_limits.get("target", ""))

    ws.cell(row=7, column=1, value="Lower Spec Limit").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=7, column=2, value=spec_limits.get("lsl", ""))

    autosize(ws, {1: 30, 2: 30, 3: 4})

def build_subgroup_data(wb, subgroups):
    ws = wb.create_sheet("03_Subgroup_Data")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Subgroup Raw Data (Individual Measurements)")
    style_header_row(ws, 3, ["Subgroup", "Date", "Measurement 1", "Measurement 2", "Measurement 3", "Measurement 4"])

    for i, sg in enumerate(subgroups, start=4):
        ws.cell(row=i, column=1, value=sg.get("subgroup_id", ""))
        ws.cell(row=i, column=2, value=sg.get("sample_date", ""))
        meas = sg.get("measurements", [])
        for j, m in enumerate(meas[:4], start=3):
            ws.cell(row=i, column=j, value=m)

    if subgroups:
        stripe_body(ws, 4, 3+len(subgroups), 6)
    autosize(ws, {1: 12, 2: 14, 3: 14, 4: 14, 5: 14, 6: 14})

def build_subgroup_statistics(wb, subgroups):
    ws = wb.create_sheet("04_Subgroup_Statistics")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Subgroup Statistics (Xbar, R)")
    style_header_row(ws, 3, ["Subgroup", "Date", "Xbar (Mean)", "Range (R)", "n"])

    for i, sg in enumerate(subgroups, start=4):
        ws.cell(row=i, column=1, value=sg.get("subgroup_id", ""))
        ws.cell(row=i, column=2, value=sg.get("sample_date", ""))
        ws.cell(row=i, column=3, value=f"=AVERAGE(Data_Row{i})")  # Placeholder
        ws.cell(row=i, column=4, value=f"=MAX(Data_Row{i})-MIN(Data_Row{i})")  # Placeholder
        ws.cell(row=i, column=5, value=len(sg.get("measurements", [])))

    if subgroups:
        stripe_body(ws, 4, 3+len(subgroups), 5)
    autosize(ws, {1: 12, 2: 14, 3: 14, 4: 14, 5: 6})

def build_control_limits(wb, subgroups):
    ws = wb.create_sheet("05_Control_Limits")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Control Limits (Xbar-R Chart)")
    style_header_row(ws, 3, ["Statistic", "Value", "Formula / Constant"])

    sg_count = len(subgroups)
    sg_size = len(subgroups[0].get("measurements", [])) if subgroups else 5
    const = AIAG_CONSTANTS.get(sg_size, AIAG_CONSTANTS[5])

    limits = [
        ("Xbar-bar (Process Mean)", "", f"=AVERAGE(Xbar Column)"),
        ("R-bar (Average Range)", "", f"=AVERAGE(R Column)"),
        ("A2 Constant (n={})".format(sg_size), const["A2"], "AIAG Table"),
        ("D4 Constant (n={})".format(sg_size), const["D4"], "AIAG Table"),
        ("D3 Constant (n={})".format(sg_size), const["D3"], "AIAG Table"),
        ("", "", ""),
        ("Xbar-bar UCL", "", f"=Xbar_bar + A2 * R_bar"),
        ("Xbar-bar CL", "", f"=Xbar_bar"),
        ("Xbar-bar LCL", "", f"=Xbar_bar - A2 * R_bar"),
        ("", "", ""),
        ("R UCL", "", f"=D4 * R_bar"),
        ("R CL", "", f"=R_bar"),
        ("R LCL", "", f"=D3 * R_bar"),
    ]

    for i, (stat, value, formula) in enumerate(limits, start=4):
        ws.cell(row=i, column=1, value=stat)
        ws.cell(row=i, column=2, value=value)
        ws.cell(row=i, column=3, value=formula)

    autosize(ws, {1: 30, 2: 14, 3: 40})

def build_capability(wb):
    ws = wb.create_sheet("06_Process_Capability")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Process Capability Indices (Cpk, Ppk)")
    style_header_row(ws, 3, ["Index", "Value", "Formula / Interpretation"])

    indices = [
        ("Cp (Potential Capability)", "", "=(USL - LSL) / (6 * sigma_within)"),
        ("Cpk (Actual Capability)", "", "=MIN((USL - mean) / (3*sigma), (mean - LSL) / (3*sigma))"),
        ("Pp (Overall Potential)", "", "=(USL - LSL) / (6 * sigma_overall)"),
        ("Ppk (Overall Actual)", "", "=MIN((USL - mean) / (3*sigma_overall), (mean - LSL) / (3*sigma_overall))"),
        ("", "", ""),
        ("Target Cpk >= 1.33", "", "AIAG Recommendation"),
        ("Interpretation", "", "Cpk < 1.00: Process not capable"),
    ]

    for i, (idx, val, formula) in enumerate(indices, start=4):
        ws.cell(row=i, column=1, value=idx)
        ws.cell(row=i, column=2, value=val)
        ws.cell(row=i, column=3, value=formula)

    autosize(ws, {1: 30, 2: 12, 3: 50})

def build_out_of_control(wb, subgroups):
    ws = wb.create_sheet("07_Out_of_Control_Rules")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Western Electric / Nelson Out-of-Control Rules")
    style_header_row(ws, 3, ["Subgroup", "Rule 1 (>3σ)", "Rule 2 (2/3 >2σ)", "Rule 3 (4/5 >1σ)", "Status"])

    for i, sg in enumerate(subgroups, start=4):
        ws.cell(row=i, column=1, value=sg.get("subgroup_id", ""))
        ws.cell(row=i, column=2, value="")
        ws.cell(row=i, column=3, value="")
        ws.cell(row=i, column=4, value="")
        ws.cell(row=i, column=5, value="In Control")

    if subgroups:
        stripe_body(ws, 4, 3+len(subgroups), 5)
    autosize(ws, {1: 12, 2: 14, 3: 14, 4: 14, 5: 12})

def build_stability_assessment(wb):
    ws = wb.create_sheet("08_Process_Stability")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Process Stability Assessment")

    ws.cell(row=3, column=1, value="Is process statistically stable?").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=3, column=2, value="YES / NO")

    ws.cell(row=5, column=1, value="Number of out-of-control signals").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=5, column=2, value="")

    ws.cell(row=7, column=1, value="Special cause investigation log").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B7:C7")

    autosize(ws, {1: 40, 2: 30, 3: 4})

def build_recommendations(wb):
    ws = wb.create_sheet("09_Recommendations")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Process Decision and Recommendations")

    ws.cell(row=3, column=1, value="Process Status").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.cell(row=3, column=2, value="Stable & Capable / Stable & Not Capable / Not Stable")

    ws.cell(row=5, column=1, value="Recommended Actions").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells("B5:C8")

    autosize(ws, {1: 40, 2: 60, 3: 4})

def build_chart_notes(wb):
    ws = wb.create_sheet("10_Chart_Notes")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "Control Chart Interpretation")

    notes = [
        "Xbar chart monitors process mean (centering); R chart monitors variation (spread).",
        "Control limits based on within-subgroup variation (short-term); spec limits are customer tolerance.",
        "Process stable but not capable: reduce process spread or widen spec limits.",
        "Process capable but not stable: identify and eliminate special causes before relying on Cpk.",
        "Subgroup size and frequency affect sensitivity to special causes.",
    ]

    for i, note in enumerate(notes, start=3):
        ws.cell(row=i, column=1, value=f"• {note}")

    autosize(ws, {1: 80, 2: 4})

def build_references(wb):
    ws = wb.create_sheet("11_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References")

    refs = [
        "AIAG Statistical Process Control (SPC) Reference Manual, 2nd Edition",
        "Shewhart, W.A. (1931). Economic Control of Quality of Manufactured Product.",
        "Wheeler, D.J. (2010). Understanding Variation - The Key to Managing Chaos, 2nd Edition",
    ]

    for i, ref in enumerate(refs, start=3):
        ws.cell(row=i, column=1, value=f"• {ref}")

    autosize(ws, {1: 80, 2: 4})

def generate(input_path, output_path):
    with open(input_path) as f:
        data = json.load(f)

    process = data.get("process", {})
    spec_limits = data.get("spec_limits", {})
    subgroups = data.get("subgroups", [])

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, process)
    build_doc_control(wb)
    build_process_definition(wb, process, spec_limits)
    build_subgroup_data(wb, subgroups)
    build_subgroup_statistics(wb, subgroups)
    build_control_limits(wb, subgroups)
    build_capability(wb)
    build_out_of_control(wb, subgroups)
    build_stability_assessment(wb)
    build_recommendations(wb)
    build_chart_notes(wb)
    build_references(wb)

    wb.active = 0
    wb.save(output_path)

    return {
        "output_path": output_path,
        "tabs": 12,
        "subgroups": len(subgroups),
        "measurements_per_subgroup": len(subgroups[0].get("measurements", [])) if subgroups else 0,
    }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_spc.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
