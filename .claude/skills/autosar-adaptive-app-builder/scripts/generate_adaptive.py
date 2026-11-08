"""
AUTOSAR Adaptive Application Builder — generates a multi-tab Adaptive Platform workbook.

Usage:
    python generate_adaptive.py <input.json> <output.xlsx>
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

def style_title(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28

def style_header(ws, row, headers):
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 36

def build_title(wb, item):
    ws = wb.create_sheet("Title", 0)
    ws.sheet_view.showGridLines = False
    style_title(ws, 2, 4, "AUTOSAR Adaptive Application Specification Workbook")
    style_title(ws, 3, 4, item.get("name", "Unnamed Adaptive App"))
    row = 5
    fields = [
        ("Project", item.get("project")),
        ("Document ID", item.get("doc_id")),
        ("Revision", item.get("revision", "1.0")),
        ("Date", item.get("date", str(date.today()))),
        ("Author", item.get("author")),
    ]
    for label, value in fields:
        ws.cell(row=row, column=1, value=label).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

def build_document_control(wb):
    ws = wb.create_sheet("Document Control", 1)
    style_title(ws, 1, 4, "Document Control")
    headers = ["Change No.", "Revision", "Date", "Description"]
    style_header(ws, 2, headers)
    ws.cell(row=3, column=1, value=1)
    ws.cell(row=3, column=2, value="1.0")
    ws.cell(row=3, column=3, value=str(date.today()))

def build_app_identity(wb, app):
    ws = wb.create_sheet("Application Identity", 2)
    style_title(ws, 1, 5, "Application Identity")
    row = 3
    fields = [
        ("Application Name", app.get("name")),
        ("Application ID", app.get("id")),
        ("SWCL Type", app.get("swcl_type")),
        ("Adaptive Platform Version", app.get("ap_version", "R22-11")),
    ]
    for label, value in fields:
        ws.cell(row=row, column=1, value=label).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)
        row += 1

def build_app_manifest(wb, manifest):
    ws = wb.create_sheet("Application Manifest", 3)
    style_title(ws, 1, 6, "Application Manifest")
    headers = ["Manifest Element", "Value", "Description", "Cardinality", "Type", "Required"]
    style_header(ws, 2, headers)
    for idx, elem in enumerate(manifest, start=3):
        ws.cell(row=idx, column=1, value=elem.get("element"))
        ws.cell(row=idx, column=2, value=elem.get("value"))
        ws.cell(row=idx, column=3, value=elem.get("description"))

def build_service_manifest(wb, services):
    ws = wb.create_sheet("Service Manifest", 4)
    style_title(ws, 1, 7, "Service Manifest")
    headers = ["Service Name", "Service ID", "Service Interface", "ara::com Type", "Instance Count", "Notes"]
    style_header(ws, 2, headers)
    for idx, svc in enumerate(services, start=3):
        ws.cell(row=idx, column=1, value=svc.get("name"))
        ws.cell(row=idx, column=2, value=svc.get("id"))
        ws.cell(row=idx, column=3, value=svc.get("interface"))
        ws.cell(row=idx, column=4, value=svc.get("ara_com_type"))

def build_machine_manifest(wb, machine):
    ws = wb.create_sheet("Machine Manifest", 5)
    style_title(ws, 1, 6, "Machine Manifest")
    headers = ["Machine Element", "Value", "Processor", "Network Interface", "Host ECU", "Type"]
    style_header(ws, 2, headers)
    for idx, elem in enumerate(machine, start=3):
        ws.cell(row=idx, column=1, value=elem.get("element"))
        ws.cell(row=idx, column=2, value=elem.get("value"))
        ws.cell(row=idx, column=3, value=elem.get("processor"))

def build_ara_com_interfaces(wb, interfaces):
    ws = wb.create_sheet("ara::com Service Interfaces", 6)
    style_title(ws, 1, 7, "ara::com Service Interfaces")
    headers = ["Interface Name", "Communication Type", "Event Name", "Field Name", "Datatype", "Queue Length"]
    style_header(ws, 2, headers)
    for idx, iface in enumerate(interfaces, start=3):
        ws.cell(row=idx, column=1, value=iface.get("name"))
        ws.cell(row=idx, column=2, value=iface.get("comm_type"))
        ws.cell(row=idx, column=3, value=iface.get("event_name"))
        ws.cell(row=idx, column=4, value=iface.get("field_name"))
        ws.cell(row=idx, column=5, value=iface.get("datatype"))

def build_ara_exec_lifecycle(wb, states):
    ws = wb.create_sheet("ara::exec Lifecycle", 7)
    style_title(ws, 1, 6, "ara::exec Lifecycle States")
    headers = ["State Name", "State ID", "Transition From", "Transition To", "Entry Action", "Exit Action"]
    style_header(ws, 2, headers)
    for idx, state in enumerate(states, start=3):
        ws.cell(row=idx, column=1, value=state.get("name"))
        ws.cell(row=idx, column=2, value=state.get("id"))
        ws.cell(row=idx, column=3, value=state.get("from"))
        ws.cell(row=idx, column=4, value=state.get("to"))

def build_process_config(wb, processes):
    ws = wb.create_sheet("Process Configuration", 8)
    style_title(ws, 1, 7, "Process Configuration")
    headers = ["Process Name", "Process ID", "POSIX User", "Working Directory", "CPU Affinity", "Stack Size"]
    style_header(ws, 2, headers)
    for idx, proc in enumerate(processes, start=3):
        ws.cell(row=idx, column=1, value=proc.get("name"))
        ws.cell(row=idx, column=2, value=proc.get("id"))
        ws.cell(row=idx, column=3, value=proc.get("posix_user"))
        ws.cell(row=idx, column=4, value=proc.get("work_dir"))

def build_deployment_topology(wb, deployments):
    ws = wb.create_sheet("Deployment Topology", 9)
    style_title(ws, 1, 7, "Deployment Topology")
    headers = ["Application", "Target ECU", "Network Interface", "IP Address", "Service Instance", "SOME/IP"]
    style_header(ws, 2, headers)
    for idx, dep in enumerate(deployments, start=3):
        ws.cell(row=idx, column=1, value=dep.get("app"))
        ws.cell(row=idx, column=2, value=dep.get("ecu"))
        ws.cell(row=idx, column=3, value=dep.get("network_if"))
        ws.cell(row=idx, column=4, value=dep.get("ip_addr"))

def build_resource_constraints(wb):
    ws = wb.create_sheet("Resource Constraints", 10)
    style_title(ws, 1, 6, "Resource Constraints (CPU, Memory)")
    headers = ["Resource Type", "Allocated", "Unit", "Current Usage %", "Peak Usage %", "Margin"]
    style_header(ws, 2, headers)

def build_someip_config(wb, someip):
    ws = wb.create_sheet("SOME/IP Configuration", 11)
    style_title(ws, 1, 6, "SOME/IP Configuration")
    headers = ["Service Name", "Service ID", "Instance ID", "Port Number", "Protocol", "SD Enabled"]
    style_header(ws, 2, headers)
    for idx, cfg in enumerate(someip, start=3):
        ws.cell(row=idx, column=1, value=cfg.get("service"))
        ws.cell(row=idx, column=2, value=cfg.get("service_id"))
        ws.cell(row=idx, column=3, value=cfg.get("instance_id"))
        ws.cell(row=idx, column=4, value=cfg.get("port"))

def build_validation_rules(wb):
    ws = wb.create_sheet("Validation Rules", 12)
    style_title(ws, 1, 5, "Validation Rules")
    headers = ["Rule ID", "Rule Description", "Applies To", "Severity"]
    style_header(ws, 2, headers)

def build_references(wb):
    ws = wb.create_sheet("References", 13)
    style_title(ws, 1, 3, "References")
    row = 3
    refs = [
        ("AUTOSAR Adaptive R22-11", "AUTOSAR Adaptive Platform specification"),
        ("Adaptive Methodology", "scripts/references/adaptive_concepts.md"),
    ]
    for ref, desc in refs:
        ws.cell(row=row, column=1, value=ref).font = Font(bold=True)
        ws.cell(row=row, column=2, value=desc)
        row += 1

def main():
    if len(sys.argv) < 2:
        input_json = {
            "item": {"name": "Example Adaptive App", "project": "Project Y", "doc_id": "DOC-003"},
            "app": {"name": "AdaptiveApp1", "id": "APP_001", "swcl_type": "ApplicationSwComponentType"},
            "app_manifest": [],
            "service_manifest": [],
            "machine_manifest": [],
            "ara_com_interfaces": [],
            "ara_exec_lifecycle": [],
            "process_config": [],
            "deployment_topology": [],
            "someip_config": [],
        }
    else:
        with open(sys.argv[1], "r") as f:
            input_json = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    build_title(wb, input_json.get("item", {}))
    build_document_control(wb)
    build_app_identity(wb, input_json.get("app", {}))
    build_app_manifest(wb, input_json.get("app_manifest", []))
    build_service_manifest(wb, input_json.get("service_manifest", []))
    build_machine_manifest(wb, input_json.get("machine_manifest", []))
    build_ara_com_interfaces(wb, input_json.get("ara_com_interfaces", []))
    build_ara_exec_lifecycle(wb, input_json.get("ara_exec_lifecycle", []))
    build_process_config(wb, input_json.get("process_config", []))
    build_deployment_topology(wb, input_json.get("deployment_topology", []))
    build_resource_constraints(wb)
    build_someip_config(wb, input_json.get("someip_config", []))
    build_validation_rules(wb)
    build_references(wb)

    output_file = sys.argv[2] if len(sys.argv) > 2 else "adaptive_app.xlsx"
    wb.save(output_file)
    print(f"Generated {output_file}")

if __name__ == "__main__":
    main()
