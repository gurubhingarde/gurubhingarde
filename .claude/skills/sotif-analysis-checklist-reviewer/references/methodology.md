# SOTIF Analysis Checklist Methodology

## Scoring Conventions

| Rating | Meaning | When assigned |
|--------|---------|----------------|
| FC | Fully Compliant | Check verified directly from xlsx content; no gaps |
| LC | Largely Compliant | Check substantially verified; minor gaps or caveats noted |
| PC | Partially Compliant | Check partially met; significant gaps requiring action |
| NO | Not Compliant | Check not met; mandatory requirement unmet |
| NA | Not Applicable | Check does not apply to this project |
| — | Pending | Requires subjective human judgment or external artifact review |

## Confidence Levels

| Level | When assigned | Examples |
|-------|---------------|----------|
| High | Directly verified from xlsx content | "All performance limitations documented"; "ODD defined across 4 dimensions" |
| Medium | Inferred from xlsx with caveat | "Functions enumerated; reviewer to confirm against Item Definition" |
| Low / Draft | Subjective or requires external artifact | "Scenario classification accurate" (subjective); "Triggering conditions complete" (external) |

Drafts are marked with "(Auto-suggest, requires reviewer judgment)" so reviewers know where human attention is needed.

## Obligations

- **Shall**: Mandatory requirement per ISO 21448. A "NO" on a Shall is a major non-conformance.
- **Should**: Recommended per ISO 21448. A "NO" on a Should is a minor non-conformance.

## ISO 21448 Structure

SOTIF Analysis Assessment checks map to ISO 21448:2022 Part 1 "Definition of Item, Operating Scenario and Safety" Clause 6:

- **§6.2.1**: Item Definition and ODD
- **§6.2.2**: Performance limitations
- **§6.2.3**: Functional insufficiencies
- **§6.2.4**: Triggering conditions (environmental, sensor, road, system state, driver state)
- **§6.2.5**: Hazardous behaviors
- **§6.3**: Scenario classification (quadrant: Known Safe / Known Unsafe / Unknown Safe / Unknown Unsafe)
- **§6.4**: Safety measures and acceptance criteria (quantified per safety goal)

## Probe Strategy

The skill uses best-effort keyword matching to detect:
- ODD definition sheets (scenery, environment, dynamics, driver state rows)
- Performance limitations per function
- Functional insufficiencies
- Triggering conditions and their categories
- Hazardous behaviors
- Scenario quadrant classification
- Acceptance criteria and measurability indicators
- Item Definition and standard references

If a sheet contains the expected structure, the probe increments counters and classification counts.

## Checklist Coverage

**14 Confirmation Review checks** cover generic document quality (title, author, revision, TOC, references, completion).

**14 SOTIF Analysis Assessment checks** evaluate:
1. Item Definition referenced
2. ODD definition across 4 dimensions
3. Functional performance specification
4. Performance limitations enumeration
5. Functional insufficiencies cataloging
6. Triggering conditions documentation
7. Triggering condition categories (6 standard: environmental, sensor, road, system, driver)
8. Hazardous behaviors documentation
9. Scenario quadrant classification
10. Acceptance criteria (quantified)
11. ISO 21448 references
12. Out-of-ODD behavior definition
13. Multiple standard citations
14. Unknown Unsafe scenarios flagged and pending mitigation

## Common Gaps

1. **ODD definition incomplete**: Only 2-3 dimensions documented instead of all 4.
2. **Triggering conditions underspecified**: Only 2-3 categories covered instead of 6 standard categories.
3. **Scenario classification missing**: No explicit assignment of scenarios to quadrant (Known Safe vs Unknown Unsafe).
4. **Acceptance criteria not measurable**: Qualitative targets ("low probability") instead of quantified ("< 1e-6 per vehicle-lifetime").
5. **Unknown Unsafe scenarios not tracked**: No explicit list of scenarios pending mitigation or justification.
6. **Performance limitations per function missing**: Generic list instead of function-specific analysis.

## Interpretation Guidelines

- A checklist result of "FC" on Confirmation Review + FSA does NOT automatically grant acceptance of the SOTIF Analysis. Independent review per ISO 21448 organizational independence requirements is still required.
- Pending rows are normal. Subjective checks cannot be auto-filled; the reviewer applies judgment.
- The skill re-runs fresh each time the source SOTIF Analysis is updated; previous checklist edits do not carry forward.
- Use the Recommended Actions column to track what the analyst needs to fix in the source SOTIF Analysis; the skill itself is read-only on the source.
