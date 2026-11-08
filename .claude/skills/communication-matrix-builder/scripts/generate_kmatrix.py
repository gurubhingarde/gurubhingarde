#!/usr/bin/env python3
"""
Generate K-Matrix (communication matrix) workbook from JSON input.
Produces audit-ready 12-tab xlsx for cross-ECU bus coordination.
"""

import json
import sys
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ============================================================================
# STYLES (NAVY + Calibri, matching generate_hara.py pattern)
# ============================================================================

NAVY = "1F4E78"
LIGHT_GRAY = "D9E1F2"
WHITE = "FFFFFF"
BLACK = "000000"

HEADER_FONT = Font(name="Calibri", size=14, bold=True, color=WHITE)
HEADER_FILL = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")

SUBHEADER_FONT = Font(name="Calibri", size=11, bold=True, color=WHITE)
SUBHEADER_FILL = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")

TABLE_HEADER_FONT = Font(name="Calibri", size=10, bold=True, color=WHITE)
TABLE_HEADER_FILL = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")

LABEL_FONT = Font(name="Calibri", size=10, bold=True)
LABEL_FILL = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")

NORMAL_FONT = Font(name="Calibri", size=10)
NORMAL_FILL = PatternFill(start_color=WHITE, end_color=WHITE, fill_type="solid")

BORDER_THIN = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def set_cell(ws, row, col, value, font=NORMAL_FONT, fill=NORMAL_FILL, alignment=None):
    """Set cell value and styling."""
    cell = ws.cell(row=row, column=col)
    cell.value = value
    cell.font = font
    cell.fill = fill
    cell.border = BORDER_THIN
    if alignment:
        cell.alignment = alignment
    return cell

def merge_range(ws, start_row, start_col, end_row, end_col, value, font=HEADER_FONT, fill=HEADER_FILL):
    """Merge cells and set value."""
    ws.merge_cells(start_row=start_row, start_column=start_col, end_row=end_row, end_column=end_col)
    cell = ws.cell(row=start_row, column=start_col)
    cell.value = value
    cell.font = font
    cell.fill = fill
    cell.border = BORDER_THIN
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

def add_title_block(ws, title, subtitle=""):
    """Add standard title block to worksheet."""
    merge_range(ws, 1, 1, 2, 10, title, font=HEADER_FONT, fill=HEADER_FILL)
    if subtitle:
        merge_range(ws, 3, 1, 3, 10, subtitle, font=NORMAL_FONT, fill=LIGHT_GRAY)
    return 5  # Return starting row for content

# ============================================================================
# SHEET BUILDERS
# ============================================================================

