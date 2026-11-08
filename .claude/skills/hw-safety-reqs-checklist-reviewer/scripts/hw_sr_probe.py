"""
HW Safety Requirements content probe — extracts HW-SR metadata and catalog.

Returns a structured ProbedHwSR dict that downstream check functions consume.
Works best on hw-safety-reqs-builder outputs but applies heuristics to other formats.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class HwSafetyRequirement:
    """Single HW-SR catalog entry."""
    sr_id: str = ""
    parent_tsr: str = ""
    asil: str = ""
    allocated_hw_element: str = ""
    text: str = ""
    target_dc: str = ""
    verification_method: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class ProbedHwSR:
    path: str = ""

    # Metadata
    title: str = ""
    doc_id: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    linked_tsc: str = ""
    item_meta: dict[str, str] = field(default_factory=dict)

    # Sheets
    sheet_names: list[str] = field(default_factory=list)

    # Content counts
    hw_tsrs_imported_count: int = 0
    hw_tsrs_imported_sample: list[str] = field(default_factory=list)

    # HW-SR catalog
    hw_srs: list[HwSafetyRequirement] = field(default_factory=list)

    # Failure mode mapping
    failure_mode_mapping_rows: int = 0

    # HSI references
    hsi_references: int = 0

    # Verification methods per HW-SR
    verification_methods_covered: set[str] = field(default_factory=set)

    # Test strategy
    test_strategy_rows: int = 0
    test_strategy_topics: set[str] = field(default_factory=set)

    # Independence considerations
    independence_docs: int = 0

    # Format detection
    is_hw_sr_builder_format: bool = False
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
    """Find the header row by looking for a row with at least 3 non-empty cells."""
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

def probe(xlsx_path: str | Path) -> ProbedHwSR:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedHwSR(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect hw-safety-reqs-builder format by tab signature
    expected_tabs = [
        "00_Title_Page", "01_Document_Control", "02_HW_TSRs_From_TSC",
        "03_HW_Safety_Requirements", "04_Failure_Mode_Mapping",
        "05_HSI_Reference", "06_Verification_Methods"
    ]
    p.is_hw_sr_builder_format = all(t in wb.sheetnames for t in expected_tabs[:4])
    if p.is_hw_sr_builder_format:
        p.detection_notes.append("Detected hw-safety-reqs-builder format by tab names.")

    # Title / metadata
    title_sheet = "00_Title_Page" if p.is_hw_sr_builder_format else _find_sheet_by_keywords(p.sheet_names, ["title"])
    if title_sheet and title_sheet in wb.sheetnames:
        ws = wb[title_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if not label or not value:
                    continue
                if "project" in label and not p.project:
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
                elif "linked tsc" in label or "tsc" in label:
                    p.linked_tsc = value
                elif "title" == label or "document title" in label:
                    if not p.title:
                        p.title = value
                p.item_meta[label] = value

        # Also check for big title
        for r in range(1, min(ws.max_row + 1, 5)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value)
                if v and len(v) > 10 and not p.title:
                    p.title = v
                    break

    # HW-TSRs From TSC (tab 02)
    tsr_sheet = "02_HW_TSRs_From_TSC" if p.is_hw_sr_builder_format else _find_sheet_by_keywords(p.sheet_names, ["tsr", "tsrs"])
    if tsr_sheet and tsr_sheet in wb.sheetnames:
        ws = wb[tsr_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            tsr_col = _col_for(header_map, ["tsr id", "tsr_id", "id"])
            count = 0
            sample = []
            for r in range(header_row + 1, min(ws.max_row + 1, header_row + 200)):
                tsr_id = _norm(ws.cell(r, tsr_col).value) if tsr_col else ""
                if tsr_id:
                    count += 1
                    if len(sample) < 3:
                        sample.append(tsr_id)
            p.hw_tsrs_imported_count = count
            p.hw_tsrs_imported_sample = sample

    # HW-SR Catalog (tab 03)
    sr_sheet = "03_HW_Safety_Requirements" if p.is_hw_sr_builder_format else _find_sheet_by_keywords(p.sheet_names, ["hw safety requirement", "hw_sr", "requirement"])
    if sr_sheet and sr_sheet in wb.sheetnames:
        ws = wb[sr_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["sr id", "sr_id", "id"]),
                "parent_tsr": _col_for(header_map, ["parent tsr", "parent_tsr", "tsr"]),
                "asil": _col_for(header_map, ["asil"]),
                "hw_element": _col_for(header_map, ["allocated hw element", "hw_element", "element"]),
                "text": _col_for(header_map, ["requirement text", "text"]),
                "target_dc": _col_for(header_map, ["target dc", "target_dc", "dc"]),
                "verification": _col_for(header_map, ["verification method", "verification_method", "method"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                sr_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                if not sr_id:
                    continue
                sr = HwSafetyRequirement(
                    sr_id=sr_id,
                    parent_tsr=_norm(ws.cell(r, cols["parent_tsr"]).value) if cols["parent_tsr"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    allocated_hw_element=_norm(ws.cell(r, cols["hw_element"]).value) if cols["hw_element"] else "",
                    text=_norm(ws.cell(r, cols["text"]).value) if cols["text"] else "",
                    target_dc=_norm(ws.cell(r, cols["target_dc"]).value) if cols["target_dc"] else "",
                    verification_method=_norm(ws.cell(r, cols["verification"]).value) if cols["verification"] else "",
                    sheet=sr_sheet,
                    row=r,
                )
                p.hw_srs.append(sr)
                if sr.verification_method:
                    p.verification_methods_covered.add(sr.verification_method)

    # Failure Mode Mapping (tab 04)
    fmm_sheet = "04_Failure_Mode_Mapping" if p.is_hw_sr_builder_format else _find_sheet_by_keywords(p.sheet_names, ["failure mode", "fmea", "fmm"])
    if fmm_sheet and fmm_sheet in wb.sheetnames:
        ws = wb[fmm_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            count = 0
            for r in range(header_row + 1, ws.max_row + 1):
                row_vals = [_norm(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)]
                if any(row_vals):
                    count += 1
            p.failure_mode_mapping_rows = count

    # HSI Reference (tab 05)
    hsi_sheet = "05_HSI_Reference" if p.is_hw_sr_builder_format else _find_sheet_by_keywords(p.sheet_names, ["hsi", "interface"])
    if hsi_sheet and hsi_sheet in wb.sheetnames:
        ws = wb[hsi_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            count = 0
            for r in range(header_row + 1, ws.max_row + 1):
                row_vals = [_norm(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)]
                if any(row_vals):
                    count += 1
            p.hsi_references = count

    # Verification Methods (tab 06)
    vm_sheet = "06_Verification_Methods" if p.is_hw_sr_builder_format else _find_sheet_by_keywords(p.sheet_names, ["verification method", "verification"])
    if vm_sheet and vm_sheet in wb.sheetnames:
        ws = wb[vm_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            method_col = _col_for(header_map, ["method"])
            for r in range(header_row + 1, ws.max_row + 1):
                method = _norm(ws.cell(r, method_col).value) if method_col else ""
                if method:
                    p.verification_methods_covered.add(method)

    # Test Strategy (tab 07)
    ts_sheet = "07_Test_Strategy" if p.is_hw_sr_builder_format else _find_sheet_by_keywords(p.sheet_names, ["test strategy", "test"])
    if ts_sheet and ts_sheet in wb.sheetnames:
        ws = wb[ts_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            topic_col = _col_for(header_map, ["topic", "test topic"])
            count = 0
            for r in range(header_row + 1, ws.max_row + 1):
                row_vals = [_norm(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)]
                if any(row_vals):
                    count += 1
                    if topic_col:
                        topic = _norm(ws.cell(r, topic_col).value)
                        if topic:
                            p.test_strategy_topics.add(topic)
            p.test_strategy_rows = count

    # Independence Considerations (tab 08)
    ind_sheet = "08_Independence_Considerations" if p.is_hw_sr_builder_format else _find_sheet_by_keywords(p.sheet_names, ["independence"])
    if ind_sheet and ind_sheet in wb.sheetnames:
        ws = wb[ind_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            count = 0
            for r in range(header_row + 1, ws.max_row + 1):
                row_vals = [_norm(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)]
                if any(row_vals):
                    count += 1
            p.independence_docs = count

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "is_hw_sr_builder_format": p.is_hw_sr_builder_format,
        "title": p.title,
        "doc_id": p.doc_id,
        "revision": p.revision,
        "status": p.status,
        "author": p.author,
        "approver": p.approver,
        "project": p.project,
        "linked_tsc": p.linked_tsc,
        "hw_tsrs_imported_count": p.hw_tsrs_imported_count,
        "hw_tsrs_sample": p.hw_tsrs_imported_sample,
        "hw_srs_count": len(p.hw_srs),
        "failure_mode_mapping_rows": p.failure_mode_mapping_rows,
        "hsi_references": p.hsi_references,
        "verification_methods_count": len(p.verification_methods_covered),
        "test_strategy_rows": p.test_strategy_rows,
        "independence_docs": p.independence_docs,
        "detection_notes": p.detection_notes,
    }
    print(json.dumps(summary, indent=2))
