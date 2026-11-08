# SW FMEA Checklist Methodology

## What This Skill Does

The SW FMEA Checklist Reviewer is a **confirmation-measures workbench** that automates the ISO 26262-9 Section 8 review of a Software Failure Mode, Effects & Analysis (SW FMEA) document. It reads your xlsx, probes its content, runs 32 predefined checks (14 document-quality + 14 SW-FMEA-specific + 4 external verification), and writes a 7-tab checklist summarizing findings, confidence, and recommended actions.

## What It Does NOT Do

- **Does not modify** your source SW FMEA (read-only)
- **Does not generate** test cases, safety goals, or requirements (those come from HARA/FSC/TSC)
- **Does not replace** independent reviewer judgment (per ISO 26262-2)
- **Does not validate** methodology correctness or architectural fit (subjective; drafted for reviewer acceptance)

## Assessment Ratings

| Rating | Meaning | Action |
|--------|---------|--------|
| FC | Fully Compliant | Check passes; all evidence collected. Reviewer may accept or request deeper review. |
| LC | Largely Compliant | Check mostly passes; minor gaps noted. Reviewer assesses criticality and accepts or requests closure. |
| PC | Partially Compliant | Check partly satisfied; significant gaps. Recommended Action suggests path forward; requires analyst decision. |
| NO | Not Compliant | Check fails; major gap or violation. Blocking item; must be resolved before acceptance. |
| NA | Not Applicable | Check does not apply to this SW FMEA (e.g., no high-severity modes → no propagation analysis). No action needed. |
| — | Pending | Check awaiting external artifact (e.g., Verification Plan). Reviewer to tick off when available. |

## Confidence Levels

| Level | When Used | Example |
|-------|-----------|---------|
| High | Evidence directly from xlsx (counts, values, comparisons) | "All 12 failure modes have severity rated" |
| Medium | Inferred with caveat (ratios, completeness heuristics) | "SW catalog 92% complete (12/13 components with ASIL)" |
| Low | Subjective or requires external artifact | "(Auto-suggest) Methodology consistent with architectural decomposition" |

## Scoring Convention: Obligation

Two obligation levels appear in requirements:

| Obligation | Meaning | Consequence of NO |
|-----------|---------|-------------------|
| Shall | Mandatory per ISO 26262-9 §8 | Major non-conformance; resolution required before acceptance |
| Should | Recommended per ISO 26262-9 §8 | Minor non-conformance; reviewer assesses risk/value of closure |

## Residual Risk Acceptance (Check #10, Headline)

SW FMEA Check #10 auto-verifies that post-mitigation risk for each failure mode is acceptable per ASIL:

**ASIL Thresholds (Risk Score):**
- **ASIL D**: <= 1
- **ASIL C**: <= 3
- **ASIL B**: <= 9
- **ASIL A**: <= 27
- **QM (non-safety)**: unlimited

If any failure mode's post-risk exceeds its ASIL threshold, Check #10 returns **NO** with a count of exceeding modes. This is a **data-driven halt**: mitigation is insufficient.

### How Risk is Computed

Typical formulas (SW FMEA builder conventions):
- **Pre-Risk** = Severity index × Frequency index (before mitigation)
- **Post-Risk** = Pre-Risk × (1 - Detection Coverage / 100) × (1 - Mitigation Coverage / 100)

Post-Risk must be <= ASIL threshold for the failure mode to be acceptable.

## Tabs in Output Checklist

1. **Title**: Context (source SW FMEA, project, revision, ASIL, reviewer)
2. **General Info**: TOC and reference list
3. **Guide**: Interpretation hints
4. **Summary**: Visual dashboard with KPI tiles, pie chart (ratings), bar charts (compliance %), findings list
5. **Confirmation Review**: 14 doc-quality checks
6. **SW FMEA Assessment**: 14 SW-FMEA-substantive checks (rows 1-9 rate completeness; row 10 rates residual risk)
7. **Verification Assessment**: 4 external verification checks (all Pending until Verification Plan provided)

## Using the Checklist

1. **Reviewer reads Summary tab first**: Scan KPI tiles and Findings list to prioritize work.
2. **Focus on NO and blank (Pending) rows**: Decide what to fix, what to accept, what awaits external input.
3. **For each NO**: Read Recommended Action; decide whether to ask analyst to update SW FMEA and re-run, or accept as-is with justification.
4. **For each Pending**: Identify required external artifact (e.g., "Provide Verification Plan"), track to closure.
5. **Update Assessment column**: Reviewer types FC/LC/PC/NO as they judge each row.
6. **Re-run checklist generator** when SW FMEA changes: Produces fresh checklist for iteration.

## Typical Review Cycle

1. Analyst generates checklist from draft SW FMEA
2. Reviewer opens Summary tab, identifies top gaps
3. Analyst prioritizes: high-impact NO items first (e.g., Check #10 — unmitigated high-risk modes)
4. Analyst updates SW FMEA, re-runs generator
5. Reviewer assesses new checklist, iterates
6. When all Shall items are FC/LC and no blocking NOs remain, checklist is complete

## Integration with Other Skills

- **SW FMEA Builder** (upstream): Produces the source SW FMEA xlsx
- **SW Architectural Checklist Reviewer**: Validates SW architecture blocks map to SW components in FMEA
- **SW Requirements Checklist Reviewer**: Validates requirements trace to FMEA failure modes
- **Verification Plan Hooks** (downstream): Link FMEA failure modes to test cases in Verification Plan

## References

- ISO 26262:2018 Part 9, Section 8 — SW FMEA methodology and confirmation-measures checklist
- ISO 26262:2018 Part 6 — Software development safety requirements (context for FMEA scope)
- ISO 26262:2018 Part 2 — Management of functional safety (Confirmation Measures per ASIL and independence level)
