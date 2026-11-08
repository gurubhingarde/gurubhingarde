"""
APQP Plan content probe — best-effort extractor for APQP Plan xlsx.

Returns a structured ProbedAPQPPlan dict that downstream check functions consume.
Works on apqp-plan-builder outputs and best-effort on others.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class TeamMember:
    name: str = ""
    role: str = ""
    organization: str = ""
    email: str = ""


@dataclass
class Deliverable:
    phase: str = ""
    name: str = ""
    owner: str = ""
    planned_date: str = ""
    actual_date: str = ""
    status: str = ""


@dataclass
class Milestone:
    gate_number: int = 0
    gate_name: str = ""
    planned_date: str = ""
    actual_date: str = ""
    exit_criteria: str = ""


@dataclass
class SpecialChar:
    char_name: str = ""
    type: str = ""
    source: str = ""
    oem_requirement: str = ""


@dataclass
class RiskItem:
    risk_id: str = ""
    description: str = ""
    severity: str = ""
    probability: str = ""
    mitigation: str = ""
    owner: str = ""


@dataclass
class OpenItem:
    item_id: str = ""
    description: str = ""
    owner: str = ""
    due_date: str = ""
    status: str = ""


@dataclass
class ProbedAPQPPlan:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""

    project: str = ""
    program: str = ""
    supplier: str = ""
    customer: str = ""

    sheet_names: list[str] = field(default_factory=list)

    program_manager: str = ""
    quality_lead: str = ""
    team_members: list[TeamMember] = field(default_factory=list)

    phase1_deliverables: list[Deliverable] = field(default_factory=list)
    phase2_deliverables: list[Deliverable] = field(default_factory=list)
    phase3_deliverables: list[Deliverable] = field(default_factory=list)
    phase4_deliverables: list[Deliverable] = field(default_factory=list)
    phase5_deliverables: list[Deliverable] = field(default_factory=list)

    milestones: list[Milestone] = field(default_factory=list)
    gate_reviews: list[dict] = field(default_factory=list)

    special_characteristics: list[SpecialChar] = field(default_factory=list)
    risks: list[RiskItem] = field(default_factory=list)
    open_items: list[OpenItem] = field(default_factory=list)

    is_apqp_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm(s: Any) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _find_sheet_by_keywords(sheet_names: list[str], keywords: list[str]) -> str:
    for name in sheet_names:
        s_lower = name.lower()
        if any(k.lower() in s_lower for k in keywords):
            return name
    return ""


def _find_header_row(ws, max_search: int = 30) -> tuple[int, dict[str, int]]:
    """Find header row by looking for a row with at least 3 non-empty cells."""
    # #63: prefer a >=3-cell header; accept a 2-cell header only if no wider row exists,
    # so a two-column tab is located without letting a 2-cell key/value row pre-empt a real header.
    fallback: tuple[int, dict[str, int]] = (0, {})
    for r in range(1, min(ws.max_row, max_search) + 1):
        cells = [(c, _norm(ws.cell(r, c).value)) for c in range(1, ws.max_column + 1)]
        non_empty = [(c, v) for c, v in cells if v]
        if len(non_empty) >= 2:
            if all(len(v) < 60 and not v.startswith("=") for c, v in non_empty):
                header_map = {v.lower(): c for c, v in non_empty}
                if len(non_empty) >= 3:
                    return r, header_map
                if not fallback[0]:
                    fallback = (r, header_map)
    return fallback


def _col_for(header_map: dict[str, int], candidates: list[str]) -> int:
    for cand in candidates:
        cand_lower = cand.lower()
        for header, col in header_map.items():
            if cand_lower in header:
                return col
    return 0


# ---------------------------------------------------------------------------
# Probe orchestrator
# ---------------------------------------------------------------------------

def probe(xlsx_path: str | Path) -> ProbedAPQPPlan:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedAPQPPlan(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect apqp-plan-builder format
    expected_tabs = [
        "00_Title_Page", "01_Document_Control", "02_Program_Info", "03_Cross_Functional_Team",
        "04_Phase1_Plan_Define", "05_Phase2_Product_Design", "06_Phase3_Process_Design",
        "07_Phase4_Product_Process_Validation", "08_Phase5_Feedback_Corrective",
        "09_Master_Schedule", "10_Gate_Reviews", "11_Special_Characteristics",
        "12_Risk_Register", "13_Open_Items_Tracker", "14_References"
    ]
    p.is_apqp_builder_format = all(t in wb.sheetnames for t in expected_tabs)
    if p.is_apqp_builder_format:
        p.detection_notes.append("Detected apqp-plan-builder format by tab names.")

    # Title / metadata from Title Page
    title_sheet = "00_Title_Page" if p.is_apqp_builder_format else _find_sheet_by_keywords(p.sheet_names, ["title"])
    if title_sheet and title_sheet in wb.sheetnames:
        ws = wb[title_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                if not label:
                    continue
                value = _norm(ws.cell(r, c + 1).value)
                if not value:
                    continue
                if "project" in label and not p.project:
                    p.project = value
                elif "program" in label and not p.program:
                    p.program = value
                elif "supplier" in label and not p.supplier:
                    p.supplier = value
                elif "customer" in label and not p.customer:
                    p.customer = value
                elif "revision" in label and not p.revision:
                    p.revision = value
                elif "status" in label and not p.status:
                    p.status = value
                elif "author" in label and not p.author:
                    p.author = value
                elif "approver" in label and not p.approver:
                    p.approver = value
                elif "title" == label or "document title" in label:
                    if not p.title:
                        p.title = value

    # Program Info
    prog_sheet = "02_Program_Info" if p.is_apqp_builder_format else _find_sheet_by_keywords(p.sheet_names, ["program", "info"])
    if prog_sheet and prog_sheet in wb.sheetnames:
        ws = wb[prog_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                if "manager" in label:
                    value = _norm(ws.cell(r, c + 1).value)
                    if value and not p.program_manager:
                        p.program_manager = value
                elif "quality" in label and "lead" in label:
                    value = _norm(ws.cell(r, c + 1).value)
                    if value and not p.quality_lead:
                        p.quality_lead = value

    # Cross-Functional Team
    team_sheet = "03_Cross_Functional_Team" if p.is_apqp_builder_format else _find_sheet_by_keywords(p.sheet_names, ["team", "function"])
    if team_sheet and team_sheet in wb.sheetnames:
        ws = wb[team_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "name": _col_for(header_map, ["name", "person"]),
                "role": _col_for(header_map, ["role", "position"]),
                "organization": _col_for(header_map, ["organization", "org"]),
                "email": _col_for(header_map, ["email", "contact"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                member = TeamMember(
                    name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    role=_norm(ws.cell(r, cols["role"]).value) if cols["role"] else "",
                    organization=_norm(ws.cell(r, cols["organization"]).value) if cols["organization"] else "",
                    email=_norm(ws.cell(r, cols["email"]).value) if cols["email"] else "",
                )
                if member.name or member.role:
                    p.team_members.append(member)

    # Deliverables from Phase tabs
    phase_map = {
        "04_Phase1_Plan_Define": ("Phase 1", p.phase1_deliverables),
        "05_Phase2_Product_Design": ("Phase 2", p.phase2_deliverables),
        "06_Phase3_Process_Design": ("Phase 3", p.phase3_deliverables),
        "07_Phase4_Product_Process_Validation": ("Phase 4", p.phase4_deliverables),
        "08_Phase5_Feedback_Corrective": ("Phase 5", p.phase5_deliverables),
    }
    for sheet_name, (phase_label, deliv_list) in phase_map.items():
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            header_row, header_map = _find_header_row(ws)
            if header_row:
                cols = {
                    "name": _col_for(header_map, ["deliverable", "name", "activity"]),
                    "owner": _col_for(header_map, ["owner", "responsible"]),
                    "planned": _col_for(header_map, ["planned", "due", "date"]),
                    "actual": _col_for(header_map, ["actual", "completion", "complete"]),
                    "status": _col_for(header_map, ["status"]),
                }
                for r in range(header_row + 1, ws.max_row + 1):
                    deliv = Deliverable(
                        phase=phase_label,
                        name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                        owner=_norm(ws.cell(r, cols["owner"]).value) if cols["owner"] else "",
                        planned_date=_norm(ws.cell(r, cols["planned"]).value) if cols["planned"] else "",
                        actual_date=_norm(ws.cell(r, cols["actual"]).value) if cols["actual"] else "",
                        status=_norm(ws.cell(r, cols["status"]).value) if cols["status"] else "",
                    )
                    if deliv.name:
                        deliv_list.append(deliv)

    # Master Schedule / Gate Reviews
    sched_sheet = "09_Master_Schedule" if p.is_apqp_builder_format else _find_sheet_by_keywords(p.sheet_names, ["schedule"])
    if sched_sheet and sched_sheet in wb.sheetnames:
        ws = wb[sched_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            for r in range(header_row + 1, ws.max_row + 1):
                row_vals = [_norm(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)]
                if any(row_vals):
                    p.milestones.append({"row": r, "values": [v for v in row_vals if v]})

    # Gate Reviews
    gate_sheet = "10_Gate_Reviews" if p.is_apqp_builder_format else _find_sheet_by_keywords(p.sheet_names, ["gate"])
    if gate_sheet and gate_sheet in wb.sheetnames:
        ws = wb[gate_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            for r in range(header_row + 1, ws.max_row + 1):
                row_vals = {h: _norm(ws.cell(r, c).value) for h, c in header_map.items()}
                if any(row_vals.values()):
                    p.gate_reviews.append(row_vals)

    # Special Characteristics
    sc_sheet = "11_Special_Characteristics" if p.is_apqp_builder_format else _find_sheet_by_keywords(p.sheet_names, ["special", "characteristic"])
    if sc_sheet and sc_sheet in wb.sheetnames:
        ws = wb[sc_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "name": _col_for(header_map, ["name", "characteristic"]),
                "type": _col_for(header_map, ["type", "category"]),
                "source": _col_for(header_map, ["source", "origin"]),
                "oem": _col_for(header_map, ["oem", "requirement"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                sc = SpecialChar(
                    char_name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    type=_norm(ws.cell(r, cols["type"]).value) if cols["type"] else "",
                    source=_norm(ws.cell(r, cols["source"]).value) if cols["source"] else "",
                    oem_requirement=_norm(ws.cell(r, cols["oem"]).value) if cols["oem"] else "",
                )
                if sc.char_name:
                    p.special_characteristics.append(sc)

    # Risk Register
    risk_sheet = "12_Risk_Register" if p.is_apqp_builder_format else _find_sheet_by_keywords(p.sheet_names, ["risk"])
    if risk_sheet and risk_sheet in wb.sheetnames:
        ws = wb[risk_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["id", "number"]),
                "description": _col_for(header_map, ["description", "risk"]),
                "severity": _col_for(header_map, ["severity"]),
                "probability": _col_for(header_map, ["probability", "likelihood"]),
                "mitigation": _col_for(header_map, ["mitigation", "action"]),
                "owner": _col_for(header_map, ["owner", "responsible"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                risk = RiskItem(
                    risk_id=_norm(ws.cell(r, cols["id"]).value) if cols["id"] else "",
                    description=_norm(ws.cell(r, cols["description"]).value) if cols["description"] else "",
                    severity=_norm(ws.cell(r, cols["severity"]).value) if cols["severity"] else "",
                    probability=_norm(ws.cell(r, cols["probability"]).value) if cols["probability"] else "",
                    mitigation=_norm(ws.cell(r, cols["mitigation"]).value) if cols["mitigation"] else "",
                    owner=_norm(ws.cell(r, cols["owner"]).value) if cols["owner"] else "",
                )
                if risk.risk_id or risk.description:
                    p.risks.append(risk)

    # Open Items Tracker
    oi_sheet = "13_Open_Items_Tracker" if p.is_apqp_builder_format else _find_sheet_by_keywords(p.sheet_names, ["open", "item"])
    if oi_sheet and oi_sheet in wb.sheetnames:
        ws = wb[oi_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["id", "number"]),
                "description": _col_for(header_map, ["description"]),
                "owner": _col_for(header_map, ["owner", "responsible"]),
                "due": _col_for(header_map, ["due", "date"]),
                "status": _col_for(header_map, ["status"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                oi = OpenItem(
                    item_id=_norm(ws.cell(r, cols["id"]).value) if cols["id"] else "",
                    description=_norm(ws.cell(r, cols["description"]).value) if cols["description"] else "",
                    owner=_norm(ws.cell(r, cols["owner"]).value) if cols["owner"] else "",
                    due_date=_norm(ws.cell(r, cols["due"]).value) if cols["due"] else "",
                    status=_norm(ws.cell(r, cols["status"]).value) if cols["status"] else "",
                )
                if oi.item_id or oi.description:
                    p.open_items.append(oi)

    return p


if __name__ == "__main__":
    import sys
    import json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "is_apqp_builder_format": p.is_apqp_builder_format,
        "title": p.title,
        "project": p.project,
        "program": p.program,
        "supplier": p.supplier,
        "program_manager": p.program_manager,
        "quality_lead": p.quality_lead,
        "n_team_members": len(p.team_members),
        "n_phase1_deliverables": len(p.phase1_deliverables),
        "n_phase2_deliverables": len(p.phase2_deliverables),
        "n_phase3_deliverables": len(p.phase3_deliverables),
        "n_phase4_deliverables": len(p.phase4_deliverables),
        "n_phase5_deliverables": len(p.phase5_deliverables),
        "n_milestones": len(p.milestones),
        "n_gate_reviews": len(p.gate_reviews),
        "n_special_characteristics": len(p.special_characteristics),
        "n_risks": len(p.risks),
        "n_open_items": len(p.open_items),
        "sheets": p.sheet_names,
        "detection_notes": p.detection_notes,
    }
    print(json.dumps(summary, indent=2))
