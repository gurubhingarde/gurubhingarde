"""
SW-HSI Builder — generates a contract-grade ISO 26262-6 SW-side HSI specification workbook.

Usage:
    python generate_sw_hsis.py <hsi.xlsx> <refinement.json> <output.xlsx>

Pipeline:
- Read HSI signals from hsi-builder xlsx (02_HSI_Signal_Catalog, 04_Timing_Specification, 05_Failure_Modes tabs)
- Apply refinement JSON (handler names, SWC allocation, RTOS task, debounce strategy, max execution time)
- Generate 11-tab SW-HSI workbook per ISO 26262-6 Section 7
- Generate C header file with handler function declarations
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from hsi_reader import read_hsi_signals, read_hsi_timing, read_hsi_failure_modes


# ---------------------------------------------------------------------------
# Styling (aligned with hsi-builder)
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

def build_title_page(wb: Workbook, refinement: dict, hsi_path: str) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "SW-HSI Specification (Software-side Hardware-Software Interface)")
    style_title_row(ws, 3, 4, "ISO 26262-6 Section 7 + ISO 26262-4 Section 6.4.6")
    proj_meta = refinement.get("project", {})
    fields = [
        ("Project", proj_meta.get("name", "")),
        ("SW-HSI Document ID", proj_meta.get("doc_id", "")),
        ("Revision", proj_meta.get("revision", "")),
        ("Date", proj_meta.get("date", "")),
        ("Author", proj_meta.get("author", "")),
        ("Approver", proj_meta.get("approver", "")),
        ("Linked HSI (HW-side)", hsi_path),
        ("Linked SW Architecture", refinement.get("linked_sw_arch", "(not provided)")),
        ("Standard", "ISO 26262:2018, Part 6 Section 7 (SW implementation); Part 4 §6.4.6 (HSI contract)."),
        ("Methodology", "Contract-grade SW-HSI with handler catalog, debouncing strategies, RTOS integration, fault propagation, initialization sequence, and C header generation."),
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
        ("0.1", "", "", "Initial draft generated by sw-hsis-builder skill", ""),
        ("0.2", "", "", "Handler allocation and debounce strategy refinement applied", ""),
        ("1.0", "", "", "Released for SW design and integration test", ""),
    ], start=4):
        for c, v in enumerate(row, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 6, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_signal_catalog_echo(wb: Workbook, signals: list[dict]) -> None:
    ws = wb.create_sheet("02_HSI_Signal_Catalog_Echo")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 11, "HSI Signal Catalog Echo (Read-only from HW-side HSI)")
    note = ws.cell(row=2, column=1, value="This is a read-only echo of the signals from the HW-side HSI. It shows the signal names, directions, encodings, and allocated ASIL that the SW side must handle.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=11)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, [
        "Signal Name", "Direction", "Data Type", "Bit Width", "Range", "Units", "Default",
        "Encoding Rules", "Integrity Protection", "Validity Bit", "Allocated ASIL"
    ])

    row = 5
    for sig in signals:
        ws.cell(row=row, column=1, value=sig["signal_name"])
        ws.cell(row=row, column=2, value=sig["direction"])
        ws.cell(row=row, column=3, value=sig["data_type"])
        ws.cell(row=row, column=4, value=sig["bit_width"])
        ws.cell(row=row, column=5, value=sig["range"])
        ws.cell(row=row, column=6, value=sig["units"])
        ws.cell(row=row, column=7, value=sig["default_value"])
        ws.cell(row=row, column=8, value=sig["encoding_rules"])
        ws.cell(row=row, column=9, value=sig["integrity_protection"])
        ws.cell(row=row, column=10, value=sig["validity_bit"])
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


def build_handler_catalog(wb: Workbook, signals: list[dict], overrides: dict) -> None:
    ws = wb.create_sheet("03_SW_Handler_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "SW Handler Catalog")
    note = ws.cell(row=2, column=1, value="Per signal: SW handler function name, allocated SWC, calling RTOS task, call frequency, max execution time budget, return type. This is the contract for SW implementation.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, [
        "Signal Name", "Handler Function Name", "Allocated SWC", "RTOS Task ID",
        "Call Frequency", "Max Execution Time (us)", "Return Type", "Notes"
    ])

    by_name = {o["signal_name"]: o for o in overrides}
    row = 5
    handler_count = 0
    for sig in signals:
        override = by_name.get(sig["signal_name"], {})
        handler_name = override.get("handler", f"sw_handle_{sig['signal_name'].replace('.', '_')}")
        ws.cell(row=row, column=1, value=sig["signal_name"])
        ws.cell(row=row, column=2, value=handler_name)
        ws.cell(row=row, column=3, value=override.get("swc", "SWC_TBD"))
        ws.cell(row=row, column=4, value=override.get("task", "T_TBD"))
        ws.cell(row=row, column=5, value=override.get("frequency", "event-driven"))
        ws.cell(row=row, column=6, value=override.get("max_exec_us", ""))
        ws.cell(row=row, column=7, value=override.get("return_type", "fault_status_t"))
        ws.cell(row=row, column=8, value="")
        handler_count += 1
        row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 8)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 32, 2: 32, 3: 14, 4: 12, 5: 16, 6: 20, 7: 16, 8: 30})

    return handler_count


def build_debounce_strategy(wb: Workbook, signals: list[dict], overrides: dict) -> None:
    ws = wb.create_sheet("04_Debounce_Strategy_per_Signal")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Debounce Strategy per Signal")
    note = ws.cell(row=2, column=1, value="Per safety signal: debounce method (N-of-M / time-based / hysteresis / leaky-bucket), parameters, rationale, false-positive risk percentage.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, [
        "Signal Name", "Debounce Method", "Parameters", "Rationale", "False-Positive Risk (%)", "Validation Approach", "Notes"
    ])

    by_name = {o["signal_name"]: o for o in overrides}
    row = 5
    for sig in signals:
        override = by_name.get(sig["signal_name"], {})
        ws.cell(row=row, column=1, value=sig["signal_name"])
        ws.cell(row=row, column=2, value=override.get("debounce", "N-of-M"))
        ws.cell(row=row, column=3, value=override.get("debounce_params", "3-of-5"))
        ws.cell(row=row, column=4, value=override.get("debounce_rationale", "<TBD>"))
        ws.cell(row=row, column=5, value=override.get("false_positive_risk", ""))
        ws.cell(row=row, column=6, value=override.get("validation_approach", "<TBD>"))
        ws.cell(row=row, column=7, value="")
        row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 7)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 32, 2: 18, 3: 18, 4: 30, 5: 18, 6: 28, 7: 30})


def build_fault_propagation(wb: Workbook, signals: list[dict], failure_modes: dict) -> None:
    ws = wb.create_sheet("05_Fault_Propagation_Maps")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Fault Propagation Maps")
    note = ws.cell(row=2, column=1, value="Per signal fault: detection point → fault flag set → propagation path through SWCs → vehicle reaction.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, [
        "Signal Name", "Fault Mode", "Detection Handler", "Fault Flag Set", "SWC Propagation Chain", "Vehicle Reaction"
    ])

    row = 5
    for sig in signals:
        faults = failure_modes.get(sig["signal_name"], ["Stuck-at 0", "Stuck-at 1", "Missing", "Late"])
        for idx, fault in enumerate(faults):
            if idx == 0:
                ws.cell(row=row, column=1, value=sig["signal_name"])
            ws.cell(row=row, column=2, value=fault)
            ws.cell(row=row, column=3, value=f"sw_handle_{sig['signal_name'].replace('.', '_')}")
            ws.cell(row=row, column=4, value=f"{sig['signal_name']}_fault")
            ws.cell(row=row, column=5, value="<TBD: SWC chain>")
            ws.cell(row=row, column=6, value="<TBD: vehicle reaction>")
            row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 6)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 32, 2: 18, 3: 28, 4: 28, 5: 32, 6: 32})


def build_rtos_integration(wb: Workbook, signals: list[dict], overrides: dict) -> None:
    ws = wb.create_sheet("06_RTOS_Integration")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "RTOS Integration")
    note = ws.cell(row=2, column=1, value="Per signal: RTOS task ID, task period (ms), task priority, latency from signal arrival to handler execution (ms), jitter budget (ms).")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, [
        "Signal Name", "RTOS Task ID", "Task Period (ms)", "Task Priority", "Latency to Handler (ms)", "Jitter Budget (ms)", "Notes"
    ])

    by_name = {o["signal_name"]: o for o in overrides}
    row = 5
    for sig in signals:
        override = by_name.get(sig["signal_name"], {})
        ws.cell(row=row, column=1, value=sig["signal_name"])
        ws.cell(row=row, column=2, value=override.get("task", "T_TBD"))
        ws.cell(row=row, column=3, value=override.get("task_period_ms", ""))
        ws.cell(row=row, column=4, value=override.get("task_priority", ""))
        ws.cell(row=row, column=5, value=override.get("latency_to_handler_ms", ""))
        ws.cell(row=row, column=6, value=override.get("jitter_budget_ms", ""))
        ws.cell(row=row, column=7, value="")
        row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 7)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 32, 2: 14, 3: 16, 4: 14, 5: 22, 6: 16, 7: 30})


def build_init_sequence(wb: Workbook) -> None:
    ws = wb.create_sheet("07_Init_Sequence_SW_Side")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "SW-side Initialization Sequence")
    note = ws.cell(row=2, column=1, value="SW startup sequence: phase, SWCs activated, HSI register reads, self-test handler calls, fault behavior on init failure.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=5)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["Phase", "SWCs Activated", "HSI Register Reads / Init Values", "Self-Test Handler Calls", "Fault Behavior"])

    init_rows = [
        ("Pre-RTOS", "Safety Monitor", "Read HSI signal validity bits; validate HW register lock state", "hsi_selftest_validity_bits()", "Log fault; set fault flag if HW not ready"),
        ("RTOS Startup", "Safety Monitor + Main App", "Clear liveness counters; initialize fault flags to nominal", "hsi_init_liveness_counters()", "Stop startup; request safe state if init fails"),
        ("Normal Operation Hand-shake", "All SWCs", "Poll HSI signals at task rate", "Per-signal handlers per RTOS schedule", "Propagate detected faults per fault chain"),
    ]

    row = 5
    for phase, swcs, reads, tests, fault_behavior in init_rows:
        ws.cell(row=row, column=1, value=phase)
        ws.cell(row=row, column=2, value=swcs)
        ws.cell(row=row, column=3, value=reads)
        ws.cell(row=row, column=4, value=tests)
        ws.cell(row=row, column=5, value=fault_behavior)
        row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 5)
    autosize(ws, {1: 28, 2: 28, 3: 40, 4: 40, 5: 40})


def build_test_cases(wb: Workbook, signals: list[dict]) -> None:
    ws = wb.create_sheet("08_Test_Cases")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Test Cases per Signal Handler")
    note = ws.cell(row=2, column=1, value="Per handler: nominal operation, fault injection, boundary/edge, timing edge case (max latency, jitter), integration with dependent SWCs.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, [
        "Handler Function", "Test Type", "Input / Condition", "Expected Output / Behavior", "Pass/Fail Criteria", "Notes"
    ])

    test_types = ["Nominal", "Fault Injection (stuck-at)", "Boundary (edge values)", "Timing (max latency + jitter)", "Integration"]
    row = 5
    for sig in signals:
        handler = f"sw_handle_{sig['signal_name'].replace('.', '_')}"
        for idx, test_type in enumerate(test_types):
            if idx == 0:
                ws.cell(row=row, column=1, value=handler)
            else:
                ws.cell(row=row, column=1, value="")
            ws.cell(row=row, column=2, value=test_type)
            ws.cell(row=row, column=3, value="<TBD: test input>")
            ws.cell(row=row, column=4, value="<TBD: expected output>")
            ws.cell(row=row, column=5, value="<TBD: pass criteria>")
            ws.cell(row=row, column=6, value="")
            row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, 6)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 32, 2: 20, 3: 32, 4: 32, 5: 28, 6: 30})


def build_c_header_stub(wb: Workbook, signals: list[dict], overrides: dict) -> None:
    ws = wb.create_sheet("09_C_Header_Stub")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "C Header Function Declarations (Preview; see .h file for full content)")

    code_preview = "// Auto-generated SW handler function declarations\n// See <output>_sw_handlers.h for full content\n\n"
    by_name = {o["signal_name"]: o for o in overrides}
    for sig in signals:
        override = by_name.get(sig["signal_name"], {})
        handler = override.get("handler", f"sw_handle_{sig['signal_name'].replace('.', '_')}")
        swc = override.get("swc", "SWC_TBD")
        task = override.get("task", "T_TBD")
        max_exec = override.get("max_exec_us", "")
        return_type = override.get("return_type", "fault_status_t")
        code_preview += f"/* Signal: {sig['signal_name']}\n"
        code_preview += f" * SWC: {swc} | Task: {task}\n"
        if max_exec:
            code_preview += f" * Max execution: {max_exec} us\n"
        code_preview += f" */\n"
        code_preview += f"{return_type} {handler}(const hsi_signal_t* hsi);\n\n"

    ws.cell(row=2, column=1, value=code_preview).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    ws.cell(row=2, column=1).font = Font(name="Courier New", size=9)
    ws.row_dimensions[2].height = 400
    ws.column_dimensions["A"].width = 100


def build_references(wb: Workbook, refinement: dict, hsi_path: str) -> None:
    ws = wb.create_sheet("10_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References")

    refs_text = f"""
