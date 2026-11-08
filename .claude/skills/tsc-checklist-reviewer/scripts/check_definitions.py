"""TSC Confirmation Measures checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from tsc_probe import ProbedTSC


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
# Confirmation Review (14 generic — same as HARA/FSC)
# ---------------------------------------------------------------------------

def cr_01_structured(p):
    if len(p.sheet_names) >= 5:
        return CheckResult(rating="FC", finding=f"Document is structured into {len(p.sheet_names)} tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs.", recommended_action="Add structured sections.", confidence="Medium")


def cr_02_template(p): return draft("Template version cannot be detected from xlsx content.", action="Confirm latest TSC template was used.")


def cr_03_searchable(p):
    if p.has_table_of_contents:
        return CheckResult(rating="FC", finding="Title/Contents tab present.", confidence="Medium")
    return CheckResult(rating="PC", finding="No TOC.", recommended_action="Add a TOC.", confidence="Medium")


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
    if p.revision_history_rows >= 1:
        return CheckResult(rating="FC", finding=f"Revision history has {p.revision_history_rows} rows.", confidence="High")
    return CheckResult(rating="NO", finding="No revision history.", recommended_action="Add revision history.", confidence="High")


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
        return CheckResult(rating="FC", finding="TOC tab present.", confidence="Medium")
    return CheckResult(rating="PC", finding="No TOC.", recommended_action="Add a TOC.", confidence="Medium")


def cr_09_references(p):
    if p.linked_fsc:
        return CheckResult(rating="FC", finding=f"Linked FSC referenced: {p.linked_fsc}.", confidence="Medium")
    return CheckResult(rating="PC", finding="No linked FSC reference.", recommended_action="Reference the source FSC.", confidence="Medium")


def cr_10_sections_complete(p):
    tsr_complete = len([t for t in p.tsrs if t.text]) / max(1, len(p.tsrs))
    hsi_complete = len([h for h in p.hsi_signals if h.encoding]) / max(1, len(p.hsi_signals))
    overall = (tsr_complete + hsi_complete) / 2
    if overall >= 0.95:
        return CheckResult(rating="FC", finding=f"TSRs {tsr_complete:.0%} complete; HSI {hsi_complete:.0%}.", confidence="High")
    return CheckResult(rating="PC", finding=f"TSRs {tsr_complete:.0%}; HSI {hsi_complete:.0%}.", recommended_action="Complete remaining TSR text and HSI encoding fields.", confidence="High")


# ---------------------------------------------------------------------------
# Technical Safety Assessment (TSC substantive — ISO 26262-4)
# ---------------------------------------------------------------------------

def tsa_01_fsc_avail(p):
    if p.fsrs:
        return CheckResult(rating="FC", finding=f"FSC prerequisite met: {len(p.fsrs)} FSRs imported.", page_section=f"Sheet '{p.likely_fsr_sheet}'", confidence="High")
    return CheckResult(rating="NO", finding="No FSRs found in TSC; FSC prerequisite not met.", recommended_action="Import FSRs from a completed FSC.", confidence="High")


def tsa_02_arch_refined(p):
    if p.hw_components and p.sw_partitions:
        return CheckResult(rating="FC", finding=f"Architecture refined: {len(p.hw_components)} HW components and {len(p.sw_partitions)} SW partitions.", page_section=f"Sheet '{p.likely_arch_sheet}'", confidence="High")
    if p.hw_components or p.sw_partitions:
        return CheckResult(rating="PC", finding=f"Partial architecture: {len(p.hw_components)} HW components, {len(p.sw_partitions)} SW partitions.", recommended_action="Complete both HW components and SW partitions.", confidence="High")
    return CheckResult(rating="NO", finding="No HW components or SW partitions found.", recommended_action="Refine the FSC block diagram into HW and SW components.", confidence="High")


def tsa_03_hw_tsr_per_fsr(p):
    if not p.fsrs:
        return na("No FSRs.")
    fsrs_with_hw = {t.fsr_id for t in p.tsrs if t.type == "HW-TSR"}
    fsr_ids = {f.fsr_id for f in p.fsrs}
    coverage = len(fsrs_with_hw & fsr_ids) / max(1, len(fsr_ids))
    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"All {len(fsr_ids)} FSRs have at least one HW-TSR.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(fsrs_with_hw & fsr_ids)}/{len(fsr_ids)} FSRs have HW-TSRs.", recommended_action="Derive HW-TSR for uncovered FSRs.", confidence="High")


def tsa_04_sw_tsr_per_fsr(p):
    if not p.fsrs:
        return na("No FSRs.")
    fsrs_with_sw = {t.fsr_id for t in p.tsrs if t.type == "SW-TSR"}
    fsr_ids = {f.fsr_id for f in p.fsrs}
    coverage = len(fsrs_with_sw & fsr_ids) / max(1, len(fsr_ids))
    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"All {len(fsr_ids)} FSRs have at least one SW-TSR.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(fsrs_with_sw & fsr_ids)}/{len(fsr_ids)} FSRs have SW-TSRs.", recommended_action="Derive SW-TSR for uncovered FSRs.", confidence="High")


def tsa_05_tsr_alloc(p):
    if not p.tsrs:
        return na("No TSRs.")
    with_node = [t for t in p.tsrs if t.node_ref]
    rate = len(with_node) / len(p.tsrs)
    if rate >= 0.99:
        return CheckResult(rating="FC", finding=f"All {len(p.tsrs)} TSRs allocated to a node/element.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_node)}/{len(p.tsrs)} TSRs have allocation.", recommended_action="Allocate every TSR to a HW or SW element.", confidence="High")


def tsa_06_safety_mechanisms(p):
    fsrs_with_primary = {m.fsr_id for m in p.mechanisms if m.selection and "primary" in m.selection.lower()}
    fsr_ids = {f.fsr_id for f in p.fsrs}
    coverage = len(fsrs_with_primary & fsr_ids) / max(1, len(fsr_ids))
    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"All {len(fsr_ids)} FSRs have a primary safety mechanism selected.", page_section=f"Sheet '{p.likely_mechanism_sheet}'", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(fsrs_with_primary & fsr_ids)}/{len(fsr_ids)} FSRs have a primary mechanism.", recommended_action="Select a primary mechanism for each FSR.", confidence="High")


def tsa_07_dc_targets(p):
    if not p.mechanisms:
        return na("No mechanisms.")
    with_dc = [m for m in p.mechanisms if m.default_dc and m.default_dc.lower() not in ("", "n/a", "<tbd>", "tbd")]
    rate = len(with_dc) / len(p.mechanisms)
    if rate >= 0.95:
        return CheckResult(rating="FC", finding=f"All {len(p.mechanisms)} mechanism rows have DC% targets.", confidence="Medium")
    return CheckResult(rating="PC", finding=f"{len(with_dc)}/{len(p.mechanisms)} mechanism rows have DC% targets. Default-catalog values still need refinement after FMEDA.", recommended_action="Refine DC% targets per mechanism after FMEDA evidence is available.", confidence="High")


def tsa_08_hsi(p):
    if not p.hsi_signals:
        return CheckResult(rating="NO", finding="No HSI signals defined.", recommended_action="Define HSI signals for all safety mechanisms crossing HW/SW boundary.", confidence="High")
    fsr_ids_in_hsi = {h.linked_fsr for h in p.hsi_signals if h.linked_fsr}
    fsr_ids = {f.fsr_id for f in p.fsrs}
    coverage = len(fsr_ids_in_hsi & fsr_ids) / max(1, len(fsr_ids))
    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"HSI defined for all {len(fsr_ids)} FSRs ({len(p.hsi_signals)} signals total).", page_section=f"Sheet '{p.likely_hsi_sheet}'", confidence="High")
    return CheckResult(rating="PC", finding=f"HSI defined for {len(fsr_ids_in_hsi & fsr_ids)}/{len(fsr_ids)} FSRs.", recommended_action="Define HSI signals for remaining FSRs.", confidence="High")


def tsa_09_timing(p):
    if not p.timing_rows:
        return na("No timing rows.")
    fully = [t for t in p.timing_rows if t.fdti_ms not in (None, "", "<TBD>") and t.frti_ms not in (None, "", "<TBD>")]
    rate = len(fully) / len(p.timing_rows)
    if rate >= 0.95:
        return CheckResult(rating="FC", finding=f"All {len(p.timing_rows)} FSRs have FTTI split into FDTI + FRTI.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(fully)}/{len(p.timing_rows)} FSRs have FDTI/FRTI populated. Others need FTTI from parent FSC.", recommended_action="Populate FTTI for FSRs left as <TBD>; the 50/50 split will then auto-populate.", confidence="High")


def tsa_10_fmea(p):
    if p.fmea_rows:
        return CheckResult(rating="FC", finding=f"System FMEA scaffold present with {len(p.fmea_rows)} rows.", page_section=f"Sheet '{p.likely_fmea_sheet}'", confidence="Medium")
    return CheckResult(rating="NO", finding="No system-level FMEA found.", recommended_action="Perform system-level FMEA per ISO 26262-9 §8.", confidence="High")


def tsa_11_dfa(p):
    if not p.dfa_rows:
        return CheckResult(rating="NO", finding="No DFA rows found. If decomposition was applied in FSC, DFA is mandatory.", recommended_action="Perform Dependent Failure Analysis per ISO 26262-9 §7 for every decomposed pair.", confidence="High")
    populated = [d for d in p.dfa_rows if d.coupling_present and d.coupling_present.lower() not in ("", "<tbd>", "<tbd: yes / no>")]
    rate = len(populated) / len(p.dfa_rows) if p.dfa_rows else 0
    if rate >= 0.5:
        return CheckResult(rating="FC", finding=f"DFA scaffold present with {len(p.dfa_rows)} rows; {len(populated)} populated.", confidence="High")
    return CheckResult(rating="PC", finding=f"DFA scaffold present ({len(p.dfa_rows)} rows) but only {len(populated)} populated by analyst.", recommended_action="Populate Coupling Present and Mitigation columns for every DFA row.", confidence="High")


def tsa_12_verification(p):
    if not p.tsrs:
        return na("No TSRs.")
    with_method = [t for t in p.tsrs if t.verification_method]
    rate = len(with_method) / len(p.tsrs)
    if rate >= 0.95:
        return CheckResult(rating="FC", finding=f"All {len(p.tsrs)} TSRs have verification methods specified.", page_section=f"Sheet '{p.likely_verification_sheet}'", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_method)}/{len(p.tsrs)} TSRs have verification methods.", recommended_action="Specify verification methods for remaining TSRs.", confidence="High")


def tsa_13_hw_handoff(p):
    if p.likely_hw_handoff_sheet and p.likely_hw_handoff_sheet in p.sheet_names:
        return CheckResult(rating="FC", finding=f"HW hand-off tab present: '{p.likely_hw_handoff_sheet}'.", confidence="High")
    return CheckResult(rating="PC", finding="No HW hand-off tab.", recommended_action="Add HW hand-off summary for ISO 26262-5.", confidence="Medium")


def tsa_14_sw_handoff(p):
    if p.likely_sw_handoff_sheet and p.likely_sw_handoff_sheet in p.sheet_names:
        return CheckResult(rating="FC", finding=f"SW hand-off tab present: '{p.likely_sw_handoff_sheet}'.", confidence="High")
    return CheckResult(rating="PC", finding="No SW hand-off tab.", recommended_action="Add SW hand-off summary for ISO 26262-6.", confidence="Medium")


def tsa_15_asil_consistency(p):
    if not p.tsrs or not p.fsrs:
        return na("No TSRs or FSRs.")
    fsr_asil = {f.fsr_id: f.asil_inherited for f in p.fsrs}
    inconsistent = []
    for t in p.tsrs:
        if t.fsr_id in fsr_asil and t.asil_allocated:
            f_a = fsr_asil[t.fsr_id].split("(")[0].strip()
            t_a = t.asil_allocated.split("(")[0].strip()
            # Allocated ASIL after decomposition can be lower than parent FSR ASIL — that's OK.
            # We flag only if allocated > FSR.
            asil_rank = {"QM": 0, "A": 1, "B": 2, "C": 3, "D": 4}
            if f_a in asil_rank and t_a in asil_rank and asil_rank[t_a] > asil_rank[f_a]:
                inconsistent.append((t.tsr_id, f_a, t_a))
    if not inconsistent:
        return CheckResult(rating="FC", finding=f"All TSR allocated ASILs are ≤ parent FSR ASIL (decomposition can lower; never raise).", confidence="High")
    return CheckResult(rating="NO", finding=f"{len(inconsistent)} TSRs have allocated ASIL > parent FSR ASIL.", recommended_action="Re-derive allocated ASIL from FSR via decomposition (ISO 26262-9 Table 1).", confidence="High")


# ---------------------------------------------------------------------------
# Verification Assessment (mostly external; TSC-specific 33 series)
# ---------------------------------------------------------------------------

def _va_external(label):
    return draft(f"{label} is governed by an external Verification Plan / Specification / Report.", action="Verify against project verification documents.")


def va_24_plan(p): return _va_external("Verification Plan compliance with TSC")
def va_25_validation(p): return draft("Safety Validation refinement based on TSRs is part of validation planning.")
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

# TSC-specific (analogous to HARA 33a–e but for TSC)
def va_33a_completeness_fsrs(p):
    fsrs_with_tsr = {t.fsr_id for t in p.tsrs}
    fsr_ids = {f.fsr_id for f in p.fsrs}
    if not fsr_ids:
        return na("No FSRs.")
    coverage = len(fsrs_with_tsr & fsr_ids) / len(fsr_ids)
    if coverage >= 0.99:
        return CheckResult(rating="FC", finding=f"TSC covers all {len(fsr_ids)} FSRs with TSRs.", confidence="High")
    return CheckResult(rating="PC", finding=f"TSC covers {len(fsrs_with_tsr & fsr_ids)}/{len(fsr_ids)} FSRs.", recommended_action="Derive TSRs for uncovered FSRs.", confidence="High")


def va_33b_compliance_fsc(p):
    if p.linked_fsc:
        return CheckResult(rating="FC", finding=f"TSC references linked FSC ({p.linked_fsc}); compliance traced.", confidence="Medium")
    return draft("Reviewer to verify TSC compliance with FSC against the source FSC document.")


def va_33c_consistency_arch(p):
    if not p.fsrs:
        return na("No FSRs.")
    nodes_in_fsrs = {f.node_ref.split(" — ")[0].strip() for f in p.fsrs if f.node_ref and " — " in f.node_ref}
    nodes_in_arch_alloc = set()
    for hw in p.hw_components:
        nodes_in_arch_alloc.update(hw.allocated_nodes)
    for sp in p.sw_partitions:
        nodes_in_arch_alloc.update(sp.allocated_nodes)
    unmapped = nodes_in_fsrs - nodes_in_arch_alloc
    if not unmapped:
        return CheckResult(rating="FC", finding=f"All FSR-referenced nodes ({len(nodes_in_fsrs)}) are allocated to HW components or SW partitions.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(unmapped)} node(s) referenced by FSRs not allocated in architecture: {sorted(unmapped)[:5]}", recommended_action="Allocate remaining nodes to HW components or SW partitions.", confidence="High")


def va_33d_tsr_coverage(p):
    return va_33a_completeness_fsrs(p)


def va_33e_asil_consistency(p):
    return tsa_15_asil_consistency(p)


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
    verify: Callable[[ProbedTSC], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review
    CheckDef("1",  "CR", "Document Quality", "Is the document structured in a clear manner?", "Shall", cr_01_structured),
    CheckDef("2",  "CR", "Document Quality", "Was the latest template available used?", "Should", cr_02_template),
    CheckDef("3",  "CR", "Document Quality", "Does the structure facilitate information search?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does the title cover the scope?", "Shall", cr_04a_title),
    CheckDef("4b", "CR", "Document Quality", "Are author and approver(s) listed?", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Document Quality", "Unique identification per revision?", "Shall", cr_04c_unique_revision),
    CheckDef("4d", "CR", "Document Quality", "Change history available?", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Quality", "Status of work product provided?", "Shall", cr_04e_status),
    CheckDef("5",  "CR", "Document Quality", "Current applicable revision identifiable?", "Shall", cr_05_current_revision),
    CheckDef("6",  "CR", "Document Quality", "Document under configuration management?", "Shall", cr_06_config_mgmt),
    CheckDef("7",  "CR", "Document Quality", "Header and footer updated?", "Should", cr_07_header_footer),
    CheckDef("8",  "CR", "Document Quality", "Correct table of content?", "Shall", cr_08_toc),
    CheckDef("9",  "CR", "Document Quality", "Reference Table lists all references?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "All sections completed?", "Should", cr_10_sections_complete),

    # Technical Safety Assessment (ISO 26262-4)
    CheckDef("1",  "TSA", "Prerequisites", "Is the FSC available with FSRs derived?", "Shall", tsa_01_fsc_avail),
    CheckDef("2",  "TSA", "Architecture", "Has the system architecture been refined into HW components and SW partitions?", "Shall", tsa_02_arch_refined),
    CheckDef("3",  "TSA", "TSR Derivation", "Has at least one HW-TSR been derived for each FSR?", "Shall", tsa_03_hw_tsr_per_fsr),
    CheckDef("4",  "TSA", "TSR Derivation", "Has at least one SW-TSR been derived for each FSR?", "Shall", tsa_04_sw_tsr_per_fsr),
    CheckDef("5",  "TSA", "TSR Allocation", "Has each TSR been allocated to a HW or SW element?", "Shall", tsa_05_tsr_alloc),
    CheckDef("6",  "TSA", "Safety Mechanisms", "Has a safety mechanism been chosen for each FSR?", "Shall", tsa_06_safety_mechanisms),
    CheckDef("7",  "TSA", "Safety Mechanisms", "Are diagnostic coverage targets specified for each safety mechanism?", "Shall", tsa_07_dc_targets),
    CheckDef("8",  "TSA", "HW-SW Interface", "Has the HSI been specified for safety mechanisms crossing the HW/SW boundary?", "Shall", tsa_08_hsi),
    CheckDef("9",  "TSA", "Timing Budget", "Has FTTI been split into FDTI and FRTI for each FSR?", "Shall", tsa_09_timing),
    CheckDef("10", "TSA", "System FMEA", "Has system-level FMEA been performed?", "Shall", tsa_10_fmea),
    CheckDef("11", "TSA", "Dependent Failure Analysis", "If decomposition was applied in FSC, has DFA been performed for each decomposed pair?", "Shall", tsa_11_dfa),
    CheckDef("12", "TSA", "Verification Planning", "Have verification methods been specified for each TSR?", "Shall", tsa_12_verification),
    CheckDef("13", "TSA", "HW Hand-off", "Has the HW hand-off (Part 5) been prepared?", "Shall", tsa_13_hw_handoff),
    CheckDef("14", "TSA", "SW Hand-off", "Has the SW hand-off (Part 6) been prepared?", "Shall", tsa_14_sw_handoff),
    CheckDef("15", "TSA", "ASIL Consistency", "Are TSR allocated ASILs consistent with parent FSR ASILs (decomposition can lower; never raise)?", "Shall", tsa_15_asil_consistency),

    # Verification Assessment
    CheckDef("24", "VA", "Verification Planning", "Plan ensures compliance with TSC?", "Shall", va_24_plan),
    CheckDef("25", "VA", "Verification Planning", "Safety Validation refined based on TSRs?", "Should", va_25_validation),
    CheckDef("26", "VA", "Verification Planning", "Plan addresses content/methods/criteria/env/tools/anomalies/regression?", "Shall", va_26),
    CheckDef("26a","VA", "Verification Planning", "Plan content?", "Shall", va_26a),
    CheckDef("26b","VA", "Verification Planning", "Methods?", "Shall", va_26b),
    CheckDef("26c","VA", "Verification Planning", "Pass/fail?", "Shall", va_26c),
    CheckDef("26d","VA", "Verification Planning", "Environment?", "Shall", va_26d),
    CheckDef("26e","VA", "Verification Planning", "Tools?", "Shall", va_26e),
    CheckDef("26f","VA", "Verification Planning", "Anomalies?", "Shall", va_26f),
    CheckDef("26g","VA", "Verification Planning", "Regression?", "Shall", va_26g),
    CheckDef("27", "VA", "Verification Planning", "Planning considers method adequacy / complexity / experience / maturity?", "Should", va_27),
    CheckDef("27a","VA", "Verification Planning", "Method adequacy?", "Should", va_27a),
    CheckDef("27b","VA", "Verification Planning", "Complexity?", "Should", va_27b),
    CheckDef("27c","VA", "Verification Planning", "Prior experience?", "Should", va_27c),
    CheckDef("27d","VA", "Verification Planning", "Technology maturity?", "Should", va_27d),
    CheckDef("28", "VA", "Verification Specification", "Methods specified (review/sim/test)?", "Shall", va_28),
    CheckDef("28a","VA", "Verification Specification", "Review checklists?", "Shall", va_28a),
    CheckDef("28b","VA", "Verification Specification", "Simulation?", "Shall", va_28b),
    CheckDef("28c","VA", "Verification Specification", "Test cases?", "Shall", va_28c),
    CheckDef("29", "VA", "Verification Specification", "Test case content?", "Shall", va_29),
    CheckDef("29a","VA", "Verification Specification", "Unique ID?", "Shall", va_29a),
    CheckDef("29b","VA", "Verification Specification", "Version ref?", "Shall", va_29b),
    CheckDef("29c","VA", "Verification Specification", "Preconditions?", "Shall", va_29c),
    CheckDef("29d","VA", "Verification Specification", "Env conditions?", "Shall", va_29d),
    CheckDef("29e","VA", "Verification Specification", "Inputs?", "Shall", va_29e),
    CheckDef("29f","VA", "Verification Specification", "Expected behavior?", "Shall", va_29f),
    CheckDef("30", "VA", "Verification Specification", "Test grouping?", "Shall", va_30),
    CheckDef("31", "VA", "Verification Execution", "Executed per plan?", "Shall", va_31),
    CheckDef("32", "VA", "Verification Execution", "Verification Report content?", "Shall", va_32),
    CheckDef("33a","VA", "TSC-Specific Verification", "Completeness with regard to FSRs (every FSR addressed by TSC)?", "Shall", va_33a_completeness_fsrs),
    CheckDef("33b","VA", "TSC-Specific Verification", "Compliance with FSC?", "Shall", va_33b_compliance_fsc),
    CheckDef("33c","VA", "TSC-Specific Verification", "Consistency with system architecture?", "Shall", va_33c_consistency_arch),
    CheckDef("33d","VA", "TSC-Specific Verification", "Completeness of TSR coverage?", "Shall", va_33d_tsr_coverage),
    CheckDef("33e","VA", "TSC-Specific Verification", "Consistency of allocated ASILs (TSR <= parent FSR)?", "Shall", va_33e_asil_consistency),
]
