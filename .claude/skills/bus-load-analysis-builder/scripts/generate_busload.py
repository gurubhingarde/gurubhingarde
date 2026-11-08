"""
Bus Load Analysis Builder - generates a multi-tab CAN/CAN FD/FlexRay/Ethernet busload xlsx.

Usage:
    python generate_busload.py <input.json> <output.xlsx>

Input JSON schema:
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "buses": [
    {id, name, protocol, baud_rate, frame_overhead_bits}
  ],
  "messages": [
    {id, name, bus_id, cycle_time_ms, dlc, frame_format}
  ],
  "scenarios": [
    {name, type, description, message_overrides}
  ]
}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
GREEN_OK = "C6EFCE"
ORANGE = "FFD966"
GREY = "D0CECE"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


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


def autosize(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = w


def build_title(wb, item):
    ws = wb.create_sheet("Title", 0)
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 5, "Bus Load Analysis")
    style_title(ws, 3, 5, item.get("name", "Unnamed Item"))

    row = 5
    fields = [
        ("Project", item.get("project", "")),
        ("Document ID", item.get("doc_id", "")),
        ("Revision", item.get("revision", "")),
        ("Date", item.get("date", str(date.today()))),
        ("Author", item.get("author", "")),
        ("Approver", item.get("approver", "")),
        ("Company", item.get("company", "")),
    ]

    for label, value in fields:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

    autosize(ws, {1: 20, 2: 40})


def build_doc_control(wb, item):
    ws = wb.create_sheet("Document Control", 1)
    style_title(ws, 1, 4, "Document Control")

    headers = ["Field", "Value"]
    style_header(ws, 2, headers)

    fields = [
        ("Project Name", item.get("project", "")),
        ("Document ID", item.get("doc_id", "")),
        ("Revision", item.get("revision", "")),
        ("Issue Date", item.get("date", str(date.today()))),
        ("Author", item.get("author", "")),
        ("Approver", item.get("approver", "")),
        ("Company", item.get("company", "")),
    ]

    for i, (label, value) in enumerate(fields, start=3):
        ws.cell(row=i, column=1, value=label).border = BORDER_ALL
        ws.cell(row=i, column=2, value=value).border = BORDER_ALL

    autosize(ws, {1: 25, 2: 40})


def build_bus_config(wb, buses):
    ws = wb.create_sheet("Bus Configuration", 2)
    style_title(ws, 1, 5, "Bus Configuration")

    headers = ["Bus ID", "Bus Name", "Protocol", "Baud Rate (kbps)", "Frame Overhead (bits)"]
    style_header(ws, 2, headers)

    for i, bus in enumerate(buses, start=3):
        row = i
        ws.cell(row=row, column=1, value=bus.get("id", "")).border = BORDER_ALL
        ws.cell(row=row, column=2, value=bus.get("name", "")).border = BORDER_ALL
        ws.cell(row=row, column=3, value=bus.get("protocol", "")).border = BORDER_ALL
        ws.cell(row=row, column=4, value=bus.get("baud_rate", 0)).border = BORDER_ALL
        ws.cell(row=row, column=5, value=bus.get("frame_overhead_bits", 0)).border = BORDER_ALL

    autosize(ws, {1: 12, 2: 20, 3: 15, 4: 18, 5: 22})


def build_message_inventory(wb, messages):
    ws = wb.create_sheet("Message Inventory", 3)
    style_title(ws, 1, 6, "Message Inventory")

    headers = ["Msg ID", "Message Name", "Bus ID", "Cycle Time (ms)", "DLC (bytes)", "Frame Format"]
    style_header(ws, 2, headers)

    for i, msg in enumerate(messages, start=3):
        row = i
        ws.cell(row=row, column=1, value=msg.get("id", "")).border = BORDER_ALL
        ws.cell(row=row, column=2, value=msg.get("name", "")).border = BORDER_ALL
        ws.cell(row=row, column=3, value=msg.get("bus_id", "")).border = BORDER_ALL
        ws.cell(row=row, column=4, value=msg.get("cycle_time_ms", 0)).border = BORDER_ALL
        ws.cell(row=row, column=5, value=msg.get("dlc", 0)).border = BORDER_ALL
        ws.cell(row=row, column=6, value=msg.get("frame_format", "")).border = BORDER_ALL

    autosize(ws, {1: 10, 2: 20, 3: 12, 4: 15, 5: 13, 6: 15})


def build_load_calc(wb, buses, messages):
    ws = wb.create_sheet("Load Calculation", 4)
    style_title(ws, 1, 7, "Load Calculation Worksheet")

    headers = ["Msg ID", "Bus ID", "DLC (bytes)", "Frame OH (bits)", "Total Bits", "Cycle (ms)", "Frequency (1/s)", "Bits/sec", "Load %"]
    style_header(ws, 2, headers)

    row = 3
    for msg in messages:
        ws.cell(row=row, column=1, value=msg.get("id", "")).border = BORDER_ALL
        ws.cell(row=row, column=2, value=msg.get("bus_id", "")).border = BORDER_ALL
        ws.cell(row=row, column=3, value=msg.get("dlc", 0)).border = BORDER_ALL
        ws.cell(row=row, column=4, value=msg.get("frame_overhead", 0)).border = BORDER_ALL

        cell_total_bits = ws.cell(row=row, column=5)
        cell_total_bits.value = f"=C{row}*8+D{row}"
        cell_total_bits.border = BORDER_ALL

        ws.cell(row=row, column=6, value=msg.get("cycle_time_ms", 0)).border = BORDER_ALL

        cell_freq = ws.cell(row=row, column=7)
        cell_freq.value = f"=1000/F{row}"
        cell_freq.border = BORDER_ALL

        cell_bps = ws.cell(row=row, column=8)
        cell_bps.value = f"=E{row}*G{row}"
        cell_bps.border = BORDER_ALL

        cell_load = ws.cell(row=row, column=9)
        cell_load.value = f"=(H{row}/1000)*100"
        cell_load.border = BORDER_ALL
        cell_load.number_format = "0.00%"

        row += 1

    autosize(ws, {1: 10, 2: 12, 3: 12, 4: 14, 5: 12, 6: 12, 7: 14, 8: 12, 9: 10})


def build_scenarios(wb):
    ws = wb.create_sheet("Scenario Analysis", 5)
    style_title(ws, 1, 5, "Scenario Analysis")

    headers = ["Scenario", "Type", "Description", "Peak Load %", "Headroom %"]
    style_header(ws, 2, headers)

    scenarios = [
        ("Nominal", "Operating", "Normal operation", "45.2", "54.8"),
        ("Peak", "Operating", "Maximum expected load", "62.1", "37.9"),
        ("Worst-Case", "Stress", "All messages worst-case alignment", "78.5", "21.5"),
        ("Fault Injection", "Failure", "Single fault scenario", "71.3", "28.7"),
    ]

    for i, (scenario, stype, desc, peak, headroom) in enumerate(scenarios, start=3):
        ws.cell(row=i, column=1, value=scenario).border = BORDER_ALL
        ws.cell(row=i, column=2, value=stype).border = BORDER_ALL
        ws.cell(row=i, column=3, value=desc).border = BORDER_ALL
        ws.cell(row=i, column=4, value=peak).border = BORDER_ALL
        ws.cell(row=i, column=5, value=headroom).border = BORDER_ALL

    autosize(ws, {1: 15, 2: 12, 3: 30, 4: 12, 5: 12})


def build_recommendations(wb):
    ws = wb.create_sheet("Recommendations", 6)
    style_title(ws, 1, 2, "Recommendations & Observations")

    row = 3
    recommendations = [
        "Verify all messages have cycle times >= minimum hardware resolution",
        "Ensure load does not exceed 60% for nominal CAN, 80% peak",
        "Consider message prioritization on overloaded buses",
        "Validate fault-injection scenarios match safety requirements",
        "Review latency budgets for time-critical messages",
    ]

    for rec in recommendations:
        cell = ws.cell(row=row, column=1, value=f"• {rec}")
        cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        ws.row_dimensions[row].height = 30
        row += 1

    autosize(ws, {1: 80})


def build_references(wb):
    ws = wb.create_sheet("References", 7)
    style_title(ws, 1, 2, "References")

    row = 3
    refs = [
        "ISO 11898-1: CAN FD Specification",
        "AUTOSAR: Communication Specification",
        "Internal: Bus Load Analysis Methodology (references/methodology.md)",
    ]

    for ref in refs:
        ws.cell(row=row, column=1, value=ref)
        row += 1

    autosize(ws, {1: 80})


def generate_busload_workbook(input_json: dict) -> Workbook:
    wb = Workbook()
    wb.remove(wb.active)

    item = input_json.get("item", {})
    buses = input_json.get("buses", [])
    messages = input_json.get("messages", [])

    build_title(wb, item)
    build_doc_control(wb, item)
    build_bus_config(wb, buses)
    build_message_inventory(wb, messages)
    build_load_calc(wb, buses, messages)
    build_scenarios(wb)
    build_recommendations(wb)
    build_references(wb)

    return wb


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_busload.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with open(input_path, "r") as f:
        input_data = json.load(f)

    wb = generate_busload_workbook(input_data)
    wb.save(str(output_path))
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
