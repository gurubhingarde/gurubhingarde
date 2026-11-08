"""
TSC Reader — extracts HSI signals from TSC xlsx (06_HSI_Specification tab).

This module reads a pre-existing HSI scaffold from a TSC workbook produced by
tsc-builder. It provides the canonical HSI signal catalog that will be refined
into the formal contract-grade HSI specification.
"""

from openpyxl import load_workbook


def read_hsi_signals(tsc_path: str) -> list[dict]:
    """
    Reads the 06_HSI_Specification tab from a TSC xlsx and returns a list of signal dicts.

    Each signal dict contains:
    - signal_name: e.g. 'esc.diag.lockstep_mismatch'
    - direction: 'HW -> SW' or 'SW -> HW'
    - linked_fsr: FSR_ID
    - mechanism: mechanism name and ID
    - encoding: bit width and encoding rule
    - update_rate: update frequency
    - integrity_protection: protection method (Parity, CRC, etc.)
    - failure_reaction: SW or HW reaction on failure
    - allocated_asil: ASIL letter
    """
    wb = load_workbook(tsc_path, data_only=True)
    if "06_HSI_Specification" not in wb.sheetnames:
        raise ValueError("TSC workbook missing tab '06_HSI_Specification'.")

    signals = []
    ws = wb["06_HSI_Specification"]
    for row in range(5, ws.max_row + 1):
        sig_name = ws.cell(row, 1).value
        if not sig_name or str(sig_name).startswith("<"):
            continue
        signals.append({
            "signal_name": str(sig_name),
            "direction": str(ws.cell(row, 2).value or ""),
            "linked_fsr": str(ws.cell(row, 3).value or ""),
            "mechanism": str(ws.cell(row, 4).value or ""),
            "encoding": str(ws.cell(row, 5).value or ""),
            "update_rate": str(ws.cell(row, 6).value or ""),
            "integrity_protection": str(ws.cell(row, 7).value or ""),
            "failure_reaction": str(ws.cell(row, 8).value or ""),
            "allocated_asil": str(ws.cell(row, 9).value or "QM"),
        })
    wb.close()
    return signals


if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) != 2:
        print("Usage: python tsc_reader.py <tsc.xlsx>", file=sys.stderr)
        sys.exit(2)
    sigs = read_hsi_signals(sys.argv[1])
    print(json.dumps(sigs, indent=2))
