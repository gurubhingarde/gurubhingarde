# Functional Safety Assessment Checks (HARA Substantive)

These checks are the HARA-specific items from ISO 26262-3:2018 Clause 7 (Hazard Analysis and Risk Assessment). The TOMCO checklist groups them by sub-clause:

## Prerequisites (FSA #1–2)

| # | Requirement                                                                                              | Obligation | Auto-fill confidence | What the skill checks                                            |
|---|----------------------------------------------------------------------------------------------------------|------------|----------------------|------------------------------------------------------------------|
| 1 | Item Definition available and useful                                                                     | Shall      | Medium               | Drafts finding pointing to scope_description / boundary tab      |
| 2 | Further supporting information (impact analysis, info on independent items) considered                   | Should     | Low (draft)          | Cannot verify from HARA xlsx alone                               |

## Initiation of HARA (FSA #3–4)

These mention "technical safety requirements" and "external system interfaces" — likely template inheritance from a TSC checklist. The skill marks these "(Reviewer to verify; appears to belong to TSC review, not HARA)".

## Situation Analysis and Hazard Identification (FSA #5–10)

| # | Requirement                                                                                              | Obligation | Auto-fill confidence | What the skill checks                                            |
|---|----------------------------------------------------------------------------------------------------------|------------|----------------------|------------------------------------------------------------------|
| 5 | Operational situations and modes (correct + incorrect use) described                                     | Shall      | High                 | Inspects Operating Environment tab for location + weather rows   |
| 6 | Adequate techniques used to systematically determine all hazards                                         | Shall      | High                 | Counts unique malfunctions evaluated per function; expects 14    |
| 7 | Hazards defined in terms of vehicle-level conditions / behavior                                          | Shall      | Medium               | Inspects Hazardous Event column for vehicle-level language       |
| 8 | Hazardous events determined for all relevant combinations of situations and hazards                       | Shall      | High                 | Verifies the Cartesian (function × malfunction × env) is present |
| 9 | All consequences of hazardous events identified                                                          | Shall      | Medium               | Drafts finding referencing the hazardous event description col   |
| 10| Measures to mitigate hazards outside ISO 26262 scope highlighted and reported                             | Should     | Low (draft)          | Cannot verify; drafts finding                                    |

## Classification of Hazardous Events (FSA #10–17)

Note: TOMCO numbers two rows as #10 (one in Hazard ID, one here in Classification). The skill uses the row index to disambiguate, not the printed ID.

| # | Requirement                                                                                              | Obligation | Auto-fill confidence | What the skill checks                                            |
|---|----------------------------------------------------------------------------------------------------------|------------|----------------------|------------------------------------------------------------------|
| 10b| All identified hazardous events classified                                                              | Shall      | High                 | Verifies every HARA row has S, E, C populated                    |
| 11| Severity estimated with rationale, assigned S0–S3                                                        | Shall      | High                 | Verifies S column populated and S Rationale non-empty per row     |
| 12| S0 used only when malfunction limited to material damage; no further analysis required                   | Shall      | Medium               | Checks no S0 rows have downstream safety goals                    |
| 13| Probability of exposure estimated with rationale, assigned E0–E4                                         | Shall      | High                 | Verifies E column populated and E Rationale non-empty per row     |
| 14| Probability of exposure does NOT account for number of vehicles equipped                                  | Shall      | Low (draft)          | Cannot verify mathematically; drafts finding citing E rationale   |
| 15| E0 assigned for situations extremely unusual / incredible, not followed up                                | Shall      | High                 | Verifies E0 rows have no safety goal derived                      |
| 16| Controllability estimated with rationale, assigned C0–C3                                                 | Shall      | High                 | Verifies C column populated and C Rationale non-empty per row     |
| 17| Hazards addressing item unavailability handled with appropriate justification                             | Should     | Low (draft)          | Drafts finding for human review                                  |

## Determination of ASIL and Safety Goals (FSA #18–23)

| # | Requirement                                                                                              | Obligation | Auto-fill confidence | What the skill checks                                            |
|---|----------------------------------------------------------------------------------------------------------|------------|----------------------|------------------------------------------------------------------|
| 18| ASIL determined for each hazardous event using S, E, C                                                   | Shall      | High                 | Verifies ASIL column populated for every row with non-S0 / non-E0|
| 19| Level of detail of operational situations does not lower ASIL inappropriately                             | Should     | Medium               | Checks env granularity; drafts finding                           |
| 20| Safety goal determined for each hazardous event with ASIL ≥ A; similar SGs combined                       | Shall      | High                 | Verifies Safety Goals tab has SG for every ASIL ≥ A row          |
| 21| When SGs combined, highest ASIL assigned                                                                 | Shall      | High                 | Verifies Worst-case ASIL column on Safety Goals tab               |
| 22| If safety goal achieved by safe state, safe states specified                                              | Shall      | High                 | Verifies every SG row has Safe State column populated             |
| 23| Safety goals attributes specified per ISO 26262-8:2011 Clause 6                                          | Should     | Medium               | Verifies SG ID, ASIL, text, safe state present                    |

## Confidence rationale

"High" means the check is purely structural — does the cell exist and is it non-empty? "Medium" means there's an automatable proxy but a human should confirm semantic correctness. "Low" means the requirement is about external artifacts or organizational practices the xlsx cannot reveal.
