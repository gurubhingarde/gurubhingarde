# DEM Config Checklist Review Methodology

## Review Scope

A DEM configuration checklist review validates the completeness, consistency, and correctness of a DEM (Diagnostic Event Manager) configuration workbook against AUTOSAR SWS_Dem and automotive functional safety best practices.

## Check Categories

### Event & Debounce Review (10 checks: E1-E10)
- DTC-to-event mapping completeness
- Event inventory and uniqueness
- Debounce threshold ranges (pre-passed, pre-confirmed, confirmed, healed)
- Safety-critical event marking (ASIL linkage)
- Debounce consistency across functional domains

### Memory & Storage Review (10 checks: M1-M10)
- Primary memory allocation vs. event count
- Secondary memory (aging data) allocation
- NvM block mapping (1-to-1 event-to-block)
- Memory utilization ratio (goal: <90% of ECU budget)
- Memory growth headroom for future events
- Redundancy for critical events

### Snapshot & OBD Review (8 checks: S1-S8)
- Snapshot record class definition (per confirmed event)
- Snapshot data adequacy (4-8 elements, 8-32 bytes)
- Extended Data Record (EDR) configuration
- OBD freeze frame enablement and configuration
- OBD frame 0 mandatory PIDs
- Safety-critical event snapshot coverage

## Rating Scale

**FC (Fully Compliant)**: Requirement is met; no issues detected.
- All checks pass automated verification or expert review.
- No corrective actions needed.

**LC (Largely Compliant)**: Minor issues that don't block compliance.
- Requirement mostly met with small gaps.
- Recommended refinements but not blocking.

**PC (Partially Compliant)**: Significant gaps that require correction.
- Requirement partially met or incomplete.
- Must be addressed before baseline approval.

**NC (Non-Compliant)**: Requirement not met.
- Critical gaps; must be corrected.
- Blocks approval of the DEM configuration.

**NA (Not Applicable)**: Requirement not relevant to this configuration.
- Feature not used or explicitly out of scope.

## Confidence Levels

**High**: Objectively verifiable through automated checks.
- Example: "Every event has a unique ID" (machine-verifiable).

**Medium**: Mostly verifiable with some engineering judgment.
- Example: "Debounce thresholds are reasonable" (some judgment on ranges).

**Low**: Requires expert review or interpretation.
- Example: "Snapshot data is adequate for diagnostics" (subjective).

## Obligation Levels

**MUST**: Mandatory requirement per AUTOSAR SWS_Dem or functional safety.
- Non-compliance blocks approval.

**SHOULD**: Strongly recommended for best practice.
- Non-compliance noted as a gap but may not block approval.

**MAY**: Optional / nice-to-have.
- Non-compliance is informational only.

## Workflow

1. **Probe the DEM config**: Extract content from the workbook (best-effort).
2. **Run automated checks**: ~12 checks are fully automated (high confidence).
3. **Flag gaps**: ~8 checks require judgment or expert review (medium/low confidence).
4. **Generate findings**: Produce a checklist xlsx with results + visual dashboard.
5. **Review summary**: Show KPI tiles, pass/fail distribution, and key findings.
6. **Iterate**: User addresses findings and re-runs the check.

## Key Compliance Points

For a DEM configuration to be audit-ready:
- [ ] Every DTC has a mapped DEM Event (1-to-1 mapping)
- [ ] All events have valid debounce thresholds (within recommended ranges)
- [ ] Primary memory allocation is adequate for event count
- [ ] Secondary memory allocation is 50% of primary
- [ ] Every event is assigned to a unique NvM block
- [ ] Safety-critical events have snapshots defined
- [ ] OBD freeze frame enabled for emissions-related events
- [ ] Memory utilization is <90% of ECU budget
- [ ] 15-20% memory headroom reserved for future growth
- [ ] Debounce strategy is consistent within functional domains

## Integration with DTC Catalog and ODX

The DEM Configuration references an external DTC catalog (often from ODX). The workflow is:

1. ODX Builder produces ODX with DTC definitions.
2. DEM Config Builder consumes the DTC list and adds runtime behavior.
3. DEM Config Checklist Reviewer validates consistency and completeness.
4. Results feed back to ECU supplier for production integration.

## AUTOSAR SWS_Dem Compliance

The checklist ensures compliance with:
- **SWS_Dem.EB.DEBOUNCE**: Debounce mechanism and thresholds
- **SWS_Dem.EB.EVENTMEMORYDESTINATION**: Primary/secondary memory routing
- **SWS_Dem.EB.SNAPSHOTRECORDCLASS**: Snapshot record structure
- **SWS_Dem.EB.EXTENDEDDATARECORD**: EDR configuration
- **SWS_Dem.EB.OBDFREEZEFRAMECAPTURE**: OBD freeze frame trigger and storage
- **SWS_Dem.EB.OPERATIONCYCLETYPE**: Cycle definition for aging
- **SWS_Dem.EB.NVDATABLOCK**: NvM block assignment

## Production Readiness Checklist

- [ ] DEM config matches DTC catalog version
- [ ] All debounce thresholds validated by system engineering
- [ ] Memory footprint verified against ECU RAM budget
- [ ] NvM block IDs do not conflict with other modules
- [ ] OBD freeze frame configuration matches regulatory requirements
- [ ] Aging strategy aligns with vehicle product requirements
- [ ] Config tested in HIL (Hardware-in-the-Loop)
- [ ] Config tested in vehicle (MIL/SIL)
- [ ] Snapshot/EDR data matches diagnostic tool expectations
- [ ] Safety-critical events properly marked per ASIL
