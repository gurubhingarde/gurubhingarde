# ODX Checklist Review Methodology

## Review Scope

An ODX checklist review validates the completeness, consistency, and correctness of an ODX authoring workbook against ISO 22901-1 and automotive diagnostic engineering best practices.

## Check Categories

### Variant & Layer Review (8 checks: V1-V8)
- Base variant definition: unique ECU IDs, interface specification
- Derived variant hierarchy: parent-child relationships, specialization rules
- Inherit-From relationships: acyclic chains, property override handling
- ODX layer coverage: all four layers (D, C, V, FD) represented and linked

### PDU & Service Review (12 checks: P1-P12)
- PDU library completeness: all referenced PDUs defined
- Service-to-PDU mapping: request/response pairing
- Signal definitions: units, conversions, ranges
- Data object semantics: physical meaning, constraints
- DTC enumeration: severity, safety relevance
- Parameter validation: input/output ranges

### Communication & Flash Review (10 checks: C1-C10)
- Bus speed and protocol: CAN/LIN/Ethernet specification
- Timing parameters: timeouts, inter-frame delays, flow control
- Flash memory layout: segment allocation (Boot, App, Calib, NV)
- Programming algorithm: erase/write procedures
- CRC/checksum: algorithm, polynomial, protected regions
- Security procedures: authentication, unlock timing

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
- Blocks approval of the ODX.

**NA (Not Applicable)**: Requirement not relevant to this ODX.
- Feature not used or explicitly out of scope.

## Confidence Levels

**High**: Objectively verifiable through automated checks.
- Example: "Every base variant has an ECU ID" (machine-verifiable).

**Medium**: Mostly verifiable with some engineering judgment.
- Example: "Timeout values are reasonable" (some judgment on 'reasonable').

**Low**: Requires expert review or interpretation.
- Example: "Flash programming sequence is efficient" (subjective).

## Obligation Levels

**MUST**: Mandatory requirement per ISO 22901-1 or functional safety (ASIL).
- Non-compliance blocks approval.

**SHOULD**: Strongly recommended for best practice.
- Non-compliance noted as a gap but may not block approval.

**MAY**: Optional / nice-to-have.
- Non-compliance is informational only.

## Workflow

1. **Probe the ODX**: Extract content from the workbook (best-effort).
2. **Run automated checks**: ~15 checks are fully automated (high confidence).
3. **Flag gaps**: ~10 checks require judgment or expert review (medium/low confidence).
4. **Generate findings**: Produce a checklist xlsx with results + visual dashboard.
5. **Review summary**: Show KPI tiles, pass/fail distribution, and key findings.
6. **Iterate**: User addresses findings and re-runs the check.

## Key Compliance Points

For an ODX to be "audit-ready":
- [ ] All base variants have unique ECU IDs
- [ ] All derived variants inherit from exactly one base variant
- [ ] No circular inheritance chains
- [ ] Every service has both request and response PDU
- [ ] All PDUs referenced in services are defined
- [ ] All communication channels are specified (bus speed, timing)
- [ ] Flash memory segments are defined
- [ ] CRC algorithm and protected regions are specified
- [ ] Safety-relevant services are marked
- [ ] DTC enumeration is complete

## Integration with ODX Builder

The ODX Checklist Reviewer pairs naturally with `odx-builder`:
- `odx-builder` produces the initial ODX workbook.
- `odx-checklist-reviewer` validates that workbook.
- Findings feed back into the next revision of the ODX.

Both tools use common references (methodology.md, odx_layers.md) for consistency.
