"""Lessons Learned — generates a multi-tab ISO 26262-2 lessons register workbook from JSON.

Usage:
    python generate_ll.py <input.json> <output.xlsx>
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side


FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"
THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def style_title(ws, row, last_col, text):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header(ws, row, headers):
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 36


def build_title_page(wb, project_info):
    ws = wb.active
    ws.title = "Title Page"
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title(ws, row, 3, "Lessons Learned Register")

    row = 3
    ws.cell(row=row, column=1, value="Project Name").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project_info.get("name", ""))

    row += 1
    ws.cell(row=row, column=1, value="Document ID").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project_info.get("doc_id", "LL-001"))

    row += 1
    ws.cell(row=row, column=1, value="Lesson Period").font = Font(bold=True)
    ws.cell(row=row, column=2, value=f"{project_info.get('period_start', '')} to {project_info.get('period_end', '')}")

    row += 1
    ws.cell(row=row, column=1, value="Document Date").font = Font(bold=True)
    ws.cell(row=row, column=2, value=str(date.today()))

    row += 1
    ws.cell(row=row, column=1, value="Owner").font = Font(bold=True)
    ws.cell(row=row, column=2, value=project_info.get("owner", ""))


def build_document_control(wb):
    ws = wb.create_sheet("Document Control")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 50

    row = 1
    style_title(ws, row, 3, "Document Control")

    row = 3
    headers = ["Revision", "Date", "Summary"]
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="1.0")
    ws.cell(row=row, column=2, value=str(date.today()))
    ws.cell(row=row, column=3, value="Initial release")


def build_lesson_catalog(wb, lessons):
    ws = wb.create_sheet("Lesson Catalog")

    headers = ["Lesson ID", "Source", "Summary", "Root Cause", "Corrective Action", "Best Practice", "Applicability"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 30
    ws.column_dimensions["D"].width = 30
    ws.column_dimensions["E"].width = 30
    ws.column_dimensions["F"].width = 30
    ws.column_dimensions["G"].width = 20

    row = 1
    style_title(ws, row, len(headers), "Lesson Catalog")

    row = 3
    style_header(ws, row, headers)

    for idx, lesson in enumerate(lessons, start=4):
        ws.cell(row=idx, column=1, value=lesson.get("id", f"LL{idx-3:03d}"))
        ws.cell(row=idx, column=2, value=lesson.get("source", ""))
        ws.cell(row=idx, column=3, value=lesson.get("summary", ""))
        ws.cell(row=idx, column=4, value=lesson.get("root_cause", ""))
        ws.cell(row=idx, column=5, value=lesson.get("corrective_action", ""))
        ws.cell(row=idx, column=6, value=lesson.get("best_practice", ""))
        ws.cell(row=idx, column=7, value=lesson.get("applicability", ""))

        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=idx, column=col)
            cell.border = BORDER_ALL
            cell.alignment = Alignment(wrap_text=True)
            if (idx - 4) % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="F2F2F2")


def build_categorization(wb, lessons):
    ws = wb.create_sheet("Categorization")

    headers = ["Lesson ID", "Category", "Subcategory"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 20
    ws.column_dimensions["C"].width = 35

    row = 1
    style_title(ws, row, len(headers), "Lesson Categorization")

    row = 3
    style_header(ws, row, headers)

    categories = {"technical": [], "process": [], "tool": [], "organizational": []}

    for idx, lesson in enumerate(lessons, start=4):
        ws.cell(row=idx, column=1, value=lesson.get("id", f"LL{idx-3:03d}"))
        ws.cell(row=idx, column=2, value=lesson.get("category", ""))
        ws.cell(row=idx, column=3, value=lesson.get("subcategory", ""))


def build_distribution_plan(wb, lessons):
    ws = wb.create_sheet("Distribution Plan")

    headers = ["Lesson ID", "Distribution Target", "Delivery Method", "Target Completion"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 25
    ws.column_dimensions["D"].width = 15

    row = 1
    style_title(ws, row, len(headers), "Distribution Plan")

    row = 3
    style_header(ws, row, headers)

    for idx, lesson in enumerate(lessons, start=4):
        ws.cell(row=idx, column=1, value=lesson.get("id", f"LL{idx-3:03d}"))
        ws.cell(row=idx, column=2, value=lesson.get("distribution_target", ""))
        ws.cell(row=idx, column=3, value=lesson.get("delivery_method", ""))
        ws.cell(row=idx, column=4, value=lesson.get("target_completion", ""))


def build_application_tracker(wb):
    ws = wb.create_sheet("Application Tracker")

    headers = ["Lesson ID", "Applied In (Project)", "Application Context", "Application Date", "Effectiveness"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 35
    ws.column_dimensions["D"].width = 12
    ws.column_dimensions["E"].width = 15

    row = 1
    style_title(ws, row, len(headers), "Application Tracker")

    row = 3
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="(Track where lessons have been applied)")
    ws.merge_cells(f"A{row}:E{row}")


def build_trend_analysis(wb):
    ws = wb.create_sheet("Trend Analysis")

    headers = ["Source", "Count", "Trend"]
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 12
    ws.column_dimensions["C"].width = 30

    row = 1
    style_title(ws, row, len(headers), "Trend Analysis")

    row = 3
    style_header(ws, row, headers)

    sources = ["Incident", "Internal Audit", "RCA", "Customer Return"]

    for idx, source in enumerate(sources, start=4):
        ws.cell(row=idx, column=1, value=source)
        ws.cell(row=idx, column=2, value=0)
        ws.cell(row=idx, column=3, value="")


def build_effectiveness_review(wb):
    ws = wb.create_sheet("Effectiveness Review")

    headers = ["Lesson ID", "Effectiveness Assessment", "Review Date", "Status"]
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 15

    row = 1
    style_title(ws, row, len(headers), "Effectiveness Review")

    row = 3
    style_header(ws, row, headers)

    row = 4
    ws.cell(row=row, column=1, value="(Review effectiveness of applied lessons)")
    ws.merge_cells(f"A{row}:D{row}")


def build_references(wb):
    ws = wb.create_sheet("References")
    ws.column_dimensions["A"].width = 50

    row = 1
    style_title(ws, row, 2, "References")

    row = 3
    ws.cell(row=row, column=1, value="ISO 26262-2:2018 Section 5")
    ws.cell(row=row, column=2, value="Organizational learning and continuous improvement")

    row += 1
    ws.cell(row=row, column=1, value="IATF 16949:2016 Section 10.2.4")
    ws.cell(row=row, column=2, value="Lessons learned and management review")


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_ll.py <input.json> <output.xlsx>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with open(input_path) as f:
        data = json.load(f)

    project_info = data.get("project", {})
    lessons = data.get("lessons", [])

    wb = Workbook()

    build_title_page(wb, project_info)
    build_document_control(wb)
    build_lesson_catalog(wb, lessons)
    build_categorization(wb, lessons)
    build_distribution_plan(wb, lessons)
    build_application_tracker(wb)
    build_trend_analysis(wb)
    build_effectiveness_review(wb)
    build_references(wb)

    wb.save(str(output_path))
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
