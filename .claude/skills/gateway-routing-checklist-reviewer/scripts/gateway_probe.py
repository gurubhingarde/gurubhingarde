"""Gateway Routing Workbook Probe - extracts key data for validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from openpyxl import load_workbook


@dataclass
class ProbedGateway:
    filepath: str = ""
    title: str = ""
    author: str = ""
    approver: str = ""
    revision: str = ""
    status: str = ""

    sheet_names: list[str] = field(default_factory=list)
    has_title: bool = False
    has_doc_control: bool = False
    has_gateway_ecu: bool = False
    has_source_buses: bool = False
    has_dest_buses: bool = False
    has_routing_table: bool = False
    has_latency_budget: bool = False
    has_security_rules: bool = False

    gateway_id: str = ""
    source_bus_count: int = 0
    dest_bus_count: int = 0
    route_count: int = 0
    rule_count: int = 0
    formula_count: int = 0
    error_cells: int = 0

    source_buses: dict[str, dict] = field(default_factory=dict)
    dest_buses: dict[str, dict] = field(default_factory=dict)
    routes: dict[str, dict] = field(default_factory=dict)
    rules: dict[str, dict] = field(default_factory=dict)


def probe(filepath: str) -> ProbedGateway:
    """Extract workbook metadata and content."""
    p = ProbedGateway(filepath=filepath)

    try:
        wb = load_workbook(filepath, data_only=False)
        p.sheet_names = wb.sheetnames

        p.has_title = "Title" in p.sheet_names
        p.has_doc_control = "Document Control" in p.sheet_names
        p.has_gateway_ecu = "Gateway ECU Definition" in p.sheet_names
        p.has_source_buses = "Source Bus Inventory" in p.sheet_names
        p.has_dest_buses = "Destination Bus Inventory" in p.sheet_names
        p.has_routing_table = "Routing Table" in p.sheet_names
        p.has_latency_budget = "Latency Budget" in p.sheet_names
        p.has_security_rules = "Security/Firewall Rules" in p.sheet_names

        if p.has_title:
            ws = wb["Title"]
            for row in ws.iter_rows(min_row=5, values_only=True):
                if row[0] == "Author":
                    p.author = row[1] or ""
                elif row[0] == "Approver":
                    p.approver = row[1] or ""
                elif row[0] == "Revision":
                    p.revision = row[1] or ""
                elif row[0] == "Title" and not p.title:
                    p.title = row[1] or ""

        if p.has_gateway_ecu:
            ws = wb["Gateway ECU Definition"]
            for row in ws.iter_rows(min_row=3, values_only=True):
                if row[0] == "ECU ID":
                    p.gateway_id = row[1] or ""

        if p.has_source_buses:
            ws = wb["Source Bus Inventory"]
            for row in ws.iter_rows(min_row=3, values_only=True):
                if row[0]:
                    p.source_buses[row[0]] = {
                        "name": row[1],
                        "protocol": row[2],
                        "description": row[3] if len(row) > 3 else "",
                    }
            p.source_bus_count = len(p.source_buses)

        if p.has_dest_buses:
            ws = wb["Destination Bus Inventory"]
            for row in ws.iter_rows(min_row=3, values_only=True):
                if row[0]:
                    p.dest_buses[row[0]] = {
                        "name": row[1],
                        "protocol": row[2],
                        "description": row[3] if len(row) > 3 else "",
                    }
            p.dest_bus_count = len(p.dest_buses)

        if p.has_routing_table:
            ws = wb["Routing Table"]
            for row in ws.iter_rows(min_row=3, values_only=True):
                if row[0]:
                    p.routes[row[0]] = {
                        "source_bus": row[1],
                        "dest_bus": row[2],
                        "signal_ids": row[3],
                        "transformation": row[4] if len(row) > 4 else "None",
                        "latency_ms": row[5] if len(row) > 5 else None,
                    }
            p.route_count = len(p.routes)

        if p.has_security_rules:
            ws = wb["Security/Firewall Rules"]
            for row in ws.iter_rows(min_row=3, values_only=True):
                if row[0]:
                    p.rules[row[0]] = {
                        "source_bus": row[1],
                        "dest_bus": row[2],
                        "allowed": row[3] if len(row) > 3 else True,
                        "description": row[4] if len(row) > 4 else "",
                    }
            p.rule_count = len(p.rules)

        for sheet_name in p.sheet_names:
            ws = wb[sheet_name]
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value and isinstance(cell.value, str):
                        if cell.value.startswith("="):
                            p.formula_count += 1
                        elif "#" in cell.value and any(err in cell.value for err in ["VALUE!", "DIV/0!", "REF!", "NAME?"]):
                            p.error_cells += 1

        wb.close()

    except Exception as e:
        print(f"Error probing {filepath}: {e}")

    return p
