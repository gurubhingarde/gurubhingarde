"""
ASPICE Assessment content probe — extracts assessment artifact content from xlsx.
Returns structured ProbedAssessment dict for downstream check functions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class ProbedAssessment:
    path: str = ""
    sheet_names: list[str] = field(default_factory=list)

    # Title metadata
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    lead_assessor: str = ""
    project: str = ""
    doc_id: str = ""
    assessment_date: str = ""

    # Assessment content
    assessment_scope_rows: int = 0
    process_areas_in_scope: set[str] = field(default_factory=set)
    prm_refs: set[str] = field(default_factory=set)
    pam_refs: set[str] = field(default_factory=set)

    # BP/GP Assessment
    bp_assessment_rows: int = 0
    gp_assessment_rows: int = 0
    target_cl_stated: bool = False

    # PA Ratings
    pa_ratings_rows: int = 0
    pa_scale_values: set[str] = field(default_factory=set)

    # CL Rating
    cl_profile_present: bool = False
    capability_levels_used: set[str] = field(default_factory=set)

    # Validation
    assessor_signoff: bool = False
    sample_size_noted: bool = False
    findings_present: bool = False

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
    """Find header row by looking for a row with 3+ non-empty cells."""
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
    """Find first matching column by partial-match of candidate keyword."""
    for cand in candidates:
        cand_lower = cand.lower()
        for header, col in header_map.items():
            if cand_lower in header:
                return col
    return 0


def probe(xlsx_path: str | Path) -> ProbedAssessment:
    """Probe ASPICE Assessment xlsx."""
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedAssessment(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Title metadata — scan first sheet for label/value pairs
    title_sheet = _find_sheet_by_keywords(p.sheet_names, ["title", "cover", "assessment"])
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
                if "lead assessor" in label or "assessment lead" in label:
                    p.lead_assessor = value
                elif "revision" in label:
                    p.revision = value
                elif "status" in label:
                    p.status = value
                elif "author" in label:
                    p.author = value
                elif "approver" in label:
                    p.approver = value
                elif "assessment date" in label or "date" in label:
                    p.assessment_date = value
                elif "project" in label:
                    p.project = value

    # Assessment Scope tab
    scope_sheet = _find_sheet_by_keywords(p.sheet_names, ["assessment scope", "scope"])
    if scope_sheet and scope_sheet in wb.sheetnames:
        ws = wb[scope_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            p.assessment_scope_rows = ws.max_row - header_row
            # Extract process area list
            pa_col = _col_for(header_map, ["process", "pa"])
            if pa_col:
                for r in range(header_row + 1, ws.max_row + 1):
                    pa = _norm(ws.cell(r, pa_col).value)
                    if pa and len(pa) <= 10:
                        p.process_areas_in_scope.add(pa)

    # Process area tabs (SYS, SWE, SUP, MAN, ACQ, etc.) — count populated rows
    for pa_code in ["SYS", "SWE", "SUP", "MAN", "ACQ"]:
        pa_sheet = _find_sheet_by_keywords(p.sheet_names, [pa_code])
        if pa_sheet and pa_sheet in wb.sheetnames:
            p.process_areas_in_scope.add(pa_code)

    # BP Assessment tab
    bp_sheet = _find_sheet_by_keywords(p.sheet_names, ["bp assessment", "base practice"])
    if bp_sheet and bp_sheet in wb.sheetnames:
        ws = wb[bp_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            p.bp_assessment_rows = max(0, ws.max_row - header_row)

    # GP Assessment tab
    gp_sheet = _find_sheet_by_keywords(p.sheet_names, ["gp assessment", "generic practice"])
    if gp_sheet and gp_sheet in wb.sheetnames:
        ws = wb[gp_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            p.gp_assessment_rows = max(0, ws.max_row - header_row)

    # PA Rating tab
    pa_sheet = _find_sheet_by_keywords(p.sheet_names, ["pa rating", "process attribute"])
    if pa_sheet and pa_sheet in wb.sheetnames:
        ws = wb[pa_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            p.pa_ratings_rows = max(0, ws.max_row - header_row)
            # Detect rating scale (N/P/L/F)
            rating_col = _col_for(header_map, ["rating"])
            if rating_col:
                for r in range(header_row + 1, min(header_row + 50, ws.max_row + 1)):
                    rating = _norm(ws.cell(r, rating_col).value)
                    if rating and rating.upper() in ("N", "P", "L", "F"):
                        p.pa_scale_values.add(rating.upper())

    # Capability Level / CL Profile tab
    cl_sheet = _find_sheet_by_keywords(p.sheet_names, ["capability", "cl ", "rating"])
    if cl_sheet and cl_sheet in wb.sheetnames:
        ws = wb[cl_sheet]
        # Check for capability profile presence
        if ws.max_row > 5:
            p.cl_profile_present = True
            header_row, header_map = _find_header_row(ws)
            if header_row:
                cl_col = _col_for(header_map, ["cl", "capability level"])
                if cl_col:
                    for r in range(header_row + 1, ws.max_row + 1):
                        cl = _norm(ws.cell(r, cl_col).value)
                        if cl and cl[0] in ("0", "1", "2", "3"):
                            p.capability_levels_used.add(cl)

    # Check for signoff / approval section
    for sheet_name in p.sheet_names:
        if "signoff" in sheet_name.lower() or "approval" in sheet_name.lower():
            p.assessor_signoff = True

    # Estimate findings presence
    summary_sheet = _find_sheet_by_keywords(p.sheet_names, ["summary"])
    if summary_sheet and summary_sheet in wb.sheetnames:
        ws = wb[summary_sheet]
        text = " ".join(str(ws.cell(r, c).value or "")
                       for r in range(1, min(ws.max_row + 1, 50))
                       for c in range(1, min(ws.max_column + 1, 8)))
        if any(kw in text.lower() for kw in ["strength", "weakness", "finding", "issue", "gap"]):
            p.findings_present = True

    if not p.lead_assessor and p.author:
        p.lead_assessor = p.author

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "sheets": p.sheet_names,
        "lead_assessor": p.lead_assessor,
        "assessment_date": p.assessment_date,
        "process_areas_in_scope": sorted(p.process_areas_in_scope),
        "bp_assessment_rows": p.bp_assessment_rows,
        "gp_assessment_rows": p.gp_assessment_rows,
        "pa_ratings_rows": p.pa_ratings_rows,
        "cl_profile_present": p.cl_profile_present,
        "capability_levels_used": sorted(p.capability_levels_used),
        "assessor_signoff": p.assessor_signoff,
        "findings_present": p.findings_present,
    }
    print(json.dumps(summary, indent=2))
