"""
SOTIF Analysis content probe — extracts structure from sotif-analysis.xlsx
expected tabs: 00_Title_Page through 11_References

Probes for:
- Item Definition reference
- ODD definition (scenery, environment, dynamic elements, driver state)
- Performance limitations per function
- Functional insufficiencies
- Triggering conditions documented
- Hazardous behaviors (function × insufficiency × trigger)
- Scenario quadrant classification
- Acceptance criterion
- Standard references
- Out-of-ODD behavior
"""

from __future__ import annotations

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
class ProbedSotifAnalysis:
    path: str = ""
    sheet_names: list[str] = field(default_factory=list)

    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""

    item_def_referenced: bool = False
    item_def_version: str = ""

    odd_defined: bool = False
    odd_scenery_rows: int = 0
    odd_environment_rows: int = 0
    odd_dynamic_rows: int = 0
    odd_driver_state_rows: int = 0

    functions_with_performance: list[dict] = field(default_factory=list)
    performance_limitations_count: int = 0

    functional_insufficiencies_count: int = 0
    insufficiency_details: list[dict] = field(default_factory=list)

    triggering_conditions_count: int = 0
    triggering_by_category: dict[str, int] = field(default_factory=dict)

    hazardous_behaviors_count: int = 0

    scenario_quadrant_classification: dict[str, int] = field(default_factory=dict)

    acceptance_criteria_count: int = 0
    acceptance_measurable: int = 0

    out_of_odd_defined: bool = False

    iso_21448_references: int = 0
    other_standards: list[str] = field(default_factory=list)

    detection_notes: list[str] = field(default_factory=list)


