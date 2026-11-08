# DBC Confirmation Measures — Check Definitions

## Confirmation Review (CR) — 14 Checks

| ID | Section | Requirement | Obligation | Description |
|---|---|---|---|---|
| CR-01 | Document Structure | Document is structured into tabs | Shall | Workbook has at least 5 tabs (Title, Contents, Guide, Summary, etc.). |
| CR-02 | Document Structure | Template version is documented | Should | Template name/version is identifiable (e.g., "dbc-builder v1.0"). |
| CR-03 | Document Structure | Document is searchable (TOC present) | Should | Table of Contents or General Info tab exists for navigation. |
| CR-04a | Title & Metadata | Document has a clear title | Shall | Title page contains explicit document title (e.g., "CAN Network Specification — Vehicle X"). |
| CR-04b | Title & Metadata | Author and Approver are identified | Shall | Title page lists Author and Approver names. |
| CR-04c | Title & Metadata | Revision is unique and current | Shall | Title page shows Revision number (e.g., "1.0", "Rev C"). |
| CR-04d | Title & Metadata | Revision history is maintained | Shall | Document Control tab has revision history table with dates and change descriptions. |
| CR-04e | Title & Metadata | Document status is indicated | Shall | Title page shows Status (Draft, Released, Superseded, etc.). |
| CR-05 | Version Control | Current revision is identifiable | Shall | Current revision number is clearly marked. |
| CR-06 | Version Control | Configuration management practices apply | Should | Document is stored in version control system or document management system. |
| CR-07 | Version Control | Header and footer contain ID and revision | Should | Excel header/footer includes document ID and revision (if printed). |
| CR-08 | Searchability | Table of Contents is present | Should | TOC or overview tab aids navigation and discovery. |
| CR-09 | References | Network and scope are referenced | Should | Network name, scope, and CAN version are documented. |
| CR-10 | Completeness | All sections are substantially complete | Shall | At least 95% of Message names and Signal units are populated. |

## Technical DBC Assessment (TSA) — 18 Checks

| ID | Section | Requirement | Obligation | Description |
|---|---|---|---|---|
| TSA-01 | Message Definition | Message IDs are unique within network | Shall | No two messages share the same 11-bit or 29-bit identifier. |
| TSA-02 | Message Definition | DLC values are valid (0–8 bytes) | Shall | All DLC fields contain integers in range 0–8 (CAN 2.0); 0–64 for CAN FD. |
| TSA-03 | Signal Allocation | All signals fit within message DLC | Shall | Highest signal bit does not exceed DLC × 8 − 1. Example: DLC=4 → max bit 31. |
| TSA-04 | Signal Allocation | No signal bit overlap within messages | Shall | No two signals occupy the same bit(s) within the same message (except across multiplexed groups). |
| TSA-05 | Signal Encoding | Scale, offset, min, max, unit defined | Shall | Every signal has: scale (≠0), offset, min, max, unit (e.g., rpm, km/h, °C). |
| TSA-06 | Multiplexing | All multiplexor references are defined | Shall | Every signal that references a multiplexor signal must have that multiplexor explicitly defined. |
| TSA-07 | Signal Allocation | Every signal belongs to a message | Shall | No orphaned signals; signal message_id_hex matches a defined message. |
| TSA-08 | Message Definition | Every message has a sender ECU | Shall | Every message has a sender_ecu field populated. |
| TSA-09 | Network Definition | Message senders are defined ECUs | Shall | Sender ECU name matches an entry in ECU Inventory. |
| TSA-10 | Network Definition | Signal receivers are defined ECUs | Shall | Each signal receiver (if populated) matches an ECU in the inventory. |
| TSA-11 | Signal Encoding | Byte order is valid (little/big endian) | Shall | Byte order is "little_endian", "big_endian", "Intel", or "Motorola". |
| TSA-12 | Signal Encoding | Signal type is valid (signed/unsigned) | Shall | Type is "signed", "unsigned", or (for FD) floating-point indicator. |
| TSA-13 | Signal Encoding | Min and max values are sensible | Should | If both min and max are defined, min ≤ max. |
| TSA-14 | Message Definition | Frame type is valid | Shall | Frame type is "Standard" (11-bit), "Extended" (29-bit), or equivalent. |
| TSA-15 | Message Definition | Cyclic messages have cycle time defined | Shall | transmission_type="cyclic" implies cycle_time_ms > 0. |
| TSA-16 | Message Definition | Transmission type is valid | Should | transmission_type is "cyclic", "event", "spontaneous", "on-demand", or "triggered". |
| TSA-17 | Value Tables | Value tables present for state signals | Should | State/mode signals have enumeration tables (e.g., GearPosition: 0=Park, 1=Reverse). |
| TSA-18 | Network Topology | Network topology documented | Should | Network Topology tab or similar documents sender-receiver relationships and message flow. |

