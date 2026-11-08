"""Automotive Ethernet config xlsx probe — extract metadata and tables."""

from __future__ import annotations

from dataclasses import dataclass, field
from openpyxl import load_workbook


@dataclass
class ProbedAutoEth:
    path: str
    sheet_names: list[str] = field(default_factory=list)
    network_name: str = ""
    doc_id: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    vlans: list[dict] = field(default_factory=list)
    services: list[dict] = field(default_factory=list)
    avb_streams: list[dict] = field(default_factory=list)
    multicast_groups: list[dict] = field(default_factory=list)
    switches: list[dict] = field(default_factory=list)
    revision_history_rows: int = 0


def probe(path: str) -> ProbedAutoEth:
    """Probe an Automotive Ethernet config xlsx and extract tables, metadata."""
    wb = load_workbook(path, data_only=True)
    p = ProbedAutoEth(path=path, sheet_names=wb.sheetnames)

    # Title page
    for sname in ["Title_Page", "Title"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            for row in ws.iter_rows(min_row=1, max_row=20, values_only=True):
                if row and len(row) >= 2:
                    cell0 = str(row[0] or "")
                    if "Network Name" in cell0:
                        p.network_name = str(row[2] or "") if len(row) > 2 else ""
                    if "Document ID" in cell0:
                        p.doc_id = str(row[2] or "") if len(row) > 2 else ""
                    if "Revision" in cell0:
                        p.revision = str(row[2] or "") if len(row) > 2 else ""
                    if "Status" in cell0:
                        p.status = str(row[2] or "") if len(row) > 2 else ""
                    if "Author" in cell0:
                        p.author = str(row[2] or "") if len(row) > 2 else ""
                    if "Approver" in cell0:
                        p.approver = str(row[2] or "") if len(row) > 2 else ""
            break

    # VLAN Config
    for sname in ["VLAN_Config", "VLAN Configuration"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            for row in ws.iter_rows(min_row=4, max_row=100, values_only=True):
                if row and len(row) >= 2 and row[0] is not None:
                    p.vlans.append({
                        "vlan_id": row[0],
                        "name": str(row[1] or "") if len(row) > 1 else "",
                        "priority": row[2] if len(row) > 2 else 0,
                    })
            break

    # SOME/IP Catalog
    for sname in ["SOMEIP_Catalog", "SOME/IP Services"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            for row in ws.iter_rows(min_row=4, max_row=100, values_only=True):
                if row and len(row) >= 2 and row[0]:
                    p.services.append({
                        "service_id": str(row[0] or ""),
                        "name": str(row[1] or "") if len(row) > 1 else "",
                        "provider": str(row[4] or "") if len(row) > 4 else "",
                        "consumers": str(row[5] or "") if len(row) > 5 else "",
                    })
            break

    # AVB Streams
    for sname in ["AVB_Streams", "AVB Stream Allocation"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            for row in ws.iter_rows(min_row=4, max_row=100, values_only=True):
                if row and len(row) >= 2 and row[0]:
                    p.avb_streams.append({
                        "stream_id": str(row[0] or ""),
                        "talker": str(row[1] or "") if len(row) > 1 else "",
                        "listeners": str(row[2] or "") if len(row) > 2 else "",
                        "bandwidth": row[3] if len(row) > 3 else 0,
                    })
            break

    # Multicast Routing
    for sname in ["Multicast_Routing", "Multicast Routing"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            for row in ws.iter_rows(min_row=4, max_row=100, values_only=True):
                if row and len(row) >= 2 and row[0]:
                    p.multicast_groups.append({
                        "group_address": str(row[0] or ""),
                        "sources": str(row[1] or "") if len(row) > 1 else "",
                        "listeners": str(row[2] or "") if len(row) > 2 else "",
                    })
            break

    # Network Topology
    for sname in ["Network_Topology", "Topology"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            for row in ws.iter_rows(min_row=4, max_row=100, values_only=True):
                if row and len(row) >= 2 and row[0]:
                    p.switches.append({
                        "id": str(row[0] or ""),
                        "name": str(row[1] or "") if len(row) > 1 else "",
                    })
            break

    # Revision history
    for sname in ["Document_Control", "Document Control"]:
        if sname in wb.sheetnames:
            ws = wb[sname]
            count = 0
            for row in ws.iter_rows(min_row=4, max_row=100, values_only=True):
                if row and row[0]:
                    count += 1
            p.revision_history_rows = count
            break

    return p
