"""
TARA Builder — generates a multi-tab ISO/SAE 21434 Threat Analysis and Risk Assessment (TARA) workbook.

Usage:
    python generate_tara.py <input.json> <output.xlsx>

Input JSON schema:
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver, company},
  "target_cal": "1|2|3|4",
  "scope_description": str,
  "scope_boundary_notes": str,
  "assumptions": [{id, category, assumption, rationale}],
  "cyber_interfaces": [{id, interface, direction, protocol, description}],
  "assets": [
    {id, name, location, asset_type, properties: [C|I|A|Auth|Authz|NR], rationale}
  ],
  "threat_scenarios": [
    {id, asset_id, stride_category, threat_description, threat_agent, rationale}
  ],
  "impact_ratings": [
    {scenario_id, safety, financial, operational, privacy, worst_impact, rationale}
  ],
  "attack_path_analysis": [
    {scenario_id, entry_point, attack_vector, preconditions, propagation, exit_point}
  ],
  "feasibility_ratings": [
    {scenario_id, elapsed_time, expertise, knowledge, opportunity, equipment, overall_feasibility, rationale}
  ],
  "risk_overrides": [
    {scenario_id, impact, feasibility, risk_value, override_rationale}
  ],
  "treatment_decisions": [
    {scenario_id, treatment_type, rationale, residual_acceptable, owner, target_date}
  ]
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
from openpyxl.worksheet.table import Table, TableStyleInfo


# ---------------------------------------------------------------------------
# Styling Helpers (mirrored from HARA builder)
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"
ORANGE_MED = "F4B084"
YELLOW_MED = "FFE699"
GREEN_DARK = "92D050"

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


# Risk Value lookup table
RISK_MATRIX = {
    ("Negligible", "Very Low"): 1,
    ("Negligible", "Low"): 2,
    ("Negligible", "Medium"): 2,
    ("Negligible", "High"): 3,
    ("Moderate", "Very Low"): 2,
    ("Moderate", "Low"): 3,
    ("Moderate", "Medium"): 3,
    ("Moderate", "High"): 5,
    ("Major", "Very Low"): 3,
    ("Major", "Low"): 4,
    ("Major", "Medium"): 5,
    ("Major", "High"): 5,
    ("Severe", "Very Low"): 4,
    ("Severe", "Low"): 5,
    ("Severe", "Medium"): 5,
    ("Severe", "High"): 5,
}

RISK_COLORS = {
    5: "C00000",  # Critical Red
    4: "F4B084",  # Orange
    3: "FFE699",  # Yellow
    2: "C6EFCE",  # Light Green
    1: "92D050",  # Dark Green
}

CAL_COLORS = {
    "4": "C00000",  # Critical Red
    "3": "F4B084",  # Orange
    "2": "FFE699",  # Yellow
    "1": "C6EFCE",  # Light Green
}


def compute_risk_value(impact: str, feasibility: str) -> int:
    """Look up Risk Value from Impact x Feasibility matrix."""
    return RISK_MATRIX.get((impact, feasibility), 3)


# ---------------------------------------------------------------------------
# Tab Builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, item: dict, target_cal: str) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 2, 4, "Threat Analysis and Risk Assessment (TARA)")
    style_title_row(ws, 3, 4, f"{item.get('name', '')}  ({item.get('abbr', '')})")

    fields = [
        ("Project", item.get("project", "")),
        ("Document ID", item.get("doc_id", "")),
        ("Revision", item.get("revision", "")),
        ("Date", item.get("date", "")),
        ("Author", item.get("author", "")),
        ("Approver", item.get("approver", "")),
        ("Company", item.get("company", "")),
        ("Standard", "ISO/SAE 21434:2021, Clause 15 (TARA)"),
        ("Methodology", "7-Step STRIDE + Impact × Feasibility Risk Determination"),
        ("Target CAL", f"CAL {target_cal}"),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left")
        row += 1

    autosize(ws, {1: 4, 2: 22, 3: 60, 4: 4})


def build_doc_control(wb: Workbook) -> None:
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 5, "Document Control")

    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of change", "Approver"])
    placeholders = [
        ("0.1", "", "", "Initial TARA generated by tara-builder skill", ""),
        ("0.2", "", "", "Threat scenario and risk assessment review", ""),
        ("1.0", "", "", "Released for CSG derivation", ""),
    ]
    for i, row_data in enumerate(placeholders, start=4):
        for col, val in enumerate(row_data, start=1):
            ws.cell(row=i, column=col, value=val)
    stripe_body(ws, 4, 4 + len(placeholders) - 1, 5)

    # Distribution list
    style_title_row(ws, 10, 5, "Distribution List")
    style_header_row(ws, 11, ["Name", "Role", "Organization", "Email", "Notes"])
    for i in range(12, 16):
        for c in range(1, 6):
            ws.cell(row=i, column=c, value="")
    stripe_body(ws, 12, 15, 5)

    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_assumptions(wb: Workbook, assumptions: list[dict]) -> None:
    ws = wb.create_sheet("02_Assumptions")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Assumptions: Item Scope, Attacker Model, Environment")

    style_header_row(ws, 3, ["ID", "Category", "Assumption", "Rationale"])
    if not assumptions:
        assumptions = [
            {"id": "A01", "category": "Item Scope", "assumption": "Item includes all ECU firmware and interfaces; OTA update infrastructure separate.", "rationale": "Scope boundary per item definition."},
            {"id": "A02", "category": "Attacker Model", "assumption": "Threat agent capability ranges from casual hacker to nation-state.", "rationale": "Defense-in-breadth per ISO/SAE 21434."},
            {"id": "A03", "category": "Environment", "assumption": "Vehicle operates in road transport (light-duty passenger).", "rationale": "Market segment per business requirements."},
            {"id": "A04", "category": "Connectivity", "assumption": "Vehicle equipped with OBD-II, CAN, and optional telematics.", "rationale": "Modern vehicle assumption."},
            {"id": "A05", "category": "Development", "assumption": "Third-party suppliers involved in ECU development; supply chain integrity assumed.", "rationale": "Cybersecurity scope partition; supply chain risk assessed separately."},
        ]
    for i, a in enumerate(assumptions, start=4):
        ws.cell(row=i, column=1, value=a.get("id", ""))
        ws.cell(row=i, column=2, value=a.get("category", ""))
        ws.cell(row=i, column=3, value=a.get("assumption", ""))
        ws.cell(row=i, column=4, value=a.get("rationale", ""))
    stripe_body(ws, 4, 3 + len(assumptions), 4)
    autosize(ws, {1: 8, 2: 16, 3: 60, 4: 40})


def build_item_description(wb: Workbook, scope: str, boundary_notes: str, cyber_interfaces: list[dict]) -> None:
    ws = wb.create_sheet("03_Item_Description")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Item Description and Cyber-Relevant Interfaces")

    ws.cell(row=3, column=1, value="Item Scope").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells(start_row=3, start_column=2, end_row=3, end_column=5)
    ws.cell(row=3, column=2, value=scope or "(Describe item, functions, and what it does NOT do.)").alignment = Alignment(wrap_text=True, vertical="top")

    ws.cell(row=5, column=1, value="Cyber Boundary").font = Font(name=FONT_NAME, bold=True, size=11, color=NAVY)
    ws.merge_cells(start_row=5, start_column=2, end_row=5, end_column=5)
    ws.cell(row=5, column=2, value=boundary_notes or "(Describe cyber-physical boundary: what connects, what doesn't, attack surfaces.)").alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[5].height = 60

    # Cyber Interfaces
    style_title_row(ws, 8, 5, "Cyber-Relevant Interfaces")
    style_header_row(ws, 9, ["Interface ID", "Interface / Protocol", "Direction", "Threat Relevance", "Notes"])
    if not cyber_interfaces:
        cyber_interfaces = [
            {"id": "CI01", "interface": "OBD-II (CAN)", "direction": "Bidirectional", "threat": "Diagnostic read/write; message injection", "notes": ""},
            {"id": "CI02", "interface": "CAN bus (internal)", "direction": "Broadcast", "threat": "Message injection; eavesdropping", "notes": ""},
            {"id": "CI03", "interface": "Telematics (cellular/WiFi)", "direction": "Bidirectional", "threat": "Remote command injection; eavesdropping", "notes": ""},
        ]
    for i, intf in enumerate(cyber_interfaces, start=10):
        ws.cell(row=i, column=1, value=intf.get("id", ""))
        ws.cell(row=i, column=2, value=intf.get("interface", ""))
        ws.cell(row=i, column=3, value=intf.get("direction", ""))
        ws.cell(row=i, column=4, value=intf.get("threat", ""))
        ws.cell(row=i, column=5, value=intf.get("notes", ""))
    stripe_body(ws, 10, 9 + len(cyber_interfaces), 5)
    autosize(ws, {1: 14, 2: 26, 3: 14, 4: 40, 5: 30})


def build_asset_inventory(wb: Workbook, assets: list[dict]) -> None:
    ws = wb.create_sheet("04_Asset_Inventory")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Asset Inventory")

    style_header_row(ws, 3, ["Asset ID", "Asset Name", "Location", "Asset Type", "Cybersecurity Properties", "Value Rationale"])
    for i, asset in enumerate(assets, start=4):
        properties = ", ".join(asset.get("properties", []))
        ws.cell(row=i, column=1, value=asset.get("id", ""))
        ws.cell(row=i, column=2, value=asset.get("name", ""))
        ws.cell(row=i, column=3, value=asset.get("location", ""))
        ws.cell(row=i, column=4, value=asset.get("asset_type", ""))
        ws.cell(row=i, column=5, value=properties)
        ws.cell(row=i, column=6, value=asset.get("rationale", ""))
    stripe_body(ws, 4, 3 + len(assets), 6)
    autosize(ws, {1: 10, 2: 24, 3: 20, 4: 18, 5: 24, 6: 40})


def build_threat_scenarios(wb: Workbook, scenarios: list[dict]) -> None:
    ws = wb.create_sheet("05_Threat_Scenarios")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Threat Scenarios (STRIDE)")

    style_header_row(ws, 3, ["Scenario ID", "Asset ID", "STRIDE Category", "Threat Description", "Threat Agent", "Rationale"])
    for i, scenario in enumerate(scenarios, start=4):
        ws.cell(row=i, column=1, value=scenario.get("id", ""))
        ws.cell(row=i, column=2, value=scenario.get("asset_id", ""))
        ws.cell(row=i, column=3, value=scenario.get("stride_category", ""))
        ws.cell(row=i, column=4, value=scenario.get("threat_description", ""))
        ws.cell(row=i, column=5, value=scenario.get("threat_agent", ""))
        ws.cell(row=i, column=6, value=scenario.get("rationale", ""))
    stripe_body(ws, 4, 3 + len(scenarios), 6)
    autosize(ws, {1: 12, 2: 10, 3: 16, 4: 50, 5: 18, 6: 40})


def build_impact_assessment(wb: Workbook, impact_ratings: list[dict]) -> None:
    ws = wb.create_sheet("06_Impact_Assessment")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 7, "Impact Assessment (Safety / Financial / Operational / Privacy)")

    style_header_row(ws, 3, ["Scenario ID", "Safety", "Financial", "Operational", "Privacy", "Overall Impact", "Rationale"])
    for i, impact in enumerate(impact_ratings, start=4):
        overall = impact.get("worst_impact", "")
        ws.cell(row=i, column=1, value=impact.get("scenario_id", ""))
        ws.cell(row=i, column=2, value=impact.get("safety", ""))
        ws.cell(row=i, column=3, value=impact.get("financial", ""))
        ws.cell(row=i, column=4, value=impact.get("operational", ""))
        ws.cell(row=i, column=5, value=impact.get("privacy", ""))
        overall_cell = ws.cell(row=i, column=6, value=overall)
        ws.cell(row=i, column=7, value=impact.get("rationale", ""))

        # Color overall impact
        impact_colors = {"Severe": RED_BAD, "Major": ORANGE_MED, "Moderate": YELLOW_MED, "Negligible": GREEN_OK}
        if overall in impact_colors:
            overall_cell.fill = PatternFill("solid", fgColor=impact_colors[overall])

    stripe_body(ws, 4, 3 + len(impact_ratings), 7)
    autosize(ws, {1: 12, 2: 12, 3: 12, 4: 14, 5: 12, 6: 14, 7: 40})


def build_attack_path_analysis(wb: Workbook, attack_paths: list[dict]) -> None:
    ws = wb.create_sheet("07_Attack_Path_Analysis")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Attack Path Analysis")

    style_header_row(ws, 3, ["Scenario ID", "Entry Point", "Attack Vector", "Preconditions", "Propagation Steps", "Exit Point"])
    for i, path in enumerate(attack_paths, start=4):
        ws.cell(row=i, column=1, value=path.get("scenario_id", ""))
        ws.cell(row=i, column=2, value=path.get("entry_point", ""))
        ws.cell(row=i, column=3, value=path.get("attack_vector", ""))
        ws.cell(row=i, column=4, value=path.get("preconditions", ""))
        ws.cell(row=i, column=5, value=path.get("propagation", ""))
        ws.cell(row=i, column=6, value=path.get("exit_point", ""))
    stripe_body(ws, 4, 3 + len(attack_paths), 6)
    autosize(ws, {1: 12, 2: 16, 3: 16, 4: 20, 5: 30, 6: 16})


def build_feasibility_rating(wb: Workbook, feasibility_ratings: list[dict]) -> None:
    ws = wb.create_sheet("08_Feasibility_Rating")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "Attack Feasibility Rating (5 Factors)")

    style_header_row(ws, 3, ["Scenario ID", "Elapsed Time", "Expertise", "Knowledge", "Opportunity", "Equipment", "Overall Feasibility", "Rationale"])
    for i, feasibility in enumerate(feasibility_ratings, start=4):
        overall = feasibility.get("overall_feasibility", "")
        ws.cell(row=i, column=1, value=feasibility.get("scenario_id", ""))
        ws.cell(row=i, column=2, value=feasibility.get("elapsed_time", ""))
        ws.cell(row=i, column=3, value=feasibility.get("expertise", ""))
        ws.cell(row=i, column=4, value=feasibility.get("knowledge", ""))
        ws.cell(row=i, column=5, value=feasibility.get("opportunity", ""))
        ws.cell(row=i, column=6, value=feasibility.get("equipment", ""))
        overall_cell = ws.cell(row=i, column=7, value=overall)
        ws.cell(row=i, column=8, value=feasibility.get("rationale", ""))

        # Color overall feasibility
        feas_colors = {"Very Low": GREEN_DARK, "Low": GREEN_OK, "Medium": YELLOW_MED, "High": RED_BAD}
        if overall in feas_colors:
            overall_cell.fill = PatternFill("solid", fgColor=feas_colors[overall])

    stripe_body(ws, 4, 3 + len(feasibility_ratings), 8)
    autosize(ws, {1: 12, 2: 14, 3: 14, 4: 14, 5: 14, 6: 14, 7: 16, 8: 40})


def build_risk_determination(wb: Workbook, scenarios: list[dict], impact_index: dict, feasibility_index: dict, overrides: list[dict]) -> list[dict]:
    ws = wb.create_sheet("09_Risk_Determination")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 4, "Risk Determination (Impact x Feasibility Lookup)")

    style_header_row(ws, 3, ["Scenario ID", "Impact", "Feasibility", "Risk Value"])

    # Index overrides by scenario_id
    override_index = {o["scenario_id"]: o for o in overrides}

    risk_rows = []
    for i, scenario in enumerate(scenarios, start=4):
        scenario_id = scenario["id"]
        impact_data = impact_index.get(scenario_id, {})
        feas_data = feasibility_index.get(scenario_id, {})

        impact = impact_data.get("worst_impact", "Moderate")
        feasibility = feas_data.get("overall_feasibility", "Medium")

        # Check for override
        if scenario_id in override_index:
            risk_value = override_index[scenario_id].get("risk_value", compute_risk_value(impact, feasibility))
        else:
            risk_value = compute_risk_value(impact, feasibility)

        ws.cell(row=i, column=1, value=scenario_id)
        ws.cell(row=i, column=2, value=impact)
        ws.cell(row=i, column=3, value=feasibility)
        risk_cell = ws.cell(row=i, column=4, value=risk_value)

        # Color risk cell
        if risk_value in RISK_COLORS:
            risk_cell.fill = PatternFill("solid", fgColor=RISK_COLORS[risk_value])
            risk_cell.font = Font(name=FONT_NAME, bold=True, color="FFFFFF" if risk_value >= 4 else "000000")
            risk_cell.alignment = Alignment(horizontal="center", vertical="center")

        risk_rows.append({
            "scenario_id": scenario_id,
            "impact": impact,
            "feasibility": feasibility,
            "risk_value": risk_value,
            **scenario,
        })

    stripe_body(ws, 4, 3 + len(scenarios), 4)
    autosize(ws, {1: 12, 2: 14, 3: 14, 4: 12})

    return risk_rows


def build_risk_treatment(wb: Workbook, risk_rows: list[dict], treatments: list[dict]) -> None:
    ws = wb.create_sheet("10_Risk_Treatment")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "Risk Treatment Decisions")

    style_header_row(ws, 3, ["Scenario ID", "Risk Value", "Treatment Type", "Rationale", "Residual Risk Acceptable", "Owner"])

    # Index treatments by scenario_id
    treatment_index = {t["scenario_id"]: t for t in treatments}

    for i, risk_row in enumerate(risk_rows, start=4):
        scenario_id = risk_row["scenario_id"]
        treatment = treatment_index.get(scenario_id, {})

        ws.cell(row=i, column=1, value=scenario_id)
        risk_cell = ws.cell(row=i, column=2, value=risk_row["risk_value"])
        if risk_row["risk_value"] in RISK_COLORS:
            risk_cell.fill = PatternFill("solid", fgColor=RISK_COLORS[risk_row["risk_value"]])

        ws.cell(row=i, column=3, value=treatment.get("treatment_type", "Retain"))
        ws.cell(row=i, column=4, value=treatment.get("rationale", ""))
        ws.cell(row=i, column=5, value="Yes" if treatment.get("residual_acceptable", True) else "No")
        ws.cell(row=i, column=6, value=treatment.get("owner", ""))

    stripe_body(ws, 4, 3 + len(risk_rows), 6)
    autosize(ws, {1: 12, 2: 12, 3: 14, 4: 50, 5: 18, 6: 16})


def build_cybersecurity_goals(wb: Workbook, risk_rows: list[dict], target_cal: str) -> None:
    ws = wb.create_sheet("11_Cybersecurity_Goals")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Cybersecurity Goals (Derived from Risk >= 3)")

    style_header_row(ws, 3, ["CSG ID", "Derived From Scenario", "Cybersecurity Goal", "Risk Value", "CAL"])

    # Filter high-risk scenarios
    high_risk = [r for r in risk_rows if r["risk_value"] >= 3]

    csg_id = 1
    for i, risk_row in enumerate(high_risk, start=4):
        scenario_id = risk_row["scenario_id"]
        threat_desc = risk_row.get("threat_description", "Threat")
        csg_text = f"Prevent {threat_desc}"

        # Assign CAL based on risk and target CAL
        if risk_row["risk_value"] == 5:
            assigned_cal = "4" if target_cal in ["3", "4"] else "3"
        elif risk_row["risk_value"] == 4:
            assigned_cal = "3" if target_cal in ["2", "3", "4"] else "2"
        else:
            assigned_cal = target_cal

        ws.cell(row=i, column=1, value=f"CSG-{csg_id:03d}")
        ws.cell(row=i, column=2, value=scenario_id)
        ws.cell(row=i, column=3, value=csg_text)
        risk_cell = ws.cell(row=i, column=4, value=risk_row["risk_value"])
        if risk_row["risk_value"] in RISK_COLORS:
            risk_cell.fill = PatternFill("solid", fgColor=RISK_COLORS[risk_row["risk_value"]])

        cal_cell = ws.cell(row=i, column=5, value=assigned_cal)
        if assigned_cal in CAL_COLORS:
            cal_cell.fill = PatternFill("solid", fgColor=CAL_COLORS[assigned_cal])
            cal_cell.font = Font(name=FONT_NAME, bold=True, color="FFFFFF" if assigned_cal == "4" else "000000")

        csg_id += 1

    if high_risk:
        stripe_body(ws, 4, 3 + len(high_risk), 5)
    else:
        ws.cell(row=4, column=1, value="(No Risk >= 3 scenarios; no CSGs derived.)").font = body_font()

    autosize(ws, {1: 10, 2: 18, 3: 50, 4: 12, 5: 8})


def build_references(wb: Workbook) -> None:
    ws = wb.create_sheet("12_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 2, "References and Standards")

    refs = [
        ("ISO/SAE 21434:2021", "Cybersecurity for road vehicles; Clause 15 TARA process"),
        ("STRIDE", "Threat modeling framework: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege"),
        ("NHTSA", "Best Practices for Automotive Cybersecurity (2016)"),
        ("AUTOSAR", "Classic & Adaptive platforms; Secure Onboard Communication (SecOC)"),
        ("ETSI", "Cybersecurity standards for connected and autonomous vehicles"),
    ]

    row = 3
    for ref_name, ref_desc in refs:
        ws.cell(row=row, column=1, value=ref_name).font = Font(name=FONT_NAME, bold=True, size=10)
        ws.cell(row=row, column=2, value=ref_desc)
        row += 1

    stripe_body(ws, 3, 2 + len(refs), 2)
    autosize(ws, {1: 24, 2: 70})


# ---------------------------------------------------------------------------
# Main Generator
# ---------------------------------------------------------------------------

def generate(input_path: str, output_path: str) -> dict:
    with open(input_path) as f:
        data = json.load(f)

    item = data.get("item", {})
    target_cal = data.get("target_cal", "2")
    scenarios = data.get("threat_scenarios", [])
    if not scenarios:
        raise ValueError("Input must include at least one threat scenario.")

    assets = data.get("assets", []) or []
    cyber_interfaces = data.get("cyber_interfaces", []) or []
    assumptions = data.get("assumptions", []) or []
    impact_ratings = data.get("impact_ratings", []) or []
    attack_paths = data.get("attack_path_analysis", []) or []
    feasibility_ratings = data.get("feasibility_ratings", []) or []
    treatments = data.get("treatment_decisions", []) or []
    overrides = data.get("risk_overrides", []) or []

    # Build indices for lookups
    impact_index = {r["scenario_id"]: r for r in impact_ratings}
    feasibility_index = {r["scenario_id"]: r for r in feasibility_ratings}

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, item, target_cal)
    build_doc_control(wb)
    build_assumptions(wb, assumptions)
    build_item_description(wb, data.get("scope_description", ""), data.get("scope_boundary_notes", ""), cyber_interfaces)
    build_asset_inventory(wb, assets)
    build_threat_scenarios(wb, scenarios)
    build_impact_assessment(wb, impact_ratings)
    build_attack_path_analysis(wb, attack_paths)
    build_feasibility_rating(wb, feasibility_ratings)

    # Risk determination returns risk rows for subsequent tabs
    risk_rows = build_risk_determination(wb, scenarios, impact_index, feasibility_index, overrides)

    build_risk_treatment(wb, risk_rows, treatments)
    build_cybersecurity_goals(wb, risk_rows, target_cal)
    build_references(wb)

    wb.active = 0
    wb.save(output_path)

    # Count high-risk scenarios
    high_risk_count = len([r for r in risk_rows if r["risk_value"] >= 3])

    return {
        "assets": len(assets),
        "threat_scenarios": len(scenarios),
        "impact_ratings": len(impact_ratings),
        "feasibility_ratings": len(feasibility_ratings),
        "high_risk_scenarios": high_risk_count,
        "risk_distribution": {
            "risk_5": len([r for r in risk_rows if r["risk_value"] == 5]),
            "risk_4": len([r for r in risk_rows if r["risk_value"] == 4]),
            "risk_3": len([r for r in risk_rows if r["risk_value"] == 3]),
            "risk_2": len([r for r in risk_rows if r["risk_value"] == 2]),
            "risk_1": len([r for r in risk_rows if r["risk_value"] == 1]),
        },
        "output_path": output_path,
    }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_tara.py <input.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)
    summary = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(summary, indent=2))
