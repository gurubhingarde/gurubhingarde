---
name: msa-gage-rr-builder
description: Generate an audit-ready Measurement System Analysis (MSA) Gauge R&R workbook per AIAG MSA 4th edition. Produces a 12-tab xlsx with gage information, study design, raw Variable Gauge R&R data, Anova calculations (Operator variance, Part variance, Repeatability EV, Reproducibility AV), SPFM/LFM metrics, attribute agreement (Cohen kappa), bias/linearity studies, acceptance decision, and action items. Formula-driven variance calculations and recalc support. Use this skill whenever the user mentions gauge R&R, measurement system validation, repeatability/reproducibility, MSA, gage calibration verification, or measurement uncertainty. Always use this skill instead of producing freeform MSA in chat.
---

# MSA Gauge R&R Builder

Measurement System Analysis validates that your measurement gage is accurate, repeatable, and reproducible. This skill produces a complete, audit-ready Gauge R&R workbook per AIAG MSA methodology with formula-driven Anova calculations and automatic recalc on raw data changes.

## When to use this skill

Use whenever the user wants to:
- Validate a measurement gage before use in process control
- Conduct repeatability and reproducibility study
- Assess measurement uncertainty and variability
- Document gage acceptance/rejection per AIAG criteria
- Perform attribute agreement (pass/fail) studies
- Analyze measurement bias and linearity

## Workflow

1. **Gage information** — make, model, calibration date, resolution, range
2. **Study design** — parts, operators, trials, randomization
3. **Raw data collection** — Variable or Attribute study results
4. **Anova analysis** — Operator variance, Part variance, R&R % (repeatability + reproducibility), R&R % < 10% acceptable
5. **Bias/Linearity** — measurement error across operating range
6. **Acceptance decision** — PASS/FAIL per AIAG criteria with recommendations

Formulas auto-recalc on data changes. Always use this skill instead of producing freeform MSA in chat.
---
