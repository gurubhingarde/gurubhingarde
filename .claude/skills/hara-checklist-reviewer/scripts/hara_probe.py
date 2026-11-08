"""
HARA content probe — best-effort extractor that works on hara-builder outputs AND
on other HARA xlsx formats by keyword heuristics.

Returns a structured ProbedHara dict that downstream check functions consume.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class HaraRow:
    function: str = ""
    malfunction: str = ""
    location: str = ""
    speed_band: str = ""
    weather: str = ""
    hazardous_event: str = ""
    s: str = ""
    s_rationale: str = ""
    e: str = ""
    e_rationale: str = ""
    c: str = ""
    c_rationale: str = ""
    asil: str = ""
    safe_state: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class SafetyGoal:
    sg_id: str = ""
    function: str = ""
    hazard: str = ""
    asil: str = ""
    sg_text: str = ""
    safe_state: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class ProbedHara:
    path: str = ""
    item_meta: dict[str, str] = field(default_factory=dict)
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""

    sheet_names: list[str] = field(default_factory=list)
    likely_hara_sheet: str = ""
    likely_safety_goals_sheet: str = ""
    likely_doc_control_sheet: str = ""
    likely_assumptions_sheet: str = ""
    likely_environment_sheet: str = ""
    likely_functions_sheet: str = ""

    revision_history_rows: int = 0
    has_table_of_contents: bool = False
    references_sheet: str = ""

    functions: list[dict] = field(default_factory=list)
    malfunctions_used: set[str] = field(default_factory=set)
    operating_environment: list[dict] = field(default_factory=list)

    hara_rows: list[HaraRow] = field(default_factory=list)
    safety_goals: list[SafetyGoal] = field(default_factory=list)

    is_hara_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

HARA_BUILDER_HARA_TAB = "12_HARA_Worksheet"
HARA_BUILDER_SG_TAB = "13_Safety_Goals"
HARA_BUILDER_TITLE_TAB = "00_Title_Page"
HARA_BUILDER_DOC_CTRL_TAB = "01_Document_Control"
HARA_BUILDER_ASSUMPTIONS_TAB = "02_Assumptions"
HARA_BUILDER_ENVIRONMENT_TAB = "06_Operating_Environment"
HARA_BUILDER_FUNCTIONS_TAB = "04_Functions"


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
    """
    Find the header row by looking for a row with at least 3 non-empty cells (or 2, as a fallback — see #63)
    that look like column headers. Returns (row_index, header_to_col_map).
    """
    # #63: prefer a >=3-cell header; accept a 2-cell header only if no wider row exists,
    # so a two-column tab is located without letting a 2-cell key/value row pre-empt a real header.
    fallback: tuple[int, dict[str, int]] = (0, {})
    for r in range(1, min(ws.max_row, max_search) + 1):
        cells = [(c, _norm(ws.cell(r, c).value)) for c in range(1, ws.max_column + 1)]
        non_empty = [(c, v) for c, v in cells if v]
        if len(non_empty) >= 2:
            # Heuristic: header row tends to have short text strings, few digits, bold formatting
            if all(len(v) < 60 and not v.startswith("=") for c, v in non_empty):
                header_map = {v.lower(): c for c, v in non_empty}
                if len(non_empty) >= 3:
                    return r, header_map
                if not fallback[0]:
                    fallback = (r, header_map)
    return fallback


def _col_for(header_map: dict[str, int], candidates: list[str]) -> int:
    """Find the first matching column by partial-match of any candidate keyword."""
    for cand in candidates:
        cand_lower = cand.lower()
        for header, col in header_map.items():
            if cand_lower in header:
                return col
    return 0


# ---------------------------------------------------------------------------
# Probe orchestrator
# ---------------------------------------------------------------------------

def probe(xlsx_path: str | Path) -> ProbedHara:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedHara(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect hara-builder format by tab signature
    p.is_hara_builder_format = (
        HARA_BUILDER_HARA_TAB in wb.sheetnames and
        HARA_BUILDER_SG_TAB in wb.sheetnames
    )
    if p.is_hara_builder_format:
        p.detection_notes.append("Detected hara-builder format by tab names.")

    # Likely sheets
    p.likely_hara_sheet = HARA_BUILDER_HARA_TAB if p.is_hara_builder_format else _find_sheet_by_keywords(p.sheet_names, ["hara", "hazard", "worksheet"])
    p.likely_safety_goals_sheet = HARA_BUILDER_SG_TAB if p.is_hara_builder_format else _find_sheet_by_keywords(p.sheet_names, ["safety goal", "safety_goal", "sg"])
    p.likely_doc_control_sheet = HARA_BUILDER_DOC_CTRL_TAB if p.is_hara_builder_format else _find_sheet_by_keywords(p.sheet_names, ["doc control", "document control", "revision"])
    p.likely_assumptions_sheet = HARA_BUILDER_ASSUMPTIONS_TAB if p.is_hara_builder_format else _find_sheet_by_keywords(p.sheet_names, ["assumption", "scope"])
    p.likely_environment_sheet = HARA_BUILDER_ENVIRONMENT_TAB if p.is_hara_builder_format else _find_sheet_by_keywords(p.sheet_names, ["environment", "operating", "situation"])
    p.likely_functions_sheet = HARA_BUILDER_FUNCTIONS_TAB if p.is_hara_builder_format else _find_sheet_by_keywords(p.sheet_names, ["function"])

    # Title / metadata
    title_sheet_name = HARA_BUILDER_TITLE_TAB if p.is_hara_builder_format else _find_sheet_by_keywords(p.sheet_names, ["title"])
    if title_sheet_name and title_sheet_name in wb.sheetnames:
        ws = wb[title_sheet_name]
        # Scan first 30 rows for label/value pairs
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                if not label:
                    continue
                # Look for value in the next column
                value = _norm(ws.cell(r, c + 1).value)
                if not value:
                    continue
                if "project" in label and not p.project:
                    p.project = value
                elif "document id" in label or "doc id" in label or "doc_id" in label:
                    p.doc_id = value
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
                p.item_meta[label] = value
        # Also check for big header rows that hold the document title
        for r in range(1, min(ws.max_row + 1, 5)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value)
                if v and len(v) > 10 and not p.title:
                    p.title = v
                    break

    # Doc control / revision history
    if p.likely_doc_control_sheet and p.likely_doc_control_sheet in wb.sheetnames:
        ws = wb[p.likely_doc_control_sheet]
        # Count rows after the header that have non-empty Revision column
        header_row, header_map = _find_header_row(ws)
        if header_row:
            rev_col = _col_for(header_map, ["revision"])
            if rev_col:
                count = 0
                for r in range(header_row + 1, ws.max_row + 1):
                    if _norm(ws.cell(r, rev_col).value):
                        count += 1
                p.revision_history_rows = count

    # TOC detection — look for first content tab being "Title" or "Contents" or similar
    p.has_table_of_contents = any(
        _contains_any(s, ["title", "content", "toc", "general info"])
        for s in p.sheet_names[:3]
    )

    # References sheet
    p.references_sheet = _find_sheet_by_keywords(p.sheet_names, ["reference", "general info", "biblio"])

    # Functions
    if p.likely_functions_sheet and p.likely_functions_sheet in wb.sheetnames:
        ws = wb[p.likely_functions_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            id_col = _col_for(header_map, ["function id", "id"])
            name_col = _col_for(header_map, ["function name", "name"])
            desc_col = _col_for(header_map, ["description"])
            for r in range(header_row + 1, ws.max_row + 1):
                fid = _norm(ws.cell(r, id_col).value) if id_col else ""
                fname = _norm(ws.cell(r, name_col).value) if name_col else ""
                if not (fid or fname):
                    continue
                p.functions.append({
                    "id": fid,
                    "name": fname,
                    "description": _norm(ws.cell(r, desc_col).value) if desc_col else "",
                })

    # Operating environment
    if p.likely_environment_sheet and p.likely_environment_sheet in wb.sheetnames:
        ws = wb[p.likely_environment_sheet]
        # Just count rows that look like environment entries
        header_row, header_map = _find_header_row(ws)
        if header_row:
            for r in range(header_row + 1, ws.max_row + 1):
                row_vals = [_norm(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)]
                if any(row_vals):
                    p.operating_environment.append({"row": r, "values": [v for v in row_vals if v]})

    # Main HARA worksheet rows
    if p.likely_hara_sheet and p.likely_hara_sheet in wb.sheetnames:
        ws = wb[p.likely_hara_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "function": _col_for(header_map, ["function name", "function"]),
                "malfunction": _col_for(header_map, ["malfunction"]),
                "location": _col_for(header_map, ["location"]),
                "speed": _col_for(header_map, ["speed band", "speed"]),
                "weather": _col_for(header_map, ["weather"]),
                "hazard": _col_for(header_map, ["hazardous event", "hazard"]),
                "s": _col_for(header_map, ["severity", "s"]) if False else 0,
                "s_rationale": _col_for(header_map, ["s rationale", "severity rationale"]),
                "e_rationale": _col_for(header_map, ["e rationale", "exposure rationale"]),
                "c_rationale": _col_for(header_map, ["c rationale", "controllability rationale"]),
                "asil": _col_for(header_map, ["asil"]),
                "safe": _col_for(header_map, ["safe state"]),
            }
            # Need exact-match S/E/C columns — _col_for partial match would catch "ASIL" first for "S" etc
            # so we search by exact header
            for header, col in header_map.items():
                if header == "s":
                    cols["s"] = col
                elif header == "e":
                    cols["e"] = col
                elif header == "c":
                    cols["c"] = col

            for r in range(header_row + 1, ws.max_row + 1):
                row = HaraRow(
                    function=_norm(ws.cell(r, cols["function"]).value) if cols["function"] else "",
                    malfunction=_norm(ws.cell(r, cols["malfunction"]).value) if cols["malfunction"] else "",
                    location=_norm(ws.cell(r, cols["location"]).value) if cols["location"] else "",
                    speed_band=_norm(ws.cell(r, cols["speed"]).value) if cols["speed"] else "",
                    weather=_norm(ws.cell(r, cols["weather"]).value) if cols["weather"] else "",
                    hazardous_event=_norm(ws.cell(r, cols["hazard"]).value) if cols["hazard"] else "",
                    s=_norm(ws.cell(r, cols["s"]).value) if cols["s"] else "",
                    s_rationale=_norm(ws.cell(r, cols["s_rationale"]).value) if cols["s_rationale"] else "",
                    e=_norm(ws.cell(r, cols["e"]).value) if cols["e"] else "",
                    e_rationale=_norm(ws.cell(r, cols["e_rationale"]).value) if cols["e_rationale"] else "",
                    c=_norm(ws.cell(r, cols["c"]).value) if cols["c"] else "",
                    c_rationale=_norm(ws.cell(r, cols["c_rationale"]).value) if cols["c_rationale"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    safe_state=_norm(ws.cell(r, cols["safe"]).value) if cols["safe"] else "",
                    sheet=p.likely_hara_sheet,
                    row=r,
                )
                if row.function or row.malfunction or row.hazardous_event:
                    p.hara_rows.append(row)
                    if row.malfunction:
                        p.malfunctions_used.add(row.malfunction)

    # Safety Goals
    if p.likely_safety_goals_sheet and p.likely_safety_goals_sheet in wb.sheetnames:
        ws = wb[p.likely_safety_goals_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "sg_id": _col_for(header_map, ["sg_id", "sg id", "id"]),
                "function": _col_for(header_map, ["function"]),
                "hazard": _col_for(header_map, ["hazard"]),
                "asil": _col_for(header_map, ["asil"]),
                "sg_text": _col_for(header_map, ["safety goal", "sg text"]),
                "safe": _col_for(header_map, ["safe state"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                sg = SafetyGoal(
                    sg_id=_norm(ws.cell(r, cols["sg_id"]).value) if cols["sg_id"] else "",
                    function=_norm(ws.cell(r, cols["function"]).value) if cols["function"] else "",
                    hazard=_norm(ws.cell(r, cols["hazard"]).value) if cols["hazard"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    sg_text=_norm(ws.cell(r, cols["sg_text"]).value) if cols["sg_text"] else "",
                    safe_state=_norm(ws.cell(r, cols["safe"]).value) if cols["safe"] else "",
                    sheet=p.likely_safety_goals_sheet,
                    row=r,
                )
                if sg.sg_id and sg.sg_id.upper().startswith("SG"):
                    p.safety_goals.append(sg)

    # Project info fallback
    if not p.project and p.item_meta.get("project"):
        p.project = p.item_meta["project"]

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "is_hara_builder_format": p.is_hara_builder_format,
        "title": p.title,
        "doc_id": p.doc_id,
        "revision": p.revision,
        "status": p.status,
        "author": p.author,
        "approver": p.approver,
        "project": p.project,
        "sheets": p.sheet_names,
        "n_functions": len(p.functions),
        "n_malfunctions_used": len(p.malfunctions_used),
        "n_environment_rows": len(p.operating_environment),
        "n_hara_rows": len(p.hara_rows),
        "n_safety_goals": len(p.safety_goals),
        "revision_history_rows": p.revision_history_rows,
        "has_table_of_contents": p.has_table_of_contents,
        "detection_notes": p.detection_notes,
    }
    print(json.dumps(summary, indent=2))
