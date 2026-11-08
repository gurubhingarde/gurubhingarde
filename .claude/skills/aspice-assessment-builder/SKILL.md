---
name: aspice-assessment-builder
description: Generate a multi-tab ASPICE PAM v3.1/v4.0 process assessment workbook with capability level ratings, base practices, generic practices, and process attribute assessments. Produces 13 tabs including Title Page, Document Control, Assessment Scope, Process Reference Model, Process Assessment Model, BP/GP assessments, Capability Level determinations, strengths/weaknesses analysis, and assessor sign-off blocks. Use this skill whenever the user needs to conduct or document an ASPICE process assessment, evaluate process maturity, rate capability levels, or create audit-ready assessment evidence.
---

# ASPICE Assessment Builder

The ASPICE Process Assessment Model (PAM v3.1/v4.0) is the standard for evaluating software and system process capability in automotive development. This skill produces a complete, audit-ready assessment workbook by structuring the evaluation across processes, base practices, generic practices, process attributes, and capability levels.

Each assessment captures evidence against the ASPICE reference practices, rates indicators (N/P/L/F: Not/Partially/Largely/Fully achieved), and aggregates them into process attribute ratings and final capability levels per process.

## When to use this skill

Use whenever the user wants to:
- Conduct an ASPICE v3.1 or v4.0 process assessment
- Rate process capability levels (CL0-CL5)
- Document base practice and generic practice achievement
- Create assessment evidence inventory
- Evaluate process maturity for compliance
- Generate audit-ready assessment reports

## Workflow

### Step 1 - Capture assessment scope

Gather:
1. Project name, document ID, assessment date
2. Assessor and lead assessor names
3. Customer/sponsor
4. Target ASPICE version (v3.1 or v4.0)
5. Process areas in scope (typically SYS.1-5, SWE.1-6, SUP.1/8/9/10, MAN.3/5, ACQ.4)
6. Scope description

### Step 2 - Enumerate processes and practices

For each process in scope:
- Process ID (e.g., SYS.1)
- Process name and purpose
- List outcomes
- List base practices with evidence references
- List generic practices per capability level with evidence

### Step 3 - Rate indicators

For each BP and GP:
- Assign indicator rating: N (Not), P (Partially), L (Largely), or F (Fully) achieved
- Document evidence: review minutes, work product references, project records
- Add assessor notes

### Step 4 - Generate

Run from Python environment with openpyxl:

```bash
python scripts/generate_aspice_assessment.py <input.json> <output.xlsx>
```

### Step 5 - Review and iterate

Present xlsx and confirm:
- BP/GP evidence completeness
- Indicator ratings (N/P/L/F)
- Process Attribute aggregation (PA1.1, PA2.1-2.2, PA3.1-3.2, PA4.1-4.2, PA5.1-5.2)
- Achieved Capability Level per ASPICE rating algorithm

## Output structure (13 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Project, assessor, sponsor, assessment date, ASPICE version |
| 01 | Document Control | Revision history, assessment sign-off |
| 02 | Assessment Scope | Process areas in scope, scope description |
| 03 | Process Reference Model | PRM: process ID, name, purpose, outcomes, owner |
| 04 | Process Assessment Model | PAM: base practices and generic practices per process |
| 05 | BP Assessment | Base practice indicators with evidence and ratings |
| 06 | GP Assessment | Generic practice indicators per CL with evidence and ratings |
| 07 | PA Rating | Process Attribute ratings (PA1.1, PA2.1-2.2, PA3.1-3.2, PA4.1-4.2, PA5.1-5.2) |
| 08 | Capability Level | Achieved CL (0-5) per process from PA aggregation |
| 09 | Capability Profile | Summary bar chart of CL vs target per process |
| 10 | Strengths/Weaknesses | Qualitative observations per process |
| 11 | Assessor Sign-off | Lead assessor and sponsor signature blocks |
| 12 | References | ASPICE PAM/PRM versions, intacs, ISO/IEC 33004 |

## ASPICE rating algorithm (CL determination)

Capability Level is determined from Process Attribute ratings per ASPICE PAM and the ISO/IEC 33020 rating algorithm. To achieve a given level, the process attributes *at* that level must be Largely or Fully achieved (L or F) **and** every process attribute *below* that level must be Fully achieved (F):

- **CL0 (Incomplete)**: Process not performed or fails to achieve CL1
- **CL1 (Performed)**: PA1.1 (Performance) L or F
- **CL2 (Managed)**: PA1.1 F; PA2.1 (Performance Mgmt) and PA2.2 (Work Product Mgmt) L or F
- **CL3 (Established)**: PA1.1, PA2.1, PA2.2 F; PA3.1 (Process Definition) and PA3.2 (Process Deployment) L or F
- **CL4 (Predictable)**: PA1.1-PA3.2 F; PA4.1 (Measurement) and PA4.2 (Control) L or F
- **CL5 (Innovating)**: PA1.1-PA4.2 F; PA5.1 (Innovation) and PA5.2 (Optimization) L or F

Note the "Fully achieved below, Largely-or-Fully at level" rule: it is not enough for a lower attribute to be Largely achieved when claiming a higher level. PA ratings (N/P/L/F) aggregate from BP and GP indicator ratings using weighted evidence. Always use this skill instead of producing a freeform assessment table in chat.
