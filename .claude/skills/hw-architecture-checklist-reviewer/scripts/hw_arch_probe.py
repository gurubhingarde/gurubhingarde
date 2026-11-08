"""
Hardware Architecture content probe — extracts HW arch xlsx content produced by hw-architecture-builder.

Returns a structured ProbedHwArch dict that downstream check functions consume.
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


def _find_header_row(ws, max_search: int = 30) -> tuple[int, dict[str, int]]:
    """Find header row and return (row_index, header_to_col_map)."""
    # #63: prefer a >=3-cell header; accept a 2-cell header only if no wider row exists,
    # so a two-column tab is located without letting a 2-cell key/value row pre-empt a real header.
    fallback: tuple[int, dict[str, int]] = (0, {})
    for r in range(1, min(ws.max_row, max_search) + 1):
        cells = [(c, _norm(ws.cell(r, c).value)) for c in range(1, ws.max_column + 1)]
        non_empty = [(c, v) for c, v in cells if v]
        if len(non_empty) >= 2:
            if all(len(v) < 80 and not v.startswith("=") for c, v in non_empty):
                header_map = {v.lower(): c for c, v in non_empty}
                if len(non_empty) >= 3:
                    return r, header_map
                if not fallback[0]:
                    fallback = (r, header_map)
    return fallback


def _col_for(header_map: dict[str, int], candidates: list[str]) -> int:
    """Find first matching column."""
    for cand in candidates:
        cand_lower = cand.lower()
        for header, col in header_map.items():
            if cand_lower in header:
                return col
    return 0


@dataclass
class HwElement:
    hw_element_id: str = ""
    name: str = ""
    element_type: str = ""  # Processor, Memory, Interface, Discrete, Connector, etc.
    supplier: str = ""
    part_number: str = ""
    package: str = ""
    baseline_fit: str = ""  # FIT rate
    qualification: str = ""  # AEC-Q100/Q101/Q200, etc.
    tsc_node_id: str = ""  # Traceability to TSC
    pcb_id: str = ""
    power_rail: str = ""
    clock_source: str = ""


@dataclass
class SafetyMechanismAlloc:
    hw_element_id: str = ""
    tsc_mechanism_id: str = ""
    mechanism_description: str = ""
    allocated_asil: str = ""


@dataclass
class PowerRail:
    rail_name: str = ""
    voltage: str = ""
    regulator: str = ""
    monitor: str = ""
    fusing: str = ""


@dataclass
class ClockSource:
    clock_id: str = ""
    clock_type: str = ""  # XTAL, RC, PLL
    frequency: str = ""
    monitor: str = ""
    redundancy: str = ""


@dataclass
class CommonCauseRow:
    redundant_pair: str = ""
    shared_rail: str = ""
    shared_package: str = ""
    pcb_region: str = ""
    environmental_zone: str = ""
    mitigation_status: str = ""  # No / Yes-Mitigated / Yes-Unmitigated


@dataclass
class ProbedHwArch:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""

    sheet_names: list[str] = field(default_factory=list)

    hw_elements: list[HwElement] = field(default_factory=list)
    safety_mechanism_allocs: list[SafetyMechanismAlloc] = field(default_factory=list)
    power_rails: list[PowerRail] = field(default_factory=list)
    clock_sources: list[ClockSource] = field(default_factory=list)
    common_cause_rows: list[CommonCauseRow] = field(default_factory=list)

    pcb_design_rows: int = 0
    hw_sr_allocation_rows: int = 0
    bom_total_fit: str = ""

    detection_notes: list[str] = field(default_factory=list)


def probe(xlsx_path: str | Path) -> ProbedHwArch:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedHwArch(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Title / metadata from Title Page
    title_sheet = "00_Title_Page"
    if title_sheet in wb.sheetnames:
        ws = wb[title_sheet]
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
        # Check for big header text
        for r in range(1, min(ws.max_row + 1, 5)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value)
                if v and len(v) > 10 and not p.title:
                    p.title = v
                    break

    # HW Element Catalog
    catalog_sheet = "04_HW_Element_Catalog"
    if catalog_sheet in wb.sheetnames:
        ws = wb[catalog_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["hw element id", "element id", "id"]),
                "name": _col_for(header_map, ["name", "element name"]),
                "type": _col_for(header_map, ["element type", "type"]),
                "supplier": _col_for(header_map, ["supplier"]),
                "part": _col_for(header_map, ["part number", "part"]),
                "package": _col_for(header_map, ["package"]),
                "fit": _col_for(header_map, ["baseline fit", "fit"]),
                "qual": _col_for(header_map, ["qualification"]),
                "tsc": _col_for(header_map, ["tsc node", "tsc_node_id"]),
                "pcb": _col_for(header_map, ["pcb", "pcb_id"]),
                "power": _col_for(header_map, ["power rail", "power"]),
                "clock": _col_for(header_map, ["clock source", "clock"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                elem_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                if not elem_id:
                    continue
                hw_elem = HwElement(
                    hw_element_id=elem_id,
                    name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    element_type=_norm(ws.cell(r, cols["type"]).value) if cols["type"] else "",
                    supplier=_norm(ws.cell(r, cols["supplier"]).value) if cols["supplier"] else "",
                    part_number=_norm(ws.cell(r, cols["part"]).value) if cols["part"] else "",
                    package=_norm(ws.cell(r, cols["package"]).value) if cols["package"] else "",
                    baseline_fit=_norm(ws.cell(r, cols["fit"]).value) if cols["fit"] else "",
                    qualification=_norm(ws.cell(r, cols["qual"]).value) if cols["qual"] else "",
                    tsc_node_id=_norm(ws.cell(r, cols["tsc"]).value) if cols["tsc"] else "",
                    pcb_id=_norm(ws.cell(r, cols["pcb"]).value) if cols["pcb"] else "",
                    power_rail=_norm(ws.cell(r, cols["power"]).value) if cols["power"] else "",
                    clock_source=_norm(ws.cell(r, cols["clock"]).value) if cols["clock"] else "",
                )
                p.hw_elements.append(hw_elem)
        p.detection_notes.append(f"HW Element Catalog: {len(p.hw_elements)} elements found")

    # Safety Mechanism Allocation
    safety_mech_sheet = "05_Safety_Mechanism_Allocation"
    if safety_mech_sheet in wb.sheetnames:
        ws = wb[safety_mech_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "hw_elem": _col_for(header_map, ["hw element", "element"]),
                "tsc_mech": _col_for(header_map, ["tsc mechanism", "mechanism"]),
                "desc": _col_for(header_map, ["description"]),
                "asil": _col_for(header_map, ["asil"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                hw_id = _norm(ws.cell(r, cols["hw_elem"]).value) if cols["hw_elem"] else ""
                if not hw_id:
                    continue
                alloc = SafetyMechanismAlloc(
                    hw_element_id=hw_id,
                    tsc_mechanism_id=_norm(ws.cell(r, cols["tsc_mech"]).value) if cols["tsc_mech"] else "",
                    mechanism_description=_norm(ws.cell(r, cols["desc"]).value) if cols["desc"] else "",
                    allocated_asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                )
                p.safety_mechanism_allocs.append(alloc)
        p.detection_notes.append(f"Safety Mechanism Allocation: {len(p.safety_mechanism_allocs)} rows found")

    # Power Architecture
    power_sheet = "07_Power_Architecture"
    if power_sheet in wb.sheetnames:
        ws = wb[power_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "rail": _col_for(header_map, ["rail", "rail name"]),
                "volt": _col_for(header_map, ["voltage"]),
                "reg": _col_for(header_map, ["regulator"]),
                "mon": _col_for(header_map, ["monitor"]),
                "fuse": _col_for(header_map, ["fusing", "fuse"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                rail = _norm(ws.cell(r, cols["rail"]).value) if cols["rail"] else ""
                if not rail:
                    continue
                power = PowerRail(
                    rail_name=rail,
                    voltage=_norm(ws.cell(r, cols["volt"]).value) if cols["volt"] else "",
                    regulator=_norm(ws.cell(r, cols["reg"]).value) if cols["reg"] else "",
                    monitor=_norm(ws.cell(r, cols["mon"]).value) if cols["mon"] else "",
                    fusing=_norm(ws.cell(r, cols["fuse"]).value) if cols["fuse"] else "",
                )
                p.power_rails.append(power)
        p.detection_notes.append(f"Power Architecture: {len(p.power_rails)} rails found")

    # Clock Architecture
    clock_sheet = "08_Clock_Architecture"
    if clock_sheet in wb.sheetnames:
        ws = wb[clock_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["clock id", "id"]),
                "type": _col_for(header_map, ["type"]),
                "freq": _col_for(header_map, ["frequency"]),
                "mon": _col_for(header_map, ["monitor"]),
                "red": _col_for(header_map, ["redundancy"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                clk_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                if not clk_id:
                    continue
                clk = ClockSource(
                    clock_id=clk_id,
                    clock_type=_norm(ws.cell(r, cols["type"]).value) if cols["type"] else "",
                    frequency=_norm(ws.cell(r, cols["freq"]).value) if cols["freq"] else "",
                    monitor=_norm(ws.cell(r, cols["mon"]).value) if cols["mon"] else "",
                    redundancy=_norm(ws.cell(r, cols["red"]).value) if cols["red"] else "",
                )
                p.clock_sources.append(clk)
        p.detection_notes.append(f"Clock Architecture: {len(p.clock_sources)} sources found")

    # Common Cause Analysis
    ccfa_sheet = "09_Common_Cause_Analysis"
    if ccfa_sheet in wb.sheetnames:
        ws = wb[ccfa_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "pair": _col_for(header_map, ["redundant pair", "pair"]),
                "rail": _col_for(header_map, ["shared rail"]),
                "pkg": _col_for(header_map, ["shared package"]),
                "region": _col_for(header_map, ["pcb region", "region"]),
                "zone": _col_for(header_map, ["environmental zone", "zone"]),
                "status": _col_for(header_map, ["mitigation", "status"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                pair = _norm(ws.cell(r, cols["pair"]).value) if cols["pair"] else ""
                if not pair:
                    continue
                cc = CommonCauseRow(
                    redundant_pair=pair,
                    shared_rail=_norm(ws.cell(r, cols["rail"]).value) if cols["rail"] else "",
                    shared_package=_norm(ws.cell(r, cols["pkg"]).value) if cols["pkg"] else "",
                    pcb_region=_norm(ws.cell(r, cols["region"]).value) if cols["region"] else "",
                    environmental_zone=_norm(ws.cell(r, cols["zone"]).value) if cols["zone"] else "",
                    mitigation_status=_norm(ws.cell(r, cols["status"]).value) if cols["status"] else "",
                )
                p.common_cause_rows.append(cc)
        p.detection_notes.append(f"Common Cause Analysis: {len(p.common_cause_rows)} pairs analyzed")

    # PCB Design
    pcb_sheet = "03_PCB_Design"
    if pcb_sheet in wb.sheetnames:
        ws = wb[pcb_sheet]
        header_row, header_map = _find_header_row(ws)
        p.pcb_design_rows = max(0, ws.max_row - (header_row or 1))

    # HW-SR Allocation Matrix
    hwsr_sheet = "06_HW_SR_Allocation_Matrix"
    if hwsr_sheet in wb.sheetnames:
        ws = wb[hwsr_sheet]
        header_row, header_map = _find_header_row(ws)
        p.hw_sr_allocation_rows = max(0, ws.max_row - (header_row or 1))

    # BOM Summary
    bom_sheet = "10_Bill_of_Materials"
    if bom_sheet in wb.sheetnames:
        ws = wb[bom_sheet]
        for r in range(1, min(ws.max_row + 1, 20)):
            cell_val = _norm(ws.cell(r, 1).value)
            if "total" in cell_val.lower() and "fit" in cell_val.lower():
                p.bom_total_fit = _norm(ws.cell(r, 2).value)
                break

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "title": p.title,
        "doc_id": p.doc_id,
        "revision": p.revision,
        "status": p.status,
        "author": p.author,
        "approver": p.approver,
        "project": p.project,
        "sheets": p.sheet_names,
        "n_hw_elements": len(p.hw_elements),
        "n_safety_mechanisms": len(p.safety_mechanism_allocs),
        "n_power_rails": len(p.power_rails),
        "n_clock_sources": len(p.clock_sources),
        "n_common_cause_pairs": len(p.common_cause_rows),
        "pcb_design_rows": p.pcb_design_rows,
        "hw_sr_allocation_rows": p.hw_sr_allocation_rows,
        "bom_total_fit": p.bom_total_fit,
        "detection_notes": p.detection_notes,
    }
    print(json.dumps(summary, indent=2))
