"""
HW Safety Requirements Generator — generates a multi-tab ISO 26262-5 §6 Hardware Safety Requirements
workbook from a TSC xlsx (produced by tsc-builder) and optional project metadata JSON.

Usage:
    python generate_hw_safety_reqs.py <tsc.xlsx> <input.json> <output.xlsx>

Pipeline:
- Read HW-TSRs from TSC's 05_TSR_Catalog tab
- Read project metadata from input JSON (project, linked_tsc, hw_sr_overrides)
- For each HW-TSR: derive one or more HW-SRs from templates
- Scaffold failure mode mapping (standard modes per mechanism type)
- Pre-populate HSI reference signals from TSC's 06_HSI_Specification
- Generate verification methods per allocated ASIL
- Scaffold test strategy (HIL, fault injection, electrical, environmental, accelerated life)
- Document independence requirements for decomposition pairs
- Output 10-tab xlsx workbook with complete traceability

See references/ for methodology and ISO 26262-5 §6 mapping.
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

# Standard failure modes by mechanism type / hardware subsystem
FAILURE_MODES = {
    "sensing": [
        "No output (open circuit, sensor failure)",
        "Stuck output (signal frozen at one value)",
        "Drifted output (calibration shift over temperature)",
        "Noisy output (high-frequency jitter)",
        "Out-of-range output (exceeds min/max)",
    ],
    "monitoring": [
        "Stuck-at fault (processor state frozen)",
        "Transient bit flip (SEU in register/memory)",
        "Lockstep mismatch (cores diverge)",
        "Watchdog timeout (scheduler overload)",
        "Illegal opcode or memory access",
    ],
    "actuation": [
        "Open circuit (driver output stuck low/floating)",
        "Short to supply (unintended high state)",
        "Short to ground (unintended low state)",
        "Gate driver fault (bootstrap failure)",
        "Thermal shutdown (overtemperature)",
    ],
    "communication": [
        "Message lost (transmission failure)",
        "Message late (timing violation)",
        "Message corrupted (CRC/checksum failure)",
        "Repeated message (duplication error)",
        "Acknowledgement absent (receiver fault)",
    ],
}

# Verification methods per allocated ASIL (ISO 26262-4 Table 3)
VERIFICATION_BY_ASIL = {
    "A": ["Inspection"],
    "B": ["Inspection", "Electrical test"],
    "C": ["Inspection", "Electrical test", "Simulation"],
    "D": ["Inspection", "Electrical test", "Fault injection", "Simulation"],
    "QM": ["Inspection"],
}

# Test categories
TEST_CATEGORIES = [
    "HIL (Hardware-in-the-Loop)",
    "Fault Injection (electrical transients)",
    "Electrical Characterization (input/output, thermal)",
    "Environmental Testing (temperature, EMI, vibration)",
    "Accelerated Life Testing (reliability)",
]

# Coupling factors for independence analysis (ISO 26262-9 §7)
COUPLING_FACTORS = [
    "Shared supply voltage",
    "Shared ground",
    "Shared clock",
    "Shared bus",
    "Shared sensor input",
    "Shared memory resource",
    "Shared SW library",
    "Shared OS / scheduler",
    "Shared environmental zone",
    "Shared development team / process",
    "Shared compiler / toolchain",
    "Shared production / test process",
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
# HW-SR Template Engine
# ---------------------------------------------------------------------------

# Records which override keys were actually consumed during derivation, so that an
# override whose parent_hw_tsr does not exist in the TSC is reported instead of
# silently ignored. See docs/skill-polish-log/hw-safety-reqs-builder.md (2026-09-15).
OVERRIDES_APPLIED: set[str] = set()


def _suggest_near_matches(key: str, known_ids: list[str], limit: int = 3) -> list[str]:
    """Returns known TSR IDs that extend or are extended by `key` (ID-format drift)."""
    hits = [i for i in known_ids if i != key and (i.startswith(key) or key.startswith(i))]
    return hits[:limit]


def derive_hw_srs_from_tsr(hw_tsr: dict, overrides: dict = None) -> list[dict]:
    """
    Derives one or more HW-SRs from a single HW-TSR using templates.
    Returns list of HW-SR dicts with: id, text, allocated_element, target_dc, failure_modes.
    """
    overrides = overrides or {}
    tsr_id = hw_tsr["tsr_id"]

    # Check for user override
    if tsr_id in overrides:
        override = overrides[tsr_id]
        OVERRIDES_APPLIED.add(tsr_id)
        return [{
            "id": f"{tsr_id}-SR-01",
            "text": override.get("hw_sr_text", hw_tsr["text"]),
            "allocated_element": override.get("allocated_hw_element", "<TBD>"),
            "target_dc": override.get("target_dc_percent", 75),
            "failure_modes": FAILURE_MODES.get("sensing", []),  # default
            "mechanism": hw_tsr["mechanism"],
            "asil": hw_tsr["asil"],
        }]

    # Otherwise, template-derive based on mechanism type
    mechanism = hw_tsr["mechanism"].lower()
    srs: list[dict] = []

    if "range" in mechanism or "sm10" in mechanism:
        # Range/out-of-range check → sensing path
        srs.append({
            "id": f"{tsr_id}-SR-01",
            "text": f"The HW shall provide an ADC channel for sensor input with range 0-5V and ±5% accuracy.",
            "allocated_element": "<TBD: ADC_CHx>",
            "target_dc": 60,
            "failure_modes": FAILURE_MODES["sensing"],
            "mechanism": hw_tsr["mechanism"],
            "asil": hw_tsr["asil"],
        })
        srs.append({
            "id": f"{tsr_id}-SR-02",
            "text": f"The HW shall implement out-of-range comparator with thresholds set per calibration and assert fault within FDTI budget.",
            "allocated_element": "<TBD: CMP_01>",
            "target_dc": 75,
            "failure_modes": FAILURE_MODES["sensing"],
            "mechanism": hw_tsr["mechanism"],
            "asil": hw_tsr["asil"],
        })
        srs.append({
            "id": f"{tsr_id}-SR-03",
            "text": f"The HW shall route fault flag to safety MCU diagnostic input with parity integrity protection.",
            "allocated_element": "<TBD: MCU_GPIO>",
            "target_dc": 80,
            "failure_modes": ["Open circuit", "Short to supply"],
            "mechanism": hw_tsr["mechanism"],
            "asil": hw_tsr["asil"],
        })

    elif "lockstep" in mechanism or "sm01" in mechanism:
        # Dual-core lockstep → monitoring path
        srs.append({
            "id": f"{tsr_id}-SR-01",
            "text": f"The HW shall pair two processor cores with synchronized instruction streams and cycle-by-cycle lockstep.",
            "allocated_element": "<TBD: Core_A + Core_B>",
            "target_dc": 95,
            "failure_modes": FAILURE_MODES["monitoring"],
            "mechanism": hw_tsr["mechanism"],
            "asil": hw_tsr["asil"],
        })
        srs.append({
            "id": f"{tsr_id}-SR-02",
            "text": f"The HW shall detect mismatch in PC, register file, or memory writes within 1 cycle and assert mismatch flag.",
            "allocated_element": "<TBD: Comparator_logic>",
            "target_dc": 99,
            "failure_modes": FAILURE_MODES["monitoring"],
            "mechanism": hw_tsr["mechanism"],
            "asil": hw_tsr["asil"],
        })
        srs.append({
            "id": f"{tsr_id}-SR-03",
            "text": f"The HW shall route mismatch flag to independent watchdog timer for safe-state disable.",
            "allocated_element": "<TBD: Independent_WDT>",
            "target_dc": 99,
            "failure_modes": ["Watchdog timeout"],
            "mechanism": hw_tsr["mechanism"],
            "asil": hw_tsr["asil"],
        })

    elif "current" in mechanism or "feedback" in mechanism or "sm16" in mechanism:
        # Current feedback → actuation path
        srs.append({
            "id": f"{tsr_id}-SR-01",
            "text": f"The HW shall provide high-side or low-side current sense resistor/IC with ±5% accuracy.",
            "allocated_element": "<TBD: R_sense / INA_IC>",
            "target_dc": 70,
            "failure_modes": FAILURE_MODES["actuation"],
            "mechanism": hw_tsr["mechanism"],
            "asil": hw_tsr["asil"],
        })
        srs.append({
            "id": f"{tsr_id}-SR-02",
            "text": f"The HW shall digitize current feedback via dedicated ADC channel with >=12-bit resolution.",
            "allocated_element": "<TBD: ADC_CHx>",
            "target_dc": 75,
            "failure_modes": FAILURE_MODES["actuation"],
            "mechanism": hw_tsr["mechanism"],
            "asil": hw_tsr["asil"],
        })
        srs.append({
            "id": f"{tsr_id}-SR-03",
            "text": f"The HW shall implement closed-loop current plausibility check with expected range and deviation tolerance.",
            "allocated_element": "<TBD: Comparator_logic>",
            "target_dc": 80,
            "failure_modes": FAILURE_MODES["actuation"],
            "mechanism": hw_tsr["mechanism"],
            "asil": hw_tsr["asil"],
        })

    else:
        # Generic fallback
        srs.append({
            "id": f"{tsr_id}-SR-01",
            "text": f"[Derived from HW-TSR {tsr_id}] Specify allocated hardware element, inputs, thresholds, and diagnostic coverage.",
            "allocated_element": "<TBD>",
            "target_dc": 70,
            "failure_modes": ["<TBD: identify failure modes to be addressed>"],
            "mechanism": hw_tsr["mechanism"],
            "asil": hw_tsr["asil"],
        })

    return srs


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, project: dict, tsc_path: str) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "Hardware Safety Requirements (HW-SR)")
    style_title_row(ws, 3, 4, project.get("name", ""))
    fields = [
        ("Project", project.get("name", "")),
        ("HW-SR Document ID", project.get("doc_id", "")),
        ("Revision", project.get("revision", "")),
        ("Date", project.get("date", "")),
        ("Author", project.get("author", "")),
        ("Approver", project.get("approver", "")),
        ("Linked TSC", tsc_path),
        ("Standard", "ISO 26262:2018, Part 5, Clause 6 (Specification of Hardware Safety Requirements)"),
        ("Methodology", "Per-HW-TSR derivation of HW-SRs via templates. One or more HW-SRs per HW-TSR addressing failure modes, diagnostic coverage, allocated HW elements, and verification methods."),
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
        ("0.1", "", "", "Initial draft generated by hw-safety-reqs-builder skill", ""),
        ("0.2", "", "", "FMEDA refinement incorporated", ""),
        ("1.0", "", "", "Released to Hardware Detailed Design", ""),
    ], start=4):
        for c, v in enumerate(row, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 6, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_hw_tsrs_imported(wb: Workbook, hw_tsrs: list[dict], tsc_path: str) -> None:
    ws = wb.create_sheet("02_HW_TSRs_From_TSC")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Hardware Technical Safety Requirements — Imported from TSC")
    note = ws.cell(row=2, column=1, value=f"Source: {tsc_path}. Read-only echo for traceability.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 24

    style_header_row(ws, 4, ["HW-TSR_ID", "FSR_ID", "ASIL", "Mechanism", "Mechanism Name", "Linked Node", "Requirement Text"])
    for i, t in enumerate(hw_tsrs, start=5):
        ws.cell(row=i, column=1, value=t["tsr_id"])
        ws.cell(row=i, column=2, value=t["fsr_id"])
        cell = ws.cell(row=i, column=3, value=t["asil"])
        asil_color_cell(cell, t["asil"])
        ws.cell(row=i, column=4, value=t["mechanism"])
        ws.cell(row=i, column=5, value="<TBD: mechanism description>")
        ws.cell(row=i, column=6, value="<TBD: node ref>")
        ws.cell(row=i, column=7, value=t["text"])
    end_row = 4 + len(hw_tsrs)
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


def build_hw_safety_requirements(wb: Workbook, hw_srs_all: list[dict]) -> None:
    ws = wb.create_sheet("03_HW_Safety_Requirements")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "Hardware Safety Requirements")
    note = ws.cell(row=2, column=1, value="One or more HW-SRs derived per HW-TSR. Allocate to HW elements, refine DC% targets after FMEDA.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)
    ws.row_dimensions[2].height = 24

    style_header_row(ws, 4, ["HW-SR_ID", "Parent HW-TSR", "ASIL", "Allocated HW Element", "Requirement Text", "Addressed Failure Modes", "Target DC%", "Verification Method"])
    row = 5
    for sr in hw_srs_all:
        ws.cell(row=row, column=1, value=sr["id"])
        ws.cell(row=row, column=2, value=sr.get("parent_tsr", ""))
        cell = ws.cell(row=row, column=3, value=sr["asil"])
        asil_color_cell(cell, sr["asil"])
        ws.cell(row=row, column=4, value=sr["allocated_element"])
        ws.cell(row=row, column=5, value=sr["text"])
        ws.cell(row=row, column=6, value="; ".join(sr.get("failure_modes", [])))
        ws.cell(row=row, column=7, value=sr["target_dc"])
        ws.cell(row=row, column=8, value="<TBD>")
        row += 1
    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 9):
            cell = ws.cell(row=r, column=c)
            if c != 3:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    autosize(ws, {1: 14, 2: 16, 3: 10, 4: 20, 5: 60, 6: 50, 7: 10, 8: 24})


def build_failure_mode_mapping(wb: Workbook, hw_srs_all: list[dict]) -> None:
    ws = wb.create_sheet("04_Failure_Mode_Mapping")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 15, "Failure Mode Mapping per HW-SR")
    note = ws.cell(row=2, column=1, value="Which standard failure modes does each HW-SR address? Mark with X or DC% coverage.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=15)

    # Collect all unique failure modes across all HW-SRs
    all_modes = set()
    for sr in hw_srs_all:
        all_modes.update(sr.get("failure_modes", []))
    all_modes = sorted(list(all_modes))

    headers = ["HW-SR_ID"] + all_modes[:13]  # Limit to 14 cols total
    style_header_row(ws, 4, headers)
    row = 5
    for sr in hw_srs_all:
        ws.cell(row=row, column=1, value=sr["id"])
        sr_modes = set(sr.get("failure_modes", []))
        for col, mode in enumerate(all_modes[:13], start=2):
            cell = ws.cell(row=row, column=col, value="X" if mode in sr_modes else "")
            cell.alignment = Alignment(horizontal="center")
        row += 1
    end_row = row - 1
    stripe_body(ws, 5, end_row, 14)
    autosize(ws, {1: 14, **{i: 12 for i in range(2, 15)}})


def build_hsi_reference(wb: Workbook, hw_srs_all: list[dict]) -> None:
    ws = wb.create_sheet("05_HSI_Reference")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "HSI Reference — Hardware-owned Signals")
    note = ws.cell(row=2, column=1, value="Cross-reference: which HSI signals are owned by HW for sensing, diagnostics, or liveness? Fill in signal names from TSC HSI spec.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 32

    style_header_row(ws, 4, ["HW-SR_ID", "Signal Type (Diagnostic/Liveness)", "HSI Signal Name", "Encoding", "Update Rate", "Integrity Protection"])
    row = 5
    for sr in hw_srs_all:
        ws.cell(row=row, column=1, value=sr["id"])
        ws.cell(row=row, column=2, value="Diagnostic")
        ws.cell(row=row, column=3, value=f"<TBD: esc.diag.{sr['id'].lower()}>")
        ws.cell(row=row, column=4, value="1 bit + validity")
        ws.cell(row=row, column=5, value="<TBD: FDTI>")
        ws.cell(row=row, column=6, value="Parity / CRC")
        row += 1
    end_row = row - 1
    stripe_body(ws, 5, end_row, 6)
    autosize(ws, {1: 14, 2: 28, 3: 32, 4: 20, 5: 18, 6: 22})


def build_verification_methods(wb: Workbook, hw_srs_all: list[dict]) -> None:
    ws = wb.create_sheet("06_Verification_Methods")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Verification Methods per HW-SR and Allocated ASIL")
    note = ws.cell(row=2, column=1, value="++ = strongly recommended; + = acceptable supplementary. Per ISO 26262-4 Table 3.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)

    style_header_row(ws, 4, ["HW-SR_ID", "ASIL", "Inspection", "Electrical Test", "Fault Injection", "Simulation", "Environmental Test"])
    row = 5
    for sr in hw_srs_all:
        base_asil = sr["asil"].split("(")[0].strip() if sr["asil"] else "QM"
        methods = VERIFICATION_BY_ASIL.get(base_asil, ["Inspection"])

        ws.cell(row=row, column=1, value=sr["id"])
        cell = ws.cell(row=row, column=2, value=sr["asil"])
        asil_color_cell(cell, sr["asil"])
        for col, method in enumerate(["Inspection", "Electrical Test", "Fault Injection", "Simulation", "Environmental Test"], start=3):
            mark = "++" if method in methods else "+" if method in ["Inspection"] else ""
            ws.cell(row=row, column=col, value=mark)
            ws.cell(row=row, column=col).alignment = Alignment(horizontal="center")
        row += 1
    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 8):
            cell = ws.cell(row=r, column=c)
            if c != 2:
                cell.font = body_font()
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    autosize(ws, {1: 14, 2: 10, 3: 12, 4: 16, 5: 16, 6: 12, 7: 18})


def build_test_strategy(wb: Workbook, hw_srs_all: list[dict]) -> None:
    ws = wb.create_sheet("07_Test_Strategy")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Test Strategy — Test Categories and Coverage")
    note = ws.cell(row=2, column=1, value="Which HW-SRs are addressed by each test category?")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)

    style_header_row(ws, 4, ["Test Category", "Description", "Applicable HW-SRs", "Test Specification", "Acceptance Criteria", "Owner"])
    row = 5
    for cat in TEST_CATEGORIES:
        ws.cell(row=row, column=1, value=cat)
        ws.cell(row=row, column=2, value=f"<TBD: {cat.lower()}>")
        ws.cell(row=row, column=3, value="<TBD: select applicable HW-SRs>")
        ws.cell(row=row, column=4, value="<TBD: reference test spec>")
        ws.cell(row=row, column=5, value="<TBD: pass/fail criteria>")
        ws.cell(row=row, column=6, value="<TBD>")
        row += 1
    end_row = row - 1
    stripe_body(ws, 5, end_row, 6)
    autosize(ws, {1: 32, 2: 36, 3: 32, 4: 28, 5: 32, 6: 18})


def build_independence_considerations(wb: Workbook) -> None:
    ws = wb.create_sheet("08_Independence_Considerations")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Independence Considerations — ASIL Decomposition")
    note = ws.cell(row=2, column=1, value="When ASIL decomposition cascades from TSC to HW, document independence per ISO 26262-9 §7 coupling factors.")
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
        ws.cell(row=row, column=5, value="<TBD: FMEDA row, schematic, simulation>")
        ws.cell(row=row, column=6, value="<TBD>")
        row += 1
    end_row = row - 1
    stripe_body(ws, 5, end_row, 6)
    autosize(ws, {1: 32, 2: 28, 3: 16, 4: 36, 5: 36, 6: 18})


def build_references(wb: Workbook, tsc_path: str) -> None:
    ws = wb.create_sheet("09_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "References and Traceability")
    refs = [
        ("Linked TSC", tsc_path),
        ("ISO 26262-5:2018", "Product development at the hardware level, Clause 6 (HW-SR specification)"),
        ("ISO 26262-9:2018", "Functional Safety Management, Clause 7 (Dependent Failure Analysis)"),
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
    """Generate HW-SR workbook from TSC + input JSON."""

    # Read TSC
    tsc_data = read_tsc(tsc_path)

    # Read input JSON
    with open(input_path) as f:
        input_data = json.load(f)

    project = input_data.get("project", {})
    overrides_list = input_data.get("hw_sr_overrides", [])

    # Convert overrides list to dict keyed by parent_hw_tsr
    overrides_dict = {}
    for override in overrides_list:
        parent = override.get("parent_hw_tsr")
        if parent:
            overrides_dict[parent] = override

    # Derive HW-SRs from HW-TSRs
    hw_srs_all: list[dict] = []
    for hw_tsr in tsc_data["hw_tsrs"]:
        srs = derive_hw_srs_from_tsr(hw_tsr, overrides_dict)
        for sr in srs:
            sr["parent_tsr"] = hw_tsr["tsr_id"]
        hw_srs_all.extend(srs)

    # Create workbook
    wb = Workbook()
    wb.remove(wb.active)

    # Build tabs
    build_title_page(wb, project, tsc_path)
    build_doc_control(wb)
    build_hw_tsrs_imported(wb, tsc_data["hw_tsrs"], tsc_path)
    build_hw_safety_requirements(wb, hw_srs_all)
    build_failure_mode_mapping(wb, hw_srs_all)
    build_hsi_reference(wb, hw_srs_all)
    build_verification_methods(wb, hw_srs_all)
    build_test_strategy(wb, hw_srs_all)
    build_independence_considerations(wb)
    build_references(wb, tsc_path)

    wb.active = 0
    wb.save(output_path)

    # Report override outcomes. An override keyed on a parent_hw_tsr that the TSC does
    # not contain used to be dropped in silence, leaving the generic <TBD> template in
    # place while the run still exited 0 and looked successful.
    known_ids = [t["tsr_id"] for t in tsc_data["hw_tsrs"]]
    unmatched = [k for k in overrides_dict if k not in OVERRIDES_APPLIED]
    if unmatched:
        print(
            f"WARNING: {len(unmatched)} of {len(overrides_dict)} hw_sr_overrides matched no "
            f"HW-TSR in {tsc_path} and were NOT applied:",
            file=sys.stderr,
        )
        for k in unmatched:
            near = _suggest_near_matches(k, known_ids)
            hint = f"  did you mean: {', '.join(near)}" if near else "  no similar TSR_ID found"
            print(f"  - parent_hw_tsr '{k}'{hint}", file=sys.stderr)

    return {
        "hw_tsrs_imported": len(tsc_data["hw_tsrs"]),
        "hw_srs_derived": len(hw_srs_all),
        "overrides_supplied": len(overrides_dict),
        "overrides_applied": len(OVERRIDES_APPLIED),
        "overrides_unmatched": sorted(unmatched),
        "tabs": 10,
        "output_path": output_path,
    }


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_hw_safety_reqs.py <tsc.xlsx> <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(summary, indent=2))