Linked Documents:
- HSI (HW-side): {hsi_path}
- SW Architecture: {refinement.get('linked_sw_arch', '(not provided)')}

Standards and Guidelines:
- ISO 26262:2018 Part 6, Section 7 — Software implementation recommendations (debouncing, fault handling, RTOS integration)
- ISO 26262:2018 Part 4, Section 6.4.6 — Technical safety concept (HSI specification and verification)
- AUTOSAR Specification (if applicable) — task scheduling, signal handling patterns

Reference Docs (included in skill):
- references/methodology.md — SW-HSI structure, debouncing rationale, fault propagation chains, RTOS scheduling
- references/debouncing_patterns.md — N-of-M, time-based, hysteresis, leaky-bucket filter comparison and parameter selection

Generated Artifacts:
- This xlsx workbook (SW-HSI specification)
- <output>_sw_handlers.h — C header file with handler function declarations
"""

    ws.cell(row=2, column=1, value=refs_text).alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    ws.cell(row=2, column=1).font = body_font()
    ws.row_dimensions[2].height = 300
    ws.column_dimensions["A"].width = 100


def generate_c_header(output_path: Path, signals: list[dict], overrides: dict) -> None:
    """Generate C header file with handler function declarations."""
    header_path = output_path.parent / f"{output_path.stem}_sw_handlers.h"

    by_name = {o["signal_name"]: o for o in overrides}

    with open(header_path, "w") as f:
        f.write("""/**
 * @file <output>_sw_handlers.h
 * @brief Auto-generated SW-HSI handler function declarations
 *
 * Generated by sw-hsis-builder skill.
 * ISO 26262-6 Section 7 + ISO 26262-4 Section 6.4.6
 */

