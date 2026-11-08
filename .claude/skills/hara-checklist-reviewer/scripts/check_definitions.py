"""
Canonical checklist definitions and verification logic.

Each check is a dict with keys:
- id: row id as it appears on the TOMCO checklist (e.g. "1", "10b", "33a")
- tab: which output tab this check belongs to (CR / FSA / VA)
- section: section header text (rendered as a banner row above the check)
- requirement: the requirement text
- obligation: "Shall" or "Should" (or "" for sub-rows)
- verify: callable(probed: ProbedHara) -> CheckResult
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from hara_probe import ProbedHara


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    rating: str = ""              # FC / LC / PC / NO / NA / "" (pending)
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""          # High / Medium / Low / "" for binary CR


# Helper for "draft" results (subjective, low confidence)
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
# Verification functions — Confirmation Review
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedHara) -> CheckResult:
    if len(p.sheet_names) >= 5:
        return CheckResult(
            rating="FC",
            finding=f"Document is structured into {len(p.sheet_names)} tabs with distinct sections (Title, Doc Control, Assumptions, etc.).",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has only {len(p.sheet_names)} tabs; structure may be insufficient for maintainability.",
        recommended_action="Add separate tabs for distinct concerns (assumptions, references, summary).",
        confidence="Medium",
    )


def cr_02_template(p: ProbedHara) -> CheckResult:
    return draft(
        "Template version cannot be detected from the xlsx content alone.",
        action="Confirm the latest applicable HARA template was used at document creation.",
    )


def cr_03_searchable(p: ProbedHara) -> CheckResult:
    if p.has_table_of_contents and p.references_sheet:
        return CheckResult(
            rating="FC",
            finding="Document has a Title/Contents tab and a References tab; structured columns aid search.",
            page_section=f"Sheets: {p.sheet_names[0]}, {p.references_sheet}",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Some search aids are present but not all (TOC and Reference list).",
        recommended_action="Add a Table of Contents and References sheet for navigation.",
        confidence="Medium",
    )


def cr_04a_title_scope(p: ProbedHara) -> CheckResult:
    if p.title:
        return draft(
            f"Title is: '{p.title}'. Reviewer to confirm it covers the document scope.",
            page_section="Title page row 2",
        )
    return CheckResult(
        rating="NO",
        finding="No title detected on the Title page.",
        recommended_action="Add a clear document title that reflects the scope.",
        confidence="High",
    )


def cr_04b_author_approver(p: ProbedHara) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(
            rating="FC",
            finding=f"Author='{p.author}', Approver='{p.approver}' both populated on Title page.",
            page_section="Title page",
            confidence="High",
        )
    missing = []
    if not p.author: missing.append("Author")
    if not p.approver: missing.append("Approver")
    return CheckResult(
        rating="NO",
        finding=f"Missing on Title page: {', '.join(missing)}.",
        recommended_action=f"Populate {', '.join(missing)} field(s) on the Title page.",
        confidence="High",
    )


def cr_04c_unique_revision(p: ProbedHara) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Revision='{p.revision}' is set on the Title page.",
            page_section="Title page Revision field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Revision field not populated on Title page.",
        recommended_action="Populate the Revision field; ensure each revision has a unique identifier.",
        confidence="High",
    )


def cr_04d_change_history(p: ProbedHara) -> CheckResult:
    if p.revision_history_rows >= 1:
        return CheckResult(
            rating="FC",
            finding=f"Document Control tab contains {p.revision_history_rows} revision history row(s).",
            page_section=f"Sheet '{p.likely_doc_control_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No revision history rows detected on the Document Control tab.",
        recommended_action="Add a populated revision history table to the Document Control tab.",
        confidence="High",
    )


def cr_04e_status(p: ProbedHara) -> CheckResult:
    if p.status:
        return CheckResult(
            rating="FC",
            finding=f"Status='{p.status}' is set on the Title page.",
            page_section="Title page Status field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No work-product status field populated on the Title page.",
        recommended_action="Add a Status field (Draft / In Review / Released) to the Title page.",
        confidence="High",
    )


def cr_05_current_revision(p: ProbedHara) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Current revision '{p.revision}' is identifiable on Title page.",
            page_section="Title page Revision field",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Current revision is not identifiable.",
        recommended_action="Populate the Revision field on the Title page.",
        confidence="High",
    )


def cr_06_config_mgmt(p: ProbedHara) -> CheckResult:
    return draft(
        "Configuration management is an organizational practice; cannot be verified from xlsx content.",
        action="Confirm the document is checked into the project's configuration-management system (e.g., Polarion, DOORS, Git).",
    )


def cr_07_header_footer(p: ProbedHara) -> CheckResult:
    return draft(
        "Worksheet headers/footers cannot be reliably verified programmatically.",
        action="Open the workbook in Excel and confirm header/footer reflect current document ID and revision.",
    )


def cr_08_toc(p: ProbedHara) -> CheckResult:
    if p.has_table_of_contents:
        return CheckResult(
            rating="FC",
            finding="A Title or Contents tab is present in the first three sheets.",
            page_section=f"Sheet '{p.sheet_names[0]}'",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="No Table of Contents tab detected near the beginning of the workbook.",
        recommended_action="Add a Table of Contents tab listing all sheets and their purposes.",
        confidence="Medium",
    )


def cr_09_references(p: ProbedHara) -> CheckResult:
    if p.references_sheet:
        return draft(
            f"References-style content found on sheet '{p.references_sheet}'. Reviewer to confirm completeness.",
            page_section=f"Sheet '{p.references_sheet}'",
        )
    return CheckResult(
        rating="PC",
        finding="No dedicated References tab detected.",
        recommended_action="Add a References tab citing ISO 26262, OEM standards, item-definition document, and any related HARA work products.",
        confidence="Medium",
    )


def cr_10_sections_complete(p: ProbedHara) -> CheckResult:
    # Heuristic: count populated rows on the HARA worksheet and Safety Goals tab
    hara_completion = len([r for r in p.hara_rows if r.s and r.e and r.c]) / max(1, len(p.hara_rows))
    sg_completion = len([s for s in p.safety_goals if s.sg_text and s.safe_state]) / max(1, len(p.safety_goals))
    overall = (hara_completion + sg_completion) / 2
    if overall >= 0.95:
        return CheckResult(
            rating="FC",
            finding=f"All major sections are populated. HARA rows {hara_completion:.0%} complete; SGs {sg_completion:.0%} complete.",
            confidence="High",
        )
    if overall >= 0.7:
        return CheckResult(
            rating="LC",
            finding=f"Most sections populated. HARA rows {hara_completion:.0%}; SGs {sg_completion:.0%}.",
            recommended_action="Complete remaining S/E/C/safe-state cells.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Significant unpopulated sections. HARA rows {hara_completion:.0%}; SGs {sg_completion:.0%}.",
        recommended_action="Complete the HARA worksheet and Safety Goals tabs before review.",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Verification functions — Functional Safety Assessment
# ---------------------------------------------------------------------------

def fsa_01_item_def(p: ProbedHara) -> CheckResult:
    if p.likely_assumptions_sheet or any("scope" in s.lower() or "boundary" in s.lower() for s in p.sheet_names):
        return draft(
            f"Item-definition content appears on '{p.likely_assumptions_sheet}' or boundary tab. Reviewer to confirm an Item Definition document exists and is referenced.",
            page_section=f"Sheet '{p.likely_assumptions_sheet}'",
        )
    return CheckResult(
        rating="PC",
        finding="No assumptions / scope / boundary tab found in the HARA xlsx.",
        recommended_action="Reference the Item Definition document in the HARA References tab; add an Assumptions tab summarising scope.",
        confidence="Medium",
    )


def fsa_02_supporting_info(p: ProbedHara) -> CheckResult:
    return draft(
        "Impact analysis and information on independent items typically reside in separate documents.",
        action="Confirm the impact analysis and any related-item information are referenced in the HARA.",
    )


def fsa_03_tsr(p: ProbedHara) -> CheckResult:
    return na("This requirement appears to belong to a TSC review (refers to Technical Safety Requirements). Mark NA for HARA review.")


def fsa_04_external_interfaces(p: ProbedHara) -> CheckResult:
    return na("This requirement appears to belong to a TSC review (refers to external interface properties). Mark NA for HARA review.")


def fsa_05_situations_described(p: ProbedHara) -> CheckResult:
    if p.operating_environment:
        return CheckResult(
            rating="FC",
            finding=f"Operating environment tab lists {len(p.operating_environment)} situation rows.",
            page_section=f"Sheet '{p.likely_environment_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No operating environment / situations enumeration found.",
        recommended_action="Add an Operating Environment tab listing locations, speed bands, and weather conditions.",
        confidence="High",
    )


def fsa_06_techniques(p: ProbedHara) -> CheckResult:
    n_mal = len(p.malfunctions_used)
    if n_mal >= 14:
        return CheckResult(
            rating="FC",
            finding=f"Each function evaluated against {n_mal} malfunction guide words; matches the standard 14-malfunction technique.",
            page_section=f"Sheet '{p.likely_hara_sheet}'",
            confidence="High",
        )
    if n_mal >= 8:
        return CheckResult(
            rating="LC",
            finding=f"Each function evaluated against {n_mal} malfunction guide words.",
            recommended_action=f"Confirm coverage; consider adding the remaining {14 - n_mal} guide words from the standard 14-malfunction set.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {n_mal} malfunction guide words used. The 14-malfunction technique is widely applied in automotive HARAs.",
        recommended_action="Adopt a systematic guide-word technique (e.g., the 14-malfunction set) and re-evaluate each function.",
        confidence="High",
    )


def fsa_07_vehicle_level(p: ProbedHara) -> CheckResult:
    if p.hara_rows:
        sample = [r.hazardous_event for r in p.hara_rows[:30] if r.hazardous_event]
        keywords = ["vehicle", "driver", "lane", "yaw", "brake", "speed", "road", "crash", "collision", "stability"]
        with_vehicle_lang = sum(1 for h in sample if any(k in h.lower() for k in keywords))
        if sample and with_vehicle_lang / len(sample) >= 0.6:
            return CheckResult(
                rating="FC",
                finding=f"{with_vehicle_lang}/{len(sample)} sampled hazardous events use vehicle-level language.",
                page_section=f"Sheet '{p.likely_hara_sheet}'",
                confidence="Medium",
            )
        return CheckResult(
            rating="PC",
            finding=f"Only {with_vehicle_lang}/{len(sample)} sampled hazardous events use clearly vehicle-level language.",
            recommended_action="Reword hazardous events in vehicle-level terms (driver, vehicle, lane, road) rather than component-level (signal, ECU).",
            confidence="Medium",
        )
    return na("No HARA rows found.")


def fsa_08_combinations(p: ProbedHara) -> CheckResult:
    if not p.hara_rows:
        return CheckResult(rating="NO", finding="No HARA rows found.", recommended_action="Populate the HARA worksheet.")
    n_funcs = len({r.function for r in p.hara_rows if r.function})
    n_mals = len({r.malfunction for r in p.hara_rows if r.malfunction})
    n_envs = len({(r.location, r.weather) for r in p.hara_rows if r.location or r.weather})
    expected = n_funcs * n_mals * n_envs
    if expected and len(p.hara_rows) / expected >= 0.5:
        return CheckResult(
            rating="FC",
            finding=f"HARA contains {len(p.hara_rows)} rows from {n_funcs} functions × {n_mals} malfunctions × {n_envs} environment combinations.",
            page_section=f"Sheet '{p.likely_hara_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"HARA has {len(p.hara_rows)} rows; expected ~{expected} for full Cartesian. Coverage may be incomplete.",
        recommended_action="Verify Cartesian coverage of (function × malfunction × operational situation).",
        confidence="High",
    )


def fsa_09_consequences(p: ProbedHara) -> CheckResult:
    return draft(
        "Hazardous-event descriptions are present; reviewer to confirm consequence (occupant, other road user, property) is captured for each.",
        page_section=f"Sheet '{p.likely_hara_sheet}'",
    )


def fsa_10_outside_scope(p: ProbedHara) -> CheckResult:
    return draft(
        "Out-of-scope hazards (cybersecurity, SOTIF, environmental) and their owners are typically called out in Assumptions.",
        page_section=f"Sheet '{p.likely_assumptions_sheet}'",
    )


def fsa_10b_classified(p: ProbedHara) -> CheckResult:
    if not p.hara_rows:
        return na("No HARA rows.")
    classified = [r for r in p.hara_rows if r.s and r.e and r.c]
    rate = len(classified) / len(p.hara_rows)
    if rate == 1.0:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hara_rows)} HARA rows have S, E, and C populated.",
            page_section=f"Sheet '{p.likely_hara_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC" if rate < 0.95 else "LC",
        finding=f"{len(classified)}/{len(p.hara_rows)} ({rate:.0%}) HARA rows classified.",
        recommended_action=f"Complete S/E/C classification on {len(p.hara_rows) - len(classified)} remaining rows.",
        confidence="High",
    )


def fsa_11_severity(p: ProbedHara) -> CheckResult:
    if not p.hara_rows:
        return na("No HARA rows.")
    with_s = [r for r in p.hara_rows if r.s]
    with_rationale = [r for r in with_s if r.s_rationale]
    if not with_s:
        return CheckResult(rating="NO", finding="No severity ratings found.", recommended_action="Populate the S column.", confidence="High")
    rate = len(with_rationale) / len(with_s)
    if rate >= 0.95:
        return CheckResult(
            rating="FC",
            finding=f"All severity ratings have rationale ({len(with_rationale)}/{len(with_s)}). S values used: {sorted({r.s for r in with_s})}.",
            page_section=f"Sheet '{p.likely_hara_sheet}', S Rationale column",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_rationale)}/{len(with_s)} severity ratings have written rationale.",
        recommended_action="Add rationale text to every S rating cell.",
        confidence="High",
    )


def fsa_12_s0_handling(p: ProbedHara) -> CheckResult:
    s0_rows = [r for r in p.hara_rows if r.s == "S0"]
    if not s0_rows:
        return CheckResult(
            rating="FC",
            finding="No S0 rows in the HARA — check is vacuously satisfied.",
            confidence="High",
        )
    s0_rows_with_sg = [r for r in s0_rows if r.asil and r.asil != "—" and r.asil != "QM"]
    if not s0_rows_with_sg:
        return CheckResult(
            rating="FC",
            finding=f"{len(s0_rows)} S0 rows present; none derive a safety goal (ASIL is — or QM as expected).",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"{len(s0_rows_with_sg)} S0 rows have ASIL ≥ A; S0 should not yield a safety goal.",
        recommended_action="Review the S0 rows; either re-classify severity or remove derived safety goals.",
        confidence="High",
    )


def fsa_13_exposure(p: ProbedHara) -> CheckResult:
    if not p.hara_rows:
        return na("No HARA rows.")
    with_e = [r for r in p.hara_rows if r.e]
    with_rationale = [r for r in with_e if r.e_rationale]
    if not with_e:
        return CheckResult(rating="NO", finding="No exposure ratings found.", confidence="High")
    rate = len(with_rationale) / len(with_e)
    if rate >= 0.95:
        return CheckResult(
            rating="FC",
            finding=f"All exposure ratings have rationale ({len(with_rationale)}/{len(with_e)}). E values: {sorted({r.e for r in with_e})}.",
            page_section=f"Sheet '{p.likely_hara_sheet}', E Rationale column",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_rationale)}/{len(with_e)} exposure ratings have rationale.",
        recommended_action="Add rationale text to every E rating cell, citing operational situation frequency, not hazard frequency.",
        confidence="High",
    )


def fsa_14_e_not_fleet(p: ProbedHara) -> CheckResult:
    return draft(
        "Verify E rationale text references operational-situation probability, not number of vehicles equipped.",
        page_section=f"Sheet '{p.likely_hara_sheet}', E Rationale column",
    )


def fsa_15_e0(p: ProbedHara) -> CheckResult:
    e0_rows = [r for r in p.hara_rows if r.e == "E0"]
    if not e0_rows:
        return CheckResult(rating="FC", finding="No E0 rows; check vacuously satisfied.", confidence="High")
    e0_with_sg = [r for r in e0_rows if r.asil and r.asil not in ("QM", "—", "")]
    if not e0_with_sg:
        return CheckResult(rating="FC", finding=f"{len(e0_rows)} E0 rows; none derive a safety goal (correct).", confidence="High")
    return CheckResult(
        rating="NO",
        finding=f"{len(e0_with_sg)} E0 rows have ASIL ≥ A; E0 events should not be followed up.",
        recommended_action="Review E0 rows and remove derived safety goals.",
        confidence="High",
    )


def fsa_16_controllability(p: ProbedHara) -> CheckResult:
    if not p.hara_rows:
        return na("No HARA rows.")
    with_c = [r for r in p.hara_rows if r.c]
    with_rationale = [r for r in with_c if r.c_rationale]
    if not with_c:
        return CheckResult(rating="NO", finding="No controllability ratings found.", confidence="High")
    rate = len(with_rationale) / len(with_c)
    if rate >= 0.95:
        return CheckResult(
            rating="FC",
            finding=f"All controllability ratings have rationale ({len(with_rationale)}/{len(with_c)}). C values: {sorted({r.c for r in with_c})}.",
            page_section=f"Sheet '{p.likely_hara_sheet}', C Rationale column",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_rationale)}/{len(with_c)} controllability ratings have rationale.",
        recommended_action="Add rationale text to every C rating cell.",
        confidence="High",
    )


def fsa_17_unavailability(p: ProbedHara) -> CheckResult:
    return draft(
        "Hazards addressing item unavailability: confirm appropriate justification or applicable regulatory citations.",
    )


def fsa_18_asil_determined(p: ProbedHara) -> CheckResult:
    if not p.hara_rows:
        return na("No HARA rows.")
    eligible = [r for r in p.hara_rows if r.s != "S0" and r.e != "E0" and r.s and r.e]
    with_asil = [r for r in eligible if r.asil]
    if eligible and len(with_asil) / len(eligible) >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"ASIL determined for all {len(with_asil)} eligible HARA rows (excluding S0 and E0).",
            page_section=f"Sheet '{p.likely_hara_sheet}', ASIL column",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(with_asil)}/{len(eligible)} eligible rows have ASIL.",
        recommended_action="Populate the ASIL column for all rows where S>S0 and E>E0.",
        confidence="High",
    )


def fsa_19_situation_detail(p: ProbedHara) -> CheckResult:
    if len(p.operating_environment) >= 6:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.operating_environment)} operating-environment rows; granularity supports realistic exposure ratings.",
            confidence="Medium",
        )
    return draft(
        f"Only {len(p.operating_environment)} operating-environment rows; ensure granularity does not artificially lower ASIL.",
        page_section=f"Sheet '{p.likely_environment_sheet}'",
    )


def fsa_20_safety_goals(p: ProbedHara) -> CheckResult:
    asil_rows = [r for r in p.hara_rows if r.asil and r.asil not in ("QM", "—", "")]
    if not asil_rows:
        return CheckResult(rating="FC", finding="No ASIL≥A rows; no safety goals required.", confidence="High")
    if not p.safety_goals:
        return CheckResult(
            rating="NO",
            finding=f"{len(asil_rows)} HARA rows have ASIL≥A but no safety goals are documented.",
            recommended_action="Derive at least one safety goal per (function, hazard) pair with ASIL≥A; consolidate similar SGs.",
            confidence="High",
        )
    return CheckResult(
        rating="FC",
        finding=f"{len(p.safety_goals)} safety goals derived from {len(asil_rows)} ASIL≥A HARA rows; consolidation evident.",
        page_section=f"Sheet '{p.likely_safety_goals_sheet}'",
        confidence="High",
    )


def fsa_21_combined_asil(p: ProbedHara) -> CheckResult:
    if not p.safety_goals:
        return na("No safety goals.")
    # Each SG should carry the highest ASIL across its driving HARA rows. Without per-SG drill-down we infer.
    asil_rank = {"QM": 0, "A": 1, "B": 2, "C": 3, "D": 4}
    base_asils = [a.split("(")[0].strip() for a in (sg.asil for sg in p.safety_goals)]
    if all(a in asil_rank for a in base_asils):
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.safety_goals)} safety goals carry an ASIL value ({sorted(set(base_asils))}); presumed to reflect worst-case across driving rows.",
            confidence="Medium",
        )
    return draft(
        "Reviewer to confirm that combined safety goals carry the highest contributing ASIL.",
    )


def fsa_22_safe_states(p: ProbedHara) -> CheckResult:
    if not p.safety_goals:
        return na("No safety goals.")
    with_safe = [sg for sg in p.safety_goals if sg.safe_state]
    rate = len(with_safe) / len(p.safety_goals)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.safety_goals)} safety goals specify a safe state.",
            page_section=f"Sheet '{p.likely_safety_goals_sheet}', Safe State column",
            confidence="High",
        )
    return CheckResult(
        rating="PC" if rate < 0.95 else "LC",
        finding=f"{len(with_safe)}/{len(p.safety_goals)} safety goals specify a safe state.",
        recommended_action=f"Specify safe states for the remaining {len(p.safety_goals) - len(with_safe)} safety goals.",
        confidence="High",
    )


def fsa_23_sg_attributes(p: ProbedHara) -> CheckResult:
    if not p.safety_goals:
        return na("No safety goals.")
    complete = [sg for sg in p.safety_goals if sg.sg_id and sg.asil and sg.sg_text and sg.safe_state]
    rate = len(complete) / len(p.safety_goals)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.safety_goals)} safety goals have ID, ASIL, text, and safe state populated.",
            page_section=f"Sheet '{p.likely_safety_goals_sheet}'",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(complete)}/{len(p.safety_goals)} safety goals have all required attributes.",
        recommended_action="Complete missing SG attributes (ID, ASIL, text, safe state).",
        confidence="High",
    )


# ---------------------------------------------------------------------------
# Verification Assessment — most are external; HARA-specific 33a–e are checkable
# ---------------------------------------------------------------------------

def _va_external(label: str) -> CheckResult:
    return draft(
        f"{label} is governed by an external Verification Plan / Specification / Report — not in the HARA xlsx.",
        action="Verify against the project's Verification Plan, Specification, and Report documents.",
    )


def va_24_plan_compliance(p): return _va_external("Verification Plan ensuring compliance with FSC")
def va_25_validation_refined(p): return na("Belongs to TSC/validation review, not HARA confirmation.")
def va_26_plan_addresses(p): return _va_external("Verification Plan addressing content/methods/criteria/env/tools/anomalies/regression")
def va_26a(p): return _va_external("Plan content")
def va_26b(p): return _va_external("Verification methods")
def va_26c(p): return _va_external("Pass/fail criteria")
def va_26d(p): return _va_external("Verification environment")
def va_26e(p): return _va_external("Verification tools")
def va_26f(p): return _va_external("Anomaly handling")
def va_26g(p): return _va_external("Regression strategy")
def va_27_planning(p): return _va_external("Planning considerations")
def va_27a(p): return _va_external("Method adequacy")
def va_27b(p): return _va_external("Work product complexity")
def va_27c(p): return _va_external("Prior experience")
def va_27d(p): return _va_external("Technology maturity")
def va_28_methods(p): return _va_external("Verification method specification")
def va_28a(p): return _va_external("Review/analysis checklists (e.g., this skill's output)")
def va_28b(p): return _va_external("Simulation scenarios")
def va_28c(p): return _va_external("Test cases / data / objects")
def va_29_test_spec(p): return _va_external("Test case content specification")
def va_29a(p): return _va_external("Test case unique identification")
def va_29b(p): return _va_external("Reference to verified work-product version")
def va_29c(p): return _va_external("Preconditions and configurations")
def va_29d(p): return _va_external("Environmental conditions")
def va_29e(p): return _va_external("Input data / sequences / values")
def va_29f(p): return _va_external("Expected behavior / output / tolerances")
def va_30_grouping(p): return _va_external("Test case grouping")
def va_30a(p): return _va_external("Test environment per group")
def va_30b(p): return _va_external("Logical/temporal dependencies")
def va_30c(p): return _va_external("Resources")
def va_31_executed(p): return _va_external("Verification executed per plan")
def va_32_report(p): return _va_external("Verification Report content")
def va_32a(p): return _va_external("Verified work-product unique identification")
def va_32b(p): return _va_external("Reference to plan and specification")
def va_32c(p): return _va_external("Verification environment / tools / calibration data")
def va_32d(p): return _va_external("Compliance level of verification results")
def va_32e(p): return _va_external("Pass/fail statement and rationale")
def va_32f(p): return _va_external("Reasons for un-executed verification steps")


def va_33a_situations(p: ProbedHara) -> CheckResult:
    if len(p.operating_environment) >= 6:
        return CheckResult(
            rating="FC",
            finding=f"{len(p.operating_environment)} operating-environment rows; situational completeness adequate.",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"Only {len(p.operating_environment)} operating-environment rows.",
        recommended_action="Expand the situations enumeration (locations × weather × speed bands).",
        confidence="High",
    )


def va_33b_item_def(p: ProbedHara) -> CheckResult:
    if p.functions:
        return draft(
            f"{len(p.functions)} functions enumerated in the HARA. Reviewer to verify each is in the Item Definition.",
            page_section=f"Sheet '{p.likely_functions_sheet}'",
        )
    return CheckResult(
        rating="NO",
        finding="No functions list found in the HARA.",
        recommended_action="Enumerate the item's functions in a dedicated Functions tab.",
        confidence="High",
    )


def va_33c_consistency(p: ProbedHara) -> CheckResult:
    return draft(
        "Consistency with related HARAs / hazard analyses cannot be verified from a single workbook.",
    )


def va_33d_coverage(p: ProbedHara) -> CheckResult:
    return fsa_08_combinations(p)  # same logic


def va_33e_asil_consistency(p: ProbedHara) -> CheckResult:
    if p.is_hara_builder_format:
        return CheckResult(
            rating="FC",
            finding="HARA produced by hara-builder uses formula-driven ASIL (INDEX/MATCH against ASIL Matrix tab); recorded ASIL is structurally consistent with S/E/C inputs.",
            page_section=f"Sheet '{p.likely_hara_sheet}', ASIL formula chain",
            confidence="High",
        )
    # For other formats, recompute and compare
    asil_matrix = {
        ("S1","E1"):("QM","QM","QM"),("S1","E2"):("QM","QM","QM"),("S1","E3"):("QM","QM","A"),("S1","E4"):("QM","A","B"),
        ("S2","E1"):("QM","QM","QM"),("S2","E2"):("QM","QM","A"),("S2","E3"):("QM","A","B"),("S2","E4"):("A","B","C"),
        ("S3","E1"):("QM","QM","A"),("S3","E2"):("QM","A","B"),("S3","E3"):("A","B","C"),("S3","E4"):("B","C","D"),
    }
    inconsistent = []
    for r in p.hara_rows:
        if r.s == "S0" or r.e == "E0" or not (r.s and r.e and r.c and r.asil):
            continue
        c_idx = {"C1":0, "C2":1, "C3":2}.get(r.c)
        if c_idx is None: continue
        expected = asil_matrix.get((r.s, r.e), ("?","?","?"))[c_idx]
        if expected != r.asil.split("(")[0].strip():
            inconsistent.append((r.row, r.s, r.e, r.c, expected, r.asil))
    if not inconsistent:
        return CheckResult(rating="FC", finding="All ASIL values consistent with S/E/C per ISO 26262 Table 4.", confidence="High")
    return CheckResult(
        rating="NO",
        finding=f"{len(inconsistent)} HARA rows have ASIL inconsistent with S/E/C.",
        recommended_action="Re-derive ASIL values from S/E/C using ISO 26262-3 Table 4.",
        confidence="High",
    )


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
    verify: Callable[[ProbedHara], CheckResult]


CHECKS: list[CheckDef] = [
    # Confirmation Review
    CheckDef("1",  "CR", "Document Quality", "Is the document structured in a clear manner (using headlines, template layouts, context etc.) that supports the maintainability and understandability?", "Shall", cr_01_structured),
    CheckDef("2",  "CR", "Document Quality", "On the date the document was first created, was the latest template available used?", "Should", cr_02_template),
    CheckDef("3",  "CR", "Document Quality", "Does the document structure facilitate the search for relevant information e.g. cross references, index table, list of abbreviations?", "Should", cr_03_searchable),
    CheckDef("4a", "CR", "Document Quality", "Does the title cover the scope of the content?", "Shall", cr_04a_title_scope),
    CheckDef("4b", "CR", "Document Quality", "Are the author and approver(s) listed?", "Shall", cr_04b_author_approver),
    CheckDef("4c", "CR", "Document Quality", "Is there a unique identification for each different revision (version) e.g. in a history table?", "Shall", cr_04c_unique_revision),
    CheckDef("4d", "CR", "Document Quality", "Is there a change history available?", "Shall", cr_04d_change_history),
    CheckDef("4e", "CR", "Document Quality", "Is the status of the work product provided?", "Shall", cr_04e_status),
    CheckDef("5",  "CR", "Document Quality", "Is the current applicable revision (version) of a document clearly identifiable?", "Shall", cr_05_current_revision),
    CheckDef("6",  "CR", "Document Quality", "Is the document under configuration and change management?", "Shall", cr_06_config_mgmt),
    CheckDef("7",  "CR", "Document Quality", "Are the header and footer updated?", "Should", cr_07_header_footer),
    CheckDef("8",  "CR", "Document Quality", "Does this document contain a correct table of content?", "Shall", cr_08_toc),
    CheckDef("9",  "CR", "Document Quality", "Does the Reference Table list all of the references contained in the Work Product?", "Should", cr_09_references),
    CheckDef("10", "CR", "Document Quality", "Have all sections of the Work Product been completed?", "Should", cr_10_sections_complete),

    # Functional Safety Assessment
    CheckDef("1",  "FSA", "Prerequisites", "Prerequisites Available and Useful: Item Definition", "Shall", fsa_01_item_def),
    CheckDef("2",  "FSA", "Prerequisites", "Further Supporting Information: Impact analysis (if applicable), relevant information on other independent items", "Should", fsa_02_supporting_info),
    CheckDef("3",  "FSA", "Initiation", "Have technical safety requirements been specified in accordance with the FSC and the preliminary architectural assumptions of the item?", "Shall", fsa_03_tsr),
    CheckDef("4",  "FSA", "Initiation", "If applicable, have external system interfaces properties been considered?", "Shall", fsa_04_external_interfaces),
    CheckDef("5",  "FSA", "Situation Analysis and Hazard Identification", "Have the operational situations and operating modes been described for both correct and incorrect use of the vehicle?", "Shall", fsa_05_situations_described),
    CheckDef("6",  "FSA", "Situation Analysis and Hazard Identification", "Were adequate techniques used to systematically determine all hazards?", "Shall", fsa_06_techniques),
    CheckDef("7",  "FSA", "Situation Analysis and Hazard Identification", "Are the hazards defined in terms of the conditions or behavior that can be observed at the vehicle level?", "Shall", fsa_07_vehicle_level),
    CheckDef("8",  "FSA", "Situation Analysis and Hazard Identification", "Were hazardous events determined for all relevant combinations of operational situations and hazards?", "Shall", fsa_08_combinations),
    CheckDef("9",  "FSA", "Situation Analysis and Hazard Identification", "Were all consequences of hazardous events identified?", "Shall", fsa_09_consequences),
    CheckDef("10", "FSA", "Situation Analysis and Hazard Identification", "Were the appropriate measures to mitigate or control hazards outside the scope of ISO 26262 highlighted and reported?", "Should", fsa_10_outside_scope),
    CheckDef("10b","FSA", "Classification of Hazardous Events", "Have all identified hazardous events, except those outside the scope of ISO 26262, been classified?", "Shall", fsa_10b_classified),
    CheckDef("11", "FSA", "Classification of Hazardous Events", "Has the severity of potential harm been estimated based on a defined rationale and assigned to S0, S1, S2 or S3?", "Shall", fsa_11_severity),
    CheckDef("12", "FSA", "Classification of Hazardous Events", "Is severity class S0 used only when malfunctioning behavior is clearly limited to material damage and does not involve harm to persons (no further analysis)?", "Shall", fsa_12_s0_handling),
    CheckDef("13", "FSA", "Classification of Hazardous Events", "Has the probability of exposure of each operational situation been estimated and assigned to E0, E1, E2, E3 or E4 with rationale?", "Shall", fsa_13_exposure),
    CheckDef("14", "FSA", "Classification of Hazardous Events", "Did the estimating of the probability of exposure NOT take into account the number of vehicles equipped with the item?", "Shall", fsa_14_e_not_fleet),
    CheckDef("15", "FSA", "Classification of Hazardous Events", "Was class E0 assigned for situations that are extremely unusual or incredible and therefore not followed up?", "Shall", fsa_15_e0),
    CheckDef("16", "FSA", "Classification of Hazardous Events", "Has the controllability of each hazardous event been estimated and assigned to C0, C1, C2 or C3 with rationale?", "Shall", fsa_16_controllability),
    CheckDef("17", "FSA", "Classification of Hazardous Events", "For hazards addressing item unavailability that does not affect safe operation, are appropriate justifications or regulatory citations provided?", "Should", fsa_17_unavailability),
    CheckDef("18", "FSA", "Determination of ASIL and Safety Goals", "Was an ASIL determined for each hazardous event using S, E, and C?", "Shall", fsa_18_asil_determined),
    CheckDef("19", "FSA", "Determination of ASIL and Safety Goals", "Has it been determined that the chosen level of detail of operational situations does not lead to inappropriate lowering of ASIL?", "Should", fsa_19_situation_detail),
    CheckDef("20", "FSA", "Determination of ASIL and Safety Goals", "Was a safety goal determined for each hazardous event with ASIL≥A and were similar safety goals combined into one?", "Shall", fsa_20_safety_goals),
    CheckDef("21", "FSA", "Determination of ASIL and Safety Goals", "When similar safety goals were combined, was the highest ASIL assigned to the combined safety goal?", "Shall", fsa_21_combined_asil),
    CheckDef("22", "FSA", "Determination of ASIL and Safety Goals", "If a safety goal is achieved by transitioning to or maintaining safe state(s), were these safe state(s) specified?", "Shall", fsa_22_safe_states),
    CheckDef("23", "FSA", "Determination of ASIL and Safety Goals", "Were the safety goals with their attributes specified in accordance with ISO 26262-8:2011, Clause 6?", "Should", fsa_23_sg_attributes),

    # Verification Assessment
    CheckDef("24", "VA", "Verification Planning", "Does the Verification Plan ensure compliance and consistency with the FSC and preliminary architectural design assumptions?", "Shall", va_24_plan_compliance),
    CheckDef("25", "VA", "Verification Planning", "If applicable, was Safety Validation refined based on Technical Safety requirements?", "Should", va_25_validation_refined),
    CheckDef("26", "VA", "Verification Planning", "Does the Verification Plan address content, methods, pass/fail criteria, env, tools, anomalies, regression?", "Shall", va_26_plan_addresses),
    CheckDef("26a","VA", "Verification Planning", "Content of the work product(s) to be verified?", "Shall", va_26a),
    CheckDef("26b","VA", "Verification Planning", "Methods to be used (consistent with Safety Plan)?", "Shall", va_26b),
    CheckDef("26c","VA", "Verification Planning", "Pass/fail criteria?", "Shall", va_26c),
    CheckDef("26d","VA", "Verification Planning", "Verification environment (if applicable)?", "Shall", va_26d),
    CheckDef("26e","VA", "Verification Planning", "Tools used for verification (if applicable)?", "Shall", va_26e),
    CheckDef("26f","VA", "Verification Planning", "Actions to be taken when anomalies are detected?", "Shall", va_26f),
    CheckDef("26g","VA", "Verification Planning", "The regression strategy?", "Shall", va_26g),
    CheckDef("27", "VA", "Verification Planning", "Does verification planning consider method adequacy, complexity, prior experience, technology maturity?", "Should", va_27_planning),
    CheckDef("27a","VA", "Verification Planning", "Adequacy of the verification methods?", "Should", va_27a),
    CheckDef("27b","VA", "Verification Planning", "Complexity of the work product?", "Should", va_27b),
    CheckDef("27c","VA", "Verification Planning", "Prior experiences related to verification of the work product?", "Should", va_27c),
    CheckDef("27d","VA", "Verification Planning", "Maturity of technologies / risks associated with their use?", "Should", va_27d),
    CheckDef("28", "VA", "Verification Specification", "Are review/analysis checklists, simulation scenarios, or test cases specified for verification?", "Shall", va_28_methods),
    CheckDef("28a","VA", "Verification Specification", "Review of analysis checklists?", "Shall", va_28a),
    CheckDef("28b","VA", "Verification Specification", "Simulation scenarios?", "Shall", va_28b),
    CheckDef("28c","VA", "Verification Specification", "Test cases, data, and objects?", "Shall", va_28c),
    CheckDef("29", "VA", "Verification Specification", "If applicable, for testing does the specification of each test case include the listed elements?", "Shall", va_29_test_spec),
    CheckDef("29a","VA", "Verification Specification", "A unique identification?", "Shall", va_29a),
    CheckDef("29b","VA", "Verification Specification", "A reference to the version of the associated work product?", "Shall", va_29b),
    CheckDef("29c","VA", "Verification Specification", "The preconditions and configurations?", "Shall", va_29c),
    CheckDef("29d","VA", "Verification Specification", "If appropriate, the environmental conditions?", "Shall", va_29d),
    CheckDef("29e","VA", "Verification Specification", "The input data, their time sequence and values?", "Shall", va_29e),
    CheckDef("29f","VA", "Verification Specification", "The expected behavior including output data and tolerance behavior?", "Shall", va_29f),
    CheckDef("30", "VA", "Verification Specification", "Are test cases grouped by method with environment, dependencies, and resources specified per method?", "Shall", va_30_grouping),
    CheckDef("30a","VA", "Verification Specification", "The test environment?", "Shall", va_30a),
    CheckDef("30b","VA", "Verification Specification", "The logical and temporal dependencies?", "Shall", va_30b),
    CheckDef("30c","VA", "Verification Specification", "The resources?", "Shall", va_30c),
    CheckDef("31", "VA", "Verification Execution and Evaluation", "Was the verification executed as per the verification plan and specification?", "Shall", va_31_executed),
    CheckDef("32", "VA", "Verification Execution and Evaluation", "Does the Verification Report include the listed elements?", "Shall", va_32_report),
    CheckDef("32a","VA", "Verification Execution and Evaluation", "A unique identification of the verified work product?", "Shall", va_32a),
    CheckDef("32b","VA", "Verification Execution and Evaluation", "A reference to the verification plan and specification?", "Shall", va_32b),
    CheckDef("32c","VA", "Verification Execution and Evaluation", "Configuration of verification env / tools / calibration data?", "Shall", va_32c),
    CheckDef("32d","VA", "Verification Execution and Evaluation", "The level of compliance of the verification results with expected results?", "Shall", va_32d),
    CheckDef("32e","VA", "Verification Execution and Evaluation", "An unambiguous pass/fail statement (with rationale on failure)?", "Shall", va_32e),
    CheckDef("32f","VA", "Verification Execution and Evaluation", "The reasons why any verification step(s) were not executed?", "Shall", va_32f),
    CheckDef("33", "VA", "HARA-specific Verification", "Have the HARA-specific items been verified (see 33a–e)?", "Shall", va_33d_coverage),
    CheckDef("33a","VA", "HARA-specific Verification", "Completeness with regard to situations?", "Shall", va_33a_situations),
    CheckDef("33b","VA", "HARA-specific Verification", "Compliance with the item definition?", "Shall", va_33b_item_def),
    CheckDef("33c","VA", "HARA-specific Verification", "Consistency with related hazard analyses and risk assessments?", "Shall", va_33c_consistency),
    CheckDef("33d","VA", "HARA-specific Verification", "Completeness of the coverage of the hazardous events?", "Shall", va_33d_coverage),
    CheckDef("33e","VA", "HARA-specific Verification", "Consistency of the assigned ASILs with the corresponding hazardous events?", "Shall", va_33e_asil_consistency),
]
