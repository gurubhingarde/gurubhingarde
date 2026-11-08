"""
SW FMEA content probe — extracts metadata, assumptions, SW components,
failure mode library, FMEA worksheet rows, detection mechanisms, propagation paths,
coverage summary, and open items from sw-fmea-builder outputs.

Per ISO 26262-9 Section 8 (SW FMEA methodology).
Returns a structured ProbedSwFmea dict for downstream check functions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class FmeaRow:
    """A single row from the FMEA Worksheet (05_FMEA_Worksheet)."""
    swc_id: str = ""
    failure_mode: str = ""
    severity: str = ""  # S0, S1, S2, S3
    frequency: str = ""  # Rare, Occasional, Frequent
    pre_risk: int = 0
    detection_mechanism: str = ""
    detection_coverage: str = ""  # Low, Med, High
    post_risk: int = 0
    residual_acceptable: str = ""  # Yes/No/—
    notes: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class SwComponent:
    swc_id: str = ""
    name: str = ""
    asil: str = ""  # ASIL D, C, B, A, QM
    safety_critical: bool = False


@dataclass
class FailureMode:
    fm_id: str = ""
    description: str = ""
    category: str = ""  # Memory corruption, Timing, Data flow, etc.


@dataclass
class DetectionMechanism:
    mechanism_id: str = ""
    name: str = ""
    description: str = ""
    coverage_pct: float = 0.0


@dataclass
class ProbedSwFmea:
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
    scope: str = ""
    methodology: str = ""
    fm_library_source: str = ""

    # Catalogs
    sw_components: list[SwComponent] = field(default_factory=list)
    failure_modes_library: list[FailureMode] = field(default_factory=list)
    detection_mechanisms: list[DetectionMechanism] = field(default_factory=list)

    # FMEA worksheet rows
    fmea_rows: list[FmeaRow] = field(default_factory=list)

    # Coverage and propagation
    propagation_paths: list[str] = field(default_factory=list)
    coverage_summary: list[str] = field(default_factory=list)

    # Open items
    open_items: list[str] = field(default_factory=list)

    # Verification hooks
    verification_hooks: list[str] = field(default_factory=list)

    # Flags
    is_sw_fmea_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


def _norm(s: Any) -> str:
    """Normalize to string, handle None."""
    if s is None:
        return ""
    return str(s).strip()


def _float_or_zero(s: Any) -> float:
    try:
        val = float(_norm(s))
        return val if val >= 0 else 0.0
    except (ValueError, AttributeError):
        return 0.0


def _int_or_zero(s: Any) -> int:
    try:
        return int(float(_norm(s)))
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


def probe(xlsx_path: str | Path) -> ProbedSwFmea:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedSwFmea(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect sw-fmea-builder format by tab signature
    expected_tabs = ["00_Title_Page", "05_FMEA_Worksheet", "03_SW_Component_Catalog"]
    p.is_sw_fmea_builder_format = all(tab in wb.sheetnames for tab in expected_tabs)
    if p.is_sw_fmea_builder_format:
        p.detection_notes.append("Detected sw-fmea-builder format by tab names.")

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
        # Fallback: check for title in first big rows
        for r in range(1, min(ws.max_row + 1, 5)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value)
                if v and len(v) > 10 and not p.title:
                    p.title = v
                    break

    # Assumptions (02_Assumptions)
    if "02_Assumptions" in wb.sheetnames:
        ws = wb["02_Assumptions"]
        for r in range(1, ws.max_row + 1):
            for c in range(1, ws.max_column + 1):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if "scope" in label:
                    p.scope = value
                elif "methodology" in label:
                    p.methodology = value
                elif "failure mode library" in label or "fm library" in label:
                    p.fm_library_source = value

    # SW Component Catalog (03_SW_Component_Catalog)
    if "03_SW_Component_Catalog" in wb.sheetnames:
        ws = wb["03_SW_Component_Catalog"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["swc id", "component id", "id"]),
                "name": _col_for(header_map, ["name", "description"]),
                "asil": _col_for(header_map, ["asil"]),
                "safety": _col_for(header_map, ["safety", "safety critical"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                swc_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                if not swc_id:
                    continue
                p.sw_components.append(SwComponent(
                    swc_id=swc_id,
                    name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    safety_critical=("yes" in _norm(ws.cell(r, cols["safety"]).value).lower()) if cols["safety"] else False,
                ))

    # Failure Mode Library (04_SW_Failure_Mode_Library)
    if "04_SW_Failure_Mode_Library" in wb.sheetnames:
        ws = wb["04_SW_Failure_Mode_Library"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["fm id", "mode id", "id"]),
                "desc": _col_for(header_map, ["description", "failure mode"]),
                "category": _col_for(header_map, ["category", "type"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                fm_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                if not fm_id:
                    continue
                p.failure_modes_library.append(FailureMode(
                    fm_id=fm_id,
                    description=_norm(ws.cell(r, cols["desc"]).value) if cols["desc"] else "",
                    category=_norm(ws.cell(r, cols["category"]).value) if cols["category"] else "",
                ))

    # FMEA Worksheet (05_FMEA_Worksheet)
    if "05_FMEA_Worksheet" in wb.sheetnames:
        ws = wb["05_FMEA_Worksheet"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "swc": _col_for(header_map, ["swc id", "component", "swc"]),
                "fm": _col_for(header_map, ["failure mode", "mode"]),
                "severity": _col_for(header_map, ["severity", "s"]),
                "frequency": _col_for(header_map, ["frequency", "freq"]),
                "pre_risk": _col_for(header_map, ["pre risk", "pre-risk"]),
                "detection": _col_for(header_map, ["detection mechanism", "mechanism", "detection"]),
                "coverage": _col_for(header_map, ["coverage", "detection coverage", "dc"]),
                "post_risk": _col_for(header_map, ["post risk", "post-risk"]),
                "residual": _col_for(header_map, ["residual acceptable", "residual", "acceptable"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                swc = _norm(ws.cell(r, cols["swc"]).value) if cols["swc"] else ""
                fm = _norm(ws.cell(r, cols["fm"]).value) if cols["fm"] else ""
                if not (swc or fm):
                    continue
                p.fmea_rows.append(FmeaRow(
                    swc_id=swc,
                    failure_mode=fm,
                    severity=_norm(ws.cell(r, cols["severity"]).value) if cols["severity"] else "",
                    frequency=_norm(ws.cell(r, cols["frequency"]).value) if cols["frequency"] else "",
                    pre_risk=_int_or_zero(ws.cell(r, cols["pre_risk"]).value) if cols["pre_risk"] else 0,
                    detection_mechanism=_norm(ws.cell(r, cols["detection"]).value) if cols["detection"] else "",
                    detection_coverage=_norm(ws.cell(r, cols["coverage"]).value) if cols["coverage"] else "",
                    post_risk=_int_or_zero(ws.cell(r, cols["post_risk"]).value) if cols["post_risk"] else 0,
                    residual_acceptable=_norm(ws.cell(r, cols["residual"]).value) if cols["residual"] else "",
                    sheet="05_FMEA_Worksheet",
                    row=r,
                ))

    # Detection Mechanisms Summary (06_Detection_Mechanisms_Summary)
    if "06_Detection_Mechanisms_Summary" in wb.sheetnames:
        ws = wb["06_Detection_Mechanisms_Summary"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["mechanism id", "id"]),
                "name": _col_for(header_map, ["name"]),
                "desc": _col_for(header_map, ["description"]),
                "coverage": _col_for(header_map, ["coverage", "coverage %", "coverage_pct"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                mech_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                if not mech_id:
                    continue
                p.detection_mechanisms.append(DetectionMechanism(
                    mechanism_id=mech_id,
                    name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    description=_norm(ws.cell(r, cols["desc"]).value) if cols["desc"] else "",
                    coverage_pct=_float_or_zero(ws.cell(r, cols["coverage"]).value) if cols["coverage"] else 0.0,
                ))

    # Propagation Paths (07_Propagation_Paths)
    if "07_Propagation_Paths" in wb.sheetnames:
        ws = wb["07_Propagation_Paths"]
        for r in range(1, ws.max_row + 1):
            for c in range(1, ws.max_column + 1):
                val = _norm(ws.cell(r, c).value)
                if val and len(val) > 10:
                    p.propagation_paths.append(val)

    # Coverage Summary (08_Coverage_Summary)
    if "08_Coverage_Summary" in wb.sheetnames:
        ws = wb["08_Coverage_Summary"]
        for r in range(1, ws.max_row + 1):
            for c in range(1, ws.max_column + 1):
                val = _norm(ws.cell(r, c).value)
                if val and len(val) > 5:
                    p.coverage_summary.append(val)

    # Open Items (09_Open_Items)
    if "09_Open_Items" in wb.sheetnames:
        ws = wb["09_Open_Items"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            status_col = _col_for(header_map, ["status"])
            desc_col = _col_for(header_map, ["description", "item"])
            for r in range(header_row + 1, ws.max_row + 1):
                status = _norm(ws.cell(r, status_col).value) if status_col else ""
                desc = _norm(ws.cell(r, desc_col).value) if desc_col else ""
                if desc and status.lower() != "closed":
                    p.open_items.append(f"{status}: {desc}")

    # Verification Plan Hooks (10_Verification_Plan_Hooks)
    if "10_Verification_Plan_Hooks" in wb.sheetnames:
        ws = wb["10_Verification_Plan_Hooks"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            hook_col = _col_for(header_map, ["hook", "description", "test"])
            for r in range(header_row + 1, ws.max_row + 1):
                hook = _norm(ws.cell(r, hook_col).value) if hook_col else ""
                if hook:
                    p.verification_hooks.append(hook)

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "title": p.title,
        "author": p.author,
        "revision": p.revision,
        "n_sw_components": len(p.sw_components),
        "n_failure_modes": len(p.failure_modes_library),
        "n_fmea_rows": len(p.fmea_rows),
        "n_detection_mechanisms": len(p.detection_mechanisms),
        "n_propagation_paths": len(p.propagation_paths),
        "n_open_items": len(p.open_items),
        "n_verification_hooks": len(p.verification_hooks),
        "is_sw_fmea_builder_format": p.is_sw_fmea_builder_format,
    }
    print(json.dumps(summary, indent=2))