## Verification Assessment (VA) — 10 Checks

| ID | Section | Requirement | Obligation | Description |
|---|---|---|---|---|
| VA-01 | Signal & Message Consistency | Message signal counts are accurate | Should | signal_count in Message Catalog matches actual count in Signal Catalog for that message. |
| VA-02 | Network Definition | ECU inventory is defined | Should | At least one ECU is defined in ECU Inventory. |
| VA-03 | Signal & Message Consistency | Signal counts match allocation | Should | Declared signal counts per message match the number of signals assigned. |
| VA-04 | Signal & Message Consistency | No orphaned signals exist | Shall | Every signal references a defined message; no dangling references. |
| VA-05 | Network Definition | Signal receivers are defined | Should | At least 80% of signals have at least one receiver defined. |
| VA-06 | Signal Encoding | Scaling is consistent across signals | Should | At least 95% of signals have scale, offset, and unit populated. |
| VA-07 | Bit Allocation | Bit allocation is verified | Should | Sample audit of signal bit positions confirms correct start bit and length. |
| VA-08 | DLC Optimization | DLC allocation is efficient | Should | DLC not excessively larger than minimum required. Example: if max signal bit is 15, DLC should be 2–3, not 8. |
| VA-09 | Multiplexing | Multiplexor signals are valid | Should | Multiplexor signals are defined and actively used (not orphaned). |
| VA-10 | Traceability | Document ID and Revision enable traceability | Should | Doc ID (e.g., "COM-00123") and Revision (e.g., "1.0") are populated for version tracking. |

## Notes

### High-Confidence (Automated) Checks

These checks can be fully automated via parsing:
- TSA-01 (unique message IDs)
- TSA-02 (valid DLC)
- TSA-03 (signals fit DLC)
- TSA-04 (no bit overlap)
- TSA-08 (messages have sender)
- VA-04 (no orphaned signals)

### Medium-Confidence (Inferred) Checks

These rely on pattern matching and may have false negatives:
- TSA-05 (scale/unit complete)
- TSA-06 (multiplexor defined)
- TSA-09 (sender is valid ECU)
- TSA-10 (receiver is valid ECU)

### Low-Confidence (Manual) Checks

These require human judgment:
- CR-02 (template version)
- TSA-17 (value tables present for state signals)
- TSA-18 (network topology documented)
- VA-07 (bit allocation sampled)
- VA-08 (DLC optimization)

### J1939 Considerations

If the DBC targets J1939 (heavy-duty vehicles):
- Frame type must always be "Extended" (29-bit).
- DLC is always 8 bytes (J1939 standard).
- Message IDs follow a specific structure: P (priority 3 bits) + F (PF 8 bits) + PS (8 bits) + S (1 bit source).
- Checks TSA-02, TSA-03, TSA-14, TSA-15 may have different interpretation.

### Multi-Frame (CTS/CM) Awareness

If the DBC includes multi-frame messages (Connection Management / CTS):
- These are typically documented in a separate column or table (e.g., "Multi-Frame: Yes", "CTS Required: Yes").
- Single-frame checks (TSA-03, TSA-04) apply to each frame independently.
- DLC for multi-frame is always 8 (per CAN 2.0).

## Remediation Workflow

1. **Run checklist** on source DBC xlsx.
2. **Sort by Obligation** (Shall first) and **Rating** (NO first).
3. **For each Shall/NO**:
   - Read the Finding and Recommended Action.
   - Update the source DBC (JSON or .dbc file).
   - Regenerate the xlsx.
4. **For each Should/PC**:
   - Evaluate impact and priority.
   - Address if schedule permits; otherwise document as deferred.
5. **Re-run checklist** and repeat until **zero Shall/NO violations**.
6. **Sign off**: Author and Approver confirm acceptance.

## Integration with dbc-builder

If the DBC was generated via `dbc-builder`, the JSON source is the single source of truth. To fix issues:

1. Identify the violated check and corresponding JSON field.
2. Update the JSON input.
3. Re-run `python scripts/generate_dbc.py <updated.json> <output.xlsx>`.
4. Re-run the checklist.

This ensures consistency and maintains audit trail.
