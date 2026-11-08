"""
SW HSI Specification content probe — extracts SW-specific HSI content from xlsx.
Adapted from hsi-builder format with SW handler, SWC, RTOS task, debounce, and propagation columns.

Returns a structured ProbedSwHsis dict that downstream check functions consume.
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
class SwHsiSignal:
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
    asil: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class SwHandlerRow:
    signal_name: str = ""
    handler_function_name: str = ""
    allocated_swc: str = ""
    calling_task: str = ""
    call_frequency: str = ""
    max_execution_time: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class DebounceStrategyRow:
    signal_name: str = ""
    debounce_type: str = ""
    debounce_params: str = ""
    time_threshold_ms: str = ""
    n_of_m: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class FaultPropagationRow:
    signal_name: str = ""
    failure_mode: str = ""
    detection_mechanism: str = ""
    vehicle_reaction: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class RtosIntegrationRow:
    task_name: str = ""
    task_priority: str = ""
    period_ms: str = ""
    timeout_ms: str = ""
    signals_processed: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class InitSequenceRow:
    sequence_number: str = ""
    step_description: str = ""
    sw_init_action: str = ""
    hw_bist_reference: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class TestCaseRow:
    test_id: str = ""
    handler_name: str = ""
    test_type: str = ""
    input_signal: str = ""
    expected_behavior: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class ProbedSwHsis:
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
    likely_sw_handler_sheet: str = ""
    likely_debounce_sheet: str = ""
    likely_fault_propagation_sheet: str = ""
    likely_rtos_sheet: str = ""
    likely_init_seq_sheet: str = ""
    likely_test_cases_sheet: str = ""
    likely_references_sheet: str = ""

    revision_history_rows: int = 0
    has_table_of_contents: bool = False

    hsi_signals: list[SwHsiSignal] = field(default_factory=list)
    sw_handlers: list[SwHandlerRow] = field(default_factory=list)
    debounce_strategies: list[DebounceStrategyRow] = field(default_factory=list)
    fault_propagation_rows: list[FaultPropagationRow] = field(default_factory=list)
    rtos_integration_rows: list[RtosIntegrationRow] = field(default_factory=list)
    init_sequence_rows: list[InitSequenceRow] = field(default_factory=list)
    test_case_rows: list[TestCaseRow] = field(default_factory=list)

    is_sw_hsis_builder_format: bool = False
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

def probe(xlsx_path: str | Path) -> ProbedSwHsis:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedSwHsis(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect sw-hsis-builder format by tab signature
    p.is_sw_hsis_builder_format = any(
        s in wb.sheetnames for s in [
            "00_Title_Page", "01_Document_Control", "02_HSI_Signal_Catalog_Echo",
            "03_SW_Handler_Catalog", "04_Debounce_Strategy_per_Signal"
        ]
    )
    if p.is_sw_hsis_builder_format:
        p.detection_notes.append("Detected sw-hsis-builder format by tab names.")

    # Likely sheets
    p.likely_title_sheet = "00_Title_Page" if p.is_sw_hsis_builder_format else _find_sheet_by_keywords(p.sheet_names, ["title"])
    p.likely_doc_control_sheet = "01_Document_Control" if p.is_sw_hsis_builder_format else _find_sheet_by_keywords(p.sheet_names, ["document control", "revision"])
    p.likely_signal_catalog_sheet = "02_HSI_Signal_Catalog_Echo" if p.is_sw_hsis_builder_format else _find_sheet_by_keywords(p.sheet_names, ["hsi", "signal catalog"])
    p.likely_sw_handler_sheet = "03_SW_Handler_Catalog" if p.is_sw_hsis_builder_format else _find_sheet_by_keywords(p.sheet_names, ["handler", "sw handler"])
    p.likely_debounce_sheet = "04_Debounce_Strategy_per_Signal" if p.is_sw_hsis_builder_format else _find_sheet_by_keywords(p.sheet_names, ["debounce"])
    p.likely_fault_propagation_sheet = "05_Fault_Propagation_Maps" if p.is_sw_hsis_builder_format else _find_sheet_by_keywords(p.sheet_names, ["fault", "propagation"])
    p.likely_rtos_sheet = "06_RTOS_Integration" if p.is_sw_hsis_builder_format else _find_sheet_by_keywords(p.sheet_names, ["rtos", "task"])
    p.likely_init_seq_sheet = "07_Init_Sequence_SW_Side" if p.is_sw_hsis_builder_format else _find_sheet_by_keywords(p.sheet_names, ["init", "initialization"])
    p.likely_test_cases_sheet = "08_Test_Cases" if p.is_sw_hsis_builder_format else _find_sheet_by_keywords(p.sheet_names, ["test"])
    p.likely_references_sheet = "10_References" if p.is_sw_hsis_builder_format else _find_sheet_by_keywords(p.sheet_names, ["reference"])

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

    # HSI Signal Catalog (Echo from source HSI)
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
                "asil": _col_for(header_map, ["asil"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                sig = SwHsiSignal(
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
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    sheet=p.likely_signal_catalog_sheet,
                    row=r,
                )
                if sig.name:
                    p.hsi_signals.append(sig)

    # SW Handler Catalog
    if p.likely_sw_handler_sheet and p.likely_sw_handler_sheet in wb.sheetnames:
        ws = wb[p.likely_sw_handler_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "signal": _col_for(header_map, ["signal"]),
                "handler_func": _col_for(header_map, ["handler", "function", "function name"]),
                "swc": _col_for(header_map, ["swc", "software component"]),
                "task": _col_for(header_map, ["task", "rtos task"]),
                "frequency": _col_for(header_map, ["frequency", "call frequency"]),
                "max_time": _col_for(header_map, ["max", "execution time", "time"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                handler = SwHandlerRow(
                    signal_name=_norm(ws.cell(r, cols["signal"]).value) if cols["signal"] else "",
                    handler_function_name=_norm(ws.cell(r, cols["handler_func"]).value) if cols["handler_func"] else "",
                    allocated_swc=_norm(ws.cell(r, cols["swc"]).value) if cols["swc"] else "",
                    calling_task=_norm(ws.cell(r, cols["task"]).value) if cols["task"] else "",
                    call_frequency=_norm(ws.cell(r, cols["frequency"]).value) if cols["frequency"] else "",
                    max_execution_time=_norm(ws.cell(r, cols["max_time"]).value) if cols["max_time"] else "",
                    sheet=p.likely_sw_handler_sheet,
                    row=r,
                )
                if handler.signal_name or handler.handler_function_name:
                    p.sw_handlers.append(handler)

    # Debounce Strategy
    if p.likely_debounce_sheet and p.likely_debounce_sheet in wb.sheetnames:
        ws = wb[p.likely_debounce_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "signal": _col_for(header_map, ["signal"]),
                "debounce_type": _col_for(header_map, ["debounce", "type"]),
                "params": _col_for(header_map, ["parameters", "params"]),
                "time_threshold": _col_for(header_map, ["time", "threshold"]),
                "n_of_m": _col_for(header_map, ["n of m", "n-of-m"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                debounce = DebounceStrategyRow(
                    signal_name=_norm(ws.cell(r, cols["signal"]).value) if cols["signal"] else "",
                    debounce_type=_norm(ws.cell(r, cols["debounce_type"]).value) if cols["debounce_type"] else "",
                    debounce_params=_norm(ws.cell(r, cols["params"]).value) if cols["params"] else "",
                    time_threshold_ms=_norm(ws.cell(r, cols["time_threshold"]).value) if cols["time_threshold"] else "",
                    n_of_m=_norm(ws.cell(r, cols["n_of_m"]).value) if cols["n_of_m"] else "",
                    sheet=p.likely_debounce_sheet,
                    row=r,
                )
                if debounce.signal_name:
                    p.debounce_strategies.append(debounce)

    # Fault Propagation Maps
    if p.likely_fault_propagation_sheet and p.likely_fault_propagation_sheet in wb.sheetnames:
        ws = wb[p.likely_fault_propagation_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "signal": _col_for(header_map, ["signal"]),
                "failure": _col_for(header_map, ["failure", "fault"]),
                "detection": _col_for(header_map, ["detection", "mechanism"]),
                "vehicle_reaction": _col_for(header_map, ["vehicle", "reaction"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                fp = FaultPropagationRow(
                    signal_name=_norm(ws.cell(r, cols["signal"]).value) if cols["signal"] else "",
                    failure_mode=_norm(ws.cell(r, cols["failure"]).value) if cols["failure"] else "",
                    detection_mechanism=_norm(ws.cell(r, cols["detection"]).value) if cols["detection"] else "",
                    vehicle_reaction=_norm(ws.cell(r, cols["vehicle_reaction"]).value) if cols["vehicle_reaction"] else "",
                    sheet=p.likely_fault_propagation_sheet,
                    row=r,
                )
                if fp.signal_name or fp.failure_mode:
                    p.fault_propagation_rows.append(fp)

    # RTOS Integration
    if p.likely_rtos_sheet and p.likely_rtos_sheet in wb.sheetnames:
        ws = wb[p.likely_rtos_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "task_name": _col_for(header_map, ["task", "name"]),
                "priority": _col_for(header_map, ["priority"]),
                "period": _col_for(header_map, ["period"]),
                "timeout": _col_for(header_map, ["timeout"]),
                "signals": _col_for(header_map, ["signals", "processed"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                rtos = RtosIntegrationRow(
                    task_name=_norm(ws.cell(r, cols["task_name"]).value) if cols["task_name"] else "",
                    task_priority=_norm(ws.cell(r, cols["priority"]).value) if cols["priority"] else "",
                    period_ms=_norm(ws.cell(r, cols["period"]).value) if cols["period"] else "",
                    timeout_ms=_norm(ws.cell(r, cols["timeout"]).value) if cols["timeout"] else "",
                    signals_processed=_norm(ws.cell(r, cols["signals"]).value) if cols["signals"] else "",
                    sheet=p.likely_rtos_sheet,
                    row=r,
                )
                if rtos.task_name:
                    p.rtos_integration_rows.append(rtos)

    # Initialization Sequence
    if p.likely_init_seq_sheet and p.likely_init_seq_sheet in wb.sheetnames:
        ws = wb[p.likely_init_seq_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "seq_num": _col_for(header_map, ["sequence", "number"]),
                "description": _col_for(header_map, ["description", "step"]),
                "sw_action": _col_for(header_map, ["sw", "software"]),
                "hw_bist": _col_for(header_map, ["bist", "hardware"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                init_seq = InitSequenceRow(
                    sequence_number=_norm(ws.cell(r, cols["seq_num"]).value) if cols["seq_num"] else "",
                    step_description=_norm(ws.cell(r, cols["description"]).value) if cols["description"] else "",
                    sw_init_action=_norm(ws.cell(r, cols["sw_action"]).value) if cols["sw_action"] else "",
                    hw_bist_reference=_norm(ws.cell(r, cols["hw_bist"]).value) if cols["hw_bist"] else "",
                    sheet=p.likely_init_seq_sheet,
                    row=r,
                )
                if init_seq.sequence_number or init_seq.step_description:
                    p.init_sequence_rows.append(init_seq)

    # Test Cases
    if p.likely_test_cases_sheet and p.likely_test_cases_sheet in wb.sheetnames:
        ws = wb[p.likely_test_cases_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "test_id": _col_for(header_map, ["test id", "id"]),
                "handler": _col_for(header_map, ["handler"]),
                "test_type": _col_for(header_map, ["test type", "type"]),
                "input_signal": _col_for(header_map, ["input", "signal"]),
                "expected": _col_for(header_map, ["expected", "behavior"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                tc = TestCaseRow(
                    test_id=_norm(ws.cell(r, cols["test_id"]).value) if cols["test_id"] else "",
                    handler_name=_norm(ws.cell(r, cols["handler"]).value) if cols["handler"] else "",
                    test_type=_norm(ws.cell(r, cols["test_type"]).value) if cols["test_type"] else "",
                    input_signal=_norm(ws.cell(r, cols["input_signal"]).value) if cols["input_signal"] else "",
                    expected_behavior=_norm(ws.cell(r, cols["expected"]).value) if cols["expected"] else "",
                    sheet=p.likely_test_cases_sheet,
                    row=r,
                )
                if tc.test_id or tc.handler_name:
                    p.test_case_rows.append(tc)

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "is_sw_hsis_builder_format": p.is_sw_hsis_builder_format,
        "title": p.title,
        "doc_id": p.doc_id,
        "revision": p.revision,
        "status": p.status,
        "author": p.author,
        "approver": p.approver,
        "project": p.project,
        "sheets": p.sheet_names,
        "n_signals": len(p.hsi_signals),
        "n_handlers": len(p.sw_handlers),
        "n_debounce_strategies": len(p.debounce_strategies),
        "n_fault_propagations": len(p.fault_propagation_rows),
        "n_rtos_rows": len(p.rtos_integration_rows),
        "n_init_sequence_rows": len(p.init_sequence_rows),
        "n_test_cases": len(p.test_case_rows),
        "revision_history_rows": p.revision_history_rows,
        "has_table_of_contents": p.has_table_of_contents,
        "detection_notes": p.detection_notes,
    }
    print(json.dumps(summary, indent=2))
