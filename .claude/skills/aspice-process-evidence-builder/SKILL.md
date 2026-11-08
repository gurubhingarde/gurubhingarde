---
name: aspice-process-evidence-builder
description: Generate an ASPICE process evidence package workbook for a single process, documenting base practice evidence, generic practice evidence, work products, performance records, and improvement history. Produces 10 tabs with complete evidence inventory for assessment auditing. Use this skill whenever the user needs to compile process evidence for ASPICE assessment, create process documentation packages, demonstrate practice achievement with artifacts, or prepare for assessor review.
---

# ASPICE Process Evidence Builder

An evidence package documents all artifacts demonstrating a process's achievement against ASPICE practices. This skill produces a per-process evidence inventory with references to work products, project records, and quantitative metrics.

## When to use this skill

Use whenever the user wants to:
- Compile process evidence for ASPICE assessment
- Create auditable evidence documentation
- Document process performance metrics (CL3+)
- Prepare evidence package for assessor review
- Demonstrate practice achievement with artifacts

## Workflow

### Step 1 - Define process scope

Provide:
- Process ID (e.g., SYS.1, SWE.1)
- Process name and purpose
- Process owner and supporting roles
- Process inputs and outputs
- Evidence collection period

### Step 2 - Inventory base practice evidence

For each base practice in the process:
- BP ID and text
- Type of evidence (review records, artifact references, project logs)
- Document/artifact location (file path, database, repository)
- Whether accessible to assessor (Y/N)

### Step 3 - Inventory generic practice evidence

For each generic practice at each capability level:
- GP ID, capability level, and text
- Evidence type
- Location/reference
- Accessibility

### Step 4 - Document work products and records

List these in the input JSON under the top-level keys shown:

| Content | JSON key | Row fields | Tab |
|---------|----------|-----------|-----|
| Work products produced by this process (specifications, code, test results) | `work_products` | `id`, `type`, `location`, `vc`, `owner` | 05 |
| Process performance records (review minutes, action logs) | `performance_records` | `id`, `type`, `date`, `findings`, `location` | 06 |
| Quantitative metrics for CL3+ processes (cycle time, defect rate, etc.) | `quantitative_metrics` | `metric`, `period`, `value`, `target`, `status` | 07 |
| Continuous improvement evidence (lessons learned, process changes) | `improvements` | `id`, `description`, `date`, `impact` | 08 |

All four keys are optional. If `quantitative_metrics` is omitted, tab 07 falls back to a blank
template listing the four standard CL3+ metric names for manual completion; tabs 06 and 08 render
headers only when their keys are absent. See `examples/sample_evidence_input.json` for a fully
populated example.

### Step 5 - Generate

Run from Python:

```bash
python scripts/generate_aspice_evidence.py <input.json> <output.xlsx>
```

### Step 6 - Present to assessor

Use as evidence checklist during assessment interviews.

## Output (10 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Process ID, owner, evidence period |
| 01 | Document Control | Version, approval |
| 02 | Process Description | Purpose, scope, inputs, outputs, roles |
| 03 | BP Evidence | BP ID, evidence type, reference location, accessibility |
| 04 | GP Evidence | GP ID, CL, evidence type, reference, accessibility |
| 05 | Work Products | WP ID, type, location, version control, owner |
| 06 | Performance Records | Review minutes, action logs, metrics, dates |
| 07 | Quantitative Performance | Metrics for CL3+: cycle time, defect rate, completeness |
| 08 | Improvement Log | Process improvements, implementation dates, impact |
| 09 | References | ASPICE PAM/PRM, process standards |

Always use this skill instead of producing a freeform evidence list in chat.
