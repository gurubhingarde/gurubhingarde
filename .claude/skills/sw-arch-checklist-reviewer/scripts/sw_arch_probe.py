"""
Software Architecture content probe — extracts SW arch xlsx content produced by sw-arch-builder.

Returns a structured ProbedSwArch dict that downstream check functions consume.
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
class SwComponent:
    swc_id: str = ""
    name: str = ""
    component_type: str = ""  # Module, Driver, Library, Task, etc.
    asil: str = ""  # QM / ASIL A/B/C/D
    partition_id: str = ""
    sw_tsr_ref: str = ""  # References from SW-TSR
    description: str = ""


@dataclass
class RtosConfig:
    rtos_name: str = ""
    rtos_version: str = ""
    scheduling_policy: str = ""  # Rate-monotonic, Priority-based, etc.
    asil_support: str = ""
    notes: str = ""


@dataclass
class TaskScheduling:
    task_id: str = ""
    task_name: str = ""
    priority: str = ""
    period_ms: str = ""
    wcet_ms: str = ""
    asil: str = ""
    partition: str = ""


@dataclass
class MpuRegion:
    region_id: str = ""
    partition_id: str = ""
    base_address: str = ""
    size: str = ""
    access_permissions: str = ""
    asil: str = ""


@dataclass
class InterComponentInterface:
    interface_id: str = ""
    source_swc: str = ""
    dest_swc: str = ""
    interface_type: str = ""  # Signal, Message, Shared Memory, etc.
    integrity_protection: str = ""  # Checksum, CRC, None, etc.
    asil: str = ""


@dataclass
class SafetyMechanismAlloc:
    swc_id: str = ""
    mechanism_id: str = ""
    mechanism_description: str = ""
    allocated_asil: str = ""


@dataclass
class MisraTarget:
    swc_id: str = ""
    rule_category: str = ""
    compliance_level: str = ""
    justification: str = ""


@dataclass
class ProbedSwArch:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""

    sheet_names: list[str] = field(default_factory=list)

    sw_components: list[SwComponent] = field(default_factory=list)
    rtos_config: RtosConfig = field(default_factory=RtosConfig)
    task_scheduling: list[TaskScheduling] = field(default_factory=list)
    mpu_regions: list[MpuRegion] = field(default_factory=list)
    interfaces: list[InterComponentInterface] = field(default_factory=list)
    safety_mechanism_allocs: list[SafetyMechanismAlloc] = field(default_factory=list)
    misra_targets: list[MisraTarget] = field(default_factory=list)

    init_sequence_rows: int = 0
    tsc_reference_tabs: list[str] = field(default_factory=list)

    detection_notes: list[str] = field(default_factory=list)


def probe(xlsx_path: str | Path) -> ProbedSwArch:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedSwArch(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

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

    # SW Component Catalog
    catalog_sheet = "03_SW_Component_Catalog"
    if catalog_sheet in wb.sheetnames:
        ws = wb[catalog_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["swc id", "component id", "id"]),
                "name": _col_for(header_map, ["name", "component name"]),
                "type": _col_for(header_map, ["component type", "type"]),
                "asil": _col_for(header_map, ["asil"]),
                "partition": _col_for(header_map, ["partition", "partition id"]),
                "sw_tsr": _col_for(header_map, ["sw tsr", "tsr ref"]),
                "description": _col_for(header_map, ["description"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                swc_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                if not swc_id:
                    continue
                swc = SwComponent(
                    swc_id=swc_id,
                    name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    component_type=_norm(ws.cell(r, cols["type"]).value) if cols["type"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    partition_id=_norm(ws.cell(r, cols["partition"]).value) if cols["partition"] else "",
                    sw_tsr_ref=_norm(ws.cell(r, cols["sw_tsr"]).value) if cols["sw_tsr"] else "",
                    description=_norm(ws.cell(r, cols["description"]).value) if cols["description"] else "",
                )
                p.sw_components.append(swc)
        p.detection_notes.append(f"SW Component Catalog: {len(p.sw_components)} components found")

    # RTOS / OS Configuration
    rtos_sheet = "04_RTOS_OS_Configuration"
    if rtos_sheet in wb.sheetnames:
        ws = wb[rtos_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "name": _col_for(header_map, ["rtos name", "os name", "name"]),
                "version": _col_for(header_map, ["version"]),
                "policy": _col_for(header_map, ["scheduling", "scheduling policy"]),
                "asil": _col_for(header_map, ["asil support"]),
                "notes": _col_for(header_map, ["notes", "description"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                rtos_name = _norm(ws.cell(r, cols["name"]).value) if cols["name"] else ""
                if not rtos_name:
                    continue
                p.rtos_config = RtosConfig(
                    rtos_name=rtos_name,
                    rtos_version=_norm(ws.cell(r, cols["version"]).value) if cols["version"] else "",
                    scheduling_policy=_norm(ws.cell(r, cols["policy"]).value) if cols["policy"] else "",
                    asil_support=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    notes=_norm(ws.cell(r, cols["notes"]).value) if cols["notes"] else "",
                )
                break
        p.detection_notes.append(f"RTOS Config: {p.rtos_config.rtos_name}" if p.rtos_config.rtos_name else "RTOS Config: not found")

    # Task Scheduling Map
    task_sheet = "05_Task_Scheduling_Map"
    if task_sheet in wb.sheetnames:
        ws = wb[task_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "task_id": _col_for(header_map, ["task id", "id"]),
                "name": _col_for(header_map, ["task name", "name"]),
                "priority": _col_for(header_map, ["priority"]),
                "period": _col_for(header_map, ["period", "period ms"]),
                "wcet": _col_for(header_map, ["wcet", "wcet ms"]),
                "asil": _col_for(header_map, ["asil"]),
                "partition": _col_for(header_map, ["partition", "partition id"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                task_id = _norm(ws.cell(r, cols["task_id"]).value) if cols["task_id"] else ""
                if not task_id:
                    continue
                task = TaskScheduling(
                    task_id=task_id,
                    task_name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    priority=_norm(ws.cell(r, cols["priority"]).value) if cols["priority"] else "",
                    period_ms=_norm(ws.cell(r, cols["period"]).value) if cols["period"] else "",
                    wcet_ms=_norm(ws.cell(r, cols["wcet"]).value) if cols["wcet"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    partition=_norm(ws.cell(r, cols["partition"]).value) if cols["partition"] else "",
                )
                p.task_scheduling.append(task)
        p.detection_notes.append(f"Task Scheduling: {len(p.task_scheduling)} tasks found")

    # MPU Memory Partitioning
    mpu_sheet = "06_MPU_Memory_Partitioning"
    if mpu_sheet in wb.sheetnames:
        ws = wb[mpu_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "region_id": _col_for(header_map, ["region id", "id"]),
                "partition": _col_for(header_map, ["partition", "partition id"]),
                "base": _col_for(header_map, ["base address", "base"]),
                "size": _col_for(header_map, ["size"]),
                "perms": _col_for(header_map, ["permissions", "access"]),
                "asil": _col_for(header_map, ["asil"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                region_id = _norm(ws.cell(r, cols["region_id"]).value) if cols["region_id"] else ""
                if not region_id:
                    continue
                region = MpuRegion(
                    region_id=region_id,
                    partition_id=_norm(ws.cell(r, cols["partition"]).value) if cols["partition"] else "",
                    base_address=_norm(ws.cell(r, cols["base"]).value) if cols["base"] else "",
                    size=_norm(ws.cell(r, cols["size"]).value) if cols["size"] else "",
                    access_permissions=_norm(ws.cell(r, cols["perms"]).value) if cols["perms"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                )
                p.mpu_regions.append(region)
        p.detection_notes.append(f"MPU Regions: {len(p.mpu_regions)} regions found")

    # Inter-Component Interfaces
    interface_sheet = "07_Inter_Component_Interfaces"
    if interface_sheet in wb.sheetnames:
        ws = wb[interface_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "iface_id": _col_for(header_map, ["interface id", "id"]),
                "source": _col_for(header_map, ["source", "source swc"]),
                "dest": _col_for(header_map, ["destination", "dest", "dest swc"]),
                "type": _col_for(header_map, ["interface type", "type"]),
                "protection": _col_for(header_map, ["integrity", "protection"]),
                "asil": _col_for(header_map, ["asil"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                iface_id = _norm(ws.cell(r, cols["iface_id"]).value) if cols["iface_id"] else ""
                if not iface_id:
                    continue
                iface = InterComponentInterface(
                    interface_id=iface_id,
                    source_swc=_norm(ws.cell(r, cols["source"]).value) if cols["source"] else "",
                    dest_swc=_norm(ws.cell(r, cols["dest"]).value) if cols["dest"] else "",
                    interface_type=_norm(ws.cell(r, cols["type"]).value) if cols["type"] else "",
                    integrity_protection=_norm(ws.cell(r, cols["protection"]).value) if cols["protection"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                )
                p.interfaces.append(iface)
        p.detection_notes.append(f"Inter-Component Interfaces: {len(p.interfaces)} interfaces found")

    # Safety Mechanism Allocation
    safety_mech_sheet = "08_Safety_Mechanism_Allocation"
    if safety_mech_sheet in wb.sheetnames:
        ws = wb[safety_mech_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "swc_id": _col_for(header_map, ["swc id", "component id"]),
                "mech_id": _col_for(header_map, ["mechanism id", "id"]),
                "desc": _col_for(header_map, ["description"]),
                "asil": _col_for(header_map, ["asil"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                swc_id = _norm(ws.cell(r, cols["swc_id"]).value) if cols["swc_id"] else ""
                if not swc_id:
                    continue
                alloc = SafetyMechanismAlloc(
                    swc_id=swc_id,
                    mechanism_id=_norm(ws.cell(r, cols["mech_id"]).value) if cols["mech_id"] else "",
                    mechanism_description=_norm(ws.cell(r, cols["desc"]).value) if cols["desc"] else "",
                    allocated_asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                )
                p.safety_mechanism_allocs.append(alloc)
        p.detection_notes.append(f"Safety Mechanism Allocation: {len(p.safety_mechanism_allocs)} allocations found")

    # MISRA Compliance Targets
    misra_sheet = "09_MISRA_Compliance_Targets"
    if misra_sheet in wb.sheetnames:
        ws = wb[misra_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "swc_id": _col_for(header_map, ["swc id", "component id"]),
                "rule_cat": _col_for(header_map, ["rule category", "category"]),
                "compliance": _col_for(header_map, ["compliance", "compliance level"]),
                "justification": _col_for(header_map, ["justification"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                swc_id = _norm(ws.cell(r, cols["swc_id"]).value) if cols["swc_id"] else ""
                if not swc_id:
                    continue
                target = MisraTarget(
                    swc_id=swc_id,
                    rule_category=_norm(ws.cell(r, cols["rule_cat"]).value) if cols["rule_cat"] else "",
                    compliance_level=_norm(ws.cell(r, cols["compliance"]).value) if cols["compliance"] else "",
                    justification=_norm(ws.cell(r, cols["justification"]).value) if cols["justification"] else "",
                )
                p.misra_targets.append(target)
        p.detection_notes.append(f"MISRA Targets: {len(p.misra_targets)} targets found")

    # Initialization Sequence
    init_sheet = "10_Initialization_Sequence"
    if init_sheet in wb.sheetnames:
        ws = wb[init_sheet]
        header_row, header_map = _find_header_row(ws)
        p.init_sequence_rows = max(0, ws.max_row - (header_row or 1))
        p.detection_notes.append(f"Initialization Sequence: {p.init_sequence_rows} steps found")

    # Track TSC references
    for sheet in wb.sheetnames:
        if "tsc" in sheet.lower():
            p.tsc_reference_tabs.append(sheet)

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
        "n_sw_components": len(p.sw_components),
        "rtos_name": p.rtos_config.rtos_name,
        "n_tasks": len(p.task_scheduling),
        "n_mpu_regions": len(p.mpu_regions),
        "n_interfaces": len(p.interfaces),
        "n_safety_mechanisms": len(p.safety_mechanism_allocs),
        "n_misra_targets": len(p.misra_targets),
        "init_sequence_rows": p.init_sequence_rows,
        "detection_notes": p.detection_notes,
    }
    print(json.dumps(summary, indent=2))
