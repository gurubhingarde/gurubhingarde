# ASPICE Assessment Review Methodology

## Assessment Confirmation Scope

This checklist covers ASPICE PAM 3.1 Assessment requirements across:

1. **Assessment Initiation** — lead assessor identification, scope definition
2. **Assessment Execution** — PRM application, BP/GP assessment
3. **Assessment Analysis** — PA rating derivation, CL computation
4. **Assessment Reporting** — findings documentation, signoff

## Rating Scale

| Rating | Meaning | When assigned |
|--------|---------|---------------|
| FC     | Fully Compliant | Requirement met; supporting evidence found |
| LC     | Largely Compliant | Requirement mostly met; minor gaps noted |
| PC     | Partially Compliant | Requirement partially met; significant gaps |
| NO     | Not Compliant | Requirement not met; major gap |
| NA     | Not Applicable | Requirement does not apply |
| —      | Pending | Requires reviewer judgment |

## Confidence Levels

- **High**: Verified directly from xlsx content (e.g., "Sheet exists", "Row count = N")
- **Medium**: Inferred from xlsx with caveat (e.g., "BP Assessment present; reviewer to confirm PRM Purpose + Outcomes per process")
- **Low**: Subjective or requires external artifact (e.g., "Target CL stated" — need to review actual values)

## Obligation Scale

- **Shall**: Mandatory requirement per ASPICE PAM 3.1. A NO on Shall is a major non-conformance.
- **Should**: Recommended best practice. A NO on Should is a minor non-conformance.

## ASPICE PAM 3.1 Key Concepts

### Process Areas
Grouped by:
- **System level**: SYS.1 (Stakeholder Requirements Definition) through SYS.5
- **Software level**: SWE.1 (Software Requirement Analysis) through SWE.6
- **Supporting**: SUP.1 (Quality Assurance) through SUP.5
- **Management**: MAN.1 (Project Planning) through MAN.5
- **Acquisition**: ACQ.1 through ACQ.5

### Base Practices (BP)
Work activities that realize process outcomes. Every in-scope process must have its BPs assessed.

### Generic Practices (GP)
Practices that support institutionalization at each Capability Level:
- **CL1**: N/A (capability not addressed)
- **CL2**: GP1.1 (Process Performance)
- **CL3**: GP2.1 (Work Products), GP2.2 (Correct Assignment)
- **CL4**: GP3.x (Quantitative Management)
- **CL5**: GP4.x (Process Optimization)

### Process Attributes (PA)
Measurable characteristics of a process at each level:
- PA1.1 — Process Performance
- PA2.1 — Performance Management
- PA2.2 — Work Product Management

### Capability Level (CL) Computation
Per ISO/IEC 15504:
- **CL2**: Requires PA1.1 + (PA2.1 AND PA2.2) all at Largely Achieved (L) or Fully Achieved (F)
- **CL3**: Adds PA3.1 + PA3.2 at L+
- And so on

## Indicator Rating Scale (Assessed Per PA)

| N | P | L | F |
|---|---|---|---|
| Not Achieved (0-15%) | Partially Achieved (15-50%) | Largely Achieved (50-85%) | Fully Achieved (85-100%) |

## Assessment Evidence

Assessment evidence should support:
1. **Process documentation** — process description, work instructions
2. **Work products** — requirements, designs, code, test results
3. **Review records** — assessment notes, interview summaries, sample project reviews
4. **Metrics** — schedule adherence, defect density, effort tracking

## Sample Size Guidance

Typical minimum per process:
- **CL2**: 1-2 projects
- **CL3+**: 2-3 projects

Sample should cover representative item/project complexity and team experience levels.

## Independence Requirements

Per ASPICE PAM 3.1, assessment independence levels:
- **I1**: Individual assessor (not involved in assessed processes)
- **I2**: Assessment team (lead + co-assessors, mixed independence)
- **I3**: Organizational unit (separate from assessed organization)

Independence requirements increase with ASIL / process criticality.
