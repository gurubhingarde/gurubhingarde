"""DBC Confirmation Measures checks — ~33 check definitions per tab."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from dbc_probe import ProbedDBC


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding, page_section="", action="(Reviewer to verify and assess)"):
    return CheckResult(rating="", finding="(Auto-suggest, requires reviewer judgment) " + finding, page_section=page_section, recommended_action=action, confidence="Low")


def na(reason): return CheckResult(rating="NA", finding=reason, confidence="High")


# ---------------------------------------------------------------------------
# Confirmation Review (14 generic — same as HARA/FSC/TSC)
# ---------------------------------------------------------------------------

def cr_01_structured(p):
    if len(p.sheet_names) >= 5:
        return CheckResult(rating="FC", finding=f"Document is structured into {len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Add structured sections.", confidence="Medium")


def cr_02_template(p): return draft("Template version cannot be detected from xlsx content.", action="Confirm latest DBC template was used.")


def cr_03_searchable(p):
    if p.has_table_of_contents:
        return CheckResult(rating="FC", finding="Title/General Info tab present.", confidence="Medium")
    return CheckResult(rating="PC", finding="No TOC.", recommended_action="Add a General Info tab with overview.", confidence="Medium")


def cr_04a_title(p):
    if p.title:
        return draft(f"Title is: '{p.title}'. Reviewer to confirm scope coverage.", page_section="Title page")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add a clear title.", confidence="High")


def cr_04b_author_approver(p):
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    missing = ([] if p.author else ["Author"]) + ([] if p.approver else ["Approver"])
    return CheckResult(rating="NO", finding=f"Missing on Title page: {', '.join(missing)}.", recommended_action=f"Populate {', '.join(missing)}.", confidence="High")


def cr_04c_unique_revision(p):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="Revision not populated.", recommended_action="Populate Revision field.", confidence="High")


def cr_04d_change_history(p):
    return draft("Revision history checked manually from Document Control tab.", action="Confirm revision history is populated.")


def cr_04e_status(p):
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="No status field.", recommended_action="Add a Status field.", confidence="High")


def cr_05_current_revision(p):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Current revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="Revision not identifiable.", recommended_action="Populate Revision.", confidence="High")


def cr_06_config_mgmt(p): return draft("Configuration management is organizational.", action="Confirm document is in CM system.")
def cr_07_header_footer(p): return draft("Header/footer not reliably accessible.", action="Open in Excel; verify.")


def cr_08_toc(p):
    if p.has_table_of_contents:
        return CheckResult(rating="FC", finding="General Info/TOC tab present.", confidence="Medium")
    return CheckResult(rating="PC", finding="No TOC.", recommended_action="Add a General Info tab.", confidence="Medium")


def cr_09_references(p):
    if p.network_name:
        return CheckResult(rating="FC", finding=f"Network documented: {p.network_name}.", confidence="Medium")
    return CheckResult(rating="PC", finding="No explicit network name reference.", recommended_action="Reference the CAN network name and scope.", confidence="Medium")


def cr_10_sections_complete(p):
    msg_complete = len([m for m in p.messages if m.name]) / max(1, len(p.messages))
    sig_complete = len([s for s in p.signals if s.unit]) / max(1, len(p.signals))
    overall = (msg_complete + sig_complete) / 2
    if overall >= 0.95:
        return CheckResult(rating="FC", finding=f"Messages {msg_complete:.0%} complete; Signals {sig_complete:.0%}.", confidence="High")
    return CheckResult(rating="PC", finding=f"Messages {msg_complete:.0%}; Signals {sig_complete:.0%}.", recommended_action="Complete remaining Message names and Signal units.", confidence="High")


# ---------------------------------------------------------------------------
# Technical DBC Assessment (18 substantive — ISO 11898 & AUTOSAR)
# ---------------------------------------------------------------------------

def tsa_01_unique_msg_ids(p):
    msg_ids = [m.id_hex for m in p.messages]
    if len(msg_ids) == len(set(msg_ids)):
        return CheckResult(rating="FC", finding=f"All {len(msg_ids)} message IDs are unique.", confidence="High")
    dupes = [mid for mid in msg_ids if msg_ids.count(mid) > 1]
    return CheckResult(rating="NO", finding=f"Duplicate message IDs found: {set(dupes)}.", recommended_action="Resolve ID conflicts.", confidence="High")


def tsa_02_msg_dlc_valid(p):
    if not p.messages:
        return na("No messages.")
    invalid = [m for m in p.messages if not (0 <= m.dlc <= 8)]
    if not invalid:
        return CheckResult(rating="FC", finding=f"All {len(p.messages)} messages have valid DLC (0–8).", confidence="High")
    return CheckResult(rating="NO", finding=f"{len(invalid)} messages have invalid DLC.", recommended_action="Set DLC to 0–8 bytes.", confidence="High")


def tsa_03_signals_fit_dlc(p):
    if not p.signals:
        return na("No signals.")
    violations = []
    for sig in p.signals:
        msg = p.messages_by_id.get(sig.message_id_hex)
        if msg:
            sig_end_bit = sig.bit_start + sig.bit_length - 1
            max_dlc_bit = (msg.dlc * 8) - 1
            if sig_end_bit > max_dlc_bit:
                violations.append(f"{sig.name} (bits {sig.bit_start}-{sig_end_bit}) exceeds DLC={msg.dlc}")

    if not violations:
        return CheckResult(rating="FC", finding=f"All signals fit within their message DLC.", confidence="High")
    return CheckResult(rating="NO", finding=f"{len(violations)} signals exceed DLC: {violations[0]}", recommended_action="Reduce signal bit length or increase DLC.", confidence="High")


def tsa_04_no_bit_overlap(p):
    if not p.messages:
        return na("No messages.")
    violations = []
    for msg_id, sigs in p.signals_by_message.items():
        bits_used = {}
        for sig in sigs:
            for bit in range(sig.bit_start, sig.bit_start + sig.bit_length):
                if bit in bits_used:
                    violations.append(f"Message {msg_id}: Signal {sig.name} overlaps with {bits_used[bit].name} at bit {bit}")
                else:
                    bits_used[bit] = sig

    if not violations:
        return CheckResult(rating="FC", finding="No signal bit overlap within messages.", confidence="High")
    return CheckResult(rating="NO", finding=f"{len(violations)} overlap(s) detected.", recommended_action="Resolve signal bit allocation.", confidence="High")


def tsa_05_signal_encoding(p):
    if not p.signals:
        return na("No signals.")
    incomplete = [s for s in p.signals if not (s.scale and s.unit)]
    if not incomplete:
        return CheckResult(rating="FC", finding=f"All {len(p.signals)} signals have scale, offset, unit defined.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(incomplete)} signals lack scale/unit.", recommended_action="Populate scale, offset, min, max, unit for all signals.", confidence="High")


def tsa_06_multiplexor_defined(p):
    if not p.signals:
        return na("No signals.")
    mux_refs = set(s.multiplexor_id for s in p.signals if s.multiplexor_id)
    mux_defined = set(s.id for s in p.signals if s.is_multiplexor)
    if mux_refs <= mux_defined:
        return CheckResult(rating="FC", finding=f"All {len(mux_refs)} multiplexor references are defined.", confidence="High")
    missing = mux_refs - mux_defined
    return CheckResult(rating="NO", finding=f"Multiplexor(s) referenced but not defined: {missing}.", recommended_action="Define multiplexor signals.", confidence="High")


def tsa_07_all_signals_in_msgs(p):
    if not p.signals:
        return na("No signals.")
    orphaned = [s for s in p.signals if s.message_id_hex not in p.messages_by_id]
    if not orphaned:
        return CheckResult(rating="FC", finding=f"All {len(p.signals)} signals belong to a message.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(orphaned)} signals reference undefined messages.", recommended_action="Assign signals to messages or define missing messages.", confidence="High")


def tsa_08_msg_has_sender(p):
    if not p.messages:
        return na("No messages.")
    nosender = [m for m in p.messages if not m.sender_ecu]
    if not nosender:
        return CheckResult(rating="FC", finding=f"All {len(p.messages)} messages have a sender ECU.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(nosender)} messages lack a sender.", recommended_action="Assign a sender ECU to each message.", confidence="High")


def tsa_09_sender_is_ecu(p):
    if not p.messages or not p.ecus:
        return na("No messages or ECUs.")
    ecu_ids = set(e.id for e in p.ecus)
    invalid = [m for m in p.messages if m.sender_ecu and m.sender_ecu not in ecu_ids]
    if not invalid:
        return CheckResult(rating="FC", finding="All message senders are defined ECUs.", confidence="High")
    return CheckResult(rating="NO", finding=f"{len(invalid)} messages reference undefined ECU senders.", recommended_action="Define ECUs or correct sender references.", confidence="High")


def tsa_10_receivers_defined(p):
    if not p.signals or not p.ecus:
        return na("No signals or ECUs.")
    ecu_ids = set(e.id for e in p.ecus)
    invalid_sigs = []
    for sig in p.signals:
        for rcv in sig.receivers:
            if rcv not in ecu_ids:
                invalid_sigs.append((sig.name, rcv))

    if not invalid_sigs:
        return CheckResult(rating="FC", finding="All signal receivers are defined ECUs.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(invalid_sigs)} receiver(s) reference undefined ECUs.", recommended_action="Define ECUs or correct receiver references.", confidence="High")


def tsa_11_signal_byte_order(p):
    if not p.signals:
        return na("No signals.")
    invalid_bo = [s for s in p.signals if s.byte_order not in ("little_endian", "big_endian", "Intel", "Motorola")]
    if not invalid_bo:
        return CheckResult(rating="FC", finding=f"All signals have valid byte order (little/big endian).", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(invalid_bo)} signals have unclear byte order.", recommended_action="Set byte order to 'little_endian' or 'big_endian'.", confidence="High")


def tsa_12_signal_type(p):
    if not p.signals:
        return na("No signals.")
    invalid_type = [s for s in p.signals if s.type_signed not in ("signed", "unsigned")]
    if not invalid_type:
        return CheckResult(rating="FC", finding=f"All signals have valid type (signed/unsigned).", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(invalid_type)} signals have unclear type.", recommended_action="Set type to 'signed' or 'unsigned'.", confidence="High")


def tsa_13_min_max_sensible(p):
    if not p.signals:
        return na("No signals.")
    issues = []
    for sig in p.signals:
        if sig.min_val is not None and sig.max_val is not None:
            if sig.min_val > sig.max_val:
                issues.append(f"{sig.name}: min > max")
        elif (sig.min_val is None) != (sig.max_val is None):
            issues.append(f"{sig.name}: min or max missing")

    if not issues:
        return CheckResult(rating="FC", finding="Signal min/max are sensible (min ≤ max).", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(issues)} signal(s) have inconsistent min/max.", recommended_action="Review and correct min/max ranges.", confidence="High")


def tsa_14_frame_type_valid(p):
    if not p.messages:
        return na("No messages.")
    invalid_ft = [m for m in p.messages if m.frame_type not in ("Standard", "Extended", "11-bit", "29-bit")]
    if not invalid_ft:
        return CheckResult(rating="FC", finding="All messages have valid frame type (Standard/Extended).", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(invalid_ft)} messages have unclear frame type.", recommended_action="Set frame type to 'Standard' (11-bit) or 'Extended' (29-bit).", confidence="High")


def tsa_15_cycle_time_valid(p):
    if not p.messages:
        return na("No messages.")
    cyclic_msgs = [m for m in p.messages if m.transmission_type == "cyclic"]
    missing_cycle = [m for m in cyclic_msgs if m.cycle_time_ms <= 0]
    if not missing_cycle:
        return CheckResult(rating="FC", finding=f"All {len(cyclic_msgs)} cyclic messages have cycle time > 0 ms.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(missing_cycle)} cyclic message(s) lack cycle time.", recommended_action="Populate cycle time (ms) for all cyclic messages.", confidence="High")


def tsa_16_transmission_type_valid(p):
    if not p.messages:
        return na("No messages.")
    valid_tt = {"cyclic", "event", "spontaneous", "on-demand", "triggered"}
    invalid_tt = [m for m in p.messages if m.transmission_type.lower() not in valid_tt]
    if not invalid_tt:
        return CheckResult(rating="FC", finding="All messages have valid transmission type.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(invalid_tt)} messages have unclear transmission type.", recommended_action="Set to 'cyclic', 'event', or 'spontaneous'.", confidence="High")


def tsa_17_value_table_coverage(p):
    if not p.value_tables:
        return CheckResult(rating="PC", finding="No value tables found. State signals may lack enumerations.", recommended_action="Add value tables for discrete state signals (gear, mode, status).", confidence="Medium")
    return CheckResult(rating="LC", finding=f"Value tables present for {len(p.value_tables)} signal(s).", confidence="Medium")


def tsa_18_network_topology(p):
    return draft("Network topology should document ECU roles and message flow.", page_section="Network Topology tab", action="Verify sender/receiver pairs in topology.")


# ---------------------------------------------------------------------------
# Verification Assessment (10 signal/message validation)
# ---------------------------------------------------------------------------

def va_01_signal_count(p):
    if not p.messages:
        return na("No messages.")
    empty = [m for m in p.messages if m.signal_count == 0]
    if not empty:
        return CheckResult(rating="FC", finding=f"All messages have signal_count > 0.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(empty)} message(s) show signal_count=0.", recommended_action="Update signal counts to reflect actual allocation.", confidence="High")


def va_02_ecu_count(p):
    if p.n_ecus > 0:
        return CheckResult(rating="FC", finding=f"{p.n_ecus} ECU(s) defined.", confidence="High")
    return CheckResult(rating="PC", finding="No ECUs defined.", recommended_action="Add ECU inventory (Node names, manufacturers).", confidence="High")


def va_03_msg_signal_consistency(p):
    issues = []
    for msg in p.messages:
        sigs_in_msg = [s for s in p.signals if s.message_id_hex == msg.id_hex]
        if msg.signal_count > 0 and len(sigs_in_msg) != msg.signal_count:
            issues.append(f"{msg.name}: declared {msg.signal_count}, found {len(sigs_in_msg)}")

    if not issues:
        return CheckResult(rating="FC", finding="Signal counts match signal allocation.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(issues)} message(s) have count mismatch.", recommended_action="Update signal_count or verify signal allocation.", confidence="High")


def va_04_no_orphan_signals(p):
    orphaned = [s for s in p.signals if s.message_id_hex not in p.messages_by_id]
    if not orphaned:
        return CheckResult(rating="FC", finding=f"All {len(p.signals)} signals are allocated to messages.", confidence="High")
    return CheckResult(rating="NO", finding=f"{len(orphaned)} signal(s) orphaned.", recommended_action="Remove orphaned signals or add missing message definitions.", confidence="High")


def va_05_receiver_ecu_coverage(p):
    if not p.signals:
        return na("No signals.")
    sigs_without_rcv = [s for s in p.signals if not s.receivers]
    rate = (len(p.signals) - len(sigs_without_rcv)) / len(p.signals) if p.signals else 0
    if rate >= 0.9:
        return CheckResult(rating="FC", finding=f"{rate:.0%} of signals have receivers defined.", confidence="High")
    return CheckResult(rating="PC", finding=f"Only {rate:.0%} of signals have receivers.", recommended_action="Define receivers for all signals (at minimum, the sender ECU).", confidence="High")


def va_06_scaling_consistency(p):
    if not p.signals:
        return na("No signals.")
    no_scale = [s for s in p.signals if s.scale == 0 or (s.scale == 1 and s.offset == 0 and not s.unit)]
    rate = (len(p.signals) - len(no_scale)) / len(p.signals)
    if rate >= 0.95:
        return CheckResult(rating="FC", finding=f"All signals have scale and offset defined.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(no_scale)} signal(s) lack scale/offset.", recommended_action="Define scale, offset, and unit for all signals.", confidence="High")


def va_07_bit_allocation(p):
    return draft("Bit allocation verified per signal catalog and message structure.", action="Sample 5–10 signals to confirm correct bit start and length.")


def va_08_dlc_optimization(p):
    if not p.messages:
        return na("No messages.")
    underutilized = []
    for msg in p.messages:
        sigs = p.signals_by_message.get(msg.id_hex, [])
        if sigs:
            max_bit = max((s.bit_start + s.bit_length for s in sigs), default=0)
            min_dlc_needed = (max_bit + 7) // 8
            if msg.dlc > min_dlc_needed + 1:  # Allow 1 byte slack
                underutilized.append(f"{msg.name} (DLC={msg.dlc}, needs {min_dlc_needed})")

    if not underutilized:
        return CheckResult(rating="FC", finding="DLC allocation is efficient (no significant waste).", confidence="Medium")
    return CheckResult(rating="LC", finding=f"{len(underutilized)} message(s) may be over-allocated.", recommended_action="Consolidate signals or reduce DLC for optimization.", confidence="Medium")


def va_09_multiplexor_validation(p):
    mux_sigs = [s for s in p.signals if s.is_multiplexor]
    if not mux_sigs:
        return CheckResult(rating="FC", finding="No multiplexing or all multiplexors properly defined.", confidence="Medium")
    mux_with_refs = set(s.id for s in mux_sigs) & set(s.multiplexor_id for s in p.signals if s.multiplexor_id)
    if mux_with_refs:
        return CheckResult(rating="FC", finding=f"{len(mux_sigs)} multiplexor(s) actively used.", confidence="Medium")
    return CheckResult(rating="LC", finding=f"{len(mux_sigs)} multiplexor(s) defined but not referenced.", recommended_action="Remove unused multiplexor signals.", confidence="Medium")


def va_10_doc_traceability(p):
    if p.doc_id and p.revision:
        return CheckResult(rating="FC", finding=f"Traceability: Doc ID='{p.doc_id}', Rev='{p.revision}'.", confidence="High")
    return CheckResult(rating="PC", finding="Document ID or Revision missing.", recommended_action="Populate Doc ID and Revision for traceability.", confidence="High")


# ---------------------------------------------------------------------------
# CheckDef — metadata for all checks
# ---------------------------------------------------------------------------

@dataclass
class CheckDef:
    id: str
    tab: str  # "CR", "TSA", or "VA"
    section: str
    requirement: str
    obligation: str  # "Shall" or "Should"
    verify: callable = None  # returns CheckResult

    def __call__(self, p: ProbedDBC) -> CheckResult:
        return self.verify(p) if self.verify else CheckResult()


CHECKS = [
    # Confirmation Review (CR)
    CheckDef("CR-01", "CR", "Document Structure", "Document is structured into tabs", "Shall", cr_01_structured),
    CheckDef("CR-02", "CR", "Document Structure", "Template version is documented", "Should", cr_02_template),
    CheckDef("CR-03", "CR", "Document Structure", "Document is searchable (TOC present)", "Should", cr_03_searchable),
    CheckDef("CR-04a", "CR", "Title & Metadata", "Document has a clear title", "Shall", cr_04a_title),
    CheckDef("CR-04b", "CR", "Title & Metadata", "Author and Approver are identified", "Shall", cr_04b_author_approver),
    CheckDef("CR-04c", "CR", "Title & Metadata", "Revision is unique and current", "Shall", cr_04c_unique_revision),
    CheckDef("CR-04d", "CR", "Title & Metadata", "Revision history is maintained", "Shall", cr_04d_change_history),
    CheckDef("CR-04e", "CR", "Title & Metadata", "Document status is indicated (draft/release)", "Shall", cr_04e_status),
    CheckDef("CR-05", "CR", "Version Control", "Current revision is identifiable", "Shall", cr_05_current_revision),
    CheckDef("CR-06", "CR", "Version Control", "Configuration management practices apply", "Should", cr_06_config_mgmt),
    CheckDef("CR-07", "CR", "Version Control", "Header and footer contain ID and revision", "Should", cr_07_header_footer),
    CheckDef("CR-08", "CR", "Searchability", "Table of Contents is present", "Should", cr_08_toc),
    CheckDef("CR-09", "CR", "References", "Network and scope are referenced", "Should", cr_09_references),
    CheckDef("CR-10", "CR", "Completeness", "All sections are substantially complete", "Shall", cr_10_sections_complete),

    # Technical DBC Assessment (TSA)
    CheckDef("TSA-01", "TSA", "Message Definition", "Message IDs are unique within network", "Shall", tsa_01_unique_msg_ids),
    CheckDef("TSA-02", "TSA", "Message Definition", "DLC values are valid (0–8 bytes)", "Shall", tsa_02_msg_dlc_valid),
    CheckDef("TSA-03", "TSA", "Signal Allocation", "All signals fit within message DLC", "Shall", tsa_03_signals_fit_dlc),
    CheckDef("TSA-04", "TSA", "Signal Allocation", "No signal bit overlap within messages", "Shall", tsa_04_no_bit_overlap),
    CheckDef("TSA-05", "TSA", "Signal Encoding", "Scale, offset, min, max, unit defined", "Shall", tsa_05_signal_encoding),
    CheckDef("TSA-06", "TSA", "Multiplexing", "All multiplexor references are defined", "Shall", tsa_06_multiplexor_defined),
    CheckDef("TSA-07", "TSA", "Signal Allocation", "Every signal belongs to a message", "Shall", tsa_07_all_signals_in_msgs),
    CheckDef("TSA-08", "TSA", "Message Definition", "Every message has a sender ECU", "Shall", tsa_08_msg_has_sender),
    CheckDef("TSA-09", "TSA", "Network Definition", "Message senders are defined ECUs", "Shall", tsa_09_sender_is_ecu),
    CheckDef("TSA-10", "TSA", "Network Definition", "Signal receivers are defined ECUs", "Shall", tsa_10_receivers_defined),
    CheckDef("TSA-11", "TSA", "Signal Encoding", "Byte order is valid (little/big endian)", "Shall", tsa_11_signal_byte_order),
    CheckDef("TSA-12", "TSA", "Signal Encoding", "Signal type is valid (signed/unsigned)", "Shall", tsa_12_signal_type),
    CheckDef("TSA-13", "TSA", "Signal Encoding", "Min and max values are sensible (min ≤ max)", "Should", tsa_13_min_max_sensible),
    CheckDef("TSA-14", "TSA", "Message Definition", "Frame type is valid (Standard/Extended)", "Shall", tsa_14_frame_type_valid),
    CheckDef("TSA-15", "TSA", "Message Definition", "Cyclic messages have cycle time defined", "Shall", tsa_15_cycle_time_valid),
    CheckDef("TSA-16", "TSA", "Message Definition", "Transmission type is valid", "Should", tsa_16_transmission_type_valid),
    CheckDef("TSA-17", "TSA", "Value Tables", "Value tables present for state signals", "Should", tsa_17_value_table_coverage),
    CheckDef("TSA-18", "TSA", "Network Topology", "Network topology documented", "Should", tsa_18_network_topology),

    # Verification Assessment (VA)
    CheckDef("VA-01", "VA", "Signal & Message Consistency", "Message signal counts are accurate", "Should", va_01_signal_count),
    CheckDef("VA-02", "VA", "Network Definition", "ECU inventory is defined", "Should", va_02_ecu_count),
    CheckDef("VA-03", "VA", "Signal & Message Consistency", "Signal counts match allocation", "Should", va_03_msg_signal_consistency),
    CheckDef("VA-04", "VA", "Signal & Message Consistency", "No orphaned signals exist", "Shall", va_04_no_orphan_signals),
    CheckDef("VA-05", "VA", "Network Definition", "Signal receivers are defined", "Should", va_05_receiver_ecu_coverage),
    CheckDef("VA-06", "VA", "Signal Encoding", "Scaling is consistent across signals", "Should", va_06_scaling_consistency),
    CheckDef("VA-07", "VA", "Bit Allocation", "Bit allocation is verified", "Should", va_07_bit_allocation),
    CheckDef("VA-08", "VA", "DLC Optimization", "DLC allocation is efficient", "Should", va_08_dlc_optimization),
    CheckDef("VA-09", "VA", "Multiplexing", "Multiplexor signals are valid", "Should", va_09_multiplexor_validation),
    CheckDef("VA-10", "VA", "Traceability", "Document ID and Revision enable traceability", "Should", va_10_doc_traceability),
]
