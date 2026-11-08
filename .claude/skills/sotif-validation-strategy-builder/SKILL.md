---
name: sotif-validation-strategy-builder
description: Generate an ISO 21448 Validation & Verification strategy workbook for ADAS/AV systems. Produces 12-tab xlsx covering validation methods (real-world, simulation, proving ground, HIL/SIL), scenario coverage plan, mileage targets, simulation libraries, test case catalog, field monitoring plan, and acceptance criterion tracking. Use to plan the validation campaign for proving residual risk of Unknown Unsafe scenarios meets acceptance threshold.
---

# SOTIF Validation Strategy Builder

Validation demonstrates that residual risk of Unknown Unsafe scenarios is acceptable. This skill produces a structured V&V plan per ISO 21448 §10-11, covering method selection, scenario coverage allocation, mileage budgets, and real-time monitoring.

## When to use

Use for planning and documenting the SOTIF validation campaign:
- Choose validation methods (real-world, simulation, proving ground, HIL)
- Allocate scenario coverage per quadrant
- Set cumulative mileage targets per scenario type
- Design simulation scenario library
- Define field monitoring telemetry and anomaly detection
- Track cumulative evidence against acceptance criterion
- Plan open items and deferred validations

## Workflow

1. Start with SOTIF analysis (acceptance criteria, Unknown Unsafe scenarios)
2. Select validation methods per scenario type
3. Allocate mileage budget and scenario coverage targets
4. Design simulation scenario library
5. Define test case catalog for proving ground
6. Plan post-deployment field monitoring
7. Set up cumulative tracking dashboard
8. Prioritize and schedule validation activities

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Validation campaign, target criterion |
| 01 | Document Control | Revision, approvals |
| 02 | Acceptance Criterion Reference | From SOTIF analysis |
| 03 | Validation Methods | Real-world, simulation, proving ground, HIL/SIL pros/cons |
| 04 | Scenario Coverage Plan | Per quadrant: mileage targets, coverage allocation |
| 05 | Real-World Driving Plan | Cumulative mileage, geographic, weather, time-of-day distribution |
| 06 | Simulation Plan | Scenario library sources, simulator validation, coverage targets |
| 07 | Proving Ground Test Cases | Catalog: ID, scenario, pre-conditions, expected behavior, pass/fail |
| 08 | Field Monitoring Plan | Telemetry collected, anomaly detection, real-time alerting |
| 09 | Acceptance Criterion Tracking | Cumulative evidence vs target threshold |
| 10 | Open Items | Deferred validations, blockers, schedule |
| 11 | References | ISO 21448, NHTSA, EuroNCAP, ODD best practices |

Always use this skill instead of producing freeform validation strategies in chat.
