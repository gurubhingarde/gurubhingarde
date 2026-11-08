"""
CS Architecture Builder — generates ISO/SAE 21434 cybersecurity architecture workbook
from CS Concept xlsx + CS architecture JSON.

Usage:
    python generate_cs_architecture.py <cs_concept.xlsx> <cs_arch.json> <output.xlsx>

Reads:
  - CS Concept xlsx: CSRs, TARA levels, threats, CAL allocations
  - CS architecture JSON: security controls, crypto inventory, key management, secure boot, secure comms

Produces:
  - 12-tab xlsx with control catalog, crypto inventory, key management, secure boot chains,
    secure communication, access control, CSR-to-element allocation matrix, defense-in-depth layers
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from cs_concept_reader import read_cs_concept


FONT_NAME = "Calibri"
NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
ALT_ROW = "F2F2F2"
WARN_YELLOW = "FFF2CC"

THIN = Side(border_style="thin", color="BFBFBF")
BORDER_ALL = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def header_font() -> Font:
    return Font(name=FONT_NAME, size=11, bold=True, color="FFFFFF")


def body_font() -> Font:
    return Font(name=FONT_NAME, size=10)


def style_title_row(ws, row: int, last_col: int, text: str) -> None:
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=last_col)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name=FONT_NAME, size=14, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 28


def style_header_row(ws, row: int, headers: list[str]) -> None:
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = header_font()
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER_ALL
    ws.row_dimensions[row].height = 32


def stripe_body(ws, start_row: int, end_row: int, last_col: int) -> None:
    for r in range(start_row, end_row + 1):
        fill = PatternFill("solid", fgColor=ALT_ROW) if (r - start_row) % 2 else None
        for c in range(1, last_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = body_font()
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = BORDER_ALL
            if fill:
                cell.fill = fill


def autosize(ws, widths: dict[int, int]) -> None:
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width


def tara_color_cell(cell, tara_value: str) -> None:
    if not tara_value:
        return
    color_map = {"TARA1": "FFE699", "TARA2": "F4B084", "TARA3": "F8696B", "TARA4": "C00000"}
    for key, color in color_map.items():
        if key in str(tara_value):
            cell.fill = PatternFill("solid", fgColor=color)
            cell.font = Font(name=FONT_NAME, bold=True, color="FFFFFF" if key == "TARA4" else "000000")
            cell.alignment = Alignment(horizontal="center", vertical="center")
            break


def build_title_page(wb: Workbook, cs_concept: dict, cs_arch: dict, cs_path: str) -> None:
    ws = wb.create_sheet("00_Title_Page")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 2, 4, "Cybersecurity Architecture (ISO/SAE 21434)")
    item_title = cs_arch.get("project", {}).get("name") or cs_concept["item"].get("Item Title", "")
    style_title_row(ws, 3, 4, item_title)

    proj = cs_arch.get("project", {})
    fields = [
        ("Project", proj.get("name", "")),
        ("CS Architecture Document ID", proj.get("doc_id", "")),
        ("Revision", proj.get("revision", "")),
        ("Date", proj.get("date", "")),
        ("Author", proj.get("author", "")),
        ("Approver", proj.get("approver", "")),
        ("Linked CS Concept", cs_path),
        ("Standard", "ISO/SAE 21434:2021, Cybersecurity Engineering."),
        ("Methodology", "Cybersecurity architecture refines system CSRs into concrete security controls, cryptographic elements, key management policies, secure boot chains, and defense-in-depth strategies."),
    ]
    row = 6
    for label, value in fields:
        ws.cell(row=row, column=2, value=label).font = Font(name=FONT_NAME, size=11, bold=True, color=NAVY)
        ws.cell(row=row, column=3, value=value).font = body_font()
        ws.cell(row=row, column=3).alignment = Alignment(horizontal="left", wrap_text=True)
        row += 1
    autosize(ws, {1: 4, 2: 26, 3: 80, 4: 4})


def build_doc_control(wb: Workbook) -> None:
    ws = wb.create_sheet("01_Document_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 5, "Document Control")
    style_header_row(ws, 3, ["Revision", "Date", "Author", "Description of change", "Approver"])
    for i, row in enumerate([
        ("0.1", "", "", "Initial draft generated by cs-architecture-builder skill", ""),
        ("0.2", "", "", "Security review comments incorporated", ""),
        ("1.0", "", "", "Released for integration and secure coding teams", ""),
    ], start=4):
        for c, v in enumerate(row, start=1):
            ws.cell(row=i, column=c, value=v)
    stripe_body(ws, 4, 6, 5)
    autosize(ws, {1: 12, 2: 14, 3: 22, 4: 50, 5: 22})


def build_cs_concept_echo(wb: Workbook, cs_concept: dict) -> None:
    ws = wb.create_sheet("02_CS_Concept_Echo")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 6, "CS Concept (Read-Only Echo)")
    note = ws.cell(row=2, column=1, value="This tab echoes the CS Concept CSRs and threat mappings. Update the CS Concept and re-run if changes are needed.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=6)
    ws.row_dimensions[2].height = 28

    style_header_row(ws, 4, ["CSR_ID", "Branch", "CAL", "Requirement Text", "Allocated Node"])
    row = 5
    for csr in cs_concept.get("csrs", []):
        ws.cell(row=row, column=1, value=csr.get("csr_id", ""))
        ws.cell(row=row, column=2, value=csr.get("title", ""))
        cell = ws.cell(row=row, column=3, value=csr.get("tara_level", ""))
        tara_color_cell(cell, csr.get("tara_level", ""))
        ws.cell(row=row, column=4, value=csr.get("description", ""))
        ws.cell(row=row, column=5, value=", ".join(csr.get("allocated_nodes", [])))
        row += 1
    end_row = 4 + len(cs_concept.get("csrs", []))
    stripe_body(ws, 5, end_row, 5)
    autosize(ws, {1: 12, 2: 26, 3: 14, 4: 36, 5: 28})


def build_cs_element_catalog(wb: Workbook, cs_arch: dict) -> None:
    ws = wb.create_sheet("03_CS_Element_Catalog")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 10, "CS Element Catalog")
    note = ws.cell(row=2, column=1, value="Concrete security controls: HSM, TPM, secure element, firewall, IDS, key store, certificate authority, secure boot ROM, etc.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=10)
    ws.row_dimensions[2].height = 32

    headers = ["CS-E_ID", "Name", "Type", "Supplier", "Part Number", "Certification", "Key Length Support", "Algorithms", "Node", "Notes"]
    style_header_row(ws, 4, headers)

    row = 5
    for elem in cs_arch.get("cs_elements", []):
        ws.cell(row=row, column=1, value=elem.get("id", ""))
        ws.cell(row=row, column=2, value=elem.get("name", ""))
        ws.cell(row=row, column=3, value=elem.get("type", ""))
        ws.cell(row=row, column=4, value=elem.get("supplier", ""))
        ws.cell(row=row, column=5, value=elem.get("part_number", ""))
        ws.cell(row=row, column=6, value=elem.get("certification", ""))
        ws.cell(row=row, column=7, value=elem.get("key_length_support", ""))
        ws.cell(row=row, column=8, value=elem.get("algorithms", ""))
        ws.cell(row=row, column=9, value=elem.get("node", ""))
        ws.cell(row=row, column=10, value=elem.get("notes", ""))
        row += 1

    end_row = 4 + len(cs_arch.get("cs_elements", []))
    stripe_body(ws, 5, end_row, 10)
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:J{end_row}"
    autosize(ws, {1: 12, 2: 22, 3: 16, 4: 12, 5: 20, 6: 18, 7: 18, 8: 20, 9: 12, 10: 28})


def build_crypto_inventory(wb: Workbook, cs_arch: dict) -> None:
    ws = wb.create_sheet("04_Cryptographic_Inventory")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 10, "Cryptographic Inventory")
    note = ws.cell(row=2, column=1, value="Per cryptographic operation: algorithm, key length, mode, lifecycle stages (generation, storage, distribution, rotation, destruction).")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=10)
    ws.row_dimensions[2].height = 36

    headers = ["Op_ID", "Algorithm", "Key Length", "Mode", "Purpose", "Key Class", "Gen Method", "Storage Location", "Rotation Policy", "Notes"]
    style_header_row(ws, 4, headers)

    row = 5
    for op in cs_arch.get("crypto_operations", []):
        ws.cell(row=row, column=1, value=op.get("id", ""))
        ws.cell(row=row, column=2, value=op.get("algorithm", ""))
        ws.cell(row=row, column=3, value=op.get("key_length", ""))
        ws.cell(row=row, column=4, value=op.get("mode", ""))
        ws.cell(row=row, column=5, value=op.get("purpose", ""))
        ws.cell(row=row, column=6, value=op.get("key_class", ""))
        ws.cell(row=row, column=7, value=op.get("gen_method", ""))
        ws.cell(row=row, column=8, value=op.get("storage_location", ""))
        ws.cell(row=row, column=9, value=op.get("rotation_policy", ""))
        ws.cell(row=row, column=10, value=op.get("notes", ""))
        row += 1

    end_row = 4 + len(cs_arch.get("crypto_operations", []))
    stripe_body(ws, 5, end_row, 10)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 10, 2: 18, 3: 12, 4: 12, 5: 16, 6: 14, 7: 16, 8: 20, 9: 16, 10: 28})


def build_key_management(wb: Workbook, cs_arch: dict) -> None:
    ws = wb.create_sheet("05_Key_Management")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "Key Management")
    note = ws.cell(row=2, column=1, value="Per key class: ID, purpose, generation, storage, rotation, access control, destruction method.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)
    ws.row_dimensions[2].height = 32

    headers = ["Key_ID", "Key Class", "Purpose", "Gen Method", "Storage Location", "Key Length", "Rotation", "Access Control", "Destruction"]
    style_header_row(ws, 4, headers)

    row = 5
    for key in cs_arch.get("keys", []):
        ws.cell(row=row, column=1, value=key.get("id", ""))
        ws.cell(row=row, column=2, value=key.get("key_class", ""))
        ws.cell(row=row, column=3, value=key.get("purpose", ""))
        ws.cell(row=row, column=4, value=key.get("gen_method", ""))
        ws.cell(row=row, column=5, value=key.get("storage_location", ""))
        ws.cell(row=row, column=6, value=key.get("key_length", ""))
        ws.cell(row=row, column=7, value=key.get("rotation_policy", ""))
        ws.cell(row=row, column=8, value=key.get("access_control", ""))
        ws.cell(row=row, column=9, value=key.get("destruction_method", ""))
        row += 1

    end_row = 4 + len(cs_arch.get("keys", []))
    stripe_body(ws, 5, end_row, 9)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 12, 2: 14, 3: 18, 4: 16, 5: 18, 6: 12, 7: 18, 8: 18, 9: 18})


def build_secure_boot_chain(wb: Workbook, cs_arch: dict) -> None:
    ws = wb.create_sheet("06_Secure_Boot_Chain")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "Secure Boot Chain")
    note = ws.cell(row=2, column=1, value="Boot stages (BootROM, Bootloader, App), measurement chain, root-of-trust, anti-rollback policy, secure unlock mechanism.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)
    ws.row_dimensions[2].height = 36

    headers = ["Stage_ID", "Stage Name", "Measured", "Measurement Hash Alg", "Verification Key Loc", "Anti-Rollback Method", "Secure Unlock", "Node", "Notes"]
    style_header_row(ws, 4, headers)

    row = 5
    for stage in cs_arch.get("boot_stages", []):
        ws.cell(row=row, column=1, value=stage.get("id", ""))
        ws.cell(row=row, column=2, value=stage.get("name", ""))
        ws.cell(row=row, column=3, value=stage.get("measured", ""))
        ws.cell(row=row, column=4, value=stage.get("hash_algorithm", ""))
        ws.cell(row=row, column=5, value=stage.get("key_location", ""))
        ws.cell(row=row, column=6, value=stage.get("anti_rollback", ""))
        ws.cell(row=row, column=7, value=stage.get("secure_unlock", ""))
        ws.cell(row=row, column=8, value=stage.get("node", ""))
        ws.cell(row=row, column=9, value=stage.get("notes", ""))
        row += 1

    end_row = 4 + len(cs_arch.get("boot_stages", []))
    stripe_body(ws, 5, end_row, 9)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 12, 2: 18, 3: 12, 4: 18, 5: 18, 6: 18, 7: 16, 8: 12, 9: 28})


def build_secure_communication(wb: Workbook, cs_arch: dict) -> None:
    ws = wb.create_sheet("07_Secure_Communication")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 9, "Secure Communication")
    note = ws.cell(row=2, column=1, value="Per channel: protocol, authentication method, encryption, integrity, replay protection.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=9)
    ws.row_dimensions[2].height = 32

    headers = ["Channel_ID", "Source", "Destination", "Protocol", "Auth Method", "Encryption Algo", "Integrity Algo", "Replay Protection", "Notes"]
    style_header_row(ws, 4, headers)

    row = 5
    for chan in cs_arch.get("secure_channels", []):
        ws.cell(row=row, column=1, value=chan.get("id", ""))
        ws.cell(row=row, column=2, value=chan.get("source", ""))
        ws.cell(row=row, column=3, value=chan.get("destination", ""))
        ws.cell(row=row, column=4, value=chan.get("protocol", ""))
        ws.cell(row=row, column=5, value=chan.get("auth_method", ""))
        ws.cell(row=row, column=6, value=chan.get("encryption_algo", ""))
        ws.cell(row=row, column=7, value=chan.get("integrity_algo", ""))
        ws.cell(row=row, column=8, value=chan.get("replay_protection", ""))
        ws.cell(row=row, column=9, value=chan.get("notes", ""))
        row += 1

    end_row = 4 + len(cs_arch.get("secure_channels", []))
    stripe_body(ws, 5, end_row, 9)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 12, 2: 14, 3: 16, 4: 14, 5: 16, 6: 16, 7: 16, 8: 16, 9: 28})


def build_access_control(wb: Workbook, cs_arch: dict) -> None:
    ws = wb.create_sheet("08_Access_Control")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "Access Control")
    note = ws.cell(row=2, column=1, value="Roles, privileges, authentication factors, privilege escalation controls.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)
    ws.row_dimensions[2].height = 28

    headers = ["Role_ID", "Role Name", "Privileges", "Auth Factors", "Max Session Duration", "Audit Logging", "Privilege Escalation", "Notes"]
    style_header_row(ws, 4, headers)

    row = 5
    for role in cs_arch.get("access_control_roles", []):
        ws.cell(row=row, column=1, value=role.get("id", ""))
        ws.cell(row=row, column=2, value=role.get("name", ""))
        ws.cell(row=row, column=3, value=role.get("privileges", ""))
        ws.cell(row=row, column=4, value=role.get("auth_factors", ""))
        ws.cell(row=row, column=5, value=role.get("max_session_duration", ""))
        ws.cell(row=row, column=6, value=role.get("audit_logging", ""))
        ws.cell(row=row, column=7, value=role.get("privilege_escalation", ""))
        ws.cell(row=row, column=8, value=role.get("notes", ""))
        row += 1

    end_row = 4 + len(cs_arch.get("access_control_roles", []))
    stripe_body(ws, 5, end_row, 8)
    ws.freeze_panes = "A5"
    autosize(ws, {1: 12, 2: 16, 3: 20, 4: 16, 5: 18, 6: 14, 7: 18, 8: 28})


def build_csr_to_element_allocation(wb: Workbook, cs_arch: dict, cs_concept: dict) -> None:
    ws = wb.create_sheet("09_CSR_to_Element_Allocation")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 12, "CSR to Element Allocation Matrix")
    note = ws.cell(row=2, column=1, value="Cross-reference matrix: CSR_ID rows x CS-E_ID columns. Mark which CS element implements each CSR.")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=12)
    ws.row_dimensions[2].height = 32

    csr_ids = [c.get("csr_id", "") for c in cs_concept.get("csrs", [])]
    elem_ids = [e.get("id", "") for e in cs_arch.get("cs_elements", [])]

    headers = ["CSR_ID"] + elem_ids[:10]
    style_header_row(ws, 4, headers)

    row = 5
    for csr_id in csr_ids:
        ws.cell(row=row, column=1, value=csr_id)
        for col in range(2, min(12, len(elem_ids) + 2)):
            ws.cell(row=row, column=col, value="")
        row += 1

    end_row = row - 1
    stripe_body(ws, 5, end_row, min(11, len(elem_ids) + 1))
    ws.freeze_panes = "B5"
    for col in range(2, min(12, len(elem_ids) + 2)):
        ws.column_dimensions[get_column_letter(col)].width = 10


def build_defense_in_depth(wb: Workbook, cs_arch: dict) -> None:
    ws = wb.create_sheet("10_Defense_in_Depth_Layers")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 8, "Defense-in-Depth Layers")
    note = ws.cell(row=2, column=1, value="Per attack vector: layer 1 (perimeter), layer 2 (network), layer 3 (host), layer 4 (application), layer 5 (data).")
    note.font = Font(name=FONT_NAME, italic=True, size=10, color="9C5700")
    note.fill = PatternFill("solid", fgColor=WARN_YELLOW)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=8)
    ws.row_dimensions[2].height = 32

    headers = ["Attack Vector", "Layer 1 (Perimeter)", "Layer 2 (Network)", "Layer 3 (Host)", "Layer 4 (App)", "Layer 5 (Data)", "Overall Coverage", "Notes"]
    style_header_row(ws, 4, headers)

    row = 5
    for vec in cs_arch.get("defense_vectors", []):
        ws.cell(row=row, column=1, value=vec.get("attack_vector", ""))
        ws.cell(row=row, column=2, value=vec.get("layer1", ""))
        ws.cell(row=row, column=3, value=vec.get("layer2", ""))
        ws.cell(row=row, column=4, value=vec.get("layer3", ""))
        ws.cell(row=row, column=5, value=vec.get("layer4", ""))
        ws.cell(row=row, column=6, value=vec.get("layer5", ""))
        ws.cell(row=row, column=7, value=vec.get("coverage", ""))
        ws.cell(row=row, column=8, value=vec.get("notes", ""))
        row += 1

    end_row = 4 + len(cs_arch.get("defense_vectors", []))
    stripe_body(ws, 5, end_row, 8)
    autosize(ws, {1: 16, 2: 16, 3: 16, 4: 16, 5: 16, 6: 16, 7: 14, 8: 28})


def build_references(wb: Workbook, cs_path: str) -> None:
    ws = wb.create_sheet("11_References")
    ws.sheet_view.showGridLines = False
    style_title_row(ws, 1, 3, "References")

    refs = [
        ("Linked CS Concept", cs_path),
        ("Security Testing", "Penetration testing, fuzzing, crypto validation per FIPS 186-4 / NIST SP 800-56A"),
        ("Key Management", "NIST SP 800-57, ISO 11770, AES-KW, RSA-OAEP key wrapping standards"),
        ("Secure Boot", "SHE-EXTEND, TrustZone-M, ATECC608A secure element specifications"),
        ("Cryptography", "FIPS 140-2 / 140-3, NIST CAVP validated algorithms, AES GCM, SHA-384, ECDSA P-384"),
        ("Applicable Standards", "ISO/SAE 21434:2021, NIST Cybersecurity Framework, AUTOSAR SecOC"),
    ]

    row = 3
    for label, value in refs:
        ws.cell(row=row, column=1, value=label).font = Font(name=FONT_NAME, bold=True)
        ws.cell(row=row, column=2, value=value).alignment = Alignment(wrap_text=True)
        ws.row_dimensions[row].height = 20
        row += 1

    autosize(ws, {1: 24, 2: 80})


def generate(cs_concept_path: str, cs_arch_path: str, output_path: str) -> dict:
    cs_concept = read_cs_concept(cs_concept_path)

    with open(cs_arch_path) as f:
        cs_arch = json.load(f)

    wb = Workbook()
    wb.remove(wb.active)

    build_title_page(wb, cs_concept, cs_arch, cs_concept_path)
    build_doc_control(wb)
    build_cs_concept_echo(wb, cs_concept)
    build_cs_element_catalog(wb, cs_arch)
    build_crypto_inventory(wb, cs_arch)
    build_key_management(wb, cs_arch)
    build_secure_boot_chain(wb, cs_arch)
    build_secure_communication(wb, cs_arch)
    build_access_control(wb, cs_arch)
    build_csr_to_element_allocation(wb, cs_arch, cs_concept)
    build_defense_in_depth(wb, cs_arch)
    build_references(wb, cs_concept_path)

    wb.active = 0
    wb.save(output_path)

    elem_count = len(cs_arch.get("cs_elements", []))
    csr_alloc_count = len(cs_concept.get("csrs", [])) * len(cs_arch.get("cs_elements", []))

    return {
        "tab_count": 12,
        "cs_elements": elem_count,
        "csr_allocations": csr_alloc_count,
        "output_path": output_path,
    }


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_cs_architecture.py <cs_concept.xlsx> <cs_arch.json> <output.xlsx>", file=sys.stderr)
        sys.exit(2)

    summary = generate(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(summary, indent=2))
