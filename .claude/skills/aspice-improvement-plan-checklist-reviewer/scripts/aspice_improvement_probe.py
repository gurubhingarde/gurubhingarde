"""ASPICE Improvement Plan content probe."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from openpyxl import load_workbook

@dataclass
class ProbedImprovementPlan:
    path: str = ""
    sheet_names: list[str] = field(default_factory=list)
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    sponsor: str = ""
    project: str = ""
    doc_id: str = ""
    target_completion_date: str = ""
    program_scope_clear: bool = False
    initiative_rows: int = 0
    has_owners: bool = False
    has_milestones: bool = False
    has_budget: bool = False
    roadmap_present: bool = False
    risks_documented: bool = False
    kpis_defined: bool = False
    stakeholder_comm_plan: bool = False
    pilot_plan: bool = False
    initiatives_without_owner: int = 0

def _norm(s: Any) -> str:
    if s is None: return ""
    return str(s).strip()

def _find_sheet_by_keywords(sheet_names: list[str], keywords: list[str]) -> str:
    for name in sheet_names:
        if any(k.lower() in name.lower() for k in keywords):
            return name
    return ""

def _find_header_row(ws, max_search: int = 30) -> tuple[int, dict[str, int]]:
    # #63: prefer a >=3-cell header; accept a 2-cell header only if no wider row exists,
    # so a two-column tab is located without letting a 2-cell key/value row pre-empt a real header.
    fallback: tuple[int, dict[str, int]] = (0, {})
    for r in range(1, min(ws.max_row, max_search) + 1):
        cells = [(c, _norm(ws.cell(r, c).value)) for c in range(1, ws.max_column + 1)]
        non_empty = [(c, v) for c, v in cells if v]
        if len(non_empty) >= 2 and all(len(v) < 80 and not v.startswith("=") for c, v in non_empty):
            header_map = {v.lower(): c for c, v in non_empty}
            if len(non_empty) >= 3:
                return r, header_map
            if not fallback[0]:
                fallback = (r, header_map)
    return fallback

def _col_for(header_map: dict[str, int], candidates: list[str]) -> int:
    for cand in candidates:
        for header, col in header_map.items():
            if cand.lower() in header: return col
    return 0

def probe(xlsx_path: str | Path) -> ProbedImprovementPlan:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedImprovementPlan(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    title_sheet = _find_sheet_by_keywords(p.sheet_names, ["title", "cover"])
    if title_sheet and title_sheet in wb.sheetnames:
        ws = wb[title_sheet]
        for r in range(1, min(ws.max_row + 1, 40)):
            for c in range(1, min(ws.max_column + 1, 5)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if label and value:
                    if "sponsor" in label: p.sponsor = value
                    elif "completion" in label or "date" in label: p.target_completion_date = value
                    elif "revision" in label: p.revision = value
                    elif "status" in label: p.status = value
                    elif "author" in label: p.author = value
                    elif "approver" in label: p.approver = value

    scope_sheet = _find_sheet_by_keywords(p.sheet_names, ["scope", "program"])
    if scope_sheet and scope_sheet in wb.sheetnames:
        ws = wb[scope_sheet]
        text = " ".join(str(ws.cell(r, c).value or "") for r in range(1, min(ws.max_row + 1, 30))
                       for c in range(1, min(ws.max_column + 1, 8)))
        if len(text.strip()) > 50: p.program_scope_clear = True

    init_sheet = _find_sheet_by_keywords(p.sheet_names, ["initiative", "action", "improvement"])
    if init_sheet and init_sheet in wb.sheetnames:
        ws = wb[init_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            p.initiative_rows = max(0, ws.max_row - header_row)
            owner_col = _col_for(header_map, ["owner"])
            milestone_col = _col_for(header_map, ["milestone"])
            budget_col = _col_for(header_map, ["budget", "cost"])

            if owner_col: p.has_owners = any(_norm(ws.cell(r, owner_col).value) for r in range(header_row + 1, min(header_row + 20, ws.max_row + 1)))
            if milestone_col: p.has_milestones = any(_norm(ws.cell(r, milestone_col).value) for r in range(header_row + 1, min(header_row + 20, ws.max_row + 1)))
            if budget_col: p.has_budget = any(_norm(ws.cell(r, budget_col).value) for r in range(header_row + 1, min(header_row + 20, ws.max_row + 1)))

            for r in range(header_row + 1, ws.max_row + 1):
                if not (owner_col and _norm(ws.cell(r, owner_col).value)):
                    p.initiatives_without_owner += 1

    roadmap_sheet = _find_sheet_by_keywords(p.sheet_names, ["roadmap", "gantt", "timeline"])
    if roadmap_sheet and roadmap_sheet in wb.sheetnames:
        p.roadmap_present = True

    risk_sheet = _find_sheet_by_keywords(p.sheet_names, ["risk"])
    if risk_sheet and risk_sheet in wb.sheetnames:
        p.risks_documented = True

    kpi_sheet = _find_sheet_by_keywords(p.sheet_names, ["kpi", "metric", "measure"])
    if kpi_sheet and kpi_sheet in wb.sheetnames:
        p.kpis_defined = True

    comm_sheet = _find_sheet_by_keywords(p.sheet_names, ["communication", "comm", "stakeholder"])
    if comm_sheet and comm_sheet in wb.sheetnames:
        p.stakeholder_comm_plan = True

    pilot_sheet = _find_sheet_by_keywords(p.sheet_names, ["pilot"])
    if pilot_sheet and pilot_sheet in wb.sheetnames:
        p.pilot_plan = True

    return p

if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    print(json.dumps({
        "path": p.path,
        "sheets": p.sheet_names,
        "initiative_rows": p.initiative_rows,
        "has_owners": p.has_owners,
        "has_milestones": p.has_milestones,
        "has_budget": p.has_budget,
        "roadmap_present": p.roadmap_present,
        "risks_documented": p.risks_documented,
        "kpis_defined": p.kpis_defined,
        "initiatives_without_owner": p.initiatives_without_owner,
    }, indent=2))
