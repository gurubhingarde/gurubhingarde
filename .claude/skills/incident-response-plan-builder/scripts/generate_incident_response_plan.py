"""
Incident Response Plan Builder — generates a multi-tab ISO/SAE 21434 §13 Incident Response Plan workbook.

Usage:
    python generate_incident_response_plan.py <input.json> <output.xlsx>

Input JSON schema:
{
  "org": {name, doc_id, revision, date, psirt_lead, company, target_cal},
  "psirt_roster": [{name, role, org, email, phone, oncall}],
  "severity_thresholds": [{severity, cvss_min, cvss_max, sla_response_h, sla_comm_h, sla_fix_d}],
  "regulators": [{regulator, trigger, deadline_h, content_required, owner}]
}
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


# ---------------------------------------------------------------------------
# Styling helpers (match hara-builder palette)
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"

THIN = Side(border_style="thin", color="BFBFBF")
MEDIUM = Side(border_style="medium", color="404040")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def title_font(size: int = 16) -> Font:
    return Font(name=FONT_NAME, size=size, bold=True, color="FFFFFF")


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def style_title_row(ws, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = title_font(14)
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header_row(ws, row: int, headers: list[str]) -> None:
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = header_font()
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 32


def stripe_body(ws, start_row: int, end_row: int, last_col: int) -> None:
    for r in range(start_row, end_row + 1):
        fill = PatternFill("solid", fgColor=ALT_ROW) if (r - start_row) % 2 else None
        for c in range(1, last_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = body_font()
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER_ALL
            if fill:
                cell.fill = fill


def autosize(ws, widths: dict[int, int]) -> None:
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------

def build_title_page(wb: Workbook, data: dict) -> None:
    """00_Title_Page — Organization, item, PSIRT lead, contact, target CAL."""
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False

    org = data.get("org", {})

    style_title_row(ws, 2, 4, "Incident Response Plan")
    style_title_row(ws, 3, 4, f"ISO/SAE 21434, Section 13 (Cybersecurity Incident Response)")

    fields = [
        ("Organization", org.get("name", "")),
        ("Document ID", org.get("doc_id", "")),
        ("Revision", org.get("revision", "")),
        ("Date", org.get("date", "")),
        ("PSIRT Lead", org.get("psirt_lead", "")),
        ("Company", org.get("company", "")),
        ("Target CAL", org.get("target_cal", "")),
    ]

    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1

    autosize(ws, {1: 4, 2: 26, 3: 60, 4: 4})


def build_document_control(wb: Workbook) -> None:
    """01_Document_Control — Revision history."""
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False

    style_title_row(ws, 1, 5, "Document Control")

    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of Change", "Approver"])
    placeholders = [
        ("0.1", "", "", "Initial draft", ""),
        ("0.2", "", "", "Internal review", ""),
        ("1.0", "", "", "Released", ""),
    ]
    for i, row_data in enumerate(placeholders, start=4):
        for col, val in enumerate(row_data, start=1):
            ws.cell(row=i, column=col, value=val)
    stripe_body(ws, 4, 4 + len(placeholders) - 1, 5)
    autosize(ws, {1: 12, 2: 12, 3: 18, 4: 30, 5: 18})


def build_psirt_roster(wb: Workbook, data: dict) -> None:
    """02_PSIRT_Roster — Team roster: name, role, org, email, phone, on-call schedule."""
    ws = wb.create_sheet("02_PSIRT_Roster")

    style_title_row(ws, 1, 6, "PSIRT Roster")

    headers = ["Name", "Role", "Organization", "Email", "Phone", "On-Call Schedule"]
    style_header_row(ws, 3, headers)

    roster = data.get("psirt_roster", [])
    if not roster:
        roster = [
            {"name": "", "role": "PSIRT Manager", "org": "", "email": "", "phone": "", "oncall": ""},
            {"name": "", "role": "Triage Engineer", "org": "", "email": "", "phone": "", "oncall": ""},
            {"name": "", "role": "Comms Lead", "org": "", "email": "", "phone": "", "oncall": ""},
            {"name": "", "role": "Legal", "org": "", "email": "", "phone": "", "oncall": ""},
            {"name": "", "role": "Engineering Rep", "org": "", "email": "", "phone": "", "oncall": ""},
        ]

    for i, member in enumerate(roster, start=4):
        ws.cell(row=i, column=1, value=member.get("name", ""))
        ws.cell(row=i, column=2, value=member.get("role", ""))
        ws.cell(row=i, column=3, value=member.get("org", ""))
        ws.cell(row=i, column=4, value=member.get("email", ""))
        ws.cell(row=i, column=5, value=member.get("phone", ""))
        ws.cell(row=i, column=6, value=member.get("oncall", ""))

    stripe_body(ws, 4, 4 + len(roster) - 1, 6)
    autosize(ws, {1: 18, 2: 18, 3: 18, 4: 25, 5: 16, 6: 28})


def build_triage_classification(wb: Workbook, data: dict) -> None:
    """03_Triage_Classification — Severity with CVSS thresholds and SLA per severity."""
    ws = wb.create_sheet("03_Triage_Classification")

    style_title_row(ws, 1, 7, "Triage Classification & SLA")

    headers = ["Severity", "CVSS Min", "CVSS Max", "Response SLA (hours)", "Communication SLA (hours)", "Fix SLA (days)", "Escalation Trigger"]
    style_header_row(ws, 3, headers)

    thresholds = data.get("severity_thresholds", [])
    if not thresholds:
        thresholds = [
            {"severity": "Critical", "cvss_min": 9.0, "cvss_max": 10.0, "sla_response_h": 1, "sla_comm_h": 2, "sla_fix_d": 1},
            {"severity": "High", "cvss_min": 7.0, "cvss_max": 8.9, "sla_response_h": 4, "sla_comm_h": 8, "sla_fix_d": 7},
            {"severity": "Medium", "cvss_min": 4.0, "cvss_max": 6.9, "sla_response_h": 24, "sla_comm_h": 48, "sla_fix_d": 30},
            {"severity": "Low", "cvss_min": 0.1, "cvss_max": 3.9, "sla_response_h": 72, "sla_comm_h": 168, "sla_fix_d": 90},
        ]

    for i, thresh in enumerate(thresholds, start=4):
        ws.cell(row=i, column=1, value=thresh.get("severity", ""))
        ws.cell(row=i, column=2, value=thresh.get("cvss_min", ""))
        ws.cell(row=i, column=3, value=thresh.get("cvss_max", ""))
        ws.cell(row=i, column=4, value=thresh.get("sla_response_h", ""))
        ws.cell(row=i, column=5, value=thresh.get("sla_comm_h", ""))
        ws.cell(row=i, column=6, value=thresh.get("sla_fix_d", ""))
        ws.cell(row=i, column=7, value="")

    stripe_body(ws, 4, 4 + len(thresholds) - 1, 7)
    autosize(ws, {1: 14, 2: 12, 3: 12, 4: 18, 5: 20, 6: 14, 7: 30})


def build_detection_sources(wb: Workbook) -> None:
    """04_Detection_Sources — Vulnerability sources, handlers, intake forms."""
    ws = wb.create_sheet("04_Detection_Sources")

    style_title_row(ws, 1, 4, "Detection Sources & Intake")

    headers = ["Source", "Handler/Owner", "Intake Form/Process", "Priority"]
    style_header_row(ws, 3, headers)

    sources = [
        ("Vulnerability Disclosure (Researcher)", "", "Security vulnerability disclosure form", "High"),
        ("CVE/NVD Publication", "", "Automated monitoring + manual review", "High"),
        ("Customer Complaint", "", "Customer support ticket + escalation form", "High"),
        ("Internal Security Scan", "", "Scan report review + triage meeting", "Medium"),
        ("Intrusion Detection System", "", "IDS alert + forensics checklist", "High"),
        ("Threat Intelligence Feed", "", "Feed subscription + SIGINT analysis", "Medium"),
        ("OTA Telemetry Anomaly", "", "Telemetry dashboard alert + correlation", "Medium"),
    ]

    for i, (src, handler, form, priority) in enumerate(sources, start=4):
        ws.cell(row=i, column=1, value=src)
        ws.cell(row=i, column=2, value=handler)
        ws.cell(row=i, column=3, value=form)
        ws.cell(row=i, column=4, value=priority)

    stripe_body(ws, 4, 4 + len(sources) - 1, 4)
    autosize(ws, {1: 35, 2: 25, 3: 35, 4: 12})


def build_response_workflow(wb: Workbook) -> None:
    """05_Response_Workflow — DETECT, TRIAGE, CONTAIN, ERADICATE, RECOVER, POST-MORTEM."""
    ws = wb.create_sheet("05_Response_Workflow")

    style_title_row(ws, 1, 5, "Incident Response Workflow")

    headers = ["Stage", "Key Roles", "Activities", "Deliverables", "Escalation Triggers"]
    style_header_row(ws, 3, headers)

    stages = [
        ("DETECT", "Security Operations, SOC", "Monitor logs, alerts, threat intel feeds", "Incident report, severity assessment", "Any confirmed intrusion or data exfiltration"),
        ("TRIAGE", "PSIRT Triage Engineer, Security Lead", "Classify severity (CVSS), determine impact scope", "Triage report, SLA assignment, stakeholder list", "Escalate to Engineering if system-critical"),
        ("CONTAIN", "Engineering, Security, Legal", "Isolate affected systems, preserve evidence, notify stakeholders", "Containment plan, evidence log, comms draft", "Regulatory notification decision point"),
        ("ERADICATE", "Engineering, DevOps", "Develop patch, test in staging, prepare rollout", "Patch code, test report, rollback plan", "Rollout gate review required"),
        ("RECOVER", "Operations, Comms, Engineering", "Stage and deploy patch, monitor telemetry, customer comms", "Deployment report, telemetry analysis, customer bulletin", "Monitor for regression"),
        ("POST-MORTEM", "All stakeholders", "Timeline review, root cause analysis, corrective actions", "Lessons learned report, prevention plan", "Sign-off by PSIRT Manager and Legal"),
    ]

    for i, (stage, roles, activities, deliverables, escalation) in enumerate(stages, start=4):
        ws.cell(row=i, column=1, value=stage)
        ws.cell(row=i, column=2, value=roles)
        ws.cell(row=i, column=3, value=activities)
        ws.cell(row=i, column=4, value=deliverables)
        ws.cell(row=i, column=5, value=escalation)

    stripe_body(ws, 4, 4 + len(stages) - 1, 5)
    autosize(ws, {1: 16, 2: 25, 3: 30, 4: 30, 5: 35})


def build_coordinated_disclosure(wb: Workbook) -> None:
    """06_Coordinated_Disclosure_Policy — Embargo, CVE coordination, credit, public disclosure."""
    ws = wb.create_sheet("06_Coordinated_Disclosure_Policy")

    style_title_row(ws, 1, 3, "Coordinated Disclosure Policy")

    row = 3
    fields = [
        ("Researcher Contact Method", "security@company.com or submit via responsible-disclosure portal"),
        ("Standard Embargo Period", "90 days from first contact (extendable to 180 if patch not ready)"),
        ("CVE Coordination", "Assign CVE via MITRE, publish in NVD with severity and remediation"),
        ("Public Disclosure Timing", "Coordinate with vendor release schedule; disclose 24h after patch availability"),
        ("Credit Policy", "Acknowledge researcher by name (if agreed) in security bulletin and CVE record"),
        ("Pre-Disclosure Briefing", "Brief major customers 3-5 days before public disclosure"),
        ("Dispute Resolution", "Escalate disagreements to PSIRT Manager and Legal for mediation"),
    ]

    for label, value in fields:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=row, column=2, value=value).alignment = Alignment(wrap_text=True)
        row += 1

    autosize(ws, {1: 35, 2: 60})


def build_ota_patch_workflow(wb: Workbook) -> None:
    """07_OTA_Patch_Workflow — Vulnerability to fix dev to test to rollout."""
    ws = wb.create_sheet("07_OTA_Patch_Workflow")

    style_title_row(ws, 1, 5, "OTA Patch Workflow")

    headers = ["Stage", "Owner", "Gate Criteria", "Rollback Plan", "Timeline (Days)"]
    style_header_row(ws, 3, headers)

    stages = [
        ("Fix Development", "Engineering Lead", "Code review, security review, design approval", "Revert to prior branch; communicate delay to PSIRT", "1-3"),
        ("Unit & Integration Test", "QA Lead", "Unit tests pass (80% coverage min), integration tests green", "Revert patch; re-test prior version", "2-5"),
        ("Staging OTA Test", "OTA Eng, Test", "Deploy to staging fleet; validate rollout mechanism, telemetry", "Fall back to prior OTA version; monitor health", "3-7"),
        ("Pre-Production Validation", "Security, Engineering, Comms", "Patch functionality verified; no regressions; comms reviewed", "Hold rollout; customer comms postponed", "1-2"),
        ("Staged Rollout (10% Fleet)", "OTA Operations", "Monitor telemetry for 24h; validate no anomalies", "Pause rollout; revert affected vehicles; communication", "1-2"),
        ("Full Production Rollout", "OTA Operations", "Green light from monitoring; customer communication active", "Pause new deployments; comms to in-flight users", "1-3"),
    ]

    for i, (stage, owner, gate, rollback, timeline) in enumerate(stages, start=4):
        ws.cell(row=i, column=1, value=stage)
        ws.cell(row=i, column=2, value=owner)
        ws.cell(row=i, column=3, value=gate)
        ws.cell(row=i, column=4, value=rollback)
        ws.cell(row=i, column=5, value=timeline)

    stripe_body(ws, 4, 4 + len(stages) - 1, 5)
    autosize(ws, {1: 25, 2: 18, 3: 35, 4: 30, 5: 16})


def build_regulatory_notifications(wb: Workbook, data: dict) -> None:
    """08_Regulatory_Notifications — UN R155, ENISA, NHTSA, JAMA notification triggers and deadlines."""
    ws = wb.create_sheet("08_Regulatory_Notifications")

    style_title_row(ws, 1, 6, "Regulatory Notifications")

    headers = ["Regulator/Standard", "Notification Trigger", "Deadline (Hours)", "Content Required", "Owner", "Status"]
    style_header_row(ws, 3, headers)

    regulators = data.get("regulators", [])
    if not regulators:
        regulators = [
            {"regulator": "UN R155 (ECE)", "trigger": "Critical vulnerability in cybersecurity requirements", "deadline_h": 72, "content_required": "Incident description, impact assessment, remediation plan", "owner": "Legal/PSIRT Manager"},
            {"regulator": "ENISA (EU Cybersecurity Act)", "trigger": "Material security incident affecting EU customers", "deadline_h": 72, "content_required": "Incident report, breach notification, customer communication draft", "owner": "Legal/Comms"},
            {"regulator": "NHTSA (US)", "trigger": "Safety-related defect found via cybersecurity incident", "deadline_h": 168, "content_required": "Defect description, vehicles affected, remedy plan", "owner": "Legal/Engineering"},
            {"regulator": "JAMA (Japan)", "trigger": "Incident affecting Japan market vehicles", "deadline_h": 168, "content_required": "Japanese translation of incident details and remedy", "owner": "Comms/Legal"},
            {"regulator": "CCAS (China)", "trigger": "Cybersecurity incident in China", "deadline_h": 168, "content_required": "Incident report in Chinese, impact, remediation", "owner": "Legal/Comms"},
        ]

    for i, reg in enumerate(regulators, start=4):
        ws.cell(row=i, column=1, value=reg.get("regulator", ""))
        ws.cell(row=i, column=2, value=reg.get("trigger", ""))
        ws.cell(row=i, column=3, value=reg.get("deadline_h", ""))
        ws.cell(row=i, column=4, value=reg.get("content_required", ""))
        ws.cell(row=i, column=5, value=reg.get("owner", ""))
        ws.cell(row=i, column=6, value="")

    stripe_body(ws, 4, 4 + len(regulators) - 1, 6)
    autosize(ws, {1: 22, 2: 35, 3: 16, 4: 35, 5: 22, 6: 12})


def build_customer_communications(wb: Workbook) -> None:
    """09_Customer_Communications — Playbook: severity to comms channel and templates."""
    ws = wb.create_sheet("09_Customer_Communications")

    style_title_row(ws, 1, 4, "Customer Communications Playbook")

    headers = ["Severity", "Comms Channel", "Audience", "Message Template / Key Points"]
    style_header_row(ws, 3, headers)

    comms = [
        ("Critical", "Technical Bulletin + Press Release + Direct Customer Call", "All customers, media, analysts", "Incident description, immediate workaround, patch availability, link to security advisory"),
        ("High", "Technical Bulletin + Customer Email Notification", "Affected customer base, support team", "Vulnerability details (CVSS), remediation timeline, patch release date, customer action required"),
        ("Medium", "Technical Bulletin (internal), Customer Email (opt-in)", "Affected customers who subscribe to security updates", "Vulnerability summary, patch availability, recommendation to update at next service opportunity"),
        ("Low", "Customer FAQ / Security Update Notes", "Self-service community forum, customer portal", "Vulnerability fixed in next release, patch available for interested users, link to technical details"),
    ]

    for i, (sev, channel, audience, template) in enumerate(comms, start=4):
        ws.cell(row=i, column=1, value=sev)
        ws.cell(row=i, column=2, value=channel)
        ws.cell(row=i, column=3, value=audience)
        ws.cell(row=i, column=4, value=template)

    stripe_body(ws, 4, 4 + len(comms) - 1, 4)
    autosize(ws, {1: 12, 2: 35, 3: 25, 4: 50})


def build_post_incident_review(wb: Workbook) -> None:
    """10_Post_Incident_Review — Template for timeline, RCA, lessons learned, corrective actions."""
    ws = wb.create_sheet("10_Post_Incident_Review")

    style_title_row(ws, 1, 3, "Post-Incident Review Template")

    row = 3
    sections = [
        ("Incident ID", "e.g., INC-2024-001"),
        ("Incident Title", ""),
        ("Executive Summary", "One-paragraph overview of the incident, impact, and resolution"),
        ("", ""),
        ("Incident Timeline", ""),
        ("Detection Time", ""),
        ("Triage Completion", ""),
        ("Containment Start", ""),
        ("Patch Released", ""),
        ("Patch Deployed", ""),
        ("All-Clear Confirmed", ""),
        ("", ""),
        ("Root Cause Analysis", ""),
        ("Primary Cause", ""),
        ("Contributing Factors", "List of design, process, or environmental factors that enabled the vulnerability"),
        ("", ""),
        ("Lessons Learned", ""),
        ("What Went Well", ""),
        ("What Could Improve", ""),
        ("Process Changes Required", ""),
        ("", ""),
        ("Corrective Actions", ""),
        ("Action", "Owner"),
        ("", ""),
        ("", ""),
        ("Prevention Plan", "How will similar incidents be prevented in the future"),
        ("Sign-Off", "PSIRT Manager Name: ___________   Legal Name: ___________"),
    ]

    for label, value in sections:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, size=10, bold=True if label else False)
        ws.cell(row=row, column=2, value=value)
        row += 1

    autosize(ws, {1: 30, 2: 60})


def build_communication_templates(wb: Workbook) -> None:
    """11_Communication_Templates — Email/doc templates for researcher, CVE, escalation, customer, press."""
    ws = wb.create_sheet("11_Communication_Templates")

    style_title_row(ws, 1, 2, "Communication Templates")

    row = 3
    templates = [
        ("RESEARCHER ACKNOWLEDGMENT", "Thank you for responsibly reporting this security concern. We acknowledge receipt of your report on [DATE]. A PSIRT engineer will begin analysis immediately and will contact you within 24 hours with an initial assessment."),
        ("", ""),
        ("CVE ASSIGNMENT NOTICE", "We are coordinating with MITRE for CVE assignment. The vulnerability has been assessed at CVSS [SCORE] ([SEVERITY]). A patch will be available by [EMBARGO_DATE]. Please hold this information in confidence until the embargo is lifted."),
        ("", ""),
        ("INTERNAL ESCALATION (BRIEF)", "[SEVERITY] vulnerability detected in [SYSTEM]. Impact: [BRIEF_IMPACT]. PSIRT response initiated. Next briefing: [TIME]."),
        ("", ""),
        ("CUSTOMER TECHNICAL BULLETIN", "Security Update: [SYSTEM] Vulnerability (CVE-[XXXX-XXXXX]). Summary: [BRIEF_DESC]. Severity: [CVSS_SCORE]. Remediation: Update to version [VERSION] available [DATE]. Instructions: [LINK_TO_UPDATE_GUIDE]."),
        ("", ""),
        ("PRESS RELEASE", "[COMPANY] Addresses Security Vulnerability in [PRODUCT]. [COMPANY] has identified and patched a cybersecurity vulnerability (CVE-[ID]) affecting [PRODUCT]. Customers are encouraged to update to the latest version. Full details: [SECURITY_ADVISORY_URL]."),
        ("", ""),
    ]

    for label, text in templates:
        if label:
            ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, size=10, bold=True)
        ws.cell(row=row, column=2, value=text).alignment = Alignment(wrap_text=True)
        row += 1

    autosize(ws, {1: 35, 2: 70})


def build_references(wb: Workbook) -> None:
    """12_References — ISO/SAE 21434, UN R155, FIRST.org PSIRT framework, standards."""
    ws = wb.create_sheet("12_References")

    style_title_row(ws, 1, 3, "References")

    headers = ["Reference", "Title", "Notes"]
    style_header_row(ws, 3, headers)

    references = [
        ("ISO/SAE 21434:2021", "Road vehicles — Cybersecurity engineering", "Section 13: Incident Response Plan"),
        ("UN R155", "United Nations Regulation on Cybersecurity and Cybersecurity Management", "ECE cybersecurity requirements for vehicles"),
        ("FIRST.org PSIRT Framework", "Guidelines for Product Security Incident Response Teams", "Industry best practices for PSIRT operation"),
        ("NIST Cybersecurity Framework", "Detect, Respond, Recover incident management", "US federal guidance on incident response"),
        ("CVSS 3.1", "Common Vulnerability Scoring System", "Vulnerability severity assessment standard"),
        ("ENISA Guidelines", "Cybersecurity Incident Response Guidelines", "EU cybersecurity breach notification"),
        ("JAMA Security Bulletin", "Japanese automotive security incident procedures", "JAMA security update coordination"),
        ("OTA Best Practices", "Over-the-Air Update Security", "Secure patch delivery mechanisms"),
        ("Internal Security Policy", "Company cybersecurity incident response SOP", ""),
        ("Internal Legal Policy", "Regulatory notification procedures", ""),
    ]

    for i, (ref, title, notes) in enumerate(references, start=4):
        ws.cell(row=i, column=1, value=ref)
        ws.cell(row=i, column=2, value=title)
        ws.cell(row=i, column=3, value=notes)

    stripe_body(ws, 4, 4 + len(references) - 1, 3)
    autosize(ws, {1: 28, 2: 50, 3: 30})


def main() -> None:
    """Generate Incident Response Plan workbook from JSON input."""
    if len(sys.argv) != 3:
        print("Usage: python generate_incident_response_plan.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: input file not found: {input_file}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    # Build all 13 tabs in order
    build_title_page(wb, data)
    build_document_control(wb)
    build_psirt_roster(wb, data)
    build_triage_classification(wb, data)
    build_detection_sources(wb)
    build_response_workflow(wb)
    build_coordinated_disclosure(wb)
    build_ota_patch_workflow(wb)
    build_regulatory_notifications(wb, data)
    build_customer_communications(wb)
    build_post_incident_review(wb)
    build_communication_templates(wb)
    build_references(wb)

    wb.save(str(output_file))
    print(f"Incident Response Plan generated: {output_file}")
    print(f"Tabs: {len(wb.sheetnames)} — {', '.join(wb.sheetnames)}")


if __name__ == "__main__":
    main()
