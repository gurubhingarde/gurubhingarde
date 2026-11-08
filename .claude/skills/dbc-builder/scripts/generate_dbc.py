"""
DBC Builder — generates a multi-tab CAN database specification workbook from a JSON input.

Usage:
    python generate_dbc.py <input.json> <output.xlsx>

Input JSON schema (see examples/sample_input_can.json for a full example):
{
  "project": {name, doc_id, revision, date, author, approver, company},
  "network": {name, description, can_version},      // can_version: "2.0A"|"2.0B"|"FD"
  "ecus": [{id, name, manufacturer, software_version, description}],
  "messages": [
      {id_hex, name, dlc, cycle_time_ms, sender_ecu, frame_type, transmission_type, description}
      // frame_type: "Standard" (11-bit) or "Extended" (29-bit)
      // transmission_type: "cyclic", "event", "spontaneous"
  ],
  "signals": [
      {id, name, message_id_hex, bit_start, bit_length, byte_order, type, scale, offset, min, max, unit, receivers, multiplexor_id, is_multiplexor, description}
      // byte_order: "little_endian" or "big_endian"
      // type: "signed" or "unsigned"
      // receivers: ["ECU1", "ECU2"] or null
      // multiplexor_id: null or the ID of the multiplexing signal
      // is_multiplexor: true if this signal multiplexes others
  ],
  "value_tables": [
      {signal_id, values: [{value, description}]}
  ],
  "signal_groups": [
      {signal_id, multiplexor_signal_id, multiplexed_signals: [...]}
  ]
}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"

THIN = Side(border_style="thin", color="BFBFBF")
MEDIUM = Side(border_style="medium", color="404040")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def title_font(size: int = 16) -> Font:
    return Font(name=FONT_NAME, size=size, bold=True, color="FFFFFF")


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def style_title_row(ws, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = title_font(14)
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


def style_section_banner(ws, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=11, bold=True, color="1F3864")
    cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row].height = 22


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, project: dict, network: dict) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 2, 4, "CAN Database Specification (DBC)")
    style_title_row(ws, 3, 4, f"Network: {network.get('name', '')}")

    fields = [
        ("Project", project.get("name", "")),
        ("Document ID", project.get("doc_id", "")),
        ("Revision", project.get("revision", "")),
        ("Date", project.get("date", "")),
        ("Author", project.get("author", "")),
        ("Approver", project.get("approver", "")),
        ("Company", project.get("company", "")),
        ("Network Name", network.get("name", "")),
        ("CAN Version", network.get("can_version", "2.0B")),
        ("Standard", "ISO 11898-1 (CAN 2.0A/2.0B), AUTOSAR Communication"),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left")
        row += 1

    autosize(ws, {1: 4, 2: 22, 3: 60, 4: 4})


def build_doc_control(wb: Workbook) -> None:
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 5, "Document Control")

    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of change", "Approver"])
    placeholders = [
        ("0.1", "", "", "Initial draft generated by dbc-builder skill", ""),
        ("0.2", "", "", "Internal review comments incorporated", ""),
        ("1.0", "", "", "Released for implementation", ""),
    ]
    for i, row_data in enumerate(placeholders, start=4):
        for col, val in enumerate(row_data, start=1):
            ws.cell(row=i, column=col, value=val)
    stripe_body(ws, 4, 4 + len(placeholders) - 1, 5)

    # Distribution list
    style_title_row(ws, 10, 5, "Distribution List")
    style_header_row(ws, 11, ["Name", "Role", "Organization", "Email", "Notes"])
    for i in range(12, 16):
        for c in range(1, 6):
            ws.cell(row=i, column=c, value="")
    stripe_body(ws, 12, 15, 5)

    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_ecu_inventory(wb: Workbook, ecus: list[dict]) -> None:
    ws = wb.create_sheet("02_ECU_Inventory")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "ECU Inventory")

    style_header_row(ws, 3, ["ECU ID", "Name", "Manufacturer", "Software Version", "Description"])
    if not ecus:
        ecus = [
            {"id": "ECU01", "name": "Engine Control", "manufacturer": "Vendor A", "software_version": "1.0", "description": ""},
            {"id": "ECU02", "name": "Transmission Control", "manufacturer": "Vendor B", "software_version": "2.1", "description": ""},
        ]
    for i, e in enumerate(ecus, start=4):
        ws.cell(row=i, column=1, value=e.get("id", ""))
        ws.cell(row=i, column=2, value=e.get("name", ""))
        ws.cell(row=i, column=3, value=e.get("manufacturer", ""))
        ws.cell(row=i, column=4, value=e.get("software_version", ""))
        ws.cell(row=i, column=5, value=e.get("description", ""))
    stripe_body(ws, 4, 3 + len(ecus), 5)
    autosize(ws, {1: 10, 2: 22, 3: 20, 4: 18, 5: 40})


def build_message_catalog(wb: Workbook, messages: list[dict]) -> None:
    ws = wb.create_sheet("03_Message_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "Message Catalog")

    style_header_row(ws, 3, ["Message ID (Hex)", "Name", "DLC (bytes)", "Cycle Time (ms)", "Sender ECU", "Frame Type", "Transmission Type", "Signal Count", "Description"])
    for i, m in enumerate(messages, start=4):
        msg_id_hex = m.get("id_hex", "")
        ws.cell(row=i, column=1, value=msg_id_hex)
        ws.cell(row=i, column=2, value=m.get("name", ""))
        ws.cell(row=i, column=3, value=m.get("dlc", 8))
        ws.cell(row=i, column=4, value=m.get("cycle_time_ms", 0))
        ws.cell(row=i, column=5, value=m.get("sender_ecu", ""))
        ws.cell(row=i, column=6, value=m.get("frame_type", "Standard"))
        ws.cell(row=i, column=7, value=m.get("transmission_type", "cyclic"))
        ws.cell(row=i, column=8, value=m.get("signal_count", 0))
        ws.cell(row=i, column=9, value=m.get("description", ""))
    stripe_body(ws, 4, 3 + len(messages), 9)
    autosize(ws, {1: 14, 2: 26, 3: 12, 4: 16, 5: 18, 6: 14, 7: 16, 8: 12, 9: 40})


def build_signal_catalog(wb: Workbook, signals: list[dict]) -> None:
    ws = wb.create_sheet("04_Signal_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 13, "Signal Catalog")

    headers = ["Signal ID", "Name", "Bit Start", "Bit Length", "Byte Order", "Type", "Scale", "Offset", "Min", "Max", "Unit", "Receivers", "Multiplexor"]
    style_header_row(ws, 3, headers)
    for i, s in enumerate(signals, start=4):
        ws.cell(row=i, column=1, value=s.get("id", ""))
        ws.cell(row=i, column=2, value=s.get("name", ""))
        ws.cell(row=i, column=3, value=s.get("bit_start", 0))
        ws.cell(row=i, column=4, value=s.get("bit_length", 1))
        ws.cell(row=i, column=5, value=s.get("byte_order", "little_endian"))
        ws.cell(row=i, column=6, value=s.get("type", "unsigned"))
        ws.cell(row=i, column=7, value=s.get("scale", 1))
        ws.cell(row=i, column=8, value=s.get("offset", 0))
        ws.cell(row=i, column=9, value=s.get("min", ""))
        ws.cell(row=i, column=10, value=s.get("max", ""))
        ws.cell(row=i, column=11, value=s.get("unit", ""))
        receivers = s.get("receivers", [])
        ws.cell(row=i, column=12, value=", ".join(receivers) if receivers else "")
        ws.cell(row=i, column=13, value=s.get("multiplexor_id", ""))
    stripe_body(ws, 4, 3 + len(signals), len(headers))
    autosize(ws, {1: 10, 2: 20, 3: 10, 4: 10, 5: 14, 6: 10, 7: 8, 8: 10, 9: 8, 10: 8, 11: 12, 12: 26, 13: 14})


def build_signal_to_message_mapping(wb: Workbook, messages: list[dict], signals: list[dict]) -> None:
    ws = wb.create_sheet("05_Signal-to-Message_Mapping")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Signal-to-Message Mapping")

    style_header_row(ws, 3, ["Signal ID", "Signal Name", "Message ID (Hex)", "Message Name", "Bit Position (Start-End)", "Notes"])
    row = 4
    msg_lookup = {m.get("id_hex"): m for m in messages}
    for s in signals:
        msg_id = s.get("message_id_hex", "")
        msg = msg_lookup.get(msg_id, {})
        bit_start = s.get("bit_start", 0)
        bit_len = s.get("bit_length", 1)
        bit_end = bit_start + bit_len - 1

        ws.cell(row=row, column=1, value=s.get("id", ""))
        ws.cell(row=row, column=2, value=s.get("name", ""))
        ws.cell(row=row, column=3, value=msg_id)
        ws.cell(row=row, column=4, value=msg.get("name", ""))
        ws.cell(row=row, column=5, value=f"{bit_start}-{bit_end}")
        ws.cell(row=row, column=6, value=s.get("description", ""))
        row += 1
    stripe_body(ws, 4, row - 1, 6)
    autosize(ws, {1: 10, 2: 22, 3: 14, 4: 26, 5: 18, 6: 40})


def build_value_tables(wb: Workbook, value_tables: list[dict]) -> None:
    ws = wb.create_sheet("06_Value_Tables")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Value Tables (Enumerations)")

    row = 3
    for vt in value_tables:
        sig_id = vt.get("signal_id", "")
        style_section_banner(ws, row, 3, f"Signal: {sig_id}")
        row += 1

        style_header_row(ws, row, ["Value", "Description"])
        row += 1

        for val_entry in vt.get("values", []):
            ws.cell(row=row, column=1, value=val_entry.get("value", ""))
            ws.cell(row=row, column=2, value=val_entry.get("description", ""))
            row += 1

        row += 1

    autosize(ws, {1: 10, 2: 40, 3: 40})


def build_signal_group_definitions(wb: Workbook, signal_groups: list[dict]) -> None:
    ws = wb.create_sheet("07_Signal_Group_Definitions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Signal Group Definitions (Multiplexing)")

    style_header_row(ws, 3, ["Multiplexor Signal ID", "Multiplexor Value", "Multiplexed Signals", "Description"])
    row = 4
    for sg in signal_groups:
        ws.cell(row=row, column=1, value=sg.get("signal_id", ""))
        ws.cell(row=row, column=2, value=sg.get("multiplexor_signal_id", ""))
        multiplexed = sg.get("multiplexed_signals", [])
        ws.cell(row=row, column=3, value=", ".join(multiplexed) if multiplexed else "")
        ws.cell(row=row, column=4, value=sg.get("description", ""))
        row += 1
    stripe_body(ws, 4, row - 1, 4)
    autosize(ws, {1: 18, 2: 18, 3: 40, 4: 40})


def build_network_topology(wb: Workbook, ecus: list[dict], messages: list[dict]) -> None:
    ws = wb.create_sheet("08_Network_Topology")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Network Topology and Message Flow")

    style_header_row(ws, 3, ["Sender ECU", "Message ID (Hex)", "Message Name", "Receiver ECUs", "Cycle Time (ms)"])
    row = 4
    for m in messages:
        sender = m.get("sender_ecu", "")
        msg_id = m.get("id_hex", "")
        msg_name = m.get("name", "")
        cycle = m.get("cycle_time_ms", 0)

        # Collect receivers from signals in this message
        receiver_ecus = set()
        # In a real flow, we'd cross-reference signals, but here we simplify

        ws.cell(row=row, column=1, value=sender)
        ws.cell(row=row, column=2, value=msg_id)
        ws.cell(row=row, column=3, value=msg_name)
        ws.cell(row=row, column=4, value=", ".join(sorted(receiver_ecus)) if receiver_ecus else "(from signal receivers)")
        ws.cell(row=row, column=5, value=cycle)
        row += 1
    stripe_body(ws, 4, row - 1, 5)
    autosize(ws, {1: 18, 2: 14, 3: 26, 4: 26, 5: 16})


def build_validation_rules(wb: Workbook, messages: list[dict], signals: list[dict]) -> None:
    ws = wb.create_sheet("09_Validation_Rules")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Validation Rules and Consistency Checks")

    style_header_row(ws, 3, ["Check", "Status", "Details", "Recommendation"])
    checks = []

    # Check: No duplicate message IDs
    msg_ids = [m.get("id_hex") for m in messages]
    if len(msg_ids) == len(set(msg_ids)):
        checks.append(("Unique Message IDs", "PASS", f"All {len(msg_ids)} message IDs are unique.", ""))
    else:
        checks.append(("Unique Message IDs", "FAIL", "Duplicate message IDs detected.", "Resolve ID conflicts."))

    # Check: Signal bit overlap per message
    msg_lookup = {m.get("id_hex"): m for m in messages}
    for m in messages:
        msg_id = m.get("id_hex", "")
        dlc = m.get("dlc", 8)
        msg_signals = [s for s in signals if s.get("message_id_hex") == msg_id]

        bits_used = set()
        overlap = False
        for sig in msg_signals:
            bit_start = sig.get("bit_start", 0)
            bit_len = sig.get("bit_length", 1)
            sig_bits = set(range(bit_start, bit_start + bit_len))
            if sig_bits & bits_used:
                overlap = True
                break
            bits_used.update(sig_bits)

        if not overlap and max(bits_used) < dlc * 8:
            checks.append((f"Message {msg_id}: No bit overlap", "PASS", f"{len(msg_signals)} signals, {len(bits_used)} bits used.", ""))
        else:
            checks.append((f"Message {msg_id}: Bit validation", "FAIL" if overlap else "WARN", "Bit overlap or DLC insufficiency." if overlap else "Unused DLC capacity.", "Review signal allocation."))

    row = 4
    for check_name, status, details, rec in checks:
        ws.cell(row=row, column=1, value=check_name)
        ws.cell(row=row, column=2, value=status)
        status_cell = ws.cell(row=row, column=2)
        if status == "PASS":
            status_cell.fill = PatternFill("solid", fgColor=GREEN_OK)
        elif status == "FAIL":
            status_cell.fill = PatternFill("solid", fgColor=RED_BAD)
        else:
            status_cell.fill = PatternFill("solid", fgColor="FFF2CC")
        ws.cell(row=row, column=3, value=details)
        ws.cell(row=row, column=4, value=rec)
        row += 1
    stripe_body(ws, 4, row - 1, 4)
    autosize(ws, {1: 40, 2: 10, 3: 50, 4: 40})


def build_references(wb: Workbook) -> None:
    ws = wb.create_sheet("10_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References and Standards")

    refs = [
        ("ISO 11898-1:2015", "Road vehicles - Controller Area Network (CAN) - Part 1: Data link layer and physical signalling"),
        ("CAN 2.0A", "11-bit identifier (standard frame)"),
        ("CAN 2.0B", "29-bit identifier (extended frame)"),
        ("AUTOSAR CP", "AUTOSAR Classic Platform Communication module (Com, PduR, CanIf)"),
        ("J1939", "Heavy-duty vehicle CAN (29-bit IDs, PDU1/PDU2 structure)"),
        ("DBC Format", "Vector CANdb++ native format (used by DBC parsers and code generators)"),
    ]

    row = 3
    for standard, description in refs:
        ws.cell(row=row, column=1, value=standard).font = Font(name=FONT_NAME, bold=True, size=10)
        ws.cell(row=row, column=2, value=description).font = body_font()
        ws.cell(row=row, column=1).border = BORDER_ALL
        ws.cell(row=row, column=2).border = BORDER_ALL
        row += 1

    autosize(ws, {1: 22, 2: 90})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(input_path: str, output_path: str) -> dict:
    with open(input_path) as f:
        data = json.load(f)

    project = data.get("project", {})
    network = data.get("network", {})
    ecus = data.get("ecus", [])
    messages = data.get("messages", [])
    signals = data.get("signals", [])
    value_tables = data.get("value_tables", []) or []
    signal_groups = data.get("signal_groups", []) or []

    if not messages or not signals:
        raise ValueError("Input must include at least one message and one signal.")

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, project, network)
    build_doc_control(wb)
    build_ecu_inventory(wb, ecus)
    build_message_catalog(wb, messages)
    build_signal_catalog(wb, signals)
    build_signal_to_message_mapping(wb, messages, signals)
    build_value_tables(wb, value_tables)
    build_signal_group_definitions(wb, signal_groups)
    build_network_topology(wb, ecus, messages)
    build_validation_rules(wb, messages, signals)
    build_references(wb)

    wb.active = 0
    wb.save(output_path)

    return {
        "network": network.get("name", ""),
        "ecus": len(ecus),
        "messages": len(messages),
        "signals": len(signals),
        "value_tables": len(value_tables),
        "signal_groups": len(signal_groups),
        "output_path": output_path,
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_dbc.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
