"""
Canonical PFMEA checklist definitions per AIAG-VDA Handbook 2019.

- Confirmation Review (CR): 14 generic doc-quality checks
- PFMEA Assessment (PFMEAA): 14 AIAG-VDA specific checks
- Verification Assessment (VA): External verification + PFMEA completeness
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from pfmea_probe import ProbedPfmea


@dataclass
class CheckResult:
    rating: str = ""              # FC / LC / PC / NO / NA / "" (pending)
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""


def draft(finding: str, page_section: str = "", action: str = "(Reviewer to verify and assess)") -> CheckResult:
    return CheckResult(
        rating="",
        finding="(Auto-suggest, requires reviewer judgment) " + finding,
        page_section=page_section,
        recommended_action=action,
        confidence="Low",
    )


def na(reason: str) -> CheckResult:
    return CheckResult(rating="NA", finding=reason, page_section="", recommended_action="", confidence="High")


# ---------------------------------------------------------------------------
# Confirmation Review (14 generic doc-quality checks)
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedPfmea) -> CheckResult:
    if len(p.sheet_names) >= 10:
        return CheckResult(
            rating="FC",
            finding=f"Document is structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(rating="PC", finding=f"Only {len(p.sheet_names)} tabs; consider more structure.", confidence="Medium")


def cr_02_template(p: ProbedPfmea) -> CheckResult:
    return draft("Template version cannot be verified from xlsx content alone.", action="Confirm pfmea-builder or AIAG-VDA template was used.")


def cr_03_searchable(p: ProbedPfmea) -> CheckResult:
    has_toc = any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3])
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_toc and has_ref:
        return CheckResult(rating="FC", finding="Document has Title/TOC and References tabs.", confidence="Medium")
    return CheckResult(rating="PC", finding="Missing TOC or References tab.", recommended_action="Add search aids.", confidence="Medium")


def cr_04a_title_scope(p: ProbedPfmea) -> CheckResult:
    if p.title and p.process_name:
        return draft(f"Title: '{p.title}', Process: '{p.process_name}'. Reviewer to confirm scope.", page_section="Title page")
    return CheckResult(rating="NO", finding="No process title or name detected.", recommended_action="Populate Title page.", confidence="High")


def cr_04b_author_approver(p: ProbedPfmea) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(rating="FC", finding=f"Author='{p.author}', Approver='{p.approver}'.", confidence="High")
    missing = [x for x in ["Author", "Approver"] if not (p.author if "Author" in x else p.approver)]
    return CheckResult(rating="NO", finding=f"Missing: {', '.join(missing)}.", recommended_action="Populate Title page.", confidence="High")


def cr_04c_unique_revision(p: ProbedPfmea) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Revision='{p.revision}'.", confidence="High")
    return CheckResult(rating="NO", finding="Revision field not populated.", recommended_action="Add unique revision ID.", confidence="High")


def cr_04d_change_history(p: ProbedPfmea) -> CheckResult:
    if "01_Document_Control" in p.sheet_names:
        return CheckResult(rating="FC", finding="Document Control tab present.", page_section="Sheet '01_Document_Control'", confidence="High")
    return CheckResult(rating="PC", finding="No Document Control tab.", recommended_action="Add revision history.", confidence="High")


def cr_04e_status(p: ProbedPfmea) -> CheckResult:
    if p.status:
        return CheckResult(rating="FC", finding=f"Status='{p.status}'.", confidence="High")
    return CheckResult(rating="NO", finding="Status field not populated.", recommended_action="Set status (Draft/Review/Released).", confidence="High")


def cr_05_current_revision(p: ProbedPfmea) -> CheckResult:
    if p.revision:
        return CheckResult(rating="FC", finding=f"Current revision '{p.revision}' identifiable.", confidence="High")
    return CheckResult(rating="NO", finding="Current revision not identifiable.", recommended_action="Populate revision.", confidence="High")


def cr_06_config_mgmt(p: ProbedPfmea) -> CheckResult:
    return draft("Configuration management is organizational practice.", action="Confirm under CM system (Git, Sharepoint, Polarion).")


def cr_07_header_footer(p: ProbedPfmea) -> CheckResult:
    return draft("Headers/footers cannot be verified programmatically.", action="Manually confirm headers reflect current revision.")


def cr_08_toc(p: ProbedPfmea) -> CheckResult:
    has_toc = any("title" in s.lower() or "content" in s.lower() for s in p.sheet_names[:3])
    if has_toc:
        return CheckResult(rating="FC", finding="TOC tab present near beginning.", confidence="High")
    return CheckResult(rating="PC", finding="No TOC detected.", recommended_action="Add TOC.", confidence="High")


def cr_09_references(p: ProbedPfmea) -> CheckResult:
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_ref:
        return CheckResult(rating="FC", finding="References tab detected.", confidence="High")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add references.", confidence="High")


def cr_10_sections_complete(p: ProbedPfmea) -> CheckResult:
    pf_count = len(p.process_flow_steps)
    func_count = len(p.process_functions)
    if pf_count > 0 and func_count > 0:
        return CheckResult(rating="FC", finding=f"Process Flow ({pf_count} steps) and Functions ({func_count}) populated.", confidence="High")
    return CheckResult(rating="PC", finding=f"Process Flow/Functions sparse: steps={pf_count}, functions={func_count}.", recommended_action="Complete mapping.", confidence="High")


def cr_11_doc_id(p: ProbedPfmea) -> CheckResult:
    if p.doc_id:
        return CheckResult(rating="FC", finding=f"Document ID='{p.doc_id}'.", confidence="High")
    return CheckResult(rating="NO", finding="Document ID not populated.", recommended_action="Add unique ID.", confidence="High")


def cr_12_project_id(p: ProbedPfmea) -> CheckResult:
    if p.project:
        return CheckResult(rating="FC", finding=f"Project='{p.project}'.", confidence="High")
    return draft("Project name not detected.", action="Add project context.")


def cr_13_references_complete(p: ProbedPfmea) -> CheckResult:
    has_ref = any("reference" in s.lower() for s in p.sheet_names)
    if has_ref:
        return draft("References present; reviewer to confirm AIAG-VDA Handbook cited.", page_section="References")
    return CheckResult(rating="PC", finding="No References tab.", recommended_action="Add AIAG-VDA, Control Plan, DFMEA cross-references.", confidence="High")


def cr_14_all_sections_complete(p: ProbedPfmea) -> CheckResult:
    core_tabs = ["00_Title_Page", "02_Header_Block", "05_PFMEA_Worksheet"]
    has_all = all(t in p.sheet_names for t in core_tabs)
    if has_all:
        return CheckResult(rating="FC", finding="All core PFMEA tabs present.", confidence="High")
    return CheckResult(rating="PC", finding="Some core tabs missing.", recommended_action="Ensure all PFMEA worksheets populated.", confidence="High")


# ---------------------------------------------------------------------------
# PFMEA Assessment (14 AIAG-VDA 2019 specific checks)
# ---------------------------------------------------------------------------

def pfmeaa_01_header_block(p: ProbedPfmea) -> CheckResult:
    fields = [p.part_number, p.part_name, p.process_name, p.date_prepared]
    if all(fields):
        return CheckResult(rating="FC", finding=f"Header complete: {p.part_number} / {p.part_name} / {p.process_name}.", confidence="High")
    missing = [x for x, val in [("Part #", p.part_number), ("Part Name", p.part_name), ("Process", p.process_name), ("Date", p.date_prepared)] if not val]
    return CheckResult(rating="PC", finding=f"Missing header: {', '.join(missing)}.", recommended_action="Populate Header Block.", confidence="High")


def pfmeaa_02_process_flow(p: ProbedPfmea) -> CheckResult:
    if not p.process_flow_steps:
        return CheckResult(rating="NO", finding="Process Flow chart is empty.", recommended_action="Define all process steps.", confidence="High")
    complete = [s for s in p.process_flow_steps if s.step_type and s.equipment]
    if len(complete) == len(p.process_flow_steps):
        return CheckResult(rating="FC", finding=f"All {len(p.process_flow_steps)} steps have type and equipment.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(complete)}/{len(p.process_flow_steps)} steps complete.", recommended_action="Document all step types and equipment.", confidence="High")


def pfmeaa_03_process_functions(p: ProbedPfmea) -> CheckResult:
    if not p.process_functions:
        return CheckResult(rating="PC", finding="No process functions documented.", recommended_action="Map process functions per step.", confidence="High")
    return CheckResult(rating="FC", finding=f"{len(p.process_functions)} process functions identified.", confidence="High")


def pfmeaa_04_pfmea_worksheet_complete(p: ProbedPfmea) -> CheckResult:
    if not p.pfmea_rows:
        return CheckResult(rating="NO", finding="PFMEA worksheet is empty.", recommended_action="Populate failure modes and effects.", confidence="High")

    # Check for mandatory fields
    with_fm = [r for r in p.pfmea_rows if r.failure_mode]
    with_fe = [r for r in p.pfmea_rows if r.failure_effect]
    with_fc = [r for r in p.pfmea_rows if r.failure_cause]

    if len(with_fm) == len(p.pfmea_rows) and len(with_fe) == len(p.pfmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.pfmea_rows)} rows have FM/FE/Cause.", confidence="High")
    return CheckResult(rating="PC", finding=f"FM={len(with_fm)}, FE={len(with_fe)}, Cause={len(with_fc)}/{len(p.pfmea_rows)}.", recommended_action="Complete FM/FE/Cause for all rows.", confidence="High")


def pfmeaa_05_sod_ratings(p: ProbedPfmea) -> CheckResult:
    if not p.pfmea_rows:
        return na("No PFMEA rows.")

    with_s = [r for r in p.pfmea_rows if 1 <= r.severity <= 10]
    with_o = [r for r in p.pfmea_rows if 1 <= r.occurrence <= 10]
    with_d = [r for r in p.pfmea_rows if 1 <= r.detection <= 10]

    if len(with_s) == len(p.pfmea_rows) and len(with_o) == len(p.pfmea_rows) and len(with_d) == len(p.pfmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.pfmea_rows)} rows have valid S/O/D ratings (1-10).", confidence="High")
    return CheckResult(rating="NO", finding=f"S={len(with_s)}, O={len(with_o)}, D={len(with_d)}/{len(p.pfmea_rows)}.", recommended_action="Rate all failure modes 1-10.", confidence="High")


def pfmeaa_06_ap_computed(p: ProbedPfmea) -> CheckResult:
    if not p.pfmea_rows:
        return na("No PFMEA rows.")

    with_ap = [r for r in p.pfmea_rows if r.action_priority > 0]
    if len(with_ap) == len(p.pfmea_rows):
        return CheckResult(rating="FC", finding=f"All {len(p.pfmea_rows)} rows have Action Priority (S*O*D).", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(with_ap)}/{len(p.pfmea_rows)} have AP computed.", recommended_action="Calculate AP = S*O*D for all rows.", confidence="High")


def pfmeaa_07_high_ap_actions(p: ProbedPfmea) -> CheckResult:
    high_ap = [r for r in p.pfmea_rows if r.action_priority >= 100]
    if not high_ap:
        return CheckResult(rating="FC", finding="No high-priority items (AP >= 100).", confidence="High")

    with_action = [r for r in high_ap if r.recommended_action]
    if len(with_action) == len(high_ap):
        return CheckResult(rating="FC", finding=f"All {len(high_ap)} high-AP items have recommended actions.", confidence="High")
    return CheckResult(rating="NO", finding=f"{len(with_action)}/{len(high_ap)} high-AP items have actions.", recommended_action="Add actions for high-AP items.", confidence="High")


def pfmeaa_08_action_plan_ownership(p: ProbedPfmea) -> CheckResult:
    high_ap = [r for r in p.pfmea_rows if r.action_priority >= 100]
    if not high_ap:
        return CheckResult(rating="FC", finding="No high-AP items requiring action plan.", confidence="High")

    with_resp = [r for r in high_ap if r.responsibility]
    with_due = [r for r in high_ap if r.target_completion]

    if len(with_resp) == len(high_ap) and len(with_due) == len(high_ap):
        return CheckResult(rating="FC", finding=f"All {len(high_ap)} high-AP items have owner and due date.", confidence="High")
    return CheckResult(rating="NO", finding=f"Responsibility={len(with_resp)}, Due Date={len(with_due)}/{len(high_ap)}.", recommended_action="Assign owner and due date.", confidence="High")


def pfmeaa_09_special_characteristics(p: ProbedPfmea) -> CheckResult:
    high_s = [r for r in p.pfmea_rows if r.severity >= 8]
    if not high_s:
        return CheckResult(rating="FC", finding="No high-severity items (S >= 8) requiring special characteristics.", confidence="High")

    sc_count = len(p.special_characteristics)
    if sc_count > 0:
        return CheckResult(rating="FC", finding=f"{sc_count} special characteristics flagged for high-S items.", confidence="High")
    return CheckResult(rating="PC", finding=f"High-S items={len(high_s)}, but no special characteristics tagged.", recommended_action="Document special characteristics for high-S.", confidence="High")


def pfmeaa_10_control_plan_linkage(p: ProbedPfmea) -> CheckResult:
    high_ap = [r for r in p.pfmea_rows if r.action_priority >= 100]
    if not high_ap:
        return CheckResult(rating="FC", finding="No high-AP items requiring control plan linkage.", confidence="High")

    cp_fms = set(lnk.failure_mode for lnk in p.control_plan_linkages)
    high_ap_fms = set(r.failure_mode for r in high_ap)

    mapped = len(high_ap_fms & cp_fms)
    if mapped == len(high_ap):
        return CheckResult(rating="FC", finding=f"All {mapped} high-AP failure modes mapped to Control Plan.", confidence="High")
    return CheckResult(rating="PC", finding=f"{mapped}/{len(high_ap)} high-AP items linked to Control Plan.", recommended_action="Document linkage for all high-AP items.", confidence="High")


def pfmeaa_11_process_step_traceability(p: ProbedPfmea) -> CheckResult:
    pf_steps = set(s.step_id for s in p.process_flow_steps)
    pfmea_steps = set(r.step_id for r in p.pfmea_rows if r.step_id)

    if not pf_steps or not pfmea_steps:
        return CheckResult(rating="PC", finding=f"Process steps={len(pf_steps)}, PFMEA steps={len(pfmea_steps)}.", recommended_action="Ensure all steps traced.", confidence="High")

    orphan = pfmea_steps - pf_steps
    if not orphan:
        return CheckResult(rating="FC", finding=f"All PFMEA steps ({len(pfmea_steps)}) trace to Process Flow.", confidence="High")
    return CheckResult(rating="PC", finding=f"{len(orphan)} PFMEA steps orphaned (not in Process Flow).", recommended_action="Verify step IDs match.", confidence="High")


def pfmeaa_12_lessons_learned(p: ProbedPfmea) -> CheckResult:
    if "11_Lessons_Learned_Crossref" in p.sheet_names:
        return draft("Lessons Learned tab present; reviewer to confirm cross-references.", page_section="11_Lessons_Learned_Crossref")
    return CheckResult(rating="PC", finding="No Lessons Learned tab.", recommended_action="Add Lessons Learned cross-reference.", confidence="High")


def pfmeaa_13_dfmea_cross_link(p: ProbedPfmea) -> CheckResult:
    return draft("DFMEA cross-reference not detectible from PFMEA xlsx; must be external document link.", action="Document DFMEA traceability in Design Review.")


def pfmeaa_14_high_ap_completion(p: ProbedPfmea) -> CheckResult:
    high_ap = [r for r in p.pfmea_rows if r.action_priority >= 100]
    if not high_ap:
        return CheckResult(rating="FC", finding="No high-AP items outstanding.", confidence="High")

    completed = sum(1 for r in high_ap if r.target_completion and "complete" in r.target_completion.lower())
    if completed == len(high_ap):
        return CheckResult(rating="FC", finding=f"All {len(high_ap)} high-AP items completed.", confidence="High")
    return CheckResult(rating="NO", finding=f"{completed}/{len(high_ap)} high-AP actions completed.", recommended_action=f"{len(high_ap) - completed} items need completion.", confidence="High")


# ---------------------------------------------------------------------------
# Verification Assessment
# ---------------------------------------------------------------------------

def _va_external(label: str) -> CheckResult:
    return draft(f"{label} is governed by external documentation — not in PFMEA xlsx.", action="Verify against Control Plan / Verification Plan.")


def va_01_plan_compliance(p): return _va_external("Verification Plan alignment with PFMEA")
def va_02_methods(p): return _va_external("Verification methods and sample sizes")
def va_03_executed(p): return _va_external("Verification executed per plan")
def va_04_report(p): return _va_external("Verification Report with results")


@dataclass
class CheckDef:
    id: str
    tab: str
    section: str
    requirement: str
    obligation: str  # Shall / Should


# Build canonical checklist registry
CHECKS_CR = [
    ("CR-01", "Structured", "Doc Quality", "Document is properly structured with distinct tabs", "Shall"),
    ("CR-02", "Template", "Doc Quality", "AIAG-VDA or equivalent template used", "Should"),
    ("CR-03", "Searchable", "Doc Quality", "Document has TOC and References for navigation", "Should"),
    ("CR-04a", "Title/Scope", "Doc Quality", "Process title and scope clearly defined", "Shall"),
    ("CR-04b", "Author/Approver", "Doc Quality", "Author and approver documented", "Shall"),
    ("CR-04c", "Revision", "Doc Quality", "Unique revision identifier", "Shall"),
    ("CR-04d", "Change History", "Doc Quality", "Document control and change history logged", "Should"),
    ("CR-04e", "Status", "Doc Quality", "Document status (Draft/Review/Released) clear", "Shall"),
    ("CR-05", "Current Revision", "Doc Quality", "Current revision is identifiable", "Shall"),
    ("CR-06", "Config Mgmt", "Doc Quality", "Document under configuration management", "Should"),
    ("CR-07", "Headers/Footers", "Doc Quality", "Headers/footers show document identification", "Should"),
    ("CR-08", "TOC", "Doc Quality", "Table of Contents for navigation", "Should"),
    ("CR-09", "References", "Doc Quality", "References tab with key standards", "Should"),
    ("CR-14", "Sections", "Doc Quality", "All major PFMEA sections present", "Shall"),
]

CHECKS_PFMEAA = [
    ("PFMEA-01", "Header Block", "Completeness", "Header block contains part #, name, process, date", "Shall"),
    ("PFMEA-02", "Process Flow", "Completeness", "Process flow chart populated with all steps", "Shall"),
    ("PFMEA-03", "Process Functions", "Completeness", "Process functions identified per step", "Shall"),
    ("PFMEA-04", "PFMEA Rows", "Completeness", "PFMEA worksheet rows with FM/FE/Cause populated", "Shall"),
    ("PFMEA-05", "S/O/D Ratings", "Assessment", "Severity, Occurrence, Detection rated 1-10 for all FM", "Shall"),
    ("PFMEA-06", "AP Computed", "Assessment", "Action Priority (S*O*D) calculated for all rows", "Shall"),
    ("PFMEA-07", "High-AP Actions", "Containment", "High-AP items (>= 100) have recommended actions", "Shall"),
    ("PFMEA-08", "Action Ownership", "Containment", "High-AP actions have owner and due date", "Shall"),
    ("PFMEA-09", "Special Characteristics", "Control", "High-S items (>= 8) flagged as special characteristics", "Should"),
    ("PFMEA-10", "Control Plan Link", "Control", "High-AP items linked to Control Plan", "Shall"),
    ("PFMEA-11", "Step Traceability", "Completeness", "PFMEA failure modes trace to process steps", "Shall"),
    ("PFMEA-12", "Lessons Learned", "Completeness", "Lessons Learned cross-reference documented", "Should"),
    ("PFMEA-13", "DFMEA Link", "Traceability", "PFMEA linked to DFMEA for design inputs", "Should"),
    ("PFMEA-14", "High-AP Completion", "Closure", "High-AP actions completed or tracked", "Shall"),
]

CHECKS_VA = [
    ("VA-01", "Verification Plan", "Verification", "Verification Plan ensures PFMEA compliance", "Should"),
    ("VA-02", "Verification Methods", "Verification", "Verification methods and sample sizes defined", "Should"),
    ("VA-03", "Verification Executed", "Verification", "Verification executed per plan", "Should"),
    ("VA-04", "Verification Report", "Verification", "Verification Report with results and evidence", "Should"),
]
