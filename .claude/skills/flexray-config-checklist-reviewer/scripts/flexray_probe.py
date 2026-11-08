"""FlexRay configuration xlsx probe — extract metadata and tables."""

from __future__ import annotations

from dataclasses import dataclass, field
from openpyxl import load_workbook


@dataclass
class ProbedFlexRay:
    path: str
    sheet_names: list[str] = field(default_factory=list)
    cluster_name: str = ""
    doc_id: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    gdCycle_ms: float = 0
    gdMacrotick_us: float = 1
    gMacroPerCycle: int = 0
    gNumberOfStaticSlots: int = 0
    gNumberOfMinislots: int = 0
    gdStaticSlot_macroticks: int = 640
    gdNIT_macroticks: int = 1000
    channel_a_speed: float = 0
    channel_b_speed: float = 0
    nodes: list[dict] = field(default_factory=list)
    frames: list[dict] = field(default_factory=list)
    static_slots: list[dict] = field(default_factory=list)
    dynamic_slots: list[dict] = field(default_factory=list)
    revision_history_rows: int = 0


def probe(path: str) -> ProbedFlexRay:
    """Probe a FlexRay config xlsx and extract tables, metadata."""
    wb = load_workbook(path, data_only=True)
    p = ProbedFlexRay(path=path, sheet_names=wb.sheetnames)

    # Title page
    if "Title_Page" in wb.sheetnames or "Title" in wb.sheetnames:
        ws = wb["Title_Page"] if "Title_Page" in wb.sheetnames else wb["Title"]
        for row in ws.iter_rows(min_row=1, max_row=20, values_only=True):
            if row and len(row) >= 2:
                cell0, cell1 = str(row[0] or ""), str(row[1] or "")
                if "Cluster Name" in cell0:
                    p.cluster_name = str(row[2] or "") if len(row) > 2 else ""
                if "Document ID" in cell0:
                    p.doc_id = str(row[2] or "") if len(row) > 2 else ""
                if "Revision" in cell0:
                    p.revision = str(row[2] or "") if len(row) > 2 else ""
                if "Status" in cell0:
                    p.status = str(row[2] or "") if len(row) > 2 else ""
                if "Author" in cell0:
                    p.author = str(row[2] or "") if len(row) > 2 else ""
                if "Approver" in cell0:
                    p.approver = str(row[2] or "") if len(row) > 2 else ""

    # Cluster Parameters
    for sname in ["Cluster_Parameters", "Cluster Parameters", "Timing"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            for row in ws.iter_rows(min_row=1, max_row=50, values_only=True):
                if row and len(row) >= 2:
                    param = str(row[0] or "").lower()
                    val = row[1]
                    if "gdcycle" in param and val:
                        p.gdCycle_ms = float(val) if isinstance(val, (int, float)) else 0
                    if "macrotick" in param and not "macro" in param and val:
                        p.gdMacrotick_us = float(val) if isinstance(val, (int, float)) else 1
                    if "gmacroper" in param and val:
                        p.gMacroPerCycle = int(val) if isinstance(val, (int, float)) else 0
                    if "staticslot" in param and "number" in param and val:
                        p.gNumberOfStaticSlots = int(val) if isinstance(val, (int, float)) else 0
                    if "minislot" in param and "number" in param and val:
                        p.gNumberOfMinislots = int(val) if isinstance(val, (int, float)) else 0
            break

    # Channel Config
    for sname in ["Channel_Config", "Channel Config"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            row_count = 0
            for row in ws.iter_rows(min_row=3, max_row=20, values_only=True):
                if row and len(row) >= 2:
                    ch = str(row[0] or "").strip()
                    spd = row[1]
                    if ch == "A" and spd:
                        p.channel_a_speed = float(spd) if isinstance(spd, (int, float)) else 0
                    elif ch == "B" and spd:
                        p.channel_b_speed = float(spd) if isinstance(spd, (int, float)) else 0
            break

    # Node Inventory
    for sname in ["Node_Inventory", "Node Inventory"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            for row in ws.iter_rows(min_row=4, max_row=100, values_only=True):
                if row and len(row) >= 2 and row[0]:
                    p.nodes.append({
                        "ecu_id": str(row[0] or ""),
                        "name": str(row[1] or "") if len(row) > 1 else "",
                    })
            break

    # Frame Catalog
    for sname in ["Frame_Catalog", "Frame Catalog"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            for row in ws.iter_rows(min_row=4, max_row=100, values_only=True):
                if row and len(row) >= 2 and row[0]:
                    p.frames.append({
                        "frame_id": str(row[0] or ""),
                        "name": str(row[1] or "") if len(row) > 1 else "",
                        "data_length_bytes": int(row[2]) if len(row) > 2 and isinstance(row[2], (int, float)) else 0,
                    })
            break

    # Static Slots
    for sname in ["Static_Slot_Alloc", "Static Slot Allocation"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            for row in ws.iter_rows(min_row=4, max_row=200, values_only=True):
                if row and len(row) >= 3 and row[0] is not None:
                    p.static_slots.append({
                        "slot_id": row[0],
                        "node_id": str(row[1] or "") if len(row) > 1 else "",
                        "frame_id": str(row[2] or "") if len(row) > 2 else "",
                    })
            break

    # Dynamic Slots
    for sname in ["Dynamic_Slot_Alloc", "Dynamic Slot Allocation"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            for row in ws.iter_rows(min_row=4, max_row=200, values_only=True):
                if row and len(row) >= 2 and row[0] is not None:
                    p.dynamic_slots.append({
                        "minislot_id": row[0],
                        "node_ids": str(row[1] or "") if len(row) > 1 else "",
                    })
            break

    # Revision history
    for sname in ["Document_Control", "Document Control"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            count = 0
            for row in ws.iter_rows(min_row=4, max_row=100, values_only=True):
                if row and row[0]:
                    count += 1
            p.revision_history_rows = count
            break

    return p
