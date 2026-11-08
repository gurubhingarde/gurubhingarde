"""
CS Goals Builder — generates a multi-tab ISO/SAE 21434 Cybersecurity Goals workbook
from a TARA xlsx and optional refinement JSON.

Usage:
    python generate_cs_goals.py <tara.xlsx> [refinement.json] <output.xlsx>

Reads high-risk threat scenarios from TARA (09_Risk_Determination or 11_Cybersecurity_Goals),
optionally applies refinements from a JSON input, and produces an audit-ready workbook with
8 tabs covering cybersecurity goals, CAL determination, asset mapping, and concept handoff.

Input JSON schema (optional refinement):
{
  "item": {name, abbr, project, doc_id, revision, date, author, approver},
  "target_cal": "CAL 3",  // default target
  "csg_overrides": [
      {csg_id, asset, cs_goal_text, cal_override, property, owner}
  ],
  "csg_refinements": [
      {threat_scenario_id, asset, refined_goal_text, cal_adjust}
  ]
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

from tara_reader import read_tara_xlsx


# Styling
FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
CAL_4_RED = "F4B084"  # Red-orange
CAL_3_ORANGE = "FED8B1"  # Orange
CAL_2_YELLOW = "FFFFE0"  # Light yellow
CAL_1_GREEN = "C6EFCE"  # Green

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def title_font(size: int = 16) -> Font:
    return Font(name=FONT_NAME, size=size, bold=True, color="FFFFFF")


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def build_cs_goals_workbook(
    tara_path: str,
    refinement_json_path: str | None,
    output_path: str,
    item_metadata: dict = None
) -> dict:
    """
    Main orchestrator: reads TARA, applies refinements, generates 8-tab workbook.

    Returns summary dict with tab count and CSG counts per CAL.
    """

    # Read TARA
    tara_data = read_tara_xlsx(tara_path)
    csg_list = tara_data["csg_goals"]
    threat_list = tara_data["threat_scenarios"]
    assets = tara_data["assets"]

    # Load refinement JSON if provided
    refinements = {}
    if refinement_json_path and Path(refinement_json_path).exists():
        with open(refinement_json_path) as f:
            refinements = json.load(f)
        item_metadata = refinements.get("item", item_metadata or {})
        _apply_csg_refinements(csg_list, refinements.get("csg_refinements", []))
        _apply_csg_overrides(csg_list, refinements.get("csg_overrides", []))

    if not item_metadata:
        item_metadata = {
            "name": "Electronic Stability Control",
            "abbr": "ESC",
            "project": "Autonomous Vehicle",
            "doc_id": "CSG-ESC-001",
            "revision": "1.0",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "author": "Cybersecurity Team",
            "approver": "Chief Safety Officer"
        }

    # Build workbook
    wb = Workbook()
    wb.remove(wb.active)

    # 00_Title_Page
    _create_title_page(wb, item_metadata, tara_path)

    # 01_Document_Control
    _create_document_control(wb, item_metadata)

    # 02_TARA_Echo
    _create_tara_echo(wb, threat_list)

    # 03_Cybersecurity_Goals
    _create_csg_tab(wb, csg_list, assets)

    # 04_CAL_Determination
    _create_cal_determination(wb, csg_list)

    # 05_Asset_to_CSG_Map
    _create_asset_csG_map(wb, csg_list, assets)

    # 06_CS_Concept_Handoff
    _create_cs_concept_handoff(wb, csg_list)

    # 07_References
    _create_references(wb)

    wb.save(output_path)

    # Return summary
    cal_dist = _count_cals(csg_list)
    return {
        "output_file": str(output_path),
        "tab_count": len(wb.sheetnames),
        "csg_count": len(csg_list),
        "cal_distribution": cal_dist,
        "sheetnames": wb.sheetnames
    }


def _apply_csg_refinements(csg_list: list, refinements: list):
    """Apply refinement changes to CSG goal text and CAL."""
    for refine in refinements:
        threat_id = refine.get("threat_scenario_id")
        refined_text = refine.get("refined_goal_text")
        cal_adjust = refine.get("cal_adjust")

        for csg in csg_list:
            if csg["threat_scenario_id"] == threat_id:
                if refined_text:
                    csg["cs_goal_text"] = refined_text
                if cal_adjust:
                    csg["cal_guidance"] = cal_adjust
                break


def _apply_csg_overrides(csg_list: list, overrides: list):
    """Apply explicit CSG overrides (e.g., CSG ID reassignment, owner assignment)."""
    for override in overrides:
        csg_id = override.get("csg_id")
        for csg in csg_list:
            if csg["csg_id"] == csg_id:
                if "asset" in override:
                    csg["asset"] = override["asset"]
                if "cs_goal_text" in override:
                    csg["cs_goal_text"] = override["cs_goal_text"]
                if "cal_override" in override:
                    csg["cal_guidance"] = override["cal_override"]
                if "property" in override:
                    csg["property"] = override["property"]
                if "owner" in override:
                    csg["owner"] = override["owner"]
                break


def _count_cals(csg_list: list) -> dict:
    """Count CSGs by CAL level."""
    dist = {"CAL 4": 0, "CAL 3": 0, "CAL 2": 0, "CAL 1": 0}
    for csg in csg_list:
        cal = csg.get("cal_guidance", "CAL 1")
        if cal in dist:
            dist[cal] += 1
    return dist


def _create_title_page(wb: Workbook, metadata: dict, tara_path: str):
    """00_Title_Page — Item, doc ID, revision, dates, target CAL, linked TARA."""
    ws = wb.create_sheet("00_Title_Page", 0)

    # Header
    ws.merge_cells("A1:D1")
    cell = ws["A1"]
    cell.value = "Cybersecurity Goals (CSG)"
    cell.font = title_font()
    cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # Item info
    row = 3
    items = [
        ("Item Name", metadata.get("name", "")),
        ("Item Abbreviation", metadata.get("abbr", "")),
        ("Project", metadata.get("project", "")),
        ("Document ID", metadata.get("doc_id", "")),
        ("Revision", metadata.get("revision", "")),
        ("Date", metadata.get("date", "")),
        ("Author", metadata.get("author", "")),
        ("Approver", metadata.get("approver", "")),
        ("Linked TARA", Path(tara_path).name),
    ]

    for label, value in items:
        ws.cell(row, 1).value = label
        ws.cell(row, 1).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row, 2).value = value
        row += 1

    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 40


def _create_document_control(wb: Workbook, metadata: dict):
    """01_Document_Control — Revision history."""
    ws = wb.create_sheet("01_Document_Control", 1)

    headers = ["Revision", "Date", "Author", "Change Description"]
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(1, col_idx)
        cell.value = header
        cell.font = header_font()
        cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
        cell.alignment = Alignment(horizontal="center")

    ws.cell(2, 1).value = metadata.get("revision", "1.0")
    ws.cell(2, 2).value = metadata.get("date", "")
    ws.cell(2, 3).value = metadata.get("author", "")
    ws.cell(2, 4).value = "Initial release"

    for col in range(1, 5):
        ws.column_dimensions[get_column_letter(col)].width = 20


def _create_tara_echo(wb: Workbook, threat_list: list):
    """02_TARA_Echo — Read-only echo of imported threat scenarios."""
    ws = wb.create_sheet("02_TARA_Echo", 2)

    headers = ["Threat_ID", "Asset", "Threat_Description", "Risk_Value"]
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(1, col_idx)
        cell.value = header
        cell.font = header_font()
        cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")

    for row_idx, threat in enumerate(threat_list, 2):
        ws.cell(row_idx, 1).value = threat.get("threat_id", "")
        ws.cell(row_idx, 2).value = threat.get("asset", "")
        ws.cell(row_idx, 3).value = threat.get("threat_description", "")
        ws.cell(row_idx, 4).value = threat.get("risk_value", "")

    for col in range(1, 5):
        ws.column_dimensions[get_column_letter(col)].width = 25


def _create_csg_tab(wb: Workbook, csg_list: list, assets: list):
    """03_Cybersecurity_Goals — One row per CS Goal."""
    ws = wb.create_sheet("03_Cybersecurity_Goals", 3)

    headers = [
        "CSG_ID", "Threat_Scenario_Ref", "Asset", "CS_Goal_Text",
        "CAL", "Cybersecurity_Property", "Residual_Risk_Acceptance", "Goal_Owner"
    ]

    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(1, col_idx)
        cell.value = header
        cell.font = header_font()
        cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")

    for row_idx, csg in enumerate(csg_list, 2):
        ws.cell(row_idx, 1).value = csg.get("csg_id", "")
        ws.cell(row_idx, 2).value = csg.get("threat_scenario_id", "")
        ws.cell(row_idx, 3).value = csg.get("asset", "")
        ws.cell(row_idx, 4).value = csg.get("cs_goal_text", "")

        cal = csg.get("cal_guidance", "CAL 1")
        ws.cell(row_idx, 5).value = cal
        ws.cell(row_idx, 5).fill = PatternFill(
            start_color=_cal_color(cal), end_color=_cal_color(cal), fill_type="solid"
        )

        ws.cell(row_idx, 6).value = csg.get("property") or "Not Determined"
        ws.cell(row_idx, 7).value = ""
        ws.cell(row_idx, 8).value = csg.get("owner", "")

    for col in range(1, 9):
        ws.column_dimensions[get_column_letter(col)].width = 20


def _create_cal_determination(wb: Workbook, csg_list: list):
    """04_CAL_Determination — Justification for each CSG's CAL."""
    ws = wb.create_sheet("04_CAL_Determination", 4)

    headers = ["CSG_ID", "Risk_Value", "CAL", "Impact_Rating", "Feasibility_Rating", "Justification"]
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(1, col_idx)
        cell.value = header
        cell.font = header_font()
        cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")

    for row_idx, csg in enumerate(csg_list, 2):
        risk = csg.get("risk_value", 3)
        cal = csg.get("cal_guidance", "CAL 1")

        ws.cell(row_idx, 1).value = csg.get("csg_id", "")
        ws.cell(row_idx, 2).value = risk
        ws.cell(row_idx, 3).value = cal
        ws.cell(row_idx, 3).fill = PatternFill(
            start_color=_cal_color(cal), end_color=_cal_color(cal), fill_type="solid"
        )
        ws.cell(row_idx, 4).value = _impact_rating(risk)
        ws.cell(row_idx, 5).value = "Medium"
        ws.cell(row_idx, 6).value = _cal_justification(risk, cal)

    for col in range(1, 7):
        ws.column_dimensions[get_column_letter(col)].width = 20


