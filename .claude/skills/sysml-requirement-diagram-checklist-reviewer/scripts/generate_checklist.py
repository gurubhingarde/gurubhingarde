import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_checklist.py <input.xlsx> [output.xlsx]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2] if len(sys.argv) > 2 else input_file.stem + "_checklist.xlsx")
    
    wb = Workbook()
    ws = wb.active
    ws.title = "0_Title"
    ws.cell(row=1, column=1, value=f"Checklist for {input_file.name}")
    wb.save(output_file)
    print(f"Checklist saved to {output_file}")
