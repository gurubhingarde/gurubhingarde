#!/usr/bin/env python3
"""
K-Matrix probe: extract structure from xlsx workbook.
Returns ECUs, messages, signals, buses, routing rules.
"""

from openpyxl import load_workbook
from collections import defaultdict

class KMatrixProbe:
    """Extract K-Matrix structure from xlsx."""

    def __init__(self, xlsx_path):
        self.xlsx_path = xlsx_path
        self.wb = load_workbook(xlsx_path)
        self.ecus = {}
        self.messages = {}
        self.signals = {}
        self.buses = {}
        self.routing_rules = []
        self.sender_receiver = {}

    def extract_ecus(self):
        """Extract ECU inventory."""
        try:
            ws = self.wb["ECU Inventory"]
        except KeyError:
            return {}

        ecus = {}
        for row_idx, row in enumerate(ws.iter_rows(min_row=6, values_only=True), start=6):
            if not row[0]:  # Skip empty rows
                break
            ecu_id = row[0]
            ecu_name = row[1]
            bus_memberships = row[2]
            role = row[3]
            supplier = row[4]
            ecus[ecu_id] = {
                "name": ecu_name,
                "buses": [b.strip() for b in bus_memberships.split(",")] if bus_memberships else [],
                "role": role,
                "supplier": supplier,
            }
        self.ecus = ecus
        return ecus

    def extract_messages(self):
        """Extract message catalog."""
        try:
            ws = self.wb["Message Catalog"]
        except KeyError:
            return {}

        messages = {}
        for row_idx, row in enumerate(ws.iter_rows(min_row=6, values_only=True), start=6):
            if not row[0]:
                break
            msg_id = row[0]
            msg_name = row[1]
            bus = row[2]
            length = row[3]
            cycle_time = row[4]
            sender = row[5]
            messages[msg_id] = {
                "name": msg_name,
                "bus": bus,
                "length": length,
                "cycle_time": cycle_time,
                "sender": sender,
            }
        self.messages = messages
        return messages

    def extract_signals(self):
        """Extract signal catalog."""
        try:
            ws = self.wb["Signal Catalog"]
        except KeyError:
            return {}

        signals = {}
        for row_idx, row in enumerate(ws.iter_rows(min_row=6, values_only=True), start=6):
            if not row[0]:
                break
            signal_name = row[0]
            msg_id = row[1]
            start_bit = row[2]
            length = row[3]
            sig_type = row[4]
            owner = row[5]
            signals[signal_name] = {
                "message_id": msg_id,
                "start_bit": start_bit,
                "length": length,
                "type": sig_type,
                "owner": owner,
            }
        self.signals = signals
        return signals

    def extract_buses(self):
        """Extract bus definitions."""
        try:
            ws = self.wb["Vehicle Network Topology"]
        except KeyError:
            return {}

        buses = {}
        for row_idx, row in enumerate(ws.iter_rows(min_row=7, values_only=True), start=7):
            if not row[0]:
                break
            bus_name = row[0]
            bus_type = row[1]
            baudrate = row[2]
            max_nodes = row[3]
            description = row[4]
            buses[bus_name] = {
                "type": bus_type,
                "baudrate": baudrate,
                "max_nodes": max_nodes,
                "description": description,
            }
        self.buses = buses
        return buses

    def extract_routing_rules(self):
        """Extract gateway routing requirements."""
        try:
            ws = self.wb["Gateway Routing"]
        except KeyError:
            return []

        rules = []
        for row_idx, row in enumerate(ws.iter_rows(min_row=6, values_only=True), start=6):
            if not row[0]:
                break
            src_bus = row[0]
            dst_bus = row[1]
            msg_id = row[2]
            msg_name = row[3]
            routing_rule = row[4]
            rules.append({
                "source_bus": src_bus,
                "dest_bus": dst_bus,
                "message_id": msg_id,
                "message_name": msg_name,
                "rule": routing_rule,
            })
        self.routing_rules = rules
        return rules

    def extract_sender_receiver(self):
        """Extract sender-receiver relationships."""
        try:
            ws = self.wb["Sender-Receiver Matrix"]
        except KeyError:
            return {}

        sr_map = {}
        for row_idx, row in enumerate(ws.iter_rows(min_row=6, values_only=True), start=6):
            if not row[0]:
                break
            message = row[0]
            sender = row[1]
            receivers = row[2]
            opt_receivers = row[3]
            routing = row[4]
            sr_map[message] = {
                "sender": sender,
                "receivers": [r.strip() for r in receivers.split(",")] if receivers else [],
                "optional_receivers": [r.strip() for r in opt_receivers.split(",")] if opt_receivers else [],
                "routing": routing,
            }
        self.sender_receiver = sr_map
        return sr_map

    def extract_all(self):
        """Extract all K-Matrix structure."""
        return {
            "ecus": self.extract_ecus(),
            "messages": self.extract_messages(),
            "signals": self.extract_signals(),
            "buses": self.extract_buses(),
            "routing_rules": self.extract_routing_rules(),
            "sender_receiver": self.extract_sender_receiver(),
        }


def probe_kmatrix(xlsx_path):
    """Convenient function to probe a K-Matrix file."""
    prober = KMatrixProbe(xlsx_path)
    return prober.extract_all()
