"""
Triggering Conditions content probe — extracts from triggering-conditions.xlsx
Probes for environmental, sensor, road, system-state, driver-state, combined conditions
"""

from dataclasses import dataclass, field
from pathlib import Path
from openpyxl import load_workbook


def _norm(s) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _find_sheet_by_keywords(sheet_names: list[str], keywords: list[str]) -> str:
    for name in sheet_names:
        s_lower = name.lower()
        if any(k.lower() in s_lower for k in keywords):
            return name
    return ""


@dataclass
class ProbedTriggeringConditions:
    path: str = ""
    sheet_names: list[str] = field(default_factory=list)

    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""

    sotif_analysis_referenced: bool = False

    environmental_conditions_count: int = 0
    sensor_conditions_count: int = 0
    road_conditions_count: int = 0
    road_user_conditions_count: int = 0
    system_state_conditions_count: int = 0
    driver_state_conditions_count: int = 0

    combined_conditions_count: int = 0
    combined_method: str = ""  # Cartesian, pairwise, etc.

    likelihood_estimates: int = 0
    detectability_estimates: int = 0

    mitigation_strategies: int = 0
    high_risk_conditions: int = 0

    iso_21448_references: int = 0
    annex_b_coverage: bool = False

    detection_notes: list[str] = field(default_factory=list)


