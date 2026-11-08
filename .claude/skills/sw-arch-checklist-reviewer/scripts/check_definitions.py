"""
Canonical SW Architecture checklist definitions and verification logic.

Each check has:
- id: row id (CR/SWAA/VA tabs)
- tab: which output tab
- section: section header
- requirement: the requirement text
- obligation: "Shall" or "Should" (or "")
- verify: callable(probed: ProbedSwArch) -> CheckResult
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sw_arch_probe import ProbedSwArch


@dataclass
class CheckResult:
    rating: str = ""  # FC / LC / PC / NO / NA / "" (pending)
    finding: str = ""
    page_section: str = ""
    recommended_action: str = ""
    confidence: str = ""  # High / Medium / Low / "" for binary CR


@dataclass
class CheckDef:
    id: str = ""
    tab: str = ""
    section: str = ""
    requirement: str = ""
    obligation: str = ""  # Shall / Should / ""
    verify: Callable[[ProbedSwArch], CheckResult] = None


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
# Confirmation Review (generic doc-quality, 14 checks)
# ---------------------------------------------------------------------------

def cr_01_structured(p: ProbedSwArch) -> CheckResult:
    if len(p.sheet_names) >= 11:
        return CheckResult(
            rating="FC",
            finding=f"Document is structured into {len(p.sheet_names)} tabs with distinct sections.",
            page_section="All tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding=f"Document has only {len(p.sheet_names)} tabs; expect 11+ for SW arch.",
        recommended_action="Verify all required tabs are present.",
        confidence="Medium",
    )


def cr_02_title_scope(p: ProbedSwArch) -> CheckResult:
    if p.title:
        return draft(
            f"Title is: '{p.title}'. Reviewer to confirm it covers SW architecture scope.",
            page_section="Title page row 2",
        )
    return CheckResult(
        rating="NO",
        finding="No title detected on the Title page.",
        recommended_action="Add a clear document title reflecting SW architecture scope.",
        confidence="High",
    )


def cr_03_author_approver(p: ProbedSwArch) -> CheckResult:
    if p.author and p.approver:
        return CheckResult(
            rating="FC",
            finding=f"Author='{p.author}', Approver='{p.approver}' both populated.",
            page_section="Title page",
            confidence="High",
        )
    missing = []
    if not p.author: missing.append("Author")
    if not p.approver: missing.append("Approver")
    return CheckResult(
        rating="NO",
        finding=f"Missing on Title page: {', '.join(missing)}.",
        recommended_action=f"Populate {', '.join(missing)} field(s).",
        confidence="High",
    )


def cr_04_revision(p: ProbedSwArch) -> CheckResult:
    if p.revision:
        return CheckResult(
            rating="FC",
            finding=f"Revision documented as '{p.revision}'.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="No revision detected on Title page.",
        recommended_action="Add revision number/identifier.",
        confidence="High",
    )


def cr_05_status(p: ProbedSwArch) -> CheckResult:
    if p.status:
        return CheckResult(
            rating="FC",
            finding=f"Document status: '{p.status}'.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Document status not detected on Title page.",
        recommended_action="Add status field (Draft / In Review / Final).",
        confidence="High",
    )


def cr_06_docid_project(p: ProbedSwArch) -> CheckResult:
    missing = []
    if not p.doc_id: missing.append("Document ID")
    if not p.project: missing.append("Project")
    if not missing:
        return CheckResult(
            rating="FC",
            finding=f"Doc ID='{p.doc_id}', Project='{p.project}' both populated.",
            page_section="Title page",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"Missing on Title page: {', '.join(missing)}.",
        recommended_action=f"Populate {', '.join(missing)} field(s).",
        confidence="High",
    )


def cr_07_document_control(p: ProbedSwArch) -> CheckResult:
    if "01_Document_Control" in p.sheet_names:
        return draft(
            "Document Control tab present. Reviewer to verify change history and sign-off records.",
            page_section="01_Document_Control",
        )
    return CheckResult(
        rating="PC",
        finding="Document Control tab not found.",
        recommended_action="Add 01_Document_Control tab with change history.",
        confidence="High",
    )


def cr_08_table_of_contents(p: ProbedSwArch) -> CheckResult:
    return draft(
        f"Document has {len(p.sheet_names)} tabs. Reviewer to verify TOC is complete and current.",
        page_section="02_TSC_Architecture_Echo or General Info",
    )


def cr_09_references(p: ProbedSwArch) -> CheckResult:
    return draft(
        "Reviewer to verify References tab (11_References) contains all normative and informative documents.",
        page_section="11_References",
    )


def cr_10_glossary(p: ProbedSwArch) -> CheckResult:
    return draft(
        "Reviewer to verify glossary of SW architecture terms is available or defined in document scope.",
        page_section="Document Control / General Info",
    )


def cr_11_formatting_consistency(p: ProbedSwArch) -> CheckResult:
    return draft(
        "Reviewer to assess formatting consistency (fonts, colors, numbering, table styles).",
        page_section="All tabs",
    )


def cr_12_cross_references(p: ProbedSwArch) -> CheckResult:
    tsc_refs = [s for s in p.sheet_names if "tsc" in s.lower()]
    if tsc_refs:
        return CheckResult(
            rating="FC",
            finding=f"TSC references detected in {len(tsc_refs)} sheet(s): {', '.join(tsc_refs[:3])}.",
            page_section="Multiple tabs",
            confidence="Medium",
        )
    return CheckResult(
        rating="PC",
        finding="Limited TSC cross-references detected.",
        recommended_action="Verify TSC document integration in arch components.",
        confidence="Medium",
    )


def cr_13_signature_authority(p: ProbedSwArch) -> CheckResult:
    return draft(
        f"Author: '{p.author}', Approver: '{p.approver}'. Reviewer to verify independence per ISO 26262-2.",
        page_section="Title page",
    )


def cr_14_compliance_assertions(p: ProbedSwArch) -> CheckResult:
    return draft(
        "Reviewer to verify document claims compliance to ISO 26262-6 §7 (SW Architecture).",
        page_section="Title page / Document Control",
    )


# ---------------------------------------------------------------------------
# SW Architecture Assessment (substantive checks per ISO 26262-6 §7, 12 checks)
# ---------------------------------------------------------------------------

def swaa_01_component_catalog(p: ProbedSwArch) -> CheckResult:
    if len(p.sw_components) > 0:
        return CheckResult(
            rating="FC",
            finding=f"SW Component Catalog populated with {len(p.sw_components)} components.",
            page_section="03_SW_Component_Catalog",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="SW Component Catalog is empty or missing.",
        recommended_action="Populate SW Component Catalog with all software components.",
        confidence="High",
    )


def swaa_02_asil_assignment(p: ProbedSwArch) -> CheckResult:
    without_asil = [c for c in p.sw_components if not c.asil]
    if len(without_asil) == 0:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_components)} SW components have ASIL assigned.",
            page_section="03_SW_Component_Catalog",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding=f"{len(without_asil)} SW component(s) missing ASIL: {', '.join([c.swc_id for c in without_asil[:5]])}.",
        recommended_action="Assign ASIL (QM / ASIL A/B/C/D) to all safety-relevant components.",
        confidence="High",
    )


def swaa_03_partition_mapping(p: ProbedSwArch) -> CheckResult:
    without_partition = [c for c in p.sw_components if not c.partition_id]
    if len(without_partition) == 0:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.sw_components)} SW components mapped to partitions.",
            page_section="03_SW_Component_Catalog",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(without_partition)} component(s) not mapped to partition(s).",
        recommended_action="Map all SW components to logical partitions.",
        confidence="High",
    )


def swaa_04_rtos_config(p: ProbedSwArch) -> CheckResult:
    if p.rtos_config.rtos_name and p.rtos_config.rtos_version:
        fields = [p.rtos_config.rtos_name, p.rtos_config.rtos_version]
        if p.rtos_config.scheduling_policy:
            fields.append(p.rtos_config.scheduling_policy)
        return CheckResult(
            rating="FC",
            finding=f"RTOS/OS documented: {', '.join(fields)}.",
            page_section="04_RTOS_OS_Configuration",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="RTOS/OS configuration incomplete or missing.",
        recommended_action="Document RTOS/OS name, version, scheduling policy, and ASIL support.",
        confidence="High",
    )


def swaa_05_task_scheduling(p: ProbedSwArch) -> CheckResult:
    if len(p.task_scheduling) > 0:
        without_wcet = [t for t in p.task_scheduling if not t.wcet_ms]
        if len(without_wcet) == 0:
            return CheckResult(
                rating="FC",
                finding=f"Task scheduling map populated; {len(p.task_scheduling)} task(s) with WCET defined.",
                page_section="05_Task_Scheduling_Map",
                confidence="High",
            )
        return CheckResult(
            rating="PC",
            finding=f"{len(without_wcet)} task(s) missing WCET specification.",
            recommended_action="Define WCET (Worst-Case Execution Time) for all tasks.",
            confidence="High",
        )
    return CheckResult(
        rating="NO",
        finding="Task Scheduling Map is empty or missing.",
        recommended_action="Populate task scheduling map with period, priority, WCET.",
        confidence="High",
    )


def swaa_06_schedulability(p: ProbedSwArch) -> CheckResult:
    if len(p.task_scheduling) == 0:
        return na("No task scheduling data; schedulability check not applicable.")

    # Attempt simple rate-monotonic check: sum(WCET/Period) per priority level < 1.0
    errors = []
    for task in p.task_scheduling:
        if not task.wcet_ms or not task.period_ms:
            errors.append(f"{task.task_id} missing WCET or Period")

    if errors:
        return CheckResult(
            rating="PC",
            finding=f"Schedulability check incomplete: {len(errors)} task(s) missing timing data.",
            recommended_action="Complete WCET and Period for all tasks; run schedulability analysis.",
            confidence="Medium",
        )

    return draft(
        f"Reviewer to verify rate-monotonic schedulability: sum(WCET/Period) < 1.0 per priority. {len(p.task_scheduling)} task(s) defined.",
        page_section="05_Task_Scheduling_Map",
    )


def swaa_07_mpu_partitioning(p: ProbedSwArch) -> CheckResult:
    asil_components = [c for c in p.sw_components if c.asil and c.asil != "QM"]
    if len(asil_components) == 0:
        return na("No ASIL-relevant SW components; MPU partitioning not required.")

    if len(p.mpu_regions) > 0:
        return CheckResult(
            rating="FC",
            finding=f"MPU Memory Partitioning documented with {len(p.mpu_regions)} region(s).",
            page_section="06_MPU_Memory_Partitioning",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"MPU partitioning incomplete: {len(asil_components)} ASIL component(s) but only {len(p.mpu_regions)} MPU region(s).",
        recommended_action="Define MPU regions for all ASIL-relevant software partitions.",
        confidence="High",
    )


def swaa_08_interfaces(p: ProbedSwArch) -> CheckResult:
    without_protection = [i for i in p.interfaces if not i.integrity_protection]
    if len(p.interfaces) == 0:
        return CheckResult(
            rating="PC",
            finding="Inter-Component Interfaces tab is empty.",
            recommended_action="Document all inter-component communication with interface type and integrity protection.",
            confidence="High",
        )
    if len(without_protection) == 0:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.interfaces)} inter-component interface(s) have integrity protection specified.",
            page_section="07_Inter_Component_Interfaces",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(without_protection)} interface(s) missing integrity protection spec.",
        recommended_action="Specify integrity protection (checksum, CRC, etc.) for all interfaces.",
        confidence="High",
    )


def swaa_09_safety_mechanisms(p: ProbedSwArch) -> CheckResult:
    asil_components = [c for c in p.sw_components if c.asil and c.asil != "QM"]
    if len(asil_components) == 0:
        return na("No ASIL-relevant components; safety mechanism allocation not required.")

    if len(p.safety_mechanism_allocs) > 0:
        return CheckResult(
            rating="FC",
            finding=f"Safety mechanism allocation documented for {len(p.safety_mechanism_allocs)} mechanism(s).",
            page_section="08_Safety_Mechanism_Allocation",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding=f"{len(asil_components)} ASIL component(s) but no safety mechanisms allocated.",
        recommended_action="Allocate safety mechanisms (fault detection, recovery, logging) per ASIL.",
        confidence="High",
    )


def swaa_10_misra_compliance(p: ProbedSwArch) -> CheckResult:
    if len(p.misra_targets) > 0:
        return CheckResult(
            rating="FC",
            finding=f"MISRA C:2012 compliance targets specified for {len(p.misra_targets)} target(s).",
            page_section="09_MISRA_Compliance_Targets",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="MISRA Compliance Targets tab is empty.",
        recommended_action="Define MISRA C:2012 compliance targets per SW component or global policy.",
        confidence="High",
    )


def swaa_11_initialization(p: ProbedSwArch) -> CheckResult:
    if p.init_sequence_rows > 0:
        return CheckResult(
            rating="FC",
            finding=f"Initialization sequence documented with {p.init_sequence_rows} step(s).",
            page_section="10_Initialization_Sequence",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Initialization Sequence tab is empty or missing.",
        recommended_action="Document software initialization sequence and start-up requirements.",
        confidence="High",
    )


def swaa_12_tsc_references(p: ProbedSwArch) -> CheckResult:
    if len(p.tsc_reference_tabs) > 0:
        return CheckResult(
            rating="FC",
            finding=f"TSC references integrated: {len(p.tsc_reference_tabs)} TSC tab(s) found.",
            page_section="02_TSC_Architecture_Echo",
            confidence="High",
        )
    return CheckResult(
        rating="PC",
        finding="Limited or no TSC (Technical Safety Concept) references.",
        recommended_action="Integrate TSC document reference and traceability matrix.",
        confidence="Medium",
    )


# ---------------------------------------------------------------------------
# Verification Assessment (generic external + SW-arch-specific, 5 checks)
# ---------------------------------------------------------------------------

def va_01_swc_coverage(p: ProbedSwArch) -> CheckResult:
    return draft(
        f"Reviewer to verify all {len(p.sw_components)} SW components have corresponding SW-TSR coverage in Verification Plan/Report.",
        page_section="03_SW_Component_Catalog + Verification artifacts",
    )


def va_02_mpu_isolation(p: ProbedSwArch) -> CheckResult:
    asil_components = [c for c in p.sw_components if c.asil and c.asil != "QM"]
    if len(asil_components) == 0:
        return na("No ASIL-relevant components; MPU isolation testing not required.")
    return draft(
        f"Reviewer to verify MPU isolation testing for {len(asil_components)} ASIL component(s) in Verification Plan.",
        page_section="06_MPU_Memory_Partitioning + Verification Report",
    )


def va_03_scheduling_tests(p: ProbedSwArch) -> CheckResult:
    return draft(
        f"Reviewer to verify task scheduling and priority inversion testing documented for {len(p.task_scheduling)} task(s).",
        page_section="05_Task_Scheduling_Map + Verification Report",
    )


def va_04_interface_testing(p: ProbedSwArch) -> CheckResult:
    return draft(
        f"Reviewer to verify all {len(p.interfaces)} inter-component interface(s) have integration tests in Verification Plan.",
        page_section="07_Inter_Component_Interfaces + Verification Report",
    )


def va_05_misra_verification(p: ProbedSwArch) -> CheckResult:
    return draft(
        "Reviewer to verify MISRA C:2012 compliance verification method (static analysis, manual review, or waiver) in Verification Plan.",
        page_section="09_MISRA_Compliance_Targets + Verification Report",
    )


# ---------------------------------------------------------------------------
# Canonical checklist registry
# ---------------------------------------------------------------------------

CHECKS: list[CheckDef] = [
    # Confirmation Review (14 checks)
    CheckDef(id="CR-01", tab="Confirmation Review", section="Document Structure",
             requirement="SW Architecture document shall be structured into distinct sections",
             obligation="Shall", verify=cr_01_structured),
    CheckDef(id="CR-02", tab="Confirmation Review", section="Title & Scope",
             requirement="Document title shall identify the SW Architecture scope",
             obligation="Shall", verify=cr_02_title_scope),
    CheckDef(id="CR-03", tab="Confirmation Review", section="Authorship",
             requirement="Author and Approver shall be identified on Title page",
             obligation="Shall", verify=cr_03_author_approver),
    CheckDef(id="CR-04", tab="Confirmation Review", section="Revision",
             requirement="Document revision shall be tracked",
             obligation="Shall", verify=cr_04_revision),
    CheckDef(id="CR-05", tab="Confirmation Review", section="Status",
             requirement="Document status shall be indicated",
             obligation="Should", verify=cr_05_status),
    CheckDef(id="CR-06", tab="Confirmation Review", section="Identification",
             requirement="Document ID and Project shall be specified",
             obligation="Shall", verify=cr_06_docid_project),
    CheckDef(id="CR-07", tab="Confirmation Review", section="Document Control",
             requirement="Change history shall be maintained",
             obligation="Shall", verify=cr_07_document_control),
    CheckDef(id="CR-08", tab="Confirmation Review", section="Navigation",
             requirement="Table of contents shall be provided or tabs clearly labeled",
             obligation="Should", verify=cr_08_table_of_contents),
    CheckDef(id="CR-09", tab="Confirmation Review", section="References",
             requirement="References section shall list normative and informative documents",
             obligation="Should", verify=cr_09_references),
    CheckDef(id="CR-10", tab="Confirmation Review", section="Terminology",
             requirement="Glossary or terminology definitions shall be available",
             obligation="Should", verify=cr_10_glossary),
    CheckDef(id="CR-11", tab="Confirmation Review", section="Consistency",
             requirement="Formatting and presentation shall be consistent throughout",
             obligation="Should", verify=cr_11_formatting_consistency),
    CheckDef(id="CR-12", tab="Confirmation Review", section="Traceability",
             requirement="Cross-references to TSC shall be present where applicable",
             obligation="Should", verify=cr_12_cross_references),
    CheckDef(id="CR-13", tab="Confirmation Review", section="Independence",
             requirement="Author and Approver shall be independent per ISO 26262-2",
             obligation="Shall", verify=cr_13_signature_authority),
    CheckDef(id="CR-14", tab="Confirmation Review", section="Compliance",
             requirement="Document shall assert compliance to ISO 26262-6 Part 7",
             obligation="Shall", verify=cr_14_compliance_assertions),

    # SW Architecture Assessment (12 checks)
    CheckDef(id="SWAA-01", tab="SW Architecture Assessment", section="Component Catalog",
             requirement="SW Component Catalog shall be populated with all SW components",
             obligation="Shall", verify=swaa_01_component_catalog),
    CheckDef(id="SWAA-02", tab="SW Architecture Assessment", section="ASIL Assignment",
             requirement="Each SW component shall have ASIL assigned",
             obligation="Shall", verify=swaa_02_asil_assignment),
    CheckDef(id="SWAA-03", tab="SW Architecture Assessment", section="Partition Mapping",
             requirement="Each SW component shall be mapped to a partition or execution context",
             obligation="Shall", verify=swaa_03_partition_mapping),
    CheckDef(id="SWAA-04", tab="SW Architecture Assessment", section="RTOS/OS Config",
             requirement="RTOS/OS name, version, scheduling policy, and ASIL support shall be documented",
             obligation="Shall", verify=swaa_04_rtos_config),
    CheckDef(id="SWAA-05", tab="SW Architecture Assessment", section="Task Scheduling",
             requirement="Task scheduling map shall define period, priority, and WCET for each task",
             obligation="Shall", verify=swaa_05_task_scheduling),
    CheckDef(id="SWAA-06", tab="SW Architecture Assessment", section="Schedulability",
             requirement="Schedulability analysis shall confirm sum(WCET/Period) < 1.0 per priority",
             obligation="Shall", verify=swaa_06_schedulability),
    CheckDef(id="SWAA-07", tab="SW Architecture Assessment", section="MPU Partitioning",
             requirement="MPU memory partitioning shall be documented for ASIL-relevant components",
             obligation="Shall", verify=swaa_07_mpu_partitioning),
    CheckDef(id="SWAA-08", tab="SW Architecture Assessment", section="Inter-Component Interfaces",
             requirement="All inter-component interfaces shall specify type and integrity protection",
             obligation="Shall", verify=swaa_08_interfaces),
    CheckDef(id="SWAA-09", tab="SW Architecture Assessment", section="Safety Mechanisms",
             requirement="Safety mechanism allocation shall be documented per ASIL",
             obligation="Shall", verify=swaa_09_safety_mechanisms),
    CheckDef(id="SWAA-10", tab="SW Architecture Assessment", section="MISRA Compliance",
             requirement="MISRA C:2012 compliance targets shall be specified",
             obligation="Shall", verify=swaa_10_misra_compliance),
    CheckDef(id="SWAA-11", tab="SW Architecture Assessment", section="Initialization",
             requirement="Initialization sequence shall be documented",
             obligation="Shall", verify=swaa_11_initialization),
    CheckDef(id="SWAA-12", tab="SW Architecture Assessment", section="TSC Integration",
             requirement="Technical Safety Concept references shall be integrated",
             obligation="Should", verify=swaa_12_tsc_references),

    # Verification Assessment (5 checks)
    CheckDef(id="VA-01", tab="Verification Assessment", section="SW Component Coverage",
             requirement="Verification Plan shall cover all SW components with SW-TSR traceability",
             obligation="Shall", verify=va_01_swc_coverage),
    CheckDef(id="VA-02", tab="Verification Assessment", section="MPU Isolation Testing",
             requirement="MPU isolation shall be verified for all ASIL-relevant partitions",
             obligation="Shall", verify=va_02_mpu_isolation),
    CheckDef(id="VA-03", tab="Verification Assessment", section="Scheduling Verification",
             requirement="Task scheduling and priority inversion handling shall be tested",
             obligation="Shall", verify=va_03_scheduling_tests),
    CheckDef(id="VA-04", tab="Verification Assessment", section="Interface Verification",
             requirement="All inter-component interfaces shall have integration test coverage",
             obligation="Shall", verify=va_04_interface_testing),
    CheckDef(id="VA-05", tab="Verification Assessment", section="MISRA Verification",
             requirement="MISRA C:2012 compliance shall be verified or waived per component",
             obligation="Shall", verify=va_05_misra_verification),
]
