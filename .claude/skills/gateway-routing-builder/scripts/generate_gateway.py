"""
Gateway Routing Builder - generates a multi-tab gateway routing xlsx.

Usage:
    python generate_gateway.py <input.json> <output.xlsx>

Input JSON schema:
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "gateway": {id, name, ecu_type, hw_platform},
  "source_buses": [{id, name, protocol, description}],
  "dest_buses": [{id, name, protocol, description}],
  "routes": [
    {route_id, source_bus, dest_bus, signal_ids, transformation, latency_ms}
  ],
  "firewall_rules": [
    {rule_id, source_bus, dest_bus, allowed, description}
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
    style_title(ws, 2, 5, "Gateway Routing Specification")
    style_title(ws, 3, 5, item.get("name", "Unnamed Gateway"))

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


def build_gateway_ecu(wb, gateway):
    ws = wb.create_sheet("Gateway ECU Definition", 2)
    style_title(ws, 1, 4, "Gateway ECU Definition")

    headers = ["Parameter", "Value"]
    style_header(ws, 2, headers)

    fields = [
        ("ECU ID", gateway.get("id", "")),
        ("ECU Name", gateway.get("name", "")),
        ("ECU Type", gateway.get("ecu_type", "")),
        ("Hardware Platform", gateway.get("hw_platform", "")),
        ("Role", "Central Gateway"),
    ]

    for i, (label, value) in enumerate(fields, start=3):
        ws.cell(row=i, column=1, value=label).border = BORDER_ALL
        ws.cell(row=i, column=2, value=value).border = BORDER_ALL

    autosize(ws, {1: 25, 2: 40})


def build_source_buses(wb, buses):
    ws = wb.create_sheet("Source Bus Inventory", 3)
    style_title(ws, 1, 4, "Source Bus Inventory")

    headers = ["Bus ID", "Bus Name", "Protocol", "Description"]
    style_header(ws, 2, headers)

    for i, bus in enumerate(buses, start=3):
        ws.cell(row=i, column=1, value=bus.get("id", "")).border = BORDER_ALL
        ws.cell(row=i, column=2, value=bus.get("name", "")).border = BORDER_ALL
        ws.cell(row=i, column=3, value=bus.get("protocol", "")).border = BORDER_ALL
        ws.cell(row=i, column=4, value=bus.get("description", "")).border = BORDER_ALL

    autosize(ws, {1: 12, 2: 20, 3: 15, 4: 40})


def build_dest_buses(wb, buses):
    ws = wb.create_sheet("Destination Bus Inventory", 4)
    style_title(ws, 1, 4, "Destination Bus Inventory")

    headers = ["Bus ID", "Bus Name", "Protocol", "Description"]
    style_header(ws, 2, headers)

    for i, bus in enumerate(buses, start=3):
        ws.cell(row=i, column=1, value=bus.get("id", "")).border = BORDER_ALL
        ws.cell(row=i, column=2, value=bus.get("name", "")).border = BORDER_ALL
        ws.cell(row=i, column=3, value=bus.get("protocol", "")).border = BORDER_ALL
        ws.cell(row=i, column=4, value=bus.get("description", "")).border = BORDER_ALL

    autosize(ws, {1: 12, 2: 20, 3: 15, 4: 40})


def build_routing_table(wb, routes):
    ws = wb.create_sheet("Routing Table", 5)
    style_title(ws, 1, 7, "Routing Table")

    headers = ["Route ID", "Source Bus", "Dest Bus", "Signal/PDU IDs", "Transformation", "Latency (ms)", "Status"]
    style_header(ws, 2, headers)

    for i, route in enumerate(routes, start=3):
        ws.cell(row=i, column=1, value=route.get("route_id", "")).border = BORDER_ALL
        ws.cell(row=i, column=2, value=route.get("source_bus", "")).border = BORDER_ALL
        ws.cell(row=i, column=3, value=route.get("dest_bus", "")).border = BORDER_ALL
        ws.cell(row=i, column=4, value=route.get("signal_ids", "")).border = BORDER_ALL
        ws.cell(row=i, column=5, value=route.get("transformation", "None")).border = BORDER_ALL
        ws.cell(row=i, column=6, value=route.get("latency_ms", 0)).border = BORDER_ALL
        ws.cell(row=i, column=7, value="Active").border = BORDER_ALL

    autosize(ws, {1: 10, 2: 15, 3: 15, 4: 25, 5: 20, 6: 12, 7: 10})


def build_latency_budget(wb, routes):
    ws = wb.create_sheet("Latency Budget", 6)
    style_title(ws, 1, 5, "Latency Budget per Route")

    headers = ["Route ID", "Source", "Destination", "Max Latency (ms)", "Allocated (ms)"]
    style_header(ws, 2, headers)

    for i, route in enumerate(routes, start=3):
        ws.cell(row=i, column=1, value=route.get("route_id", "")).border = BORDER_ALL
        ws.cell(row=i, column=2, value=route.get("source_bus", "")).border = BORDER_ALL
        ws.cell(row=i, column=3, value=route.get("dest_bus", "")).border = BORDER_ALL
        ws.cell(row=i, column=4, value="100").border = BORDER_ALL
        ws.cell(row=i, column=5, value=route.get("latency_ms", 0)).border = BORDER_ALL

    autosize(ws, {1: 10, 2: 15, 3: 15, 4: 16, 5: 16})


def build_security_rules(wb, rules):
    ws = wb.create_sheet("Security/Firewall Rules", 7)
    style_title(ws, 1, 5, "Security and Firewall Rules")

    headers = ["Rule ID", "Source Bus", "Dest Bus", "Allowed", "Description"]
    style_header(ws, 2, headers)

    for i, rule in enumerate(rules, start=3):
        ws.cell(row=i, column=1, value=rule.get("rule_id", "")).border = BORDER_ALL
        ws.cell(row=i, column=2, value=rule.get("source_bus", "")).border = BORDER_ALL
        ws.cell(row=i, column=3, value=rule.get("dest_bus", "")).border = BORDER_ALL
        ws.cell(row=i, column=4, value="Yes" if rule.get("allowed", True) else "No").border = BORDER_ALL
        ws.cell(row=i, column=5, value=rule.get("description", "")).border = BORDER_ALL

    autosize(ws, {1: 10, 2: 15, 3: 15, 4: 10, 5: 40})


def build_recommendations(wb):
    ws = wb.create_sheet("Recommendations", 8)
    style_title(ws, 1, 2, "Recommendations & Observations")

    row = 3
    recommendations = [
        "Verify all routed signals have defined source and destination buses",
        "Ensure latency budgets are within system-level requirements",
        "Confirm firewall rules prevent unauthorized inter-domain routing",
        "Validate AUTOSAR PDU router configuration matches routing table",
        "Review gateway performance metrics during system testing",
    ]

    for rec in recommendations:
        cell = ws.cell(row=row, column=1, value=f"• {rec}")
        cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        ws.row_dimensions[row].height = 30
        row += 1

    autosize(ws, {1: 80})


def build_references(wb):
    ws = wb.create_sheet("References", 9)
    style_title(ws, 1, 2, "References")

    row = 3
    refs = [
        "AUTOSAR: Communication Specification",
        "ISO 11898-1: CAN FD Specification",
        "Internal: Gateway Routing Methodology (references/methodology.md)",
    ]

    for ref in refs:
        ws.cell(row=row, column=1, value=ref)
        row += 1

    autosize(ws, {1: 80})


def generate_gateway_workbook(input_json: dict) -> Workbook:
    wb = Workbook()
    wb.remove(wb.active)

    item = input_json.get("item", {})
    gateway = input_json.get("gateway", {})
    source_buses = input_json.get("source_buses", [])
    dest_buses = input_json.get("dest_buses", [])
    routes = input_json.get("routes", [])
    firewall_rules = input_json.get("firewall_rules", [])

    build_title(wb, item)
    build_doc_control(wb, item)
    build_gateway_ecu(wb, gateway)
    build_source_buses(wb, source_buses)
    build_dest_buses(wb, dest_buses)
    build_routing_table(wb, routes)
    build_latency_budget(wb, routes)
    build_security_rules(wb, firewall_rules)
    build_recommendations(wb)
    build_references(wb)

    return wb


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_gateway.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with open(input_path, "r") as f:
        input_data = json.load(f)

    wb = generate_gateway_workbook(input_data)
    wb.save(str(output_path))
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
