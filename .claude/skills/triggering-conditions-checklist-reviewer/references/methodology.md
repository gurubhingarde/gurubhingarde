# Triggering Conditions Checklist Methodology

## Scoring Conventions

| Rating | Meaning |
|--------|---------|
| FC | Fully Compliant — check verified directly from xlsx |
| LC | Largely Compliant — substantially verified with minor gaps |
| PC | Partially Compliant — significant gaps requiring action |
| NO | Not Compliant — mandatory requirement unmet |
| NA | Not Applicable — check does not apply |
| — | Pending — requires human judgment |

## Six Standard Triggering Condition Categories (ISO 21448 Annex B)

1. **Environmental**: Weather, lighting, visibility, terrain, road surface conditions
2. **Sensor**: Hardware degradation, noise, failure modes, detection range limitations
3. **Road Infrastructure**: Lane markings, road signs, road surface properties
4. **Other Road User**: Pedestrian behavior, cyclist behavior, vehicle behavior
5. **System State**: ECU processing latency, memory constraints, resource contention
6. **Driver State**: Inattention, incapacity, incorrect mode activation, operator skill

## Key Checks

**Check 2-7**: Each of the six categories must be documented with >=3 conditions per category  
**Check 8**: Combined triggering conditions (Cartesian or pairwise) analysis mandatory  
**Check 9-10**: Likelihood and detectability estimates required per condition  
**Check 11**: Mitigation strategy per high-likelihood / low-detectability condition  
**Check 12**: ISO 21448 Annex B referenced for methodology  

## Common Gaps

- Only 3-4 categories covered instead of all 6
- Single triggering conditions documented but no combined analysis
- Likelihood/detectability estimates missing
- No mitigation strategies documented
- ISO 21448 Annex B not cited
