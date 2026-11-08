"""Verification Plan checklist reviewer - generates assessment per ISO 26262-8 §9."""

from __future__ import annotations

import sys
from pathlib import Path
from datetime import date
from collections import Counter

from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

from vplan_probe import probe_vplan
from check_definitions import CHECKS, evaluate_vplan
from dashboard import build_dashboard

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
GREY = "D0CECE"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"
ORANGE_PARTIAL = "FFD966"

def main(vplan_xlsx: str, output_xlsx: str):
    try:
        probed = probe_vplan(vplan_xlsx)
        print(f"Probed Verification Plan: {probed.title}")
    except Exception as e:
        print(f"Error probing Verification Plan: {e}")
        sys.exit(1)

    results = evaluate_vplan(probed)

    wb = Workbook()
    wb.remove(wb.active)

    # Title
    ws = wb.create_sheet("Title")
    ws.merge_cells("A1:D1")
    c = ws["A1"]
    c.value = "Verification Plan Confirmation Measures Checklist"
    c.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = Alignment(horizontal="center")

    row = 4
    for label, value in [("Item", probed.title), ("Doc ID", probed.doc_id),
                         ("Revision", probed.revision), ("Checklist Generated", date.today().isoformat()),
                         ("Standard", "ISO 26262-8:2018 Section 9 & IEEE 1012")]:
        ws.cell(row=row, column=1, value=label).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

    # Checklist
    ws = wb.create_sheet("Checklist")
    ws["A1"] = "Verification Plan Confirmation Measures"
    ws["A1"].font = Font(size=12, bold=True)
    ws.merge_cells("A1:D1")

    headers = ["ID", "Confirmation Measure", "Category", "Assessment"]
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=3, column=col, value=h)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(horizontal="center")

    for row_idx, (check_id, result) in enumerate(results.items(), 4):
        check_def = CHECKS.get(check_id)
        if not check_def:
            continue

        ws.cell(row=row_idx, column=1, value=check_id)
        ws.cell(row=row_idx, column=2, value=check_def["measure"])
        ws.cell(row=row_idx, column=3, value=check_def["category"])

        rating = result.get("rating", "NA")
        c = ws.cell(row=row_idx, column=4, value=rating)
        color_map = {"FC": GREEN_OK, "LC": LIGHT_BLUE, "PC": ORANGE_PARTIAL, "NO": RED_BAD, "NA": GREY}
        c.fill = PatternFill("solid", fgColor=color_map.get(rating, GREY))
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")

    # Findings
    ws = wb.create_sheet("Findings")
    ws["A1"] = "Findings and Recommendations"
    ws["A1"].font = Font(size=12, bold=True)
    ws.merge_cells("A1:C1")

    row = 3
    failures = [r for r in results.values() if r.get("rating") == "NO"]
    partials = [r for r in results.values() if r.get("rating") == "PC"]

    if failures:
        ws.cell(row=row, column=1, value="FINDINGS (Blockers)").font = Font(bold=True, color="C00000")
        row += 1
        for f in failures:
            ws.cell(row=row, column=1, value=f.get("finding", "No details"))
            ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True)
            row += 2

    if partials:
        ws.cell(row=row, column=1, value="FINDINGS (Partial)").font = Font(bold=True, color="FF6600")
        row += 1
        for p in partials:
            ws.cell(row=row, column=1, value=p.get("finding", "No details"))
            ws.cell(row=row, column=1).alignment = Alignment(wrap_text=True)
            row += 2

    # Dashboard (placeholder)
    ws = wb.create_sheet("Dashboard")
    ws["A1"] = "Verification Plan Assessment Dashboard"
    ws["A1"].font = Font(size=12, bold=True)
    ws.merge_cells("A1:D1")

    counts = Counter(r.get("rating", "NA") for r in results.values())
    row = 3
    for rating, label in [("FC", "Fully Compliant"), ("LC", "Largely Compliant"),
                          ("PC", "Partially Compliant"), ("NO", "Non-Conforming")]:
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=counts.get(rating, 0))
        row += 1

    # Signoff
    ws = wb.create_sheet("Signoff")
    ws["A1"] = "Checklist Signoff"
    ws["A1"].font = Font(size=12, bold=True)
    ws.merge_cells("A1:C1")

    ws.cell(row=3, column=1, value="Reviewer Name:")
    ws.cell(row=3, column=2, value="TBD")
    ws.cell(row=4, column=1, value="Date:")
    ws.cell(row=4, column=2, value=date.today().isoformat())
    ws.cell(row=5, column=1, value="Approval Authority:")
    ws.cell(row=5, column=2, value="TBD")

    try:
        wb.save(output_xlsx)
        print(f"Checklist generated: {output_xlsx}")
    except Exception as e:
        print(f"Error saving checklist: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <vplan.xlsx> <output_checklist.xlsx>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
