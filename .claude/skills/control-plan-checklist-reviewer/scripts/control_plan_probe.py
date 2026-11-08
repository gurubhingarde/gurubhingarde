"""
Control Plan content probe — extracts title, header block, control plan worksheet,
special characteristics, MSA plan, reaction plans, SPC settings, poka-yoke catalog.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


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


@dataclass
class ControlPlanRow:
    process_step: str = ""
    characteristic: str = ""
    gage: str = ""
    sample_size: str = ""
    sample_frequency: str = ""
    control_method: str = ""
    reaction_plan_id: str = ""
    spec_lower: str = ""
    spec_upper: str = ""
    is_special: bool = False
    sheet: str = ""
    row: int = 0


@dataclass
class SpecialCharacteristic:
    characteristic: str = ""
    criticality: str = ""
    control_method: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class MSAPlan:
    gage_name: str = ""
    r_and_r_target: str = ""
    measurement_type: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class ReactionPlan:
    plan_id: str = ""
    description: str = ""
    action_items: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class SPCAllocation:
    characteristic: str = ""
    method: str = ""
    chart_type: str = ""
    ucl: str = ""
    lcl: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class PokaYokeCatalog:
    device_name: str = ""
    error_type: str = ""
    verification_method: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class ProbedControlPlan:
    path: str = ""
    title: str = ""
    control_plan_number: str = ""
    key_contact: str = ""
    core_team: str = ""
    customer_approval: str = ""
    supplier_approval: str = ""
    plan_type: str = ""  # Prototype / Pre-launch / Production
    sheet_names: list[str] = field(default_factory=list)

    cp_worksheet_rows: list[ControlPlanRow] = field(default_factory=list)
    special_characteristics: list[SpecialCharacteristic] = field(default_factory=list)
    msa_plans: list[MSAPlan] = field(default_factory=list)
    reaction_plans: list[ReactionPlan] = field(default_factory=list)
    spc_allocations: list[SPCAllocation] = field(default_factory=list)
    poka_yoke_catalog: list[PokaYokeCatalog] = field(default_factory=list)

    likely_title_sheet: str = ""
    likely_header_sheet: str = ""
    likely_cp_worksheet_sheet: str = ""
    likely_special_char_sheet: str = ""
    likely_msa_sheet: str = ""
    likely_reaction_sheet: str = ""
    likely_spc_sheet: str = ""
    likely_poka_yoke_sheet: str = ""

    is_control_plan_builder_format: bool = False


def probe(xlsx_path: str | Path) -> ProbedControlPlan:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedControlPlan(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect format by standard tab names
    p.is_control_plan_builder_format = any(
        s in wb.sheetnames for s in ["04_Control_Plan_Worksheet", "02_Header_Block"]
    )

    # Identify likely sheets
    p.likely_title_sheet = (
        "00_Title_Page"
        if "00_Title_Page" in wb.sheetnames
        else _find_sheet_by_keywords(p.sheet_names, ["title"])
    )
    p.likely_header_sheet = (
        "02_Header_Block"
        if "02_Header_Block" in wb.sheetnames
        else _find_sheet_by_keywords(p.sheet_names, ["header"])
    )
    p.likely_cp_worksheet_sheet = (
        "04_Control_Plan_Worksheet"
        if "04_Control_Plan_Worksheet" in wb.sheetnames
        else _find_sheet_by_keywords(p.sheet_names, ["control plan"])
    )
    p.likely_special_char_sheet = (
        "05_Special_Characteristics_Echo"
        if "05_Special_Characteristics_Echo" in wb.sheetnames
        else _find_sheet_by_keywords(p.sheet_names, ["special"])
    )
    p.likely_msa_sheet = (
        "06_Measurement_System_Plan"
        if "06_Measurement_System_Plan" in wb.sheetnames
        else _find_sheet_by_keywords(p.sheet_names, ["measurement", "msa"])
    )
    p.likely_reaction_sheet = (
        "07_Reaction_Plan_Library"
        if "07_Reaction_Plan_Library" in wb.sheetnames
        else _find_sheet_by_keywords(p.sheet_names, ["reaction"])
    )
    p.likely_spc_sheet = (
        "08_SPC_Method_Allocation"
        if "08_SPC_Method_Allocation" in wb.sheetnames
        else _find_sheet_by_keywords(p.sheet_names, ["spc"])
    )
    p.likely_poka_yoke_sheet = (
        "09_Mistake_Proofing_Catalog"
        if "09_Mistake_Proofing_Catalog" in wb.sheetnames
        else _find_sheet_by_keywords(p.sheet_names, ["mistake", "poka"])
    )

    # Extract title and header block metadata
    if p.likely_title_sheet and p.likely_title_sheet in wb.sheetnames:
        ws = wb[p.likely_title_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if "title" in label and not p.title:
                    p.title = value
                elif "control plan" in label and "number" in label:
                    p.control_plan_number = value
                elif "contact" in label:
                    p.key_contact = value

    # Extract header block
    if p.likely_header_sheet and p.likely_header_sheet in wb.sheetnames:
        ws = wb[p.likely_header_sheet]
        for r in range(1, min(ws.max_row + 1, 50)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if "team" in label:
                    p.core_team = value
                elif "customer" in label and "approval" in label:
                    p.customer_approval = value
                elif "supplier" in label and "approval" in label:
                    p.supplier_approval = value
                elif "type" in label and ("prototype" in value.lower() or "production" in value.lower() or "pre-launch" in value.lower()):
                    p.plan_type = value

    # Control Plan Worksheet rows
    if p.likely_cp_worksheet_sheet and p.likely_cp_worksheet_sheet in wb.sheetnames:
        ws = wb[p.likely_cp_worksheet_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "step": _col_for(header_map, ["process step", "step"]),
                "char": _col_for(header_map, ["characteristic"]),
                "gage": _col_for(header_map, ["gage", "measurement"]),
                "sample_size": _col_for(header_map, ["sample size"]),
                "sample_freq": _col_for(header_map, ["sample frequency", "frequency"]),
                "method": _col_for(header_map, ["control method", "method"]),
                "reaction": _col_for(header_map, ["reaction plan", "reaction"]),
                "spec_l": _col_for(header_map, ["spec lower", "lower"]),
                "spec_u": _col_for(header_map, ["spec upper", "upper"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                row = ControlPlanRow(
                    process_step=_norm(ws.cell(r, cols["step"]).value) if cols["step"] else "",
                    characteristic=_norm(ws.cell(r, cols["char"]).value) if cols["char"] else "",
                    gage=_norm(ws.cell(r, cols["gage"]).value) if cols["gage"] else "",
                    sample_size=_norm(ws.cell(r, cols["sample_size"]).value) if cols["sample_size"] else "",
                    sample_frequency=_norm(ws.cell(r, cols["sample_freq"]).value) if cols["sample_freq"] else "",
                    control_method=_norm(ws.cell(r, cols["method"]).value) if cols["method"] else "",
                    reaction_plan_id=_norm(ws.cell(r, cols["reaction"]).value) if cols["reaction"] else "",
                    spec_lower=_norm(ws.cell(r, cols["spec_l"]).value) if cols["spec_l"] else "",
                    spec_upper=_norm(ws.cell(r, cols["spec_u"]).value) if cols["spec_u"] else "",
                    sheet=p.likely_cp_worksheet_sheet,
                    row=r,
                )
                if row.characteristic or row.process_step:
                    p.cp_worksheet_rows.append(row)

    # Special Characteristics
    if p.likely_special_char_sheet and p.likely_special_char_sheet in wb.sheetnames:
        ws = wb[p.likely_special_char_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            char_col = _col_for(header_map, ["characteristic"])
            crit_col = _col_for(header_map, ["criticality", "critical"])
            method_col = _col_for(header_map, ["control method", "method"])
            for r in range(header_row + 1, ws.max_row + 1):
                sc = SpecialCharacteristic(
                    characteristic=_norm(ws.cell(r, char_col).value) if char_col else "",
                    criticality=_norm(ws.cell(r, crit_col).value) if crit_col else "",
                    control_method=_norm(ws.cell(r, method_col).value) if method_col else "",
                    sheet=p.likely_special_char_sheet,
                    row=r,
                )
                if sc.characteristic:
                    p.special_characteristics.append(sc)

    # MSA Plans
    if p.likely_msa_sheet and p.likely_msa_sheet in wb.sheetnames:
        ws = wb[p.likely_msa_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            gage_col = _col_for(header_map, ["gage", "measurement"])
            rr_col = _col_for(header_map, ["r&r", "r and r"])
            type_col = _col_for(header_map, ["type", "measurement type"])
            for r in range(header_row + 1, ws.max_row + 1):
                msa = MSAPlan(
                    gage_name=_norm(ws.cell(r, gage_col).value) if gage_col else "",
                    r_and_r_target=_norm(ws.cell(r, rr_col).value) if rr_col else "",
                    measurement_type=_norm(ws.cell(r, type_col).value) if type_col else "",
                    sheet=p.likely_msa_sheet,
                    row=r,
                )
                if msa.gage_name:
                    p.msa_plans.append(msa)

    # Reaction Plans
    if p.likely_reaction_sheet and p.likely_reaction_sheet in wb.sheetnames:
        ws = wb[p.likely_reaction_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            id_col = _col_for(header_map, ["plan id", "id"])
            desc_col = _col_for(header_map, ["description"])
            action_col = _col_for(header_map, ["action"])
            for r in range(header_row + 1, ws.max_row + 1):
                rp = ReactionPlan(
                    plan_id=_norm(ws.cell(r, id_col).value) if id_col else "",
                    description=_norm(ws.cell(r, desc_col).value) if desc_col else "",
                    action_items=_norm(ws.cell(r, action_col).value) if action_col else "",
                    sheet=p.likely_reaction_sheet,
                    row=r,
                )
                if rp.plan_id:
                    p.reaction_plans.append(rp)

    # SPC Method Allocation
    if p.likely_spc_sheet and p.likely_spc_sheet in wb.sheetnames:
        ws = wb[p.likely_spc_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            char_col = _col_for(header_map, ["characteristic"])
            method_col = _col_for(header_map, ["spc method", "method"])
            chart_col = _col_for(header_map, ["chart type", "chart"])
            ucl_col = _col_for(header_map, ["ucl"])
            lcl_col = _col_for(header_map, ["lcl"])
            for r in range(header_row + 1, ws.max_row + 1):
                spc = SPCAllocation(
                    characteristic=_norm(ws.cell(r, char_col).value) if char_col else "",
                    method=_norm(ws.cell(r, method_col).value) if method_col else "",
                    chart_type=_norm(ws.cell(r, chart_col).value) if chart_col else "",
                    ucl=_norm(ws.cell(r, ucl_col).value) if ucl_col else "",
                    lcl=_norm(ws.cell(r, lcl_col).value) if lcl_col else "",
                    sheet=p.likely_spc_sheet,
                    row=r,
                )
                if spc.characteristic:
                    p.spc_allocations.append(spc)

    # Poka-Yoke Catalog
    if p.likely_poka_yoke_sheet and p.likely_poka_yoke_sheet in wb.sheetnames:
        ws = wb[p.likely_poka_yoke_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            name_col = _col_for(header_map, ["device", "name"])
            error_col = _col_for(header_map, ["error type", "error"])
            verify_col = _col_for(header_map, ["verification"])
            for r in range(header_row + 1, ws.max_row + 1):
                py = PokaYokeCatalog(
                    device_name=_norm(ws.cell(r, name_col).value) if name_col else "",
                    error_type=_norm(ws.cell(r, error_col).value) if error_col else "",
                    verification_method=_norm(ws.cell(r, verify_col).value) if verify_col else "",
                    sheet=p.likely_poka_yoke_sheet,
                    row=r,
                )
                if py.device_name:
                    p.poka_yoke_catalog.append(py)

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "title": p.title,
        "control_plan_number": p.control_plan_number,
        "plan_type": p.plan_type,
        "n_cp_rows": len(p.cp_worksheet_rows),
        "n_special_chars": len(p.special_characteristics),
        "n_msa_plans": len(p.msa_plans),
        "n_reaction_plans": len(p.reaction_plans),
        "n_spc_allocations": len(p.spc_allocations),
        "n_poka_yoke": len(p.poka_yoke_catalog),
    }
    print(json.dumps(summary, indent=2))
