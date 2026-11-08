# HW-SR Checklist Methodology

## Rating System

The skill assigns one of six ratings to each checklist item:

### FC (Fully Compliant)
Requirement is satisfied. The finding cites specific evidence from the HW-SR xlsx (e.g., "All 42 HW-SRs have ASIL assigned. Values: QM, A, B, C, D").

**Confidence:** High (direct observation) or Medium (inferred with reasonable assumption).

### LC (Largely Compliant)
Requirement is mostly satisfied with minor gaps or concerns (e.g., "39/40 HW-SRs have target DC; 1 row missing"). Recommended action suggests completion.

**Confidence:** High.

### PC (Partially Compliant)
Requirement has significant gaps or missing evidence (e.g., "15/42 HW-SRs allocated to HW element; 27 still <TBD>"). Recommended action lists corrective steps.

**Confidence:** High.

### NO (Non-Compliant)
Requirement is not met (e.g., "No failure mode mapping rows detected"). Recommended action is mandatory.

**Confidence:** High.

### NA (Not Applicable)
Requirement does not apply to this project (e.g., "No HW-TSRs imported → no orphan-TSR check").

**Confidence:** High.

### Pending
Awaiting reviewer judgment (most subjective checks) or external verification. Marked with "(Auto-suggest, requires reviewer judgment)" prefix.

**Confidence:** Low.

---

## Confidence Levels

### High
- Verified directly from xlsx content
- Counted or boolean facts (e.g., "Author and Approver populated")
- Standard interpretation (e.g., "14 doc-quality checks always apply")

### Medium
- Inferred from xlsx with reasonable assumption
- Heuristic (e.g., "Sheet names suggest FMEA tab present")
- Sample-based (e.g., "5/8 sampled HW-SRs have requirement text")

### Low
- Subjective assessment (e.g., "Title covers scope")
- Requires external artifact (e.g., "Verification Plan addresses methods")
- Requires domain knowledge (e.g., "Verification methods appropriate for ASIL")

---

## Tab Organization

### Confirmation Review (14 checks)
Generic document-quality items from ISO 26262-8 Clause 10:
- Document structure, template version, searchability
- Title, author/approver, revision, status
- Configuration management
- Table of contents, references
- Section completeness

### HW Safety Requirements Assessment (12 checks)
Substantive HW-SR checks per ISO 26262-5 Section 6:
- HW-TSR import and coverage
- ASIL assignment and consistency
- HW element allocation
- Requirement text and target DC
- Failure mode mapping
- Verification methods
- Test strategy
- Independence considerations
- HSI references

### Verification Assessment (22 checks)
Verification-related checks per ISO 26262-8 Section 9:
- 17 external checks (Verification Plan, methods, test cases, report)
- 5 HW-SR-specific checks (33a–e: coverage, ASIL consistency, HSI consistency, element mapping, attribute completeness)

---

## Check Verification Logic

Each check invokes a verification function that:
1. Probes specific xlsx content (HW-SR catalog, failure mode mapping, etc.)
2. Counts, samples, or evaluates findings
3. Returns a CheckResult with rating, finding, page reference, recommended action, and confidence

Example:
```python
def hwsra_03_asil_assigned(p: ProbedHwSR) -> CheckResult:
    srs_with_asil = [sr for sr in p.hw_srs if sr.asil]
    if not p.hw_srs:
        return na("No HW-SRs.")
    rate = len(srs_with_asil) / len(p.hw_srs)
    if rate >= 0.99:
        return CheckResult(
            rating="FC",
            finding=f"All {len(p.hw_srs)} HW-SRs have ASIL assigned.",
            confidence="High",
        )
    # ... else PC
```

---

## Auto-fill Strategy

### Machine-Verifiable Checks (auto-fill FC/LC/PC/NO/NA)
- HW-TSR counts and import
- ASIL, element, text, DC presence/absence
- Failure mode mapping row counts
- Verification method coverage
- Test strategy row counts

### Subjective or External Checks (draft with Low confidence)
- Verification methods "appropriate for ASIL" (requires knowledge)
- Independence considerations (depends on FSC decomposition)
- Verification Plan compliance (external doc)
- Consequences of hazards (subjective scope)

For subjective items, the finding is prefaced "(Auto-suggest, requires reviewer judgment)" so you know to verify manually.

---

## No Source Modification

The skill produces a checklist xlsx but does not modify the source HW-SR workbook. All corrective actions are recommendations in the checklist's Recommended Action column. You decide whether to update the HW-SR and re-run.

Workflow:
1. Generate checklist from HW-SR v1.0
2. Review checklist; note PC and NO findings
3. Update source HW-SR based on findings
4. Re-run skill on updated HW-SR
5. Compare new checklist to old; verify improvements

---

## Limitations

1. **External checks cannot be verified from xlsx alone.** Verification Plan content, test case specifications, independence arguments—these live in separate documents. VA checks reference them but cannot validate them.

2. **Subjective judgment required.** The skill cannot definitively assess whether ASIL D requires "++ methods" in your specific context. It flags the check as Pending for you.

3. **Format variation.** The skill works best on hw-safety-reqs-builder outputs (tab names, column headers known). For other formats, heuristics apply; accuracy varies.

4. **Sample-based evaluation.** For large HW-SR catalogs (1000+ rows), the skill may sample rather than exhaustively check every row.
