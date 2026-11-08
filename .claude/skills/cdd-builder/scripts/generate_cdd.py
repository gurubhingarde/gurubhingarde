"""CDD Builder — generates a multi-tab CANdela Diagnostic Description xlsx from JSON input.

Usage:
    python generate_cdd.py <input.json> <output.xlsx>

Input JSON schema:
{
  "ecu": {name, abbr, project, doc_id, revision, date, author, approver},
  "sessions": [{id, name, description, default_session}],
  "services": [{service_id, name, enabled, description}],
  "diids": [{id, name, read_access, write_access, periodic_data_identifier}],
  "riids": [{id, name, routine_control_type, description}],
  "security_levels": [{level, request_seed_service, send_key_service}],
  "variant_coding": [{variant_id, variant_name, parent_variant, differences}],
  "dtc_catalog_ref": "path/to/dtc_catalog.xlsx"
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

    style_title(ws, 2, 5, "CDD (CANdela Diagnostic Description)")
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
        ("Standard", "ISO 14229-1, Vector CANdela"),
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


def build_ecu_identity(wb, ecu_info):
    ws = wb.create_sheet("ECU Identity", 2)
    style_title(ws, 2, 5, "ECU Identity")
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


def build_sessions(wb, sessions):
    ws = wb.create_sheet("Session Catalog", 3)
    style_title(ws, 2, 5, "Session Catalog")
    style_header(ws, 4, ["Session ID", "Session Name", "Default", "Description", "Transitions"])

    row = 5
    for session in sessions or []:
        ws.cell(row=row, column=1, value=session.get("id", ""))
        ws.cell(row=row, column=2, value=session.get("name", ""))
        ws.cell(row=row, column=3, value="Yes" if session.get("default_session") else "No")
        ws.cell(row=row, column=4, value=session.get("description", ""))
        ws.cell(row=row, column=5, value=session.get("transitions", ""))
        row += 1

    autosize(ws, {1: 14, 2: 24, 3: 10, 4: 40, 5: 30})


def build_services(wb, services):
    ws = wb.create_sheet("Service Inventory", 4)
    style_title(ws, 2, 5, "Service Inventory")
    style_header(ws, 4, ["Service ID", "Service Name", "Enabled", "Description", "Min/Max Data Length"])

    row = 5
    for service in services or []:
        ws.cell(row=row, column=1, value=service.get("service_id", ""))
        ws.cell(row=row, column=2, value=service.get("name", ""))
        ws.cell(row=row, column=3, value="Yes" if service.get("enabled") else "No")
        ws.cell(row=row, column=4, value=service.get("description", ""))
        ws.cell(row=row, column=5, value=service.get("data_length", ""))
        row += 1

    autosize(ws, {1: 14, 2: 30, 3: 10, 4: 40, 5: 20})


def build_diids(wb, diids):
    ws = wb.create_sheet("DID Catalog", 5)
    style_title(ws, 2, 6, "Data Identifier (DID) Catalog")
    style_header(ws, 4, ["DID Code", "Name", "Read Access", "Write Access", "Periodic", "Description"])

    row = 5
    for diid in diids or []:
        ws.cell(row=row, column=1, value=diid.get("id", ""))
        ws.cell(row=row, column=2, value=diid.get("name", ""))
        ws.cell(row=row, column=3, value="Yes" if diid.get("read_access") else "No")
        ws.cell(row=row, column=4, value="Yes" if diid.get("write_access") else "No")
        ws.cell(row=row, column=5, value="Yes" if diid.get("periodic_data_identifier") else "No")
        ws.cell(row=row, column=6, value=diid.get("description", ""))
        row += 1

    autosize(ws, {1: 12, 2: 30, 3: 12, 4: 12, 5: 10, 6: 40})


def build_riids(wb, riids):
    ws = wb.create_sheet("RID Catalog", 6)
    style_title(ws, 2, 5, "Routine Identifier (RID) Catalog")
    style_header(ws, 4, ["RID Code", "Name", "Control Type", "Description", "Options"])

    row = 5
    for riid in riids or []:
        ws.cell(row=row, column=1, value=riid.get("id", ""))
        ws.cell(row=row, column=2, value=riid.get("name", ""))
        ws.cell(row=row, column=3, value=riid.get("routine_control_type", ""))
        ws.cell(row=row, column=4, value=riid.get("description", ""))
        ws.cell(row=row, column=5, value=riid.get("options", ""))
        row += 1

    autosize(ws, {1: 12, 2: 30, 3: 20, 4: 40, 5: 30})


def build_dtc_cross_ref(wb, dtc_ref):
    ws = wb.create_sheet("DTC Cross-Reference", 7)
    style_title(ws, 2, 3, "DTC Cross-Reference")
    style_header(ws, 4, ["Source DTC Catalog", "Link"])

    if dtc_ref:
        ws.cell(row=5, column=1, value="Linked DTC Catalog")
        ws.cell(row=5, column=2, value=dtc_ref)

    autosize(ws, {1: 30, 2: 80})


def build_security(wb, security_levels):
    ws = wb.create_sheet("Security Access Levels", 8)
    style_title(ws, 2, 4, "Security Access Levels")
    style_header(ws, 4, ["Level", "Request Seed Service", "Send Key Service", "Description"])

    row = 5
    for level in security_levels or []:
        ws.cell(row=row, column=1, value=level.get("level", ""))
        ws.cell(row=row, column=2, value=level.get("request_seed_service", "27 01"))
        ws.cell(row=row, column=3, value=level.get("send_key_service", "27 02"))
        ws.cell(row=row, column=4, value=level.get("description", ""))
        row += 1

    autosize(ws, {1: 10, 2: 24, 3: 20, 4: 40})


def build_variants(wb, variants):
    ws = wb.create_sheet("Variant Coding", 9)
    style_title(ws, 2, 5, "Variant Coding")
    style_header(ws, 4, ["Variant ID", "Variant Name", "Parent Variant", "Differences", "Active"])

    row = 5
    for variant in variants or []:
        ws.cell(row=row, column=1, value=variant.get("variant_id", ""))
        ws.cell(row=row, column=2, value=variant.get("variant_name", ""))
        ws.cell(row=row, column=3, value=variant.get("parent_variant", ""))
        ws.cell(row=row, column=4, value=variant.get("differences", ""))
        ws.cell(row=row, column=5, value="Yes")
        row += 1

    autosize(ws, {1: 14, 2: 24, 3: 20, 4: 40, 5: 10})


def build_communication(wb):
    ws = wb.create_sheet("Communication Configuration", 10)
    style_title(ws, 2, 4, "Communication Configuration")
    style_header(ws, 4, ["Parameter", "Value", "Description"])

    params = [
        ("Transport Protocol", "ISO-TP (ISO 15765-2)", "CAN transport layer"),
        ("Addressing Scheme", "Normal (29-bit CAN ID)", "Extended CAN ID"),
        ("Request ID", "7DFh", "Broadcast ID for diagnostic requests"),
        ("Response ID", "7DEh", "ECU response identifier"),
        ("Timing P2", "50 ms", "Server response timeout"),
        ("Timing P2*", "5000 ms", "Extended server response timeout"),
    ]

    row = 5
    for param, value, desc in params:
        ws.cell(row=row, column=1, value=param).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        ws.cell(row=row, column=3, value=desc)
        row += 1

    autosize(ws, {1: 24, 2: 30, 3: 40})


def build_references(wb):
    ws = wb.create_sheet("References", 11)
    style_title(ws, 2, 3, "References")

    row = 5
    references = [
        ("ISO 14229-1:2020", "Road vehicles — Unified diagnostic services (UDS)"),
        ("Vector CANdela", "Vector diagnostic database specification"),
        ("ISO 15765-2", "Road vehicles — Diagnostic communication over CAN (ISO-TP)"),
    ]

    for ref, desc in references:
        ws.cell(row=row, column=1, value=ref).font = Font(bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1

    autosize(ws, {1: 24, 2: 80})


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_cdd.py <input.json> <output.xlsx>")
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
    build_ecu_identity(wb, ecu)
    build_sessions(wb, data.get("sessions", []))
    build_services(wb, data.get("services", []))
    build_diids(wb, data.get("diids", []))
    build_riids(wb, data.get("riids", []))
    build_dtc_cross_ref(wb, data.get("dtc_catalog_ref", ""))
    build_security(wb, data.get("security_levels", []))
    build_variants(wb, data.get("variant_coding", []))
    build_communication(wb)
    build_references(wb)

    wb.save(output_path)
    print(json.dumps({
        "status": "success",
        "services": len(data.get("services", [])),
        "diids": len(data.get("diids", [])),
        "riids": len(data.get("riids", [])),
        "variants": len(data.get("variant_coding", [])),
        "output": str(output_path)
    }))


if __name__ == "__main__":
    main()
