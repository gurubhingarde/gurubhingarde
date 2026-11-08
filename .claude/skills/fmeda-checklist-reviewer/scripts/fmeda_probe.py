"""
FMEDA content probe — extracts metadata, assumptions, HW element catalog,
failure modes, safety mechanisms, and metric calculations from fmeda-builder outputs.

Returns a structured ProbedFmeda dict for downstream check functions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class FmedaRow:
    hw_element_id: str = ""
    failure_mode: str = ""
    distribution_pct: float = 0.0
    lambda_total: float = 0.0
    classification: str = ""  # Safe/SPF/RF/MPF_D/MPF_L
    safety_mechanism: str = ""
    dc_pct: float = 0.0
    lambda_spf: float = 0.0
    lambda_rf: float = 0.0
    lambda_mpf_l: float = 0.0
    lambda_s: float = 0.0
    sheet: str = ""
    row: int = 0


@dataclass
class SafetyMechanism:
    mechanism_id: str = ""
    name: str = ""
    description: str = ""
    dc_pct: float = 0.0
    asil: str = ""


@dataclass
class HwElement:
    element_id: str = ""
    name: str = ""
    element_type: str = ""
    fit: float = 0.0
    safety_related: bool = False


@dataclass
class ProbedFmeda:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""

    sheet_names: list[str] = field(default_factory=list)

    # Assumptions
    mission_profile: str = ""
    fit_source: str = ""
    environmental_class: str = ""

    # Catalogs
    hw_elements: list[HwElement] = field(default_factory=list)
    safety_mechanisms: list[SafetyMechanism] = field(default_factory=list)

    # FMEDA worksheet rows
    fmeda_rows: list[FmedaRow] = field(default_factory=list)

    # Computed metrics (read from calculated cells, data_only=True)
    target_asil: str = ""
    spfm_computed: float = 0.0
    lfm_computed: float = 0.0
    pmhf_computed: float = 0.0  # in FIT
    total_fit: float = 0.0

    # Open items
    open_items: list[str] = field(default_factory=list)

    # Flags
    is_fmeda_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


def _norm(s: Any) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _float_or_zero(s: Any) -> float:
    try:
        val = float(_norm(s))
        return val if val >= 0 else 0.0
    except (ValueError, AttributeError):
        return 0.0


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


def probe(xlsx_path: str | Path) -> ProbedFmeda:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedFmeda(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect fmeda-builder format by tab signature
    expected_tabs = ["00_Title_Page", "06_FMEDA_Worksheet", "07_SPFM_Calculation",
                     "08_LFM_Calculation", "09_PMHF_Calculation"]
    p.is_fmeda_builder_format = all(tab in wb.sheetnames for tab in expected_tabs[:3])
    if p.is_fmeda_builder_format:
        p.detection_notes.append("Detected fmeda-builder format by tab names.")

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
                elif "title" == label or "document title" in label:
                    if not p.title:
                        p.title = value
                elif "asil" in label:
                    p.target_asil = value
        # Check for title in first big rows
        for r in range(1, min(ws.max_row + 1, 5)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value)
                if v and len(v) > 10 and not p.title:
                    p.title = v
                    break

    # Assumptions
    if "02_Assumptions" in wb.sheetnames:
        ws = wb["02_Assumptions"]
        for r in range(1, ws.max_row + 1):
            for c in range(1, ws.max_column + 1):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if "mission" in label:
                    p.mission_profile = value
                elif "fit source" in label or "failure rate source" in label:
                    p.fit_source = value
                elif "environmental" in label or "class" in label:
                    p.environmental_class = value

    # HW element catalog
    if "03_HW_Element_Catalog" in wb.sheetnames:
        ws = wb["03_HW_Element_Catalog"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["element id", "id"]),
                "name": _col_for(header_map, ["name", "description"]),
                "type": _col_for(header_map, ["type", "element type"]),
                "fit": _col_for(header_map, ["fit", "failure rate"]),
                "safety": _col_for(header_map, ["safety", "safety related"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                elem_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                if not elem_id:
                    continue
                p.hw_elements.append(HwElement(
                    element_id=elem_id,
                    name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    element_type=_norm(ws.cell(r, cols["type"]).value) if cols["type"] else "",
                    fit=_float_or_zero(ws.cell(r, cols["fit"]).value) if cols["fit"] else 0.0,
                    safety_related=("yes" in _norm(ws.cell(r, cols["safety"]).value).lower()) if cols["safety"] else False,
                ))

    # Safety mechanisms from TSC (or local mechanisms tab)
    for tab_name in ["05_Safety_Mechanisms_From_TSC", "Safety_Mechanisms"]:
        if tab_name in wb.sheetnames:
            ws = wb[tab_name]
            header_row, header_map = _find_header_row(ws)
            if header_row:
                cols = {
                    "id": _col_for(header_map, ["mechanism id", "id"]),
                    "name": _col_for(header_map, ["name"]),
                    "desc": _col_for(header_map, ["description"]),
                    "dc": _col_for(header_map, ["dc", "diagnostic coverage"]),
                    "asil": _col_for(header_map, ["asil"]),
                }
                for r in range(header_row + 1, ws.max_row + 1):
                    mech_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                    if not mech_id:
                        continue
                    p.safety_mechanisms.append(SafetyMechanism(
                        mechanism_id=mech_id,
                        name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                        description=_norm(ws.cell(r, cols["desc"]).value) if cols["desc"] else "",
                        dc_pct=_float_or_zero(ws.cell(r, cols["dc"]).value) if cols["dc"] else 0.0,
                        asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    ))
            break

    # FMEDA worksheet
    if "06_FMEDA_Worksheet" in wb.sheetnames:
        ws = wb["06_FMEDA_Worksheet"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "hw_e": _col_for(header_map, ["hw-e", "hw element", "element"]),
                "failure_mode": _col_for(header_map, ["failure mode"]),
                "dist": _col_for(header_map, ["distribution", "dist %"]),
                "lambda": _col_for(header_map, ["lambda", "failure rate"]),
                "class": _col_for(header_map, ["classification"]),
                "mech": _col_for(header_map, ["safety mechanism", "mechanism"]),
                "dc": _col_for(header_map, ["dc %", "diagnostic coverage"]),
                "lambda_spf": _col_for(header_map, ["lambda spf"]),
                "lambda_rf": _col_for(header_map, ["lambda rf"]),
                "lambda_mpf_l": _col_for(header_map, ["lambda mpf_l", "lambda l"]),
                "lambda_s": _col_for(header_map, ["lambda s", "lambda safe"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                hw_e = _norm(ws.cell(r, cols["hw_e"]).value) if cols["hw_e"] else ""
                fm = _norm(ws.cell(r, cols["failure_mode"]).value) if cols["failure_mode"] else ""
                if not (hw_e or fm):
                    continue
                p.fmeda_rows.append(FmedaRow(
                    hw_element_id=hw_e,
                    failure_mode=fm,
                    distribution_pct=_float_or_zero(ws.cell(r, cols["dist"]).value) if cols["dist"] else 0.0,
                    lambda_total=_float_or_zero(ws.cell(r, cols["lambda"]).value) if cols["lambda"] else 0.0,
                    classification=_norm(ws.cell(r, cols["class"]).value) if cols["class"] else "",
                    safety_mechanism=_norm(ws.cell(r, cols["mech"]).value) if cols["mech"] else "",
                    dc_pct=_float_or_zero(ws.cell(r, cols["dc"]).value) if cols["dc"] else 0.0,
                    lambda_spf=_float_or_zero(ws.cell(r, cols["lambda_spf"]).value) if cols["lambda_spf"] else 0.0,
                    lambda_rf=_float_or_zero(ws.cell(r, cols["lambda_rf"]).value) if cols["lambda_rf"] else 0.0,
                    lambda_mpf_l=_float_or_zero(ws.cell(r, cols["lambda_mpf_l"]).value) if cols["lambda_mpf_l"] else 0.0,
                    lambda_s=_float_or_zero(ws.cell(r, cols["lambda_s"]).value) if cols["lambda_s"] else 0.0,
                    sheet="06_FMEDA_Worksheet",
                    row=r,
                ))

    # Metric calculations (read from dashboard/calculation tabs)
    if "10_Metrics_Dashboard" in wb.sheetnames:
        ws = wb["10_Metrics_Dashboard"]
        for r in range(1, min(ws.max_row + 1, 50)):
            for c in range(1, min(ws.max_column + 1, 10)):
                label = _norm(ws.cell(r, c).value).lower()
                if "spfm" in label:
                    val = _float_or_zero(ws.cell(r, c + 1).value)
                    if val > 0 and val <= 1:
                        p.spfm_computed = val * 100
                    elif val > 1:
                        p.spfm_computed = val
                elif "lfm" in label:
                    val = _float_or_zero(ws.cell(r, c + 1).value)
                    if val > 0 and val <= 1:
                        p.lfm_computed = val * 100
                    elif val > 1:
                        p.lfm_computed = val
                elif "pmhf" in label:
                    p.pmhf_computed = _float_or_zero(ws.cell(r, c + 1).value)
                elif "total" in label and "fit" in label:
                    p.total_fit = _float_or_zero(ws.cell(r, c + 1).value)

    # Open items
    if "11_Open_Items" in wb.sheetnames:
        ws = wb["11_Open_Items"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            status_col = _col_for(header_map, ["status"])
            desc_col = _col_for(header_map, ["description", "item"])
            for r in range(header_row + 1, ws.max_row + 1):
                status = _norm(ws.cell(r, status_col).value) if status_col else ""
                desc = _norm(ws.cell(r, desc_col).value) if desc_col else ""
                if desc and status.lower() != "closed":
                    p.open_items.append(f"{status}: {desc}")

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "title": p.title,
        "target_asil": p.target_asil,
        "mission_profile": p.mission_profile,
        "fit_source": p.fit_source,
        "n_hw_elements": len(p.hw_elements),
        "n_fmeda_rows": len(p.fmeda_rows),
        "n_safety_mechanisms": len(p.safety_mechanisms),
        "spfm_computed": f"{p.spfm_computed:.1f}%",
        "lfm_computed": f"{p.lfm_computed:.1f}%",
        "pmhf_computed": f"{p.pmhf_computed:.1f} FIT",
        "total_fit": f"{p.total_fit:.1f} FIT",
        "n_open_items": len(p.open_items),
        "is_fmeda_builder_format": p.is_fmeda_builder_format,
    }
    print(json.dumps(summary, indent=2))
