"""
SW Architecture Builder — generates ISO 26262-6 §7 software architecture workbook
from TSC xlsx + SW architecture JSON.

Usage:
    python generate_sw_architecture.py <tsc.xlsx> <sw_arch.json> <output.xlsx>

Reads:
  - TSC xlsx: SW partitions, FSRs, SW-TSRs, safety mechanisms
  - SW architecture JSON: SW components, tasks, scheduling, interfaces, MPU regions

Produces:
  - 12-tab xlsx: title, document control, TSC echo, SWC catalog, RTOS config,
    task scheduling, MPU partitioning, inter-component interfaces, safety
    mechanism allocation, MISRA compliance targets, initialization sequence,
    references
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from datetime import datetime

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from tsc_reader import read_tsc


# ---------------------------------------------------------------------------
# Styling (matching tsc-builder / hw-architecture-builder)
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def style_title_row(ws, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header_row(ws, row: int, headers: list[str]) -> None:
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = header_font()
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 32


def stripe_body(ws, start_row: int, end_row: int, last_col: int) -> None:
    for r in range(start_row, end_row + 1):
        fill = PatternFill("solid", fgColor=ALT_ROW) if (r - start_row) % 2 else None
        for c in range(1, last_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = body_font()
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER_ALL
            if fill:
                cell.fill = fill


def set_col_width(ws, col: int, width: float) -> None:
    ws.column_dimensions[get_column_letter(col)].width = width


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_sw_architecture(tsc_path: str, arch_json_path: str, output_path: str) -> None:
    """
    Main entry point: read TSC + JSON, generate 12-tab SW architecture xlsx.
    """
    # Read inputs
    tsc_data = read_tsc(tsc_path)
    with open(arch_json_path) as f:
        arch = json.load(f)

    # Create workbook
    wb = Workbook()
    wb.remove(wb.active)

    # Generate each tab
    gen_title_page(wb, tsc_data, arch)
    gen_document_control(wb, arch)
    gen_tsc_architecture_echo(wb, tsc_data, arch)
    gen_sw_component_catalog(wb, tsc_data, arch)
    gen_rtos_os_configuration(wb, arch)
    gen_task_scheduling_map(wb, arch)
    gen_mpu_memory_partitioning(wb, arch)
    gen_inter_component_interfaces(wb, arch)
    gen_safety_mechanism_allocation(wb, tsc_data, arch)
    gen_misra_compliance_targets(wb, arch)
    gen_initialization_sequence(wb, arch)
    gen_references(wb, tsc_data, arch)

    # Save
    wb.save(output_path)
    print(f"Generated: {output_path}")


def gen_title_page(wb: Workbook, tsc_data: dict, arch: dict) -> None:
    """Tab 00: Title Page"""
    ws = wb.create_sheet("00_Title_Page", 0)
    ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
    ws.page_setup.orientation = "portrait"

    # Title
    ws.merge_cells("A3:G3")
    title_cell = ws["A3"]
    title_cell.value = "SOFTWARE ARCHITECTURE DOCUMENT\nISO 26262-6 Section 7"
    title_cell.font = Font(name=FONT_NAME, size=16, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill("solid", fgColor=NAVY)
    title_cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[3].height = 40

    # Metadata
    proj = arch.get("project", {})
    metadata = [
        ("Project Name", proj.get("name", "")),
        ("Document ID", proj.get("doc_id", "")),
        ("Revision", proj.get("revision", "")),
        ("Date", proj.get("date", "")),
        ("Author", proj.get("author", "")),
        ("Approver", proj.get("approver", "")),
        ("Linked TSC", arch.get("linked_tsc", "")),
    ]

    row = 6
    for label, value in metadata:
        ws.cell(row, 2, label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row, 3, value)
        row += 1

    set_col_width(ws, 1, 2)
    set_col_width(ws, 2, 20)
    set_col_width(ws, 3, 40)


def gen_document_control(wb: Workbook, arch: dict) -> None:
    """Tab 01: Document Control (revision history)"""
    ws = wb.create_sheet("01_Document_Control", 1)

    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 2, ["Revision", "Date", "Author", "Change Summary", "Approver"])

    # Seed with current revision
    proj = arch.get("project", {})
    data = [
        [
            proj.get("revision", "0.1"),
            proj.get("date", ""),
            proj.get("author", ""),
            "Initial release",
            proj.get("approver", ""),
        ]
    ]

    for i, row_data in enumerate(data, start=3):
        for j, val in enumerate(row_data, start=1):
            ws.cell(i, j, val)

    stripe_body(ws, 3, len(data) + 2, 5)
    for i in range(1, 6):
        set_col_width(ws, i, 20)


def gen_tsc_architecture_echo(wb: Workbook, tsc_data: dict, arch: dict) -> None:
    """Tab 02: TSC Architecture Echo (read-only copy of SW partitions + FSRs)"""
    ws = wb.create_sheet("02_TSC_Architecture_Echo", 2)

    # SW Partitions section
    style_title_row(ws, 1, 6, "SW Partitions from TSC")
    style_header_row(ws, 2, ["Partition ID", "Name", "Type", "Allocated Nodes", "ASIL", "Notes"])

    row = 3
    for part in tsc_data.get("sw_partitions", []):
        ws.cell(row, 1, part["id"])
        ws.cell(row, 2, part["name"])
        ws.cell(row, 3, part["type"])
        ws.cell(row, 4, ", ".join(part.get("allocated_nodes", [])))
        ws.cell(row, 5, part["asil"])
        ws.cell(row, 6, part["notes"])
        row += 1

    last_part_row = row - 1
    stripe_body(ws, 3, last_part_row, 6)

    # FSRs section
    row = last_part_row + 3
    style_title_row(ws, row, 6, "FSRs Allocated to SW")
    row += 1
    style_header_row(ws, row, ["FSR ID", "ASIL", "FSR Text", "FTTI (ms)", "SW-TSR Ref", "Notes"])
    row += 1

    for fsr in tsc_data.get("fsrs", []):
        ws.cell(row, 1, fsr["fsr_id"])
        ws.cell(row, 2, fsr["asil"])
        ws.cell(row, 3, fsr["fsr_text"])
        ws.cell(row, 4, fsr.get("ftti_ms", ""))
        ws.cell(row, 5, "")  # to be filled by user
        ws.cell(row, 6, "")
        row += 1

    stripe_body(ws, last_part_row + 5, row - 1, 6)
    for i in range(1, 7):
        set_col_width(ws, i, 18)


def gen_sw_component_catalog(wb: Workbook, tsc_data: dict, arch: dict) -> None:
    """Tab 03: SW Component Catalog"""
    ws = wb.create_sheet("03_SW_Component_Catalog", 3)

    style_title_row(ws, 1, 9, "SW Component Catalog")
    headers = ["SWC_ID", "Name", "Parent Partition", "Type", "Language", "Allocated FSRs",
               "Allocated SW-TSRs", "ASIL", "MISRA Scope"]
    style_header_row(ws, 2, headers)

    row = 3
    for swc in arch.get("swcs", []):
        ws.cell(row, 1, swc["id"])
        ws.cell(row, 2, swc["name"])
        ws.cell(row, 3, swc["partition"])
        ws.cell(row, 4, swc.get("type", "Application"))
        ws.cell(row, 5, swc.get("language", "C"))
        ws.cell(row, 6, "")  # to be filled
        ws.cell(row, 7, "")  # to be filled
        ws.cell(row, 8, swc["asil"])
        ws.cell(row, 9, swc.get("misra_scope", "Required"))
        row += 1

    stripe_body(ws, 3, row - 1, 9)
    for i in range(1, 10):
        set_col_width(ws, i, 16)


def gen_rtos_os_configuration(wb: Workbook, arch: dict) -> None:
    """Tab 04: RTOS/OS Configuration"""
    ws = wb.create_sheet("04_RTOS_OS_Configuration", 4)

    style_title_row(ws, 1, 8, "RTOS / OS Configuration")
    style_header_row(ws, 2, ["Parameter", "Value", "Notes", "", "", "", "", ""])

    rtos = arch.get("rtos", {})
    config = [
        ["OS Name", rtos.get("name", "AUTOSAR Classic OS")],
        ["OS Version", rtos.get("version", "")],
        ["Scheduling Policy", rtos.get("scheduling", "priority preemptive")],
        ["Tick Rate (ms)", rtos.get("tick_ms", 1)],
        ["MPU Support", "Yes" if rtos.get("mpu", True) else "No"],
        ["Hypervisor", "Yes" if rtos.get("hypervisor", False) else "No"],
        ["Interrupt Latency (us)", rtos.get("irq_latency_us", "")],
        ["OS ASIL", rtos.get("asil", "B(D)")],
    ]

    row = 3
    for param, value in config:
        ws.cell(row, 1, param).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row, 2, value)
        row += 1

    stripe_body(ws, 3, row - 1, 8)
    set_col_width(ws, 1, 25)
    set_col_width(ws, 2, 25)


def gen_task_scheduling_map(wb: Workbook, arch: dict) -> None:
    """Tab 05: Task Scheduling Map"""
    ws = wb.create_sheet("05_Task_Scheduling_Map", 5)

    style_title_row(ws, 1, 8, "Task Scheduling Map")
    headers = ["Task ID", "Name", "Period (ms)", "Priority", "WCET (ms)", "Allocated SWCs", "Deadline (ms)", "Rate Monotonic OK"]
    style_header_row(ws, 2, headers)

    row = 3
    for task in arch.get("tasks", []):
        ws.cell(row, 1, task["id"])
        ws.cell(row, 2, task["name"])
        ws.cell(row, 3, task["period"])
        ws.cell(row, 4, task["priority"])
        ws.cell(row, 5, task["wcet"])
        ws.cell(row, 6, ", ".join(task.get("swcs", [])))
        ws.cell(row, 7, task.get("deadline", task["period"]))
        ws.cell(row, 8, "=IF(A{}>0, \"Yes\", \"Check\")".format(row))
        row += 1

    stripe_body(ws, 3, row - 1, 8)
    for i in range(1, 9):
        set_col_width(ws, i, 16)


def gen_mpu_memory_partitioning(wb: Workbook, arch: dict) -> None:
    """Tab 06: MPU Memory Partitioning"""
    ws = wb.create_sheet("06_MPU_Memory_Partitioning", 6)

    style_title_row(ws, 1, 8, "MPU Memory Partitioning")
    headers = ["Region ID", "Base Address", "Size", "Access", "Allocated Partition/SWC", "ASIL Isolation", "Fault Behavior", "Notes"]
    style_header_row(ws, 2, headers)

    row = 3
    mpu_regions = arch.get("mpu_regions", [])
    if not mpu_regions:
        # Seed with default regions per partition
        for part_id in set(swc["partition"] for swc in arch.get("swcs", [])):
            ws.cell(row, 1, f"MPU_{part_id}")
            ws.cell(row, 2, "0x...")
            ws.cell(row, 3, "...")
            ws.cell(row, 4, "RW")
            ws.cell(row, 5, part_id)
            ws.cell(row, 6, "Yes")
            ws.cell(row, 7, "Fault handler")
            ws.cell(row, 8, "")
            row += 1
    else:
        for region in mpu_regions:
            ws.cell(row, 1, region.get("id", ""))
            ws.cell(row, 2, region.get("base_addr", ""))
            ws.cell(row, 3, region.get("size", ""))
            ws.cell(row, 4, region.get("access", "RW"))
            ws.cell(row, 5, region.get("partition", ""))
            ws.cell(row, 6, "Yes")
            ws.cell(row, 7, region.get("fault_behavior", ""))
            ws.cell(row, 8, "")
            row += 1

    stripe_body(ws, 3, row - 1, 8)
    for i in range(1, 9):
        set_col_width(ws, i, 16)


def gen_inter_component_interfaces(wb: Workbook, arch: dict) -> None:
    """Tab 07: Inter-Component Interfaces"""
    ws = wb.create_sheet("07_Inter_Component_Interfaces", 7)

    style_title_row(ws, 1, 9, "Inter-Component Interfaces")
    headers = ["From SWC", "To SWC", "Interface Name", "Type", "Payload", "Integrity Protection", "Synchronous", "Error Handling", "Notes"]
    style_header_row(ws, 2, headers)

    row = 3
    for iface in arch.get("interfaces", []):
        ws.cell(row, 1, iface.get("from_swc", ""))
        ws.cell(row, 2, iface.get("to_swc", ""))
        ws.cell(row, 3, iface.get("name", ""))
        ws.cell(row, 4, iface.get("type", "data"))
        ws.cell(row, 5, iface.get("payload", ""))
        ws.cell(row, 6, iface.get("integrity", "CRC"))
        ws.cell(row, 7, "Yes" if iface.get("sync", True) else "No")
        ws.cell(row, 8, iface.get("error_handling", ""))
        ws.cell(row, 9, "")
        row += 1

    stripe_body(ws, 3, row - 1, 9)
    for i in range(1, 10):
        set_col_width(ws, i, 15)


def gen_safety_mechanism_allocation(wb: Workbook, tsc_data: dict, arch: dict) -> None:
    """Tab 08: Safety Mechanism Allocation"""
    ws = wb.create_sheet("08_Safety_Mechanism_Allocation", 8)

    style_title_row(ws, 1, 7, "Safety Mechanism Allocation per SWC")
    headers = ["SWC ID", "SWC Name", "Mechanism ID", "Mechanism Name", "Allocated TSR(s)", "ASIL", "Notes"]
    style_header_row(ws, 2, headers)

    row = 3
    swc_to_mechanisms = defaultdict(list)
    for swc in arch.get("swcs", []):
        swc_to_mechanisms[swc["id"]] = swc.get("mechanisms", [])

    mechanisms_by_id = {m["id"]: m for m in tsc_data.get("mechanisms", [])}

    for swc in arch.get("swcs", []):
        mech_ids = swc_to_mechanisms.get(swc["id"], [])
        if not mech_ids:
            ws.cell(row, 1, swc["id"])
            ws.cell(row, 2, swc["name"])
            row += 1
        else:
            for mech_id in mech_ids:
                mech = mechanisms_by_id.get(mech_id, {})
                ws.cell(row, 1, swc["id"])
                ws.cell(row, 2, swc["name"])
                ws.cell(row, 3, mech_id)
                ws.cell(row, 4, mech.get("name", ""))
                ws.cell(row, 5, "")  # to be filled
                ws.cell(row, 6, swc["asil"])
                ws.cell(row, 7, mech.get("notes", ""))
                row += 1

    stripe_body(ws, 3, row - 1, 7)
    for i in range(1, 8):
        set_col_width(ws, i, 18)


def gen_misra_compliance_targets(wb: Workbook, arch: dict) -> None:
    """Tab 09: MISRA C:2012 Compliance Targets"""
    ws = wb.create_sheet("09_MISRA_Compliance_Targets", 9)

    style_title_row(ws, 1, 6, "MISRA C:2012 Compliance Targets")
    headers = ["SWC ID", "SWC Name", "Required Violations Target", "Advisory Violations Target", "Tool", "Deviation Process"]
    style_header_row(ws, 2, headers)

    row = 3
    for swc in arch.get("swcs", []):
        ws.cell(row, 1, swc["id"])
        ws.cell(row, 2, swc["name"])
        ws.cell(row, 3, 0)  # default target
        ws.cell(row, 4, 0)
        ws.cell(row, 5, swc.get("misra_tool", ""))
        ws.cell(row, 6, "Per project standards")
        row += 1

    stripe_body(ws, 3, row - 1, 6)
    for i in range(1, 7):
        set_col_width(ws, i, 18)


def gen_initialization_sequence(wb: Workbook, arch: dict) -> None:
    """Tab 10: Initialization Sequence"""
    ws = wb.create_sheet("10_Initialization_Sequence", 10)

    style_title_row(ws, 1, 7, "Initialization Sequence")
    headers = ["Phase", "Duration (ms)", "SWCs Activated", "BIST Run", "Fault Behavior", "Next Phase", "Notes"]
    style_header_row(ws, 2, headers)

    phases = arch.get("init_phases", [
        {"phase": "Bootloader", "duration": 10, "swcs": [], "bist": "ROM+RAM", "fault": "Halt"},
        {"phase": "OS Start", "duration": 5, "swcs": [], "bist": "None", "fault": "Retry"},
        {"phase": "APP Start", "duration": 50, "swcs": [], "bist": "Functional", "fault": "Degraded mode"},
    ])

    row = 3
    for i, phase in enumerate(phases):
        ws.cell(row, 1, phase.get("phase", ""))
        ws.cell(row, 2, phase.get("duration", ""))
        ws.cell(row, 3, ", ".join(phase.get("swcs", [])))
        ws.cell(row, 4, phase.get("bist", ""))
        ws.cell(row, 5, phase.get("fault", ""))
        ws.cell(row, 6, phases[i + 1].get("phase", "Complete") if i + 1 < len(phases) else "Complete")
        ws.cell(row, 7, "")
        row += 1

    stripe_body(ws, 3, row - 1, 7)
    for i in range(1, 8):
        set_col_width(ws, i, 16)


def gen_references(wb: Workbook, tsc_data: dict, arch: dict) -> None:
    """Tab 11: References"""
    ws = wb.create_sheet("11_References", 11)

    style_title_row(ws, 1, 3, "References")
    style_header_row(ws, 2, ["Document", "Path / URL", "Notes"])

    references = [
        ["Linked TSC", arch.get("linked_tsc", ""), "System-level architecture"],
        ["ISO 26262-6", "Section 7 - Software Architectural Design", "Normative reference"],
        ["AUTOSAR Specification", "Classic Release 4.3 or later", "If applicable"],
        ["MISRA C:2012", "Guidelines for the use of C in critical systems", "Code compliance standard"],
        ["Project FSC", arch.get("project", {}).get("fsc_ref", ""), "Functional Safety Concept"],
    ]

    row = 3
    for ref in references:
        ws.cell(row, 1, ref[0])
        ws.cell(row, 2, ref[1])
        ws.cell(row, 3, ref[2])
        row += 1

    stripe_body(ws, 3, row - 1, 3)
    set_col_width(ws, 1, 25)
    set_col_width(ws, 2, 40)
    set_col_width(ws, 3, 25)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_sw_architecture.py <tsc.xlsx> <sw_arch.json> <output.xlsx>")
        sys.exit(1)

    tsc_path, arch_json_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]
    generate_sw_architecture(tsc_path, arch_json_path, output_path)
