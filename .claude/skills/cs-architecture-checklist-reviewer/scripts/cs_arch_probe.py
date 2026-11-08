"""CS Architecture content probe - extracts structure from CS Architecture xlsx."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from openpyxl import load_workbook

@dataclass
class CSArchElement:
    element_id: str = ""
    name: str = ""
    asil_cal: str = ""
    supplier: str = ""
    part_number: str = ""
    certification: str = ""
    sheet: str = ""
    row: int = 0

@dataclass
class ProbedCSArch:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    doc_id: str = ""
    sheet_names: list[str] = field(default_factory=list)
    elements: list[CSArchElement] = field(default_factory=list)
    crypto_items: list[dict] = field(default_factory=list)
    key_mgmt_items: list[dict] = field(default_factory=list)
    comm_channels: int = 0
    access_controls: int = 0
    is_builder_format: bool = False

def _norm(s: Any) -> str:
    if s is None: return ""
    return str(s).strip()

def probe(xlsx_path: str | Path) -> ProbedCSArch:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedCSArch(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    p.is_builder_format = "03_CS_Element_Catalog" in wb.sheetnames

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

    # CS Element Catalog
    if "03_CS_Element_Catalog" in wb.sheetnames:
        ws = wb["03_CS_Element_Catalog"]
        for r in range(2, min(ws.max_row + 1, 500)):
            elem_id = _norm(ws.cell(r, 1).value)
            name = _norm(ws.cell(r, 2).value)
            if not (elem_id or name): continue
            elem = CSArchElement(
                element_id=elem_id, name=name,
                asil_cal=_norm(ws.cell(r, 3).value),
                supplier=_norm(ws.cell(r, 4).value),
                part_number=_norm(ws.cell(r, 5).value),
                certification=_norm(ws.cell(r, 6).value),
                sheet="03_CS_Element_Catalog", row=r
            )
            p.elements.append(elem)

    # Cryptographic Inventory
    if "04_Cryptographic_Inventory" in wb.sheetnames:
        ws = wb["04_Cryptographic_Inventory"]
        for r in range(2, min(ws.max_row + 1, 200)):
            alg = _norm(ws.cell(r, 1).value)
            if alg: p.crypto_items.append({"algorithm": alg, "row": r})

    # Key Management
    if "05_Key_Management" in wb.sheetnames:
        ws = wb["05_Key_Management"]
        for r in range(2, min(ws.max_row + 1, 200)):
            key_class = _norm(ws.cell(r, 1).value)
            if key_class: p.key_mgmt_items.append({"class": key_class, "row": r})

    # Secure Communication
    if "07_Secure_Communication" in wb.sheetnames:
        ws = wb["07_Secure_Communication"]
        p.comm_channels = sum(1 for r in range(2, ws.max_row + 1) if _norm(ws.cell(r, 1).value))

    # Access Control
    if "08_Access_Control" in wb.sheetnames:
        ws = wb["08_Access_Control"]
        p.access_controls = sum(1 for r in range(2, ws.max_row + 1) if _norm(ws.cell(r, 1).value))

    return p

if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    print(json.dumps({
        "path": p.path, "title": p.title, "revision": p.revision, "status": p.status,
        "author": p.author, "approver": p.approver, "doc_id": p.doc_id,
        "sheets": p.sheet_names, "n_elements": len(p.elements),
        "n_crypto": len(p.crypto_items), "n_key_mgmt": len(p.key_mgmt_items),
        "comm_channels": p.comm_channels, "access_controls": p.access_controls,
        "is_builder_format": p.is_builder_format
    }, indent=2))
