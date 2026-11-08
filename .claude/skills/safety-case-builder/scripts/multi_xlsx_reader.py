"""
Multi-XLSX reader for safety-case-builder.
Extracts safety goals, FSRs, TSRs, ASIL allocations, and FMEDA metrics from upstream artifacts.

Usage:
    from multi_xlsx_reader import read_all_artifacts
    data = read_all_artifacts(hara_path, fsc_path, tsc_path, fmeda_path=None, ...)
"""

from pathlib import Path
from typing import Optional, Any
from openpyxl import load_workbook


def read_hara(path: str) -> dict:
    """Extract safety goals, hazards, and ASIL from HARA xlsx."""
    wb = load_workbook(path, data_only=True)
    safety_goals = []

    # Try both tab names (hara-builder v1 = 05_Safety_Goals, v2 = 13_Safety_Goals)
    sg_tab = None
    if "13_Safety_Goals" in wb.sheetnames:
        sg_tab = "13_Safety_Goals"
    elif "05_Safety_Goals" in wb.sheetnames:
        sg_tab = "05_Safety_Goals"

    if sg_tab:
        ws = wb[sg_tab]
        for r in range(5, ws.max_row + 1):
            sg_id = ws.cell(r, 1).value
            if not sg_id or not str(sg_id).startswith("SG-"):
                continue
            safety_goals.append({
                "sg_id": str(sg_id),
                "hazard_id": str(ws.cell(r, 2).value or ""),
                "hazard": str(ws.cell(r, 3).value or ""),
                "asil": str(ws.cell(r, 4).value or "QM"),
                "ftti_ms": ws.cell(r, 5).value,
            })

    return {"safety_goals": safety_goals, "hara_path": path}


def read_fsc(path: str) -> dict:
    """Extract FSRs, ASIL allocations, and decomposition from FSC xlsx."""
    wb = load_workbook(path, data_only=True)
    fsrs = []
    allocations = []

    if "05_FSR_Catalog" in wb.sheetnames:
        ws = wb["05_FSR_Catalog"]
        for r in range(5, ws.max_row + 1):
            fsr_id = ws.cell(r, 1).value
            if not fsr_id or not str(fsr_id).startswith("FSR-"):
                continue
            fsrs.append({
                "fsr_id": str(fsr_id),
                "sg_id": str(ws.cell(r, 2).value or ""),
                "asil_inherited": str(ws.cell(r, 3).value or "QM"),
                "branch": str(ws.cell(r, 4).value or ""),
                "fsr_text": str(ws.cell(r, 7).value or ""),
                "ftti_ms": ws.cell(r, 8).value,
            })

    if "06_ASIL_Allocation" in wb.sheetnames:
        ws = wb["06_ASIL_Allocation"]
        for r in range(5, ws.max_row + 1):
            sg_id = ws.cell(r, 1).value
            if not sg_id or not str(sg_id).startswith("SG-"):
                continue
            allocations.append({
                "sg_id": str(sg_id),
                "node_id": str(ws.cell(r, 2).value or ""),
                "node_name": str(ws.cell(r, 3).value or ""),
                "branch": str(ws.cell(r, 4).value or ""),
                "inherited_asil": str(ws.cell(r, 5).value or ""),
                "decomposition": str(ws.cell(r, 7).value or ""),
                "resulting_asil": str(ws.cell(r, 8).value or ""),
            })

    return {"fsrs": fsrs, "allocations": allocations, "fsc_path": path}


def read_tsc(path: str) -> dict:
    """Extract TSRs and mechanisms from TSC xlsx."""
    wb = load_workbook(path, data_only=True)
    tsrs = []
    mechanisms = []

    if "05_TSR_Catalog" in wb.sheetnames:
        ws = wb["05_TSR_Catalog"]
        for r in range(5, ws.max_row + 1):
            tsr_id = ws.cell(r, 1).value
            if not tsr_id or not str(tsr_id).startswith("TSR-"):
                continue
            tsrs.append({
                "tsr_id": str(tsr_id),
                "fsr_id": str(ws.cell(r, 2).value or ""),
                "asil": str(ws.cell(r, 3).value or "QM"),
                "type": str(ws.cell(r, 4).value or ""),
                "mechanism": str(ws.cell(r, 5).value or ""),
                "node": str(ws.cell(r, 6).value or ""),
                "text": str(ws.cell(r, 7).value or ""),
            })

    if "04_Safety_Mechanism_Catalog" in wb.sheetnames:
        ws = wb["04_Safety_Mechanism_Catalog"]
        for r in range(5, ws.max_row + 1):
            mech_id = ws.cell(r, 5).value
            if not mech_id or "[" in str(mech_id):
                continue
            mechanisms.append({
                "fsr_id": str(ws.cell(r, 1).value or ""),
                "mechanism_id": str(mech_id),
                "mechanism_name": str(ws.cell(r, 6).value or ""),
                "default_dc": str(ws.cell(r, 7).value or ""),
            })

    return {"tsrs": tsrs, "mechanisms": mechanisms, "tsc_path": path}


def read_fmeda(path: Optional[str]) -> dict:
    """Extract SPFM, LFM, PMHF metrics from FMEDA xlsx (if provided)."""
    if not path or not Path(path).exists():
        return {"metrics": [], "fmeda_path": None}

    wb = load_workbook(path, data_only=True)
    metrics = []

    # Try to read SPFM from tab 07
    if "07_SPFM_Calculation" in wb.sheetnames:
        ws = wb["07_SPFM_Calculation"]
        for r in range(4, ws.max_row + 1):
            sg_id = ws.cell(r, 1).value
            if not sg_id:
                continue
            metrics.append({
                "sg_id": str(sg_id),
                "spfm": ws.cell(r, 4).value,
                "lfm": ws.cell(r, 4).value if "08_LFM_Calculation" not in wb.sheetnames else None,
                "pmhf": ws.cell(r, 2).value if "09_PMHF_Calculation" not in wb.sheetnames else None,
            })

    return {"metrics": metrics, "fmeda_path": path}


def read_all_artifacts(
    hara_path: str,
    fsc_path: str,
    tsc_path: str,
    fmeda_path: Optional[str] = None,
    sw_safety_reqs_path: Optional[str] = None,
    hw_safety_reqs_path: Optional[str] = None,
) -> dict:
    """Read all upstream artifacts and return consolidated data."""
    hara_data = read_hara(hara_path)
    fsc_data = read_fsc(fsc_path)
    tsc_data = read_tsc(tsc_path)
    fmeda_data = read_fmeda(fmeda_path)

    return {"hara": hara_data, "fsc": fsc_data, "tsc": tsc_data, "fmeda": fmeda_data}
