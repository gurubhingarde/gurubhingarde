---
name: mbse-requirements-allocation-checklist-reviewer
description: Run a confirmation review on any MBSE requirements allocation matrix xlsx workbook, executing 28+ checks to confirm requirement decomposition, allocation completeness, relationship validity, and coverage against logical and physical architectures. Use this skill when the user mentions mbse requirements allocation checklist reviewer.
---

# mbse-requirements-allocation-checklist-reviewer

Run a confirmation review on any MBSE requirements allocation matrix xlsx workbook, executing 28+ checks to confirm requirement decomposition, allocation completeness, relationship validity, and coverage against logical and physical architectures.

Use this skill to audit MBSE requirements allocation workbooks for traceability, consistency, and readiness for model-based requirements management.

## Inputs
- Completed mbse-requirements-allocation-builder xlsx workbook

## Outputs
- Confirmation checklist xlsx with dashboard, rating summary (FC/LC/PC/NO), findings, recommended actions
- Coverage analysis, orphan detection, traceability path validation

## Check Categories

1. **Structure** (4 checks): Tab completeness, document control, requirement hierarchy
2. **Requirements** (6 checks): Requirement population by level, unique IDs, priority assignment
3. **Allocation** (6 checks): All requirements allocated, allocation targets valid, type consistency
4. **Relationships** (6 checks): Satisfy/derive/verify relationship completeness, circular derivation check
5. **Coverage** (4 checks): No orphan requirements, no unallocated elements, decomposition closure
6. **Traceability** (2 checks): End-to-end paths from stakeholder to implementation, verify methods defined

## Ratings
- FC (Fully Compliant): All criteria met
- LC (Largely Compliant): Minor gaps, easily resolved
- PC (Partially Compliant): Significant gaps
- NO (Non-Compliant): Major deficiencies
- NA (Not Applicable): Not relevant
