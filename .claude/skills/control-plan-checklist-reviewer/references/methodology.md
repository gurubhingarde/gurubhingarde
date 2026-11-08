# Control Plan Checklist Methodology

## Scoring Conventions

### Rating Scale

| Rating | Meaning | Action Required |
|--------|---------|-----------------|
| FC | Fully Compliant | None; requirement satisfied |
| LC | Largely Compliant | Minor gaps that do not prevent use |
| PC | Partially Compliant | Corrective action required before release |
| NO | Not Compliant | Critical gap; must be resolved |
| NA | Not Applicable | Requirement does not apply to this plan |
| Pending | Not Yet Assessed | Awaiting reviewer judgment |

### Confidence Levels

- **High**: Verified directly from xlsx content or standard heuristics
- **Medium**: Inferred from xlsx with reasonable caveat
- **Low**: Subjective or requires external artifact (Verification Plan, PFMEA, etc.)

## Check Categories

The checklist is organized into three categories per AIAG Control Plan standard and IATF 16949:

### 1. Confirmation Review (16 doc-quality checks)

Generic document quality checks aligned with ISO 26262-8 §10 and IATF auditing standards.

**Scope**: Title page, revision history, document structure, section completeness
**Obligation**: Shall/Should
**Auto-fill confidence**: High (mostly machine-verifiable)

### 2. Control Plan Assessment (14 substantive checks)

AIAG Control Plan core requirements per IATF 16949:2016 and ISO 26262-5 §7.

**Scope**: Header block, worksheet completeness, special characteristics, MSA, SPC, reaction plans, poka-yoke, PFMEA linkage
**Obligation**: Shall (critical); Should (important)
**Auto-fill confidence**: High (worksheet structure is mostly machine-verifiable)

### 3. Verification Assessment (8 verification checks)

Testing adequacy per IATF 16949. Most checks (5) are external (refer to separate Verification Plan/Report); 3 are Control-Plan-specific.

**Scope**: Verification Plan content, test specification, control effectiveness, gage GR&R, reaction plan testing, special characteristic testing, poka-yoke testing
**Obligation**: Shall (critical); Should (important)
**Auto-fill confidence**: Low for most items (external docs); High for Control-Plan-specific items

## What This Skill Does

- **Probes** the source Control Plan xlsx (any format; optimized for control-plan-builder output)
- **Runs 36 checks** across three tabs
- **Auto-fills** FC, LC, PC, NO, or NA for machine-verifiable checks (header block, worksheet structure, special characteristics, MSA, SPC, poka-yoke)
- **Drafts** findings for subjective or external items with "(Auto-suggest, requires reviewer judgment)" preface
- **Produces** a 7-tab checklist xlsx with Summary dashboard, detailed findings, and recommended actions
- **Does not modify** the source Control Plan

## What This Skill Does NOT Do

1. **Does not audit** Verification Plan, test cases, or GR&R studies (those are external)
2. **Does not judge** whether controls are *right* for the process (that is engineer judgment)
3. **Does not produce** corrective actions (recommends action direction; human decides implementation)
4. **Does not replace** an independent confirmation review (skill is a workbench tool)

## Common Pitfalls

1. **"NA" and "Pending" rows are normal.**
   - NA: Poka-yoke may not apply to all processes
   - Pending: Verification effectiveness, special characteristic control, etc. require external verification

2. **Most "NO" ratings point at worksheet gaps.**
   - Missing process steps, gages, sample plans, reaction plan references
   - These are fixable by updating the source Control Plan and re-running

3. **Special Characteristics echo from PFMEA.**
   - If PFMEA was not completed, the Special Characteristics tab will be empty
   - This is a PC (not NO) because special characteristics may not exist for all processes

4. **Reaction Plan references require library population.**
   - Every characteristic row references a Reaction Plan ID
   - The library must have an entry for that ID
   - If a characteristic references a plan that doesn't exist, you get a PC rating

5. **SPC allocation is SC (should) for production; may be NA for prototype.**
   - Prototype and pre-launch control plans may not have full SPC setup
   - Mark NA if SPC is not yet required

## Workflow

1. **Get the Control Plan path** — user provides file
2. **Run the skill** — generates checklist in ~5 seconds
3. **Review Summary tab** — scan KPI tiles, compliance %, major issues count
4. **Walk through CR tab** — resolve NO and PC ratings (usually title-page / doc-control hygiene)
5. **Walk through CPA tab** — resolve NO and PC ratings (usually worksheet / library gaps)
6. **Walk through VA tab** — most rows will be Pending (external); focus on Control-Plan-specific items
7. **Iterate** — update source Control Plan, re-run skill, repeat until target compliance reached

## Recommendation: Integration with PFMEA Workflow

For best results, run this skill *after* PFMEA and control-plan-builder have completed:

```
PFMEA → Control Plan Builder → Control Plan Checklist Reviewer
  (high-AP FM)    (derives controls)     (audit-ready)
```

This ensures Special Characteristics are echoed and PFMEA linkage is verifiable.
