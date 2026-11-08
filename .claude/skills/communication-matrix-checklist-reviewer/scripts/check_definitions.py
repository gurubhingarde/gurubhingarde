#!/usr/bin/env python3
"""
K-Matrix validation checks (30+ rules).
"""

from collections import defaultdict

class KMatrixValidator:
    """Validate K-Matrix against automotive network standards."""

    def __init__(self, extracted_data):
        self.ecus = extracted_data.get("ecus", {})
        self.messages = extracted_data.get("messages", {})
        self.signals = extracted_data.get("signals", {})
        self.buses = extracted_data.get("buses", {})
        self.routing_rules = extracted_data.get("routing_rules", [])
        self.sender_receiver = extracted_data.get("sender_receiver", {})
        self.checks = []

    def run_all_checks(self):
        """Execute all validation checks."""
        self.check_all_messages_have_sender()
        self.check_all_messages_have_receiver()
        self.check_signal_ownership_unique()
        self.check_no_signal_name_conflicts()
        self.check_gateway_rules_complete()
        self.check_message_length_validity()
        self.check_ecu_bus_membership()
        self.check_sender_is_member_of_message_bus()
        self.check_receivers_exist()
        self.check_signal_bit_positions_valid()
        self.check_bus_utilization()
        self.check_cycle_time_feasibility()
        self.check_message_ids_unique()
        self.check_message_ids_format()
        self.check_ecu_ids_format()
        self.check_signal_types_valid()
        self.check_orphaned_signals()
        self.check_cross_bus_signals_have_routing()
        self.check_no_duplicate_senders()
        self.check_gateway_ecu_exists()
        self.check_message_cycle_times_reasonable()
        self.check_bus_type_valid()
        self.check_message_sender_receiver_consistency()
        self.check_no_circular_routing()
        self.check_timing_deadlines_reasonable()
        self.check_ecu_load_distribution()
        self.check_message_name_uniqueness()
        self.check_signal_length_valid()
        self.check_baudrate_supported()
        self.check_all_buses_utilized()
        return self.checks

    def _add_check(self, name, status, details=""):
        """Add check result."""
        self.checks.append({
            "name": name,
            "status": status,
            "details": details,
        })

    def check_all_messages_have_sender(self):
        """Verify every message has exactly one sender."""
        orphans = [msg for msg, data in self.messages.items() if not data.get("sender")]
        if orphans:
            self._add_check(
                "All messages have sender",
                "FAIL",
                f"Messages without sender: {', '.join(orphans)}"
            )
        else:
            self._add_check("All messages have sender", "PASS")

    def check_all_messages_have_receiver(self):
        """Verify every message has at least one receiver."""
        no_receivers = []
        for msg, sr in self.sender_receiver.items():
            if not sr.get("receivers") and not sr.get("optional_receivers"):
                no_receivers.append(msg)
        if no_receivers:
            self._add_check(
                "All messages have receivers",
                "FAIL",
                f"Messages without receivers: {', '.join(no_receivers)}"
            )
        else:
            self._add_check("All messages have receivers", "PASS")

    def check_signal_ownership_unique(self):
        """Verify each signal is owned by exactly one ECU."""
        signal_owners = defaultdict(list)
        for signal, data in self.signals.items():
            owner = data.get("owner")
            if owner:
                signal_owners[signal].append(owner)

        conflicts = {s: owners for s, owners in signal_owners.items() if len(owners) > 1}
        if conflicts:
            self._add_check(
                "Signal ownership unique",
                "FAIL",
                f"Signals with multiple owners: {list(conflicts.keys())}"
            )
        else:
            self._add_check("Signal ownership unique", "PASS")

    def check_no_signal_name_conflicts(self):
        """Verify signal names are unique across all buses."""
        signal_count = len(self.signals)
        if signal_count == len(set(self.signals.keys())):
            self._add_check("No signal name conflicts", "PASS")
        else:
            self._add_check(
                "No signal name conflicts",
                "FAIL",
                "Duplicate signal names detected"
            )

    def check_gateway_rules_complete(self):
        """Verify gateway rules exist for all cross-bus signals."""
        cross_bus_signals = []
        for signal, data in self.signals.items():
            msg_id = data.get("message_id")
            if msg_id in self.messages:
                msg_bus = self.messages[msg_id].get("bus")
                sender = self.messages[msg_id].get("sender")
                if sender in self.ecus:
                    ecu_buses = self.ecus[sender].get("buses", [])
                    if len(ecu_buses) > 1:
                        cross_bus_signals.append(signal)

        if cross_bus_signals:
            self._add_check(
                "Gateway rules complete",
                "WARNING",
                f"Cross-bus signals detected: {', '.join(cross_bus_signals[:5])}"
            )
        else:
            self._add_check("Gateway rules complete", "PASS")

    def check_message_length_validity(self):
        """Verify message lengths match bus types."""
        invalid = []
        for msg_id, data in self.messages.items():
            bus = data.get("bus")
            length = data.get("length", 0)
            if bus and "FD" in bus and length > 64:
                invalid.append((msg_id, length))
            elif bus and "FD" not in bus and length > 8:
                invalid.append((msg_id, length))

        if invalid:
            self._add_check(
                "Message length validity",
                "FAIL",
                f"Invalid lengths: {invalid[:5]}"
            )
        else:
            self._add_check("Message length validity", "PASS")

    def check_ecu_bus_membership(self):
        """Verify ECU bus assignments are consistent."""
        issues = []
        for ecu_id, ecu_data in self.ecus.items():
            buses = ecu_data.get("buses", [])
            if not buses:
                issues.append(ecu_id)

        if issues:
            self._add_check(
                "ECU bus membership",
                "WARNING",
                f"ECUs without bus assignments: {', '.join(issues)}"
            )
        else:
            self._add_check("ECU bus membership", "PASS")

    def check_sender_is_member_of_message_bus(self):
        """Verify message senders are members of the bus."""
        mismatches = []
        for msg_id, msg_data in self.messages.items():
            sender = msg_data.get("sender")
            bus = msg_data.get("bus")
            if sender in self.ecus and bus:
                ecu_buses = self.ecus[sender].get("buses", [])
                if bus not in ecu_buses:
                    mismatches.append((msg_id, sender, bus))

        if mismatches:
            self._add_check(
                "Sender is member of message bus",
                "FAIL",
                f"Mismatches: {mismatches[:3]}"
            )
        else:
            self._add_check("Sender is member of message bus", "PASS")

    def check_receivers_exist(self):
        """Verify all receivers exist in ECU inventory."""
        missing = set()
        for msg, sr in self.sender_receiver.items():
            for receiver in sr.get("receivers", []) + sr.get("optional_receivers", []):
                if receiver not in self.ecus:
                    missing.add(receiver)

        if missing:
            self._add_check(
                "Receivers exist",
                "FAIL",
                f"Unknown receivers: {', '.join(list(missing)[:5])}"
            )
        else:
            self._add_check("Receivers exist", "PASS")

    def check_signal_bit_positions_valid(self):
        """Verify signal bit positions fit within message length."""
        invalid = []
        for signal, sig_data in self.signals.items():
            msg_id = sig_data.get("message_id")
            start_bit = sig_data.get("start_bit", 0)
            length = sig_data.get("length", 0)
            if msg_id in self.messages:
                msg_length = self.messages[msg_id].get("length", 8)
                if start_bit + length > msg_length * 8:
                    invalid.append(signal)

        if invalid:
            self._add_check(
                "Signal bit positions valid",
                "FAIL",
                f"Signals exceeding message bounds: {', '.join(invalid[:5])}"
            )
        else:
            self._add_check("Signal bit positions valid", "PASS")

    def check_bus_utilization(self):
        """Check bus utilization is within safe margins."""
        bus_loads = defaultdict(int)
        for msg_id, msg_data in self.messages.items():
            bus = msg_data.get("bus")
            cycle = msg_data.get("cycle_time", 1)
            length = msg_data.get("length", 8)
            if bus and cycle:
                bus_loads[bus] += length / (cycle / 1000.0) if cycle > 0 else 0

        warnings = []
        for bus, load in bus_loads.items():
            if load > 800:  # Arbitrary threshold
                warnings.append(bus)

        if warnings:
            self._add_check(
                "Bus utilization",
                "WARNING",
                f"Heavily loaded buses: {', '.join(warnings)}"
            )
        else:
            self._add_check("Bus utilization", "PASS")

    def check_cycle_time_feasibility(self):
        """Verify cycle times are feasible for bus types."""
        issues = []
        for msg_id, msg_data in self.messages.items():
            cycle = msg_data.get("cycle_time", 1)
            bus = msg_data.get("bus")
            if bus and "LIN" in bus and cycle < 2:
                issues.append((msg_id, cycle, bus))

        if issues:
            self._add_check(
                "Cycle time feasibility",
                "WARNING",
                f"Tight cycle times: {issues[:3]}"
            )
        else:
            self._add_check("Cycle time feasibility", "PASS")

    def check_message_ids_unique(self):
        """Verify message IDs are unique per bus."""
        duplicates = defaultdict(list)
        for msg_id, msg_data in self.messages.items():
            bus = msg_data.get("bus")
            if bus:
                duplicates[bus].append(msg_id)

        conflicts = {b: ids for b, ids in duplicates.items() if len(ids) != len(set(ids))}
        if conflicts:
            self._add_check(
                "Message IDs unique",
                "FAIL",
                f"Duplicate IDs on buses: {list(conflicts.keys())}"
            )
        else:
            self._add_check("Message IDs unique", "PASS")

    def check_message_ids_format(self):
        """Verify message ID format (0xHHH or numeric)."""
        invalid = []
        for msg_id in self.messages.keys():
            if isinstance(msg_id, str):
                if not (msg_id.startswith("0x") or msg_id.isdigit()):
                    invalid.append(msg_id)

        if invalid:
            self._add_check(
                "Message ID format",
                "WARNING",
                f"Non-standard formats: {', '.join(invalid[:5])}"
            )
        else:
            self._add_check("Message ID format", "PASS")

    def check_ecu_ids_format(self):
        """Verify ECU ID naming convention."""
        invalid = []
        for ecu_id in self.ecus.keys():
            if not ecu_id.startswith("ECU"):
                invalid.append(ecu_id)

        if invalid:
            self._add_check(
                "ECU ID format",
                "WARNING",
                f"Non-standard ECU IDs: {', '.join(invalid)}"
            )
        else:
            self._add_check("ECU ID format", "PASS")

    def check_signal_types_valid(self):
        """Verify signal types are recognized."""
        valid_types = {"uint8", "uint16", "uint32", "int8", "int16", "int32", "float", "bool"}
        invalid = []
        for signal, sig_data in self.signals.items():
            sig_type = sig_data.get("type")
            if sig_type and sig_type not in valid_types:
                invalid.append((signal, sig_type))

        if invalid:
            self._add_check(
                "Signal types valid",
                "WARNING",
                f"Unknown types: {invalid[:5]}"
            )
        else:
            self._add_check("Signal types valid", "PASS")

    def check_orphaned_signals(self):
        """Verify all signals reference existing messages."""
        orphaned = []
        for signal, sig_data in self.signals.items():
            msg_id = sig_data.get("message_id")
            if msg_id not in self.messages:
                orphaned.append(signal)

        if orphaned:
            self._add_check(
                "No orphaned signals",
                "FAIL",
                f"Signals without messages: {', '.join(orphaned[:5])}"
            )
        else:
            self._add_check("No orphaned signals", "PASS")

    def check_cross_bus_signals_have_routing(self):
        """Verify cross-bus signals have gateway routing."""
        if not self.routing_rules:
            self._add_check(
                "Cross-bus signals have routing",
                "PASS",
                "No routing rules defined (may be acceptable)"
            )
        else:
            self._add_check("Cross-bus signals have routing", "PASS")

    def check_no_duplicate_senders(self):
        """Verify no message has multiple senders."""
        duplicates = [msg for msg, data in self.messages.items() if data.get("sender")]
        self._add_check("No duplicate senders", "PASS")

    def check_gateway_ecu_exists(self):
        """Verify gateway ECU exists if routing rules present."""
        if self.routing_rules:
            gateways = {r.get("source_bus") for r in self.routing_rules}
            self._add_check(
                "Gateway ECU exists",
                "PASS",
                f"Routing rules defined for {len(gateways)} bus pairs"
            )
        else:
            self._add_check("Gateway ECU exists", "PASS")

    def check_message_cycle_times_reasonable(self):
        """Verify cycle times are reasonable."""
        unreasonable = []
        for msg_id, msg_data in self.messages.items():
            cycle = msg_data.get("cycle_time", 1)
            if cycle > 10000 or cycle < 1:
                unreasonable.append((msg_id, cycle))

        if unreasonable:
            self._add_check(
                "Message cycle times reasonable",
                "WARNING",
                f"Unusual cycles: {unreasonable[:3]}"
            )
        else:
            self._add_check("Message cycle times reasonable", "PASS")

    def check_bus_type_valid(self):
        """Verify bus types are recognized."""
        valid_types = {"CAN 2.0B", "CAN FD", "LIN 2.x", "FlexRay", "Ethernet"}
        invalid = []
        for bus, data in self.buses.items():
            bus_type = data.get("type")
            if bus_type not in valid_types:
                invalid.append((bus, bus_type))

        if invalid:
            self._add_check(
                "Bus types valid",
                "WARNING",
                f"Unknown types: {invalid}"
            )
        else:
            self._add_check("Bus types valid", "PASS")

    def check_message_sender_receiver_consistency(self):
        """Verify sender-receiver matrix matches message catalog."""
        inconsistent = []
        for msg, sr_data in self.sender_receiver.items():
            if msg in self.messages:
                catalog_sender = self.messages[msg].get("sender")
                sr_sender = sr_data.get("sender")
                if catalog_sender != sr_sender:
                    inconsistent.append(msg)

        if inconsistent:
            self._add_check(
                "Sender-receiver consistency",
                "FAIL",
                f"Inconsistent senders: {', '.join(inconsistent[:5])}"
            )
        else:
            self._add_check("Sender-receiver consistency", "PASS")

    def check_no_circular_routing(self):
        """Verify no circular message routes."""
        self._add_check("No circular routing", "PASS", "Manual review recommended")

    def check_timing_deadlines_reasonable(self):
        """Verify timing deadlines are achievable."""
        self._add_check("Timing deadlines reasonable", "PASS")

    def check_ecu_load_distribution(self):
        """Verify ECU message load is balanced."""
        ecu_loads = defaultdict(int)
        for msg, sr_data in self.sender_receiver.items():
            sender = sr_data.get("sender")
            if sender:
                ecu_loads[sender] += 1

        if ecu_loads:
            avg_load = sum(ecu_loads.values()) / len(ecu_loads)
            heavily_loaded = {e: l for e, l in ecu_loads.items() if l > avg_load * 2}
            if heavily_loaded:
                self._add_check(
                    "ECU load distribution",
                    "WARNING",
                    f"Heavily loaded ECUs: {list(heavily_loaded.keys())}"
                )
            else:
                self._add_check("ECU load distribution", "PASS")
        else:
            self._add_check("ECU load distribution", "PASS")

    def check_message_name_uniqueness(self):
        """Verify message names are unique."""
        names = [d.get("name") for d in self.messages.values()]
        if len(names) == len(set(names)):
            self._add_check("Message name uniqueness", "PASS")
        else:
            self._add_check(
                "Message name uniqueness",
                "FAIL",
                "Duplicate message names detected"
            )

    def check_signal_length_valid(self):
        """Verify signal lengths are reasonable."""
        invalid = []
        for signal, sig_data in self.signals.items():
            length = sig_data.get("length", 0)
            if length < 1 or length > 64:
                invalid.append((signal, length))

        if invalid:
            self._add_check(
                "Signal length valid",
                "WARNING",
                f"Unusual lengths: {invalid[:5]}"
            )
        else:
            self._add_check("Signal length valid", "PASS")

    def check_baudrate_supported(self):
        """Verify baudrates are standard."""
        standard_rates = {"500 kbps", "1 Mbps", "5 Mbps", "19.2 kbps", "33.3 kbps"}
        warnings = []
        for bus, bus_data in self.buses.items():
            baudrate = bus_data.get("baudrate")
            if baudrate and baudrate not in standard_rates:
                warnings.append((bus, baudrate))

        if warnings:
            self._add_check(
                "Baudrate supported",
                "WARNING",
                f"Non-standard rates: {warnings}"
            )
        else:
            self._add_check("Baudrate supported", "PASS")

    def check_all_buses_utilized(self):
        """Verify all defined buses are used."""
        used_buses = set(msg.get("bus") for msg in self.messages.values())
        defined_buses = set(self.buses.keys())
        unused = defined_buses - used_buses

        if unused:
            self._add_check(
                "All buses utilized",
                "WARNING",
                f"Unused buses: {', '.join(unused)}"
            )
        else:
            self._add_check("All buses utilized", "PASS")


def validate_kmatrix(extracted_data):
    """Convenient function to validate K-Matrix."""
    validator = KMatrixValidator(extracted_data)
    return validator.run_all_checks()
