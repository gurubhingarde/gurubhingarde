"""
HSI Builder — generates a contract-grade ISO 26262-4 + -5 HSI specification workbook.

Usage:
    python generate_hsi.py <tsc.xlsx> <refinement.json> <output.xlsx>

Pipeline:
- Read HSI signals from TSC xlsx (06_HSI_Specification tab)
- Apply refinement JSON (register addresses, integrity methods, validity bits, timing)
- Generate 11-tab HSI workbook per ISO 26262 Parts 4 & 5, Section 6.4.6
- Optionally generate C header file with struct definitions
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
from tsc_reader import read_hsi_signals


# ---------------------------------------------------------------------------
# Styling (aligned with tsc-builder)
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
    base = asil_value.split("(")[0].strip() if asil_value else "QM"
    color_map = {"A": "FFE699", "B": "F4B084", "C": "F8696B", "D": "C00000"}
    if base in color_map:
        cell.fill = PatternFill("solid", fgColor=color_map[base])
        cell.font = Font(name=FONT_NAME, bold=True, color="FFFFFF" if base == "D" else "000000")
        cell.alignment = Alignment(horizontal="center", vertical="center")


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, refinement: dict, tsc_path: str) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "HSI Specification (Hardware-Software Interface)")
    style_title_row(ws, 3, 4, "ISO 26262-4 §6.4.6 + ISO 26262-5 §6.4.6")
    proj_meta = refinement.get("project", {})
    fields = [
        ("Project", proj_meta.get("name", "")),
        ("HSI Document ID", proj_meta.get("doc_id", "")),
        ("Revision", proj_meta.get("revision", "")),
        ("Date", proj_meta.get("date", "")),
        ("Author", proj_meta.get("author", "")),
        ("Approver", proj_meta.get("approver", "")),
        ("Linked TSC", tsc_path),
        ("Linked HW Architecture", refinement.get("linked_hw_arch", "")),
        ("Standard", "ISO 26262:2018, Part 4 §6.4.6 (TSC HSI) + Part 5 §6.4.6 (HW verification of HSI signals)."),
        ("Methodology", "Contract-grade HSI specification with signal catalog, register map, timing, failure modes, initialization, and cross-reference. Includes C header generation for embedded SW hand-off."),
    ]
    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1
    autosize(ws, {1: 4, 2: 26, 3: 80, 4: 4})


def build_doc_control(wb: Workbook) -> None:
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of change", "Approver"])
    for i, row in enumerate([
        ("0.1", "", "", "Initial draft generated by hsi-builder skill", ""),
        ("0.2", "", "", "HSI signal refinement applied", ""),
        ("1.0", "", "", "Released for HW design and verification", ""),
    ], start=4):
        for c, v in enumerate(row, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 6, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_signal_catalog(wb: Workbook, signals: list[dict], overrides: dict) -> None:
    ws = wb.create_sheet("02_HSI_Signal_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 11, "HSI Signal Catalog")
    note = ws.cell(row=2, column=1, value="One row per HSI signal. Defines direction (HW->SW or SW->HW), data type, integrity protection, validity bits, and allocated ASIL. This is the contract between HW and SW teams.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=11)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, [
        "Signal Name", "Direction", "Data Type", "Bit Width", "Range", "Units", "Default",
        "Encoding Rules", "Integrity Protection", "Validity Bit", "Allocated ASIL"
    ])

    by_name = {o["signal_name"]: o for o in overrides}
    row = 5
    for sig in signals:
        override = by_name.get(sig["signal_name"], {})
        ws.cell(row=row, column=1, value=sig["signal_name"])
        ws.cell(row=row, column=2, value=sig["direction"])
        ws.cell(row=row, column=3, value=override.get("data_type", "bit"))
        ws.cell(row=row, column=4, value=override.get("bit_width", 1))
        ws.cell(row=row, column=5, value=override.get("range", ""))
        ws.cell(row=row, column=6, value=override.get("units", ""))
        ws.cell(row=row, column=7, value=override.get("default_value", "0"))
        ws.cell(row=row, column=8, value=override.get("encoding_rules", "0=ok, 1=fault"))
        ws.cell(row=row, column=9, value=override.get("integrity", sig["integrity_protection"]))
        ws.cell(row=row, column=10, value=override.get("validity_bit", ""))
        cell = ws.cell(row=row, column=11, value=sig["allocated_asil"])
        asil_color_cell(cell, sig["allocated_asil"])
        row += 1

    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 12):
            cell = ws.cell(row=r, column=c)
            if c != 11:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:K{end_row}"
    autosize(ws, {1: 32, 2: 12, 3: 12, 4: 10, 5: 14, 6: 10, 7: 12, 8: 24, 9: 20, 10: 20, 11: 12})


def build_register_map(wb: Workbook, signals: list[dict], overrides: dict) -> None:
    ws = wb.create_sheet("03_Register_Map")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "Register Map (Memory-Mapped Signals)")
    note = ws.cell(row=2, column=1, value="For signals mapped to HW registers: address, bit offset, access mode, reset value, and bit-field layout. Placeholder rows for signals without fixed register addresses.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["Signal Name", "Register Address", "Bit Offset", "Access", "Reset Value", "Bit Field Layout", "Locked (LOCK bit)", "Notes"])

    by_name = {o["signal_name"]: o for o in overrides}
    row = 5
    for sig in signals:
        override = by_name.get(sig["signal_name"], {})
        ws.cell(row=row, column=1, value=sig["signal_name"])
        ws.cell(row=row, column=2, value=override.get("register_addr", "(memory-mapped TBD)"))
        ws.cell(row=row, column=3, value=override.get("register_offset", ""))
        ws.cell(row=row, column=4, value=override.get("access", "RW" if "HW" in sig["direction"] else "R"))
        ws.cell(row=row, column=5, value=override.get("reset_value", "0x00"))
        ws.cell(row=row, column=6, value=override.get("bit_field_layout", ""))
        ws.cell(row=row, column=7, value=override.get("locked", "No"))
        ws.cell(row=row, column=8, value="")
        row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 8)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 32, 2: 18, 3: 12, 4: 10, 5: 14, 6: 36, 7: 16, 8: 30})


def build_timing_spec(wb: Workbook, signals: list[dict], overrides: dict) -> None:
    ws = wb.create_sheet("04_Timing_Specification")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "Timing Specification")
    note = ws.cell(row=2, column=1, value="Per signal: sample rate, max age, latency budgets (HW->SW and SW->HW), worst-case detection time, settling time.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["Signal Name", "Sample Rate (Hz)", "Max Age (ms)", "Latency HW->SW (ms)", "Latency SW->HW (ms)", "Detection Time (ms)", "Settling Time (ms)", "Notes"])

    by_name = {o["signal_name"]: o for o in overrides}
    row = 5
    for sig in signals:
        override = by_name.get(sig["signal_name"], {})
        ws.cell(row=row, column=1, value=sig["signal_name"])
        ws.cell(row=row, column=2, value=override.get("sample_rate", ""))
        ws.cell(row=row, column=3, value=override.get("max_age_ms", ""))
        ws.cell(row=row, column=4, value=override.get("latency_hw_to_sw", ""))
        ws.cell(row=row, column=5, value=override.get("latency_sw_to_hw", ""))
        ws.cell(row=row, column=6, value=override.get("detection_time_ms", ""))
        ws.cell(row=row, column=7, value=override.get("settling_time_ms", ""))
        ws.cell(row=row, column=8, value="")
        row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 8)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 32, 2: 18, 3: 14, 4: 18, 5: 18, 6: 18, 7: 18, 8: 30})


def build_failure_modes(wb: Workbook, signals: list[dict]) -> None:
    ws = wb.create_sheet("05_Failure_Modes_and_Reactions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Failure Modes and Reactions")
    note = ws.cell(row=2, column=1, value="Per signal: possible faults (stuck, parity error, missing, late, out-of-range), detection method, SW reaction, HW fail-safe behavior.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["Signal Name", "Possible Faults", "Detection Method", "SW Reaction", "HW Fail-Safe Behavior", "Detection Coverage (target %)", "Notes"])

    failure_modes = ["Stuck-at 0", "Stuck-at 1", "Parity error", "Missing", "Late", "Out-of-range"]
    row = 5
    for sig in signals:
        for idx, fm in enumerate(failure_modes):
            if idx == 0:
                ws.cell(row=row, column=1, value=sig["signal_name"])
            ws.cell(row=row, column=2, value=fm)
            ws.cell(row=row, column=3, value="<TBD>")
            ws.cell(row=row, column=4, value="<TBD: SW action on fault detection>")
            ws.cell(row=row, column=5, value="<TBD: HW independent disable>")
            ws.cell(row=row, column=6, value="")
            ws.cell(row=row, column=7, value="")
            row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 7)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 32, 2: 20, 3: 28, 4: 30, 5: 30, 6: 22, 7: 30})


def build_initialization(wb: Workbook) -> None:
    ws = wb.create_sheet("06_Initialization_Sequence")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Initialization Sequence")
    note = ws.cell(row=2, column=1, value="HW power-on diagnostic (BIST, register lock, supply monitor), SW startup checks (validity bit state machine), and hand-shake protocol.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=5)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["Phase", "Actor (HW/SW)", "Action", "Timing", "Condition for success"])

    init_rows = [
        ("Power-on BIST", "HW", "Self-test on all HSI registers and protection logic", "<TBD>", "All tests pass; set ready flag"),
        ("Register Lock", "HW", "Lock HSI register addresses to prevent SW write-by-mistake", "<TBD>", "Lock bit set; re-locks on watchdog reset"),
        ("Supply Monitor Boot", "HW", "Enable OV/UV detection; assert nINIT if out-of-spec", "<TBD>", "Supply nominal; nINIT released"),
        ("SW Startup", "SW", "Poll ready flag; clear all validity bits; initialize liveness counter", "<TBD>", "Ready flag set; validity counters clear"),
        ("Hand-shake", "HW+SW", "HW asserts first diagnostic flag; SW increments liveness counter; HW confirms counter change", "<TBD>", "Liveness counter confirmed; FSM transitions to normal operation"),
    ]

    row = 5
    for phase, actor, action, timing, success in init_rows:
        ws.cell(row=row, column=1, value=phase)
        ws.cell(row=row, column=2, value=actor)
        ws.cell(row=row, column=3, value=action)
        ws.cell(row=row, column=4, value=timing)
        ws.cell(row=row, column=5, value=success)
        row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 5)
    autosize(ws, {1: 22, 2: 14, 3: 40, 4: 14, 5: 40})


def build_cross_reference(wb: Workbook, signals: list[dict]) -> None:
    ws = wb.create_sheet("07_Cross_Reference")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Cross-Reference — HSI Signals to Safety Requirements")
    note = ws.cell(row=2, column=1, value="Traceability matrix: HSI signal -> FSR_ID -> TSR_ID -> Safety Mechanism -> ASIL. Enables impact analysis for design changes.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["HSI Signal", "FSR_ID", "TSR_ID", "Safety Mechanism", "Allocated ASIL", "Notes"])

    row = 5
    for sig in signals:
        ws.cell(row=row, column=1, value=sig["signal_name"])
        ws.cell(row=row, column=2, value=sig["linked_fsr"])
        ws.cell(row=row, column=3, value="<TBD: TSR_ID from TSC>")
        ws.cell(row=row, column=4, value=sig["mechanism"])
        cell = ws.cell(row=row, column=5, value=sig["allocated_asil"])
        asil_color_cell(cell, sig["allocated_asil"])
        ws.cell(row=row, column=6, value="")
        row += 1

    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 7):
            cell = ws.cell(row=r, column=c)
            if c != 5:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    autosize(ws, {1: 36, 2: 12, 3: 14, 4: 36, 5: 12, 6: 36})


def build_c_header_stub(wb: Workbook, signals: list[dict]) -> None:
    ws = wb.create_sheet("08_C_Header_Stub")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "C Header Definitions (Preview)")
    note = ws.cell(row=2, column=1, value="Auto-generated C struct definitions for embedded SW. Full .h file written to <output>_hsi.h. This tab shows preview; do not edit.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=2)
    ws.row_dimensions[2].height = 32

    # Group signals by module (first part of signal name before '.')
    by_module = defaultdict(list)
    for sig in signals:
        parts = sig["signal_name"].split(".")
        module = parts[0] if parts else "misc"
        by_module[module].append(sig)

    row = 4
    for module in sorted(by_module.keys()):
        ws.cell(row=row, column=1, value=f"Module: {module}").font = Font(name=FONT_NAME, bold=True, size=10)
        row += 1
        for sig in by_module[module]:
            direction = "HW->SW" if "HW" in sig["direction"] else "SW->HW"
            comment = f"// {direction}; {sig['linked_fsr']}; {sig['mechanism']}"
            ws.cell(row=row, column=1, value=comment).font = Font(name=FONT_NAME, size=9, italic=True, color="666666")
            row += 1
            clean_name = sig["signal_name"].replace(".", "_")
            ws.cell(row=row, column=1, value=f"// uint{sig.get('bit_width', 1)}_t {clean_name};").font = body_font()
            row += 1
        row += 1

    autosize(ws, {1: 100, 2: 4})


def build_test_cases(wb: Workbook, signals: list[dict]) -> None:
    ws = wb.create_sheet("09_Test_Cases")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Test Cases")
    note = ws.cell(row=2, column=1, value="Per signal: nominal path, fault injection (stuck-at, parity), boundary conditions, timing edge cases. Basis for HW/SW integration and verification.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["Signal Name", "Test Scenario", "Input Stimulus", "Expected Output", "Pass/Fail Criteria", "Notes"])

    scenarios = ["Nominal path", "Stuck-at 0", "Stuck-at 1", "Parity error", "Timeout", "Boundary"]
    row = 5
    for sig in signals:
        for idx, scenario in enumerate(scenarios):
            if idx == 0:
                ws.cell(row=row, column=1, value=sig["signal_name"])
            ws.cell(row=row, column=2, value=scenario)
            ws.cell(row=row, column=3, value="<TBD: test stimulus>")
            ws.cell(row=row, column=4, value="<TBD: expected result>")
            ws.cell(row=row, column=5, value="<TBD: acceptance criteria>")
            ws.cell(row=row, column=6, value="")
            row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 6)
    autosize(ws, {1: 32, 2: 20, 3: 28, 4: 28, 5: 28, 6: 30})


def build_references(wb: Workbook, tsc_path: str) -> None:
    ws = wb.create_sheet("10_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "References")

    refs = [
        ("TSC (Technical Safety Concept)", tsc_path),
        ("ISO 26262-4:2018 Section 6.4.6", "TSC HSI specification requirements"),
        ("ISO 26262-5:2018 Section 6.4.6", "HW HSI verification and FMEDA input"),
        ("AUTOSAR Classic", "If applicable: HSI alignment with AUTOSAR 4.x I/O contracts"),
        ("Methodology Reference", "See references/ directory in hsi-builder skill"),
    ]

    row = 4
    for label, value in refs:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True, size=10)
        ws.cell(row=row, column=2, value=value).font = body_font()
        row += 1

    autosize(ws, {1: 36, 2: 80})


# ---------------------------------------------------------------------------
# C header generation
# ---------------------------------------------------------------------------

def generate_c_header(signals: list[dict], output_basename: str) -> str:
    """Generate a C header file with struct definitions."""
    # Group signals by module
    by_module = defaultdict(list)
    for sig in signals:
        parts = sig["signal_name"].split(".")
        module = parts[0] if parts else "misc"
        by_module[module].append(sig)

    lines = [
        "#pragma once",
        "/* Auto-generated HSI struct definitions. Do not edit by hand. */",
        "",
        "#include <stdint.h>",
        "",
    ]

    for module in sorted(by_module.keys()):
        struct_name = f"{module}_hsi_t"
        lines.append(f"typedef struct {{")
        for sig in by_module[module]:
            direction = "HW->SW" if "HW" in sig["direction"] else "SW->HW"
            clean_name = sig["signal_name"].replace(".", "_").replace(module + "_", "")
            # Extract bit width if available
            encoding = sig["encoding"]
            bit_width = 1
            if "bit" in encoding.lower():
                try:
                    bits = "".join(filter(str.isdigit, encoding.split()[0]))
                    if bits:
                        bit_width = int(bits)
                except:
                    pass
            if bit_width <= 8:
                ctype = "uint8_t"
            elif bit_width <= 16:
                ctype = "uint16_t"
            elif bit_width <= 32:
                ctype = "uint32_t"
            else:
                ctype = "uint64_t"

            bit_field = f" : {bit_width}" if bit_width < (8 if ctype == "uint8_t" else 16) else ""
            lines.append(f"    {ctype} {clean_name}{bit_field};  // {direction}; {sig['linked_fsr']}")

        lines.append(f"}} {struct_name};")
        lines.append("")

    header_path = output_basename.replace(".xlsx", "") + "_hsi.h"
    Path(header_path).write_text("\n".join(lines), encoding="utf-8")
    return header_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(tsc_path: str, refinement_path: str, output_path: str) -> dict:
    # Load inputs
    signals = read_hsi_signals(tsc_path)
    with open(refinement_path) as f:
        refinement = json.load(f)

    signal_overrides = refinement.get("signal_overrides", [])

    # Build workbook
    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, refinement, tsc_path)
    build_doc_control(wb)
    build_signal_catalog(wb, signals, signal_overrides)
    build_register_map(wb, signals, signal_overrides)
    build_timing_spec(wb, signals, signal_overrides)
    build_failure_modes(wb, signals)
    build_initialization(wb)
    build_cross_reference(wb, signals)
    build_c_header_stub(wb, signals)
    build_test_cases(wb, signals)
    build_references(wb, tsc_path)

    wb.active = 0
    wb.save(output_path)

    # Generate C header
    header_path = generate_c_header(signals, output_path)

    return {
        "tabs": 11,
        "signals": len(signals),
        "output_path": output_path,
        "header_path": header_path,
        "header_size_bytes": len(Path(header_path).read_bytes()),
    }


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_hsi.py <tsc.xlsx> <refinement.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(summary, indent=2))
