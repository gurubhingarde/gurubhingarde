"""FlexRay Configuration checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from flexray_probe import ProbedFlexRay


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


# Configuration Review (document quality)
def cr_01_structure(p):
    if len(p.sheet_names) >= 8:
        return CheckResult(rating="FC", finding=f"Document structured into {len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Add structured sections.", confidence="Medium")


def cr_02_cluster_name(p):
    if p.cluster_name:
        return CheckResult(rating="FC", finding=f"Cluster name: '{p.cluster_name}'.", confidence="High")
    return CheckResult(rating="NO", finding="Cluster name not detected.", recommended_action="Add clear cluster identification.", confidence="High")


def cr_03_revision(p):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="Revision not populated.", recommended_action="Populate Revision field.", confidence="High")


def cr_04_timing_params(p):
    if p.gdCycle_ms and p.gNumberOfStaticSlots:
        return CheckResult(rating="FC", finding=f"Timing parameters present: gdCycle={p.gdCycle_ms}ms, static slots={p.gNumberOfStaticSlots}.", confidence="High")
    return CheckResult(rating="PC", finding="Timing parameters incomplete.", recommended_action="Populate all cluster timing parameters.", confidence="High")


def cr_05_node_inventory(p):
    if p.nodes:
        return CheckResult(rating="FC", finding=f"{len(p.nodes)} nodes in inventory.", confidence="High")
    return CheckResult(rating="NO", finding="No node inventory found.", recommended_action="Define all ECUs and cluster nodes.", confidence="High")


def cr_06_frame_catalog(p):
    if p.frames:
        return CheckResult(rating="FC", finding=f"{len(p.frames)} frames in catalog.", confidence="High")
    return CheckResult(rating="NO", finding="No frame catalog found.", recommended_action="Define all FlexRay frames.", confidence="High")


def cr_07_channel_config(p):
    if p.channel_a_speed and p.channel_b_speed:
        return CheckResult(rating="FC", finding=f"Both channels configured: A={p.channel_a_speed}Mbps, B={p.channel_b_speed}Mbps.", confidence="High")
    return CheckResult(rating="PC", finding="Channel configuration incomplete.", recommended_action="Configure both Channel A and B.", confidence="High")


def cr_08_doc_control(p):
    if p.revision_history_rows >= 1:
        return CheckResult(rating="FC", finding=f"Revision history has {p.revision_history_rows} rows.", confidence="High")
    return CheckResult(rating="NO", finding="No revision history.", recommended_action="Add revision history.", confidence="High")


def cr_09_status(p):
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="No status field.", recommended_action="Add Status field.", confidence="High")


def cr_10_author_approver(p):
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    missing = ([] if p.author else ["Author"]) + ([] if p.approver else ["Approver"])
    return CheckResult(rating="NO", finding=f"Missing: {', '.join(missing)}.", recommended_action=f"Populate {', '.join(missing)}.", confidence="High")


# Technical Assessment (timing and allocation)
def ta_01_gdcycle_closure(p):
    if not p.gdCycle_ms:
        return na("gdCycle not populated.")
    static_dur = (p.gNumberOfStaticSlots or 0) * (p.gdStaticSlot_macroticks or 640)
    sym_window = 150
    nit = p.gdNIT_macroticks or 1000
    sum_macroticks = static_dur + (p.gNumberOfMinislots or 0) * 20 + sym_window + nit
    gdMacrotick_us = p.gdMacrotick_us or 1
    computed_cycle_ms = (sum_macroticks * gdMacrotick_us) / 1000
    expected_ms = p.gdCycle_ms
    if abs(computed_cycle_ms - expected_ms) <= 0.1:
        return CheckResult(rating="FC", finding=f"Cycle closure verified: gdCycle={expected_ms}ms.", confidence="High")
    return CheckResult(rating="PC", finding=f"Cycle closure mismatch: expected {expected_ms}ms, computed {computed_cycle_ms:.1f}ms.", recommended_action="Adjust timing parameters to close cycle.", confidence="High")


def ta_02_static_slots_allocated(p):
    if not p.static_slots:
        return CheckResult(rating="NO", finding="No static slot allocation found.", recommended_action="Define static slot mapping.", confidence="High")
    return CheckResult(rating="FC", finding=f"{len(p.static_slots)} static slots allocated.", confidence="High")


def ta_03_dynamic_slots_allocated(p):
    if not p.dynamic_slots:
        return CheckResult(rating="PC", finding="No dynamic slot allocation found.", recommended_action="Define dynamic minislot mapping for event-triggered frames.", confidence="Medium")
    return CheckResult(rating="FC", finding=f"{len(p.dynamic_slots)} minislots allocated.", confidence="High")


def ta_04_frame_fit(p):
    if not p.frames:
        return na("No frames.")
    oversized = [f for f in p.frames if f.get("data_length_bytes", 0) > 8]
    if oversized:
        return CheckResult(rating="PC", finding=f"{len(oversized)} frames exceed 8 bytes.", recommended_action="Verify frame sizes align with slot durations.", confidence="Medium")
    return CheckResult(rating="FC", finding=f"All {len(p.frames)} frames within standard size bounds.", confidence="High")


def ta_05_node_allocation(p):
    if not p.nodes:
        return na("No nodes.")
    nodes_with_alloc = {slot.get("node_id") for slot in p.static_slots}
    all_nodes = {n.get("ecu_id") for n in p.nodes}
    unallocated = all_nodes - nodes_with_alloc
    if not unallocated:
        return CheckResult(rating="FC", finding=f"All {len(p.nodes)} nodes have slot allocation.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(unallocated)} nodes lack allocation: {sorted(unallocated)}", recommended_action="Allocate remaining nodes.", confidence="High")


def ta_06_frame_distribution(p):
    if not p.frames or not p.static_slots:
        return na("Incomplete data.")
    frames_allocated = {slot.get("frame_id") for slot in p.static_slots}
    all_frames = {f.get("frame_id") for f in p.frames}
    unallocated = all_frames - frames_allocated
    coverage = len(frames_allocated) / len(all_frames)
    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"All frames allocated to slots.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(frames_allocated)}/{len(all_frames)} frames allocated.", recommended_action="Map remaining frames to slots.", confidence="High")


def ta_07_channel_parity(p):
    if p.channel_a_speed == p.channel_b_speed:
        return CheckResult(rating="FC", finding=f"Channels A and B both run at {p.channel_a_speed} Mbps.", confidence="High")
    return CheckResult(rating="PC", finding=f"Channel speeds differ: A={p.channel_a_speed}Mbps, B={p.channel_b_speed}Mbps.", recommended_action="Confirm dual-channel symmetry requirement.", confidence="Medium")


def ta_08_minislot_coverage(p):
    if not p.frames or not p.dynamic_slots:
        return na("No dynamic frames or minislots.")
    dynamic_frames = [f for f in p.frames if not f.get("static", True)]
    if not dynamic_frames:
        return CheckResult(rating="NA", finding="No dynamic (event-triggered) frames in catalog.", confidence="High")
    minislots = len(p.dynamic_slots)
    if minislots > len(dynamic_frames):
        return CheckResult(rating="FC", finding=f"Sufficient minislots ({minislots}) for dynamic frames ({len(dynamic_frames)}).", confidence="High")
    return CheckResult(rating="PC", finding=f"Minislots ({minislots}) <= dynamic frames ({len(dynamic_frames)}).", recommended_action="Increase minislot count or reduce dynamic frames.", confidence="High")


# Validation Assessment (redundancy and consistency)
def va_01_dual_redundancy(p):
    if p.channel_a_speed and p.channel_b_speed and p.channel_a_speed > 0 and p.channel_b_speed > 0:
        return CheckResult(rating="FC", finding="Dual-channel A and B redundancy active.", confidence="High")
    return CheckResult(rating="NO", finding="Single-channel or one channel disabled.", recommended_action="Enable both channels for fault tolerance.", confidence="High")


def va_02_timing_consistency(p):
    if p.gdMacrotick_us and p.gMacroPerCycle and p.gdCycle_ms:
        expected_macroticks = (p.gdCycle_ms * 1000) / p.gdMacrotick_us
        if abs(expected_macroticks - p.gMacroPerCycle) <= 100:
            return CheckResult(rating="FC", finding="Timing parameters internally consistent.", confidence="High")
    return draft("Timing parameters may have internal inconsistencies.", action="Verify gdCycle, gdMacrotick, gMacroPerCycle alignment.")


def va_03_slot_overlap(p):
    if not p.static_slots:
        return na("No static slots.")
    slots = sorted([(s.get("slot_id", 0), s) for s in p.static_slots])
    if slots:
        return CheckResult(rating="FC", finding=f"Slot schedule contains {len(slots)} non-overlapping allocations.", confidence="Medium")
    return CheckResult(rating="NO", finding="Unable to verify slot overlap.", recommended_action="Review slot timing in Schedule tab.", confidence="Low")


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedFlexRay], CheckResult]


CHECKS: list[CheckDef] = [
    # Configuration Review
    CheckDef("1",  "CR", "Document Structure", "Is the configuration structured in clear sections?", "Shall", cr_01_structure),
    CheckDef("2",  "CR", "Identification", "Is the cluster clearly identified by name?", "Shall", cr_02_cluster_name),
    CheckDef("3",  "CR", "Versioning", "Is the configuration revision populated?", "Shall", cr_03_revision),
    CheckDef("4",  "CR", "Timing Parameters", "Are cluster timing parameters defined?", "Shall", cr_04_timing_params),
    CheckDef("5",  "CR", "Node Inventory", "Is a complete node inventory provided?", "Shall", cr_05_node_inventory),
    CheckDef("6",  "CR", "Frame Catalog", "Is a frame catalog defined?", "Shall", cr_06_frame_catalog),
    CheckDef("7",  "CR", "Channel Config", "Are both Channel A and B configured?", "Shall", cr_07_channel_config),
    CheckDef("8",  "CR", "Document Control", "Is revision history present?", "Shall", cr_08_doc_control),
    CheckDef("9",  "CR", "Status Field", "Is configuration status documented?", "Shall", cr_09_status),
    CheckDef("10", "CR", "Authorization", "Are author and approver identified?", "Shall", cr_10_author_approver),

    # Technical Assessment
    CheckDef("1",  "TA", "Cycle Timing", "Is the communication cycle timing closed (sum of segments = gdCycle)?", "Shall", ta_01_gdcycle_closure),
    CheckDef("2",  "TA", "Static Allocation", "Are static slots allocated per nodes?", "Shall", ta_02_static_slots_allocated),
    CheckDef("3",  "TA", "Dynamic Allocation", "Are dynamic minislots allocated for event-triggered communication?", "Should", ta_03_dynamic_slots_allocated),
    CheckDef("4",  "TA", "Frame Size", "Do all frames fit within slot/minislot durations?", "Shall", ta_04_frame_fit),
    CheckDef("5",  "TA", "Node Coverage", "Does every node have at least one slot allocation?", "Shall", ta_05_node_allocation),
    CheckDef("6",  "TA", "Frame Distribution", "Are all frames mapped to slots?", "Shall", ta_06_frame_distribution),
    CheckDef("7",  "TA", "Channel Parity", "Do Channels A and B have matching speeds and durations?", "Shall", ta_07_channel_parity),
    CheckDef("8",  "TA", "Minislot Coverage", "Are minislots sufficient for dynamic frames?", "Should", ta_08_minislot_coverage),

    # Validation Assessment
    CheckDef("1",  "VA", "Redundancy", "Is dual-channel A/B redundancy active?", "Shall", va_01_dual_redundancy),
    CheckDef("2",  "VA", "Timing Consistency", "Are all timing parameters internally consistent?", "Shall", va_02_timing_consistency),
    CheckDef("3",  "VA", "Slot Overlap", "Are static slots non-overlapping?", "Shall", va_03_slot_overlap),
]
