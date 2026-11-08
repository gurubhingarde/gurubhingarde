---
name: sysml-state-machine-checklist-reviewer
description: Run a confirmation review on any SysML state machine diagram xlsx, probing for well-formedness, transition completeness, guard coherence, pseudo-state correctness, and region balance per OMG SysML 1.6 and 2.0. Use this skill when the user mentions sysml state machine checklist reviewer.
---

# sysml-state-machine-checklist-reviewer

Run a confirmation review on any SysML state machine diagram xlsx, probing for well-formedness, transition completeness, guard coherence, pseudo-state correctness, and region balance per OMG SysML 1.6 and 2.0.

**Use this skill whenever the user provides a completed SysML state machine xlsx and requests checklist validation or state semantics audit.**

## Runs
- 25 canonical checks across 6 confirmation review tabs
- Every state machine has initial pseudo-state
- Every transition has source and target state
- No orphan states or dangling transitions
- History pseudo-states only inside composite states
- Guards mutually exclusive on outgoing transitions
- Entry/exit/do behaviors properly assigned

## Output
- 7-tab checklist xlsx with Summary, Findings
- Dashboard with KPIs (Transition Coverage %, Issues)
- Per-section findings and confidence levels