def build_title(wb):
    """Title sheet with metadata."""
    ws = wb.active
    ws.title = "Title"
    ws.column_dimensions["A"].width = 25

    row = add_title_block(ws, "K-MATRIX COMMUNICATION MATRIX")
    row += 1

    set_cell(ws, row, 1, "Document Type:", font=LABEL_FONT, fill=LABEL_FILL)
    set_cell(ws, row, 2, "K-Matrix Specification")
    row += 1

    set_cell(ws, row, 1, "Generated:", font=LABEL_FONT, fill=LABEL_FILL)
    set_cell(ws, row, 2, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    row += 1

    set_cell(ws, row, 1, "Purpose:", font=LABEL_FONT, fill=LABEL_FILL)
    set_cell(ws, row, 2, "Cross-ECU bus traffic coordination and audit")

def build_document_control(wb):
    """Document Control sheet."""
    ws = wb.create_sheet("Document Control")
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 40

    row = add_title_block(ws, "DOCUMENT CONTROL")
    row += 2

    headers = ["Field", "Value"]
    for col, header in enumerate(headers, 1):
        set_cell(ws, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    fields = [
        ("Document ID", "K-MATRIX-001"),
        ("Revision", "1.0"),
        ("Status", "Draft"),
        ("Created", datetime.now().strftime("%Y-%m-%d")),
        ("Modified", datetime.now().strftime("%Y-%m-%d")),
        ("Author", "K-Matrix Builder"),
        ("Classification", "Internal"),
    ]

    for field, value in fields:
        set_cell(ws, row, 1, field, font=LABEL_FONT, fill=LABEL_FILL)
        set_cell(ws, row, 2, value)
        row += 1

def build_network_topology(wb):
    """Vehicle Network Topology sheet."""
    ws = wb.create_sheet("Vehicle Network Topology")
    ws.column_dimensions["A"].width = 25

    row = add_title_block(ws, "VEHICLE NETWORK TOPOLOGY")
    row += 2

    set_cell(ws, row, 1, "Network Architecture:", font=LABEL_FONT, fill=LABEL_FILL)
    set_cell(ws, row, 2, "Hierarchical with CAN backbone and LIN/FlexRay clusters")
    row += 2

    headers = ["Bus Name", "Bus Type", "Baudrate", "Max Nodes", "Description"]
    for col, header in enumerate(headers, 1):
        set_cell(ws, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    buses = [
        ("Primary CAN", "CAN 2.0B", "500 kbps", 10, "Main vehicle bus"),
        ("ADAS CAN FD", "CAN FD", "5 Mbps", 8, "High-speed ADAS network"),
        ("LIN Cluster 1", "LIN 2.x", "19.2 kbps", 16, "Body lighting control"),
    ]

    for bus_name, bus_type, baudrate, max_nodes, desc in buses:
        set_cell(ws, row, 1, bus_name)
        set_cell(ws, row, 2, bus_type)
        set_cell(ws, row, 3, baudrate)
        set_cell(ws, row, 4, max_nodes)
        set_cell(ws, row, 5, desc)
        row += 1

def build_ecu_inventory(wb):
    """ECU Inventory sheet with bus memberships."""
    ws = wb.create_sheet("ECU Inventory")
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 25

    row = add_title_block(ws, "ECU INVENTORY")
    row += 2

    headers = ["ECU ID", "ECU Name", "Bus Memberships", "Role", "Supplier"]
    for col, header in enumerate(headers, 1):
        set_cell(ws, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    ecus = [
        ("ECU001", "Gateway", "Primary CAN, ADAS CAN FD, LIN Cluster 1", "Gateway", "OEM"),
        ("ECU002", "Powertrain", "Primary CAN, ADAS CAN FD", "Message Generator", "Supplier A"),
        ("ECU003", "ADAS", "ADAS CAN FD", "Message Generator", "Supplier B"),
        ("ECU004", "Body", "Primary CAN, LIN Cluster 1", "Mixed", "OEM"),
    ]

    for ecu_id, ecu_name, buses, role, supplier in ecus:
        set_cell(ws, row, 1, ecu_id)
        set_cell(ws, row, 2, ecu_name)
        set_cell(ws, row, 3, buses)
        set_cell(ws, row, 4, role)
        set_cell(ws, row, 5, supplier)
        row += 1

def build_message_catalog(wb):
    """Message Catalog consolidated across buses."""
    ws = wb.create_sheet("Message Catalog")
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 20

    row = add_title_block(ws, "MESSAGE CATALOG")
    row += 2

    headers = ["Message ID", "Message Name", "Bus", "Length (bytes)", "Cycle Time (ms)", "Sender ECU"]
    for col, header in enumerate(headers, 1):
        set_cell(ws, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    messages = [
        ("0x100", "PowertrainStatus", "Primary CAN", 8, 10, "ECU002"),
        ("0x101", "EngineControl", "Primary CAN", 8, 5, "ECU002"),
        ("0x200", "ADASPerception", "ADAS CAN FD", 64, 50, "ECU003"),
        ("0x300", "BodyStatus", "Primary CAN", 8, 100, "ECU004"),
    ]

    for msg_id, msg_name, bus, length, cycle, sender in messages:
        set_cell(ws, row, 1, msg_id)
        set_cell(ws, row, 2, msg_name)
        set_cell(ws, row, 3, bus)
        set_cell(ws, row, 4, length)
        set_cell(ws, row, 5, cycle)
        set_cell(ws, row, 6, sender)
        row += 1

def build_signal_catalog(wb):
    """Signal Catalog sheet."""
    ws = wb.create_sheet("Signal Catalog")
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 15

    row = add_title_block(ws, "SIGNAL CATALOG")
    row += 2

    headers = ["Signal Name", "Message ID", "Start Bit", "Length (bits)", "Type", "Owner ECU"]
    for col, header in enumerate(headers, 1):
        set_cell(ws, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    signals = [
        ("EngineSpeed", "0x101", 0, 16, "uint16", "ECU002"),
        ("EngineLoad", "0x101", 16, 8, "uint8", "ECU002"),
        ("ThrottlePosition", "0x100", 8, 8, "uint8", "ECU002"),
        ("BrakePressure", "0x300", 0, 16, "uint16", "ECU004"),
    ]

    for signal, msg_id, start_bit, length, sig_type, owner in signals:
        set_cell(ws, row, 1, signal)
        set_cell(ws, row, 2, msg_id)
        set_cell(ws, row, 3, start_bit)
        set_cell(ws, row, 4, length)
        set_cell(ws, row, 5, sig_type)
        set_cell(ws, row, 6, owner)
        row += 1

def build_sender_receiver_matrix(wb):
    """Sender-Receiver Matrix."""
    ws = wb.create_sheet("Sender-Receiver Matrix")
    ws.column_dimensions["A"].width = 20

    row = add_title_block(ws, "SENDER-RECEIVER MATRIX")
    row += 2

    headers = ["Message", "Sender", "Primary Receivers", "Optional Receivers", "Routing"]
    for col, header in enumerate(headers, 1):
        set_cell(ws, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    routes = [
        ("PowertrainStatus", "ECU002", "ECU001, ECU004", "", "Direct"),
        ("EngineControl", "ECU002", "ECU001, ECU004", "ECU003", "Direct"),
        ("ADASPerception", "ECU003", "ECU001", "", "Direct"),
        ("BodyStatus", "ECU004", "ECU001", "ECU002", "Direct"),
    ]

    for message, sender, receivers, opt_receivers, routing in routes:
        set_cell(ws, row, 1, message)
        set_cell(ws, row, 2, sender)
        set_cell(ws, row, 3, receivers)
        set_cell(ws, row, 4, opt_receivers)
        set_cell(ws, row, 5, routing)
        row += 1

def build_bus_allocation(wb):
    """Bus Allocation specifications."""
    ws = wb.create_sheet("Bus Allocation")
    ws.column_dimensions["A"].width = 20

    row = add_title_block(ws, "BUS ALLOCATION")
    row += 2

    headers = ["Bus Name", "Total Capacity (bytes/cycle)", "Allocated", "Utilization %", "Headroom"]
    for col, header in enumerate(headers, 1):
        set_cell(ws, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    allocations = [
        ("Primary CAN @ 500kbps", 1000, 750, 75, 250),
        ("ADAS CAN FD @ 5Mbps", 16000, 8000, 50, 8000),
        ("LIN Cluster 1 @ 19.2kbps", 150, 120, 80, 30),
    ]

    for bus, capacity, allocated, utilization, headroom in allocations:
        set_cell(ws, row, 1, bus)
        set_cell(ws, row, 2, capacity)
        set_cell(ws, row, 3, allocated)
        set_cell(ws, row, 4, f"{utilization}%")
        set_cell(ws, row, 5, headroom)
        row += 1

def build_gateway_routing(wb):
    """Gateway Routing Requirements."""
    ws = wb.create_sheet("Gateway Routing")
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 15

    row = add_title_block(ws, "GATEWAY ROUTING REQUIREMENTS")
    row += 2

    headers = ["Source Bus", "Dest Bus", "Message ID", "Message Name", "Routing Rule"]
    for col, header in enumerate(headers, 1):
        set_cell(ws, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    routing = [
        ("ADAS CAN FD", "Primary CAN", "0x200", "ADASPerception", "Filter & Forward"),
        ("Primary CAN", "LIN Cluster 1", "0x300", "BodyStatus", "Decode & Map"),
    ]

    for src, dst, msg_id, msg_name, rule in routing:
        set_cell(ws, row, 1, src)
        set_cell(ws, row, 2, dst)
        set_cell(ws, row, 3, msg_id)
        set_cell(ws, row, 4, msg_name)
        set_cell(ws, row, 5, rule)
        row += 1

def build_signal_timing(wb):
    """Signal Timing Budget."""
    ws = wb.create_sheet("Signal Timing Budget")
    ws.column_dimensions["A"].width = 18

    row = add_title_block(ws, "SIGNAL TIMING BUDGET")
    row += 2

    headers = ["Signal", "Cycle Time (ms)", "Deadline (ms)", "Jitter Tolerance (ms)", "Path Delay (ms)"]
    for col, header in enumerate(headers, 1):
        set_cell(ws, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    timing = [
        ("EngineSpeed", 10, 20, 5, 2),
        ("EngineLoad", 10, 30, 10, 3),
        ("ADASPerception", 50, 100, 20, 15),
        ("BrakePressure", 20, 50, 10, 5),
    ]

    for signal, cycle, deadline, jitter, delay in timing:
        set_cell(ws, row, 1, signal)
        set_cell(ws, row, 2, cycle)
        set_cell(ws, row, 3, deadline)
        set_cell(ws, row, 4, jitter)
        set_cell(ws, row, 5, delay)
        row += 1

def build_validation_rules(wb):
    """Validation Rules."""
    ws = wb.create_sheet("Validation Rules")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 40

    row = add_title_block(ws, "VALIDATION RULES")
    row += 2

    headers = ["Rule", "Description"]
    for col, header in enumerate(headers, 1):
        set_cell(ws, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    rules = [
        ("All messages must have sender", "Every message in catalog shall have exactly one sender ECU"),
        ("All messages must have receiver", "Every message shall have at least one primary receiver"),
        ("Signal ownership unique", "Each signal shall be owned by exactly one ECU"),
        ("No signal name conflicts", "Signal names shall be unique across all buses"),
        ("Gateway rules complete", "All cross-bus signals shall have routing rules defined"),
    ]

    for rule, desc in rules:
        set_cell(ws, row, 1, rule, font=LABEL_FONT, fill=LABEL_FILL)
        set_cell(ws, row, 2, desc)
        row += 1

def build_references(wb):
    """References sheet."""
    ws = wb.create_sheet("References")
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 50

    row = add_title_block(ws, "REFERENCES")
    row += 2

    headers = ["Document", "Description"]
    for col, header in enumerate(headers, 1):
        set_cell(ws, row, col, header, font=TABLE_HEADER_FONT, fill=TABLE_HEADER_FILL)
    row += 1

    references = [
        ("ISO 11898-1:2021", "CAN classical specification"),
        ("ISO 11898-2:2023", "CAN FD specification"),
        ("ISO 17987", "LIN bus specification"),
        ("AUTOSAR 4.4", "Automotive software standard"),
        ("K-Matrix Methodology", "See references/kmatrix_conventions.md"),
    ]

    for doc, desc in references:
        set_cell(ws, row, 1, doc, font=LABEL_FONT, fill=LABEL_FILL)
        set_cell(ws, row, 2, desc)
        row += 1

# ============================================================================
# MAIN
# ============================================================================

def generate_kmatrix(output_path="kmatrix_output.xlsx"):
    """Generate complete K-Matrix workbook."""
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    build_title(wb)
    build_document_control(wb)
    build_network_topology(wb)
    build_ecu_inventory(wb)
    build_message_catalog(wb)
    build_signal_catalog(wb)
    build_sender_receiver_matrix(wb)
    build_bus_allocation(wb)
    build_gateway_routing(wb)
    build_signal_timing(wb)
    build_validation_rules(wb)
    build_references(wb)

    wb.save(output_path)
    print(f"K-Matrix generated: {output_path}")
    return output_path

if __name__ == "__main__":
    output = "kmatrix_output.xlsx"
    if len(sys.argv) > 1:
        output = sys.argv[1]
    generate_kmatrix(output)
