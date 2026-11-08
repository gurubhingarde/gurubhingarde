"""
Visual dashboard for the Summary tab of any checklist reviewer skill.

Renders:
- KPI tiles (Total / Compliant% / Pending / Major Issues)
- Pie chart of rating distribution (FC / LC / PC / NO / NA / Pending)
- Horizontal bar chart of compliance % per checklist tab
- Stacked bar chart of rating breakdown per section
- Findings table (NO and PC items)

The build_dashboard function consumes a `results` dict shaped:
    { tab_code (str): [(check_def, check_result), ...] }

where check_def has .id, .tab, .section, .requirement, .obligation
and check_result has .rating, .finding, .recommended_action.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.chart.marker import DataPoint
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# ---------------------------------------------------------------------------
# Style constants
# ---------------------------------------------------------------------------

FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"
GREEN_OK = "C6EFCE"
RED_BAD = "F8CBAD"
ORANGE_PARTIAL = "FFD966"
GREY = "D0CECE"

# Rating colors for chart slices (must be hex strings without #)
RATING_COLORS = {
    "FC": "70AD47",
    "LC": "9DC3E6",
    "PC": "FFC000",
    "NO": "C00000",
    "NA": "BFBFBF",
    "PENDING": "404040",
}

THIN = Side(border_style="thin", color="BFBFBF")
MEDIUM = Side(border_style="medium", color="404040")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
BORDER_HEAVY = Border(left=MEDIUM, right=MEDIUM, top=MEDIUM, bottom=MEDIUM)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _kpi_tile(ws, anchor_row: int, anchor_col: int, label: str, value: str, value_color: str = NAVY):
    """Render a 2x4 KPI tile starting at (row, col)."""
    # Border around the tile (5 columns wide, 3 rows tall)
    last_col = anchor_col + 4
    last_row = anchor_row + 2
    for r in range(anchor_row, last_row + 1):
        for c in range(anchor_col, last_col + 1):
            ws.cell(row=r, column=c).border = BORDER_HEAVY

    # Label row
    ws.merge_cells(start_row=anchor_row, start_column=anchor_col, end_row=anchor_row, end_column=last_col)
    label_cell = ws.cell(row=anchor_row, column=anchor_col, value=label)
    label_cell.font = Font(name=FONT_NAME, size=10, bold=True, color="FFFFFF")
    label_cell.fill = PatternFill("solid", fgColor=NAVY)
    label_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[anchor_row].height = 18

    # Value rows (merged, big)
    ws.merge_cells(start_row=anchor_row + 1, start_column=anchor_col, end_row=last_row, end_column=last_col)
    val_cell = ws.cell(row=anchor_row + 1, column=anchor_col, value=value)
    val_cell.font = Font(name=FONT_NAME, size=20, bold=True, color=value_color)
    val_cell.alignment = Alignment(horizontal="center", vertical="center")
    val_cell.fill = PatternFill("solid", fgColor="FFFFFF")
    ws.row_dimensions[anchor_row + 1].height = 22
    ws.row_dimensions[anchor_row + 2].height = 22


def _color_data_points(chart, color_seq: list[str]):
    """Apply per-slice / per-bar colors from a sequence."""
    from openpyxl.chart.shapes import GraphicalProperties
    from openpyxl.drawing.fill import ColorChoice
    series = chart.series[0]
    series.dPt = []
    for i, color in enumerate(color_seq):
        pt = DataPoint(idx=i)
        pt.graphicalProperties = GraphicalProperties(solidFill=color)
        series.dPt.append(pt)


def _scoring_label(rating: str) -> str:
    """Short label for charts."""
    return {"FC": "Fully Compliant", "LC": "Largely Compliant", "PC": "Partially Compliant",
            "NO": "Not Compliant", "NA": "Not Applicable", "PENDING": "Pending Review"}.get(rating, rating)


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_dashboard(ws, results: dict, project_label: str = "", checklist_label: str = "Confirmation Measures Checklist"):
    """
    Replace ws contents with a visual dashboard summarizing `results`.
    The caller has already created the worksheet (no overwrite of name).
    """
    ws.sheet_view.showGridLines = False

    # ---- Title banner ----
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=22)
    title_cell = ws.cell(row=1, column=1, value=f"{checklist_label} — Dashboard")
    title_cell.font = Font(name=FONT_NAME, size=18, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill("solid", fgColor=NAVY)
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 36

    if project_label:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=22)
        sub = ws.cell(row=2, column=1, value=project_label)
        sub.font = Font(name=FONT_NAME, size=11, italic=True, color=NAVY)
        sub.alignment = Alignment(horizontal="center", vertical="center")
        ws.row_dimensions[2].height = 22

    # ---- Aggregate metrics ----
    all_results = []
    for tab, items in results.items():
        for c, r in items:
            all_results.append((tab, c, r))

    total_items = len(all_results)
    n_fc = sum(1 for _, _, r in all_results if r.rating == "FC")
    n_lc = sum(1 for _, _, r in all_results if r.rating == "LC")
    n_pc = sum(1 for _, _, r in all_results if r.rating == "PC")
    n_no = sum(1 for _, _, r in all_results if r.rating == "NO")
    n_na = sum(1 for _, _, r in all_results if r.rating == "NA")
    n_pending = sum(1 for _, _, r in all_results if r.rating in ("", None))
    n_applicable = max(1, total_items - n_na)
    n_compliant = n_fc + n_lc  # FC + LC count as compliant
    compliance_pct = n_compliant / n_applicable * 100 if n_applicable else 0
    n_major = sum(1 for _, c, r in all_results if r.rating == "NO" and c.obligation == "Shall")
    n_minor = sum(1 for _, c, r in all_results if r.rating == "NO" and c.obligation == "Should")

    # Determine status color / label
    if n_major > 0:
        status_label = "REJECTED"
        status_color = "C00000"
    elif n_no > 0 or n_pc > 0:
        status_label = "CONDITIONAL APPROVAL"
        status_color = "ED7D31"
    elif n_pending > 0:
        status_label = "PENDING REVIEW"
        status_color = "404040"
    else:
        status_label = "APPROVED"
        status_color = "548235"

    # ---- KPI tiles row (rows 4-6) ----
    _kpi_tile(ws, 4, 1, "Total Items", str(total_items), NAVY)
    _kpi_tile(ws, 4, 6, "Compliance %", f"{compliance_pct:.0f}%", "548235" if compliance_pct >= 80 else ("ED7D31" if compliance_pct >= 50 else "C00000"))
    _kpi_tile(ws, 4, 11, "Pending Review", str(n_pending), "404040")
    _kpi_tile(ws, 4, 16, "Major Issues", str(n_major), "C00000" if n_major > 0 else "548235")

    # ---- Status banner (row 8) ----
    ws.merge_cells(start_row=8, start_column=1, end_row=8, end_column=20)
    status_cell = ws.cell(row=8, column=1, value=f"OVERALL STATUS: {status_label}")
    status_cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    status_cell.fill = PatternFill("solid", fgColor=status_color)
    status_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[8].height = 32

    # ---- Pie chart data (rating distribution) — written hidden in cols Y..Z ----
    pie_data_start = 4
    pie_labels = ["FC", "LC", "PC", "NO", "NA", "PENDING"]
    pie_counts = [n_fc, n_lc, n_pc, n_no, n_na, n_pending]
    # Filter out zero entries to avoid cluttered legend, but keep ordering
    visible_labels = []
    visible_counts = []
    visible_colors = []
    for label, count in zip(pie_labels, pie_counts):
        if count > 0:
            visible_labels.append(_scoring_label(label))
            visible_counts.append(count)
            visible_colors.append(RATING_COLORS[label])

    for i, (lbl, cnt) in enumerate(zip(visible_labels, visible_counts), start=pie_data_start):
        ws.cell(row=i, column=25, value=lbl)
        ws.cell(row=i, column=26, value=cnt)

    if visible_counts:
        pie = PieChart()
        pie.title = "Rating Distribution"
        labels_ref = Reference(ws, min_col=25, min_row=pie_data_start, max_row=pie_data_start + len(visible_labels) - 1)
        data_ref = Reference(ws, min_col=26, min_row=pie_data_start, max_row=pie_data_start + len(visible_counts) - 1)
        pie.add_data(data_ref, titles_from_data=False)
        pie.set_categories(labels_ref)
        pie.dataLabels = DataLabelList(showPercent=True, showCatName=True)
        pie.height = 9
        pie.width = 14
        try:
            _color_data_points(pie, visible_colors)
        except Exception:
            pass
        ws.add_chart(pie, "A11")

    # ---- Bar chart: compliance % per tab ----
    bar_data_start = 4
    bar_row = bar_data_start
    tab_labels = []
    tab_compliance = []
    for tab_code, items in results.items():
        ratings = Counter(r.rating for _, r in items)
        applicable = max(1, sum(ratings.values()) - ratings["NA"])
        compliant = ratings["FC"] + ratings["LC"]
        pct = compliant / applicable * 100 if applicable else 0
        tab_labels.append(tab_code)
        tab_compliance.append(round(pct, 1))
        ws.cell(row=bar_row, column=28, value=tab_code)
        ws.cell(row=bar_row, column=29, value=pct)
        bar_row += 1

    if tab_labels:
        bar = BarChart()
        bar.type = "bar"
        bar.style = 11
        bar.title = "Compliance % by Tab"
        bar.y_axis.title = None
        bar.x_axis.title = "Compliance %"
        bar.x_axis.scaling.min = 0
        bar.x_axis.scaling.max = 100
        labels_ref = Reference(ws, min_col=28, min_row=bar_data_start, max_row=bar_data_start + len(tab_labels) - 1)
        data_ref = Reference(ws, min_col=29, min_row=bar_data_start, max_row=bar_data_start + len(tab_labels) - 1)
        bar.add_data(data_ref, titles_from_data=False)
        bar.set_categories(labels_ref)
        bar.legend = None
        bar.dataLabels = DataLabelList(showVal=True)
        bar.height = 9
        bar.width = 14
        ws.add_chart(bar, "L11")

    # ---- Stacked bar: rating breakdown by section ----
    section_data: dict[str, Counter] = defaultdict(Counter)
    section_order: list[str] = []
    for tab_code, items in results.items():
        for c, r in items:
            key = f"{tab_code}: {c.section}"
            if key not in section_order:
                section_order.append(key)
            section_data[key][r.rating or "PENDING"] += 1

    stack_data_start = 30
    # Header row
    stack_categories = ["FC", "LC", "PC", "NO", "NA", "PENDING"]
    ws.cell(row=stack_data_start - 1, column=28, value="Section")
    for ci, cat in enumerate(stack_categories):
        ws.cell(row=stack_data_start - 1, column=29 + ci, value=_scoring_label(cat))
    for ri, section in enumerate(section_order):
        r = stack_data_start + ri
        ws.cell(row=r, column=28, value=section)
        counts = section_data[section]
        for ci, cat in enumerate(stack_categories):
            ws.cell(row=r, column=29 + ci, value=counts.get(cat, 0))

    if section_order:
        stack = BarChart()
        stack.type = "bar"
        stack.style = 12
        stack.grouping = "stacked"
        stack.overlap = 100
        stack.title = "Rating Breakdown by Section"
        labels_ref = Reference(ws, min_col=28, min_row=stack_data_start, max_row=stack_data_start + len(section_order) - 1)
        data_ref = Reference(ws, min_col=29, min_row=stack_data_start - 1, max_col=29 + len(stack_categories) - 1, max_row=stack_data_start + len(section_order) - 1)
        stack.add_data(data_ref, titles_from_data=True)
        stack.set_categories(labels_ref)
        stack.legend.position = "b"
        stack.height = max(8, 0.5 * len(section_order) + 6)
        stack.width = 28
        # Color each series
        try:
            from openpyxl.chart.shapes import GraphicalProperties
            for s_idx, cat in enumerate(stack_categories):
                if s_idx < len(stack.series):
                    stack.series[s_idx].graphicalProperties = GraphicalProperties(solidFill=RATING_COLORS[cat])
        except Exception:
            pass
        ws.add_chart(stack, "A29")

    # ---- Findings table (NO + PC items) ----
    findings_start = 60
    ws.merge_cells(start_row=findings_start, start_column=1, end_row=findings_start, end_column=22)
    title = ws.cell(row=findings_start, column=1, value="Findings — Non-Conformances and Partial Compliance")
    title.font = Font(name=FONT_NAME, size=12, bold=True, color="FFFFFF")
    title.fill = PatternFill("solid", fgColor=NAVY)
    title.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[findings_start].height = 22

    # Headers
    headers = ["Tab", "ID", "Obligation", "Rating", "Requirement", "Finding", "Recommended Action"]
    header_row = findings_start + 1
    for ci, h in enumerate(headers, start=1):
        cell = ws.cell(row=header_row, column=ci, value=h)
        cell.font = Font(name=FONT_NAME, size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[header_row].height = 28

    row = header_row + 1
    for tab_code, items in results.items():
        for c, r in items:
            if r.rating not in ("NO", "PC"):
                continue
            ws.cell(row=row, column=1, value=tab_code)
            ws.cell(row=row, column=2, value=c.id)
            ws.cell(row=row, column=3, value=c.obligation)
            rating_cell = ws.cell(row=row, column=4, value=r.rating)
            rating_cell.fill = PatternFill("solid", fgColor=RED_BAD if r.rating == "NO" else ORANGE_PARTIAL)
            rating_cell.font = Font(name=FONT_NAME, bold=True, size=10, color="C00000" if r.rating == "NO" else "806000")
            rating_cell.alignment = Alignment(horizontal="center")
            ws.cell(row=row, column=5, value=c.requirement)
            ws.cell(row=row, column=6, value=r.finding)
            ws.cell(row=row, column=7, value=r.recommended_action)
            for cc in range(1, 8):
                cell = ws.cell(row=row, column=cc)
                if cc != 4:
                    cell.font = Font(name=FONT_NAME, size=10)
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                cell.border = BORDER_ALL
            row += 1
    if row == header_row + 1:
        # No findings — green note
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=7)
        cell = ws.cell(row=row, column=1, value="No NO or PC findings — all checks either compliant or pending review.")
        cell.font = Font(name=FONT_NAME, size=11, italic=True, color="548235")
        cell.fill = PatternFill("solid", fgColor=GREEN_OK)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER_ALL

    # ---- Column widths ----
    for ci, w in enumerate([10, 10, 12, 10, 50, 60, 50], start=1):
        ws.column_dimensions[get_column_letter(ci)].width = w
    # Hide helper data columns
    for col in range(25, 36):
        ws.column_dimensions[get_column_letter(col)].hidden = True

    return {
        "total": total_items,
        "compliance_pct": compliance_pct,
        "major": n_major,
        "minor": n_minor,
        "pending": n_pending,
        "status": status_label,
    }
