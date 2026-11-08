# Calibration Data Exchange Agreement Methodology

## Overview

Calibration data exchange agreements define how OEM and Tier-1 suppliers manage calibration parameters across development and production. This workbook guides creation of audit-ready agreements covering ownership, baselines, change protocols, and acceptance criteria.

## Key Concepts

### Parameter Ownership
Every calibration parameter has a single owner:
- **OEM-owned**: OEM retains all change rights; Tier-1 integrates OEM-supplied values
- **Tier-1-owned**: Tier-1 develops and maintains; OEM reviews and approves
- **Shared**: Both parties have change rights; approval required from both

### Baseline References
Each parameter group has an approved baseline snapshot:
- **Baseline version**: Unique identifier (e.g., "BL_2024-05-01")
- **Baseline date**: When approved
- **Approved by**: Authority signature
- **Change history**: Trace all modifications against baseline

### Exchange Formats

#### DCM (ETAS Data Conservation)
- File extension: .dcm
- Use: INTA, CANape, ATI Vision
- Advantages: Standard, widely supported
- Limitations: Single variant per file

#### CDFX (Calibration Data Format eXchange)
- File extension: .cdfx
- Use: OEM-specific, often proprietary
- Advantages: Flexible, can include variants
- Limitations: Custom parsing required

#### PaCo (Parameter Control)
- File extension: .paco
- Use: Vector tools
- Advantages: Detailed metadata, version control
- Limitations: Vector-specific tooling

### Change Protocol
Process for baseline modifications:
1. **Initiator** identifies parameter change need
2. **Owner** verifies change aligns with requirements
3. **Change description** documents what/why
4. **Approval chain** routes through both parties
5. **Baseline update** new version tagged and released
6. **Notification** all stakeholders informed

### Acceptance Criteria
Measurable conditions for deliverable acceptance:
- All parameters within physical ranges
- Baseline traceability documented
- Format compatibility verified
- Change history complete
- Approvals collected
- Unit consistency verified

## Workbook Structure

1. **Title** — Agreement identification, parties, scope
2. **Document Control** — Version history, approvals
3. **Parties** — OEM, Tier-1, Tier-2 identification
4. **Parameter Ownership Matrix** — Per parameter: owner, rights, baseline
5. **Baseline References** — Approved baseline snapshot for each group
6. **Exchange Format Specification** — DCM, CDFX, PaCo rules
7. **Change Protocol** — Process for modifications, approvals, notification
8. **Version Control** — Versioning scheme, baseline tags, retention
9. **Acceptance Criteria** — Measurable acceptance conditions
10. **Signoff Block** — OEM and Tier-1 authorization
11. **References** — Standard cross-references

## Best Practices

### Ownership Clarity
- Assign every parameter to exactly one owner
- Document change rights (OEM-only, Tier-1-only, shared)
- Define approval chain for each change type

### Baseline Management
- Baseline = approved, controlled version snapshot
- Baseline version: date-tagged (BL_YYYY-MM-DD)
- Baseline retained for 12+ months
- Every production build references baseline

### Change Protocol
- Approval required from parameter owner AND other party
- Change reason documented (requirement, bug fix, optimization)
- Change notification within 24 hours
- Baseline rebase schedule (daily, weekly, per-milestone)

### Exchange Format
- Choose format per supplier capability (DCM if all tools support)
- Document format compatibility matrix
- Validate format before production handoff
- Archive exchange format definitions with baselines

### Documentation
- Ownership matrix drives all other discussions
- Baseline references traceable to approved snapshots
- Change history complete and auditable
- Signoffs collected and retained