def probe(xlsx_path: str | Path) -> ProbedSotifAnalysis:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedSotifAnalysis(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Title page / metadata
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

    # ODD Definition — look for dedicated ODD tab or sections
    odd_sheet = _find_sheet_by_keywords(p.sheet_names, ["odd", "operational design domain"])
    if odd_sheet and odd_sheet in wb.sheetnames:
        ws = wb[odd_sheet]
        p.odd_defined = True
        # Count rows that appear to define scenery, environment, dynamics, driver state
        for r in range(2, min(ws.max_row + 1, 100)):
            row_text = " ".join(_norm(ws.cell(r, c).value) for c in range(1, min(ws.max_column + 1, 5))).lower()
            if "scen" in row_text:
                p.odd_scenery_rows += 1
            if "environment" in row_text or "weather" in row_text or "lighting" in row_text:
                p.odd_environment_rows += 1
            if "dynamic" in row_text or "vehicle" in row_text or "road user" in row_text:
                p.odd_dynamic_rows += 1
            if "driver" in row_text or "operator" in row_text:
                p.odd_driver_state_rows += 1

    # Performance limitations
    perf_sheet = _find_sheet_by_keywords(p.sheet_names, ["performance"])
    if perf_sheet and perf_sheet in wb.sheetnames:
        ws = wb[perf_sheet]
        for r in range(2, ws.max_row + 1):
            func_name = _norm(ws.cell(r, 1).value)
            limitation = _norm(ws.cell(r, 2).value)
            if func_name and limitation:
                p.performance_limitations_count += 1
                p.functions_with_performance.append({"function": func_name, "limitation": limitation})

    # Functional insufficiencies
    insufficiency_sheet = _find_sheet_by_keywords(p.sheet_names, ["insufficiency", "insufficient"])
    if insufficiency_sheet and insufficiency_sheet in wb.sheetnames:
        ws = wb[insufficiency_sheet]
        for r in range(2, ws.max_row + 1):
            func = _norm(ws.cell(r, 1).value)
            insuff = _norm(ws.cell(r, 2).value)
            if func and insuff:
                p.functional_insufficiencies_count += 1
                p.insufficiency_details.append({"function": func, "insufficiency": insuff})

    # Triggering conditions — count by category
    trigger_sheet = _find_sheet_by_keywords(p.sheet_names, ["trigger", "triggering condition"])
    if trigger_sheet and trigger_sheet in wb.sheetnames:
        ws = wb[trigger_sheet]
        for r in range(2, ws.max_row + 1):
            category = _norm(ws.cell(r, 1).value)
            if category:
                p.triggering_conditions_count += 1
                cat_key = category.split()[0] if category else "other"
                p.triggering_by_category[cat_key] = p.triggering_by_category.get(cat_key, 0) + 1

    # Hazardous behaviors (function × insufficiency × trigger combinations)
    behavior_sheet = _find_sheet_by_keywords(p.sheet_names, ["hazard", "behavior"])
    if behavior_sheet and behavior_sheet in wb.sheetnames:
        ws = wb[behavior_sheet]
        for r in range(2, ws.max_row + 1):
            if _norm(ws.cell(r, 1).value) or _norm(ws.cell(r, 2).value):
                p.hazardous_behaviors_count += 1

    # Scenario quadrant classification
    scenario_sheet = _find_sheet_by_keywords(p.sheet_names, ["scenario", "quadrant"])
    if scenario_sheet and scenario_sheet in wb.sheetnames:
        ws = wb[scenario_sheet]
        for r in range(2, ws.max_row + 1):
            quad = _norm(ws.cell(r, 2).value)  # Assume column B is quadrant
            if quad:
                p.scenario_quadrant_classification[quad] = p.scenario_quadrant_classification.get(quad, 0) + 1

    # Acceptance criteria
    ac_sheet = _find_sheet_by_keywords(p.sheet_names, ["acceptance"])
    if ac_sheet and ac_sheet in wb.sheetnames:
        ws = wb[ac_sheet]
        for r in range(2, ws.max_row + 1):
            criterion = _norm(ws.cell(r, 2).value)
            measurable = _norm(ws.cell(r, 3).value)
            if criterion:
                p.acceptance_criteria_count += 1
                if measurable and measurable.lower() in ("yes", "y", "measurable", "quantified"):
                    p.acceptance_measurable += 1

    # Out-of-ODD behavior
    if "ODD" in p.sheet_names or odd_sheet:
        for sheet_name in p.sheet_names:
            if "out" in sheet_name.lower() and "odd" in sheet_name.lower():
                p.out_of_odd_defined = True
                break

    # References to ISO 21448 and other standards
    ref_sheet = _find_sheet_by_keywords(p.sheet_names, ["reference", "general info"])
    if ref_sheet and ref_sheet in wb.sheetnames:
        ws = wb[ref_sheet]
        for r in range(1, ws.max_row + 1):
            row_text = " ".join(_norm(ws.cell(r, c).value) for c in range(1, min(ws.max_column + 1, 5))).lower()
            if "iso 21448" in row_text or "sotif" in row_text:
                p.iso_21448_references += 1
            if "iso" in row_text or "standard" in row_text.lower():
                std = _norm(ws.cell(r, 2).value)
                if std and std not in p.other_standards:
                    p.other_standards.append(std)

    # Item definition reference check
    for sheet_name in p.sheet_names:
        if "item definition" in sheet_name.lower() or "id" in sheet_name.lower():
            p.item_def_referenced = True
            break

    if not p.item_def_referenced and ref_sheet:
        ws = wb[ref_sheet]
        for r in range(1, ws.max_row + 1):
            row_text = " ".join(_norm(ws.cell(r, c).value) for c in range(1, 4)).lower()
            if "item definition" in row_text:
                p.item_def_referenced = True
                break

    return p


if __name__ == "__main__":
    import sys
    import json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "title": p.title,
        "doc_id": p.doc_id,
        "revision": p.revision,
        "sheets": p.sheet_names,
        "item_def_referenced": p.item_def_referenced,
        "odd_defined": p.odd_defined,
        "performance_limitations_count": p.performance_limitations_count,
        "functional_insufficiencies_count": p.functional_insufficiencies_count,
        "triggering_conditions_count": p.triggering_conditions_count,
        "hazardous_behaviors_count": p.hazardous_behaviors_count,
        "scenario_quadrant_classes": dict(p.scenario_quadrant_classification),
        "acceptance_criteria_count": p.acceptance_criteria_count,
        "acceptance_measurable_count": p.acceptance_measurable,
        "out_of_odd_defined": p.out_of_odd_defined,
        "iso_21448_references": p.iso_21448_references,
    }
    print(json.dumps(summary, indent=2))
