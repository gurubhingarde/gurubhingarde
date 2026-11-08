"""
SW FMEA Builder - generates an ISO 26262-9 §8 + ISO 26262-6 §7-8 SW FMEA workbook from TSC + input JSON.

Usage:
    python generate_sw_fmea.py <tsc.xlsx> <input.json> <output.xlsx> [<sw_arch.xlsx>]

Produces 12 tabs:
  00_Title_Page, 01_Document_Control, 02_Assumptions, 03_SW_Component_Catalog,
  04_SW_Failure_Mode_Library, 05_FMEA_Worksheet, 06_Detection_Mechanisms_Summary,
  07_Propagation_Paths, 08_Coverage_Summary, 09_Open_Items, 10_Verification_Plan_Hooks, 11_References
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from tsc_reader import read_tsc, read_sw_arch


# ============================================================================
# Reference data — SW failure mode library per SWC type
# ============================================================================

SW_FAILURE_MODES = {
    "Application": [
        "Deadline miss (task timeout)",
        "Illegal state (FSM violation)",
        "Divide-by-zero / arithmetic exception",
        "NaN propagation (invalid float)",
        "Stack overflow / heap exhaustion",
        "Configuration corruption (persistent state)",
    ],
    "Service": [
        "Missed periodic execution",
        "Race condition (shared resource)",
        "Mutex deadlock / starvation",
        "Resource leak (memory / handles)",
    ],
    "Driver": [
        "Incorrect register write",
        "Missed interrupt / deferred ISR",
        "Stuck busy bit / timeout",
        "Transmit underrun / receive overrun",
    ],
    "Diagnostic": [
        "False positive (nuisance DTC)",
        "False negative (missed fault)",
        "Priority inversion (DTC ordering)",
        "Log corruption / rollover",
    ],
}

SEVERITY_SCORES = {"S0": 0, "S1": 1, "S2": 3, "S3": 9}
FREQUENCY_SCORES = {"Rare": 1, "Occasional": 3, "Frequent": 9}
COVERAGE_ADJUSTMENTS = {"Low": 1.0, "Medium": 0.4, "High": 0.1}

ASIL_TARGETS = {
    "A": 27,
    "B": 9,
    "C": 3,
    "D": 1,
    "QM": 999,
}


# ============================================================================
# Styling
# ============================================================================

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def style_title_row(ws, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header_row(ws, row: int, headers: list[str]) -> None:
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = header_font()
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 22


def style_body_cell(cell, is_alt_row: bool = False, is_formula: bool = False) -> None:
    cell.font = body_font()
    cell.border = BORDER_ALL
    if is_alt_row:
        cell.fill = PatternFill("solid", fgColor=ALT_ROW)
    if is_formula:
        cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)


# ============================================================================
# Tab generators
# ============================================================================


def make_title_page(wb, project: dict, linked_tsc: str, target_asil: str) -> None:
    ws = wb.create_sheet("00_Title_Page", 0)
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 60

    row = 1
    style_title_row(ws, row, 2, "SW FMEA (ISO 26262-9 §8 + ISO 26262-6 §7-8)")
    row += 2

    data = [
        ("Project Name", project.get("name", "TBD")),
        ("Document ID", project.get("doc_id", "TBD")),
        ("Revision", project.get("revision", "1.0")),
        ("Date", project.get("date", datetime.now().strftime("%Y-%m-%d"))),
        ("Author", project.get("author", "TBD")),
        ("Approver", project.get("approver", "TBD")),
        ("Target ASIL", target_asil),
        ("Linked TSC", linked_tsc),
    ]

    for label, value in data:
        cell_l = ws.cell(row=row, column=1, value=label)
        cell_l.font = Font(name=FONT_NAME, size=11, bold=True)
        cell_v = ws.cell(row=row, column=2, value=value)
        cell_v.alignment = Alignment(wrap_text=True)
        row += 1


def make_document_control(wb) -> None:
    ws = wb.create_sheet("01_Document_Control", 1)
    headers = ["Rev", "Date", "Author", "Change Description"]
    style_header_row(ws, 1, headers)

    for col_idx, h in enumerate(headers, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 20

    # Sample revision entry
    row = 2
    cell_r = ws.cell(row=row, column=1, value="1.0")
    cell_d = ws.cell(row=row, column=2, value=datetime.now().strftime("%Y-%m-%d"))
    cell_a = ws.cell(row=row, column=3, value="Initial")
    cell_c = ws.cell(row=row, column=4, value="Initial release")

    for col in range(1, 5):
        style_body_cell(ws.cell(row=row, column=col), is_alt_row=False)


def make_assumptions(wb, project: dict, methodology: str) -> None:
    ws = wb.create_sheet("02_Assumptions", 2)
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 70

    row = 1
    style_title_row(ws, row, 2, "Analysis Assumptions & Scope")
    row += 2

    assumptions = [
        ("Methodology", methodology),
        (
            "Analysis Type",
            "Qualitative (per ISO 26262-6 §7 — no quantitative metrics)",
        ),
        ("Failure Mode Library Source", "ISO 26262-6 Table 5-6 + SW FMEA Handbook"),
        ("SW Process Maturity", "Assumed per ASIL allocation"),
        (
            "Scope",
            "All SW components in linked TSC; safety-related and QM partitions in scope",
        ),
        ("Mitigation Strategy", "Detection + control flow analysis"),
        ("Propagation Analysis", "SWC → partition → vehicle effect"),
    ]

    for label, value in assumptions:
        cell_l = ws.cell(row=row, column=1, value=label)
        cell_l.font = Font(name=FONT_NAME, size=11, bold=True)
        cell_v = ws.cell(row=row, column=2, value=value)
        cell_v.alignment = Alignment(wrap_text=True)
        row += 1


def make_sw_component_catalog(wb, sw_components: list[dict]) -> None:
    ws = wb.create_sheet("03_SW_Component_Catalog", 3)
    headers = ["SWC_ID", "SWC Name", "Type", "Partition", "ASIL", "Language"]
    style_header_row(ws, 1, headers)

    for col_idx, h in enumerate(headers, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 18

    for row_idx, swc in enumerate(sw_components, start=2):
        for col_idx, header in enumerate(headers, start=1):
            key = header.lower().replace("_", "").replace(" ", "")
            if key == "swcid":
                key = "id"
            elif key == "swcname":
                key = "name"
            value = swc.get(key, "")
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            style_body_cell(cell, is_alt_row=(row_idx % 2 == 0))


def make_failure_mode_library(wb) -> None:
    ws = wb.create_sheet("04_SW_Failure_Mode_Library", 4)
    headers = ["SWC Type", "Failure Mode"]
    style_header_row(ws, 1, headers)

    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 50

    row = 2
    for swc_type, modes in SW_FAILURE_MODES.items():
        for mode_idx, mode in enumerate(modes):
            if mode_idx == 0:
                ws.cell(row=row, column=1, value=swc_type)
            ws.cell(row=row, column=2, value=mode)
            for col in range(1, 3):
                style_body_cell(ws.cell(row=row, column=col), is_alt_row=(row % 2 == 0))
            row += 1


def make_fmea_worksheet(
    wb, sw_components: list[dict], failure_mode_overrides: list[dict]
) -> int:
    """Create FMEA worksheet. Return number of rows."""
    ws = wb.create_sheet("05_FMEA_Worksheet", 5)

    headers = [
        "SWC_ID",
        "SWC Name",
        "Failure Mode",
        "Local Effect",
        "Subsystem Effect",
        "Vehicle Effect",
        "Parent FSR/SG",
        "Severity",
        "Frequency",
        "Pre-Mit Risk",
        "Detection Mechanism",
        "Detection Coverage",
        "Post-Mit Risk",
        "Residual Risk OK",
        "Mitigation",
        "Notes",
    ]
    style_header_row(ws, 1, headers)

    for col_idx, h in enumerate(headers, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 16

    row = 2
    data_rows = []

    for swc in sw_components:
        swc_type = swc.get("type", "Application")
        failure_modes = SW_FAILURE_MODES.get(swc_type, [])

        for fm in failure_modes:
            # Check for override
            override = None
            for ov in failure_mode_overrides:
                if ov.get("swc_id") == swc.get("id") and ov.get(
                    "failure_mode"
                ) == fm:
                    override = ov
                    break

            severity = override.get("severity", "S2") if override else "S2"
            frequency = override.get("frequency", "Occasional") if override else "Occasional"
            detection = (
                override.get("detection", "TBD") if override else "TBD"
            )
            coverage = override.get("coverage", "Low") if override else "Low"
            mitigation = override.get("mitigation", "") if override else ""

            # Calculate risk scores
            severity_val = SEVERITY_SCORES.get(severity, 3)
            frequency_val = FREQUENCY_SCORES.get(frequency, 3)
            pre_risk = severity_val * frequency_val
            coverage_adj = COVERAGE_ADJUSTMENTS.get(coverage, 1.0)
            post_risk = pre_risk * coverage_adj

            # Build actual row number for formulas (will be set during write loop)
            data_rows.append(
                {
                    "swc_id": swc.get("id"),
                    "swc_name": swc.get("name"),
                    "failure_mode": fm,
                    "local_effect": f"SWC {swc.get('id')} failure",
                    "subsystem_effect": f"Partition effect",
                    "vehicle_effect": "Vehicle behavior impact",
                    "parent_fsr": "TBD",
                    "severity": severity,
                    "frequency": frequency,
                    "pre_risk_value": pre_risk,
                    "detection": detection,
                    "coverage": coverage,
                    "post_risk_value": post_risk,
                    "residual_ok": "Y" if post_risk <= ASIL_TARGETS.get(swc.get("asil", "D"), 1) else "N",
                    "mitigation": mitigation,
                    "notes": "",
                }
            )

    for row_idx, data in enumerate(data_rows, start=2):
        ws.cell(row=row_idx, column=1, value=data["swc_id"])
        ws.cell(row=row_idx, column=2, value=data["swc_name"])
        ws.cell(row=row_idx, column=3, value=data["failure_mode"])
        ws.cell(row=row_idx, column=4, value=data["local_effect"])
        ws.cell(row=row_idx, column=5, value=data["subsystem_effect"])
        ws.cell(row=row_idx, column=6, value=data["vehicle_effect"])
        ws.cell(row=row_idx, column=7, value=data["parent_fsr"])
        ws.cell(row=row_idx, column=8, value=data["severity"])
        ws.cell(row=row_idx, column=9, value=data["frequency"])

        # Pre-risk (calculated value, analyst can edit severity/frequency to recalculate)
        cell_pre = ws.cell(row=row_idx, column=10, value=data["pre_risk_value"])
        style_body_cell(cell_pre, is_alt_row=(row_idx % 2 == 0), is_formula=True)

        ws.cell(row=row_idx, column=11, value=data["detection"])
        ws.cell(row=row_idx, column=12, value=data["coverage"])

        # Post-risk (calculated value, analyst can edit coverage to recalculate)
        cell_post = ws.cell(row=row_idx, column=13, value=data["post_risk_value"])
        style_body_cell(cell_post, is_alt_row=(row_idx % 2 == 0), is_formula=True)

        ws.cell(row=row_idx, column=14, value=data["residual_ok"])
        ws.cell(row=row_idx, column=15, value=data["mitigation"])
        ws.cell(row=row_idx, column=16, value=data["notes"])

        # Apply styling to all cells
        for col_idx in range(1, 17):
            style_body_cell(
                ws.cell(row=row_idx, column=col_idx), is_alt_row=(row_idx % 2 == 0)
            )

    return len(data_rows)


def make_detection_mechanisms_summary(wb, fmea_rows: int) -> None:
    ws = wb.create_sheet("06_Detection_Mechanisms_Summary", 6)
    headers = [
        "Detection Mechanism",
        "Failure Modes Covered",
        "Avg Coverage",
        "Maturity",
    ]
    style_header_row(ws, 1, headers)

    for col_idx, h in enumerate(headers, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 22

    # Placeholder data
    mechanisms = [
        ("Window watchdog", "3-5", "High", "Proven"),
        ("Assertion / code review", "2-3", "Medium", "Design-dependent"),
        ("Range checking", "4-6", "Medium", "Proven"),
        ("Control flow analysis", "2", "Low-Medium", "Analysis-dependent"),
        ("Monitor / sentinel", "3-4", "Medium-High", "Proven"),
    ]

    for row_idx, (mech, count, coverage, maturity) in enumerate(mechanisms, start=2):
        ws.cell(row=row_idx, column=1, value=mech)
        ws.cell(row=row_idx, column=2, value=count)
        ws.cell(row=row_idx, column=3, value=coverage)
        ws.cell(row=row_idx, column=4, value=maturity)

        for col in range(1, 5):
            style_body_cell(ws.cell(row=row_idx, column=col), is_alt_row=(row_idx % 2 == 0))


def make_propagation_paths(wb, fmea_rows: int) -> None:
    ws = wb.create_sheet("07_Propagation_Paths", 7)
    headers = ["SWC_ID", "Failure Mode", "Propagation Chain", "Severity"]
    style_header_row(ws, 1, headers)

    for col_idx, h in enumerate(headers, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 28

    # Placeholder
    row = 2
    sample = ("SWC01", "Deadline miss", "SWC01 → CAN output → actuator → vehicle", "S3")
    ws.cell(row=row, column=1, value=sample[0])
    ws.cell(row=row, column=2, value=sample[1])
    ws.cell(row=row, column=3, value=sample[2])
    ws.cell(row=row, column=4, value=sample[3])
    for col in range(1, 5):
        style_body_cell(ws.cell(row=row, column=col))


def make_coverage_summary(wb) -> None:
    ws = wb.create_sheet("08_Coverage_Summary", 8)
    headers = ["Safety Goal / FSR", "Failure Modes", "Detected", "Total Risk", "Status"]
    style_header_row(ws, 1, headers)

    for col_idx, h in enumerate(headers, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 22

    # Placeholder
    row = 2
    sample = ("SG_01", "5", "4", "Medium", "Acceptable with mitigations")
    ws.cell(row=row, column=1, value=sample[0])
    ws.cell(row=row, column=2, value=sample[1])
    ws.cell(row=row, column=3, value=sample[2])
    ws.cell(row=row, column=4, value=sample[3])
    ws.cell(row=row, column=5, value=sample[4])
    for col in range(1, 6):
        style_body_cell(ws.cell(row=row, column=col))


def make_open_items(wb, fmea_rows: int) -> None:
    ws = wb.create_sheet("09_Open_Items", 9)
    headers = ["SWC_ID", "Failure Mode", "Issue", "Owner", "Due Date"]
    style_header_row(ws, 1, headers)

    for col_idx, h in enumerate(headers, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 20

    ws.cell(row=2, column=1, value="TBD")
    ws.cell(
        row=2,
        column=3,
        value="Review and update failure mode mitigations per ASIL target",
    )


def make_verification_plan_hooks(wb, fmea_rows: int) -> None:
    ws = wb.create_sheet("10_Verification_Plan_Hooks", 10)
    headers = [
        "Failure Mode",
        "Test Method (Unit/Integration/System)",
        "Expected Result",
        "Owner",
    ]
    style_header_row(ws, 1, headers)

    for col_idx, h in enumerate(headers, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = 26

    # Placeholder
    row = 2
    sample = (
        "Deadline miss",
        "Unit test: inject task delay",
        "Watchdog fires; safe state",
        "SW team",
    )
    for col_idx, val in enumerate(sample, start=1):
        ws.cell(row=row, column=col_idx, value=val)
        style_body_cell(ws.cell(row=row, column=col_idx))


def make_references(wb) -> None:
    ws = wb.create_sheet("11_References", 11)
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title_row(ws, row, 1, "References & Methodology")
    row += 2

    refs = [
        "ISO 26262-9:2018 Functional safety - Automotive - Part 9: ASIL-oriented and safety-oriented analyses",
        "ISO 26262-6:2018 Functional safety - Automotive - Part 6: Product development at the software level",
        "ISO 26262-6 Table 5: SW product metrics (control flow coverage, statement coverage, etc.)",
        "ISO 26262-6 Table 6: SW architecture metrics (partitioning isolation, interface integrity)",
        "AIAG Automotive Safety Handbook - Chapter 5: Software FMEA",
        "Linked TSC: See Title Page",
    ]

    for ref in refs:
        cell = ws.cell(row=row, column=1, value=ref)
        cell.alignment = Alignment(wrap_text=True)
        row += 1


# ============================================================================
# Main generator
# ============================================================================


def main():
    if len(sys.argv) < 4:
        print(
            "Usage: python generate_sw_fmea.py <tsc.xlsx> <input.json> <output.xlsx> [<sw_arch.xlsx>]"
        )
        sys.exit(1)

    tsc_path = sys.argv[1]
    input_json_path = sys.argv[2]
    output_path = sys.argv[3]
    sw_arch_path = sys.argv[4] if len(sys.argv) > 4 else None

    # Load input JSON
    with open(input_json_path, "r") as f:
        input_data = json.load(f)

    project = input_data.get("project", {})
    target_asil = input_data.get("target_asil", project.get("target_asil", "D"))
    linked_tsc = input_data.get("linked_tsc", tsc_path)

    # Read TSC
    tsc_data = read_tsc(tsc_path)

    # Merge SW components from TSC or SW arch
    sw_components = input_data.get("swcs_override", None)
    if not sw_components:
        sw_components = tsc_data.get("sw_partitions", [])
        if sw_arch_path:
            sw_arch_data = read_sw_arch(sw_arch_path)
            sw_components = sw_arch_data.get("sw_components", sw_components)

    # Populate with default structure if empty
    if not sw_components:
        sw_components = [
            {"id": "SWC01", "name": "Application SWC", "type": "Application", "asil": target_asil, "partition_id": "P01", "language": "C"},
            {"id": "SWC02", "name": "Service SWC", "type": "Service", "asil": target_asil, "partition_id": "P01", "language": "C"},
        ]

    failure_mode_overrides = input_data.get("failure_mode_overrides", [])

    # Create workbook
    wb = Workbook()
    wb.remove(wb.active)

    # Generate tabs
    make_title_page(wb, project, linked_tsc, target_asil)
    make_document_control(wb)
    make_assumptions(wb, project, "Qualitative (ISO 26262-6 §7)")
    make_sw_component_catalog(wb, sw_components)
    make_failure_mode_library(wb)
    fmea_rows = make_fmea_worksheet(wb, sw_components, failure_mode_overrides)
    make_detection_mechanisms_summary(wb, fmea_rows)
    make_propagation_paths(wb, fmea_rows)
    make_coverage_summary(wb)
    make_open_items(wb, fmea_rows)
    make_verification_plan_hooks(wb, fmea_rows)
    make_references(wb)

    wb.save(output_path)
    print(f"SW FMEA workbook generated: {output_path}")
    print(f"  - 12 tabs created")
    print(f"  - {fmea_rows} FMEA worksheet rows")


if __name__ == "__main__":
    main()
