"""
TSC Reader - extracts SW partitions, SW-TSRs from a TSC xlsx workbook.
Optional: reads SW components from SW architecture xlsx.

Returns SW component catalog with ASIL, language, partition info.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from openpyxl import load_workbook


def read_tsc(tsc_path: str) -> dict[str, Any]:
    """
    Reads TSC xlsx and extracts:
      - project metadata (name, doc_id, revision, asil)
      - sw_partitions: list of (partition_id, name, asil)
      - sw_tsrs: list of (tsr_id, description, partition_id, asil)

    Returns dict with keys: project, sw_partitions, sw_tsrs
    """
    wb = load_workbook(tsc_path, data_only=True)

    result = {
        "project": {},
        "sw_partitions": [],
        "sw_tsrs": [],
    }

    # Try to extract project metadata from Title Page or assumptions
    if "00_Title_Page" in wb.sheetnames:
        ws = wb["00_Title_Page"]
        for row in ws.iter_rows(min_row=1, max_row=20, values_only=True):
            if row[0] and isinstance(row[0], str):
                if "Project" in row[0]:
                    result["project"]["name"] = row[1] if len(row) > 1 else ""
                elif "Doc ID" in row[0]:
                    result["project"]["doc_id"] = row[1] if len(row) > 1 else ""
                elif "Revision" in row[0]:
                    result["project"]["revision"] = row[1] if len(row) > 1 else ""
                elif "ASIL" in row[0] or "Target ASIL" in row[0]:
                    result["project"]["target_asil"] = row[1] if len(row) > 1 else "D"

    # Extract SW partitions and TSRs from relevant tabs
    # Look for tabs with "Partition", "SW_TSR", "Software" in name
    for sheet_name in wb.sheetnames:
        if "partition" in sheet_name.lower() or "sw_partition" in sheet_name.lower():
            ws = wb[sheet_name]
            for row_idx, row in enumerate(
                ws.iter_rows(min_row=2, values_only=True), start=2
            ):
                if row[0]:  # partition_id
                    partition = {
                        "id": row[0],
                        "name": row[1] if len(row) > 1 else "",
                        "asil": row[2] if len(row) > 2 else "D",
                    }
                    result["sw_partitions"].append(partition)

        if "sw_tsr" in sheet_name.lower() or "software_tsr" in sheet_name.lower():
            ws = wb[sheet_name]
            for row_idx, row in enumerate(
                ws.iter_rows(min_row=2, values_only=True), start=2
            ):
                if row[0]:  # tsr_id
                    tsr = {
                        "id": row[0],
                        "description": row[1] if len(row) > 1 else "",
                        "partition_id": row[2] if len(row) > 2 else "",
                        "asil": row[3] if len(row) > 3 else "D",
                    }
                    result["sw_tsrs"].append(tsr)

    wb.close()
    return result


def read_sw_arch(sw_arch_path: str) -> dict[str, Any]:
    """
    Reads SW architecture xlsx and extracts SW components:
      - swc_id, name, type (Application/Service/Driver/Diagnostic)
      - partition_id, asil, language (C/C++/Python/Ada)

    Returns dict with key: sw_components (list of dicts)
    """
    wb = load_workbook(sw_arch_path, data_only=True)

    result = {"sw_components": []}

    # Look for tab with "Component", "SWC", "Software Component"
    for sheet_name in wb.sheetnames:
        if (
            "component" in sheet_name.lower()
            or "swc" in sheet_name.lower()
            or "architecture" in sheet_name.lower()
        ):
            ws = wb[sheet_name]
            headers = {}
            for col_idx, cell in enumerate(
                ws.iter_rows(min_row=1, max_row=1, values_only=True)[0], start=1
            ):
                if cell:
                    headers[cell.lower()] = col_idx - 1

            for row_idx, row in enumerate(
                ws.iter_rows(min_row=2, values_only=True), start=2
            ):
                if not row or not row[0]:
                    continue
                swc = {
                    "id": row[0],
                    "name": row[1] if len(row) > 1 else "",
                    "type": row[2] if len(row) > 2 else "Application",
                    "partition_id": row[3] if len(row) > 3 else "",
                    "asil": row[4] if len(row) > 4 else "D",
                    "language": row[5] if len(row) > 5 else "C",
                }
                result["sw_components"].append(swc)

    wb.close()
    return result