#ifndef SW_HANDLERS_H
#define SW_HANDLERS_H

#include <stdint.h>

/* Placeholder for HSI signal type */
typedef struct {
    uint32_t signal_value;
    uint8_t valid;
} hsi_signal_t;

/* Placeholder for fault status return type */
typedef enum {
    FAULT_STATUS_OK = 0,
    FAULT_STATUS_FAULT_DETECTED = 1,
    FAULT_STATUS_INIT_FAIL = 2,
} fault_status_t;

""")

        for sig in signals:
            override = by_name.get(sig["signal_name"], {})
            handler = override.get("handler", f"sw_handle_{sig['signal_name'].replace('.', '_')}")
            swc = override.get("swc", "SWC_TBD")
            task = override.get("task", "T_TBD")
            max_exec = override.get("max_exec_us", "")
            return_type = override.get("return_type", "fault_status_t")
            debounce = override.get("debounce", "N-of-M")
            debounce_params = override.get("debounce_params", "3-of-5")

            f.write(f"""/**
 * Handler for HSI signal: {sig['signal_name']}
 * Allocated SWC: {swc}
 * Called by: {task}
 * Debounce: {debounce} ({debounce_params})
""")
            if max_exec:
                f.write(f" * Max execution: {max_exec} us\n")
            f.write(f" */\n")
            f.write(f"{return_type} {handler}(const hsi_signal_t* hsi);\n\n")

        f.write("""
#endif /* SW_HANDLERS_H */
""")


