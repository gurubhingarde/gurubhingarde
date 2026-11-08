"""TSC content probe — extracts FSRs, TSRs (HW+SW), safety mechanisms, HSI signals, timing, FMEA, DFA."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class FSR:
    fsr_id: str = ""
    sg_id: str = ""
    asil_inherited: str = ""
    branch: str = ""
    node_ref: str = ""
    fsr_text: str = ""
    ftti_ms: Any = None


@dataclass
class TSR:
    tsr_id: str = ""
    fsr_id: str = ""
    asil_allocated: str = ""
    type: str = ""              # HW-TSR or SW-TSR
    mechanism: str = ""
    node_ref: str = ""
    text: str = ""
    verification_method: str = ""


@dataclass
class SafetyMechanism:
    fsr_id: str = ""
    asil: str = ""
    branch: str = ""
    node_ref: str = ""
    mechanism_id: str = ""
    mechanism_name: str = ""
    default_dc: str = ""
    detection_time: str = ""
    selection: str = ""           # [primary] / [alternative]


@dataclass
class HSISignal:
    name: str = ""
    direction: str = ""
    linked_fsr: str = ""
    mechanism: str = ""
    encoding: str = ""
    update_rate: str = ""
    integrity: str = ""
    failure_reaction: str = ""
    asil: str = ""


@dataclass
class TimingRow:
    fsr_id: str = ""
    asil: str = ""
    ftti_ms: Any = None
    fdti_ms: Any = None
    frti_ms: Any = None


@dataclass
class FMEARow:
    element: str = ""
    failure_mode: str = ""
    local_effect: str = ""
    vehicle_effect: str = ""
    linked_sg_fsr: str = ""
    existing_mechanism: str = ""
    dc_target: str = ""


@dataclass
class DFARow:
    pair_label: str = ""
    coupling_factor: str = ""
    coupling_present: str = ""
    mitigation: str = ""
    conclusion: str = ""


@dataclass
class HWComponent:
    id: str = ""
    name: str = ""
    part: str = ""
    allocated_nodes: list[str] = field(default_factory=list)
    power_domain: str = ""
    clock_domain: str = ""


@dataclass
class SWPartition:
    id: str = ""
    name: str = ""
    hosted_on: str = ""
    allocated_nodes: list[str] = field(default_factory=list)
    rtos: str = ""
    asil: str = ""


@dataclass
class ProbedTSC:
    path: str = ""
    item_meta: dict[str, str] = field(default_factory=dict)
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""
    linked_fsc: str = ""

    sheet_names: list[str] = field(default_factory=list)
    likely_fsr_sheet: str = ""
    likely_arch_sheet: str = ""
    likely_mechanism_sheet: str = ""
    likely_tsr_sheet: str = ""
    likely_hsi_sheet: str = ""
    likely_timing_sheet: str = ""
    likely_fmea_sheet: str = ""
    likely_dfa_sheet: str = ""
    likely_verification_sheet: str = ""
    likely_hw_handoff_sheet: str = ""
    likely_sw_handoff_sheet: str = ""
    likely_doc_control_sheet: str = ""

    revision_history_rows: int = 0
    has_table_of_contents: bool = False

    fsrs: list[FSR] = field(default_factory=list)
    tsrs: list[TSR] = field(default_factory=list)
    mechanisms: list[SafetyMechanism] = field(default_factory=list)
    hsi_signals: list[HSISignal] = field(default_factory=list)
    timing_rows: list[TimingRow] = field(default_factory=list)
    fmea_rows: list[FMEARow] = field(default_factory=list)
    dfa_rows: list[DFARow] = field(default_factory=list)
    hw_components: list[HWComponent] = field(default_factory=list)
    sw_partitions: list[SWPartition] = field(default_factory=list)

    is_tsc_builder_format: bool = False
    detection_notes: list[str] = field(default_factory=list)


TSC_BUILDER_TABS = {
    "title": "00_Title_Page",
    "doc_control": "01_Document_Control",
    "fsrs": "02_FSRs_From_FSC",
    "arch": "03_System_Architecture",
    "mechanism": "04_Safety_Mechanism_Catalog",
    "tsr": "05_TSR_Catalog",
    "hsi": "06_HSI_Specification",
    "timing": "07_Timing_Budget",
    "fmea": "08_System_FMEA",
    "dfa": "09_DFA",
    "verification": "10_Verification",
    "hw_handoff": "11_HW_Handoff",
    "sw_handoff": "12_SW_Handoff",
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
        if len(non_empty) >= 3 and all(len(v) < 60 for _, v in non_empty):
            return r, {v.lower(): c for c, v in non_empty}
    return 0, {}


def _col(headers: dict[str, int], candidates: list[str]) -> int:
    for cand in candidates:
        for h, col in headers.items():
            if cand.lower() in h:
                return col
    return 0


def probe(xlsx_path: str | Path) -> ProbedTSC:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedTSC(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    p.is_tsc_builder_format = (
        TSC_BUILDER_TABS["tsr"] in wb.sheetnames and
        TSC_BUILDER_TABS["mechanism"] in wb.sheetnames
    )
    if p.is_tsc_builder_format:
        p.detection_notes.append("Detected tsc-builder format by tab names.")
        for key, val in TSC_BUILDER_TABS.items():
            setattr(p, f"likely_{ {'doc_control':'doc_control_sheet','fsrs':'fsr_sheet','arch':'arch_sheet','mechanism':'mechanism_sheet','tsr':'tsr_sheet','hsi':'hsi_sheet','timing':'timing_sheet','fmea':'fmea_sheet','dfa':'dfa_sheet','verification':'verification_sheet','hw_handoff':'hw_handoff_sheet','sw_handoff':'sw_handoff_sheet','title':'_dummy'}[key]}", val)
    else:
        p.likely_fsr_sheet = _find_sheet(p.sheet_names, ["fsr"])
        p.likely_arch_sheet = _find_sheet(p.sheet_names, ["architecture", "system arch"])
        p.likely_mechanism_sheet = _find_sheet(p.sheet_names, ["mechanism", "safety mech"])
        p.likely_tsr_sheet = _find_sheet(p.sheet_names, ["tsr", "technical safety req"])
        p.likely_hsi_sheet = _find_sheet(p.sheet_names, ["hsi", "interface"])
        p.likely_timing_sheet = _find_sheet(p.sheet_names, ["timing", "ftti"])
        p.likely_fmea_sheet = _find_sheet(p.sheet_names, ["fmea"])
        p.likely_dfa_sheet = _find_sheet(p.sheet_names, ["dfa", "dependent failure"])
        p.likely_verification_sheet = _find_sheet(p.sheet_names, ["verification"])
        p.likely_hw_handoff_sheet = _find_sheet(p.sheet_names, ["hw hand", "hw_hand"])
        p.likely_sw_handoff_sheet = _find_sheet(p.sheet_names, ["sw hand", "sw_hand"])
        p.likely_doc_control_sheet = _find_sheet(p.sheet_names, ["doc control", "document control"])

    # Title
    title_sheet = TSC_BUILDER_TABS["title"] if TSC_BUILDER_TABS["title"] in wb.sheetnames else _find_sheet(p.sheet_names, ["title"])
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
                elif "tsc document id" in label or "document id" in label or "doc id" in label:
                    p.doc_id = value
                elif "revision" in label and not p.revision:
                    p.revision = value
                elif "status" in label and not p.status:
                    p.status = value
                elif "author" in label and not p.author:
                    p.author = value
                elif "approver" in label and not p.approver:
                    p.approver = value
                elif "linked fsc" in label and not p.linked_fsc:
                    p.linked_fsc = value
                elif label == "title" and not p.title:
                    p.title = value
                p.item_meta[label] = value
        for r in range(1, 5):
            for c in range(1, 4):
                v = _norm(ws.cell(r, c).value)
                if v and "technical safety concept" in v.lower() and not p.title:
                    p.title = v
                    break

    # Doc control
    if p.likely_doc_control_sheet and p.likely_doc_control_sheet in wb.sheetnames:
        ws = wb[p.likely_doc_control_sheet]
        hr, hm = _find_header(ws)
        if hr:
            rev_col = _col(hm, ["revision"])
            if rev_col:
                p.revision_history_rows = sum(1 for r in range(hr + 1, ws.max_row + 1) if _norm(ws.cell(r, rev_col).value))

    p.has_table_of_contents = any(any(k in s.lower() for k in ["title", "content", "toc", "general"]) for s in p.sheet_names[:3])

    # FSRs
    if p.likely_fsr_sheet and p.likely_fsr_sheet in wb.sheetnames:
        ws = wb[p.likely_fsr_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "fsr": _col(hm, ["fsr_id", "fsr id"]),
                "sg": _col(hm, ["sg_id", "sg id"]),
                "asil": _col(hm, ["asil"]),
                "branch": _col(hm, ["branch"]),
                "node": _col(hm, ["linked node", "node"]),
                "text": _col(hm, ["functional safety requirement", "fsr text", "requirement"]),
                "ftti": _col(hm, ["ftti"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                fsr_id = _norm(ws.cell(r, cols["fsr"]).value) if cols["fsr"] else ""
                if not fsr_id or not fsr_id.upper().startswith("FSR"):
                    continue
                p.fsrs.append(FSR(
                    fsr_id=fsr_id,
                    sg_id=_norm(ws.cell(r, cols["sg"]).value) if cols["sg"] else "",
                    asil_inherited=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    branch=_norm(ws.cell(r, cols["branch"]).value) if cols["branch"] else "",
                    node_ref=_norm(ws.cell(r, cols["node"]).value) if cols["node"] else "",
                    fsr_text=_norm(ws.cell(r, cols["text"]).value) if cols["text"] else "",
                    ftti_ms=ws.cell(r, cols["ftti"]).value if cols["ftti"] else None,
                ))

    # TSRs
    if p.likely_tsr_sheet and p.likely_tsr_sheet in wb.sheetnames:
        ws = wb[p.likely_tsr_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "tsr": _col(hm, ["tsr_id", "tsr id"]),
                "fsr": _col(hm, ["fsr_id", "fsr id"]),
                "asil": _col(hm, ["allocated asil", "asil"]),
                "type": _col(hm, ["type"]),
                "mechanism": _col(hm, ["mechanism"]),
                "node": _col(hm, ["linked node", "node"]),
                "text": _col(hm, ["technical safety requirement", "tsr text", "requirement"]),
                "ver": _col(hm, ["verification method"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                tsr_id = _norm(ws.cell(r, cols["tsr"]).value) if cols["tsr"] else ""
                if not tsr_id or not tsr_id.upper().startswith("TSR"):
                    continue
                p.tsrs.append(TSR(
                    tsr_id=tsr_id,
                    fsr_id=_norm(ws.cell(r, cols["fsr"]).value) if cols["fsr"] else "",
                    asil_allocated=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    type=_norm(ws.cell(r, cols["type"]).value) if cols["type"] else "",
                    mechanism=_norm(ws.cell(r, cols["mechanism"]).value) if cols["mechanism"] else "",
                    node_ref=_norm(ws.cell(r, cols["node"]).value) if cols["node"] else "",
                    text=_norm(ws.cell(r, cols["text"]).value) if cols["text"] else "",
                    verification_method=_norm(ws.cell(r, cols["ver"]).value) if cols["ver"] else "",
                ))

    # Safety mechanisms
    if p.likely_mechanism_sheet and p.likely_mechanism_sheet in wb.sheetnames:
        ws = wb[p.likely_mechanism_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "fsr": _col(hm, ["fsr_id", "fsr id"]),
                "asil": _col(hm, ["allocated asil", "asil"]),
                "branch": _col(hm, ["branch"]),
                "node": _col(hm, ["linked node", "node"]),
                "mid": _col(hm, ["mechanism id"]),
                "mname": _col(hm, ["mechanism name"]),
                "dc": _col(hm, ["dc"]),
                "dt": _col(hm, ["detection time"]),
                "sel": _col(hm, ["selection"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                mid = _norm(ws.cell(r, cols["mid"]).value) if cols["mid"] else ""
                if not mid:
                    continue
                p.mechanisms.append(SafetyMechanism(
                    fsr_id=_norm(ws.cell(r, cols["fsr"]).value) if cols["fsr"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    branch=_norm(ws.cell(r, cols["branch"]).value) if cols["branch"] else "",
                    node_ref=_norm(ws.cell(r, cols["node"]).value) if cols["node"] else "",
                    mechanism_id=mid,
                    mechanism_name=_norm(ws.cell(r, cols["mname"]).value) if cols["mname"] else "",
                    default_dc=_norm(ws.cell(r, cols["dc"]).value) if cols["dc"] else "",
                    detection_time=_norm(ws.cell(r, cols["dt"]).value) if cols["dt"] else "",
                    selection=_norm(ws.cell(r, cols["sel"]).value) if cols["sel"] else "",
                ))

    # HSI
    if p.likely_hsi_sheet and p.likely_hsi_sheet in wb.sheetnames:
        ws = wb[p.likely_hsi_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "name": _col(hm, ["hsi signal", "signal"]),
                "dir": _col(hm, ["direction"]),
                "fsr": _col(hm, ["linked fsr", "fsr"]),
                "mech": _col(hm, ["mechanism"]),
                "enc": _col(hm, ["encoding"]),
                "rate": _col(hm, ["update rate"]),
                "int": _col(hm, ["integrity"]),
                "react": _col(hm, ["failure reaction"]),
                "asil": _col(hm, ["allocated asil", "asil"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                name = _norm(ws.cell(r, cols["name"]).value) if cols["name"] else ""
                if not name or "esc" not in name.lower() and "diag" not in name.lower() and "live" not in name.lower():
                    continue
                p.hsi_signals.append(HSISignal(
                    name=name,
                    direction=_norm(ws.cell(r, cols["dir"]).value) if cols["dir"] else "",
                    linked_fsr=_norm(ws.cell(r, cols["fsr"]).value) if cols["fsr"] else "",
                    mechanism=_norm(ws.cell(r, cols["mech"]).value) if cols["mech"] else "",
                    encoding=_norm(ws.cell(r, cols["enc"]).value) if cols["enc"] else "",
                    update_rate=_norm(ws.cell(r, cols["rate"]).value) if cols["rate"] else "",
                    integrity=_norm(ws.cell(r, cols["int"]).value) if cols["int"] else "",
                    failure_reaction=_norm(ws.cell(r, cols["react"]).value) if cols["react"] else "",
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                ))

    # Timing
    if p.likely_timing_sheet and p.likely_timing_sheet in wb.sheetnames:
        ws = wb[p.likely_timing_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "fsr": _col(hm, ["fsr_id", "fsr id"]),
                "asil": _col(hm, ["allocated asil", "asil"]),
                "ftti": _col(hm, ["ftti"]),
                "fdti": _col(hm, ["fdti"]),
                "frti": _col(hm, ["frti"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                fsr_id = _norm(ws.cell(r, cols["fsr"]).value) if cols["fsr"] else ""
                if not fsr_id or not fsr_id.upper().startswith("FSR"):
                    continue
                p.timing_rows.append(TimingRow(
                    fsr_id=fsr_id,
                    asil=_norm(ws.cell(r, cols["asil"]).value) if cols["asil"] else "",
                    ftti_ms=ws.cell(r, cols["ftti"]).value if cols["ftti"] else None,
                    fdti_ms=ws.cell(r, cols["fdti"]).value if cols["fdti"] else None,
                    frti_ms=ws.cell(r, cols["frti"]).value if cols["frti"] else None,
                ))

    # FMEA
    if p.likely_fmea_sheet and p.likely_fmea_sheet in wb.sheetnames:
        ws = wb[p.likely_fmea_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "elem": _col(hm, ["element", "node"]),
                "fm": _col(hm, ["failure mode"]),
                "local": _col(hm, ["local effect"]),
                "vehicle": _col(hm, ["vehicle effect"]),
                "linked": _col(hm, ["linked sg", "sg"]),
                "mech": _col(hm, ["existing mechanism", "mechanism"]),
                "dc": _col(hm, ["dc"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                elem = _norm(ws.cell(r, cols["elem"]).value) if cols["elem"] else ""
                fm = _norm(ws.cell(r, cols["fm"]).value) if cols["fm"] else ""
                if not (elem and fm):
                    continue
                p.fmea_rows.append(FMEARow(
                    element=elem,
                    failure_mode=fm,
                    local_effect=_norm(ws.cell(r, cols["local"]).value) if cols["local"] else "",
                    vehicle_effect=_norm(ws.cell(r, cols["vehicle"]).value) if cols["vehicle"] else "",
                    linked_sg_fsr=_norm(ws.cell(r, cols["linked"]).value) if cols["linked"] else "",
                    existing_mechanism=_norm(ws.cell(r, cols["mech"]).value) if cols["mech"] else "",
                    dc_target=_norm(ws.cell(r, cols["dc"]).value) if cols["dc"] else "",
                ))

    # DFA
    if p.likely_dfa_sheet and p.likely_dfa_sheet in wb.sheetnames:
        ws = wb[p.likely_dfa_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "pair": _col(hm, ["decomposition pair", "pair"]),
                "factor": _col(hm, ["coupling factor", "factor"]),
                "present": _col(hm, ["coupling present", "present"]),
                "mit": _col(hm, ["mitigation"]),
                "concl": _col(hm, ["conclusion"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                factor = _norm(ws.cell(r, cols["factor"]).value) if cols["factor"] else ""
                if not factor:
                    continue
                p.dfa_rows.append(DFARow(
                    pair_label=_norm(ws.cell(r, cols["pair"]).value) if cols["pair"] else "",
                    coupling_factor=factor,
                    coupling_present=_norm(ws.cell(r, cols["present"]).value) if cols["present"] else "",
                    mitigation=_norm(ws.cell(r, cols["mit"]).value) if cols["mit"] else "",
                    conclusion=_norm(ws.cell(r, cols["concl"]).value) if cols["concl"] else "",
                ))

    # HW components (architecture tab)
    if p.likely_arch_sheet and p.likely_arch_sheet in wb.sheetnames:
        ws = wb[p.likely_arch_sheet]
        hr, hm = _find_header(ws)
        if hr:
            cols = {
                "id": _col(hm, ["hw component id", "component id", "id"]),
                "name": _col(hm, ["name"]),
                "part": _col(hm, ["part"]),
                "alloc": _col(hm, ["allocated nodes"]),
                "power": _col(hm, ["power"]),
                "clock": _col(hm, ["clock"]),
            }
            for r in range(hr + 1, ws.max_row + 1):
                hid = _norm(ws.cell(r, cols["id"]).value) if cols["id"] else ""
                if hid.startswith("HW"):
                    p.hw_components.append(HWComponent(
                        id=hid,
                        name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                        part=_norm(ws.cell(r, cols["part"]).value) if cols["part"] else "",
                        allocated_nodes=[s.strip() for s in (_norm(ws.cell(r, cols["alloc"]).value) if cols["alloc"] else "").split(",") if s.strip()],
                        power_domain=_norm(ws.cell(r, cols["power"]).value) if cols["power"] else "",
                        clock_domain=_norm(ws.cell(r, cols["clock"]).value) if cols["clock"] else "",
                    ))
                elif hid.startswith("SP"):
                    p.sw_partitions.append(SWPartition(
                        id=hid,
                        name=_norm(ws.cell(r, cols["name"]).value) if cols["name"] else "",
                        hosted_on=_norm(ws.cell(r, cols["part"]).value) if cols["part"] else "",
                        allocated_nodes=[s.strip() for s in (_norm(ws.cell(r, cols["alloc"]).value) if cols["alloc"] else "").split(",") if s.strip()],
                        rtos=_norm(ws.cell(r, cols["power"]).value) if cols["power"] else "",
                        asil=_norm(ws.cell(r, cols["clock"]).value) if cols["clock"] else "",
                    ))

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    print(json.dumps({
        "path": p.path,
        "is_tsc_builder_format": p.is_tsc_builder_format,
        "title": p.title,
        "doc_id": p.doc_id,
        "revision": p.revision,
        "project": p.project,
        "linked_fsc": p.linked_fsc,
        "n_fsrs": len(p.fsrs),
        "n_tsrs": len(p.tsrs),
        "n_mechanisms": len(p.mechanisms),
        "n_hsi_signals": len(p.hsi_signals),
        "n_timing_rows": len(p.timing_rows),
        "n_fmea_rows": len(p.fmea_rows),
        "n_dfa_rows": len(p.dfa_rows),
        "n_hw_components": len(p.hw_components),
        "n_sw_partitions": len(p.sw_partitions),
        "revision_history_rows": p.revision_history_rows,
    }, indent=2))
