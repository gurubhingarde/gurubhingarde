# HW Architecture Checklist Methodology

## Overview

This skill performs a structured confirmation-measures review on any ISO 26262 HW Architecture xlsx produced by `hw-architecture-builder` or similar tools. The checklist verifies compliance with ISO 26262-5 §7 (HW Architecture requirements) and ISO 26262-8 §9 (verification processes).

## Rating Convention

| Rating | Meaning | Interpretation |
|--------|---------|-----------------|
| **FC** | Fully Compliant | Requirement met; evidence verified in source document; no gaps or corrective actions needed. |
| **LC** | Largely Compliant | Requirement substantially met with minor gaps or caveats; evidence present but incomplete; low-risk corrective actions recommended. |
| **PC** | Partially Compliant | Requirement partially met; significant gaps identified; corrective actions required before approval. |
| **NO** | Not Compliant | Requirement not met; no evidence found; major corrective action required. |
| **NA** | Not Applicable | Requirement does not apply to this HW Architecture (e.g., external verification checks). |
| **(blank)** | Pending Review | Subjective or complex check requiring reviewer judgment; auto-suggest provided with (Low) confidence. |

## Confidence Levels

| Confidence | Basis |
|------------|-------|
| **High** | Directly verified from xlsx content; machine-verifiable (e.g., "Author field populated", "HW elements > 0") |
| **Medium** | Inferred from xlsx with reasonable caveats (e.g., "PCB design rows present; reviewer to verify detail") |
| **Low** | Subjective check or depends on external artifact (e.g., "HW independence strategy" requires design review) |

## Obligations

- **Shall** (mandatory): Non-compliance on a Shall requirement is a major non-conformance (NO prevents approval).
- **Should** (recommended): Non-compliance on a Should is a minor issue; can be tracked as deferred action (LC/PC acceptable with justification).

## Check Categories

### Confirmation Review (12 checks)
Generic document quality and configuration management checks per ISO 26262-8 §10. Verifies:
- Title page hygiene (author, approver, revision, status, document ID)
- Document structure and navigation (tabs, table of contents, references)
- Revision history and configuration management

### HW Architecture Assessment (12 checks)
Substantive HW architecture checks per ISO 26262-5 §7. Verifies:
- HW Element Catalog populated with complete attributes (supplier, part, package, FIT)
- Safety qualification (AEC-Q100/Q101/Q200) recorded for ASIL-relevant elements
- PCB design documented (layers, area allocations)
- Power architecture complete (rails, regulators, monitors)
- Clock architecture complete (sources, monitoring, redundancy)
- Traceability from HW elements to TSC nodes and HW-TSRs
- Safety mechanism allocation and HWSR allocation matrix
- Common-cause failure analysis for redundant pairs
- Total system FIT computed from BOM
- Independence requirements respected between decomposed FSC channels

### Verification Assessment (5 checks)
High-level verification checks per ISO 26262-8 §9. Most are external (refer to Verification Plan/Report); HARA-specific items marked.

## Auto-fill Confidence Model

For each check, the skill assigns:
1. **Rating** (FC / LC / PC / NO / NA / blank)
2. **Finding** — evidence observed or lack thereof
3. **Page/Section** — where to find supporting evidence in the source xlsx
4. **Recommended Action** — corrective step if non-compliant
5. **Confidence** — how certain the verdict is

- **Fully-Compliant (FC)** findings always cite specific evidence (count, field names, cell values).
- **Pending (blank)** findings start with "(Auto-suggest, requires reviewer judgment)" to flag subjective assessments.
- **No changes to source xlsx** — all corrective actions live in Recommended Actions; analyst decides whether to update.

## When This Checklist Is Complete

- All Confirmation Review items checked and either FC or explained.
- All HW Architecture Assessment items at least LC or NA (no PC/NO on Shall items).
- All Verification Assessment items either FC/LC or explicitly Pending with reference to external Verification Plan.
- No major unresolved gaps between HW elements, TSC nodes, HW-TSRs, and safety mechanisms.

## Limitations

1. **Does not modify source HW Architecture** — only reports findings and recommendations.
2. **Does not perform design closure** — corrective actions are proposals; analyst / design team implements them.
3. **Verification Assessment mostly external** — most VA checks refer to a separate Verification Plan / Report that lives outside the HW Architecture xlsx.
4. **Independence verification is qualitative** — the skill checks that TSC references exist; actual independence of fault domains is a design review task.

## Iteration Workflow

1. Run the skill on the source HW Architecture xlsx.
2. Review the Summary tab for high-level statistics and findings.
3. Walk the CR, HWAA, and VA tabs; focus on PC and NO items first.
4. Decide: either update the source HW Architecture or defer the action.
5. Re-run the skill after updates to produce a fresh checklist.
6. Each re-run produces a new checklist xlsx; keep old versions for diff comparison.
