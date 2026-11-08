"""DBC Specification prober — extracts structure from xlsx for checklist verification."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from openpyxl import load_workbook


@dataclass
class ECU:
    id: str = ""
    name: str = ""
    manufacturer: str = ""
    software_version: str = ""


@dataclass
class Message:
    id_hex: str = ""
    name: str = ""
    dlc: int = 8
    cycle_time_ms: int = 0
    sender_ecu: str = ""
    frame_type: str = "Standard"
    transmission_type: str = "cyclic"
    signal_count: int = 0


@dataclass
class Signal:
    id: str = ""
    name: str = ""
    message_id_hex: str = ""
    bit_start: int = 0
    bit_length: int = 1
    byte_order: str = "little_endian"
    type_signed: str = "unsigned"
    scale: float = 1.0
    offset: float = 0.0
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    unit: str = ""
    receivers: list[str] = field(default_factory=list)
    multiplexor_id: Optional[str] = None
    is_multiplexor: bool = False


@dataclass
class ProbedDBC:
    path: str = ""
    project: str = ""
    doc_id: str = ""
    revision: str = ""
    status: str = ""
    title: str = ""
    sheet_names: list[str] = field(default_factory=list)
    n_messages: int = 0
    n_signals: int = 0
    n_ecus: int = 0
    ecus: list[ECU] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)
    signals: list[Signal] = field(default_factory=list)
    messages_by_id: dict[str, Message] = field(default_factory=dict)
    signals_by_message: dict[str, list[Signal]] = field(default_factory=dict)
    value_tables: dict[str, dict] = field(default_factory=dict)
    has_table_of_contents: bool = False
    author: str = ""
    approver: str = ""
    network_name: str = ""


def probe(xlsx_path: str) -> ProbedDBC:
    """Open and extract DBC structure from xlsx."""
    p = ProbedDBC(path=xlsx_path)

    try:
        wb = load_workbook(xlsx_path, data_only=True)
    except Exception as e:
        p.title = f"(Error opening workbook: {e})"
        return p

    p.sheet_names = wb.sheetnames
    p.has_table_of_contents = "General Info" in p.sheet_names or "TOC" in p.sheet_names

    # Extract Title page
    title_ws = None
    for sn in ["00_Title_Page", "Title", "Title Page"]:
        if sn in wb.sheetnames:
            title_ws = wb[sn]
            break

    if title_ws:
        # Row 3 typically has title
        for r in range(1, 20):
            cell_val = title_ws.cell(row=r, column=1).value
            if cell_val and isinstance(cell_val, str):
                if "CAN" in cell_val.upper() or "DBC" in cell_val.upper():
                    p.title = str(cell_val)
                    break

        # Extract metadata fields
        for r in range(1, 25):
            label_cell = title_ws.cell(row=r, column=2)
            value_cell = title_ws.cell(row=r, column=3)
            label = str(label_cell.value or "").strip().lower()
            value = str(value_cell.value or "").strip()

            if "project" in label and not p.project:
                p.project = value
            elif "doc" in label and "id" in label:
                p.doc_id = value
            elif "revision" in label:
                p.revision = value
            elif "status" in label:
                p.status = value
            elif "author" in label:
                p.author = value
            elif "approver" in label:
                p.approver = value
            elif "network" in label and "name" in label:
                p.network_name = value

    # Extract ECU Inventory
    ecu_ws = None
    for sn in ["02_ECU_Inventory", "ECU Inventory", "ECUs"]:
        if sn in wb.sheetnames:
            ecu_ws = wb[sn]
            break

    if ecu_ws:
        for r in range(4, 50):
            ecu_id = ecu_ws.cell(row=r, column=1).value
            if not ecu_id or str(ecu_id).strip() == "":
                break
            ecu = ECU(
                id=str(ecu_id).strip(),
                name=str(ecu_ws.cell(row=r, column=2).value or "").strip(),
                manufacturer=str(ecu_ws.cell(row=r, column=3).value or "").strip(),
                software_version=str(ecu_ws.cell(row=r, column=4).value or "").strip(),
            )
            p.ecus.append(ecu)

    p.n_ecus = len(p.ecus)

    # Extract Message Catalog
    msg_ws = None
    for sn in ["03_Message_Catalog", "Message Catalog", "Messages"]:
        if sn in wb.sheetnames:
            msg_ws = wb[sn]
            break

    if msg_ws:
        for r in range(4, 200):
            msg_id = msg_ws.cell(row=r, column=1).value
            if not msg_id or str(msg_id).strip() == "":
                break
            msg = Message(
                id_hex=str(msg_id).strip().upper(),
                name=str(msg_ws.cell(row=r, column=2).value or "").strip(),
                dlc=int(msg_ws.cell(row=r, column=3).value or 8),
                cycle_time_ms=int(msg_ws.cell(row=r, column=4).value or 0),
                sender_ecu=str(msg_ws.cell(row=r, column=5).value or "").strip(),
                frame_type=str(msg_ws.cell(row=r, column=6).value or "Standard").strip(),
                transmission_type=str(msg_ws.cell(row=r, column=7).value or "cyclic").strip(),
                signal_count=int(msg_ws.cell(row=r, column=8).value or 0),
            )
            p.messages.append(msg)
            p.messages_by_id[msg.id_hex] = msg

    p.n_messages = len(p.messages)

    # Extract Signal Catalog
    sig_ws = None
    for sn in ["04_Signal_Catalog", "Signal Catalog", "Signals"]:
        if sn in wb.sheetnames:
            sig_ws = wb[sn]
            break

    if sig_ws:
        for r in range(4, 500):
            sig_id = sig_ws.cell(row=r, column=1).value
            if not sig_id or str(sig_id).strip() == "":
                break

            receivers_str = str(sig_ws.cell(row=r, column=12).value or "").strip()
            receivers = [x.strip() for x in receivers_str.split(",") if x.strip()]

            sig = Signal(
                id=str(sig_id).strip(),
                name=str(sig_ws.cell(row=r, column=2).value or "").strip(),
                message_id_hex=str(sig_ws.cell(row=r, column=3).value or "").strip().upper(),
                bit_start=int(sig_ws.cell(row=r, column=3).value or 0),
                bit_length=int(sig_ws.cell(row=r, column=4).value or 1),
                byte_order=str(sig_ws.cell(row=r, column=5).value or "little_endian").strip(),
                type_signed=str(sig_ws.cell(row=r, column=6).value or "unsigned").strip(),
                scale=float(sig_ws.cell(row=r, column=7).value or 1.0),
                offset=float(sig_ws.cell(row=r, column=8).value or 0.0),
                min_val=_to_float(sig_ws.cell(row=r, column=9).value),
                max_val=_to_float(sig_ws.cell(row=r, column=10).value),
                unit=str(sig_ws.cell(row=r, column=11).value or "").strip(),
                receivers=receivers,
                multiplexor_id=_to_str_or_none(sig_ws.cell(row=r, column=13).value),
                is_multiplexor=str(sig_ws.cell(row=r, column=14).value or "").lower() == "true",
            )
            p.signals.append(sig)

            # Index by message
            if sig.message_id_hex not in p.signals_by_message:
                p.signals_by_message[sig.message_id_hex] = []
            p.signals_by_message[sig.message_id_hex].append(sig)

    p.n_signals = len(p.signals)

    # Extract Value Tables
    vt_ws = None
    for sn in ["06_Value_Tables", "Value Tables", "Enumerations"]:
        if sn in wb.sheetnames:
            vt_ws = wb[sn]
            break

    if vt_ws:
        current_signal = None
        values_dict = {}
        for r in range(3, 100):
            cell1 = vt_ws.cell(row=r, column=1).value
            cell2 = vt_ws.cell(row=r, column=2).value

            if cell1 and "Signal" in str(cell1):
                # New signal section
                current_signal = str(cell1).replace("Signal:", "").strip()
                values_dict[current_signal] = {}
            elif current_signal and cell1 is not None and cell2 is not None:
                # Value entry
                try:
                    val = int(cell1)
                    desc = str(cell2)
                    values_dict[current_signal][val] = desc
                except (ValueError, TypeError):
                    pass

        p.value_tables = values_dict

    return p


def _to_float(val) -> Optional[float]:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _to_str_or_none(val) -> Optional[str]:
    if val is None or val == "":
        return None
    s = str(val).strip()
    return s if s else None
