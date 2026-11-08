"""
FSC Builder — generates a multi-tab ISO 26262 Functional Safety Concept (FSC) workbook
from (a) a HARA xlsx produced by hara-builder and (b) a block-diagram JSON.

Usage:
    python generate_fsc.py <hara.xlsx> <block_diagram.json> <output.xlsx>

Methodology:
- Top-level event per safety goal = Violation of SG-XXX
- Below: OR gate connecting 3 standard intermediates (Input failure, Process failure, Output failure)
- Each intermediate expands into basic events, one per ASIL-relevant block-diagram node of that role
- Each basic event yields one Functional Safety Requirement (FSR)
- ASIL allocation defaults to inheritance; redundant peers are flagged for analyst-confirmed decomposition

See references/fta_methodology.md, references/asil_decomposition.md, references/fsr_templates.md.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

# Optional fault tree rendering. Soft import so the script still runs without graphviz.
try:
    from fault_tree_renderer import FaultTree, render_fault_tree
    _FT_AVAILABLE = True
except ImportError:
    _FT_AVAILABLE = False


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

# FSR template per (branch, node_type)
FSR_TEMPLATES: dict[tuple[str, str], str] = {
    ("Input failure", "sensor"):
        "The item shall detect implausible, out-of-range, or stuck readings from {name} within <TBD> ms and transition to the safe state ('{safe_state}') within {ftti} ms.",
    ("Input failure", "comm_in"):
        "The item shall detect missing, stale, or CRC-invalid messages on {name} within <TBD> ms and substitute a safe default or transition to the safe state ('{safe_state}') within {ftti} ms.",
    ("Input failure", "power_in"):
        "The item shall detect supply voltage outside the qualification range on {name} and disable the dependent function within <TBD> ms, transitioning to the safe state ('{safe_state}') within {ftti} ms.",
    ("Process failure", "processor"):
        "The item shall detect faults of {name} via lockstep, dual-channel comparison, or program-flow monitoring with diagnostic coverage ≥ <TBD>% and transition to the safe state ('{safe_state}') within {ftti} ms.",
    ("Process failure", "software"):
        "The item shall detect timing, sequence, and state-machine violations in {name} via watchdog and runtime monitoring, and transition to the safe state ('{safe_state}') within {ftti} ms.",
    ("Process failure", "memory"):
        "The item shall detect single-bit and multi-bit faults in {name} via ECC/SECDED (or equivalent), and transition to the safe state ('{safe_state}') within {ftti} ms upon uncorrectable fault.",
    ("Output failure", "actuator"):
        "The item shall continuously monitor the response of {name} via current sensing or position feedback and detect deviations from the commanded state within <TBD> ms, transitioning to the safe state ('{safe_state}') within {ftti} ms.",
    ("Output failure", "driver"):
        "The item shall detect open-circuit, short-to-supply, and short-to-ground conditions on {name} within <TBD> ms and transition to the safe state ('{safe_state}') within {ftti} ms.",
    ("Output failure", "comm_out"):
        "The item shall verify acknowledgement of the {name} message by the downstream receiver within <TBD> ms; on absent acknowledgement the item shall transition to the safe state ('{safe_state}') within {ftti} ms.",
}

# ISO 26262-9, Table 1 decomposition options
DECOMPOSITION_OPTIONS: dict[str, list[tuple[str, str, str]]] = {
    "D": [
        ("D + QM(D)",        "D",     "QM(D)"),
        ("C(D) + A(D)",      "C(D)",  "A(D)"),
        ("B(D) + B(D)",      "B(D)",  "B(D)"),
    ],
    "C": [
        ("C + QM(C)",        "C",     "QM(C)"),
        ("B(C) + A(C)",      "B(C)",  "A(C)"),
    ],
    "B": [
        ("B + QM(B)",        "B",     "QM(B)"),
        ("A(B) + A(B)",      "A(B)",  "A(B)"),
    ],
    "A": [
        ("A + QM(A)",        "A",     "QM(A)"),
    ],
    "QM": [],
    "—": [],
}

# Verification methods recommended (++) and optional (+) per ASIL — ISO 26262-4 Table 3
VERIFICATION_PLUS_PLUS = {
    "A":   ["Walk-through"],
    "B":   ["Walk-through", "Inspection"],
    "C":   ["Inspection", "Semi-formal verification", "Simulation"],
    "D":   ["Inspection", "Semi-formal verification", "Formal verification", "Simulation", "Prototype testing"],
    "QM":  ["Walk-through"],
}
VERIFICATION_PLUS = {
    "A":   ["Inspection", "Semi-formal verification", "Simulation"],
    "B":   ["Semi-formal verification", "Formal verification", "Simulation", "Prototype testing"],
    "C":   ["Walk-through", "Formal verification", "Prototype testing"],
    "D":   ["Walk-through"],
    "QM":  ["Inspection"],
}


def asil_base(asil: str) -> str:
    """Strip the (Y) annotation and return the developed-to base level."""
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
            if fill and not cell.fill.fgColor or (fill and cell.fill.fgColor and cell.fill.fgColor.rgb in (None, "00000000")):
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
# HARA reader
# ---------------------------------------------------------------------------

def read_hara(hara_path: str) -> dict:
    """Extract item metadata and safety goals from a hara-builder xlsx."""
    wb = load_workbook(hara_path, data_only=True)

    # Item metadata
    item: dict[str, str] = {}
    if "00_Title_Page" in wb.sheetnames:
        ws = wb["00_Title_Page"]
        # Title row 3 has "Item name (abbr)"; field labels live in column B starting row 6
        for r in range(6, 25):
            label = ws.cell(row=r, column=2).value
            value = ws.cell(row=r, column=3).value
            if label and value:
                item[str(label).strip()] = str(value).strip()
        # Pull item name from row 3
        title_text = ws.cell(row=3, column=1).value or ""
        if title_text:
            item["Item Title"] = title_text

    # Safety goals
    sgs: list[dict] = []
    if "13_Safety_Goals" not in wb.sheetnames:
        raise ValueError("HARA workbook is missing tab '13_Safety_Goals'. Was this produced by hara-builder?")
    ws = wb["13_Safety_Goals"]
    for r in range(5, ws.max_row + 1):
        sg_id = ws.cell(row=r, column=1).value
        if not sg_id or not str(sg_id).startswith("SG-"):
            continue
        sgs.append({
            "sg_id": str(sg_id),
            "function": ws.cell(row=r, column=2).value or "",
            "hazard": ws.cell(row=r, column=3).value or "",
            "asil": (ws.cell(row=r, column=4).value or "QM"),
            "driving_hara_ids": ws.cell(row=r, column=5).value or "",
            "sg_text": ws.cell(row=r, column=6).value or "",
            "safe_state": ws.cell(row=r, column=7).value or "",
        })

    if not sgs:
        raise ValueError("HARA workbook contained no safety goals (13_Safety_Goals tab is empty).")

    return {"item": item, "safety_goals": sgs, "hara_path": hara_path}


# ---------------------------------------------------------------------------
# Block diagram analysis
# ---------------------------------------------------------------------------

def group_nodes_by_branch(nodes: list[dict]) -> dict[str, list[dict]]:
    """Bucket nodes into Input/Process/Output failure branches based on type."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for n in nodes:
        if not n.get("asil_relevant", True):
            continue
        branch = NODE_TYPE_TO_BRANCH.get(n["type"], "Process failure")
        grouped[branch].append(n)
    return grouped


