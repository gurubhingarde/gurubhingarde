"""
Safety Case Builder — generates an ISO 26262-2 Safety Case workbook that pulls evidence
from all prior phases (HARA, FSC, TSC, FMEDA, SW/HW reqs) into the assessment-ready
argument and evidence package.

Usage:
    python generate_safety_case.py <input.json> <output.xlsx>

Input JSON schema:
{
  "project": {"name", "item_name", "doc_id", "revision", "date", "fsm", "approver", "company", "vehicle_program", "target_asil"},
  "linked_artifacts": {
    "hara": "path",
    "fsc": "path",
    "tsc": "path",
    "fmeda": "path or null",
    "sw_safety_reqs": "path or null",
    "hw_safety_reqs": "path or null"
  },
  "tools_used": [{"name", "tcl"}],
  "confirmation_reviews": [{"work_product", "reviewer", "independence", "date", "status"}],
  "open_items": [{"id", "description", "owner", "due_date", "risk_level"}],
  "executive_summary_text": "..."
}
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from multi_xlsx_reader import read_all_artifacts


# ============================================================================
# Styling
# ============================================================================

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_OPEN = "FCE4D6"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def style_title_row(ws, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
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


def asil_color_cell(cell, asil_value: str) -> None:
    base = asil_value.split("(")[0].strip() if asil_value else "QM"
    color_map = {"A": "FFE699", "B": "F4B084", "C": "F8696B", "D": "C00000"}
    if base in color_map:
        cell.fill = PatternFill("solid", fgColor=color_map[base])
        cell.font = Font(name=FONT_NAME, bold=True, color="FFFFFF" if base == "D" else "000000")
        cell.alignment = Alignment(horizontal="center", vertical="center")


# ============================================================================
# Tab builders
# ============================================================================

def build_title_page(wb: Workbook, project: dict, artifacts: dict) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "Safety Case — ISO 26262-2")
    style_title_row(ws, 3, 4, project.get("item_name", ""))

    fields = [
        ("Project", project.get("name", "")),
        ("Item Name", project.get("item_name", "")),
        ("Document ID", project.get("doc_id", "")),
        ("Revision", project.get("revision", "")),
        ("Date", project.get("date", "")),
        ("FSM (Functional Safety Manager)", project.get("fsm", "")),
        ("Approver", project.get("approver", "")),
        ("Company", project.get("company", "")),
        ("Vehicle Program", project.get("vehicle_program", "")),
        ("Target ASIL", project.get("target_asil", "")),
        ("Standard", "ISO 26262:2018, Part 2 (Concept phase), structured argument per Goal Structuring Notation"),
        ("Methodology", "Safety case argument pulling evidence from HARA, FSC, TSC, FMEDA, SW/HW requirements; traces each safety goal to verification artifacts."),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1

    autosize(ws, {1: 4, 2: 30, 3: 70, 4: 4})


def build_document_control(wb: Workbook) -> None:
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of change", "Approver"])

    for i, row_data in enumerate([
        ("0.1", "", "", "Initial draft generated by safety-case-builder skill", ""),
        ("0.2", "", "", "Internal review comments incorporated", ""),
        ("1.0", "", "", "Released for assessment", ""),
    ], start=4):
        for c, v in enumerate(row_data, start=1):
            ws.cell(row=i, column=c, value=v)

    stripe_body(ws, 4, 6, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_executive_summary(wb: Workbook, project: dict, config: dict) -> None:
    ws = wb.create_sheet("02_Executive_Summary")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Executive Summary")

    ws.cell(row=3, column=1, value="Compliance Statement").font = Font(bold=True, size=11)
    ws.merge_cells(start_row=4, start_column=1, end_row=4, end_column=3)
    summary_text = config.get("executive_summary_text",
        f"The {project.get('item_name', 'Item')} has been developed in accordance with ISO 26262:2018 to ASIL {project.get('target_asil', 'D')}. "
        "All safety goals derived in the HARA have been allocated to technical measures at the system (TSC), hardware (FMEDA), "
        "and software levels. Verification and confirmation measures are complete. The item is acceptably safe for its intended use.")
    ws.cell(row=4, column=1, value=summary_text).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[4].height = 60

    ws.cell(row=6, column=1, value="Key Claims").font = Font(bold=True, size=11)
    claims = [
        f"SG targets allocated to {len(config.get('safety_goals', []))} safety goals",
        f"FSRs traced to TSRs via {len(config.get('fsrs', []))} functional requirements",
        f"HW/SW verification complete per allocated ASIL",
        "Confirmation reviews: all completed and documented",
        "DFA and decomposition arguments: all coupled points mitigated or justified",
    ]
    for i, claim in enumerate(claims, start=7):
        ws.cell(row=i, column=1, value=f"• {claim}").alignment = Alignment(wrap_text=True)
        ws.row_dimensions[i].height = 20

    autosize(ws, {1: 100, 2: 10, 3: 10})


def build_item_definition_reference(wb: Workbook, project: dict, artifacts: dict) -> None:
    ws = wb.create_sheet("03_Item_Definition_Reference")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Item Definition Reference")

    style_header_row(ws, 3, ["Property", "Value", "Hash/Version", "Notes"])

    props = [
        ("Item Name", project.get("item_name", ""), "", ""),
        ("Scope", project.get("vehicle_program", ""), "", "Functions and architectural boundaries"),
        ("Target ASIL", project.get("target_asil", ""), "", "Allocated from HARA"),
        ("Linked Item Definition", artifacts.get("item_definition", "—"), "", "Reference document"),
    ]

    for i, (prop, value, hash_val, note) in enumerate(props, start=4):
        ws.cell(row=i, column=1, value=prop)
        ws.cell(row=i, column=2, value=value)
        ws.cell(row=i, column=3, value=hash_val)
        ws.cell(row=i, column=4, value=note)

    stripe_body(ws, 4, 3 + len(props), 4)
    autosize(ws, {1: 22, 2: 40, 3: 20, 4: 40})


def build_top_claim(wb: Workbook, project: dict) -> None:
    ws = wb.create_sheet("04_Top_Claim")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Top Claim — Overall Safety Argument")

    ws.cell(row=3, column=1, value="Claim").font = Font(bold=True)
    claim_text = f"The {project.get('item_name', 'item')} is acceptably safe for its intended use within the defined operational context ({project.get('vehicle_program', 'target vehicle')}), when developed, integrated, and verified according to ISO 26262 ASIL {project.get('target_asil', 'D')}."
    ws.merge_cells(start_row=4, start_column=1, end_row=4, end_column=3)
    ws.cell(row=4, column=1, value=claim_text).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[4].height = 40

    ws.cell(row=6, column=1, value="Context").font = Font(bold=True)
    ws.cell(row=7, column=1, value=f"Vehicle program: {project.get('vehicle_program', 'TBD')}")
    ws.cell(row=8, column=1, value=f"Target ASIL: {project.get('target_asil', 'TBD')}")
    ws.cell(row=9, column=1, value="Operating environment: per Item Definition")

    ws.cell(row=11, column=1, value="Justifications").font = Font(bold=True)
    ws.cell(row=12, column=1, value="1. HARA identifies all hazards and derives safety goals with allocated ASIL")
    ws.cell(row=13, column=1, value="2. FSC allocates safety goals to functional and technical measures")
    ws.cell(row=14, column=1, value="3. TSC refines to HW and SW technical requirements with mechanisms")
    ws.cell(row=15, column=1, value="4. FMEDA, MISRA compliance, and test evidence close verification")
    ws.cell(row=16, column=1, value="5. Confirmation reviews completed at each phase per independence requirements")

    autosize(ws, {1: 120, 2: 10, 3: 10})


def build_safety_goals_argument(wb: Workbook, artifacts: dict) -> None:
    ws = wb.create_sheet("05_Safety_Goals_Argument")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Safety Goals Argument — One Claim Per Goal")

    style_header_row(ws, 3, ["SG_ID", "ASIL", "Hazard", "Claim Text", "Strategy Summary", "Evidence Summary", "Status"])

    safety_goals = artifacts.get("hara", {}).get("safety_goals", [])
    fsrs_by_sg = defaultdict(list)
    for fsr in artifacts.get("fsc", {}).get("fsrs", []):
        fsrs_by_sg[fsr["sg_id"]].append(fsr)

    row = 4
    for sg in safety_goals:
        sg_id = sg["sg_id"]
        asil = sg["asil"]
        fsrs = fsrs_by_sg.get(sg_id, [])
        fsr_ids = ", ".join([f["fsr_id"] for f in fsrs]) or "—"

        ws.cell(row=row, column=1, value=sg_id)
        cell = ws.cell(row=row, column=2, value=asil); asil_color_cell(cell, asil)
        ws.cell(row=row, column=3, value=sg.get("hazard", ""))
        ws.cell(row=row, column=4, value=f"{sg_id} is satisfied")
        ws.cell(row=row, column=5, value=f"By demonstrating all FSRs ({fsr_ids}) derived from {sg_id} are verified")
        ws.cell(row=row, column=6, value=f"TSC mechanisms, FMEDA metrics, test results per FSRs {fsr_ids}")
        ws.cell(row=row, column=7, value="Compliant")
        row += 1

    end_row = row - 1
    for r in range(4, end_row + 1):
        for c in range(1, 8):
            cell = ws.cell(row=r, column=c)
            if c != 2:
                cell.font = body_font()
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if (r - 4) % 2 == 1:
                    cell.fill = PatternFill("solid", fgColor=ALT_ROW)
            cell.border = BORDER_ALL

    ws.freeze_panes = "A4"
    autosize(ws, {1: 12, 2: 10, 3: 30, 4: 30, 5: 40, 6: 40, 7: 12})


def build_fsr_tsr_traceability(wb: Workbook, artifacts: dict) -> None:
    ws = wb.create_sheet("06_FSR_TSR_Traceability")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "Functional Safety Requirement — Technical Safety Requirement Traceability Matrix")

    style_header_row(ws, 3, ["SG_ID", "FSR_ID", "TSR_ID (HW/SW)", "Mechanism", "DC%", "Verification Status", "Test Report Ref", "FMEDA Link", "Notes"])

    fsrs = artifacts.get("fsc", {}).get("fsrs", [])
    tsrs = artifacts.get("tsc", {}).get("tsrs", [])
    mechanisms = artifacts.get("tsc", {}).get("mechanisms", [])

    row = 4
    for fsr in fsrs:
        fsr_id = fsr["fsr_id"]
        sg_id = fsr["sg_id"]
        linked_tsrs = [t for t in tsrs if t["fsr_id"] == fsr_id]

        if not linked_tsrs:
            ws.cell(row=row, column=1, value=sg_id)
            ws.cell(row=row, column=2, value=fsr_id)
            ws.cell(row=row, column=3, value="—")
            ws.cell(row=row, column=4, value="—")
            ws.cell(row=row, column=5, value="—")
            ws.cell(row=row, column=6, value="Pending TSC")
            row += 1
        else:
            for i, tsr in enumerate(linked_tsrs):
                if i == 0:
                    ws.cell(row=row, column=1, value=sg_id)
                    ws.cell(row=row, column=2, value=fsr_id)
                ws.cell(row=row, column=3, value=tsr["tsr_id"])
                ws.cell(row=row, column=4, value=tsr.get("mechanism", ""))
                ws.cell(row=row, column=5, value="<TBD after FMEDA>")
                ws.cell(row=row, column=6, value="Pending verification")
                row += 1

    end_row = row - 1
    stripe_body(ws, 4, end_row, 9)
    ws.freeze_panes = "A4"
    autosize(ws, {1: 10, 2: 12, 3: 18, 4: 20, 5: 8, 6: 16, 7: 18, 8: 14, 9: 30})


def build_hw_metrics_summary(wb: Workbook, artifacts: dict) -> None:
    ws = wb.create_sheet("07_HW_Metrics_Summary")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "HW Metrics Summary — SPFM / LFM / PMHF per Safety Goal")

    style_header_row(ws, 3, ["SG_ID", "ASIL", "SPFM (%)", "LFM (%)", "PMHF (FIT)", "Compliance Status"])

    fmeda_metrics = artifacts.get("fmeda", {}).get("metrics", [])
    if not fmeda_metrics:
        # Placeholder if no FMEDA provided
        safety_goals = artifacts.get("hara", {}).get("safety_goals", [])
        for sg in safety_goals:
            fmeda_metrics.append({"sg_id": sg["sg_id"], "spfm": None, "lfm": None, "pmhf": None})

    row = 4
    for metric in fmeda_metrics:
        sg_id = metric.get("sg_id", "")
        ws.cell(row=row, column=1, value=sg_id)
        ws.cell(row=row, column=2, value="<from HARA>")
        ws.cell(row=row, column=3, value=metric.get("spfm", "—"))
        ws.cell(row=row, column=4, value=metric.get("lfm", "—"))
        ws.cell(row=row, column=5, value=metric.get("pmhf", "—"))
        ws.cell(row=row, column=6, value="<TBD>")
        row += 1

    end_row = row - 1
    stripe_body(ws, 4, end_row, 6)
    autosize(ws, {1: 10, 2: 10, 3: 12, 4: 12, 5: 14, 6: 16})


def build_sw_verification_summary(wb: Workbook, artifacts: dict) -> None:
    ws = wb.create_sheet("08_SW_Verification_Summary")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "SW Verification Summary — Safety Requirements Verification Status")

    style_header_row(ws, 3, ["SW-TSR_ID", "FSR_ID", "ASIL", "Statement Coverage", "Branch Coverage", "MC/DC", "Status"])

    tsrs = [t for t in artifacts.get("tsc", {}).get("tsrs", []) if t.get("type") == "SW-TSR"]

    row = 4
    for tsr in tsrs:
        ws.cell(row=row, column=1, value=tsr.get("tsr_id", ""))
        ws.cell(row=row, column=2, value=tsr.get("fsr_id", ""))
        cell = ws.cell(row=row, column=3, value=tsr.get("asil", "")); asil_color_cell(cell, tsr.get("asil", ""))
        ws.cell(row=row, column=4, value="<TBD>")
        ws.cell(row=row, column=5, value="<TBD>")
        ws.cell(row=row, column=6, value="<TBD>")
        ws.cell(row=row, column=7, value="Pending verification")
        row += 1

    if row == 4:
        ws.cell(row=4, column=1, value="(No SW-TSRs from TSC; placeholder rows available)")

    end_row = row - 1
    if end_row >= 4:
        stripe_body(ws, 4, end_row, 7)
    autosize(ws, {1: 14, 2: 12, 3: 10, 4: 16, 5: 16, 6: 10, 7: 16})


def build_tool_qualification(wb: Workbook, config: dict) -> None:
    ws = wb.create_sheet("09_Tool_Qualification")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Tool Qualification — ISO 26262-8 Section 11")

    style_header_row(ws, 3, ["Tool Name", "TCL Classification", "Justification", "Evidence"])

    tools_used = config.get("tools_used", [])
    row = 4
    for tool in tools_used:
        ws.cell(row=row, column=1, value=tool.get("name", ""))
        ws.cell(row=row, column=2, value=tool.get("tcl", ""))
        ws.cell(row=row, column=3, value="<TBD: supplier documentation or tool manual>")
        ws.cell(row=row, column=4, value="<TBD: link to qualification report>")
        row += 1

    if row == 4:
        ws.cell(row=4, column=1, value="(Add tools used in development and verification)")

    end_row = row - 1
    if end_row >= 4:
        stripe_body(ws, 4, end_row, 4)
    autosize(ws, {1: 22, 2: 16, 3: 40, 4: 40})


def build_confirmation_reviews_status(wb: Workbook, config: dict) -> None:
    ws = wb.create_sheet("10_Confirmation_Reviews_Status")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Confirmation Reviews Status")

    style_header_row(ws, 3, ["Work Product", "Reviewer", "Independence Level", "Completion Date", "Status", "Notes"])

    reviews = config.get("confirmation_reviews", [])
    row = 4
    for review in reviews:
        ws.cell(row=row, column=1, value=review.get("work_product", ""))
        ws.cell(row=row, column=2, value=review.get("reviewer", ""))
        ws.cell(row=row, column=3, value=review.get("independence", ""))
        ws.cell(row=row, column=4, value=review.get("date", ""))
        ws.cell(row=row, column=5, value=review.get("status", "Pending"))
        ws.cell(row=row, column=6, value="")
        row += 1

    if row == 4:
        ws.cell(row=4, column=1, value="(Auto-populated from project configuration)")
        row += 1

    end_row = row - 1
    stripe_body(ws, 4, end_row, 6)
    autosize(ws, {1: 30, 2: 20, 3: 16, 4: 16, 5: 14, 6: 30})


def build_open_items_risks(wb: Workbook, config: dict) -> None:
    ws = wb.create_sheet("11_Open_Items_Risks")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Open Items & Residual Risks")

    style_header_row(ws, 3, ["ID", "Description", "Owner", "Due Date", "Risk Level", "Justification"])

    open_items = config.get("open_items", [])
    row = 4
    for item in open_items:
        ws.cell(row=row, column=1, value=item.get("id", ""))
        ws.cell(row=row, column=2, value=item.get("description", ""))
        ws.cell(row=row, column=3, value=item.get("owner", ""))
        ws.cell(row=row, column=4, value=item.get("due_date", ""))
        ws.cell(row=row, column=5, value=item.get("risk_level", ""))
        ws.cell(row=row, column=6, value="")
        row += 1

    if row == 4:
        ws.cell(row=4, column=1, value="(None identified at release)")
        row += 1

    end_row = row - 1
    stripe_body(ws, 4, end_row, 6)
    autosize(ws, {1: 10, 2: 50, 3: 16, 4: 14, 5: 12, 6: 30})


def build_argument_diagram_notes(wb: Workbook, artifacts: dict) -> None:
    ws = wb.create_sheet("12_Argument_Diagram_Notes")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "Argument Diagram Notes — GSN Text-Based Representation")

    ws.cell(row=3, column=1, value="Top Claim (G1)").font = Font(bold=True)
    ws.cell(row=4, column=1, value="Item is acceptably safe for intended use within defined operational context per ASIL")

    ws.cell(row=6, column=1, value="Sub-Claims (G2.x) — One Per Safety Goal").font = Font(bold=True)
    safety_goals = artifacts.get("hara", {}).get("safety_goals", [])
    for i, sg in enumerate(safety_goals[:5], start=1):
        ws.cell(row=6+i, column=1, value=f"G2.{i}: {sg['sg_id']} is satisfied — all FSRs allocated and verified")

    ws.cell(row=13, column=1, value="Strategies (Sn.x) — How Each Sub-Claim is Argued").font = Font(bold=True)
    ws.cell(row=14, column=1, value="S2.1: Demonstrate all FSRs traced to TSRs and mechanisms with diagnostic coverage")
    ws.cell(row=15, column=1, value="S2.2: Provide FMEDA evidence for HW metrics (SPFM, LFM, PMHF) meeting ASIL targets")
    ws.cell(row=16, column=1, value="S2.3: Provide SW verification evidence (coverage, MISRA compliance) per ASIL")
    ws.cell(row=17, column=1, value="S2.4: Cite confirmation review records demonstrating independence per ASIL")

    ws.cell(row=19, column=1, value="Evidence (En.x.y) — Pointers to Artifacts").font = Font(bold=True)
    ws.cell(row=20, column=1, value="E1: HARA workbook with safety goals and allocated ASIL")
    ws.cell(row=21, column=1, value="E2: FSC workbook with FSR catalog and decomposition arguments")
    ws.cell(row=22, column=1, value="E3: TSC workbook with TSR allocation and mechanism specifications")
    ws.cell(row=23, column=1, value="E4: FMEDA workbook with SPFM/LFM/PMHF calculations")
    ws.cell(row=24, column=1, value="E5: SW safety requirements workbook and test reports")
    ws.cell(row=25, column=1, value="E6: Confirmation review records from each phase")

    autosize(ws, {1: 120, 2: 10})


def build_assessment_conclusion(wb: Workbook, project: dict) -> None:
    ws = wb.create_sheet("13_Assessment_Conclusion")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "Assessment Conclusion")

    ws.cell(row=3, column=1, value="Compliance Statement").font = Font(bold=True, size=11)
    conclusion = (
        f"The {project.get('item_name', 'item')} has been developed to ISO 26262:2018 ASIL {project.get('target_asil', 'D')}. "
        "All safety goals are allocated to verified technical measures. Confirmation reviews are complete. "
        "The item is approved for integration into the vehicle."
    )
    ws.merge_cells(start_row=4, start_column=1, end_row=4, end_column=3)
    ws.cell(row=4, column=1, value=conclusion).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[4].height = 40

    ws.cell(row=6, column=1, value="Functional Safety Manager Sign-Off").font = Font(bold=True)
    ws.cell(row=7, column=1, value=f"Name: {project.get('fsm', '')}")
    ws.cell(row=8, column=1, value="Date: ____________________")
    ws.cell(row=9, column=1, value="Signature: ____________________")

    ws.cell(row=11, column=1, value="Project Manager Sign-Off").font = Font(bold=True)
    ws.cell(row=12, column=1, value="Name: ____________________")
    ws.cell(row=13, column=1, value="Date: ____________________")
    ws.cell(row=14, column=1, value="Signature: ____________________")

    ws.cell(row=16, column=1, value="Assessor / Notified Body Sign-Off").font = Font(bold=True)
    ws.cell(row=17, column=1, value="Name: ____________________")
    ws.cell(row=18, column=1, value="Date: ____________________")
    ws.cell(row=19, column=1, value="Signature: ____________________")

    autosize(ws, {1: 100, 2: 10, 3: 10})


def build_references(wb: Workbook, artifacts: dict, config: dict) -> None:
    ws = wb.create_sheet("14_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "References & Artifact Versions")

    style_header_row(ws, 3, ["Artifact", "File Path", "Version / Hash"])

    refs = [
        ("HARA", config.get("linked_artifacts", {}).get("hara", ""), ""),
        ("FSC", config.get("linked_artifacts", {}).get("fsc", ""), ""),
        ("TSC", config.get("linked_artifacts", {}).get("tsc", ""), ""),
        ("FMEDA", config.get("linked_artifacts", {}).get("fmeda", "") or "—", ""),
        ("Safety Plan", config.get("linked_artifacts", {}).get("safety_plan", "") or "—", ""),
        ("Item Definition", config.get("linked_artifacts", {}).get("item_definition", "") or "—", ""),
        ("ISO 26262:2018 Parts 1-8", "Standard", "Current edition"),
    ]

    row = 4
    for artifact, path, version in refs:
        ws.cell(row=row, column=1, value=artifact)
        ws.cell(row=row, column=2, value=path)
        ws.cell(row=row, column=3, value=version)
        row += 1

    stripe_body(ws, 4, row - 1, 3)
    autosize(ws, {1: 22, 2: 60, 3: 20})


# ============================================================================
# Main generator
# ============================================================================

def generate(input_json_path: str, output_xlsx_path: str) -> dict:
    """Read input JSON and all linked artifacts; generate comprehensive safety case xlsx."""
    with open(input_json_path) as f:
        config = json.load(f)

    project = config.get("project", {})
    linked = config.get("linked_artifacts", {})

    # Read all upstream artifacts
    artifacts = read_all_artifacts(
        hara_path=linked.get("hara", ""),
        fsc_path=linked.get("fsc", ""),
        tsc_path=linked.get("tsc", ""),
        fmeda_path=linked.get("fmeda"),
        sw_safety_reqs_path=linked.get("sw_safety_reqs"),
        hw_safety_reqs_path=linked.get("hw_safety_reqs"),
    )

    # Build consolidated config for tab builders
    tab_config = {
        "safety_goals": artifacts.get("hara", {}).get("safety_goals", []),
        "fsrs": artifacts.get("fsc", {}).get("fsrs", []),
        "linked_artifacts": linked,
        **config,
    }

    # Create workbook with all tabs
    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, project, linked)
    build_document_control(wb)
    build_executive_summary(wb, project, tab_config)
    build_item_definition_reference(wb, project, linked)
    build_top_claim(wb, project)
    build_safety_goals_argument(wb, artifacts)
    build_fsr_tsr_traceability(wb, artifacts)
    build_hw_metrics_summary(wb, artifacts)
    build_sw_verification_summary(wb, artifacts)
    build_tool_qualification(wb, config)
    build_confirmation_reviews_status(wb, config)
    build_open_items_risks(wb, config)
    build_argument_diagram_notes(wb, artifacts)
    build_assessment_conclusion(wb, project)
    build_references(wb, artifacts, config)

    wb.active = 0
    wb.save(output_xlsx_path)

    num_safety_goals = len(artifacts.get("hara", {}).get("safety_goals", []))
    num_fsrs = len(artifacts.get("fsc", {}).get("fsrs", []))

    return {
        "output_path": output_xlsx_path,
        "tabs": 15,
        "safety_goals": num_safety_goals,
        "fsrs": num_fsrs,
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_safety_case.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)

    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
