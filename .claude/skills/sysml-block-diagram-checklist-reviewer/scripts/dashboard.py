"""Dashboard builder for SysML checklist reviewers."""

from openpyxl.styles import Font, PatternFill


def build_dashboard(ws, results_by_tab, start_row=3):
    """Build KPI dashboard in worksheet."""
    navy = "1F3864"
    green_ok = "C6EFCE"
    red_bad = "F8CBAD"
    orange = "FFD966"

    all_results = []
    for tab, checks in results_by_tab.items():
        all_results.extend([r for _, r in checks])

    total = len(all_results)
    fc = sum(1 for r in all_results if r.rating == "FC")
    pc = sum(1 for r in all_results if r.rating == "PC")
    no = sum(1 for r in all_results if r.rating == "NO")
    pending = sum(1 for r in all_results if not r.rating)

    row = start_row
    ws.cell(row=row, column=1, value="TOTAL").font = Font(bold=True, color="FFFFFF")
    ws.cell(row=row, column=1).fill = PatternFill("solid", fgColor=navy)
    ws.cell(row=row + 1, column=1, value=total)

    ws.cell(row=row, column=2, value="COMPLIANT %").font = Font(bold=True, color="FFFFFF")
    ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor=green_ok)
    compliance = int(fc / total * 100) if total > 0 else 0
    ws.cell(row=row + 1, column=2, value=f"{compliance}%")

    ws.cell(row=row, column=3, value="ISSUES").font = Font(bold=True, color="FFFFFF")
    ws.cell(row=row, column=3).fill = PatternFill("solid", fgColor=red_bad)
    ws.cell(row=row + 1, column=3, value=pc + no)

    ws.cell(row=row, column=4, value="PENDING").font = Font(bold=True, color="FFFFFF")
    ws.cell(row=row, column=4).fill = PatternFill("solid", fgColor=orange)
    ws.cell(row=row + 1, column=4, value=pending)

    return row + 3
