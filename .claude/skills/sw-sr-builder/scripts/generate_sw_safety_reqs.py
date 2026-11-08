"""
SW Safety Requirements Generator — generates a multi-tab ISO 26262-6 §6 Software Safety Requirements
workbook from a TSC xlsx (produced by tsc-builder) and optional project metadata JSON.

Usage:
    python generate_sw_safety_reqs.py <tsc.xlsx> <input.json> <output.xlsx>

Pipeline:
- Read SW-TSRs from TSC's 05_TSR_Catalog tab
- Read project metadata from input JSON (project, linked_tsc, sw_sr_overrides)
- For each SW-TSR: derive one or more SW-SRs from templates
- Scaffold failure mode mapping (standard SW modes per mechanism type)
- Pre-populate HSI reference signals from TSC's 06_HSI_Specification
- Generate verification methods per allocated ASIL
- Scaffold test strategy (unit test, integration test, back-to-back, fault injection, requirements coverage)
- Document independence requirements for decomposition pairs
- Output 11-tab xlsx workbook with complete traceability

See references/ for methodology and ISO 26262-6 §6 mapping.
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
# Reference tables
# ---------------------------------------------------------------------------

# Standard SW failure modes by mechanism type
SW_FAILURE_MODES = {
    "monitoring": [
        "Deadline miss (task overrun)",
        "Illegal state transition (state machine)",
        "Divide-by-zero exception",
        "Array index out of bounds",
        "Stack overflow",
        "Buffer overflow",
    ],
    "control": [
        "Control logic error (wrong branch)",
        "Lost update (race condition)",
        "Incorrect arithmetic (truncation, overflow)",
        "Deadlock (mutex hold cycle)",
        "Priority inversion",
        "Stale data read",
    ],
    "communication": [
        "Message lost or dropped",
        "Message late (timing miss)",
        "Message corrupted (checksum fail)",
        "Repeated or duplicated message",
        "Out-of-sequence message",
        "Lost handshake / acknowledgement",
    ],
    "memory": [
        "ECC error uncorrected (SECDED timeout)",
        "Memory corruption (wild write)",
        "Stack smash",
        "Heap fragmentation",
        "Memory leak",
        "Calibration data inconsistency",
    ],
    "diagnostic": [
        "Diagnostic flag not set",
        "Diagnostic flag latched (not cleared)",
        "Diagnostic timeout",
        "False positive diagnosis",
        "False negative diagnosis",
        "Diagnostic data loss",
    ],
}

# Verification methods per allocated ASIL (ISO 26262-6 Tables 7-10)
VERIFICATION_BY_ASIL = {
    "A": ["Review / Walkthrough / Inspection"],
    "B": ["Review / Walkthrough / Inspection", "Static analysis"],
    "C": ["Review / Walkthrough / Inspection", "Static analysis", "Control flow analysis", "Data flow analysis"],
    "D": ["Review / Walkthrough / Inspection", "Static analysis", "Control flow analysis", "Data flow analysis", "MC/DC", "Fault injection"],
    "QM": ["Review / Walkthrough / Inspection"],
}

# Test categories for SW
TEST_CATEGORIES = [
    "Unit Test (gtest / cmocka)",
    "Integration Test (HIL / SIL)",
    "Back-to-Back Testing (reference model vs implementation)",
    "Fault Injection (memory, timing, CPU)",
    "Requirements Coverage Analysis (traceability matrix)",
]

# Coupling factors for independence analysis (ISO 26262-9 §7)
COUPLING_FACTORS = [
    "Shared compilation unit (same .c/.o file)",
    "Shared header file (define macro conflicts)",
    "Shared task / process context",
    "Shared memory resource (global variable, static)",
    "Shared OS / scheduler state",
    "Shared interrupt handler",
    "Shared library or module",
    "Shared development team / code review process",
    "Shared testing environment",
    "Shared toolchain / compiler",
    "Shared debug/trace infrastructure",
    "Shared storage (Flash, ECC block)",
]

# ---------------------------------------------------------------------------
# Styling (same as tsc-builder for consistency)
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
# SW-SR Template Engine
# ---------------------------------------------------------------------------

def derive_sw_srs_from_tsr(sw_tsr: dict, overrides: dict = None) -> list[dict]:
    """
    Derives one or more SW-SRs from a single SW-TSR using templates.
    Returns list of SW-SR dicts with: id, text, allocated_swc, target_detection_time, failure_modes.
    """
    overrides = overrides or {}
    tsr_id = sw_tsr["tsr_id"]

    # Check for user override
    if tsr_id in overrides:
        override = overrides[tsr_id]
        return [{
            "id": f"{tsr_id}-SR-01",
            "text": override.get("sw_sr_text", sw_tsr["text"]),
            "allocated_swc": override.get("allocated_swc", "<TBD>"),
            "target_detection_time": override.get("target_detection_time", "1 cycle"),
            "failure_modes": SW_FAILURE_MODES.get("monitoring", []),
            "mechanism": sw_tsr["mechanism"],
            "asil": sw_tsr["asil"],
        }]

    # Otherwise, template-derive based on mechanism type
    mechanism = sw_tsr["mechanism"].lower()
    srs: list[dict] = []

    if "diagnostic" in mechanism or "debounce" in mechanism:
        # Diagnostic flag sampling, debounce, command safe state
        srs.append({
            "id": f"{tsr_id}-SR-01",
            "text": f"The SW shall sample the diagnostic flag signal every {'{period_ms}'} ms and buffer samples.",
            "allocated_swc": "<TBD: Diag_Monitor_SWC>",
            "target_detection_time": "<FDTI_budget>",
            "failure_modes": SW_FAILURE_MODES["diagnostic"],
            "mechanism": sw_tsr["mechanism"],
            "asil": sw_tsr["asil"],
        })
        srs.append({
            "id": f"{tsr_id}-SR-02",
            "text": f"The SW shall debounce the diagnostic flag with {'{N_consecutive}'} consecutive samples to filter transients.",
            "allocated_swc": "<TBD: Diag_Monitor_SWC>",
            "target_detection_time": "<FDTI_budget>",
            "failure_modes": SW_FAILURE_MODES["diagnostic"],
            "mechanism": sw_tsr["mechanism"],
            "asil": sw_tsr["asil"],
        })
        srs.append({
            "id": f"{tsr_id}-SR-03",
            "text": f"The SW shall command {'{safe_state}'} state within {'{FRTI_ms}'} ms of confirmed fault detection.",
            "allocated_swc": "<TBD: Actuator_Control_SWC>",
            "target_detection_time": "<FRTI_budget>",
            "failure_modes": SW_FAILURE_MODES["control"],
            "mechanism": sw_tsr["mechanism"],
            "asil": sw_tsr["asil"],
        })

    elif "monitor" in mechanism or "plausibility" in mechanism:
        # Value monitoring, threshold check, persistence timer
        srs.append({
            "id": f"{tsr_id}-SR-01",
            "text": f"The SW shall continuously evaluate {'{monitored_value}'} against {'{threshold}'} thresholds per cycle.",
            "allocated_swc": "<TBD: Monitor_SWC>",
            "target_detection_time": "1 cycle",
            "failure_modes": SW_FAILURE_MODES["monitoring"],
            "mechanism": sw_tsr["mechanism"],
            "asil": sw_tsr["asil"],
        })
        srs.append({
            "id": f"{tsr_id}-SR-02",
            "text": f"The SW shall declare fault if {'{monitored_value}'} deviates by > {'{tolerance}'} for > {'{persistence_ms}'} ms.",
            "allocated_swc": "<TBD: Monitor_SWC>",
            "target_detection_time": "<persistence_ms>",
            "failure_modes": SW_FAILURE_MODES["diagnostic"],
            "mechanism": sw_tsr["mechanism"],
            "asil": sw_tsr["asil"],
        })

    elif "watchdog" in mechanism or "deadline" in mechanism:
        # Watchdog service, deadline monitoring
        srs.append({
            "id": f"{tsr_id}-SR-01",
            "text": f"The SW shall service the watchdog within every {'{window_ms}'} ms window.",
            "allocated_swc": "<TBD: Watchdog_Service_SWC>",
            "target_detection_time": "<window_ms>",
            "failure_modes": SW_FAILURE_MODES["monitoring"],
            "mechanism": sw_tsr["mechanism"],
            "asil": sw_tsr["asil"],
        })
        srs.append({
            "id": f"{tsr_id}-SR-02",
            "text": f"The SW shall transition to safe state upon watchdog timeout expiration.",
            "allocated_swc": "<TBD: Watchdog_Handler_SWC>",
            "target_detection_time": "1 WDT cycle",
            "failure_modes": SW_FAILURE_MODES["control"],
            "mechanism": sw_tsr["mechanism"],
            "asil": sw_tsr["asil"],
        })

    elif "ecc" in mechanism or "memory" in mechanism:
        # ECC error handling, memory diagnostics
        srs.append({
            "id": f"{tsr_id}-SR-01",
            "text": f"The SW shall detect and log single-bit ECC errors on every RAM read access.",
            "allocated_swc": "<TBD: Memory_Handler_SWC>",
            "target_detection_time": "1 access",
            "failure_modes": SW_FAILURE_MODES["memory"],
            "mechanism": sw_tsr["mechanism"],
            "asil": sw_tsr["asil"],
        })
        srs.append({
            "id": f"{tsr_id}-SR-02",
            "text": f"The SW shall execute ECC error handler within 1 cycle; transition to safe state if uncorrectable.",
            "allocated_swc": "<TBD: Memory_Handler_SWC>",
            "target_detection_time": "1 cycle",
            "failure_modes": SW_FAILURE_MODES["memory"],
            "mechanism": sw_tsr["mechanism"],
            "asil": sw_tsr["asil"],
        })

    else:
        # Generic fallback
        srs.append({
            "id": f"{tsr_id}-SR-01",
            "text": f"[Derived from SW-TSR {tsr_id}] Specify SW component, algorithm, inputs, thresholds, and verification method.",
            "allocated_swc": "<TBD>",
            "target_detection_time": "<TBD>",
            "failure_modes": ["<TBD: identify failure modes to be addressed>"],
            "mechanism": sw_tsr["mechanism"],
            "asil": sw_tsr["asil"],
        })

    return srs


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, project: dict, tsc_path: str) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "Software Safety Requirements (SW-SR)")
    style_title_row(ws, 3, 4, project.get("name", ""))
    fields = [
        ("Project", project.get("name", "")),
        ("SW-SR Document ID", project.get("doc_id", "")),
        ("Revision", project.get("revision", "")),
        ("Date", project.get("date", "")),
        ("Author", project.get("author", "")),
        ("Approver", project.get("approver", "")),
        ("Linked TSC", tsc_path),
        ("Standard", "ISO 26262:2018, Part 6, Clause 6 (Specification of Software Safety Requirements)"),
        ("Methodology", "Per-SW-TSR derivation of SW-SRs via templates. One or more SW-SRs per SW-TSR addressing failure modes, detection time, allocated SW components, and verification methods."),
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
        ("0.1", "", "", "Initial draft generated by sw-sr-builder skill", ""),
        ("0.2", "", "", "Code review and unit test plan incorporated", ""),
        ("1.0", "", "", "Released to Software Detailed Design", ""),
    ], start=4):
        for c, v in enumerate(row, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 6, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_sw_tsrs_imported(wb: Workbook, sw_tsrs: list[dict], tsc_path: str) -> None:
    ws = wb.create_sheet("02_SW_TSRs_From_TSC")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Software Technical Safety Requirements — Imported from TSC")
    note = ws.cell(row=2, column=1, value=f"Source: {tsc_path}. Read-only echo for traceability.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 24

    style_header_row(ws, 4, ["SW-TSR_ID", "FSR_ID", "ASIL", "Mechanism", "Mechanism Name", "Linked Node", "Requirement Text"])
    for i, t in enumerate(sw_tsrs, start=5):
        ws.cell(row=i, column=1, value=t["tsr_id"])
        ws.cell(row=i, column=2, value=t["fsr_id"])
        cell = ws.cell(row=i, column=3, value=t["asil"])
        asil_color_cell(cell, t["asil"])
        ws.cell(row=i, column=4, value=t["mechanism"])
        ws.cell(row=i, column=5, value="<TBD: mechanism description>")
        ws.cell(row=i, column=6, value="<TBD: SW node ref>")
        ws.cell(row=i, column=7, value=t["text"])
    end_row = 4 + len(sw_tsrs)
    for r in range(5, end_row + 1):
        for c in range(1, 8):
            cell = ws.cell(row=r, column=c)
            if c != 3:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    autosize(ws, {1: 16, 2: 12, 3: 10, 4: 12, 5: 32, 6: 26, 7: 70})


def build_sw_safety_requirements(wb: Workbook, sw_srs_all: list[dict]) -> None:
    ws = wb.create_sheet("03_SW_Safety_Requirements")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "Software Safety Requirements")
    note = ws.cell(row=2, column=1, value="One or more SW-SRs derived per SW-TSR. Allocate to SW components, refine detection times per architecture.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)
    ws.row_dimensions[2].height = 24

    style_header_row(ws, 4, ["SW-SR_ID", "Parent SW-TSR", "ASIL", "Allocated SW Component", "Requirement Text", "Addressed Failure Modes", "Target Detection Time", "Verification Method", "Test Strategy"])
    row = 5
    for sr in sw_srs_all:
        ws.cell(row=row, column=1, value=sr["id"])
        ws.cell(row=row, column=2, value=sr.get("parent_tsr", ""))
        cell = ws.cell(row=row, column=3, value=sr["asil"])
        asil_color_cell(cell, sr["asil"])
        ws.cell(row=row, column=4, value=sr["allocated_swc"])
        ws.cell(row=row, column=5, value=sr["text"])
        ws.cell(row=row, column=6, value="; ".join(sr.get("failure_modes", [])))
        ws.cell(row=row, column=7, value=sr.get("target_detection_time", ""))
        ws.cell(row=row, column=8, value="<TBD>")
        ws.cell(row=row, column=9, value="<TBD>")
        row += 1
    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 10):
            cell = ws.cell(row=r, column=c)
            if c != 3:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    autosize(ws, {1: 14, 2: 16, 3: 10, 4: 20, 5: 60, 6: 50, 7: 18, 8: 24, 9: 24})


def build_failure_mode_mapping(wb: Workbook, sw_srs_all: list[dict]) -> None:
    ws = wb.create_sheet("04_Failure_Mode_Mapping")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 15, "Failure Mode Mapping per SW-SR")
    note = ws.cell(row=2, column=1, value="Which SW failure modes does each SW-SR address? Mark with X or coverage detail.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=15)

    # Collect all unique failure modes across all SW-SRs
    all_modes = set()
    for sr in sw_srs_all:
        all_modes.update(sr.get("failure_modes", []))
    all_modes = sorted(list(all_modes))

    headers = ["SW-SR_ID"] + all_modes[:13]  # Limit to 14 cols total
    style_header_row(ws, 4, headers)
    row = 5
    for sr in sw_srs_all:
        ws.cell(row=row, column=1, value=sr["id"])
        sr_modes = set(sr.get("failure_modes", []))
        for col, mode in enumerate(all_modes[:13], start=2):
            cell = ws.cell(row=row, column=col, value="X" if mode in sr_modes else "")
            cell.alignment = Alignment(horizontal="center")
        row += 1
    end_row = row - 1
    stripe_body(ws, 5, end_row, 14)
    autosize(ws, {1: 14, **{i: 12 for i in range(2, 15)}})


def build_hsi_reference(wb: Workbook, sw_srs_all: list[dict]) -> None:
    ws = wb.create_sheet("05_HSI_Reference")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "HSI Reference — Software-Owned Signals")
    note = ws.cell(row=2, column=1, value="Cross-reference: which HSI signals are consumed/produced by SW for each SW-SR? Fill in signal names from TSC HSI spec.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["SW-SR_ID", "Signal Direction (Input/Output/Diag)", "HSI Signal Name", "Encoding", "Update Rate", "Integrity Protection"])
    row = 5
    for sr in sw_srs_all:
        ws.cell(row=row, column=1, value=sr["id"])
        ws.cell(row=row, column=2, value="Input / Output / Diagnostic")
        ws.cell(row=row, column=3, value=f"<TBD: esc.sw.{sr['id'].lower()}>")
        ws.cell(row=row, column=4, value="<TBD: encoding>")
        ws.cell(row=row, column=5, value="<TBD: update_rate>")
        ws.cell(row=row, column=6, value="Parity / CRC / Timestamp")
        row += 1
    end_row = row - 1
    stripe_body(ws, 5, end_row, 6)
    autosize(ws, {1: 14, 2: 32, 3: 32, 4: 20, 5: 18, 6: 22})


def build_verification_methods(wb: Workbook, sw_srs_all: list[dict]) -> None:
    ws = wb.create_sheet("06_Verification_Methods_per_ASIL")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "Verification Methods per SW-SR and Allocated ASIL")
    note = ws.cell(row=2, column=1, value="++ = strongly recommended; + = acceptable supplementary. Per ISO 26262-6 Tables 7-10.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)

    style_header_row(ws, 4, ["SW-SR_ID", "ASIL", "Review / Walkthrough", "Static Analysis", "Control Flow Analysis", "Data Flow Analysis", "MC/DC", "Fault Injection"])
    row = 5
    for sr in sw_srs_all:
        base_asil = sr["asil"].split("(")[0].strip() if sr["asil"] else "QM"
        methods = VERIFICATION_BY_ASIL.get(base_asil, ["Review / Walkthrough / Inspection"])

        ws.cell(row=row, column=1, value=sr["id"])
        cell = ws.cell(row=row, column=2, value=sr["asil"])
        asil_color_cell(cell, sr["asil"])
        for col, method in enumerate(["Review / Walkthrough / Inspection", "Static analysis", "Control flow analysis", "Data flow analysis", "MC/DC", "Fault injection"], start=3):
            mark = "++" if method in methods else "+" if method in ["Review / Walkthrough / Inspection"] else ""
            ws.cell(row=row, column=col, value=mark)
            ws.cell(row=row, column=col).alignment = Alignment(horizontal="center")
        row += 1
    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 9):
            cell = ws.cell(row=r, column=c)
            if c != 2:
                cell.font = body_font()
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    autosize(ws, {1: 14, 2: 10, 3: 18, 4: 16, 5: 18, 6: 18, 7: 12, 8: 16})


def build_misra_mapping(wb: Workbook, sw_srs_all: list[dict]) -> None:
    ws = wb.create_sheet("07_MISRA_Mapping")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "MISRA C:2012 Compliance Mapping")
    note = ws.cell(row=2, column=1, value="Per SW-SR: relevant MISRA C:2012 rule categories. Use as coding standard reference during implementation and review.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=4)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["SW-SR_ID", "MISRA Category (e.g., Pointer use, Memory alloc, Loops, Recursion)", "Applicable Rules", "Notes"])
    row = 5
    misra_categories = [
        "No dynamic memory (malloc/free prohibited)",
        "No function pointers or pointer arithmetic",
        "No recursion (bounded call depth)",
        "Loop iteration count bounded (static analysis verifiable)",
        "No volatile or implicit conversions",
        "No indirect function calls",
    ]
    for sr in sw_srs_all:
        ws.cell(row=row, column=1, value=sr["id"])
        ws.cell(row=row, column=2, value="; ".join(misra_categories[:3]))
        ws.cell(row=row, column=3, value="<TBD: cite MISRA C:2012 rule IDs>")
        ws.cell(row=row, column=4, value="<TBD: implementation notes>")
        row += 1
    end_row = row - 1
    stripe_body(ws, 5, end_row, 4)
    autosize(ws, {1: 14, 2: 50, 3: 32, 4: 50})


def build_test_strategy(wb: Workbook, sw_srs_all: list[dict]) -> None:
    ws = wb.create_sheet("08_Test_Strategy")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Test Strategy — Test Categories and Coverage")
    note = ws.cell(row=2, column=1, value="Which SW-SRs are addressed by each test category?")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)

    style_header_row(ws, 4, ["Test Category", "Description", "Applicable SW-SRs", "Test Specification", "Acceptance Criteria", "Owner"])
    row = 5
    for cat in TEST_CATEGORIES:
        ws.cell(row=row, column=1, value=cat)
        ws.cell(row=row, column=2, value=f"<TBD: {cat.lower()}>")
        ws.cell(row=row, column=3, value="<TBD: select applicable SW-SRs>")
        ws.cell(row=row, column=4, value="<TBD: reference test spec>")
        ws.cell(row=row, column=5, value="<TBD: pass/fail criteria>")
        ws.cell(row=row, column=6, value="<TBD>")
        row += 1
    end_row = row - 1
    stripe_body(ws, 5, end_row, 6)
    autosize(ws, {1: 32, 2: 36, 3: 32, 4: 28, 5: 32, 6: 18})


def build_independence_considerations(wb: Workbook) -> None:
    ws = wb.create_sheet("09_Independence_Considerations")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Independence Considerations — ASIL Decomposition")
    note = ws.cell(row=2, column=1, value="When ASIL decomposition cascades from TSC to SW, document independence per ISO 26262-9 §7 coupling factors.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["Decomposition Pair", "Coupling Factor", "Coupling Present?", "Mitigation", "Evidence", "Status"])
    row = 5
    for i, cf in enumerate(COUPLING_FACTORS[:8], start=1):  # Show first 8 examples
        if i == 1:
            ws.cell(row=row, column=1, value="<Decomposition SG / Channel A vs. Channel B>")
        ws.cell(row=row, column=2, value=cf)
        ws.cell(row=row, column=3, value="<Yes / No>")
        ws.cell(row=row, column=4, value="<TBD: cite mitigation>")
        ws.cell(row=row, column=5, value="<TBD: code review, static analysis, unit test>")
        ws.cell(row=row, column=6, value="<TBD>")
        row += 1
    end_row = row - 1
    stripe_body(ws, 5, end_row, 6)
    autosize(ws, {1: 32, 2: 28, 3: 16, 4: 36, 5: 36, 6: 18})


def build_references(wb: Workbook, tsc_path: str) -> None:
    ws = wb.create_sheet("10_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "References and Traceability")
    refs = [
        ("Linked TSC", tsc_path),
        ("ISO 26262-6:2018", "Product development at the software level, Clause 6 (SW-SR specification)"),
        ("ISO 26262-9:2018", "Functional Safety Management, Clause 7 (Dependent Failure Analysis)"),
        ("MISRA C:2012", "Guidelines for the use of the C language in critical systems"),
        ("Requirement", "Description / Citation"),
    ]
    row = 3
    for label, value in refs:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=value).font = body_font()
        ws.cell(row=row, column=2).alignment = Alignment(wrap_text=True)
        row += 1
    autosize(ws, {1: 28, 2: 80})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(tsc_path: str, input_path: str, output_path: str) -> dict:
    """Generate SW-SR workbook from TSC + input JSON."""

    # Read TSC
    tsc_data = read_tsc(tsc_path)

    # Read input JSON
    with open(input_path) as f:
        input_data = json.load(f)

    project = input_data.get("project", {})
    overrides_list = input_data.get("sw_sr_overrides", [])

    # Convert overrides list to dict keyed by parent_sw_tsr
    overrides_dict = {}
    for override in overrides_list:
        parent = override.get("parent_sw_tsr")
        if parent:
            overrides_dict[parent] = override

    # Derive SW-SRs from SW-TSRs
    sw_srs_all: list[dict] = []
    for sw_tsr in tsc_data["sw_tsrs"]:
        srs = derive_sw_srs_from_tsr(sw_tsr, overrides_dict)
        for sr in srs:
            sr["parent_tsr"] = sw_tsr["tsr_id"]
        sw_srs_all.extend(srs)

    # Create workbook
    wb = Workbook()
    wb.remove(wb.active)

    # Build tabs
    build_title_page(wb, project, tsc_path)
    build_doc_control(wb)
    build_sw_tsrs_imported(wb, tsc_data["sw_tsrs"], tsc_path)
    build_sw_safety_requirements(wb, sw_srs_all)
    build_failure_mode_mapping(wb, sw_srs_all)
    build_hsi_reference(wb, sw_srs_all)
    build_verification_methods(wb, sw_srs_all)
    build_misra_mapping(wb, sw_srs_all)
    build_test_strategy(wb, sw_srs_all)
    build_independence_considerations(wb)
    build_references(wb, tsc_path)

    wb.active = 0
    wb.save(output_path)

    return {
        "sw_tsrs_imported": len(tsc_data["sw_tsrs"]),
        "sw_srs_derived": len(sw_srs_all),
        "tabs": 11,
        "output_path": output_path,
    }


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_sw_safety_reqs.py <tsc.xlsx> <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(summary, indent=2))
