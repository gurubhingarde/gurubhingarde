"""Incident Response Plan probe - extracts structure from IRP xlsx."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from openpyxl import load_workbook

@dataclass
class ProbedIRP:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    doc_id: str = ""
    sheet_names: list[str] = field(default_factory=list)
    psirt_members: int = 0
    triage_severities: int = 0
    detection_sources: int = 0
    response_stages: int = 0
    disclosure_policy: bool = False
    oui_workflow: bool = False
    regulatory_notifs: int = 0
    customer_comms: int = 0
    post_incident: bool = False
    templates: int = 0
    is_builder_format: bool = False

def _norm(s: Any) -> str:
    if s is None: return ""
    return str(s).strip()

def probe(xlsx_path: str | Path) -> ProbedIRP:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedIRP(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    p.is_builder_format = "02_PSIRT_Roster" in wb.sheetnames

    # Title page metadata
    if "00_Title_Page" in wb.sheetnames:
        ws = wb["00_Title_Page"]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if "title" in label: p.title = value
                elif "revision" in label: p.revision = value
                elif "status" in label: p.status = value
                elif "author" in label: p.author = value
                elif "approver" in label: p.approver = value
                elif "doc" in label: p.doc_id = value

    # PSIRT Roster
    if "02_PSIRT_Roster" in wb.sheetnames:
        ws = wb["02_PSIRT_Roster"]
        p.psirt_members = sum(1 for r in range(2, ws.max_row + 1) if _norm(ws.cell(r, 1).value))

    # Triage Classification
    if "03_Triage_Classification" in wb.sheetnames:
        ws = wb["03_Triage_Classification"]
        p.triage_severities = sum(1 for r in range(2, ws.max_row + 1) if _norm(ws.cell(r, 1).value))

    # Detection Sources
    if "04_Detection_Sources" in wb.sheetnames:
        ws = wb["04_Detection_Sources"]
        p.detection_sources = sum(1 for r in range(2, ws.max_row + 1) if _norm(ws.cell(r, 1).value))

    # Response Workflow
    if "05_Response_Workflow" in wb.sheetnames:
        ws = wb["05_Response_Workflow"]
        p.response_stages = sum(1 for r in range(2, ws.max_row + 1) if _norm(ws.cell(r, 1).value))

    # Coordinated Disclosure Policy
    if "06_Coordinated_Disclosure_Policy" in wb.sheetnames:
        ws = wb["06_Coordinated_Disclosure_Policy"]
        p.disclosure_policy = ws.max_row > 1

    # OTA Patch Workflow
    if "07_OTA_Patch_Workflow" in wb.sheetnames:
        ws = wb["07_OTA_Patch_Workflow"]
        p.oui_workflow = ws.max_row > 1

    # Regulatory Notifications
    if "08_Regulatory_Notifications" in wb.sheetnames:
        ws = wb["08_Regulatory_Notifications"]
        p.regulatory_notifs = sum(1 for r in range(2, ws.max_row + 1) if _norm(ws.cell(r, 1).value))

    # Customer Communications
    if "09_Customer_Communications" in wb.sheetnames:
        ws = wb["09_Customer_Communications"]
        p.customer_comms = sum(1 for r in range(2, ws.max_row + 1) if _norm(ws.cell(r, 1).value))

    # Post-Incident Review
    if "10_Post_Incident_Review" in wb.sheetnames:
        ws = wb["10_Post_Incident_Review"]
        p.post_incident = ws.max_row > 1

    # Communication Templates
    if "11_Communication_Templates" in wb.sheetnames:
        ws = wb["11_Communication_Templates"]
        p.templates = sum(1 for r in range(2, ws.max_row + 1) if _norm(ws.cell(r, 1).value))

    return p

if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    print(json.dumps({
        "path": p.path, "title": p.title, "revision": p.revision, "status": p.status,
        "author": p.author, "approver": p.approver, "doc_id": p.doc_id,
        "sheets": p.sheet_names, "psirt_members": p.psirt_members,
        "triage_severities": p.triage_severities, "detection_sources": p.detection_sources,
        "response_stages": p.response_stages, "regulatory_notifs": p.regulatory_notifs,
        "customer_comms": p.customer_comms, "templates": p.templates,
        "is_builder_format": p.is_builder_format
    }, indent=2))