def _create_asset_csG_map(wb: Workbook, csg_list: list, assets: list):
    """05_Asset_to_CSG_Map — Cross-reference matrix."""
    ws = wb.create_sheet("05_Asset_to_CSG_Map", 5)

    # Create matrix: rows = assets, columns = CSG IDs
    csg_ids = [c.get("csg_id", "") for c in csg_list]

    # Header
    ws.cell(1, 1).value = "Asset"
    ws.cell(1, 1).font = header_font()
    ws.cell(1, 1).fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")

    for col_idx, csg_id in enumerate(csg_ids, 2):
        cell = ws.cell(1, col_idx)
        cell.value = csg_id
        cell.font = header_font()
        cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", wrap_text=True)

    # Data rows
    for row_idx, asset in enumerate(assets, 2):
        ws.cell(row_idx, 1).value = asset
        for col_idx, csg in enumerate(csg_list, 2):
            if csg.get("asset") == asset:
                ws.cell(row_idx, col_idx).value = "X"
                ws.cell(row_idx, col_idx).alignment = Alignment(horizontal="center")

    ws.column_dimensions["A"].width = 25
    for col_idx in range(2, len(csg_ids) + 2):
        ws.column_dimensions[get_column_letter(col_idx)].width = 12


def _create_cs_concept_handoff(wb: Workbook, csg_list: list):
    """06_CS_Concept_Handoff — Each CSG with placeholder CSC requirement rows."""
    ws = wb.create_sheet("06_CS_Concept_Handoff", 6)

    headers = ["CSG_ID", "CSG_Text", "CSC_ID", "Cybersecurity_Control_Requirement", "Category"]
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(1, col_idx)
        cell.value = header
        cell.font = header_font()
        cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")

    row = 2
    for csg in csg_list:
        ws.cell(row, 1).value = csg.get("csg_id", "")
        ws.cell(row, 2).value = csg.get("cs_goal_text", "")
        ws.cell(row, 3).value = ""
        ws.cell(row, 4).value = "TBD"
        ws.cell(row, 5).value = csg.get("property") or "Not Determined"
        row += 1

    for col in range(1, 6):
        ws.column_dimensions[get_column_letter(col)].width = 25


