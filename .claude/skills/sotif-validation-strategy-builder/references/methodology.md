# SOTIF Validation & Verification Methodology

ISO 21448 Sections 10-11 define validation as demonstrating residual risk of Unknown Unsafe scenarios is acceptable.

## Validation Methods

1. **Real-World Driving** — Natural exposure; fleet data collection
2. **Simulation** — Controlled scenario reproduction; fast iteration
3. **Proving Ground** — Repeatable closed-course scenarios
4. **HIL/SIL Testing** — Offline algorithm validation

## Scenario Quadrant Mapping

- **Known Safe** → Design verification; no additional validation required
- **Known Unsafe** → Design already mitigated; confirm mitigation effectiveness
- **Unknown Safe** → Document via fleet data; low priority
- **Unknown Unsafe** → PRIMARY VALIDATION TARGET; use all methods to reduce residual risk

## Acceptance Criterion Tracking

Cumulative evidence (mileage, simulation runs, test passes) is tracked against quantified acceptance threshold (e.g., residual unintended behavior rate <1e-7 per operating hour).