def main():
    if len(sys.argv) != 4:
        print("Usage: python generate_sw_hsis.py <hsi.xlsx> <refinement.json> <output.xlsx>")
        sys.exit(1)

    hsi_path = sys.argv[1]
    refinement_path = sys.argv[2]
    output_path = sys.argv[3]

    # Load HSI
    try:
        signals = read_hsi_signals(hsi_path)
    except Exception as e:
        print(f"Error reading HSI: {e}")
        sys.exit(1)

    timing = read_hsi_timing(hsi_path)
    failure_modes = read_hsi_failure_modes(hsi_path)

    # Load refinement
    try:
        with open(refinement_path, "r") as f:
            refinement = json.load(f)
    except Exception as e:
        print(f"Error reading refinement JSON: {e}")
        sys.exit(1)

    overrides = refinement.get("handler_overrides", [])

    # Create workbook
    wb = Workbook()
    if wb.sheetnames and "Sheet" in wb.sheetnames:
        wb.remove(wb["Sheet"])

    # Build tabs
    build_title_page(wb, refinement, hsi_path)
    build_doc_control(wb)
    build_signal_catalog_echo(wb, signals)
    handler_count = build_handler_catalog(wb, signals, overrides)
    build_debounce_strategy(wb, signals, overrides)
    build_fault_propagation(wb, signals, failure_modes)
    build_rtos_integration(wb, signals, overrides)
    build_init_sequence(wb)
    build_test_cases(wb, signals)
    build_c_header_stub(wb, signals, overrides)
    build_references(wb, refinement, hsi_path)

    # Save workbook
    wb.save(output_path)
    print(f"SW-HSI workbook saved: {output_path}")
    print(f"Tabs: {len(wb.sheetnames)}, Handlers: {handler_count}")

    # Generate C header
    generate_c_header(Path(output_path), signals, overrides)
    header_path = Path(output_path).parent / f"{Path(output_path).stem}_sw_handlers.h"
    print(f"C header file saved: {header_path}")


if __name__ == "__main__":
    main()
