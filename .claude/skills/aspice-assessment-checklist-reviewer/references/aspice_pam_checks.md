# ASPICE PAM 3.1 Assessment Checks

## Substantive Checks (1-14)

### 1. Lead Assessor Identified
**Shall** identify the lead assessor with INTACS codes referenced.

**Why**: Lead assessor is responsible for assessment quality and independence. INTACS codes verify assessor qualifications per ASPICE guidelines.

**What the skill verifies**:
- Lead Assessor field is populated on Title page
- Evidence from xlsx: field name matching or author fallback

### 2. Process Areas in Scope Documented
**Shall** have all in-scope process areas clearly listed (typical: SYS.1-5, SWE.1-6, SUP, MAN, ACQ).

**Why**: Scope definition is prerequisite for proper assessment execution. Scope drives BP/GP assessment extent.

**What the skill verifies**:
- Assessment Scope tab exists with Process Area column populated
- At least one process area identified

### 3. PRM Correctly Applied per Process
**Shall** apply Process Reference Model correctly (Purpose + Outcomes documented for each in-scope process).

**Why**: PRM provides the normative definition of each process. Correct application ensures assessment against the right standard.

**What the skill verifies**:
- BP Assessment tab is populated with >= 5 rows
- (Reviewer must verify PRM Purpose + Outcomes are present for each process)

### 4. Base Practices Assessed for All In-Scope Processes
**Shall** assess every Base Practice for every in-scope process.

**Why**: BPs are the work activities that realize process outcomes. Missing BP assessment means process realization is not confirmed.

**What the skill verifies**:
- BP Assessment tab exists and has >= 10 rows
- Rating: FC if >= 10 rows, LC if > 0, NO if empty

### 5. Generic Practices Assessed at Target CL
**Shall** assess all Generic Practices relevant to target Capability Level.

**Why**: GPs are the institutionalization activities that support sustainable process performance. Target CL determines which GPs are required.

**What the skill verifies**:
- GP Assessment tab exists and is populated
- >= 5 GP rows detected

### 6. Indicator Ratings Use ASPICE N/P/L/F Scale
**Shall** use the correct ASPICE indicator scale: N (Not Achieved), P (Partially), L (Largely), F (Fully).

**Why**: ASPICE defines a specific rating scale per PA. Deviation could invalidate CL computation.

**What the skill verifies**:
- PA Rating tab uses N, P, L, or F values
- (Reviewer must spot-check for non-standard values)

### 7. PA Ratings Derived per ASPICE Rules
**Shall** derive PA ratings correctly according to ASPICE algorithms.

**Why**: PA ratings are inputs to CL computation. Incorrect derivation leads to false capability claims.

**What the skill verifies**:
- PA Rating tab is populated (>= 5 rows)
- (Reviewer must verify derivation logic against ASPICE rules)

### 8. CL Computed per ASPICE Rating Algorithm
**Shall** compute Capability Level using the ASPICE algorithm (e.g., CL2 requires PA1.1 + PA2.1 + PA2.2 all at L+).

**Why**: ASPICE defines a precise CL computation algorithm. Following it ensures comparable assessments across organizations.

**What the skill verifies**:
- Capability Level tab is present and populated
- CL values detected (e.g., CL0, CL1, CL2, etc.)
- (Reviewer must verify computation against ASPICE algorithm)

### 9. Capability Profile Chart per Process
**Should** present a capability profile chart showing CL for each process (e.g., radar diagram or bar chart).

**Why**: Visual capability profile aids understanding of process maturity across the assessed item/organization.

**What the skill verifies**:
- CL profile tab is present
- (Reviewer must visually inspect chart)

### 10. Target CL Stated per Process
**Shall** explicitly state target Capability Level for each process.

**Why**: Target CL drives the assessment scope and interpretation. Without it, assessment cannot be judged against goals.

**What the skill verifies**:
- Target CL field is populated
- (Reviewer must check Assessment Scope or CL tab for explicit target values)

### 11. Strengths and Weaknesses Documented per Process
**Shall** document strengths and weaknesses for each process.

**Why**: Strengths/weaknesses form the basis for improvement planning and process understanding.

**What the skill verifies**:
- Summary or process-level tabs contain Strengths / Weaknesses sections
- Keywords detected: "strength", "weakness", "finding", "issue", "gap"

### 12. Assessor Signoff Present
**Shall** have assessor signoff (lead + co-assessors + sponsor).

**Why**: Signoff is evidence of assessor responsibility and assessment approval.

**What the skill verifies**:
- Dedicated Signoff or Approval tab exists
- (Reviewer must verify signatures are present)

### 13. Sample Size Adequate
**Should** sample 1-3 projects per process, with representation of complexity and team experience.

**Why**: Adequate sampling ensures evidence is representative and assessment credibility is established.

**What the skill verifies**:
- (Reviewer must check assessment notes for sample sizes)

### 14. Processes Below Target CL (Headline)
**Should** count and highlight processes that fall below their target Capability Level.

**Why**: This headline metric drives improvement planning.

**What the skill verifies**:
- (Reviewer must compare current CL vs target CL per process)

## Validation Checks (VA-1 to VA-5)

### VA-1. Document Structure
**Should** have clear, maintainable structure with multiple tabs for distinct concerns.

**What the skill verifies**: >= 5 sheets present

### VA-2. Title Page Complete
**Shall** populate Author and Approver fields on Title page.

**What the skill verifies**: Both Author and Approver are populated

### VA-3. Revision History Tracked
**Shall** track revisions with unique identifiers.

**What the skill verifies**: Revision field is populated

### VA-4. Assessment Date Documented
**Shall** record the assessment date.

**What the skill verifies**: Assessment Date field is populated

### VA-5. Status Clearly Stated
**Shall** indicate work-product status (Draft / In Review / Released).

**What the skill verifies**: Status field is populated
