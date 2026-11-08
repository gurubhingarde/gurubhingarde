"""ODX Builder — generates a multi-tab ISO 22901-1 ODX workbook from a JSON input.

Usage:
    python generate_odx.py <input.json> <output.xlsx>

Input JSON schema:
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "odx_layers": [
    {id, layer_type (D|C|V|FD), description}
  ],
  "base_variants": [
    {id, name, ecu_id, interfaces: [{name, type}]}
  ],
  "derived_variants": [
    {id, name, parent_variant_id, specializations: [{property, value}]}
  ],
  "pdu_library": [
    {id, name, length, multiplexing, signals: [{name, position, length}]}
  ],
  "services": [
    {id, name, request_pdu_id, response_pdu_id, parameters: [{name, type}]}
  ],
  "dtcs": [
    {id, name, severity, functionally_safe}
  ],
  "data_objects": [
    {id, name, type, unit, semantic_ref}
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


# ============================================================================
# Styles and constants
# ============================================================================

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
    style_title(ws, row, 2, "ODX Authoring Workbook")
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
        ("Abbreviation", item_data.get("abbr", "")),
    ]

    for label, value in fields:
        ws.cell(row=row, column=1, value=label).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

    ws.cell(row=row, column=1, value="Standard").font = Font(bold=True)
    ws.cell(row=row, column=2, value="ISO 22901-1 (ODX)")


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


def build_odx_layer_hierarchy_sheet(wb, odx_layers):
    ws = wb.create_sheet("ODX Layer Hierarchy")
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 50

    row = 1
    style_title(ws, row, 3, "ODX Layer Hierarchy")
    row += 2

    style_header(ws, row, ["Layer ID", "Type", "Description"])
    row += 1

    layer_order = {"D": 1, "C": 2, "V": 3, "FD": 4}
    sorted_layers = sorted(odx_layers, key=lambda x: layer_order.get(x.get("layer_type", "D"), 99))

    for layer in sorted_layers:
        layer_id = layer.get("id", "")
        layer_type = layer.get("layer_type", "D")
        desc = layer.get("description", "")

        ws.cell(row=row, column=1, value=layer_id)
        ws.cell(row=row, column=2, value=f"ODX-{layer_type}")
        ws.cell(row=row, column=3, value=desc)
        row += 1


def build_base_variant_sheet(wb, base_variants):
    ws = wb.create_sheet("Base Variant Definition")
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 25
    ws.column_dimensions["D"].width = 40

    row = 1
    style_title(ws, row, 4, "Base Variant Definition")
    row += 2

    style_header(ws, row, ["Variant ID", "Variant Name", "ECU ID", "Interfaces"])
    row += 1

    for variant in base_variants:
        ws.cell(row=row, column=1, value=variant.get("id", ""))
        ws.cell(row=row, column=2, value=variant.get("name", ""))
        ws.cell(row=row, column=3, value=variant.get("ecu_id", ""))
        interfaces = variant.get("interfaces", [])
        iface_str = "; ".join([f['name'] for f in interfaces]) if interfaces else ""
        ws.cell(row=row, column=4, value=iface_str)
        row += 1


def build_derived_variants_sheet(wb, derived_variants, base_variants):
    ws = wb.create_sheet("Derived Variants")
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 25
    ws.column_dimensions["D"].width = 40

    row = 1
    style_title(ws, row, 4, "Derived Variants")
    row += 2

    style_header(ws, row, ["Variant ID", "Variant Name", "Parent Variant", "Specializations"])
    row += 1

    for variant in derived_variants:
        ws.cell(row=row, column=1, value=variant.get("id", ""))
        ws.cell(row=row, column=2, value=variant.get("name", ""))
        ws.cell(row=row, column=3, value=variant.get("parent_variant_id", ""))
        specs = variant.get("specializations", [])
        spec_str = "; ".join([f"{s['property']}={s['value']}" for s in specs]) if specs else ""
        ws.cell(row=row, column=4, value=spec_str)
        row += 1


def build_pdu_library_sheet(wb, pdu_library):
    ws = wb.create_sheet("PDU Library")
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 40

    row = 1
    style_title(ws, row, 5, "PDU Library Definition")
    row += 2

    style_header(ws, row, ["PDU ID", "PDU Name", "Length (bits)", "Multiplexing", "Signals"])
    row += 1

    for pdu in pdu_library:
        ws.cell(row=row, column=1, value=pdu.get("id", ""))
        ws.cell(row=row, column=2, value=pdu.get("name", ""))
        ws.cell(row=row, column=3, value=pdu.get("length", ""))
        ws.cell(row=row, column=4, value=pdu.get("multiplexing", "None"))
        signals = pdu.get("signals", [])
        signal_str = "; ".join([f"{s['name']}({s['position']},{s['length']})" for s in signals]) if signals else ""
        ws.cell(row=row, column=5, value=signal_str)
        row += 1


def build_diag_layer_containers_sheet(wb, services):
    ws = wb.create_sheet("Diag Layer Containers")
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 40

    row = 1
    style_title(ws, row, 3, "Diagnostic Layer Containers")
    row += 2

    style_header(ws, row, ["Service ID", "Service Name", "Description"])
    row += 1

    for svc in services[:10]:
        ws.cell(row=row, column=1, value=svc.get("id", ""))
        ws.cell(row=row, column=2, value=svc.get("name", ""))
        ws.cell(row=row, column=3, value=svc.get("id", ""))
        row += 1


def build_service_definitions_sheet(wb, services):
    ws = wb.create_sheet("Service Definitions (ODX-D)")
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 40

    row = 1
    style_title(ws, row, 5, "Service Definitions (ODX-D Layer)")
    row += 2

    style_header(ws, row, ["Service ID", "Service Name", "Request PDU", "Response PDU", "Parameters"])
    row += 1

    for svc in services:
        ws.cell(row=row, column=1, value=svc.get("id", ""))
        ws.cell(row=row, column=2, value=svc.get("name", ""))
        ws.cell(row=row, column=3, value=svc.get("request_pdu_id", ""))
        ws.cell(row=row, column=4, value=svc.get("response_pdu_id", ""))
        params = svc.get("parameters", [])
        param_str = "; ".join([f"{p['name']}({p['type']})" for p in params]) if params else ""
        ws.cell(row=row, column=5, value=param_str)
        row += 1


def build_communication_parameters_sheet(wb, base_variants):
    ws = wb.create_sheet("Communication Parameters (ODX-C)")
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40

    row = 1
    style_title(ws, row, 2, "Communication Parameters (ODX-C Layer)")
    row += 2

    style_header(ws, row, ["Parameter", "Value"])
    row += 1

    params = [
        ("Protocol", "CAN / LIN / Ethernet"),
        ("Bus Speed", "500 kbit/s (CAN) / 19.2 kbaud (LIN)"),
        ("Timeout", "1000 ms"),
        ("Retry Count", "3"),
        ("Flow Control", "CTS / WAIT"),
    ]

    for param, value in params:
        ws.cell(row=row, column=1, value=param).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1


def build_vehicle_information_sheet(wb, base_variants):
    ws = wb.create_sheet("Vehicle Information (ODX-V)")
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40

    row = 1
    style_title(ws, row, 2, "Vehicle Information (ODX-V Layer)")
    row += 2

    style_header(ws, row, ["Vehicle Element", "Value"])
    row += 1

    vehicle_info = [
        ("Vehicle Type", "Automotive (Car/Truck/Bus)"),
        ("OBD Standard", "ISO 15765 / SAE J1979"),
        ("Vehicle Network Topology", "See variant mapping"),
        ("System Voltage", "12V / 24V / 48V"),
    ]

    for elem, value in vehicle_info:
        ws.cell(row=row, column=1, value=elem).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1


def build_flash_data_sheet(wb, odx_layers):
    ws = wb.create_sheet("Flash Data (ODX-FD)")
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 40

    row = 1
    style_title(ws, row, 2, "Flash Data Configuration (ODX-FD Layer)")
    row += 2

    style_header(ws, row, ["Flash Parameter", "Value"])
    row += 1

    flash_params = [
        ("Flash Memory Type", "Flash / EEPROM / NOR / NAND"),
        ("Memory Segments", "Boot / Appl / Calib / NvData"),
        ("Programming Protocol", "ODX FlashData spec"),
        ("CRC Algorithm", "CRC-32 / CRC-16"),
    ]

    for param, value in flash_params:
        ws.cell(row=row, column=1, value=param).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1


def build_inherit_from_relationships_sheet(wb, derived_variants):
    ws = wb.create_sheet("Inherit-From Relationships")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 50

    row = 1
    style_title(ws, row, 3, "Inherit-From Relationships (Variant Hierarchy)")
    row += 2

    style_header(ws, row, ["Child Variant", "Parent Variant", "Override Properties"])
    row += 1

    for variant in derived_variants:
        ws.cell(row=row, column=1, value=variant.get("id", ""))
        ws.cell(row=row, column=2, value=variant.get("parent_variant_id", ""))
        specs = variant.get("specializations", [])
        spec_str = "; ".join([f"{s['property']}={s['value']}" for s in specs]) if specs else "None"
        ws.cell(row=row, column=3, value=spec_str)
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
        ("ISO 22901-1:2019", "ODX - Data Exchange Format (Part 1: Specification)"),
        ("ISO 22900-1:2021", "MVCI - Modular Vehicle Communication Interface"),
        ("ISO 14229-1:2020", "UDS - Unified Diagnostic Services"),
        ("ISO 15765", "Diagnostic communication over CAN"),
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
    odx_layers = data.get("odx_layers", [])
    base_variants = data.get("base_variants", [])
    derived_variants = data.get("derived_variants", [])
    pdu_library = data.get("pdu_library", [])
    services = data.get("services", [])
    dtcs = data.get("dtcs", [])
    data_objects = data.get("data_objects", [])

    wb = Workbook()
    build_title_sheet(wb, item_data)
    build_document_control_sheet(wb, item_data)
    build_odx_layer_hierarchy_sheet(wb, odx_layers)
    build_base_variant_sheet(wb, base_variants)
    build_derived_variants_sheet(wb, derived_variants, base_variants)
    build_pdu_library_sheet(wb, pdu_library)
    build_diag_layer_containers_sheet(wb, services)
    build_service_definitions_sheet(wb, services)
    build_communication_parameters_sheet(wb, base_variants)
    build_vehicle_information_sheet(wb, base_variants)
    build_flash_data_sheet(wb, odx_layers)
    build_inherit_from_relationships_sheet(wb, derived_variants)
    build_references_sheet(wb, item_data)

    wb.save(output_file)
    print(f"ODX workbook written to {output_file}")


if __name__ == "__main__":
    main()
