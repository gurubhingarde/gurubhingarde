"""
TSC Reader — extracts HW components and SW partitions from TSC xlsx.

Usage:
    from tsc_reader import read_tsc
    tsc_data = read_tsc("path/to/tsc.xlsx")
    print(tsc_data["hw_components"])
"""

from pathlib import Path
from openpyxl import load_workbook


def read_tsc(tsc_path: str) -> dict:
    """
    Reads a TSC xlsx and extracts:
    - Item metadata (project, doc_id, revision, date, author, approver)
    - FSRs with allocated ASIL
    - TSC nodes
    - HW components and SW partitions from architecture tab
    - Safety mechanisms from catalog
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
                "branch": str(ws.cell(r, 4).value or ""),
                "node_ref": str(ws.cell(r, 5).value or ""),
                "fsr_text": str(ws.cell(r, 6).value or ""),
                "ftti_ms": ws.cell(r, 7).value,
            })

    # Extract HW components and SW partitions from 03_System_Architecture
    hw_components: list[dict] = []
    sw_partitions: list[dict] = []
    if "03_System_Architecture" in wb.sheetnames:
        ws = wb["03_System_Architecture"]
        # Find the HW components header row
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
                    allocated_nodes_str = str(ws.cell(r, 4).value or "")
                    allocated_nodes = [n.strip() for n in allocated_nodes_str.split(",") if n.strip()]
                    hw_components.append({
                        "id": str(hw_id),
                        "name": str(ws.cell(r, 2).value or ""),
                        "part": str(ws.cell(r, 3).value or ""),
                        "allocated_nodes": allocated_nodes,
                        "power_domain": str(ws.cell(r, 5).value or ""),
                        "clock_domain": str(ws.cell(r, 6).value or ""),
                        "notes": str(ws.cell(r, 7).value or ""),
                    })

        # Read SW partitions
        if sw_header_row:
            for r in range(sw_header_row + 1, ws.max_row + 1):
                sp_id = ws.cell(r, 1).value
                if not sp_id:
                    break
                if sp_id:
                    allocated_nodes_str = str(ws.cell(r, 4).value or "")
                    allocated_nodes = [n.strip() for n in allocated_nodes_str.split(",") if n.strip()]
                    sw_partitions.append({
                        "id": str(sp_id),
                        "name": str(ws.cell(r, 2).value or ""),
                        "hosted_on": str(ws.cell(r, 3).value or ""),
                        "allocated_nodes": allocated_nodes,
                        "rtos": str(ws.cell(r, 5).value or ""),
                        "asil": str(ws.cell(r, 6).value or ""),
                        "notes": str(ws.cell(r, 7).value or ""),
                    })

    # Extract HW-TSRs from 05_TSR_Catalog
    hw_tsrs: list[dict] = []
    if "05_TSR_Catalog" in wb.sheetnames:
        ws = wb["05_TSR_Catalog"]
        for r in range(5, ws.max_row + 1):
            tsr_id = ws.cell(r, 1).value
            tsr_type = str(ws.cell(r, 4).value or "")
            if not tsr_id or "HW" not in tsr_type:
                continue
            hw_tsrs.append({
                "tsr_id": str(tsr_id),
                "fsr_id": str(ws.cell(r, 2).value or ""),
                "asil": str(ws.cell(r, 3).value or ""),
                "mechanism": str(ws.cell(r, 5).value or ""),
                "text": str(ws.cell(r, 7).value or ""),
            })

    # Extract safety mechanisms from 04_Safety_Mechanism_Catalog
    mechanisms: list[dict] = []
    if "04_Safety_Mechanism_Catalog" in wb.sheetnames:
        ws = wb["04_Safety_Mechanism_Catalog"]
        seen_mechanisms = set()
        for r in range(5, ws.max_row + 1):
            mech_id = ws.cell(r, 5).value
            if not mech_id or str(mech_id) in seen_mechanisms:
                continue
            mech_name = str(ws.cell(r, 6).value or "")
            if mech_id and mech_name:
                seen_mechanisms.add(str(mech_id))
                mechanisms.append({
                    "id": str(mech_id),
                    "name": mech_name,
                    "dc": str(ws.cell(r, 7).value or ""),
                    "detection_time": str(ws.cell(r, 8).value or ""),
                })

    wb.close()

    return {
        "tsc_path": tsc_path,
        "item": item,
        "fsrs": fsrs,
        "hw_components": hw_components,
        "sw_partitions": sw_partitions,
        "hw_tsrs": hw_tsrs,
        "mechanisms": mechanisms,
    }


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python tsc_reader.py <tsc.xlsx>", file=sys.stderr)
        sys.exit(2)

    data = read_tsc(sys.argv[1])
    print(json.dumps({
        "hw_components_count": len(data["hw_components"]),
        "sw_partitions_count": len(data["sw_partitions"]),
        "fsrs_count": len(data["fsrs"]),
        "mechanisms_count": len(data["mechanisms"]),
    }, indent=2))
