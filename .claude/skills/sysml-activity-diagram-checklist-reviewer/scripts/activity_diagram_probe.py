from dataclasses import dataclass, field
from pathlib import Path
from openpyxl import load_workbook

@dataclass
class ProbeResult:
    file_path: str = ""
    sheet_names: list = field(default_factory=list)
    is_builder_format: bool = False
    element_count: int = 0

def probe(file_path):
    file_path = Path(file_path)
    wb = load_workbook(file_path, data_only=True)
    return ProbeResult(
        file_path=str(file_path),
        sheet_names=list(wb.sheetnames),
        is_builder_format=any(s.startswith("0") for s in wb.sheetnames) if wb.sheetnames else False,
    )
