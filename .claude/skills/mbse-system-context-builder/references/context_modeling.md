# System Context Modeling Best Practices

## Boundary Definition

Clear boundary statements prevent scope creep:
- "This system manages autonomous navigation and obstacle avoidance up to vehicle deceleration."
- "Out of scope: long-term path planning, driver comfort optimization."

## Actor Identification

Comprehensive actor inventory:
- Interview stakeholders to identify all users and interfacing systems
- Categorize by actor type
- Document actor goals and constraints
- Consider regulatory and third-party actors

## Interface Definition

Each actor relationship is an interface:
- Specify data/control/energy/material flows
- Direction (in, out, bidirectional)
- Protocol or medium
- Example: "Driver Command Interface (in): steering/throttle/brake inputs"

## Use Cases

Customer-facing scenarios:
- "User enables autonomous driving" involves multiple actors
- Flow describes system responses to actor stimuli
- Captures both happy path and error handling

## Scenario Definition

Temporal sequences illustrating typical system operation:
- "Morning commute": routine highway driving
- "Emergency braking": unexpected obstacle
- "Loss of sensor": degraded mode operation

## Stakeholder Needs

Link back to business and operational requirements:
- Safety: "System shall not cause injury"
- Performance: "Latency < 100ms"
- Usability: "Interface easy for novice driver"
- Cost: "BOM under $5000"
