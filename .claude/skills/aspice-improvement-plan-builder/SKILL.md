---
name: aspice-improvement-plan-builder
description: Generate an ASPICE improvement plan workbook from gap analysis, defining initiatives, timeline, resources, risks, KPIs, and stakeholder communication. Produces 11 tabs covering improvement roadmap, resource allocation, Gantt-style timeline, risk register, pilot planning, and KPI tracking. Use this skill whenever the user needs to plan and execute ASPICE process improvement initiatives, create capability improvement budgets, establish improvement governance, or track progress against process maturity targets.
---

# ASPICE Improvement Plan Builder

An improvement plan operationalizes gap-analysis findings into a managed, tracked improvement program with timeline, resources, governance, and success metrics. This skill structures improvement from gaps through pilot execution and scaling.

## When to use this skill

Use whenever the user wants to:
- Create an ASPICE improvement program plan
- Allocate resources and budget for capability improvement
- Schedule improvement initiatives with dependencies
- Track improvement progress with KPIs
- Execute improvement pilots and scale lessons learned

## Workflow

### Step 1 - Gather gap analysis output

Review the output from aspice-gap-analysis-builder (gaps, severity, effort estimates)
and transcribe the gap rows into the `processes` key of the input JSON. The generator
reads gaps from the JSON only; it does not open the gap-analysis workbook.

### Step 2 - Define initiatives

For each initiative:
- Initiative ID and name
- Gaps addressed (map to gap IDs)
- Owner and team composition
- Estimated duration and budget
- Success criteria

### Step 3 - Plan timeline and resources

Build:
- Roadmap timeline (Gantt-style month grid)
- Resource allocation per initiative (FTE, training, tools, consultant)
- Budget summary
- Dependencies between initiatives

### Step 4 - Risk and stakeholder planning

Define:
- Risks to improvement program (likelihood, impact, mitigation)
- Stakeholder communication plan (audience, message, channel, frequency)
- Pilot project scope and success criteria

### Step 5 - Generate

Run from Python:

```bash
python scripts/generate_aspice_improvement_plan.py <input.json> <output.xlsx>

# Legacy 3-argument form is still accepted; the leading workbook is ignored with a warning:
# python scripts/generate_aspice_improvement_plan.py <gap_analysis.xlsx> <input.json> <output.xlsx>
```

### Step 6 - Execute and track

Use KPIs and communication plan to manage program execution and measure success.

## Output (11 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Program name, sponsor, target completion |
| 01 | Document Control | Revision, approval |
| 02 | Gaps from Analysis | Read-only echo of gaps transcribed into the input JSON `processes` key |
| 03 | Initiatives | Initiative ID, gaps, owner, duration, budget |
| 04 | Roadmap | Gantt-style timeline (initiative x month) |
| 05 | Resources/Budget | Resource types, costs, timeline |
| 06 | Risk Register | Program risks, likelihood, impact, mitigation |
| 07 | KPIs | Baseline, targets, current values, status |
| 08 | Communication Plan | Audience, message, channel, frequency |
| 09 | Pilot Plan | Pilot scope, success criteria, learnings to scale |
| 10 | References | ASPICE standards, process improvement guides |

Always use this skill instead of producing a freeform improvement plan in chat.
