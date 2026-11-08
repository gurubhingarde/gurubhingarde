# Confirmation Independence Levels (ISO 26262-2 Table 1)

## What is Confirmation Independence?

Confirmation is the process of verifying that a safety-critical work product (e.g., HARA, FSC, TSC, design specification, verification report) is correct, complete, and ready for the next phase. Confirmation independence ensures that the reviewer has sufficient organizational separation from the author to provide an objective assessment.

ISO 26262-2 Clause 6.2.5 defines THREE LEVELS of confirmation independence, based on the target ASIL:

## Independence Levels

### I1: Different Person (ASIL A, B)

**Definition:** The confirmer is a different individual from the author, but may be in the same department/team and report to the same manager.

**Organizational structure:**
```
Manager
├── Author (e.g., SW Architect)
└── Confirmer (e.g., another SW engineer, HW engineer, or project lead)
```

**When required:** ASIL A and ASIL B items

**Rationale:** At lower ASILs, the primary check is that work is thorough and internally consistent. Different eyes catch obvious omissions and inconsistencies. No organizational separation is needed because the risk is moderate and the overall verification strategy provides adequate rigor.

**Evidence for audit:** Document the confirmer's name and organization in the Confirmation Reviews tab.

### I2: Different Team (ASIL C)

**Definition:** The confirmer is in a DIFFERENT TEAM or DEPARTMENT from the author. Both may work at the same site and for the same company, but report to different managers.

**Organizational structure:**
```
Director 1                    Director 2
├── Team A (Author)           ├── Team B (Confirmer)
└── Manager A                 └── Manager B
```

**When required:** ASIL C items

**Rationale:** At ASIL C, the risk is significant (severe injury credible). The review must include both technical depth and independence. A different team ensures that the confirmer has no conflicting incentives (e.g., schedule pressure) and brings fresh perspective.

**Evidence for audit:** Document the confirmer's name, team/department, and manager in the Confirmation Reviews tab. Show org chart or reporting structure.

### I3: Different Organisational Unit (ASIL D)

**Definition:** The confirmer is in a DIFFERENT ORGANIZATIONAL UNIT from the author. This typically means:
- Different business division or subsidiary, OR
- Different external supplier/partner, OR
- Customer-appointed reviewer

Confirmer reports to a different VP/Director and has no reporting relationship to the author's manager.

**Organizational structure:**
```
Company A                     Company B (Supplier/Partner)
├── Division X                ├── Engineering Dept
│   └── Team (Author)         └── Confirmer (Independent)
```

**When required:** ASIL D items

**Rationale:** At ASIL D, the risk is life-threatening or fatal. The confirmation process must be robust enough to catch subtle design flaws and corner-case failures. Organizational independence ensures that the confirmer:
- Has no schedule pressure from the development project
- Can escalate concerns without reporting to the author's management
- Can request independent testing or analysis if needed
- Is accountable to a different entity (e.g., customer, different company)

**Evidence for audit:** Document the confirmer's name, external organization, and appointment letter (if customer-appointed). Show org chart with separate reporting lines.

## Implementation Table

| ASIL | Required Independence | Confirmer Selection | Typical Role | Same Site? | Same Company? |
|---|---|---|---|---|---|
| QM | None (recommended I1) | Project lead, peer reviewer | PM, team lead | Yes | Yes |
| A | I1 (different person) | Peer engineer, tech lead | SW engineer, HW engineer | Yes | Yes |
| B | I1 (different person) | Peer engineer, tech lead | SW engineer, HW engineer | Yes | Yes |
| C | I2 (different team) | Different team/department | Quality lead, verification lead | Typically yes | Yes |
| D | I3 (different org unit) | External supplier, partner, or customer | Supplier representative, customer's independent assessor | No (often external) | No (often external) |

## Example Scenarios

### Scenario 1: ASIL D Yaw Control Safety Plan (Company A developing for Customer Z)

- **Author:** John (Company A, SW Architecture Lead)
- **Manager:** Alice (Company A, SW Director)
- **Required Independence:** I3

**Acceptable confirmers:**
- Bob from Company B (external supplier, quality assurance role) — different company ✓
- Carol from Customer Z (customer-appointed reviewer) — different company ✓
- Dave from Company A's separate quality unit (reports to Quality VP, not SW VP) — different org unit within same company ✓