def _create_references(wb: Workbook):
    """07_References — Methodology and normative references."""
    ws = wb.create_sheet("07_References", 7)

    content = [
        ("ISO/SAE 21434", "Road vehicles — Cybersecurity engineering"),
        ("TARA", "Threat Analysis and Risk Assessment (source of CSG derivation)"),
        ("CAL", "Cybersecurity Assurance Level (1-4 per ISO/SAE 21434)"),
        ("CSG", "Cybersecurity Goal (high-level security objective per threat scenario)"),
        ("CSC", "Cybersecurity Control (technical requirement derived from CSG)"),
    ]

    ws.cell(1, 1).value = "Reference"
    ws.cell(1, 2).value = "Description"
    ws.cell(1, 1).font = header_font()
    ws.cell(1, 2).font = header_font()
    ws.cell(1, 1).fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
    ws.cell(1, 2).fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")

    for row_idx, (ref, desc) in enumerate(content, 2):
        ws.cell(row_idx, 1).value = ref
        ws.cell(row_idx, 2).value = desc

    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 50


def _cal_color(cal: str) -> str:
    """Return color code for CAL level."""
    if "4" in cal:
        return CAL_4_RED
    elif "3" in cal:
        return CAL_3_ORANGE
    elif "2" in cal:
        return CAL_2_YELLOW
    else:
        return CAL_1_GREEN


