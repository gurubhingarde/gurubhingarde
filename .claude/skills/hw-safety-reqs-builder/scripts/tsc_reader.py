"""
TSC Reader — extracts HW-TSRs and architecture from a TSC xlsx produced by tsc-builder.

Usage:
    from tsc_reader import read_tsc
    tsc_data = read_tsc("path/to/TSC.xlsx")
"""

from openpyxl import load_workbook


def read_tsc(tsc_path: str) -> dict:
    """
    Reads a TSC workbook and extracts HW-TSRs, architecture, and metadata.

    Returns:
        dict with keys:
            - item: project metadata (name, doc_id, revision, date, author, approver)
            - hw_tsrs: list of HW-TSR dicts (tsr_id, fsr_id, type, asil, mechanism, text)
            - hw_components: list of HW component dicts
            - sw_partitions: list of SW partition dicts
            - tsc_path: path to source TSC
    """
    wb = load_workbook(tsc_path, data_only=True)

    if "05_TSR_Catalog" not in wb.sheetnames:
        raise ValueError("TSC workbook missing tab '05_TSR_Catalog'.")

    # Extract project metadata from Title Page
    item: dict = {}
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

    # Extract HW-TSRs from TSR Catalog (filter for type == "HW-TSR")
    hw_tsrs: list[dict] = []
    ws = wb["05_TSR_Catalog"]
    for r in range(5, ws.max_row + 1):
        tsr_id = ws.cell(r, 1).value
        if not tsr_id or not str(tsr_id).startswith("TSR-"):
            continue
        tsr_type = str(ws.cell(r, 4).value or "").strip()
        if tsr_type != "HW-TSR":
            continue

        fsr_id = str(ws.cell(r, 2).value or "")
        asil = str(ws.cell(r, 3).value or "QM")
        mechanism = str(ws.cell(r, 5).value or "")
        text = str(ws.cell(r, 7).value or "")

        hw_tsrs.append({
            "tsr_id": str(tsr_id),
            "fsr_id": fsr_id,
            "asil": asil,
            "mechanism": mechanism,
            "text": text,
            "type": tsr_type,
        })

    # Extract HW components from Architecture tab
    hw_components: list[dict] = []
    if "03_System_Architecture" in wb.sheetnames:
        ws = wb["03_System_Architecture"]
        for r in range(5, ws.max_row + 1):
            hw_id = ws.cell(r, 1).value
            if not hw_id:
                break
            hw_id_str = str(hw_id).strip()
            if not hw_id_str.startswith("HW"):
                continue
            hw_components.append({
                "id": hw_id_str,
                "name": str(ws.cell(r, 2).value or ""),
                "part": str(ws.cell(r, 3).value or ""),
                "allocated_nodes": [s.strip() for s in str(ws.cell(r, 4).value or "").split(",") if s.strip()],
                "power_domain": str(ws.cell(r, 5).value or ""),
                "clock_domain": str(ws.cell(r, 6).value or ""),
                "notes": str(ws.cell(r, 7).value or ""),
            })

    # Extract SW partitions from Architecture tab (starts after HW components)
    sw_partitions: list[dict] = []
    if "03_System_Architecture" in wb.sheetnames:
        ws = wb["03_System_Architecture"]
        sw_start = None
        for r in range(5, ws.max_row + 1):
            label = ws.cell(r, 1).value
            if label and "Software Partitions" in str(label):
                sw_start = r + 2
                break
        if sw_start:
            for r in range(sw_start, ws.max_row + 1):
                sp_id = ws.cell(r, 1).value
                if not sp_id:
                    break
                sp_id_str = str(sp_id).strip()
                if not sp_id_str.startswith("SP"):
                    continue
                sw_partitions.append({
                    "id": sp_id_str,
                    "name": str(ws.cell(r, 2).value or ""),
                    "hosted_on": str(ws.cell(r, 3).value or ""),
                    "allocated_nodes": [s.strip() for s in str(ws.cell(r, 4).value or "").split(",") if s.strip()],
                    "rtos": str(ws.cell(r, 5).value or ""),
                    "asil": str(ws.cell(r, 6).value or ""),
                    "notes": str(ws.cell(r, 7).value or ""),
                })

    wb.close()

    return {
        "item": item,
        "hw_tsrs": hw_tsrs,
        "hw_components": hw_components,
        "sw_partitions": sw_partitions,
        "tsc_path": tsc_path,
    }
