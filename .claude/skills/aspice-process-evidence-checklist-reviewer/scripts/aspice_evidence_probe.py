"""ASPICE Process Evidence content probe."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from openpyxl import load_workbook

@dataclass
class ProbedProcessEvidence:
    path: str = ""
    sheet_names: list[str] = field(default_factory=list)
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    process_owner: str = ""
    project: str = ""
    doc_id: str = ""
    process_desc_present: bool = False
    bp_evidence_rows: int = 0
    gp_evidence_rows: int = 0
    work_products_rows: int = 0
    perf_records_present: bool = False
    metrics_present: bool = False
    improv_log_present: bool = False
    evidence_current: bool = False
    evidence_accessible: bool = False
    cross_refs_present: bool = False

def _norm(s: Any) -> str:
    if s is None: return ""
    return str(s).strip()

def _find_sheet_by_keywords(sheet_names: list[str], keywords: list[str]) -> str:
    for name in sheet_names:
        if any(k.lower() in name.lower() for k in keywords): return name
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

def probe(xlsx_path: str | Path) -> ProbedProcessEvidence:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedProcessEvidence(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    title_sheet = _find_sheet_by_keywords(p.sheet_names, ["title", "cover"])
    if title_sheet and title_sheet in wb.sheetnames:
        ws = wb[title_sheet]
        for r in range(1, min(ws.max_row + 1, 40)):
            for c in range(1, min(ws.max_column + 1, 5)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if label and value:
                    if "process owner" in label: p.process_owner = value
                    elif "revision" in label: p.revision = value
                    elif "status" in label: p.status = value
                    elif "author" in label: p.author = value
                    elif "approver" in label: p.approver = value

    desc_sheet = _find_sheet_by_keywords(p.sheet_names, ["process", "description"])
    if desc_sheet and desc_sheet in wb.sheetnames:
        ws = wb[desc_sheet]
        text = " ".join(str(ws.cell(r, c).value or "") for r in range(1, min(ws.max_row + 1, 30)) for c in range(1, min(ws.max_column + 1, 8)))
        if len(text) > 100: p.process_desc_present = True

    bp_sheet = _find_sheet_by_keywords(p.sheet_names, ["bp evidence", "base practice"])
    if bp_sheet and bp_sheet in wb.sheetnames:
        ws = wb[bp_sheet]
        header_row, _ = _find_header_row(ws)
        if header_row: p.bp_evidence_rows = max(0, ws.max_row - header_row)

    gp_sheet = _find_sheet_by_keywords(p.sheet_names, ["gp evidence", "generic practice"])
    if gp_sheet and gp_sheet in wb.sheetnames:
        ws = wb[gp_sheet]
        header_row, _ = _find_header_row(ws)
        if header_row: p.gp_evidence_rows = max(0, ws.max_row - header_row)

    wp_sheet = _find_sheet_by_keywords(p.sheet_names, ["work product", "artifact"])
    if wp_sheet and wp_sheet in wb.sheetnames:
        ws = wb[wp_sheet]
        header_row, _ = _find_header_row(ws)
        if header_row: p.work_products_rows = max(0, ws.max_row - header_row)

    perf_sheet = _find_sheet_by_keywords(p.sheet_names, ["performance", "record", "review"])
    if perf_sheet and perf_sheet in wb.sheetnames:
        p.perf_records_present = True

    metric_sheet = _find_sheet_by_keywords(p.sheet_names, ["metric", "measure", "performance"])
    if metric_sheet and metric_sheet in wb.sheetnames:
        p.metrics_present = True

    improv_sheet = _find_sheet_by_keywords(p.sheet_names, ["improvement", "action"])
    if improv_sheet and improv_sheet in wb.sheetnames:
        p.improv_log_present = True

    for sheet_name in p.sheet_names:
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            text = " ".join(str(ws.cell(r, c).value or "") for r in range(1, min(ws.max_row + 1, 50)) for c in range(1, min(ws.max_column + 1, 10)))
            if any(kw in text.lower() for kw in ["current", "version", "dated", "updated", "assessment window"]): p.evidence_current = True
            if any(kw in text.lower() for kw in ["accessible", "available", "provided", "location", "path"]): p.evidence_accessible = True
            if any(kw in text.lower() for kw in ["cross", "reference", "link", "refer"]): p.cross_refs_present = True

    return p

if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    print(json.dumps({
        "path": p.path,
        "sheets": p.sheet_names,
        "process_desc_present": p.process_desc_present,
        "bp_evidence_rows": p.bp_evidence_rows,
        "gp_evidence_rows": p.gp_evidence_rows,
        "work_products_rows": p.work_products_rows,
        "perf_records_present": p.perf_records_present,
        "metrics_present": p.metrics_present,
    }, indent=2))
