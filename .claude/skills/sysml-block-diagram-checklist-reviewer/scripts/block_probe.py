"""Probe and extract SysML block diagram content from xlsx."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook


@dataclass
class BlockInfo:
    name: str
    stereotype: str = ""
    parent: str = ""
    description: str = ""


@dataclass
class PropertyInfo:
    block: str
    name: str
    type_: str = ""
    multiplicity: str = ""


@dataclass
class PortInfo:
    owner_block: str
    name: str
    port_type: str = ""
    flow_type: str = ""
    direction: str = ""


@dataclass
class ConnectorInfo:
    name: str
    source_port: str = ""
    target_port: str = ""
    connector_type: str = ""


@dataclass
class ProbedBlockDiagram:
    file_path: str = ""
    sheet_names: list[str] = field(default_factory=list)
    blocks: dict[str, BlockInfo] = field(default_factory=dict)
    properties: dict[str, list[PropertyInfo]] = field(default_factory=dict)
    ports: dict[str, list[PortInfo]] = field(default_factory=dict)
    connectors: list[ConnectorInfo] = field(default_factory=list)
    is_builder_format: bool = False

    def block_count(self) -> int:
        return len(self.blocks)

    def port_count(self) -> int:
        return sum(len(p) for p in self.ports.values())

    def connector_count(self) -> int:
        return len(self.connectors)


def probe(file_path: str | Path) -> ProbedBlockDiagram:
    """Probe a block diagram xlsx and extract structured content."""
    file_path = Path(file_path)
    wb = load_workbook(file_path, data_only=True)

    result = ProbedBlockDiagram(
        file_path=str(file_path),
        sheet_names=list(wb.sheetnames),
        is_builder_format=any(s.startswith("0") for s in wb.sheetnames) if wb.sheetnames else False,
    )

    # Probe Block Catalog (tab 3 or containing "Block_Catalog")
    for sheet_name in result.sheet_names:
        if "block_catalog" in sheet_name.lower() or sheet_name.startswith("3"):
            ws = wb[sheet_name]
            for row in ws.iter_rows(min_row=4, values_only=True):
                if row[0]:
                    block = BlockInfo(
                        name=str(row[0]).strip(),
                        stereotype=str(row[1]).strip() if row[1] else "",
                        parent=str(row[3]).strip() if len(row) > 3 and row[3] else "",
                        description=str(row[2]).strip() if len(row) > 2 and row[2] else "",
                    )
                    result.blocks[block.name] = block

    # Probe Port Catalog
    for sheet_name in result.sheet_names:
        if "port_catalog" in sheet_name.lower() or sheet_name.startswith("6"):
            ws = wb[sheet_name]
            for row in ws.iter_rows(min_row=4, values_only=True):
                if row[0]:
                    owner = str(row[0]).strip()
                    port = PortInfo(
                        owner_block=owner,
                        name=str(row[1]).strip() if row[1] else "",
                        port_type=str(row[2]).strip() if len(row) > 2 and row[2] else "",
                        flow_type=str(row[3]).strip() if len(row) > 3 and row[3] else "",
                        direction=str(row[4]).strip() if len(row) > 4 and row[4] else "",
                    )
                    if owner not in result.ports:
                        result.ports[owner] = []
                    result.ports[owner].append(port)

    # Probe Connector Catalog
    for sheet_name in result.sheet_names:
        if "connector_catalog" in sheet_name.lower() or sheet_name.startswith("7"):
            ws = wb[sheet_name]
            for row in ws.iter_rows(min_row=4, values_only=True):
                if row[0]:
                    conn = ConnectorInfo(
                        name=str(row[0]).strip(),
                        source_port=str(row[1]).strip() if row[1] else "",
                        target_port=str(row[2]).strip() if len(row) > 2 and row[2] else "",
                        connector_type=str(row[3]).strip() if len(row) > 3 and row[3] else "",
                    )
                    result.connectors.append(conn)

    # Probe Property Catalog
    for sheet_name in result.sheet_names:
        if "property_catalog" in sheet_name.lower() or sheet_name.startswith("4"):
            ws = wb[sheet_name]
            for row in ws.iter_rows(min_row=4, values_only=True):
                if row[0]:
                    owner = str(row[0]).strip()
                    prop = PropertyInfo(
                        block=owner,
                        name=str(row[1]).strip() if row[1] else "",
                        type_=str(row[2]).strip() if len(row) > 2 and row[2] else "",
                        multiplicity=str(row[3]).strip() if len(row) > 3 and row[3] else "",
                    )
                    if owner not in result.properties:
                        result.properties[owner] = []
                    result.properties[owner].append(prop)

    return result
