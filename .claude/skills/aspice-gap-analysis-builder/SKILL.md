---
name: aspice-gap-analysis-builder
description: Generate an ASPICE gap analysis workbook from an upstream assessment, identifying capability level gaps and missing practices to reach target capability. Produces 10 tabs including Current State, Target State definition, gap identification per process, severity classification, effort estimation, quick wins, and major initiatives. Use this skill whenever the user needs to analyze process maturity gaps, define improvement targets, estimate remediation effort, or create an ASPICE roadmap for process improvement.
---

# ASPICE Gap Analysis Builder

A gap analysis identifies the difference between current process capability (from an ASPICE assessment) and target capability levels, then structures this into improvement roadmap inputs. This skill reads assessment results and target definitions, then produces a comprehensive gap inventory with severity, effort, and prioritization.

## When to use this skill

Use whenever the user wants to:
- Identify gaps between current and target ASPICE capability levels
- Prioritize process improvement initiatives
- Estimate effort and resources for improvement
- Plan ASPICE capability growth roadmap
- Define organizational process maturity targets

## Workflow

### Step 1 - Gather current state

Take the achieved capability level per process from aspice-assessment-builder (or equivalent assessment results) and record it as `processes[].current_cl` in the input JSON. The generator does not read the assessment workbook directly.

### Step 2 - Define target state

For each process in scope, specify:
- Process ID and name
- Current capability level (from assessment)
- Target capability level (customer requirement or internal goal)
- Justification for target

### Step 3 - Analyze gaps

Tool identifies:
- CL deltas (current to target)
- Missing Process Attributes per gap
- Gap severity classification (Show-stopper / Major / Minor)

### Step 4 - Generate

Run from Python with openpyxl:

```bash
python scripts/generate_aspice_gap_analysis.py <input.json> <output.xlsx>
```

The workbook is generated entirely from `<input.json>`. Current capability levels
belong in `processes[].current_cl` — transcribe them from the upstream assessment
when you build the input file. A legacy 3-argument form
(`<assessment.xlsx> <input.json> <output.xlsx>`) is still accepted, but the leading
workbook is ignored and the tool warns on stderr.

### Step 5 - Review

Confirm gap severity, effort estimates, and prioritization before moving to improvement planning.

## Output (10 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Project, analysis date, owner |
| 01 | Document Control | Revision history |
| 02 | Current State | Assessed CL per process, echoed from `processes[].current_cl` |
| 03 | Target State | Target CL per process with justification |
| 04 | Gaps | Gap description, missing PAs per process |
| 05 | Gap Severity | Severity classification (Show-stopper/Major/Minor) |
| 06 | Effort Estimation | Est. effort (days), elapsed time, resources |
| 07 | Quick Wins | Fast closures, low effort |
| 08 | Major Initiatives | Multi-process, high-effort improvements |
| 09 | References | ASPICE PAM/PRM, ISO/IEC 33004 |

Always use this skill instead of producing a freeform gap analysis in chat.
