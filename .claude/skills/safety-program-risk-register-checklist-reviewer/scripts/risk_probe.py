"""Probe and extract risk register data from xlsx."""

from typing import NamedTuple, List
from openpyxl import load_workbook


class ProbedRisk(NamedTuple):
    risk_id: str
    category: str
    description: str
    likelihood: int
    impact: int
    risk_score: int
    owner: str
    status: str
    target_date: str
    mitigation: str


class ProbedRiskRegister(NamedTuple):
    project_name: str
    doc_id: str
    target_asil: str
    risks: List[ProbedRisk]
    num_tabs: int
    has_mitigation_plan: bool
    has_contingency_plan: bool
    has_escalation_log: bool
    has_trend_analysis: bool


def probe(xlsx_path: str) -> ProbedRiskRegister:
    """Extract data from risk register workbook."""
    wb = load_workbook(xlsx_path)

    project_name = ""
    doc_id = ""
    target_asil = ""

    # Extract from title page
    if "Title Page" in wb.sheetnames:
        ws_title = wb["Title Page"]
        for row in ws_title.iter_rows(min_row=3, max_row=10, values_only=True):
            if row[0] == "Project Name":
                project_name = str(row[1] or "")
            elif row[0] == "Document ID":
                doc_id = str(row[1] or "")
            elif row[0] == "Target ASIL":
                target_asil = str(row[1] or "")

    risks = []

    # Extract from Risk Catalog tab
    if "Risk Catalog" in wb.sheetnames:
        ws_risks = wb["Risk Catalog"]
        for row in ws_risks.iter_rows(min_row=4, max_row=ws_risks.max_row, values_only=True):
            if not row[0]:
                break
            try:
                risk = ProbedRisk(
                    risk_id=str(row[0] or ""),
                    category=str(row[1] or ""),
                    description=str(row[2] or ""),
                    likelihood=int(row[3] or 0),
                    impact=int(row[4] or 0),
                    risk_score=int(row[5] or 0),
                    owner=str(row[6] or ""),
                    status=str(row[7] or ""),
                    target_date=str(row[8] or ""),
                    mitigation=""
                )
                risks.append(risk)
            except (ValueError, TypeError):
                pass

    # Extract mitigation data
    if "Mitigation Plan" in wb.sheetnames:
        ws_mit = wb["Mitigation Plan"]
        for row in ws_mit.iter_rows(min_row=4, max_row=ws_mit.max_row, values_only=True):
            if not row[0]:
                break
            risk_id = str(row[0] or "")
            mitigation = str(row[1] or "")
            for i, risk in enumerate(risks):
                if risk.risk_id == risk_id:
                    risks[i] = risk._replace(mitigation=mitigation)
                    break

    return ProbedRiskRegister(
        project_name=project_name,
        doc_id=doc_id,
        target_asil=target_asil,
        risks=risks,
        num_tabs=len(wb.sheetnames),
        has_mitigation_plan="Mitigation Plan" in wb.sheetnames,
        has_contingency_plan="Contingency Plan" in wb.sheetnames,
        has_escalation_log="Escalation Log" in wb.sheetnames,
        has_trend_analysis="Risk Trend" in wb.sheetnames,
    )
