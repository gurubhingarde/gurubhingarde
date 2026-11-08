# PPAP Checklist Reviewer — Methodology

## Scoring conventions

The checklist uses a 6-point scale:

| Rating | Meaning | Meaning |
|--------|---------|---------|
| **FC** | Fully Compliant | Requirement is met; no discrepancies. |
| **LC** | Largely Compliant | Meets intent; minor gaps acceptable with minor corrective action. |
| **PC** | Partially Compliant | Significant gaps; must be addressed before submission. |
| **NO** | Not Compliant | Requirement not met; cannot proceed without resolution. |
| **NA** | Not Applicable | Requirement does not apply in this context. |
| **PENDING** | Pending Review | Requires subjective assessment by reviewer. |

**Compliance calculation:** (FC + LC) / (Total - NA) × 100%

## Confidence model

Every check result includes a confidence level:

| Confidence | Assigned when | Example |
|------------|---------------|---------|
| **High** | Verified directly from xlsx content | Author/Approver populated; PSW signature block filled; drawing number present |
| **Medium** | Inferred from xlsx with reasonable caveat | 15+ elements present (heuristic suggests completeness); R&R values calculated from MSA sheet |
| **Low / Draft** | Subjective or requires external artifacts | Drawing under change control (external); sample approved by customer (external); FAR data present (external) |

## What the skill does

- **Probes PPAP content** from all 22 tabs (Title through References).
- **Extracts metadata:** customer, supplier, part name/number, submission level.
- **Evaluates submission readiness** (PSW fields, signature block, element statuses).
- **Flags headline issues:**
  - Out-of-spec dimensional results
  - Low process capability (Cpk/Ppk < 1.33)
  - High MSA R&R (> 30%)
- **Runs 33 checks** spanning:
  - 14 Confirmation Review (CR) — doc-quality, structure, completeness
  - 14 PPAP Assessment (PPAPA) — element-by-element per AIAG PPAP 4th ed
  - 5 Verification Assessment (VA) — external references (drawing control, material certs, sample approval, FAR, FMEA closure)

## What the skill does NOT do

- **Modify the source PPAP.** All corrective actions land in Recommended Actions; the analyst decides whether to update the PPAP and re-run.
- **Substitute for independent review.** AIAG PPAP and customer specs require authorized personnel review and sign-off. This skill is a workbench.
- **Evaluate subjective quality** (e.g., "Does the DFMEA adequately address all failure modes?"). Those checks are marked Pending and drafted for reviewer judgment.
- **Access external documents** (customer drawing standards, Item Definition, Functional Safety Concept, etc.). VA checks that depend on external artifacts are marked Pending.
- **Validate against customer-specific requirements** beyond AIAG standard. Reviewer must cross-reference against customer's PPA or RFQ.

## Output tabs explained

### Title
Displays the PPAP being assessed (customer, supplier, part, part number, source file path).

### General Info
Table of Contents and standard references (AIAG PPAP Manual, ISO 9001, etc.).

### Guide
Scoring guide (what FC/LC/PC/NO/NA/Pending mean and how to interpret them).

### Summary
- **KPI tiles:** Total items, Compliance %, Pending count, Major issues
- **Overall status banner:** APPROVED / CONDITIONAL APPROVAL / REJECTED / PENDING REVIEW
- **Rating distribution pie chart:** shows breakdown of FC/LC/PC/NO/NA/Pending
- **Compliance % by tab:** horizontal bar chart of each tab's compliance
- **Rating breakdown by section:** stacked bar showing rating distribution per section
- **Findings table:** all NO and PC items with requirement, finding, recommended action

### Confirmation Review
14 doc-quality checks (structure, title page, doc control, TOC, headers, approval authority, status, completeness, sign-off, formatting, accuracy, traceability, archive plan).

### PPAP Assessment
14 element-specific checks per AIAG PPAP 4th edition:
1. PSW fields populated (part name, number, codes, drawing change level/date, declaration)
2. Submission level clearly identified (1-5)
3. Element 1 (Design Records) referenced
4. Element 4 (DFMEA) referenced with version
5. Element 6 (PFMEA) referenced with version
6. Element 7 (Control Plan) referenced
7. Element 8 (MSA R&R) results present, all gages ≤ 30%
8. Element 9 (Dimensional) all characteristics in spec
9. Element 11 (Process Capability) Cpk/Ppk ≥ 1.33
10. Element 12 (Lab) from accredited labs (A2LA / ISO 17025)
11. Element 17 (Customer-Specific) all requirements addressed with evidence
12. Element 18 (Submission Status Matrix) complete
13. Required elements per submission level all marked submitted
14. PSW signature block completed

### Verification Assessment
5 checks on external artifacts:
1. Customer drawing under change control
2. Material certifications provided
3. Sample parts approved by customer
4. First article run (FAR / tooling) data documented
5. FMEA corrective actions closed

Most VA checks are Pending because they require external documents (drawing standards, customer approval records, etc.).

## Submission levels (per AIAG PPAP Manual)

| Level | Scope | Typical use |
|-------|-------|-------------|
| 1 | Minimal | Engineering change on existing part; established supplier; low risk |
| 2 | Reduced | Design change; new supplier for existing product; moderate risk |
| 3 | Full | New part; new supplier; high risk; complex changes |
| 4 | Sourcing change | Same design, different supplier/location |
| 5 | Revalidation | Periodic re-approval of existing part |

**Required elements vary by level.** The skill checks that all elements for the declared level are marked submitted per AIAG table.

## Common pitfalls

1. **NO findings do not mean failure — they are improvement opportunities.** Many NO findings are trivial (missing revision number on title page) and quick to fix. The recommended action explains the fix.

2. **Pending findings are normal and expected.** Many VA checks and subjective CR/PPAPA checks are Pending because they require external artifacts or human judgment. Reviewer is expected to work through these.

3. **Headline findings (out-of-spec, low Cpk, high R&R) require root-cause investigation.** The skill flags the data; engineering must respond with corrective action.

4. **The skill does not score the FMEA, process design, or the engineering.** It checks that the PPAP *references* the FMEA and that required elements are *present*. It does not evaluate the quality of the FMEA itself.

5. **Accuracy of dimensional and capability data is the user's responsibility.** The skill reads what is in the xlsx; garbage in = garbage out.
