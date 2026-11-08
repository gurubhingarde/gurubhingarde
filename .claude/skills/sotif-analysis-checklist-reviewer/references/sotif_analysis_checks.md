# SOTIF Analysis Assessment Checks (ISO 21448 §6)

## Check 1: Item Definition Referenced

**Requirement**: Is the Item Definition referenced with version?  
**Obligation**: Shall

Verifies that the SOTIF Analysis explicitly references the Item Definition document (system, ECU, function) with version number. This ensures traceability between requirements and analysis.

**What the skill looks for**:
- An Item Definition tab or reference sheet
- Keywords: "Item Definition", "System Requirements", "Functional Specification"
- Version/revision number

## Check 2: ODD Defined Across Four Dimensions

**Requirement**: Is ODD defined across scenery, environment, dynamics, and driver state?  
**Obligation**: Shall

ODD (Operational Design Domain) must cover all four dimensions per ISO 21448 §6.2.1:
- Scenery (urban/highway/rural, speed limits, parking)
- Environment (weather, lighting, road conditions)
- Dynamics (vehicle state, other road users, traffic patterns)
- Driver state (awake/drowsy, sober/impaired, skill level)

**What the skill looks for**:
- ODD or Operating Design Domain tab
- Rows or sections labeled with category keywords
- >=1 entry per dimension

## Checks 3-4: Performance and Functional Performance

**Requirement**: Are functional performance specifications and limitations documented per function?  
**Obligation**: Shall

Each function must have documented:
- Nominal performance (what it does when working correctly)
- Performance limitations (what it cannot do, or does degraded)

Examples: ACC min/max speed limits, detection range at low light, yaw rate limits.

**What the skill looks for**:
- Performance or Specification tab
- Function name + limitation pairs
- >=3 functions with limitations

## Check 5: Functional Insufficiencies Cataloged

**Requirement**: Are functional insufficiencies identified and documented?  
**Obligation**: Shall

A functional insufficiency is a condition where the function cannot be performed or is performed inadequately due to trigger events outside expected operation.

**What the skill looks for**:
- Insufficiency or Malfunction tab
- Function name + insufficiency description pairs
- >=2 insufficiencies per function

## Check 6: Triggering Conditions Documented

**Requirement**: Are triggering conditions documented per insufficiency?  
**Obligation**: Shall

For each insufficiency, identify all conditions (environmental, sensor, road, system, driver) that could trigger it.

**What the skill looks for**:
- Triggering Conditions tab
- Insufficiency + trigger pairs
- >=10 triggers across all insufficiencies

## Check 7: Standard Triggering Condition Categories

**Requirement**: Are six standard triggering condition categories covered?  
**Obligation**: Shall

Categories per ISO 21448 Annex B:
1. Environmental (weather, lighting, visibility, terrain)
2. Sensor (hardware limits, degradation, failure)
3. Road infrastructure (lane markings, signs, road surface)
4. Other road user (pedestrian, cyclist, vehicle behavior)
5. System state (ECU processing, memory, latency)
6. Driver state (inattention, incapacity, wrong mode activation)

**What the skill looks for**:
- >=4 of the 6 categories explicitly documented

## Check 8: Hazardous Behaviors Documented

**Requirement**: Are hazardous behaviors (function × insufficiency × trigger) documented?  
**Obligation**: Shall

A hazardous behavior is the unintended, inadequate, or missing behavior that results from a triggering condition.

**What the skill looks for**:
- Hazardous Behavior or Scenario Behavior tab
- >=5 behaviors documented

## Check 9: Scenario Quadrant Classification

**Requirement**: Is each scenario assigned to a quadrant (Known Safe / Known Unsafe / Unknown)?  
**Obligation**: Shall

Classification:
- **Known Safe**: Scenario analyzed, trigger mitigated, safe
- **Known Unsafe**: Scenario analyzed, hazard identified, awaiting mitigation
- **Unknown Safe**: Scenario identified but analysis incomplete; presumed safe pending validation
- **Unknown Unsafe**: Scenario identified but analysis incomplete; potential hazard pending validation

**What the skill looks for**:
- Scenario or Quadrant tab
- Each scenario has an explicit quadrant assignment
- All 4 quadrants present in the analysis

## Check 10: Acceptance Criteria Quantified

**Requirement**: Is a measurable acceptance criterion stated per safety goal?  
**Obligation**: Shall

Examples:
- "Residual unintended behavior rate < 1e-6 per vehicle-lifetime"
- "False positive rate < 1% over validation fleet"
- "Latency < 200 ms in 99.9th percentile"

**What the skill looks for**:
- Acceptance Criteria or Safety Goals tab
- Criteria with numerical thresholds, not qualitative statements
- >=80% of criteria measurable

## Check 11: ISO 21448 References

**Requirement**: Are ISO 21448 and applicable standards referenced?  
**Obligation**: Shall

SOTIF Analysis must cite ISO 21448 and any other applicable standards (OEM requirements, regional regulations).

**What the skill looks for**:
- References tab or section
- "ISO 21448" or "SOTIF" mentioned >=2 times

## Check 12: Out-of-ODD Behavior Defined

**Requirement**: What happens when ODD boundaries are crossed?  
**Obligation**: Shall

Define behavior if:
- Vehicle operates outside documented ODD (e.g., in snow, fog, unmapped region)
- Triggers fail (e.g., all sensors degraded)

**What the skill looks for**:
- "Out-of-ODD" or "ODD Boundary" tab/section
- Explicit statement of fallback behavior (safe state, warning, degradation)

## Check 13: Multiple Standard Citations

**Requirement**: Are multiple applicable standards and regulations cited?  
**Obligation**: Should

Examples: ISO 21448 (SOTIF), ISO 26262 (FSA), ISO 23601 (HMI), regional safety standards.

**What the skill looks for**:
- >=3 standards or regulatory references

## Check 14: Unknown Unsafe Scenarios Flagged

**Requirement**: Are Unknown Unsafe scenarios identified and tracked for mitigation?  
**Obligation**: Shall

Unknown Unsafe scenarios represent potential hazards identified but not yet fully analyzed. They require explicit mitigation strategy or justification (e.g., "validation will confirm safe").

**What the skill looks for**:
- Count of scenarios in "Unknown Unsafe" quadrant
- If >0, recommendation for mitigation or validation plan
- Each Unknown Unsafe scenario has an owner and planned action
