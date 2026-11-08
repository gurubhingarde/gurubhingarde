# Calibration Data Exchange Checks (25 total)

## Agreement Structure (11)

### AGR.01 Title & Scope
Clear title and scope present. MUST.
- Title field populated
- Scope clearly defines parameters and exclusions
- Agreement boundaries unambiguous

### AGR.02 Authorship
Author/initiator documented. SHOULD.
- Author name recorded
- Initiating organization clear

### AGR.03 Versioning
Revision number recorded. MUST.
- Revision field populated
- Version identifier unique

### AGR.04 Parties
OEM and Tier-1 identified. MUST.
- OEM name and contact documented
- Tier-1 name and contact documented
- Tier-2 roles (if applicable) defined

### AGR.05 Ownership
Parameter ownership matrix complete. MUST.
- Every parameter assigned to owner
- Change rights documented (OEM-only, Tier-1-only, shared)
- Conflict resolution process defined

### AGR.06 Baselines
Baseline references documented. MUST.
- Baseline versions recorded
- Baseline dates documented
- Approved baseline snapshots traceable

### AGR.07 Document Control
Change log present. SHOULD.
- Revision history recorded
- Change dates and authors documented
- Approvals logged

### AGR.08 Change Protocol
Change approval process defined. MUST.
- Approval chain specified (who signs off)
- Notification timeline defined
- Baseline update frequency specified

### AGR.09 Roles
Roles and responsibilities clear. SHOULD.
- OEM role in calibration management specified
- Tier-1 role in calibration management specified
- Interface and handoff responsibilities clear

### AGR.10 Scope Clarity
Agreement scope clearly bounded. MUST.
- Parameters covered explicitly listed or bounded
- Exclusions documented (if any)
- Version applicability (Euro5, EPA, etc.) specified

### AGR.11 Functional Safety
Safety requirements documented if applicable. SHOULD.
- Safety-critical parameters flagged (if ISO 26262 applies)
- Cross-reference to safety plan
- Change impact on safety assessed

## Exchange & Acceptance (9)

### EXCH.01 Exchange Formats
Exchange formats specified. MUST.
- DCM, CDFX, PaCo or other format chosen
- Justification for format selection
- Tool compatibility documented

### EXCH.02 Version Control
Version control scheme defined. MUST.
- Versioning format specified (MAJOR.MINOR, date-tag, etc.)
- Baseline tagging convention (BL_YYYY-MM-DD, etc.)
- Branch/variant management (if applicable)

### EXCH.03 Acceptance Criteria
Acceptance criteria measurable and complete. MUST.
- All values within physical ranges
- Axis monotonicity verified
- Map dimensions match axes
- Unit consistency checked
- No NaN/Inf values
- Baseline traceability documented

### EXCH.04 Unit Consistency
Unit consistency rules documented. MUST.
- All parameters use physical (engineering) units
- Unit definitions match A2L
- Conversion factors documented

### EXCH.05 Baseline Snapshot
Baseline snapshots immutable and traceable. MUST.
- Baseline = approved, controlled version
- Baseline dates and approvals recorded
- Previous baselines retained 12+ months
- Rollback capability maintained

### EXCH.06 Metadata Retention
Data retention policy defined. SHOULD.
- Baseline history retention period (minimum 12 months)
- Change log retention period
- Archive location documented

### EXCH.07 File Validation
File validation and checksums defined. SHOULD.
- Checksum or hash algorithm specified
- Format validation rules documented
- Corruption detection method

### EXCH.08 Multi-Variant
Multi-variant support defined if applicable. SHOULD.
- Variant identification method (Euro5, EPA, etc.)
- Variant management process
- Cross-variant impact analysis

### EXCH.09 Tool Compatibility
Tool compatibility matrix documented. SHOULD.
- INCA, CANape, ATI Vision compatibility matrix
- Format-to-tool mapping
- Interoperability testing requirements

## Signoff & Authority (5)

### SIGN.01 OEM Signoff
OEM authorization signatures collected. MUST.
- OEM Calibration Lead signature and date
- OEM Manager signature and date
- Both signoffs present and valid

### SIGN.02 Tier-1 Signoff
Tier-1 authorization signatures collected. MUST.
- Tier-1 Calibration Lead signature and date
- Tier-1 Manager signature and date
- Both signoffs present and valid

### SIGN.03 Approval Dates
Approval dates recorded for all signoffs. MUST.
- Date field populated for every signature
- Dates chronological and reasonable

### SIGN.04 Dispute Resolution
Dispute resolution procedure documented. SHOULD.
- Escalation chain defined (e.g., Program Manager, Director)
- Conflict resolution timeline specified
- Arbitration or decision authority named

### SIGN.05 Change Notification
Change notification process defined. MUST.
- Notification timeline (e.g., within 24 hours)
- Distribution list (recipients)
- Notification channel (email, meeting, etc.)
- Acknowledgment requirement