def _impact_rating(risk_value: int) -> str:
    """Derive impact rating from risk value."""
    if risk_value >= 5:
        return "Critical"
    elif risk_value == 4:
        return "High"
    elif risk_value == 3:
        return "Medium"
    else:
        return "Low"


def _cal_justification(risk_value: int, cal: str) -> str:
    """Generate CAL justification text."""
    if "4" in cal:
        return "Risk Value 5 + severe safety impact → CAL 4 required"
    elif "3" in cal:
        return "Risk Value 4 + significant safety impact → CAL 3"
    elif "2" in cal:
        return "Risk Value 3 + moderate risk → CAL 2"
    else:
        return "Risk Value 1-2 + low impact → CAL 1"


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_cs_goals.py <tara.xlsx> [refinement.json] <output.xlsx>")
        print("\nExample:")
        print("  python generate_cs_goals.py tara.xlsx output_goals.xlsx")
        print("  python generate_cs_goals.py tara.xlsx refinement.json output_goals.xlsx")
        sys.exit(1)

    if len(sys.argv) == 3:
        tara_path = sys.argv[1]
        output_path = sys.argv[2]
        refinement_path = None
    else:
        tara_path = sys.argv[1]
        refinement_path = sys.argv[2]
        output_path = sys.argv[3]

    result = build_cs_goals_workbook(tara_path, refinement_path, output_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
