---
name: sysml-block-diagram-checklist-reviewer
description: Run a confirmation review on any SysML block diagram xlsx, probing for well-formedness, structural integrity, port typings, connector completeness, and item flow semantics per OMG SysML 1.6 and 2.0. Use this skill when the user mentions sysml block diagram checklist reviewer.
---

# sysml-block-diagram-checklist-reviewer

Run a confirmation review on any SysML block diagram xlsx, probing for well-formedness, structural integrity, port typings, connector completeness, and item flow semantics per OMG SysML 1.6 and 2.0.

**Use this skill whenever the user provides a completed SysML block diagram xlsx and requests checklist validation, structural audit, or well-formedness certification.**

## Runs
- 28 canonical checks across 6 confirmation review tabs
- Structural completeness (all blocks stereotyped, all parts typed)
- Port semantics (directions, flow vs full vs proxy consistency)
- Connector topology (no orphans, no dangling references)
- Item flows (compatible types, proper directions)
- Validation rules (multiplicity, interface compliance)

## Checks
- Block stereotype presence and correctness
- Property/part typing completeness
- Port direction assignment (in/out/inout/provides/requires)
- Connector source/target binding
- Item flow type compatibility
- No orphan blocks, ports, or connectors
- Port count and naming consistency
- Interface coherence

## Output
- 7-tab checklist xlsx with Summary, Findings, Recommended Actions
- Dashboard with KPIs (Compliant%, Issues, Status)
- Pie/bar charts for rating distribution
- Detailed per-section findings and confidence levels
