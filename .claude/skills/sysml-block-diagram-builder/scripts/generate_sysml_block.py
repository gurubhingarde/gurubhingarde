"""
SysML Block Definition Diagram (BDD) and Internal Block Diagram (IBD) builder.

Generates an 11-tab xlsx for authoring blocks, properties, parts, ports (flow/full/proxy),
connectors, item flows, and value type definitions per OMG SysML 1.6 and 2.0.

Usage:
    python generate_sysml_block.py <output.xlsx> --input <model.json> [--title "System Name"] [--author "Name"]

Input JSON schema (all keys optional; see SKILL.md and examples/sysml-block-diagram-builder/sample_input.json):
    {
      "system_name": "...", "author": "...", "version": "1.0",
      "model_header": {"purpose": "...", "viewpoint": "...", "scope": "...", "environment": "...",
                       "assumptions": "...", "tool": "..."},
      "blocks":      [{"name","stereotype","description","parent","multiplicity"}],
      "properties":  [{"block","name","type","multiplicity","description"}],
      "parts":       [{"owner","name","type","multiplicity","description"}],
      "ports":       [{"owner","name","port_type","flow_type","direction","description"}],
      "connectors":  [{"name","source","target","type","description"}],
      "item_flows":  [{"connector","item_type","multiplicity","direction","description"}],
      "value_types": [{"name","base_type","description","unit"}],
      "references":  [{"name","description"}]
    }
Without --input the catalog tabs are emitted with headers only (no placeholder rows).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
NAVY_BORDER = Side(border_style="thin", color=NAVY)
BORDER_ALL = Border(left=NAVY_BORDER, right=NAVY_BORDER, top=NAVY_BORDER, bottom=NAVY_BORDER)


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
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 24


def style_data(ws, row, values, alt=False):
    fill = PatternFill("solid", fgColor=ALT_ROW) if alt else PatternFill()
    for col, val in enumerate(values, start=1):
        cell = ws.cell(row=row, column=col, value=val)
        cell.font = Font(name=FONT_NAME, size=10)
        cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        cell.fill = fill
        cell.border = BORDER_ALL


def _g(d, *keys, default=""):
    """First present key from a dict (schema aliases), else default."""
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def write_rows(ws, rows, start=4):
    for i, row_data in enumerate(rows, start=start):
        style_data(ws, i, row_data, alt=(i % 2 == 0))


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_tab(wb, system_name="Unnamed System"):
    ws = wb.active
    ws.title = "0_Title"
    ws.column_dimensions["A"].width = 60

    style_title(ws, 1, 4, "SysML Block Definition Diagram (BDD) / Internal Block Diagram (IBD)")
    ws.cell(row=3, column=1, value="System Name").font = Font(bold=True)
    ws.cell(row=3, column=2, value=system_name)
    ws.cell(row=4, column=1, value="Created").font = Font(bold=True)
    ws.cell(row=4, column=2, value=str(date.today()))
    ws.cell(row=5, column=1, value="Standard").font = Font(bold=True)
    ws.cell(row=5, column=2, value="OMG SysML 1.6 / 2.0")
    ws.cell(row=7, column=1, value="Tabs").font = Font(bold=True, size=12)
    tabs = [
        "1_Document_Control - version, approvals",
        "2_Model_Header - context and scope",
        "3_Block_Catalog - all blocks with stereotypes",
        "4_Property_Catalog - block properties",
        "5_Part_Reference_Properties - parts and references",
        "6_Port_Catalog - flow, full, proxy ports",
        "7_Connector_Catalog - connector definitions",
        "8_Item_Flow_Catalog - item flows and interfaces",
        "9_Value_Type_Definitions - data types",
        "10_References - external model references"
    ]
    for i, tab in enumerate(tabs, start=8):
        ws.cell(row=i, column=2, value=tab)


def build_document_control_tab(wb, system_name="Unnamed System", author="", version="1.0"):
    ws = wb.create_sheet("1_Document_Control")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 40

    style_title(ws, 1, 4, "Document Control")
    style_header(ws, 3, ["Field", "Value", "Notes", "Status"])

    data = [
        ["System", system_name, "Block definition domain", ""],
        ["Version", version, "Initial release", "Draft"],
        ["Author", author or "To be assigned", "", ""],
        ["Reviewed By", "", "SysML SME review", "Pending"],
        ["Approved By", "", "Project lead", "Pending"],
        ["Classification", "Internal", "Access level", ""],
        ["Standard Compliance", "OMG SysML 1.6 / 2.0", "Well-formedness rules", ""],
    ]

    write_rows(ws, data)


def build_model_header_tab(wb, header=None, counts=""):
    header = header or {}
    ws = wb.create_sheet("2_Model_Header")
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 50

    style_title(ws, 1, 3, "Model Context and Scope")
    style_header(ws, 3, ["Property", "Value", "Description"])

    data = [
        ["Model Purpose", _g(header, "purpose", default="System structural definition"), "Define component hierarchy and interfaces"],
        ["Modeling Viewpoint", _g(header, "viewpoint", default="Structural/Compositional"), "Emphasizes blocks and their composition"],
        ["Scope Boundaries", _g(header, "scope", default="To be defined by user"), "Identify system extent and boundaries"],
        ["Environment", _g(header, "environment", default="To be defined by user"), "Context and external actors"],
        ["Key Assumptions", _g(header, "assumptions", default="To be defined by user"), "Design and analysis assumptions"],
        ["Modeling Tool", _g(header, "tool", default="Cameo / Rhapsody / Capella"), "Target import environment"],
        ["Model Element Count (est.)", counts, "Total blocks, ports, connectors"],
    ]

    write_rows(ws, data)


def build_block_catalog_tab(wb, blocks):
    ws = wb.create_sheet("3_Block_Catalog")
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 40
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 20

    style_title(ws, 1, 5, "Block Catalog")
    style_header(ws, 3, ["Block Name", "Stereotype", "Description", "Parent Block", "Multiplicity"])

    data = [[_g(b, "name"), _g(b, "stereotype", default="<<block>>"), _g(b, "description"),
             _g(b, "parent", "parent_block"), _g(b, "multiplicity", default="1")] for b in blocks]

    write_rows(ws, data)


def build_property_catalog_tab(wb, properties):
    ws = wb.create_sheet("4_Property_Catalog")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 30

    style_title(ws, 1, 5, "Property Catalog")
    style_header(ws, 3, ["Block Name", "Property Name", "Type", "Multiplicity", "Description"])

    data = [[_g(p, "block", "owner"), _g(p, "name"), _g(p, "type"), _g(p, "multiplicity", default="1"),
             _g(p, "description")] for p in properties]

    write_rows(ws, data)


def build_part_reference_tab(wb, parts):
    ws = wb.create_sheet("5_Part_Reference_Properties")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 30

    style_title(ws, 1, 5, "Part and Reference Properties")
    style_header(ws, 3, ["Owner Block", "Part Name", "Part Type", "Multiplicity", "Description"])

    data = [[_g(p, "owner", "block"), _g(p, "name"), _g(p, "type", "part_type"), _g(p, "multiplicity", default="1"),
             _g(p, "description")] for p in parts]

    write_rows(ws, data)


def build_port_catalog_tab(wb, ports):
    ws = wb.create_sheet("6_Port_Catalog")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 15
    ws.column_dimensions["F"].width = 30

    style_title(ws, 1, 6, "Port Catalog")
    style_header(ws, 3, ["Owner Block", "Port Name", "Port Type", "Flow Type", "Direction", "Description"])

    data = [[_g(p, "owner", "block"), _g(p, "name"), _g(p, "port_type", "type", default="FlowPort"),
             _g(p, "flow_type"), _g(p, "direction"), _g(p, "description")] for p in ports]

    write_rows(ws, data)


def build_connector_catalog_tab(wb, connectors):
    ws = wb.create_sheet("7_Connector_Catalog")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 30

    style_title(ws, 1, 5, "Connector Catalog")
    style_header(ws, 3, ["Connector Name", "Source Port", "Target Port", "Connector Type", "Description"])

    data = [[_g(c, "name"), _g(c, "source", "source_port"), _g(c, "target", "target_port"),
             _g(c, "type", "connector_type", default="ItemFlow"), _g(c, "description")] for c in connectors]

    write_rows(ws, data)


def build_item_flow_catalog_tab(wb, item_flows):
    ws = wb.create_sheet("8_Item_Flow_Catalog")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 20
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 30

    style_title(ws, 1, 5, "Item Flow Catalog")
    style_header(ws, 3, ["Connector Name", "Item Type", "Multiplicity", "Direction", "Description"])

    data = [[_g(f, "connector", "connector_name"), _g(f, "item_type", "type"), _g(f, "multiplicity", default="1"),
             _g(f, "direction", default="unidirectional"), _g(f, "description")] for f in item_flows]

    write_rows(ws, data)


def build_value_type_tab(wb, value_types):
    ws = wb.create_sheet("9_Value_Type_Definitions")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 40
    ws.column_dimensions["D"].width = 20

    style_title(ws, 1, 4, "Value Type and Interface Definitions")
    style_header(ws, 3, ["Type Name", "Base Type", "Description", "Unit"])

    data = [[_g(v, "name"), _g(v, "base_type", "type"), _g(v, "description"), _g(v, "unit")] for v in value_types]

    write_rows(ws, data)


def build_references_tab(wb, references=None):
    ws = wb.create_sheet("10_References")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 50

    style_title(ws, 1, 2, "References and External Models")
    style_header(ws, 3, ["Reference", "Description"])

    data = [
        ["OMG SysML 1.6 Specification", "https://www.omg.org/spec/SysML/1.6"],
        ["OMG SysML 2.0 Specification", "https://www.omg.org/spec/SysML/2.0"],
    ] + [[_g(r, "name", "reference"), _g(r, "description")] for r in (references or [])]

    write_rows(ws, data)


def load_input(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        sys.exit(f"ERROR: {path} must contain a JSON object at top level")
    return data


def main():
    parser = argparse.ArgumentParser(description="Generate SysML Block Diagram authoring workbook")
    parser.add_argument("output", nargs="?", default="sysml_block_diagram.xlsx")
    parser.add_argument("--input", "-i", default=None, help="JSON model description (see SKILL.md)")
    parser.add_argument("--title", default=None, help="System name (overrides input system_name)")
    parser.add_argument("--author", default=None, help="Author (overrides input author)")

    args = parser.parse_args()

    data = load_input(args.input) if args.input else {}
    if not args.input:
        print("WARNING: no --input given; catalog tabs will contain headers only", file=sys.stderr)

    system_name = args.title or data.get("system_name") or data.get("title") or "Unnamed System"
    author = args.author if args.author is not None else data.get("author", "")
    version = str(data.get("version", "1.0"))

    blocks = data.get("blocks", [])
    ports = data.get("ports", [])
    connectors = data.get("connectors", [])
    counts = f"{len(blocks)} blocks, {len(ports)} ports, {len(connectors)} connectors" if data else ""

    wb = Workbook()
    build_title_tab(wb, system_name)
    build_document_control_tab(wb, system_name, author, version)
    build_model_header_tab(wb, data.get("model_header", {}), counts)
    build_block_catalog_tab(wb, blocks)
    build_property_catalog_tab(wb, data.get("properties", []))
    build_part_reference_tab(wb, data.get("parts", []))
    build_port_catalog_tab(wb, ports)
    build_connector_catalog_tab(wb, connectors)
    build_item_flow_catalog_tab(wb, data.get("item_flows", []))
    build_value_type_tab(wb, data.get("value_types", []))
    build_references_tab(wb, data.get("references", []))

    wb.save(args.output)
    print(f"Block diagram workbook saved to {args.output}")


if __name__ == "__main__":
    main()
