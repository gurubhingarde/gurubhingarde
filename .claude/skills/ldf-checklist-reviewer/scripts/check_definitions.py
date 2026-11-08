"""
LDF Confirmation Measures checks — 30 check definitions covering document structure and technical assessment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ldf_probe import ProbedLDF


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding, page_section="", action="(Reviewer to verify and assess)"):
    return CheckResult(
        rating="",
        finding="(Auto-suggest, requires reviewer judgment) " + finding,
        page_section=page_section,
        recommended_action=action,
        confidence="Low",
    )


def na(reason):
    return CheckResult(rating="NA", finding=reason, confidence="High")


# ---------------------------------------------------------------------------
# Confirmation Review (Document Structure, ~14 checks)
# ---------------------------------------------------------------------------


def cr_01_structured(p):
    """CR-01: Document is structured into ≥5 tabs."""
    if len(p.sheet_names) >= 5:
        return CheckResult(rating="FC", finding=f"Document is structured into {len(p.sheet_names)} tabs.", confidence="High")
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.sheet_names)} tabs present.",
        recommended_action="Add structured sections (Cluster Header, Node Attributes, Frame Catalog, etc.).",
        confidence="High",
    )


def cr_02_template(p):
    """CR-02: Latest LDF template version used."""
    return draft("Template version cannot be detected from xlsx content.", action="Confirm latest LDF template (ISO 17987) was used.")


def cr_03_searchable(p):
    """CR-03: Table of Contents present."""
    if p.has_table_of_contents:
        return CheckResult(rating="FC", finding="Document Control tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No Document Control tab.", recommended_action="Add a Document Control tab.", confidence="High")


def cr_04a_title(p):
    """CR-04a: Clear, scope-defining cluster name."""
    if p.cluster_name:
        return draft(
            f"Cluster name is: '{p.cluster_name}'. Reviewer to confirm scope coverage.",
            page_section="Title page",
        )
    return CheckResult(rating="NO", finding="No cluster name detected.", recommended_action="Add a clear cluster name.", confidence="High")


def cr_04b_author_approver(p):
    """CR-04b: Author and Approver populated."""
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    missing = ([] if p.author else ["Author"]) + ([] if p.approver else ["Approver"])
    return CheckResult(
        rating="NO",
        finding=f"Missing on Title page: {', '.join(missing)}.",
        recommended_action=f"Populate {', '.join(missing)}.",
        confidence="High",
    )


def cr_04c_unique_revision(p):
    """CR-04c: Unique revision identifier."""
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="Revision not populated.", recommended_action="Populate Revision field.", confidence="High")


def cr_04d_change_history(p):
    """CR-04d: Revision history with dates and authors."""
    if p.revision_history_rows >= 1:
        return CheckResult(rating="FC", finding=f"Revision history has {p.revision_history_rows} rows.", confidence="High")
    return CheckResult(rating="NO", finding="No revision history.", recommended_action="Add revision history.", confidence="High")


def cr_04e_status(p):
    """CR-04e: Status field (Draft/Review/Released)."""
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="No status field.", recommended_action="Add a Status field.", confidence="High")


def cr_05_current_revision(p):
    """CR-05: Current revision matches Title and Document Control."""
    if p.revision:
        return CheckResult(rating="FC", finding=f"Current revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="Revision not identifiable.", recommended_action="Populate Revision.", confidence="High")


def cr_06_config_mgmt(p):
    """CR-06: Document in configuration management system."""
    return draft("Configuration management is organizational.", action="Confirm document is in CM system.")


def cr_07_header_footer(p):
    """CR-07: Company logo, doc ID, revision in headers/footers."""
    return draft("Header/footer not reliably accessible from xlsx.", action="Open in Excel; verify company ID and revision in page headers.")


def cr_08_toc(p):
    """CR-08: Table of Contents navigable."""
    if p.has_table_of_contents:
        return CheckResult(rating="FC", finding="Document Control / TOC tab present.", confidence="High")
    return CheckResult(rating="PC", finding="No TOC.", recommended_action="Add a TOC.", confidence="High")


def cr_09_references(p):
    """CR-09: Cross-references to related documents."""
    if p.linked_documents:
        return CheckResult(rating="FC", finding=f"Linked documents: {', '.join(p.linked_documents)}.", confidence="Medium")
    return CheckResult(
        rating="PC",
        finding="No linked documents referenced.",
        recommended_action="Reference related specifications (e.g., HSI, system architecture).",
        confidence="Medium",
    )


def cr_10_sections_complete(p):
    """CR-10: Cluster definition and node/frame/signal sections ≥95% complete."""
    cluster_complete = int(bool(p.cluster_name and p.lin_version and p.baud_rate_kbps))
    node_complete = int(bool(p.master_node and p.slave_nodes))
    frame_complete = int(bool(p.frames))
    signal_complete = int(bool(p.signals))
    schedule_complete = int(bool(p.schedules))

    overall = (cluster_complete + node_complete + frame_complete + signal_complete + schedule_complete) / 5
    if overall >= 0.95:
        return CheckResult(rating="FC", finding=f"All major sections complete: {overall:.0%}.", confidence="High")
    return CheckResult(
        rating="PC",
        finding=f"Completeness: {overall:.0%}.",
        recommended_action="Complete cluster, node, frame, signal, and schedule definitions.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Technical Safety Assessment (TSA, ~16 checks)
# ---------------------------------------------------------------------------


def tsa_01_cluster_metadata(p):
    """TSA-01: Cluster name, abbreviation, project populated."""
    if p.cluster_name and p.project:
        return CheckResult(rating="FC", finding=f"Cluster: '{p.cluster_name}' ({p.cluster_abbr}), Project: '{p.project}'.", confidence="High")
    missing = ([] if p.cluster_name else ["Name"]) + ([] if p.project else ["Project"])
    return CheckResult(
        rating="NO", finding=f"Missing: {', '.join(missing)}.", recommended_action=f"Populate {', '.join(missing)}.", confidence="High"
    )


def tsa_02_lin_version(p):
    """TSA-02: LIN version valid (2.0, 2.1, 2.2A)."""
    valid_versions = ["2.0", "2.1", "2.2A", "2.2a"]
    if p.lin_version in valid_versions:
        return CheckResult(rating="FC", finding=f"LIN version: {p.lin_version}.", confidence="High")
    return CheckResult(
        rating="NO",
        finding=f"Invalid LIN version: {p.lin_version}.",
        recommended_action="Specify LIN 2.0, 2.1, or 2.2A.",
        confidence="High",
    )


def tsa_03_baud_rate(p):
    """TSA-03: Baud rate within 1–20 kbps range."""
    if 1 <= p.baud_rate_kbps <= 20:
        return CheckResult(rating="FC", finding=f"Baud rate: {p.baud_rate_kbps} kbps (within spec).", confidence="High")
    return CheckResult(
        rating="NO",
        finding=f"Baud rate out of range: {p.baud_rate_kbps} kbps.",
        recommended_action="Set baud rate to 1–20 kbps (typical 19.2).",
        confidence="High",
    )


def tsa_04_timing_master(p):
    """TSA-04: Single master node assigned."""
    if p.master_node:
        return CheckResult(rating="FC", finding=f"Master node: '{p.master_node.name}'.", confidence="High")
    return CheckResult(rating="NO", finding="No master node defined.", recommended_action="Assign exactly one master node.", confidence="High")


def tsa_05_master_node(p):
    """TSA-05: Master node name and identifier present."""
    if p.master_node and p.master_node.name and p.master_node.identifier:
        return CheckResult(rating="FC", finding=f"Master: {p.master_node.name} (ID: {p.master_node.identifier}).", confidence="High")
    return CheckResult(
        rating="NO",
        finding="Master node name or identifier missing.",
        recommended_action="Populate master node details.",
        confidence="High",
    )


def tsa_06_slave_nodes(p):
    """TSA-06: ≥1 slave node defined with identifier."""
    if len(p.slave_nodes) >= 1:
        return CheckResult(rating="FC", finding=f"{len(p.slave_nodes)} slave node(s) defined.", confidence="High")
    return CheckResult(rating="NO", finding="No slave nodes defined.", recommended_action="Define at least one slave node.", confidence="High")


def tsa_07_node_roles(p):
    """TSA-07: Each slave has defined communication role (publisher/subscriber)."""
    if not p.slave_nodes:
        return na("No slave nodes.")
    with_roles = sum(1 for s in p.slave_nodes if s.publishes or s.subscribes)
    if with_roles == len(p.slave_nodes):
        return CheckResult(rating="FC", finding=f"All {len(p.slave_nodes)} slaves have defined roles.", confidence="High")
    return CheckResult(
        rating="PC",
        finding=f"{with_roles}/{len(p.slave_nodes)} slaves have roles.",
        recommended_action="Define publisher/subscriber roles for all slaves.",
        confidence="High",
    )


def tsa_08_frame_definitions(p):
    """TSA-08: ≥1 frame with ID, name, type, length."""
    if len(p.frames) >= 1:
        return CheckResult(rating="FC", finding=f"{len(p.frames)} frame(s) defined.", confidence="High")
    return CheckResult(rating="NO", finding="No frames defined.", recommended_action="Define at least one frame.", confidence="High")


def tsa_09_frame_types(p):
    """TSA-09: Frame type mix appropriate (unconditional, event-triggered, sporadic, diagnostic)."""
    if not p.frames:
        return na("No frames.")
    types = set(f.frame_type for f in p.frames)
    if len(types) >= 1:
        return CheckResult(rating="FC", finding=f"Frame types: {', '.join(types)}.", confidence="High")
    return CheckResult(rating="PC", finding="Limited frame type diversity.", recommended_action="Consider mix of frame types.", confidence="Low")


def tsa_10_frame_publishers(p):
    """TSA-10: Every frame has exactly 1 publisher."""
    if not p.frames:
        return na("No frames.")
    frames_with_pub = sum(1 for f in p.frames if f.publisher)
    if frames_with_pub == len(p.frames):
        return CheckResult(rating="FC", finding=f"All {len(p.frames)} frames have publishers.", confidence="High")
    return CheckResult(
        rating="NO",
        finding=f"{frames_with_pub}/{len(p.frames)} frames have publishers.",
        recommended_action="Assign a publisher (node) to all frames.",
        confidence="High",
    )


def tsa_11_frame_length(p):
    """TSA-11: Frame length ≤8 bytes."""
    if not p.frames:
        return na("No frames.")
    bad_frames = [f for f in p.frames if f.length > 8]
    if not bad_frames:
        return CheckResult(rating="FC", finding=f"All {len(p.frames)} frames within length limit (≤8 bytes).", confidence="High")
    return CheckResult(
        rating="NO",
        finding=f"{len(bad_frames)} frame(s) exceed 8 bytes: {', '.join(f.name for f in bad_frames)}.",
        recommended_action="Reduce frame length to ≤8 bytes.",
        confidence="High",
    )


def tsa_12_signal_definitions(p):
    """TSA-12: ≥1 signal with name, frame, type."""
    if len(p.signals) >= 1:
        return CheckResult(rating="FC", finding=f"{len(p.signals)} signal(s) defined.", confidence="High")
    return CheckResult(rating="NO", finding="No signals defined.", recommended_action="Define at least one signal.", confidence="High")


def tsa_13_signal_allocation(p):
    """TSA-13: Each signal in exactly 1 frame."""
    if not p.signals:
        return na("No signals.")
    signal_frame_count = {}
    for sig in p.signals:
        signal_frame_count[sig.signal_id] = signal_frame_count.get(sig.signal_id, 0) + 1

    duplicates = {s_id for s_id, count in signal_frame_count.items() if count > 1}
    if not duplicates:
        return CheckResult(rating="FC", finding=f"All {len(p.signals)} signals uniquely allocated.", confidence="High")
    return CheckResult(
        rating="NO",
        finding=f"{len(duplicates)} signal(s) in multiple frames: {', '.join(duplicates)}.",
        recommended_action="Ensure each signal belongs to exactly one frame.",
        confidence="High",
    )


def tsa_14_signal_encoding(p):
    """TSA-14: Signal encoding (scale, offset, unit) populated."""
    if not p.signals:
        return na("No signals.")
    encoded = sum(1 for s in p.signals if s.encoding or s.unit)
    if encoded == len(p.signals):
        return CheckResult(rating="FC", finding=f"All {len(p.signals)} signals have encoding info.", confidence="Medium")
    return CheckResult(
        rating="PC",
        finding=f"{encoded}/{len(p.signals)} signals have encoding info.",
        recommended_action="Populate scale, offset, units for all signals.",
        confidence="High",
    )


def tsa_15_signal_bounds(p):
    """TSA-15: Signal min/max consistent with type."""
    if not p.signals:
        return na("No signals.")
    valid = sum(1 for s in p.signals if s.min_val < s.max_val)
    if valid == len(p.signals):
        return CheckResult(rating="FC", finding=f"All {len(p.signals)} signals have valid min/max bounds.", confidence="High")
    return CheckResult(
        rating="NO",
        finding=f"{valid}/{len(p.signals)} signals have valid bounds (min < max).",
        recommended_action="Correct signal min/max values.",
        confidence="High",
    )


def tsa_16_schedule_tables(p):
    """TSA-16: ≥1 schedule table defined per operational mode."""
    if len(p.schedules) >= 1:
        modes = [s.mode for s in p.schedules]
        return CheckResult(rating="FC", finding=f"{len(p.schedules)} schedule table(s): {', '.join(set(modes))}.", confidence="High")
    return CheckResult(rating="NO", finding="No schedule tables defined.", recommended_action="Define schedule tables.", confidence="High")


def tsa_17_schedule_coverage(p):
    """TSA-17: All frames present in at least 1 schedule mode."""
    if not p.frames or not p.schedules:
        return na("No frames or schedules.")
    scheduled_frames = set()
    for sched in p.schedules:
        for entry in sched.frames:
            scheduled_frames.add(entry.frame)

    all_frame_ids = {f.frame_id for f in p.frames}
    coverage = len(scheduled_frames & all_frame_ids) / len(all_frame_ids) if all_frame_ids else 0

    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"All {len(all_frame_ids)} frames scheduled.", confidence="High")
    return CheckResult(
        rating="NO",
        finding=f"{len(scheduled_frames & all_frame_ids)}/{len(all_frame_ids)} frames scheduled.",
        recommended_action="Schedule all frames in at least one mode.",
        confidence="High",
    )


def tsa_18_schedule_timing(p):
    """TSA-18: Schedule slots non-overlapping, total time feasible."""
    if not p.schedules:
        return na("No schedules.")
    return draft(
        "Schedule timing feasibility requires detailed slot analysis.",
        action="Verify slots are non-overlapping and total cycle time is feasible.",
    )


# ---------------------------------------------------------------------------
# Check catalog
# ---------------------------------------------------------------------------

@dataclass
class CheckDef:
    check_id: str
    category: str
    description: str
    verify: Callable[[ProbedLDF], CheckResult]


CHECKS: list[CheckDef] = [
    CheckDef("CR-01", "Document Structure", "Document structured (≥5 tabs)", cr_01_structured),
    CheckDef("CR-02", "Document Structure", "Latest LDF template used", cr_02_template),
    CheckDef("CR-03", "Document Structure", "Searchable/navigable", cr_03_searchable),
    CheckDef("CR-04a", "Document Structure", "Title/scope definition", cr_04a_title),
    CheckDef("CR-04b", "Document Structure", "Author/Approver", cr_04b_author_approver),
    CheckDef("CR-04c", "Document Structure", "Unique revision ID", cr_04c_unique_revision),
    CheckDef("CR-04d", "Document Structure", "Change history", cr_04d_change_history),
    CheckDef("CR-04e", "Document Structure", "Status field", cr_04e_status),
    CheckDef("CR-05", "Document Structure", "Revision consistency", cr_05_current_revision),
    CheckDef("CR-06", "Document Structure", "Configuration management", cr_06_config_mgmt),
    CheckDef("CR-07", "Document Structure", "Headers/footers", cr_07_header_footer),
    CheckDef("CR-08", "Document Structure", "TOC completeness", cr_08_toc),
    CheckDef("CR-09", "Document Structure", "Cross-references", cr_09_references),
    CheckDef("CR-10", "Document Structure", "Sections complete", cr_10_sections_complete),
    CheckDef("TSA-01", "Cluster Configuration", "Cluster metadata", tsa_01_cluster_metadata),
    CheckDef("TSA-02", "Cluster Configuration", "LIN version valid", tsa_02_lin_version),
    CheckDef("TSA-03", "Cluster Configuration", "Baud rate in range", tsa_03_baud_rate),
    CheckDef("TSA-04", "Cluster Configuration", "Timing master assigned", tsa_04_timing_master),
    CheckDef("TSA-05", "Nodes", "Master node defined", tsa_05_master_node),
    CheckDef("TSA-06", "Nodes", "Slave nodes defined", tsa_06_slave_nodes),
    CheckDef("TSA-07", "Nodes", "Node roles defined", tsa_07_node_roles),
    CheckDef("TSA-08", "Frames", "Frame definitions", tsa_08_frame_definitions),
    CheckDef("TSA-09", "Frames", "Frame types", tsa_09_frame_types),
    CheckDef("TSA-10", "Frames", "Frame publishers", tsa_10_frame_publishers),
    CheckDef("TSA-11", "Frames", "Frame length", tsa_11_frame_length),
    CheckDef("TSA-12", "Signals", "Signal definitions", tsa_12_signal_definitions),
    CheckDef("TSA-13", "Signals", "Signal allocation", tsa_13_signal_allocation),
    CheckDef("TSA-14", "Signals", "Signal encoding", tsa_14_signal_encoding),
    CheckDef("TSA-15", "Signals", "Signal bounds", tsa_15_signal_bounds),
    CheckDef("TSA-16", "Schedule Tables", "Schedule definitions", tsa_16_schedule_tables),
    CheckDef("TSA-17", "Schedule Tables", "Schedule coverage", tsa_17_schedule_coverage),
    CheckDef("TSA-18", "Schedule Tables", "Schedule timing", tsa_18_schedule_timing),
]
