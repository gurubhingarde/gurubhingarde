"""Bus Load Analysis Workbook Probe - extracts key data for validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from openpyxl import load_workbook


@dataclass
class ProbedBusLoad:
    filepath: str = ""
    title: str = ""
    author: str = ""
    approver: str = ""
    revision: str = ""
    status: str = ""

    sheet_names: list[str] = field(default_factory=list)
    has_title: bool = False
    has_doc_control: bool = False
    has_bus_config: bool = False
    has_message_inventory: bool = False
    has_load_calc: bool = False
    has_scenarios: bool = False

    bus_count: int = 0
    message_count: int = 0
    formula_count: int = 0
    error_cells: int = 0

    buses: dict[str, dict] = field(default_factory=dict)
    messages: dict[str, dict] = field(default_factory=dict)
    loads: dict[str, float] = field(default_factory=dict)


def probe(filepath: str) -> ProbedBusLoad:
    """Extract workbook metadata and content."""
    p = ProbedBusLoad(filepath=filepath)

    try:
        wb = load_workbook(filepath, data_only=False)
        p.sheet_names = wb.sheetnames

        p.has_title = "Title" in p.sheet_names
        p.has_doc_control = "Document Control" in p.sheet_names
        p.has_bus_config = "Bus Configuration" in p.sheet_names
        p.has_message_inventory = "Message Inventory" in p.sheet_names
        p.has_load_calc = "Load Calculation" in p.sheet_names
        p.has_scenarios = "Scenario Analysis" in p.sheet_names

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

        if p.has_bus_config:
            ws = wb["Bus Configuration"]
            for row in ws.iter_rows(min_row=3, values_only=True):
                if row[0]:
                    p.buses[row[0]] = {
                        "name": row[1],
                        "protocol": row[2],
                        "baud_rate": row[3],
                        "frame_overhead": row[4],
                    }
            p.bus_count = len(p.buses)

        if p.has_message_inventory:
            ws = wb["Message Inventory"]
            for row in ws.iter_rows(min_row=3, values_only=True):
                if row[0]:
                    p.messages[row[0]] = {
                        "name": row[1],
                        "bus_id": row[2],
                        "cycle_time": row[3],
                        "dlc": row[4],
                        "format": row[5],
                    }
            p.message_count = len(p.messages)

        if p.has_load_calc:
            ws = wb["Load Calculation"]
            for row in ws.iter_rows(min_row=3, values_only=True):
                if row[0]:
                    load_pct = row[8] if len(row) > 8 else None
                    if load_pct is not None:
                        p.loads[row[0]] = float(load_pct) if isinstance(load_pct, (int, float)) else 0.0

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
