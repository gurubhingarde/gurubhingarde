from openpyxl.styles import Font, PatternFill

def build_dashboard(ws, results_by_tab, start_row=3):
    navy = "1F3864"
    green_ok = "C6EFCE"
    red_bad = "F8CBAD"
    orange = "FFD966"
    
    all_results = []
    for tab, checks in results_by_tab.items():
        all_results.extend([r for _, r in checks])
    
    total = len(all_results)
    fc = sum(1 for r in all_results if r.rating == "FC")
    
    ws.cell(row=start_row, column=1, value="TOTAL").fill = PatternFill("solid", fgColor=navy)
    ws.cell(row=start_row + 1, column=1, value=total)
    ws.cell(row=start_row, column=2, value="COMPLIANT %").fill = PatternFill("solid", fgColor=green_ok)
    compliance = int(fc / total * 100) if total > 0 else 0
    ws.cell(row=start_row + 1, column=2, value=f"{compliance}%")
    
    return start_row + 3
