"""
Safety Plan content probe — best-effort extractor for ISO 26262 Safety Plan xlsx.

Returns a structured ProbedSafetyPlan dict that downstream check functions consume.
Works on safety-plan-builder outputs and best-effort on others.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class RoleEntry:
    name: str = ""
    role: str = ""
    organization: str = ""
    email: str = ""
    independence_level: str = ""


@dataclass
class WorkProduct:
    wp_id: str = ""
    name: str = ""
    owner: str = ""
    target_asil: str = ""
    planned_date: str = ""
    actual_date: str = ""
    status: str = ""


@dataclass
class ConfirmationReview:
    wp_id: str = ""
    required_independence: str = ""
    assigned_reviewer: str = ""
    planned_date: str = ""


@dataclass
class ToolEntry:
    name: str = ""
    vendor: str = ""
    tcl: str = ""
    qualification_status: str = ""


@dataclass
class ProbedSafetyPlan:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""

    project: str = ""
    item: str = ""
    target_asil: str = ""
    vehicle_programs: str = ""
    suppliers: str = ""

    sheet_names: list[str] = field(default_factory=list)

    roles: list[RoleEntry] = field(default_factory=list)
    tailoring_decisions: dict[str, str] = field(default_factory=dict)  # key: requirement name, value: status/justification

    work_products: list[WorkProduct] = field(default_factory=list)
    confirmation_reviews: list[ConfirmationReview] = field(default_factory=list)

    tools: list[ToolEntry] = field(default_factory=list)
    milestones: list[dict] = field(default_factory=list)

    is_safety_plan_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm(s: Any) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _contains_any(s: str, keywords: list[str]) -> bool:
    s_lower = s.lower()
    return any(k.lower() in s_lower for k in keywords)


def _find_sheet_by_keywords(sheet_names: list[str], keywords: list[str]) -> str:
    for name in sheet_names:
        if _contains_any(name, keywords):
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
    """Find first matching column by partial-match of any candidate keyword."""
    for cand in candidates:
        cand_lower = cand.lower()
        for header, col in header_map.items():
            if cand_lower in header:
                return col
    return 0


# ---------------------------------------------------------------------------
# Probe orchestrator
# ---------------------------------------------------------------------------

def probe(xlsx_path: str | Path) -> ProbedSafetyPlan:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedSafetyPlan(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect safety-plan-builder format by tab signature
    expected_tabs = [
        "00_Title_Page", "01_Document_Control", "02_Project_Info",
        "03_Roles_Responsibilities", "04_Tailoring", "05_Work_Products",
        "06_Confirmation_Reviews", "07_Tools", "08_Resources", "09_Anomaly_Resolution",
        "10_Schedule", "11_References"
    ]
    p.is_safety_plan_builder_format = all(t in wb.sheetnames for t in expected_tabs)
    if p.is_safety_plan_builder_format:
        p.detection_notes.append("Detected safety-plan-builder format by tab names.")

    # Title / metadata from Title Page
    title_sheet = "00_Title_Page" if p.is_safety_plan_builder_format else _find_sheet_by_keywords(p.sheet_names, ["title"])
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
                elif "item" in label and not p.item:
                    p.item = value
                elif "document id" in label or "doc id" in label:
                    pass  # could store doc_id if needed
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
                elif "target asil" in label and not p.target_asil:
                    p.target_asil = value
                elif "vehicle" in label and "program" in label and not p.vehicle_programs:
                    p.vehicle_programs = value
                elif "supplier" in label and not p.suppliers:
                    p.suppliers = value

    # Roles from Roles & Responsibilities tab
    roles_sheet = "03_Roles_Responsibilities" if p.is_safety_plan_builder_format else _find_sheet_by_keywords(p.sheet_names, ["role", "responsibility"])
    if roles_sheet and roles_sheet in wb.sheetnames:
        ws = wb[roles_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "name": _col_for(header_map, ["name", "person"]),
                "role": _col_for(header_map, ["role", "position"]),
                "organization": _col_for(header_map, ["organization", "org"]),
                "email": _col_for(header_map, ["email", "contact"]),
                "independence": _col_for(header_map, ["independence", "level"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                role = RoleEntry(
                    name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    role=_norm(ws.cell(r, cols["role"]).value) if cols["role"] else "",
                    organization=_norm(ws.cell(r, cols["organization"]).value) if cols["organization"] else "",
                    email=_norm(ws.cell(r, cols["email"]).value) if cols["email"] else "",
                    independence_level=_norm(ws.cell(r, cols["independence"]).value) if cols["independence"] else "",
                )
                if role.name or role.role:
                    p.roles.append(role)

    # Tailoring from Tailoring tab
    tailoring_sheet = "04_Tailoring" if p.is_safety_plan_builder_format else _find_sheet_by_keywords(p.sheet_names, ["tailor"])
    if tailoring_sheet and tailoring_sheet in wb.sheetnames:
        ws = wb[tailoring_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            req_col = _col_for(header_map, ["requirement", "clause"])
            status_col = _col_for(header_map, ["applicable", "status"])
            just_col = _col_for(header_map, ["justification"])
            for r in range(header_row + 1, ws.max_row + 1):
                req = _norm(ws.cell(r, req_col).value) if req_col else ""
                status = _norm(ws.cell(r, status_col).value) if status_col else ""
                just = _norm(ws.cell(r, just_col).value) if just_col else ""
                if req:
                    p.tailoring_decisions[req] = f"{status}: {just}" if just else status

    # Work Products from Work Products tab
    wp_sheet = "05_Work_Products" if p.is_safety_plan_builder_format else _find_sheet_by_keywords(p.sheet_names, ["work product"])
    if wp_sheet and wp_sheet in wb.sheetnames:
        ws = wb[wp_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["wp_id", "id"]),
                "name": _col_for(header_map, ["name", "title"]),
                "owner": _col_for(header_map, ["owner", "responsible"]),
                "asil": _col_for(header_map, ["asil", "target"]),
                "planned": _col_for(header_map, ["planned", "due"]),
                "actual": _col_for(header_map, ["actual", "completion"]),
                "status": _col_for(header_map, ["status"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                wp = WorkProduct(
                    wp_id=_norm(ws.cell(r, cols["id"]).value) if cols["id"] else "",
                    name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    owner=_norm(ws.cell(r, cols["owner"]).value) if cols["owner"] else "",
                    target_asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    planned_date=_norm(ws.cell(r, cols["planned"]).value) if cols["planned"] else "",
                    actual_date=_norm(ws.cell(r, cols["actual"]).value) if cols["actual"] else "",
                    status=_norm(ws.cell(r, cols["status"]).value) if cols["status"] else "",
                )
                if wp.wp_id or wp.name:
                    p.work_products.append(wp)

    # Confirmation Reviews from CR tab
    cr_sheet = "06_Confirmation_Reviews" if p.is_safety_plan_builder_format else _find_sheet_by_keywords(p.sheet_names, ["confirmation"])
    if cr_sheet and cr_sheet in wb.sheetnames:
        ws = wb[cr_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "wp_id": _col_for(header_map, ["wp_id", "work product"]),
                "independence": _col_for(header_map, ["independence", "required"]),
                "reviewer": _col_for(header_map, ["reviewer", "assigned"]),
                "planned": _col_for(header_map, ["planned", "date"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                cr = ConfirmationReview(
                    wp_id=_norm(ws.cell(r, cols["wp_id"]).value) if cols["wp_id"] else "",
                    required_independence=_norm(ws.cell(r, cols["independence"]).value) if cols["independence"] else "",
                    assigned_reviewer=_norm(ws.cell(r, cols["reviewer"]).value) if cols["reviewer"] else "",
                    planned_date=_norm(ws.cell(r, cols["planned"]).value) if cols["planned"] else "",
                )
                if cr.wp_id:
                    p.confirmation_reviews.append(cr)

    # Tools from Tools tab
    tools_sheet = "07_Tools" if p.is_safety_plan_builder_format else _find_sheet_by_keywords(p.sheet_names, ["tool"])
    if tools_sheet and tools_sheet in wb.sheetnames:
        ws = wb[tools_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "name": _col_for(header_map, ["name", "tool"]),
                "vendor": _col_for(header_map, ["vendor"]),
                "tcl": _col_for(header_map, ["tcl"]),
                "qualification": _col_for(header_map, ["qualification", "status"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                tool = ToolEntry(
                    name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    vendor=_norm(ws.cell(r, cols["vendor"]).value) if cols["vendor"] else "",
                    tcl=_norm(ws.cell(r, cols["tcl"]).value) if cols["tcl"] else "",
                    qualification_status=_norm(ws.cell(r, cols["qualification"]).value) if cols["qualification"] else "",
                )
                if tool.name:
                    p.tools.append(tool)

    # Schedule / Milestones from Schedule tab
    sched_sheet = "10_Schedule" if p.is_safety_plan_builder_format else _find_sheet_by_keywords(p.sheet_names, ["schedule"])
    if sched_sheet and sched_sheet in wb.sheetnames:
        ws = wb[sched_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            for r in range(header_row + 1, ws.max_row + 1):
                row_vals = [_norm(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)]
                if any(row_vals):
                    p.milestones.append({"row": r, "values": [v for v in row_vals if v]})

    return p


if __name__ == "__main__":
    import sys
    import json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "is_safety_plan_builder_format": p.is_safety_plan_builder_format,
        "title": p.title,
        "project": p.project,
        "item": p.item,
        "revision": p.revision,
        "target_asil": p.target_asil,
        "n_roles": len(p.roles),
        "n_work_products": len(p.work_products),
        "n_confirmation_reviews": len(p.confirmation_reviews),
        "n_tools": len(p.tools),
        "n_tailoring_decisions": len(p.tailoring_decisions),
        "n_milestones": len(p.milestones),
        "sheets": p.sheet_names,
        "detection_notes": p.detection_notes,
    }
    print(json.dumps(summary, indent=2))
