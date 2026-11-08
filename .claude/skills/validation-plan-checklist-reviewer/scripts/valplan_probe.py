"""Probe a Validation Plan xlsx and extract structured data."""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from openpyxl import load_workbook

@dataclass
class ProbedValPlan:
    title: str = "Validation Plan"
    doc_id: str = "VP-001"
    revision: str = "1.0"
    project: str = ""
    scope: str = ""
    safety_goals: list = None
    scenarios: list = None
    environments: list = None
    resources: list = None
    exit_criteria: list = None

    def __post_init__(self):
        if self.safety_goals is None:
            self.safety_goals = []
        if self.scenarios is None:
            self.scenarios = []
        if self.environments is None:
            self.environments = []
        if self.resources is None:
            self.resources = []
        if self.exit_criteria is None:
            self.exit_criteria = []

def probe_valplan(xlsx_path: str) -> ProbedValPlan:
    """Extract metadata from Validation Plan xlsx."""
    try:
        wb = load_workbook(xlsx_path, data_only=True)
    except Exception as e:
        raise ValueError(f"Cannot open {xlsx_path}: {e}")

    probed = ProbedValPlan()

    # Extract from Title sheet
    if "Title" in wb.sheetnames:
        ws = wb["Title"]
        for row in ws.iter_rows(min_row=5, max_row=20, min_col=1, max_col=2, values_only=False):
            if row[0] and row[0].value:
                key = str(row[0].value).strip().lower()
                val = row[1].value if row[1] else ""
                if "project" in key:
                    probed.project = val or ""
                elif "doc" in key:
                    probed.doc_id = val or ""
                elif "revision" in key:
                    probed.revision = val or ""

    # Extract scenarios
    if "Scenario Catalog" in wb.sheetnames:
        ws = wb["Scenario Catalog"]
        for row in ws.iter_rows(min_row=4, max_row=50, min_col=1, max_col=4, values_only=True):
            if row and row[0]:
                probed.scenarios.append({
                    "id": row[0],
                    "description": row[1] if len(row) > 1 else "",
                    "use_case": row[2] if len(row) > 2 else "",
                    "edge_case": row[3] if len(row) > 3 else ""
                })

    # Extract environments
    if "Validation Environments" in wb.sheetnames:
        ws = wb["Validation Environments"]
        for row in ws.iter_rows(min_row=4, max_row=20, min_col=1, max_col=3, values_only=True):
            if row and row[0]:
                probed.environments.append({
                    "env": row[0],
                    "description": row[1] if len(row) > 1 else "",
                    "location": row[2] if len(row) > 2 else ""
                })

    # Extract resources
    if "Resources" in wb.sheetnames:
        ws = wb["Resources"]
        for row in ws.iter_rows(min_row=4, max_row=20, min_col=1, max_col=3, values_only=True):
            if row and row[0]:
                probed.resources.append({
                    "resource": row[0],
                    "quantity": row[1] if len(row) > 1 else "",
                    "specification": row[2] if len(row) > 2 else ""
                })

    # Extract exit criteria
    if "Exit Criteria" in wb.sheetnames:
        ws = wb["Exit Criteria"]
        for row in ws.iter_rows(min_row=4, max_row=20, min_col=1, max_col=4, values_only=True):
            if row and row[0]:
                probed.exit_criteria.append({
                    "criterion": row[0],
                    "measurement": row[1] if len(row) > 1 else "",
                    "threshold": row[2] if len(row) > 2 else ""
                })

    return probed
