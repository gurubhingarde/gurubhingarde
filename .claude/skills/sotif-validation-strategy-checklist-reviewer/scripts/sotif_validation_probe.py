"""SOTIF Validation Strategy probe — extracts from sotif-validation-strategy.xlsx"""

from dataclasses import dataclass, field
from pathlib import Path
from openpyxl import load_workbook

def _norm(s) -> str:
    return str(s).strip() if s else ""

def _find_sheet(sheet_names, keywords):
    for name in sheet_names:
        if any(k.lower() in name.lower() for k in keywords):
            return name
    return ""

@dataclass
class ProbedValidationStrategy:
    path: str = ""
    sheet_names: list[str] = field(default_factory=list)
    title: str = ""
    revision: str = ""
    status: str = ""
    author: str = ""
    approver: str = ""
    project: str = ""
    doc_id: str = ""
    acceptance_criteria_referenced: bool = False
    validation_methods_count: int = 0
    real_world_mileage_target: str = ""
    fleet_coverage_defined: bool = False
    simulation_library_cited: bool = False
    simulation_correlation: bool = False
    proving_ground_tests: int = 0
    field_monitoring_defined: bool = False
    acceptance_tracking_present: bool = False
    coverage_gaps_noted: bool = False
    statistical_significance: bool = False
    iso_21448_references: int = 0

def probe(xlsx_path: str | Path) -> ProbedValidationStrategy:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedValidationStrategy(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    title_sheet = _find_sheet(p.sheet_names, ["title"])
    if title_sheet in wb.sheetnames:
        ws = wb[title_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value) if c < ws.max_column else ""
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

    # Acceptance criteria reference
    for sheet_name in p.sheet_names:
        if "acceptance" in sheet_name.lower() or "criterion" in sheet_name.lower():
            p.acceptance_criteria_referenced = True
            break

    # Validation methods
    methods_sheet = _find_sheet(p.sheet_names, ["validation", "method"])
    if methods_sheet in wb.sheetnames:
        ws = wb[methods_sheet]
        for r in range(2, ws.max_row + 1):
            if _norm(ws.cell(r, 1).value) or _norm(ws.cell(r, 2).value):
                p.validation_methods_count += 1

    # Real-world mileage
    rw_sheet = _find_sheet(p.sheet_names, ["real-world", "field", "driving"])
    if rw_sheet in wb.sheetnames:
        ws = wb[rw_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            row_text = " ".join(_norm(ws.cell(r, c).value) for c in range(1, 4)).lower()
            if "mileage" in row_text or "distance" in row_text:
                value = _norm(ws.cell(r, 2).value)
                if value and any(c.isdigit() for c in value):
                    p.real_world_mileage_target = value
            if "geography" in row_text or "weather" in row_text or "distribution" in row_text:
                p.fleet_coverage_defined = True

    # Simulation
    sim_sheet = _find_sheet(p.sheet_names, ["simulation"])
    if sim_sheet in wb.sheetnames:
        ws = wb[sim_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            row_text = " ".join(_norm(ws.cell(r, c).value) for c in range(1, 4)).lower()
            if "nhtsa" in row_text or "eurocap" in row_text or "library" in row_text:
                p.simulation_library_cited = True
            if "correlation" in row_text or "validate" in row_text:
                p.simulation_correlation = True

    # Proving ground
    pg_sheet = _find_sheet(p.sheet_names, ["proving", "test", "track"])
    if pg_sheet in wb.sheetnames:
        ws = wb[pg_sheet]
        for r in range(2, ws.max_row + 1):
            if _norm(ws.cell(r, 1).value) or _norm(ws.cell(r, 2).value):
                p.proving_ground_tests += 1

    # Field monitoring
    fm_sheet = _find_sheet(p.sheet_names, ["field", "monitoring", "telemetry"])
    if fm_sheet in wb.sheetnames:
        ws = wb[fm_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            row_text = " ".join(_norm(ws.cell(r, c).value) for c in range(1, 4)).lower()
            if "telemetry" in row_text or "log" in row_text or "monitor" in row_text:
                p.field_monitoring_defined = True

    # Acceptance tracking
    if _find_sheet(p.sheet_names, ["acceptance", "tracking", "status"]) in wb.sheetnames:
        p.acceptance_tracking_present = True

    # Coverage gaps
    for sheet_name in p.sheet_names:
        if "gap" in sheet_name.lower() or "coverage" in sheet_name.lower():
            p.coverage_gaps_noted = True
            break

    # Statistical significance
    ref_sheet = _find_sheet(p.sheet_names, ["reference", "general"])
    if ref_sheet in wb.sheetnames:
        ws = wb[ref_sheet]
        for r in range(1, ws.max_row + 1):
            row_text = " ".join(_norm(ws.cell(r, c).value) for c in range(1, 4)).lower()
            if "statistical" in row_text or "significance" in row_text or "confidence" in row_text:
                p.statistical_significance = True
            if "iso 21448" in row_text:
                p.iso_21448_references += 1

    return p

if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    print(json.dumps({
        "path": p.path,
        "title": p.title,
        "acceptance_criteria_referenced": p.acceptance_criteria_referenced,
        "validation_methods": p.validation_methods_count,
        "real_world_mileage_target": p.real_world_mileage_target,
        "fleet_coverage_defined": p.fleet_coverage_defined,
        "simulation_library_cited": p.simulation_library_cited,
        "proving_ground_tests": p.proving_ground_tests,
        "field_monitoring_defined": p.field_monitoring_defined,
        "acceptance_tracking_present": p.acceptance_tracking_present,
        "coverage_gaps_noted": p.coverage_gaps_noted,
        "statistical_significance": p.statistical_significance,
        "iso_21448_references": p.iso_21448_references,
    }, indent=2))
