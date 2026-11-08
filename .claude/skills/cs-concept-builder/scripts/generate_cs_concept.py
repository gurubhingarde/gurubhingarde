"""
CS Concept Builder — generates ISO/SAE 21434 Cybersecurity Concept workbook
from (a) CS Goals xlsx produced by cs-goals-builder and (b) a block-diagram JSON.

Usage:
    python generate_cs_concept.py <cs_goals.xlsx> <block_diagram.json> <output.xlsx>
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from cs_goals_reader import read_cs_goals


# Node types to security property mapping
NODE_TYPE_TO_BRANCH = {
    "gateway": ["Authentication", "Authorization", "Integrity-Confidentiality"],
    "processor": ["Authentication", "Authorization", "Integrity-Confidentiality", "Availability"],
    "ecu": ["Authentication", "Authorization", "Integrity-Confidentiality", "Availability"],
    "memory": ["Integrity-Confidentiality", "Availability"],
    "key_store": ["Integrity-Confidentiality"],
    "comm_channel": ["Authentication", "Integrity-Confidentiality"],
    "debug_if": ["Authentication", "Authorization"],
}

# CAL color scheme
CAL_COLORS = {
    "CAL-1": "FFE699",
    "CAL-2": "F4B084",
    "CAL-3": "F8696B",
}

# Styling constants
FONT_NAME = "Calibri"
NAVY = "1F3864"
ALT_ROW = "F2F2F2"
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
            if fill and (not cell.fill.fgColor or cell.fill.fgColor.rgb in (None, "00000000")):
                cell.fill = fill


def autosize(ws, widths: dict[int, int]) -> None:
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width


def cal_color_cell(cell, cal_value: str) -> None:
    if cal_value in CAL_COLORS:
        cell.fill = PatternFill("solid", fgColor=CAL_COLORS[cal_value])
        cell.font = Font(name=FONT_NAME, bold=True, color="FFFFFF" if cal_value == "CAL-3" else "000000")
        cell.alignment = Alignment(horizontal="center", vertical="center")


def read_block_diagram(json_path: str) -> dict:
    """Load and validate block diagram JSON."""
    with open(json_path, 'r') as f:
        bd = json.load(f)
    return bd


# ===== TAB BUILDERS =====

def build_title_page(wb: Workbook, item: dict, cs_meta: dict) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 2, 4, "Cybersecurity Concept (CS Concept)")
    item_line = item.get("Item Title", "") or item.get("name", "")
    style_title_row(ws, 3, 4, item_line)

    fields = [
        ("Project", cs_meta.get("project") or item.get("Project", "")),
        ("CS Concept Doc ID", cs_meta.get("doc_id", "")),
        ("Revision", cs_meta.get("revision", "")),
        ("Date", cs_meta.get("date", "")),
        ("Author", cs_meta.get("author", "")),
        ("Linked TARA", cs_meta.get("linked_tara", "")),
        ("Linked CS Goals", cs_meta.get("linked_cs_goals", "")),
        ("Standard", "ISO/SAE 21434:2021 Section 9.4.5"),
        ("Methodology", "Goal-driven CSR derivation across six security properties per node"),
    ]
    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value)
        row += 1
    autosize(ws, {2: 22, 3: 50})


def build_document_control(wb: Workbook) -> None:
    ws = wb.create_sheet("01_Document_Control")
    headers = ["Revision", "Date", "Author", "Description"]
    style_header_row(ws, 2, headers)
    ws.cell(row=3, column=1, value="0.1")
    ws.cell(row=3, column=2, value=datetime.now().strftime("%Y-%m-%d"))
    ws.cell(row=3, column=3, value="Generated")
    ws.cell(row=3, column=4, value="Initial draft from CS Goals and block diagram")
    stripe_body(ws, 3, 3, 4)
    autosize(ws, {1: 12, 2: 12, 3: 20, 4: 50})


def build_csg_echo(wb: Workbook, csg_list: list[dict]) -> None:
    ws = wb.create_sheet("02_CS_Goals_Echo")
    headers = ["CSG ID", "Threat", "Asset", "CAL", "TARA IDs", "CS Goal Text"]
    style_header_row(ws, 2, headers)

    row = 3
    for csg in csg_list:
        ws.cell(row=row, column=1, value=csg["csg_id"])
        ws.cell(row=row, column=2, value=csg["threat"])
        ws.cell(row=row, column=3, value=csg["asset"])
        cal_cell = ws.cell(row=row, column=4, value=csg["cal"])
        cal_color_cell(cal_cell, csg["cal"])
        ws.cell(row=row, column=5, value=csg["driving_tara_ids"])
        ws.cell(row=row, column=6, value=csg["csg_text"])
        row += 1

    stripe_body(ws, 3, row - 1, 6)
    autosize(ws, {1: 12, 2: 20, 3: 20, 4: 10, 5: 20, 6: 50})


def build_block_diagram_tab(wb: Workbook, nodes: list[dict]) -> None:
    ws = wb.create_sheet("03_System_Block_Diagram")
    headers = ["Node ID", "Node Name", "Type", "CAL Relevant", "Inputs", "Outputs", "Shared Resources"]
    style_header_row(ws, 2, headers)

    row = 3
    for node in sorted(nodes, key=lambda n: n.get("id", "")):
        ws.cell(row=row, column=1, value=node.get("id"))
        ws.cell(row=row, column=2, value=node.get("name"))
        ws.cell(row=row, column=3, value=node.get("type"))
        ws.cell(row=row, column=4, value="Yes" if node.get("cal_relevant", True) else "No")
        ws.cell(row=row, column=5, value=", ".join(node.get("inputs", [])))
        ws.cell(row=row, column=6, value=", ".join(node.get("outputs", [])))
        ws.cell(row=row, column=7, value=", ".join(node.get("shared_resources", [])))
        row += 1

    stripe_body(ws, 3, row - 1, 7)
    autosize(ws, {1: 10, 2: 20, 3: 20, 4: 12, 5: 20, 6: 20, 7: 30})


def build_cs_concept_argument(wb: Workbook, csg_list: list[dict], nodes: list[dict]) -> None:
    ws = wb.create_sheet("04_CS_Concept_Argument")
    headers = ["CSG ID", "Threat/Asset", "OR Gate", "Branch", "Node ID", "Basic Event", "CAL"]
    style_header_row(ws, 2, headers)

    row = 3
    for csg in csg_list:
        csg_id = csg["csg_id"]
        threat_asset = f"{csg['threat']} / {csg['asset']}"

        # OR gate row
        ws.cell(row=row, column=1, value=csg_id)
        ws.cell(row=row, column=2, value=threat_asset)
        ws.cell(row=row, column=3, value="OR (Branch)")
        row += 1

        # Branches and basic events
        for branch in ["Authentication", "Authorization", "Integrity-Confidentiality", "Availability"]:
            for node in nodes:
                if not node.get("cal_relevant", True):
                    continue
                node_type = node.get("type", "")
                if node_type not in NODE_TYPE_TO_BRANCH:
                    continue
                if branch not in NODE_TYPE_TO_BRANCH[node_type]:
                    continue

                ws.cell(row=row, column=4, value=branch)
                ws.cell(row=row, column=5, value=node.get("id"))
                ws.cell(row=row, column=6, value=f"Failure of {node.get('name')} {branch.lower()}")
                cal_cell = ws.cell(row=row, column=7, value=csg["cal"])
                cal_color_cell(cal_cell, csg["cal"])
                row += 1

    stripe_body(ws, 3, row - 1, 7)
    autosize(ws, {1: 12, 2: 30, 3: 20, 4: 25, 5: 10, 6: 40, 7: 10})


def build_csr_catalog(wb: Workbook, csr_list: list[dict]) -> None:
    ws = wb.create_sheet("05_CSR_Catalog")
    headers = ["CSR ID", "Parent CSG", "CAL", "Branch", "Node ID", "Requirement Text", "Verification Method"]
    style_header_row(ws, 2, headers)

    row = 3
    for csr in csr_list:
        ws.cell(row=row, column=1, value=csr["csr_id"])
        ws.cell(row=row, column=2, value=csr["parent_csg"])
        cal_cell = ws.cell(row=row, column=3, value=csr["cal"])
        cal_color_cell(cal_cell, csr["cal"])
        ws.cell(row=row, column=4, value=csr["branch"])
        ws.cell(row=row, column=5, value=csr["node_id"])
        ws.cell(row=row, column=6, value=csr["requirement_text"])
        ws.cell(row=row, column=7, value=csr.get("verification_method", "Penetration Testing"))
        row += 1

    stripe_body(ws, 3, row - 1, 7)
    autosize(ws, {1: 12, 2: 14, 3: 10, 4: 20, 5: 10, 6: 50, 7: 30})


def build_cal_allocation(wb: Workbook, nodes: list[dict], csr_list: list[dict]) -> None:
    ws = wb.create_sheet("06_CAL_Allocation")
    headers = ["Node ID", "Node Name", "Type", "Inherited CAL", "CSR Count"]
    style_header_row(ws, 2, headers)

    node_cals = defaultdict(lambda: "CAL-1")
    for csr in csr_list:
        nid = csr["node_id"]
        cal = csr["cal"]
        if cal == "CAL-3" or (node_cals[nid] == "CAL-1" and cal in ["CAL-2", "CAL-3"]) or (node_cals[nid] == "CAL-2" and cal == "CAL-3"):
            node_cals[nid] = cal

    csr_per_node = defaultdict(int)
    for csr in csr_list:
        csr_per_node[csr["node_id"]] += 1

    row = 3
    for node in sorted(nodes, key=lambda n: n.get("id", "")):
        nid = node.get("id")
        ws.cell(row=row, column=1, value=nid)
        ws.cell(row=row, column=2, value=node.get("name"))
        ws.cell(row=row, column=3, value=node.get("type"))
        cal_cell = ws.cell(row=row, column=4, value=node_cals[nid])
        cal_color_cell(cal_cell, node_cals[nid])
        ws.cell(row=row, column=5, value=csr_per_node[nid])
        row += 1

    stripe_body(ws, 3, row - 1, 5)
    autosize(ws, {1: 10, 2: 20, 3: 20, 4: 14, 5: 12})


def build_verification_matrix(wb: Workbook, csr_list: list[dict]) -> None:
    ws = wb.create_sheet("07_Verification_Matrix")
    headers = ["CSR ID", "CAL", "Requirement Text", "Penetration Testing", "Fuzzing", "Code Review", "Static Analysis"]
    style_header_row(ws, 2, headers)

    row = 3
    for csr in csr_list:
        ws.cell(row=row, column=1, value=csr["csr_id"])
        cal_cell = ws.cell(row=row, column=2, value=csr["cal"])
        cal_color_cell(cal_cell, csr["cal"])
        ws.cell(row=row, column=3, value=csr["requirement_text"])
        cal = csr["cal"]
        ws.cell(row=row, column=4, value="++" if cal in ["CAL-2", "CAL-3"] else "+")
        ws.cell(row=row, column=5, value="++" if cal == "CAL-3" else "+")
        ws.cell(row=row, column=6, value="++" if cal in ["CAL-2", "CAL-3"] else "")
        ws.cell(row=row, column=7, value="++" if cal == "CAL-3" else "+")
        row += 1

    stripe_body(ws, 3, row - 1, 7)
    autosize(ws, {1: 12, 2: 10, 3: 50, 4: 14, 5: 10, 6: 12, 7: 14})


def build_csi_handoff(wb: Workbook, csr_list: list[dict]) -> None:
    ws = wb.create_sheet("08_CSI_Handoff")
    headers = ["CSR ID", "Requirement Text", "CSI ID", "Implementation", "Verification Status"]
    style_header_row(ws, 2, headers)

    row = 3
    for i, csr in enumerate(csr_list, start=1):
        ws.cell(row=row, column=1, value=csr["csr_id"])
        ws.cell(row=row, column=2, value=csr["requirement_text"])
        ws.cell(row=row, column=3, value=f"CSI-{i:03d}")
        ws.cell(row=row, column=4, value="<TBD>")
        ws.cell(row=row, column=5, value="Pending")
        row += 1

    stripe_body(ws, 3, row - 1, 5)
    autosize(ws, {1: 12, 2: 50, 3: 12, 4: 30, 5: 18})


def build_references(wb: Workbook) -> None:
    ws = wb.create_sheet("09_References")
    headers = ["Reference", "Source"]
    style_header_row(ws, 2, headers)

    refs = [
        ("ISO/SAE 21434:2021", "Road vehicles - Cybersecurity engineering"),
        ("CS Goals Input", "Cybersecurity Goals workbook from TARA analysis"),
        ("Block Diagram", "System architecture and node inventory JSON"),
    ]
    row = 3
    for ref, source in refs:
        ws.cell(row=row, column=1, value=ref)
        ws.cell(row=row, column=2, value=source)
        row += 1

    stripe_body(ws, 3, row - 1, 2)
    autosize(ws, {1: 30, 2: 60})


# ===== MAIN =====

def main():
    if len(sys.argv) != 4:
        print("Usage: python generate_cs_concept.py <cs_goals.xlsx> <block_diagram.json> <output.xlsx>")
        sys.exit(1)

    cs_goals_path, bd_json_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]

    print(f"Reading CS Goals from {cs_goals_path}...")
    cs_data = read_cs_goals(cs_goals_path)
    item = cs_data["item"]
    csg_list = cs_data["cybersecurity_goals"]

    print(f"Reading block diagram from {bd_json_path}...")
    bd = read_block_diagram(bd_json_path)
    nodes = bd.get("nodes", [])

    # Generate CSRs
    csr_list = []
    csr_counter = 1
    for csg in csg_list:
        csg_id = csg["csg_id"]
        cal = csg["cal"]
        for node in nodes:
            if not node.get("cal_relevant", True):
                continue
            node_type = node.get("type", "")
            if node_type not in NODE_TYPE_TO_BRANCH:
                continue
            for branch in NODE_TYPE_TO_BRANCH[node_type]:
                template_base = f"The item shall implement {branch.lower()} on {node.get('name')}"
                csr = {
                    "csr_id": f"CSR-{csr_counter:03d}",
                    "parent_csg": csg_id,
                    "cal": cal,
                    "branch": branch,
                    "node_id": node.get("id"),
                    "requirement_text": template_base,
                    "verification_method": "Penetration Testing / Code Review",
                }
                csr_list.append(csr)
                csr_counter += 1

    print(f"Generating workbook with {len(csr_list)} CSRs...")
    wb = Workbook()
    wb.remove(wb.active)

    cs_meta = {
        "doc_id": "CS-CONCEPT-001",
        "revision": "0.1",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "author": "Generated",
        "project": item.get("Project", ""),
        "linked_tara": "",
        "linked_cs_goals": cs_goals_path,
    }

    build_title_page(wb, item, cs_meta)
    build_document_control(wb)
    build_csg_echo(wb, csg_list)
    build_block_diagram_tab(wb, nodes)
    build_cs_concept_argument(wb, csg_list, nodes)
    build_csr_catalog(wb, csr_list)
    build_cal_allocation(wb, nodes, csr_list)
    build_verification_matrix(wb, csr_list)
    build_csi_handoff(wb, csr_list)
    build_references(wb)

    wb.save(output_path)
    print(f"Saved to {output_path}")
    print(f"Summary: {len(csg_list)} CS Goals, {len(nodes)} nodes, {len(csr_list)} CSRs")


if __name__ == "__main__":
    main()
