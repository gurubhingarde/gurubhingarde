"""DEM Config Builder — generates a multi-tab AUTOSAR DEM configuration workbook from JSON input.

Usage:
    python generate_dem.py <input.json> <output.xlsx>

Input JSON schema:
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "events": [
    {event_id, dtc, name, confirmation_threshold, healing_threshold, aging_counter_enabled}
  ],
  "debounce_config": [
    {event_id, pre_passed, pre_confirmed, confirmed, healed}
  ],
  "memory_config": {
    primary_size_bytes, secondary_size_bytes, mirror_enabled
  },
  "snapshot_records": [
    {event_id, snapshot_class, data_elements}
  ],
  "extended_data_records": [
    {event_id, edr_class, data_elements}
  ],
  "obd_config": {
    operation_cycle: "", freeze_frame_enabled: bool
  }
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


FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
ORANGE = "FFE699"
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


def build_title_sheet(wb, item_data):
    ws = wb.active
    ws.title = "Title"
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 50

    row = 1
    style_title(ws, row, 2, "DEM Configuration Workbook")
    row += 2

    fields = [
        ("Project", item_data.get("project", "")),
        ("Document Title", item_data.get("name", "")),
        ("Document ID", item_data.get("doc_id", "")),
        ("Revision", item_data.get("revision", "")),
        ("Date", item_data.get("date", "")),
        ("Author", item_data.get("author", "")),
        ("Approver", item_data.get("approver", "")),
        ("Company", item_data.get("company", "")),
    ]

    for label, value in fields:
        ws.cell(row=row, column=1, value=label).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

    ws.cell(row=row, column=1, value="Standard").font = Font(bold=True)
    ws.cell(row=row, column=2, value="AUTOSAR Classic Platform SWS_Dem")


def build_document_control_sheet(wb, item_data):
    ws = wb.create_sheet("Document Control")
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 30
    ws.column_dimensions["D"].width = 40

    row = 1
    style_title(ws, row, 4, "Document Control and Revision History")
    row += 2

    style_header(ws, row, ["Revision", "Date", "Author", "Changes"])
    row += 1

    ws.cell(row=row, column=1, value=item_data.get("revision", "1.0"))
    ws.cell(row=row, column=2, value=item_data.get("date", ""))
    ws.cell(row=row, column=3, value=item_data.get("author", ""))
    ws.cell(row=row, column=4, value="Initial release")


def build_module_id_sheet(wb, item_data):
    ws = wb.create_sheet("Module Identification")
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40

    row = 1
    style_title(ws, row, 2, "DEM Module Identification")
    row += 2

    style_header(ws, row, ["Parameter", "Value"])
    row += 1

    params = [
        ("Module Name", "Dem (Diagnostic Event Manager)"),
        ("Module Abbreviation", item_data.get("abbr", "")),
        ("Variant", item_data.get("project", "")),
        ("Target Platform", "AUTOSAR Classic 4.x"),
        ("Dem Instance ID", "0"),
    ]

    for param, value in params:
        ws.cell(row=row, column=1, value=param).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1


def build_event_inventory_sheet(wb, events):
    ws = wb.create_sheet("Event Inventory")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 30
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 18

    row = 1
    style_title(ws, row, 5, "Event Inventory (DTC Mapping)")
    row += 2

    style_header(ws, row, ["Event ID", "DTC", "Event Name", "Confirmation Threshold", "Healing Threshold"])
    row += 1

    for event in events:
        ws.cell(row=row, column=1, value=event.get("event_id", ""))
        ws.cell(row=row, column=2, value=event.get("dtc", ""))
        ws.cell(row=row, column=3, value=event.get("name", ""))
        ws.cell(row=row, column=4, value=event.get("confirmation_threshold", ""))
        ws.cell(row=row, column=5, value=event.get("healing_threshold", ""))
        row += 1


def build_debounce_sheet(wb, debounce_config):
    ws = wb.create_sheet("Debounce Configuration")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 16
    ws.column_dimensions["D"].width = 16
    ws.column_dimensions["E"].width = 16

    row = 1
    style_title(ws, row, 5, "Debounce Configuration (Counter-Based)")
    row += 2

    style_header(ws, row, ["Event ID", "Pre-Passed", "Pre-Confirmed", "Confirmed", "Healed"])
    row += 1

    for config in debounce_config:
        ws.cell(row=row, column=1, value=config.get("event_id", ""))
        ws.cell(row=row, column=2, value=config.get("pre_passed", ""))
        ws.cell(row=row, column=3, value=config.get("pre_confirmed", ""))
        ws.cell(row=row, column=4, value=config.get("confirmed", ""))
        ws.cell(row=row, column=5, value=config.get("healed", ""))
        row += 1


def build_memory_allocation_sheet(wb, memory_config):
    ws = wb.create_sheet("Memory Allocation")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 25

    row = 1
    style_title(ws, row, 2, "Event Memory Allocation")
    row += 2

    style_header(ws, row, ["Memory Region", "Size (bytes)"])
    row += 1

    ws.cell(row=row, column=1, value="Primary Memory").font = Font(bold=True)
    ws.cell(row=row, column=2, value=memory_config.get("primary_size_bytes", "1024"))
    row += 1

    ws.cell(row=row, column=1, value="Secondary Memory").font = Font(bold=True)
    ws.cell(row=row, column=2, value=memory_config.get("secondary_size_bytes", "512"))
    row += 1

    ws.cell(row=row, column=1, value="Mirror Memory Enabled").font = Font(bold=True)
    ws.cell(row=row, column=2, value=memory_config.get("mirror_enabled", "true"))


def build_snapshot_records_sheet(wb, snapshot_records):
    ws = wb.create_sheet("Snapshot Record Class")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 50

    row = 1
    style_title(ws, row, 3, "Snapshot Record Class Configuration")
    row += 2

    style_header(ws, row, ["Event ID", "Snapshot Class", "Data Elements"])
    row += 1

    for snap in snapshot_records:
        ws.cell(row=row, column=1, value=snap.get("event_id", ""))
        ws.cell(row=row, column=2, value=snap.get("snapshot_class", ""))
        data_elems = snap.get("data_elements", [])
        data_str = "; ".join(data_elems) if data_elems else ""
        ws.cell(row=row, column=3, value=data_str)
        row += 1


def build_edr_sheet(wb, edr_config):
    ws = wb.create_sheet("Extended Data Record")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 50

    row = 1
    style_title(ws, row, 3, "Extended Data Record (EDR) Configuration")
    row += 2

    style_header(ws, row, ["Event ID", "EDR Class", "Data Elements"])
    row += 1

    for edr in edr_config:
        ws.cell(row=row, column=1, value=edr.get("event_id", ""))
        ws.cell(row=row, column=2, value=edr.get("edr_class", ""))
        data_elems = edr.get("data_elements", [])
        data_str = "; ".join(data_elems) if data_elems else ""
        ws.cell(row=row, column=3, value=data_str)
        row += 1


def build_nvm_mapping_sheet(wb, events):
    ws = wb.create_sheet("NvM Block Mapping")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 20

    row = 1
    style_title(ws, row, 3, "NvM Block Mapping for Event Data Persistence")
    row += 2

    style_header(ws, row, ["Event ID", "Block ID", "Block Type"])
    row += 1

    block_id = 1
    for event in events:
        ws.cell(row=row, column=1, value=event.get("event_id", ""))
        ws.cell(row=row, column=2, value=block_id)
        ws.cell(row=row, column=3, value="EventData")
        row += 1
        block_id += 1


def build_aging_cycles_sheet(wb, events):
    ws = wb.create_sheet("Aging Cycles")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 25

    row = 1
    style_title(ws, row, 3, "Aging Cycle Configuration")
    row += 2

    style_header(ws, row, ["Event ID", "Aging Enabled", "Aging Threshold"])
    row += 1

    for event in events:
        ws.cell(row=row, column=1, value=event.get("event_id", ""))
        ws.cell(row=row, column=2, value=event.get("aging_counter_enabled", "true"))
        ws.cell(row=row, column=3, value="40 operation cycles")
        row += 1


def build_operation_cycles_sheet(wb, obd_config):
    ws = wb.create_sheet("Operation Cycles")
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40

    row = 1
    style_title(ws, row, 2, "Operation Cycle Definition")
    row += 2

    style_header(ws, row, ["Cycle Type", "Description"])
    row += 1

    cycles = [
        ("Ignition Cycle", "Key on → Key off, or engine start → stop"),
        ("Warm-up Cycle", "Engine cold start → reaches 70C"),
        ("OBD Cycle", obd_config.get("operation_cycle", "Ignition cycle")),
    ]

    for cycle_type, desc in cycles:
        ws.cell(row=row, column=1, value=cycle_type).font = Font(bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1


def build_obd_freeze_frame_sheet(wb, obd_config):
    ws = wb.create_sheet("OBD Freeze Frame Layout")
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40

    row = 1
    style_title(ws, row, 2, "OBD Freeze Frame Configuration")
    row += 2

    style_header(ws, row, ["Parameter", "Value"])
    row += 1

    params = [
        ("Freeze Frame Enabled", obd_config.get("freeze_frame_enabled", "true")),
        ("Frame Number", "0 (primary) + 1-4 (additional optional)"),
        ("Data PIDs", "PIDs from UDS data identifier list"),
        ("Capture Trigger", "DTC confirmation threshold exceeded"),
        ("Storage", "NvM block with freeze frame image"),
    ]

    for param, value in params:
        ws.cell(row=row, column=1, value=param).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1


def build_references_sheet(wb, item_data):
    ws = wb.create_sheet("References")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 60

    row = 1
    style_title(ws, row, 2, "References and Normative Documents")
    row += 2

    style_header(ws, row, ["Reference", "Description"])
    row += 1

    references = [
        ("AUTOSAR Classic 4.2", "AUTOSAR Platform specification (http://www.autosar.org)"),
        ("SWS_Dem", "Diagnostic Event Manager module specification"),
        ("ISO 14229-1:2020", "UDS - Unified Diagnostic Services"),
        ("ISO 15031-1", "Road vehicles - Diagnostic data dictionary"),
        ("SAE J1979", "OBD-II Diagnostic Service Data"),
    ]

    for ref, desc in references:
        ws.cell(row=row, column=1, value=ref).font = Font(bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.json> <output.xlsx>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    with open(input_file) as f:
        data = json.load(f)

    item_data = data.get("item", {})
    events = data.get("events", [])
    debounce_config = data.get("debounce_config", [])
    memory_config = data.get("memory_config", {})
    snapshot_records = data.get("snapshot_records", [])
    edr_config = data.get("extended_data_records", [])
    obd_config = data.get("obd_config", {})

    wb = Workbook()
    build_title_sheet(wb, item_data)
    build_document_control_sheet(wb, item_data)
    build_module_id_sheet(wb, item_data)
    build_event_inventory_sheet(wb, events)
    build_debounce_sheet(wb, debounce_config)
    build_memory_allocation_sheet(wb, memory_config)
    build_snapshot_records_sheet(wb, snapshot_records)
    build_edr_sheet(wb, edr_config)
    build_nvm_mapping_sheet(wb, events)
    build_aging_cycles_sheet(wb, events)
    build_operation_cycles_sheet(wb, obd_config)
    build_obd_freeze_frame_sheet(wb, obd_config)
    build_references_sheet(wb, item_data)

    wb.save(output_file)
    print(f"DEM config workbook written to {output_file}")


if __name__ == "__main__":
    main()
