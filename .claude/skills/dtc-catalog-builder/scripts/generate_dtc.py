"""DTC Catalog Builder — generates a multi-tab ISO 14229-1 + SAE J2012 DTC catalog xlsx from JSON input.

Usage:
    python generate_dtc.py <input.json> <output.xlsx>

Input JSON schema:
{
  "ecu": {name, abbr, project, doc_id, revision, date, author, approver},
  "dtcs": [{code, description, fault_type, severity, customer_impact, hex_code, mal_function_id}],
  "snapshot_bindings": [{dtc_code, did_list}],
  "extended_data": [{dtc_code, data_fields, retention_level}],
  "status_masks": [{bit_name, bit_position, definition}],
  "debounce_algorithms": [{id, method, counter_threshold, time_threshold_ms}],
  "healing_logic": [{dtc_code, healing_condition, recovery_action}],
  "obd_mapping": [{dtc_code, obd_code, monitor_type, emissions_relevance}]
}
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
FONT_NAME = "Calibri"
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


def build_title(wb, ecu_info):
    ws = wb.create_sheet("Title", 0)
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 5, "DTC Catalog")
    style_title(ws, 3, 5, ecu_info.get("name", "ECU"))

    fields = [
        ("ECU Name", ecu_info.get("name", "")),
        ("Abbreviation", ecu_info.get("abbr", "")),
        ("Project", ecu_info.get("project", "")),
        ("Document ID", ecu_info.get("doc_id", "")),
        ("Revision", ecu_info.get("revision", "1.0")),
        ("Date", ecu_info.get("date", date.today().isoformat())),
        ("Author", ecu_info.get("author", "")),
        ("Approver", ecu_info.get("approver", "")),
        ("Standard", "ISO 14229-1, SAE J2012"),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = Font(name=FONT_NAME, size=10)
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1

    autosize(ws, {1: 4, 2: 26, 3: 60, 4: 4, 5: 4})


def build_document_control(wb):
    ws = wb.create_sheet("Document Control", 1)
    style_title(ws, 2, 5, "Document Control")
    style_header(ws, 4, ["Revision", "Date", "Author", "Change Description", "Status"])

    ws.cell(row=5, column=1, value="1.0")
    ws.cell(row=5, column=2, value=date.today().isoformat())
    ws.cell(row=5, column=3, value="")
    ws.cell(row=5, column=4, value="Initial release")
    ws.cell(row=5, column=5, value="Draft")

    autosize(ws, {1: 12, 2: 14, 3: 20, 4: 40, 5: 12})


def build_ecu_id(wb, ecu_info):
    ws = wb.create_sheet("ECU Identification", 2)
    style_title(ws, 2, 5, "ECU Identification")
    style_header(ws, 4, ["Parameter", "Value"])

    params = [
        ("ECU Name", ecu_info.get("name", "")),
        ("Abbreviation", ecu_info.get("abbr", "")),
        ("Supplier", ecu_info.get("supplier", "")),
        ("Hardware Version", ecu_info.get("hw_version", "")),
        ("Software Version", ecu_info.get("sw_version", "")),
        ("Market Region", ecu_info.get("market", "")),
    ]

    row = 5
    for param, value in params:
        ws.cell(row=row, column=1, value=param).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

    autosize(ws, {1: 24, 2: 50})


def build_dtc_inventory(wb, dtcs):
    ws = wb.create_sheet("DTC Inventory", 3)
    style_title(ws, 2, 8, "DTC Inventory")
    style_header(ws, 4, ["DTC Code", "Hex", "Description", "Fault Type", "Severity", "Customer Impact", "MIL Trigger", "Malfunction ID"])

    row = 5
    for dtc in dtcs or []:
        ws.cell(row=row, column=1, value=dtc.get("code", ""))
        ws.cell(row=row, column=2, value=dtc.get("hex_code", ""))
        ws.cell(row=row, column=3, value=dtc.get("description", ""))
        ws.cell(row=row, column=4, value=dtc.get("fault_type", ""))
        ws.cell(row=row, column=5, value=dtc.get("severity", ""))
        ws.cell(row=row, column=6, value=dtc.get("customer_impact", ""))
        ws.cell(row=row, column=7, value=dtc.get("mil_trigger", "No"))
        ws.cell(row=row, column=8, value=dtc.get("mal_function_id", ""))
        row += 1

    autosize(ws, {1: 14, 2: 12, 3: 40, 4: 18, 5: 12, 6: 20, 7: 14, 8: 16})


def build_snapshot_diag(wb, snapshot_bindings):
    ws = wb.create_sheet("Snapshot DID Bindings", 4)
    style_title(ws, 2, 4, "Snapshot DID Bindings")
    style_header(ws, 4, ["DTC Code", "Snapshot DIDs", "Freeze Condition"])

    row = 5
    for binding in snapshot_bindings or []:
        ws.cell(row=row, column=1, value=binding.get("dtc_code", ""))
        ws.cell(row=row, column=2, value=", ".join(binding.get("did_list", [])))
        ws.cell(row=row, column=3, value=binding.get("freeze_condition", "At DTC set"))
        row += 1

    autosize(ws, {1: 14, 2: 50, 3: 30})


def build_extended_data(wb, extended_data):
    ws = wb.create_sheet("Extended Data Records", 5)
    style_title(ws, 2, 4, "Extended Data Records")
    style_header(ws, 4, ["DTC Code", "Data Fields", "Retention Level"])

    row = 5
    for edr in extended_data or []:
        ws.cell(row=row, column=1, value=edr.get("dtc_code", ""))
        ws.cell(row=row, column=2, value=", ".join(edr.get("data_fields", [])))
        ws.cell(row=row, column=3, value=edr.get("retention_level", "Permanent"))
        row += 1

    autosize(ws, {1: 14, 2: 50, 3: 20})


def build_status_mask(wb, status_masks):
    ws = wb.create_sheet("Status Mask Configuration", 6)
    style_title(ws, 2, 4, "Status Mask Configuration")
    style_header(ws, 4, ["Bit Name", "Bit Position", "Definition", "Mandatory"])

    row = 5
    for mask in status_masks or []:
        ws.cell(row=row, column=1, value=mask.get("bit_name", ""))
        ws.cell(row=row, column=2, value=mask.get("bit_position", ""))
        ws.cell(row=row, column=3, value=mask.get("definition", ""))
        ws.cell(row=row, column=4, value="Yes")
        row += 1

    autosize(ws, {1: 20, 2: 14, 3: 40, 4: 12})


def build_debounce(wb, debounce_algorithms):
    ws = wb.create_sheet("Debounce Algorithms", 7)
    style_title(ws, 2, 5, "Debounce Algorithm Catalog")
    style_header(ws, 4, ["Algorithm ID", "Method", "Counter Threshold", "Time Threshold (ms)", "Description"])

    row = 5
    for alg in debounce_algorithms or []:
        ws.cell(row=row, column=1, value=alg.get("id", ""))
        ws.cell(row=row, column=2, value=alg.get("method", ""))
        ws.cell(row=row, column=3, value=alg.get("counter_threshold", ""))
        ws.cell(row=row, column=4, value=alg.get("time_threshold_ms", ""))
        ws.cell(row=row, column=5, value=alg.get("description", ""))
        row += 1

    autosize(ws, {1: 16, 2: 16, 3: 18, 4: 18, 5: 30})


def build_healing(wb, healing_logic):
    ws = wb.create_sheet("Healing Logic", 8)
    style_title(ws, 2, 4, "Healing Logic")
    style_header(ws, 4, ["DTC Code", "Healing Condition", "Recovery Action"])

    row = 5
    for heal in healing_logic or []:
        ws.cell(row=row, column=1, value=heal.get("dtc_code", ""))
        ws.cell(row=row, column=2, value=heal.get("healing_condition", ""))
        ws.cell(row=row, column=3, value=heal.get("recovery_action", ""))
        row += 1

    autosize(ws, {1: 14, 2: 40, 3: 40})


def build_obd_mapping(wb, obd_mapping):
    ws = wb.create_sheet("OBD Mapping", 9)
    style_title(ws, 2, 5, "OBD-II Mapping")
    style_header(ws, 4, ["DTC Code", "OBD Code", "Monitor Type", "Readiness Monitor", "Emissions Relevance"])

    row = 5
    for mapping in obd_mapping or []:
        ws.cell(row=row, column=1, value=mapping.get("dtc_code", ""))
        ws.cell(row=row, column=2, value=mapping.get("obd_code", ""))
        ws.cell(row=row, column=3, value=mapping.get("monitor_type", ""))
        ws.cell(row=row, column=4, value=mapping.get("readiness_monitor", ""))
        ws.cell(row=row, column=5, value=mapping.get("emissions_relevance", "No"))
        row += 1

    autosize(ws, {1: 14, 2: 14, 3: 20, 4: 20, 5: 20})


def build_test_conditions(wb):
    ws = wb.create_sheet("Test Conditions", 10)
    style_title(ws, 2, 4, "Test Conditions")
    style_header(ws, 4, ["DTC Code", "Set Condition", "Clear Condition"])

    autosize(ws, {1: 14, 2: 40, 3: 40})


def build_references(wb):
    ws = wb.create_sheet("References", 11)
    style_title(ws, 2, 3, "References")

    row = 5
    references = [
        ("ISO 14229-1:2020", "Road vehicles — Unified diagnostic services (UDS)"),
        ("SAE J2012", "Diagnostic Trouble Code Definitions"),
        ("ISO 15031-6", "Road vehicles — OBD codes and data dictionary"),
    ]

    for ref, desc in references:
        ws.cell(row=row, column=1, value=ref).font = Font(bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1

    autosize(ws, {1: 20, 2: 60})


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_dtc.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with open(input_path) as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    ecu = data.get("ecu", {})
    build_title(wb, ecu)
    build_document_control(wb)
    build_ecu_id(wb, ecu)
    build_dtc_inventory(wb, data.get("dtcs", []))
    build_snapshot_diag(wb, data.get("snapshot_bindings", []))
    build_extended_data(wb, data.get("extended_data", []))
    build_status_mask(wb, data.get("status_masks", []))
    build_debounce(wb, data.get("debounce_algorithms", []))
    build_healing(wb, data.get("healing_logic", []))
    build_obd_mapping(wb, data.get("obd_mapping", []))
    build_test_conditions(wb)
    build_references(wb)

    wb.save(output_path)
    print(json.dumps({
        "status": "success",
        "dtc_count": len(data.get("dtcs", [])),
        "snapshot_bindings": len(data.get("snapshot_bindings", [])),
        "extended_data_records": len(data.get("extended_data", [])),
        "output": str(output_path)
    }))


if __name__ == "__main__":
    main()