def find_decomposition_candidates(nodes: list[dict]) -> list[tuple[dict, dict]]:
    """Pairs of nodes that share a redundancy_group AND have disjoint shared_resources."""
    candidates: list[tuple[dict, dict]] = []
    by_group: dict[str, list[dict]] = defaultdict(list)
    for n in nodes:
        rg = n.get("redundancy_group")
        if rg:
            by_group[rg].append(n)
    for group_nodes in by_group.values():
        for a, b in combinations(group_nodes, 2):
            shared_a = set(a.get("shared_resources", []) or [])
            shared_b = set(b.get("shared_resources", []) or [])
            overlap = shared_a & shared_b
            if not overlap:
                candidates.append((a, b))
    return candidates


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, item: dict, fsc_meta: dict) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 2, 4, "Functional Safety Concept (FSC)")
    item_line = item.get("Item Title", "") or item.get("name", "")
    style_title_row(ws, 3, 4, item_line)

    fields = [
        ("Project",        fsc_meta.get("project") or item.get("Project", "")),
        ("FSC Document ID",fsc_meta.get("doc_id", "")),
        ("Revision",       fsc_meta.get("revision", "")),
        ("Date",           fsc_meta.get("date", "")),
        ("Author",         fsc_meta.get("author", "")),
        ("Approver",       fsc_meta.get("approver", "")),
        ("Linked HARA",    fsc_meta.get("linked_hara", "")),
        ("Standard",       "ISO 26262:2018, Part 3 §7 (Functional Safety Concept) and Part 9 §5 (ASIL Decomposition)"),
        ("Methodology",    "FTA top-down: top event → OR gate (Input/Process/Output failure) → basic events per block-diagram node → FSRs"),
    ]
    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left")
        row += 1

    autosize(ws, {1: 4, 2: 22, 3: 70, 4: 4})


