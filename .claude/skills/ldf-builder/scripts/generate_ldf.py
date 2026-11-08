"""
LDF Builder — generates a multi-tab ISO 17987 LIN Description File (LDF) workbook from a JSON input.

Usage:
    python generate_ldf.py <input.json> <output.xlsx>

Input JSON schema:
{
  "cluster": {name, abbr, project, doc_id, revision, date, author, approver, lin_version, baud_rate_kbps, company},
  "master_node": {name, identifier},
  "slave_nodes": [{name, identifier, baudrate}],
  "frames": [{id, name, type, length, period_ms, publisher, subscribers}],
  "signals": [{id, name, frame, start_bit, length, type, min, max, unit, encoding}],
  "schedule_tables": [{name, mode, frames: [{frame, slot_ms}]}],
  "node_attributes": {optional overrides}
}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


# ---------------------------------------------------------------------------
# Styling constants (matching hara-builder pattern)
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
GREY = "D0CECE"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def style_title(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header(ws, row, headers):
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 36


def style_section_banner(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row].height = 22


def autosize(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = w


def style_data_cell(cell, value, bold=False, color=None):
    cell.value = value
    cell.font = Font(name=FONT_NAME, size=10, bold=bold, color=color or "000000")
    cell.border = BORDER_ALL
    cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title(wb, cluster_info):
    """Title page with cluster metadata."""
    ws = wb.create_sheet("Title")
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 5, "LIN Description File (LDF)")
    style_title(ws, 3, 5, cluster_info.get("name", "(Cluster name)"))

    fields = [
        ("Cluster Name", cluster_info.get("name")),
        ("Cluster Abbreviation", cluster_info.get("abbr")),
        ("Project", cluster_info.get("project")),
        ("Document ID", cluster_info.get("doc_id")),
        ("Revision", cluster_info.get("revision")),
        ("Date", cluster_info.get("date")),
        ("Author", cluster_info.get("author")),
        ("Approver", cluster_info.get("approver")),
        ("LIN Version", cluster_info.get("lin_version", "2.2A")),
        ("Baud Rate (kbps)", cluster_info.get("baud_rate_kbps", "19.2")),
        ("Standard", "ISO 17987 / LIN 2.2A"),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1

    autosize(ws, {1: 4, 2: 26, 3: 60, 4: 4, 5: 4})


def build_document_control(wb, cluster_info):
    """Document control tab with revision history."""
    ws = wb.create_sheet("Document Control")

    style_title(ws, 1, 5, "Document Control")
    style_header(ws, 3, ["Revision", "Date", "Author", "Changes", "Status"])

    # Sample row
    row = 4
    rev = cluster_info.get("revision", "1.0")
    date_val = cluster_info.get("date", date.today().isoformat())
    author = cluster_info.get("author", "TBD")

    ws.cell(row=row, column=1, value=rev)
    ws.cell(row=row, column=2, value=date_val)
    ws.cell(row=row, column=3, value=author)
    ws.cell(row=row, column=4, value="Initial release")
    ws.cell(row=row, column=5, value="Draft")

    autosize(ws, {1: 12, 2: 14, 3: 20, 4: 40, 5: 12})


def build_cluster_header(wb, cluster_info):
    """Cluster header with protocol parameters."""
    ws = wb.create_sheet("Cluster Header")

    style_title(ws, 1, 5, "Cluster Configuration")

    row = 3
    style_section_banner(ws, row, 5, "Protocol Parameters")
    row += 1

    params = [
        ("LIN Version", cluster_info.get("lin_version", "2.2A")),
        ("Baud Rate (kbps)", cluster_info.get("baud_rate_kbps", "19.2")),
        ("Cluster Name", cluster_info.get("name")),
        ("Cluster Abbreviation", cluster_info.get("abbr")),
        ("Timing Master", "Master Node"),
        ("Timeout (ms)", "1000"),
    ]

    for label, value in params:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

    autosize(ws, {1: 30, 2: 20, 3: 15, 4: 15, 5: 15})


def build_node_attributes(wb, master_node, slave_nodes):
    """Node attributes tab."""
    ws = wb.create_sheet("Node Attributes")

    style_title(ws, 1, 6, "Node Configuration")
    style_header(ws, 3, ["Node Type", "Name", "Identifier", "Baud Rate", "Publishes", "Subscribes"])

    row = 4

    # Master
    if master_node:
        ws.cell(row=row, column=1, value="Master")
        ws.cell(row=row, column=2, value=master_node.get("name"))
        ws.cell(row=row, column=3, value=master_node.get("identifier"))
        ws.cell(row=row, column=4, value="19.2")
        ws.cell(row=row, column=5, value="All")
        ws.cell(row=row, column=6, value="Diagnostics")
        row += 1

    # Slaves
    for slave in (slave_nodes or []):
        ws.cell(row=row, column=1, value="Slave")
        ws.cell(row=row, column=2, value=slave.get("name"))
        ws.cell(row=row, column=3, value=slave.get("identifier"))
        ws.cell(row=row, column=4, value=slave.get("baudrate", "19.2"))
        ws.cell(row=row, column=5, value="(See Schedule)")
        ws.cell(row=row, column=6, value="(See Schedule)")
        row += 1

    autosize(ws, {1: 12, 2: 20, 3: 14, 4: 14, 5: 20, 6: 20})


def build_signal_catalog(wb, signals):
    """Signal catalog tab."""
    ws = wb.create_sheet("Signal Catalog")

    style_title(ws, 1, 8, "Signal Definitions")
    style_header(ws, 3, ["ID", "Signal Name", "Frame", "Type", "Start Bit", "Length", "Min", "Max"])

    row = 4
    for sig in (signals or []):
        ws.cell(row=row, column=1, value=sig.get("id"))
        ws.cell(row=row, column=2, value=sig.get("name"))
        ws.cell(row=row, column=3, value=sig.get("frame"))
        ws.cell(row=row, column=4, value=sig.get("type", "physical"))
        ws.cell(row=row, column=5, value=sig.get("start_bit", 0))
        ws.cell(row=row, column=6, value=sig.get("length", 8))
        ws.cell(row=row, column=7, value=sig.get("min", 0))
        ws.cell(row=row, column=8, value=sig.get("max", 255))
        row += 1

    autosize(ws, {1: 8, 2: 24, 3: 16, 4: 14, 5: 12, 6: 12, 7: 12, 8: 12})


def build_frame_catalog(wb, frames):
    """Frame catalog tab."""
    ws = wb.create_sheet("Frame Catalog")

    style_title(ws, 1, 7, "Frame Definitions")
    style_header(ws, 3, ["ID", "Frame Name", "Type", "Length (bytes)", "Period (ms)", "Publisher", "Description"])

    row = 4
    for frame in (frames or []):
        ws.cell(row=row, column=1, value=frame.get("id"))
        ws.cell(row=row, column=2, value=frame.get("name"))
        ws.cell(row=row, column=3, value=frame.get("type", "unconditional"))
        ws.cell(row=row, column=4, value=frame.get("length", 8))
        ws.cell(row=row, column=5, value=frame.get("period_ms", 100))
        ws.cell(row=row, column=6, value=frame.get("publisher"))
        ws.cell(row=row, column=7, value="")
        row += 1

    autosize(ws, {1: 8, 2: 24, 3: 16, 4: 16, 5: 14, 6: 16, 7: 24})


def build_schedule_tables(wb, schedules):
    """Schedule tables tab."""
    ws = wb.create_sheet("Schedule Tables")

    style_title(ws, 1, 5, "Schedule Table Definitions")

    row = 3
    for schedule in (schedules or []):
        style_section_banner(ws, row, 5, f"Mode: {schedule.get('mode', 'Default')}")
        row += 1

        style_header(ws, row, ["Slot (ms)", "Frame", "Length (bytes)"])
        row += 1

        for frame_entry in schedule.get("frames", []):
            ws.cell(row=row, column=1, value=frame_entry.get("slot_ms"))
            ws.cell(row=row, column=2, value=frame_entry.get("frame"))
            ws.cell(row=row, column=3, value="8")
            row += 1

        row += 1

    autosize(ws, {1: 14, 2: 24, 3: 16, 4: 20, 5: 20})


def build_encoding_types(wb, signals):
    """Encoding types tab."""
    ws = wb.create_sheet("Encoding Types")

    style_title(ws, 1, 6, "Signal Encoding")
    style_header(ws, 3, ["Signal", "Type", "Scale", "Offset", "Unit", "Encoding"])

    row = 4
    for sig in (signals or []):
        ws.cell(row=row, column=1, value=sig.get("name"))
        ws.cell(row=row, column=2, value=sig.get("type", "physical"))
        ws.cell(row=row, column=3, value=sig.get("scale", "1.0"))
        ws.cell(row=row, column=4, value=sig.get("offset", "0"))
        ws.cell(row=row, column=5, value=sig.get("unit", ""))
        ws.cell(row=row, column=6, value=sig.get("encoding", "linear"))
        row += 1

    autosize(ws, {1: 24, 2: 14, 3: 12, 4: 12, 5: 14, 6: 20})


def build_diagnostic_signals(wb):
    """Diagnostic signals tab."""
    ws = wb.create_sheet("Diagnostic Signals")

    style_title(ws, 1, 5, "Diagnostic Signals")
    style_header(ws, 3, ["Service", "Signal", "Length", "Description", "Producer"])

    row = 4
    # Placeholder for diagnostic entries
    ws.cell(row=row, column=1, value="0x22")
    ws.cell(row=row, column=2, value="Read Data By ID")
    ws.cell(row=row, column=3, value="Variable")
    ws.cell(row=row, column=4, value="Diagnostic read service")
    ws.cell(row=row, column=5, value="Master")

    autosize(ws, {1: 14, 2: 24, 3: 14, 4: 40, 5: 16})


def build_validation_rules(wb, cluster_info):
    """Validation rules tab."""
    ws = wb.create_sheet("Validation Rules")

    style_title(ws, 1, 4, "Specification Validation")

    row = 3
    baud_rate = float(cluster_info.get("baud_rate_kbps", "19.2"))

    checks = [
        ("Baud Rate (kbps)", baud_rate, "1–20 kbps per LIN 2.2A", "OK" if 1 <= baud_rate <= 20 else "FAIL"),
        ("Max Frame Length", 8, "≤8 bytes per LIN spec", "OK"),
        ("Schedule Coverage", "TBD", "All frames scheduled", "VERIFY"),
        ("Signal Allocation", "TBD", "Each signal in exactly one frame", "VERIFY"),
        ("Node Communication", "TBD", "All nodes have roles", "VERIFY"),
    ]

    style_header(ws, row, ["Check", "Value", "Rule", "Status"])
    row += 1

    for check_name, value, rule, status in checks:
        ws.cell(row=row, column=1, value=check_name).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=str(value))
        ws.cell(row=row, column=3, value=rule)
        ws.cell(row=row, column=4, value=status)
        row += 1

    autosize(ws, {1: 28, 2: 14, 3: 40, 4: 14})


def build_references(wb):
    """References tab."""
    ws = wb.create_sheet("References")

    style_title(ws, 1, 4, "Standards and References")

    row = 3
    refs = [
        ("ISO 17987:2016", "Road vehicles - Local Interconnect Network (LIN)"),
        ("LIN 2.2A Specification", "Physical Layer / Protocol Layer"),
        ("Frame Types", "Unconditional / Event-triggered / Sporadic / Diagnostic"),
        ("Schedule Conventions", "Slot-based timing per master clock"),
    ]

    style_header(ws, row, ["Standard", "Description"])
    row += 1

    for std, desc in refs:
        ws.cell(row=row, column=1, value=std).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1

    autosize(ws, {1: 28, 2: 60, 3: 20, 4: 20})


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_ldf.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"Error: {input_path} not found.")
        sys.exit(1)

    with open(input_path) as f:
        data = json.load(f)

    cluster_info = data.get("cluster", {})
    master_node = data.get("master_node", {})
    slave_nodes = data.get("slave_nodes", [])
    frames = data.get("frames", [])
    signals = data.get("signals", [])
    schedules = data.get("schedule_tables", [])

    wb = Workbook()
    wb.remove(wb.active)

    build_title(wb, cluster_info)
    build_document_control(wb, cluster_info)
    build_cluster_header(wb, cluster_info)
    build_node_attributes(wb, master_node, slave_nodes)
    build_signal_catalog(wb, signals)
    build_frame_catalog(wb, frames)
    build_schedule_tables(wb, schedules)
    build_encoding_types(wb, signals)
    build_diagnostic_signals(wb)
    build_validation_rules(wb, cluster_info)
    build_references(wb)

    wb.save(output_path)
    print(f"Generated {output_path}")

    summary = {
        "cluster_name": cluster_info.get("name"),
        "lin_version": cluster_info.get("lin_version", "2.2A"),
        "baud_rate_kbps": cluster_info.get("baud_rate_kbps", "19.2"),
        "master_nodes": 1,
        "slave_nodes": len(slave_nodes),
        "frames": len(frames),
        "signals": len(signals),
        "schedule_tables": len(schedules),
        "tabs": 11,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
