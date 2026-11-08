"""
TARA content probe — best-effort extractor for TARA xlsx following ISO/SAE 21434.

Reads: 00_Title_Page, 01_Document_Control, 02_Assumptions, 03_Item_Description,
       04_Asset_Inventory, 05_Threat_Scenarios, 06_Impact_Assessment, 07_Attack_Path_Analysis,
       08_Feasibility_Rating, 09_Risk_Determination, 10_Risk_Treatment, 11_Cybersecurity_Goals,
       12_References

Returns a structured ProbedTara dict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class Asset:
    asset_id: str = ""
    name: str = ""
    description: str = ""
    cybersecurity_properties: list[str] = field(default_factory=list)
    sheet: str = ""
    row: int = 0


@dataclass
class ThreatScenario:
    threat_id: str = ""
    threat: str = ""
    asset: str = ""
    stride: str = ""
    impact_s: str = ""
    impact_f: str = ""
    impact_o: str = ""
    impact_p: str = ""
    feasibility_rating: str = ""
    attack_potential: str = ""
    risk_value: str = ""
    treatment: str = ""
    csg_reference: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class CybersecurityGoal:
    csg_id: str = ""
    csg_text: str = ""
    cal: str = ""
    threat_ref: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class ProbedTara:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""
    sheet_names: list[str] = field(default_factory=list)

    # Inventory counts
    n_assets: int = 0
    n_threats: int = 0
    n_csg: int = 0
    n_assumptions: int = 0

    assets: list[Asset] = field(default_factory=list)
    threats: list[ThreatScenario] = field(default_factory=list)
    cybersecurity_goals: list[CybersecurityGoal] = field(default_factory=list)

    stride_categories: set[str] = field(default_factory=set)
    treatment_decisions: set[str] = field(default_factory=set)
    risk_values: list[str] = field(default_factory=list)
    cal_values: set[str] = field(default_factory=set)

    has_table_of_contents: bool = False
    revision_history_rows: int = 0
    detection_notes: list[str] = field(default_factory=list)


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


def probe(xlsx_path: str | Path) -> ProbedTara:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedTara(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Title page metadata
    title_sheet = _find_sheet_by_keywords(p.sheet_names, ["title", "00_title"])
    if title_sheet and title_sheet in wb.sheetnames:
        ws = wb[title_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if not label or not value:
                    continue
                if "title" in label and not p.title:
                    p.title = value
                elif "project" in label and not p.project:
                    p.project = value
                elif "doc id" in label or "document id" in label:
                    p.doc_id = value
                elif "revision" in label and not p.revision:
                    p.revision = value
                elif "status" in label and not p.status:
                    p.status = value
                elif "author" in label and not p.author:
                    p.author = value
                elif "approver" in label and not p.approver:
                    p.approver = value

    # Document control / revision history
    doc_ctrl_sheet = _find_sheet_by_keywords(p.sheet_names, ["document control", "01_document"])
    if doc_ctrl_sheet and doc_ctrl_sheet in wb.sheetnames:
        ws = wb[doc_ctrl_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            rev_col = _col_for(header_map, ["revision"])
            if rev_col:
                count = 0
                for r in range(header_row + 1, ws.max_row + 1):
                    if _norm(ws.cell(r, rev_col).value):
                        count += 1
                p.revision_history_rows = count

    # Asset Inventory
    assets_sheet = _find_sheet_by_keywords(p.sheet_names, ["asset inventory", "04_asset"])
    if assets_sheet and assets_sheet in wb.sheetnames:
        ws = wb[assets_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            id_col = _col_for(header_map, ["asset id", "id"])
            name_col = _col_for(header_map, ["asset name", "name"])
            desc_col = _col_for(header_map, ["description"])
            sec_col = _col_for(header_map, ["cybersecurity properties", "properties"])
            for r in range(header_row + 1, ws.max_row + 1):
                aid = _norm(ws.cell(r, id_col).value) if id_col else ""
                aname = _norm(ws.cell(r, name_col).value) if name_col else ""
                if not (aid or aname):
                    continue
                props = _norm(ws.cell(r, sec_col).value) if sec_col else ""
                asset = Asset(
                    asset_id=aid,
                    name=aname,
                    description=_norm(ws.cell(r, desc_col).value) if desc_col else "",
                    cybersecurity_properties=[p.strip() for p in props.split(",") if p.strip()],
                    sheet=assets_sheet,
                    row=r,
                )
                p.assets.append(asset)

    p.n_assets = len(p.assets)

    # Threat Scenarios
    threats_sheet = _find_sheet_by_keywords(p.sheet_names, ["threat scenarios", "05_threat"])
    if threats_sheet and threats_sheet in wb.sheetnames:
        ws = wb[threats_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "threat_id": _col_for(header_map, ["threat id", "id"]),
                "threat": _col_for(header_map, ["threat", "threat scenario"]),
                "asset": _col_for(header_map, ["asset"]),
                "stride": _col_for(header_map, ["stride"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                tid = _norm(ws.cell(r, cols["threat_id"]).value) if cols["threat_id"] else ""
                threat = _norm(ws.cell(r, cols["threat"]).value) if cols["threat"] else ""
                if not (tid or threat):
                    continue
                stride = _norm(ws.cell(r, cols["stride"]).value) if cols["stride"] else ""
                t = ThreatScenario(
                    threat_id=tid,
                    threat=threat,
                    asset=_norm(ws.cell(r, cols["asset"]).value) if cols["asset"] else "",
                    stride=stride,
                    sheet=threats_sheet,
                    row=r,
                )
                p.threats.append(t)
                if stride:
                    p.stride_categories.add(stride[0].upper() if stride else "")

    # Impact Assessment
    impact_sheet = _find_sheet_by_keywords(p.sheet_names, ["impact", "06_impact"])
    if impact_sheet and impact_sheet in wb.sheetnames:
        ws = wb[impact_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            threat_col = _col_for(header_map, ["threat id", "threat"])
            s_col = _col_for(header_map, ["safety"])
            f_col = _col_for(header_map, ["financial"])
            o_col = _col_for(header_map, ["operational"])
            p_col = _col_for(header_map, ["privacy"])
            for r in range(header_row + 1, ws.max_row + 1):
                threat_ref = _norm(ws.cell(r, threat_col).value) if threat_col else ""
                if not threat_ref:
                    continue
                for t in p.threats:
                    if t.threat_id.lower() == threat_ref.lower():
                        t.impact_s = _norm(ws.cell(r, s_col).value) if s_col else ""
                        t.impact_f = _norm(ws.cell(r, f_col).value) if f_col else ""
                        t.impact_o = _norm(ws.cell(r, o_col).value) if o_col else ""
                        t.impact_p = _norm(ws.cell(r, p_col).value) if p_col else ""
                        break

    # Feasibility Rating
    feas_sheet = _find_sheet_by_keywords(p.sheet_names, ["feasibility", "08_feasibility"])
    if feas_sheet and feas_sheet in wb.sheetnames:
        ws = wb[feas_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            threat_col = _col_for(header_map, ["threat id", "threat"])
            rating_col = _col_for(header_map, ["feasibility rating", "rating"])
            for r in range(header_row + 1, ws.max_row + 1):
                threat_ref = _norm(ws.cell(r, threat_col).value) if threat_col else ""
                if not threat_ref:
                    continue
                rating = _norm(ws.cell(r, rating_col).value) if rating_col else ""
                for t in p.threats:
                    if t.threat_id.lower() == threat_ref.lower():
                        t.feasibility_rating = rating
                        break

    # Risk Determination
    risk_sheet = _find_sheet_by_keywords(p.sheet_names, ["risk determination", "09_risk"])
    if risk_sheet and risk_sheet in wb.sheetnames:
        ws = wb[risk_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            threat_col = _col_for(header_map, ["threat id", "threat"])
            risk_col = _col_for(header_map, ["risk value", "risk"])
            for r in range(header_row + 1, ws.max_row + 1):
                threat_ref = _norm(ws.cell(r, threat_col).value) if threat_col else ""
                if not threat_ref:
                    continue
                risk = _norm(ws.cell(r, risk_col).value) if risk_col else ""
                for t in p.threats:
                    if t.threat_id.lower() == threat_ref.lower():
                        t.risk_value = risk
                        if risk:
                            p.risk_values.append(risk)
                        break

    # Risk Treatment
    treatment_sheet = _find_sheet_by_keywords(p.sheet_names, ["risk treatment", "10_risk_treatment"])
    if treatment_sheet and treatment_sheet in wb.sheetnames:
        ws = wb[treatment_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            threat_col = _col_for(header_map, ["threat id", "threat"])
            treatment_col = _col_for(header_map, ["treatment", "decision"])
            for r in range(header_row + 1, ws.max_row + 1):
                threat_ref = _norm(ws.cell(r, threat_col).value) if threat_col else ""
                if not threat_ref:
                    continue
                treatment = _norm(ws.cell(r, treatment_col).value) if treatment_col else ""
                for t in p.threats:
                    if t.threat_id.lower() == threat_ref.lower():
                        t.treatment = treatment
                        if treatment:
                            p.treatment_decisions.add(treatment)
                        break

    # Cybersecurity Goals
    csg_sheet = _find_sheet_by_keywords(p.sheet_names, ["cybersecurity goals", "11_cybersecurity"])
    if csg_sheet and csg_sheet in wb.sheetnames:
        ws = wb[csg_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            id_col = _col_for(header_map, ["csg id", "id"])
            text_col = _col_for(header_map, ["cybersecurity goal", "goal"])
            cal_col = _col_for(header_map, ["cal"])
            threat_col = _col_for(header_map, ["threat ref", "threat"])
            for r in range(header_row + 1, ws.max_row + 1):
                csg_id = _norm(ws.cell(r, id_col).value) if id_col else ""
                csg_text = _norm(ws.cell(r, text_col).value) if text_col else ""
                if not (csg_id or csg_text):
                    continue
                cal = _norm(ws.cell(r, cal_col).value) if cal_col else ""
                csg = CybersecurityGoal(
                    csg_id=csg_id,
                    csg_text=csg_text,
                    cal=cal,
                    threat_ref=_norm(ws.cell(r, threat_col).value) if threat_col else "",
                    sheet=csg_sheet,
                    row=r,
                )
                p.cybersecurity_goals.append(csg)
                if cal:
                    p.cal_values.add(cal)

    p.n_threats = len(p.threats)
    p.n_csg = len(p.cybersecurity_goals)
    p.has_table_of_contents = any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3])

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "title": p.title,
        "doc_id": p.doc_id,
        "revision": p.revision,
        "n_assets": p.n_assets,
        "n_threats": p.n_threats,
        "n_csg": p.n_csg,
        "stride_coverage": list(p.stride_categories),
        "treatment_decisions": list(p.treatment_decisions),
        "cal_values": list(p.cal_values),
    }
    print(json.dumps(summary, indent=2))
