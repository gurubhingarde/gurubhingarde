"""
Safety Case content probe — extracts structured data from safety-case-builder outputs
and other Safety Case xlsx formats by keyword heuristics.

Probes 14 standard tabs: 00_Title_Page, 01_Document_Control, 02_Executive_Summary,
03_Item_Definition_Reference, 04_Top_Claim, 05_Safety_Goals_Argument,
06_FSR_TSR_Traceability, 07_HW_Metrics_Summary, 08_SW_Verification_Summary,
09_Tool_Qualification, 10_Confirmation_Reviews_Status, 11_Open_Items_Risks,
12_Argument_Diagram_Notes, 13_Assessment_Conclusion, 14_References.

Returns a structured ProbedSafetyCase dict that downstream check functions consume.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SafetyGoalRow:
    sg_id: str = ""
    asil: str = ""
    claim: str = ""
    status: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class FSRRow:
    fsr_id: str = ""
    description: str = ""
    traceability_status: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class HWMetricsRow:
    sg_id: str = ""
    spfm: str = ""
    lfm: str = ""
    pmhf: str = ""
    target: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class ConfirmationReviewRow:
    work_product: str = ""
    reviewer_independence: str = ""
    status: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class OpenItemRow:
    item_id: str = ""
    description: str = ""
    risk_level: str = ""
    accepted: str = ""
    sheet: str = ""
    row: int = 0


@dataclass
class ProbedSafetyCase:
    path: str = ""
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    item_def_ref: str = ""

    sheet_names: list[str] = field(default_factory=list)

    # From Title Page
    top_claim: str = ""
    top_claim_context: str = ""

    # From Safety Goals Argument tab
    safety_goals: list[SafetyGoalRow] = field(default_factory=list)

    # From FSR-TSR Traceability
    fsr_rows: list[FSRRow] = field(default_factory=list)

    # From HW Metrics Summary
    hw_metrics: list[HWMetricsRow] = field(default_factory=list)

    # SW Verification Summary (tab present: Yes/No)
    has_sw_verification: bool = False
    sw_verification_status: str = ""

    # Tool Qualification
    has_tool_qualification: bool = False
    tool_qualification_status: str = ""

    # Confirmation Reviews Status
    confirmation_reviews: list[ConfirmationReviewRow] = field(default_factory=list)

    # Open Items and Risks
    open_items: list[OpenItemRow] = field(default_factory=list)

    # Assessment Conclusion
    assessment_conclusion: str = ""
    has_signoff_block: bool = False

    # References
    references_count: int = 0

    is_safety_case_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _norm(s: Any) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _contains_any(s: str, keywords: list[str]) -> bool:
    s_lower = s.lower()
    return any(k.lower() in s_lower for k in keywords)


def _find_header_row(ws, max_search: int = 30) -> tuple[int, dict[str, int]]:
    """Find the header row by looking for a row with at least 3 non-empty cells."""
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


# ---------------------------------------------------------------------------
# Probe orchestrator
# ---------------------------------------------------------------------------

def probe(xlsx_path: str | Path) -> ProbedSafetyCase:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedSafetyCase(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Detect safety-case-builder format by tab signature
    expected_tabs = [
        "00_Title_Page", "01_Document_Control", "02_Executive_Summary",
        "03_Item_Definition_Reference", "04_Top_Claim", "05_Safety_Goals_Argument",
        "06_FSR_TSR_Traceability", "07_HW_Metrics_Summary", "08_SW_Verification_Summary",
        "09_Tool_Qualification", "10_Confirmation_Reviews_Status", "11_Open_Items_Risks",
        "12_Argument_Diagram_Notes", "13_Assessment_Conclusion", "14_References"
    ]
    p.is_safety_case_builder_format = all(tab in wb.sheetnames for tab in expected_tabs[:5])
    if p.is_safety_case_builder_format:
        p.detection_notes.append("Detected safety-case-builder format by tab names.")

    # Title / metadata from Title Page
    title_sheet = "00_Title_Page" if "00_Title_Page" in wb.sheetnames else None
    if title_sheet:
        ws = wb[title_sheet]
        for r in range(1, min(ws.max_row + 1, 40)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if not label or not value:
                    continue
                if "project" in label and not p.title:
                    p.title = value
                elif "document title" in label and not p.title:
                    p.title = value
                elif "revision" in label and not p.revision:
                    p.revision = value
                elif "status" in label and not p.status:
                    p.status = value
                elif "author" in label and not p.author:
                    p.author = value
                elif "approver" in label and not p.approver:
                    p.approver = value
                elif "item definition" in label and not p.item_def_ref:
                    p.item_def_ref = value
                elif "top claim" in label and not p.top_claim:
                    p.top_claim = value
                    # Next cell might be context
                    if c + 2 <= ws.max_column:
                        p.top_claim_context = _norm(ws.cell(r, c + 2).value)

    # Item Definition Reference
    if "03_Item_Definition_Reference" in wb.sheetnames:
        ws = wb["03_Item_Definition_Reference"]
        for r in range(1, min(ws.max_row + 1, 20)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value)
                if v and len(v) > 5 and "definition" in v.lower():
                    if not p.item_def_ref:
                        p.item_def_ref = v

    # Top Claim from tab 04
    if "04_Top_Claim" in wb.sheetnames and not p.top_claim:
        ws = wb["04_Top_Claim"]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 3)):
                v = _norm(ws.cell(r, c).value)
                if v and len(v) > 10:
                    p.top_claim = v
                    break

    # Safety Goals Argument (tab 05)
    if "05_Safety_Goals_Argument" in wb.sheetnames:
        ws = wb["05_Safety_Goals_Argument"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "sg_id": _col_for(header_map, ["sg_id", "sg id", "id"]),
                "asil": _col_for(header_map, ["asil"]),
                "claim": _col_for(header_map, ["claim", "argument"]),
                "status": _col_for(header_map, ["status"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                sg = SafetyGoalRow(
                    sg_id=_norm(ws.cell(r, cols["sg_id"]).value) if cols["sg_id"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    claim=_norm(ws.cell(r, cols["claim"]).value) if cols["claim"] else "",
                    status=_norm(ws.cell(r, cols["status"]).value) if cols["status"] else "",
                    sheet="05_Safety_Goals_Argument",
                    row=r,
                )
                if sg.sg_id or sg.claim:
                    p.safety_goals.append(sg)

    # FSR-TSR Traceability (tab 06)
    if "06_FSR_TSR_Traceability" in wb.sheetnames:
        ws = wb["06_FSR_TSR_Traceability"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "fsr_id": _col_for(header_map, ["fsr_id", "fsr id", "id"]),
                "description": _col_for(header_map, ["description"]),
                "status": _col_for(header_map, ["status", "traceability"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                fsr = FSRRow(
                    fsr_id=_norm(ws.cell(r, cols["fsr_id"]).value) if cols["fsr_id"] else "",
                    description=_norm(ws.cell(r, cols["description"]).value) if cols["description"] else "",
                    traceability_status=_norm(ws.cell(r, cols["status"]).value) if cols["status"] else "",
                    sheet="06_FSR_TSR_Traceability",
                    row=r,
                )
                if fsr.fsr_id or fsr.description:
                    p.fsr_rows.append(fsr)

    # HW Metrics Summary (tab 07)
    if "07_HW_Metrics_Summary" in wb.sheetnames:
        ws = wb["07_HW_Metrics_Summary"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "sg_id": _col_for(header_map, ["sg_id", "sg id"]),
                "spfm": _col_for(header_map, ["spfm"]),
                "lfm": _col_for(header_map, ["lfm"]),
                "pmhf": _col_for(header_map, ["pmhf"]),
                "target": _col_for(header_map, ["target"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                hw = HWMetricsRow(
                    sg_id=_norm(ws.cell(r, cols["sg_id"]).value) if cols["sg_id"] else "",
                    spfm=_norm(ws.cell(r, cols["spfm"]).value) if cols["spfm"] else "",
                    lfm=_norm(ws.cell(r, cols["lfm"]).value) if cols["lfm"] else "",
                    pmhf=_norm(ws.cell(r, cols["pmhf"]).value) if cols["pmhf"] else "",
                    target=_norm(ws.cell(r, cols["target"]).value) if cols["target"] else "",
                    sheet="07_HW_Metrics_Summary",
                    row=r,
                )
                if hw.sg_id or hw.spfm:
                    p.hw_metrics.append(hw)

    # SW Verification Summary (tab 08)
    if "08_SW_Verification_Summary" in wb.sheetnames:
        p.has_sw_verification = True
        ws = wb["08_SW_Verification_Summary"]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value).lower()
                if "status" in v:
                    p.sw_verification_status = _norm(ws.cell(r, c + 1).value)
                    break

    # Tool Qualification (tab 09)
    if "09_Tool_Qualification" in wb.sheetnames:
        p.has_tool_qualification = True
        ws = wb["09_Tool_Qualification"]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value).lower()
                if "status" in v or "tcl" in v:
                    p.tool_qualification_status = _norm(ws.cell(r, c + 1).value)
                    break

    # Confirmation Reviews Status (tab 10)
    if "10_Confirmation_Reviews_Status" in wb.sheetnames:
        ws = wb["10_Confirmation_Reviews_Status"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "work_product": _col_for(header_map, ["work product", "product"]),
                "independence": _col_for(header_map, ["independence", "i level"]),
                "status": _col_for(header_map, ["status"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                cr = ConfirmationReviewRow(
                    work_product=_norm(ws.cell(r, cols["work_product"]).value) if cols["work_product"] else "",
                    reviewer_independence=_norm(ws.cell(r, cols["independence"]).value) if cols["independence"] else "",
                    status=_norm(ws.cell(r, cols["status"]).value) if cols["status"] else "",
                    sheet="10_Confirmation_Reviews_Status",
                    row=r,
                )
                if cr.work_product or cr.reviewer_independence:
                    p.confirmation_reviews.append(cr)

    # Open Items and Risks (tab 11)
    if "11_Open_Items_Risks" in wb.sheetnames:
        ws = wb["11_Open_Items_Risks"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            cols = {
                "item_id": _col_for(header_map, ["item_id", "id"]),
                "description": _col_for(header_map, ["description"]),
                "risk_level": _col_for(header_map, ["risk level", "risk"]),
                "accepted": _col_for(header_map, ["accepted"]),
            }
            for r in range(header_row + 1, ws.max_row + 1):
                oi = OpenItemRow(
                    item_id=_norm(ws.cell(r, cols["item_id"]).value) if cols["item_id"] else "",
                    description=_norm(ws.cell(r, cols["description"]).value) if cols["description"] else "",
                    risk_level=_norm(ws.cell(r, cols["risk_level"]).value) if cols["risk_level"] else "",
                    accepted=_norm(ws.cell(r, cols["accepted"]).value) if cols["accepted"] else "",
                    sheet="11_Open_Items_Risks",
                    row=r,
                )
                if oi.item_id or oi.description:
                    p.open_items.append(oi)

    # Assessment Conclusion (tab 13)
    if "13_Assessment_Conclusion" in wb.sheetnames:
        ws = wb["13_Assessment_Conclusion"]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value)
                if v and len(v) > 10:
                    p.assessment_conclusion = v
                    break
        # Check for signoff block
        for r in range(1, ws.max_row + 1):
            for c in range(1, ws.max_column + 1):
                v = _norm(ws.cell(r, c).value).lower()
                if any(x in v for x in ["signoff", "approved by", "reviewed by"]):
                    p.has_signoff_block = True
                    break

    # References (tab 14)
    if "14_References" in wb.sheetnames:
        ws = wb["14_References"]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            ref_count = 0
            for r in range(header_row + 1, ws.max_row + 1):
                if any(_norm(ws.cell(r, c).value) for c in range(1, min(ws.max_column + 1, 4))):
                    ref_count += 1
            p.references_count = ref_count

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "is_safety_case_builder_format": p.is_safety_case_builder_format,
        "title": p.title,
        "revision": p.revision,
        "status": p.status,
        "author": p.author,
        "approver": p.approver,
        "item_def_ref": p.item_def_ref,
        "top_claim": p.top_claim,
        "sheets": p.sheet_names,
        "n_safety_goals": len(p.safety_goals),
        "n_fsr_rows": len(p.fsr_rows),
        "n_hw_metrics": len(p.hw_metrics),
        "n_confirmation_reviews": len(p.confirmation_reviews),
        "n_open_items": len(p.open_items),
        "has_sw_verification": p.has_sw_verification,
        "has_tool_qualification": p.has_tool_qualification,
        "has_signoff_block": p.has_signoff_block,
        "references_count": p.references_count,
        "detection_notes": p.detection_notes,
    }
    print(json.dumps(summary, indent=2))
