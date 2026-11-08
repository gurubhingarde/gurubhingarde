"""FSC content probe — extracts FSRs, ASIL allocations, decompositions, safety mechanisms from FSC xlsx."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class FSR:
    fsr_id: str = ""
    sg_id: str = ""
    asil_inherited: str = ""
    branch: str = ""              # Input failure / Process failure / Output failure
    be_code: str = ""
    node_ref: str = ""
    node_id: str = ""
    fsr_text: str = ""
    ftti_ms: Any = None
    sheet: str = ""
    row: int = 0


@dataclass
class ASILAllocation:
    sg_id: str = ""
    node_id: str = ""
    node_name: str = ""
    branch: str = ""
    inherited_asil: str = ""
    decomposition: str = ""
    resulting_asil: str = ""
    independence_evidence: str = ""


@dataclass
class BlockNode:
    id: str = ""
    name: str = ""
    type: str = ""
    branch: str = ""
    asil_relevant: bool = True
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    redundancy_group: str = ""
    shared_resources: list[str] = field(default_factory=list)


@dataclass
class SafetyGoal:
    sg_id: str = ""
    function: str = ""
    hazard: str = ""
    asil: str = ""
    sg_text: str = ""
    safe_state: str = ""


@dataclass
class FTAEntry:
    sg_id: str = ""
    level: int = 0
    gate: str = ""
    code: str = ""
    description: str = ""
    node_id: str = ""


@dataclass
class ProbedFSC:
    path: str = ""
    item_meta: dict[str, str] = field(default_factory=dict)
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""
    linked_hara: str = ""

    sheet_names: list[str] = field(default_factory=list)
    likely_sg_sheet: str = ""
    likely_block_sheet: str = ""
    likely_fta_sheet: str = ""
    likely_fsr_sheet: str = ""
    likely_alloc_sheet: str = ""
    likely_verification_sheet: str = ""
    likely_tsc_handoff_sheet: str = ""
    likely_doc_control_sheet: str = ""

    revision_history_rows: int = 0
    has_table_of_contents: bool = False

    safety_goals: list[SafetyGoal] = field(default_factory=list)
    nodes: list[BlockNode] = field(default_factory=list)
    fsrs: list[FSR] = field(default_factory=list)
    allocations: list[ASILAllocation] = field(default_factory=list)
    fta_entries: list[FTAEntry] = field(default_factory=list)

    is_fsc_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


# Known sheet names from fsc-builder
FSC_BUILDER_TABS = {
    "title": "00_Title_Page",
    "doc_control": "01_Document_Control",
    "sgs": "02_SGs_From_HARA",
    "block_diagram": "03_System_Block_Diagram",
    "fta": "04_FTA_Combined",
    "fta_diagrams": "04b_FTA_Diagrams",
    "fsrs": "05_FSR_Catalog",
    "alloc": "06_ASIL_Allocation",
    "verification": "07_Verification_Matrix",
    "tsc_handoff": "08_TSC_Handoff",
}


def _norm(s: Any) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _find_sheet(names: list[str], keywords: list[str]) -> str:
    for n in names:
        if any(k.lower() in n.lower() for k in keywords):
            return n
    return ""


def _find_header(ws, max_search: int = 30) -> tuple[int, dict[str, int]]:
    for r in range(1, min(ws.max_row, max_search) + 1):
        cells = [(c, _norm(ws.cell(r, c).value)) for c in range(1, ws.max_column + 1)]
        non_empty = [(c, v) for c, v in cells if v]
        if len(non_empty) >= 3:
            if all(len(v) < 60 for _, v in non_empty):
                return r, {v.lower(): c for c, v in non_empty}
    return 0, {}


def _col(headers: dict[str, int], candidates: list[str]) -> int:
    for cand in candidates:
        for h, col in headers.items():
            if cand.lower() in h:
                return col
    return 0


# ---------------------------------------------------------------------------
# Probe
# ---------------------------------------------------------------------------

def probe(xlsx_path: str | Path) -> ProbedFSC:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedFSC(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    p.is_fsc_builder_format = (
        FSC_BUILDER_TABS["fsrs"] in wb.sheetnames and
        FSC_BUILDER_TABS["alloc"] in wb.sheetnames
    )
    if p.is_fsc_builder_format:
        p.detection_notes.append("Detected fsc-builder format by tab names.")
        p.likely_sg_sheet = FSC_BUILDER_TABS["sgs"]
        p.likely_block_sheet = FSC_BUILDER_TABS["block_diagram"]
        p.likely_fta_sheet = FSC_BUILDER_TABS["fta"]
        p.likely_fsr_sheet = FSC_BUILDER_TABS["fsrs"]
        p.likely_alloc_sheet = FSC_BUILDER_TABS["alloc"]
        p.likely_verification_sheet = FSC_BUILDER_TABS["verification"]
        p.likely_tsc_handoff_sheet = FSC_BUILDER_TABS["tsc_handoff"]
        p.likely_doc_control_sheet = FSC_BUILDER_TABS["doc_control"]
    else:
        p.likely_sg_sheet = _find_sheet(p.sheet_names, ["safety goal", "sg"])
        p.likely_block_sheet = _find_sheet(p.sheet_names, ["block diagram", "architecture", "system"])
        p.likely_fta_sheet = _find_sheet(p.sheet_names, ["fta", "fault tree"])
        p.likely_fsr_sheet = _find_sheet(p.sheet_names, ["fsr", "functional safety req"])
        p.likely_alloc_sheet = _find_sheet(p.sheet_names, ["asil allocation", "allocation"])
        p.likely_verification_sheet = _find_sheet(p.sheet_names, ["verification"])
        p.likely_tsc_handoff_sheet = _find_sheet(p.sheet_names, ["tsc", "handoff", "hand-off"])
        p.likely_doc_control_sheet = _find_sheet(p.sheet_names, ["doc control", "document control", "revision"])

    # Title metadata
    title_sheet = "00_Title_Page" if "00_Title_Page" in wb.sheetnames else _find_sheet(p.sheet_names, ["title"])
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
                if "project" in label and not p.project:
                    p.project = value
                elif "fsc document id" in label or "document id" in label or "doc id" in label:
                    p.doc_id = value
                elif "revision" in label and not p.revision:
                    p.revision = value
                elif "status" in label and not p.status:
                    p.status = value
                elif "author" in label and not p.author:
                    p.author = value
                elif "approver" in label and not p.approver:
                    p.approver = value
                elif "linked hara" in label and not p.linked_hara:
                    p.linked_hara = value
                elif "title" == label and not p.title:
                    p.title = value
                p.item_meta[label] = value
        for r in range(1, min(ws.max_row + 1, 5)):
            for c in range(1, min(ws.max_column + 1, 4)):
                v = _norm(ws.cell(r, c).value)
                if v and len(v) > 10 and "concept" in v.lower() and not p.title:
                    p.title = v
                    break

    # Doc control / revision history
    if p.likely_doc_control_sheet and p.likely_doc_control_sheet in wb.sheetnames:
        ws = wb[p.likely_doc_control_sheet]
        hr, hm = _find_header(ws)
        if hr:
            rev_col = _col(hm, ["revision"])
            if rev_col:
                count = 0
                for r in range(hr + 1, ws.max_row + 1):
                    if _norm(ws.cell(r, rev_col).value):
                        count += 1
                p.revision_history_rows = count

    p.has_table_of_contents = any(
        any(k in s.lower() for k in ["title", "content", "toc", "general info"])
        for s in p.sheet_names[:3]
    )

    # Safety goals (imported from HARA)
    if p.likely_sg_sheet and p.likely_sg_sheet in wb.sheetnames:
        ws = wb[p.likely_sg_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "sg_id": _col(hm, ["sg_id", "sg id", "id"]),
                "function": _col(hm, ["function"]),
                "hazard": _col(hm, ["hazard"]),
                "asil": _col(hm, ["asil"]),
                "sg_text": _col(hm, ["safety goal", "sg text"]),
                "safe": _col(hm, ["safe state"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                sg_id = _norm(ws.cell(r, cols["sg_id"]).value) if cols["sg_id"] else ""
                if not sg_id or not sg_id.upper().startswith("SG"):
                    continue
                p.safety_goals.append(SafetyGoal(
                    sg_id=sg_id,
                    function=_norm(ws.cell(r, cols["function"]).value) if cols["function"] else "",
                    hazard=_norm(ws.cell(r, cols["hazard"]).value) if cols["hazard"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    sg_text=_norm(ws.cell(r, cols["sg_text"]).value) if cols["sg_text"] else "",
                    safe_state=_norm(ws.cell(r, cols["safe"]).value) if cols["safe"] else "",
                ))

    # Block diagram nodes
    if p.likely_block_sheet and p.likely_block_sheet in wb.sheetnames:
        ws = wb[p.likely_block_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "id": _col(hm, ["node id", "id"]),
                "name": _col(hm, ["name"]),
                "type": _col(hm, ["type"]),
                "branch": _col(hm, ["branch", "fta branch"]),
                "asil_rel": _col(hm, ["asil-relevant", "asil relevant"]),
                "inputs": _col(hm, ["inputs"]),
                "outputs": _col(hm, ["outputs"]),
                "redundancy": _col(hm, ["redundancy"]),
                "shared": _col(hm, ["shared"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                nid = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                if not nid or not nid.startswith("N"):
                    continue
                p.nodes.append(BlockNode(
                    id=nid,
                    name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                    type=_norm(ws.cell(r, cols["type"]).value) if cols["type"] else "",
                    branch=_norm(ws.cell(r, cols["branch"]).value) if cols["branch"] else "",
                    asil_relevant=(_norm(ws.cell(r, cols["asil_rel"]).value) or "Yes").lower() == "yes" if cols["asil_rel"] else True,
                    inputs=[s.strip() for s in (_norm(ws.cell(r, cols["inputs"]).value) if cols["inputs"] else "").split(",") if s.strip()],
                    outputs=[s.strip() for s in (_norm(ws.cell(r, cols["outputs"]).value) if cols["outputs"] else "").split(",") if s.strip()],
                    redundancy_group=_norm(ws.cell(r, cols["redundancy"]).value) if cols["redundancy"] else "",
                    shared_resources=[s.strip() for s in (_norm(ws.cell(r, cols["shared"]).value) if cols["shared"] else "").split(",") if s.strip()],
                ))

    # FSRs
    if p.likely_fsr_sheet and p.likely_fsr_sheet in wb.sheetnames:
        ws = wb[p.likely_fsr_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "fsr_id": _col(hm, ["fsr_id", "fsr id"]),
                "sg_id": _col(hm, ["sg_id", "sg id"]),
                "asil": _col(hm, ["asil"]),
                "branch": _col(hm, ["branch"]),
                "be": _col(hm, ["basic event", "be code"]),
                "node": _col(hm, ["linked node", "node"]),
                "fsr_text": _col(hm, ["functional safety requirement", "fsr text", "requirement"]),
                "ftti": _col(hm, ["ftti"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                fsr_id = _norm(ws.cell(r, cols["fsr_id"]).value) if cols["fsr_id"] else ""
                if not fsr_id or not fsr_id.upper().startswith("FSR"):
                    continue
                node_ref = _norm(ws.cell(r, cols["node"]).value) if cols["node"] else ""
                node_id = node_ref.split(" — ")[0].strip() if " — " in node_ref else node_ref
                ftti_val = ws.cell(r, cols["ftti"]).value if cols["ftti"] else None
                p.fsrs.append(FSR(
                    fsr_id=fsr_id,
                    sg_id=_norm(ws.cell(r, cols["sg_id"]).value) if cols["sg_id"] else "",
                    asil_inherited=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    branch=_norm(ws.cell(r, cols["branch"]).value) if cols["branch"] else "",
                    be_code=_norm(ws.cell(r, cols["be"]).value) if cols["be"] else "",
                    node_ref=node_ref,
                    node_id=node_id,
                    fsr_text=_norm(ws.cell(r, cols["fsr_text"]).value) if cols["fsr_text"] else "",
                    ftti_ms=ftti_val,
                    sheet=p.likely_fsr_sheet,
                    row=r,
                ))

    # Allocations
    if p.likely_alloc_sheet and p.likely_alloc_sheet in wb.sheetnames:
        ws = wb[p.likely_alloc_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "sg": _col(hm, ["sg_id", "sg id"]),
                "node_id": _col(hm, ["node id"]),
                "node_name": _col(hm, ["node name"]),
                "branch": _col(hm, ["branch"]),
                "inherited": _col(hm, ["inherited"]),
                "decomp": _col(hm, ["selected decomposition", "decomposition"]),
                "resulting": _col(hm, ["resulting", "per-node"]),
                "evidence": _col(hm, ["independence", "evidence"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                sg_id = _norm(ws.cell(r, cols["sg"]).value) if cols["sg"] else ""
                if not sg_id or not sg_id.upper().startswith("SG"):
                    continue
                p.allocations.append(ASILAllocation(
                    sg_id=sg_id,
                    node_id=_norm(ws.cell(r, cols["node_id"]).value) if cols["node_id"] else "",
                    node_name=_norm(ws.cell(r, cols["node_name"]).value) if cols["node_name"] else "",
                    branch=_norm(ws.cell(r, cols["branch"]).value) if cols["branch"] else "",
                    inherited_asil=_norm(ws.cell(r, cols["inherited"]).value) if cols["inherited"] else "",
                    decomposition=_norm(ws.cell(r, cols["decomp"]).value) if cols["decomp"] else "",
                    resulting_asil=_norm(ws.cell(r, cols["resulting"]).value) if cols["resulting"] else "",
                    independence_evidence=_norm(ws.cell(r, cols["evidence"]).value) if cols["evidence"] else "",
                ))

    # FTA entries
    if p.likely_fta_sheet and p.likely_fta_sheet in wb.sheetnames:
        ws = wb[p.likely_fta_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "sg": _col(hm, ["sg_id", "sg id"]),
                "level": _col(hm, ["level"]),
                "gate": _col(hm, ["gate"]),
                "code": _col(hm, ["event code", "code"]),
                "desc": _col(hm, ["description"]),
                "node": _col(hm, ["linked node", "node"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                sg_id = _norm(ws.cell(r, cols["sg"]).value) if cols["sg"] else ""
                if not sg_id or not sg_id.upper().startswith("SG"):
                    continue
                level_val = ws.cell(r, cols["level"]).value if cols["level"] else None
                try:
                    level_int = int(level_val) if level_val is not None else 0
                except (TypeError, ValueError):
                    level_int = 0
                p.fta_entries.append(FTAEntry(
                    sg_id=sg_id,
                    level=level_int,
                    gate=_norm(ws.cell(r, cols["gate"]).value) if cols["gate"] else "",
                    code=_norm(ws.cell(r, cols["code"]).value) if cols["code"] else "",
                    description=_norm(ws.cell(r, cols["desc"]).value) if cols["desc"] else "",
                    node_id=_norm(ws.cell(r, cols["node"]).value) if cols["node"] else "",
                ))

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    print(json.dumps({
        "path": p.path,
        "is_fsc_builder_format": p.is_fsc_builder_format,
        "title": p.title,
        "doc_id": p.doc_id,
        "revision": p.revision,
        "project": p.project,
        "linked_hara": p.linked_hara,
        "n_safety_goals": len(p.safety_goals),
        "n_nodes": len(p.nodes),
        "n_fsrs": len(p.fsrs),
        "n_allocations": len(p.allocations),
        "n_fta_entries": len(p.fta_entries),
        "decompositions_used": sum(1 for a in p.allocations if a.decomposition and "None" not in a.decomposition),
        "revision_history_rows": p.revision_history_rows,
    }, indent=2))
