"""Generate secure coding guidelines checklist xlsx."""
from __future__ import annotations
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from sec_coding_probe import probe
from check_definitions import CHECKS
from dashboard import build_dashboard

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
GREEN_OK = "C6EFCE"
ORANGE_PARTIAL = "FFD966"
RED_BAD = "F8CBAD"

def build_title(wb, probed):
    ws = wb.create_sheet("Title", 0)
    ws['A1'] = "SECURE CODING GUIDELINES CHECKLIST"
    ws['A1'].font = Font(bold=True, color="FFFFFF", size=14)
    ws['A1'].fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
    rows = [("Title", probed.title), ("Revision", probed.revision), ("Status", probed.status), ("Author", probed.author), ("Approver", probed.approver), ("Document ID", probed.doc_id)]
    for idx, (label, value) in enumerate(rows, start=3):
        ws[f'A{idx}'] = label
        ws[f'B{idx}'] = value or ""

def build_general_info(wb):
    ws = wb.create_sheet("General Info", 1)
    ws['A1'] = "General Information"
    ws['A1'].font = Font(bold=True, size=12)
    rows = [("Title", "Guidelines being assessed"), ("General Info", "TOC and conventions"), ("Guide", "How to interpret ratings"), ("Summary", "Dashboard with findings"), ("Confirmation Review", "Generic document quality checks"), ("SCG Assessment", "SCG substantive checks"), ("Verification Assessment", "Verification checks")]
    row = 3
    for tab, purpose in rows:
        ws[f'A{row}'] = tab
        ws[f'B{row}'] = purpose
        row += 1

def build_guide(wb):
    ws = wb.create_sheet("Guide", 2)
    ws['A1'] = "Guide — How to Use This Checklist"
    ws['A1'].font = Font(bold=True, size=12)
    items = ["FC/LC/PC/NO/NA ratings and PENDING for incomplete assessments", "Findings show evidence; subjective items require reviewer judgment", "Page/Section references source locations; Confidence: High/Medium/Low", "Recommended Actions are suggestions only; do not modify source document", "Shall=mandatory, Should=recommended obligations", "Auto-fill aids reviewer judgment but is not a substitute", "FC on SCG indicates full compliance; NO items must be resolved"]
    for i, instr in enumerate(items, start=3):
        ws[f'A{i}'] = instr

def build_confirmation_review(wb, results):
    ws = wb.create_sheet("Confirmation Review", 4)
    headers = ["ID", "Requirement", "Category", "Assessment", "Finding", "Recommended Action"]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col)
        cell.value = h
        cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
        cell.font = Font(bold=True, color="FFFFFF")
    row = 2
    for check in CHECKS[0:14]:
        result = results.get(check.id, {})
        rating = result.get('rating', 'PENDING')
        color = {
            'FC': GREEN_OK, 'LC': GREEN_OK, 'PC': ORANGE_PARTIAL, 'NO': RED_BAD, 'NA': LIGHT_BLUE
        }.get(rating, LIGHT_BLUE)
        ws.cell(row=row, column=1).value = check.id
        ws.cell(row=row, column=2).value = check.requirement
        ws.cell(row=row, column=3).value = check.category
        ws.cell(row=row, column=4).value = rating
        ws.cell(row=row, column=4).fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        ws.cell(row=row, column=5).value = result.get('finding', '')
        ws.cell(row=row, column=6).value = result.get('recommended_action', '')
        row += 1

def build_scg_assessment(wb, results):
    ws = wb.create_sheet("Secure Coding Guidelines Assessment", 5)
    headers = ["ID", "Requirement", "Category", "Assessment", "Finding", "Recommended Action"]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col)
        cell.value = h
        cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
        cell.font = Font(bold=True, color="FFFFFF")
    row = 2
    for check in CHECKS[14:28]:
        result = results.get(check.id, {})
        rating = result.get('rating', 'PENDING')
        color = {
            'FC': GREEN_OK, 'LC': GREEN_OK, 'PC': ORANGE_PARTIAL, 'NO': RED_BAD, 'NA': LIGHT_BLUE
        }.get(rating, LIGHT_BLUE)
        ws.cell(row=row, column=1).value = check.id
        ws.cell(row=row, column=2).value = check.requirement
        ws.cell(row=row, column=3).value = check.category
        ws.cell(row=row, column=4).value = rating
        ws.cell(row=row, column=4).fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        ws.cell(row=row, column=5).value = result.get('finding', '')
        ws.cell(row=row, column=6).value = result.get('recommended_action', '')
        row += 1

def build_verification_assessment(wb, results):
    ws = wb.create_sheet("Verification Assessment", 6)
    headers = ["ID", "Requirement", "Category", "Assessment", "Finding", "Recommended Action"]
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col)
        cell.value = h
        cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
        cell.font = Font(bold=True, color="FFFFFF")
    row = 2
    for check in CHECKS[28:42]:
        result = results.get(check.id, {})
        rating = result.get('rating', 'PENDING')
        color = {
            'FC': GREEN_OK, 'LC': GREEN_OK, 'PC': ORANGE_PARTIAL, 'NO': RED_BAD, 'NA': LIGHT_BLUE
        }.get(rating, LIGHT_BLUE)
        ws.cell(row=row, column=1).value = check.id
        ws.cell(row=row, column=2).value = check.requirement
        ws.cell(row=row, column=3).value = check.category
        ws.cell(row=row, column=4).value = rating
        ws.cell(row=row, column=4).fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        ws.cell(row=row, column=5).value = result.get('finding', '')
        ws.cell(row=row, column=6).value = result.get('recommended_action', '')
        row += 1

def generate(input_path: str, output_path: str) -> dict:
    probed = probe(input_path)
    wb = Workbook()
    wb.remove(wb.active)
    results = {}
    for check in CHECKS:
        result = check.verify(probed)
        results[check.id] = result
    build_title(wb, probed)
    build_general_info(wb)
    build_guide(wb)
    summary_ws = wb.create_sheet("Summary", 3)
    build_dashboard(summary_ws, results, project_label="SCG", checklist_label="Secure Coding Guidelines")
    build_confirmation_review(wb, results)
    build_scg_assessment(wb, results)
    build_verification_assessment(wb, results)
    wb.save(output_path)
    cr_results = [results[c.id] for c in CHECKS[0:14]]
    scg_results = [results[c.id] for c in CHECKS[14:28]]
    va_results = [results[c.id] for c in CHECKS[28:42]]
    return {
        "input": input_path,
        "output": output_path,
        "tabs": 7,
        "checks_by_tab": {"CR": 14, "SCG": 14, "VA": 14},
        "ratings_by_tab": {
            "CR": {r: sum(1 for x in cr_results if x['rating'] == r) for r in ['FC', 'LC', 'PC', 'NO', 'NA', 'PENDING']},
            "SCG": {r: sum(1 for x in scg_results if x['rating'] == r) for r in ['FC', 'LC', 'PC', 'NO', 'NA', 'PENDING']},
            "VA": {r: sum(1 for x in va_results if x['rating'] == r) for r in ['FC', 'LC', 'PC', 'NO', 'NA', 'PENDING']}
        }
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_checklist.py <input.xlsx> <output.xlsx>")
        sys.exit(1)
    result = generate(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))
