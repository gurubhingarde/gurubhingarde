"""ODX Checklist Reviewer — orchestrator + xlsx writer with visual dashboard."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from check_definitions import CHECKS, CheckDef, CheckResult
from dashboard import build_dashboard


FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"
ORANGE_PARTIAL = "FFD966"
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


def build_title_sheet(wb):
    ws = wb.active
    ws.title = "Title"
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 60

    row = 1
    style_title(ws, row, 2, "ODX Checklist Review")
    row += 3

    ws.cell(row=row, column=1, value="Document").font = Font(bold=True)
    ws.cell(row=row, column=2, value="ODX Authoring Workbook")
    row += 1

    ws.cell(row=row, column=1, value="Review Date").font = Font(bold=True)
    ws.cell(row=row, column=2, value=str(date.today()))
    row += 1

    ws.cell(row=row, column=1, value="Standard").font = Font(bold=True)
    ws.cell(row=row, column=2, value="ISO 22901-1")


def build_general_info_sheet(wb):
    ws = wb.create_sheet("General Info")
    ws.column_dimensions["A"].width = 50
    ws.column_dimensions["B"].width = 20

    row = 1
    style_title(ws, row, 2, "Checklist Overview")
    row += 2

    ws.cell(row=row, column=1, value="Section").font = Font(bold=True)
    ws.cell(row=row, column=2, value="Checks").font = Font(bold=True)
    row += 1

    sections = [
        ("Variant & Layer Review", 8),
        ("PDU & Service Review", 12),
        ("Communication & Flash Review", 10),
    ]

    for section, count in sections:
        ws.cell(row=row, column=1, value=section)
        ws.cell(row=row, column=2, value=count)
        row += 1


def build_guide_sheet(wb):
    ws = wb.create_sheet("Guide")
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 60

    row = 1
    style_title(ws, row, 2, "Legend and Rating Scale")
    row += 2

    ws.cell(row=row, column=1, value="Rating").font = Font(bold=True)
    ws.cell(row=row, column=2, value="Meaning").font = Font(bold=True)
    row += 1

    ratings = [
        ("FC", "Fully Compliant - requirement met"),
        ("LC", "Largely Compliant - minor issues noted"),
        ("PC", "Partially Compliant - significant gaps"),
        ("NC", "Non-Compliant - requirement not met"),
        ("NA", "Not Applicable - not relevant to this ODX"),
    ]

    for rating, meaning in ratings:
        ws.cell(row=row, column=1, value=rating).font = Font(bold=True)
        ws.cell(row=row, column=2, value=meaning)
        row += 1

    row += 2
    ws.cell(row=row, column=1, value="Confidence").font = Font(bold=True)
    ws.cell(row=row, column=2, value="Meaning").font = Font(bold=True)
    row += 1

    confidence = [
        ("High", "Objectively verifiable (automated check)"),
        ("Medium", "Mostly verifiable with some judgment"),
        ("Low", "Requires expert review or interpretation"),
    ]

    for conf, meaning in confidence:
        ws.cell(row=row, column=1, value=conf).font = Font(bold=True)
        ws.cell(row=row, column=2, value=meaning)
        row += 1


def build_summary_sheet(wb, results: list[CheckResult]):
    ws = wb.create_sheet("Summary")
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 60

    row = 1
    style_title(ws, row, 3, "Review Summary and Dashboard")
    row += 2

    # KPI tiles
    rating_counts = Counter(r.rating for r in results)
    total = len(results)
    pass_count = rating_counts.get("FC", 0)
    warn_count = rating_counts.get("LC", 0) + rating_counts.get("PC", 0)
    fail_count = rating_counts.get("NC", 0)
    na_count = rating_counts.get("NA", 0)

    ws.cell(row=row, column=1, value="Checks Passed").font = Font(bold=True, size=12)
    ws.cell(row=row, column=2, value=pass_count).font = Font(size=12, bold=True, color="008000")
    row += 1

    ws.cell(row=row, column=1, value="Checks with Issues").font = Font(bold=True, size=12)
    ws.cell(row=row, column=2, value=warn_count).font = Font(size=12, bold=True, color="FF9900")
    row += 1

    ws.cell(row=row, column=1, value="Checks Failed").font = Font(bold=True, size=12)
    ws.cell(row=row, column=2, value=fail_count).font = Font(size=12, bold=True, color="FF0000")
    row += 1

    ws.cell(row=row, column=1, value="Not Applicable").font = Font(bold=True, size=12)
    ws.cell(row=row, column=2, value=na_count).font = Font(size=12, bold=True)
    row += 3

    # Findings table
    ws.cell(row=row, column=1, value="Check").font = Font(bold=True)
    ws.cell(row=row, column=2, value="Rating").font = Font(bold=True)
    ws.cell(row=row, column=3, value="Findings / Recommendation").font = Font(bold=True)
    row += 1

    for result in results:
        ws.cell(row=row, column=1, value=result.check_id)
        ws.cell(row=row, column=2, value=result.rating)
        ws.cell(row=row, column=3, value=result.finding or "")
        row += 1


def build_variant_review_sheet(wb, results: list[CheckResult]):
    ws = wb.create_sheet("Variant & Layer Review")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 50

    row = 1
    style_title(ws, row, 4, "Variant Definition and Layer Review")
    row += 2

    style_header(ws, row, ["Check ID", "Requirement", "Rating", "Notes"])
    row += 1

    variant_checks = [r for r in results if r.check_id.startswith("V")]
    for result in variant_checks:
        ws.cell(row=row, column=1, value=result.check_id)
        ws.cell(row=row, column=2, value=result.check_name or "")
        ws.cell(row=row, column=3, value=result.rating)
        ws.cell(row=row, column=4, value=result.finding or "")
        row += 1


def build_pdu_service_sheet(wb, results: list[CheckResult]):
    ws = wb.create_sheet("PDU & Service Review")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 50

    row = 1
    style_title(ws, row, 4, "PDU Library and Service Definition Review")
    row += 2

    style_header(ws, row, ["Check ID", "Requirement", "Rating", "Notes"])
    row += 1

    pdu_checks = [r for r in results if r.check_id.startswith("P")]
    for result in pdu_checks:
        ws.cell(row=row, column=1, value=result.check_id)
        ws.cell(row=row, column=2, value=result.check_name or "")
        ws.cell(row=row, column=3, value=result.rating)
        ws.cell(row=row, column=4, value=result.finding or "")
        row += 1


def build_comm_flash_sheet(wb, results: list[CheckResult]):
    ws = wb.create_sheet("Communication & Flash Review")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 50

    row = 1
    style_title(ws, row, 4, "Communication Parameters and Flash Data Review")
    row += 2

    style_header(ws, row, ["Check ID", "Requirement", "Rating", "Notes"])
    row += 1

    comm_checks = [r for r in results if r.check_id.startswith("C")]
    for result in comm_checks:
        ws.cell(row=row, column=1, value=result.check_id)
        ws.cell(row=row, column=2, value=result.check_name or "")
        ws.cell(row=row, column=3, value=result.rating)
        ws.cell(row=row, column=4, value=result.finding or "")
        row += 1


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <odx.xlsx> <output_checklist.xlsx>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    # Placeholder results (in a real implementation, probe the input ODX and run checks)
    results = [
        CheckResult("V1", "Base variant defined", "FC", "All base variants have ECU IDs", "High"),
        CheckResult("V2", "Derived variant inheritance", "FC", "All derived variants inherit from base", "High"),
        CheckResult("V3", "Circular inheritance check", "FC", "No circular dependencies detected", "High"),
        CheckResult("V4", "Layer hierarchy defined", "FC", "All four ODX layers specified", "Medium"),
        CheckResult("V5", "Variant naming consistency", "LC", "Some variant IDs lack standardized prefix", "Medium"),
        CheckResult("V6", "ODX-D coverage", "FC", "All services mapped to variants", "Medium"),
        CheckResult("V7", "ODX-C channel definition", "FC", "Communication channels specified", "Medium"),
        CheckResult("V8", "ODX-V topology", "FC", "Vehicle topology documented", "Low"),
        CheckResult("P1", "PDU library complete", "FC", "All referenced PDUs defined", "High"),
        CheckResult("P2", "Service-to-PDU mapping", "FC", "Every service has request/response PDU", "High"),
        CheckResult("P3", "Signal definitions", "LC", "Some signals lack unit conversions", "Medium"),
        CheckResult("P4", "DTC enumeration", "FC", "All DTCs listed with severity", "High"),
        CheckResult("P5", "Data object semantics", "PC", "3 data objects missing range limits", "Medium"),
        CheckResult("P6", "Parameter validation", "FC", "Input parameters validated", "Medium"),
        CheckResult("P7", "Service dependencies", "FC", "No orphaned services", "High"),
        CheckResult("P8", "Response mapping", "LC", "Some negative responses lack description", "Low"),
        CheckResult("P9", "PDU multiplexing", "FC", "Multiplexing rules consistent", "Medium"),
        CheckResult("P10", "Signal overlaps", "FC", "No signal bit overlaps in PDU", "High"),
        CheckResult("P11", "Safety indicators", "FC", "Safety-relevant services marked", "Medium"),
        CheckResult("P12", "Service versioning", "NA", "Not applicable; no legacy versions", "Low"),
        CheckResult("C1", "Bus speed defined", "FC", "CAN/LIN/Ethernet speed specified", "High"),
        CheckResult("C2", "Timing parameters", "LC", "Some timeouts lack justification", "Medium"),
        CheckResult("C3", "Flow control", "FC", "CTS/WAIT mechanisms defined", "Medium"),
        CheckResult("C4", "Protocol headers", "FC", "CAN frame IDs, LIN frame bytes specified", "High"),
        CheckResult("C5", "Memory segments", "FC", "Boot, App, Calib segments defined", "High"),
        CheckResult("C6", "Flash algorithm", "LC", "Programming sequence incomplete", "Medium"),
        CheckResult("C7", "CRC algorithm", "FC", "CRC-32 specified with polynomial", "High"),
        CheckResult("C8", "Security unlock", "PC", "Auth procedure missing details", "Low"),
        CheckResult("C9", "NV data layout", "FC", "Persistent data regions defined", "Medium"),
        CheckResult("C10", "Rollback strategy", "NA", "Not applicable; no rollback mechanism", "Low"),
    ]

    wb = Workbook()
    build_title_sheet(wb)
    build_general_info_sheet(wb)
    build_guide_sheet(wb)
    build_summary_sheet(wb, results)
    build_variant_review_sheet(wb, results)
    build_pdu_service_sheet(wb, results)
    build_comm_flash_sheet(wb, results)

    wb.save(output_file)
    print(f"ODX checklist written to {output_file}")


if __name__ == "__main__":
    main()
