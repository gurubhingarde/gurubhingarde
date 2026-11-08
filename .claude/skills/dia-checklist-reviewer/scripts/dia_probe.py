"""
DIA content probe — extracts agreement content from dia-builder outputs and others.

Returns a structured ProbedDia dict that downstream check functions consume.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Party:
    id: str = ""
    organization: str = ""
    role: str = ""
    primary_contact: str = ""
    fusa_contact: str = ""


@dataclass
class RACIRow:
    wp_id: str = ""
    work_product: str = ""
    assignments: dict[str, str] = field(default_factory=dict)


@dataclass
class CommunicationChannel:
    channel: str = ""
    cadence: str = ""
    format: str = ""
    owner: str = ""
    escalation: str = ""


@dataclass
class JointReview:
    milestone: str = ""
    participants: str = ""
    schedule: str = ""


@dataclass
class SupplierDeliverable:
    item: str = ""
    format: str = ""
    language: str = ""
    planned_date: str = ""
    acceptance_criteria: str = ""


@dataclass
class ProbedDia:
    path: str = ""
    item: str = ""
    doc_id: str = ""
    revision: str = ""
    parties_list: list[Party] = field(default_factory=list)
    signatories: list[str] = field(default_factory=list)

    scope_in: list[str] = field(default_factory=list)
    scope_out: list[str] = field(default_factory=list)

    raci_matrix: list[RACIRow] = field(default_factory=list)
    communication_channels: list[CommunicationChannel] = field(default_factory=list)
    joint_reviews: list[JointReview] = field(default_factory=list)
    supplier_deliverables: list[SupplierDeliverable] = field(default_factory=list)

    change_management: str = ""
    tool_sharing: str = ""
    confidentiality_ip: str = ""

    sheet_names: list[str] = field(default_factory=list)
    is_dia_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm(s: Any) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _find_header_row(ws, max_search: int = 30) -> tuple[int, dict[str, int]]:
    """Find the header row and return (row_index, header_to_col_map)."""
    # #63: prefer a >=3-cell header; accept a 2-cell header only if no wider row exists,
    # so a two-column tab is located without letting a 2-cell key/value row pre-empt a real header.
    fallback: tuple[int, dict[str, int]] = (0, {})
    for r in range(1, min(ws.max_row, max_search) + 1):
        cells = [(c, _norm(ws.cell(r, c).value)) for c in range(1, ws.max_column + 1)]
        non_empty = [(c, v) for c, v in cells if v]
        if len(non_empty) >= 2:
            if all(len(v) < 60 and not v.startswith("=") for c, v in non_empty):
                header_map = {v.lower(): c for c, v in non_empty}
                if len(non_empty) >= 3:
                    return r, header_map
                if not fallback[0]:
                    fallback = (r, header_map)
    return fallback


def _col_for(header_map: dict[str, int], candidates: list[str]) -> int:
    """Find the first matching column by partial-match of any candidate keyword."""
    for cand in candidates:
        cand_lower = cand.lower()
        for header, col in header_map.items():
            if cand_lower in header:
                return col
    return 0


_NON_PARTY_RACI_HEADERS = ("work product", "wp", "wp_id", "wp id", "id",
                           "iso ref", "iso reference", "ref", "reference",
                           "notes", "comment", "comments")


def _is_non_party_raci_header(header: str) -> bool:
    """True for RACI columns that identify the work product rather than a party.

    Party columns carry organization names; everything else (WP_ID, ISO Ref,
    notes) must be excluded or its text is mistaken for an RACI assignment.
    """
    h = (header or "").strip().lower()
    return h in _NON_PARTY_RACI_HEADERS


def _scan_vertical_scope(ws, p) -> None:
    """Parse a single-column Item Scope tab laid out as vertical sections."""
    bucket = None
    for r in range(1, ws.max_row + 1):
        val = _norm(ws.cell(r, 1).value)
        if not val:
            continue
        low = val.lower().strip(" :")
        if low in ("in scope", "in-scope", "included"):
            bucket = p.scope_in
            continue
        if low in ("out of scope", "out-of-scope", "excluded"):
            bucket = p.scope_out
            continue
        if bucket is None:
            continue
        p_item = val.lstrip("\u2022-*\u2013 ").strip()
        if p_item:
            bucket.append(p_item)


# ---------------------------------------------------------------------------
# Probe orchestrator
# ---------------------------------------------------------------------------

def probe(xlsx_path: str | Path) -> ProbedDia:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedDia(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect dia-builder format
    expected_tabs = ["00_Title_Page", "03_Item_Scope", "04_RACI_Matrix"]
    p.is_dia_builder_format = all(tab in wb.sheetnames for tab in expected_tabs)
    if p.is_dia_builder_format:
        p.detection_notes.append("Detected dia-builder format by expected tab names.")

    # Title page — extract metadata
    title_sheet = "00_Title_Page" if "00_Title_Page" in wb.sheetnames else None
    if title_sheet and title_sheet in wb.sheetnames:
        ws = wb[title_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                if not label:
                    continue
                value = _norm(ws.cell(r, c + 1).value)
                if not value:
                    continue
                if "item" in label and not p.item:
                    p.item = value
                elif "doc id" in label or "document id" in label:
                    p.doc_id = value
                elif "revision" in label and not p.revision:
                    p.revision = value

    # Parties (02_Parties tab)
    if "02_Parties" in wb.sheetnames:
        ws = wb["02_Parties"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "id": _col_for(header_map, ["party id", "id"]),
                "org": _col_for(header_map, ["organization", "org"]),
                "role": _col_for(header_map, ["role"]),
                "primary": _col_for(header_map, ["primary contact", "contact"]),
                "fusa": _col_for(header_map, ["fusa contact", "functional safety contact"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                party_id = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                if not party_id:
                    continue
                p.parties_list.append(Party(
                    id=party_id,
                    organization=_norm(ws.cell(r, cols["org"]).value) if cols["org"] else "",
                    role=_norm(ws.cell(r, cols["role"]).value) if cols["role"] else "",
                    primary_contact=_norm(ws.cell(r, cols["primary"]).value) if cols["primary"] else "",
                    fusa_contact=_norm(ws.cell(r, cols["fusa"]).value) if cols["fusa"] else "",
                ))

    # Item Scope (03_Item_Scope tab)
    if "03_Item_Scope" in wb.sheetnames:
        ws = wb["03_Item_Scope"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            in_col = _col_for(header_map, ["in scope", "in-scope", "included"])
            out_col = _col_for(header_map, ["out of scope", "out-of-scope", "excluded"])
            for r in range(header_row + 1, ws.max_row + 1):
                if in_col:
                    in_val = _norm(ws.cell(r, in_col).value)
                    if in_val:
                        p.scope_in.append(in_val)
                if out_col:
                    out_val = _norm(ws.cell(r, out_col).value)
                    if out_val:
                        p.scope_out.append(out_val)
        if not p.scope_in and not p.scope_out:
            # dia-builder emits a single-column vertical layout: an "In Scope"
            # section heading followed by bullet rows, then "Out of Scope".
            # _find_header_row cannot see that (it needs >=3 populated cells),
            # so fall back to section-marker scanning.
            _scan_vertical_scope(ws, p)

    # RACI Matrix (04_RACI_Matrix tab)
    if "04_RACI_Matrix" in wb.sheetnames:
        ws = wb["04_RACI_Matrix"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            wp_col = _col_for(header_map, ["work product", "wp"])
            for r in range(header_row + 1, ws.max_row + 1):
                wp = _norm(ws.cell(r, wp_col).value) if wp_col else ""
                if not wp:
                    continue
                row_data = RACIRow(work_product=wp)
                for c in range(1, ws.max_column + 1):
                    header = _norm(ws.cell(header_row, c).value).lower()
                    val = _norm(ws.cell(r, c).value)
                    if header and val and not _is_non_party_raci_header(header):
                        row_data.assignments[header] = val
                p.raci_matrix.append(row_data)

    # Communication Protocol (05_Communication_Protocol tab)
    if "05_Communication_Protocol" in wb.sheetnames:
        ws = wb["05_Communication_Protocol"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "channel": _col_for(header_map, ["channel"]),
                "cadence": _col_for(header_map, ["cadence"]),
                "format": _col_for(header_map, ["format"]),
                "owner": _col_for(header_map, ["owner"]),
                "escalation": _col_for(header_map, ["escalation"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                ch = _norm(ws.cell(r, cols["channel"]).value) if cols["channel"] else ""
                if not ch:
                    continue
                p.communication_channels.append(CommunicationChannel(
                    channel=ch,
                    cadence=_norm(ws.cell(r, cols["cadence"]).value) if cols["cadence"] else "",
                    format=_norm(ws.cell(r, cols["format"]).value) if cols["format"] else "",
                    owner=_norm(ws.cell(r, cols["owner"]).value) if cols["owner"] else "",
                    escalation=_norm(ws.cell(r, cols["escalation"]).value) if cols["escalation"] else "",
                ))

    # Joint Reviews (06_Joint_Reviews tab)
    if "06_Joint_Reviews" in wb.sheetnames:
        ws = wb["06_Joint_Reviews"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "milestone": _col_for(header_map, ["milestone", "review name", "review"]),
                "participants": _col_for(header_map, ["participants", "attendees"]),
                "schedule": _col_for(header_map, ["schedule", "planned date", "date"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                ms = _norm(ws.cell(r, cols["milestone"]).value) if cols["milestone"] else ""
                if not ms:
                    continue
                p.joint_reviews.append(JointReview(
                    milestone=ms,
                    participants=_norm(ws.cell(r, cols["participants"]).value) if cols["participants"] else "",
                    schedule=_norm(ws.cell(r, cols["schedule"]).value) if cols["schedule"] else "",
                ))

    # Supplier Deliverables (07_Supplier_Deliverables tab)
    if "07_Supplier_Deliverables" in wb.sheetnames:
        ws = wb["07_Supplier_Deliverables"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "item": _col_for(header_map, ["item", "deliverable"]),
                "format": _col_for(header_map, ["format"]),
                "language": _col_for(header_map, ["language"]),
                "date": _col_for(header_map, ["planned date", "date"]),
                "criteria": _col_for(header_map, ["acceptance criteria", "criteria"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                item = _norm(ws.cell(r, cols["item"]).value) if cols["item"] else ""
                if not item:
                    continue
                p.supplier_deliverables.append(SupplierDeliverable(
                    item=item,
                    format=_norm(ws.cell(r, cols["format"]).value) if cols["format"] else "",
                    language=_norm(ws.cell(r, cols["language"]).value) if cols["language"] else "",
                    planned_date=_norm(ws.cell(r, cols["date"]).value) if cols["date"] else "",
                    acceptance_criteria=_norm(ws.cell(r, cols["criteria"]).value) if cols["criteria"] else "",
                ))

    # Change Management (08_Change_Management tab) — grab text content
    if "08_Change_Management" in wb.sheetnames:
        ws = wb["08_Change_Management"]
        content = []
        for r in range(1, min(ws.max_row + 1, 50)):
            for c in range(1, min(ws.max_column + 1, 5)):
                val = _norm(ws.cell(r, c).value)
                if val and len(val) > 3:
                    content.append(val)
        p.change_management = " | ".join(content[:10])

    # Tool Sharing (09_Tool_Sharing tab)
    if "09_Tool_Sharing" in wb.sheetnames:
        ws = wb["09_Tool_Sharing"]
        content = []
        for r in range(1, min(ws.max_row + 1, 50)):
            for c in range(1, min(ws.max_column + 1, 5)):
                val = _norm(ws.cell(r, c).value)
                if val and len(val) > 3:
                    content.append(val)
        p.tool_sharing = " | ".join(content[:10])

    # Confidentiality / IP (10_Confidentiality_IP tab)
    if "10_Confidentiality_IP" in wb.sheetnames:
        ws = wb["10_Confidentiality_IP"]
        content = []
        for r in range(1, min(ws.max_row + 1, 50)):
            for c in range(1, min(ws.max_column + 1, 5)):
                val = _norm(ws.cell(r, c).value)
                if val and len(val) > 3:
                    content.append(val)
        p.confidentiality_ip = " | ".join(content[:10])

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "is_dia_builder_format": p.is_dia_builder_format,
        "item": p.item,
        "doc_id": p.doc_id,
        "revision": p.revision,
        "sheets": p.sheet_names,
        "n_parties": len(p.parties_list),
        "n_raci_rows": len(p.raci_matrix),
        "n_communication_channels": len(p.communication_channels),
        "n_joint_reviews": len(p.joint_reviews),
        "n_supplier_deliverables": len(p.supplier_deliverables),
        "detection_notes": p.detection_notes,
    }
    print(json.dumps(summary, indent=2))
