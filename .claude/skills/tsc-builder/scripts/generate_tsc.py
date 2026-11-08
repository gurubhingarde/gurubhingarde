"""
TSC Builder — generates a multi-tab ISO 26262 Technical Safety Concept (TSC) workbook from
(a) an FSC xlsx produced by fsc-builder and (b) an architecture refinement JSON.

Usage:
    python generate_tsc.py <fsc.xlsx> <architecture.json> <output.xlsx>

Pipeline:
- Read FSRs, ASIL allocations, decomposition decisions, block-diagram nodes from FSC xlsx
- Read architecture refinement (HW components + SW partitions + interfaces) from JSON
- For each FSR: propose 1–3 safety mechanisms (per branch + node type), draft HW-TSR + SW-TSR
- HSI: pre-populate signals for each chosen safety mechanism
- Timing: split FTTI into FDTI + FRTI (50/50 default)
- System FMEA: one row per (architecture element × failure mode taxonomy)
- DFA: one row per (decomposition pair × coupling factor)
- Verification: methods recommended per allocated ASIL
- HW Hand-off (to ISO 26262-5) and SW Hand-off (to ISO 26262-6) summaries
- Architecture diagram exported as both Mermaid (text) and a draw.io editable XML

See references/ for the methodology behind each tab.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as _xml_escape

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# ---------------------------------------------------------------------------
# Reference tables
# ---------------------------------------------------------------------------

NODE_TYPE_TO_BRANCH = {
    "sensor":    "Input failure",
    "comm_in":   "Input failure",
    "power_in":  "Input failure",
    "processor": "Process failure",
    "software":  "Process failure",
    "memory":    "Process failure",
    "actuator":  "Output failure",
    "driver":    "Output failure",
    "comm_out":  "Output failure",
}

# Safety mechanism candidates per (branch, node_type). Each entry: (id, name, default_dc, detection_time_ms)
MECHANISM_CANDIDATES: dict[tuple[str, str], list[tuple[str, str, str, str]]] = {
    ("Input failure", "sensor"): [
        ("SM10", "Range / out-of-range check", "60-80%", "1 sample"),
        ("SM11", "Plausibility cross-check (paired sensor)", "80-95%", "few samples"),
        ("SM12", "Sensor diagnostic register read", "90-99%", "per spec"),
    ],
    ("Input failure", "comm_in"): [
        ("SM13", "E2E protection (CRC + counter + timeout)", ">=99%", "1 cycle"),
        ("SM10", "Range / out-of-range check on payload", "60-80%", "1 cycle"),
    ],
    ("Input failure", "power_in"): [
        ("SM14", "Supply OV / UV monitor", ">=99%", "<1 ms"),
    ],
    ("Process failure", "processor"): [
        ("SM01", "Dual-core lockstep", ">=99%", "<1 us"),
        ("SM03", "Program-flow monitoring", "90-95%", "1 task period"),
        ("SM04", "Window watchdog", "90-95%", "1 window"),
    ],
    ("Process failure", "software"): [
        ("SM03", "Program-flow monitoring", "90-95%", "1 task period"),
        ("SM04", "Window watchdog", "90-95%", "1 window"),
        ("SM08", "MPU/MMU partition + violation handler", "n/a", "1 access"),
    ],
    ("Process failure", "memory"): [
        ("SM05", "ECC/SECDED on RAM/Flash", "99%+", "1 access"),
        ("SM07", "CRC over calibration / config", ">=99%", "startup or periodic"),
        ("SM06", "Memory BIST at startup", "90%", "startup"),
    ],
    ("Output failure", "actuator"): [
        ("SM16", "Current / voltage feedback", "80-95%", "<10 ms"),
        ("SM17", "Position / encoder feedback", "90-95%", "<1 motor cycle"),
    ],
    ("Output failure", "driver"): [
        ("SM18", "Driver IC self-test (open/short-to-supply/short-to-ground)", "90-99%", "<10 ms"),
        ("SM31", "Independent disable path", "n/a", "n/a (architectural)"),
    ],
    ("Output failure", "comm_out"): [
        ("SM19", "Downstream-receiver acknowledgement timeout", "n/a", "ack timeout"),
        ("SM13", "E2E protection on outgoing message", ">=99%", "1 cycle"),
    ],
}

# Standard reaction mechanism each FSR ends in
DEFAULT_REACTION = ("SM30", "Transition to safe state")

# System FMEA failure mode taxonomy per node type
FAILURE_MODES_BY_TYPE: dict[str, list[str]] = {
    "sensor":    ["No output", "Stuck output", "Drifted output", "Noisy output", "Out-of-range output"],
    "comm_in":   ["Lost message", "Late message", "Repeated message", "Corrupted message"],
    "power_in":  ["Loss of supply", "Undervoltage", "Overvoltage", "Supply transient"],
    "processor": ["Stuck-at fault", "Transient bit flip", "Lockstep mismatch", "Watchdog timeout", "Illegal opcode"],
    "software":  ["Missed deadline", "Illegal state", "Stack overflow", "Mutex deadlock", "Divide-by-zero"],
    "memory":    ["Single-bit flip", "Multi-bit flip", "Read disturb", "Address decoder fault"],
    "driver":    ["Open output", "Short to supply", "Short to ground", "Gate driver fault", "Thermal shutdown"],
    "actuator":  ["Stuck open", "Stuck closed", "Slow response", "Partial response", "Mechanical jam"],
    "comm_out":  ["Message not sent", "Late", "Wrong content", "Acknowledgement absent"],
}

# DFA coupling factors (from references/dfa_method.md)
DFA_COUPLING_FACTORS = [
    "Shared supply", "Shared ground", "Shared clock", "Shared bus",
    "Shared sensor", "Shared memory", "Shared SW library", "Shared OS / scheduler",
    "Shared environmental zone", "Shared development team / process",
    "Shared compiler / toolchain", "Shared production / test process",
]

# Verification method recommendations by allocated ASIL (ISO 26262-4 Table 3, repeated for TSC)
VERIFICATION_PLUS_PLUS = {
    "A":  ["Walk-through"],
    "B":  ["Walk-through", "Inspection"],
    "C":  ["Inspection", "Semi-formal verification", "Simulation"],
    "D":  ["Inspection", "Semi-formal verification", "Formal verification", "Simulation", "Prototype testing"],
    "QM": ["Walk-through"],
}


def asil_base(asil: str) -> str:
    if not asil:
        return "QM"
    return asil.split("(")[0].strip()


# ---------------------------------------------------------------------------
# Styling
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
    base = asil_base(asil_value)
    color_map = {"A": "FFE699", "B": "F4B084", "C": "F8696B", "D": "C00000"}
    if base in color_map:
        cell.fill = PatternFill("solid", fgColor=color_map[base])
        cell.font = Font(name=FONT_NAME, bold=True, color="FFFFFF" if base == "D" else "000000")
        cell.alignment = Alignment(horizontal="center", vertical="center")


# ---------------------------------------------------------------------------
# FSC reader
# ---------------------------------------------------------------------------

def read_fsc(fsc_path: str) -> dict:
    wb = load_workbook(fsc_path, data_only=True)
    if "05_FSR_Catalog" not in wb.sheetnames:
        raise ValueError("FSC workbook missing tab '05_FSR_Catalog'.")

    # Item meta
    item: dict[str, str] = {}
    if "00_Title_Page" in wb.sheetnames:
        ws = wb["00_Title_Page"]
        for r in range(6, 25):
            label = ws.cell(r, 2).value
            value = ws.cell(r, 3).value
            if label and value:
                item[str(label).strip()] = str(value).strip()
        title_text = ws.cell(3, 1).value
        if title_text:
            item["Item Title"] = str(title_text)

    # FSRs
    fsrs: list[dict] = []
    ws = wb["05_FSR_Catalog"]
    for r in range(5, ws.max_row + 1):
        fsr_id = ws.cell(r, 1).value
        if not fsr_id or not str(fsr_id).startswith("FSR-"):
            continue
        node_cell = str(ws.cell(r, 6).value or "")
        node_id = node_cell.split(" — ")[0].strip() if " — " in node_cell else node_cell.strip()
        fsrs.append({
            "fsr_id": str(fsr_id),
            "sg_id": str(ws.cell(r, 2).value or ""),
            "asil_inherited": str(ws.cell(r, 3).value or "QM"),
            "branch": str(ws.cell(r, 4).value or ""),
            "be_code": str(ws.cell(r, 5).value or ""),
            "node_ref": node_cell,
            "node_id": node_id,
            "fsr_text": str(ws.cell(r, 7).value or ""),
            "ftti_ms": ws.cell(r, 8).value,
        })

    # ASIL allocations (gives us the *allocated* per-node ASIL)
    allocations: list[dict] = []
    if "06_ASIL_Allocation" in wb.sheetnames:
        ws = wb["06_ASIL_Allocation"]
        for r in range(5, ws.max_row + 1):
            sg_id = ws.cell(r, 1).value
            if not sg_id or not str(sg_id).startswith("SG-"):
                continue
            allocations.append({
                "sg_id": str(sg_id),
                "node_id": str(ws.cell(r, 2).value or ""),
                "node_name": str(ws.cell(r, 3).value or ""),
                "branch": str(ws.cell(r, 4).value or ""),
                "inherited_asil": str(ws.cell(r, 5).value or ""),
                "decomposition": str(ws.cell(r, 7).value or ""),
                "resulting_asil": str(ws.cell(r, 8).value or ""),
                "independence_evidence": str(ws.cell(r, 9).value or ""),
            })

    # Block diagram nodes (from FSC's 03 tab)
    nodes: list[dict] = []
    if "03_System_Block_Diagram" in wb.sheetnames:
        ws = wb["03_System_Block_Diagram"]
        for r in range(5, ws.max_row + 1):
            nid = ws.cell(r, 1).value
            if not nid or not str(nid).startswith("N"):
                continue
            nodes.append({
                "id": str(nid),
                "name": str(ws.cell(r, 2).value or ""),
                "type": str(ws.cell(r, 3).value or ""),
                "branch": str(ws.cell(r, 4).value or ""),
                "asil_relevant": str(ws.cell(r, 5).value or "Yes") == "Yes",
                "inputs": [s.strip() for s in str(ws.cell(r, 6).value or "").split(",") if s.strip()],
                "outputs": [s.strip() for s in str(ws.cell(r, 7).value or "").split(",") if s.strip()],
                "redundancy_group": str(ws.cell(r, 8).value or "") or None,
                "shared_resources": [s.strip() for s in str(ws.cell(r, 9).value or "").split(",") if s.strip()],
            })

    return {"item": item, "fsrs": fsrs, "allocations": allocations, "nodes": nodes, "fsc_path": fsc_path}


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, item: dict, tsc_meta: dict, fsc_path: str) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "Technical Safety Concept (TSC)")
    style_title_row(ws, 3, 4, item.get("Item Title", "") or item.get("Project", ""))
    fields = [
        ("Project",       tsc_meta.get("project") or item.get("Project", "")),
        ("TSC Document ID", tsc_meta.get("doc_id", "")),
        ("Revision",       tsc_meta.get("revision", "")),
        ("Date",           tsc_meta.get("date", "")),
        ("Author",         tsc_meta.get("author", "")),
        ("Approver",       tsc_meta.get("approver", "")),
        ("Linked FSC",     fsc_path),
        ("Standard",       "ISO 26262:2018, Part 4 (System level), with Part 9 §5 (decomposition) and §7 (DFA)."),
        ("Methodology",    "Per-FSR safety mechanism allocation, HW/SW TSR derivation, HSI specification, timing budget split (FDTI + FRTI <= FTTI), system FMEA, DFA against decomposition claims."),
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
        ("0.1", "", "", "Initial draft generated by tsc-builder skill", ""),
        ("0.2", "", "", "Internal review comments incorporated", ""),
        ("1.0", "", "", "Released to HW (Part 5) and SW (Part 6) teams", ""),
    ], start=4):
        for c, v in enumerate(row, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 6, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_fsrs_imported(wb: Workbook, fsrs: list[dict], fsc_path: str) -> None:
    ws = wb.create_sheet("02_FSRs_From_FSC")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Functional Safety Requirements — Imported from FSC")
    note = ws.cell(row=2, column=1, value=f"Source: {fsc_path}. Read-only echo for traceability. Update the FSC and re-run if changes are needed.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 32
    style_header_row(ws, 4, ["FSR_ID", "SG_ID", "ASIL (inherited)", "Branch", "Linked Node", "Functional Safety Requirement", "FTTI (ms)"])
    for i, f in enumerate(fsrs, start=5):
        ws.cell(row=i, column=1, value=f["fsr_id"])
        ws.cell(row=i, column=2, value=f["sg_id"])
        cell = ws.cell(row=i, column=3, value=f["asil_inherited"])
        asil_color_cell(cell, f["asil_inherited"])
        ws.cell(row=i, column=4, value=f["branch"])
        ws.cell(row=i, column=5, value=f["node_ref"])
        ws.cell(row=i, column=6, value=f["fsr_text"])
        ws.cell(row=i, column=7, value=f["ftti_ms"])
    end_row = 4 + len(fsrs)
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
    ws.auto_filter.ref = f"A4:G{end_row}"
    autosize(ws, {1: 14, 2: 10, 3: 10, 4: 14, 5: 26, 6: 70, 7: 12})


def build_architecture(wb: Workbook, nodes: list[dict], hw_components: list[dict], sw_partitions: list[dict]) -> None:
    ws = wb.create_sheet("03_System_Architecture")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "System Architecture — HW Components and SW Partitions")
    note = ws.cell(row=2, column=1, value="Architecture refines the FSC block diagram into HW components and SW partitions. Each component / partition maps to one or more block-diagram nodes via the Allocated Nodes column.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 36

    # HW components table
    style_header_row(ws, 4, ["HW Component ID", "Name", "Part / Vendor", "Allocated Nodes", "Power Domain", "Clock Domain", "Notes"])
    for i, c in enumerate(hw_components or [], start=5):
        ws.cell(row=i, column=1, value=c.get("id", ""))
        ws.cell(row=i, column=2, value=c.get("name", ""))
        ws.cell(row=i, column=3, value=c.get("part", ""))
        ws.cell(row=i, column=4, value=", ".join(c.get("allocated_nodes", []) or []))
        ws.cell(row=i, column=5, value=c.get("power_domain", ""))
        ws.cell(row=i, column=6, value=c.get("clock_domain", ""))
        ws.cell(row=i, column=7, value=c.get("notes", ""))
    hw_end = 4 + max(1, len(hw_components or []))
    stripe_body(ws, 5, hw_end, 7)

    # SW partitions table
    base = hw_end + 3
    style_title_row(ws, base, 7, "Software Partitions")
    style_header_row(ws, base + 1, ["SW Partition ID", "Name", "Hosted On (HW Comp ID)", "Allocated Nodes", "RTOS / OS", "ASIL (developed-to)", "Notes"])
    for i, sp in enumerate(sw_partitions or [], start=base + 2):
        ws.cell(row=i, column=1, value=sp.get("id", ""))
        ws.cell(row=i, column=2, value=sp.get("name", ""))
        ws.cell(row=i, column=3, value=sp.get("hosted_on", ""))
        ws.cell(row=i, column=4, value=", ".join(sp.get("allocated_nodes", []) or []))
        ws.cell(row=i, column=5, value=sp.get("rtos", ""))
        cell = ws.cell(row=i, column=6, value=sp.get("asil", ""))
        asil_color_cell(cell, sp.get("asil", ""))
        ws.cell(row=i, column=7, value=sp.get("notes", ""))
    sw_end = base + 1 + max(1, len(sw_partitions or []))
    stripe_body(ws, base + 2, sw_end, 7)

    autosize(ws, {1: 14, 2: 26, 3: 22, 4: 26, 5: 16, 6: 16, 7: 30})


def _node_lookup(nodes: list[dict]) -> dict[str, dict]:
    return {n["id"]: n for n in nodes}


def build_safety_mechanism_catalog(wb: Workbook, fsrs: list[dict], allocations: list[dict], nodes: list[dict]) -> list[dict]:
    """Returns the chosen mechanism rows (one per FSR by default — first candidate)."""
    ws = wb.create_sheet("04_Safety_Mechanism_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "Safety Mechanism Catalog")
    note = ws.cell(row=2, column=1, value="Each FSR is paired with one or more candidate safety mechanisms. The first candidate is marked '[primary]' by default; alternatives appear on subsequent rows for analyst review. Trim to the chosen mechanism per FSR before downstream use.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)
    ws.row_dimensions[2].height = 36

    style_header_row(ws, 4, ["FSR_ID", "Allocated ASIL", "Branch", "Linked Node", "Mechanism ID", "Mechanism Name", "Default DC%", "Detection Time (target)", "Selection"])

    nl = _node_lookup(nodes)
    alloc_lookup = {(a["sg_id"], a["node_id"]): a["resulting_asil"] for a in allocations}

    chosen: list[dict] = []
    row = 5
    for f in fsrs:
        node = nl.get(f["node_id"], {})
        node_type = node.get("type", "")
        candidates = MECHANISM_CANDIDATES.get((f["branch"], node_type), [])
        allocated_asil = alloc_lookup.get((f["sg_id"], f["node_id"]), f["asil_inherited"])
        if not candidates:
            ws.cell(row=row, column=1, value=f["fsr_id"])
            cell = ws.cell(row=row, column=2, value=allocated_asil); asil_color_cell(cell, allocated_asil)
            ws.cell(row=row, column=3, value=f["branch"])
            ws.cell(row=row, column=4, value=f["node_ref"])
            ws.cell(row=row, column=5, value="<TBD>")
            ws.cell(row=row, column=6, value=f"(No catalog entry for branch={f['branch']} / type={node_type}; analyst to define)")
            ws.cell(row=row, column=9, value="[primary — to define]")
            row += 1
            continue
        for idx, (sm_id, sm_name, dc, detection_time) in enumerate(candidates):
            ws.cell(row=row, column=1, value=f["fsr_id"] if idx == 0 else "")
            if idx == 0:
                cell = ws.cell(row=row, column=2, value=allocated_asil); asil_color_cell(cell, allocated_asil)
                ws.cell(row=row, column=3, value=f["branch"])
                ws.cell(row=row, column=4, value=f["node_ref"])
            ws.cell(row=row, column=5, value=sm_id)
            ws.cell(row=row, column=6, value=sm_name)
            ws.cell(row=row, column=7, value=dc)
            ws.cell(row=row, column=8, value=detection_time)
            ws.cell(row=row, column=9, value="[primary]" if idx == 0 else "[alternative]")
            if idx == 0:
                chosen.append({
                    "fsr": f,
                    "allocated_asil": allocated_asil,
                    "mechanism_id": sm_id,
                    "mechanism_name": sm_name,
                    "default_dc": dc,
                    "detection_time": detection_time,
                    "node": node,
                })
            row += 1

    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 10):
            cell = ws.cell(row=r, column=c)
            if c != 2:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:I{end_row}"
    autosize(ws, {1: 14, 2: 12, 3: 14, 4: 26, 5: 10, 6: 36, 7: 12, 8: 18, 9: 18})
    return chosen


def build_tsr_catalog(wb: Workbook, chosen_mechanisms: list[dict]) -> list[dict]:
    """One HW-TSR + one SW-TSR per chosen mechanism. Returns TSR rows."""
    ws = wb.create_sheet("05_TSR_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "Technical Safety Requirements (TSRs)")
    note = ws.cell(row=2, column=1, value="Each chosen safety mechanism produces one HW-TSR (the diagnostic implementation) and one SW-TSR (the reaction). Both rows trace back to the FSR. Refine wording during TSC review.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)
    ws.row_dimensions[2].height = 36

    style_header_row(ws, 4, ["TSR_ID", "FSR_ID", "Allocated ASIL", "Type", "Mechanism", "Linked Node", "Technical Safety Requirement", "Verification Method"])

    tsrs: list[dict] = []
    row = 5
    for c in chosen_mechanisms:
        f = c["fsr"]
        sg_num = f["sg_id"].split("-")[1]
        fsr_suffix = f["fsr_id"].split("-", 1)[1]
        for j, kind in enumerate(["HW-TSR", "SW-TSR"], start=1):
            tsr_id = f"TSR-{fsr_suffix}-{j:02d}"
            if kind == "HW-TSR":
                text = (f"The HW shall implement {c['mechanism_name']} ({c['mechanism_id']}) on {c['node'].get('name', f['node_ref'])} "
                        f"with diagnostic coverage of at least {c['default_dc']} (target; refine after FMEDA) and assert the corresponding "
                        f"diagnostic flag on detection within {c['detection_time']}.")
            else:
                text = (f"The SW shall consume the {c['mechanism_id']} diagnostic flag for {c['node'].get('name', f['node_ref'])}, debounce per HSI spec, "
                        f"and command the safe state within the FRTI budget of FSR {f['fsr_id']}.")
            ws.cell(row=row, column=1, value=tsr_id)
            ws.cell(row=row, column=2, value=f["fsr_id"] if j == 1 else "")
            if j == 1:
                cell = ws.cell(row=row, column=3, value=c["allocated_asil"]); asil_color_cell(cell, c["allocated_asil"])
                ws.cell(row=row, column=5, value=f"{c['mechanism_id']} — {c['mechanism_name']}")
                ws.cell(row=row, column=6, value=f["node_ref"])
            ws.cell(row=row, column=4, value=kind)
            ws.cell(row=row, column=7, value=text)
            base = asil_base(c["allocated_asil"])
            ws.cell(row=row, column=8, value=", ".join(VERIFICATION_PLUS_PLUS.get(base, [])))
            tsrs.append({"tsr_id": tsr_id, "fsr": f, "type": kind, "asil": c["allocated_asil"], "mechanism": c["mechanism_id"], "text": text})
            row += 1

    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 9):
            cell = ws.cell(row=r, column=c)
            if c != 3:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if ((r - 5) // 2) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:H{end_row}"
    autosize(ws, {1: 16, 2: 14, 3: 12, 4: 10, 5: 32, 6: 26, 7: 70, 8: 36})
    return tsrs


def build_hsi(wb: Workbook, chosen_mechanisms: list[dict]) -> None:
    ws = wb.create_sheet("06_HSI_Specification")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "Hardware-Software Interface (HSI)")
    note = ws.cell(row=2, column=1, value="One HW->SW diagnostic signal and one SW->HW liveness signal per chosen safety mechanism. Refine signal names, encoding, and timing during integration planning.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)
    ws.row_dimensions[2].height = 32
    style_header_row(ws, 4, ["HSI Signal", "Direction", "Linked FSR / TSR", "Mechanism", "Encoding", "Update Rate", "Integrity Protection", "Failure Reaction", "Allocated ASIL"])
    row = 5
    for c in chosen_mechanisms:
        f = c["fsr"]
        node_short = (c["node"].get("name", f["node_ref"]) or "").split(" ")[0].lower().replace(",", "")
        sm_short = c["mechanism_id"].lower()
        # HW -> SW diagnostic flag
        ws.cell(row=row, column=1, value=f"esc.diag.{node_short}_{sm_short}")
        ws.cell(row=row, column=2, value="HW -> SW")
        ws.cell(row=row, column=3, value=f["fsr_id"])
        ws.cell(row=row, column=4, value=f"{c['mechanism_id']} — {c['mechanism_name']}")
        ws.cell(row=row, column=5, value="1 bit (0=ok, 1=fault) + companion validity bit")
        ws.cell(row=row, column=6, value=c["detection_time"])
        ws.cell(row=row, column=7, value="Parity over flag+validity; CRC if multi-bit")
        ws.cell(row=row, column=8, value=f"SW transitions to safe state per FSR {f['fsr_id']}")
        cell = ws.cell(row=row, column=9, value=c["allocated_asil"]); asil_color_cell(cell, c["allocated_asil"])
        row += 1
        # SW -> HW liveness
        ws.cell(row=row, column=1, value=f"esc.live.{node_short}_{sm_short}_ack")
        ws.cell(row=row, column=2, value="SW -> HW")
        ws.cell(row=row, column=3, value=f["fsr_id"])
        ws.cell(row=row, column=4, value=f"{c['mechanism_id']} — {c['mechanism_name']}")
        ws.cell(row=row, column=5, value="8-bit rolling counter, increment per task period")
        ws.cell(row=row, column=6, value="<TBD: per task period>")
        ws.cell(row=row, column=7, value="None (HW infers liveness from counter increment)")
        ws.cell(row=row, column=8, value="HW asserts independent disable on missed counter")
        cell = ws.cell(row=row, column=9, value=c["allocated_asil"]); asil_color_cell(cell, c["allocated_asil"])
        row += 1
    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 10):
            cell = ws.cell(row=r, column=c)
            if c != 9:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if ((r - 5) // 2) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:I{end_row}"
    autosize(ws, {1: 36, 2: 12, 3: 14, 4: 32, 5: 32, 6: 18, 7: 28, 8: 32, 9: 12})


def build_timing_budget(wb: Workbook, chosen_mechanisms: list[dict]) -> None:
    ws = wb.create_sheet("07_Timing_Budget")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Timing Budget — FTTI = FDTI + FRTI")
    note = ws.cell(row=2, column=1, value="Default split FDTI = FRTI = 50%. Adjust per FSR if the detection mechanism or actuator response demands a different split.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 32
    style_header_row(ws, 4, ["FSR_ID", "Allocated ASIL", "FTTI (ms)", "FDTI target (ms)", "FRTI target (ms)", "Mechanism Detection Time", "Notes"])
    row = 5
    for c in chosen_mechanisms:
        f = c["fsr"]
        ftti = f["ftti_ms"]
        try:
            ftti_num = float(ftti)
            fdti = ftti_num / 2
            frti = ftti_num / 2
        except (TypeError, ValueError):
            fdti = "<TBD>"
            frti = "<TBD>"
        ws.cell(row=row, column=1, value=f["fsr_id"])
        cell = ws.cell(row=row, column=2, value=c["allocated_asil"]); asil_color_cell(cell, c["allocated_asil"])
        ws.cell(row=row, column=3, value=ftti)
        ws.cell(row=row, column=4, value=fdti)
        ws.cell(row=row, column=5, value=frti)
        ws.cell(row=row, column=6, value=c["detection_time"])
        ws.cell(row=row, column=7, value="<TBD: validate that mechanism detection time fits within FDTI; note actuator reaction time inside FRTI>")
        row += 1
    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 8):
            cell = ws.cell(row=r, column=c)
            if c != 2:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:G{end_row}"
    autosize(ws, {1: 14, 2: 12, 3: 12, 4: 14, 5: 14, 6: 22, 7: 50})


def build_system_fmea(wb: Workbook, nodes: list[dict], allocations: list[dict]) -> None:
    ws = wb.create_sheet("08_System_FMEA")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "System-Level FMEA")
    note = ws.cell(row=2, column=1, value="One row per (architecture node x failure-mode taxonomy). Cross-checks the deductive FTA: every FMEA Vehicle Effect classified as a hazard MUST appear as a basic event in the FTA, and vice versa.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)
    ws.row_dimensions[2].height = 36
    style_header_row(ws, 4, ["Element / Node", "Failure Mode", "Local Effect", "Subsystem Effect", "Vehicle Effect", "Linked SG / FSR", "Existing Mechanism", "DC% (target)"])
    # Map node -> SGs that reference it (via allocations)
    node_to_sgs: dict[str, set[str]] = defaultdict(set)
    for a in allocations:
        node_to_sgs[a["node_id"]].add(a["sg_id"])
    row = 5
    for n in nodes:
        if not n.get("asil_relevant", True):
            continue
        modes = FAILURE_MODES_BY_TYPE.get(n["type"], ["Generic failure mode (define)"])
        sgs = ", ".join(sorted(node_to_sgs.get(n["id"], set()))) or "<TBD>"
        for mode in modes:
            ws.cell(row=row, column=1, value=f"{n['id']} — {n['name']}")
            ws.cell(row=row, column=2, value=mode)
            ws.cell(row=row, column=3, value=f"<TBD: {mode.lower()} of {n['name']}>")
            ws.cell(row=row, column=4, value="<TBD>")
            ws.cell(row=row, column=5, value="<TBD: trace to HARA hazardous event>")
            ws.cell(row=row, column=6, value=sgs)
            ws.cell(row=row, column=7, value="<TBD: select from Safety Mechanism Catalog>")
            ws.cell(row=row, column=8, value="<TBD>")
            row += 1
    end_row = row - 1
    stripe_body(ws, 5, end_row, 8)
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:H{end_row}"
    autosize(ws, {1: 26, 2: 22, 3: 36, 4: 36, 5: 36, 6: 18, 7: 36, 8: 12})


def build_dfa(wb: Workbook, allocations: list[dict], nodes: list[dict]) -> None:
    ws = wb.create_sheet("09_DFA")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Dependent Failure Analysis (DFA)")
    note = ws.cell(row=2, column=1, value="One row per (decomposition pair x coupling factor). Analyst marks each cell as 'No', 'Yes — mitigated by ...', or 'Yes — UNMITIGATED'. Any unmitigated coupling invalidates the decomposition; the corresponding ASIL Allocation row must revert to full inheritance in the FSC.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 50
    style_header_row(ws, 4, ["Decomposition Pair (SG / Node A / Node B)", "Coupling Factor", "Coupling Present?", "Mitigation", "Conclusion", "Status"])
    nl = _node_lookup(nodes)
    # Find decomposition pairs from allocations: nodes with same SG and decomposition != "None (full inheritance)"
    by_sg: dict[str, list[dict]] = defaultdict(list)
    for a in allocations:
        if a["decomposition"] and "None" not in a["decomposition"]:
            by_sg[a["sg_id"]].append(a)
    row = 5
    pair_count = 0
    for sg_id, allocs in by_sg.items():
        # Pair candidates by redundancy_group (use shared resource overlap as a proxy)
        pairs = []
        for i in range(len(allocs)):
            for j in range(i + 1, len(allocs)):
                a, b = allocs[i], allocs[j]
                na, nb = nl.get(a["node_id"], {}), nl.get(b["node_id"], {})
                # Same redundancy group required for genuine decomposition
                if na.get("redundancy_group") and na.get("redundancy_group") == nb.get("redundancy_group"):
                    pairs.append((a, b))
        for a, b in pairs:
            pair_count += 1
            for cf in DFA_COUPLING_FACTORS:
                ws.cell(row=row, column=1, value=f"{sg_id} / {a['node_id']} ({a['node_name']}) / {b['node_id']} ({b['node_name']})" if cf == DFA_COUPLING_FACTORS[0] else "")
                ws.cell(row=row, column=2, value=cf)
                ws.cell(row=row, column=3, value="<TBD: Yes / No>")
                ws.cell(row=row, column=4, value="<TBD: cite mitigation if Yes>")
                ws.cell(row=row, column=5, value="")
                ws.cell(row=row, column=6, value="")
                row += 1
    if row == 5:
        ws.cell(row=5, column=1, value="(No decomposition pairs found in FSC; DFA not required for this item.)").font = body_font()
    end_row = row - 1
    if end_row >= 5:
        stripe_body(ws, 5, end_row, 6)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 50, 2: 30, 3: 16, 4: 36, 5: 28, 6: 16})


def build_verification(wb: Workbook, tsrs: list[dict]) -> None:
    ws = wb.create_sheet("10_Verification")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Verification Specification")
    note = ws.cell(row=2, column=1, value="Verification methods per allocated ASIL (ISO 26262-4 Table 3, also applicable to TSC verification per Part 4 §7.4).")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 32
    style_header_row(ws, 4, ["TSR_ID", "FSR_ID", "Allocated ASIL", "Type", "Recommended Methods (++)", "Confirmation Review Independence"])
    row = 5
    for t in tsrs:
        base = asil_base(t["asil"])
        plus_plus = ", ".join(VERIFICATION_PLUS_PLUS.get(base, []))
        independence = "I3" if base == "D" else ("I2" if base == "C" else ("I1" if base in ("A", "B") else "—"))
        ws.cell(row=row, column=1, value=t["tsr_id"])
        ws.cell(row=row, column=2, value=t["fsr"]["fsr_id"])
        cell = ws.cell(row=row, column=3, value=t["asil"]); asil_color_cell(cell, t["asil"])
        ws.cell(row=row, column=4, value=t["type"])
        ws.cell(row=row, column=5, value=plus_plus)
        ws.cell(row=row, column=6, value=independence)
        row += 1
    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 7):
            cell = ws.cell(row=r, column=c)
            if c != 3:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:F{end_row}"
    autosize(ws, {1: 16, 2: 14, 3: 12, 4: 10, 5: 50, 6: 18})


def build_hw_handoff(wb: Workbook, tsrs: list[dict]) -> None:
    ws = wb.create_sheet("11_HW_Handoff")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "HW Hand-off (to ISO 26262-5)")
    note = ws.cell(row=2, column=1, value="HW-TSRs handed to the HW team. The HW team uses these as inputs to FMEDA, hardware metrics (SPFM, LFM, PMHF), and HW-level verification per ISO 26262-5.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 36
    style_header_row(ws, 4, ["HW-TSR_ID", "FSR_ID", "Allocated ASIL", "Mechanism", "Hand-off Status", "Owner"])
    row = 5
    for t in tsrs:
        if t["type"] != "HW-TSR":
            continue
        ws.cell(row=row, column=1, value=t["tsr_id"])
        ws.cell(row=row, column=2, value=t["fsr"]["fsr_id"])
        cell = ws.cell(row=row, column=3, value=t["asil"]); asil_color_cell(cell, t["asil"])
        ws.cell(row=row, column=4, value=t["mechanism"])
        ws.cell(row=row, column=5, value="Pending HW review")
        ws.cell(row=row, column=6, value="<TBD>")
        row += 1
    end_row = row - 1
    if end_row >= 5:
        for r in range(5, end_row + 1):
            for c in range(1, 7):
                cell = ws.cell(row=r, column=c)
                if c != 3:
                    cell.font = body_font()
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                    if (r - 5) % 2 == 1:
                        cell.fill = PatternFill("solid", fgColor=ALT_ROW)
                cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    autosize(ws, {1: 16, 2: 14, 3: 12, 4: 36, 5: 22, 6: 22})


def build_sw_handoff(wb: Workbook, tsrs: list[dict]) -> None:
    ws = wb.create_sheet("12_SW_Handoff")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "SW Hand-off (to ISO 26262-6)")
    note = ws.cell(row=2, column=1, value="SW-TSRs handed to the SW team. SW team allocates to SW components, derives unit requirements, and verifies per ISO 26262-6 (MISRA C compliance, MC/DC for ASIL D, etc.).")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 36
    style_header_row(ws, 4, ["SW-TSR_ID", "FSR_ID", "Allocated ASIL", "Mechanism", "Hand-off Status", "Owner"])
    row = 5
    for t in tsrs:
        if t["type"] != "SW-TSR":
            continue
        ws.cell(row=row, column=1, value=t["tsr_id"])
        ws.cell(row=row, column=2, value=t["fsr"]["fsr_id"])
        cell = ws.cell(row=row, column=3, value=t["asil"]); asil_color_cell(cell, t["asil"])
        ws.cell(row=row, column=4, value=t["mechanism"])
        ws.cell(row=row, column=5, value="Pending SW review")
        ws.cell(row=row, column=6, value="<TBD>")
        row += 1
    end_row = row - 1
    if end_row >= 5:
        for r in range(5, end_row + 1):
            for c in range(1, 7):
                cell = ws.cell(row=r, column=c)
                if c != 3:
                    cell.font = body_font()
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                    if (r - 5) % 2 == 1:
                        cell.fill = PatternFill("solid", fgColor=ALT_ROW)
                cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    autosize(ws, {1: 16, 2: 14, 3: 12, 4: 36, 5: 22, 6: 22})


# ---------------------------------------------------------------------------
# draw.io exporter
# ---------------------------------------------------------------------------

def write_drawio(nodes: list[dict], hw_components: list[dict], sw_partitions: list[dict], output_path: str) -> str:
    """Generate an editable .drawio (mxGraph XML) file for the system architecture."""
    cells_xml = []
    cell_id = 2
    layout_x_step = 200
    layout_y_step = 100
    type_to_x = {
        "sensor": 80, "comm_in": 80, "power_in": 80,
        "processor": 600, "software": 600, "memory": 600,
        "actuator": 1100, "driver": 1100, "comm_out": 1100,
    }
    type_y_counters: dict[str, int] = defaultdict(int)
    type_to_color = {
        "sensor": "#D9E2F3", "comm_in": "#D9E2F3", "power_in": "#D9E2F3",
        "processor": "#FFE699", "software": "#FFF2CC", "memory": "#F2F2F2",
        "actuator": "#F4B084", "driver": "#F4B084", "comm_out": "#F4B084",
    }
    id_to_cell: dict[str, str] = {}

    for n in nodes:
        x = type_to_x.get(n["type"], 600)
        y = 80 + type_y_counters[n["type"]] * layout_y_step
        type_y_counters[n["type"]] += 1
        color = type_to_color.get(n["type"], "#FFFFFF")
        label = _xml_escape(f"{n['id']}\n{n['name']}\n[{n['type']}]")
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={color};strokeColor=#1F3864;fontSize=10;"
        cells_xml.append(
            f'<mxCell id="{cell_id}" value="{label}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="160" height="70" as="geometry"/></mxCell>'
        )
        id_to_cell[n["id"]] = str(cell_id)
        cell_id += 1

    # Edges
    edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
    for n in nodes:
        for out in n.get("outputs", []):
            src = id_to_cell.get(n["id"])
            tgt = id_to_cell.get(out)
            if not src or not tgt:
                continue
            cells_xml.append(
                f'<mxCell id="{cell_id}" style="{edge_style}" edge="1" parent="1" source="{src}" target="{tgt}">'
                f'<mxGeometry relative="1" as="geometry"/></mxCell>'
            )
            cell_id += 1

    body = "\n        ".join(cells_xml)
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="tsc-builder" modified="2026-04-28T00:00:00.000Z" agent="tsc-builder/1.0" version="22.0.0">
  <diagram id="system_architecture" name="System Architecture">
    <mxGraphModel dx="1422" dy="754" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400" pageHeight="900" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {body}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(xml, encoding="utf-8")
    return output_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(fsc_path: str, architecture_path: str, output_path: str) -> dict:
    fsc_data = read_fsc(fsc_path)
    with open(architecture_path) as f:
        arch = json.load(f)

    tsc_meta = arch.get("tsc_metadata", {}) or {}
    hw_components = arch.get("architecture", {}).get("hw_components", [])
    sw_partitions = arch.get("architecture", {}).get("sw_partitions", [])

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, fsc_data["item"], tsc_meta, fsc_path)
    build_doc_control(wb)
    build_fsrs_imported(wb, fsc_data["fsrs"], fsc_path)
    build_architecture(wb, fsc_data["nodes"], hw_components, sw_partitions)
    chosen = build_safety_mechanism_catalog(wb, fsc_data["fsrs"], fsc_data["allocations"], fsc_data["nodes"])
    tsrs = build_tsr_catalog(wb, chosen)
    build_hsi(wb, chosen)
    build_timing_budget(wb, chosen)
    build_system_fmea(wb, fsc_data["nodes"], fsc_data["allocations"])
    build_dfa(wb, fsc_data["allocations"], fsc_data["nodes"])
    build_verification(wb, tsrs)
    build_hw_handoff(wb, tsrs)
    build_sw_handoff(wb, tsrs)

    wb.active = 0
    wb.save(output_path)

    drawio_path = str(Path(output_path).with_suffix(".drawio"))
    write_drawio(fsc_data["nodes"], hw_components, sw_partitions, drawio_path)

    return {
        "fsrs_imported": len(fsc_data["fsrs"]),
        "asil_allocations": len(fsc_data["allocations"]),
        "nodes": len(fsc_data["nodes"]),
        "chosen_safety_mechanisms": len(chosen),
        "tsrs": len(tsrs),
        "drawio_path": drawio_path,
        "output_path": output_path,
    }


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_tsc.py <fsc.xlsx> <architecture.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(summary, indent=2))
