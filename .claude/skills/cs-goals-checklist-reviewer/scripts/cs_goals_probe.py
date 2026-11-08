"""
CS Goals content probe — extracts CSG, CAL, asset mapping, and TARA traceability.

Reads: 00_Title_Page, 01_Document_Control, 02_TARA_Echo, 03_Cybersecurity_Goals,
       04_CAL_Determination, 05_Asset_to_CSG_Map, 06_CS_Concept_Handoff, 07_References

Returns a structured ProbedCSGoals dict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class CSGEntry:
    csg_id: str = ""
    csg_text: str = ""
    cal: str = ""
    threat_ref: str = ""
    property: str = ""
    owner: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class AssetCSGMapping:
    asset_id: str = ""
    asset_name: str = ""
    csg_id: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class TaraEcho:
    threat_id: str = ""
    threat: str = ""
    risk_value: str = ""
    csg_ref: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class ProbedCSGoals:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""
    sheet_names: list[str] = field(default_factory=list)

    n_csg: int = 0
    n_tara_echo: int = 0
    n_asset_csg_mappings: int = 0

    csg_entries: list[CSGEntry] = field(default_factory=list)
    tara_threats: list[TaraEcho] = field(default_factory=list)
    asset_mappings: list[AssetCSGMapping] = field(default_factory=list)

    cal_distribution: dict[str, int] = field(default_factory=dict)
    properties_covered: set[str] = field(default_factory=set)

    has_table_of_contents: bool = False
    revision_history_rows: int = 0


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


def probe(xlsx_path: str | Path) -> ProbedCSGoals:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedCSGoals(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

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

    # TARA Echo
    tara_sheet = _find_sheet_by_keywords(p.sheet_names, ["tara echo", "02_tara"])
    if tara_sheet and tara_sheet in wb.sheetnames:
        ws = wb[tara_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            tid_col = _col_for(header_map, ["threat id"])
            threat_col = _col_for(header_map, ["threat"])
            risk_col = _col_for(header_map, ["risk value"])
            csg_col = _col_for(header_map, ["csg ref", "csg"])
            for r in range(header_row + 1, ws.max_row + 1):
                tid = _norm(ws.cell(r, tid_col).value) if tid_col else ""
                threat = _norm(ws.cell(r, threat_col).value) if threat_col else ""
                if not (tid or threat):
                    continue
                te = TaraEcho(
                    threat_id=tid,
                    threat=threat,
                    risk_value=_norm(ws.cell(r, risk_col).value) if risk_col else "",
                    csg_ref=_norm(ws.cell(r, csg_col).value) if csg_col else "",
                    sheet=tara_sheet,
                    row=r,
                )
                p.tara_threats.append(te)

    p.n_tara_echo = len(p.tara_threats)

    # Cybersecurity Goals
    csg_sheet = _find_sheet_by_keywords(p.sheet_names, ["cybersecurity goals", "03_cybersecurity"])
    if csg_sheet and csg_sheet in wb.sheetnames:
        ws = wb[csg_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            id_col = _col_for(header_map, ["csg id", "id"])
            text_col = _col_for(header_map, ["cybersecurity goal", "goal"])
            cal_col = _col_for(header_map, ["cal"])
            threat_col = _col_for(header_map, ["threat ref"])
            prop_col = _col_for(header_map, ["property", "sec property"])
            owner_col = _col_for(header_map, ["owner"])
            for r in range(header_row + 1, ws.max_row + 1):
                csg_id = _norm(ws.cell(r, id_col).value) if id_col else ""
                csg_text = _norm(ws.cell(r, text_col).value) if text_col else ""
                if not (csg_id or csg_text):
                    continue
                cal = _norm(ws.cell(r, cal_col).value) if cal_col else ""
                prop = _norm(ws.cell(r, prop_col).value) if prop_col else ""
                csg = CSGEntry(
                    csg_id=csg_id,
                    csg_text=csg_text,
                    cal=cal,
                    threat_ref=_norm(ws.cell(r, threat_col).value) if threat_col else "",
                    property=prop,
                    owner=_norm(ws.cell(r, owner_col).value) if owner_col else "",
                    sheet=csg_sheet,
                    row=r,
                )
                p.csg_entries.append(csg)
                if cal:
                    p.cal_distribution[cal] = p.cal_distribution.get(cal, 0) + 1
                if prop:
                    p.properties_covered.add(prop)

    p.n_csg = len(p.csg_entries)

    # Asset to CSG Mapping
    mapping_sheet = _find_sheet_by_keywords(p.sheet_names, ["asset to csg", "05_asset"])
    if mapping_sheet and mapping_sheet in wb.sheetnames:
        ws = wb[mapping_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            asset_id_col = _col_for(header_map, ["asset id"])
            asset_name_col = _col_for(header_map, ["asset name"])
            csg_col = _col_for(header_map, ["csg id", "csg"])
            for r in range(header_row + 1, ws.max_row + 1):
                asset_id = _norm(ws.cell(r, asset_id_col).value) if asset_id_col else ""
                asset_name = _norm(ws.cell(r, asset_name_col).value) if asset_name_col else ""
                csg_id = _norm(ws.cell(r, csg_col).value) if csg_col else ""
                if not (asset_id or asset_name or csg_id):
                    continue
                m = AssetCSGMapping(
                    asset_id=asset_id,
                    asset_name=asset_name,
                    csg_id=csg_id,
                    sheet=mapping_sheet,
                    row=r,
                )
                p.asset_mappings.append(m)

    p.n_asset_csg_mappings = len(p.asset_mappings)
    p.has_table_of_contents = any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3])

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "title": p.title,
        "n_csg": p.n_csg,
        "n_tara_echo": p.n_tara_echo,
        "n_asset_csg_mappings": p.n_asset_csg_mappings,
        "cal_distribution": p.cal_distribution,
        "properties_covered": list(p.properties_covered),
    }
    print(json.dumps(summary, indent=2))
