# DBC Checklist Methodology

The DBC Checklist Reviewer applies a structured confirmation-measures review to validate CAN database specifications against ISO 11898 and AUTOSAR Communication best practices.

## Review Structure

The checklist is organized into three major categories:

### 1. Confirmation Review (CR) — 14 checks
Generic document-quality checks ensuring the DBC specification is complete, controlled, and auditable:
- Document structure and organization
- Title, author, approver identification
- Revision tracking and status
- Searchability and table of contents
- Completeness of all tabs and sections

**Obligation**: Primarily "Shall" (mandatory) with some "Should" (recommended).

### 2. Technical DBC Assessment (TSA) — 18 checks
Substantive validation of CAN network design per ISO 11898-1 and AUTOSAR specifications:
- Message ID uniqueness
- DLC (Data Length Code) validity
- Signal bit allocation and overlap detection
- Signal encoding (scale, offset, min, max, unit)
- Multiplexor signal definition and consistency
- ECU definition and sender/receiver validity
- Byte order and signal type validation
- Cycle time specification for cyclic messages
- Value tables for discrete state signals
- Network topology documentation

**Obligation**: Mostly "Shall" (mandatory); some "Should" (recommended).

### 3. Verification Assessment (VA) — 10 checks
Cross-validation of signal and message consistency:
- Signal count accuracy
- ECU inventory completeness
- Consistency between declared and actual signal counts
- Orphaned signal detection
- Receiver ECU coverage
- Scaling consistency
- Bit allocation verification
- DLC optimization checks
- Multiplexor signal validation
- Traceability (Doc ID and Revision)

**Obligation**: Mostly "Should" (recommended) with some "Shall" (mandatory).

## Scoring System

### Ratings

- **FC (Fully Conforming)**: Requirement is met. Direct inspection or high-confidence inference from probed data.
- **LC (Largely Conforming)**: Requirement is mostly met. Minor gaps or inferred from structure; likely acceptable with light review.
- **PC (Partially Conforming)**: Requirement is partially met. Significant work remains; corrective action needed before release.
- **NO (Non-Conforming)**: Requirement is not met. Major non-conformance; blocks acceptance.
- **NA (Not Applicable)**: Requirement does not apply to this DBC (e.g., J1939 checks on a standard CAN network).
- **(blank or PENDING)**: Check incomplete; requires human verification.

### Confidence Levels

- **High**: Check is automated and based on direct inspection of the DBC content (e.g., message IDs are unique).
- **Medium**: Check is inferred from structure or pattern matching (e.g., value tables present).
- **Low**: Check requires subjective judgment or external evidence (e.g., "network topology documented").

### Obligation Levels

- **Shall**: Mandatory per ISO 11898 or AUTOSAR specification. NO rating = major non-conformance; blocks acceptance.
- **Should**: Recommended best practice. LC or PC acceptable with documented justification; NO rating requires mitigation.

## Acceptance Criteria

A DBC specification is **acceptable** if:

1. **No Shall/NO violations**: Every check marked "Shall" must have rating FC, LC, or NA.
2. **Signal/message consistency**: No orphaned signals, no bit overlap, all signals fit within DLC.
3. **Network definition complete**: All ECUs and messages are defined; all senders and receivers are valid.
4. **Encoding complete**: All signals have scale, offset, min, max, unit.
5. **Traceability**: Document ID and revision enable version control and change history.

A **major non-conformance** (FC/NO on a Shall requirement) must be resolved before release.

## Probing Strategy

The reviewer automatically extracts DBC content from the xlsx via best-effort parsing:

- **Title Page**: Project metadata, network name, document control fields
- **ECU Inventory**: List of ECUs and their properties
- **Message Catalog**: Message IDs, DLC, cycle time, sender, frame type
- **Signal Catalog**: Signal definitions with bit positions, encoding, receivers
- **Signal-to-Message Mapping**: Cross-references
- **Value Tables**: Enumerations
- **Network Topology**: Sender/receiver relationships

If a tab is missing or has non-standard formatting, the check will report PC or NA rather than crashing.

## Common Non-Conformances

1. **Duplicate message IDs**: Two or more messages with the same ID (CAN arbitration collision).
2. **Signal bit overlap**: Two signals assigned to the same bits within a message.
3. **Signal exceeds DLC**: A signal's bit range extends beyond the message payload size.
4. **Missing multiplexor**: A signal references a multiplexor that is not defined.
5. **Undefined sender/receiver**: Message sender or signal receiver does not exist in ECU inventory.
6. **Incomplete encoding**: Signal lacks scale, offset, min, max, or unit.
7. **No cycle time**: Cyclic message has no cycle time specified.
8. **DLC underflow**: Message payload requires only 2 bytes but DLC is set to 8.

## Mitigation Paths

### NO on Shall — Message ID Conflict
**Finding**: Duplicate message IDs detected.
**Recommended Action**: Resolve ID conflicts by assigning unique hexadecimal IDs per CAN standard (0x000–0x7FF for 11-bit, 0x00000000–0x1FFFFFFF for 29-bit).

### NO on Shall — Signal Bit Overlap
**Finding**: Two signals occupy the same bits within a message.
**Recommended Action**: Review signal bit allocation. Either shift signal positions or use multiplexing if the signals are never sent together.

### PC on Shall — Missing Scale/Unit
**Finding**: Several signals lack scale or unit definitions.
**Recommended Action**: Populate scale, offset, min, max, and unit for all signals. Refer to CAN database conventions or hardware specifications for unit mappings (rpm, km/h, °C, %, V, etc.).

## Iteration and Review

After running the checklist:

1. **Review the Summary dashboard** for KPI tiles, pie chart of ratings, compliance bar chart, and section breakdown.
2. **Focus on Shall/NO items** first; these block acceptance.
3. **Address Should/PC items** if time and priority permit.
4. **Update the source DBC** (JSON or original .dbc file) and regenerate the xlsx.
5. **Re-run the checklist** and repeat until acceptance criteria are met.

## Tools and Integration

The DBC Checklist Reviewer is designed to pair with **dbc-builder**, which generates the DBC xlsx from a JSON specification. However, it can audit any DBC xlsx via best-effort probing, making it suitable for legacy or hand-authored databases.

For integration with code generation (CANdb++, Vector DBC parsers, AUTOSAR Com module), run this checklist as a gate before implementation. A clean checklist reduces the risk of signal encoding errors, message ID conflicts, and network topology bugs downstream.
