"""
DIA Builder — generates a multi-tab ISO 26262-8 §5 Development Interface Agreement workbook from a JSON input.

Usage:
    python generate_dia.py <input.json> <output.xlsx>

Input JSON schema (see examples/sample_dia_esc.json for a full example):
{
  "dia": {doc_id, revision, date, item_name, item_def_reference, contract_reference},
  "parties": [{id, organization, role, primary_contact, fusa_contact, address}],
  "scope_in": ["..."], "scope_out": ["..."],
  "communication_channels": [{channel, cadence, format, owner, attendees, escalation}],
  "joint_reviews": [{name, work_products, planned_date, attendees, format}],
  "supplier_deliverables": [{name, from_party, format, language, planned_date, acceptance_criteria}],
  "raci_overrides": [{wp_id, party_id, raci}]
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
# Reference data
# ---------------------------------------------------------------------------

WORK_PRODUCTS = [
    {"wp_id": "WP01", "name": "HARA", "iso_ref": "26262-3:7.4"},
    {"wp_id": "WP02", "name": "Item Definition", "iso_ref": "26262-3:7.5"},
    {"wp_id": "WP03", "name": "FSC", "iso_ref": "26262-4:8.4"},
    {"wp_id": "WP04", "name": "TSC", "iso_ref": "26262-5:8.4"},
    {"wp_id": "WP05", "name": "HW Safety Reqs", "iso_ref": "26262-5:8.2"},
    {"wp_id": "WP06", "name": "HW Architecture", "iso_ref": "26262-5:9"},
    {"wp_id": "WP07", "name": "HSI", "iso_ref": "26262-5:10"},
    {"wp_id": "WP08", "name": "FMEDA", "iso_ref": "26262-5:12"},
    {"wp_id": "WP09", "name": "SW Safety Reqs", "iso_ref": "26262-6:8.2"},
    {"wp_id": "WP10", "name": "SW Arch/Unit/Test", "iso_ref": "26262-6:9-11"},
    {"wp_id": "WP11", "name": "Safety Plan", "iso_ref": "26262-2:8.3"},
    {"wp_id": "WP12", "name": "Safety Case", "iso_ref": "26262-2:11"},
]

# Default RACI per OEM/Tier1/IC split
DEFAULT_RACI = {
    "WP01": {"OEM": "A,R", "Tier-1": "C", "IC": "I"},
    "WP02": {"OEM": "A,R", "Tier-1": "C", "IC": "I"},
    "WP03": {"OEM": "A", "Tier-1": "R", "IC": "C"},
    "WP04": {"OEM": "A", "Tier-1": "R", "IC": "C"},
    "WP05": {"OEM": "I", "Tier-1": "A,R", "IC": "C"},
    "WP06": {"OEM": "I", "Tier-1": "A,R", "IC": "C"},
    "WP07": {"OEM": "I", "Tier-1": "A,R", "IC": "C"},
    "WP08": {"OEM": "I", "Tier-1": "A,R", "IC": "R"},
    "WP09": {"OEM": "I", "Tier-1": "A,R", "IC": "—"},
    "WP10": {"OEM": "I", "Tier-1": "A,R", "IC": "—"},
    "WP11": {"OEM": "A", "Tier-1": "A", "IC": "C"},
    "WP12": {"OEM": "A,R", "Tier-1": "R", "IC": "R"},
}


# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"

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


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, dia: dict, parties: list[dict]) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 2, 4, "Development Interface Agreement (DIA)")
    style_title_row(ws, 3, 4, f"ISO 26262-8 Section 5")

    fields = [
        ("Item", dia.get("item_name", "")),
        ("Item Definition Reference", dia.get("item_def_reference", "")),
        ("Contract Reference", dia.get("contract_reference", "")),
        ("Document ID", dia.get("doc_id", "")),
        ("Revision", dia.get("revision", "")),
        ("Date", dia.get("date", "")),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left")
        row += 1

    row += 1
    ws.cell(row=row, column=2, value="Signatory Parties").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    row += 1

    for party in parties:
        sig_line = f"{party.get('organization', '')} ({party.get('role', '')})"
        ws.cell(row=row, column=2, value=sig_line).font = body_font()
        ws.cell(row=row, column=3, value="Date: _____________  Signature: _________________________").font = body_font()
        row += 1

    autosize(ws, {1: 4, 2: 28, 3: 60, 4: 4})


def build_document_control(wb: Workbook) -> None:
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 5, "Document Control")

    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of change", "Approver"])
    placeholders = [
        ("0.1", "", "", "Initial draft generated by dia-builder skill", ""),
        ("0.2", "", "", "Stakeholder review and refinement", ""),
        ("1.0", "", "", "Released for contract execution", ""),
    ]
    for i, row_data in enumerate(placeholders, start=4):
        for col, val in enumerate(row_data, start=1):
            ws.cell(row=i, column=col, value=val)
    stripe_body(ws, 4, 4 + len(placeholders) - 1, 5)
    autosize(ws, {1: 12, 2: 12, 3: 20, 4: 40, 5: 20})


def build_parties(wb: Workbook, parties: list[dict]) -> None:
    ws = wb.create_sheet("02_Parties")

    style_title_row(ws, 1, 6, "Party Information")

    headers = ["Party ID", "Organization", "Role", "Primary Contact", "FuSa Contact", "Address"]
    style_header_row(ws, 3, headers)

    for i, party in enumerate(parties, start=4):
        ws.cell(row=i, column=1, value=party.get("id", ""))
        ws.cell(row=i, column=2, value=party.get("organization", ""))
        ws.cell(row=i, column=3, value=party.get("role", ""))
        ws.cell(row=i, column=4, value=party.get("primary_contact", ""))
        ws.cell(row=i, column=5, value=party.get("fusa_contact", ""))
        ws.cell(row=i, column=6, value=party.get("address", ""))

    stripe_body(ws, 4, 4 + len(parties) - 1, 6)
    autosize(ws, {1: 12, 2: 24, 3: 12, 4: 20, 5: 20, 6: 30})


def build_item_scope(wb: Workbook, scope_in: list[str], scope_out: list[str]) -> None:
    ws = wb.create_sheet("03_Item_Scope")

    style_title_row(ws, 1, 2, "Item Scope Definition")

    ws.cell(row=3, column=1, value="In Scope").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    for i, item in enumerate(scope_in, start=4):
        ws.cell(row=i, column=1, value=f"• {item}")
        ws.cell(row=i, column=1).alignment = Alignment(wrap_text=True)

    row = 4 + len(scope_in) + 1
    ws.cell(row=row, column=1, value="Out of Scope").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    for i, item in enumerate(scope_out, start=row + 1):
        ws.cell(row=i, column=1, value=f"• {item}")
        ws.cell(row=i, column=1).alignment = Alignment(wrap_text=True)

    autosize(ws, {1: 80})


def build_raci_matrix(wb: Workbook, parties: list[dict], raci_overrides: dict[str, dict[str, str]]) -> None:
    ws = wb.create_sheet("04_RACI_Matrix")

    style_title_row(ws, 1, 2 + len(parties), "RACI Matrix — Work Product Responsibility")

    headers = ["WP_ID", "Work Product", "ISO Ref"] + [p["organization"] for p in parties]
    style_header_row(ws, 3, headers)

    party_id_map = {p["id"]: p for p in parties}

    for i, wp in enumerate(WORK_PRODUCTS, start=4):
        ws.cell(row=i, column=1, value=wp["wp_id"])
        ws.cell(row=i, column=2, value=wp["name"])
        ws.cell(row=i, column=3, value=wp["iso_ref"])

        for col_idx, party in enumerate(parties, start=4):
            party_id = party["id"]
            default_val = DEFAULT_RACI.get(wp["wp_id"], {}).get(party["role"], "—")
            overrides = raci_overrides.get(wp["wp_id"], {})
            cell_val = overrides.get(party_id, default_val)

            ws.cell(row=i, column=col_idx, value=cell_val)
            ws.cell(row=i, column=col_idx).alignment = Alignment(horizontal="center", vertical="center")

    stripe_body(ws, 4, 4 + len(WORK_PRODUCTS) - 1, 2 + len(parties))
    autosize(ws, {1: 10, 2: 20, 3: 18, **{3 + i + 1: 18 for i in range(len(parties))}})


def build_communication_protocol(wb: Workbook, channels: list[dict]) -> None:
    ws = wb.create_sheet("05_Communication_Protocol")

    style_title_row(ws, 1, 6, "Communication Protocol")

    headers = ["Channel", "Cadence", "Format", "Owner", "Attendees", "Escalation Path"]
    style_header_row(ws, 3, headers)

    for i, ch in enumerate(channels, start=4):
        ws.cell(row=i, column=1, value=ch.get("channel", ""))
        ws.cell(row=i, column=2, value=ch.get("cadence", ""))
        ws.cell(row=i, column=3, value=ch.get("format", ""))
        ws.cell(row=i, column=4, value=ch.get("owner", ""))
        ws.cell(row=i, column=5, value=ch.get("attendees", ""))
        ws.cell(row=i, column=6, value=ch.get("escalation", ""))

    stripe_body(ws, 4, 4 + len(channels) - 1, 6)
    autosize(ws, {1: 20, 2: 15, 3: 15, 4: 18, 5: 30, 6: 30})


def build_joint_reviews(wb: Workbook, reviews: list[dict]) -> None:
    ws = wb.create_sheet("06_Joint_Reviews")

    style_title_row(ws, 1, 6, "Joint Review Schedule")

    headers = ["Review Name", "Work Products", "Planned Date", "Attendees", "Format", "Status"]
    style_header_row(ws, 3, headers)

    for i, review in enumerate(reviews, start=4):
        ws.cell(row=i, column=1, value=review.get("name", ""))
        wp_list = ", ".join(review.get("work_products", []))
        ws.cell(row=i, column=2, value=wp_list)
        ws.cell(row=i, column=3, value=review.get("planned_date", ""))
        ws.cell(row=i, column=4, value=review.get("attendees", ""))
        ws.cell(row=i, column=5, value=review.get("format", ""))
        ws.cell(row=i, column=6, value="Pending")

    stripe_body(ws, 4, 4 + len(reviews) - 1, 6)
    autosize(ws, {1: 25, 2: 30, 3: 15, 4: 25, 5: 15, 6: 12})


def build_supplier_deliverables(wb: Workbook, deliverables: list[dict]) -> None:
    ws = wb.create_sheet("07_Supplier_Deliverables")

    style_title_row(ws, 1, 7, "Supplier Deliverables")

    headers = ["Deliverable", "From Party", "Format", "Language", "Planned Date", "Acceptance Criteria", "Status"]
    style_header_row(ws, 3, headers)

    for i, deliv in enumerate(deliverables, start=4):
        ws.cell(row=i, column=1, value=deliv.get("name", ""))
        ws.cell(row=i, column=2, value=deliv.get("from_party", ""))
        ws.cell(row=i, column=3, value=deliv.get("format", ""))
        ws.cell(row=i, column=4, value=deliv.get("language", ""))
        ws.cell(row=i, column=5, value=deliv.get("planned_date", ""))
        ws.cell(row=i, column=6, value=deliv.get("acceptance_criteria", ""))
        ws.cell(row=i, column=7, value="Not yet delivered")

    stripe_body(ws, 4, 4 + len(deliverables) - 1, 7)
    autosize(ws, {1: 25, 2: 18, 3: 12, 4: 12, 5: 15, 6: 35, 7: 18})


def build_change_management(wb: Workbook) -> None:
    ws = wb.create_sheet("08_Change_Management")

    style_title_row(ws, 1, 7, "Change Management Process")

    ws.cell(row=3, column=1, value="Change Request Process").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    ws.cell(row=4, column=1, value="All changes to the DIA or work products require a Change Request (CR) form. CCB reviews based on impact scope.")

    ws.cell(row=6, column=1, value="Approval Thresholds").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    ws.cell(row=7, column=1, value="Cost / Schedule: Tier-1 lead; Safety impact: OEM + Tier-1 joint approval")

    ws.cell(row=9, column=1, value="Change Log").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)

    headers = ["CR ID", "Date", "Description", "Initiated By", "Impact", "Status", "Approved By"]
    style_header_row(ws, 10, headers)
    stripe_body(ws, 11, 20, 7)

    autosize(ws, {1: 18, 2: 12, 3: 30, 4: 16, 5: 15, 6: 15, 7: 18})


def build_tool_sharing(wb: Workbook) -> None:
    ws = wb.create_sheet("09_Tool_Sharing")

    style_title_row(ws, 1, 5, "Tool Sharing & Qualification")

    headers = ["Tool Name", "Owner", "Granted To", "License Terms", "Qualification Responsibility"]
    style_header_row(ws, 3, headers)

    # Placeholder rows
    for i in range(4, 14):
        ws.cell(row=i, column=1, value="")
        ws.cell(row=i, column=2, value="")
        ws.cell(row=i, column=3, value="")
        ws.cell(row=i, column=4, value="")
        ws.cell(row=i, column=5, value="")

    stripe_body(ws, 4, 13, 5)
    autosize(ws, {1: 25, 2: 18, 3: 25, 4: 30, 5: 30})


def build_confidentiality_ip(wb: Workbook) -> None:
    ws = wb.create_sheet("10_Confidentiality_IP")

    style_title_row(ws, 1, 2, "Confidentiality and IP Ownership")

    ws.cell(row=3, column=1, value="IP Ownership Rules").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    ws.cell(row=4, column=1, value="Pre-existing IP: Retained by contributing party")
    ws.cell(row=5, column=1, value="DIA work products: Co-owned by OEM and executing Tier-1; Tier-1 may assert residual knowledge")
    ws.cell(row=6, column=1, value="IC supplier assets: Owned by supplier; OEM receives license for item deployment only")

    ws.cell(row=8, column=1, value="Confidentiality Scope").font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
    ws.cell(row=9, column=1, value="All safety work products (HARA, FSC, TSC, test results, etc.) treated as confidential")
    ws.cell(row=10, column=1, value="Disclosure limited to: parties to this DIA, regulatory authorities, and OEM supply chain")
    ws.cell(row=11, column=1, value="No publication or third-party licensing without written consent of all parties")

    autosize(ws, {1: 80})


def build_references(wb: Workbook, dia: dict) -> None:
    ws = wb.create_sheet("11_References")

    style_title_row(ws, 1, 2, "References")

    refs = [
        ("Master Contract", dia.get("contract_reference", "[Reference commercial contract]")),
        ("Item Definition", dia.get("item_def_reference", "[Reference item definition document]")),
        ("ISO 26262:2018", "Road vehicles – Functional safety"),
        ("ISO 26262-2:2018", "Management of functional safety"),
        ("ISO 26262-8:2018", "Guidelines on ISO 26262"),
    ]

    row = 3
    for label, ref in refs:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=2, value=ref)
        row += 1

    autosize(ws, {1: 30, 2: 60})


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_dia(input_json: str, output_xlsx: str) -> None:
    with open(input_json, "r") as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    dia = data.get("dia", {})
    parties = data.get("parties", [])
    scope_in = data.get("scope_in", [])
    scope_out = data.get("scope_out", [])
    channels = data.get("communication_channels", [])
    reviews = data.get("joint_reviews", [])
    deliverables = data.get("supplier_deliverables", [])

    raci_overrides = {}
    for override in data.get("raci_overrides", []):
        wp_id = override.get("wp_id", "")
        party_id = override.get("party_id", "")
        raci = override.get("raci", "")
        if wp_id and party_id:
            if wp_id not in raci_overrides:
                raci_overrides[wp_id] = {}
            raci_overrides[wp_id][party_id] = raci

    # Build all tabs
    build_title_page(wb, dia, parties)
    build_document_control(wb)
    build_parties(wb, parties)
    build_item_scope(wb, scope_in, scope_out)
    build_raci_matrix(wb, parties, raci_overrides)
    build_communication_protocol(wb, channels)
    build_joint_reviews(wb, reviews)
    build_supplier_deliverables(wb, deliverables)
    build_change_management(wb)
    build_tool_sharing(wb)
    build_confidentiality_ip(wb)
    build_references(wb, dia)

    wb.save(output_xlsx)

    # Print summary
    summary = {
        "status": "success",
        "tabs": len(wb.sheetnames),
        "tab_names": wb.sheetnames,
        "parties": len(parties),
        "deliverables": len(deliverables),
    }
    print(json.dumps(summary, indent=2))


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_dia.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_json = sys.argv[1]
    output_xlsx = sys.argv[2]

    if not Path(input_json).exists():
        print(f"Error: Input file {input_json} not found", file=sys.stderr)
        sys.exit(1)

    generate_dia(input_json, output_xlsx)


if __name__ == "__main__":
    main()
