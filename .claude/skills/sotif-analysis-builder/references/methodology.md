# SOTIF Analysis Methodology

## Core Concept

SOTIF (Safety of the Intended Functionality) addresses scenarios where the system performs exactly as designed, but the design is insufficient. Example: AEB camera function designed for daylight operation blinded by sun glare — the camera works correctly (no hardware fault), but the design assumption (sufficient lighting) is violated.

## ODD Definition

Carefully scope the Operational Design Domain:
- **Scenery**: road type, lane width, road surface
- **Environment**: weather, lighting, visibility
- **Dynamic elements**: other road users, pedestrians, obstacles
- **Driver state**: expected driver engagement, monitoring capability

ODD defines where the system is intended to operate.

## Performance Limitations

Enumerate known limits:
- Sensor range, resolution, latency
- Algorithm confidence thresholds
- Environmental sensor degradation (rain, fog, glare)
- Processing load constraints
- Actuator response time

## Functional Insufficiencies

Root causes why the design is insufficient:
- **Sensor insufficiency**: camera cannot detect in low light
- **Algorithmic insufficiency**: neural network unreliable on edge cases
- **System insufficiency**: sensor fusion failed to account for cross-correlation
- **Actuator insufficiency**: brake response time inadequate for emergency scenario

## Triggering Conditions

Conditions that activate the insufficiency:
- Heavy rain (sensor contamination)
- Dawn/dusk (low contrast)
- High sun angle (camera saturation)
- Pedestrian in non-standard pose
- Road markings obscured or faded
- Vehicle speed > ODD assumption

## Hazardous Behaviors

Resulting unintended vehicle behaviors:
- False brake activation (rear-end collision risk)
- Missed brake (forward collision)
- Unintended steering
- Loss of control

## Scenario Quadrant Logic

Classify each (insufficiency × triggering condition) combination:
- **Known Safe**: specified scenario within performance envelope
- **Known Unsafe**: specified scenario; mitigated by design (e.g., fail-safe)
- **Unknown Safe**: unspecified scenario; safe by chance
- **Unknown Unsafe**: unspecified scenario; hazardous outcome (target residual risk)

## Acceptance Criterion

Quantified threshold for residual risk of Unknown Unsafe scenarios:
- Example: "Probability of unintended emergency braking < 1e-7 per operating hour"
- Must be justified by risk analysis and validation evidence
