"""
HW Safety Requirements Checklist Reviewer — generates completed confirmation-measures checklist.

Usage:
    python generate_checklist.py <hw_sr.xlsx> <output_checklist.xlsx>

Methodology:
- Probe the HW-SR xlsx content.
- Run each canonical checklist requirement with verification logic.
- For machine-verifiable checks: fill assessment, finding, section, and action.
- For subjective checks: draft marked Low confidence.
- Write 7-tab xlsx (Title, General Info, Guide, Summary, Confirmation Review, HWSRA, VA).
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from hw_sr_probe import ProbedHwSR, probe
from check_definitions import CHECKS, CheckDef, CheckResult
from dashboard import build_dashboard


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

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


def style_section_banner(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=11, bold=True, color="1F3864")
    cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row].height = 22


def autosize(ws, widths):
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = w


def color_assessment(cell, rating, obligation):
    color_map = {
        "FC": GREEN_OK,
        "LC": "DAEEF3",
        "PC": ORANGE_PARTIAL,
        "NO": RED_BAD,
        "NA": GREY,
    }
    color = color_map.get(rating)
    if color:
        cell.fill = PatternFill("solid", fgColor=color)
    cell.font = Font(name=FONT_NAME, bold=True, size=10)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    if rating == "NO":
        cell.font = Font(name=FONT_NAME, bold=True, size=10, color="C00000")


# ---------------------------------------------------------------------------
# Tab writers
# ---------------------------------------------------------------------------

def write_title_tab(wb, probed):
    ws = wb.create_sheet("Title", 0)
    style_title(ws, 1, 4, "HW Safety Requirements Checklist")
    ws.row_dimensions[2].height = 30

    r = 3
    ws.cell(row=r, column=1, value="Document Being Assessed")
    ws.cell(row=r, column=2, value=probed.title or "(No title detected)")
    r += 1
    ws.cell(row=r, column=1, value="Document ID")
    ws.cell(row=r, column=2, value=probed.doc_id or "—")
    r += 1
    ws.cell(row=r, column=1, value="Revision")
    ws.cell(row=r, column=2, value=probed.revision or "—")
    r += 1
    ws.cell(row=r, column=1, value="Status")
    ws.cell(row=r, column=2, value=probed.status or "—")
    r += 1
    ws.cell(row=r, column=1, value="Author")
    ws.cell(row=r, column=2, value=probed.author or "—")
    r += 1
    ws.cell(row=r, column=1, value="Approver")
    ws.cell(row=r, column=2, value=probed.approver or "—")
    r += 1
    ws.cell(row=r, column=1, value="Project")
    ws.cell(row=r, column=2, value=probed.project or "—")
    r += 1
    ws.cell(row=r, column=1, value="Linked TSC")
    ws.cell(row=r, column=2, value=probed.linked_tsc or "—")
    r += 2

    ws.cell(row=r, column=1, value="Checklist Generated")
    ws.cell(row=r, column=2, value=str(date.today()))
    r += 1
    ws.cell(row=r, column=1, value="Format Detected")
    ws.cell(row=r, column=2, value="hw-safety-reqs-builder" if probed.is_hw_sr_builder_format else "best-effort")

    autosize(ws, {1: 20, 2: 40, 3: 12, 4: 12})


def write_general_info_tab(wb, probed):
    ws = wb.create_sheet("General Info", 1)
    style_title(ws, 1, 3, "HW-SR Checklist — Contents & References")

    r = 3
    ws.cell(row=r, column=1, value="Tab")
    ws.cell(row=r, column=2, value="Purpose")
    style_header(ws, r, ["Tab", "Purpose"])
    r += 1

    tabs = [
        ("Title", "Document metadata and checklist info"),
        ("General Info", "Table of contents and references"),
        ("Guide", "How to interpret ratings and confidence"),
        ("Summary", "Statistical roll-up and findings"),
        ("Confirmation Review", "14 generic doc-quality checks"),
        ("HW-SR Assessment", "12 substantive HW-SR checks per ISO 26262-5"),
        ("Verification Assessment", "22 verification-related checks (mostly external)"),
    ]
    for tab, purpose in tabs:
        ws.cell(row=r, column=1, value=tab)
        ws.cell(row=r, column=2, value=purpose)
        r += 1

    r += 2
    ws.cell(row=r, column=1, value="References").font = Font(name=FONT_NAME, size=12, bold=True)
    r += 1
    refs = [
        "ISO 26262-5:2018 — Product development at system level, hardware design & verification",
        "ISO 26262-1:2018 — Functional Safety",
        "hw-safety-reqs-builder documentation",
        "TSC (Technical Safety Concept) document",
    ]
    for ref in refs:
        ws.cell(row=r, column=1, value=ref)
        ws.cell(row=r, column=1).alignment = Alignment(wrap_text=True)
        ws.row_dimensions[r].height = 25
        r += 1

    autosize(ws, {1: 20, 2: 50})


def write_guide_tab(wb):
    ws = wb.create_sheet("Guide", 2)
    style_title(ws, 1, 3, "How to Use This Checklist")

    r = 3
    ws.cell(row=r, column=1, value="Rating").font = Font(bold=True)
    ws.cell(row=r, column=2, value="Meaning").font = Font(bold=True)
    style_header(ws, r, ["Rating", "Meaning"])
    r += 1

    ratings = [
        ("FC", "Fully Compliant — requirement satisfied, evidence cited"),
        ("LC", "Largely Compliant — minor gaps or concerns"),
        ("PC", "Partially Compliant — significant gaps or missing evidence"),
        ("NO", "Non-Compliant — requirement not met"),
        ("NA", "Not Applicable — requirement does not apply"),
        ("Pending", "Awaiting reviewer judgment or external verification"),
    ]
    for code, meaning in ratings:
        ws.cell(row=r, column=1, value=code).font = Font(bold=True)
        ws.cell(row=r, column=2, value=meaning)
        r += 1

    r += 2
    ws.cell(row=r, column=1, value="Confidence").font = Font(bold=True)
    ws.cell(row=r, column=2, value="Meaning").font = Font(bold=True)
    style_header(ws, r, ["Confidence", "Meaning"])
    r += 1

    confs = [
        ("High", "Verified directly from xlsx or standard interpretation"),
        ("Medium", "Inferred from xlsx with reasonable assumption"),
        ("Low", "Subjective or requires external artifact; marked for reviewer judgment"),
    ]
    for conf, meaning in confs:
        ws.cell(row=r, column=1, value=conf)
        ws.cell(row=r, column=2, value=meaning)
        r += 1

    r += 2
    ws.cell(row=r, column=1, value="Workflow").font = Font(bold=True, size=12)
    r += 1
    workflow = [
        "1. Review Title tab to confirm the HW-SR document.",
        "2. Review Summary tab for statistical roll-up and key findings.",
        "3. Walk Confirmation Review tab; focus on NO and Pending rows.",
        "4. Walk HW-SR Assessment tab; address PC and NO findings.",
        "5. Walk Verification Assessment tab; note that most items are external.",
        "6. For each finding, decide: accept / refine / reject.",
        "7. For PC or NO rows, update the source HW-SR and re-run the checklist.",
    ]
    for line in workflow:
        ws.cell(row=r, column=1, value=line)
        ws.cell(row=r, column=1).alignment = Alignment(wrap_text=True)
        ws.row_dimensions[r].height = 20
        r += 1

    autosize(ws, {1: 20, 2: 60})


def write_summary_tab(wb, results):
    """Summary tab with dashboard charts."""
    ws = wb.create_sheet("Summary", 3)
    style_title(ws, 1, 8, "Summary & Findings")

    # Call dashboard to fill in charts, KPIs, and findings table
    build_dashboard(ws, results)

    autosize(ws, {c: 18 for c in range(1, 9)})


def write_checklist_tab(wb, tab_name, tab_code, checks_and_results):
    """Write a single checklist tab (CR, HWSRA, or VA)."""
    ws = wb.create_sheet(tab_name)

    headers = ["ID", "Section", "Requirement", "Obligation", "Assessment", "Finding", "Page/Section", "Recommended Action", "Confidence"]
    style_header(ws, 1, headers)

    row = 2
    last_section = None

    for check_def, check_result in checks_and_results:
        # Section banner
        if check_def.section != last_section:
            style_section_banner(ws, row, len(headers), check_def.section)
            last_section = check_def.section
            row += 1

        # Data row
        ws.cell(row=row, column=1, value=check_def.id)
        ws.cell(row=row, column=2, value=check_def.section)
        ws.cell(row=row, column=3, value=check_def.requirement)
        ws.cell(row=row, column=4, value=check_def.obligation)

        # Assessment (colored)
        assessment_cell = ws.cell(row=row, column=5, value=check_result.rating)
        color_assessment(assessment_cell, check_result.rating, check_def.obligation)

        ws.cell(row=row, column=6, value=check_result.finding)
        ws.cell(row=row, column=7, value=check_result.page_section)
        ws.cell(row=row, column=8, value=check_result.recommended_action)
        ws.cell(row=row, column=9, value=check_result.confidence)

        # Wrap text
        for col in [3, 6, 7, 8]:
            ws.cell(row=row, column=col).alignment = Alignment(wrap_text=True)
        ws.row_dimensions[row].height = 30

        row += 1

    # Autosize
    widths = {1: 6, 2: 22, 3: 45, 4: 8, 5: 10, 6: 30, 7: 20, 8: 30, 9: 12}
    autosize(ws, widths)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def generate_checklist(input_path: str, output_path: str) -> dict:
    """
    Generate the HW-SR checklist xlsx.

    Returns a summary dict with tab ratings distributions.
    """
    # Probe
    probed = probe(input_path)

    # Run all checks
    results = defaultdict(list)  # tab_code -> [(check_def, check_result), ...]
    for check_def in CHECKS:
        try:
            check_result = check_def.verify(probed)
        except Exception as e:
            check_result = CheckResult(
                rating="",
                finding=f"[Error executing check: {e}]",
                page_section="",
                recommended_action="",
                confidence="",
            )
        results[check_def.tab].append((check_def, check_result))

    # Create workbook
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    # Write tabs
    write_title_tab(wb, probed)
    write_general_info_tab(wb, probed)
    write_guide_tab(wb)
    write_summary_tab(wb, results)
    write_checklist_tab(wb, "Confirmation Review", "CR", results["CR"])
    write_checklist_tab(wb, "HW-SR Assessment", "HWSRA", results["HWSRA"])
    write_checklist_tab(wb, "Verification Assessment", "VA", results["VA"])

    # Save
    wb.save(output_path)

    # Summarize
    summary = {}
    for tab_code, checks_results in results.items():
        rating_counts = Counter(r.rating or "PENDING" for _, r in checks_results)
        summary[tab_code] = {
            "total": len(checks_results),
            "FC": rating_counts.get("FC", 0),
            "LC": rating_counts.get("LC", 0),
            "PC": rating_counts.get("PC", 0),
            "NO": rating_counts.get("NO", 0),
            "NA": rating_counts.get("NA", 0),
            "PENDING": rating_counts.get("PENDING", 0),
        }

    return summary


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <input.xlsx> <output.xlsx>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    print(f"Probing {input_file}...")
    summary = generate_checklist(input_file, output_file)

    print(f"\nChecklist written to {output_file}")
    print("\nRating summary by tab:")
    print(json.dumps(summary, indent=2))
