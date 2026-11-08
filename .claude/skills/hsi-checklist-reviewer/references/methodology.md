# HSI Specification Checklist — Methodology

## Scoring Conventions

### Rating Scale

| Rating | Interpretation | Action Required |
|--------|-----------------|-----------------|
| **FC** (Fully Compliant) | Requirement is satisfied; evidence found in xlsx | None |
| **LC** (Largely Compliant) | Requirement mostly satisfied; minor gaps only | Consider mitigation for gaps |
| **PC** (Partially Compliant) | Significant gaps identified; requirement not fully met | Corrective action required before release |
| **NO** (Not Compliant) | Requirement not met; evidence absent or inadequate | Mandatory corrective action |
| **NA** (Not Applicable) | Check does not apply to this artifact | Document rationale; move on |
| **—** (Pending) | Requires reviewer judgment; auto-reviewer cannot decide | Reviewer decision required |

### Obligation Levels

- **Shall**: Mandatory requirement per ISO 26262. A "NO" on a Shall is a major non-conformance.
- **Should**: Recommended best practice. A "NO" on a Should is a minor non-conformance.

## Confidence Levels

### High Confidence

Checks that can be verified directly from xlsx content without ambiguity:
- Author and Approver populated (existence check)
- Revision history present (row count)
- Signal catalog populated (>0 rows)
- Each signal has direction specified (column value check)
- ASIL allocated (column not empty)
- Test cases enumerated (row count)

### Medium Confidence

Checks that require inference or pattern-matching:
- Signal encoding adequate (bit width + data type both populated)
- Timing specification complete (majority of signals have sample rate AND max age AND latency)
- Test case coverage (count ≥ signal count)
- Failure mode documentation (rows present for key signals)

### Low Confidence

Checks that require subjective judgment or external artifact verification:
- Title covers scope (requires reading and interpretation)
- Consistency with TSC / DIA (requires cross-document comparison)
- Integrity protection adequacy (requires knowledge of application ASIL, architecture)
- Diagnostics strategy (requires link to safety mechanisms)

## Check Categories

### Confirmation Review (14 checks)

Generic document quality checks applicable to any ISO 26262 work product:
1. Document structure (headlines, templates, maintainability)
2. Template version currency
3. Search aids (TOC, index, cross-references)
4. Title scope coverage
5. Author and approver identification
6. Unique revision identification
7. Change history
8. Work-product status
9. Current revision identifiability
10. Configuration management
11. Header/footer currency
12. Table of contents
13. References list
14. Section completion

### HSI Assessment (14 checks)

Substantive HSI Specification checks per ISO 26262-4 §6.4.6 and ISO 26262-5 §6.4.6:
1. HSI signal catalog populated (count > 0)
2. Signal direction specified (HW→SW or SW→HW)
3. Bit width / encoding specified per signal
4. Owner identified per signal (HW or SW)
5. Integrity protection for safety-relevant signals (Parity/CRC/SECDED/Dual-channel)
6. Validity bit or liveness counter for safety-relevant signals
7. FSR traceability (linked FSR_ID per signal)
8. Timing specification (sample rate, max age, latency per signal)
9. Failure modes documented per signal
10. SW reaction specified for fault scenarios
11. Initialization sequence documented (HW BIST + SW startup checks)
12. Cross-reference table covers all signals (no orphans)
13. Test cases defined per signal (nominal, fault injection, boundary, timing)
14. ASIL allocated per safety-relevant signal

### Verification Assessment (5 checks)

HSI-specific verification checks per ISO 26262-8:
1. Register map completeness (MCU memory layout coverage)
2. Timing budget adequacy (latencies, max ages, sample rates realistic)
3. Consistency with HW architecture specification
4. Integrity protection mechanisms verified against TSC test cases
5. Diagnostics and error handling strategy for HSI faults

## Key Assumptions and Limitations

1. **Source format**: Skill works best on hsi-builder outputs (named tabs 00_Title_Page, 02_HSI_Signal_Catalog, etc.). On other HSI formats, keyword heuristics are applied (best-effort).
2. **No source modification**: The skill generates a checklist; it does NOT modify the source HSI.
3. **External artifact checks**: Verification Assessment items #3, #4, #5 require cross-reference with TSC, DIA, safety mechanisms. These are marked Pending in auto-review and require human judgment.
4. **ASIL determination**: Skill checks for presence of ASIL allocation; it does NOT re-derive ASIL from failure modes or FTA. Derivation is assumed to be in external documents.
5. **Reviewer independence**: ISO 26262-2 requires confirmation reviews to be performed by independent person (I1), team (I2), or organizational unit (I3) per ASIL. The skill is a workbench; the reviewer is responsible for independence.

## Workflow Integration

### Typical Review Flow

1. **Analyst** generates HSI Specification (hsi-builder or manual).
2. **Analyst** runs this skill: `generate_checklist.py <hsi.xlsx> <checklist.xlsx>`.
3. **Reviewer** (independent) opens checklist, reads Summary tab for executive view.
4. **Reviewer** walks Confirmation Review, HSI Assessment, VA tabs; for each NO/PC/Pending row:
   - Reads Recommended Action
   - Decides: update source HSI or accept as-is (with rationale)
   - For Pending rows (low confidence), applies judgment
5. **Reviewer** updates Assessment column (or source HSI).
6. **Analyst** (optional) updates source HSI based on feedback, re-runs skill for fresh checklist.
7. **Reviewer** marks checklist as "Accepted" or "Rejected" (via external sign-off process).

### Re-run After Updates

- Each skill run generates a fresh checklist from the current HSI state.
- Previous checklist is overwritten (no change-tracking across runs).
- **Recommended practice**: keep old checklists for diff comparison if needed.

## Interpretation of Results

### NO Findings (Not Compliant)

Indicate a requirement is not met. Examples:
- Author/Approver fields are empty → "NO" for CR #4b
- No signals in catalog → "NO" for HSIA #1
- Missing initialization sequence tab → "NO" for HSIA #11

**Action**: Corrective action is mandatory before acceptance. Analyst updates source HSI, skill is re-run.

### PC Findings (Partially Compliant)

Indicate a requirement is partially satisfied; gaps are identified. Examples:
- Only 70% of signals have direction specified → "PC" for HSIA #2
- Timing spec covers 60% of signals → "PC" for HSIA #8

**Action**: Corrective action is recommended. Reviewer decides: accept gap with documented exception, or require completion.

### LC Findings (Largely Compliant)

Indicate requirement is mostly met; minor gaps only. Examples:
- 90% of signals have bit width, 85% have data type → "LC" for HSIA #3

**Action**: Minor corrective action encouraged. Acceptable for release with documented caveat.

### FC Findings (Fully Compliant)

Indicate requirement is satisfied; no action needed.

### NA Findings (Not Applicable)

Indicate check does not apply. Marked as NA if preconditions are not met. Example:
- HSIA #5 (integrity protection) is NA if there are no safety-relevant signals.

### Pending (blank Assessment)

Indicate reviewer judgment is required. Examples:
- Scope coverage (requires reading title and comparing to architecture)
- Consistency with other documents (requires cross-reference)

**Action**: Reviewer reads the Auto-suggest finding, applies judgment, and sets Assessment to FC/LC/PC/NO.

---

## Reference Links

- ISO 26262-1:2018 — Road vehicles - Functional safety - Part 1: Vocabulary
- ISO 26262-4:2018 — Part 4: Specification and management of functional safety
- ISO 26262-5:2018 — Part 5: Product development at the system level
- ISO 26262-8:2018 — Part 8: Guidelines on functional safety
