"""CDD probe — reads xlsx and extracts CDD content."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from openpyxl import load_workbook


@dataclass
class ProbedCDD:
    path: str = ""
    sheet_names: list[str] = field(default_factory=list)
    title: str = ""
    project: str = ""
    doc_id: str = ""
    revision: str = ""
    author: str = ""
    approver: str = ""
    status: str = ""
    has_document_control: bool = False
    revision_history_rows: int = 0
    sessions: int = 0
    services: int = 0
    diids: int = 0
    riids: int = 0
    security_levels: int = 0
    variants: int = 0
    dtc_cross_ref: str = ""
    has_table_of_contents: bool = False


def probe(xlsx_path: str) -> ProbedCDD:
    """Probe a CDD xlsx and return structured data."""
    p = ProbedCDD(path=xlsx_path)

    try:
        wb = load_workbook(xlsx_path, data_only=True)
        p.sheet_names = wb.sheetnames

        # Title page
        if "Title" in wb.sheetnames:
            ws = wb["Title"]
            p.title = ws.cell(3, 1).value or ""
            for row in ws.iter_rows(min_row=6, max_row=15):
                label = row[1].value
                value = row[2].value
                if label == "Project":
                    p.project = value or ""
                elif label == "Document ID":
                    p.doc_id = value or ""
                elif label == "Revision":
                    p.revision = value or ""
                elif label == "Author":
                    p.author = value or ""
                elif label == "Approver":
                    p.approver = value or ""

        # Document Control
        if "Document Control" in wb.sheetnames:
            p.has_document_control = True
            ws = wb["Document Control"]
            for row in ws.iter_rows(min_row=5):
                if row[0].value:
                    p.revision_history_rows += 1

        # Sessions
        if "Session Catalog" in wb.sheetnames:
            ws = wb["Session Catalog"]
            for row in ws.iter_rows(min_row=5):
                if row[0].value:
                    p.sessions += 1

        # Services
        if "Service Inventory" in wb.sheetnames:
            ws = wb["Service Inventory"]
            for row in ws.iter_rows(min_row=5):
                if row[0].value:
                    p.services += 1

        # DIDs
        if "DID Catalog" in wb.sheetnames:
            ws = wb["DID Catalog"]
            for row in ws.iter_rows(min_row=5):
                if row[0].value:
                    p.diids += 1

        # RIDs
        if "RID Catalog" in wb.sheetnames:
            ws = wb["RID Catalog"]
            for row in ws.iter_rows(min_row=5):
                if row[0].value:
                    p.riids += 1

        # Security Levels
        if "Security Access Levels" in wb.sheetnames:
            ws = wb["Security Access Levels"]
            for row in ws.iter_rows(min_row=5):
                if row[0].value:
                    p.security_levels += 1

        # Variants
        if "Variant Coding" in wb.sheetnames:
            ws = wb["Variant Coding"]
            for row in ws.iter_rows(min_row=5):
                if row[0].value:
                    p.variants += 1

        # DTC Cross-ref
        if "DTC Cross-Reference" in wb.sheetnames:
            ws = wb["DTC Cross-Reference"]
            if ws.cell(5, 2).value:
                p.dtc_cross_ref = str(ws.cell(5, 2).value)

        # TOC check
        p.has_table_of_contents = "Title" in wb.sheetnames or len(p.sheet_names) >= 8

    except Exception:
        pass

    return p
