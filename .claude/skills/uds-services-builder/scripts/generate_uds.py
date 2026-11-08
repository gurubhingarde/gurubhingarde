"""
UDS Services Builder — generates a multi-tab ISO 14229-1 UDS service catalog from JSON.

Usage:
    python generate_uds.py <input.json> <output.xlsx>

Input JSON schema (see examples/sample_input.json for a full example):
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "ecu_identity": {logical_address, physical_address, functional_address, hw_part_number},
  "session_definitions": [{type: default|programming|extended, access_level, timeout_ms}],
  "service_inventory": [{service_id: 0xNN, name, sub_functions: [...], session_restrictions: [...]}],
  "did_catalog": [{id, name, data_type, length_bytes, read_security, write_security, session_restrictions: [...]}],
  "rid_catalog": [{id, name, routine_type, execution_time_ms, security_level}],
  "security_access": [{level, name, seed_length, key_length, algorithm}],
  "negative_response_codes": [{code, name, trigger_condition}],
  "timing_parameters": {P2_ms, P2_star_ms, S3_ms},
  "memory_programming_layout": {start_address, size_bytes, erase_block_size}
}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# =========================================================================
# Styling Constants
# =========================================================================

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def title_font(size: int = 16) -> Font:
    return Font(name=FONT_NAME, size=size, bold=True, color="FFFFFF")


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def style_title(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = title_font()
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header(ws, row, headers):
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = header_font()
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 36


def autosize(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = w


# =========================================================================
# Sheet Builders
# =========================================================================

def build_title(wb, item_dict):
    ws = wb.create_sheet("Title", 0)
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 6, "UDS Diagnostic Services Catalog")
    style_title(ws, 3, 6, item_dict.get("name", "ECU Name"))

    fields = [
        ("Project", item_dict.get("project", "")),
        ("Document ID", item_dict.get("doc_id", "")),
        ("ECU Abbreviation", item_dict.get("abbr", "")),
        ("Revision", item_dict.get("revision", "")),
        ("Date", item_dict.get("date", "")),
        ("Author", item_dict.get("author", "")),
        ("Approver", item_dict.get("approver", "")),
        ("Company", item_dict.get("company", "")),
        ("Standard", "ISO 14229-1:2020 UDS"),
        ("Workbook Generated", datetime.now().isoformat()),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True)
        ws.cell(row=row, column=3, value=value).font = body_font()
        row += 1

    autosize(ws, {1: 4, 2: 28, 3: 50, 4: 4, 5: 4, 6: 4})


def build_document_control(wb, item_dict):
    ws = wb.create_sheet("Document Control")
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 6, "Document Control")
    style_header(ws, 4, ["Revision", "Date", "Author", "Change Description", "Status"])

    row = 5
    ws.cell(row=row, column=1, value=item_dict.get("revision", "1.0")).font = body_font()
    ws.cell(row=row, column=2, value=item_dict.get("date", "")).font = body_font()
    ws.cell(row=row, column=3, value=item_dict.get("author", "")).font = body_font()
    ws.cell(row=row, column=4, value="Initial release").font = body_font()
    ws.cell(row=row, column=5, value="Released").font = body_font()
    for col in range(1, 6):
        ws.cell(row=row, column=col).border = BORDER_ALL

    autosize(ws, {1: 14, 2: 14, 3: 18, 4: 35, 5: 14})


def build_ecu_identity(wb, identity_dict):
    ws = wb.create_sheet("ECU Diagnostic Identity")
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 6, "ECU Diagnostic Identity")

    rows_data = [
        ("ECU Logical Address", identity_dict.get("logical_address", "")),
        ("ECU Physical Address", identity_dict.get("physical_address", "")),
        ("ECU Functional Address", identity_dict.get("functional_address", "")),
        ("HW Part Number", identity_dict.get("hw_part_number", "")),
    ]

    row = 4
    for label, value in rows_data:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=value).font = body_font()
        row += 1

    autosize(ws, {1: 28, 2: 30})


def build_session_definitions(wb, sessions_list):
    ws = wb.create_sheet("Session Definitions")

    style_header(ws, 1, ["Session Type", "Access Level", "Timeout (ms)", "Security Required", "Description"])

    for i, sess in enumerate(sessions_list or [], start=2):
        ws.cell(row=i, column=1, value=sess.get("type", "")).font = body_font()
        ws.cell(row=i, column=2, value=sess.get("access_level", "")).font = body_font()
        ws.cell(row=i, column=3, value=sess.get("timeout_ms", "")).font = body_font()
        ws.cell(row=i, column=4, value=sess.get("security_required", "N")).font = body_font()
        ws.cell(row=i, column=5, value=sess.get("description", "")).font = body_font()
        for col in range(1, 6):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 16, 2: 16, 3: 14, 4: 16, 5: 35})


def build_service_inventory(wb, services_list):
    ws = wb.create_sheet("Service Inventory")

    style_header(ws, 1, ["Service ID", "Service Name", "Sub-Functions", "Session Restrictions", "Security Required"])

    services = [
        ("0x10", "DiagnosticSessionControl", "00,01,02,03", "", ""),
        ("0x11", "ECUReset", "00,01,02,03", "", ""),
        ("0x14", "ClearDiagnosticInformation", "", "", ""),
        ("0x19", "ReadDTCInformation", "00-19", "", ""),
        ("0x22", "ReadDataByIdentifier", "", "", ""),
        ("0x27", "SecurityAccess", "", "Programming", "Y"),
        ("0x2E", "WriteDataByIdentifier", "", "", "Y"),
        ("0x31", "RoutineControl", "01,02,03", "", "Y"),
        ("0x34", "RequestDownload", "", "Programming", "Y"),
        ("0x36", "TransferData", "", "Programming", "Y"),
        ("0x37", "RequestTransferExit", "", "Programming", "Y"),
        ("0x3D", "WriteMemoryByAddress", "", "Programming", "Y"),
        ("0x85", "ControlDTCSetting", "01,02", "", ""),
    ]

    for i, (sid, name, subfuncs, sess_restrict, sec_req) in enumerate(services, start=2):
        # Merge with provided data if available
        svc_data = next((s for s in services_list or [] if s.get("service_id") == sid), {})

        ws.cell(row=i, column=1, value=sid).font = body_font()
        ws.cell(row=i, column=2, value=svc_data.get("name", name)).font = body_font()
        ws.cell(row=i, column=3, value=svc_data.get("sub_functions", subfuncs)).font = body_font()
        ws.cell(row=i, column=4, value=svc_data.get("session_restrictions", sess_restrict)).font = body_font()
        ws.cell(row=i, column=5, value=svc_data.get("security_required", sec_req)).font = body_font()
        for col in range(1, 6):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 12, 2: 28, 3: 20, 4: 24, 5: 18})


def build_did_catalog(wb, did_list):
    ws = wb.create_sheet("DID Catalog")

    style_header(ws, 1, ["DID ID", "DID Name", "Data Type", "Length (bytes)", "Read Security", "Write Security", "Session Restrictions"])

    for i, did in enumerate(did_list or [], start=2):
        ws.cell(row=i, column=1, value=did.get("id", "")).font = body_font()
        ws.cell(row=i, column=2, value=did.get("name", "")).font = body_font()
        ws.cell(row=i, column=3, value=did.get("data_type", "")).font = body_font()
        ws.cell(row=i, column=4, value=did.get("length_bytes", "")).font = body_font()
        ws.cell(row=i, column=5, value=did.get("read_security", "")).font = body_font()
        ws.cell(row=i, column=6, value=did.get("write_security", "")).font = body_font()
        ws.cell(row=i, column=7, value=", ".join(did.get("session_restrictions", []))).font = body_font()
        for col in range(1, 8):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 10, 2: 20, 3: 14, 4: 14, 5: 14, 6: 14, 7: 24})


def build_rid_catalog(wb, rid_list):
    ws = wb.create_sheet("RID Catalog")

    style_header(ws, 1, ["RID ID", "Routine Name", "Routine Type", "Execution Time (ms)", "Security Level"])

    for i, rid in enumerate(rid_list or [], start=2):
        ws.cell(row=i, column=1, value=rid.get("id", "")).font = body_font()
        ws.cell(row=i, column=2, value=rid.get("name", "")).font = body_font()
        ws.cell(row=i, column=3, value=rid.get("routine_type", "")).font = body_font()
        ws.cell(row=i, column=4, value=rid.get("execution_time_ms", "")).font = body_font()
        ws.cell(row=i, column=5, value=rid.get("security_level", "")).font = body_font()
        for col in range(1, 6):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 10, 2: 22, 3: 16, 4: 18, 5: 14})


def build_security_access(wb, security_list):
    ws = wb.create_sheet("Security Access Configuration")

    style_header(ws, 1, ["Level", "Level Name", "Seed Length", "Key Length", "Algorithm"])

    for i, sec in enumerate(security_list or [], start=2):
        ws.cell(row=i, column=1, value=sec.get("level", "")).font = body_font()
        ws.cell(row=i, column=2, value=sec.get("name", "")).font = body_font()
        ws.cell(row=i, column=3, value=sec.get("seed_length", "")).font = body_font()
        ws.cell(row=i, column=4, value=sec.get("key_length", "")).font = body_font()
        ws.cell(row=i, column=5, value=sec.get("algorithm", "")).font = body_font()
        for col in range(1, 6):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 8, 2: 18, 3: 14, 4: 12, 5: 20})


def build_negative_response_codes(wb, nrc_list):
    ws = wb.create_sheet("Negative Response Codes")

    style_header(ws, 1, ["NRC Code", "Name", "Service", "Trigger Condition"])

    nrc_defaults = [
        ("0x10", "generalReject", "", "General reject"),
        ("0x11", "serviceNotSupported", "", "Service not supported"),
        ("0x12", "subFunctionNotSupported", "", "Sub-function not supported"),
        ("0x13", "incorrectLengthOrFormat", "", "Incorrect data format"),
        ("0x14", "responseToolongOrFormatIncorrect", "", "Response too long"),
        ("0x22", "conditionsNotCorrect", "", "Conditions not met"),
        ("0x24", "requestSequenceError", "", "Sequence error"),
        ("0x31", "requestOutOfRange", "", "Out of range"),
        ("0x33", "securityAccessDenied", "", "Security access denied"),
        ("0x37", "lengthSecurityAccessCounterExceeded", "", "Failed attempts exceeded"),
    ]

    for i, (code, name, service, trigger) in enumerate(nrc_defaults, start=2):
        nrc_data = next((n for n in nrc_list or [] if n.get("code") == code), {})

        ws.cell(row=i, column=1, value=code).font = body_font()
        ws.cell(row=i, column=2, value=nrc_data.get("name", name)).font = body_font()
        ws.cell(row=i, column=3, value=nrc_data.get("service", service)).font = body_font()
        ws.cell(row=i, column=4, value=nrc_data.get("trigger_condition", trigger)).font = body_font()
        for col in range(1, 5):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 10, 2: 20, 3: 16, 4: 35})


def build_timing_parameters(wb, timing_dict):
    ws = wb.create_sheet("Timing Parameters")
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 4, "UDS Timing Parameters")

    timing_rows = [
        ("P2 Timeout (ms)", timing_dict.get("P2_ms", "50-5000")),
        ("P2* Extended Timeout (ms)", timing_dict.get("P2_star_ms", "5000-10000")),
        ("S3 Session Timeout (ms)", timing_dict.get("S3_ms", "0-32000")),
        ("P3* Client Timeout (ms)", timing_dict.get("P3_star_ms", "0-1000")),
    ]

    row = 4
    for label, value in timing_rows:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=value).font = body_font()
        row += 1

    autosize(ws, {1: 28, 2: 20})


def build_memory_programming(wb, memory_dict):
    ws = wb.create_sheet("Memory Programming Layout")
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 4, "Memory Programming Layout")

    memory_rows = [
        ("Flash Start Address", memory_dict.get("start_address", "")),
        ("Total Flash Size (bytes)", memory_dict.get("size_bytes", "")),
        ("Erase Block Size (bytes)", memory_dict.get("erase_block_size", "")),
        ("Programming Granularity (bytes)", memory_dict.get("programming_granularity", "")),
    ]

    row = 4
    for label, value in memory_rows:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=value).font = body_font()
        row += 1

    autosize(ws, {1: 28, 2: 20})


def build_validation_rules(wb):
    ws = wb.create_sheet("Validation Rules")

    style_header(ws, 1, ["Field", "Rule", "Min", "Max", "Notes"])

    rules = [
        ("DID ID", "Unique per ECU", "0x0000", "0xFFFF", ""),
        ("RID ID", "Unique per ECU", "0x00", "0xFF", ""),
        ("Security Level", "Sequential", "0x00", "0x0F", "Even = request, Odd = response"),
        ("P2 Timeout", "Positive integer", "50", "5000", "milliseconds"),
        ("P2* Timeout", "Positive integer", "5000", "10000", "milliseconds"),
        ("DID Length", "Positive integer", "1", "65535", "bytes"),
    ]

    for i, (field, rule, min_val, max_val, notes) in enumerate(rules, start=2):
        ws.cell(row=i, column=1, value=field).font = body_font()
        ws.cell(row=i, column=2, value=rule).font = body_font()
        ws.cell(row=i, column=3, value=min_val).font = body_font()
        ws.cell(row=i, column=4, value=max_val).font = body_font()
        ws.cell(row=i, column=5, value=notes).font = body_font()
        for col in range(1, 6):
            ws.cell(row=i, column=col).border = BORDER_ALL
            if i % 2 == 0:
                ws.cell(row=i, column=col).fill = PatternFill("solid", fgColor=ALT_ROW)

    autosize(ws, {1: 18, 2: 25, 3: 12, 4: 12, 5: 30})


def build_references(wb):
    ws = wb.create_sheet("References")
    ws.sheet_view.showGridLines = False

    style_title(ws, 2, 4, "References and Service Index")

    row = 4
    refs = [
        ("ISO 14229-1:2020", "Road Vehicles — Unified Diagnostic Services", "www.iso.org"),
        ("Service 0x10", "DiagnosticSessionControl", "Establish diagnostic session"),
        ("Service 0x27", "SecurityAccess", "Unlock protected services"),
        ("Service 0x22", "ReadDataByIdentifier", "Read DID values"),
        ("Service 0x2E", "WriteDataByIdentifier", "Write DID values"),
    ]

    for label, desc, url in refs:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=desc).font = body_font()
        ws.cell(row=row, column=3, value=url).font = body_font()
        row += 1

    autosize(ws, {1: 18, 2: 35, 3: 30})


# =========================================================================
# Main
# =========================================================================

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_uds.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: Input file {input_file} not found.")
        sys.exit(1)

    with open(input_file) as f:
        data = json.load(f)

    wb = Workbook()
    if wb.sheetnames and wb.sheetnames[0] == "Sheet":
        wb.remove(wb.active)

    item_dict = data.get("item", {})
    build_title(wb, item_dict)
    build_document_control(wb, item_dict)
    build_ecu_identity(wb, data.get("ecu_identity", {}))
    build_session_definitions(wb, data.get("session_definitions", []))
    build_service_inventory(wb, data.get("service_inventory", []))
    build_did_catalog(wb, data.get("did_catalog", []))
    build_rid_catalog(wb, data.get("rid_catalog", []))
    build_security_access(wb, data.get("security_access", []))
    build_negative_response_codes(wb, data.get("negative_response_codes", []))
    build_timing_parameters(wb, data.get("timing_parameters", {}))
    build_memory_programming(wb, data.get("memory_programming_layout", {}))
    build_validation_rules(wb)
    build_references(wb)

    wb.save(output_file)
    print(f"UDS service catalog generated: {output_file}")


if __name__ == "__main__":
    main()
