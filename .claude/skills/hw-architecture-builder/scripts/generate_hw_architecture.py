"""
HW Architecture Builder — generates ISO 26262-5 §7 hardware architecture workbook
from TSC xlsx + HW BOM JSON.

Usage:
    python generate_hw_architecture.py <tsc.xlsx> <hw_arch.json> <output.xlsx>

Reads:
  - TSC xlsx: system-level architecture, FSRs, HW-TSRs, safety mechanisms
  - HW BOM JSON: concrete ICs, PCBs, power/clock architecture, FIT rates

Produces:
  - 12-tab xlsx with board designs, HW element catalog, safety mappings, BOM, FIT budgets
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


# ---------------------------------------------------------------------------
# Styling (matching tsc-builder)
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"

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


def asil_color_cell(cell, asil_value: str) -> None:
    if not asil_value:
        return
    base = asil_value.split("(")[0].strip() if asil_value else "QM"
    color_map = {"A": "FFE699", "B": "F4B084", "C": "F8696B", "D": "C00000"}
    if base in color_map:
        cell.fill = PatternFill("solid", fgColor=color_map[base])
        cell.font = Font(name=FONT_NAME, bold=True, color="FFFFFF" if base == "D" else "000000")
        cell.alignment = Alignment(horizontal="center", vertical="center")


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, tsc_data: dict, hw_arch: dict, tsc_path: str) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "Hardware Architecture (ISO 26262-5 §7)")
    item_title = hw_arch.get("project", {}).get("name") or tsc_data["item"].get("Item Title", "")
    style_title_row(ws, 3, 4, item_title)

    proj = hw_arch.get("project", {})
    fields = [
        ("Project", proj.get("name", "")),
        ("HW Architecture Document ID", proj.get("doc_id", "")),
        ("Revision", proj.get("revision", "")),
        ("Date", proj.get("date", "")),
        ("Author", proj.get("author", "")),
        ("Approver", proj.get("approver", "")),
        ("Linked TSC", tsc_path),
        ("Standard", "ISO 26262:2018, Part 5 §7 (Hardware design architecture and FMEDA)."),
        ("Methodology", "Hardware architecture refines TSC into concrete PCBs, ICs, and passive elements. Includes FIT rate compilation, power/clock architecture, common-cause analysis, safety mechanism allocation, and bill of materials for FMEDA and layout teams."),
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
    for i, row in enumerate([
        ("0.1", "", "", "Initial draft generated by hw-architecture-builder skill", ""),
        ("0.2", "", "", "Internal review comments incorporated", ""),
        ("1.0", "", "", "Released to FMEDA and layout teams", ""),
    ], start=4):
        for c, v in enumerate(row, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 6, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_tsc_architecture_echo(wb: Workbook, tsc_data: dict) -> None:
    ws = wb.create_sheet("02_TSC_Architecture_Echo")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "TSC Architecture (Read-Only Echo)")
    note = ws.cell(row=2, column=1, value="This tab echoes the TSC's system architecture. Update the TSC and re-run if changes are needed. Links HW elements (tabs 4+) back to TSC nodes and HW-TSRs.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 32

    # HW Components section
    style_header_row(ws, 4, ["HW Component ID", "Name", "Part / Vendor", "Allocated Nodes", "Power Domain", "Clock Domain", "Notes"])
    row = 5
    for c in tsc_data.get("hw_components", []):
        ws.cell(row=row, column=1, value=c.get("id", ""))
        ws.cell(row=row, column=2, value=c.get("name", ""))
        ws.cell(row=row, column=3, value=c.get("part", ""))
        ws.cell(row=row, column=4, value=", ".join(c.get("allocated_nodes", [])))
        ws.cell(row=row, column=5, value=c.get("power_domain", ""))
        ws.cell(row=row, column=6, value=c.get("clock_domain", ""))
        ws.cell(row=row, column=7, value=c.get("notes", ""))
        row += 1
    hw_end = 4 + len(tsc_data.get("hw_components", []))
    stripe_body(ws, 5, hw_end, 7)

    # SW Partitions section
    base = hw_end + 3
    style_title_row(ws, base, 7, "Software Partitions")
    style_header_row(ws, base + 1, ["SW Partition ID", "Name", "Hosted On", "Allocated Nodes", "RTOS / OS", "ASIL (dev-to)", "Notes"])
    row = base + 2
    for sp in tsc_data.get("sw_partitions", []):
        ws.cell(row=row, column=1, value=sp.get("id", ""))
        ws.cell(row=row, column=2, value=sp.get("name", ""))
        ws.cell(row=row, column=3, value=sp.get("hosted_on", ""))
        ws.cell(row=row, column=4, value=", ".join(sp.get("allocated_nodes", [])))
        ws.cell(row=row, column=5, value=sp.get("rtos", ""))
        cell = ws.cell(row=row, column=6, value=sp.get("asil", ""))
        asil_color_cell(cell, sp.get("asil", ""))
        ws.cell(row=row, column=7, value=sp.get("notes", ""))
        row += 1
    sw_end = base + 1 + len(tsc_data.get("sw_partitions", []))
    stripe_body(ws, base + 2, sw_end, 7)
    autosize(ws, {1: 14, 2: 26, 3: 22, 4: 26, 5: 16, 6: 16, 7: 30})


def build_pcb_design(wb: Workbook, hw_arch: dict) -> None:
    ws = wb.create_sheet("03_PCB_Design")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "PCB Design")
    note = ws.cell(row=2, column=1, value="Board-level layout specification: main PCB and daughter cards. Dimensions, layers, key area allocations for power/analog/digital regions.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["PCB ID", "Name", "Layers", "Dimensions (mm)", "Key Area Allocations", "Notes"])
    row = 5
    for pcb in hw_arch.get("pcbs", []):
        ws.cell(row=row, column=1, value=pcb.get("id", ""))
        ws.cell(row=row, column=2, value=pcb.get("name", ""))
        ws.cell(row=row, column=3, value=pcb.get("layers", ""))
        ws.cell(row=row, column=4, value=pcb.get("dimensions", ""))
        ws.cell(row=row, column=5, value=pcb.get("key_area_allocations", ""))
        ws.cell(row=row, column=6, value=pcb.get("notes", ""))
        row += 1
    end_row = 4 + len(hw_arch.get("pcbs", []))
    stripe_body(ws, 5, end_row, 6)
    autosize(ws, {1: 12, 2: 18, 3: 12, 4: 20, 5: 36, 6: 30})


def build_hw_element_catalog(wb: Workbook, hw_arch: dict) -> None:
    ws = wb.create_sheet("04_HW_Element_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 10, "Hardware Element Catalog")
    note = ws.cell(row=2, column=1, value="Concrete list of every IC, discrete, passive, and connector. Each row is one part instance with traceability to TSC node, baseline FIT rate, and safety qualification.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=10)
    ws.row_dimensions[2].height = 36

    headers = ["HW-E_ID", "Name", "Type", "Supplier", "Part Number", "Package", "Pin Count", "Baseline FIT", "Qualification", "TSC Node ID"]
    style_header_row(ws, 4, headers)

    row = 5
    for elem in hw_arch.get("hw_elements", []):
        ws.cell(row=row, column=1, value=elem.get("id", ""))
        ws.cell(row=row, column=2, value=elem.get("name", ""))
        ws.cell(row=row, column=3, value=elem.get("type", ""))
        ws.cell(row=row, column=4, value=elem.get("supplier", ""))
        ws.cell(row=row, column=5, value=elem.get("part_number", ""))
        ws.cell(row=row, column=6, value=elem.get("package", ""))
        ws.cell(row=row, column=7, value=elem.get("pin_count", ""))
        ws.cell(row=row, column=8, value=elem.get("baseline_fit", ""))
        ws.cell(row=row, column=9, value=elem.get("qualification", ""))
        ws.cell(row=row, column=10, value=elem.get("tsc_node_id", ""))
        row += 1

    end_row = 4 + len(hw_arch.get("hw_elements", []))
    stripe_body(ws, 5, end_row, 10)
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:J{end_row}"
    autosize(ws, {1: 12, 2: 22, 3: 14, 4: 12, 5: 18, 6: 12, 7: 10, 8: 12, 9: 16, 10: 14})


def build_safety_mechanism_allocation(wb: Workbook, hw_arch: dict, tsc_data: dict) -> None:
    ws = wb.create_sheet("05_Safety_Mechanism_Allocation")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Safety Mechanism Allocation")
    note = ws.cell(row=2, column=1, value="Per HW element: which safety mechanisms apply, reference to TSC mechanism, and allocated ASIL. Enables traceability from HW-E to TSC mechanism to HW-TSR.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 36

    headers = ["HW-E_ID", "Name", "TSC Node ID", "Mechanism ID", "Mechanism Name", "Allocated ASIL", "DC Target %"]
    style_header_row(ws, 4, headers)

    # Build a mechanism lookup from TSC
    mech_lookup = {m["id"]: m["name"] for m in tsc_data.get("mechanisms", [])}

    row = 5
    for elem in hw_arch.get("hw_elements", []):
        mechanisms_str = elem.get("mechanisms", "")
        if mechanisms_str:
            mech_ids = [m.strip() for m in str(mechanisms_str).split(",")]
        else:
            mech_ids = []

        if not mech_ids:
            ws.cell(row=row, column=1, value=elem.get("id", ""))
            ws.cell(row=row, column=2, value=elem.get("name", ""))
            ws.cell(row=row, column=3, value=elem.get("tsc_node_id", ""))
            ws.cell(row=row, column=4, value="<TBD>")
            ws.cell(row=row, column=5, value="(No mechanisms assigned yet)")
            ws.cell(row=row, column=6, value="")
            ws.cell(row=row, column=7, value="")
            row += 1
        else:
            for idx, mech_id in enumerate(mech_ids):
                if idx == 0:
                    ws.cell(row=row, column=1, value=elem.get("id", ""))
                    ws.cell(row=row, column=2, value=elem.get("name", ""))
                    ws.cell(row=row, column=3, value=elem.get("tsc_node_id", ""))
                ws.cell(row=row, column=4, value=mech_id)
                ws.cell(row=row, column=5, value=mech_lookup.get(mech_id, ""))
                cell = ws.cell(row=row, column=6, value=elem.get("asil", ""))
                asil_color_cell(cell, elem.get("asil", ""))
                ws.cell(row=row, column=7, value=elem.get("dc_target", ""))
                row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 7)
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:G{end_row}"
    autosize(ws, {1: 12, 2: 22, 3: 14, 4: 12, 5: 26, 6: 14, 7: 12})


def build_hw_sr_allocation_matrix(wb: Workbook, hw_arch: dict, tsc_data: dict) -> None:
    ws = wb.create_sheet("06_HW_SR_Allocation_Matrix")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 12, "HW Safety Requirement Allocation Matrix")
    note = ws.cell(row=2, column=1, value="Cross-reference matrix: HW-SR_ID rows x HW-E_ID columns. Mark which HW element implements each HW-SR. Provides traceability from HW-SR to concrete IC.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=12)
    ws.row_dimensions[2].height = 36

    # Derive HW-SR IDs from HW-TSRs
    hw_sr_ids = [t["tsr_id"] for t in tsc_data.get("hw_tsrs", []) if t.get("tsr_id")]
    if not hw_sr_ids:
        hw_sr_ids = ["HW-SR-001", "HW-SR-002", "HW-SR-003"]  # placeholder

    hw_elem_ids = [e.get("id", "") for e in hw_arch.get("hw_elements", [])]

    # Build matrix header
    headers = ["HW-SR_ID"] + hw_elem_ids[:10]  # limit to 10 columns for readability
    style_header_row(ws, 4, headers)

    row = 5
    for sr_id in hw_sr_ids:
        ws.cell(row=row, column=1, value=sr_id)
        for col, elem_id in enumerate(hw_elem_ids[:10], start=2):
            ws.cell(row=row, column=col, value="")  # to be filled by analyst
        row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, min(11, len(hw_elem_ids) + 1))
    ws.freeze_panes = "B5"
    autosize(ws, {1: 12})
    for col in range(2, min(12, len(hw_elem_ids) + 2)):
        ws.column_dimensions[get_column_letter(col)].width = 10


def build_power_architecture(wb: Workbook, hw_arch: dict) -> None:
    ws = wb.create_sheet("07_Power_Architecture")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "Power Architecture")
    note = ws.cell(row=2, column=1, value="Power rails, regulators, monitoring, fusing, isolation. Identifies common-cause risks and monitoring thresholds.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)
    ws.row_dimensions[2].height = 32

    headers = ["Rail Name", "Voltage (V)", "Regulator Type", "Regulator IC", "OV Threshold", "UV Threshold", "Fusing (A)", "Isolation From", "Notes"]
    style_header_row(ws, 4, headers)

    row = 5
    for rail in hw_arch.get("power_rails", []):
        ws.cell(row=row, column=1, value=rail.get("rail", ""))
        ws.cell(row=row, column=2, value=rail.get("voltage", ""))
        ws.cell(row=row, column=3, value=rail.get("regulator_type", ""))
        ws.cell(row=row, column=4, value=rail.get("regulator_ic", ""))
        ws.cell(row=row, column=5, value=rail.get("ov_threshold", ""))
        ws.cell(row=row, column=6, value=rail.get("uv_threshold", ""))
        ws.cell(row=row, column=7, value=rail.get("fusing", ""))
        ws.cell(row=row, column=8, value=rail.get("isolation_from", ""))
        ws.cell(row=row, column=9, value=rail.get("notes", ""))
        row += 1

    end_row = 4 + len(hw_arch.get("power_rails", []))
    stripe_body(ws, 5, end_row, 9)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 14, 2: 12, 3: 14, 4: 16, 5: 14, 6: 14, 7: 12, 8: 16, 9: 30})


def build_clock_architecture(wb: Workbook, hw_arch: dict) -> None:
    ws = wb.create_sheet("08_Clock_Architecture")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "Clock Architecture")
    note = ws.cell(row=2, column=1, value="Clock sources (XTAL, RC, PLL), distribution, monitoring, redundancy strategy.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)
    ws.row_dimensions[2].height = 32

    headers = ["Clock Source ID", "Type", "Frequency (MHz)", "Monitor Type", "Monitor Thresholds", "Redundancy", "Monitored By", "Notes"]
    style_header_row(ws, 4, headers)

    row = 5
    for clk in hw_arch.get("clocks", []):
        ws.cell(row=row, column=1, value=clk.get("source", ""))
        ws.cell(row=row, column=2, value=clk.get("type", ""))
        ws.cell(row=row, column=3, value=clk.get("frequency", ""))
        ws.cell(row=row, column=4, value=clk.get("monitor_type", ""))
        ws.cell(row=row, column=5, value=clk.get("monitor_thresholds", ""))
        ws.cell(row=row, column=6, value=clk.get("redundancy", ""))
        ws.cell(row=row, column=7, value=clk.get("monitored_by", ""))
        ws.cell(row=row, column=8, value=clk.get("notes", ""))
        row += 1

    end_row = 4 + len(hw_arch.get("clocks", []))
    stripe_body(ws, 5, end_row, 8)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 14, 2: 10, 3: 14, 4: 14, 5: 20, 6: 14, 7: 14, 8: 30})


def build_common_cause_analysis(wb: Workbook, hw_arch: dict) -> None:
    ws = wb.create_sheet("09_Common_Cause_Analysis")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "Common-Cause Failure Analysis (CCFA)")
    note = ws.cell(row=2, column=1, value="Per redundant pair: shared rail, package, PCB region, environmental zone. Marks each coupling as 'No', 'Yes - Mitigated', or 'Yes - Unmitigated'.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)
    ws.row_dimensions[2].height = 36

    headers = ["Redundant Pair (Node A / Node B)", "Coupling Type", "Coupling Present?", "Shared Resource", "Mitigation", "Unmitigated?", "Test Evidence", "Notes"]
    style_header_row(ws, 4, headers)

    # Placeholder rows (analyst fills in)
    row = 5
    for ccfa in hw_arch.get("common_cause_pairs", []):
        ws.cell(row=row, column=1, value=ccfa.get("pair_id", ""))
        ws.cell(row=row, column=2, value=ccfa.get("coupling_type", ""))
        ws.cell(row=row, column=3, value=ccfa.get("present", ""))
        ws.cell(row=row, column=4, value=ccfa.get("shared_resource", ""))
        ws.cell(row=row, column=5, value=ccfa.get("mitigation", ""))
        ws.cell(row=row, column=6, value=ccfa.get("unmitigated", ""))
        ws.cell(row=row, column=7, value=ccfa.get("test_evidence", ""))
        ws.cell(row=row, column=8, value=ccfa.get("notes", ""))
        row += 1

    if row == 5:
        ws.cell(row=5, column=1, value="(Analyst to fill in per redundancy analysis)")
        row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 8)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 26, 2: 16, 3: 16, 4: 18, 5: 26, 6: 14, 7: 16, 8: 30})


def build_bill_of_materials(wb: Workbook, hw_arch: dict) -> None:
    ws = wb.create_sheet("10_Bill_of_Materials")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Bill of Materials (BOM) Summary")
    note = ws.cell(row=2, column=1, value="Summary BOM: total FIT per element type and per safety function. Total system FIT used in PMHF calculation.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 32

    headers = ["Element Type", "Quantity", "Unit FIT", "Total FIT", "AEC-Q Grade", "Notes"]
    style_header_row(ws, 4, headers)

    # Aggregate by type
    by_type: dict[str, dict] = defaultdict(lambda: {"qty": 0, "fit": 0})
    for elem in hw_arch.get("hw_elements", []):
        elem_type = elem.get("type", "Unknown")
        fit = float(elem.get("baseline_fit", 0) or 0)
        by_type[elem_type]["qty"] += 1
        by_type[elem_type]["fit"] += fit
        if "qualification" not in by_type[elem_type]:
            by_type[elem_type]["qualification"] = elem.get("qualification", "")

    row = 5
    total_fit = 0
    for elem_type in sorted(by_type.keys()):
        data = by_type[elem_type]
        qty = data["qty"]
        fit = data["fit"]
        total_fit += fit
        ws.cell(row=row, column=1, value=elem_type)
        ws.cell(row=row, column=2, value=qty)
        ws.cell(row=row, column=3, value="")  # unit FIT
        ws.cell(row=row, column=4, value=fit)
        ws.cell(row=row, column=5, value=data.get("qualification", ""))
        ws.cell(row=row, column=6, value="")
        row += 1

    # Total row
    ws.cell(row=row, column=1, value="TOTAL SYSTEM")
    ws.cell(row=row, column=2, value=sum(e["qty"] for e in by_type.values()))
    ws.cell(row=row, column=3, value="")
    ws.cell(row=row, column=4, value=total_fit).font = Font(name=FONT_NAME, bold=True)
    ws.cell(row=row, column=5, value="")
    ws.cell(row=row, column=6, value="")

    end_row = row
    stripe_body(ws, 5, end_row, 6)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 16, 2: 10, 3: 10, 4: 12, 5: 14, 6: 30})


def build_references(wb: Workbook, tsc_path: str, hw_arch: dict) -> None:
    ws = wb.create_sheet("11_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "References")

    refs = [
        ("Linked TSC", tsc_path),
        ("Related Documents", "Schematic (TBD), PCB Layout (TBD), FMEDA report (TBD)"),
        ("Component Datasheets", "See links in HW Element Catalog (Tab 04)"),
        ("FIT Sources", "IEC 62380:2004, Component suppliers, FMEDA baseline reports"),
        ("Applicable Standards", "ISO 26262-5:2018 §7, IEC 62380, AEC-Q100/Q200"),
        ("FMEA Methodology", "ISO 26262-5 Annex B (FMEDA guidance, SPFM/PMHF calculation)"),
    ]

    row = 3
    for label, value in refs:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=value).alignment = Alignment(wrap_text=True)
        ws.row_dimensions[row].height = 20
        row += 1

    autosize(ws, {1: 20, 2: 80})


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate(tsc_path: str, hw_arch_path: str, output_path: str) -> dict:
    # Read TSC
    tsc_data = read_tsc(tsc_path)

    # Read HW BOM JSON
    with open(hw_arch_path) as f:
        hw_arch = json.load(f)

    # Create workbook
    wb = Workbook()
    wb.remove(wb.active)

    # Build tabs
    build_title_page(wb, tsc_data, hw_arch, tsc_path)
    build_doc_control(wb)
    build_tsc_architecture_echo(wb, tsc_data)
    build_pcb_design(wb, hw_arch)
    build_hw_element_catalog(wb, hw_arch)
    build_safety_mechanism_allocation(wb, hw_arch, tsc_data)
    build_hw_sr_allocation_matrix(wb, hw_arch, tsc_data)
    build_power_architecture(wb, hw_arch)
    build_clock_architecture(wb, hw_arch)
    build_common_cause_analysis(wb, hw_arch)
    build_bill_of_materials(wb, hw_arch)
    build_references(wb, tsc_path, hw_arch)

    wb.active = 0
    wb.save(output_path)

    # Count outputs
    hw_elem_count = len(hw_arch.get("hw_elements", []))
    total_fit = sum(float(e.get("baseline_fit", 0) or 0) for e in hw_arch.get("hw_elements", []))

    return {
        "tab_count": 12,
        "hw_elements": hw_elem_count,
        "total_fit": total_fit,
        "output_path": output_path,
    }


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_hw_architecture.py <tsc.xlsx> <hw_arch.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)

    summary = generate(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(summary, indent=2))
