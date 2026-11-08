"""
Item Definition content probe — best-effort extractor that works on item-definition-builder
outputs AND on other Item Definition xlsx formats by keyword heuristics.

Returns a structured ProbedItemDef dict that downstream check functions consume.
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
class Function:
    id: str = ""
    name: str = ""
    description: str = ""

@dataclass
class NonFunctionalRequirement:
    id: str = ""
    requirement: str = ""
    category: str = ""

@dataclass
class ExternalInterface:
    id: str = ""
    interface: str = ""
    counterpart: str = ""
    direction: str = ""
    data: str = ""
    integrity: str = ""

@dataclass
class OperatingMode:
    id: str = ""
    name: str = ""
    entry: str = ""
    exit: str = ""
    safety_relevant: str = ""

@dataclass
class Allocation:
    function_id: str = ""
    hw: str = ""
    sw: str = ""
    mech: str = ""

@dataclass
class ProbedItemDef:
    path: str = ""

    # Title metadata
    title: str = ""
    doc_id: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""

    # Item description
    scope: str = ""
    classification: str = ""
    distinguishing_notes: str = ""

    # Content lists
    functions: list[Function] = field(default_factory=list)
    non_functional_requirements: list[NonFunctionalRequirement] = field(default_factory=list)

    # Boundary
    boundary_in_items: list[str] = field(default_factory=list)
    boundary_out_items: list[str] = field(default_factory=list)
    adjacent_systems: list[str] = field(default_factory=list)

    # Interfaces
    external_interfaces: list[ExternalInterface] = field(default_factory=list)

    # Operating modes
    operating_modes: list[OperatingMode] = field(default_factory=list)

    # Allocation
    allocations: list[Allocation] = field(default_factory=list)

    # Assumptions and references
    assumptions: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)

    sheet_names: list[str] = field(default_factory=list)
    is_item_def_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Tab detection constants
# ---------------------------------------------------------------------------

ITEM_DEF_BUILDER_TABS = {
    "title": "00_Title_Page",
    "doc_control": "01_Document_Control",
    "description": "02_Item_Description",
    "functions": "03_Functions",
    "nfr": "04_Non_Functional_Requirements",
    "boundary": "05_Boundary_Diagram",
    "interfaces": "06_External_Interfaces",
    "modes": "07_Operating_Modes",
    "allocation": "08_Allocation_HW_SW_Mech",
    "assumptions": "09_Initial_Assumptions",
    "references": "10_References",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(s: str) -> str:
    """Clean and strip text."""
    if not s:
        return ""
    return str(s).strip()

def _extract_from_title_page(ws) -> dict:
    """Extract metadata from title page."""
    meta = {
        "title": "",
        "doc_id": "",
        "revision": "",
        "status": "",
        "author": "",
        "approver": "",
        "project": "",
    }
    if not ws:
        return meta

    # Scan for labeled fields (naive: look for cells ending with : or structured cells)
    for row in ws.iter_rows(min_row=1, max_row=50, min_col=1, max_col=5):
        for cell in row:
            if not cell.value:
                continue
            val = _clean(str(cell.value))
            val_lower = val.lower()

            # Title is typically the longest text early on
            if "item" in val_lower and "definition" in val_lower and "title" in val_lower:
                # Check adjacent cell
                if cell.column < cell.parent.max_column:
                    next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                    if next_cell.value:
                        meta["title"] = _clean(next_cell.value)
            elif "document id" in val_lower or "document number" in val_lower:
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    meta["doc_id"] = _clean(next_cell.value)
            elif "revision" in val_lower and "revision" not in meta.get("revision", ""):
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    meta["revision"] = _clean(next_cell.value)
            elif "status" in val_lower:
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    meta["status"] = _clean(next_cell.value)
            elif "author" in val_lower:
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    meta["author"] = _clean(next_cell.value)
            elif "approver" in val_lower:
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    meta["approver"] = _clean(next_cell.value)
            elif "project" in val_lower:
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    meta["project"] = _clean(next_cell.value)

    return meta

def _extract_description(ws) -> tuple[str, str, str]:
    """Extract scope, classification, distinguishing notes from description tab."""
    scope, classification, distinguishing = "", "", ""
    if not ws:
        return scope, classification, distinguishing

    for row in ws.iter_rows(min_row=1, max_row=50, min_col=1, max_col=5):
        for cell in row:
            if not cell.value:
                continue
            val_lower = _clean(str(cell.value)).lower()

            if "scope" in val_lower:
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    scope = _clean(next_cell.value)
            elif "classification" in val_lower:
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    classification = _clean(next_cell.value)
            elif "distinguish" in val_lower:
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    distinguishing = _clean(next_cell.value)

    return scope, classification, distinguishing

def _extract_functions(ws) -> list[Function]:
    """Extract functions from Functions tab."""
    functions = []
    if not ws:
        return functions

    # Scan for headers (ID, Name, Description columns)
    header_row = None
    for row_idx, row in enumerate(ws.iter_rows(min_row=1, max_row=10, min_col=1, max_col=5), start=1):
        if any(_clean(str(c.value)).lower() in ("id", "function_id", "func_id") for c in row if c.value):
            header_row = row_idx
            break

    if not header_row:
        header_row = 2

    for row in ws.iter_rows(min_row=header_row + 1, max_row=ws.max_row, min_col=1, max_col=5):
        func_id = _clean(str(row[0].value)) if row[0].value else ""
        func_name = _clean(str(row[1].value)) if len(row) > 1 and row[1].value else ""
        func_desc = _clean(str(row[2].value)) if len(row) > 2 and row[2].value else ""

        if func_id:
            functions.append(Function(id=func_id, name=func_name, description=func_desc))

    return functions

def _extract_nfr(ws) -> list[NonFunctionalRequirement]:
    """Extract non-functional requirements."""
    nfr_list = []
    if not ws:
        return nfr_list

    header_row = 2
    for row in ws.iter_rows(min_row=header_row, max_row=ws.max_row, min_col=1, max_col=5):
        nfr_id = _clean(str(row[0].value)) if row[0].value else ""
        nfr_req = _clean(str(row[1].value)) if len(row) > 1 and row[1].value else ""
        nfr_cat = _clean(str(row[2].value)) if len(row) > 2 and row[2].value else ""

        if nfr_id or nfr_req:
            nfr_list.append(NonFunctionalRequirement(id=nfr_id, requirement=nfr_req, category=nfr_cat))

    return nfr_list

def _extract_boundary(ws) -> tuple[list[str], list[str], list[str]]:
    """Extract boundary in/out items and adjacent systems."""
    in_items, out_items, adjacent = [], [], []
    if not ws:
        return in_items, out_items, adjacent

    for row in ws.iter_rows(min_row=1, max_row=100, min_col=1, max_col=5):
        for cell in row:
            if not cell.value:
                continue
            val = _clean(str(cell.value))
            val_lower = val.lower()

            if "in" in val_lower and ("item" in val_lower or "input" in val_lower):
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    in_items.append(_clean(next_cell.value))
            elif "out" in val_lower and ("item" in val_lower or "output" in val_lower):
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    out_items.append(_clean(next_cell.value))
            elif "adjacent" in val_lower or "neighbor" in val_lower:
                next_cell = cell.parent.cell(row=cell.row, column=cell.column + 1)
                if next_cell.value:
                    adjacent.append(_clean(next_cell.value))

    return in_items, out_items, adjacent

def _extract_interfaces(ws) -> list[ExternalInterface]:
    """Extract external interfaces."""
    interfaces = []
    if not ws:
        return interfaces

    header_row = 2
    for row in ws.iter_rows(min_row=header_row, max_row=ws.max_row, min_col=1, max_col=10):
        iface_id = _clean(str(row[0].value)) if row[0].value else ""
        iface_name = _clean(str(row[1].value)) if len(row) > 1 and row[1].value else ""
        counterpart = _clean(str(row[2].value)) if len(row) > 2 and row[2].value else ""
        direction = _clean(str(row[3].value)) if len(row) > 3 and row[3].value else ""
        data = _clean(str(row[4].value)) if len(row) > 4 and row[4].value else ""
        integrity = _clean(str(row[5].value)) if len(row) > 5 and row[5].value else ""

        if iface_id or iface_name:
            interfaces.append(ExternalInterface(
                id=iface_id, interface=iface_name, counterpart=counterpart,
                direction=direction, data=data, integrity=integrity
            ))

    return interfaces

def _extract_modes(ws) -> list[OperatingMode]:
    """Extract operating modes."""
    modes = []
    if not ws:
        return modes

    header_row = 2
    for row in ws.iter_rows(min_row=header_row, max_row=ws.max_row, min_col=1, max_col=10):
        mode_id = _clean(str(row[0].value)) if row[0].value else ""
        mode_name = _clean(str(row[1].value)) if len(row) > 1 and row[1].value else ""
        entry = _clean(str(row[2].value)) if len(row) > 2 and row[2].value else ""
        exit_cond = _clean(str(row[3].value)) if len(row) > 3 and row[3].value else ""
        safety_rel = _clean(str(row[4].value)) if len(row) > 4 and row[4].value else ""

        if mode_id or mode_name:
            modes.append(OperatingMode(
                id=mode_id, name=mode_name, entry=entry, exit=exit_cond,
                safety_relevant=safety_rel
            ))

    return modes

def _extract_allocations(ws) -> list[Allocation]:
    """Extract HW/SW/Mech allocations."""
    allocations = []
    if not ws:
        return allocations

    header_row = 2
    for row in ws.iter_rows(min_row=header_row, max_row=ws.max_row, min_col=1, max_col=10):
        func_id = _clean(str(row[0].value)) if row[0].value else ""
        hw = _clean(str(row[1].value)) if len(row) > 1 and row[1].value else ""
        sw = _clean(str(row[2].value)) if len(row) > 2 and row[2].value else ""
        mech = _clean(str(row[3].value)) if len(row) > 3 and row[3].value else ""

        if func_id:
            allocations.append(Allocation(function_id=func_id, hw=hw, sw=sw, mech=mech))

    return allocations

def _extract_assumptions(ws) -> list[str]:
    """Extract assumptions."""
    assumptions = []
    if not ws:
        return assumptions

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=3):
        if row[0].value:
            assumptions.append(_clean(str(row[0].value)))

    return assumptions

def _extract_references(ws) -> list[str]:
    """Extract references."""
    references = []
    if not ws:
        return references

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=3):
        if row[0].value:
            references.append(_clean(str(row[0].value)))

    return references


# ---------------------------------------------------------------------------
# Main probe function
# ---------------------------------------------------------------------------

def probe(path: str) -> ProbedItemDef:
    """Probe an Item Definition xlsx and extract all content."""
    p = ProbedItemDef(path=path)

    try:
        wb = load_workbook(path, data_only=True)
    except Exception as e:
        p.detection_notes.append(f"Failed to open workbook: {e}")
        return p

    p.sheet_names = wb.sheetnames

    # Detect format
    if ITEM_DEF_BUILDER_TABS["title"] in wb.sheetnames:
        p.is_item_def_builder_format = True
        p.detection_notes.append("Detected item-definition-builder format")
    else:
        p.detection_notes.append("No item-definition-builder format detected; using keyword heuristics")

    # Extract title metadata
    title_ws = wb[ITEM_DEF_BUILDER_TABS["title"]] if p.is_item_def_builder_format else (wb[wb.sheetnames[0]] if wb.sheetnames else None)
    if title_ws:
        meta = _extract_from_title_page(title_ws)
        p.title = meta["title"]
        p.doc_id = meta["doc_id"]
        p.revision = meta["revision"]
        p.status = meta["status"]
        p.author = meta["author"]
        p.approver = meta["approver"]
        p.project = meta["project"]

    # Extract description
    desc_ws = wb[ITEM_DEF_BUILDER_TABS["description"]] if p.is_item_def_builder_format and ITEM_DEF_BUILDER_TABS["description"] in wb.sheetnames else None
    if desc_ws:
        p.scope, p.classification, p.distinguishing_notes = _extract_description(desc_ws)

    # Extract functions
    func_ws = wb[ITEM_DEF_BUILDER_TABS["functions"]] if p.is_item_def_builder_format and ITEM_DEF_BUILDER_TABS["functions"] in wb.sheetnames else None
    if func_ws:
        p.functions = _extract_functions(func_ws)

    # Extract non-functional requirements
    nfr_ws = wb[ITEM_DEF_BUILDER_TABS["nfr"]] if p.is_item_def_builder_format and ITEM_DEF_BUILDER_TABS["nfr"] in wb.sheetnames else None
    if nfr_ws:
        p.non_functional_requirements = _extract_nfr(nfr_ws)

    # Extract boundary
    boundary_ws = wb[ITEM_DEF_BUILDER_TABS["boundary"]] if p.is_item_def_builder_format and ITEM_DEF_BUILDER_TABS["boundary"] in wb.sheetnames else None
    if boundary_ws:
        p.boundary_in_items, p.boundary_out_items, p.adjacent_systems = _extract_boundary(boundary_ws)

    # Extract interfaces
    iface_ws = wb[ITEM_DEF_BUILDER_TABS["interfaces"]] if p.is_item_def_builder_format and ITEM_DEF_BUILDER_TABS["interfaces"] in wb.sheetnames else None
    if iface_ws:
        p.external_interfaces = _extract_interfaces(iface_ws)

    # Extract operating modes
    modes_ws = wb[ITEM_DEF_BUILDER_TABS["modes"]] if p.is_item_def_builder_format and ITEM_DEF_BUILDER_TABS["modes"] in wb.sheetnames else None
    if modes_ws:
        p.operating_modes = _extract_modes(modes_ws)

    # Extract allocations
    alloc_ws = wb[ITEM_DEF_BUILDER_TABS["allocation"]] if p.is_item_def_builder_format and ITEM_DEF_BUILDER_TABS["allocation"] in wb.sheetnames else None
    if alloc_ws:
        p.allocations = _extract_allocations(alloc_ws)

    # Extract assumptions
    assump_ws = wb[ITEM_DEF_BUILDER_TABS["assumptions"]] if p.is_item_def_builder_format and ITEM_DEF_BUILDER_TABS["assumptions"] in wb.sheetnames else None
    if assump_ws:
        p.assumptions = _extract_assumptions(assump_ws)

    # Extract references
    ref_ws = wb[ITEM_DEF_BUILDER_TABS["references"]] if p.is_item_def_builder_format and ITEM_DEF_BUILDER_TABS["references"] in wb.sheetnames else None
    if ref_ws:
        p.references = _extract_references(ref_ws)

    wb.close()
    return p
