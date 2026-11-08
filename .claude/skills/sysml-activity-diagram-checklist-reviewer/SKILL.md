---
name: sysml-activity-diagram-checklist-reviewer
description: Run a confirmation review on any SysML activity diagram xlsx, probing for well-formedness, control/object flow integrity, decision node guards, fork/join balance, and swim-lane consistency per OMG SysML 1.6 and 2.0. Use this skill when the user mentions sysml activity diagram checklist reviewer.
---

# sysml-activity-diagram-checklist-reviewer

Run a confirmation review on any SysML activity diagram xlsx, probing for well-formedness, control/object flow integrity, decision node guards, fork/join balance, and swim-lane consistency per OMG SysML 1.6 and 2.0.

**Use this skill whenever the user provides a completed SysML activity diagram xlsx and requests checklist validation or behavioral audit.**

## Runs
- 25 canonical checks across 6 confirmation review tabs
- Every action assigned to swim-lane
- Every control flow has source and target
- Decision nodes have at least 2 outgoing flows
- Fork and join nodes balanced
- Every parameter typed and assigned
- No orphan actions or flows

## Output
- 7-tab checklist xlsx with Summary, Findings
- Dashboard with KPIs (Flow Completeness %, Issues)
- Per-section findings and confidence levels
