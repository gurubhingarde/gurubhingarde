"""
TSC Reader — extracts SW partitions, FSRs, SW-TSRs from TSC xlsx for SW Architecture refinement.

Usage:
    from tsc_reader import read_tsc
    tsc_data = read_tsc("path/to/tsc.xlsx")
    print(tsc_data["sw_partitions"])
    print(tsc_data["fsrs"])
"""

from pathlib import Path
from openpyxl import load_workbook


def read_tsc(tsc_path: str) -> dict:
    """
    Reads a TSC xlsx and extracts SW architecture context:
    - Item metadata (project, doc_id, revision, date, author, approver)
    - FSRs with allocated ASIL
    - SW partitions from architecture tab
    - HW components (for partition housing)
    - Safety mechanisms from catalog (for mechanism allocation)
    """
    wb = load_workbook(tsc_path, data_only=True)

    # Extract item metadata
    item: dict[str, str] = {}
    if "00_Title_Page" in wb.sheetnames:
        ws = wb["00_Title_Page"]
        for r in range(6, 25):
            label = ws.cell(r, 2).value
            value = ws.cell(r, 3).value
            if label and value:
                item[str(label).strip()] = str(value).strip()
        title_text = ws.cell(3, 1).value
        if title_text:
            item["Item Title"] = str(title_text)

    # Extract FSRs from 02_FSRs_From_FSC
    fsrs: list[dict] = []
    if "02_FSRs_From_FSC" in wb.sheetnames:
        ws = wb["02_FSRs_From_FSC"]
        for r in range(5, ws.max_row + 1):
            fsr_id = ws.cell(r, 1).value
            if not fsr_id or not str(fsr_id).startswith("FSR-"):
                continue
            fsrs.append({
                "fsr_id": str(fsr_id),
                "sg_id": str(ws.cell(r, 2).value or ""),
                "asil": str(ws.cell(r, 3).value or "QM"),
                "fsr_text": str(ws.cell(r, 6).value or ""),
                "ftti_ms": ws.cell(r, 7).value,
            })

    # Extract SW partitions from 03_System_Architecture
    sw_partitions: list[dict] = []
    hw_components: list[dict] = []
    if "03_System_Architecture" in wb.sheetnames:
        ws = wb["03_System_Architecture"]

        # Find header rows
        hw_header_row = None
        sw_header_row = None
        for r in range(1, ws.max_row + 1):
            cell_val = str(ws.cell(r, 1).value or "").lower()
            if "hw component" in cell_val and "id" in cell_val:
                hw_header_row = r
            if "sw partition" in cell_val and "id" in cell_val:
                sw_header_row = r

        # Read HW components
        if hw_header_row:
            for r in range(hw_header_row + 1, ws.max_row + 1):
                hw_id = ws.cell(r, 1).value
                if not hw_id or (str(hw_id).startswith("SW") or str(hw_id).lower().startswith("software")):
                    break
                if hw_id:
                    hw_components.append({
                        "id": str(hw_id),
                        "name": str(ws.cell(r, 2).value or ""),
                        "part": str(ws.cell(r, 3).value or ""),
                        "notes": str(ws.cell(r, 7).value or ""),
                    })

        # Read SW partitions
        if sw_header_row:
            for r in range(sw_header_row + 1, ws.max_row + 1):
                sp_id = ws.cell(r, 1).value
                if not sp_id:
                    break
                allocated_nodes_str = str(ws.cell(r, 4).value or "")
                allocated_nodes = [n.strip() for n in allocated_nodes_str.split(",") if n.strip()]
                sw_partitions.append({
                    "id": str(sp_id),
                    "name": str(ws.cell(r, 2).value or ""),
                    "type": str(ws.cell(r, 3).value or "Partition"),
                    "allocated_nodes": allocated_nodes,
                    "asil": str(ws.cell(r, 5).value or "QM"),
                    "notes": str(ws.cell(r, 6).value or ""),
                })

    # Extract TSR catalog (both HW-TSR and SW-TSR)
    sw_tsrs: list[dict] = []
    if "05_TSR_Catalog" in wb.sheetnames:
        ws = wb["05_TSR_Catalog"]
        for r in range(5, ws.max_row + 1):
            tsr_id = ws.cell(r, 1).value
            if not tsr_id or not str(tsr_id).startswith("TSR-"):
                continue
            tsr_type = str(ws.cell(r, 2).value or "")
            if "SW" in tsr_type:
                sw_tsrs.append({
                    "tsr_id": str(tsr_id),
                    "type": tsr_type,
                    "fsr_ref": str(ws.cell(r, 3).value or ""),
                    "text": str(ws.cell(r, 4).value or ""),
                    "asil": str(ws.cell(r, 5).value or "QM"),
                    "mechanism_ref": str(ws.cell(r, 6).value or ""),
                })

    # Extract safety mechanisms from 04_Safety_Mechanism_Catalog
    mechanisms: list[dict] = []
    if "04_Safety_Mechanism_Catalog" in wb.sheetnames:
        ws = wb["04_Safety_Mechanism_Catalog"]
        for r in range(5, ws.max_row + 1):
            mech_id = ws.cell(r, 1).value
            if not mech_id:
                continue
            mechanisms.append({
                "id": str(mech_id),
                "name": str(ws.cell(r, 2).value or ""),
                "branch": str(ws.cell(r, 3).value or ""),
                "dc": str(ws.cell(r, 4).value or ""),
                "detection_time": str(ws.cell(r, 5).value or ""),
                "implementation": str(ws.cell(r, 6).value or ""),
                "notes": str(ws.cell(r, 7).value or ""),
            })

    return {
        "item": item,
        "fsrs": fsrs,
        "sw_partitions": sw_partitions,
        "hw_components": hw_components,
        "sw_tsrs": sw_tsrs,
        "mechanisms": mechanisms,
    }
