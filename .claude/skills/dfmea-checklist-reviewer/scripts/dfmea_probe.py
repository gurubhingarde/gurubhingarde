"""
DFMEA content probe — extracts metadata, header block, structure analysis,
function analysis, failure modes, special characteristics, and action plan items
from AIAG-VDA 2019 DFMEA worksheets.

Returns a structured ProbedDfmea dict for downstream check functions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class DfmeaRow:
    """Represents one failure mode row from 05_DFMEA_Worksheet."""
    item_id: str = ""
    focus_element: str = ""
    function: str = ""
    failure_mode: str = ""
    failure_effect: str = ""
    failure_cause: str = ""
    severity: int = 0
    failure_class: str = ""
    occurrence: int = 0
    prevention_control: str = ""
    detection_control: str = ""
    detection: int = 0
    action_priority: str = ""
    recommended_action: str = ""
    owner: str = ""
    status: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class SpecialCharacteristic:
    """Represents one Special Characteristic from 06_Special_Characteristics."""
    sc_id: str = ""
    description: str = ""
    severity: int = 0
    critical_dimension: bool = False
    control_method: str = ""


@dataclass
class ActionItem:
    """Represents one action from 08_Action_Plan_Tracker."""
    action_id: str = ""
    failure_mode_ref: str = ""
    action_description: str = ""
    owner: str = ""
    due_date: str = ""
    status: str = ""


@dataclass
class ProbedDfmea:
    """Complete extraction of DFMEA worksheet content."""
    path: str = ""
    title: str = ""
    part_number: str = ""
    design_responsibility: str = ""
    project_name: str = ""
    fmea_id: str = ""
    revision: str = ""
    status: str = ""
    date: str = ""

    sheet_names: list[str] = field(default_factory=list)

    # Header block (from 02_Header_Block)
    subject: str = ""
    fmea_owner: str = ""
    customer: str = ""
    model_years: str = ""
    confidential: bool = False

    # Structure analysis (from 03_Structure_Analysis)
    system_elements: list[str] = field(default_factory=list)
    subsystem_elements: list[str] = field(default_factory=list)
    component_elements: list[str] = field(default_factory=list)

    # Function analysis (from 04_Function_Analysis)
    functions: list[tuple[str, str]] = field(default_factory=list)  # (function_id, statement)

    # DFMEA worksheet rows
    dfmea_rows: list[DfmeaRow] = field(default_factory=list)

    # Special characteristics
    special_characteristics: list[SpecialCharacteristic] = field(default_factory=list)

    # Action plan items
    action_items: list[ActionItem] = field(default_factory=list)

    # Computed metrics
    total_failure_modes: int = 0
    high_ap_count: int = 0
    medium_ap_count: int = 0
    low_ap_count: int = 0

    # Flags
    is_dfmea_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


def _norm(s: Any) -> str:
    """Normalize cell value to string."""
    if s is None:
        return ""
    return str(s).strip()


def _int_or_zero(s: Any) -> int:
    """Parse integer or return 0."""
    try:
        val = int(_norm(s))
        return val if val >= 0 else 0
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


def probe(xlsx_path: str | Path) -> ProbedDfmea:
    """Extract DFMEA content from an AIAG-VDA 2019 DFMEA worksheet."""
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedDfmea(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect dfmea-builder format by tab signature
    expected_tabs = ["00_Title_Page", "02_Header_Block", "03_Structure_Analysis",
                     "04_Function_Analysis", "05_DFMEA_Worksheet"]
    p.is_dfmea_builder_format = all(tab in wb.sheetnames for tab in expected_tabs)
    if p.is_dfmea_builder_format:
        p.detection_notes.append("Detected dfmea-builder format by tab names.")

    # Title and metadata
    if "00_Title_Page" in wb.sheetnames:
        ws = wb["00_Title_Page"]
        for r in range(1, min(ws.max_row + 1, 50)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                if not label:
                    continue
                value = _norm(ws.cell(r, c + 1).value)
                if not value:
                    continue
                if "project" in label and not p.project_name:
                    p.project_name = value
                elif "part number" in label or "part_number" in label:
                    p.part_number = value
                elif "revision" in label and not p.revision:
                    p.revision = value
                elif "status" in label and not p.status:
                    p.status = value
                elif "date" in label and not p.date:
                    p.date = value
                elif "design responsibility" in label or "design owner" in label:
                    p.design_responsibility = value
                elif "title" == label or "document title" in label or "fmea subject" in label:
                    if not p.title:
                        p.title = value
                elif "fmea id" in label or "fmea_id" in label:
                    p.fmea_id = value
        # Check for title in first few rows
        for r in range(1, min(ws.max_row + 1, 5)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value)
                if v and len(v) > 10 and not p.title:
                    p.title = v
                    break

    # Header block (02_Header_Block)
    if "02_Header_Block" in wb.sheetnames:
        ws = wb["02_Header_Block"]
        for r in range(1, min(ws.max_row + 1, 40)):
            for c in range(1, min(ws.max_column + 1, 5)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if "subject" in label and not p.subject:
                    p.subject = value
                elif "fmea owner" in label or "team leader" in label:
                    p.fmea_owner = value
                elif "customer" in label and not p.customer:
                    p.customer = value
                elif "model year" in label or "model years" in label:
                    p.model_years = value
                elif "confidential" in label:
                    p.confidential = "yes" in value.lower()

    # Structure analysis (03_Structure_Analysis)
    if "03_Structure_Analysis" in wb.sheetnames:
        ws = wb["03_Structure_Analysis"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["element id", "id"]),
                "name": _col_for(header_map, ["name", "element", "description"]),
                "level": _col_for(header_map, ["level", "type"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                elem_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                name = _norm(ws.cell(r, cols["name"]).value) if cols["name"] else ""
                level = _norm(ws.cell(r, cols["level"]).value).lower() if cols["level"] else ""
                if not (elem_id or name):
                    continue
                if "system" in level:
                    p.system_elements.append(f"{elem_id}: {name}")
                elif "subsystem" in level:
                    p.subsystem_elements.append(f"{elem_id}: {name}")
                elif "component" in level:
                    p.component_elements.append(f"{elem_id}: {name}")

    # Function analysis (04_Function_Analysis)
    if "04_Function_Analysis" in wb.sheetnames:
        ws = wb["04_Function_Analysis"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["function id", "id"]),
                "statement": _col_for(header_map, ["function", "statement", "description"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                func_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                statement = _norm(ws.cell(r, cols["statement"]).value) if cols["statement"] else ""
                if func_id or statement:
                    p.functions.append((func_id, statement))

    # DFMEA worksheet (05_DFMEA_Worksheet)
    if "05_DFMEA_Worksheet" in wb.sheetnames:
        ws = wb["05_DFMEA_Worksheet"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "item": _col_for(header_map, ["item", "id", "item id"]),
                "focus": _col_for(header_map, ["focus", "element", "component"]),
                "function": _col_for(header_map, ["function"]),
                "fm": _col_for(header_map, ["failure mode", "fm"]),
                "fe": _col_for(header_map, ["failure effect", "effect"]),
                "cause": _col_for(header_map, ["failure cause", "cause"]),
                "s": _col_for(header_map, ["severity", "s"]),
                "fc": _col_for(header_map, ["failure class", "classification"]),
                "o": _col_for(header_map, ["occurrence", "o"]),
                "pc": _col_for(header_map, ["prevention control", "prevention"]),
                "dc": _col_for(header_map, ["detection control", "detection mechanism"]),
                "d": _col_for(header_map, ["detection", "d"]),
                "ap": _col_for(header_map, ["action priority", "ap"]),
                "action": _col_for(header_map, ["recommended action", "action", "recommendation"]),
                "owner": _col_for(header_map, ["owner", "responsible"]),
                "status": _col_for(header_map, ["status", "state"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                item_id = _norm(ws.cell(r, cols["item"]).value) if cols["item"] else ""
                fm = _norm(ws.cell(r, cols["fm"]).value) if cols["fm"] else ""
                if not (item_id or fm):
                    continue
                s = _int_or_zero(ws.cell(r, cols["s"]).value) if cols["s"] else 0
                o = _int_or_zero(ws.cell(r, cols["o"]).value) if cols["o"] else 0
                d = _int_or_zero(ws.cell(r, cols["d"]).value) if cols["d"] else 0
                ap = _norm(ws.cell(r, cols["ap"]).value) if cols["ap"] else ""
                p.dfmea_rows.append(DfmeaRow(
                    item_id=item_id,
                    focus_element=_norm(ws.cell(r, cols["focus"]).value) if cols["focus"] else "",
                    function=_norm(ws.cell(r, cols["function"]).value) if cols["function"] else "",
                    failure_mode=fm,
                    failure_effect=_norm(ws.cell(r, cols["fe"]).value) if cols["fe"] else "",
                    failure_cause=_norm(ws.cell(r, cols["cause"]).value) if cols["cause"] else "",
                    severity=s,
                    failure_class=_norm(ws.cell(r, cols["fc"]).value) if cols["fc"] else "",
                    occurrence=o,
                    prevention_control=_norm(ws.cell(r, cols["pc"]).value) if cols["pc"] else "",
                    detection_control=_norm(ws.cell(r, cols["dc"]).value) if cols["dc"] else "",
                    detection=d,
                    action_priority=ap,
                    recommended_action=_norm(ws.cell(r, cols["action"]).value) if cols["action"] else "",
                    owner=_norm(ws.cell(r, cols["owner"]).value) if cols["owner"] else "",
                    status=_norm(ws.cell(r, cols["status"]).value) if cols["status"] else "",
                    sheet="05_DFMEA_Worksheet",
                    row=r,
                ))

    # Count AP items
    p.total_failure_modes = len(p.dfmea_rows)
    for row in p.dfmea_rows:
        if "H" in row.action_priority.upper():
            p.high_ap_count += 1
        elif "M" in row.action_priority.upper():
            p.medium_ap_count += 1
        elif "L" in row.action_priority.upper():
            p.low_ap_count += 1

    # Special characteristics (06_Special_Characteristics)
    if "06_Special_Characteristics" in wb.sheetnames:
        ws = wb["06_Special_Characteristics"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["sc id", "id"]),
                "desc": _col_for(header_map, ["description", "characteristic"]),
                "sev": _col_for(header_map, ["severity", "s"]),
                "critical": _col_for(header_map, ["critical"]),
                "control": _col_for(header_map, ["control", "method"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                sc_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                desc = _norm(ws.cell(r, cols["desc"]).value) if cols["desc"] else ""
                if not (sc_id or desc):
                    continue
                p.special_characteristics.append(SpecialCharacteristic(
                    sc_id=sc_id,
                    description=desc,
                    severity=_int_or_zero(ws.cell(r, cols["sev"]).value) if cols["sev"] else 0,
                    critical_dimension=("yes" in _norm(ws.cell(r, cols["critical"]).value).lower()) if cols["critical"] else False,
                    control_method=_norm(ws.cell(r, cols["control"]).value) if cols["control"] else "",
                ))

    # Action plan tracker (08_Action_Plan_Tracker)
    if "08_Action_Plan_Tracker" in wb.sheetnames:
        ws = wb["08_Action_Plan_Tracker"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "action_id": _col_for(header_map, ["action id", "id"]),
                "fm_ref": _col_for(header_map, ["failure mode", "fm_ref"]),
                "desc": _col_for(header_map, ["action", "description"]),
                "owner": _col_for(header_map, ["owner", "responsible"]),
                "due": _col_for(header_map, ["due date", "due"]),
                "status": _col_for(header_map, ["status", "state"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                action_id = _norm(ws.cell(r, cols["action_id"]).value) if cols["action_id"] else ""
                desc = _norm(ws.cell(r, cols["desc"]).value) if cols["desc"] else ""
                if not (action_id or desc):
                    continue
                p.action_items.append(ActionItem(
                    action_id=action_id,
                    failure_mode_ref=_norm(ws.cell(r, cols["fm_ref"]).value) if cols["fm_ref"] else "",
                    action_description=desc,
                    owner=_norm(ws.cell(r, cols["owner"]).value) if cols["owner"] else "",
                    due_date=_norm(ws.cell(r, cols["due"]).value) if cols["due"] else "",
                    status=_norm(ws.cell(r, cols["status"]).value) if cols["status"] else "",
                ))

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "title": p.title,
        "part_number": p.part_number,
        "fmea_id": p.fmea_id,
        "project_name": p.project_name,
        "n_system_elements": len(p.system_elements),
        "n_subsystem_elements": len(p.subsystem_elements),
        "n_component_elements": len(p.component_elements),
        "n_functions": len(p.functions),
        "n_failure_modes": p.total_failure_modes,
        "high_ap_count": p.high_ap_count,
        "medium_ap_count": p.medium_ap_count,
        "low_ap_count": p.low_ap_count,
        "n_special_characteristics": len(p.special_characteristics),
        "n_action_items": len(p.action_items),
        "is_dfmea_builder_format": p.is_dfmea_builder_format,
    }
    print(json.dumps(summary, indent=2))
