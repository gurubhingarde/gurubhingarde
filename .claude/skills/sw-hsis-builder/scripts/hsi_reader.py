"""
HSI Reader — extracts signal catalog from hsi-builder xlsx.

Usage:
    from hsi_reader import read_hsi_signals
    signals = read_hsi_signals("hsi.xlsx")

Reads the 02_HSI_Signal_Catalog tab from an HSI workbook produced by hsi-builder.
Returns list of dicts with keys: signal_name, direction, data_type, bit_width, range,
units, default_value, encoding_rules, integrity_protection, validity_bit, allocated_asil,
linked_fsr, mechanism.
"""

from pathlib import Path
from typing import Any

from openpyxl import load_workbook


def read_hsi_signals(hsi_path: str) -> list[dict[str, Any]]:
    """Extract HSI signal catalog from hsi-builder xlsx."""
    wb = load_workbook(hsi_path, data_only=True)

    # Try to find the signal catalog tab
    ws = None
    for sheet_name in wb.sheetnames:
        if "02" in sheet_name and "Signal" in sheet_name:
            ws = wb[sheet_name]
            break

    if not ws:
        raise ValueError(f"Could not find HSI signal catalog tab in {hsi_path}")

    signals = []

    # Header row is typically row 4
    # Columns: Signal Name, Direction, Data Type, Bit Width, Range, Units, Default,
    #          Encoding Rules, Integrity Protection, Validity Bit, Allocated ASIL

    for row_idx in range(5, ws.max_row + 1):
        signal_name = ws.cell(row=row_idx, column=1).value
        if not signal_name:
            break

        direction = ws.cell(row=row_idx, column=2).value or ""
        data_type = ws.cell(row=row_idx, column=3).value or "bit"
        bit_width = ws.cell(row=row_idx, column=4).value or 1
        range_val = ws.cell(row=row_idx, column=5).value or ""
        units = ws.cell(row=row_idx, column=6).value or ""
        default_value = ws.cell(row=row_idx, column=7).value or "0"
        encoding_rules = ws.cell(row=row_idx, column=8).value or ""
        integrity_prot = ws.cell(row=row_idx, column=9).value or "None"
        validity_bit = ws.cell(row=row_idx, column=10).value or ""
        allocated_asil = ws.cell(row=row_idx, column=11).value or "QM"

        # Try to extract from 07_Cross_Reference if available
        linked_fsr = ""
        mechanism = ""
        try:
            for sheet_name in wb.sheetnames:
                if "07" in sheet_name and "Cross" in sheet_name:
                    xref = wb[sheet_name]
                    for xref_row in range(5, xref.max_row + 1):
                        if xref.cell(row=xref_row, column=1).value == signal_name:
                            linked_fsr = xref.cell(row=xref_row, column=2).value or ""
                            mechanism = xref.cell(row=xref_row, column=4).value or ""
                            break
        except:
            pass

        signals.append({
            "signal_name": str(signal_name),
            "direction": direction,
            "data_type": data_type,
            "bit_width": bit_width,
            "range": range_val,
            "units": units,
            "default_value": default_value,
            "encoding_rules": encoding_rules,
            "integrity_protection": integrity_prot,
            "validity_bit": validity_bit,
            "allocated_asil": allocated_asil,
            "linked_fsr": linked_fsr,
            "mechanism": mechanism,
        })

    return signals


def read_hsi_timing(hsi_path: str) -> dict[str, dict[str, Any]]:
    """Extract timing constraints from 04_Timing_Specification tab."""
    wb = load_workbook(hsi_path, data_only=True)

    ws = None
    for sheet_name in wb.sheetnames:
        if "04" in sheet_name and "Timing" in sheet_name:
            ws = wb[sheet_name]
            break

    if not ws:
        return {}

    timing_by_signal = {}

    # Header row is typically row 4
    # Columns: Signal Name, Sample Rate (Hz), Max Age (ms), Latency HW->SW (ms),
    #          Latency SW->HW (ms), Detection Time (ms), Settling Time (ms)

    for row_idx in range(5, ws.max_row + 1):
        signal_name = ws.cell(row=row_idx, column=1).value
        if not signal_name:
            break

        timing_by_signal[str(signal_name)] = {
            "sample_rate_hz": ws.cell(row=row_idx, column=2).value,
            "max_age_ms": ws.cell(row=row_idx, column=3).value,
            "latency_hw_to_sw_ms": ws.cell(row=row_idx, column=4).value,
            "latency_sw_to_hw_ms": ws.cell(row=row_idx, column=5).value,
            "detection_time_ms": ws.cell(row=row_idx, column=6).value,
            "settling_time_ms": ws.cell(row=row_idx, column=7).value,
        }

    return timing_by_signal


def read_hsi_failure_modes(hsi_path: str) -> dict[str, list[str]]:
    """Extract failure modes from 05_Failure_Modes_and_Reactions tab."""
    wb = load_workbook(hsi_path, data_only=True)

    ws = None
    for sheet_name in wb.sheetnames:
        if "05" in sheet_name and "Failure" in sheet_name:
            ws = wb[sheet_name]
            break

    if not ws:
        return {}

    modes_by_signal = {}

    # Header row is typically row 4
    # Columns: Signal Name, Possible Faults, Detection Method, SW Reaction, ...

    for row_idx in range(5, ws.max_row + 1):
        signal_name = ws.cell(row=row_idx, column=1).value
        fault_mode = ws.cell(row=row_idx, column=2).value

        if signal_name:
            signal_name = str(signal_name)
            if signal_name not in modes_by_signal:
                modes_by_signal[signal_name] = []
            if fault_mode:
                modes_by_signal[signal_name].append(str(fault_mode))

    return modes_by_signal
