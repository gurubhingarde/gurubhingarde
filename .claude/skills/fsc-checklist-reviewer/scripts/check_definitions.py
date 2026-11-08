"""FSC Confirmation Measures checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from fsc_probe import ProbedFSC


@dataclass
class CheckResult:
    rating: str = ""
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding: str, page_section: str = "", action: str = "(Reviewer to verify and assess)") -> CheckResult:
    return CheckResult(rating="", finding="(Auto-suggest, requires reviewer judgment) " + finding, page_section=page_section, recommended_action=action, confidence="Low")


def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, confidence="High")


# ---------------------------------------------------------------------------
# Confirmation Review (generic doc-quality, ISO 26262-8 §10) — same 14 as HARA
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedFSC) -> CheckResult:
    if len(p.sheet_names) >= 5:
        return CheckResult(rating="FC", finding=f"Document is structured into {len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Add structured sections.", confidence="Medium")


def cr_02_template(p): return draft("Template version cannot be detected from the xlsx content.", action="Confirm latest FSC template was used.")


def cr_03_searchable(p):
    if p.has_table_of_contents:
        return CheckResult(rating="FC", finding="Title/Contents tab present.", confidence="Medium")
    return CheckResult(rating="PC", finding="No TOC tab detected.", recommended_action="Add a TOC.", confidence="Medium")


def cr_04a_title(p):
    if p.title:
        return draft(f"Title is: '{p.title}'. Reviewer to confirm scope coverage.", page_section="Title page")
    return CheckResult(rating="NO", finding="No title detected.", recommended_action="Add a clear document title.", confidence="High")


def cr_04b_author_approver(p):
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    missing = ([] if p.author else ["Author"]) + ([] if p.approver else ["Approver"])
    return CheckResult(rating="NO", finding=f"Missing on Title page: {', '.join(missing)}.", recommended_action=f"Populate {', '.join(missing)} fields.", confidence="High")


def cr_04c_unique_revision(p):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="Revision not populated.", recommended_action="Populate Revision field.", confidence="High")


def cr_04d_change_history(p):
    if p.revision_history_rows >= 1:
        return CheckResult(rating="FC", finding=f"Revision history has {p.revision_history_rows} rows.", confidence="High")
    return CheckResult(rating="NO", finding="No revision history rows.", recommended_action="Add a populated revision history.", confidence="High")


def cr_04e_status(p):
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="No status field.", recommended_action="Add a Status field (Draft/Released/etc.).", confidence="High")


def cr_05_current_revision(p):
    if p.revision:
        return CheckResult(rating="FC", finding=f"Current revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="Current revision not identifiable.", recommended_action="Populate Revision field.", confidence="High")


def cr_06_config_mgmt(p): return draft("Configuration management is organizational.", action="Confirm document is in CM system.")
def cr_07_header_footer(p): return draft("Header/footer not reliably accessible.", action="Open in Excel; verify header/footer.")


def cr_08_toc(p):
    if p.has_table_of_contents:
        return CheckResult(rating="FC", finding="TOC tab present.", confidence="Medium")
    return CheckResult(rating="PC", finding="No TOC.", recommended_action="Add a TOC.", confidence="Medium")


def cr_09_references(p):
    if p.linked_hara:
        return CheckResult(rating="FC", finding=f"Linked HARA referenced: {p.linked_hara}.", confidence="Medium")
    return CheckResult(rating="PC", finding="No linked HARA reference.", recommended_action="Reference the source HARA in the FSC.", confidence="Medium")


def cr_10_sections_complete(p):
    fsr_complete = len([f for f in p.fsrs if f.fsr_text]) / max(1, len(p.fsrs))
    alloc_complete = len([a for a in p.allocations if a.resulting_asil]) / max(1, len(p.allocations))
    overall = (fsr_complete + alloc_complete) / 2
    if overall >= 0.95:
        return CheckResult(rating="FC", finding=f"FSRs {fsr_complete:.0%} complete; allocations {alloc_complete:.0%}.", confidence="High")
    return CheckResult(rating="PC", finding=f"Some sections incomplete: FSRs {fsr_complete:.0%}; allocations {alloc_complete:.0%}.", recommended_action="Complete remaining cells.", confidence="High")


# ---------------------------------------------------------------------------
# Functional Safety Assessment — FSC substantive (ISO 26262-3 §8)
# ---------------------------------------------------------------------------

def fsa_01_hara_avail(p):
    if p.safety_goals:
        return CheckResult(rating="FC", finding=f"HARA prerequisite met: {len(p.safety_goals)} safety goals imported.", page_section=f"Sheet '{p.likely_sg_sheet}'", confidence="High")
    return CheckResult(rating="NO", finding="No safety goals found in FSC; HARA prerequisite not met.", recommended_action="Import safety goals from a completed HARA.", confidence="High")


def fsa_02_item_def(p): return draft("Item definition lives in a separate document.", action="Confirm Item Definition is referenced and complete.")


def fsa_03_arch_assumed(p):
    if p.nodes:
        return CheckResult(rating="FC", finding=f"Preliminary architecture present: {len(p.nodes)} block-diagram nodes documented.", page_section=f"Sheet '{p.likely_block_sheet}'", confidence="High")
    return CheckResult(rating="NO", finding="No preliminary architecture / block diagram found.", recommended_action="Document the preliminary block diagram with all ASIL-relevant nodes.", confidence="High")


def fsa_04_fsr_per_sg(p):
    if not p.safety_goals:
        return na("No safety goals.")
    sg_with_fsrs = {f.sg_id for f in p.fsrs}
    sg_ids = {sg.sg_id for sg in p.safety_goals}
    coverage = len(sg_with_fsrs & sg_ids) / max(1, len(sg_ids))
    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"All {len(sg_ids)} safety goals have at least one derived FSR ({len(p.fsrs)} FSRs total).", page_section=f"Sheet '{p.likely_fsr_sheet}'", confidence="High")
    missing = sg_ids - sg_with_fsrs
    return CheckResult(rating="PC", finding=f"{len(sg_with_fsrs)}/{len(sg_ids)} safety goals have FSRs derived. Missing: {sorted(missing)[:5]}", recommended_action="Derive at least one FSR per safety goal.", confidence="High")


def fsa_05_asil_inherited(p):
    if not p.fsrs:
        return na("No FSRs.")
    with_asil = [f for f in p.fsrs if f.asil_inherited]
    rate = len(with_asil) / len(p.fsrs)
    if rate >= 0.99:
        return CheckResult(rating="FC", finding=f"All {len(p.fsrs)} FSRs carry an inherited ASIL.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_asil)}/{len(p.fsrs)} FSRs have inherited ASIL.", recommended_action="Inherit ASIL from parent SG for all FSRs.", confidence="High")


def fsa_06_safe_states(p):
    if not p.safety_goals:
        return na("No safety goals.")
    with_safe = [sg for sg in p.safety_goals if sg.safe_state]
    rate = len(with_safe) / len(p.safety_goals)
    if rate >= 0.99:
        return CheckResult(rating="FC", finding=f"All {len(p.safety_goals)} safety goals specify safe state(s).", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_safe)}/{len(p.safety_goals)} safety goals specify safe states.", recommended_action="Specify safe state for every SG.", confidence="High")


def fsa_07_ftti(p):
    if not p.fsrs:
        return na("No FSRs.")
    with_ftti = [f for f in p.fsrs if f.ftti_ms not in (None, "", "<TBD>")]
    rate = len(with_ftti) / len(p.fsrs)
    if rate >= 0.99:
        return CheckResult(rating="FC", finding=f"All {len(p.fsrs)} FSRs have FTTI specified.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_ftti)}/{len(p.fsrs)} FSRs have FTTI specified.", recommended_action="Specify FTTI for every FSR (typically inherited from SG).", confidence="High")


def fsa_08_warning_degradation(p):
    return draft("Warning and degradation strategies are typically captured in the safe-state description.", action="Verify each safe-state entry includes warning indicator + degraded-mode behaviour.")


def fsa_09_alloc_to_arch(p):
    if not p.fsrs:
        return na("No FSRs.")
    with_node = [f for f in p.fsrs if f.node_id]
    rate = len(with_node) / len(p.fsrs)
    if rate >= 0.99:
        return CheckResult(rating="FC", finding=f"All {len(p.fsrs)} FSRs allocated to a block-diagram node.", page_section=f"Sheet '{p.likely_fsr_sheet}'", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_node)}/{len(p.fsrs)} FSRs have node allocation.", recommended_action="Allocate every FSR to an architectural element.", confidence="High")


def fsa_10_decomp_independence(p):
    decomp_allocs = [a for a in p.allocations if a.decomposition and "None" not in a.decomposition]
    if not decomp_allocs:
        return CheckResult(rating="FC", finding="No ASIL decomposition applied; independence requirements vacuously met.", confidence="High")
    with_evidence = [a for a in decomp_allocs if a.independence_evidence and "<TBD>" not in a.independence_evidence and "TBD" not in a.independence_evidence.upper()]
    if not with_evidence:
        return CheckResult(rating="NO", finding=f"{len(decomp_allocs)} decomposition allocations present, but Independence Evidence is <TBD> on all of them.", recommended_action="Document independence evidence for each decomposed pair (cite analysis or design argument). Per ISO 26262-9 §6.", confidence="High")
    rate = len(with_evidence) / len(decomp_allocs)
    if rate >= 0.99:
        return CheckResult(rating="FC", finding=f"All {len(decomp_allocs)} decomposition allocations have independence evidence cited.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_evidence)}/{len(decomp_allocs)} decomposition allocations have independence evidence.", recommended_action="Document evidence for the remaining decomposed pairs.", confidence="High")


def fsa_11_fsc_vs_sg(p):
    fta_top_events = {e.sg_id for e in p.fta_entries if e.level == 0}
    sg_ids = {sg.sg_id for sg in p.safety_goals}
    if not sg_ids:
        return na("No safety goals.")
    coverage = len(fta_top_events & sg_ids) / len(sg_ids)
    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"FSC has a top-level fault tree event for every {len(sg_ids)} safety goal(s); compliance demonstrated structurally.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(fta_top_events & sg_ids)}/{len(sg_ids)} safety goals have a corresponding FTA top event.", recommended_action="Add a fault tree top event for each safety goal.", confidence="High")


def fsa_12_arch_consistency(p):
    if p.nodes and p.fsrs:
        node_ids_in_fsrs = {f.node_id for f in p.fsrs if f.node_id}
        node_ids_in_arch = {n.id for n in p.nodes}
        unmapped = node_ids_in_fsrs - node_ids_in_arch
        if not unmapped:
            return CheckResult(rating="FC", finding=f"All FSR-referenced nodes ({len(node_ids_in_fsrs)}) appear in the block diagram.", confidence="High")
        return CheckResult(rating="PC", finding=f"{len(unmapped)} node(s) referenced by FSRs missing from block diagram: {sorted(unmapped)[:5]}", recommended_action="Reconcile FSR node references with the block diagram.", confidence="High")
    return draft("Reviewer to confirm consistency with preliminary architecture.")


def fsa_13_external_interfaces(p):
    sensor_count = sum(1 for n in p.nodes if n.type in ("sensor", "comm_in", "power_in"))
    actuator_count = sum(1 for n in p.nodes if n.type in ("actuator", "driver", "comm_out"))
    if sensor_count and actuator_count:
        return CheckResult(rating="FC", finding=f"External interfaces present: {sensor_count} input nodes, {actuator_count} output nodes.", confidence="Medium")
    return draft(f"Input nodes={sensor_count}, output nodes={actuator_count}. Reviewer to confirm completeness.")


def fsa_14_operating_modes(p):
    return draft("Operating modes (start-up / normal / shutdown / fault) are typically described in the FSC narrative.", action="Confirm operating modes are described and FSRs cover each.")


def fsa_15_verification_planned(p):
    if p.likely_verification_sheet and p.likely_verification_sheet in p.sheet_names:
        return CheckResult(rating="FC", finding=f"Verification matrix tab present: '{p.likely_verification_sheet}'.", confidence="Medium")
    return CheckResult(rating="PC", finding="No verification tab/section detected.", recommended_action="Add a verification matrix planning method per FSR.", confidence="Medium")


def fsa_16_handoff(p):
    if p.likely_tsc_handoff_sheet and p.likely_tsc_handoff_sheet in p.sheet_names:
        return CheckResult(rating="FC", finding=f"TSC hand-off tab present: '{p.likely_tsc_handoff_sheet}'.", confidence="High")
    return CheckResult(rating="PC", finding="No TSC hand-off tab detected.", recommended_action="Add a TSC hand-off summary with placeholder TSR rows.", confidence="Medium")


# ---------------------------------------------------------------------------
# Verification Assessment — generic + FSC-specific
# ---------------------------------------------------------------------------

def _va_external(label):
    return draft(f"{label} is governed by an external Verification Plan / Specification / Report.", action="Verify against the project's verification documents.")


def va_24_plan(p): return _va_external("Verification Plan compliance with FSC")
def va_25_validation(p): return na("Belongs to TSC validation review.")
def va_26(p): return _va_external("Plan addresses content/methods/criteria/env/tools/anomalies/regression")
def va_26a(p): return _va_external("Plan content")
def va_26b(p): return _va_external("Methods")
def va_26c(p): return _va_external("Pass/fail")
def va_26d(p): return _va_external("Environment")
def va_26e(p): return _va_external("Tools")
def va_26f(p): return _va_external("Anomalies")
def va_26g(p): return _va_external("Regression")
def va_27(p): return _va_external("Planning considerations")
def va_27a(p): return _va_external("Method adequacy")
def va_27b(p): return _va_external("Complexity")
def va_27c(p): return _va_external("Prior experience")
def va_27d(p): return _va_external("Technology maturity")
def va_28(p): return _va_external("Verification methods specified")
def va_28a(p): return _va_external("Review/analysis checklists (e.g., this skill's output)")
def va_28b(p): return _va_external("Simulation scenarios")
def va_28c(p): return _va_external("Test cases")
def va_29(p): return _va_external("Test case content")
def va_29a(p): return _va_external("Unique ID")
def va_29b(p): return _va_external("Version reference")
def va_29c(p): return _va_external("Preconditions")
def va_29d(p): return _va_external("Environment")
def va_29e(p): return _va_external("Inputs")
def va_29f(p): return _va_external("Expected behavior")
def va_30(p): return _va_external("Test grouping")
def va_31(p): return _va_external("Verification executed per plan")
def va_32(p): return _va_external("Verification Report")

# FSC-specific verification (analogous to HARA 33a-e)
def va_33a_completeness_sgs(p):
    fta_top_events = {e.sg_id for e in p.fta_entries if e.level == 0}
    sg_ids = {sg.sg_id for sg in p.safety_goals}
    if not sg_ids:
        return na("No safety goals.")
    if fta_top_events == sg_ids or fta_top_events >= sg_ids:
        return CheckResult(rating="FC", finding=f"FSC covers all {len(sg_ids)} safety goals with FTA entries.", confidence="High")
    return CheckResult(rating="PC", finding=f"FSC covers {len(fta_top_events & sg_ids)}/{len(sg_ids)} safety goals.", recommended_action="Add FTA / FSRs for missing safety goals.", confidence="High")


def va_33b_compliance_item(p): return draft("Compliance with item definition cannot be verified from the FSC alone.")


def va_33c_consistency_arch(p):
    return fsa_12_arch_consistency(p)


def va_33d_fsr_coverage(p):
    if not p.fsrs:
        return CheckResult(rating="NO", finding="No FSRs derived.", confidence="High")
    sg_with_fsrs = {f.sg_id for f in p.fsrs}
    sg_ids = {sg.sg_id for sg in p.safety_goals}
    coverage = len(sg_with_fsrs & sg_ids) / max(1, len(sg_ids))
    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"FSR coverage of safety goals: {coverage:.0%} ({len(sg_with_fsrs)}/{len(sg_ids)}).", confidence="High")
    return CheckResult(rating="PC", finding=f"FSR coverage: {coverage:.0%}.", recommended_action="Derive FSRs for uncovered safety goals.", confidence="High")


def va_33e_asil_consistency(p):
    if not p.fsrs or not p.safety_goals:
        return na("No FSRs or safety goals.")
    sg_asil = {sg.sg_id: sg.asil for sg in p.safety_goals}
    inconsistent = []
    for f in p.fsrs:
        if f.sg_id in sg_asil:
            sg_a = sg_asil[f.sg_id].split("(")[0].strip()
            f_a = f.asil_inherited.split("(")[0].strip()
            if sg_a and f_a and sg_a != f_a:
                inconsistent.append((f.fsr_id, sg_a, f_a))
    if not inconsistent:
        return CheckResult(rating="FC", finding=f"All {len(p.fsrs)} FSRs carry ASIL consistent with their parent safety goal.", confidence="High")
    return CheckResult(rating="NO", finding=f"{len(inconsistent)} FSRs have ASIL inconsistent with parent SG.", recommended_action="Re-inherit ASIL from parent SG for inconsistent FSRs.", confidence="High")


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str
    verify: Callable[[ProbedFSC], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review
    CheckDef("1",  "CR", "Document Quality", "Is the document structured in a clear manner that supports maintainability and understandability?", "Shall", cr_01_structured),
    CheckDef("2",  "CR", "Document Quality", "On the date the document was first created, was the latest template available used?", "Should", cr_02_template),
    CheckDef("3",  "CR", "Document Quality", "Does the document structure facilitate the search for relevant information?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does the title cover the scope of the content?", "Shall", cr_04a_title),
    CheckDef("4b", "CR", "Document Quality", "Are the author and approver(s) listed?", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Document Quality", "Is there a unique identification for each different revision?", "Shall", cr_04c_unique_revision),
    CheckDef("4d", "CR", "Document Quality", "Is there a change history available?", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Quality", "Is the status of the work product provided?", "Shall", cr_04e_status),
    CheckDef("5",  "CR", "Document Quality", "Is the current applicable revision clearly identifiable?", "Shall", cr_05_current_revision),
    CheckDef("6",  "CR", "Document Quality", "Is the document under configuration and change management?", "Shall", cr_06_config_mgmt),
    CheckDef("7",  "CR", "Document Quality", "Are the header and footer updated?", "Should", cr_07_header_footer),
    CheckDef("8",  "CR", "Document Quality", "Does this document contain a correct table of content?", "Shall", cr_08_toc),
    CheckDef("9",  "CR", "Document Quality", "Does the Reference Table list all references?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "Have all sections of the Work Product been completed?", "Should", cr_10_sections_complete),

    # FSC Functional Safety Assessment (ISO 26262-3 §8)
    CheckDef("1",  "FSA", "Prerequisites", "Is the HARA available with safety goals derived?", "Shall", fsa_01_hara_avail),
    CheckDef("2",  "FSA", "Prerequisites", "Is the Item Definition available and consistent with the HARA?", "Shall", fsa_02_item_def),
    CheckDef("3",  "FSA", "Prerequisites", "Is the preliminary architectural design / block diagram present?", "Shall", fsa_03_arch_assumed),
    CheckDef("4",  "FSA", "FSR Derivation", "Has at least one Functional Safety Requirement been derived from each safety goal?", "Shall", fsa_04_fsr_per_sg),
    CheckDef("5",  "FSA", "FSR Derivation", "Has each FSR been allocated an ASIL inherited from its safety goal?", "Shall", fsa_05_asil_inherited),
    CheckDef("6",  "FSA", "Safe States", "Have safe state(s) been specified for every safety goal?", "Shall", fsa_06_safe_states),
    CheckDef("7",  "FSA", "Timing", "Has the FTTI been specified for every FSR?", "Shall", fsa_07_ftti),
    CheckDef("8",  "FSA", "Warning & Degradation", "Have warning and degradation strategies been defined where applicable?", "Should", fsa_08_warning_degradation),
    CheckDef("9",  "FSA", "Architecture Allocation", "Has each FSR been allocated to architectural elements (preliminary)?", "Shall", fsa_09_alloc_to_arch),
    CheckDef("10", "FSA", "ASIL Decomposition", "If ASIL decomposition is applied, are independence requirements per ISO 26262-9 documented?", "Shall", fsa_10_decomp_independence),
    CheckDef("11", "FSA", "FSC Verification", "Has the FSC been verified for compliance with the safety goals?", "Shall", fsa_11_fsc_vs_sg),
    CheckDef("12", "FSA", "FSC Verification", "Has the FSC been verified for consistency with the preliminary architectural design?", "Shall", fsa_12_arch_consistency),
    CheckDef("13", "FSA", "External Interfaces", "Are external interface properties considered (sensors, actuators, communication)?", "Shall", fsa_13_external_interfaces),
    CheckDef("14", "FSA", "Operating Modes", "Are operating modes (start-up, normal, shutdown, fault) considered?", "Should", fsa_14_operating_modes),
    CheckDef("15", "FSA", "Verification Planning", "Have means of verification been planned for each FSR?", "Shall", fsa_15_verification_planned),
    CheckDef("16", "FSA", "TSC Hand-off", "Has a TSC hand-off been prepared with FSR-to-TSR mapping placeholders?", "Should", fsa_16_handoff),

    # Verification Assessment
    CheckDef("24", "VA", "Verification Planning", "Does the Verification Plan ensure compliance with the FSC?", "Shall", va_24_plan),
    CheckDef("25", "VA", "Verification Planning", "If applicable, was Safety Validation refined based on TSRs?", "Should", va_25_validation),
    CheckDef("26", "VA", "Verification Planning", "Does the Verification Plan address content, methods, criteria, env, tools, anomalies, regression?", "Shall", va_26),
    CheckDef("26a","VA", "Verification Planning", "Plan content?", "Shall", va_26a),
    CheckDef("26b","VA", "Verification Planning", "Methods consistent with Safety Plan?", "Shall", va_26b),
    CheckDef("26c","VA", "Verification Planning", "Pass/fail criteria?", "Shall", va_26c),
    CheckDef("26d","VA", "Verification Planning", "Verification environment?", "Shall", va_26d),
    CheckDef("26e","VA", "Verification Planning", "Tools used?", "Shall", va_26e),
    CheckDef("26f","VA", "Verification Planning", "Actions on anomalies?", "Shall", va_26f),
    CheckDef("26g","VA", "Verification Planning", "Regression strategy?", "Shall", va_26g),
    CheckDef("27", "VA", "Verification Planning", "Planning considers method adequacy / complexity / prior experience / technology maturity?", "Should", va_27),
    CheckDef("27a","VA", "Verification Planning", "Method adequacy?", "Should", va_27a),
    CheckDef("27b","VA", "Verification Planning", "Complexity?", "Should", va_27b),
    CheckDef("27c","VA", "Verification Planning", "Prior experience?", "Should", va_27c),
    CheckDef("27d","VA", "Verification Planning", "Technology maturity?", "Should", va_27d),
    CheckDef("28", "VA", "Verification Specification", "Are review checklists, simulation, or test cases specified?", "Shall", va_28),
    CheckDef("28a","VA", "Verification Specification", "Review of analysis checklists?", "Shall", va_28a),
    CheckDef("28b","VA", "Verification Specification", "Simulation scenarios?", "Shall", va_28b),
    CheckDef("28c","VA", "Verification Specification", "Test cases?", "Shall", va_28c),
    CheckDef("29", "VA", "Verification Specification", "Test case content includes ID, version, preconditions, env, inputs, expected behavior?", "Shall", va_29),
    CheckDef("29a","VA", "Verification Specification", "Unique identification?", "Shall", va_29a),
    CheckDef("29b","VA", "Verification Specification", "Reference to work product version?", "Shall", va_29b),
    CheckDef("29c","VA", "Verification Specification", "Preconditions and configurations?", "Shall", va_29c),
    CheckDef("29d","VA", "Verification Specification", "Environmental conditions?", "Shall", va_29d),
    CheckDef("29e","VA", "Verification Specification", "Input data and timing?", "Shall", va_29e),
    CheckDef("29f","VA", "Verification Specification", "Expected behavior with tolerances?", "Shall", va_29f),
    CheckDef("30", "VA", "Verification Specification", "Test cases grouped with environment, dependencies, resources?", "Shall", va_30),
    CheckDef("31", "VA", "Verification Execution", "Was verification executed per plan?", "Shall", va_31),
    CheckDef("32", "VA", "Verification Execution", "Does the Verification Report include required content?", "Shall", va_32),
    CheckDef("33a","VA", "FSC-Specific Verification", "Completeness with regard to safety goals (every SG addressed by FSC)?", "Shall", va_33a_completeness_sgs),
    CheckDef("33b","VA", "FSC-Specific Verification", "Compliance with item definition?", "Shall", va_33b_compliance_item),
    CheckDef("33c","VA", "FSC-Specific Verification", "Consistency with preliminary architectural design?", "Shall", va_33c_consistency_arch),
    CheckDef("33d","VA", "FSC-Specific Verification", "Completeness of FSR coverage of safety goals?", "Shall", va_33d_fsr_coverage),
    CheckDef("33e","VA", "FSC-Specific Verification", "Consistency of allocated ASILs with parent safety goals?", "Shall", va_33e_asil_consistency),
]
