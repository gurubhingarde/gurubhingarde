"""ODX content probing utility for best-effort introspection of ODX workbooks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


@dataclass
class ProbedODX:
    """Probed ODX content from xlsx."""
    base_variants: list[dict[str, Any]]
    derived_variants: list[dict[str, Any]]
    services: list[dict[str, Any]]
    pdus: list[dict[str, Any]]
    dtcs: list[dict[str, Any]]
    data_objects: list[dict[str, Any]]
    odx_layers: list[dict[str, Any]]


def probe(odx_path: str | Path) -> ProbedODX:
    """Probe an ODX workbook and extract content."""
    wb = load_workbook(odx_path)

    base_variants = _probe_base_variants(wb)
    derived_variants = _probe_derived_variants(wb)
    services = _probe_services(wb)
    pdus = _probe_pdus(wb)
    dtcs = _probe_dtcs(wb)
    data_objects = _probe_data_objects(wb)
    odx_layers = _probe_odx_layers(wb)

    return ProbedODX(
        base_variants=base_variants,
        derived_variants=derived_variants,
        services=services,
        pdus=pdus,
        dtcs=dtcs,
        data_objects=data_objects,
        odx_layers=odx_layers,
    )


def _probe_base_variants(wb) -> list[dict[str, Any]]:
    if "Base Variant Definition" not in wb.sheetnames:
        return []

    ws = wb["Base Variant Definition"]
    variants = []

    for row in ws.iter_rows(min_row=4, values_only=True):
        if row[0]:
            variants.append({
                "id": row[0],
                "name": row[1],
                "ecu_id": row[2],
                "interfaces": row[3] or "",
            })

    return variants


def _probe_derived_variants(wb) -> list[dict[str, Any]]:
    if "Derived Variants" not in wb.sheetnames:
        return []

    ws = wb["Derived Variants"]
    variants = []

    for row in ws.iter_rows(min_row=4, values_only=True):
        if row[0]:
            variants.append({
                "id": row[0],
                "name": row[1],
                "parent_variant_id": row[2],
                "specializations": row[3] or "",
            })

    return variants


def _probe_services(wb) -> list[dict[str, Any]]:
    if "Service Definitions (ODX-D)" not in wb.sheetnames:
        return []

    ws = wb["Service Definitions (ODX-D)"]
    services = []

    for row in ws.iter_rows(min_row=4, values_only=True):
        if row[0]:
            services.append({
                "id": row[0],
                "name": row[1],
                "request_pdu_id": row[2],
                "response_pdu_id": row[3],
                "parameters": row[4] or "",
            })

    return services


def _probe_pdus(wb) -> list[dict[str, Any]]:
    if "PDU Library" not in wb.sheetnames:
        return []

    ws = wb["PDU Library"]
    pdus = []

    for row in ws.iter_rows(min_row=4, values_only=True):
        if row[0]:
            pdus.append({
                "id": row[0],
                "name": row[1],
                "length": row[2],
                "multiplexing": row[3] or "None",
                "signals": row[4] or "",
            })

    return pdus


def _probe_dtcs(wb) -> list[dict[str, Any]]:
    # DTCs typically embedded in service definitions or separate sheet
    # Placeholder for best-effort extraction
    return []


def _probe_data_objects(wb) -> list[dict[str, Any]]:
    # Data objects typically in ODX-D layer
    # Placeholder for best-effort extraction
    return []


def _probe_odx_layers(wb) -> list[dict[str, Any]]:
    if "ODX Layer Hierarchy" not in wb.sheetnames:
        return []

    ws = wb["ODX Layer Hierarchy"]
    layers = []

    for row in ws.iter_rows(min_row=4, values_only=True):
        if row[0]:
            layers.append({
                "id": row[0],
                "layer_type": row[1],
                "description": row[2] or "",
            })

    return layers
