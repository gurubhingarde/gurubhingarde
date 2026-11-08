"""
AUTOSAR SWC Builder — generates a multi-tab AUTOSAR R22-11 SWC specification workbook from JSON input.

Usage:
    python generate_swc.py <input.json> <output.xlsx>

Input JSON schema:
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "swc_type": {name, category, implementation_type, description},  // category: Application|Sensor/Actuator|Service|Complex Driver
  "ports": [
    {id, name, category, direction, interface_name, interface_type}  // direction: Provided|Required; category: SR|CS|MS|NV|Param|Trigger
  ],
  "runnables": [
    {id, name, description, timing_trigger, schedule, exclusive_areas}
  ],
  "events": [
    {id, name, trigger_type, startup, period_ms}  // trigger_type: TimingEvent|DataReceivedEvent|etc
  ],
  "exclusive_areas": [
    {id, name, runnables}
  ],
  "data_types": [
    {id, name, base_type, range_min, range_max, unit, precision}
  ],
  "implementation_data_types": [
    {id, name, category, underlying_type, description}
  ]
}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import date as today_date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


# Styling constants
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


# Tab builders

def build_title_page(wb: Workbook, item: dict, swc_type: dict) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 2, 4, "AUTOSAR R22-11 Software Component (SWC) Specification")
    style_title_row(ws, 3, 4, f"{swc_type.get('name', '')} ({item.get('abbr', '')})")

    fields = [
        ("Project", item.get("project", "")),
        ("SWC Name", swc_type.get("name", "")),
        ("SWC Category", swc_type.get("category", "")),
        ("Document ID", item.get("doc_id", "")),
        ("Revision", item.get("revision", "")),
        ("Date", item.get("date", str(today_date.today()))),
        ("Author", item.get("author", "")),
        ("Approver", item.get("approver", "")),
        ("Company", item.get("company", "")),
        ("AUTOSAR Version", "R22-11 (Classic Platform)"),
        ("Implementation Type", swc_type.get("implementation_type", "Software")),
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
        ("0.1", "", "", "Initial draft generated by autosar-swc-builder", ""),
        ("0.2", "", "", "Internal review comments incorporated", ""),
        ("1.0", "", "", "Released for architecture review", ""),
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


def build_swc_identification(wb: Workbook, item: dict, swc_type: dict) -> None:
    ws = wb.create_sheet("02_SWC_Identification")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "SWC Identification and Classification")

    fields = [
        ("SWC Name", swc_type.get("name", "")),
        ("Abbreviation", item.get("abbr", "")),
        ("Category", swc_type.get("category", "")),
        ("Description", swc_type.get("description", "")),
        ("Implementation Type", swc_type.get("implementation_type", "Software")),
        ("Vendor/Owner", item.get("company", "")),
    ]

    row = 3
    for label, value in fields:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True, size=10)
        ws.cell(row=row, column=2, value=value).font = body_font()
        ws.cell(row=row, column=2).alignment = Alignment(wrap_text=True, vertical="top")
        row += 1

    autosize(ws, {1: 22, 2: 60})


def build_port_inventory(wb: Workbook, ports: list[dict]) -> None:
    ws = wb.create_sheet("03_Port_Inventory")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Port Inventory (Provided and Required)")

    style_header_row(ws, 3, ["Port ID", "Port Name", "Category", "Direction", "Interface Name", "Interface Type"])
    if not ports:
        ports = [
            {"id": "P01", "name": "SamplePort", "category": "SR", "direction": "Provided", "interface_name": "SampleInterface", "interface_type": "SenderReceiver"},
        ]
    for i, p in enumerate(ports, start=4):
        ws.cell(row=i, column=1, value=p.get("id", ""))
        ws.cell(row=i, column=2, value=p.get("name", ""))
        ws.cell(row=i, column=3, value=p.get("category", ""))
        ws.cell(row=i, column=4, value=p.get("direction", ""))
        ws.cell(row=i, column=5, value=p.get("interface_name", ""))
        ws.cell(row=i, column=6, value=p.get("interface_type", ""))
    stripe_body(ws, 4, 3 + len(ports), 6)
    autosize(ws, {1: 10, 2: 22, 3: 12, 4: 14, 5: 28, 6: 20})


def build_sr_interfaces(wb: Workbook, ports: list[dict]) -> None:
    ws = wb.create_sheet("04_SR_Interfaces")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Sender-Receiver Port Interfaces")

    style_header_row(ws, 3, ["Port ID", "Interface Name", "Data Element", "Type", "Direction"])
    sr_ports = [p for p in ports if p.get("category") == "SR"]
    if not sr_ports:
        sr_ports = []
    for i, p in enumerate(sr_ports, start=4):
        ws.cell(row=i, column=1, value=p.get("id", ""))
        ws.cell(row=i, column=2, value=p.get("interface_name", ""))
        ws.cell(row=i, column=3, value=p.get("data_element", ""))
        ws.cell(row=i, column=4, value=p.get("type", ""))
        ws.cell(row=i, column=5, value=p.get("direction", ""))
    if sr_ports:
        stripe_body(ws, 4, 3 + len(sr_ports), 5)
    autosize(ws, {1: 10, 2: 28, 3: 28, 4: 20, 5: 14})


def build_cs_interfaces(wb: Workbook, ports: list[dict]) -> None:
    ws = wb.create_sheet("05_CS_Interfaces")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Client-Server Port Interfaces")

    style_header_row(ws, 3, ["Port ID", "Interface Name", "Operation", "Input Args", "Output Args"])
    cs_ports = [p for p in ports if p.get("category") == "CS"]
    if not cs_ports:
        cs_ports = []
    for i, p in enumerate(cs_ports, start=4):
        ws.cell(row=i, column=1, value=p.get("id", ""))
        ws.cell(row=i, column=2, value=p.get("interface_name", ""))
        ws.cell(row=i, column=3, value=p.get("operation", ""))
        ws.cell(row=i, column=4, value=p.get("input_args", ""))
        ws.cell(row=i, column=5, value=p.get("output_args", ""))
    if cs_ports:
        stripe_body(ws, 4, 3 + len(cs_ports), 5)
    autosize(ws, {1: 10, 2: 28, 3: 24, 4: 28, 5: 28})


def build_ms_interfaces(wb: Workbook, ports: list[dict]) -> None:
    ws = wb.create_sheet("06_MS_Interfaces")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Mode-Switch Port Interfaces")

    style_header_row(ws, 3, ["Port ID", "Interface Name", "Mode Group", "Modes"])
    ms_ports = [p for p in ports if p.get("category") == "MS"]
    if not ms_ports:
        ms_ports = []
    for i, p in enumerate(ms_ports, start=4):
        ws.cell(row=i, column=1, value=p.get("id", ""))
        ws.cell(row=i, column=2, value=p.get("interface_name", ""))
        ws.cell(row=i, column=3, value=p.get("mode_group", ""))
        ws.cell(row=i, column=4, value=p.get("modes", ""))
    if ms_ports:
        stripe_body(ws, 4, 3 + len(ms_ports), 4)
    autosize(ws, {1: 10, 2: 28, 3: 24, 4: 40})


def build_internal_behavior(wb: Workbook, runnables: list[dict], events: list[dict]) -> None:
    ws = wb.create_sheet("07_Internal_Behavior")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Internal Behavior — Runnables and Events")

    ws.cell(row=3, column=1, value="Runnables Summary").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    style_header_row(ws, 4, ["Runnable ID", "Name", "Trigger Type", "Schedule (ms)", "Exclusive Areas"])
    if not runnables:
        runnables = []
    for i, r in enumerate(runnables, start=5):
        ws.cell(row=i, column=1, value=r.get("id", ""))
        ws.cell(row=i, column=2, value=r.get("name", ""))
        ws.cell(row=i, column=3, value=r.get("timing_trigger", "Periodic"))
        ws.cell(row=i, column=4, value=r.get("schedule", ""))
        ws.cell(row=i, column=5, value=r.get("exclusive_areas", ""))
    if runnables:
        stripe_body(ws, 5, 4 + len(runnables), 5)

    base_row = 6 + len(runnables)
    ws.cell(row=base_row, column=1, value="Events Summary").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    style_header_row(ws, base_row + 1, ["Event ID", "Name", "Trigger Type", "Period (ms)"])
    if not events:
        events = []
    for i, e in enumerate(events, start=base_row + 2):
        ws.cell(row=i, column=1, value=e.get("id", ""))
        ws.cell(row=i, column=2, value=e.get("name", ""))
        ws.cell(row=i, column=3, value=e.get("trigger_type", ""))
        ws.cell(row=i, column=4, value=e.get("period_ms", ""))
    if events:
        stripe_body(ws, base_row + 2, base_row + 1 + len(events), 4)

    autosize(ws, {1: 12, 2: 24, 3: 18, 4: 16, 5: 28})


def build_runnable_catalog(wb: Workbook, runnables: list[dict]) -> None:
    ws = wb.create_sheet("08_Runnable_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Runnable Catalog")

    if not runnables:
        runnables = []

    row = 3
    for r in runnables:
        ws.cell(row=row, column=1, value=f"ID: {r.get('id', '')}").font = Font(name=FONT_NAME, bold=True, size=10)
        ws.cell(row=row, column=2, value=f"Name: {r.get('name', '')}").font = Font(name=FONT_NAME, size=10)
        row += 1
        ws.cell(row=row, column=1, value="Description:").font = Font(name=FONT_NAME, bold=True, size=9)
        ws.cell(row=row, column=2, value=r.get("description", "")).font = body_font()
        row += 1
        ws.cell(row=row, column=1, value="Timing Trigger:").font = Font(name=FONT_NAME, bold=True, size=9)
        ws.cell(row=row, column=2, value=r.get("timing_trigger", "")).font = body_font()
        row += 1
        ws.cell(row=row, column=1, value="Schedule:").font = Font(name=FONT_NAME, bold=True, size=9)
        ws.cell(row=row, column=2, value=r.get("schedule", "")).font = body_font()
        row += 2

    autosize(ws, {1: 28, 2: 60})


def build_event_catalog(wb: Workbook, events: list[dict]) -> None:
    ws = wb.create_sheet("09_Event_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Event Catalog")

    if not events:
        events = []

    row = 3
    for e in events:
        ws.cell(row=row, column=1, value=f"ID: {e.get('id', '')}").font = Font(name=FONT_NAME, bold=True, size=10)
        ws.cell(row=row, column=2, value=f"Name: {e.get('name', '')}").font = Font(name=FONT_NAME, size=10)
        row += 1
        ws.cell(row=row, column=1, value="Trigger Type:").font = Font(name=FONT_NAME, bold=True, size=9)
        ws.cell(row=row, column=2, value=e.get("trigger_type", "")).font = body_font()
        row += 1
        ws.cell(row=row, column=1, value="Startup:").font = Font(name=FONT_NAME, bold=True, size=9)
        ws.cell(row=row, column=2, value=e.get("startup", "")).font = body_font()
        row += 1
        ws.cell(row=row, column=1, value="Period (ms):").font = Font(name=FONT_NAME, bold=True, size=9)
        ws.cell(row=row, column=2, value=e.get("period_ms", "")).font = body_font()
        row += 2

    autosize(ws, {1: 28, 2: 60})


def build_exclusive_areas(wb: Workbook, exclusive_areas: list[dict]) -> None:
    ws = wb.create_sheet("10_Exclusive_Areas")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Exclusive Areas")

    style_header_row(ws, 3, ["Exclusive Area ID", "Name", "Runnables"])
    if not exclusive_areas:
        exclusive_areas = []
    for i, ea in enumerate(exclusive_areas, start=4):
        ws.cell(row=i, column=1, value=ea.get("id", ""))
        ws.cell(row=i, column=2, value=ea.get("name", ""))
        ws.cell(row=i, column=3, value=ea.get("runnables", ""))
    if exclusive_areas:
        stripe_body(ws, 4, 3 + len(exclusive_areas), 3)

    autosize(ws, {1: 18, 2: 24, 3: 40})


def build_data_types(wb: Workbook, data_types: list[dict]) -> None:
    ws = wb.create_sheet("11_Data_Types")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Data Types")

    style_header_row(ws, 3, ["Type ID", "Name", "Base Type", "Range Min", "Range Max", "Unit"])
    if not data_types:
        data_types = []
    for i, dt in enumerate(data_types, start=4):
        ws.cell(row=i, column=1, value=dt.get("id", ""))
        ws.cell(row=i, column=2, value=dt.get("name", ""))
        ws.cell(row=i, column=3, value=dt.get("base_type", ""))
        ws.cell(row=i, column=4, value=dt.get("range_min", ""))
        ws.cell(row=i, column=5, value=dt.get("range_max", ""))
        ws.cell(row=i, column=6, value=dt.get("unit", ""))
    if data_types:
        stripe_body(ws, 4, 3 + len(data_types), 6)

    autosize(ws, {1: 12, 2: 24, 3: 18, 4: 14, 5: 14, 6: 16})


def build_implementation_data_types(wb: Workbook, impl_data_types: list[dict]) -> None:
    ws = wb.create_sheet("12_Implementation_Data_Types")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Implementation Data Types")

    style_header_row(ws, 3, ["Impl Type ID", "Name", "Category", "Underlying Type"])
    if not impl_data_types:
        impl_data_types = []
    for i, idt in enumerate(impl_data_types, start=4):
        ws.cell(row=i, column=1, value=idt.get("id", ""))
        ws.cell(row=i, column=2, value=idt.get("name", ""))
        ws.cell(row=i, column=3, value=idt.get("category", ""))
        ws.cell(row=i, column=4, value=idt.get("underlying_type", ""))
    if impl_data_types:
        stripe_body(ws, 4, 3 + len(impl_data_types), 4)

    autosize(ws, {1: 16, 2: 24, 3: 20, 4: 28})


def build_references(wb: Workbook) -> None:
    ws = wb.create_sheet("13_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "References")

    style_header_row(ws, 3, ["Document / Standard", "Title / Description"])
    refs = [
        ("AUTOSAR R22-11", "AUTOSAR Classic Platform Specification"),
        ("ISO 26262:2018", "Road vehicles - Functional safety"),
        ("MISRA C:2012", "Guidelines for the use of the C language in vehicle systems"),
    ]
    for i, (ref, title) in enumerate(refs, start=4):
        ws.cell(row=i, column=1, value=ref)
        ws.cell(row=i, column=2, value=title)
    stripe_body(ws, 4, 3 + len(refs), 2)

    autosize(ws, {1: 24, 2: 60})


def generate(input_path: str, output_path: str) -> dict:
    with open(input_path) as f:
        data = json.load(f)

    item = data.get("item", {})
    swc_type = data.get("swc_type", {})
    ports = data.get("ports", [])
    runnables = data.get("runnables", [])
    events = data.get("events", [])
    exclusive_areas = data.get("exclusive_areas", [])
    data_types = data.get("data_types", [])
    impl_data_types = data.get("implementation_data_types", [])

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, item, swc_type)
    build_doc_control(wb)
    build_swc_identification(wb, item, swc_type)
    build_port_inventory(wb, ports)
    build_sr_interfaces(wb, ports)
    build_cs_interfaces(wb, ports)
    build_ms_interfaces(wb, ports)
    build_internal_behavior(wb, runnables, events)
    build_runnable_catalog(wb, runnables)
    build_event_catalog(wb, events)
    build_exclusive_areas(wb, exclusive_areas)
    build_data_types(wb, data_types)
    build_implementation_data_types(wb, impl_data_types)
    build_references(wb)

    wb.active = 0
    wb.save(output_path)

    return {
        "swc_name": swc_type.get("name", "Unknown"),
        "category": swc_type.get("category", ""),
        "ports": len(ports),
        "runnables": len(runnables),
        "events": len(events),
        "exclusive_areas": len(exclusive_areas),
        "data_types": len(data_types),
        "implementation_data_types": len(impl_data_types),
        "output_path": output_path,
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_swc.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
