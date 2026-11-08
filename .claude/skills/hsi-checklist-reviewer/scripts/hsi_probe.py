"""
HSI Specification content probe — best-effort extractor for HSI xlsx files.
Works on hsi-builder outputs and other HSI specification formats via keyword heuristics.

Returns a structured ProbedHsi dict that downstream check functions consume.
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
class HsiSignal:
    name: str = ""
    direction: str = ""
    data_type: str = ""
    bit_width: str = ""
    range: str = ""
    units: str = ""
    encoding: str = ""
    integrity_protection: str = ""
    validity_bit: str = ""
    owner: str = ""
    linked_fsr: str = ""
    linked_mechanism: str = ""
    asil: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class RegisterMapRow:
    register_name: str = ""
    address: str = ""
    description: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class TimingRow:
    signal_name: str = ""
    sample_rate: str = ""
    max_age: str = ""
    latency_budget: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class FailureModeRow:
    signal_name: str = ""
    failure_mode: str = ""
    detection_mechanism: str = ""
    reaction: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class TestCaseRow:
    test_id: str = ""
    signal_name: str = ""
    test_type: str = ""
    expected_behavior: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class ProbedHsi:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""

    sheet_names: list[str] = field(default_factory=list)
    likely_title_sheet: str = ""
    likely_doc_control_sheet: str = ""
    likely_signal_catalog_sheet: str = ""
    likely_register_map_sheet: str = ""
    likely_timing_sheet: str = ""
    likely_failure_modes_sheet: str = ""
    likely_init_seq_sheet: str = ""
    likely_xref_sheet: str = ""
    likely_test_cases_sheet: str = ""
    likely_references_sheet: str = ""

    revision_history_rows: int = 0
    has_table_of_contents: bool = False

    hsi_signals: list[HsiSignal] = field(default_factory=list)
    register_map_rows: list[RegisterMapRow] = field(default_factory=list)
    timing_rows: list[TimingRow] = field(default_factory=list)
    failure_mode_rows: list[FailureModeRow] = field(default_factory=list)
    test_case_rows: list[TestCaseRow] = field(default_factory=list)
    init_sequence: str = ""
    xref_table: str = ""

    is_hsi_builder_format: bool = False
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
    """Find the first matching column by partial-match."""
    for cand in candidates:
        cand_lower = cand.lower()
        for header, col in header_map.items():
            if cand_lower in header:
                return col
    return 0


# ---------------------------------------------------------------------------
# Probe orchestrator
# ---------------------------------------------------------------------------

def probe(xlsx_path: str | Path) -> ProbedHsi:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedHsi(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect hsi-builder format by tab signature
    p.is_hsi_builder_format = any(
        s in wb.sheetnames for s in [
            "00_Title_Page", "01_Document_Control", "02_HSI_Signal_Catalog",
            "03_Register_Map", "04_Timing_Specification"
        ]
    )
    if p.is_hsi_builder_format:
        p.detection_notes.append("Detected hsi-builder format by tab names.")

    # Likely sheets
    p.likely_title_sheet = "00_Title_Page" if p.is_hsi_builder_format else _find_sheet_by_keywords(p.sheet_names, ["title"])
    p.likely_doc_control_sheet = "01_Document_Control" if p.is_hsi_builder_format else _find_sheet_by_keywords(p.sheet_names, ["document control", "revision"])
    p.likely_signal_catalog_sheet = "02_HSI_Signal_Catalog" if p.is_hsi_builder_format else _find_sheet_by_keywords(p.sheet_names, ["signal", "catalog", "signal catalog"])
    p.likely_register_map_sheet = "03_Register_Map" if p.is_hsi_builder_format else _find_sheet_by_keywords(p.sheet_names, ["register"])
    p.likely_timing_sheet = "04_Timing_Specification" if p.is_hsi_builder_format else _find_sheet_by_keywords(p.sheet_names, ["timing"])
    p.likely_failure_modes_sheet = "05_Failure_Modes_and_Reactions" if p.is_hsi_builder_format else _find_sheet_by_keywords(p.sheet_names, ["failure", "fault"])
    p.likely_init_seq_sheet = "06_Initialization_Sequence" if p.is_hsi_builder_format else _find_sheet_by_keywords(p.sheet_names, ["init", "initialization"])
    p.likely_xref_sheet = "07_Cross_Reference" if p.is_hsi_builder_format else _find_sheet_by_keywords(p.sheet_names, ["cross", "xref", "reference"])
    p.likely_test_cases_sheet = "09_Test_Cases" if p.is_hsi_builder_format else _find_sheet_by_keywords(p.sheet_names, ["test"])
    p.likely_references_sheet = "10_References" if p.is_hsi_builder_format else _find_sheet_by_keywords(p.sheet_names, ["reference"])

    # Title / metadata
    if p.likely_title_sheet and p.likely_title_sheet in wb.sheetnames:
        ws = wb[p.likely_title_sheet]
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
                elif "document id" in label or "doc id" in label:
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
        # Check for big header rows
        for r in range(1, min(ws.max_row + 1, 5)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value)
                if v and len(v) > 10 and not p.title:
                    p.title = v
                    break

    # Doc control / revision history
    if p.likely_doc_control_sheet and p.likely_doc_control_sheet in wb.sheetnames:
        ws = wb[p.likely_doc_control_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            rev_col = _col_for(header_map, ["revision"])
            if rev_col:
                count = 0
                for r in range(header_row + 1, ws.max_row + 1):
                    if _norm(ws.cell(r, rev_col).value):
                        count += 1
                p.revision_history_rows = count

    # TOC detection
    p.has_table_of_contents = any(
        _contains_any(s, ["title", "content", "toc", "general info"])
        for s in p.sheet_names[:3]
    )

    # HSI Signal Catalog
    if p.likely_signal_catalog_sheet and p.likely_signal_catalog_sheet in wb.sheetnames:
        ws = wb[p.likely_signal_catalog_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "name": _col_for(header_map, ["signal name", "name"]),
                "direction": _col_for(header_map, ["direction"]),
                "data_type": _col_for(header_map, ["data type", "type"]),
                "bit_width": _col_for(header_map, ["bit width", "bits", "width"]),
                "range": _col_for(header_map, ["range"]),
                "units": _col_for(header_map, ["units", "unit"]),
                "encoding": _col_for(header_map, ["encoding"]),
                "integrity": _col_for(header_map, ["integrity", "protection"]),
                "validity": _col_for(header_map, ["validity", "valid"]),
                "owner": _col_for(header_map, ["owner", "owned"]),
                "fsr": _col_for(header_map, ["fsr", "fsr_id"]),
                "mechanism": _col_for(header_map, ["mechanism", "function"]),
                "asil": _col_for(header_map, ["asil"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                sig = HsiSignal(
                    name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    direction=_norm(ws.cell(r, cols["direction"]).value) if cols["direction"] else "",
                    data_type=_norm(ws.cell(r, cols["data_type"]).value) if cols["data_type"] else "",
                    bit_width=_norm(ws.cell(r, cols["bit_width"]).value) if cols["bit_width"] else "",
                    range=_norm(ws.cell(r, cols["range"]).value) if cols["range"] else "",
                    units=_norm(ws.cell(r, cols["units"]).value) if cols["units"] else "",
                    encoding=_norm(ws.cell(r, cols["encoding"]).value) if cols["encoding"] else "",
                    integrity_protection=_norm(ws.cell(r, cols["integrity"]).value) if cols["integrity"] else "",
                    validity_bit=_norm(ws.cell(r, cols["validity"]).value) if cols["validity"] else "",
                    owner=_norm(ws.cell(r, cols["owner"]).value) if cols["owner"] else "",
                    linked_fsr=_norm(ws.cell(r, cols["fsr"]).value) if cols["fsr"] else "",
                    linked_mechanism=_norm(ws.cell(r, cols["mechanism"]).value) if cols["mechanism"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    sheet=p.likely_signal_catalog_sheet,
                    row=r,
                )
                if sig.name:
                    p.hsi_signals.append(sig)

    # Register Map
    if p.likely_register_map_sheet and p.likely_register_map_sheet in wb.sheetnames:
        ws = wb[p.likely_register_map_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "name": _col_for(header_map, ["register", "name"]),
                "address": _col_for(header_map, ["address"]),
                "desc": _col_for(header_map, ["description", "desc"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                row = RegisterMapRow(
                    register_name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    address=_norm(ws.cell(r, cols["address"]).value) if cols["address"] else "",
                    description=_norm(ws.cell(r, cols["desc"]).value) if cols["desc"] else "",
                    sheet=p.likely_register_map_sheet,
                    row=r,
                )
                if row.register_name:
                    p.register_map_rows.append(row)

    # Timing Specification
    if p.likely_timing_sheet and p.likely_timing_sheet in wb.sheetnames:
        ws = wb[p.likely_timing_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "signal": _col_for(header_map, ["signal"]),
                "sample_rate": _col_for(header_map, ["sample", "rate"]),
                "max_age": _col_for(header_map, ["max age", "age"]),
                "latency": _col_for(header_map, ["latency", "budget"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                timing = TimingRow(
                    signal_name=_norm(ws.cell(r, cols["signal"]).value) if cols["signal"] else "",
                    sample_rate=_norm(ws.cell(r, cols["sample_rate"]).value) if cols["sample_rate"] else "",
                    max_age=_norm(ws.cell(r, cols["max_age"]).value) if cols["max_age"] else "",
                    latency_budget=_norm(ws.cell(r, cols["latency"]).value) if cols["latency"] else "",
                    sheet=p.likely_timing_sheet,
                    row=r,
                )
                if timing.signal_name:
                    p.timing_rows.append(timing)

    # Failure Modes & Reactions
    if p.likely_failure_modes_sheet and p.likely_failure_modes_sheet in wb.sheetnames:
        ws = wb[p.likely_failure_modes_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "signal": _col_for(header_map, ["signal"]),
                "failure": _col_for(header_map, ["failure", "fault"]),
                "detection": _col_for(header_map, ["detection", "mechanism"]),
                "reaction": _col_for(header_map, ["reaction", "response"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                fm = FailureModeRow(
                    signal_name=_norm(ws.cell(r, cols["signal"]).value) if cols["signal"] else "",
                    failure_mode=_norm(ws.cell(r, cols["failure"]).value) if cols["failure"] else "",
                    detection_mechanism=_norm(ws.cell(r, cols["detection"]).value) if cols["detection"] else "",
                    reaction=_norm(ws.cell(r, cols["reaction"]).value) if cols["reaction"] else "",
                    sheet=p.likely_failure_modes_sheet,
                    row=r,
                )
                if fm.signal_name or fm.failure_mode:
                    p.failure_mode_rows.append(fm)

    # Test Cases
    if p.likely_test_cases_sheet and p.likely_test_cases_sheet in wb.sheetnames:
        ws = wb[p.likely_test_cases_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "test_id": _col_for(header_map, ["test id", "id"]),
                "signal": _col_for(header_map, ["signal"]),
                "test_type": _col_for(header_map, ["test type", "type"]),
                "expected": _col_for(header_map, ["expected", "behavior"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                tc = TestCaseRow(
                    test_id=_norm(ws.cell(r, cols["test_id"]).value) if cols["test_id"] else "",
                    signal_name=_norm(ws.cell(r, cols["signal"]).value) if cols["signal"] else "",
                    test_type=_norm(ws.cell(r, cols["test_type"]).value) if cols["test_type"] else "",
                    expected_behavior=_norm(ws.cell(r, cols["expected"]).value) if cols["expected"] else "",
                    sheet=p.likely_test_cases_sheet,
                    row=r,
                )
                if tc.test_id or tc.signal_name:
                    p.test_case_rows.append(tc)

    # Initialization Sequence and Cross-Reference (content capture)
    if p.likely_init_seq_sheet and p.likely_init_seq_sheet in wb.sheetnames:
        ws = wb[p.likely_init_seq_sheet]
        p.init_sequence = f"Tab '{p.likely_init_seq_sheet}' present ({ws.max_row} rows)"

    if p.likely_xref_sheet and p.likely_xref_sheet in wb.sheetnames:
        ws = wb[p.likely_xref_sheet]
        p.xref_table = f"Tab '{p.likely_xref_sheet}' present ({ws.max_row} rows)"

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "is_hsi_builder_format": p.is_hsi_builder_format,
        "title": p.title,
        "doc_id": p.doc_id,
        "revision": p.revision,
        "status": p.status,
        "author": p.author,
        "approver": p.approver,
        "project": p.project,
        "sheets": p.sheet_names,
        "n_signals": len(p.hsi_signals),
        "n_registers": len(p.register_map_rows),
        "n_timing_rows": len(p.timing_rows),
        "n_failure_modes": len(p.failure_mode_rows),
        "n_test_cases": len(p.test_case_rows),
        "revision_history_rows": p.revision_history_rows,
        "has_table_of_contents": p.has_table_of_contents,
        "detection_notes": p.detection_notes,
    }
    print(json.dumps(summary, indent=2))
