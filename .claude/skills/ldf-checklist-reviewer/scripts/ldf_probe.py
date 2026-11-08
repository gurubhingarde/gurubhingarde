"""
LDF Probe — extracts cluster metadata, nodes, frames, signals, schedule tables from an LDF xlsx.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from openpyxl import load_workbook


@dataclass
class NodeInfo:
    node_type: str
    name: str
    identifier: str
    baudrate: str = "19.2"
    publishes: list[str] = field(default_factory=list)
    subscribes: list[str] = field(default_factory=list)


@dataclass
class FrameInfo:
    frame_id: str
    name: str
    frame_type: str
    length: int
    period_ms: int
    publisher: Optional[str] = None
    subscribers: list[str] = field(default_factory=list)


@dataclass
class SignalInfo:
    signal_id: str
    name: str
    frame: str
    start_bit: int
    length: int
    signal_type: str
    min_val: float = 0
    max_val: float = 255
    unit: str = ""
    encoding: str = "linear"


@dataclass
class ScheduleEntry:
    frame: str
    slot_ms: int


@dataclass
class ScheduleTableInfo:
    name: str
    mode: str
    frames: list[ScheduleEntry] = field(default_factory=list)


@dataclass
class ProbedLDF:
    """Probed LDF metadata."""

    path: str
    sheet_names: list[str]
    cluster_name: Optional[str] = None
    cluster_abbr: Optional[str] = None
    project: Optional[str] = None
    doc_id: Optional[str] = None
    revision: Optional[str] = None
    status: Optional[str] = None
    author: Optional[str] = None
    approver: Optional[str] = None
    lin_version: str = "2.2A"
    baud_rate_kbps: float = 19.2

    master_node: Optional[NodeInfo] = None
    slave_nodes: list[NodeInfo] = field(default_factory=list)
    frames: list[FrameInfo] = field(default_factory=list)
    signals: list[SignalInfo] = field(default_factory=list)
    schedules: list[ScheduleTableInfo] = field(default_factory=list)

    has_table_of_contents: bool = False
    revision_history_rows: int = 0
    linked_documents: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.sheet_names:
            self.sheet_names = []


def probe(xlsx_path: str | Path) -> ProbedLDF:
    """
    Extract all LDF metadata from an xlsx file.
    """
    xlsx_path = Path(xlsx_path)
    wb = load_workbook(xlsx_path, data_only=True)
    sheet_names = wb.sheetnames

    probed = ProbedLDF(path=str(xlsx_path), sheet_names=sheet_names)

    # Title page
    if "Title" in sheet_names:
        ws_title = wb["Title"]
        probed.cluster_name = _get_cell_value(ws_title, "C2")
        probed.project = _get_cell_value(ws_title, "C5")
        probed.doc_id = _get_cell_value(ws_title, "C6")
        probed.revision = _get_cell_value(ws_title, "C7")
        probed.author = _get_cell_value(ws_title, "C8")
        probed.approver = _get_cell_value(ws_title, "C9")
        probed.lin_version = _get_cell_value(ws_title, "C10") or "2.2A"
        baud = _get_cell_value(ws_title, "C11")
        if baud:
            try:
                probed.baud_rate_kbps = float(str(baud).replace("kbps", "").strip())
            except (ValueError, AttributeError):
                probed.baud_rate_kbps = 19.2

    # Document Control
    if "Document Control" in sheet_names:
        ws_dc = wb["Document Control"]
        probed.has_table_of_contents = True
        # Count revision history rows (excluding header)
        for row in range(4, 100):
            if ws_dc.cell(row, 1).value:
                probed.revision_history_rows += 1
            else:
                break

    # Node Attributes
    if "Node Attributes" in sheet_names:
        ws_nodes = wb["Node Attributes"]
        for row in range(4, 50):
            node_type = _get_cell_value(ws_nodes, row, 1)
            if not node_type:
                break
            name = _get_cell_value(ws_nodes, row, 2)
            identifier = _get_cell_value(ws_nodes, row, 3)
            baudrate = _get_cell_value(ws_nodes, row, 4) or "19.2"

            node_info = NodeInfo(node_type=node_type, name=name, identifier=identifier, baudrate=baudrate)

            if node_type.lower() == "master":
                probed.master_node = node_info
            else:
                probed.slave_nodes.append(node_info)

    # Frame Catalog
    if "Frame Catalog" in sheet_names:
        ws_frames = wb["Frame Catalog"]
        for row in range(4, 100):
            frame_id = _get_cell_value(ws_frames, row, 1)
            if not frame_id:
                break
            name = _get_cell_value(ws_frames, row, 2)
            frame_type = _get_cell_value(ws_frames, row, 3) or "unconditional"
            length = _get_cell_value(ws_frames, row, 4) or 8
            period_ms = _get_cell_value(ws_frames, row, 5) or 100
            publisher = _get_cell_value(ws_frames, row, 6)

            frame_info = FrameInfo(
                frame_id=str(frame_id),
                name=name,
                frame_type=frame_type,
                length=int(length),
                period_ms=int(period_ms),
                publisher=publisher,
            )
            probed.frames.append(frame_info)

    # Signal Catalog
    if "Signal Catalog" in sheet_names:
        ws_signals = wb["Signal Catalog"]
        for row in range(4, 100):
            signal_id = _get_cell_value(ws_signals, row, 1)
            if not signal_id:
                break
            name = _get_cell_value(ws_signals, row, 2)
            frame = _get_cell_value(ws_signals, row, 3)
            signal_type = _get_cell_value(ws_signals, row, 4) or "physical"
            start_bit = _get_cell_value(ws_signals, row, 5) or 0
            length = _get_cell_value(ws_signals, row, 6) or 8
            min_val = _get_cell_value(ws_signals, row, 7) or 0
            max_val = _get_cell_value(ws_signals, row, 8) or 255

            signal_info = SignalInfo(
                signal_id=str(signal_id),
                name=name,
                frame=frame,
                start_bit=int(start_bit),
                length=int(length),
                signal_type=signal_type,
                min_val=float(min_val),
                max_val=float(max_val),
            )
            probed.signals.append(signal_info)

    # Schedule Tables
    if "Schedule Tables" in sheet_names:
        ws_sched = wb["Schedule Tables"]
        current_mode = None
        current_schedule = None

        for row in range(4, 200):
            col1 = _get_cell_value(ws_sched, row, 1)
            col2 = _get_cell_value(ws_sched, row, 2)

            if not col1 and not col2:
                if current_schedule:
                    probed.schedules.append(current_schedule)
                    current_schedule = None
                continue

            # Check if this is a mode header (e.g., "Mode: Heating")
            if col1 and isinstance(col1, str) and "Mode:" in col1:
                if current_schedule:
                    probed.schedules.append(current_schedule)
                current_mode = col1.replace("Mode:", "").strip()
                current_schedule = ScheduleTableInfo(name=f"Schedule_{len(probed.schedules)}", mode=current_mode)
            elif col1 and col2 and not isinstance(col1, str):
                # This is a data row (slot_ms, frame)
                if current_schedule is None:
                    current_schedule = ScheduleTableInfo(name=f"Schedule_{len(probed.schedules)}", mode="Default")

                try:
                    slot_ms = int(col1)
                    frame = str(col2)
                    current_schedule.frames.append(ScheduleEntry(frame=frame, slot_ms=slot_ms))
                except (ValueError, TypeError):
                    pass

        if current_schedule:
            probed.schedules.append(current_schedule)

    return probed


def _get_cell_value(ws, row_or_letter, col=None):
    """Get cell value by row/col number or by letter."""
    try:
        if col is not None:
            return ws.cell(row=row_or_letter, column=col).value
        else:
            return ws[row_or_letter].value
    except (KeyError, AttributeError, IndexError):
        return None
