# Hardware Failure Mode Libraries — IEC 62380 & FIDES

Baseline failure mode distributions per element type. Use these as defaults in the FMEDA; override per project FIT source (supplier datasheet, FIDES model, operational data).

## Microcontroller (MCU)

**Total FIT assumption: 50–150 FIT per MHz**. Highly dependent on process (28nm, 90nm), voltage, temperature.

| Failure Mode | Distribution | Notes |
|---|---|---|
| Stuck-at (bit stuck 0 or 1) | 30% | Combinational logic, instruction fetch |
| Transient (single-event upset, cosmic/alpha) | 40% | Overwhelms stuck-at at lower voltages; increases with altitude |
| I/O fault (pad stuck high/low) | 15% | Output driver or receiver; often environmental (ESD, crosstalk) |
| Oscillator fault (clock loss, drift) | 15% | Quartz oscillator degradation; RC oscillator less reliable |

## Sensor IC (Pressure, Temperature, Hall Effect)

**Total FIT: 20–80 FIT** depending on integration density and environmental stress.

| Failure Mode | Distribution | Notes |
|---|---|---|
| No output (open, short to GND) | 20% | Bond wire break, pad open |
| Stuck output (short to VDD or latch-up) | 30% | Latch-up from ESD or overvoltage |
| Drifted / out-of-range (gain or offset error) | 30% | Aging of filter capacitor, oxidation of interface |
| Noisy output (oscillation, intermittent) | 20% | Supply coupling, common-mode noise |

## Power Supply / Voltage Regulator IC

**Total FIT: 30–100 FIT** depending on input range, power dissipation, thermal management.

| Failure Mode | Distribution | Notes |
|---|---|---|
| Undervoltage (VDD below spec) | 40% | Soft start failure, load transient overshoot during shutdown |
| Overvoltage (VDD above spec) | 20% | Loss of feedback, output capacitor ESR degradation, Zener drift |
| Oscillation (unstable feedback loop) | 30% | Phase margin loss due to aging of compensation components |
| Thermal shutdown (false trigger) | 10% | Temperature sensor drift, threshold variation |

## Memory IC (SRAM, Flash, EEPROM)

**Total FIT: 50–300 FIT** depending on density, refresh rate (SRAM), cycling (Flash).

| Failure Mode | Distribution | Notes |
|---|---|---|
| Single-bit error (soft, correctable by ECC) | 50% | Dominant at low voltages; alpha particle, CMOS noise |
| Multi-bit error (hard, uncorrectable) | 5% | Semiconductor defect, electromigration in interconnect |
| Address decoder fault | 15% | Multiplexer failure, address line stuck or shorted |
| Read-disturb / write-disturb (Flash) | 30% | Repeated access degrades adjacent cells; common in NOR Flash |

## Driver IC (Gate driver, H-bridge, half-bridge)

**Total FIT: 40–150 FIT** depending on switching frequency, current rating.

| Failure Mode | Distribution | Notes |
|---|---|---|
| Open output (gate no longer driven) | 25% | Bond wire break, FET channel leakage |
| Short to supply (always on) | 25% | Gate driver output floating or pulled high; FET body diode conducts |
| Short to ground (always off) | 25% | Gate driver pull-down failure |
| Gate driver IC fault (latch-up) | 25% | Over-current, over-temperature, supply transient |

## Communication IC (CAN, LIN, SPI transceiver)

**Total FIT: 20–100 FIT** depending on baudrate, EMI environment.

| Failure Mode | Distribution | Notes |
|---|---|---|
| No transmission (TX stuck low or floating) | 30% | Output driver failure, driver enable signal lost |
| No reception (RX stuck or insensitive) | 30% | Input stage failure, overvoltage clamp open |
| Corrupted frames (bit errors, parity loss) | 20% | Receiver threshold drift, capacitive coupling from switching noise |
| Loss of supply (internal regulator failure) | 20% | Integrated LDO or bandgap failure; oscillation in supply feedback |

## Inductor (Choke, transformer)

**Total FIT: 1–10 FIT** (mechanical/magnetic, not electrical aging).

| Failure Mode | Distribution | Notes |
|---|---|---|
| Open winding (wire break, cold joint) | 60% | Mechanical stress from thermal cycling, vibration |
| Shorted turns (insulation breakdown, arcing) | 30% | Transient overvoltage, manufacturing defect |
| Core saturation (permeability loss) | 10% | Aging of ferrite core, temperature drift of initial permeability |

## Capacitor (Ceramic, electrolytic)

**Total FIT: 5–50 FIT** depending on technology and stress.

| Failure Mode | Distribution | Notes |
|---|---|---|
| Capacitance loss (open or leakage) | 50% | Dielectric breakdown; common in aged electrolytics |
| ESR increase (equivalent series resistance) | 40% | Electrolyte evaporation (electrolytics), conductive oxide aging |
| Voltage derating overshoot (catastrophic) | 10% | Applied voltage exceeds derating; transient overvoltage |

## Resistor (Thin-film, thick-film)

**Total FIT: 0.5–5 FIT** (very reliable; rarely the dominant failure).

| Failure Mode | Distribution | Notes |
|---|---|---|
| Resistance increase (open or high resistance) | 50% | Aging of resistive material, oxidation of terminations |
| Resistance decrease (short or low resistance) | 40% | Electromigration, contamination, overvoltage transient |
| Thermal runaway (excessive dissipation) | 10% | Power derating violated; compounding with temperature drift |

## Printed Circuit Board (Traces, vias, solder joints)

**Total FIT: 5–30 FIT** depending on design rules, environmental class.

| Failure Mode | Distribution | Notes |
|---|---|---|
| Solder joint crack (open connection) | 60% | Thermal cycling, vibration-induced fatigue, Pb-free solder brittleness |
| Trace crack / via separation (open net) | 20% | Mechanical flexing, CTE mismatch, current stress migration |
| Trace-to-trace short (crosstalk, contamination) | 15% | Conductive residue, dendrite growth, acid flux residue |
| Via fill void (open connection in multilayer) | 5% | Manufacturing defect; plating incompleteness |

## Notes for FMEDA Analyst

1. **Sourcing is critical.** Use supplier FIT data (from JESD47 testing per AEC-Q100 / AEC-Q200) whenever available. IEC 62380 and FIDES provide order-of-magnitude guidance, but are less accurate than production field data.

2. **Temperature and stress affect distribution.** The percentages above assume nominal operating conditions (25–65°C, rated voltage/current, low EMI). Higher temperature, voltage stress, or EMI can shift distributions (e.g., more transient events in a harsh environment).

3. **Process corner matters.** A 7 nm MCU will have a different failure distribution than a 90 nm MCU. Always cross-check against the actual technology node and process characterization.

4. **Design margins reduce residual rates.** Overdesign (e.g., 20% voltage margin, 40°C derate) lowers residual fault rates by reducing the probability that a detected fault propagates to a safety goal violation.

5. **Overrides in JSON.** If you have specific evidence for a different distribution (e.g., "Our production data shows 15% of MCU failures are oscillator faults, not 15%"), include a `failure_mode_overrides` entry in the HW BOM JSON with the corrected percentage.

