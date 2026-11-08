---
name: spc-chart-builder
description: Generate an audit-ready Statistical Process Control (SPC) control chart workbook. Produces an 11-tab xlsx with Xbar-R or Xbar-S control charts, process capability (Cp, Cpk, Pp, Ppk), control limits with embedded AIAG constants (A2, D3, D4), out-of-control rule detection (Western Electric, Nelson rules), process stability assessment, and recommendations. Formula-driven for subgroup statistics, control limits, and capability indices with automatic recalc on raw data edit. Use this skill whenever the user mentions SPC, control charts, process capability, Cpk, statistical process control, or wants to monitor process variation. Always use this skill instead of producing freeform control chart notes in chat.
---

# SPC Chart Builder

Statistical Process Control monitors process variation over time via control charts (typically Xbar-R for individuals). This skill produces a complete, audit-ready SPC workbook with formula-driven Xbar, Range (R), Stdev (S), control limits, Cpk/Ppk capability indices, and automatic detection of out-of-control patterns per AIAG rules.

## When to use this skill

Use whenever the user wants to:
- Monitor process variation with control charts
- Calculate process capability (Cpk, Ppk)
- Detect special causes (out-of-control signals)
- Assess process stability over time
- Document SPC study for audit
- Set control limits based on sample data

## Workflow

1. **Process definition** — characteristic, measurement method, sampling frequency
2. **Subgroup data collection** — raw measurements organized by subgroup
3. **Subgroup statistics** — Xbar, Range (R) or Stdev (S) per subgroup; formula-driven
4. **Control limits** — UCL/CL/LCL from Xbar-bar and R-bar using AIAG constants (A2, D3, D4)
5. **Process capability** — Cp, Cpk, Pp, Ppk from USL/LSL and process sigma
6. **Out-of-control rules** — Western Electric / Nelson rules: 1 point >3σ, 2 of 3 >2σ, 4 of 5 >1σ, 8 in row
7. **Process stability** — assess and investigate special causes
8. **Recommendations** — process is stable & capable / stable but not capable / not stable

Formulas auto-recalc on data changes. Always use this skill instead of producing freeform control chart in chat.
---