def probe(xlsx_path: str | Path) -> ProbedTriggeringConditions:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedTriggeringConditions(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Title / metadata
    title_sheet = _find_sheet_by_keywords(p.sheet_names, ["title"])
    if title_sheet and title_sheet in wb.sheetnames:
        ws = wb[title_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value) if c < ws.max_column else ""
                if not label or not value:
                    continue
                if "project" in label and not p.project:
                    p.project = value
                elif "document id" in label or "doc id" in label:
                    p.doc_id = value
                elif "revision" in label and not p.revision:
                    p.revision = value
                elif "status" in label and not p.status:
                    p.status = value
                elif "author" in label and not p.author:
                    p.author = value
                elif "approver" in label and not p.approver:
                    p.approver = value
                elif "title" in label and not p.title:
                    p.title = value

    # SOTIF Analysis reference
    for sheet_name in p.sheet_names:
        if "sotif" in sheet_name.lower() or "analysis" in sheet_name.lower():
            p.sotif_analysis_referenced = True
            break

    # Count triggering conditions by category
    env_sheet = _find_sheet_by_keywords(p.sheet_names, ["environmental", "weather"])
    if env_sheet and env_sheet in wb.sheetnames:
        ws = wb[env_sheet]
        for r in range(2, ws.max_row + 1):
            if _norm(ws.cell(r, 1).value) or _norm(ws.cell(r, 2).value):
                p.environmental_conditions_count += 1

    sensor_sheet = _find_sheet_by_keywords(p.sheet_names, ["sensor"])
    if sensor_sheet and sensor_sheet in wb.sheetnames:
        ws = wb[sensor_sheet]
        for r in range(2, ws.max_row + 1):
            if _norm(ws.cell(r, 1).value) or _norm(ws.cell(r, 2).value):
                p.sensor_conditions_count += 1

    road_sheet = _find_sheet_by_keywords(p.sheet_names, ["road infrastructure", "road"])
    if road_sheet and road_sheet in wb.sheetnames:
        ws = wb[road_sheet]
        for r in range(2, ws.max_row + 1):
            if _norm(ws.cell(r, 1).value) or _norm(ws.cell(r, 2).value):
                p.road_conditions_count += 1

    user_sheet = _find_sheet_by_keywords(p.sheet_names, ["road user", "other road user"])
    if user_sheet and user_sheet in wb.sheetnames:
        ws = wb[user_sheet]
        for r in range(2, ws.max_row + 1):
            if _norm(ws.cell(r, 1).value) or _norm(ws.cell(r, 2).value):
                p.road_user_conditions_count += 1

    sys_sheet = _find_sheet_by_keywords(p.sheet_names, ["system state", "system"])
    if sys_sheet and sys_sheet in wb.sheetnames:
        ws = wb[sys_sheet]
        for r in range(2, ws.max_row + 1):
            if _norm(ws.cell(r, 1).value) or _norm(ws.cell(r, 2).value):
                p.system_state_conditions_count += 1

    driver_sheet = _find_sheet_by_keywords(p.sheet_names, ["driver state", "driver"])
    if driver_sheet and driver_sheet in wb.sheetnames:
        ws = wb[driver_sheet]
        for r in range(2, ws.max_row + 1):
            if _norm(ws.cell(r, 1).value) or _norm(ws.cell(r, 2).value):
                p.driver_state_conditions_count += 1

    # Combined conditions
    combined_sheet = _find_sheet_by_keywords(p.sheet_names, ["combined", "cartesian", "pairwise"])
    if combined_sheet and combined_sheet in wb.sheetnames:
        ws = wb[combined_sheet]
        for r in range(2, ws.max_row + 1):
            if _norm(ws.cell(r, 1).value):
                p.combined_conditions_count += 1
        # Try to detect Cartesian vs pairwise
        header_row_text = " ".join(_norm(ws.cell(1, c).value) for c in range(1, 5)).lower()
        if "cartesian" in header_row_text or "product" in header_row_text:
            p.combined_method = "Cartesian"
        elif "pairwise" in header_row_text:
            p.combined_method = "Pairwise"

    # Likelihood and detectability
    for sheet_name in p.sheet_names:
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            for r in range(1, min(ws.max_row + 1, 50)):
                header_text = " ".join(_norm(ws.cell(r, c).value) for c in range(1, 4)).lower()
                if "likelihood" in header_text or "probability" in header_text:
                    for data_r in range(r + 1, ws.max_row + 1):
                        if _norm(ws.cell(data_r, 2).value):
                            p.likelihood_estimates += 1
                if "detectab" in header_text:
                    for data_r in range(r + 1, ws.max_row + 1):
                        if _norm(ws.cell(data_r, 2).value):
                            p.detectability_estimates += 1

    # Mitigation strategies
    mitigation_sheet = _find_sheet_by_keywords(p.sheet_names, ["mitigation", "strategy"])
    if mitigation_sheet and mitigation_sheet in wb.sheetnames:
        ws = wb[mitigation_sheet]
        for r in range(2, ws.max_row + 1):
            strategy = _norm(ws.cell(r, 2).value)
            if strategy:
                p.mitigation_strategies += 1
                if any(kw in strategy.lower() for kw in ["high", "critical", "severe"]):
                    p.high_risk_conditions += 1

    # ISO 21448 references
    ref_sheet = _find_sheet_by_keywords(p.sheet_names, ["reference", "general info"])
    if ref_sheet and ref_sheet in wb.sheetnames:
        ws = wb[ref_sheet]
        for r in range(1, ws.max_row + 1):
            row_text = " ".join(_norm(ws.cell(r, c).value) for c in range(1, min(ws.max_column + 1, 5))).lower()
            if "iso 21448" in row_text or "annex b" in row_text:
                p.iso_21448_references += 1
                if "annex b" in row_text:
                    p.annex_b_coverage = True

    return p


if __name__ == "__main__":
    import sys
    import json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "title": p.title,
        "sheets": p.sheet_names,
        "sotif_analysis_referenced": p.sotif_analysis_referenced,
        "environmental": p.environmental_conditions_count,
        "sensor": p.sensor_conditions_count,
        "road": p.road_conditions_count,
        "road_user": p.road_user_conditions_count,
        "system_state": p.system_state_conditions_count,
        "driver_state": p.driver_state_conditions_count,
        "combined_count": p.combined_conditions_count,
        "combined_method": p.combined_method,
        "likelihood_estimates": p.likelihood_estimates,
        "detectability_estimates": p.detectability_estimates,
        "mitigation_strategies": p.mitigation_strategies,
        "high_risk_conditions": p.high_risk_conditions,
        "iso_21448_references": p.iso_21448_references,
        "annex_b_coverage": p.annex_b_coverage,
    }
    print(json.dumps(summary, indent=2))
