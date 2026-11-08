"""
ASPICE Gap Analysis content probe — extracts gap analysis artifact content from xlsx.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class ProbedGapAnalysis:
    path: str = ""
    sheet_names: list[str] = field(default_factory=list)

    # Title metadata
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    assessment_ref: str = ""
    project: str = ""
    doc_id: str = ""

    # Content
    current_state_rows: int = 0
    target_cl_rows: int = 0
    gap_rows: int = 0
    gap_severity_values: set[str] = field(default_factory=set)
    effort_estimated: bool = False
    quick_wins_identified: bool = False
    major_initiatives_present: bool = False
    cross_process_deps_noted: bool = False
    effort_totals_present: bool = False

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
            if all(len(v) < 80 and not v.startswith("=") for c, v in non_empty):
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


def probe(xlsx_path: str | Path) -> ProbedGapAnalysis:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedGapAnalysis(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Title metadata
    title_sheet = _find_sheet_by_keywords(p.sheet_names, ["title", "cover"])
    if title_sheet and title_sheet in wb.sheetnames:
        ws = wb[title_sheet]
        for r in range(1, min(ws.max_row + 1, 40)):
            for c in range(1, min(ws.max_column + 1, 5)):
                label = _norm(ws.cell(r, c).value).lower()
                if not label:
                    continue
                value = _norm(ws.cell(r, c + 1).value)
                if not value:
                    continue
                if "assessment" in label and "ref" in label:
                    p.assessment_ref = value
                elif "revision" in label:
                    p.revision = value
                elif "status" in label:
                    p.status = value
                elif "author" in label:
                    p.author = value
                elif "approver" in label:
                    p.approver = value

    # Current State tab (echo from Assessment)
    current_sheet = _find_sheet_by_keywords(p.sheet_names, ["current state", "current"])
    if current_sheet and current_sheet in wb.sheetnames:
        ws = wb[current_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            p.current_state_rows = max(0, ws.max_row - header_row)

    # Target CL tab
    target_sheet = _find_sheet_by_keywords(p.sheet_names, ["target", "goal"])
    if target_sheet and target_sheet in wb.sheetnames:
        ws = wb[target_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            p.target_cl_rows = max(0, ws.max_row - header_row)

    # Gaps tab
    gaps_sheet = _find_sheet_by_keywords(p.sheet_names, ["gap", "finding"])
    if gaps_sheet and gaps_sheet in wb.sheetnames:
        ws = wb[gaps_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            p.gap_rows = max(0, ws.max_row - header_row)
            severity_col = _col_for(header_map, ["severity"])
            if severity_col:
                for r in range(header_row + 1, min(header_row + 100, ws.max_row + 1)):
                    sev = _norm(ws.cell(r, severity_col).value)
                    if sev and sev.lower() in ("show-stopper", "major", "minor", "observation"):
                        p.gap_severity_values.add(sev.lower())
            # Check for effort column
            effort_col = _col_for(header_map, ["effort", "estimate"])
            if effort_col:
                for r in range(header_row + 1, min(header_row + 50, ws.max_row + 1)):
                    eff = _norm(ws.cell(r, effort_col).value)
                    if eff and any(c.isdigit() for c in eff):
                        p.effort_estimated = True

    # Quick Wins tab
    quickwins_sheet = _find_sheet_by_keywords(p.sheet_names, ["quick win", "quick-win", "low hanging"])
    if quickwins_sheet and quickwins_sheet in wb.sheetnames:
        p.quick_wins_identified = True

    # Initiatives tab
    init_sheet = _find_sheet_by_keywords(p.sheet_names, ["initiative", "roadmap", "improvement"])
    if init_sheet and init_sheet in wb.sheetnames:
        ws = wb[init_sheet]
        if ws.max_row > 5:
            p.major_initiatives_present = True

    # Check for cross-process dependencies in gaps or initiatives
    for sheet_name in p.sheet_names:
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            text = " ".join(str(ws.cell(r, c).value or "")
                           for r in range(1, min(ws.max_row + 1, 100))
                           for c in range(1, min(ws.max_column + 1, 10)))
            if any(kw in text.lower() for kw in ["cross-process", "cross process", "dependency", "depend", "coupling"]):
                p.cross_process_deps_noted = True

    # Check for effort totals
    summary_sheet = _find_sheet_by_keywords(p.sheet_names, ["summary"])
    if summary_sheet and summary_sheet in wb.sheetnames:
        ws = wb[summary_sheet]
        text = " ".join(str(ws.cell(r, c).value or "")
                       for r in range(1, min(ws.max_row + 1, 50))
                       for c in range(1, min(ws.max_column + 1, 8)))
        if any(kw in text.lower() for kw in ["total effort", "total estimate", "effort summary"]):
            p.effort_totals_present = True

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "sheets": p.sheet_names,
        "current_state_rows": p.current_state_rows,
        "target_cl_rows": p.target_cl_rows,
        "gap_rows": p.gap_rows,
        "gap_severity_values": sorted(p.gap_severity_values),
        "effort_estimated": p.effort_estimated,
        "quick_wins_identified": p.quick_wins_identified,
        "major_initiatives_present": p.major_initiatives_present,
        "cross_process_deps_noted": p.cross_process_deps_noted,
    }
    print(json.dumps(summary, indent=2))
