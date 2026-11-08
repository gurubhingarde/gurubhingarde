"""Probe AUTOSAR Adaptive App xlsx and extract key structures."""

from __future__ import annotations

from dataclasses import dataclass
from openpyxl import load_workbook

@dataclass
class ProbedAdaptive:
    title: str
    app_id: str
    app_manifest: list
    service_manifest: list
    machine_manifest: list
    ara_com_interfaces: list
    ara_exec_states: list
    process_config: list
    someip_config: list

def probe(xlsx_path: str) -> ProbedAdaptive:
    wb = load_workbook(xlsx_path)

    title = ""
    if "Title" in wb.sheetnames:
        ws = wb["Title"]
        title = ws.cell(3, 1).value or "Adaptive App"

    app_id = ""
    if "Application Identity" in wb.sheetnames:
        ws = wb["Application Identity"]
        app_id = ws.cell(4, 2).value or ""

    app_manifest = []
    if "Application Manifest" in wb.sheetnames:
        ws = wb["Application Manifest"]
        for row in range(3, 100):
            elem = ws.cell(row, 1).value
            if not elem:
                break
            app_manifest.append({
                "element": elem,
                "value": ws.cell(row, 2).value,
                "description": ws.cell(row, 3).value,
            })

    service_manifest = []
    if "Service Manifest" in wb.sheetnames:
        ws = wb["Service Manifest"]
        for row in range(3, 100):
            svc = ws.cell(row, 1).value
            if not svc:
                break
            service_manifest.append({
                "name": svc,
                "id": ws.cell(row, 2).value,
                "interface": ws.cell(row, 3).value,
                "ara_com_type": ws.cell(row, 4).value,
            })

    machine_manifest = []
    if "Machine Manifest" in wb.sheetnames:
        ws = wb["Machine Manifest"]
        for row in range(3, 100):
            elem = ws.cell(row, 1).value
            if not elem:
                break
            machine_manifest.append({
                "element": elem,
                "value": ws.cell(row, 2).value,
                "processor": ws.cell(row, 3).value,
            })

    ara_com_interfaces = []
    if "ara::com Service Interfaces" in wb.sheetnames:
        ws = wb["ara::com Service Interfaces"]
        for row in range(3, 100):
            iface = ws.cell(row, 1).value
            if not iface:
                break
            ara_com_interfaces.append({
                "name": iface,
                "comm_type": ws.cell(row, 2).value,
                "event_name": ws.cell(row, 3).value,
                "field_name": ws.cell(row, 4).value,
                "datatype": ws.cell(row, 5).value,
            })

    ara_exec_states = []
    if "ara::exec Lifecycle" in wb.sheetnames:
        ws = wb["ara::exec Lifecycle"]
        for row in range(3, 100):
            state = ws.cell(row, 1).value
            if not state:
                break
            ara_exec_states.append({
                "name": state,
                "id": ws.cell(row, 2).value,
                "from": ws.cell(row, 3).value,
                "to": ws.cell(row, 4).value,
            })

    process_config = []
    if "Process Configuration" in wb.sheetnames:
        ws = wb["Process Configuration"]
        for row in range(3, 100):
            proc = ws.cell(row, 1).value
            if not proc:
                break
            process_config.append({
                "name": proc,
                "id": ws.cell(row, 2).value,
                "posix_user": ws.cell(row, 3).value,
                "work_dir": ws.cell(row, 4).value,
            })

    someip_config = []
    if "SOME/IP Configuration" in wb.sheetnames:
        ws = wb["SOME/IP Configuration"]
        for row in range(3, 100):
            svc = ws.cell(row, 1).value
            if not svc:
                break
            someip_config.append({
                "service": svc,
                "service_id": ws.cell(row, 2).value,
                "instance_id": ws.cell(row, 3).value,
                "port": ws.cell(row, 4).value,
            })

    return ProbedAdaptive(
        title=title,
        app_id=app_id,
        app_manifest=app_manifest,
        service_manifest=service_manifest,
        machine_manifest=machine_manifest,
        ara_com_interfaces=ara_com_interfaces,
        ara_exec_states=ara_exec_states,
        process_config=process_config,
        someip_config=someip_config,
    )
