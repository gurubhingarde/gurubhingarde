---
name: triggering-conditions-builder
description: Generate a detailed ISO 21448 triggering conditions catalog for ADAS/AV systems. Produces 11-tab xlsx enumerating environmental, sensor, road infrastructure, road user, system state, driver state, and combined triggering conditions per function. Use to decompose performance limitations into concrete environmental factors, sensor degradation modes, and system state triggers that activate functional insufficiencies.
---

# Triggering Conditions Builder

Triggering conditions are environmental, sensor, road user, system state, or driver state factors that activate or expose a functional insufficiency. This skill produces a structured enumeration per ISO 21448 Annex, useful for scenario testing, fleet monitoring, and validation planning.

## When to use

Use whenever analyzing which triggering conditions expose ADAS insufficiencies:
- Environmental triggers (rain, fog, glare, lighting)
- Sensor triggers (occlusion, contamination, calibration drift, EMI)
- Road infrastructure triggers (lane markings, construction zones, signage)
- Road user triggers (motorcycle, pedestrian, cyclist, debris)
- System state triggers (warm-up, OTA update, degraded mode)
- Driver state triggers (inattention, hands-off)
- Combined triggers (rare 2+ factor combinations)

## Workflow

1. Upstream SOTIF analysis established insufficiencies
2. Enumerate all triggering conditions per category
3. Assign likelihood (very rare, rare, occasional, common, frequent)
4. Cross-reference to insufficiency × trigger → hazardous behavior
5. Use for scenario test design and fleet data monitoring

## Output structure (11 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Triggering conditions campaign |
| 01 | Document Control | Revision |
| 02 | SOTIF Analysis Reference | Link to upstream SOTIF analysis |
| 03 | Environmental Triggering Conditions | Weather, lighting, road surface |
| 04 | Sensor Triggering Conditions | Per sensor: occlusion, contamination, drift |
| 05 | Road Infrastructure Triggering Conditions | Lane markings, geometry, signage |
| 06 | Other Road User Triggering Conditions | Pedestrian, cyclist, motorcycle, animal |
| 07 | System State Triggering Conditions | Warm-up, OTA, degraded mode |
| 08 | Driver State Triggering Conditions | Inattention, drowsiness, override |
| 09 | Combined Triggering Conditions | Cartesian: 2+ simultaneous factors |
| 10 | References |

Always use this skill instead of producing freeform triggering conditions in chat.