**NOT acceptable:**
- Eve from Company A's SW team (reports to Alice) — same team ✗
- Frank from Company A's HW team (reports to Alice or same VP) — same organizational unit ✗

### Scenario 2: ASIL C System Verification Plan (Company X)

- **Author:** Pat (Company X, Verification Lead, System Testing Department)
- **Manager:** Quinn (Company X, System Testing Manager)
- **Required Independence:** I2

**Acceptable confirmers:**
- Riley from Company X's Requirements/Analysis Department (reports to different manager) — different team ✓
- Sam from Company X's HW Integration Department (reports to different manager) — different team ✓

**NOT acceptable:**
- Terry from Company X's System Testing Department (same team) ✗
- Uma (external supplier) — I3 exceeds requirement, but is acceptable if forced ✓ (over-qualified)

### Scenario 3: ASIL B HARA for Brake Pedal Sensor (Company Y, in-house development)

- **Author:** Victor (Company Y, Safety Analyst)
- **Manager:** Wendy (Company Y, Safety Engineering Manager)
- **Required Independence:** I1

**Acceptable confirmers:**
- Xavier from Company Y's Safety Engineering team (different person, same team) ✓
- Yuri from Company Y's Systems team (different person, different team) ✓

**NOT acceptable:**
- Zoe (external assessor) — over-qualified but acceptable ✓

## Audit Red Flags

Auditors specifically look for:

1. **Independence mismatch:** Confirmer assigned is not independent enough for the target ASIL. Example: ASIL D work confirmed by a peer in the same team (I1 assigned, I3 required).
2. **Confirmation incomplete:** Work product status shows "Complete" but no confirmation date/sign-off. Example: HARA marked "Complete" but Confirmation Reviews tab shows "Not Started".
3. **No org chart:** Claims of I3 or I2 independence but no documentation of reporting structure or supplier/customer relationship.
4. **Self-confirmation:** Author and confirmer are the same person. This violates I1 minimum.
5. **Latent conflicts:** Confirmer reports to author's manager or shares performance goals (e.g., both on same bonus pool). This undermines independence.

## How to Document Independence in the Safety Plan

**In the Confirmation Reviews tab:**
- **Row:** One per work product (or per review point)
- **Required Independence column:** Auto-populated per ASIL (I1/I2/I3)
- **Assigned Reviewer column:** Name of the actual person (or external entity)
- **Notes column:** If I2 or I3, explain the organizational separation (e.g., "Different department — reports to Quality VP, not SW VP" or "External supplier XYZ, ref: Purchase Order 12345")

**In the Roles and Responsibilities tab:**
- **Independence Level column:** For each role, confirm their independence level relative to the author roles
  - Example: "Confirmation Reviewer: I2 (Quality Department, reports to VP Operations, independent of Development)"

**Supporting evidence:**
- Org chart (appendix)
- Purchase orders or supplier contracts (for I3 external reviewers)
- Customer appointment letter (for I3 customer-appointed reviewers)
- Email or memo confirming reviewer assignment and independence

## Waivers and Exceptions

In exceptional circumstances (e.g., small project, startup, isolated safety-critical function), a project may request a WAIVER to use lower independence than required.

**Waiver approval process:**
1. Document the requirement (e.g., "ASIL C requires I2, but only I1 available")
2. Justify the waiver (e.g., "Project size prevents I2 separation; mitigation: external assessor will audit the review at final assessment gate")
3. Identify mitigation measures (e.g., increased documentation, customer review, automated analysis)
4. Get explicit approval from the Functional Safety Manager AND the customer (if applicable)
5. Document in the Safety Plan (04_Tailoring or 09_Anomaly_Resolution)

Waivers are NOT encouraged and are a red flag for auditors — they imply increased risk that must be offset by stronger compensating controls.

## Summary Table for Quick Reference

| ASIL | Minimum Independence | Rule | Confirmer Can Be |
|---|---|---|---|
| QM | None (I1 recommended) | No requirement | Anyone (peer recommended) |
| A | I1 | Different person | Colleague in same team |
| B | I1 | Different person | Colleague in same team |
| C | I2 | Different team | From different department/manager |
| D | I3 | Different org unit | External supplier/partner or different company division |
