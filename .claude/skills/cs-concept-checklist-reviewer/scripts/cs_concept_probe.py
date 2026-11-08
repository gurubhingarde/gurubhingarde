"""
CS Concept content probe — extracts block diagram, CSR catalog, CSI handoff, and verification.

Reads: 00_Title_Page, 01_Document_Control, 02_CS_Goals_Echo, 03_System_Block_Diagram,
       04_CS_Concept_Argument, 05_CSR_Catalog, 06_CAL_Allocation, 07_Verification_Matrix,
       08_CSI_Handoff, 09_References

Returns a structured ProbedCSConcept dict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class BlockDiagramNode:
    node_id: str = ""
    node_name: str = ""
    description: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class CSREntry:
    csr_id: str = ""
    description: str = ""
    csg_ref: str = ""
    cal: str = ""
    property: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class VerificationMethod:
    csr_id: str = ""
    method: str = ""
    cal: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class ProbedCSConcept:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""
    sheet_names: list[str] = field(default_factory=list)

    n_csg_echo: int = 0
    n_block_diagram_nodes: int = 0
    n_csr: int = 0
    n_verification_methods: int = 0

    block_nodes: list[BlockDiagramNode] = field(default_factory=list)
    csr_entries: list[CSREntry] = field(default_factory=list)
    verification_methods: list[VerificationMethod] = field(default_factory=list)

    cal_distribution: dict[str, int] = field(default_factory=dict)
    properties_covered: set[str] = field(default_factory=set)
    verification_methods_by_cal: dict[str, set[str]] = field(default_factory=dict)

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


def probe(xlsx_path: str | Path) -> ProbedCSConcept:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedCSConcept(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

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

    # Block Diagram
    bd_sheet = _find_sheet_by_keywords(p.sheet_names, ["block diagram", "03_system"])
    if bd_sheet and bd_sheet in wb.sheetnames:
        ws = wb[bd_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            id_col = _col_for(header_map, ["node id", "id"])
            name_col = _col_for(header_map, ["node name", "name"])
            desc_col = _col_for(header_map, ["description"])
            for r in range(header_row + 1, ws.max_row + 1):
                nid = _norm(ws.cell(r, id_col).value) if id_col else ""
                nname = _norm(ws.cell(r, name_col).value) if name_col else ""
                if not (nid or nname):
                    continue
                node = BlockDiagramNode(
                    node_id=nid,
                    node_name=nname,
                    description=_norm(ws.cell(r, desc_col).value) if desc_col else "",
                    sheet=bd_sheet,
                    row=r,
                )
                p.block_nodes.append(node)

    p.n_block_diagram_nodes = len(p.block_nodes)

    # CSR Catalog
    csr_sheet = _find_sheet_by_keywords(p.sheet_names, ["csr catalog", "05_csr"])
    if csr_sheet and csr_sheet in wb.sheetnames:
        ws = wb[csr_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            id_col = _col_for(header_map, ["csr id", "id"])
            desc_col = _col_for(header_map, ["description"])
            csg_col = _col_for(header_map, ["csg ref", "csg"])
            cal_col = _col_for(header_map, ["cal"])
            prop_col = _col_for(header_map, ["property"])
            for r in range(header_row + 1, ws.max_row + 1):
                csr_id = _norm(ws.cell(r, id_col).value) if id_col else ""
                desc = _norm(ws.cell(r, desc_col).value) if desc_col else ""
                if not (csr_id or desc):
                    continue
                cal = _norm(ws.cell(r, cal_col).value) if cal_col else ""
                prop = _norm(ws.cell(r, prop_col).value) if prop_col else ""
                csr = CSREntry(
                    csr_id=csr_id,
                    description=desc,
                    csg_ref=_norm(ws.cell(r, csg_col).value) if csg_col else "",
                    cal=cal,
                    property=prop,
                    sheet=csr_sheet,
                    row=r,
                )
                p.csr_entries.append(csr)
                if cal:
                    p.cal_distribution[cal] = p.cal_distribution.get(cal, 0) + 1
                if prop:
                    p.properties_covered.add(prop)

    p.n_csr = len(p.csr_entries)

    # Verification Matrix
    vm_sheet = _find_sheet_by_keywords(p.sheet_names, ["verification", "07_verification"])
    if vm_sheet and vm_sheet in wb.sheetnames:
        ws = wb[vm_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            csr_col = _col_for(header_map, ["csr id", "csr"])
            method_col = _col_for(header_map, ["verification method", "method"])
            cal_col = _col_for(header_map, ["cal"])
            for r in range(header_row + 1, ws.max_row + 1):
                csr_id = _norm(ws.cell(r, csr_col).value) if csr_col else ""
                method = _norm(ws.cell(r, method_col).value) if method_col else ""
                if not (csr_id or method):
                    continue
                cal = _norm(ws.cell(r, cal_col).value) if cal_col else ""
                vm = VerificationMethod(
                    csr_id=csr_id,
                    method=method,
                    cal=cal,
                    sheet=vm_sheet,
                    row=r,
                )
                p.verification_methods.append(vm)
                if cal:
                    if cal not in p.verification_methods_by_cal:
                        p.verification_methods_by_cal[cal] = set()
                    p.verification_methods_by_cal[cal].add(method)

    p.n_verification_methods = len(p.verification_methods)
    p.has_table_of_contents = any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3])

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "title": p.title,
        "n_block_nodes": p.n_block_diagram_nodes,
        "n_csr": p.n_csr,
        "n_verification_methods": p.n_verification_methods,
        "cal_distribution": p.cal_distribution,
        "properties_covered": list(p.properties_covered),
    }
    print(json.dumps(summary, indent=2))
