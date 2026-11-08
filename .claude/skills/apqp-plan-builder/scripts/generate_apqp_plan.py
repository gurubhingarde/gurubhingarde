"""
APQP Plan Builder — generates a multi-tab AIAG APQP 5-phase master plan workbook.

Usage:
    python generate_apqp_plan.py <input.json> <output.xlsx>

Input JSON schema:
{
  "program": {
    "name", "customer", "oem", "vehicle_program", "model_year", "part_number",
    "doc_id", "revision", "date", "program_manager", "quality_lead",
    "engineering_lead", "company", "sop_date", "eop_date", "peak_annual_volume"
  },
  "team": [{"name", "role", "department", "phases_responsible"}],
  "phase_deliverables_overrides": {"phase1": [...], ...},
  "milestones": [{"id", "name", "phase", "planned_date", "predecessors"}],
  "gate_reviews": [{"id", "phase_exit", "planned_date", "exit_criteria"}],
  "special_characteristics": [{"id", "characteristic", "type", "source", "control_method"}],
  "risks": [{"id", "description", "likelihood", "impact", "mitigation", "owner"}]
}
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


# -------------------------------------------------------------------------
# Styling helpers (match safety-plan-builder palette)
# -------------------------------------------------------------------------

FONT_NAME = "Calibri"

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"

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


# -------------------------------------------------------------------------
# AIAG APQP 5-Phase Deliverables
# -------------------------------------------------------------------------

DEFAULT_DELIVERABLES = {
    "phase1": [
        ("P1-D01", "Voice of Customer (VOC) Analysis", "Customer inputs and expectations documented", "QE", "Planned"),
        ("P1-D02", "Business Case / Business Plan", "Program business justification and ROI", "PM", "Planned"),
        ("P1-D03", "Customer Requirements Review", "Customer requirements and CSL definition", "QE", "Planned"),
        ("P1-D04", "Preliminary BOM", "Initial bill of materials, make/buy decision", "DE", "Planned"),
        ("P1-D05", "Preliminary Process Flow", "High-level manufacturing/assembly flow", "Mfg", "Planned"),
        ("P1-D06", "Design Goals and Targets", "Performance, cost, reliability targets", "DE", "Planned"),
        ("P1-D07", "Reliability Targets", "MTBF, MTTR, FTA requirements", "QE", "Planned"),
        ("P1-D08", "Preliminary Special Characteristics (SC) List", "CTQ and CSL characteristics", "QE", "Planned"),
        ("P1-D09", "Team APQP Kickoff / Gate 1 Review", "Cross-functional team formed and roles assigned", "PM", "Planned"),
    ],
    "phase2": [
        ("P2-D01", "Design FMEA (DFMEA)", "Failure modes and effects per AIAG-VDA", "DE", "Planned"),
        ("P2-D02", "Design for Assembly (DFA) / Manufacturability (DFM)", "Design simplification and ease of manufacture", "DE/Mfg", "Planned"),
        ("P2-D03", "Design Verification Plan and Report (DVP&R)", "Prototype testing verification", "QE", "Planned"),
        ("P2-D04", "Design Reviews (including Prototype Build)", "DR1/DR2/DR3, prototype hardware/software", "DE", "Planned"),
        ("P2-D05", "Engineering Drawings and Specifications", "Final design drawings, materials, tolerances", "DE", "Planned"),
        ("P2-D06", "Finalized Special Characteristics List", "SC/CC per customer and regulatory designations", "QE", "Planned"),
        ("P2-D07", "Supplier APQP Cascaded", "Suppliers given APQP inputs and schedule", "SQ", "Planned"),
        ("P2-D08", "Prototype Build and Functional Testing", "Prototype hardware/software validation", "Mfg/DE", "Planned"),
        ("P2-D09", "Gate 2 Review (Design Confirmation)", "Design adequate for full development", "PM", "Planned"),
    ],
    "phase3": [
        ("P3-D01", "Packaging Standards and Specifications", "Customer/regulatory packaging requirements", "QE", "Planned"),
        ("P3-D02", "Process Flow Chart", "Detailed process flow with all operations", "Mfg", "Planned"),
        ("P3-D03", "Floor Plan and Layout", "Manufacturing/assembly facility layout", "Mfg", "Planned"),
        ("P3-D04", "Characteristics Matrix", "Product/process characteristics traceability", "QE", "Planned"),
        ("P3-D05", "Process FMEA (PFMEA)", "Manufacturing process failure modes and effects", "Mfg", "Planned"),
        ("P3-D06", "Pre-Launch Control Plan (PLCP)", "Reaction plan for non-conformances pre-SOP", "QE/Mfg", "Planned"),
        ("P3-D07", "Process Instructions and Work Instructions", "Standard operating procedures (SOP stubs)", "Mfg", "Planned"),
        ("P3-D08", "MSA (Measurement System Analysis) Plan", "Gage R&R and measurement adequacy plan", "QE", "Planned"),
        ("P3-D09", "Preliminary Process Capability Study Plan", "Cpk targets and sampling plan outline", "QE", "Planned"),
        ("P3-D10", "Gate 3 Review (Process Confirmation)", "Process capability and controls defined", "PM", "Planned"),
    ],
    "phase4": [
        ("P4-D01", "Production Trial Run", "PRR execution and validation at production rates", "Mfg/QE", "Planned"),
        ("P4-D02", "MSA (Measurement System Analysis) Executed", "Gage R&R completed on all measuring devices", "QE", "Planned"),
        ("P4-D03", "Preliminary Process Capability Study (PPC)", "Cpk/Ppk data from trial run", "QE", "Planned"),
        ("P4-D04", "Production Validation Testing", "Full production trial lot testing (physical, functional)", "QE", "Planned"),
        ("P4-D05", "Production Part Approval Plan (PPAP) Submission", "Customer approval per AIAG PPAP level", "QE", "Planned"),
        ("P4-D06", "Production Control Plan (PCP)", "Final control plan for production", "QE/Mfg", "Planned"),
        ("P4-D07", "Production Run @ Rate (@ SOP rates)", "Sustained production at planned volume", "Mfg", "Planned"),
        ("P4-D08", "Quality Planning Sign-Off", "Customer and supplier quality sign-off", "QE/SQ", "Planned"),
        ("P4-D09", "Gate 4 Review (Production Readiness)", "All deliverables complete, ready for SOP", "PM", "Planned"),
    ],
    "phase5": [
        ("P5-D01", "Reduced Variation", "Continuous improvement and variation reduction", "QE/Mfg", "Planned"),
        ("P5-D02", "Customer Satisfaction Monitoring", "On-time delivery, quality metrics", "SQ/PM", "Planned"),
        ("P5-D03", "Delivery and Service Performance", "Supply chain performance and support", "SQ", "Planned"),
        ("P5-D04", "Lessons Learned", "Project retrospective and knowledge capture", "PM", "Planned"),
        ("P5-D05", "Effective Use of Corrective Actions", "RCCA and preventive action implementation", "QE", "Planned"),
        ("P5-D06", "Gate 5 Review (Feedback and Optimization)", "Performance summary and close-out", "PM", "Planned"),
    ],
}


# -------------------------------------------------------------------------
# Tab builders
# -------------------------------------------------------------------------

def build_title_page(wb: Workbook, data: dict) -> None:
    """00_Title_Page — Program name, customer, part number, doc ID, signatories."""
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False

    prog = data.get("program", {})

    style_title_row(ws, 2, 4, "APQP Master Plan")
    style_title_row(ws, 3, 4, "Advanced Product Quality Planning — AIAG 5-Phase")

    fields = [
        ("Program Name", prog.get("name", "")),
        ("Customer / OEM", prog.get("customer", "")),
        ("Part Number", prog.get("part_number", "")),
        ("Document ID", prog.get("doc_id", "")),
        ("Revision", prog.get("revision", "")),
        ("Date", prog.get("date", "")),
        ("Supplier Company", prog.get("company", "")),
        ("Model Year", prog.get("model_year", "")),
        ("Vehicle Program", prog.get("vehicle_program", "")),
        ("SOP Date", prog.get("sop_date", "")),
        ("EOP Date", prog.get("eop_date", "")),
        ("Peak Annual Volume", prog.get("peak_annual_volume", "")),
        ("Program Manager", prog.get("program_manager", "")),
        ("Quality Lead", prog.get("quality_lead", "")),
        ("Engineering Lead", prog.get("engineering_lead", "")),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1

    autosize(ws, {1: 4, 2: 26, 3: 60, 4: 4})


def build_document_control(wb: Workbook) -> None:
    """01_Document_Control — Revision history and distribution."""
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 5, "Document Control")

    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description", "Approver"])
    placeholders = [
        ("0.1", "", "", "Initial draft", ""),
        ("0.2", "", "", "Internal review", ""),
        ("1.0", "", "", "Released", ""),
    ]
    for i, row_data in enumerate(placeholders, start=4):
        for col, val in enumerate(row_data, start=1):
            ws.cell(row=i, column=col, value=val)
    stripe_body(ws, 4, 4 + len(placeholders) - 1, 5)
    autosize(ws, {1: 12, 2: 12, 3: 18, 4: 30, 5: 18})


def build_program_info(wb: Workbook, data: dict) -> None:
    """02_Program_Info — Customer, OEM, vehicle program, model year, key dates."""
    ws = wb.create_sheet("02_Program_Info")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 4, "Program Information")

    prog = data.get("program", {})

    row = 3
    fields = [
        ("Program Name", prog.get("name", "")),
        ("Customer / OEM", prog.get("customer", "")),
        ("Supplier Company", prog.get("company", "")),
        ("Part Number", prog.get("part_number", "")),
        ("Vehicle Program", prog.get("vehicle_program", "")),
        ("Model Year", prog.get("model_year", "")),
        ("Contract Value", ""),
        ("SOP Date", prog.get("sop_date", "")),
        ("EOP Date", prog.get("eop_date", "")),
        ("Peak Annual Volume", prog.get("peak_annual_volume", "")),
    ]

    for label, value in fields:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

    autosize(ws, {1: 30, 2: 50})


def build_cross_functional_team(wb: Workbook, data: dict) -> None:
    """03_Cross_Functional_Team — Team roster with roles and phase responsibilities."""
    ws = wb.create_sheet("03_Cross_Functional_Team")

    style_title_row(ws, 1, 5, "Cross-Functional Team")

    headers = ["Name", "Role", "Department", "Phases Responsible", "Contact"]
    style_header_row(ws, 3, headers)

    team = data.get("team", [])
    if not team:
        team = [
            {"name": "", "role": "Program Manager", "department": "", "phases_responsible": "All", "contact": ""},
            {"name": "", "role": "Quality Engineer", "department": "", "phases_responsible": "All", "contact": ""},
            {"name": "", "role": "Design Engineer", "department": "", "phases_responsible": "P1-P3", "contact": ""},
            {"name": "", "role": "Manufacturing Engineer", "department": "", "phases_responsible": "P2-P4", "contact": ""},
            {"name": "", "role": "Supplier Quality", "department": "", "phases_responsible": "All", "contact": ""},
        ]

    for i, mbr in enumerate(team, start=4):
        ws.cell(row=i, column=1, value=mbr.get("name", ""))
        ws.cell(row=i, column=2, value=mbr.get("role", ""))
        ws.cell(row=i, column=3, value=mbr.get("department", ""))
        ws.cell(row=i, column=4, value=mbr.get("phases_responsible", ""))
        ws.cell(row=i, column=5, value=mbr.get("contact", ""))

    stripe_body(ws, 4, 4 + len(team) - 1, 5)
    autosize(ws, {1: 20, 2: 25, 3: 20, 4: 25, 5: 25})


def build_phase_deliverables(wb: Workbook, phase_num: int, phase_name: str, data: dict) -> None:
    """Build a phase deliverables tab (P1, P2, P3, P4, P5)."""
    phase_key = f"phase{phase_num}"
    ws = wb.create_sheet(f"0{phase_num}_Phase{phase_num}_{phase_name}")

    style_title_row(ws, 1, 5, f"Phase {phase_num}: {phase_name} — Deliverables")

    headers = ["Deliverable ID", "Deliverable Name", "Description", "Owner", "Status"]
    style_header_row(ws, 3, headers)

    overrides = data.get("phase_deliverables_overrides", {})
    deliverables = overrides.get(phase_key, DEFAULT_DELIVERABLES.get(phase_key, []))

    for i, (del_id, del_name, desc, owner, status) in enumerate(deliverables, start=4):
        ws.cell(row=i, column=1, value=del_id)
        ws.cell(row=i, column=2, value=del_name)
        ws.cell(row=i, column=3, value=desc)
        ws.cell(row=i, column=4, value=owner)
        ws.cell(row=i, column=5, value=status)

    stripe_body(ws, 4, 4 + len(deliverables) - 1, 5)
    autosize(ws, {1: 14, 2: 35, 3: 40, 4: 15, 5: 15})


def build_master_schedule(wb: Workbook, data: dict) -> None:
    """09_Master_Schedule — Gantt-style milestone table."""
    ws = wb.create_sheet("09_Master_Schedule")

    style_title_row(ws, 1, 7, "Master Schedule")

    headers = ["Milestone ID", "Milestone Name", "Phase", "Planned Date", "Actual Date", "Predecessors", "Status"]
    style_header_row(ws, 3, headers)

    milestones = data.get("milestones", [])
    if not milestones:
        milestones = [
            {"id": "M01", "name": "Program Kickoff", "phase": "P1", "planned_date": "", "actual_date": "", "predecessors": "", "status": "Open"},
            {"id": "M02", "name": "Gate 1 Review", "phase": "P1", "planned_date": "", "actual_date": "", "predecessors": "M01", "status": "Open"},
            {"id": "M03", "name": "Gate 2 Review", "phase": "P2", "planned_date": "", "actual_date": "", "predecessors": "M02", "status": "Open"},
            {"id": "M04", "name": "Gate 3 Review", "phase": "P3", "planned_date": "", "actual_date": "", "predecessors": "M03", "status": "Open"},
            {"id": "M05", "name": "Gate 4 Review", "phase": "P4", "planned_date": "", "actual_date": "", "predecessors": "M04", "status": "Open"},
            {"id": "M06", "name": "Production Run @ Rate", "phase": "P4", "planned_date": "", "actual_date": "", "predecessors": "M05", "status": "Open"},
            {"id": "M07", "name": "PPAP Submission", "phase": "P4", "planned_date": "", "actual_date": "", "predecessors": "M06", "status": "Open"},
            {"id": "M08", "name": "Gate 5 Review", "phase": "P5", "planned_date": "", "actual_date": "", "predecessors": "M07", "status": "Open"},
        ]

    for i, ms in enumerate(milestones, start=4):
        ws.cell(row=i, column=1, value=ms.get("id", ""))
        ws.cell(row=i, column=2, value=ms.get("name", ""))
        ws.cell(row=i, column=3, value=ms.get("phase", ""))
        ws.cell(row=i, column=4, value=ms.get("planned_date", ""))
        ws.cell(row=i, column=5, value=ms.get("actual_date", ""))
        ws.cell(row=i, column=6, value=ms.get("predecessors", ""))
        ws.cell(row=i, column=7, value=ms.get("status", "Open"))

    stripe_body(ws, 4, 4 + len(milestones) - 1, 7)
    autosize(ws, {1: 14, 2: 28, 3: 10, 4: 14, 5: 14, 6: 20, 7: 12})


def build_gate_reviews(wb: Workbook, data: dict) -> None:
    """10_Gate_Reviews — Phase gate review schedule and exit criteria."""
    ws = wb.create_sheet("10_Gate_Reviews")

    style_title_row(ws, 1, 6, "Phase Gate Reviews")

    headers = ["Gate ID", "Phase Exit", "Planned Date", "Exit Criteria", "Status", "Notes"]
    style_header_row(ws, 3, headers)

    gate_reviews = data.get("gate_reviews", [])
    if not gate_reviews:
        gate_reviews = [
            {"id": "G1", "phase_exit": "P1", "planned_date": "", "exit_criteria": "VOC captured, BOM and process flow preliminary, team aligned", "status": "Open", "notes": ""},
            {"id": "G2", "phase_exit": "P2", "planned_date": "", "exit_criteria": "Design complete, DFMEA approved, DVP&R plan ready, prototype built", "status": "Open", "notes": ""},
            {"id": "G3", "phase_exit": "P3", "planned_date": "", "exit_criteria": "Process flow finalized, PFMEA complete, MSA and PPC plan approved", "status": "Open", "notes": ""},
            {"id": "G4", "phase_exit": "P4", "planned_date": "", "exit_criteria": "PRR successful, PPC data acceptable, PPAP ready, production @ rate", "status": "Open", "notes": ""},
            {"id": "G5", "phase_exit": "P5", "planned_date": "", "exit_criteria": "Variation reduced, customer satisfaction confirmed, lessons learned", "status": "Open", "notes": ""},
        ]

    for i, gr in enumerate(gate_reviews, start=4):
        ws.cell(row=i, column=1, value=gr.get("id", ""))
        ws.cell(row=i, column=2, value=gr.get("phase_exit", ""))
        ws.cell(row=i, column=3, value=gr.get("planned_date", ""))
        ws.cell(row=i, column=4, value=gr.get("exit_criteria", ""))
        ws.cell(row=i, column=5, value=gr.get("status", "Open"))
        ws.cell(row=i, column=6, value=gr.get("notes", ""))

    stripe_body(ws, 4, 4 + len(gate_reviews) - 1, 6)
    autosize(ws, {1: 12, 2: 12, 3: 14, 4: 50, 5: 12, 6: 25})


def build_special_characteristics(wb: Workbook, data: dict) -> None:
    """11_Special_Characteristics — SC/CC list with source and control method."""
    ws = wb.create_sheet("11_Special_Characteristics")

    style_title_row(ws, 1, 5, "Special Characteristics")

    headers = ["SC/CC ID", "Characteristic", "Type (SC/CC)", "Source (CTQ/CSL/Regulatory)", "Control Method"]
    style_header_row(ws, 3, headers)

    special_chars = data.get("special_characteristics", [])
    if not special_chars:
        special_chars = [
            {"id": "SC-001", "characteristic": "Overall Dimension", "type": "SC", "source": "CTQ", "control_method": "CMM, 100%"},
            {"id": "SC-002", "characteristic": "Function / Performance", "type": "CC", "source": "CSL", "control_method": "Functional test"},
            {"id": "SC-003", "characteristic": "Surface Finish", "type": "SC", "source": "Regulatory", "control_method": "Profilometer"},
            {"id": "SC-004", "characteristic": "Material / Weight", "type": "SC", "source": "CTQ", "control_method": "Certificate of analysis"},
        ]

    for i, sc in enumerate(special_chars, start=4):
        ws.cell(row=i, column=1, value=sc.get("id", ""))
        ws.cell(row=i, column=2, value=sc.get("characteristic", ""))
        ws.cell(row=i, column=3, value=sc.get("type", "SC"))
        ws.cell(row=i, column=4, value=sc.get("source", "CTQ"))
        ws.cell(row=i, column=5, value=sc.get("control_method", ""))

    stripe_body(ws, 4, 4 + len(special_chars) - 1, 5)
    autosize(ws, {1: 12, 2: 30, 3: 12, 4: 25, 5: 30})


def build_risk_register(wb: Workbook, data: dict) -> None:
    """12_Risk_Register — Program-level risks with likelihood, impact, mitigation."""
    ws = wb.create_sheet("12_Risk_Register")

    style_title_row(ws, 1, 6, "Program Risk Register")

    headers = ["Risk ID", "Description", "Likelihood", "Impact", "Mitigation", "Owner"]
    style_header_row(ws, 3, headers)

    risks = data.get("risks", [])
    if not risks:
        risks = [
            {"id": "R01", "description": "Supplier capacity constraints", "likelihood": "Medium", "impact": "High", "mitigation": "Capacity planning, backup supplier", "owner": "SQ"},
            {"id": "R02", "description": "Design complexity requiring design iteration", "likelihood": "Medium", "impact": "Medium", "mitigation": "Early design review, prototyping", "owner": "DE"},
            {"id": "R03", "description": "Process capability not met at trial run", "likelihood": "Low", "impact": "High", "mitigation": "MSA and PPC planning, process optimization", "owner": "Mfg"},
            {"id": "R04", "description": "Late customer requirement change", "likelihood": "Medium", "impact": "High", "mitigation": "Change control, impact analysis", "owner": "PM"},
            {"id": "R05", "description": "Key resource turnover", "likelihood": "Low", "impact": "High", "mitigation": "Cross-training, documentation", "owner": "HR"},
            {"id": "R06", "description": "Supply chain delay", "likelihood": "Medium", "impact": "Medium", "mitigation": "Supplier agreement, buffer stock", "owner": "SQ"},
        ]

    for i, risk in enumerate(risks, start=4):
        ws.cell(row=i, column=1, value=risk.get("id", ""))
        ws.cell(row=i, column=2, value=risk.get("description", ""))
        ws.cell(row=i, column=3, value=risk.get("likelihood", ""))
        ws.cell(row=i, column=4, value=risk.get("impact", ""))
        ws.cell(row=i, column=5, value=risk.get("mitigation", ""))
        ws.cell(row=i, column=6, value=risk.get("owner", ""))

    stripe_body(ws, 4, 4 + len(risks) - 1, 6)
    autosize(ws, {1: 10, 2: 35, 3: 12, 4: 10, 5: 30, 6: 12})


def build_open_items_tracker(wb: Workbook) -> None:
    """13_Open_Items_Tracker — Action items and open issues."""
    ws = wb.create_sheet("13_Open_Items_Tracker")

    style_title_row(ws, 1, 6, "Open Items Tracker")

    headers = ["Item ID", "Description", "Owner", "Due Date", "Status", "Notes"]
    style_header_row(ws, 3, headers)

    items = [
        ("OI-001", "", "", "", "Open", ""),
        ("OI-002", "", "", "", "Open", ""),
    ]

    for i, (item_id, desc, owner, due, status, notes) in enumerate(items, start=4):
        ws.cell(row=i, column=1, value=item_id)
        ws.cell(row=i, column=2, value=desc)
        ws.cell(row=i, column=3, value=owner)
        ws.cell(row=i, column=4, value=due)
        ws.cell(row=i, column=5, value=status)
        ws.cell(row=i, column=6, value=notes)

    stripe_body(ws, 4, 4 + len(items) - 1, 6)
    autosize(ws, {1: 10, 2: 35, 3: 15, 4: 14, 5: 12, 6: 25})


def build_references(wb: Workbook) -> None:
    """14_References — Customer requirements, IATF 16949, AIAG APQP manual."""
    ws = wb.create_sheet("14_References")

    style_title_row(ws, 1, 3, "References")

    headers = ["Reference", "Title", "Notes"]
    style_header_row(ws, 3, headers)

    references = [
        ("AIAG APQP", "APQP Manual, 2nd Edition", "Advanced Product Quality Planning"),
        ("AIAG PPAP", "PPAP Manual, 4th Edition", "Production Part Approval Process"),
        ("AIAG FMEA", "FMEA Manual, 5th Edition (AIAG-VDA)", "Failure Mode and Effects Analysis"),
        ("IATF 16949", "Quality Management System Standard", "Automotive Industry Requirements"),
        ("ISO/TS 16949", "Previous automotive quality standard", "For reference only if applicable"),
        ("Customer Drawing", "", "Link or reference to customer design"),
        ("Customer Specifications", "", "Link or reference to CSL/CTQ requirements"),
        ("Internal Procedure", "", "Quality, Manufacturing, Engineering procedures"),
    ]

    for i, (ref, title, notes) in enumerate(references, start=4):
        ws.cell(row=i, column=1, value=ref)
        ws.cell(row=i, column=2, value=title)
        ws.cell(row=i, column=3, value=notes)

    stripe_body(ws, 4, 4 + len(references) - 1, 3)
    autosize(ws, {1: 25, 2: 50, 3: 30})


def main() -> None:
    """Generate APQP Master Plan workbook from JSON input."""
    if len(sys.argv) != 3:
        print("Usage: python generate_apqp_plan.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: input file not found: {input_file}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    # Build all 15 tabs in order
    build_title_page(wb, data)
    build_document_control(wb)
    build_program_info(wb, data)
    build_cross_functional_team(wb, data)
    build_phase_deliverables(wb, 1, "Plan and Define Program", data)
    build_phase_deliverables(wb, 2, "Product Design and Development", data)
    build_phase_deliverables(wb, 3, "Process Design and Development", data)
    build_phase_deliverables(wb, 4, "Product and Process Validation", data)
    build_phase_deliverables(wb, 5, "Feedback and Assessment", data)
    build_master_schedule(wb, data)
    build_gate_reviews(wb, data)
    build_special_characteristics(wb, data)
    build_risk_register(wb, data)
    build_open_items_tracker(wb)
    build_references(wb)

    wb.save(str(output_file))
    print(f"APQP Master Plan generated: {output_file}")
    print(f"Tabs: {len(wb.sheetnames)} — {', '.join(wb.sheetnames)}")


if __name__ == "__main__":
    main()
