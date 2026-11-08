# Verification Assessment Checks

These checks live in the TOMCO checklist's Verification Assessment tab. They are split into:

- **#24–30** — Generic verification planning, specification, execution, and reporting requirements (ISO 26262-8 Clause 9). These typically refer to a separate Verification Plan / Specification / Report document, NOT the HARA xlsx itself.
- **#31–32** — Verification execution and report content requirements.
- **#33a–33e** — HARA-specific verification checks (completeness, consistency, ASIL coherence).

## Generic verification checks (#24–32)

For most HARAs, the verification artifacts are separate from the HARA xlsx. The skill marks these checks "(Reviewer to verify against external Verification Plan / Spec / Report)" and assigns rating "—" (pending), unless the HARA xlsx contains a Verification tab the skill can recognize.

| # | Requirement (paraphrased)                                          | Obligation | Auto-fill confidence | What the skill checks                                |
|---|---------------------------------------------------------------------|------------|----------------------|------------------------------------------------------|
| 24| Verification Plan ensures compliance & consistency with FSC + arch  | Shall      | Low                  | Drafts finding pointing to (external) Verification Plan |
| 25| Safety Validation refined based on TSRs                              | Should     | NA (TSC scope)       | Marks NA — belongs to TSC review                     |
| 26a–g| Verification Plan addresses content, methods, pass/fail, env, tools, anomalies, regression | Shall | Low | Drafts finding; reviewer to check |
| 27a–d| Verification planning considers method adequacy, complexity, prior experience, technology maturity | Should | Low | Drafts finding |
| 28a–c| Verification methods specified: review checklists, simulation, test cases | Shall | Low | Drafts finding |
| 29a–f| Test case specification includes ID, version ref, preconditions, env, inputs, expected behavior | Shall | Low | Drafts finding |
| 30a–c| Test case grouping with environment, dependencies, resources         | Shall | Low | Drafts finding |
| 31| Verification executed per plan and specification                     | Shall | Low | Drafts finding |
| 32a–f| Verification Report includes ID, plan ref, environment config, compliance level, pass/fail statement, skip reasons | Shall | Low | Drafts finding |

## HARA-specific verification checks (#33a–33e)

These are the only verification checks the skill can attempt against the HARA xlsx itself.

| # | Requirement                                                                          | Obligation | Auto-fill confidence | What the skill checks                                            |
|---|--------------------------------------------------------------------------------------|------------|----------------------|------------------------------------------------------------------|
| 33a| Completeness with regard to situations                                              | Shall      | High                 | Verifies operating environment count; expects sufficient diversity |
| 33b| Compliance with the item definition                                                  | Shall      | Medium               | Cross-checks function list against scope_description tokens       |
| 33c| Consistency with related hazard analyses                                             | Shall      | Low (draft)          | Cannot detect; drafts finding                                    |
| 33d| Completeness of the coverage of the hazardous events                                 | Shall      | High                 | Verifies the Cartesian function × malfunction × env is full       |
| 33e| Consistency of assigned ASILs with the corresponding hazardous events                | Shall      | High                 | Recomputes ASIL from S/E/C and compares to recorded ASIL          |

## Important note

When the HARA was produced by `hara-builder`, the ASIL is formula-driven (the HARA tab uses INDEX/MATCH against the ASIL Matrix tab). In that case, check 33e cannot fail by construction — the recorded ASIL will always match the recomputed value because they are the same value. The skill notes this in the Findings cell so the auditor sees that the consistency is structural.