def build_doc_control(wb: Workbook) -> None:
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of change", "Approver"])
    placeholders = [
        ("0.1", "", "", "Initial draft generated by fsc-builder skill", ""),
        ("0.2", "", "", "Internal review comments incorporated", ""),
        ("1.0", "", "", "Released for TSC", ""),
    ]
    for i, row_data in enumerate(placeholders, start=4):
        for col, val in enumerate(row_data, start=1):
            ws.cell(row=i, column=col, value=val)
    stripe_body(ws, 4, 6, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_sgs_imported(wb: Workbook, sgs: list[dict], hara_path: str) -> None:
    ws = wb.create_sheet("02_SGs_From_HARA")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Safety Goals — Imported from HARA")
    note = ws.cell(row=2, column=1,
                   value=f"Source: {hara_path}. This tab is read-only echo for traceability. To change a safety goal, "
                         "update the HARA workbook and re-run the FSC generator.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 36

    style_header_row(ws, 4, ["SG_ID", "Function", "Hazard", "ASIL", "Driving HARA IDs", "Safety Goal", "Safe State"])
    for i, sg in enumerate(sgs, start=5):
        ws.cell(row=i, column=1, value=sg["sg_id"])
        ws.cell(row=i, column=2, value=sg["function"])
        ws.cell(row=i, column=3, value=sg["hazard"])
        cell = ws.cell(row=i, column=4, value=sg["asil"])
        asil_color_cell(cell, sg["asil"])
        ws.cell(row=i, column=5, value=sg["driving_hara_ids"])
        ws.cell(row=i, column=6, value=sg["sg_text"])
        ws.cell(row=i, column=7, value=sg["safe_state"])
    end_row = 4 + len(sgs)
    for r in range(5, end_row + 1):
        for c in range(1, 8):
            cell = ws.cell(row=r, column=c)
            if c != 4:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    autosize(ws, {1: 10, 2: 24, 3: 50, 4: 10, 5: 26, 6: 60, 7: 40})


def build_block_diagram(wb: Workbook, nodes: list[dict]) -> None:
    ws = wb.create_sheet("03_System_Block_Diagram")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "System Block Diagram — Node Inventory")
    note = ws.cell(row=2, column=1,
                   value="Insert architecture image above the table (Insert → Picture). The node table is the "
                         "machine-readable view consumed by the FTA expansion.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)
    ws.row_dimensions[2].height = 36

    style_header_row(ws, 4, ["Node ID", "Name", "Type", "FTA Branch", "ASIL-relevant", "Inputs (IDs)", "Outputs (IDs)", "Redundancy Group", "Shared Resources"])
    for i, n in enumerate(nodes, start=5):
        ws.cell(row=i, column=1, value=n["id"])
        ws.cell(row=i, column=2, value=n["name"])
        ws.cell(row=i, column=3, value=n["type"])
        ws.cell(row=i, column=4, value=NODE_TYPE_TO_BRANCH.get(n["type"], "Process failure"))
        ws.cell(row=i, column=5, value="Yes" if n.get("asil_relevant", True) else "No")
        ws.cell(row=i, column=6, value=", ".join(n.get("inputs", []) or []))
        ws.cell(row=i, column=7, value=", ".join(n.get("outputs", []) or []))
        ws.cell(row=i, column=8, value=n.get("redundancy_group") or "")
        ws.cell(row=i, column=9, value=", ".join(n.get("shared_resources", []) or []))
    stripe_body(ws, 5, 4 + len(nodes), 9)
    autosize(ws, {1: 8, 2: 28, 3: 12, 4: 16, 5: 14, 6: 20, 7: 20, 8: 18, 9: 30})

    # Mermaid diagram
    base = 4 + len(nodes) + 3
    ws.cell(row=base, column=1, value="Mermaid representation (paste into mermaid.live to visualise):").font = Font(name=FONT_NAME, italic=True, size=10, color=NAVY)
    mermaid_lines = ["graph LR"]
    for n in nodes:
        label = n["name"].replace('"', "'")
        node_shape = "[" + label + "]"
        if n["type"] in {"sensor", "comm_in", "power_in"}:
            node_shape = "([" + label + "])"
        elif n["type"] in {"actuator", "driver", "comm_out"}:
            node_shape = "[[" + label + "]]"
        mermaid_lines.append(f"  {n['id']}{node_shape}")
    for n in nodes:
        for out in n.get("outputs", []) or []:
            mermaid_lines.append(f"  {n['id']} --> {out}")
    ws.cell(row=base + 1, column=1, value="\n".join(mermaid_lines))
    ws.merge_cells(start_row=base + 1, start_column=1, end_row=base + 1 + len(mermaid_lines) // 2, end_column=9)
    ws.cell(row=base + 1, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    ws.cell(row=base + 1, column=1).font = Font(name="Consolas", size=9)
    ws.row_dimensions[base + 1].height = 18 * max(8, len(mermaid_lines))


def build_fta_combined(wb: Workbook, sgs: list[dict], nodes: list[dict], sg_overrides: dict) -> list[dict]:
    """
    Build the combined FTA tab. Returns an ordered list of basic events with the metadata
    needed to populate the FSR catalog downstream.
    """
    ws = wb.create_sheet("04_FTA_Combined")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Fault Tree Analysis — All Safety Goals")
    note = ws.cell(row=2, column=1,
                   value="One sub-tree per safety goal. Top event (Level 0) → OR gate to three intermediate events "
                         "(Level 1: Input / Process / Output failure) → OR gate to basic events per ASIL-relevant node "
                         "(Level 2). Filter by 'SG_ID' to focus on a single tree.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 40

    style_header_row(ws, 4, ["SG_ID", "Level", "Gate", "Event Code", "Event Description", "Linked Node ID", "Notes"])

    branches_grouped = group_nodes_by_branch(nodes)
    branch_order = ["Input failure", "Process failure", "Output failure"]
    basic_events: list[dict] = []

    row = 5
    for sg in sgs:
        sg_id = sg["sg_id"]
        ftti = sg_overrides.get(sg_id, {}).get("ftti_ms") or "<TBD>"

        # Level 0 — top event
        ws.cell(row=row, column=1, value=sg_id)
        ws.cell(row=row, column=2, value=0)
        ws.cell(row=row, column=3, value="—")
        top_code = f"TE-{sg_id.split('-')[1]}"
        ws.cell(row=row, column=4, value=top_code)
        ws.cell(row=row, column=5, value=f"Violation of {sg_id}: {sg['sg_text']}")
        ws.cell(row=row, column=6, value="—")
        ws.cell(row=row, column=7, value=f"Top-level event. ASIL {sg['asil']}.")
        for c in range(1, 8):
            cell = ws.cell(row=row, column=c)
            cell.font = Font(name=FONT_NAME, bold=True, size=10, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor=NAVY)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER_ALL
        row += 1

        # Level 1 — three intermediates under OR gate
        for branch_idx, branch in enumerate(branch_order, start=1):
            int_code = f"IE-{sg_id.split('-')[1]}-{branch_idx}"
            ws.cell(row=row, column=1, value=sg_id)
            ws.cell(row=row, column=2, value=1)
            ws.cell(row=row, column=3, value="OR")
            ws.cell(row=row, column=4, value=int_code)
            ws.cell(row=row, column=5, value=f"  └── {branch} contributes to violation of {sg_id}")
            ws.cell(row=row, column=6, value="—")
            ws.cell(row=row, column=7, value="Standard intermediate event.")
            for c in range(1, 8):
                cell = ws.cell(row=row, column=c)
                cell.font = Font(name=FONT_NAME, bold=True, size=10)
                cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                cell.border = BORDER_ALL
            row += 1

            # Level 2 — basic events per node assigned to this branch
            branch_nodes = branches_grouped.get(branch, [])
            if not branch_nodes:
                ws.cell(row=row, column=1, value=sg_id)
                ws.cell(row=row, column=2, value=2)
                ws.cell(row=row, column=3, value="—")
                ws.cell(row=row, column=4, value=f"BE-{sg_id.split('-')[1]}-{branch_idx}-00")
                ws.cell(row=row, column=5, value=f"      • (No ASIL-relevant {branch.lower()} nodes in block diagram — analyst review required)")
                ws.cell(row=row, column=6, value="—")
                ws.cell(row=row, column=7, value="Investigate: missing nodes?")
                for c in range(1, 8):
                    cell = ws.cell(row=row, column=c)
                    cell.font = body_font()
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                    cell.fill = PatternFill("solid", fgColor=WARN_YELLOW)
                    cell.border = BORDER_ALL
                row += 1
                continue

            for node_idx, node in enumerate(branch_nodes, start=1):
                be_code = f"BE-{sg_id.split('-')[1]}-{branch_idx}-{node_idx:02d}"
                event_text = (
                    f"      • {branch} of {node['name']} (Node {node['id']}, type={node['type']}) "
                    f"causes branch '{branch}' under {sg_id}."
                )
                ws.cell(row=row, column=1, value=sg_id)
                ws.cell(row=row, column=2, value=2)
                ws.cell(row=row, column=3, value="—")
                ws.cell(row=row, column=4, value=be_code)
                ws.cell(row=row, column=5, value=event_text)
                ws.cell(row=row, column=6, value=node["id"])
                ws.cell(row=row, column=7, value=f"FSR derived: see FSR Catalog row for {be_code}.")
                for c in range(1, 8):
                    cell = ws.cell(row=row, column=c)
                    cell.font = body_font()
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                    if (row % 2) == 0:
                        cell.fill = PatternFill("solid", fgColor=ALT_ROW)
                    cell.border = BORDER_ALL

                basic_events.append({
                    "sg": sg,
                    "branch": branch,
                    "node": node,
                    "be_code": be_code,
                    "ftti": ftti,
                })
                row += 1

    end_row = row - 1
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:G{end_row}"
    autosize(ws, {1: 10, 2: 8, 3: 8, 4: 16, 5: 80, 6: 14, 7: 36})
    return basic_events


def build_fsr_catalog(wb: Workbook, basic_events: list[dict], fsr_overrides: list[dict]) -> list[dict]:
    """One FSR per basic event. Returns list of FSR dicts for downstream tabs."""
    ws = wb.create_sheet("05_FSR_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "Functional Safety Requirements (FSRs)")
    note = ws.cell(row=2, column=1,
                   value="Each row is one FSR derived from one basic event. The wording is template-based; the analyst "
                         "refines <TBD> placeholders during FSC review. FSR ID convention: FSR-<SG number>-<NN>.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)
    ws.row_dimensions[2].height = 36

    style_header_row(ws, 4, ["FSR_ID", "SG_ID", "ASIL (inherited)", "Branch", "Linked Basic Event", "Linked Node", "Functional Safety Requirement", "FTTI (ms)"])

    override_index = {(o.get("sg_id"), o.get("be_code")): o for o in fsr_overrides or []}

    fsrs: list[dict] = []
    counter_per_sg: dict[str, int] = defaultdict(int)
    row = 5
    for be in basic_events:
        sg = be["sg"]
        node = be["node"]
        branch = be["branch"]
        counter_per_sg[sg["sg_id"]] += 1
        sg_num = sg["sg_id"].split("-")[1]
        fsr_id = f"FSR-{sg_num}-{counter_per_sg[sg['sg_id']]:02d}"

        template = FSR_TEMPLATES.get((branch, node["type"])) or (
            "The item shall detect failure of {name} and transition to the safe state ('{safe_state}') within {ftti} ms."
        )
        text = template.format(
            name=node["name"],
            safe_state=sg["safe_state"] or "function disabled, driver in control",
            ftti=be["ftti"],
        )
        override = override_index.get((sg["sg_id"], be["be_code"]))
        if override and override.get("fsr_text"):
            text = override["fsr_text"]

        ws.cell(row=row, column=1, value=fsr_id)
        ws.cell(row=row, column=2, value=sg["sg_id"])
        cell = ws.cell(row=row, column=3, value=sg["asil"])
        asil_color_cell(cell, sg["asil"])
        ws.cell(row=row, column=4, value=branch)
        ws.cell(row=row, column=5, value=be["be_code"])
        ws.cell(row=row, column=6, value=f"{node['id']} — {node['name']}")
        ws.cell(row=row, column=7, value=text)
        ws.cell(row=row, column=8, value=be["ftti"])

        fsrs.append({
            **be,
            "fsr_id": fsr_id,
            "fsr_text": text,
        })
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
    ws.auto_filter.ref = f"A4:H{end_row}"
    autosize(ws, {1: 14, 2: 10, 3: 10, 4: 16, 5: 16, 6: 26, 7: 70, 8: 12})
    return fsrs


def build_asil_allocation(wb: Workbook, sgs: list[dict], nodes: list[dict], fsrs: list[dict], sg_overrides: dict) -> list[dict]:
    """
    For each (SG, node) pair where the node contributes to the SG's chain,
    record the inherited ASIL and propose decomposition options when applicable.
    Returns the per-node allocation rows for the verification matrix.
    """
    ws = wb.create_sheet("06_ASIL_Allocation")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "ASIL Allocation by Block-Diagram Node")
    note = ws.cell(row=2, column=1,
                   value="Default: each ASIL-relevant node inherits the safety goal's top-level ASIL. Where two nodes "
                         "share a redundancy_group AND have non-overlapping shared_resources, valid ISO 26262-9 "
                         "decomposition options are proposed. Independence MUST be confirmed by the analyst before "
                         "writing the developed-to ASIL.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)
    ws.row_dimensions[2].height = 50

    style_header_row(ws, 4, [
        "SG_ID", "Node ID", "Node Name", "Branch", "Inherited ASIL",
        "Proposed Decomposition Options", "Selected Decomposition", "Resulting Per-Node ASIL", "Independence Evidence (analyst)"
    ])

    decomposition_pairs = find_decomposition_candidates(nodes)
    pair_lookup: dict[str, list[str]] = defaultdict(list)
    for a, b in decomposition_pairs:
        pair_lookup[a["id"]].append(b["id"])
        pair_lookup[b["id"]].append(a["id"])

    allocations: list[dict] = []
    # Index: which nodes are linked to which SG via FSRs
    sg_to_nodes: dict[str, set[str]] = defaultdict(set)
    for f in fsrs:
        sg_to_nodes[f["sg"]["sg_id"]].add(f["node"]["id"])

    row = 5
    for sg in sgs:
        sg_id = sg["sg_id"]
        sg_asil_base = asil_base(sg["asil"])
        ovr = sg_overrides.get(sg_id, {}) or {}
        selected_decomp = ovr.get("selected_decomposition")  # e.g. "B(D) + B(D)"

        for node in nodes:
            if node["id"] not in sg_to_nodes[sg_id]:
                continue

            opts = DECOMPOSITION_OPTIONS.get(sg_asil_base, [])
            if pair_lookup.get(node["id"]) and opts:
                opt_text = "; ".join(f"[{label}] with peer {peers[0]}" for label, _, _ in opts for peers in [pair_lookup[node["id"]]])
                # Pick the symmetric option if user hasn't chosen
                default_decomp = next((label for label, e1, e2 in opts if e1 == e2), opts[0][0])
                effective = selected_decomp or default_decomp
                # Map effective to per-node ASIL
                chosen = next((opts_t for opts_t in opts if opts_t[0] == effective), opts[0])
                resulting = chosen[1]  # this node gets first element; peer would get second
            else:
                opt_text = "None (no eligible peer node — full inheritance)"
                effective = "None (full inheritance)"
                resulting = sg["asil"]

            ws.cell(row=row, column=1, value=sg_id)
            ws.cell(row=row, column=2, value=node["id"])
            ws.cell(row=row, column=3, value=node["name"])
            ws.cell(row=row, column=4, value=NODE_TYPE_TO_BRANCH.get(node["type"], "Process failure"))
            cell = ws.cell(row=row, column=5, value=sg["asil"])
            asil_color_cell(cell, sg["asil"])
            ws.cell(row=row, column=6, value=opt_text)
            ws.cell(row=row, column=7, value=effective)
            cell = ws.cell(row=row, column=8, value=resulting)
            asil_color_cell(cell, resulting)
            ws.cell(row=row, column=9, value="<TBD: cite independence analysis document or argument>")

            allocations.append({
                "sg_id": sg_id,
                "node": node,
                "inherited_asil": sg["asil"],
                "decomposition": effective,
                "resulting_asil": resulting,
            })
            row += 1

    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 10):
            cell = ws.cell(row=r, column=c)
            if c not in (5, 8):
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL

    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:I{end_row}"
    autosize(ws, {1: 10, 2: 10, 3: 26, 4: 14, 5: 12, 6: 50, 7: 24, 8: 14, 9: 50})
    return allocations


def build_verification_matrix(wb: Workbook, fsrs: list[dict], allocations: list[dict]) -> None:
    ws = wb.create_sheet("07_Verification_Matrix")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Verification Matrix (ISO 26262-4, Table 3)")
    note = ws.cell(row=2, column=1,
                   value="Verification methods are recommended per the ALLOCATED ASIL of the implementing element "
                         "(i.e., after any decomposition), not the safety goal's top-level ASIL.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    ws.row_dimensions[2].height = 36

    style_header_row(ws, 4, ["FSR_ID", "SG_ID", "SG ASIL", "Allocated ASIL", "Recommended Methods (++)", "Optional Methods (+)", "Confirmation Review Independence"])

    # Build node->allocated_asil map per SG
    alloc_lookup: dict[tuple[str, str], str] = {}
    for a in allocations:
        alloc_lookup[(a["sg_id"], a["node"]["id"])] = a["resulting_asil"]

    row = 5
    for f in fsrs:
        sg_id = f["sg"]["sg_id"]
        node_id = f["node"]["id"]
        allocated = alloc_lookup.get((sg_id, node_id), f["sg"]["asil"])
        base = asil_base(allocated)
        plus_plus = ", ".join(VERIFICATION_PLUS_PLUS.get(base, []))
        plus = ", ".join(VERIFICATION_PLUS.get(base, []))
        independence = "I3 (different organisational unit)" if base == "D" else (
            "I2 (different team)" if base == "C" else (
            "I1 (different person)" if base in ("A", "B") else "—"))

        ws.cell(row=row, column=1, value=f["fsr_id"])
        ws.cell(row=row, column=2, value=sg_id)
        cell = ws.cell(row=row, column=3, value=f["sg"]["asil"])
        asil_color_cell(cell, f["sg"]["asil"])
        cell = ws.cell(row=row, column=4, value=allocated)
        asil_color_cell(cell, allocated)
        ws.cell(row=row, column=5, value=plus_plus)
        ws.cell(row=row, column=6, value=plus)
        ws.cell(row=row, column=7, value=independence)
        row += 1

    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 8):
            cell = ws.cell(row=r, column=c)
            if c not in (3, 4):
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 5) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL

    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:G{end_row}"
    autosize(ws, {1: 14, 2: 10, 3: 10, 4: 14, 5: 50, 6: 36, 7: 32})


def _trees_from_basic_events(sgs: list[dict], basic_events: list[dict]) -> list:
    """Convert the basic-event list into FaultTree objects ready for rendering."""
    if not _FT_AVAILABLE:
        return []
    by_sg: dict[str, list[dict]] = defaultdict(list)
    for be in basic_events:
        by_sg[be["sg"]["sg_id"]].append(be)
    sg_lookup = {s["sg_id"]: s for s in sgs}
    trees = []
    branch_codes = {"Input failure": 1, "Process failure": 2, "Output failure": 3}
    for sg_id, bes in by_sg.items():
        sg = sg_lookup[sg_id]
        sg_num = sg_id.split("-")[1]
        t = FaultTree(sg_id=sg_id, sg_text=sg["sg_text"], asil=sg["asil"])
        for branch_name, branch_idx in branch_codes.items():
            t.add_intermediate(f"IE-{sg_num}-{branch_idx}", f"{branch_name} contributes to violation of {sg_id}")
        for be in bes:
            branch_idx = branch_codes.get(be["branch"], 2)
            label = be["node"]["name"]
            t.add_basic_event(f"IE-{sg_num}-{branch_idx}", be["be_code"], label, be["node"]["id"])
        trees.append(t)
    return trees


def build_fta_diagrams(wb: Workbook, sgs: list[dict], basic_events: list[dict], output_xlsx_path: str) -> dict:
    """Render one PNG fault tree per safety goal, embed each on its own row in a new tab."""
    if not _FT_AVAILABLE:
        return {"rendered": 0, "skipped": "graphviz module not available"}

    trees = _trees_from_basic_events(sgs, basic_events)
    if not trees:
        return {"rendered": 0}

    diagram_dir = Path(output_xlsx_path).parent / (Path(output_xlsx_path).stem + "_diagrams")
    diagram_dir.mkdir(parents=True, exist_ok=True)

    ws = wb.create_sheet("04b_FTA_Diagrams")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Fault Tree Diagrams (one per Safety Goal)")
    note = ws.cell(row=2, column=1,
                   value="Visual fault trees rendered with Graphviz. Standard FTA notation: red rectangle = top event; "
                         "yellow shield = OR gate; light-blue rectangle = intermediate event; gray circle = basic event. "
                         "PNGs are also saved alongside the workbook in <output_basename>_diagrams/ for use in slide decks "
                         "and standalone reviews.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 50

    rendered = 0
    row = 4
    for tree in trees:
        basename = diagram_dir / f"FT_{tree.sg_id}"
        try:
            paths = render_fault_tree(tree, basename, formats=("png",))
        except Exception as exc:
            ws.cell(row=row, column=1, value=f"{tree.sg_id} — render failed: {exc}").font = Font(name=FONT_NAME, color="C00000")
            row += 2
            continue

        ws.cell(row=row, column=1, value=f"{tree.sg_id} — ASIL {tree.asil} — {tree.sg_text}").font = Font(name=FONT_NAME, bold=True, size=12, color=NAVY)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        ws.row_dimensions[row].height = 22
        row += 1

        try:
            img = XLImage(paths["png"])
            # Scale down — original PNG is wide; cap width to a readable but compact value
            max_width = 1100
            if img.width > max_width:
                ratio = max_width / img.width
                img.width = max_width
                img.height = int(img.height * ratio)
            anchor = f"A{row}"
            ws.add_image(img, anchor)
            # Reserve enough rows underneath for the image
            row += max(20, int(img.height / 18))
        except Exception as exc:
            ws.cell(row=row, column=1, value=f"(Image embed failed: {exc})").font = Font(name=FONT_NAME, italic=True, color="C00000")
            row += 2

        row += 2  # spacer between trees
        rendered += 1

    autosize(ws, {1: 24, 2: 24, 3: 24, 4: 24, 5: 24, 6: 24})
    return {"rendered": rendered, "diagram_dir": str(diagram_dir)}


def build_tsc_handoff(wb: Workbook, fsrs: list[dict], allocations: list[dict]) -> None:
    ws = wb.create_sheet("08_TSC_Handoff")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "Technical Safety Concept (TSC) Hand-off")
    note = ws.cell(row=2, column=1,
                   value="Each FSR is pre-populated with two TSR placeholder rows. The TSC author refines these into "
                         "hardware and software technical safety requirements during ISO 26262-4 system-level work.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)
    ws.row_dimensions[2].height = 36

    style_header_row(ws, 4, ["FSR_ID", "FSR Text", "Allocated ASIL", "Allocation Target Node", "TSR ID", "Technical Safety Requirement", "TSR Type", "Verification Method", "Notes"])

    alloc_lookup: dict[tuple[str, str], str] = {(a["sg_id"], a["node"]["id"]): a["resulting_asil"] for a in allocations}

    row = 5
    for f in fsrs:
        sg_id = f["sg"]["sg_id"]
        allocated = alloc_lookup.get((sg_id, f["node"]["id"]), f["sg"]["asil"])
        for j, kind in enumerate(["HW-TSR", "SW-TSR"], start=1):
            tsr_id = f"TSR-{f['fsr_id'].split('-', 1)[1]}-{j:02d}"
            ws.cell(row=row, column=1, value=f["fsr_id"] if j == 1 else "")
            ws.cell(row=row, column=2, value=f["fsr_text"] if j == 1 else "")
            if j == 1:
                cell = ws.cell(row=row, column=3, value=allocated)
                asil_color_cell(cell, allocated)
                ws.cell(row=row, column=4, value=f"{f['node']['id']} — {f['node']['name']}")
            ws.cell(row=row, column=5, value=tsr_id)
            ws.cell(row=row, column=6, value="(Derived requirement — to be authored in TSC phase.)")
            ws.cell(row=row, column=7, value=kind)
            ws.cell(row=row, column=8, value="Test")
            ws.cell(row=row, column=9, value="")
            row += 1

    end_row = row - 1
    for r in range(5, end_row + 1):
        for c in range(1, 10):
            cell = ws.cell(row=r, column=c)
            if c != 3:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if ((r - 5) // 2) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL
    ws.freeze_panes = "A5"
    autosize(ws, {1: 14, 2: 60, 3: 14, 4: 26, 5: 16, 6: 50, 7: 10, 8: 14, 9: 24})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(hara_path: str, block_diagram_path: str, output_path: str) -> dict:
    hara_data = read_hara(hara_path)
    with open(block_diagram_path) as f:
        bd = json.load(f)

    nodes = bd.get("block_diagram", {}).get("nodes", [])
    if not nodes:
        raise ValueError("Block diagram input must include at least one node under block_diagram.nodes.")

    fsc_meta = bd.get("fsc_metadata", {}) or {}
    fsc_meta.setdefault("linked_hara", hara_path)
    sg_overrides = bd.get("safety_goal_overrides", {}) or {}
    fsr_overrides = bd.get("fsr_overrides", []) or []

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, hara_data["item"], fsc_meta)
    build_doc_control(wb)
    build_sgs_imported(wb, hara_data["safety_goals"], hara_path)
    build_block_diagram(wb, nodes)
    basic_events = build_fta_combined(wb, hara_data["safety_goals"], nodes, sg_overrides)
    diagram_summary = build_fta_diagrams(wb, hara_data["safety_goals"], basic_events, output_path)
    fsrs = build_fsr_catalog(wb, basic_events, fsr_overrides)
    allocations = build_asil_allocation(wb, hara_data["safety_goals"], nodes, fsrs, sg_overrides)
    build_verification_matrix(wb, fsrs, allocations)
    build_tsc_handoff(wb, fsrs, allocations)

    wb.active = 0
    wb.save(output_path)

    return {
        "safety_goals": len(hara_data["safety_goals"]),
        "asil_relevant_nodes": sum(1 for n in nodes if n.get("asil_relevant", True)),
        "basic_events": len(basic_events),
        "fsrs": len(fsrs),
        "asil_allocations": len(allocations),
        "decomposition_candidate_pairs": len(find_decomposition_candidates(nodes)),
        "fault_tree_diagrams": diagram_summary,
        "output_path": output_path,
    }


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_fsc.py <hara.xlsx> <block_diagram.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(summary, indent=2))
