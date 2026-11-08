# AIAG-VDA Severity Table (1–10)

The Severity rating reflects the seriousness of the customer-facing effect if the failure mode occurs. It is *independent* of how likely the failure is or how easy it is to detect.

## Rating Scale

| Rating | Severity | Criteria | Vehicle / Customer Impact Examples |
|--------|----------|----------|-----------------------------------|
| **10** | Hazardous, Uncontrolled | A potential hazard that could result in customer / occupant death or serious injury; loss of vehicle control without warning or opportunity for mitigation | - Loss of steering control (LKAS failure causing unintended lane departure) - Unintended sudden maximum brake apply (no driver ability to recover) - Fuel leak leading to fire - Loss of brake function on all wheels - Airbag non-deployment in crash condition |
| **9** | Serious Injury or Major System Failure | A failure that results in serious injury, loss of vehicle control, or loss of a critical safety function; customer has little or no time to react and may not be able to compensate | - Partial loss of steering assist (LKAS dropout during critical maneuver) - Incorrect brake modulation by ESC in dynamic event (loss of yaw control) - Engine stall at highway speed - Transmission loss of all gears - Failure of critical sensor (wheel speed, brake pressure) with no redundancy |
| **8** | Moderate Degradation or Safety Impact | Significant degradation of intended function or moderate safety impact; customer may notice but system may still operate or customer has some ability to respond | - Intermittent power steering assist loss - Incorrect ABS modulation (rough braking but still functional) - Delayed engine response (stumble on acceleration) - Minor sensor drift causing noticeable vehicle behavior change - Headlight dimming or intermittent failure |
| **7** | Moderate System Malfunction | Clear malfunction or degradation of performance; noticeable to customer but does not immediately endanger safety; customer experiences frustration or inconvenience | - Inconsistent cruise control speed tracking (within 5–10 km/h) - Minor transmission shift quality issue - Infotainment system frozen (navigation unavailable) - Door lock intermittently fails to unlock - Fuel gauge reading incorrect but reserves work |
| **6** | Minor Degradation | Minor degradation of function or comfort; customer notices but impact is manageable | - Air conditioning cycles on/off more frequently (less efficient but still cools) - Minor power window noise - Seat belt warning light false positive - Occasional radio static - Speedometer reading within 5% variance |
| **5** | Minor Malfunction, Minimal Customer Impact | Small degradation that does not significantly affect customer experience or function | - Dashboard warning light brightness slightly dim - Occasional low-fuel warning chime missed - Radio preset buttons occasionally unresponsive - Wipers skip a beat - Steering wheel audio controls require double press |
| **4** | Very Minor Malfunction, Barely Noticeable | Defect barely noticeable by most customers; requires very close inspection or specific conditions to observe | - Minor interior panel gap tolerance out of spec (but panel fits) - Very slight steering wheel vibration under specific condition - Occasional soft click in transmission (benign) - Minor seat fabric snag | - Trivial color variation in trim |
| **3** | Insignificant Impact | Defect has no practical impact on vehicle operation, appearance, or customer satisfaction; would be noticed only on very close inspection | - Scuff mark on underbody panel (hidden) - Misalignment of instrument bezel by < 1mm - Very slight odor in cabin (not persisting) - Negligible paint overspray on hidden edge |
| **2** | No Discernible Effect | No observable effect under normal use; defect does not meet the definition of a failure mode; included for completeness | - Slight adhesive residue under seat (hidden, non-functional) - Internal component marking slightly faded - Assembly dust inside sealed enclosure |
| **1** | No Effect | No effect whatsoever; theoretically possible but never observed in practice | - Spare fastener left in parts bin | - Unused design placeholder |

## Guidance for Assessors

### Key Questions to Determine Severity

1. **What happens if this failure occurs?** Trace the failure mode → local effect → subsystem effect → vehicle effect → customer experience.

2. **Is safety involved?** If yes, Severity ≥ 7 (often 8–10). If the customer is injured or the vehicle is uncontrollable, S ≥ 9.

3. **Can the customer compensate?** If the customer can apply workaround (e.g., pump brakes in ABS failure), Severity is lower than if the failure is catastrophic. S=9 implies little customer recourse.

4. **Is the failure detectable by the customer before harm?** If the failure is silent (latent) and only manifests in a critical situation (e.g., yaw sensor fault), Severity tends higher (S ≥ 8) because detection opportunity is lost.

5. **Legal or warranty liability?** If failure could trigger recalls or litigation, Severity ≥ 8.

### Common Pitfalls

- **Conflating Severity with Occurrence**: A high-Severity failure that is extremely rare is still high Severity. S=10, O=1 is realistic (e.g., steering lock-up from manufacturing defect in 1 per million).
- **Under-rating Latent Failures**: A failure mode that is not immediately obvious to the customer (e.g., CAN message loss detected only by diagnostic scanner) should still reflect customer impact if it compromises safety. S ≥ 7 if safety-related.
- **Over-rating Comfort Issues**: Infotainment freezing is annoying (S=7), not dangerous (S≥8). Stick to objective customer impact.
- **Forgetting Regulatory Context**: If the failure violates a regulation (e.g., emissions, safety standard), consider escalating Severity by 1–2 points.

## Safety-Related Design Considerations

For DFMEA linked to ISO 26262 Functional Safety:
- **ASIL D** (highest) items typically have **Severity 9–10** (hazardous or serious injury without control).
- **ASIL C** items: Severity 7–9 (major malfunction with potential for injury).
- **ASIL B** items: Severity 5–7 (moderate to major degradation; injury possible but not certain).
- **ASIL A / QM** items: Severity 1–5 (minor to no customer impact; no safety goal).

Example: A wheel speed sensor signal loss in an ESC system:
- Failure Mode: "Wheel speed sensor output = 0 (open circuit)"
- Effect: "Loss of speed input to ESC algorithm → ESC cannot compute slip ratio"
- Vehicle Effect: "Potential loss of yaw control during emergency maneuver; if yaw spin occurs, customer may overcorrect and crash"
- **Severity = 9** (potential serious injury / loss of control, customer has limited reaction time)
