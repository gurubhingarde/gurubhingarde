# FMEDA Assessment Checks — Detailed Reference

## Confirmation Review (CR) — 14 checks

| # | Section | Requirement | Auto-Verify | Notes |
|---|---------|-------------|------------|-------|
| 1 | Doc Quality | Document structured clearly | Tab count >= 10 | Counts distinct worksheet tabs |
| 2 | Doc Quality | Latest template used | **Draft** (Low conf) | User confirms at doc creation |
| 3 | Doc Quality | Search aids (TOC, Ref) | Tab names for title/ref | Keyword heuristic |
| 4a | Doc Quality | Title covers scope | Draft if title present | Requires subjective review |
| 4b | Doc Quality | Author/Approver listed | Both fields populated | High confidence |
| 4c | Doc Quality | Revision uniquely identified | Revision field set | High confidence |
| 4d | Doc Quality | Change history available | Doc Control tab present | Counts revision rows |
| 4e | Doc Quality | Status provided | Status field set | High confidence |
| 5 | Doc Quality | Current revision identifiable | Revision field set | High confidence (same as 4c) |
| 6 | Doc Quality | Configuration management | **Draft** (Low conf) | Organizational practice |
| 7 | Doc Quality | Headers/footers updated | **Draft** (Low conf) | Manual Excel verification required |
| 8 | Doc Quality | Table of contents correct | Title/Contents tab present | Heuristic |
| 9 | Doc Quality | References complete | References tab present | Draft for completeness |
| 10 | Doc Quality | All sections completed | HW catalog completion % | Counts populated elements |
| 11 | Doc Quality | Document ID unique | Doc ID field set | High confidence |
| 12 | Doc Quality | Project context | Project field populated | Draft if empty |
| 13 | Doc Quality | References complete/traceable | References tab presence | Draft for full audit trail |
| 14 | Doc Quality | All FMEDA sections populated | Core tabs present | Checks for Title, Catalog, Worksheet, Metrics |

## FMEDA Assessment (FMEDAA) — 14 substantive checks

| # | Section | Requirement | ISO Ref | Auto-Verify | Notes |
|---|---------|-------------|---------|------------|-------|
| 1 | Prerequisites | Assumptions documented (mission, FIT, env) | 26262-5:8.1 | All three fields | Checks mission profile, FIT source, env class |
| 2 | HW Catalog | Element catalog complete with FIT | 26262-5:8.2 | Count > 0; all with FIT | PASS if 100% have FIT |
| 3 | Coverage | ASIL-relevant elements in FMEDA | 26262-5:8.3 | Coverage % check | Each safety element has rows |
| 4 | Distribution | Failure mode distributions sum to 100% | 26262-5:8.4 | Sum check ±1% | Per HW element |
| 5 | Classification | All modes classified (Safe/SPF/RF/MPF) | 26262-5:8.5 | 100% coverage | Checks classification field |
| 6 | Mechanisms | Safety-relevant modes have mechanisms | 26262-5:8.6 | Allocation check | SPF/RF/MPF_D/MPF_L require mechanism |
| 7 | DC% Specified | Mechanisms have DC% (no TBD) | 26262-5:8.7 | 0 < DC <= 100 | Checks all mechanisms |
| **8** | **Metric Targets** | **SPFM >= target for ASIL** | **26262-5:8.8** | **COMPUTED vs TARGET** | **HIGH-VALUE: Reads calculated SPFM, compares to ASIL table** |
| **9** | **Metric Targets** | **LFM >= target for ASIL** | **26262-5:8.9** | **COMPUTED vs TARGET** | **HIGH-VALUE: Reads calculated LFM, compares to ASIL table** |
| **10** | **Metric Targets** | **PMHF <= target for ASIL** | **26262-5:8.10** | **COMPUTED vs TARGET** | **HIGH-VALUE: Reads calculated PMHF (FIT), compares to ASIL table** |
| 11 | Reasonableness | Total FIT reasonable for device | 26262-5:8.11 | FIT <= 500 typical | Draft for high FIT |
| 12 | Open Items | No critical pending items | 26262-5:8.12 | Item status check | Flags unresolved blockers |
| 13 | Consistency | Mission consistent with vehicle program | 26262-5:8.13 | **Draft** (Medium conf) | Requires Item Definition cross-check |
| 14 | Justification | FIT source cited (IEC 62380 / FIDES / datasheet) | 26262-5:8.14 | Source text check | Validates citation |

### Checks #8–10: Metric Target Verification (THE HEADLINE VALUE)

These are **headline auto-verifications** that read computed metrics and apply per-ASIL targets:

**SPFM Target (Check #8):**
- ASIL B: >= 90%
- ASIL C: >= 97%
- ASIL D: >= 99%

**LFM Target (Check #9):**
- ASIL B: >= 60%
- ASIL C: >= 80%
- ASIL D: >= 90%

**PMHF Target (Check #10):**
- ASIL B: < 100 FIT
- ASIL C: < 100 FIT
- ASIL D: < 10 FIT

**Reading Metrics:**
Uses `openpyxl.load_workbook(..., data_only=True)` to read evaluated cell values from `10_Metrics_Dashboard` or calculation tabs. Automatically validates against target; returns FC if met, NO if failed.

## Verification Assessment (VA) — 4 checks

| # | Requirement | Status |
|---|------------|--------|
| 1 | Verification Plan ensures FMEDA compliance | **Pending** (external) |
| 2 | Plan addresses methods, criteria, environment | **Pending** (external) |
| 3 | Verification executed per plan | **Pending** (external) |
| 4 | Verification Report with pass/fail | **Pending** (external) |

All VA checks are marked **Pending** because they reference a separate Verification Plan / Report document that lives outside the FMEDA xlsx. Reviewer completes these checks once Verification documentation is available.

## Example: Metric Target Check Flow

```
Input FMEDA xlsx with formulas on 10_Metrics_Dashboard
             |
             v
fmeda_probe.py reads openpyxl(data_only=True)
    Extracts: p.spfm_computed = 92.5%
              p.lfm_computed = 75.0%
              p.pmhf_computed = 8.5 FIT
              p.target_asil = "D"
             |
             v
check_definitions.py::fmedaa_08_spfm_target(p)
    Compare: 92.5% >= 99% (ASIL D target)?
    Result: NO (FAIL)
    Output: "SPFM 92.5% < target 99% for ASIL D"
            "Recommended Action: Increase SPFM via mechanism allocation..."
             |
             v
generate_checklist.py builds row in FMEDA Assessment tab
    Cell Assessment = "NO" (colored red)
    Finding = auto-generated with specific metrics
```
