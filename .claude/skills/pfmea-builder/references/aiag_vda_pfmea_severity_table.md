# AIAG-VDA PFMEA Severity Rating Scale (1-10)

## Manufacturing Context: How Severe is the Customer Impact?

Severity rates the **worst-case effect** of the failure mode if it reaches the customer *undetected*. It is independent of how likely the failure is (Occurrence) or how easy it is to catch (Detection).

## Severity Scale

| Rating | Severity Level | Manufacturing Impact | Examples |
|--------|---|---|---|
| **10** | **Hazardous / Safety Critical** | Customer could be severely injured or killed. Vehicle malfunction poses imminent risk to occupant or other road users. Regulatory non-compliance (emissions, safety recall). | Brake system failure (loss of braking), airbag non-deployment, fuel leak (fire risk), unintended acceleration, steering loss |
| **9** | **Hazardous / Major Performance Loss** | Serious performance loss or malfunction that impacts vehicle safety or drivability. Customer will be very dissatisfied; likely warranty return. High repair cost. | ECU not booting (engine won't start), transmission stuck in gear, loss of power steering, loss of climate control, no communication with diagnostic tools |
| **8** | **Major** | Significant functional loss; vehicle may still be operable but with reduced performance or customer convenience. Warranty return likely. Customer will notice and report. | Intermittent sensor failure, inconsistent gauge readings, occasional communication error, reduced fuel economy, warning light comes on |
| **7** | **Major / Moderate** | Moderate functional degradation or loss of convenience feature. Noticeable but not critical. Partial operation still possible. | One of multiple gauge clusters fails, backup camera intermittent, voice control glitchy |
| **6** | **Moderate** | Minor to moderate loss of convenience or performance. May be noticed by observant customer. | Bluetooth connectivity intermittent, voice commands missed, audio muting at certain RPMs |
| **5** | **Moderate / Minor** | Minimal impact on function or convenience. Customer may not notice on first use. Easy to work around. | Minor cosmetic defect (label misaligned), dashboard brightness slightly low, button requires harder press |
| **4** | **Minor** | Very low customer impact. Easily ignored or worked around. No safety risk. | Cosmetic scratches on connector, label not perfectly centered, slightly degraded appearance |
| **3** | **Minor / Negligible** | Cosmetic or packaging defect only. No functional or safety impact. Customer unlikely to notice unless they actively inspect. | Package arrived with minor dent (product inside OK), label slightly faded, foam insert slightly compressed |
| **2** | **Very Low** | Almost no impact. Discernible only under close inspection. No functional or customer impact. | Packaging dust, minor surface discoloration on non-visible part |
| **1** | **No Effect** | Absolutely no customer or functional impact. Pure internal or documentation issue. | Extra label in box, typo in user manual, internal tracking number misprint |

---

## Guidance for Rating Selection

### Use Severity 9-10 When:
- **Safety**: The failure can cause injury or death (driver, passenger, pedestrian)
- **Regulatory**: Non-compliance with emissions, crash safety, or other mandatory standards
- **Critical Performance**: Vehicle cannot be driven or is severely impaired
- **No workaround**: Customer has no practical option to continue operating
- **Recall risk**: OEM would be forced to issue a recall due to safety/regulatory concern

### Use Severity 7-8 When:
- **Performance Loss**: Major functional loss but vehicle may still limp along
- **Warranty Return**: Most customers would return the vehicle for repair
- **OEM reputation**: Widespread failure would damage brand reputation
- **High repair cost**: Fixing the problem is expensive (requires major disassembly, replacement)
- **Customer frustration**: Clear and immediate frustration (e.g., check engine light, loss of convenience feature)

### Use Severity 5-6 When:
- **Noticeable but tolerable**: Customer notices but can continue normal operation
- **Intermittent issues**: Problem comes and goes; customer may describe as "weird glitch"
- **Reduced convenience**: Loss of a convenience feature but core functionality intact
- **Low repair cost**: Easy fix if customer brings car in for service

### Use Severity 3-4 When:
- **Cosmetic defects**: Appearance issue only; no functional impact
- **Packaging damage**: Product inside OK; external packaging damaged
- **Minor functionality**: Barely noticeable degradation (e.g., slightly reduced brightness, slightly harder button press)

### Use Severity 1-2 When:
- **Documentation errors**: Typo in manual, wrong internal tracking number
- **Pure logistics**: Shipping label mix-up but product correct
- **Zero customer impact**: Truly no effect on customer perception or vehicle operation

---

## Special Cases in Manufacturing

### Hidden Defects (Cannot be caught in field)
If a defect is hidden (e.g., poor solder joint inside an enclosure) and is unlikely to be discovered by customer inspection, use **high severity** (8-9) because once it escapes, it is very difficult or impossible for the customer to diagnose. The customer will perceive it as a random failure: "My car died and I don't know why."

### Intermittent Failures
If the failure is intermittent (e.g., occasional sensor dropout), rate **higher** (7-8) because intermittent problems are:
- Harder to diagnose (customers and service departments struggle)
- More likely to result in warranty returns (customer brings car back multiple times)
- More likely to cause customer frustration and brand damage

### Failed Test Escape (False Negative)
If a defect is supposed to be caught by a test (e.g., ICT test) but the test fails to detect it (test gap), the failure mode is "Failed ICT test" and the severity is **the worst-case if that defect escapes untested**. Use the severity of the underlying defect, not the test failure.

Example:
- Underlying defect: "Trace break on power rail" → severity 9 (no power, no boot)
- Test gap: "ICT fails to detect open trace" → Severity = 9 (because the open trace severity is 9)
- Recommended action: Add probe point or netlist check to ICT; improve test coverage

---

## Examples: ESC ECU Assembly

| Failure Mode | Effect | Severity Rationale | Rating |
|---|---|---|---|
| MCU placed backwards during SMT | Solder joint formed but pins shorted; MCU doesn't boot | Hazardous: no engine control, unintended acceleration risk | **9** |
| Cold solder joint on power supply | Intermittent power loss; random vehicle shutdowns while driving | Hazardous: safety-critical; intermittent failures are especially dangerous | **9** |
| Wrong resistor value (gain resistor) | Sensor signal gain incorrect; braking instability | Major: reduced vehicle stability, potential accident risk | **8** |
| Missing capacitor (decoupling) | Power supply noise; intermittent MCU resets during operation | Major: intermittent performance loss; customer perceives as unreliable | **8** |
| Trace bridge (short circuit) | Short detected during ICT but escapes if ICT not 100% | Hazardous: if it reaches customer (ICT false pass), device may fail in field | **9** |
| Label not applied during final pack | No serial number; cannot trace part back to build lot | Major: traceability loss; cannot investigate field failures or recalls | **7** |
| Firmware wrong version | Incorrect calibration; emission compliance failure | Hazardous: regulatory non-compliance | **10** |
| Connector contacts not fully seated | High-impedance connection; intermittent communication | Major: intermittent failures; customer frustration | **8** |
| Conformal coat on connector | Connection intermittent; loss of communication | Major: intermittent diagnostic communication loss | **8** |
| Packaging damaged (crushed); product OK inside | Cosmetic damage only; product functional | Minor: customer may complain about packaging but vehicle works | **3** |

---

## ISO/AIAG PFMEA Severity vs. ISO 26262 ASIL

Note: ISO 26262 (Functional Safety) uses a different classification system (ASIL A/B/C/D) that combines severity, exposure, and controllability. PFMEA Severity is **not the same** as ASIL.

For functional safety-critical products:
- Use ISO 26262 Item Definition to identify Safety Goals
- Use FMEA (or FMEDA for hardware) to perform safety analysis per ISO 26262
- PFMEA is still useful for manufacturing risk management, even in functional safety projects

**Best practice**: Conduct both DFMEA/PFMEA (for manufacturing and production readiness) AND a formal ISO 26262 FMEA/FMEDA (for functional safety). They are complementary.
