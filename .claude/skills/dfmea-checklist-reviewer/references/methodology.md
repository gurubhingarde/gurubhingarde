# DFMEA Checklist Reviewer — Methodology

## Scoring Conventions

### Rating Scale

| Rating | Meaning | When to Use | Counts Toward |
|--------|---------|-------------|---|
| **FC** | Fully Compliant | Requirement is satisfied; no gaps | Compliance % |
| **LC** | Largely Compliant | Minor gaps, acceptable with caveats | Compliance % |
| **PC** | Partially Compliant | Significant gaps; corrective action recommended | Findings list |
| **NO** | Not Compliant | Requirement not met; blocker | Findings list + Rejection criteria |
| **NA** | Not Applicable | Check does not apply to this DFMEA | Excluded from applicable count |
| Pending | Under Review | Awaiting reviewer judgment | Not counted as compliant |

Compliance % = (FC + LC) / (Total - NA) × 100

### Obligation Levels

- **Shall** (Mandatory): Requirement is mandatory per AIAG-VDA 2019 or ISO 26262-3. A NO rating on a Shall check may block approval.
- **Should** (Recommended): Best practice or recommended per guidance. A NO on Should is noted but not a blocker.

### Confidence Levels

| Confidence | Criterion | What It Means |
|------------|-----------|---|
| **High** | Verified directly from worksheet data | Direct observation; no interpretation needed |
| **Medium** | Inferred with reasonable assurance | Minor interpolation; high likelihood accurate |
| **Low / Draft** | Subjective or requires external artifact | Requires reviewer judgment; marked auto-suggest |

Every Low-confidence finding is prefixed "(Auto-suggest, requires reviewer judgment)" to signal human review required.

## What This Skill Does

### Automatic Validations (High Confidence)

1. **Structural Checks**: Tab presence, metadata population (title, FMEA ID, revision, status, owner)
2. **Row-Level Counts**: Number of failure modes, S/O/D ratings, AP assignments, action items
3. **Completeness**: % of rows with FM, FE, Cause, S, O, D, AP populated
4. **Action Priority Metrics**: Count of High/Medium/Low AP items; count pending closure
5. **Special Characteristics**: Count of SCs identified
6. **Action Plan**: Count of items with owner and due date

### Draft Validations (Low Confidence — Auto-Suggest)

1. **Design Intent**: "Structure hierarchy matches design architecture" (needs design spec)
2. **Function Consistency**: "Function statements are clear and testable" (requires domain review)
3. **Severity/Occurrence Justification**: "S/O/D ratings are defensible" (needs field data / expert judgment)
4. **Configuration Management**: "DFMEA is under CM system" (organizational practice)
5. **Header/Footer Updates**: "Current revision is reflected in document metadata" (manual verification)

### What This Skill Does NOT Do

1. **Does not validate design correctness**: The skill does not assess whether the design is safe or meets requirements. It validates that the DFMEA worksheet is complete per AIAG-VDA 2019 structure.

2. **Does not make severity or occurrence judgments**: The skill accepts S/O/D as given and verifies they are rated 1-10. It does not assess whether S=8 is too high or O=3 is defensible for a particular failure mode. That is the analyst's engineering judgment.

3. **Does not modify source DFMEA**: All findings are recommendations. The analyst decides whether to update the DFMEA and re-run the skill.

4. **Does not perform design review**: Confirmation review is a checklist audit, not a safety assessment. Independent technical review (I1/I2/I3 per ISO 26262-2) is still required.

5. **Does not check traceability to safety requirements**: The skill does not verify that failure modes link to HARA safety goals or Item Definition functional safety requirements. That is a separate integration check.

## Headline Metric: High-AP Items Pending Closure

**Check #14 in DFMEA Assessment** reports the count of High-AP failure modes whose status is not Closed or Completed.

**Rationale**: AIAG-VDA 2019 Section 6 (Optimization and Verification) requires all recommended actions be tracked and closed. High-AP items represent the highest-risk failure modes; untracked high-AP items are a sign of incomplete DFMEA.

**Interpretation**:
- **Rating FC**: 0 high-AP items pending → DFMEA action loop is closed
- **Rating NO**: Any high-AP items pending → Actions must be tracked to completion

This single metric is the **most important validation** a reviewer can perform.

## Three-Tab Structure: CR, DFMEAA, VA

### Confirmation Review (CR) — 14 doc-quality checks

Generic checks applicable to any engineering document per ISO 26262-8 Section 10.

- Checks 1-14 verify structure, metadata, document control, references, section completeness.
- Most are FC/PC checks; few are hard NO.
- Mostly Shall obligations (mandatory).

### DFMEA Assessment (DFMEAA) — 14 substantive checks

Specific to DFMEA worksheet structure and content per AIAG-VDA 2019 Handbook.

- Checks 1-3: Header block, structure analysis, function analysis
- Checks 4-8: DFMEA worksheet population (FM, FE, Cause, S, O, D, AP)
- Checks 9-11: Action planning (High-AP actions, action plan tracker, special characteristics)
- Checks 12-14: Learning, references, **headline pending-AP metric**

### Verification Assessment (VA) — 4 external checks

External verification per AIAG-VDA 2019 Section 7 and ISO 26262-4/5.

- All 4 checks are marked Pending by default because they require external Verification Plan/Report.
- Reviewer ticks off once verification docs are available.

## How to Use This Skill in a Review Workflow

### Phase 1: Preparation

1. Run `generate_checklist.py` on the DFMEA.
2. Review the JSON summary output for headline metrics.
3. Open the output checklist xlsx.

### Phase 2: Initial Triage (Summary tab)

1. Read the 4 KPI tiles (Total, Compliance %, Pending, Major Issues).
2. Look at the Findings table (NO and PC items only).
3. Check DFMEA Assessment Check #14 (high-AP pending count).

### Phase 3: Detailed Review (CR, DFMEAA, VA tabs)

For each Pending row:
- Accept or refine the auto-suggested finding.
- If auto-suggest, mark as FC, LC, PC, or NO after review.

For each PC row:
- Reviewer decides if the gap is acceptable.
- If not, mark NO and assign Recommended Action to source DFMEA.

For each NO row:
- Reviewer assesses severity (Shall vs Should).
- Assigns action owner and due date.
- Updates source DFMEA and re-runs skill when action is complete.

### Phase 4: Closure

Once all Shall (mandatory) checks are FC or LC and all No items are closed:
- Archive the checklist as confirmation-measures evidence.
- Attach to DFMEA submission package.

## References

- AIAG-VDA FMEA Handbook, 2019 Edition
- ISO 26262-3:2018 Section 7 (Product Development)
- ISO 26262-4:2018 Section 5 (Specification Derivation)
