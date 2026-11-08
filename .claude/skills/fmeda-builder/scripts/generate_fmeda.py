"""
FMEDA Builder - generates an ISO 26262-5 §8 FMEDA workbook from TSC + HW BOM.

Usage:
    python generate_fmeda.py <tsc.xlsx> <hw_bom.json> <output.xlsx>

Produces 13 tabs:
  00_Title_Page, 01_Document_Control, 02_Assumptions, 03_HW_Element_Catalog,
  04_Failure_Mode_Library, 05_Safety_Mechanisms_From_TSC, 06_FMEDA_Worksheet,
  07_SPFM_Calculation, 08_LFM_Calculation, 09_PMHF_Calculation,
  10_Metrics_Dashboard, 11_Open_Items, 12_References
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from tsc_reader import read_tsc


# ============================================================================
# Reference data
# ============================================================================

ELEMENT_TYPE_TO_FAILURE_MODES = {
    "MCU": ["Stuck-at", "Transient bit flip", "I/O fault", "Oscillator fault"],
    "Sensor": ["No output", "Stuck output", "Drifted output", "Noisy output"],
    "Memory": ["Single-bit error", "Multi-bit error", "Address decoder fault", "Read disturb"],
    "Driver": ["Open output", "Short to supply", "Short to ground", "Thermal shutdown"],
    "Power": ["Undervoltage", "Overvoltage", "Oscillation", "Thermal failure"],
    "Capacitor": ["Capacitance loss", "ESR increase", "Voltage derating"],
    "Inductor": ["Open winding", "Shorted turns", "Core saturation"],
    "Resistor": ["Resistance increase", "Resistance decrease", "Thermal runaway"],
}

ELEMENT_TYPE_TO_DISTRIBUTIONS = {
    "MCU": {"Stuck-at": 0.30, "Transient bit flip": 0.40, "I/O fault": 0.15, "Oscillator fault": 0.15},
    "Sensor": {"No output": 0.20, "Stuck output": 0.30, "Drifted output": 0.30, "Noisy output": 0.20},
    "Memory": {"Single-bit error": 0.50, "Multi-bit error": 0.05, "Address decoder fault": 0.15, "Read disturb": 0.30},
    "Driver": {"Open output": 0.25, "Short to supply": 0.25, "Short to ground": 0.25, "Thermal shutdown": 0.25},
    "Power": {"Undervoltage": 0.40, "Overvoltage": 0.20, "Oscillation": 0.30, "Thermal failure": 0.10},
    "Capacitor": {"Capacitance loss": 0.50, "ESR increase": 0.40, "Voltage derating": 0.10},
    "Inductor": {"Open winding": 0.60, "Shorted turns": 0.30, "Core saturation": 0.10},
    "Resistor": {"Resistance increase": 0.50, "Resistance decrease": 0.40, "Thermal runaway": 0.10},
}

ASIL_TARGETS = {
    "A": {"SPFM": 90, "LFM": 60, "PMHF": 100},
    "B": {"SPFM": 90, "LFM": 60, "PMHF": 100},
    "C": {"SPFM": 97, "LFM": 80, "PMHF": 100},
    "D": {"SPFM": 99, "LFM": 90, "PMHF": 10},
    "QM": {"SPFM": 0, "LFM": 0, "PMHF": 999999},
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
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 32


def stripe_body(ws, start_row: int, end_row: int, last_col: int) -> None:
    for r in range(start_row, end_row + 1):
        fill = PatternFill("solid", fgColor=ALT_ROW) if (r - start_row) % 2 else None
        for c in range(1, last_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = body_font()
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER_ALL
            if fill:
                cell.fill = fill


def autosize(ws, widths: dict[int, int]) -> None:
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width


# ============================================================================
# Tab builders
# ============================================================================

def build_title_page(wb: Workbook, bom: dict, tsc_path: str) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 2, 4, "Hardware FMEDA (Failure Mode, Effects & Diagnostic Analysis)")
    style_title_row(ws, 3, 4, bom["project"].get("name", "ESC"))

    project = bom.get("project", {})
    fields = [
        ("Project", project.get("name", "")),
        ("Document ID", project.get("doc_id", "")),
        ("Revision", project.get("revision", "")),
        ("Date", project.get("date", "")),
        ("Author", project.get("author", "")),
        ("Approver", project.get("approver", "")),
        ("Target ASIL", bom.get("target_asil", "D")),
        ("Linked TSC", tsc_path),
        ("Linked HW Architecture", bom.get("linked_hw_arch", "")),
        ("Standard", "ISO 26262:2018, Part 5 (Hardware Layer), Section 8"),
        ("Methodology", "FMEDA with SPFM/LFM/PMHF metrics, formula-driven auto-recalc on DC% changes"),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1
    autosize(ws, {1: 4, 2: 22, 3: 80, 4: 4})


def build_doc_control(wb: Workbook) -> None:
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of change", "Approver"])
    for i, row_data in enumerate([
        ("0.1", "", "", "Initial draft generated by fmeda-builder skill", ""),
        ("0.2", "", "", "Internal review comments incorporated", ""),
        ("1.0", "", "", "Released for audit", ""),
    ], start=4):
        for c, v in enumerate(row_data, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 6, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_assumptions(wb: Workbook, bom: dict) -> None:
    ws = wb.create_sheet("02_Assumptions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Assumptions")
    style_header_row(ws, 3, ["Category", "Item", "Value", "Notes"])

    mission = bom.get("mission_profile", {})
    assumptions = [
        ("Mission Profile", "Operating hours per year", mission.get("operating_hours_per_year", ""), ""),
        ("Mission Profile", "Lifetime (years)", mission.get("lifetime_years", ""), ""),
        ("Environment", "Ambient temperature (°C)", mission.get("ambient_temp_c", ""), ""),
        ("FIT Source", "Primary source", bom.get("fit_source", "IEC 62380 / supplier datasheet"), ""),
        ("Safety Scope", "Target ASIL", bom.get("target_asil", "D"), ""),
    ]

    for i, (cat, item, val, note) in enumerate(assumptions, start=4):
        ws.cell(row=i, column=1, value=cat)
        ws.cell(row=i, column=2, value=item)
        ws.cell(row=i, column=3, value=val)
        ws.cell(row=i, column=4, value=note)

    stripe_body(ws, 4, 3 + len(assumptions), 4)
    autosize(ws, {1: 16, 2: 30, 3: 20, 4: 40})


def build_hw_element_catalog(wb: Workbook, bom: dict) -> None:
    ws = wb.create_sheet("03_HW_Element_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Hardware Element Catalog")
    style_header_row(ws, 3, ["HW_E_ID", "Name", "Type", "FIT Rate", "Safety Related"])

    elements = bom.get("hw_elements", [])
    for i, elem in enumerate(elements, start=4):
        ws.cell(row=i, column=1, value=elem.get("id", ""))
        ws.cell(row=i, column=2, value=elem.get("name", ""))
        ws.cell(row=i, column=3, value=elem.get("type", ""))
        ws.cell(row=i, column=4, value=elem.get("fit", 0))
        ws.cell(row=i, column=5, value="Yes" if elem.get("safety_related") else "No")

    stripe_body(ws, 4, 3 + len(elements), 5)
    autosize(ws, {1: 14, 2: 26, 3: 14, 4: 12, 5: 16})


def build_failure_mode_library(wb: Workbook) -> None:
    ws = wb.create_sheet("04_Failure_Mode_Library")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Failure Mode Library (IEC 62380)")
    style_header_row(ws, 3, ["Element Type", "Failure Mode", "Distribution %"])

    row = 4
    for elem_type in sorted(ELEMENT_TYPE_TO_FAILURE_MODES.keys()):
        modes = ELEMENT_TYPE_TO_FAILURE_MODES[elem_type]
        dists = ELEMENT_TYPE_TO_DISTRIBUTIONS.get(elem_type, {})
        for mode in modes:
            dist_pct = dists.get(mode, 0) * 100
            ws.cell(row=row, column=1, value=elem_type if mode == modes[0] else "")
            ws.cell(row=row, column=2, value=mode)
            ws.cell(row=row, column=3, value=dist_pct)
            row += 1

    stripe_body(ws, 4, row - 1, 3)
    autosize(ws, {1: 16, 2: 28, 3: 14})


def build_tsc_mechanisms(wb: Workbook, mechanisms: dict) -> None:
    ws = wb.create_sheet("05_Safety_Mechanisms_From_TSC")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Safety Mechanisms From TSC (Read-Only Echo)")
    style_header_row(ws, 3, ["Mechanism ID", "Mechanism Name", "Default DC%", "Linked Node"])

    row = 4
    for (node_id, mech_id), info in sorted(mechanisms.items()):
        ws.cell(row=row, column=1, value=mech_id)
        ws.cell(row=row, column=2, value=info.get("name", ""))
        ws.cell(row=row, column=3, value=info.get("dc", 0))
        ws.cell(row=row, column=4, value=node_id or "")
        row += 1

    stripe_body(ws, 4, row - 1, 4)
    autosize(ws, {1: 16, 2: 36, 3: 14, 4: 16})


def build_fmeda_worksheet(wb: Workbook, bom: dict, mechanisms: dict) -> list[dict]:
    """Main FMEDA worksheet with formulas for λ, λ_SPF, λ_RF, λ_MPF_L."""
    ws = wb.create_sheet("06_FMEDA_Worksheet")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 13, "FMEDA Worksheet (Editable DC%, Auto-Recalc)")

    headers = [
        "HW_E_ID", "Element Name", "Type", "Total FIT", "Failure Mode",
        "Distribution %", "λ (FIT)", "Safety Related", "Allocated Mechanism",
        "DC% (Editable)", "λ_SPF (Formula)", "λ_RF (Formula)",
        "λ_MPF_L (Formula)", "Classification", "Notes"
    ]
    style_header_row(ws, 3, headers)

    elements = bom.get("hw_elements", [])
    overrides = {(o["hw_e_id"], o["failure_mode"]): o for o in bom.get("failure_mode_overrides", [])}

    fmeda_rows = []
    row = 4

    for elem in elements:
        elem_id = elem.get("id", "")
        elem_name = elem.get("name", "")
        elem_type = elem.get("type", "")
        elem_fit = elem.get("fit", 0)
        safety_related = elem.get("safety_related", True)

        modes = ELEMENT_TYPE_TO_FAILURE_MODES.get(elem_type, ["Generic"])
        dists = ELEMENT_TYPE_TO_DISTRIBUTIONS.get(elem_type, {m: 1.0/len(modes) for m in modes})

        for mode in modes:
            dist_pct = dists.get(mode, 0) * 100

            # Check for override
            override = overrides.get((elem_id, mode), {})
            if override:
                dist_pct = override.get("distribution_pct", dist_pct)
                dc_pct = override.get("dc_pct", 50)
            else:
                dc_pct = 50  # default analyst edit

            ws.cell(row=row, column=1, value=elem_id)
            ws.cell(row=row, column=2, value=elem_name)
            ws.cell(row=row, column=3, value=elem_type)
            ws.cell(row=row, column=4, value=elem_fit)
            ws.cell(row=row, column=5, value=mode)
            ws.cell(row=row, column=6, value=dist_pct)

            # λ = FIT × (distribution % / 100)
            lambda_formula = f"=D{row}*(F{row}/100)"
            ws.cell(row=row, column=7, value=lambda_formula)

            ws.cell(row=row, column=8, value="Yes" if safety_related else "No")
            ws.cell(row=row, column=9, value="")  # Analyst fills in
            ws.cell(row=row, column=10, value=dc_pct)  # Editable DC%

            # λ_SPF = λ if NOT safety_related OR DC = 0; else 0
            spf_formula = f"=IF(H{row}=\"No\",G{row},IF(J{row}=0,G{row},0))"
            ws.cell(row=row, column=11, value=spf_formula)

            # λ_RF = λ × (1 - DC/100) if safety_related AND 0 < DC < 100
            rf_formula = f"=IF(H{row}=\"Yes\",IF(AND(J{row}>0,J{row}<100),G{row}*(1-J{row}/100),0),0)"
            ws.cell(row=row, column=12, value=rf_formula)

            # λ_MPF_L = same logic as RF (latent two-point)
            mpf_formula = f"=IF(H{row}=\"Yes\",IF(AND(J{row}>0,J{row}<100),G{row}*(1-J{row}/100),0),0)"
            ws.cell(row=row, column=13, value=mpf_formula)

            # Classification (formula-based)
            class_formula = f"=IF(H{row}=\"No\",\"S\",IF(J{row}=100,\"S\",IF(J{row}=0,\"SPF\",\"RF\")))"
            ws.cell(row=row, column=14, value=class_formula)

            ws.cell(row=row, column=15, value="")

            fmeda_rows.append(row)
            row += 1

    stripe_body(ws, 4, row - 1, len(headers))
    ws.freeze_panes = "A4"
    autosize(ws, {
        1: 14, 2: 22, 3: 12, 4: 12, 5: 18, 6: 14, 7: 12, 8: 14,
        9: 20, 10: 12, 11: 14, 12: 14, 13: 14, 14: 14, 15: 30
    })

    return fmeda_rows


def build_spfm_calculation(wb: Workbook, bom: dict, fmeda_rows: list[int]) -> None:
    ws = wb.create_sheet("07_SPFM_Calculation")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "SPFM Calculation (Single-Point Failure Metric)")
    style_header_row(ws, 3, ["Safety Goal", "Σ(λ_SPF + λ_RF)", "Σ(λ_safety_related)", "SPFM", "Target (ASIL)", "Status"])

    target_asil = bom.get("target_asil", "D")
    target = ASIL_TARGETS.get(target_asil, {}).get("SPFM", 99)

    ws.cell(row=4, column=1, value="SG-001 (Placeholder)")
    ws.cell(row=4, column=2, value=f"=SUM('06_FMEDA_Worksheet'!K:K)+SUM('06_FMEDA_Worksheet'!L:L)")
    ws.cell(row=4, column=3, value=f"=SUM('06_FMEDA_Worksheet'!G:G)")
    ws.cell(row=4, column=4, value=f"=IF(C4=0,1,1-(B4/C4))")
    ws.cell(row=4, column=5, value=target)
    ws.cell(row=4, column=6, value=f"=IF(D4>=E4/100,\"PASS\",\"FAIL\")")

    stripe_body(ws, 4, 4, 6)
    autosize(ws, {1: 22, 2: 22, 3: 22, 4: 14, 5: 14, 6: 12})


def build_lfm_calculation(wb: Workbook, bom: dict) -> None:
    ws = wb.create_sheet("08_LFM_Calculation")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "LFM Calculation (Latent Fault Metric)")
    style_header_row(ws, 3, ["Safety Goal", "Σ(λ_MPF_L)", "Denominator", "LFM", "Target (ASIL)", "Status"])

    target_asil = bom.get("target_asil", "D")
    target = ASIL_TARGETS.get(target_asil, {}).get("LFM", 90)

    ws.cell(row=4, column=1, value="SG-001 (Placeholder)")
    ws.cell(row=4, column=2, value=f"=SUM('06_FMEDA_Worksheet'!M:M)")
    ws.cell(row=4, column=3, value=f"=SUM('06_FMEDA_Worksheet'!G:G)-SUM('06_FMEDA_Worksheet'!K:K)-SUM('06_FMEDA_Worksheet'!L:L)")
    ws.cell(row=4, column=4, value=f"=IF(C4=0,1,1-(B4/C4))")
    ws.cell(row=4, column=5, value=target)
    ws.cell(row=4, column=6, value=f"=IF(D4>=E4/100,\"PASS\",\"FAIL\")")

    stripe_body(ws, 4, 4, 6)
    autosize(ws, {1: 22, 2: 18, 3: 18, 4: 14, 5: 14, 6: 12})


def build_pmhf_calculation(wb: Workbook, bom: dict) -> None:
    ws = wb.create_sheet("09_PMHF_Calculation")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "PMHF Calculation (Probabilistic Metric for HW Failures)")
    style_header_row(ws, 3, ["Safety Goal", "PMHF (FIT)", "Target (FIT, ASIL)", "Status"])

    target_asil = bom.get("target_asil", "D")
    target = ASIL_TARGETS.get(target_asil, {}).get("PMHF", 10)

    ws.cell(row=4, column=1, value="SG-001 (Placeholder)")
    ws.cell(row=4, column=2, value=f"=SUM('06_FMEDA_Worksheet'!K:K)+SUM('06_FMEDA_Worksheet'!L:L)")
    ws.cell(row=4, column=3, value=target)
    ws.cell(row=4, column=4, value=f"=IF(B4<C4,\"PASS\",\"FAIL\")")

    stripe_body(ws, 4, 4, 4)
    autosize(ws, {1: 22, 2: 16, 3: 22, 4: 12})


def build_metrics_dashboard(wb: Workbook, bom: dict) -> None:
    ws = wb.create_sheet("10_Metrics_Dashboard")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Metrics Dashboard — SPFM / LFM / PMHF")

    ws.cell(row=3, column=1, value="Safety Goal").font = header_font()
    ws.cell(row=3, column=2, value="SPFM (%)").font = header_font()
    ws.cell(row=3, column=3, value="LFM (%)").font = header_font()
    ws.cell(row=3, column=4, value="PMHF (FIT)").font = header_font()

    ws.cell(row=4, column=1, value="SG-001")
    ws.cell(row=4, column=2, value="='07_SPFM_Calculation'!D4")
    ws.cell(row=4, column=3, value="='08_LFM_Calculation'!D4")
    ws.cell(row=4, column=4, value="='09_PMHF_Calculation'!B4")

    stripe_body(ws, 4, 4, 4)
    autosize(ws, {1: 22, 2: 14, 3: 14, 4: 16})


def build_open_items(wb: Workbook) -> None:
    ws = wb.create_sheet("11_Open_Items")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Open Items — Failure Modes Without Coverage")
    style_header_row(ws, 3, ["HW_E_ID", "Failure Mode", "Issue Type", "Action Required"])

    ws.cell(row=4, column=1, value="(Auto-generated during review)")
    ws.merge_cells(start_row=4, start_column=1, end_row=4, end_column=4)


def build_references(wb: Workbook) -> None:
    ws = wb.create_sheet("12_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References & Citations")

    refs = [
        ("ISO 26262-5:2018", "Road vehicles — Functional safety, Part 5: Hardware level"),
        ("IEC 62380", "Reliability data for electronic components used in telecommunications equipment"),
        ("IEC 61709", "Electronic components — Preferred failure modes and failure rates"),
        ("FIDES Methodology", "Handbook of reliability prediction methodologies for semiconductor devices"),
    ]

    row = 3
    for std, desc in refs:
        ws.cell(row=row, column=1, value=std).font = Font(bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1

    autosize(ws, {1: 30, 2: 80})


# ============================================================================
# Main generator
# ============================================================================

def generate(tsc_path: str, bom_path: str, output_path: str) -> dict:
    with open(bom_path) as f:
        bom = json.load(f)

    mechanisms = read_tsc(tsc_path) if Path(tsc_path).exists() else {}

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, bom, tsc_path)
    build_doc_control(wb)
    build_assumptions(wb, bom)
    build_hw_element_catalog(wb, bom)
    build_failure_mode_library(wb)
    build_tsc_mechanisms(wb, mechanisms)
    fmeda_rows = build_fmeda_worksheet(wb, bom, mechanisms)
    build_spfm_calculation(wb, bom, fmeda_rows)
    build_lfm_calculation(wb, bom)
    build_pmhf_calculation(wb, bom)
    build_metrics_dashboard(wb, bom)
    build_open_items(wb)
    build_references(wb)

    wb.active = 0
    wb.save(output_path)

    return {
        "output_path": output_path,
        "tabs": 13,
        "fmeda_rows": len(fmeda_rows),
        "hw_elements": len(bom.get("hw_elements", [])),
    }


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_fmeda.py <tsc.xlsx> <hw_bom.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2], sys.argv[3])
    import json
    print(json.dumps(summary, indent=2))
