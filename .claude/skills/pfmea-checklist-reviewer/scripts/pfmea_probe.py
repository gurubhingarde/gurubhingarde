"""
PFMEA content probe — extracts metadata, process flow, process functions,
failure modes, risk priority, action plan, and control plan linkage
from pfmea-builder outputs (AIAG-VDA 2019).

Returns a structured ProbedPfmea dict for downstream check functions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class ProcessFlowStep:
    step_id: str = ""
    step_type: str = ""  # e.g., Process, Equipment, Assembly
    equipment: str = ""
    characteristics: str = ""
    row: int = 0


@dataclass
class ProcessFunction:
    step_id: str = ""
    function_id: str = ""
    function_description: str = ""
    row: int = 0


@dataclass
class PfmeaRow:
    step_id: str = ""
    failure_mode: str = ""
    failure_effect: str = ""
    severity: int = 0  # 1-10
    failure_cause: str = ""
    occurrence: int = 0  # 1-10
    prevention_control: str = ""
    detection_control: str = ""
    detection: int = 0  # 1-10
    action_priority: int = 0  # calculated: S*O*D
    recommended_action: str = ""
    responsibility: str = ""
    target_completion: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class SpecialCharacteristic:
    characteristic: str = ""
    related_severity: int = 0
    row: int = 0


@dataclass
class ActionPlanItem:
    action_id: str = ""
    action_description: str = ""
    responsible: str = ""
    due_date: str = ""
    status: str = ""
    row: int = 0


@dataclass
class ControlPlanLinkage:
    failure_mode: str = ""
    control_method: str = ""
    sample_size: str = ""
    row: int = 0


@dataclass
class ProbedPfmea:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""

    sheet_names: list[str] = field(default_factory=list)

    # Header block
    part_number: str = ""
    part_name: str = ""
    process_name: str = ""
    date_prepared: str = ""

    # Process flow
    process_flow_steps: list[ProcessFlowStep] = field(default_factory=list)

    # Process functions
    process_functions: list[ProcessFunction] = field(default_factory=list)

    # PFMEA worksheet rows
    pfmea_rows: list[PfmeaRow] = field(default_factory=list)

    # Special characteristics
    special_characteristics: list[SpecialCharacteristic] = field(default_factory=list)

    # Action plan
    action_plan_items: list[ActionPlanItem] = field(default_factory=list)

    # Control plan linkage
    control_plan_linkages: list[ControlPlanLinkage] = field(default_factory=list)

    # Metrics
    high_ap_count: int = 0  # AP >= 100
    completed_actions: int = 0

    # Flags
    is_pfmea_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


def _norm(s: Any) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _int_or_zero(s: Any) -> int:
    try:
        val = int(_norm(s))
        return val if val > 0 else 0
    except (ValueError, AttributeError):
        return 0


def _find_header_row(ws, max_search: int = 30) -> tuple[int, dict[str, int]]:
    """Find header row by looking for a row with 3+ non-empty cells."""
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
    """Find first matching column by partial match."""
    for cand in candidates:
        cand_lower = cand.lower()
        for header, col in header_map.items():
            if cand_lower in header:
                return col
    return 0


def probe(xlsx_path: str | Path) -> ProbedPfmea:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedPfmea(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect pfmea-builder format
    expected_tabs = ["00_Title_Page", "02_Header_Block", "05_PFMEA_Worksheet"]
    p.is_pfmea_builder_format = all(tab in wb.sheetnames for tab in expected_tabs)
    if p.is_pfmea_builder_format:
        p.detection_notes.append("Detected pfmea-builder format by tab names.")

    # Title and metadata
    if "00_Title_Page" in wb.sheetnames:
        ws = wb["00_Title_Page"]
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
                elif "title" in label or "process" in label:
                    if not p.title:
                        p.title = value

    # Header block (part number, name, process name, date)
    if "02_Header_Block" in wb.sheetnames:
        ws = wb["02_Header_Block"]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 4)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if not label or not value:
                    continue
                if "part number" in label:
                    p.part_number = value
                elif "part name" in label:
                    p.part_name = value
                elif "process name" in label:
                    p.process_name = value
                elif "date" in label and "prepared" in label:
                    p.date_prepared = value

    # Process flow
    if "03_Process_Flow" in wb.sheetnames:
        ws = wb["03_Process_Flow"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "step_id": _col_for(header_map, ["step id", "id"]),
                "type": _col_for(header_map, ["type", "step type"]),
                "equipment": _col_for(header_map, ["equipment"]),
                "characteristics": _col_for(header_map, ["characteristics", "process characteristics"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                step_id = _norm(ws.cell(r, cols["step_id"]).value) if cols["step_id"] else ""
                if not step_id:
                    continue
                p.process_flow_steps.append(ProcessFlowStep(
                    step_id=step_id,
                    step_type=_norm(ws.cell(r, cols["type"]).value) if cols["type"] else "",
                    equipment=_norm(ws.cell(r, cols["equipment"]).value) if cols["equipment"] else "",
                    characteristics=_norm(ws.cell(r, cols["characteristics"]).value) if cols["characteristics"] else "",
                    row=r,
                ))

    # Process functions
    if "04_Process_Function_Analysis" in wb.sheetnames:
        ws = wb["04_Process_Function_Analysis"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "step_id": _col_for(header_map, ["step id", "id"]),
                "func_id": _col_for(header_map, ["function id"]),
                "func_desc": _col_for(header_map, ["function", "description"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                func_id = _norm(ws.cell(r, cols["func_id"]).value) if cols["func_id"] else ""
                if not func_id:
                    continue
                p.process_functions.append(ProcessFunction(
                    step_id=_norm(ws.cell(r, cols["step_id"]).value) if cols["step_id"] else "",
                    function_id=func_id,
                    function_description=_norm(ws.cell(r, cols["func_desc"]).value) if cols["func_desc"] else "",
                    row=r,
                ))

    # PFMEA worksheet
    if "05_PFMEA_Worksheet" in wb.sheetnames:
        ws = wb["05_PFMEA_Worksheet"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "step_id": _col_for(header_map, ["step id", "id"]),
                "fm": _col_for(header_map, ["failure mode"]),
                "fe": _col_for(header_map, ["failure effect"]),
                "s": _col_for(header_map, ["severity", "s"]),
                "fc": _col_for(header_map, ["failure cause", "cause"]),
                "o": _col_for(header_map, ["occurrence", "o"]),
                "pc": _col_for(header_map, ["prevention control", "prevention"]),
                "dc": _col_for(header_map, ["detection control", "detection"]),
                "d": _col_for(header_map, ["detection", "d"]),
                "ap": _col_for(header_map, ["action priority", "ap"]),
                "action": _col_for(header_map, ["recommended action", "action"]),
                "resp": _col_for(header_map, ["responsibility", "responsible", "owner"]),
                "due": _col_for(header_map, ["due date", "target completion"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                step_id = _norm(ws.cell(r, cols["step_id"]).value) if cols["step_id"] else ""
                fm = _norm(ws.cell(r, cols["fm"]).value) if cols["fm"] else ""
                if not (step_id or fm):
                    continue
                s_val = _int_or_zero(ws.cell(r, cols["s"]).value) if cols["s"] else 0
                o_val = _int_or_zero(ws.cell(r, cols["o"]).value) if cols["o"] else 0
                d_val = _int_or_zero(ws.cell(r, cols["d"]).value) if cols["d"] else 0
                ap_val = _int_or_zero(ws.cell(r, cols["ap"]).value) if cols["ap"] else (s_val * o_val * d_val)

                p.pfmea_rows.append(PfmeaRow(
                    step_id=step_id,
                    failure_mode=fm,
                    failure_effect=_norm(ws.cell(r, cols["fe"]).value) if cols["fe"] else "",
                    severity=s_val,
                    failure_cause=_norm(ws.cell(r, cols["fc"]).value) if cols["fc"] else "",
                    occurrence=o_val,
                    prevention_control=_norm(ws.cell(r, cols["pc"]).value) if cols["pc"] else "",
                    detection_control=_norm(ws.cell(r, cols["dc"]).value) if cols["dc"] else "",
                    detection=d_val,
                    action_priority=ap_val,
                    recommended_action=_norm(ws.cell(r, cols["action"]).value) if cols["action"] else "",
                    responsibility=_norm(ws.cell(r, cols["resp"]).value) if cols["resp"] else "",
                    target_completion=_norm(ws.cell(r, cols["due"]).value) if cols["due"] else "",
                    sheet="05_PFMEA_Worksheet",
                    row=r,
                ))

        # Count high AP items and completed actions
        p.high_ap_count = sum(1 for row in p.pfmea_rows if row.action_priority >= 100)
        p.completed_actions = sum(1 for row in p.pfmea_rows if row.action_priority >= 100 and row.recommended_action and "complete" in row.target_completion.lower())

    # Special characteristics
    if "06_Special_Characteristics" in wb.sheetnames:
        ws = wb["06_Special_Characteristics"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "characteristic": _col_for(header_map, ["characteristic"]),
                "severity": _col_for(header_map, ["severity", "related severity"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                char = _norm(ws.cell(r, cols["characteristic"]).value) if cols["characteristic"] else ""
                if not char:
                    continue
                p.special_characteristics.append(SpecialCharacteristic(
                    characteristic=char,
                    related_severity=_int_or_zero(ws.cell(r, cols["severity"]).value) if cols["severity"] else 0,
                    row=r,
                ))

    # Action plan
    if "08_Action_Plan_Tracker" in wb.sheetnames:
        ws = wb["08_Action_Plan_Tracker"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "action_id": _col_for(header_map, ["action id", "id"]),
                "action": _col_for(header_map, ["action"]),
                "resp": _col_for(header_map, ["responsible", "owner"]),
                "due": _col_for(header_map, ["due date"]),
                "status": _col_for(header_map, ["status"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                action_id = _norm(ws.cell(r, cols["action_id"]).value) if cols["action_id"] else ""
                if not action_id:
                    continue
                p.action_plan_items.append(ActionPlanItem(
                    action_id=action_id,
                    action_description=_norm(ws.cell(r, cols["action"]).value) if cols["action"] else "",
                    responsible=_norm(ws.cell(r, cols["resp"]).value) if cols["resp"] else "",
                    due_date=_norm(ws.cell(r, cols["due"]).value) if cols["due"] else "",
                    status=_norm(ws.cell(r, cols["status"]).value) if cols["status"] else "",
                    row=r,
                ))

    # Control plan linkage
    if "10_Linkage_to_Control_Plan" in wb.sheetnames:
        ws = wb["10_Linkage_to_Control_Plan"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "fm": _col_for(header_map, ["failure mode"]),
                "control": _col_for(header_map, ["control method"]),
                "sample": _col_for(header_map, ["sample size"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                fm = _norm(ws.cell(r, cols["fm"]).value) if cols["fm"] else ""
                if not fm:
                    continue
                p.control_plan_linkages.append(ControlPlanLinkage(
                    failure_mode=fm,
                    control_method=_norm(ws.cell(r, cols["control"]).value) if cols["control"] else "",
                    sample_size=_norm(ws.cell(r, cols["sample"]).value) if cols["sample"] else "",
                    row=r,
                ))

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "title": p.title,
        "process_name": p.process_name,
        "part_number": p.part_number,
        "n_process_flow_steps": len(p.process_flow_steps),
        "n_process_functions": len(p.process_functions),
        "n_pfmea_rows": len(p.pfmea_rows),
        "n_special_characteristics": len(p.special_characteristics),
        "n_action_plan_items": len(p.action_plan_items),
        "n_control_plan_linkages": len(p.control_plan_linkages),
        "high_ap_count": p.high_ap_count,
        "completed_actions": p.completed_actions,
        "is_pfmea_builder_format": p.is_pfmea_builder_format,
    }
    print(json.dumps(summary, indent=2))
