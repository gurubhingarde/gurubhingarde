"""
ARXML System Builder — generates a multi-tab AUTOSAR ARXML system specification workbook from JSON.

Usage:
    python generate_arxml_system.py <input.json> <output.xlsx>

Input JSON schema (see examples/sample_input.json for a full example):
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "scope_description": str,
  "system_diagram_notes": str,
  "ecu_instances": [{id, name, stack: [CAN|LIN|FlexRay|Ethernet], hw_variant}],
  "system_mappings": [{signal_id, source_ecu, target_ecus: [ecu_id, ...], pdu_id, frame_id}],
  "signal_catalog": [{id, name, length_bits, byte_order, data_type, physical_unit, scaling}],
  "pdu_catalog": [{id, name, length_bytes, trigger, signals: [signal_id, ...]}],
  "frame_catalog": [{id, name, frame_id, protocol: CAN|LIN, dlc, pdus: [pdu_id, ...]}],
  "port_interfaces": [{id, name, interface_type: SR|CS|MS, sender_receiver: [{id, name, type}], ...}],
  "composition": [{swc_id, port_id, interface_id, direction: provide|require}]
}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


# =========================================================================
# Styling Constants
# =========================================================================

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def title_font(size: int = 16) -> Font:
    return Font(name=FONT_NAME, size=size, bold=True, color="FFFFFF")


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def style_title(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = title_font()
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header(ws, row, headers):
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = header_font()
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 36


def autosize(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = w


# =========================================================================
# Sheet Builders
# =========================================================================

def build_title(wb, item_dict):
    ws = wb.create_sheet("Title", 0)
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 6, "AUTOSAR ARXML System Specification")
    style_title(ws, 3, 6, item_dict.get("name", "System Name"))

    fields = [
        ("Project", item_dict.get("project", "")),
        ("System Document ID", item_dict.get("doc_id", "")),
        ("System Abbreviation", item_dict.get("abbr", "")),
        ("Revision", item_dict.get("revision", "")),
        ("Date", item_dict.get("date", "")),
        ("Author", item_dict.get("author", "")),
        ("Approver", item_dict.get("approver", "")),
        ("Company", item_dict.get("company", "")),
        ("AUTOSAR Standard", "AUTOSAR Classic Platform R22-11+"),
        ("Workbook Generated", datetime.now().isoformat()),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True)
        ws.cell(row=row, column=3, value=value).font = body_font()
        row += 1

    autosize(ws, {1: 4, 2: 28, 3: 50, 4: 4, 5: 4, 6: 4})


def build_document_control(wb, item_dict):
    ws = wb.create_sheet("Document Control")
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 6, "Document Control")
    style_header(ws, 4, ["Revision", "Date", "Author", "Change Description", "Status"])

    row = 5
    ws.cell(row=row, column=1, value=item_dict.get("revision", "1.0")).font = body_font()
    ws.cell(row=row, column=2, value=item_dict.get("date", "")).font = body_font()
    ws.cell(row=row, column=3, value=item_dict.get("author", "")).font = body_font()
    ws.cell(row=row, column=4, value="Initial release").font = body_font()
    ws.cell(row=row, column=5, value="Released").font = body_font()
    for col in range(1, 6):
        ws.cell(row=row, column=col).border = BORDER_ALL

    autosize(ws, {1: 14, 2: 14, 3: 18, 4: 35, 5: 14})


def build_system_header(wb, data_dict):
    ws = wb.create_sheet("System Header")
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 6, "System Context and Scope")

    row = 4
    ws.cell(row=row, column=1, value="Scope Description").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row=row, column=2, value=data_dict.get("scope_description", "")).font = body_font()
    ws.cell(row=row, column=2).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[row].height = 40

    row += 2
    ws.cell(row=row, column=1, value="System Diagram Notes").font = Font(name=FONT_NAME, bold=True)
    ws.cell(row=row, column=2, value=data_dict.get("system_diagram_notes", "")).font = body_font()
    ws.cell(row=row, column=2).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[row].height = 40

    autosize(ws, {1: 24, 2: 80})


def build_ecu_instances(wb, ecu_list):
    ws = wb.create_sheet("ECU Instances")

    style_header(ws, 1, ["ECU ID", "ECU Name", "Comm Stack", "HW Variant", "Description"])

    for i, ecu in enumerate(ecu_list or [], start=2):
        ws.cell(row=i, column=1, value=ecu.get("id", "")).font = body_font()
        ws.cell(row=i, column=2, value=ecu.get("name", "")).font = body_font()
        ws.cell(row=i, column=3, value=", ".join(ecu.get("stack", []))).font = body_font()
        ws.cell(row=i, column=4, value=ecu.get("hw_variant", "")).font = body_font()
        ws.cell(row=i, column=5, value=ecu.get("description", "")).font = body_font()
        for col in range(1, 6):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 12, 2: 18, 3: 18, 4: 16, 5: 35})


def build_system_mappings(wb, mappings_list):
    ws = wb.create_sheet("System Mappings")

    style_header(ws, 1, ["Signal ID", "Source ECU", "Target ECUs", "PDU ID", "Frame ID", "Protocol"])

    for i, mapping in enumerate(mappings_list or [], start=2):
        ws.cell(row=i, column=1, value=mapping.get("signal_id", "")).font = body_font()
        ws.cell(row=i, column=2, value=mapping.get("source_ecu", "")).font = body_font()
        ws.cell(row=i, column=3, value=", ".join(mapping.get("target_ecus", []))).font = body_font()
        ws.cell(row=i, column=4, value=mapping.get("pdu_id", "")).font = body_font()
        ws.cell(row=i, column=5, value=mapping.get("frame_id", "")).font = body_font()
        ws.cell(row=i, column=6, value=mapping.get("protocol", "")).font = body_font()
        for col in range(1, 7):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 12, 2: 14, 3: 24, 4: 12, 5: 12, 6: 12})


def build_communication_connectors(wb, data_dict):
    ws = wb.create_sheet("Communication Connectors")

    style_header(ws, 1, ["Network ID", "Network Name", "Protocol", "Baudrate", "Physical Medium"])

    connectors = data_dict.get("connectors", [])
    for i, conn in enumerate(connectors or [], start=2):
        ws.cell(row=i, column=1, value=conn.get("id", "")).font = body_font()
        ws.cell(row=i, column=2, value=conn.get("name", "")).font = body_font()
        ws.cell(row=i, column=3, value=conn.get("protocol", "")).font = body_font()
        ws.cell(row=i, column=4, value=conn.get("baudrate", "")).font = body_font()
        ws.cell(row=i, column=5, value=conn.get("medium", "")).font = body_font()
        for col in range(1, 6):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 12, 2: 18, 3: 12, 4: 14, 5: 20})


def build_signal_catalog(wb, signal_list):
    ws = wb.create_sheet("Signal Catalog")

    style_header(ws, 1, ["Signal ID", "Signal Name", "Length (bits)", "Byte Order", "Data Type", "Unit", "Scaling"])

    for i, sig in enumerate(signal_list or [], start=2):
        ws.cell(row=i, column=1, value=sig.get("id", "")).font = body_font()
        ws.cell(row=i, column=2, value=sig.get("name", "")).font = body_font()
        ws.cell(row=i, column=3, value=sig.get("length_bits", "")).font = body_font()
        ws.cell(row=i, column=4, value=sig.get("byte_order", "")).font = body_font()
        ws.cell(row=i, column=5, value=sig.get("data_type", "")).font = body_font()
        ws.cell(row=i, column=6, value=sig.get("physical_unit", "")).font = body_font()
        ws.cell(row=i, column=7, value=sig.get("scaling", "")).font = body_font()
        for col in range(1, 8):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 12, 2: 18, 3: 14, 4: 12, 5: 14, 6: 12, 7: 14})


def build_pdu_catalog(wb, pdu_list):
    ws = wb.create_sheet("PDU Catalog")

    style_header(ws, 1, ["PDU ID", "PDU Name", "Length (bytes)", "Trigger Type", "Signals"])

    for i, pdu in enumerate(pdu_list or [], start=2):
        ws.cell(row=i, column=1, value=pdu.get("id", "")).font = body_font()
        ws.cell(row=i, column=2, value=pdu.get("name", "")).font = body_font()
        ws.cell(row=i, column=3, value=pdu.get("length_bytes", "")).font = body_font()
        ws.cell(row=i, column=4, value=pdu.get("trigger", "")).font = body_font()
        ws.cell(row=i, column=5, value=", ".join(pdu.get("signals", []))).font = body_font()
        for col in range(1, 6):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 12, 2: 18, 3: 16, 4: 16, 5: 35})


def build_frame_catalog(wb, frame_list):
    ws = wb.create_sheet("Frame Catalog")

    style_header(ws, 1, ["Frame ID", "Frame Name", "CAN ID", "Protocol", "DLC", "PDUs"])

    for i, frame in enumerate(frame_list or [], start=2):
        ws.cell(row=i, column=1, value=frame.get("id", "")).font = body_font()
        ws.cell(row=i, column=2, value=frame.get("name", "")).font = body_font()
        ws.cell(row=i, column=3, value=frame.get("can_id", "")).font = body_font()
        ws.cell(row=i, column=4, value=frame.get("protocol", "")).font = body_font()
        ws.cell(row=i, column=5, value=frame.get("dlc", "")).font = body_font()
        ws.cell(row=i, column=6, value=", ".join(frame.get("pdus", []))).font = body_font()
        for col in range(1, 7):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 12, 2: 18, 3: 12, 4: 12, 5: 8, 6: 35})


def build_port_interfaces(wb, port_list):
    ws = wb.create_sheet("Port Interfaces")

    style_header(ws, 1, ["Port ID", "Port Name", "Interface Type", "Sender/Receiver Elements", "Direction"])

    for i, port in enumerate(port_list or [], start=2):
        ws.cell(row=i, column=1, value=port.get("id", "")).font = body_font()
        ws.cell(row=i, column=2, value=port.get("name", "")).font = body_font()
        ws.cell(row=i, column=3, value=port.get("interface_type", "")).font = body_font()
        elements = port.get("elements", [])
        elem_str = "; ".join([f"{e.get('name')} ({e.get('type')})" for e in elements])
        ws.cell(row=i, column=4, value=elem_str).font = body_font()
        ws.cell(row=i, column=5, value=port.get("direction", "")).font = body_font()
        for col in range(1, 6):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 12, 2: 18, 3: 16, 4: 40, 5: 12})


def build_composition(wb, comp_list):
    ws = wb.create_sheet("Composition SWC References")

    style_header(ws, 1, ["SWC ID", "Port ID", "Interface ID", "Direction", "Binding Status"])

    for i, comp in enumerate(comp_list or [], start=2):
        ws.cell(row=i, column=1, value=comp.get("swc_id", "")).font = body_font()
        ws.cell(row=i, column=2, value=comp.get("port_id", "")).font = body_font()
        ws.cell(row=i, column=3, value=comp.get("interface_id", "")).font = body_font()
        ws.cell(row=i, column=4, value=comp.get("direction", "")).font = body_font()
        ws.cell(row=i, column=5, value=comp.get("binding_status", "bound")).font = body_font()
        for col in range(1, 6):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 12, 2: 12, 3: 14, 4: 12, 5: 16})


def build_triggers_events(wb, triggers_list):
    ws = wb.create_sheet("Trigger and Event Mappings")

    style_header(ws, 1, ["Trigger ID", "Event Type", "Source Port", "Target Port", "Timing (ms)"])

    for i, trigger in enumerate(triggers_list or [], start=2):
        ws.cell(row=i, column=1, value=trigger.get("id", "")).font = body_font()
        ws.cell(row=i, column=2, value=trigger.get("event_type", "")).font = body_font()
        ws.cell(row=i, column=3, value=trigger.get("source_port", "")).font = body_font()
        ws.cell(row=i, column=4, value=trigger.get("target_port", "")).font = body_font()
        ws.cell(row=i, column=5, value=trigger.get("timing_ms", "")).font = body_font()
        for col in range(1, 6):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 12, 2: 16, 3: 18, 4: 18, 5: 14})


def build_references(wb):
    ws = wb.create_sheet("References")
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 4, "References and Methodology")

    row = 4
    refs = [
        ("AUTOSAR", "Classic Platform R22-11+ Specification", "www.autosar.org"),
        ("ISO 26262", "Functional Safety", "ISO 26262-3, 26262-4"),
        ("DBC/FIBEX", "Communication Database Standards", "CAN: .dbc; AUTOSAR: .fibex"),
    ]

    for label, desc, url in refs:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=desc).font = body_font()
        ws.cell(row=row, column=3, value=url).font = body_font()
        row += 1

    autosize(ws, {1: 18, 2: 35, 3: 30})


# =========================================================================
# Main
# =========================================================================

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_arxml_system.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: Input file {input_file} not found.")
        sys.exit(1)

    with open(input_file) as f:
        data = json.load(f)

    wb = Workbook()
    if wb.sheetnames and wb.sheetnames[0] == "Sheet":
        wb.remove(wb.active)

    item_dict = data.get("item", {})
    build_title(wb, item_dict)
    build_document_control(wb, item_dict)
    build_system_header(wb, data)
    build_ecu_instances(wb, data.get("ecu_instances", []))
    build_system_mappings(wb, data.get("system_mappings", []))
    build_communication_connectors(wb, data)
    build_signal_catalog(wb, data.get("signal_catalog", []))
    build_pdu_catalog(wb, data.get("pdu_catalog", []))
    build_frame_catalog(wb, data.get("frame_catalog", []))
    build_port_interfaces(wb, data.get("port_interfaces", []))
    build_composition(wb, data.get("composition", []))
    build_triggers_events(wb, data.get("triggers_events", []))
    build_references(wb)

    wb.save(output_file)
    print(f"ARXML system workbook generated: {output_file}")


if __name__ == "__main__":
    main()
